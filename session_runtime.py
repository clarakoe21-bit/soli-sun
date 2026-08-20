from __future__ import annotations

from dataclasses import dataclass, field
import re
import uuid

from .memory import Memory, MemoryStore, MemoryType
from .observability import EventStore, EventStatus, Severity, make_event
from .runtime import process_turn


@dataclass
class SessionState:
    user_id: str = "u1"
    memories: MemoryStore = field(default_factory=MemoryStore)
    events: EventStore = field(default_factory=EventStore)
    last_topic: str | None = None
    pending_delete_memory_id: str | None = None
    last_restricted_action: str | None = None


def _run_id() -> str:
    return f"run_{uuid.uuid4().hex[:10]}"


def process_stateful_turn(state: SessionState, user_text: str, candidate_response: str) -> dict:
    run_id = _run_id()
    lower = user_text.casefold()
    memory_action = None

    # Minimal alpha reference behavior for explicit preference memory.
    if "merk dir" in lower and "entscheidung" in lower and "nacht" in lower:
        memory = Memory(
            "pref_decision_sleep",
            state.user_id,
            MemoryType.PREFERENCE,
            "Bei großen Entscheidungen schlafe ich gern eine Nacht darüber.",
            "USER_DIRECT",
        )
        state.memories.write(memory)
        memory_action = "WRITE"
        state.events.append(make_event(run_id=run_id, component="MEMORIA", event_type="MEMORY_WRITTEN", status=EventStatus.PASS))

    if "gilt für mich nicht mehr" in lower:
        replacement = Memory(
            "pref_decision_sleep_v2",
            state.user_id,
            MemoryType.PREFERENCE,
            "Diese Präferenz gilt nicht mehr.",
            "USER_DIRECT",
        )
        if state.memories.retrieve("pref_decision_sleep"):
            state.memories.correct("pref_decision_sleep", replacement)
            memory_action = "CORRECT"
            state.events.append(make_event(run_id=run_id, component="MEMORIA", event_type="MEMORY_CORRECTED", status=EventStatus.PASS))

    if re.search(r"lösch|vergiss", lower) and not lower.strip().startswith("ja"):
        target = "pref_decision_sleep_v2" if state.memories.raw_get("pref_decision_sleep_v2") else "pref_decision_sleep"
        state.pending_delete_memory_id = target
        memory_action = "DELETE_PENDING"
        state.events.append(make_event(run_id=run_id, component="MEMORIA", event_type="MEMORY_DELETE_REQUESTED", status=EventStatus.INFO))

    if state.pending_delete_memory_id and re.search(r"\bja\b.*lösch|lösch.*\bja\b", lower):
        state.memories.delete(state.pending_delete_memory_id)
        state.pending_delete_memory_id = None
        memory_action = "DELETE"
        state.events.append(make_event(run_id=run_id, component="MEMORIA", event_type="MEMORY_DELETED", status=EventStatus.PASS))

    result = process_turn(user_text, candidate_response)
    if result.decision.outcome.value in {"REDIRECT", "DENIED", "SAFETY"}:
        state.last_restricted_action = result.decision.outcome.value
    severity = Severity.NONE if result.validation.status == "PASS" else Severity.S4
    status = EventStatus.PASS if result.validation.status == "PASS" else EventStatus.FAIL
    state.events.append(make_event(
        run_id=run_id,
        component="REFLEXIO",
        event_type="FINAL_VALIDATION",
        status=status,
        reason_codes=result.validation.reason_codes,
        severity=severity,
    ))

    return {
        "run_id": run_id,
        "runtime": result,
        "memory_action": memory_action,
    }
