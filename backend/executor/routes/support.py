from fastapi import APIRouter, status

from core.schemas.support import SupportRequestCreate, SupportRequestRead
from core.dependencies import CurrentExecutor, DbSession
from core.models.support_request import SupportRequest
from executor.services import support_service

router = APIRouter(prefix="/account/support", tags=["executor support"])


@router.post(
    "/create-request",
    response_model=SupportRequestRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_support_request(
    data: SupportRequestCreate,
    current: CurrentExecutor,
    db: DbSession,
) -> SupportRequest:
    return await support_service.create_request(
        session=db,
        executor_id=current.id,
        request_type=data.request_type,
        title=data.title,
        description=data.description,
    )


@router.get("/requests", response_model=list[SupportRequestRead])
async def get_support_requests(
    current: CurrentExecutor,
    db: DbSession,
) -> list[SupportRequest]:
    return await support_service.get_requests(session=db, executor_id=current.id)