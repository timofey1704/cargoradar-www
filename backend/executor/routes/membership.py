from fastapi import APIRouter, status

from core.dependencies import CurrentExecutor, DbSession
from core.schemas.membership_read import SubscriptionRemainingRead
from core.services import membership_service

router = APIRouter(prefix="/membership", tags=["executor membership"])


@router.get("/info", response_model=SubscriptionRemainingRead, status_code=status.HTTP_200_OK)
async def get_membership_info(
    current: CurrentExecutor,
    db: DbSession,
) -> SubscriptionRemainingRead:
    """Подписка/триал текущего клиента (с остатком дней) и каталог доступных тарифных планов."""
    service = membership_service.MembershipService(db)
    return await service.get_subscription_info(executor_id=current.id)