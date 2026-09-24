
from fastapi import APIRouter, Query

from core.schemas.geo import (
    GeoReverseResult,
    GeoSearchResult,
    RouteData,
)
from core.services.geocoding import GeocodingService
from core.services.routing import RoutingService
from core.config import settings


router = APIRouter(
    prefix="/geo",
    tags=["Geo"],
)


geocoding_service = GeocodingService(
    base_url=settings.nominatim_url,
    user_agent=settings.nominatim_user_agent,
)

routing_service = RoutingService(
    base_url=settings.osrm_url,
)


@router.get(
    "/route",
    response_model=RouteData,
)
async def get_route(
    origin_latitude: float = Query(
        ge=-90,
        le=90,
    ),
    origin_longitude: float = Query(
        ge=-180,
        le=180,
    ),
    destination_latitude: float = Query(
        ge=-90,
        le=90,
    ),
    destination_longitude: float = Query(
        ge=-180,
        le=180,
    ),
):
    return await routing_service.route(
        origin_latitude=origin_latitude,
        origin_longitude=origin_longitude,
        destination_latitude=destination_latitude,
        destination_longitude=destination_longitude,
    )

@router.get(
    "/search",
    response_model=list[GeoSearchResult],
)
async def search_geo(
    q: str = Query(min_length=2, max_length=200),
    limit: int = Query(default=5, ge=1, le=10),
):
    return await geocoding_service.search(
        query=q,
        limit=limit,
    )


@router.get(
    "/reverse",
    response_model=GeoReverseResult,
)
async def reverse_geo(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
):
    return await geocoding_service.reverse(
        latitude=latitude,
        longitude=longitude,
    )