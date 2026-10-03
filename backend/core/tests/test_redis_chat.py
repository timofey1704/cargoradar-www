"""Юнит-тесты Redis Pub/Sub для чата (`core/redis/chat.py`) — реальный Redis не нужен.

Покрыто:
- именование каналов с ролью (`chat:user:{role}:{id}`) — защита от коллизии id
  клиентов и исполнителей, которые живут в разных таблицах;
- конверт события `{type, data}`: encode/parse roundtrip и битые payload'ы;
- публикация через pipeline: dedup каналов, счётчик получателей,
  graceful degradation при недоступном Redis (возвращаем 0, запрос не падает);
- подписка-генератор: доставка событий и отбрасывание служебных сообщений
  подписки (subscribe/unsubscribe) и некорректных payload'ов.

Фейк `FakePubSubRedis` воспроизводит ровно те команды, которые использует
chat.py: `pipeline().publish()` + `execute()`, `pubsub().subscribe()/listen()`,
`publish()`. Для приведения фейка к типу `aioredis.Redis` используется `_as_redis`
(фейк структурно совместим, но не наследует redis.Redis).
"""

import asyncio
import json
from typing import cast

import redis.asyncio as aioredis

from core.redis.chat import (
    CHANNEL_PREFIX,
    EVENT_MESSAGE_CREATED,
    EVENT_OFFER_UPDATED,
    ROLE_CLIENT,
    ROLE_EXECUTOR,
    build_event,
    encode_event,
    parse_event,
    participant_channels,
    publish_event,
    publish_to_participants,
    subscribe,
    user_channel,
)


def _as_redis(fake: object) -> aioredis.Redis:
    """Фейки структурно совместимы с нужными командами; для типизации приводим к Redis."""
    return cast(aioredis.Redis, fake)


# --- фейковый Redis с pub/sub ------------------------------------------------


class FakePubSub:
    """In-memory подписка: listen() отдаёт сообщения из очереди."""

    def __init__(self, redis: "FakePubSubRedis") -> None:
        self._redis = redis
        self.channels: set[str] = set()
        self._queue: asyncio.Queue = asyncio.Queue()
        self.closed = False

    async def subscribe(self, *channels: str) -> None:
        for channel in channels:
            self.channels.add(channel)
            self._redis.subscribers.setdefault(channel, set()).add(self)

    async def unsubscribe(self, *channels: str) -> None:
        for channel in channels:
            self.channels.discard(channel)
            self._redis.subscribers.get(channel, set()).discard(self)

    async def listen(self):
        while True:
            message = await self._queue.get()
            if message is None:
                return
            yield message

    async def aclose(self) -> None:
        self.closed = True
        await self._queue.put(None)

    def feed(self, channel: str, payload: str, message_type: str = "message") -> None:
        self._queue.put_nowait(
            {"type": message_type, "channel": channel, "data": payload}
        )


class FakePipeline:
    def __init__(self, redis: "FakePubSubRedis") -> None:
        self._redis = redis
        self._calls: list[tuple[str, str]] = []

    async def __aenter__(self) -> "FakePipeline":
        return self

    async def __aexit__(self, *exc_info) -> bool:
        return False

    def publish(self, channel: str, payload: str) -> None:
        self._calls.append((channel, payload))

    async def execute(self) -> list[int]:
        return [
            await self._redis.publish(channel, payload)
            for channel, payload in self._calls
        ]


class FakePubSubRedis:
    """Мини-реализация publish/pubsub, достаточная для тестов chat.py."""

    def __init__(self) -> None:
        self.subscribers: dict[str, set[FakePubSub]] = {}
        self.published: list[tuple[str, str]] = []

    def pubsub(self) -> FakePubSub:
        return FakePubSub(self)

    async def publish(self, channel: str, payload: str) -> int:
        self.published.append((channel, payload))
        subscribers = self.subscribers.get(channel, set())
        for pubsub in subscribers:
            pubsub.feed(channel, payload)
        return len(subscribers)

    def pipeline(self, transaction: bool = False) -> FakePipeline:
        return FakePipeline(self)


class BrokenPipelineRedis:
    """Redis, который падает на любой публикации (проверяем graceful degradation)."""

    def pipeline(self, transaction: bool = False):
        raise ConnectionError("redis is down")


# --- именование каналов ------------------------------------------------------


def test_user_channel_namespaces_role():
    assert user_channel(ROLE_CLIENT, 12) == f"{CHANNEL_PREFIX}:client:12"
    assert user_channel(ROLE_EXECUTOR, 12) == f"{CHANNEL_PREFIX}:executor:12"


