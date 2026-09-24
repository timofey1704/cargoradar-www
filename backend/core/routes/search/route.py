"""Роуты поиска маршрутов водителей (Route)."""

from fastapi import APIRouter, status

from core.dependencies import DbSession
from core.schemas.search.route import RoutePageRead
from core.services.search.common import DEFAULT_PAGE_LIMIT
from core.services.search.route import RouteService

router = APIRouter(prefix="/routes", tags=["search"])


@router.get("", response_model=RoutePageRead, status_code=status.HTTP_200_OK)
async def get_routes(
    db: DbSession,
    executor_id: int,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_LIMIT,
) -> RoutePageRead:
    """Маршруты конкретного водителя (исполнителя): откуда, куда и за сколько едет."""
    return await RouteService(db).get_by_executor(
        executor_id, skip=skip, limit=limit
    )

