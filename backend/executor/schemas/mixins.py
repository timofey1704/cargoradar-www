from typing import Any

from pydantic import field_validator

from executor.models.enums.car_brands import CarBrands


class BrandsFromORMMixin:
    """Разворачивает list[XxxBrand] (relationship) в list[CarBrands] при чтении из ORM.

    Create-схемы получают brands напрямую от клиента (уже list[CarBrands]),
    поэтому для них validator — no-op.
    """

    @field_validator("brands", mode="before")
    @classmethod
    def _unwrap_brand_rows(cls, v: Any) -> Any:
        if v and hasattr(v[0], "brand"):
            return [row.brand for row in v]
        return v