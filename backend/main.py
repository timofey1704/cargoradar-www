import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from routes import (auth, connect_user, user, activity, matches, finder)

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


# app.include_router(auth.router, prefix="/api") # регистрация, логин и инфа для входа
# app.include_router(connect_user.router, prefix="/api") # связать аккаунты пользователей
# app.include_router(user.router, prefix="/api") # вся логика по юзеру
# app.include_router(activity.router, prefix="/api") # активности
# app.include_router(matches.router, prefix="/api") # метчи
# app.include_router(finder.router, prefix="/api") # свайпы в finder

# отдаём загруженный медиаконтент по /uploads/...
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}