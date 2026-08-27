from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.executor import Executor
    
class TowTruck(Base):
    __tablename__ = "tow_trucks"

    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executors.id"),
        primary_key=True,
    )

    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    unp: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
    
    # address: Mapped[str] = mapped_column(String(255), nullable=False)
    
    is_available_for_work: Mapped[bool] = mapped_column(nullable=False, default=True)

    executor: Mapped["Executor"] = relationship(
        back_populates="service"
    )