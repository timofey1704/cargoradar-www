from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from executor.models.executor import Executor
    from client.models.client import Client
    from client.models.request import CargoRequest
    from core.models.chats.message import Message
    from core.models.offer import Offer


class Conversation(Base):
    """Беседа по паре «заказ + исполнитель»."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("cargo_requests.id", ondelete="CASCADE"), nullable=False
    )

    # оба участника обязательны: беседа всегда между клиентом и исполнителем.
    # client_id выводится из order.client_id, но храним денормализованно для
    # быстрого доступа к участникам беседы.
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executors.id", ondelete="CASCADE"), nullable=False
    )

    client: Mapped["Client"] = relationship(back_populates="conversations")
    executor: Mapped["Executor"] = relationship(back_populates="conversations")
    order: Mapped["CargoRequest"] = relationship(back_populates="conversations")

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    offers: Mapped[list["Offer"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )

    # непрочитанные = сообщения с id > last_read_id от второй стороны
    client_last_read_id: Mapped[int] = mapped_column(
        default=0, server_default="0", nullable=False
    )
    executor_last_read_id: Mapped[int] = mapped_column(
        default=0, server_default="0", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # денормализация для сортировки списка бесед без джойна к messages
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        # одна беседа на пару «заказ + исполнитель»; executor_id NOT NULL, поэтому
        # ограничение корректно работает (с NULL в Postgres уникальность не держится)
        UniqueConstraint(
            "order_id", "executor_id", name="uq_conversations_order_executor"
        ),
        Index("ix_conversations_client_last_message", "client_id", "last_message_at"),
        Index(
            "ix_conversations_executor_last_message", "executor_id", "last_message_at"
        ),
    )