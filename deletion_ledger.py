from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DeletionRecord:
    memory_id: str
    deleted_at: datetime
    reason: str = "USER_CONFIRMED_DELETE"


class DeletionLedger:
    """Minimal deletion metadata used to prevent resurrection after restore.

    The ledger intentionally does not store the deleted personal content.
    """

    def __init__(self) -> None:
        self._records: dict[str, DeletionRecord] = {}

    def record(self, memory_id: str, *, reason: str = "USER_CONFIRMED_DELETE") -> None:
        self._records[memory_id] = DeletionRecord(memory_id, datetime.now(timezone.utc), reason)

    def contains(self, memory_id: str) -> bool:
        return memory_id in self._records

    def ids(self) -> frozenset[str]:
        return frozenset(self._records)

    def export_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._records))

    @classmethod
    def from_ids(cls, ids: tuple[str, ...] | list[str]) -> "DeletionLedger":
        ledger = cls()
        for memory_id in ids:
            ledger.record(memory_id, reason="RESTORED_TOMBSTONE")
        return ledger
