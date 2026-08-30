from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Integer, SmallInteger, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from core.database import Base
from executor.models.enums.car_brands import CarBrands
from executor.models.enums.vehicle_types import CarTypes, VehicleTypes

if TYPE_CHECKING:
    from executor.models.executor import Executor

class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    executor: Mapped["Executor"] = relationship(
        back_populates="vehicles"
    )

    type: Mapped[VehicleTypes] = mapped_column(
        SQLEnum(VehicleTypes),
        nullable=False,
    )
    brand: Mapped[CarBrands] = mapped_column(
        SQLEnum(CarBrands),
        nullable=False,
    )
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo_capacity: Mapped[int] = mapped_column(Integer, nullable=False) # в килограммах
    volume_capacity: Mapped[int] = mapped_column(Integer, nullable=True) # m3
    car_type: Mapped[CarTypes] = mapped_column(
        SQLEnum(CarTypes),
        nullable=True
    ) # тип кузова
    license_plate: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    manufacture_year: Mapped[int] = mapped_column(
    SmallInteger,
    nullable=False,
)
    photo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    VIN: Mapped[str] = mapped_column(String(17), nullable=True, unique=True)
    
    __table_args__ = (
        CheckConstraint(
            "manufacture_year >= 1960 AND manufacture_year <= 2026",
            name="ck_vehicle_manufacture_year",
        ),
    )
    