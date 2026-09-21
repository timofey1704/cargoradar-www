from typing import Tuple, cast

import redis.asyncio as aioredis


async def can_send_new_code(redis_client: aioredis.Redis, phone_number: str) -> Tuple[bool, str]:
    """
    Проверяет, можно ли отправить новый код

    Args:
        redis_client: подключение к Redis
        phone_number: Номер телефона пользователя

    Returns:
        Tuple[bool, str]: (можно отправить, сообщение об ошибке)
    """
    try:
        cooldown_key = f"verification_cooldown:{phone_number}"

        # проверяем, не отправляли ли мы код недавно
        if await redis_client.exists(cooldown_key):
            ttl = cast(int, await redis_client.ttl(cooldown_key))
            return False, f"Подождите {ttl} секунд перед повторной отправкой"

        # устанавливаем задержку в 60 секунд между отправками
        await redis_client.set(cooldown_key, "1", ex=60)
        return True, ""

    except Exception as e:
        print(f"Redis error in can_send_new_code: {str(e)}")
        return True, ""  # в случае ошибки Redis позволяем отправить код
