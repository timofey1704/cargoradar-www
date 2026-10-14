from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from pydantic import Field
from sqlalchemy.exc import IntegrityError

from core.dependencies import CurrentExecutor, DbSession
from core.utils.image_upload import ImageUploadError, store_image_upload
from executor.models.enums.executor_types import ExecutorTypes
from executor.models.vehicles import VehiclePhoto
from executor.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from executor.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicles", tags=["executor vehicles"])


def _require_carrier(current: CurrentExecutor) -> None:
    if current.type != ExecutorTypes.carrier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Управлять транспортом могут только перевозчики",
        )


def _vehicle_integrity_error_detail(error: IntegrityError) -> str:
    original = error.orig
    constraint_name = getattr(original, "constraint_name", None)
    if constraint_name is None:
        constraint_name = getattr(getattr(original, "diag", None), "constraint_name", None)
    constraint_name = str(constraint_name or original).lower()

    if "license_plate" in constraint_name:
        return "Этот номерной знак уже используется другим автомобилем"
    if "vin" in constraint_name:
        return "Автомобиль с таким VIN уже существует"
    return "Номерной знак или VIN уже используются другим автомобилем"


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
            detail=_vehicle_integrity_error_detail(error),
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
            detail=_vehicle_integrity_error_detail(error),
        ) from error


@router.post("/{vehicle_id}/photos", response_model=VehicleRead)
async def upload_vehicle_photos(
    vehicle_id: int,
    current: CurrentExecutor,
    db: DbSession,
    photos: Annotated[list[UploadFile], File(...)],
) -> VehicleRead:
    _require_carrier(current)
    service = VehicleService(db)
    vehicle = await service.get_active(current.id, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")

    storage_directory = Path("uploads/vehicles") / str(current.id) / str(vehicle_id)
    public_directory = f"/uploads/vehicles/{current.id}/{vehicle_id}"
    uploaded_paths: list[Path] = []
    next_position = max((photo.position for photo in vehicle.photos), default=-1) + 1

    try:
        for offset, upload in enumerate(photos):
            image = await store_image_upload(
                upload,
                storage_directory=storage_directory,
                public_directory=public_directory,
            )
            uploaded_paths.append(storage_directory / Path(image).name)
            vehicle.photos.append(
                VehiclePhoto(image=image, position=next_position + offset)
            )
        await db.commit()
    except ImageUploadError as error:
        await db.rollback()
        for path in uploaded_paths:
            path.unlink(missing_ok=True)
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
    except Exception:
        await db.rollback()
        for path in uploaded_paths:
            path.unlink(missing_ok=True)
        raise

    return VehicleRead.model_validate(vehicle)


@router.delete("/{vehicle_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle_photo(
    vehicle_id: int,
    photo_id: int,
    current: CurrentExecutor,
    db: DbSession,
) -> Response:
    _require_carrier(current)
    vehicle = await VehicleService(db).get_active(current.id, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автомобиль не найден")

    photo = next((item for item in vehicle.photos if item.id == photo_id), None)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фото не найдено")

    image_path = Path("uploads/vehicles") / str(current.id) / str(vehicle_id) / Path(photo.image).name
    await db.delete(photo)
    await db.commit()
    image_path.unlink(missing_ok=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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