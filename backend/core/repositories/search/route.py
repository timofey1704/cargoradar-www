from __future__ import annotations

from typing import Sequence

from sqlalchemy import select

from core.repositories.search.base import BaseRepository
from executor.models.route import Route


class RouteRepository(BaseRepository[Route]):
    """Репозиторий маршрутов (Route), которые создают водители (исполнители)."""

    model = Route

    async def get_by_executor(
        self, executor_id: int, *, skip: int = 0, limit: int = 20
    ) -> Sequence[Route]:
        stmt = (
            select(Route)
            .where(Route.executor_id == executor_id, Route.is_deleted.is_(False))
            .order_by(Route.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()