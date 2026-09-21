from typing import Tuple, cast

import redis.asyncio as aioredis


async def verify_code(redis_client: aioredis.Redis, phone_number: str, code: str) -> Tuple[bool, str]:
    """
    Проверяет код верификации

    Args:
        redis_client: подключение к Redis
        phone_number: Номер телефона пользователя
        code: Код для проверки

    Returns:
        Tuple[bool, str]: (успех, сообщение об ошибке)
    """
    try:
        verification_key = f"phone_number_verification:{phone_number}"
        attempts_key = f"verification_attempts:{phone_number}"

        # проверяем количество попыток
        attempts_str = await redis_client.get(attempts_key)
        attempts = 0 if attempts_str is None else int(cast(str, attempts_str))

        if attempts >= 3:
            return False, "Превышено количество попыток. Запросите новый код"

        # получаем сохраненный код
        stored_code = await redis_client.get(verification_key)
        if stored_code is None:
            return False, "Код верификации истек или недействителен"

        # увеличиваем счетчик попыток
        await redis_client.incr(attempts_key)

        # проверяем код
        if cast(str, stored_code) != code:
            return False, "Неверный код верификации"

        # если код верный, удаляем все ключи
        await redis_client.delete(verification_key, attempts_key)
        return True, ""

    except Exception as e:
        print(f"Redis error in verify_code: {str(e)}")
        return False, "Ошибка проверки кода"
