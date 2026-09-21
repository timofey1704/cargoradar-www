"""Юнит-тесты RedisClient на фейковом подключении — реальный Redis не нужен."""

import asyncio
import time

from redis.asyncio.retry import Retry
from redis.backoff import NoBackoff

from core.config import settings
from core.redis.redis_client import RedisClient

PHONE_NUMBER = "+375291234567"
CODE = "1234"

VERIFICATION_KEY = f"phone_number_verification:{PHONE_NUMBER}"
ATTEMPTS_KEY = f"verification_attempts:{PHONE_NUMBER}"
COOLDOWN_KEY = f"verification_cooldown:{PHONE_NUMBER}"


# --- can_send_new_code -------------------------------------------------------

async def test_can_send_new_code_allows_first_send(redis_client):
    allowed, error = await redis_client.can_send_new_code(PHONE_NUMBER)

    assert allowed is True
    assert error == ""


async def test_can_send_new_code_sets_cooldown_for_60_seconds(redis_client, fake_redis):
    await redis_client.can_send_new_code(PHONE_NUMBER)

    assert await fake_redis.get(COOLDOWN_KEY) == "1"
    assert fake_redis.ttl_of(COOLDOWN_KEY) == 60


async def test_can_send_new_code_blocks_repeat_send(redis_client):
    await redis_client.can_send_new_code(PHONE_NUMBER)

    allowed, error = await redis_client.can_send_new_code(PHONE_NUMBER)

    assert allowed is False
    assert "Подождите" in error
    assert "60" in error


# --- set_verification_code ---------------------------------------------------

async def test_set_verification_code_stores_code_and_initializes_attempts(redis_client, fake_redis):
    assert await redis_client.set_verification_code(PHONE_NUMBER, CODE) is True

    assert await fake_redis.get(VERIFICATION_KEY) == CODE
    assert await fake_redis.get(ATTEMPTS_KEY) == "0"
    assert fake_redis.ttl_of(VERIFICATION_KEY) == 600
    assert fake_redis.ttl_of(ATTEMPTS_KEY) == 600


async def test_set_verification_code_uses_custom_expires_in(redis_client, fake_redis):
    await redis_client.set_verification_code(PHONE_NUMBER, CODE, expires_in=60)

    assert fake_redis.ttl_of(VERIFICATION_KEY) == 60


async def test_set_verification_code_does_not_reset_existing_attempts(redis_client, fake_redis):
    await redis_client.set_verification_code(PHONE_NUMBER, CODE)
    await redis_client.verify_code(PHONE_NUMBER, "0000")  # 1 неудачная попытка

    await redis_client.set_verification_code(PHONE_NUMBER, CODE)

    assert await fake_redis.get(ATTEMPTS_KEY) == "1"


# --- verify_code -------------------------------------------------------------

async def test_verify_code_accepts_correct_code_and_clears_keys(redis_client, fake_redis):
    await redis_client.set_verification_code(PHONE_NUMBER, CODE)

    ok, error = await redis_client.verify_code(PHONE_NUMBER, CODE)

    assert ok is True
    assert error == ""
    assert await fake_redis.exists(VERIFICATION_KEY, ATTEMPTS_KEY) == 0


async def test_verify_code_rejects_wrong_code_and_counts_attempt(redis_client, fake_redis):
    await redis_client.set_verification_code(PHONE_NUMBER, CODE)

    ok, error = await redis_client.verify_code(PHONE_NUMBER, "0000")

    assert ok is False
    assert error == "Неверный код верификации"
    assert await fake_redis.get(ATTEMPTS_KEY) == "1"


async def test_verify_code_fails_when_code_is_missing(redis_client):
    ok, error = await redis_client.verify_code(PHONE_NUMBER, CODE)

    assert ok is False
    assert error == "Код верификации истек или недействителен"


async def test_verify_code_blocks_after_three_failed_attempts(redis_client):
    await redis_client.set_verification_code(PHONE_NUMBER, CODE)
    for _ in range(3):
        await redis_client.verify_code(PHONE_NUMBER, "0000")

    ok, error = await redis_client.verify_code(PHONE_NUMBER, CODE)

    assert ok is False
    assert error == "Превышено количество попыток. Запросите новый код"


