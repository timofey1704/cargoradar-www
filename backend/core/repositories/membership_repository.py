from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.membership import Membership


class MembershipRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, membership_id: int) -> Membership | None:
        result = await self.db.execute(select(Membership).where(Membership.id == membership_id))
        return result.scalar_one_or_none()

    async def get_trial_plan(self) -> Membership | None:
        result = await self.db.execute(select(Membership).where(Membership.is_trial.is_(True)))
        return result.scalar_one_or_none()

    async def get_available(self) -> list[Membership]:
        result = await self.db.execute(
            select(Membership).where(Membership.is_available.is_(True)).order_by(Membership.price)
        )
        return list(result.scalars().all())

    async def get_with_features(self, membership_id: int) -> Membership | None:
        result = await self.db.execute(
            select(Membership)
            .options(selectinload(Membership.features))
            .where(Membership.id == membership_id)
        )
        return result.scalar_one_or_none()