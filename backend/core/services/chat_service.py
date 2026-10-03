"""Сервис чата: беседы, сообщения, вложения.

Правила домена — здесь, SQL — в core.repositories.chat.ChatRepository.
Ключевое правило раздела 2: событие публикуется в Redis **строго после commit**
(Postgres — источник истины, Pub/Sub только доставляет), а повторная отправка
с тем же `idempotency_key` не создаёт дубликата.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dependencies import ChatActor
from core.exceptions import (
    AttachmentLimitError,
    AttachmentNotAvailableError,
    AttachmentNotFoundError,
    AttachmentsMissingError,
    ChatError,
    ConversationNotFoundError,
    MessageEmptyError,
    MessageTooLongError,
)
from core.models.chats.attachment import Attachment
from core.models.chats.conversation import Conversation
from core.models.chats.message import Message
from core.models.enums.actor_types import ActorType
from core.models.enums.message_types import MessageType
from client.models.client import Client
from client.models.request import CargoRequest
from executor.models.executor import Executor
from core.redis.chat import EVENT_MESSAGE_CREATED
from core.redis.redis_client import redis_client
from core.repositories.chat import ChatRepository
from core.schemas.chat import (
    AttachmentRead,
    ChatPeerRead,
    ConversationRead,
    ConversationUnreadRead,
    MessageCreate,
    MessageRead,
    OrderBriefRead,
)
from core.services import attachment_storage


class ChatService:
    """Одна сессия БД на запрос: транзакцию закрывает сам сервис."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ChatRepository(db)

    # беседы

    async def list_conversations(
        self, actor: ChatActor, *, skip: int = 0, limit: int = 20
    ) -> list[ConversationRead]:
        """Список бесед участника: активные сверху, с непрочитанными и последним сообщением.

        Пять запросов на страницу (список + непрочитанные + последние сообщения +
        собеседники + заказы) вместо N+1: страница ограничена `limit`.
        """
        conversations = await self.repository.list_conversations(
            actor.role, actor.id, skip=skip, limit=limit
        )
        if not conversations:
            return []

        ids = [conversation.id for conversation in conversations]
        unread = await self.repository.unread_counts(ids, actor.role)
        last_messages = await self.repository.get_last_messages(ids)
        peers = await self.repository.get_counterparties(conversations, actor.role)
        orders = await self.repository.get_orders(
            [conversation.order_id for conversation in conversations]
        )

        items: list[ConversationRead] = []
        for conversation in conversations:
            # участники и заказ — CASCADE-FK: без них беседа физически не существует
            peer = peers.get(
                conversation.executor_id
                if actor.role is ActorType.client
                else conversation.client_id
            )
            order = orders.get(conversation.order_id)
            if peer is None or order is None:
                continue

            items.append(
                self._conversation_read(
                    conversation,
                    peer=peer,
                    order=order,
                    last_message=last_messages.get(conversation.id),
                    unread_count=unread.get(conversation.id, 0),
                )
            )
        return items

    async def get_conversation(
        self, actor: ChatActor, conversation_id: int
    ) -> ConversationRead:
        """Одна беседа: 404, если её нет или участником она не является."""
        conversation = await self._get_participant_conversation(actor, conversation_id)

        ids = [conversation.id]
        unread = await self.repository.unread_counts(ids, actor.role)
        last_messages = await self.repository.get_last_messages(ids)
        peers = await self.repository.get_counterparties([conversation], actor.role)
        orders = await self.repository.get_orders([conversation.order_id])

        peer = peers.get(
            conversation.executor_id
            if actor.role is ActorType.client
            else conversation.client_id
        )
        order = orders.get(conversation.order_id)
        if peer is None or order is None:
            raise ConversationNotFoundError(conversation_id)

        return self._conversation_read(
            conversation,
            peer=peer,
            order=order,
            last_message=last_messages.get(conversation.id),
            unread_count=unread.get(conversation.id, 0),
        )

    # сообщения

    async def list_messages(
        self,
        actor: ChatActor,
        conversation_id: int,
        *,
        before_id: int | None = None,
        after_id: int | None = None,
        limit: int = 50,
    ) -> list[MessageRead]:
        """История беседы (курсорная) — всегда по возрастанию id.

        `after_id` после реконнекта догружает пропущенное: Pub/Sub доставку
        не гарантирует, источник истины — Postgres (§7).
        """
        await self._get_participant_conversation(actor, conversation_id)
        messages = await self.repository.list_messages(
            conversation_id, before_id=before_id, after_id=after_id, limit=limit
        )
        return [MessageRead.model_validate(message) for message in messages]

    @staticmethod
    def _conversation_read(
        conversation: Conversation,
        *,
        peer: Client | Executor,
        order: CargoRequest,
        last_message: Message | None,
        unread_count: int,
    ) -> ConversationRead:
        """Сборка карточки беседы из уже загруженных данных (без ленивых обращений)."""
        return ConversationRead(
            id=conversation.id,
            order_id=conversation.order_id,
            peer=ChatPeerRead(id=peer.id, name=peer.name, image_url=peer.image_url),
            order=OrderBriefRead.model_validate(order),
            last_message=(
                MessageRead.model_validate(last_message) if last_message else None
            ),
            unread_count=unread_count,
            last_message_at=conversation.last_message_at,
            created_at=conversation.created_at,
        )

    async def _get_participant_conversation(
        self, actor: ChatActor, conversation_id: int
    ) -> Conversation:
        """Беседа участника; чужая или несуществующая — одна и та же 404 (§9)."""
        conversation = await self.repository.get_participant_conversation(
            actor.role, actor.id, conversation_id
        )
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    async def create_message(
        self, actor: ChatActor, conversation_id: int, data: MessageCreate
    ) -> MessageRead:
        """Отправка сообщения: проверки → INSERT с вложениями → commit → publish.

        Ретрай с тем же `idempotency_key` возвращает уже созданное сообщение,
        а не дубль: нарушение частичного UNIQUE ловим как `IntegrityError`.
        """
        conversation = await self._get_participant_conversation(actor, conversation_id)
        body, attachments = await self._prepare_payload(actor, data)

        try:
            message = await self.repository.create_message(
                conversation,
                role=actor.role,
                user_id=actor.id,
                message_type=data.type,
                body=body,
                attachments=attachments,
                idempotency_key=data.idempotency_key,
            )
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            existing = await self._idempotent_hit(
                conversation.id, data.idempotency_key
            )
            if existing is None:
                raise exc
            # это ретрай уже отправленного сообщения: событие ушло при первой попытке
            return MessageRead.model_validate(existing)

        # вложения — отдельным запросом: в async ленивое отношение после commit
        # не заряжается (MissingGreenlet), а ретрай мы уже вернули выше
        stored = await self.repository.get_message(message.id)
        if stored is None:  # pragma: no cover — строку вставили в этой же сессии
            raise ChatError("Сообщение исчезло сразу после сохранения")

        # строго после commit: публикация не должна уехала раньше транзакции (§2)
        await self._publish_message_created(conversation, stored)
        return MessageRead.model_validate(stored)

    async def _prepare_payload(
        self, actor: ChatActor, data: MessageCreate
    ) -> tuple[str | None, list[Attachment]]:
        """Чистка текста и лимиты/проверка вложений до записи в БД (§9)."""
        body = (data.body or "").strip() or None

        if data.type is MessageType.text:
            if body is None:
                raise MessageEmptyError()
            self._check_body_length(body)
            return body, []

        # у media подпись опциональна, но пустой строкой не бывает
        if body is not None:
            self._check_body_length(body)

        attachment_ids = list(dict.fromkeys(data.attachment_ids))
        if not attachment_ids:
            raise AttachmentsMissingError()
        if len(attachment_ids) > settings.chat_max_attachments:
            raise AttachmentLimitError(settings.chat_max_attachments)

        return body, await self._claim_attachments(actor, attachment_ids)

    @staticmethod
    def _check_body_length(body: str) -> None:
        if len(body) > settings.chat_max_message_length:
            raise MessageTooLongError(settings.chat_max_message_length)

    async def _claim_attachments(
        self, actor: ChatActor, attachment_ids: list[int]
    ) -> list[Attachment]:
        """Вложения должны принадлежать отправителю и быть ещё не отправленными.

        Чужое вложение неотличимо от несуществующего — та же 404 (§9).
        """
        attachments = await self.repository.get_attachments(attachment_ids)
        found = {attachment.id: attachment for attachment in attachments}

        for attachment_id in attachment_ids:
            if attachment_id not in found:
                raise AttachmentNotFoundError(attachment_id)

        for attachment in attachments:
            if not self._is_uploader(actor, attachment):
                raise AttachmentNotFoundError(attachment.id)
            if attachment.message_id is not None:
                raise AttachmentNotAvailableError(attachment.id)

        return attachments

    @staticmethod
    def _is_uploader(actor: ChatActor, attachment: Attachment) -> bool:
        """Вложение загружено этим же участником (роль обязана совпасть: id разных таблиц)."""
        if attachment.uploader_type is not actor.role:
            return False
        if actor.role is ActorType.client:
            return attachment.uploader_client_id == actor.id
        return attachment.uploader_executor_id == actor.id

    async def _idempotent_hit(
        self, conversation_id: int, idempotency_key: str | None
    ) -> Message | None:
        """Сообщение этого же ключа; без ключа дублем считать нечего."""
        if not idempotency_key:
            return None
        return await self.repository.get_by_idempotency_key(
            conversation_id, idempotency_key
        )

    @staticmethod
    async def _publish_message_created(
        conversation: Conversation, message: Message
    ) -> None:
        """Событие в каналы обоих участников — строго после commit (§2, §7).

        Ошибки Redis не пробрасывает publish_chat_event: доставка по WS —
        ускоритель, а не источник правды.
        """
        await redis_client.publish_chat_event(
            client_id=conversation.client_id,
            executor_id=conversation.executor_id,
            event_type=EVENT_MESSAGE_CREATED,
            data={
                "conversation_id": conversation.id,
                "message": MessageRead.model_validate(message).model_dump(mode="json"),
            },
        )

    # прочитано и вложения

    async def mark_read(
        self, actor: ChatActor, conversation_id: int, last_read_id: int
    ) -> ConversationUnreadRead:
        """«Прочитано до id=X» и актуальный счётчик (непрочитанных обычно 0)."""
        conversation = await self._get_participant_conversation(actor, conversation_id)
        await self.repository.mark_read(conversation, actor.role, last_read_id)
        await self.db.commit()

        counts = await self.repository.unread_counts([conversation.id], actor.role)
        return ConversationUnreadRead(
            conversation_id=conversation.id,
            unread_count=counts.get(conversation.id, 0),
        )

    async def upload_attachment(
        self, actor: ChatActor, file: UploadFile
    ) -> AttachmentRead:
        """Multipart-загрузка: диск → строка `Attachment` без `message_id` (§5).

        Привязка к сообщению произойдёт в `create_message`. Если после записи
        файла упал БД-шаг — файл удаляем сами, чтобы в `uploads/` не копились сироты.
        """
        stored = await attachment_storage.save_upload(file)

        try:
            attachment = await self.repository.create_attachment(
                role=actor.role,
                user_id=actor.id,
                url=stored.url,
                content_type=stored.content_type,
                size=stored.size,
                width=stored.width,
                height=stored.height,
            )
            await self.db.commit()
        except Exception:
            (attachment_storage.UPLOAD_DIR / Path(stored.url).name).unlink(
                missing_ok=True
            )
            raise

        await self.db.refresh(attachment)  # created_at из server_default
        return AttachmentRead.model_validate(attachment)

    async def get_attachment_url(self, actor: ChatActor, attachment_id: int) -> str:
        """URL вложения: его видит загрузивший либо участники беседы, куда файл ушёл (§9)."""
        attachment = await self.repository.get_attachment(attachment_id)
        if attachment is None:
            raise AttachmentNotFoundError(attachment_id)

        if attachment.message_id is None:
            # еще не отправлено — доступно только аплоадеру
            if not self._is_uploader(actor, attachment):
                raise AttachmentNotFoundError(attachment_id)
            return attachment.url

        message = await self.repository.get_message(attachment.message_id)
        if message is None:  # pragma: no cover — FK не даёт удалить сообщение с вложением
            raise AttachmentNotFoundError(attachment_id)

        await self._get_participant_conversation(actor, message.conversation_id)
        return attachment.url




