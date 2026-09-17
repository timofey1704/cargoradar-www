from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.faq import FAQ


class MainPageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_faqs(self) -> list[FAQ]:
        """Получаем все FAQ"""
        result = await self.db.execute(
            select(FAQ)
            .order_by(FAQ.updated_at)
        )
        return list(result.scalars().all())
