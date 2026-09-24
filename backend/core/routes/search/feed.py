"""Роут общей ленты поиска: маршруты водителей + посты СТО и поставщиков."""

from fastapi import APIRouter, status

from core.dependencies import DbSession
from core.schemas.search.feed import FeedPageRead
from core.services.search.common import DEFAULT_PAGE_LIMIT
from core.services.search.feed import FeedService

router = APIRouter(prefix="/feed", tags=["search"])


@router.get("", response_model=FeedPageRead, status_code=status.HTTP_200_OK)
async def get_feed(
    db: DbSession,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_LIMIT,
) -> FeedPageRead:
    """Общая лента: маршруты водителей и посты СТО/поставщиков по убыванию даты."""
    return await FeedService(db).get_feed(skip=skip, limit=limit)

