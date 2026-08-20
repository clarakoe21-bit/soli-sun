from soli_sun.memory import Memory, MemoryStore, MemoryStatus, MemoryType


def test_restore_does_not_resurrect_deleted_memory():
    store = MemoryStore()
    store.write(Memory("m1", "u1", MemoryType.PREFERENCE, "secret preference", "USER_DIRECT"))
    before_delete_snapshot = store.snapshot()
    store.delete("m1")

    # Reference recovery semantics: restore old data, then apply current deletion ledger.
    merged_snapshot = type(before_delete_snapshot)(
        items=before_delete_snapshot.items,
        deleted_ids=store.deletion_ledger.export_ids(),
    )
    restored = MemoryStore.restore(merged_snapshot)

    assert restored.retrieve("m1") is None
    assert restored.raw_get("m1").status == MemoryStatus.DELETED
    assert restored.raw_get("m1").personalization_allowed is False


def test_deleted_id_cannot_be_rewritten_after_restore():
    store = MemoryStore()
    store.write(Memory("m1", "u1", MemoryType.PREFERENCE, "A", "USER_DIRECT"))
    store.delete("m1")
    restored = MemoryStore.restore(store.snapshot())

    try:
        restored.write(Memory("m1", "u1", MemoryType.PREFERENCE, "B", "USER_DIRECT"))
        raised = False
    except ValueError as exc:
        raised = str(exc) == "MEM02_DELETED_MEMORY_REUSE"
    assert raised
