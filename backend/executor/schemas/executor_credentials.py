from pydantic import EmailStr, Field, model_validator

from core.schemas.common_auth_credentials import CommonCredentialsFields

from executor.models.enums.executor_types import ExecutorTypes
from executor.schemas.service import ServiceCreate
from executor.schemas.supplier import SupplierCreate
from executor.schemas.towtruck import TowTruckCreate
from executor.schemas.vehicle import VehicleCreate

# какой профиль ожидается для каждого типа аккаунта
_EXECUTOR_PROFILE_FIELDS: dict[ExecutorTypes, str] = {
    ExecutorTypes.carrier: "cars",
    ExecutorTypes.service: "service",
    ExecutorTypes.supplier: "supplier",
    ExecutorTypes.towtruck: "towtruck",
}

class ExecutorRegister(CommonCredentialsFields):
    """Поля для регистрации исполнителя"""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    type: ExecutorTypes
    price_per_km: int | None = Field(default=None, ge=0)
    privacy_accepted: bool = Field(default=True, description="Принятие политики конфиденциальности")

    # профиль, соответствующий типу аккаунта
    cars: list[VehicleCreate] | None = Field(
        default=None, min_length=1, description="Транспорт перевозчика (carrier)"
    )
    service: ServiceCreate | None = None   # service (СТО)
    supplier: SupplierCreate | None = None  # supplier
    towtruck: TowTruckCreate | None = None  # towtruck

    @model_validator(mode="after")
    def _check_profile_for_type(self) -> "ExecutorRegister":
        """Профиль обязателен и должен соответствовать типу аккаунта."""
        expected_field = _EXECUTOR_PROFILE_FIELDS[self.type]

        present_fields = [
            field
            for field in _EXECUTOR_PROFILE_FIELDS.values()
            if getattr(self, field) is not None
        ]

        if expected_field not in present_fields:
            raise ValueError(
                f"Для типа аккаунта {self.type.value!r} нужно передать поле {expected_field!r}"
            )
        if len(present_fields) > 1:
            raise ValueError(
                "Можно передать только один профиль, соответствующий типу аккаунта"
            )
        return self
