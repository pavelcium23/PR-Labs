from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass(slots=True)
class Entry:
    key: str
    value: Any
    version: int
    updated_at: float

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


class KVStore:
    """Concurrency-safe in-memory key-value store with versioning."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._data: Dict[str, Entry] = {}
        self._version = 0

    async def set_local(self, key: str, value: Any) -> Entry:
        async with self._lock:
            self._version += 1
            entry = Entry(key=key, value=value, version=self._version, updated_at=time.time())
            self._data[key] = entry
            return entry

    async def apply_replica(self, key: str, value: Any, version: int) -> tuple[Entry, bool]:
        async with self._lock:
            current = self._data.get(key)
            if current and current.version > version:
                return current, False
            entry = Entry(key=key, value=value, version=version, updated_at=time.time())
            self._data[key] = entry
            self._version = max(self._version, version)
            return entry, True

    async def get(self, key: str) -> Optional[Entry]:
        async with self._lock:
            return self._data.get(key)

    async def snapshot(self) -> Dict[str, Dict[str, Any]]:
        async with self._lock:
            return {key: entry.to_dict() for key, entry in self._data.items()}

    async def version(self) -> int:
        async with self._lock:
            return self._version

