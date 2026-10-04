"""Схемы заявок клиента на перевозку (CargoRequest): чтение, создание, правка, удаление.

Геометрия PostGIS через API не ходит: точки передаются парой `latitude`/`longitude`
(фронт шлёт их как объект точки маршрута), а в колонки модели `Geometry` их
превращает сервис. Read-схема поэтому содержит только адреса — как и
core.schemas.search.request.CargoRequestRead, который отдаёт ленту поиска.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from client.models.enums.request_statuses import CargoRequestStatus
from core.schemas.search.page import PageRead
from utils.address_formatter import FormattedAddress


class CargoRequestLocation(BaseModel):
    """Координаты точки маршрута в WGS84.

    В БД (PostGIS, SRID 4326) точка хранится в порядке (lng lat) — этот же
    порядок использует сервис при сборке WKT.
    """

    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90, description="Широта, градусы")
    longitude: float = Field(ge=-180, le=180, description="Долгота, градусы")


class CargoRequestCreate(BaseModel):
    """Тело запроса на создание заявки (маршрут + груз + условия)."""

    model_config = ConfigDict(extra="forbid")

    origin_address: str = Field(min_length=1, max_length=500)
    origin_location: CargoRequestLocation

    destination_address: str = Field(min_length=1, max_length=500)
    destination_location: CargoRequestLocation

    cargo_type: str = Field(min_length=1, max_length=100)
    weight_kg: float = Field(gt=0, description="Вес груза, кг")
    volume_m3: float | None = Field(default=None, gt=0, description="Объём груза, м³")
    vehicle_type: str | None = Field(default=None, max_length=100)

    loading_date: date
    budget: float | None = Field(default=None, ge=0, description="Бюджет")
    comment: str | None = Field(default=None, description="Комментарий клиента")


# Поля модели, которые в БД объявлены NOT NULL: явный null для них отклоняем,
# иначе PATCH упал бы IntegrityError вместо понятной 422.
_NON_NULLABLE_FIELDS = (
    "origin_address",
    "origin_location",
    "destination_address",
    "destination_location",
    "cargo_type",
    "weight_kg",
    "loading_date",
)


class CargoRequestUpdate(BaseModel):
    """Поля заявки, которые владелец может изменить.

    Все поля опциональны — применяются только переданные (`exclude_unset`).
    `volume_m3`, `vehicle_type`, `budget` и `comment` можно очистить, передав null;
    обязательные колонки (адреса, координаты, груз, дата загрузки) — нельзя.
    """

    model_config = ConfigDict(extra="forbid")

    origin_address: str | None = Field(default=None, min_length=1, max_length=500)
    origin_location: CargoRequestLocation | None = None

    destination_address: str | None = Field(default=None, min_length=1, max_length=500)
    destination_location: CargoRequestLocation | None = None

    cargo_type: str | None = Field(default=None, min_length=1, max_length=100)
    weight_kg: float | None = Field(default=None, gt=0)
    volume_m3: float | None = Field(default=None, gt=0)
    vehicle_type: str | None = Field(default=None, max_length=100)

    loading_date: date | None = None
    budget: float | None = Field(default=None, ge=0)
    comment: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> CargoRequestUpdate:
        if not self.model_fields_set:
            raise ValueError("Нужно передать хотя бы одно поле для обновления")

        for field in _NON_NULLABLE_FIELDS:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"Поле '{field}' не может быть null")
        return self


class CargoRequestRead(BaseModel):
    """Заявка глазами владельца. Геометрия (PostGIS) наружу не отдаётся."""

    id: int
    client_id: int
    status: CargoRequestStatus

    origin_address: FormattedAddress
    destination_address: FormattedAddress

    cargo_type: str
    weight_kg: float
    volume_m3: float | None = None
    vehicle_type: str | None = None

    loading_date: date
    budget: float | None = None
    comment: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


CargoRequestPageRead = PageRead[CargoRequestRead]


class CargoRequestDeleted(BaseModel):
    """Ответ на мягкое удаление заявки (`is_deleted=True`)."""

    id: int
    status: CargoRequestStatus
    is_deleted: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

