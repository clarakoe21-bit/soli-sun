from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BuildEvidence:
    canaries: dict[str, str] = field(default_factory=dict)
    critical_tests: dict[str, str] = field(default_factory=dict)
    open_s4: int = 0
    validation_status: str = "MISSING"
    traceability_status: str = "UNVERIFIED"


def release_status(evidence: BuildEvidence) -> str:
    if evidence.open_s4 > 0:
        return "BLOCKED"
    if evidence.validation_status != "CURRENT":
        return "BLOCKED"
    if evidence.traceability_status != "PASS":
        return "BLOCKED"
    if not evidence.canaries:
        return "BLOCKED"
    if any(result != "PASS" for result in evidence.canaries.values()):
        return "BLOCKED"
    if any(result != "PASS" for result in evidence.critical_tests.values()):
        return "BLOCKED"
    return "PASS"
