from pydantic import BaseModel, ConfigDict, EmailStr

from utils.phone_number_validator import BelarusPhoneNumber
from client.models.enums.client_types import ClientTypes


class ClientRead(BaseModel):
    """Публичные данные клиента, безопасные для отдачи на фронт"""

    id: int
    name: str
    email: EmailStr
    phone_number: BelarusPhoneNumber
    type: ClientTypes
    VIN_code: str | None
    image_url: str | None
    is_notifications_enabled: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)