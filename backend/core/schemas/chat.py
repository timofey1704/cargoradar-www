"""Схемы чата: беседы, сообщения, вложения.

Вложения в ответе содержат относительный URL (`/uploads/chat/...`) — фронт
дописывает origin бэкенда.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.models.enums.actor_types import ActorType
from core.models.enums.message_types import MessageType
from utils.address_formatter import FormattedAddress


class AttachmentRead(BaseModel):
    """Вложение сообщения (или загруженное, но ещё не привязанное)."""

    id: int
    url: str
    content_type: str
    size: int
    width: int | None = None
    height: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatPeerRead(BaseModel):
    """Собеседник глазами текущего участника: имя и аватар для списка бесед."""

    id: int
    name: str
    image_url: str | None = None


class OrderBriefRead(BaseModel):
    """Заказ, по которому заведена беседа (для заголовка карточки)."""

    id: int
    origin_address: FormattedAddress
    destination_address: FormattedAddress
    cargo_type: str

    model_config = ConfigDict(from_attributes=True)


class MessageRead(BaseModel):
    """Сообщение ленты: текст, медиа или карточка оффера (`offer_id`)."""

    id: int
    conversation_id: int

    sender_type: ActorType
    sender_client_id: int | None = None
    sender_executor_id: int | None = None

    type: MessageType
    body: str | None = None
    offer_id: int | None = None

    attachments: list[AttachmentRead] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationRead(BaseModel):
    """Карточка беседы списка: собеседник, заказ, последнее сообщение, непрочитанные."""

    id: int
    order_id: int

    # собеседник с точки зрения запросившего: клиенту — исполнитель, и наоборот
    peer: ChatPeerRead
    order: OrderBriefRead

    last_message: MessageRead | None = None
    unread_count: int = 0
    last_message_at: datetime | None = None
    created_at: datetime


class MessageCreate(BaseModel):
    """Тело POST /conversations/{id}/messages.

    Структурные проверки (какой `type` с каким payload допустим) — здесь, они
    превращаются в 422 без похода в БД; лимиты из настроек — в сервисе
    (MessageTooLongError / AttachmentLimitError).
    """

    model_config = ConfigDict(extra="forbid")

    type: MessageType = MessageType.text
    body: str | None = None
    attachment_ids: list[int] = Field(default_factory=list)
    idempotency_key: str | None = Field(default=None, max_length=36)

    @model_validator(mode="after")
    def check_payload(self) -> MessageCreate:
        if self.type not in (MessageType.text, MessageType.media):
            raise ValueError("type может быть только 'text' или 'media'")

        if self.type is MessageType.text:
            if not (self.body or "").strip():
                raise ValueError("текстовое сообщение требует body")
            if self.attachment_ids:
                raise ValueError("текстовое сообщение не может содержать вложения")
        elif not self.attachment_ids:
            raise ValueError("media-сообщение требует attachment_ids")

        return self


class ConversationReadUpdate(BaseModel):
    """Тело POST /conversations/{id}/read: отметка «прочитано до id=X»."""

    model_config = ConfigDict(extra="forbid")

    last_read_id: int = Field(ge=0)


class ConversationUnreadRead(BaseModel):
    """Ответ POST /conversations/{id}/read: обновлённый счётчик непрочитанных."""

    conversation_id: int
    unread_count: int
