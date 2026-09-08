from pydantic import BaseModel, EmailStr, Field, ConfigDict
from executor.models.enums.car_brands import CarBrands
from utils.phone_number_validator import BelarusPhoneNumber


class _ExecutorAccountFields(BaseModel):
    """Базовые поля профиля исполнителя.

    Все поля опциональны — обновляются только переданные (exclude_unset).
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone_number: BelarusPhoneNumber | None = None
    is_notifications_enabled: bool | None = None
    image_url: str | None = Field(default=None, alias="image")
    is_active: bool | None = None


class _LegalEntityFields(BaseModel):
    legal_name: str | None = Field(default=None, min_length=1, max_length=255)
    unp: str | None = Field(default=None, min_length=1, max_length=50, alias="UNP")
    address: str | None = Field(default=None, min_length=1, max_length=255)
    brands: list[CarBrands] | None = Field(default=None, min_length=1, max_length=255)


class ExecutorUpdate(_ExecutorAccountFields):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SupplierUpdate(_LegalEntityFields):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ServiceUpdate(_LegalEntityFields):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ProfileUpdateRequest(_ExecutorAccountFields, _LegalEntityFields):
    """Единый payload с фронта — сервис сам решает, какие поля куда применить
    в зависимости от executor.type.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)