from fastapi import APIRouter

from core.schemas.faq import FAQRead
from core.dependencies import DbSession
from core.services.main_page_service import MainPageService

router = APIRouter(prefix="/main", tags=["main page"])


@router.get("/faq", response_model=list[FAQRead])
async def get_faqs(
    db: DbSession,
) -> list[FAQRead]:
    service = MainPageService(db)
    return await service.get_faqs()