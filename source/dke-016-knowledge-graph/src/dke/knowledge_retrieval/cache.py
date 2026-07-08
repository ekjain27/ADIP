from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class CacheEntry(Generic[T]):
    value: T
    expires_at: float | None


class RetrievalCache(Generic[T]):
    def __init__(self, ttl_seconds: float | None = 300.0) -> None:
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, CacheEntry[T]] = {}

    def get(self, key: str) -> T | None:
        entry = self._items.get(key)
        if entry is None:
            return None
        if entry.expires_at is not None and entry.expires_at < monotonic():
            self._items.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: T) -> None:
        expires_at = None if self.ttl_seconds is None else monotonic() + self.ttl_seconds
        self._items[key] = CacheEntry(value=value, expires_at=expires_at)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        expired = [key for key, entry in self._items.items() if entry.expires_at is not None and entry.expires_at < monotonic()]
        for key in expired:
            self._items.pop(key, None)
        return len(self._items)
