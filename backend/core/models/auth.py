from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models.oauth_providers import OAuthProvider

if TYPE_CHECKING:
    from executor.models.executor import Executor
    from client.models.client import Client


class OAuthAccount(Base):
    """Связь аккаунта (клиента или исполнителя) с OAuth-провайдером (Apple/Google)."""

    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id"), index=True, nullable=True
    )
    executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("executors.id"), index=True, nullable=True
    )
    provider: Mapped[OAuthProvider] = mapped_column(String(20))
    provider_user_id: Mapped[str] = mapped_column(String(255), index=True)  # apple, google
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="oauth_accounts")
    executor: Mapped["Executor"] = relationship(back_populates="oauth_accounts")

    __table_args__ = (
        # клиент и исполнитель — независимые аккаунты: один и тот же человек может
        # войти через один провайдер и как клиент, и как исполнитель, поэтому
        # уникальность (provider, provider_user_id) держим раздельно — по владельцу.
        # но один и тот же аккаунт не может дважды привязать один и тот же провайдер
        Index(
            "uq_oauth_client_provider",
            "provider",
            "provider_user_id",
            unique=True,
            postgresql_where=text("client_id IS NOT NULL"),
        ),
        Index(
            "uq_oauth_executor_provider",
            "provider",
            "provider_user_id",
            unique=True,
            postgresql_where=text("executor_id IS NOT NULL"),
        ),
        # аккаунт привязан ровно к одному владельцу: либо клиент, либо исполнитель
        CheckConstraint(
            "(client_id IS NULL) <> (executor_id IS NULL)",
            name="ck_oauth_accounts_one_owner",
        ),
    )


class RefreshToken(Base):
    """
    Храним не сам JWT, а его jti (уникальный идентификатор) — этого достаточно
    для отзыва/ротации, а сам токен подписан и самодостаточен для верификации подписи.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), index=True, nullable=True
    )
    executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("executors.id", ondelete="CASCADE"), index=True, nullable=True
    )
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # при ротации: старый токен помечается revoked_at + ссылкой на новый
    # если кто-то попробует переиспользовать отозванный refresh — это сигнал компрометации
    replaced_by_jti: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped["Client"] = relationship(back_populates="refresh_tokens")
    executor: Mapped["Executor"] = relationship(back_populates="refresh_tokens")

    __table_args__ = (
        # токен принадлежит ровно одному аккаунту: либо клиент, либо исполнитель
        CheckConstraint(
            "(client_id IS NULL) <> (executor_id IS NULL)",
            name="ck_refresh_tokens_one_owner",
        ),
    )

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None