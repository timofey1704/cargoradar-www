from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Boolean, String, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from core.database import Base

from models.oauth_accounts import OAuthAccount
from executor.models.enums.executor_types import ExecutorTypes

if TYPE_CHECKING:
    from models.refresh_token import RefreshToken

class Executor(Base):
    __tablename__ = "executors"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ExecutorTypes] = mapped_column(
        SQLEnum(ExecutorTypes),
        nullable=False,
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    price_per_km: Mapped[int] = mapped_column(Integer, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)  # null потому что может быть социальный логин
    
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="executor", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="executor", cascade="all, delete-orphan")
    
    is_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)