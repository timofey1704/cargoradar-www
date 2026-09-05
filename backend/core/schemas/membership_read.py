from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.models.enums.subscription_statuses import SubscriptionStatus


class MembershipRead(BaseModel):
    """Тариф, на который оформлена подписка."""

    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class SubscriptionRead(BaseModel):
    """Активная подписка клиента."""

    id: int
    status: SubscriptionStatus
    subscription_start: datetime
    subscription_end: datetime
    auto_renewal: bool
    membership: MembershipRead

    model_config = ConfigDict(from_attributes=True)