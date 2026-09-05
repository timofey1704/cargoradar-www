from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from core.database import Base
from core.models.enums.subscription_statuses import SubscriptionStatus, SubscriptionSource

if TYPE_CHECKING:
    from executor.models.executor import Executor
    from client.models.client import Client


class Membership(Base):
    """Каталог тарифов — что доступно к покупке. Не хранит ничьего владения."""

    __tablename__ = "memberships"
    __table_args__ = (
        CheckConstraint(
            "NOT (is_trial IS TRUE AND is_available IS TRUE)",
            name="ck_membership_trial_not_available",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    is_popular: Mapped[bool] = mapped_column(default=False)
    is_available: Mapped[bool] = mapped_column(default=True)
    is_trial: Mapped[bool] = mapped_column(default=False)

    features: Mapped[list["Feature"]] = relationship(back_populates="membership")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="membership")


class Feature(Base):
    """Функции, входящие в тариф."""

    __tablename__ = "features"

    id: Mapped[int] = mapped_column(primary_key=True)
    membership_id: Mapped[int] = mapped_column(
        ForeignKey("memberships.id"), index=True, nullable=False
    )
    membership: Mapped["Membership"] = relationship(back_populates="features")

    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Subscription(Base):
    """Факт владения тарифом конкретным клиентом/исполнителем."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint(
            "(client_id IS NOT NULL AND executor_id IS NULL) "
            "OR (client_id IS NULL AND executor_id IS NOT NULL)",
            name="ck_subscription_owner_xor",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), index=True)
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("executors.id"), index=True)
    membership_id: Mapped[int] = mapped_column(
        ForeignKey("memberships.id"), index=True, nullable=False
    )

    client: Mapped["Client | None"] = relationship(back_populates="subscriptions")
    executor: Mapped["Executor | None"] = relationship(back_populates="subscriptions")
    membership: Mapped["Membership"] = relationship(back_populates="subscriptions")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="subscription")

    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus),default=SubscriptionStatus.ACTIVE,
        nullable=False,
    )
    source: Mapped[SubscriptionSource] = mapped_column(
        SQLEnum(SubscriptionSource),default=SubscriptionSource.PURCHASE,
        nullable=False,
    )
    
    auto_renewal: Mapped[bool] = mapped_column(default=False)
    subscription_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    subscription_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    suspended_reason: Mapped[str | None] = mapped_column(String(255))  # почему заблокировали, для саппорта/логов
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Transaction(Base):
    """История платежей за подписку."""

    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("request_id", name="uq_transactions_request_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id"), index=True, nullable=False
    )
    subscription: Mapped["Subscription"] = relationship(back_populates="transactions")

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False)
    request_id: Mapped[str] = mapped_column(String(255), nullable=False)
    bepaid_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())