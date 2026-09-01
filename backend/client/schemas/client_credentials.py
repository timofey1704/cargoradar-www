from pydantic import BaseModel, EmailStr, Field

from core.schemas.common_auth_credentials import CommonCredentialsFields
class ClientRegister(CommonCredentialsFields):
    """Поля для регистрации клиента"""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    VIN_code: str | None = Field(default=None, min_length=17, max_length=17)
    privacy_accepted: bool = Field(default=True, description="Принятие политики конфиденциальности")
