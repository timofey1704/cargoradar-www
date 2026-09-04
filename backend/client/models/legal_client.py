from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from client.models.client import Client
    
class LegalClient(Base):
    __tablename__ = "legal_clients"

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        primary_key=True,
    )

    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unp: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    client: Mapped["Client"] = relationship(
        back_populates="legal_client"
    )