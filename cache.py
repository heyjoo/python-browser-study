import time
from abc import ABC, abstractmethod


class CacheEntry:
    """캐시 항목 - 응답 본문과 만료 시각을 함께 저장"""

    def __init__(self, body: str, expires_at: float):
        self.body = body
        self.expires_at = expires_at  # time.time() 기준 만료 시각


class Cache(ABC):
    """캐시 인터페이스 - 저장소 구현체를 교체할 수 있도록 추상화"""

    @abstractmethod
    def get(self, key: str) -> str | None:
        """캐시에서 값을 가져온다. 없거나 만료됐으면 None 반환."""
        ...

    @abstractmethod
    def set(self, key: str, value: str, max_age: int) -> None:
        """캐시에 값을 저장한다. max_age초 후 만료."""
        ...


class MemoryCache(Cache):
    """dict 기반 메모리 캐시 구현"""

    def __init__(self):
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> str | None:
        if key not in self._store:
            return None
        entry = self._store[key]
        if entry.expires_at <= time.time():
            del self._store[key]
            return None
        return entry.body

    def set(self, key: str, value: str, max_age: int) -> None:
        expires_at = time.time() + max_age
        self._store[key] = CacheEntry(value, expires_at)
