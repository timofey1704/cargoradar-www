import logging
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from executor.models import *  # noqa: F401
from client.models import *  # noqa: F401
from admin.models import *  # noqa: F401
from core.models import *  # noqa: F401

from executor.routes.auth import router as executor_auth_router
from client.routes.auth import router as client_auth_router
from client.routes.profile import router as client_profile_router
from client.routes.support import router as client_support_router
from client.routes.membership import router as client_membership_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cargoradar Backend app",
    description="Backend application contests server logic",
    version="0.1.0",
)

def _mask_sensitive(data: dict) -> dict:
    """Маскируем пароль в логах — не пишем его в открытом виде."""
    masked = dict(data)
    if "password" in masked:
        masked["password"] = "***"
    return masked


def _json_safe(value: object) -> object:
    """Рекурсивно приводит значение к JSON-сериализуемому виду.

    Pydantic v2 в случае ``model_validator`` кладёт сам объект исключения
    (например ``ValueError``) в ``ctx.error`` внутри ``exc.errors()``.
    ``json.dumps`` такие объекты не сериализует, поэтому без этого шага
    любой validation error превращался бы из 422 в 500.
    """
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Exception):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Log the body and validation errors - otherwise uvicorn silently returns 422."""
    
    # Get the request body if available
    body = await request.body() if hasattr(request, '_body') else b''
    try:
        body_json = await request.json() if body else {}
    except:
        body_json = body.decode('utf-8', errors='ignore') if body else ''
    
    # Log the validation error with method, path, and errors
    logger.error(
        "Validation error: %s %s -> errors=%s, body=%s",
        request.method,
        request.url.path,
        exc.errors(),
        body_json if isinstance(body_json, dict) else str(body_json),
    )
    
    # Log masked version if it's a dict (to mask passwords)
    if isinstance(body_json, dict):
        masked_body = body_json.copy()
        # Mask common sensitive fields
        for field in ['password', 'password_confirm', 'secret', 'token']:
            if field in masked_body:
                masked_body[field] = '***MASKED***'
        logger.error(
            "Validation error body (masked): %s",
            masked_body,
        )
    
    # Return only errors in response (like default 422)
    # Очищаем ошибки от не-JSON-сериализуемых объектов (ValueError в ctx).
    return JSONResponse(
        status_code=422,
        content={"detail": _json_safe(exc.errors())},
    )

# CORS — настроить разрешенные источники, методы и заголовки для запросов из браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(executor_auth_router, prefix="/api/executor") # авторизация исполнителей: /api/executor/auth/*
app.include_router(client_auth_router, prefix="/api/client") # авторизация клиентов: /api/client/auth/*
app.include_router(client_profile_router, prefix="/api/client") # профиль клиентов: /api/client/profile/*
app.include_router(client_support_router, prefix="/api/client") # саппорт клиентов: /api/client/account/support*
app.include_router(client_membership_router, prefix="/api/client")  # тарифы и подписка клиента: /api/client/membership/*

# отдаём загруженный медиаконтент по /uploads/...
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}