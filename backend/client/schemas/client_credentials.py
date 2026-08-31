from pydantic import BaseModel, EmailStr, Field

from core.schemas.common_auth_credentials import CommonCredentialsFields


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class RefreshRequest(BaseModel):
    refresh_token: str
    
class ClientRegister(CommonCredentialsFields):
    """Поля для регистрации клиента"""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    VIN_code: str = Field(max_length=17, min_length=17)
