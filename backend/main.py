import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from executor.routes.auth import router as executor_auth_router

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

# CORS — настроить разрешенные источники, методы и заголовки для запросов из браузера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# авторизация исполнителей: /api/executor/auth/*
app.include_router(executor_auth_router, prefix="/api/executor")

# отдаём загруженный медиаконтент по /uploads/...
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}