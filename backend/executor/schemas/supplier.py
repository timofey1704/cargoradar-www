from pydantic import BaseModel, ConfigDict, Field


class SupplierBase(BaseModel):
    """Общие поля поставщика запчастей."""

    legal_name: str = Field(min_length=1, max_length=255)
    unp: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1, max_length=255)


class SupplierCreate(SupplierBase):
    """Данные для создания профиля поставщика (в т.ч. при регистрации)."""


class SupplierRead(SupplierBase):
    """Публичные данные поставщика."""

    executor_id: int

    model_config = ConfigDict(from_attributes=True)