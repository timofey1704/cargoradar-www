import hashlib

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from core import rate_limiter as rate_limiter_module
from core.rate_limiter import RateLimiter


class RedisStub:
    def __init__(self, result: list[float | int]) -> None:
        self.result = result
        self.eval_args: tuple[object, ...] | None = None

    async def eval(self, *args: object) -> list[float | int]:
        self.eval_args = args
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
    dependency = limiter.limit(requests_per_second=0.5, burst=4, scope="auth-login")
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

    await limiter.limit(requests_per_second=1, burst=3, scope="public-search")(
        make_request()
    )

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

    await limiter.limit(requests_per_second=1, burst=3, scope="profile")(request)

    expected_identity = hashlib.sha256(b"executor:29").hexdigest()
    assert redis_stub.eval_args is not None
    assert redis_stub.eval_args[2] == f"rate_limit:profile:{expected_identity}"


async def test_rejected_request_returns_retry_after_and_uses_burst() -> None:
    redis_stub = RedisStub([0, 0, 1.2])
    limiter = RateLimiter(redis_stub)  # type: ignore[arg-type]

    with pytest.raises(HTTPException) as error:
        await limiter.limit(requests_per_second=0.25, burst=6, scope="register")(
            make_request()
        )

    assert error.value.status_code == 429
    assert error.value.headers == {"Retry-After": "2"}
    assert redis_stub.eval_args is not None
    assert redis_stub.eval_args[3:5] == (6, 0.25)