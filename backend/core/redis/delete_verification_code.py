import redis.asyncio as aioredis


async def delete_verification_code(redis_client: aioredis.Redis, phone_number: str) -> bool:
    """
    Удаляет код верификации

    Args:
        redis_client: подключение к Redis
        phone_number: Номер телефона пользователя

    Returns:
        bool: True если успешно удалено, False если произошла ошибка
    """
    try:
        verification_key = f"phone_number_verification:{phone_number}"
        attempts_key = f"verification_attempts:{phone_number}"

        await redis_client.delete(verification_key)
        await redis_client.delete(attempts_key)

        return True

    except Exception as e:
        print(f"Redis error in delete_verification_code: {str(e)}")
        return False
