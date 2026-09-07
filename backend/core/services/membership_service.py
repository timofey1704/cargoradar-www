from datetime import datetime, timezone
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.repositories.membership_repository import MembershipRepository
from core.repositories.subscription_repository import SubscriptionRepository
from core.schemas.membership_read import (
    MembershipPlanRead,
    SubscriptionRead,
    SubscriptionRemainingRead,
)

class MembershipService:

    """Каталог тарифов и данные о подписке клиента/исполнителя."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_plans(self) -> list[MembershipPlanRead]:
        """Все доступные к покупке тарифные планы со списком фич."""
        repo = MembershipRepository(self.db)
        plans = await repo.get_available_with_features()
        return [MembershipPlanRead.model_validate(plan) for plan in plans]

    async def get_subscription_info(
        self,
        client_id: int | None = None,
        executor_id: int | None = None,
    ) -> SubscriptionRemainingRead:
        """Универсальный метод: отдаёт активную подписку (и триал тоже) с остатком дней и каталог планов.

        Передаётся ровно один идентификатор—в зависимости от типа аккаунта юзера (client_id для клиента, executor_id для исполнителя).
        """
        if (client_id is None) == (executor_id is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Должен быть передан ровно один идентификатор: client_id или executor_id",
            )

        subscription_repo = SubscriptionRepository(self.db)
        if client_id is not None:
            subscription = await subscription_repo.get_active_for_client(client_id)
        else:
            # после XOR-проверки выше executor_id гарантированно задан
            assert executor_id is not None
            subscription = await subscription_repo.get_active_for_executor(executor_id)

        days_left = None
        if subscription is not None:
            days_left = self._days_left(subscription.subscription_end)

        return SubscriptionRemainingRead(
            subscription=SubscriptionRead.model_validate(subscription) if subscription else None,
            days_left=days_left,
            plans=await self.get_plans(),
        )

    @staticmethod
    def _days_left(subscription_end: datetime) -> int:
        """Полные дни до окончания подписки (округление вверх: последний день считается за 1).
        
        Возвращает 0, если срок уже истёк или истекает прямо сейчас.
        """
        end = subscription_end
        if end.tzinfo is None:
            # может вернуться naive datetime — приводим к UTC для корректного вычитания
            end = end.replace(tzinfo=timezone.utc)
        
        remaining = end - datetime.now(timezone.utc)
        if remaining.total_seconds() <= 0:
            return 0
        return ceil(remaining.total_seconds() / 86400)