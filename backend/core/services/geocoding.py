from typing import Any

import httpx

from core.schemas.geo import (
    GeoReverseResult,
    GeoSearchResult,
)


class GeocodingService:
    def __init__(
        self,
        base_url: str,
        user_agent: str,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[GeoSearchResult]:
        params = {
            "q": query,
            "format": "jsonv2",
            "limit": limit,
            "addressdetails": 1,
            "accept-language": "ru",
        }

        async with httpx.AsyncClient(
            timeout=5.0,
            headers={
                "User-Agent": self.user_agent,
            },
        ) as client:
            response = await client.get(
                f"{self.base_url}/search",
                params=params,
            )

        response.raise_for_status()

        data: list[dict[str, Any]] = response.json()

        return [
            GeoSearchResult(
                place_id=str(item["place_id"]),
                display_name=item["display_name"],
                latitude=float(item["lat"]),
                longitude=float(item["lon"]),
            )
            for item in data
        ]

    async def reverse(
        self,
        latitude: float,
        longitude: float,
    ) -> GeoReverseResult:
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
            "zoom": 18,
            "accept-language": "ru",
        }

        async with httpx.AsyncClient(
            timeout=5.0,
            headers={
                "User-Agent": self.user_agent,
            },
        ) as client:
            response = await client.get(
                f"{self.base_url}/reverse",
                params=params,
            )

        response.raise_for_status()

        data: dict[str, Any] = response.json()

        return GeoReverseResult(
            address=data["display_name"],
            latitude=float(data["lat"]),
            longitude=float(data["lon"]),
        )
