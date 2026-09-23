from __future__ import annotations

from typing import Sequence

from sqlalchemy import select

from core.repositories.search.base import BaseRepository
from core.models.post import Post
from core.models.enums.post_creator_type import PostCreatorType


class PostRepository(BaseRepository[Post]):
    """Репозиторий постов (Post), которые создают СТО и поставщики (или водители)."""

    model = Post

    async def get_by_client(
        self, client_id: int, *, skip: int = 0, limit: int = 20
    ) -> Sequence[Post]:
        stmt = (
            select(Post)
            .where(Post.client_id == client_id, Post.is_deleted.is_(False))
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_executor(
        self, executor_id: int, *, skip: int = 0, limit: int = 20
    ) -> Sequence[Post]:
        stmt = (
            select(Post)
            .where(Post.executor_id == executor_id, Post.is_deleted.is_(False))
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_creator_type(
        self, creator_type: PostCreatorType, *, skip: int = 0, limit: int = 20
    ) -> Sequence[Post]:
        stmt = (
            select(Post)
            .where(Post.creator_type == creator_type, Post.is_deleted.is_(False))
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()