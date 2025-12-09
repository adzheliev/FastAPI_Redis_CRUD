from __future__ import annotations
from typing import Optional
from redis.asyncio import Redis


class PhoneRepository:
    """
    Репозиторий для хранения связок телефон→адрес в Redis.
    Ключи хранятся в формате: phone:{номер_в_E164}
    """

    def __init__(self, redis_client: Redis) -> None:
        """
        Инициализация репозитория.
        :param redis_client: асинхронный клиент Redis.
        """
        self._redis = redis_client

    @staticmethod
    def _key(phone: str) -> str:
        """Построить ключ Redis для номера телефона."""
        return f"phone:{phone}"

    async def get(self, phone: str) -> Optional[str]:
        """
        Получить адрес по номеру телефона.
        :return: строка с адресом или None, если запись не найдена.
        """
        raw = await self._redis.get(self._key(phone))
        if raw is None:
            return None

        return raw.decode("utf-8")

    async def create(self, phone: str, address: str) -> bool:
        """
        Создать новую запись, если её ещё нет.
        Используем SETNX, чтобы не перезаписать существующее значение.
        :return: True, если запись создана; False, если телефон уже существовал.
        """
        created: bool = await self._redis.setnx(self._key(phone), address)
        return created

    async def update(self, phone: str, address: str) -> bool:
        """
        Обновить адрес для существующего телефона.
        :return: True, если обновили; False, если телефона нет.
        """
        key = self._key(phone)
        exists: int = await self._redis.exists(key)
        if not exists:
            return False

        await self._redis.set(key, address)
        return True

    async def delete(self, phone: str) -> bool:
        """
        Удалить запись по номеру телефона.
        :return: True, если удалили; False, если записи не было.
        """
        deleted: int = await self._redis.delete(self._key(phone))
        return deleted > 0
