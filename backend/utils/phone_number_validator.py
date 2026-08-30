"""Валидатор белорусских телефонных номеров (E164).

`BelarusPhoneNumber` принимает номер в любом формате, который умеет
распарсить libphonenumber (например, "+375 29 123-45-67"),
проверяет, что он относится к региону BY, и нормализует его
в канонический формат E164: "+375291234567".

Номер без международного кода страны (+375) не принимается.
"""

from typing import Annotated

from pydantic_extra_types.phone_numbers import PhoneNumberValidator


BelarusPhoneNumber = Annotated[
    str,
    PhoneNumberValidator(
        supported_regions=["BY"],
        number_format="E164",
    ),
]