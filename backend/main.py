import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from executor.routes.auth import router as executor_auth_router
from client.routes.auth import router as client_auth_router

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
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
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

# отдаём загруженный медиаконтент по /uploads/...
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}