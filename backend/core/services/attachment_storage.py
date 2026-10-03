"""Хранилище вложений чата: локальный диск `uploads/chat/`.

Файл принимается только после проверки сигнатуры (magic bytes) — `content_type`
от клиенту не доверяем (§9), поэтому SVG и прочие «текстовые» форматы,
которые можно вложить в HTML, отсекаются автоматически: у них нет сигнатуры
из белого списка.

Ширина/высота изображения читает Pillow: поля `width`/`height` в `Attachment`
нужны, чтобы лента не прыгала.

Модель `Attachment` создаёт сервис (core.services.chat_service): здесь только
файл и его метаданные.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile

from core.config import settings
from core.exceptions import AttachmentTooLargeError, AttachmentUnsupportedError

# каталог задаётся относительно рабочего каталога бэкенда — так же, как
# uploads/clients/ в ClientService, маунт /uploads отдаёт его статикой
UPLOAD_DIR = Path("uploads/chat")

# для проверки сигнатуры и первичного лимита размера достаточно первых килобайт
_HEAD_BYTES = 4096
_CHUNK_BYTES = 1024 * 1024


@dataclass(frozen=True, slots=True)
class StoredFile:
    """Файл на диске вместе с метаданными для строки `Attachment`."""

    url: str
    content_type: str
    size: int
    width: int | None
    height: int | None


@dataclass(frozen=True, slots=True)
class _FileType:
    extension: str  # каноническое расширение с точкой
    content_type: str
    matches: Callable[[bytes], bool]


def _is_jpeg(head: bytes) -> bool:
    return head[:3] == b"\xff\xd8\xff"


def _is_png(head: bytes) -> bool:
    return head[:8] == b"\x89PNG\r\n\x1a\n"


def _is_gif(head: bytes) -> bool:
    return head[:6] in (b"GIF87a", b"GIF89a")


def _is_webp(head: bytes) -> bool:
    return len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP"


def _is_bmp(head: bytes) -> bool:
    return head[:2] == b"BM"


def _is_iso_video(head: bytes) -> bool:
    # MP4/MOV: семейство ISO-BMFF начинается с размера блока и `ftyp`;
    # старые QuickTime-файлы — с `moov`/`mdat` на том же месте
    if len(head) < 12:
        return False
    if head[4:8] == b"ftyp":
        return True
    return head[4:8] in (b"moov", b"mdat", b"free", b"wide", b"skip")


def _is_ebml(head: bytes) -> bool:
    # WebM/Matroska: EBML-заголовок
    return head[:4] == b"\x1a\x45\xdf\xa3"


_ALLOWED_TYPES: tuple[_FileType, ...] = (
    _FileType(".jpg", "image/jpeg", _is_jpeg),
    _FileType(".png", "image/png", _is_png),
    _FileType(".gif", "image/gif", _is_gif),
    _FileType(".webp", "image/webp", _is_webp),
    _FileType(".bmp", "image/bmp", _is_bmp),
    _FileType(".mp4", "video/mp4", _is_iso_video),
    _FileType(".mov", "video/quicktime", _is_iso_video),
    _FileType(".webm", "video/webm", _is_ebml),
)

_IMAGE_EXTENSIONS = frozenset({".jpg", ".png", ".gif", ".webp", ".bmp"})


def detect_type(head: bytes) -> _FileType | None:
    """Тип файла по сигнатуре; None — не из белого списка."""
    for file_type in _ALLOWED_TYPES:
        if file_type.matches(head):
            return file_type
    return None


def image_dimensions(
    file_type: _FileType, path: Path
) -> tuple[int | None, int | None]:
    """Ширина и высота изображения (Pillow); для видео и битых файлов — (None, None).

    Битый файл с валидной сигнатурой габаритов не имеет — гасим ошибку:
    вложение сохранится, а лента просто не сможет зарезервировать место.
    """
    if file_type.extension not in _IMAGE_EXTENSIONS:
        return None, None

    try:
        with Image.open(path) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError, ValueError):
        return None, None

    return width or None, height or None


async def save_upload(file: UploadFile) -> StoredFile:
    """Сохраняет multipart-файл в `uploads/chat/` и возвращает метаданные.

    Порядок: сигнатура из белого списка → лимит размера → запись на диск →
    габариты. При отказе на диске ничего не остаётся (сироты чистить не нужно).
    """
    await file.seek(0)
    head = await file.read(_HEAD_BYTES) or b""

    file_type = detect_type(head)
    if file_type is None:
        # формат не из белого списка: SVG/HTML и прочие «текстовые» угрозы
        raise AttachmentUnsupportedError()

    limit = settings.chat_max_file_bytes
    if len(head) > limit:
        raise AttachmentTooLargeError(len(head), limit)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{file_type.extension}"
    path = UPLOAD_DIR / name
    size = 0

    try:
        with path.open("wb") as handle:
            handle.write(head)
            size = len(head)
            while True:
                chunk = await file.read(_CHUNK_BYTES)
                if not chunk:
                    break
                size += len(chunk)
                if size > limit:
                    raise AttachmentTooLargeError(size, limit)
                handle.write(chunk)
    except BaseException:
        path.unlink(missing_ok=True)
        raise

    width, height = image_dimensions(file_type, path)
    return StoredFile(
        url=f"/uploads/chat/{name}",
        content_type=file_type.content_type,
        size=size,
        width=width,
        height=height,
    )

