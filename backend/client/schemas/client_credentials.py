from pydantic import EmailStr, Field, model_validator

from core.schemas.common_auth_credentials import CommonCredentialsFields

from client.models.enums.client_types import ClientTypes


class ClientRegister(CommonCredentialsFields):
    """Поля для регистрации клиента"""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    type: ClientTypes  # individual (физ лицо) | legal (юр лицо)
    VIN_code: str | None = Field(default=None, min_length=17, max_length=17)
    privacy_accepted: bool = Field(default=True, description="Принятие политики конфиденциальности")

    # поля профиля юридического лица — обязательны только при type=legal
    legal_name: str | None = Field(default=None, min_length=1, max_length=255)
    UNP: str | None = Field(default=None, min_length=9, max_length=9, description="УНП юр. лица (9 символов)")
    address: str | None = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def _check_legal_profile(self) -> "ClientRegister":
        """Для type=legal профиль юридического лица обязателен."""
        if self.type is ClientTypes.legal:
            if not (self.legal_name and self.UNP and self.address):
                raise ValueError(
                    "Для типа аккаунта 'legal' обязательны поля legal_name, UNP и address"
                )
        return self
