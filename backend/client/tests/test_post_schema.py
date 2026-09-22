"""Интеграционные тесты схемы постов (core.models.post.Post).

Посты создают и клиенты, и исполнители, поэтому тесты живут рядом с тестами
грузовых заявок и используют общие фикстуры client/tests/conftest.py.

    docker compose exec backend uv run pytest client/tests -q
"""

from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from core.models.enums.post_creator_type import PostCreatorType
from core.models.post import Post

pytestmark = pytest.mark.integration

TABLE = "posts"


def _normalize_predicate(predicate: str) -> str:
    """Убираем скобки и каст enum — Postgres рендерит предикат по-своему."""
    return predicate.replace("(", "").replace(")", "").replace("::post_creator_type", "").strip()


async def _add_post(session, **overrides) -> Post:
    params: dict[str, Any] = {
        "title": "Перевозка 12 т Москва → Тверь",
        "request_text": "Нужен тент, загрузка завтра",
        "creator_type": PostCreatorType.CLIENT,
    }
    params.update(overrides)
    post = Post(**params)
    session.add(post)
    await session.flush()
    await session.refresh(post)
    return post


async def test_creator_type_enum_uses_lowercase_values(db_session):
    """В БД лежат значения enum, а не имена членов: с ними сравнивается CHECK-констрейнт."""
    labels = (
        await db_session.execute(
            text(
                "SELECT enumlabel FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid "
                "WHERE t.typname = 'post_creator_type' ORDER BY e.enumsortorder"
            )
        )
    ).scalars().all()

    assert labels == ["client", "executor"]


async def test_client_post_is_stored_with_lowercase_creator_type(db_session, individual_client):
    """Пост клиента хранится с creator_type = 'client' и не помечен удалённым."""
    post = await _add_post(db_session, client_id=individual_client.id)

    stored = (
        await db_session.execute(
            text("SELECT creator_type::text FROM posts WHERE id = :id"), {"id": post.id}
        )
    ).scalar_one()

    assert stored == "client"
    assert post.creator_type is PostCreatorType.CLIENT
    assert post.is_deleted is False, "значение по умолчанию из модели"


async def test_executor_post_is_stored_with_executor_creator_type(db_session, carrier_executor):
    """Пост исполнителя хранится с creator_type = 'executor'."""
    post = await _add_post(
        db_session,
        creator_type=PostCreatorType.EXECUTOR,
        executor_id=carrier_executor.id,
    )

    stored = (
        await db_session.execute(
            text("SELECT creator_type::text FROM posts WHERE id = :id"), {"id": post.id}
        )
    ).scalar_one()

    assert stored == "executor"


async def test_post_without_owner_is_rejected(db_session):
    """CHECK-констрейнт требует владельца: ни client_id, ни executor_id не заданы."""
    with pytest.raises(IntegrityError):
        await _add_post(db_session)

    await db_session.rollback()


async def test_creator_type_must_match_owner(db_session, carrier_executor):
    """creator_type='client' вместе с executor_id — противоречие, БД такое не примет."""
    with pytest.raises(IntegrityError):
        await _add_post(
            db_session,
            creator_type=PostCreatorType.CLIENT,
            executor_id=carrier_executor.id,
        )

    await db_session.rollback()


async def test_feed_indexes_filter_deleted_posts(db_session):
    """Частичные индексы ленты и профилей покрывают только неудалённые посты."""
    rows = (
        await db_session.execute(
            text(
                "SELECT indexname, indexdef FROM pg_indexes "
                "WHERE tablename = :table AND indexdef ILIKE '%WHERE%'"
            ),
            {"table": TABLE},
        )
    ).all()

    predicates = {}
    for row in rows:
        _, _, predicate = row.indexdef.partition(" WHERE ")
        predicates[row.indexname] = _normalize_predicate(predicate)

    assert predicates == {
        "ix_posts_feed": "NOT is_deleted",
        "ix_posts_client_created": "client_id IS NOT NULL AND NOT is_deleted",
        "ix_posts_executor_created": "executor_id IS NOT NULL AND NOT is_deleted",
    }
