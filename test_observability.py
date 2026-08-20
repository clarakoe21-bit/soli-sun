import pytest

from soli_sun.observability import EventStore, EventStatus, Severity, make_event


def test_l0_event_has_no_raw_user_content_by_default():
    event = make_event(run_id="r1", component="CONSILIUM", event_type="DECISION_COMPLETED", status=EventStatus.PASS)
    assert event.contains_raw_user_content is False


def test_event_store_rejects_raw_user_content():
    store = EventStore()
    event = make_event(run_id="r1", component="SENSUS", event_type="INPUT_ACCEPTED", contains_raw_user_content=True)
    with pytest.raises(ValueError, match="OBS01_RAW_CONTENT_UNNECESSARY"):
        store.append(event)


def test_event_store_is_queryable_by_run():
    store = EventStore()
    store.append(make_event(run_id="r1", component="MEMORIA", event_type="MEMORY_DELETED", status=EventStatus.PASS))
    store.append(make_event(run_id="r2", component="REFLEXIO", event_type="FINAL_VALIDATION", status=EventStatus.FAIL, severity=Severity.S4))
    assert len(store.by_run("r1")) == 1
