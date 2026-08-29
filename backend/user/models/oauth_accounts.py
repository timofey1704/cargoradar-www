from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

from executor.models.enums.oauth_providers import OAuthProvider

if TYPE_CHECKING:
    from user.models.client import Client

class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    executor_id: Mapped[int] = mapped_column(ForeignKey("executors.id"), index=True)
    provider: Mapped[OAuthProvider] = mapped_column(String(20))
    provider_user_id: Mapped[str] = mapped_column(String(255), index=True)  # apple, google
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="oauth_accounts")

    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_account"),
    )