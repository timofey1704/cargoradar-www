from pydantic import BaseModel, Field


class GeoSearchResult(BaseModel):
    place_id: str
    display_name: str
    latitude: float
    longitude: float


class GeoReverseResult(BaseModel):
    address: str
    latitude: float
    longitude: float


class GeoSearchQuery(BaseModel):
    q: str = Field(min_length=2, max_length=200)
    limit: int = Field(default=5, ge=1, le=10)


class GeoReverseQuery(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

class RouteData(BaseModel):
    distance_km: float
    duration_minutes: float
    geometry: list[tuple[float, float]]