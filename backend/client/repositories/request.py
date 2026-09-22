from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography

from client.models.request import CargoRequest, CargoRequestStatus
from executor.models.route import Route


async def find_requests_near_route(
    session: AsyncSession,
    route_id: int,
    radius_meters: float,
) -> list[CargoRequest]:
    route = await session.get(Route, route_id)
    if route is None or route.path is None:
        return []

    # route.path — уже загруженный Python-объект (WKBElement), в SQL его не подставить,
    # поэтому берём геометрию пути скалярным подзапросом по колонке routes.path: так
    # не появляется cartesian product между routes и cargo_requests.
    route_path = (
        select(sa_func.cast(Route.path, Geography))
        .where(Route.id == route_id)
        .scalar_subquery()
    )

    stmt = select(CargoRequest).where(
        sa_func.ST_DWithin(
            sa_func.cast(CargoRequest.origin_location, Geography),
            route_path,
            radius_meters,
        ),
        CargoRequest.status == CargoRequestStatus.NEW,
        CargoRequest.is_deleted.is_(False),
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())