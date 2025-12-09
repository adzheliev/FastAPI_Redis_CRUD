from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
import phonenumbers
from phonenumbers import PhoneNumberFormat


def normalize_phone(value: str) -> str:
    """
    Нормализует и проверяет номер телефона.
    - принимает любые варианты вроде '8 (999) 123-45-67', '+7 999 1234567'
    - бросает ValueError, если номер некорректен
    - возвращает строку в формате E.164: +79991234567
    """
    value = value.strip()

    try:
        parsed = phonenumbers.parse(value, "RU")
    except phonenumbers.NumberParseException as exc:
        raise ValueError("Неверный формат номера телефона") from exc

    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Некорректный номер телефона")

    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)


class PhoneBase(BaseModel):
    """Базовая схема с номером телефона с валидацией и нормализацией."""

    phone: str = Field(
        ...,
        description="Номер телефона в международном формате (E.164)",
        example="+79991234567",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """
        Валидация и нормализация номера телефона для body.
        Использует общую функцию normalize_phone.
        """
        return normalize_phone(value)


class PhoneCreate(PhoneBase):
    """DTO для создания записи телефон→адрес (POST /phones)."""

    address: str = Field(
        ...,
        description="Адрес клиента",
        example="Moscow, Red Square, 1",
        max_length=255,
    )


class PhoneResponse(PhoneBase):
    """DTO для ответа API — телефон + адрес (GET/POST/PUT)."""

    address: str = Field(
        ...,
        description="Адрес клиента",
        max_length=255,
    )


class PhoneUpdate(BaseModel):
    """DTO для обновления адреса (PUT /phones/{phone})."""

    address: str = Field(
        ...,
        description="Новый адрес клиента",
        example="Saint Petersburg, Nevsky 10",
        max_length=255,
    )
