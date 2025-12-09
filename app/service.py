from __future__ import annotations
from typing import Optional
from .models import PhoneCreate, PhoneUpdate, PhoneResponse
from .repository import PhoneRepository


class PhoneService:
    """
    Сервис для работы с логикой телефон-адрес.
    Здесь можно добавлять логи, проверки, дополнительные правила и т.п.
    """

    def __init__(self, repository: PhoneRepository) -> None:
        """
        Инициализация сервиса.
        :param repository: объект хранилища телефон-адрес.
        """
        self._repo = repository

    async def get_by_phone(self, phone: str) -> Optional[PhoneResponse]:
        """
        Получить телефон и адрес по номеру.
        :return: PhoneResponse или None, если не найден.
        """
        address = await self._repo.get(phone)
        if address is None:
            return None
        return PhoneResponse(phone=phone, address=address)

    async def create(self, data: PhoneCreate) -> bool:
        """
        Создать новую запись телефон-адрес.
        :return: True, если создано; False, если телефон уже есть.
        """
        return await self._repo.create(phone=data.phone, address=data.address)

    async def update(self, phone: str, data: PhoneUpdate) -> bool:
        """
        Обновить адрес по телефону.
        :return: True, если обновили; False, если телефон не найден.
        """
        return await self._repo.update(phone=phone, address=data.address)

    async def delete(self, phone: str) -> bool:
        """
        Удалить запись по телефону.
        :return: True, если удалили; False, если телефона не было.
        """
        return await self._repo.delete(phone=phone)
