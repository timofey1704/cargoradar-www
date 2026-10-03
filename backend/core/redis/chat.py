"""Redis Pub/Sub для чата (доставка событий по WebSocket).

REST-хендлеры публикуют события **строго после commit** в каналы участников
беседы; WebSocket-хаб подписывается на каналы пользователей и рассылает
события локальным сокетам. Источник истины — PostgreSQL: Pub/Sub доставку не
гарантирует, поэтому после реконнекта клиент догружает пропущенное через REST
(`after_id`), а сокет — лишь ускоритель (см. 05-chat.md §7).

Формат события (envelope): ``{"type": <event>, "data": {...}}``.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Iterable
from typing import Any

import redis.asyncio as aioredis

# --- именование каналов ------------------------------------------------------
#
# Роль в ключе обязательна: id клиентов и исполнителей живут в разных таблицах
# и могут совпадать — без роли каналы разных людей «слиплись» бы в один.
CHANNEL_PREFIX = "chat:user"

ROLE_CLIENT = "client"
ROLE_EXECUTOR = "executor"

# --- типы событий (совпадают с событиями из 05-chat.md §7) -------------------
EVENT_MESSAGE_CREATED = "message.created"
EVENT_OFFER_UPDATED = "offer.updated"


def user_channel(role: str, user_id: int) -> str:
    """Канал одного пользователя: ``chat:user:{role}:{id}``."""
    return f"{CHANNEL_PREFIX}:{role}:{user_id}"


def participant_channels(client_id: int, executor_id: int) -> list[str]:
    """Каналы обоих участников беседы: клиента и исполнителя."""
    return [
        user_channel(ROLE_CLIENT, client_id),
        user_channel(ROLE_EXECUTOR, executor_id),
    ]


def build_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Собирает конверт события ``{type, data}``."""
    return {"type": event_type, "data": data}


def encode_event(event_type: str, data: dict[str, Any]) -> str:
    """JSON-представление события для публикации в канал."""
    return json.dumps(build_event(event_type, data), ensure_ascii=False, default=str)


def parse_event(raw: str | bytes | None) -> dict[str, Any] | None:
    """Разбирает payload из канала.

    Returns:
        dict | None: конверт события, либо None — если payload пустой,
        битый или в нём нет обязательного поля ``type``
    """
    if raw is None:
        return None

    try:
        event = json.loads(raw)
    except (TypeError, ValueError):
        return None

    if not isinstance(event, dict) or "type" not in event:
        return None

    return event


async def publish_event(
    redis_client: aioredis.Redis,
    channels: Iterable[str],
    event_type: str,
    data: dict[str, Any],
) -> int:
    """Публикует событие во все каналы.

    Дубликаты каналов схлопываются. Ошибки Redis не пробрасываются: Pub/Sub —
    доставка, а не источник правды, поэтому падение публикации не должно ломать
    REST-запрос (пропущенное клиент догрузит по REST после реконнекта).

    Returns:
        int: суммарное число получателей, которым доставлено событие
        (0 — если каналов нет или произошла ошибка Redis)
    """
    unique_channels = list(dict.fromkeys(channels))
    if not unique_channels:
        return 0

    payload = encode_event(event_type, data)

    try:
        async with redis_client.pipeline(transaction=False) as pipe:
            for channel in unique_channels:
                pipe.publish(channel, payload)
            results = await pipe.execute()

        return sum(int(received) for received in results)

    except Exception as e:  # noqa: BLE001 — публикация не должна ломать запрос
        print(f"Redis error in publish_event: {str(e)}")
        return 0


async def publish_to_participants(
    redis_client: aioredis.Redis,
    *,
    client_id: int,
    executor_id: int,
    event_type: str,
    data: dict[str, Any],
) -> int:
    """Публикует событие обоим участникам беседы (клиенту и исполнителю)."""
    return await publish_event(
        redis_client,
        participant_channels(client_id, executor_id),
        event_type,
        data,
    )


async def subscribe(
    redis_client: aioredis.Redis,
    *channels: str,
) -> AsyncGenerator[dict[str, Any], None]:
    """Подписка на каналы: асинхронный генератор валидных событий.

    Используется WebSocket-хабом. Pub/Sub занимает отдельное соединение,
    поэтому генератор владеет своим pubsub-объектом и закрывает его при выходе.
    Служебные сообщения (subscribe/unsubscribe) отфильтровываются.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(*channels)

    try:
        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue

            event = parse_event(message.get("data"))
            if event is not None:
                yield event

    finally:
        await pubsub.unsubscribe(*channels)
        await pubsub.aclose()

