"""Форматтер адресов Nominatim.

Nominatim в `display_name` отдаёт адрес от частного к общему:
"41, улица Одинцова, Запад, Фрунзенский район, Минск, 220018, Беларусь".
Для карточки и точки на карте такой адрес избыточен, поэтому `format_address`
оставляет только страну, город и улицу с домом: "Беларусь, Минск, Одинцова 41".

Строки, не похожие на `display_name` Nominatim (например, введённые вручную
"Минск, ул. Складская 1" или уже сокращённые), возвращаются без изменений.
"""

import re
from typing import Annotated

from pydantic import AfterValidator

# Номер дома в начале display_name: "41", "41А", "12/3", "12-3".
_HOUSE_RE = re.compile(r"^\d+[А-Яа-яA-Za-z]?(?:[/\-]\d+[А-Яа-яA-Za-z]?)?$")

# Индекс (4–10 цифр) в коротком адресе не нужен.
_POSTCODE_RE = re.compile(r"^\d{4,10}$")

# Полные названия улиц, которые пишет Nominatim (в отличие от "ул." / "пр-т").
_STREET_PREFIXES = (
    "улица",
    "проспект",
    "переулок",
    "шоссе",
    "площадь",
    "проезд",
    "бульвар",
    "набережная",
    "тракт",
    "тупик",
    "аллея",
    "микрорайон",
    "квартал",
)

# Административные единицы — в короткий адрес не входят.
_ADMIN_SUFFIXES = (
    "район",
    "область",
    "обл.",
    "округ",
    "край",
    "республика",
    "region",
    "district",
    "county",
)


def _is_house_number(part: str) -> bool:
    return bool(_HOUSE_RE.match(part))


def _is_street(part: str) -> bool:
    lowered = part.lower()
    return any(lowered.startswith(f"{prefix} ") for prefix in _STREET_PREFIXES)


def _strip_street_prefix(part: str) -> str:
    """Убирает словесный тип улицы: "улица Одинцова" -> "Одинцова"."""
    lowered = part.lower()
    for prefix in _STREET_PREFIXES:
        if lowered.startswith(f"{prefix} "):
            return part[len(prefix):].strip()
    return part


def _is_admin_area(part: str) -> bool:
    lowered = part.lower()
    return any(lowered.endswith(suffix) for suffix in _ADMIN_SUFFIXES)


def _looks_like_nominatim(parts: list[str]) -> bool:
    """display_name Nominatim узнаём по дому в начале либо по полному типу улицы и индексу."""
    if len(parts) < 3:
        return False
    if _is_house_number(parts[0]):
        return True
    has_street = any(_is_street(part) for part in parts)
    has_postcode = any(_POSTCODE_RE.match(part) for part in parts)
    return has_street and has_postcode


def _pick_city(parts: list[str]) -> str | None:
    """Город — последняя часть без индекса и административной единицы."""
    for part in reversed(parts):
        if _POSTCODE_RE.match(part) or _is_admin_area(part):
            continue
        return part
    return None


def format_address(address: str) -> str:
    """Сокращает `display_name` Nominatim до "Страна, Город, Улица Дом"."""
    parts = [part.strip() for part in address.split(",") if part.strip()]

    if not _looks_like_nominatim(parts):
        return address

    country = parts[-1]
    rest = parts[:-1]

    house: str | None = None
    if rest and _is_house_number(rest[0]):
        house, rest = rest[0], rest[1:]

    street: str | None = None
    others: list[str] = []
    for part in rest:
        if street is None and _is_street(part):
            street = _strip_street_prefix(part)
        else:
            others.append(part)

    city = _pick_city(others)

    result = [country]
    if city:
        result.append(city)
    if street:
        result.append(f"{street} {house}" if house else street)
    return ", ".join(result)


# Тип поля адреса в read-схемах: любое `display_name` Nominatim при сборке ответа
# автоматически сокращается до "Страна, Город, Улица Дом".
FormattedAddress = Annotated[str, AfterValidator(format_address)]
