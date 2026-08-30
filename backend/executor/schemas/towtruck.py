from pydantic import BaseModel, ConfigDict, Field


class TowTruckBase(BaseModel):
    """Общие поля эвакуатора."""

    legal_name: str = Field(min_length=1, max_length=255)
    unp: str = Field(min_length=1, max_length=50)


class TowTruckCreate(TowTruckBase):
    """Данные для создания профиля эвакуатора (в т.ч. при регистрации)."""


class TowTruckRead(TowTruckBase):
    """Публичные данные эвакуатора."""

    executor_id: int
    is_available_for_work: bool

    model_config = ConfigDict(from_attributes=True)