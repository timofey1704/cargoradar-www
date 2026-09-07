from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from core.models.enums.support_statuses import RequestStatuses, SupportRequestTypes

class SupportRequestRead(BaseModel):
    """Данные по запросам пользователя в поддержку"""
    
    id: int
    title: str
    description: str
    status: RequestStatuses
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class SupportRequestCreate(BaseModel):
    """Данные для создания заявки в поддержку от клиента/исполнителя"""

    request_type: SupportRequestTypes
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)