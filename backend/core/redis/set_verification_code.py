import redis.asyncio as aioredis


async def set_verification_code(
    redis_client: aioredis.Redis,
    phone_number: str,
    code: str,
    expires_in: int = 600,
) -> bool:
    """
    Сохраняет код верификации в Redis

    Args:
        redis_client: подключение к Redis
        phone_number: Номер телефона пользователя
        code: Код верификации
        expires_in: Время жизни кода в секундах (по умолчанию 10 минут)

    Returns:
        bool: True если успешно сохранено, False если произошла ошибка
    """
    try:
        # создаем ключ для кода верификации
        verification_key = f"phone_number_verification:{phone_number}"

        # создаем ключ для счетчика попыток
        attempts_key = f"verification_attempts:{phone_number}"

        # сохраняем код с временем жизни
        await redis_client.set(verification_key, code, ex=expires_in)

        # инициализируем счетчик попыток, если его еще нет
        if not await redis_client.exists(attempts_key):
            await redis_client.set(attempts_key, "0", ex=expires_in)

        return True
    except Exception as e:
        print(f"Redis error in set_verification_code: {str(e)}")
        return False
