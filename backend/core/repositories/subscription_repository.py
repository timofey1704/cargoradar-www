from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.membership import Membership, Subscription, SubscriptionSource, SubscriptionStatus


class SubscriptionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, subscription_id: int) -> Subscription | None:
        result = await self.db.execute(select(Subscription).where(Subscription.id == subscription_id))
        return result.scalar_one_or_none()

    async def get_active_for_client(self, client_id: int) -> Subscription | None:
        result = await self.db.execute(
            select(Subscription)
            .options(
                selectinload(Subscription.membership).selectinload(Membership.features)
            )
            .where(
                Subscription.client_id == client_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_for_executor(self, executor_id: int) -> Subscription | None:
        result = await self.db.execute(
            select(Subscription)
            .options(
                selectinload(Subscription.membership).selectinload(Membership.features)
            )
            .where(
                Subscription.executor_id == executor_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
        return result.scalar_one_or_none()

    async def grant_trial_to_client(self, client_id: int, membership_id: int, days: int = 30) -> Subscription:
        return await self._grant_trial(client_id=client_id, executor_id=None, membership_id=membership_id, days=days)

    async def grant_trial_to_executor(self, executor_id: int, membership_id: int, days: int = 30) -> Subscription:
        return await self._grant_trial(client_id=None, executor_id=executor_id, membership_id=membership_id, days=days)

    async def _grant_trial(
        self,
        client_id: int | None,
        executor_id: int | None,
        membership_id: int,
        days: int,
    ) -> Subscription:
        now = datetime.now(timezone.utc)
        subscription = Subscription(
            client_id=client_id,
            executor_id=executor_id,
            membership_id=membership_id,
            status=SubscriptionStatus.ACTIVE,
            source=SubscriptionSource.TRIAL_GRANT,
            auto_renewal=False,
            subscription_start=now,
            subscription_end=now + timedelta(days=days),
        )
        self.db.add(subscription)
        await self.db.flush()
        return subscription