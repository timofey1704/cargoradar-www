from __future__ import annotations

from typing import Any, Generic, Protocol, Sequence, Type, TypeVar, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class _ModelWithId(Protocol):
    """ORM-модель с первичным ключом `id`.

    У самого `Base` (DeclarativeBase) атрибуты не объявлены, поэтому
    типизаторы не видят `id` у `type[ModelType]`. Протокол описывает
    только типы и на работу SQLAlchemy не влияет.
    """

    id: Any


class _ModelWithSoftDelete(_ModelWithId, Protocol):
    """ORM-модель с флагом мягкого удаления `is_deleted`."""

    is_deleted: Any


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с общими CRUD-операциями.
    Конкретные репозитории наследуются от него и задают `model`.
    """

    model: Type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, obj_id: int, *, include_deleted: bool = False
    ) -> ModelType | None:
        identifiable_model = cast("type[_ModelWithId]", self.model)
        stmt = select(self.model).where(identifiable_model.id == obj_id)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            soft_delete_model = cast("type[_ModelWithSoftDelete]", self.model)
            stmt = stmt.where(soft_delete_model.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self, *, skip: int = 0, limit: int = 50, include_deleted: bool = False
    ) -> Sequence[ModelType]:
        stmt = select(self.model)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            soft_delete_model = cast("type[_ModelWithSoftDelete]", self.model)
            stmt = stmt.where(soft_delete_model.is_deleted.is_(False))
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj_id: int, **kwargs: Any) -> ModelType | None:
        obj = await self.get_by_id(obj_id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.session.flush()
        return obj

    async def soft_delete(self, obj_id: int) -> bool:
        obj = await self.get_by_id(obj_id)
        if obj is None or not hasattr(obj, "is_deleted"):
            return False
        soft_delete_obj = cast("_ModelWithSoftDelete", obj)
        soft_delete_obj.is_deleted = True
        await self.session.flush()
        return True

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, obj: ModelType) -> None:
        await self.session.refresh(obj)