def test_same_id_for_client_and_executor_gives_different_channels():
    """Защита от коллизии: id клиента и исполнителя могут совпадать."""
    assert user_channel(ROLE_CLIENT, 7) != user_channel(ROLE_EXECUTOR, 7)


def test_participant_channels_returns_both_participants():
    assert participant_channels(1, 2) == [
        f"{CHANNEL_PREFIX}:client:1",
        f"{CHANNEL_PREFIX}:executor:2",
    ]


# --- конверт события ---------------------------------------------------------


def test_build_event_wraps_type_and_data():
    assert build_event("x", {"a": 1}) == {"type": "x", "data": {"a": 1}}


def test_encode_and_parse_event_roundtrip():
    raw = encode_event(EVENT_MESSAGE_CREATED, {"id": 5})

    assert parse_event(raw) == {"type": EVENT_MESSAGE_CREATED, "data": {"id": 5}}


def test_parse_event_returns_none_for_empty_or_broken_payload():
    assert parse_event(None) is None
    assert parse_event("not-json") is None
    assert parse_event("[1, 2]") is None
    assert parse_event(json.dumps({"data": {}})) is None  # нет обязательного "type"


# --- публикация --------------------------------------------------------------


async def test_publish_event_sends_to_all_channels_via_pipeline():
    fake = FakePubSubRedis()

    await publish_event(_as_redis(fake), ["a", "b"], EVENT_OFFER_UPDATED, {"offer_id": 1})

    assert [channel for channel, _ in fake.published] == ["a", "b"]


async def test_publish_event_deduplicates_channels():
    fake = FakePubSubRedis()

    await publish_event(_as_redis(fake), ["a", "a", "b", "a"], "x", {})

    assert [channel for channel, _ in fake.published] == ["a", "b"]


async def test_publish_event_without_channels_does_nothing():
    fake = FakePubSubRedis()

    assert await publish_event(_as_redis(fake), [], "x", {}) == 0
    assert fake.published == []


async def test_publish_to_participants_targets_both_and_counts_receivers():
    fake = FakePubSubRedis()
    await fake.pubsub().subscribe(user_channel(ROLE_CLIENT, 1))
    await fake.pubsub().subscribe(user_channel(ROLE_EXECUTOR, 2))

    receivers = await publish_to_participants(
        _as_redis(fake),
        client_id=1,
        executor_id=2,
        event_type=EVENT_OFFER_UPDATED,
        data={"offer_id": 9, "status": "accepted"},
    )

    assert receivers == 2
    assert json.loads(fake.published[0][1]) == {
        "type": EVENT_OFFER_UPDATED,
        "data": {"offer_id": 9, "status": "accepted"},
    }


async def test_publish_event_returns_zero_on_redis_error():
    assert await publish_event(_as_redis(BrokenPipelineRedis()), ["a"], "x", {}) == 0


# --- подписка ----------------------------------------------------------------


async def test_subscribe_yields_published_event():
    fake = FakePubSubRedis()
    channel = user_channel(ROLE_CLIENT, 42)

    events = subscribe(_as_redis(fake), channel)
    # `__anext__()` типизируется как Awaitable, а не Coroutine — поэтому ensure_future
    pending = asyncio.ensure_future(events.__anext__())
    await asyncio.sleep(0)  # даём подписке встать

    await fake.publish(channel, encode_event(EVENT_MESSAGE_CREATED, {"id": 1}))

    event = await asyncio.wait_for(pending, timeout=1)
    assert event == {"type": EVENT_MESSAGE_CREATED, "data": {"id": 1}}

    await events.aclose()


async def test_subscribe_skips_service_messages_and_broken_payloads():
    fake = FakePubSubRedis()
    channel = user_channel(ROLE_CLIENT, 42)

    events = subscribe(_as_redis(fake), channel)
    pending = asyncio.ensure_future(events.__anext__())
    await asyncio.sleep(0)

    subscriber = next(iter(fake.subscribers[channel]))
    subscriber.feed(channel, "ignored", message_type="subscribe")  # служебное
    subscriber.feed(channel, "not-json")  # битый payload
    await fake.publish(channel, encode_event(EVENT_OFFER_UPDATED, {"offer_id": 3}))

    event = await asyncio.wait_for(pending, timeout=1)
    assert event == {"type": EVENT_OFFER_UPDATED, "data": {"offer_id": 3}}

    await events.aclose()
