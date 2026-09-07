from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from utils.phone_number_validator import BelarusPhoneNumber


class ClientUpdate(BaseModel):
    """Поля профиля клиента, которые он может изменить самостоятельно.

    Все поля опциональны — обновляются только переданные (exclude_unset).
    """

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone_number: BelarusPhoneNumber | None = None
    image_url: str | None = Field(default=None, max_length=255)
    is_notifications_enabled: bool | None = None
    VIN_code: str | None = Field(default=None, min_length=17, max_length=17)
    
    @model_validator(mode="after")
    def at_least_one_field(self) -> "ClientUpdate":
        if not self.model_fields_set:
            raise ValueError("Нужно передать хотя бы одно поле для обновления")
        return self
    
class LegalClientUpdate(BaseModel):
    """Поля юр. профиля клиента, которые он может изменить самостоятельно.

    Все поля опциональны — обновляются только переданные (exclude_unset).
    """

    model_config = ConfigDict(extra="forbid")

    legal_name: str | None = Field(default=None, min_length=1, max_length=255)
    unp: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "LegalClientUpdate":
        if not self.model_fields_set:
            raise ValueError("Нужно передать хотя бы одно поле для обновления")
        return self
    
class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    email: EmailStr | None = None
    phone_number: BelarusPhoneNumber | None = None
    image_url: str | None = None
    is_notifications_enabled: bool | None = None
    VIN_code: str | None = None

    legal_name: str | None = None
    unp: str | None = None
    address: str | None = None