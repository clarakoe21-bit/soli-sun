from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class Severity(str, Enum):
    NONE = "NONE"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


class EventStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNVERIFIED = "UNVERIFIED"
    INFO = "INFO"


@dataclass(frozen=True)
class Event:
    event_id: str
    run_id: str
    component: str
    event_type: str
    status: EventStatus
    reason_codes: tuple[str, ...] = ()
    severity: Severity = Severity.NONE
    contains_raw_user_content: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def make_event(*, run_id: str, component: str, event_type: str, status: EventStatus = EventStatus.INFO,
               reason_codes: tuple[str, ...] = (), severity: Severity = Severity.NONE,
               contains_raw_user_content: bool = False) -> Event:
    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:12]}",
        run_id=run_id,
        component=component,
        event_type=event_type,
        status=status,
        reason_codes=reason_codes,
        severity=severity,
        contains_raw_user_content=contains_raw_user_content,
    )


class EventStore:
    """Operational telemetry only. Not a personalization memory source."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def append(self, event: Event) -> None:
        if event.contains_raw_user_content:
            raise ValueError("OBS01_RAW_CONTENT_UNNECESSARY")
        self._events.append(event)

    def by_run(self, run_id: str) -> tuple[Event, ...]:
        return tuple(event for event in self._events if event.run_id == run_id)

    def all(self) -> tuple[Event, ...]:
        return tuple(self._events)
