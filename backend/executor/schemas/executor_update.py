from pydantic import BaseModel, EmailStr, Field

from utils.phone_number_validator import BelarusPhoneNumber


class ExecutorUpdate(BaseModel):
    """Поля профиля исполнителя, которые он может изменить самостоятельно.

    Все поля опциональны — обновляются только переданные.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone_number: BelarusPhoneNumber | None = None
    is_notifications_enabled: bool | None = None