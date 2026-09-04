"""Установка httpOnly-кук с JWT для клиентов и исполнителей.

Куки — основной механизм аутентификации на фронте: fetch ходит с
`credentials: 'include'`, браузер сам хранит и подставляет куки. Заголовок
`Authorization: Bearer` остаётся запасным путём (для внешних API-клиентов).

Важность для dev-окружения: фронт и API должны быть в одном site — отличие
`localhost:3000` от `127.0.0.1:8000` браузер считает cross-site и молчит
SameSite=Lax куку, поэтому в .env фронта API адрес — `http://localhost:8000`.
"""

from fastapi import Response

from core.config import settings

_ACCESS_CLIENT_COOKIE = "client_access_token"
_REFRESH_CLIENT_COOKIE = "client_refresh_token"
_ACCESS_EXECUTOR_COOKIE = "executor_access_token"
_REFRESH_EXECUTOR_COOKIE = "executor_refresh_token"


def _set_cookie(response: Response, name: str, value: str, max_age: int) -> None:
    response.set_cookie(
        key=name,
        value=value,
        max_age=max_age,
        path="/",
        secure=False,  # локальная разработка идёт по http; над https нужна True
        httponly=True,  # токены не видны из JS
        samesite="lax",
    )


def set_client_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Ставит пару httpOnly-кук access/refresh для клиента."""
    _set_cookie(
        response,
        _ACCESS_CLIENT_COOKIE,
        access_token,
        settings.access_token_expire_minutes * 60,
    )
    _set_cookie(
        response,
        _REFRESH_CLIENT_COOKIE,
        refresh_token,
        settings.refresh_token_expire_days * 24 * 60 * 60,
    )


def set_executor_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Ставит пару httpOnly-кук access/refresh для исполнителя."""
    _set_cookie(
        response,
        _ACCESS_EXECUTOR_COOKIE,
        access_token,
        settings.admin_access_token_expire_minutes * 60,
    )
    _set_cookie(
        response,
        _REFRESH_EXECUTOR_COOKIE,
        refresh_token,
        settings.admin_refresh_token_expire_days * 24 * 60 * 60,
    )


def clear_client_auth_cookies(response: Response) -> None:
    """Стирает куки клиента при logout."""
    response.delete_cookie(_ACCESS_CLIENT_COOKIE, path="/")
    response.delete_cookie(_REFRESH_CLIENT_COOKIE, path="/")


def clear_executor_auth_cookies(response: Response) -> None:
    """Стирает куки исполнителя при logout."""
    response.delete_cookie(_ACCESS_EXECUTOR_COOKIE, path="/")
    response.delete_cookie(_REFRESH_EXECUTOR_COOKIE, path="/")