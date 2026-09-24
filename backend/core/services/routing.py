
from typing import Any

import httpx

from core.schemas.geo import RouteData


class RoutingService:
    def __init__(
        self,
        base_url: str,
    ) -> None:
        self.base_url = base_url.rstrip("/")

    async def route(
        self,
        origin_latitude: float,
        origin_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
    ) -> RouteData:
        coordinates = (
            f"{origin_longitude},{origin_latitude};"
            f"{destination_longitude},{destination_latitude}"
        )

        params = {
            "overview": "full",
            "geometries": "geojson",
        }

        async with httpx.AsyncClient(
            timeout=10.0,
        ) as client:
            response = await client.get(
                f"{self.base_url}/route/v1/driving/"
                f"{coordinates}",
                params=params,
            )

        response.raise_for_status()

        data: dict[str, Any] = response.json()

        route = data["routes"][0]

        geometry = [
            (latitude, longitude)
            for longitude, latitude
            in route["geometry"]["coordinates"]
        ]

        return RouteData(
            distance_km=route["distance"] / 1000,
            duration_minutes=route["duration"] / 60,
            geometry=geometry,
        )
