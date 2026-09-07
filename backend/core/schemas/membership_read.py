from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

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


class FeatureRead(BaseModel):
    """Фича, входящая в тарифный план."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MembershipPlanRead(BaseModel):
    """Тарифный план из каталога — со списком фич."""

    id: int
    name: str
    description: str
    price: Decimal
    is_popular: bool
    is_available: bool
    is_trial: bool
    features: list[FeatureRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SubscriptionRemainingRead(BaseModel):
    """Данные для клиента/исполнителя: активная подписка, остаток дней и каталог планов."""

    subscription: SubscriptionRead | None = None
    days_left: int | None = None
    plans: list[MembershipPlanRead] = Field(default_factory=list)