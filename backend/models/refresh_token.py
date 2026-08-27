from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.client import Client

class RefreshToken(Base):
    """
    Храним не сам JWT, а его jti (уникальный идентификатор) — этого достаточно
    для отзыва/ротации, а сам токен подписан и самодостаточен для верификации подписи.
    """
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    executor_id: Mapped[int] = mapped_column(ForeignKey("executors.id", ondelete="CASCADE"), index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # при ротации: старый токен помечается revoked_at + ссылкой на новый
    # если кто-то попробует переиспользовать отозванный refresh — это сигнал компрометации
    replaced_by_jti: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped["Client"] = relationship(back_populates="refresh_tokens")

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None