from pydantic import BaseModel, Field

from utils.phone_number_validator import BelarusPhoneNumber

class CommonCredentialsFields(BaseModel):
    """Общие поля для регистрации и логина"""

    phone_number: BelarusPhoneNumber
    password: str = Field(min_length=8, max_length=72)