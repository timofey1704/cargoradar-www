"""Общая схема страницы результатов поиска."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

ItemT = TypeVar("ItemT")


class PageRead(BaseModel, Generic[ItemT]):
    """Страница списка: элементы + данные для пагинации.

    `total` заполняется только там, где по фильтру есть дешёвый COUNT
    (например общая лента). Если count недоступен — `total=None`, а про
    следующую страницу говорит `has_more`.
    """

    items: list[ItemT] = Field(default_factory=list)
    total: int | None = None
    skip: int
    limit: int
    has_more: bool
