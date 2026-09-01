from pydantic import BaseModel, ConfigDict, Field

from executor.models.enums.car_brands import CarBrands
from executor.models.enums.vehicle_types import CarTypes, VehicleTypes


class VehicleBase(BaseModel):
    """Общие поля транспорта исполнителя."""

    type: VehicleTypes = Field(
        default=VehicleTypes.truck,
        description=(
            "Тип транспорта. В БД поле обязательное, но форма регистрации "
            "перевозчика пока его не собирает — по умолчанию грузовик."
        ),
    )
    brand: CarBrands
    model: str = Field(min_length=1, max_length=255)
    cargo_capacity: int = Field(gt=0, description="Грузоподъёмность, кг")
    volume_capacity: int | None = Field(default=None, gt=0, description="Объём, м³")
    car_type: CarTypes | None = None  # тип кузова
    license_plate: str = Field(min_length=1, max_length=10)
    manufacture_year: int = Field(ge=1960, le=2026)
    photo_url: str | None = Field(default=None, max_length=255)
    VIN: str | None = Field(default=None, min_length=1, max_length=17)


class VehicleCreate(VehicleBase):
    """Данные для создания/сохранения транспорта (в т.ч. при регистрации)."""


class VehicleRead(VehicleBase):
    """Публичные данные транспорта исполнителя."""

    id: int
    executor_id: int

    model_config = ConfigDict(from_attributes=True)