from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models.enums.actor_types import ActorType
from core.models.enums.message_types import MessageType

if TYPE_CHECKING:
    from core.models.chats.conversation import Conversation
    from core.models.chats.attachment import Attachment
    from core.models.offer import Offer


class Message(Base):
    """Сообщение в беседе: текст, медиа, карточка оффера или системное."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

    # полиморфный отправитель: клиент, исполнитель или system
    # (для system оба FK пустые)
    sender_type: Mapped[ActorType] = mapped_column(
        SAEnum(
            ActorType,
            name="message_sender_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ActorType.system,
        server_default=ActorType.system.value,
    )
    sender_client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    sender_executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("executors.id", ondelete="SET NULL"), nullable=True
    )

    type: Mapped[MessageType] = mapped_column(
        SAEnum(
            MessageType,
            name="message_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=MessageType.text,
        server_default=MessageType.text.value,
    )
    body: Mapped[str | None] = mapped_column(Text, nullable=True)

    # карточка оффера в ленте: message(type='offer', offer_id=...)
    offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("offers.id", ondelete="SET NULL"), nullable=True
    )

    # ключ идемпотентности от клиента (UUID), чтобы ретраи не создавали дубликаты
    idempotency_key: Mapped[str | None] = mapped_column(String(36), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    offer: Mapped["Offer | None"] = relationship(back_populates="messages")
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # курсорная пагинация «50 сообщений старше id=X»
        Index("ix_messages_conv_id", "conversation_id", "id"),
        # идемпотентность только для сообщений с ключом (частичный индекс, чтобы
        # строки без ключа, включая system/offer, не конфликтовали между собой)
        Index(
            "uq_messages_idempotency",
            "conversation_id",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
        # отправитель однозначен: либо клиент, либо исполнитель, либо system
        CheckConstraint(
            "(sender_type = 'client'   AND sender_client_id IS NOT NULL AND sender_executor_id IS NULL) OR "
            "(sender_type = 'executor' AND sender_executor_id IS NOT NULL AND sender_client_id IS NULL) OR "
            "(sender_type = 'system'   AND sender_client_id IS NULL AND sender_executor_id IS NULL)",
            name="ck_messages_sender",
        ),
    )