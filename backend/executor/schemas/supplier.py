from pydantic import BaseModel, ConfigDict, Field

from executor.models.enums.car_brands import CarBrands
from executor.schemas.mixins import BrandsFromORMMixin


class SupplierBase(BrandsFromORMMixin, BaseModel):
    """Общие поля поставщика запчастей."""

    legal_name: str = Field(min_length=1, max_length=255)
    unp: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1, max_length=255)
    brands: list[CarBrands] = Field(
        default_factory=lambda: [CarBrands.all],
        description="Марки автомобилей, с которыми работает поставщик",
    )


class SupplierCreate(SupplierBase):
    """Данные для создания профиля поставщика (в т.ч. при регистрации)."""


class SupplierRead(SupplierBase):
    """Публичные данные поставщика."""

    executor_id: int

    model_config = ConfigDict(from_attributes=True)