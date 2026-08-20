from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import yaml

from .claim import Claim, EpistemicType, Verification, validate_claim_transition, ClaimTransitionError
from .decision import Decision, DecisionOutcome, validate_decision_transition, DecisionTransitionError
from .memory import Memory, MemoryStore, MemoryType, MemoryStatus
from .response_guard import validate_non_dependency, validate_non_exclusive_care, validate_safety_output
from .sensus import analyze


@dataclass
class CanaryResult:
    test_id: str
    status: str
    reason: str | None = None


def load_fixture(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_fixture(fixture: dict) -> CanaryResult:
    test_id = fixture["id"]
    kind = fixture["kind"]
    try:
        if kind == "claim_promotion":
            sensed = analyze(fixture["input"])
            old = sensed.claims[0]
            new = Claim(
                claim_id=old.claim_id,
                content=old.content,
                epistemic_type=EpistemicType.VERIFIED_FACT,
                verification=Verification.VERIFIED,
                source_type=old.source_type,
                subject_type=old.subject_type,
            )
            try:
                validate_claim_transition(old, new, qualified_new_evidence=False)
            except ClaimTransitionError:
                return CanaryResult(test_id, "PASS")
            return CanaryResult(test_id, "FAIL", "Promotion was not blocked")

        if kind == "decision_downgrade":
            old = Decision("a1", DecisionOutcome.DENIED, terminal=True)
            new = Decision("a1", DecisionOutcome.ALLOW, terminal=False)
            try:
                validate_decision_transition(old, new)
            except DecisionTransitionError:
                return CanaryResult(test_id, "PASS")
            return CanaryResult(test_id, "FAIL", "DENIED->ALLOW was not blocked")

        if kind == "dependency_guard":
            sensed = analyze(fixture["input"])
            if not sensed.vulnerability_signal or not sensed.exclusivity_signal:
                return CanaryResult(test_id, "FAIL", "SENSUS missed vulnerability/exclusivity signal")
            check = validate_non_dependency(fixture["candidate_response"])
            return CanaryResult(test_id, check.status, check.reason)

        if kind == "exclusivity_guard":
            sensed = analyze(fixture["input"])
            if not sensed.exclusivity_signal:
                return CanaryResult(test_id, "FAIL", "SENSUS missed exclusivity signal")
            check = validate_non_exclusive_care(fixture["candidate_response"])
            return CanaryResult(test_id, check.status, check.reason)

        if kind == "deleted_memory_reuse":
            store = MemoryStore()
            m = Memory("m1", "u1", MemoryType.PREFERENCE, fixture["memory"], "USER_DIRECT")
            store.write(m)
            store.delete("m1")
            if store.retrieve("m1") is None:
                return CanaryResult(test_id, "PASS")
            return CanaryResult(test_id, "FAIL", "Deleted memory was retrievable")

        if kind == "correction_propagation":
            store = MemoryStore()
            old = Memory("m1", "u1", MemoryType.USER_EXPLICIT_FACT, fixture["old_memory"], "USER_DIRECT")
            new = Memory("m2", "u1", MemoryType.USER_EXPLICIT_FACT, fixture["corrected_memory"], "USER_DIRECT")
            store.write(old)
            store.correct("m1", new)
            old_raw = store.raw_get("m1")
            new_active = store.retrieve("m2")
            if old_raw and old_raw.status == MemoryStatus.SUPERSEDED and new_active and new_active.content == fixture["corrected_memory"]:
                return CanaryResult(test_id, "PASS")
            return CanaryResult(test_id, "FAIL", "Correction did not propagate")

        if kind == "safety_output_guard":
            check = validate_safety_output(fixture["candidate_response"])
            return CanaryResult(test_id, check.status, check.reason)

        return CanaryResult(test_id, "UNVERIFIED", f"Unknown fixture kind: {kind}")
    except Exception as exc:  # fail visibly, never silently green
        return CanaryResult(test_id, "FAIL", str(exc))
