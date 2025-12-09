from __future__ import annotations
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from redis.asyncio import Redis
from .models import (
    PhoneCreate,
    PhoneResponse,
    PhoneUpdate,
    normalize_phone,
)
from .repository import PhoneRepository
from .service import PhoneService


REDIS_URL = "redis://localhost:6379/0"


async def get_redis_client() -> Redis:
    """
    Создать и отдать асинхронный Redis-клиент.
    Клиент закрывается после обработки запроса.
    """
    client = Redis.from_url(REDIS_URL, decode_responses=False)
    try:
        yield client
    finally:
        await client.close()


def get_phone_service(
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> PhoneService:
    """
    DI-зависимость для PhoneService.
    Собирает сервис из Redis-клиента и репозитория.
    """
    repo = PhoneRepository(redis_client=redis)
    return PhoneService(repository=repo)


PhoneServiceDep = Annotated[PhoneService, Depends(get_phone_service)]


app = FastAPI(
    title="Phone-Address Service",
    version="1.0.0",
)


@app.get("/health", tags=["service"])
async def healthcheck() -> dict[str, str]:
    """Простой healthcheck для проверки, что сервер жив."""
    return {"status": "ok"}


@app.post(
    "/phones",
    response_model=PhoneResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["phones"],
)
async def create_phone(
    data: PhoneCreate,
    service: PhoneServiceDep,
) -> PhoneResponse:
    """
    Создание новой записи телефон→адрес.
    Телефон из тела нормализуется в модели (normalize_phone).
    """
    created = await service.create(data)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone already exists",
        )

    return PhoneResponse(phone=data.phone, address=data.address)


@app.get(
    "/phones/{phone}",
    response_model=PhoneResponse,
    status_code=status.HTTP_200_OK,
    tags=["phones"],
)
async def get_phone(
    phone: str,
    service: PhoneServiceDep,
) -> PhoneResponse:
    """
    Получить запись по номеру телефона.
    Номер из path нормализуем через normalize_phone.
    """
    normalized_phone = normalize_phone(phone)

    result = await service.get_by_phone(normalized_phone)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone not found",
        )
    return result


@app.put(
    "/phones/{phone}",
    response_model=PhoneResponse,
    status_code=status.HTTP_200_OK,
    tags=["phones"],
)
async def update_phone(
    phone: str,
    data: PhoneUpdate,
    service: PhoneServiceDep,
) -> PhoneResponse:
    """
    Обновление адреса для существующего телефона.
    """
    normalized_phone = normalize_phone(phone)

    updated = await service.update(normalized_phone, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone not found",
        )

    return PhoneResponse(phone=normalized_phone, address=data.address)


@app.delete(
    "/phones/{phone}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["phones"],
)
async def delete_phone(
    phone: str,
    service: PhoneServiceDep,
) -> None:
    """
    Удаление записи по номеру телефона.
    """
    normalized_phone = normalize_phone(phone)

    deleted = await service.delete(normalized_phone)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone not found",
        )

    return None
