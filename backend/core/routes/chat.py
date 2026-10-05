"""REST-роуты чата: беседы, сообщения, вложения.

Одни и те же `/api/conversations*` обслуживают обе роли: аутентификация —
`CurrentChatActor` (Bearer или httpOnly-куки client/executor), а права
(«является ли пользователь участником беседы») проверяются в сервисе на каждый
запрос
"""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from core.dependencies import ChatActor, CurrentChatActor, CurrentExecutor, DbSession
from core.exceptions import (
    AttachmentLimitError,
    AttachmentNotAvailableError,
    AttachmentNotFoundError,
    AttachmentTooLargeError,
    AttachmentUnsupportedError,
    AttachmentsMissingError,
    ChatError,
    ConversationNotFoundError,
    MessageEmptyError,
    MessageTooLongError,
)
from core.models.enums.actor_types import ActorType
from core.schemas.chat import (
    AttachmentRead,
    ConversationRead,
    ConversationReadUpdate,
    ConversationUnreadRead,
    MessageCreate,
    MessageRead,
)
from core.schemas.offer import OfferCreate, OfferRead
from core.services.chat_service import ChatService
from core.services.offer_service import (
    OfferAlreadyPendingError,
    OfferRequestNotFoundError,
    OfferRequestUnavailableError,
    OfferService,
)
from core.services.search.common import DEFAULT_PAGE_LIMIT

router = APIRouter(tags=["chat"])


@router.post(
    "/executor/orders/{order_id}/offers",
    response_model=OfferRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_offer(
    order_id: int,
    data: OfferCreate,
    current: CurrentExecutor,
    db: DbSession,
) -> OfferRead:
    service = OfferService(db)
    actor = ChatActor(role=ActorType.executor, id=current.id)
    try:
        return await service.create(actor, order_id, data)
    except OfferRequestNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Заявка не найдена") from exc
    except OfferRequestUnavailableError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "Заявка уже закрыта") from exc
    except OfferAlreadyPendingError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "У вас уже есть активное предложение по этой заявке",
        ) from exc


def _http_error(exc: ChatError) -> HTTPException:
    """Доменные ошибки сервиса — в HTTP-ответы (как в client/routes/request.py)."""
    if isinstance(exc, ConversationNotFoundError):
        # чужая беседа неотличима от несуществующей — не подсказываем
        return HTTPException(status.HTTP_404_NOT_FOUND, "Беседа не найдена")
    if isinstance(exc, AttachmentNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Вложение не найдено")
    if isinstance(exc, AttachmentNotAvailableError):
        return HTTPException(status.HTTP_409_CONFLICT, "Вложение уже отправлено")
    if isinstance(exc, AttachmentTooLargeError):
        return HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"Файл больше {exc.limit} байт",
        )
    if isinstance(exc, AttachmentUnsupportedError):
        return HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Неподдерживаемый тип файла: нужны изображение или видео",
        )
    if isinstance(exc, MessageEmptyError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Сообщение пустое")
    if isinstance(exc, MessageTooLongError):
        return HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"Максимальная длина сообщения — {exc.limit} символов",
        )
    if isinstance(exc, AttachmentsMissingError):
        return HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "У медиа-сообщения нет вложений"
        )
    if isinstance(exc, AttachmentLimitError):
        return HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"В сообщении не больше {exc.limit} вложений",
        )
    return HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


@router.get(
    "/conversations",
    response_model=list[ConversationRead],
    status_code=status.HTTP_200_OK,
)
async def get_conversations(
    current: CurrentChatActor,
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_LIMIT, ge=1, le=100),
) -> list[ConversationRead]:
    """Беседы текущего участника: активные сверху, с последним сообщением и непрочитанными."""
    service = ChatService(db)
    return await service.list_conversations(current, skip=skip, limit=limit)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationRead,
    status_code=status.HTTP_200_OK,
)
async def get_conversation(
    conversation_id: int,
    current: CurrentChatActor,
    db: DbSession,
) -> ConversationRead:
    """Одна беседа (404 — если её нет или вы не её участник)."""
    service = ChatService(db)
    try:
        return await service.get_conversation(current, conversation_id)
    except ChatError as exc:
        raise _http_error(exc) from exc


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageRead],
    status_code=status.HTTP_200_OK,
)
async def get_conversation_messages(
    conversation_id: int,
    current: CurrentChatActor,
    db: DbSession,
    before_id: int | None = Query(
        None, ge=0, description="Курсор: вернуть limit сообщений строго старше него"
    ),
    after_id: int | None = Query(
        None, ge=0, description="Догрузка после реконнекта: limit сообщений новее"
    ),
    limit: int = Query(50, ge=1, le=100),
) -> list[MessageRead]:
    """История беседы (курсорная пагинация) — всегда по возрастанию id.

    После (ре)коннекта фронт догружает пропущенное через `after_id`:
    Pub/Sub доставку не гарантирует, источник истины — Postgres (§7).
    """
    service = ChatService(db)
    try:
        return await service.list_messages(
            current,
            conversation_id,
            before_id=before_id,
            after_id=after_id,
            limit=limit,
        )
    except ChatError as exc:
        raise _http_error(exc) from exc


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation_message(
    conversation_id: int,
    data: MessageCreate,
    current: CurrentChatActor,
    db: DbSession,
) -> MessageRead:
    """Отправить текст или медиа; `idempotency_key` защищает от дублей при ретрае.

    Сохранённое сообщение публикуется в Redis обоим участникам уже после commit —
    по WebSocket придёт `{type: "message.created", data: {...}}`.
    """
    service = ChatService(db)
    try:
        return await service.create_message(current, conversation_id, data)
    except ChatError as exc:
        raise _http_error(exc) from exc


@router.post(
    "/conversations/{conversation_id}/read",
    response_model=ConversationUnreadRead,
    status_code=status.HTTP_200_OK,
)
async def read_conversation(
    conversation_id: int,
    data: ConversationReadUpdate,
    current: CurrentChatActor,
    db: DbSession,
) -> ConversationUnreadRead:
    """Отметить беседу прочитанной «до last_read_id» и вернуть новый счётчик."""
    service = ChatService(db)
    try:
        return await service.mark_read(current, conversation_id, data.last_read_id)
    except ChatError as exc:
        raise _http_error(exc) from exc


@router.post(
    "/attachments",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    current: CurrentChatActor,
    db: DbSession,
    file: UploadFile = File(..., description="Файл изображения или видео"),
) -> AttachmentRead:
    """Multipart-загрузка вложения: тип проверяется по сигнатуре, размер — по лимиту.

    Вложение создаётся без привязки к сообщению и привязывается при
    `POST /conversations/{id}/messages` с `attachment_ids` (§5).
    """
    service = ChatService(db)
    try:
        return await service.upload_attachment(current, file)
    except ChatError as exc:
        raise _http_error(exc) from exc


@router.get(
    "/attachments/{attachment_id}/url",
    status_code=status.HTTP_200_OK,
)
async def get_attachment_url(
    attachment_id: int,
    current: CurrentChatActor,
    db: DbSession,
) -> dict[str, str]:
    """URL вложения для просмотра/скачивания: его видит загрузивший или участники беседы."""
    service = ChatService(db)
    try:
        url = await service.get_attachment_url(current, attachment_id)
    except ChatError as exc:
        raise _http_error(exc) from exc
    return {"url": url}


