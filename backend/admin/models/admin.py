from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Boolean, String, DateTime, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from admin.models.enums.admin_types import AdminTypes

if TYPE_CHECKING:
    from core.models.support_request import SupportRequest


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    surname: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    type: Mapped[AdminTypes] = mapped_column(
        SQLEnum(AdminTypes),
        nullable=False,
        default=AdminTypes.support
    )
    
    support_requests: Mapped[list["SupportRequest"]] = relationship(back_populates="admin")
    
    def __repr__(self) -> str:
        return f"<Admin (id={self.id}, email={self.email})>"