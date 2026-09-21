import redis.asyncio as aioredis


async def delete_cached_by_prefix(redis_client: aioredis.Redis, prefix: str) -> int:
    """
    Удаляет все ключи кеша по префиксу (например "cache:main:")

    Идёт через SCAN небольшими батчами, чтобы не блокировать Redis
    на больших базах.

    Args:
        redis_client: подключение к Redis
        prefix: префикс ключей кеша

    Returns:
        int: сколько ключей удалено, 0 если произошла ошибка
    """
    try:
        deleted = 0
        batch: list[str] = []

        async for key in redis_client.scan_iter(match=f"{prefix}*", count=100):
            batch.append(key)
            if len(batch) >= 100:
                deleted += await redis_client.delete(*batch)
                batch.clear()

        if batch:
            deleted += await redis_client.delete(*batch)

        return deleted

    except Exception as e:
        print(f"Redis error in delete_cached_by_prefix: {str(e)}")
        return 0
