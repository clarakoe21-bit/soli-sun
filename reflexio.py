from __future__ import annotations

from dataclasses import dataclass

from .decision import Decision, DecisionOutcome
from .response_contract import ResponseContract
from .response_guard import validate_non_dependency, validate_non_exclusive_care, validate_safety_output
from .reason_codes import ReasonCode
from .non_domination import validate_mutual_non_domination


@dataclass(frozen=True)
class ReflexioResult:
    status: str
    action: str
    reason_codes: tuple[str, ...] = ()


def validate_candidate(
    candidate: str,
    decision: Decision,
    contract: ResponseContract,
    *,
    vulnerability_signal: bool = False,
    exclusivity_signal: bool = False,
) -> ReflexioResult:
    reasons: list[str] = []

    if decision.outcome == DecisionOutcome.SAFETY:
        result = validate_safety_output(candidate)
        if result.status != "PASS":
            reasons.append(result.reason or ReasonCode.VAL02_SAFETY_BYPASS.value)

    if vulnerability_signal:
        result = validate_non_dependency(candidate)
        if result.status != "PASS":
            reasons.append(result.reason or ReasonCode.DEP02_VULNERABILITY_EXPLOITATION.value)

    if exclusivity_signal:
        result = validate_non_exclusive_care(candidate)
        if result.status != "PASS":
            reasons.append(result.reason or ReasonCode.DEP01_EXCLUSIVITY_REINFORCEMENT.value)

    interaction = validate_mutual_non_domination(candidate)
    if interaction.status != "PASS":
        reasons.append(interaction.reason or "MND00_NON_DOMINATION")

    if reasons:
        return ReflexioResult("FAIL", "BLOCK", tuple(dict.fromkeys(reasons)))

    return ReflexioResult("PASS", "RELEASE_OUTPUT")
