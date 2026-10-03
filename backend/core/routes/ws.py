"""WebSocket-хаб чата (05-chat.md §7).

Одно соединение на пользователя, а не на чат: хаб подписывается на канал
`chat:user:{role}:{id}` через Redis pub/sub и пересылает события локальным
сокетам. Postgres — источник истины, поэтому после реконнекта клиент
догружает пропущенное через REST (`after_id`).

Аутентификация: браузерный `WebSocket` не умеет ставить заголовки, поэтому
токен берётся из httpOnly-куки (основной путь) либо из `?token=` (§7).
От клиента сервер принимает только `ping`; всё остальное — через REST.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import suppress
from typing import Any

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from core.database import AsyncSessionLocal
from core.dependencies import ChatActor, authenticate_chat_actor
from core.redis.chat import user_channel
from core.redis.redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter()

# клиент шлёт ping примерно раз в 25 c (§7); таймаут в 2 интервала с запасом
HEARTBEAT_TIMEOUT = 60.0


async def _forward_events(
    websocket: WebSocket,
    channel: str,
    events: AsyncGenerator[dict[str, Any], None],
) -> None:
    """Подписка Redis → сокет. Обрыв подписки закрывает соединение: клиент реконнектится."""
    try:
        async for event in events:
            await websocket.send_json(event)
    except asyncio.CancelledError:
        raise  # нормальный выход при закрытии сокета — не глушим
    except Exception:  # noqa: BLE001 — одна упавшая подписка не должна валить процесс
        logger.warning("WS: канал %s оборвался", channel, exc_info=True)
        with suppress(RuntimeError):  # сокет мог закрыться раньше
            await websocket.close(code=1011)


async def _authenticate(websocket: WebSocket, token: str | None) -> ChatActor | None:
    """Cookie либо `?token=` → участник чата; None — отказ в доступе.

    Сессию открываем и сразу закрываем: подключение к БД живёт весь срок
    сокета, а пул на нём держать нельзя (pool_size=10 на весь процесс).
    """
    try:
        async with AsyncSessionLocal() as session:
            return await authenticate_chat_actor(
                session,
                (
                    token,
                    websocket.cookies.get("client_access_token"),
                    websocket.cookies.get("executor_access_token"),
                ),
            )
    except HTTPException:
        return None


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str | None = Query(
        None, description="Access-токен, если httpOnly-куки недоступны (кросс-домен)"
    ),
) -> None:
    """Единственное WS-соединение пользователя: события всех его бесед."""
    actor = await _authenticate(websocket, token)
    if actor is None:
        # accept + close(1008), а не отказ до accept: браузер получает код
        # закрытия и может отличить «нет прав» от обрыва сети
        await websocket.accept()
        await websocket.close(code=1008)
        return

    await websocket.accept()
    channel = user_channel(actor.role.value, actor.id)

    events = redis_client.subscribe_chat(channel)
    pump = asyncio.create_task(_forward_events(websocket, channel, events))

    try:
        while True:
            try:
                payload = await asyncio.wait_for(
                    websocket.receive_text(), timeout=HEARTBEAT_TIMEOUT
                )
            except asyncio.TimeoutError:
                # два интервала heartbeat молчания — считаем соединение мёртвым
                logger.info("WS: heartbeat пропущен (%s), закрываем", channel)
                break

            if payload == "ping":
                await websocket.send_json({"type": "pong"})
            # всё остальное клиент отправляет через REST (§7)
    except WebSocketDisconnect:
        pass
    finally:
        pump.cancel()
        with suppress(asyncio.CancelledError, Exception):
            await pump
        # генератор подписки закрывает pubsub (unsubscribe + aclose)
        with suppress(Exception):
            await events.aclose()
