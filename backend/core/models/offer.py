from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models.enums.actor_types import ActorType
from core.models.enums.offer_statuses import OfferStatus

if TYPE_CHECKING:
    from core.models.chats.conversation import Conversation
    from core.models.chats.message import Message


class Offer(Base):
    """Оффер в беседе и цепочка встречных предложений (торг)."""

    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

    # полиморфный автор: клиент или исполнитель (system запрещён CheckConstraint-ом)
    author_type: Mapped[ActorType] = mapped_column(
        SAEnum(
            ActorType,
            name="offer_author_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    author_client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    author_executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("executors.id", ondelete="SET NULL"), nullable=True
    )

    # цепочка торга: встречное предложение ссылается на предыдущий оффер
    parent_offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("offers.id", ondelete="SET NULL"), nullable=True
    )

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="RUB"
    )
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)  # сроки, описание

    status: Mapped[OfferStatus] = mapped_column(
        SAEnum(
            OfferStatus,
            name="offer_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=OfferStatus.pending,
        server_default=OfferStatus.pending.value,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="offers")
    parent: Mapped["Offer | None"] = relationship(
        back_populates="counter_offers", remote_side="Offer.id"
    )
    counter_offers: Mapped[list["Offer"]] = relationship(back_populates="parent")
    messages: Mapped[list["Message"]] = relationship(back_populates="offer")

    __table_args__ = (
        # автор однозначен: либо клиент, либо исполнитель (system недопустим)
        CheckConstraint(
            "(author_type = 'client'   AND author_client_id IS NOT NULL AND author_executor_id IS NULL) OR "
            "(author_type = 'executor' AND author_executor_id IS NOT NULL AND author_client_id IS NULL)",
            name="ck_offers_author",
        ),
        Index("ix_offers_conversation", "conversation_id"),
        # в беседе не больше одного активного (pending) оффера
        Index(
            "uq_one_pending_offer",
            "conversation_id",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
        # для фонового перевода в 'expired' по истечении expires_at
        Index(
            "ix_offers_pending_expires",
            "expires_at",
            postgresql_where=text("status = 'pending'"),
        ),
    )