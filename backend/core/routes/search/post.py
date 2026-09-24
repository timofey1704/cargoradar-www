"""Роуты поиска постов (СТО, поставщики, водители)."""

from fastapi import APIRouter, status

from core.dependencies import DbSession
from core.models.enums.post_creator_type import PostCreatorType
from core.schemas.search.post import PostPageRead
from core.services.search.common import DEFAULT_PAGE_LIMIT
from core.services.search.post import PostService

router = APIRouter(prefix="/posts", tags=["search"])


@router.get("", response_model=PostPageRead, status_code=status.HTTP_200_OK)
async def get_posts(
    db: DbSession,
    creator_type: PostCreatorType,
    skip: int = 0,
    limit: int = DEFAULT_PAGE_LIMIT,
) -> PostPageRead:
    """Посты по типу автора: `executor` — СТО/поставщики и водители, `client` — клиенты."""
    return await PostService(db).get_by_creator_type(
        creator_type, skip=skip, limit=limit
    )

