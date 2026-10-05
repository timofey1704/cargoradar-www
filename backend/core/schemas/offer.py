from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from core.models.enums.offer_statuses import OfferStatus


class OfferCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    terms: str | None = Field(default=None, max_length=2000)


class OfferRead(BaseModel):
    id: int
    conversation_id: int
    price: Decimal
    currency: str
    terms: str | None
    status: OfferStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)