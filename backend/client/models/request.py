from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement

from sqlalchemy import (
    Boolean, String, DateTime, Date, func, ForeignKey, Text,
    Float, Enum as SAEnum, Index, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

from client.models.enums.request_statuses import CargoRequestStatus

if TYPE_CHECKING:
    from client.models.client import Client
    from core.models.chats.conversation import Conversation


class CargoRequest(Base):
    __tablename__ = "cargo_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    client: Mapped["Client"] = relationship(back_populates="cargo_requests")
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    # маршрут — текст для пользователя + геометрия для поиска
    origin_address: Mapped[str] = mapped_column(String(500))
    origin_location: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    destination_address: Mapped[str] = mapped_column(String(500))
    destination_location: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    # груз
    cargo_type: Mapped[str] = mapped_column(String(100))
    weight_kg: Mapped[float] = mapped_column(Float)
    volume_m3: Mapped[float | None] = mapped_column(Float, nullable=True)
    vehicle_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # условия
    loading_date: Mapped[date] = mapped_column(Date)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[CargoRequestStatus] = mapped_column(
        SAEnum(
            CargoRequestStatus,
            name="cargo_request_status",
            # Без values_callable SQLAlchemy пишет в БД имена членов ('NEW'),
            # а server_default/частичный индекс ниже используют значения ('new').
            values_callable=lambda x: [e.value for e in x],
        ),
        default=CargoRequestStatus.NEW,
        server_default=CargoRequestStatus.NEW.value,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    __table_args__ = (
        Index(
            "ix_cargo_requests_feed",
            "status", "created_at",
            postgresql_where=text("NOT is_deleted"),
        ),
        Index(
            "ix_cargo_requests_client_created",
            "client_id", "created_at",
            postgresql_where=text("NOT is_deleted"),
        ),
        Index(
            "ix_cargo_requests_loading_date",
            "loading_date",
            postgresql_where=text("NOT is_deleted AND status = 'new'"),
        ),
    )