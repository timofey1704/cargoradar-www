"""Репозиторий чата: выборки бесед, сообщений и вложений.

Как и в client.repositories.request: только готовит данные и делает flush —
транзакцию закрывает сервис (core.services.chat_service.ChatService).

Проверка участия в беседе живёт здесь, в условии SQL (`membership_clause`):
постороннему ответ такой же, как для несуществующей беседы, а объект чужой
беседы не попадает в сессию.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from client.models.client import Client
from client.models.request import CargoRequest
from core.models.chats.attachment import Attachment
from core.models.chats.conversation import Conversation
from core.models.chats.message import Message
from core.models.enums.actor_types import ActorType
from core.models.enums.message_types import MessageType
from executor.models.executor import Executor

Counterparty = Client | Executor


class ChatRepository:
    """Данные чата в рамках текущей сессии."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # участники

    @staticmethod
    def membership_clause(role: ActorType, user_id: int):
        """Условие «пользователь — участник беседы» для роли из ChatActor."""
        if role is ActorType.client:
            return Conversation.client_id == user_id
        return Conversation.executor_id == user_id

    @staticmethod
    def read_marker_column(role: ActorType):
        """Колонка `*_last_read_id` участника (для подсчёта непрочитанных)."""
        if role is ActorType.client:
            return Conversation.client_last_read_id
        return Conversation.executor_last_read_id

    @staticmethod
    def counterparty_type(role: ActorType) -> ActorType:
        """Сторона, от которой приходят непрочитанные (собеседник)."""
        return ActorType.executor if role is ActorType.client else ActorType.client

    # беседы
    async def get_participant_conversation(
        self, role: ActorType, user_id: int, conversation_id: int
    ) -> Conversation | None:
        """Беседа текущего участника; чужая или несуществующая — None."""
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            self.membership_clause(role, user_id),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_conversations(
        self, role: ActorType, user_id: int, *, skip: int = 0, limit: int = 20
    ) -> Sequence[Conversation]:
        """Беседы участника: активные сверху, без сообщений — в конец страницы.

        `last_message_at` денормализован в модели именно ради этой сортировки:
        без неё пришлось бы джойнить messages на каждую страницу списка.
        """
        stmt = (
            select(Conversation)
            .where(self.membership_clause(role, user_id))
            .order_by(
                Conversation.last_message_at.desc().nulls_last(),
                Conversation.id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def unread_counts(
        self, conversation_ids: Sequence[int], role: ActorType
    ) -> dict[int, int]:
        """Непрочитанные по каждой беседе: сообщения собеседника новее моего last_read_id.

        Одна агрегация на всю страницу списка вместо подзапроса на каждую строку.
        """
        if not conversation_ids:
            return {}

        stmt = (
            select(Message.conversation_id, func.count().label("unread"))
            .join(Conversation, Conversation.id == Message.conversation_id)
            .where(Message.conversation_id.in_(list(conversation_ids)))
            .where(Message.id > self.read_marker_column(role))
            .where(Message.sender_type == self.counterparty_type(role))
            .group_by(Message.conversation_id)
        )
        rows = (await self.session.execute(stmt)).all()
        return {row.conversation_id: int(row.unread) for row in rows}

    async def get_last_messages(
        self, conversation_ids: Sequence[int]
    ) -> dict[int, Message]:
        """Последнее сообщение каждой беседы (с вложениями) одним запросом.

        Последнее = максимум id: id монотонен, поэтому не нужен джойн по
        created_at, а индекс `(conversation_id, id)` покрывает агрегат.
        """
        if not conversation_ids:
            return {}

        max_ids = (
            select(
                Message.conversation_id.label("conversation_id"),
                func.max(Message.id).label("message_id"),
            )
            .where(Message.conversation_id.in_(list(conversation_ids)))
            .group_by(Message.conversation_id)
            .subquery()
        )

        stmt = (
            select(Message)
            .join(max_ids, Message.id == max_ids.c.message_id)
            .options(selectinload(Message.attachments))
        )
        messages = (await self.session.execute(stmt)).scalars().all()
        return {message.conversation_id: message for message in messages}

    async def get_counterparties(
        self, conversations: Sequence[Conversation], role: ActorType
    ) -> dict[int, Counterparty]:
        """Собеседники страницы: клиенту — исполнители, исполнителю — клиенты."""
        if not conversations:
            return {}

        if role is ActorType.client:
            ids = [conversation.executor_id for conversation in conversations]
            stmt = select(Executor).where(Executor.id.in_(ids))
        else:
            ids = [conversation.client_id for conversation in conversations]
            stmt = select(Client).where(Client.id.in_(ids))

        result = await self.session.execute(stmt)
        return {user.id: user for user in result.scalars().all()}

    async def get_orders(self, order_ids: Sequence[int]) -> dict[int, CargoRequest]:
        """Заказы страницы бесед (заголовок карточки: маршрут и груз)."""
        if not order_ids:
            return {}
        result = await self.session.execute(
            select(CargoRequest).where(CargoRequest.id.in_(list(order_ids)))
        )
        return {order.id: order for order in result.scalars().all()}

    # сообщения 

    async def list_messages(
        self,
        conversation_id: int,
        *,
        before_id: int | None = None,
        after_id: int | None = None,
        limit: int = 50,
    ) -> list[Message]:
        """Курсорная выборка сообщений — наружу всегда по возрастанию id.

        - `after_id` — догрузка после реконнекта: первые `limit` новее курсора;
        - `before_id` — прокрутка истории назад: последние `limit` старше курсора;
        - без курсоров — последние `limit` сообщений ленты.

        При прокрутке курсор идёт от границы к началу истории, поэтому такая
        выборка разворачивается перед отдачей (фронт рендерит ленту по возрастанию).
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .options(selectinload(Message.attachments))
        )

        reverse = False
        if after_id is not None:
            stmt = stmt.where(Message.id > after_id).order_by(Message.id.asc())
        elif before_id is not None:
            stmt = stmt.where(Message.id < before_id).order_by(Message.id.desc())
            reverse = True
        else:
            stmt = stmt.order_by(Message.id.desc())
            reverse = True

        rows = list((await self.session.execute(stmt.limit(limit))).scalars().all())
        return list(reversed(rows)) if reverse else rows

    async def get_message(self, message_id: int) -> Message | None:
        """Сообщение вместе с вложениями (selectin: в async ленивые отношения не грузятся)."""
        stmt = (
            select(Message)
            .where(Message.id == message_id)
            .options(selectinload(Message.attachments))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(
        self, conversation_id: int, idempotency_key: str
    ) -> Message | None:
        """Сообщение, созданное этим же ключом (ретрай клиента — не дубль)."""
        stmt = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.idempotency_key == idempotency_key,
            )
            .options(selectinload(Message.attachments))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_message(
        self,
        conversation: Conversation,
        *,
        role: ActorType,
        user_id: int,
        message_type: MessageType,
        body: str | None,
        attachments: Sequence[Attachment],
        idempotency_key: str | None,
    ) -> Message:
        """Создаёт сообщение, привязывает вложения и двигает `last_message_at` беседы.

        flush + refresh нужны до коммита: `id`/`created_at` приходят из
        server_default, а `last_message_at` обязан совпасть с `created_at`
        сообщения — иначе список бесед отсортируется не так, как выглядит лента.
        """
        message = Message(
            conversation_id=conversation.id,
            sender_type=role,
            sender_client_id=user_id if role is ActorType.client else None,
            sender_executor_id=user_id if role is ActorType.executor else None,
            type=message_type,
            body=body,
            idempotency_key=idempotency_key,
        )
        self.session.add(message)
        await self.session.flush()  # id из sequence

        for attachment in attachments:
            attachment.message_id = message.id

        await self.session.refresh(message)  # created_at из server_default
        conversation.last_message_at = message.created_at
        await self.session.flush()
        return message

    # вложения

    async def get_attachment(self, attachment_id: int) -> Attachment | None:
        result = await self.session.execute(
            select(Attachment).where(Attachment.id == attachment_id)
        )
        return result.scalar_one_or_none()

    async def get_attachments(
        self, attachment_ids: Sequence[int]
    ) -> list[Attachment]:
        """Вложения в порядке, заданном запросом; отсутствующие пропускаются — их доругает сервис."""
        if not attachment_ids:
            return []

        result = await self.session.execute(
            select(Attachment).where(Attachment.id.in_(list(attachment_ids)))
        )
        found = {attachment.id: attachment for attachment in result.scalars().all()}
        return [found[i] for i in attachment_ids if i in found]

    async def create_attachment(
        self,
        *,
        role: ActorType,
        user_id: int,
        url: str,
        content_type: str,
        size: int,
        width: int | None,
        height: int | None,
    ) -> Attachment:
        """Вложение без `message_id`: привяжется к сообщению, когда его отправят (§5)."""
        attachment = Attachment(
            uploader_type=role,
            uploader_client_id=user_id if role is ActorType.client else None,
            uploader_executor_id=user_id if role is ActorType.executor else None,
            url=url,
            content_type=content_type,
            size=size,
            width=width,
            height=height,
        )
        self.session.add(attachment)
        await self.session.flush()
        return attachment

    # отметка прочитано
    async def get_conversation(self, conversation_id: int) -> Conversation | None:
        """Беседа без проверки участия — для приватности вложений (§9)."""
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def mark_read(
        self, conversation: Conversation, role: ActorType, last_read_id: int
    ) -> Conversation:
        """Двигает `*_last_read_id` только вперёд: назад — значит «разпрочитать» и вернуть счётчик."""
        column = self.read_marker_column(role)
        if last_read_id > getattr(conversation, column.key):
            setattr(conversation, column.key, last_read_id)
            await self.session.flush()
        return conversation



