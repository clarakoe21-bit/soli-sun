from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Criticality(str, Enum):
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class Policy:
    policy_id: str
    title: str
    constitutional_refs: tuple[str, ...]
    criticality: Criticality = Criticality.NORMAL
    reason_codes: tuple[str, ...] = ()


POLICIES: dict[str, Policy] = {
    "POL-EPI-01": Policy("POL-EPI-01", "Belief Is Not Fact", ("C-01",), Criticality.CRITICAL, ("CLM01_UNVERIFIED_FACT_PROMOTION",)),
    "POL-MEM-02": Policy("POL-MEM-02", "Deleted Memory Isolation", ("C-04", "C-05"), Criticality.CRITICAL, ("MEM02_DELETED_MEMORY_REUSE",)),
    "POL-FID-01": Policy("POL-FID-01", "No Non-Consensual Surveillance", ("C-08", "C-10"), Criticality.HIGH, ("AGN01_NONCONSENSUAL_MONITORING",)),
    "POL-SAF-01": Policy("POL-SAF-01", "Safety Terminality", ("C-06",), Criticality.CRITICAL, ("SAF01_TERMINAL_DECISION_DOWNGRADE",)),
    "POL-RESP-02": Policy("POL-RESP-02", "Non-Exclusive Care", ("C-07",), Criticality.HIGH, ("DEP01_EXCLUSIVITY_REINFORCEMENT",)),
    "POL-CONTENT-01": Policy("POL-CONTENT-01", "No Pornographic Generation", ("C-10",), Criticality.HIGH, ("CNT01_PORNOGRAPHIC_GENERATION",)),
}


def get_policy(policy_id: str) -> Policy:
    return POLICIES[policy_id]


def validate_policy_registry() -> None:
    for key, policy in POLICIES.items():
        if key != policy.policy_id:
            raise ValueError("POLICY_ID_MISMATCH")
        if not policy.constitutional_refs:
            raise ValueError(f"POLICY_WITHOUT_CONSTITUTION:{key}")
