from sqlalchemy.ext.asyncio import AsyncSession

from core.repositories.search.route import RouteRepository
from core.schemas.search.route import RoutePageRead, RouteRead
from core.services.search.common import DEFAULT_PAGE_LIMIT, build_page, search_cached


class RouteService:
    """Маршруты водителей: поиск по исполнителю."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = RouteRepository(db)

    @search_cached("search:route")
    async def get_by_executor(
        self, executor_id: int, *, skip: int = 0, limit: int = DEFAULT_PAGE_LIMIT
    ) -> RoutePageRead:
        """Маршруты одного водителя (кешируем в Redis)."""
        routes = await self.repository.get_by_executor(
            executor_id, skip=skip, limit=limit
        )
        return build_page(
            [RouteRead.model_validate(route) for route in routes],
            skip=skip,
            limit=limit,
        )

