import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from core.database import Base
from executor.models import *  # noqa: F401
from user.models import *  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Схемы, которыми полностью управляет расширение PostGIS. Alembic не должен
# ни создавать, ни удалять объекты в них (иначе autogenerate генерирует
# DROP TABLE для таблиц типового геокодера и upgrade падает).
POSTGIS_OWNED_SCHEMAS = frozenset({
    "postgis",
    "topology",
    "tiger",
    "tiger_data",
})


def include_object(object, name, type_, reflected, compare_to):
    """Исключаем объекты, принадлежащие расширению PostGIS."""
    # Таблица spatial_ref_sys живёт в public, но принадлежит расширению postgis.
    if type_ == "table" and name == "spatial_ref_sys":
        return False

    # Всё, что находится в схемах PostGIS (tiger, topology и т.п.), создаётся
    # расширениями postgis_tiger_geocoder / postgis_topology и должно попадать
    # в автогенерацию.
    schema = getattr(object, "schema", None)
    if schema in POSTGIS_OWNED_SCHEMAS:
        return False

    return True


def do_run_migrations(connection) -> None:
    # Ограничиваем search_path только при autogenerate, чтобы extension-таблицы
    # PostGIS (tiger/topology) не попадали в автогенерацию и не генерировался
    # DROP TABLE для них (иначе upgrade падает с
    # "cannot drop table ... because extension postgis_tiger_geocoder requires it").
    #
    # При обычном upgrade/применении миграций этого делать НЕЛЬЗЯ: SET search_path
    # на asyncpg-соединении приводит к тому, что миграция молча НЕ применяется
    # (транзакция не фиксируется). Миграции, сгенерённые без extension-таблиц,
    # применяются и без ограничения search_path.
    cmd_opts = getattr(config, "cmd_opts", None)
    is_autogenerate = bool(getattr(cmd_opts, "autogenerate", False))
    if is_autogenerate:
        connection.execute(text("SET search_path TO public"))

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.database_url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())