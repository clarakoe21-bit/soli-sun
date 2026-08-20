from soli_sun.memory import Memory, MemoryStore, MemoryStatus, MemoryType


def test_deleted_memory_not_retrievable():
    store = MemoryStore()
    memory = Memory("m1", "u1", MemoryType.PREFERENCE, "Ich mag kurze Antworten.", "USER_DIRECT")
    store.write(memory)
    store.delete("m1")

    assert store.retrieve("m1") is None
    assert store.raw_get("m1").status == MemoryStatus.DELETED
    assert store.raw_get("m1").personalization_allowed is False


def test_deleted_id_cannot_be_rewritten():
    store = MemoryStore()
    memory = Memory("m1", "u1", MemoryType.PREFERENCE, "A", "USER_DIRECT")
    store.write(memory)
    store.delete("m1")

    replacement = Memory("m1", "u1", MemoryType.PREFERENCE, "B", "USER_DIRECT")
    try:
        store.write(replacement)
        raised = False
    except ValueError as exc:
        raised = str(exc) == "MEM02_DELETED_MEMORY_REUSE"
    assert raised
