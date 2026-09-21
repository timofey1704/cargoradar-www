import json
from typing import Any

import redis.asyncio as aioredis


async def get_cached_json(redis_client: aioredis.Redis, key: str) -> Any | None:
    """
    Читает значение из кеша Redis и распаковывает его из JSON

    Args:
        redis_client: подключение к Redis
        key: ключ кеша

    Returns:
        Any | None: распакованное значение, либо None — если кеша нет
        или Redis недоступен (кеш не должен ломать запрос)
    """
    try:
        raw = await redis_client.get(key)
        if raw is None:
            return None

        return json.loads(raw)

    except Exception as e:
        print(f"Redis error in get_cached_json: {str(e)}")
        return None
