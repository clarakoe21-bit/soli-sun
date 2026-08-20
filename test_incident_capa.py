import pytest

from soli_sun.capa import CAPARecord
from soli_sun.incident import IncidentStatus, IncidentTransitionError, incident_from_event, transition
from soli_sun.observability import EventStatus, Severity, make_event


def test_s4_failed_event_creates_incident():
    event = make_event(run_id="r1", component="REFLEXIO", event_type="FINAL_VALIDATION", status=EventStatus.FAIL, reason_codes=("VAL02_SAFETY_BYPASS",), severity=Severity.S4)
    incident = incident_from_event(event)
    assert incident is not None
    assert incident.status == IncidentStatus.OPEN


def test_s4_cannot_close_before_verified():
    event = make_event(run_id="r1", component="REFLEXIO", event_type="FINAL_VALIDATION", status=EventStatus.FAIL, severity=Severity.S4)
    incident = incident_from_event(event)
    with pytest.raises(IncidentTransitionError):
        transition(incident, IncidentStatus.CLOSED)


def test_full_incident_lifecycle_and_capa():
    event = make_event(run_id="r1", component="REFLEXIO", event_type="FINAL_VALIDATION", status=EventStatus.FAIL, severity=Severity.S4)
    incident = incident_from_event(event)
    incident = transition(incident, IncidentStatus.INVESTIGATING, root_cause="RC-VALIDATION")
    incident = transition(incident, IncidentStatus.FIXED, corrective_action="add validator rule")
    incident = transition(incident, IncidentStatus.VERIFIED, regression_fixture_ref="REG-001")
    incident = transition(incident, IncidentStatus.CLOSED)
    capa = CAPARecord(incident.incident_id, "RC-VALIDATION", "add validator rule", "add mutation test", "REG-001").verified()
    assert incident.status == IncidentStatus.CLOSED
    assert capa.verification_status == "PASS"
