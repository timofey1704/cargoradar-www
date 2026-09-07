# executor/schemas/executor_read.py
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from executor.models.enums.executor_types import ExecutorTypes
from executor.schemas.vehicle import VehicleRead
from executor.schemas.service import ServiceRead
from executor.schemas.supplier import SupplierRead
from utils.phone_number_validator import BelarusPhoneNumber
from core.schemas.membership_read import SubscriptionRead


class ExecutorBase(BaseModel):
    """Общие поля исполнителя, безопасные для отдачи клиенту"""

    id: int
    name: str
    email: EmailStr
    phone_number: BelarusPhoneNumber
    image_url: str | None
    is_notifications_enabled: bool
    is_active: bool
    subscription: SubscriptionRead | None

    model_config = ConfigDict(from_attributes=True)


class CarrierRead(ExecutorBase):
    type: Literal[ExecutorTypes.carrier]
    cars: list[VehicleRead]


class ServiceExecutorRead(ExecutorBase):
    type: Literal[ExecutorTypes.service]
    service: ServiceRead


class SupplierExecutorRead(ExecutorBase):
    type: Literal[ExecutorTypes.supplier]
    supplier: SupplierRead


class TowTruckExecutorRead(ExecutorBase):
    type: Literal[ExecutorTypes.towtruck]


ExecutorRead = Annotated[
    Union[CarrierRead, ServiceExecutorRead, SupplierExecutorRead, TowTruckExecutorRead],
    Field(discriminator="type"),
]