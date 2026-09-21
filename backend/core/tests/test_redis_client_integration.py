"""Интеграционные тесты RedisClient на реальном Redis.

Нужен запущенный Redis (например `docker compose up -d redis`).
Если Redis недоступен — тесты автоматически пропускаются,
поэтому обычный `pytest` работает и без него.
"""

import pytest

from core.redis.redis_client import RedisClient

pytestmark = pytest.mark.integration

PHONE_NUMBER = "+375000000099"
VERIFICATION_KEY = f"phone_number_verification:{PHONE_NUMBER}"
ATTEMPTS_KEY = f"verification_attempts:{PHONE_NUMBER}"
COOLDOWN_KEY = f"verification_cooldown:{PHONE_NUMBER}"
KEYS = (VERIFICATION_KEY, ATTEMPTS_KEY, COOLDOWN_KEY)


@pytest.fixture
async def real_redis_client():
    """Реальный RedisClient; чистит тестовые ключи до и после теста."""
    client = RedisClient()
    try:
        await client.redis.ping()
    except Exception:
        await client.close()
        pytest.skip("Redis недоступен — интеграционные тесты пропущены")

    await client.redis.delete(*KEYS)
    yield client
    await client.redis.delete(*KEYS)
    await client.close()


async def test_redis_is_available(real_redis_client):
    assert await real_redis_client.redis.ping() is True


async def test_can_send_new_code_blocks_repeat_send(real_redis_client):
    allowed, error = await real_redis_client.can_send_new_code(PHONE_NUMBER)

    assert allowed is True
    assert error == ""

    allowed, error = await real_redis_client.can_send_new_code(PHONE_NUMBER)

    assert allowed is False
    assert "Подождите" in error


async def test_full_sms_code_flow(real_redis_client):
    # 1. код сохраняется с временем жизни
    assert await real_redis_client.set_verification_code(PHONE_NUMBER, "5555") is True
    assert await real_redis_client.redis.ttl(VERIFICATION_KEY) == 600

    # 2. неверный код отклоняется и считает попытку
    ok, error = await real_redis_client.verify_code(PHONE_NUMBER, "0000")

    assert ok is False
    assert error == "Неверный код верификации"

    # 3. верный код принимается, ключи удаляются
    ok, error = await real_redis_client.verify_code(PHONE_NUMBER, "5555")

    assert ok is True
    assert error == ""
    assert await real_redis_client.redis.exists(VERIFICATION_KEY, ATTEMPTS_KEY) == 0


async def test_delete_verification_code_clears_keys(real_redis_client):
    await real_redis_client.set_verification_code(PHONE_NUMBER, "5555")

    assert await real_redis_client.delete_verification_code(PHONE_NUMBER) is True
    assert await real_redis_client.redis.exists(VERIFICATION_KEY, ATTEMPTS_KEY) == 0
