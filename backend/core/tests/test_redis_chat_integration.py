"""Интеграционные тесты Redis Pub/Sub чата на реальном Redis.

Нужен запущенный Redis (например `docker compose up -d redis`).
Если Redis недоступен — тесты автоматически пропускаются,
поэтому обычный `pytest` работает и без него.

Тесты гоняют боевой путь — генератор `subscribe()` (тот, что использует
WebSocket-хаб): он использует `pubsub.listen()` и сам отфильтровывает
служебные сообщения подписки.
"""

import asyncio

import pytest

from core.redis.chat import (
    EVENT_MESSAGE_CREATED,
    EVENT_OFFER_UPDATED,
    participant_channels,
    user_channel,
)

pytestmark = pytest.mark.integration

CLIENT_ID = 987001
EXECUTOR_ID = 987002


async def _collect(events, count: int) -> list[dict]:
    """Собирает count событий из async-генератора подписки."""
    collected: list[dict] = []
    async for event in events:
        collected.append(event)
        if len(collected) >= count:
            break
    return collected


async def test_publish_chat_event_delivers_to_both_participants(real_redis_client):
    channels = participant_channels(CLIENT_ID, EXECUTOR_ID)

    events = real_redis_client.subscribe_chat(*channels)
    collector = asyncio.create_task(_collect(events, 2))
    await asyncio.sleep(0.2)  # даём подписке встать на реальном Redis

    try:
        receivers = await real_redis_client.publish_chat_event(
            client_id=CLIENT_ID,
            executor_id=EXECUTOR_ID,
            event_type=EVENT_OFFER_UPDATED,
            data={"offer_id": 5, "status": "accepted"},
        )
        assert receivers == 2  # два канала, по одному подписчику

        received = await asyncio.wait_for(collector, timeout=3)
        assert [event["type"] for event in received] == [EVENT_OFFER_UPDATED] * 2
        assert all(
            event["data"] == {"offer_id": 5, "status": "accepted"}
            for event in received
        )
    finally:
        await events.aclose()


async def test_subscribe_helper_yields_event(real_redis_client):
    events = real_redis_client.subscribe_chat(user_channel("client", CLIENT_ID))
    # `__anext__()` типизируется как Awaitable, а не Coroutine — поэтому ensure_future
    pending = asyncio.ensure_future(events.__anext__())
    await asyncio.sleep(0.2)  # даём подписке встать на реальном Redis

    await real_redis_client.publish_chat_event(
        client_id=CLIENT_ID,
        executor_id=EXECUTOR_ID,
        event_type=EVENT_MESSAGE_CREATED,
        data={"id": 42},
    )

    event = await asyncio.wait_for(pending, timeout=3)
    assert event == {"type": EVENT_MESSAGE_CREATED, "data": {"id": 42}}

    await events.aclose()


async def test_event_is_not_delivered_to_foreign_user(real_redis_client):
    """Событие не должно утекать постороннему пользователю."""
    events = real_redis_client.subscribe_chat(user_channel("client", CLIENT_ID + 1))
    pending = asyncio.ensure_future(events.__anext__())
    await asyncio.sleep(0.2)

    await real_redis_client.publish_chat_event(
        client_id=CLIENT_ID,
        executor_id=EXECUTOR_ID,
        event_type=EVENT_MESSAGE_CREATED,
        data={"id": 1},
    )

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(pending, timeout=0.5)

    await events.aclose()