from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .observability import Event, Severity


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    FIXED = "FIXED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class Incident:
    incident_id: str
    severity: Severity
    status: IncidentStatus
    reason_codes: tuple[str, ...]
    affected_components: tuple[str, ...]
    regression_fixture_ref: str | None = None
    root_cause: str | None = None
    corrective_action: str | None = None
    preventive_action: str | None = None


class IncidentTransitionError(ValueError):
    pass


def incident_from_event(event: Event) -> Incident | None:
    if event.severity != Severity.S4 or event.status.value != "FAIL":
        return None
    return Incident(
        incident_id=f"inc_{event.event_id}",
        severity=event.severity,
        status=IncidentStatus.OPEN,
        reason_codes=event.reason_codes,
        affected_components=(event.component,),
    )


def transition(incident: Incident, new_status: IncidentStatus, **updates: str | None) -> Incident:
    order = {
        IncidentStatus.OPEN: 0,
        IncidentStatus.INVESTIGATING: 1,
        IncidentStatus.FIXED: 2,
        IncidentStatus.VERIFIED: 3,
        IncidentStatus.CLOSED: 4,
    }
    if new_status == IncidentStatus.CLOSED and incident.status != IncidentStatus.VERIFIED:
        raise IncidentTransitionError("S4_INCIDENT_MUST_BE_VERIFIED_BEFORE_CLOSE")
    if order[new_status] < order[incident.status]:
        raise IncidentTransitionError("INCIDENT_STATUS_REGRESSION")
    return replace(incident, status=new_status, **updates)
