from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from core.database import Base

from executor.models.enums.car_brands import CarBrands

if TYPE_CHECKING:
    from executor.models.executor import Executor

class Service(Base):
    __tablename__ = "services"

    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executors.id"),
        primary_key=True,
    )

    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unp: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    brands: Mapped[list["ServiceBrand"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
    )
    executor: Mapped["Executor"] = relationship(back_populates="service")
    
class ServiceBrand(Base):
    __tablename__ = "service_brands"

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.executor_id"),
        primary_key=True,
    )
    brand: Mapped[CarBrands] = mapped_column(SQLEnum(CarBrands), primary_key=True)

    service: Mapped["Service"] = relationship(back_populates="brands")