async def test_verify_code_is_invalid_after_successful_check(redis_client):
    await redis_client.set_verification_code(PHONE_NUMBER, CODE)
    assert (await redis_client.verify_code(PHONE_NUMBER, CODE))[0] is True

    ok, error = await redis_client.verify_code(PHONE_NUMBER, CODE)

    assert ok is False
    assert error == "Код верификации истек или недействителен"


# --- delete_verification_code ------------------------------------------------

async def test_delete_verification_code_clears_code_and_attempts(redis_client, fake_redis):
    await redis_client.set_verification_code(PHONE_NUMBER, CODE)

    assert await redis_client.delete_verification_code(PHONE_NUMBER) is True
    assert await fake_redis.exists(VERIFICATION_KEY, ATTEMPTS_KEY) == 0


async def test_delete_verification_code_is_ok_when_nothing_to_delete(redis_client):
    assert await redis_client.delete_verification_code(PHONE_NUMBER) is True


# --- поведение при недоступном Redis ----------------------------------------

async def test_set_verification_code_returns_false_on_redis_error(broken_redis_client):
    assert await broken_redis_client.set_verification_code(PHONE_NUMBER, CODE) is False


async def test_verify_code_returns_error_on_redis_error(broken_redis_client):
    ok, error = await broken_redis_client.verify_code(PHONE_NUMBER, CODE)

    assert ok is False
    assert error == "Ошибка проверки кода"


async def test_can_send_new_code_still_allows_send_on_redis_error(broken_redis_client):
    ok, error = await broken_redis_client.can_send_new_code(PHONE_NUMBER)

    assert ok is True
    assert error == ""


async def test_delete_verification_code_returns_false_on_redis_error(broken_redis_client):
    assert await broken_redis_client.delete_verification_code(PHONE_NUMBER) is False


# --- ретраи и таймауты: флоу регистрации не должен тормозить ------------------

def test_redis_client_retries_connection_errors_without_delay():
    """Ретраи есть (моргнувшее соединение), но backoff выключен (без пауз)."""
    client = RedisClient()

    assert settings.redis_retry_count > 0
    assert client.redis.get_retry() == Retry(NoBackoff(), settings.redis_retry_count)


def test_redis_client_uses_short_timeouts():
    client = RedisClient()
    connection_kwargs = client.redis.connection_pool.connection_kwargs

    assert connection_kwargs["socket_connect_timeout"] == settings.redis_connect_timeout
    assert connection_kwargs["socket_timeout"] == settings.redis_command_timeout


async def test_connection_error_is_retried_without_delay(monkeypatch):
    """Соединение рвётся — команда повторяется мгновенно, ответ отдаём сразу."""
    accepted = 0

    async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        nonlocal accepted
        accepted += 1
        writer.close()  # имитируем моргнувший Redis

    server = await asyncio.start_server(handler, "127.0.0.1", 0)
    monkeypatch.setattr(settings, "redis_host", "127.0.0.1")
    monkeypatch.setattr(settings, "redis_port", server.sockets[0].getsockname()[1])

    client = RedisClient()
    try:
        started = time.perf_counter()
        allowed, error = await client.can_send_new_code(PHONE_NUMBER)
        elapsed = time.perf_counter() - started
    finally:
        await client.close()
        server.close()
        await server.wait_closed()

    assert accepted >= 2, "redis-py должен был повторить команду"
    assert elapsed < 1.0, "повторы не должны вносить задержку"
    assert allowed is True  # graceful degradation из can_send_new_code
    assert error == ""


async def test_can_send_new_code_fails_fast_when_redis_is_unreachable(monkeypatch):
    """Недоступный Redis: отдаём «можно отправлять» сразу, без ожидания ретраев."""
    monkeypatch.setattr(settings, "redis_port", 6399)  # порт, где Redis не слушает

    client = RedisClient()
    started = time.perf_counter()
    allowed, error = await client.can_send_new_code(PHONE_NUMBER)
    elapsed = time.perf_counter() - started
    await client.close()

    assert allowed is True
    assert error == ""
    assert elapsed < 1.0
