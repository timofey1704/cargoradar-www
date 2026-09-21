import redis.asyncio as aioredis

from core.config import settings

# смс-логика лежит рядом, в этой же папке (core/redis)
from core.redis.can_send_new_code import can_send_new_code
from core.redis.delete_verification_code import delete_verification_code
from core.redis.set_verification_code import set_verification_code
from core.redis.verify_code import verify_code


class RedisClient:
    """Асинхронный клиент Redis для работы со смс-кодами верификации.

    Держит подключение к Redis и даёт единую точку входа в смс-логику:
    сохранение кода, проверка кода, cooldown между отправками и очистка.
    Сама логика живет в функциях этой же папки, класс их вызывает.
    """

    def __init__(self) -> None:
        self.redis: aioredis.Redis = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,  # используем базу данных 0 для верификации
            decode_responses=True  # автоматически декодировать ответы в строки
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


redis_client = RedisClient()
