from pydantic import BaseModel, ConfigDict, EmailStr

from executor.models.enums.executor_types import ExecutorTypes
from utils.phone_number_validator import BelarusPhoneNumber
from core.schemas.membership_read import SubscriptionRead


class ExecutorRead(BaseModel):
    """Публичные данные исполнителя, безопасные для отдачи клиенту"""

    id: int
    name: str
    email: EmailStr
    phone_number: BelarusPhoneNumber
    type: ExecutorTypes
    image_url: str | None
    is_notifications_enabled: bool
    is_active: bool
    subscription: SubscriptionRead | None

    model_config = ConfigDict(from_attributes=True)