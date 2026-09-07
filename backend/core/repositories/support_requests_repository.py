from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.support_request import SupportRequest
from core.models.enums.support_statuses import SupportRequestTypes


class BaseSupportRequestRepository:
    """Общая логика работы с заявками поддержки.
    Наследники обязаны передавать owner_field и owner_id.
    """

    owner_field: str  # "client_id" | "executor_id" — задаётся в наследнике

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_requests_by_id(self, owner_id: int) -> list[SupportRequest]:
        """Получить все заявки конкретного владельца."""
        result = await self.db.execute(
            select(SupportRequest).where(
                getattr(SupportRequest, self.owner_field) == owner_id
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        owner_id: int,
        request_type: SupportRequestTypes,
        title: str,
        description: str,
    ) -> SupportRequest:
        request = SupportRequest(
            request_type=request_type,
            title=title,
            description=description,
            **{self.owner_field: owner_id},
        )
        self.db.add(request)
        await self.db.flush()
        return request