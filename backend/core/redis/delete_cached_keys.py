import redis.asyncio as aioredis


async def delete_cached_keys(redis_client: aioredis.Redis, *keys: str) -> bool:
    """
    Удаляет ключи кеша (точечная инвалидация)

    Args:
        redis_client: подключение к Redis
        keys: ключи кеша, которые нужно сбросить

    Returns:
        bool: True если успешно удалено, False если произошла ошибка
    """
    try:
        if not keys:
            return True

        await redis_client.delete(*keys)
        return True

    except Exception as e:
        print(f"Redis error in delete_cached_keys: {str(e)}")
        return False
