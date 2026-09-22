from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import Boolean, String, DateTime, func, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from executor.models.executor import Executor

class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)

    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    executor: Mapped["Executor"] = relationship(back_populates="routes")

    # адреса точек маршрута — текстовое представление, которое видит пользователь
    point_a: Mapped[str] = mapped_column(String(255), nullable=False)
    point_b: Mapped[str] = mapped_column(String(255), nullable=False)

    # координаты точек маршрута в PostGIS (WGS84 / EPSG:4326, порядок lng, lat).
    # spatial_index=True — для колонок создаётся GiST-индекс
    # (idx_routes_point_a_location / idx_routes_point_b_location).
    point_a_location: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )
    point_b_location: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    price: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)