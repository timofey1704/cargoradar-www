from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from sqlalchemy import func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from client.models.enums.request_statuses import CargoRequestStatus
from client.models.request import CargoRequest
from core.models.post import Post
from executor.models.route import Route

FeedKind = Literal["route", "post", "request"]


@dataclass(slots=True)
class FeedItem:
    kind: FeedKind
    id: int
    created_at: datetime
    object: Route | Post | CargoRequest
    map_points: list["FeedMapPoint"] = field(default_factory=list)


@dataclass(slots=True)
class FeedMapPoint:
    label: str
    latitude: float
    longitude: float


class FeedRepository:
    """
    Общая лента: Route (создают водители) + Post (создают СТО и поставщики).
    Порядок и пагинация считаются на уровне БД через UNION ALL по id+kind+created_at,
    затем по этим id подгружаются полные объекты — так offset/limit работают
    корректно для смешанной ленты, а не только в рамках одной таблицы.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_feed(self, *, skip: int = 0, limit: int = 20) -> list[FeedItem]:
        route_rows = select(
            Route.id.label("id"),
            literal("route").label("kind"),
            Route.created_at.label("created_at"),
            func.ST_Y(Route.point_a_location).label("point_a_latitude"),
            func.ST_X(Route.point_a_location).label("point_a_longitude"),
            func.ST_Y(Route.point_b_location).label("point_b_latitude"),
            func.ST_X(Route.point_b_location).label("point_b_longitude"),
        ).where(Route.is_deleted.is_(False))

        post_rows = select(
            Post.id.label("id"),
            literal("post").label("kind"),
            Post.created_at.label("created_at"),
            literal(None).label("point_a_latitude"),
            literal(None).label("point_a_longitude"),
            literal(None).label("point_b_latitude"),
            literal(None).label("point_b_longitude"),
        ).where(Post.is_deleted.is_(False))

        request_rows = select(
            CargoRequest.id.label("id"),
            literal("request").label("kind"),
            CargoRequest.created_at.label("created_at"),
            func.ST_Y(CargoRequest.origin_location).label("point_a_latitude"),
            func.ST_X(CargoRequest.origin_location).label("point_a_longitude"),
            func.ST_Y(CargoRequest.destination_location).label("point_b_latitude"),
            func.ST_X(CargoRequest.destination_location).label("point_b_longitude"),
        ).where(
            CargoRequest.is_deleted.is_(False),
            CargoRequest.status == CargoRequestStatus.NEW,
        )

        union_sq = route_rows.union_all(post_rows, request_rows).subquery()

        order_stmt = (
            select(
                union_sq.c.id,
                union_sq.c.kind,
                union_sq.c.created_at,
                union_sq.c.point_a_latitude,
                union_sq.c.point_a_longitude,
                union_sq.c.point_b_latitude,
                union_sq.c.point_b_longitude,
            )
            .order_by(union_sq.c.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = (await self.session.execute(order_stmt)).all()

        route_ids = [row.id for row in rows if row.kind == "route"]
        post_ids = [row.id for row in rows if row.kind == "post"]
        request_ids = [row.id for row in rows if row.kind == "request"]

        routes_by_id: dict[int, Route] = {}
        if route_ids:
            route_res = await self.session.execute(
                select(Route).where(Route.id.in_(route_ids))
            )
            routes_by_id = {r.id: r for r in route_res.scalars().all()}

        posts_by_id: dict[int, Post] = {}
        if post_ids:
            post_res = await self.session.execute(
                select(Post).where(Post.id.in_(post_ids))
            )
            posts_by_id = {p.id: p for p in post_res.scalars().all()}

        requests_by_id: dict[int, CargoRequest] = {}
        if request_ids:
            request_res = await self.session.execute(
                select(CargoRequest).where(CargoRequest.id.in_(request_ids))
            )
            requests_by_id = {r.id: r for r in request_res.scalars().all()}

        items: list[FeedItem] = []
        for row in rows:
            if row.kind == "route":
                obj = routes_by_id.get(row.id)
            elif row.kind == "post":
                obj = posts_by_id.get(row.id)
            else:
                obj = requests_by_id.get(row.id)
            if obj is None:
                # объект удалили между двумя запросами — пропускаем
                continue
            if isinstance(obj, Route):
                map_points = [
                    FeedMapPoint(obj.point_a, float(row.point_a_latitude), float(row.point_a_longitude)),
                    FeedMapPoint(obj.point_b, float(row.point_b_latitude), float(row.point_b_longitude)),
                ]
            elif isinstance(obj, CargoRequest):
                map_points = [
                    FeedMapPoint(obj.origin_address, float(row.point_a_latitude), float(row.point_a_longitude)),
                    FeedMapPoint(obj.destination_address, float(row.point_b_latitude), float(row.point_b_longitude)),
                ]
            else:
                map_points = []
            items.append(
                FeedItem(
                    kind=row.kind,
                    id=row.id,
                    created_at=row.created_at,
                    object=obj,
                    map_points=map_points,
                )
            )
        return items

    async def count_feed(self) -> int:
        route_count_stmt = (
            select(func.count()).select_from(Route).where(Route.is_deleted.is_(False))
        )
        post_count_stmt = (
            select(func.count()).select_from(Post).where(Post.is_deleted.is_(False))
        )
        request_count_stmt = (
            select(func.count())
            .select_from(CargoRequest)
            .where(
                CargoRequest.is_deleted.is_(False),
                CargoRequest.status == CargoRequestStatus.NEW,
            )
        )
        route_count = (await self.session.execute(route_count_stmt)).scalar_one()
        post_count = (await self.session.execute(post_count_stmt)).scalar_one()
        request_count = (await self.session.execute(request_count_stmt)).scalar_one()
        return route_count + post_count + request_count