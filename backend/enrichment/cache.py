from __future__ import annotations

import time
from typing import Any


class EnrichmentCache:
    """Simple in-memory cache for enrichment results with TTL."""

    def __init__(self, ttl: int = 3600) -> None:
        self._cache: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        ts, value = entry
        if time.time() - ts > self._ttl:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (time.time(), value)


# Singleton
enrichment_cache = EnrichmentCache()
