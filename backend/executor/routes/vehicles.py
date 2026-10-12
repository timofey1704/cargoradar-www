from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from pydantic import Field
from sqlalchemy.exc import IntegrityError

from core.dependencies import CurrentExecutor, DbSession
from executor.models.enums.executor_types import ExecutorTypes
from executor.schemas.vehicle import VehicleCreate, VehicleRead
from executor.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicles", tags=["executor vehicles"])


@router.post("", response_model=list[VehicleRead], status_code=status.HTTP_201_CREATED)
async def create_vehicles(
    cars: Annotated[list[VehicleCreate], Field(min_length=1)],
    current: CurrentExecutor,
    db: DbSession,
):
    if current.type != ExecutorTypes.carrier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Добавлять транспорт могут только перевозчики",
        )

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