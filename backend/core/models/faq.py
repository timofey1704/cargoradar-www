from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from admin.models.admin import Admin

class FAQ(Base):
    __tablename__ = "faqs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("admins.id"), index=True)
    updated_by: Mapped["Admin| None"] = relationship(back_populates="faqs")

    def __repr__(self) -> str:
        return f"<FAQ (id={self.id}, title={self.title})>"