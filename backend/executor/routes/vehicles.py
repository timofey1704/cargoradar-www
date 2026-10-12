from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import Field
from sqlalchemy.exc import IntegrityError

from core.dependencies import CurrentExecutor, DbSession
from executor.models.enums.executor_types import ExecutorTypes
from executor.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from executor.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicles", tags=["executor vehicles"])


def _require_carrier(current: CurrentExecutor) -> None:
    if current.type != ExecutorTypes.carrier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Управлять транспортом могут только перевозчики",
        )


@router.post("", response_model=list[VehicleRead], status_code=status.HTTP_201_CREATED)
async def create_vehicles(
    cars: Annotated[list[VehicleCreate], Field(min_length=1)],
    current: CurrentExecutor,
    db: DbSession,
):
    _require_carrier(current)

    try:
        vehicles = await VehicleService(db).create_many(current.id, cars)
        await db.flush()
        response = [VehicleRead.model_validate(vehicle) for vehicle in vehicles]
        await db.commit()
        return response
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Автомобиль с таким номерным знаком или VIN уже существует",
        ) from error


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    current: CurrentExecutor,
    db: DbSession,
) -> VehicleRead:
    _require_carrier(current)
    service = VehicleService(db)

    try:
        vehicle = await service.update(current.id, vehicle_id, data)
        if vehicle is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")
        response = VehicleRead.model_validate(vehicle)
        await db.commit()
        return response
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Автомобиль с таким номерным знаком уже существует",
        ) from error


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int,
    current: CurrentExecutor,
    db: DbSession,
) -> Response:
    _require_carrier(current)
    deleted = await VehicleService(db).soft_delete(current.id, vehicle_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)