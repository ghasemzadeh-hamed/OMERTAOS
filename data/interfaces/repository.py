from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def get(self, entity_id: str) -> T | None: ...

    @abstractmethod
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[T]: ...

    @abstractmethod
    async def save(self, entity: T) -> None: ...

    @abstractmethod
    async def delete(self, entity_id: str) -> None: ...


class UnitOfWork(ABC):
    @abstractmethod
    async def begin(self) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


class HealthcheckAdapter(ABC):
    @abstractmethod
    async def healthcheck(self) -> dict[str, Any]: ...
