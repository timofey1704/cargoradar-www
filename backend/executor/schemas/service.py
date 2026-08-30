from pydantic import BaseModel, ConfigDict, Field

from executor.models.enums.car_brands import CarBrands


class ServiceBase(BaseModel):
    """Общие поля СТО."""

    legal_name: str = Field(min_length=1, max_length=255)
    unp: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1, max_length=255)
    brands: list[CarBrands] = Field(
        default_factory=lambda: [CarBrands.all],
        description="Марки автомобилей, с которыми работает СТО",
    )


class ServiceCreate(ServiceBase):
    """Данные для создания профиля СТО (в т.ч. при регистрации)."""


class ServiceRead(ServiceBase):
    """Публичные данные СТО."""

    executor_id: int

    model_config = ConfigDict(from_attributes=True)