"""Общие фикстуры для тестов client.

Интеграционные тесты работают с живой БД (PostGIS). Если PostgreSQL/PostGIS
недоступен — тесты пропускаются (фикстура db_engine).

Запуск (внутри docker-сети хост postgres резолвится):
    docker compose exec backend uv run pytest client/tests -q

Снаружи (БД проброшена на localhost:5433) можно переопределить DSN:
    TEST_DATABASE_URL=postgresql+asyncpg://admin:<pass>@localhost:5433/cargoradardb \
        uv run pytest client/tests -q
"""

import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

# регистрируем все ORM-модели (как в main.py), иначе SQLAlchemy не сможет
# сконфигурировать мапперы
from admin.models import *  # noqa: F401
from client.models import *  # noqa: F401
from core.models import *  # noqa: F401
from executor.models import *  # noqa: F401

from client.models.client import Client
from client.models.enums.client_types import ClientTypes
from executor.models.enums.executor_types import ExecutorTypes
from executor.models.executor import Executor


@pytest.fixture(scope="session")
def database_url() -> str:
    """DSN для интеграционных тестов: TEST_DATABASE_URL или DATABASE_URL из .env."""
    return os.getenv("TEST_DATABASE_URL") or settings.database_url


@pytest.fixture
async def db_engine(database_url: str):
    """Async-движок до живой БД. Если БД или расширение PostGIS недоступны — skip."""
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT postgis_version()"))
    except Exception as exc:  # pragma: no cover - зависит от окружения
        await engine.dispose()
        pytest.skip(f"PostgreSQL/PostGIS недоступен ({exc.__class__.__name__}) — тесты пропущены")

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Сессия в общей транзакции: в конце теста всё откатывается, БД не засоряется."""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def individual_client(db_session: AsyncSession) -> Client:
    """Заказчик-физлицо для проверки FK-связи cargo_requests.client_id."""
    client = Client(
        name="Тестовый заказчик",
        phone_number="+375000000002",
        email="cargo_request_test@example.com",
        type=ClientTypes.individual,
    )
    db_session.add(client)
    await db_session.flush()
    return client


@pytest.fixture
async def carrier_executor(db_session: AsyncSession) -> Executor:
    """Перевозчик для проверки FK-связей posts.executor_id и routes.executor_id."""
    executor = Executor(
        type=ExecutorTypes.carrier,
        name="Тестовый перевозчик",
        email="client_tests_carrier@example.com",
        phone_number="+375000000003",
    )
    db_session.add(executor)
    await db_session.flush()
    return executor
