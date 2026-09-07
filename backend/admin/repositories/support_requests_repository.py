from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.support_request import SupportRequest
from core.models.enums.support_statuses import RequestStatuses


class AdminSupportRequestRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_requests(
        self,
        status: RequestStatuses | None = None,
        limit: int | None = 50,
        offset: int = 0,
    ) -> list[SupportRequest]:
        """Все заявки, опционально отфильтрованные по статусу, с пагинацией"""
        query = select(SupportRequest).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        if status is not None:
            query = query.where(SupportRequest.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, request_id: int) -> SupportRequest | None:
        return await self.db.get(SupportRequest, request_id)

    async def assign(self, request_id: int, admin_id: int) -> SupportRequest | None:
        """Назначить админа на заявку. Возвращает None, если заявка не найдена
        или уже назначена другому админу. Статус не меняет"""
        request = await self.get_by_id(request_id)
        if request is None or request.admin_id is not None:
            return None
        request.admin_id = admin_id
        await self.db.flush()
        return request

    async def change_status(
        self,
        request_id: int,
        status: RequestStatuses,
    ) -> SupportRequest | None:
        """Сменить статус заявки. Возвращает None, если заявка не найдена"""
        request = await self.get_by_id(request_id)
        if request is None:
            return None
        request.status = status
        if status in (
            RequestStatuses.RESOLVED,
            RequestStatuses.REJECTED,
        ):
            request.closed_at = func.now()
        await self.db.flush()
        return request