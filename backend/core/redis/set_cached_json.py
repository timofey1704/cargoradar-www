import json
from typing import Any

import redis.asyncio as aioredis


async def set_cached_json(
    redis_client: aioredis.Redis,
    key: str,
    value: Any,
    ttl: int,
) -> bool:
    """
    Кладёт значение в кеш Redis как JSON с временем жизни

    Args:
        redis_client: подключение к Redis
        key: ключ кеша
        value: значение (модели Pydantic, списки, словари, примитивы)
        ttl: время жизни кеша в секундах

    Returns:
        bool: True если успешно сохранено, False если произошла ошибка
    """
    try:
        payload = json.dumps(value, ensure_ascii=False, default=str)
        await redis_client.set(key, payload, ex=ttl)
        return True

    except Exception as e:
        print(f"Redis error in set_cached_json: {str(e)}")
        return False
