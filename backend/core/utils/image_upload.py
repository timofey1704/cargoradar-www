from __future__ import annotations

import uuid
import warnings
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.ext.asyncio import AsyncSession


MAX_IMAGE_BYTES = 10 * 1024 * 1024
_IMAGE_FORMATS = {
	"JPEG": ".jpg",
	"PNG": ".png",
	"GIF": ".gif",
	"WEBP": ".webp",
	"BMP": ".bmp",
}


class ImageUploadError(Exception):
	status_code = 400


class ImageTooLargeError(ImageUploadError):
	status_code = 413


class UnsupportedImageError(ImageUploadError):
	status_code = 415


async def store_image_upload(
	file: UploadFile,
	*,
	storage_directory: Path,
	public_directory: str,
) -> str:
	"""Validate and store an image, returning its public URL."""
	content = await file.read(MAX_IMAGE_BYTES + 1)
	if len(content) > MAX_IMAGE_BYTES:
		raise ImageTooLargeError("Размер изображения не должен превышать 10 МБ")

	try:
		with warnings.catch_warnings():
			warnings.simplefilter("error", Image.DecompressionBombWarning)
			with Image.open(BytesIO(content)) as image:
				extension = _IMAGE_FORMATS.get(image.format or "")
				if extension is None:
					raise UnsupportedImageError("Поддерживаются JPEG, PNG, GIF, WEBP и BMP")
				image.verify()
	except UnsupportedImageError:
		raise
	except (Image.DecompressionBombError, Image.DecompressionBombWarning, OSError, UnidentifiedImageError, ValueError) as exc:
		raise UnsupportedImageError("Файл не является корректным изображением") from exc

	storage_directory.mkdir(parents=True, exist_ok=True)
	filename = f"{uuid.uuid4().hex}{extension}"
	(storage_directory / filename).write_bytes(content)
	return f"{public_directory.rstrip('/')}/{filename}"


async def handle_image_upload(
	file: UploadFile,
	*,
	entity: Any,
	field_name: str,
	db: AsyncSession,
	storage_directory: Path,
	public_directory: str,
) -> str:
	try:
		image_url = await store_image_upload(
			file,
			storage_directory=storage_directory,
			public_directory=public_directory,
		)
	except ImageUploadError as exc:
		raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

	setattr(entity, field_name, image_url)
	try:
		await db.commit()
		await db.refresh(entity)
	except Exception:
		await db.rollback()
		(storage_directory / Path(image_url).name).unlink(missing_ok=True)
		raise

	return image_url
