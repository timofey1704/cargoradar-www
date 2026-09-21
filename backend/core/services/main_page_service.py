from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.redis.cache import cached
from core.repositories.main_page_repository import MainPageRepository
from core.schemas.faq import FAQRead


class MainPageService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = MainPageRepository(db)

    @cached(ttl=settings.cache_ttl_faq, key="main:faq")
    async def get_faqs(self) -> list[FAQRead]:
        """Получаем список FAQ для главной страницы (кешируем в Redis)"""
        faqs = await self.repository.get_faqs()
        return [FAQRead.model_validate(faq) for faq in faqs]