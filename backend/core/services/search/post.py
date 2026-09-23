from sqlalchemy.ext.asyncio import AsyncSession

from core.models.enums.post_creator_type import PostCreatorType
from core.repositories.search.post import PostRepository
from core.schemas.search.post import PostPageRead, PostRead
from core.services.search.common import DEFAULT_PAGE_LIMIT, build_page, search_cached


class PostService:
    """Посты: поиск по автору (клиент/исполнитель) и по типу автора."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = PostRepository(db)

    @search_cached("search:post")
    async def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = DEFAULT_PAGE_LIMIT
    ) -> PostPageRead:
        """Посты конкретного клиента (кешируем в Redis)."""
        posts = await self.repository.get_by_client(
            client_id, skip=skip, limit=limit
        )
        return build_page(
            [PostRead.model_validate(post) for post in posts],
            skip=skip,
            limit=limit,
        )

    @search_cached("search:post")
    async def get_by_executor(
        self, executor_id: int, *, skip: int = 0, limit: int = DEFAULT_PAGE_LIMIT
    ) -> PostPageRead:
        """Посты конкретного исполнителя (кешируем в Redis)."""
        posts = await self.repository.get_by_executor(
            executor_id, skip=skip, limit=limit
        )
        return build_page(
            [PostRead.model_validate(post) for post in posts],
            skip=skip,
            limit=limit,
        )

    @search_cached("search:post")
    async def get_by_creator_type(
        self,
        creator_type: PostCreatorType,
        *,
        skip: int = 0,
        limit: int = DEFAULT_PAGE_LIMIT,
    ) -> PostPageRead:
        """Посты нужного типа автора: СТО/поставщик или клиент (кешируем в Redis)."""
        posts = await self.repository.get_by_creator_type(
            creator_type, skip=skip, limit=limit
        )
        return build_page(
            [PostRead.model_validate(post) for post in posts],
            skip=skip,
            limit=limit,
        )

