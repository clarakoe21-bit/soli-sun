from pathlib import Path

import pytest

from soli_sun.memory import Memory, MemoryType
from soli_sun.sqlite_store import SQLiteStore


def test_sqlite_delete_ledger_blocks_repersonalization(tmp_path: Path):
    db = SQLiteStore(tmp_path / "soli.db")
    memory = Memory("m1", "u1", MemoryType.PREFERENCE, "Mag kurze Antworten", "USER_DIRECT")
    db.write_memory(memory)
    assert db.get_memory("m1") is not None
    db.delete_memory("m1")
    assert db.get_memory("m1") is None
    assert "m1" in db.deletion_ids()
    with pytest.raises(ValueError):
        db.write_memory(memory)
    db.close()


def test_sqlite_active_memories_are_owner_scoped(tmp_path: Path):
    db = SQLiteStore(tmp_path / "soli.db")
    db.write_memory(Memory("a", "u1", MemoryType.PREFERENCE, "A", "USER_DIRECT"))
    db.write_memory(Memory("b", "u2", MemoryType.PREFERENCE, "B", "USER_DIRECT"))
    assert [m.memory_id for m in db.list_active_memories("u1")] == ["a"]
    db.close()
