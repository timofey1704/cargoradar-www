from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile
from PIL import Image

from core.utils import image_upload


def _image_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(output, format="JPEG")
    return output.getvalue()


@pytest.mark.asyncio
async def test_handle_image_upload_saves_valid_image(tmp_path: Path) -> None:
    file = UploadFile(file=BytesIO(_image_bytes()), filename="photo.jpg")

    url = await image_upload.store_image_upload(
        file,
        storage_directory=tmp_path,
        public_directory="/uploads/clients/1",
    )

    filename = url.rsplit("/", 1)[-1]
    assert url == f"/uploads/clients/1/{filename}"
    assert filename.endswith(".jpg")
    assert (tmp_path / filename).read_bytes() == _image_bytes()


@pytest.mark.asyncio
async def test_handle_image_upload_rejects_non_image(tmp_path: Path) -> None:
    file = UploadFile(file=BytesIO(b"not an image"), filename="photo.jpg")

    with pytest.raises(image_upload.UnsupportedImageError):
        await image_upload.store_image_upload(
            file,
            storage_directory=tmp_path,
            public_directory="/uploads/clients/1",
        )


@pytest.mark.asyncio
async def test_handle_image_upload_rejects_oversized_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(image_upload, "MAX_IMAGE_BYTES", 4)
    file = UploadFile(file=BytesIO(_image_bytes()), filename="photo.jpg")

    with pytest.raises(image_upload.ImageTooLargeError):
        await image_upload.store_image_upload(
            file,
            storage_directory=tmp_path,
            public_directory="/uploads/clients/1",
        )