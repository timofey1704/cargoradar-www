from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio.retry import Retry
from redis.backoff import NoBackoff

from core.config import settings

from core.redis.can_send_new_code import can_send_new_code
from core.redis.chat import publish_to_participants, subscribe
from core.redis.delete_cached_by_prefix import delete_cached_by_prefix
from core.redis.delete_cached_keys import delete_cached_keys
from core.redis.delete_verification_code import delete_verification_code
from core.redis.get_cached_json import get_cached_json
from core.redis.set_cached_json import set_cached_json
from core.redis.set_verification_code import set_verification_code
from core.redis.verify_code import verify_code


class RedisClient:
    """Асинхронный клиент Redis для работы со смс-кодами верификации.

    Держит подключение к Redis и даёт единую точку входа в смс-логику:
    сохранение кода, проверка кода, cooldown между отправками и очистка.
    Сама логика живет в функциях этой же папки, класс их вызывает.
    """

    def __init__(self) -> None:
        # повторы мгновенные , их количество — settings.redis_retry_count
        self.redis: aioredis.Redis = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,  # используем базу данных 0 для верификации
            decode_responses=True,  # автоматически декодировать ответы в строки
            socket_connect_timeout=settings.redis_connect_timeout,
            socket_timeout=settings.redis_command_timeout,
            retry=Retry(NoBackoff(), settings.redis_retry_count),
        )

    async def set_verification_code(self, phone_number: str, code: str, expires_in: int = 600) -> bool:
        """Сохраняет смс-код верификации по номеру телефона.

        Returns:
            bool: True если код сохранен, False если произошла ошибка Redis
        """
        return await set_verification_code(self.redis, phone_number, code, expires_in)

    async def verify_code(self, phone_number: str, code: str) -> tuple[bool, str]:
        """Проверяет смс-код верификации.

        Returns:
            tuple[bool, str]: (успех, сообщение об ошибке)
        """
        return await verify_code(self.redis, phone_number, code)

    async def can_send_new_code(self, phone_number: str) -> tuple[bool, str]:
        """Проверяет, можно ли отправить новый смс-код.

        Returns:
            tuple[bool, str]: (можно отправить, сообщение об ошибке)
        """
        return await can_send_new_code(self.redis, phone_number)

    async def delete_verification_code(self, phone_number: str) -> bool:
        """Удаляет смс-код верификации и счетчик попыток.

        Returns:
            bool: True если успешно удалено, False если произошла ошибка Redis
        """
        return await delete_verification_code(self.redis, phone_number)

    async def close(self) -> None:
        """Закрывает пул подключений к Redis (например, на shutdown приложения)."""
        await self.redis.aclose()

    # --- кеш ответов ---------------------------------------------------------

    async def get_cached_json(self, key: str):
        """Читает значение из кеша; None — если кеша нет или Redis недоступен."""
        return await get_cached_json(self.redis, key)

    async def set_cached_json(self, key: str, value, ttl: int) -> bool:
        """Кладёт значение в кеш как JSON с временем жизни ttl секунд."""
        return await set_cached_json(self.redis, key, value, ttl)

    async def delete_cached_keys(self, *keys: str) -> bool:
        """Удаляет конкретные ключи кеша (точечная инвалидация)."""
        return await delete_cached_keys(self.redis, *keys)

    async def delete_cached_by_prefix(self, prefix: str) -> int:
        """Удаляет все ключи кеша по префиксу, возвращает количество удалённых."""
        return await delete_cached_by_prefix(self.redis, prefix)

    # --- чат: pub/sub --------------------------------------------------------

    async def publish_chat_event(
        self,
        *,
        client_id: int,
        executor_id: int,
        event_type: str,
        data: dict[str, Any],
    ) -> int:
        """Публикует событие чата обоим участникам беседы (после commit).

        Returns:
            int: сколько получателей получило событие (0 при ошибке Redis)
        """
        return await publish_to_participants(
            self.redis,
            client_id=client_id,
            executor_id=executor_id,
            event_type=event_type,
            data=data,
        )

    def subscribe_chat(self, *channels: str) -> AsyncGenerator[dict[str, Any], None]:
        """Подписка на каналы чата (async-генератор событий) для WS-хаба."""
        return subscribe(self.redis, *channels)


redis_client = RedisClient()
