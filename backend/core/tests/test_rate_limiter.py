import hashlib

import pytest
from fastapi import HTTPException, Response
from redis.exceptions import RedisError
from starlette.requests import Request

from core import rate_limiter as rate_limiter_module
from core.rate_limiter import RateLimiter
from core.schemas.common_auth_credentials import CommonCredentialsFields
from client.routes import auth as client_auth
from executor.routes import auth as executor_auth


class RedisStub:
    def __init__(
        self,
        result: list[float | int] | None = None,
        error: RedisError | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.eval_args: tuple[object, ...] | None = None

    async def eval(self, *args: object) -> list[float | int]:
        self.eval_args = args
        if self.error:
            raise self.error
        assert self.result is not None
        return self.result


def make_request(*, headers: list[tuple[bytes, bytes]] | None = None) -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/auth/login",
            "raw_path": b"/auth/login",
            "query_string": b"",
            "headers": headers or [],
            "client": ("203.0.113.10", 12345),
            "server": ("test", 80),
        }
    )


@pytest.mark.parametrize(
    ("cookie_name", "role", "subject"),
    [
        ("client_access_token", "client", "17"),
        ("executor_access_token", "executor", "29"),
    ],
)
async def test_authenticated_requests_use_role_and_account_bucket(
    monkeypatch: pytest.MonkeyPatch,
    cookie_name: str,
    role: str,
    subject: str,
) -> None:
    redis_stub = RedisStub([1, 3, 0])
    limiter = RateLimiter(redis_stub)  # type: ignore[arg-type]
    monkeypatch.setattr(
        rate_limiter_module,
        "decode_token",
        lambda token, *, is_refresh: {"type": "access", "role": role, "sub": subject},
    )
    dependency = limiter.limit(
        requests_per_second=0.5,
        burst=4,
        scope="auth-login",
        fail_open=False,
    )
    request = make_request(headers=[(b"cookie", f"{cookie_name}=token".encode())])

    await dependency(request)

    expected_identity = f"{role}:{subject}"
    expected_hash = hashlib.sha256(expected_identity.encode()).hexdigest()
    assert redis_stub.eval_args is not None
    assert redis_stub.eval_args[2] == f"rate_limit:auth-login:{expected_hash}"
    assert redis_stub.eval_args[3:5] == (4, 0.5)


async def test_anonymous_requests_use_client_ip_bucket() -> None:
    redis_stub = RedisStub([1, 3, 0])
    limiter = RateLimiter(redis_stub)  # type: ignore[arg-type]

    await limiter.limit(
        requests_per_second=1,
        burst=3,
        scope="public-search",
        fail_open=True,
    )(make_request())

    expected_hash = hashlib.sha256(b"ip:203.0.113.10").hexdigest()
    assert redis_stub.eval_args is not None
    assert redis_stub.eval_args[2] == f"rate_limit:public-search:{expected_hash}"


async def test_invalid_client_cookie_does_not_hide_executor_cookie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis_stub = RedisStub([1, 3, 0])
    limiter = RateLimiter(redis_stub)  # type: ignore[arg-type]

    def decode(token: str, *, is_refresh: bool) -> dict[str, str] | None:
        if token == "executor-token":
            return {"type": "access", "role": "executor", "sub": "29"}
        return None

    monkeypatch.setattr(rate_limiter_module, "decode_token", decode)
    request = make_request(
        headers=[
            (b"cookie", b"client_access_token=expired; executor_access_token=executor-token")
        ]
    )

    await limiter.limit(
        requests_per_second=1,
        burst=3,
        scope="profile",
        fail_open=False,
    )(request)

    expected_identity = hashlib.sha256(b"executor:29").hexdigest()
    assert redis_stub.eval_args is not None
    assert redis_stub.eval_args[2] == f"rate_limit:profile:{expected_identity}"


async def test_rejected_request_returns_retry_after_and_uses_burst() -> None:
    redis_stub = RedisStub([0, 0, 1.2])
    limiter = RateLimiter(redis_stub)  # type: ignore[arg-type]

    with pytest.raises(HTTPException) as error:
        await limiter.limit(
            requests_per_second=0.25,
            burst=6,
            scope="register",
            fail_open=False,
        )(make_request())

    assert error.value.status_code == 429
    assert error.value.headers == {"Retry-After": "2"}
    assert redis_stub.eval_args is not None
    assert redis_stub.eval_args[3:5] == (6, 0.25)


async def test_untrusted_forwarded_for_header_is_ignored() -> None:
    redis_stub = RedisStub([1, 3, 0])
    limiter = RateLimiter(redis_stub)  # type: ignore[arg-type]

    await limiter.limit(
        requests_per_second=1,
        burst=3,
        scope="public-search",
        fail_open=True,
    )(
        make_request(headers=[(b"x-forwarded-for", b"198.51.100.99")])
    )

    expected_hash = hashlib.sha256(b"ip:203.0.113.10").hexdigest()
    assert redis_stub.eval_args is not None
    assert redis_stub.eval_args[2] == f"rate_limit:public-search:{expected_hash}"


@pytest.mark.parametrize(
    ("fail_open", "expected_status"),
    [(True, None), (False, 503)],
)
async def test_redis_error_obeys_explicit_failure_policy(
    fail_open: bool,
    expected_status: int | None,
) -> None:
    limiter = RateLimiter(RedisStub(error=RedisError("Redis is unavailable")))  # type: ignore[arg-type]
    dependency = limiter.limit(
        requests_per_second=1,
        burst=3,
        scope="public-search",
        fail_open=fail_open,
    )

    if expected_status is None:
        await dependency(make_request())
    else:
        with pytest.raises(HTTPException) as error:
            await dependency(make_request())
        assert error.value.status_code == expected_status


@pytest.mark.parametrize(
    ("auth_module", "scope"),
    [
        (client_auth, "client-login-account"),
        (executor_auth, "executor-login-account"),
    ],
)
async def test_login_uses_normalized_account_bucket_and_rejects_before_auth(
    monkeypatch: pytest.MonkeyPatch,
    auth_module,
    scope: str,
) -> None:
    calls: list[dict[str, object]] = []

    async def deny(**kwargs: object) -> tuple[bool, float]:
        calls.append(kwargs)
        return False, 2.1

    monkeypatch.setattr(auth_module.rate_limiter, "is_allowed", deny)
    data = CommonCredentialsFields(
        phone_number="+375 29 123-45-67",
        password="password123",
    )

    with pytest.raises(HTTPException) as error:
        await auth_module.login(data=data, db=None, response=Response())

    expected_key = auth_module.rate_limiter.build_key(
        scope=scope,
        identifier="+375291234567",
    )
    assert data.phone_number == "+375291234567"
    assert error.value.status_code == 429
    assert error.value.headers == {"Retry-After": "3"}
    assert calls == [
        {
            "key": expected_key,
            "requests_per_second": 0.02,
            "burst": 5,
        }
    ]