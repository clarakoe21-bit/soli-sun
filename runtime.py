from __future__ import annotations

from dataclasses import dataclass

from .agentia import assess_action, decision_from_assessment
from .decision import Decision
from .response_contract import ResponseContract, build_response_contract
from .reflexio import ReflexioResult, validate_candidate
from .sensus import SensusResult, analyze


@dataclass(frozen=True)
class RuntimeResult:
    sensus: SensusResult
    decision: Decision
    contract: ResponseContract
    validation: ReflexioResult
    final_response: str | None


def process_turn(user_text: str, candidate_response: str) -> RuntimeResult:
    sensed = analyze(user_text)
    assessment = assess_action(user_text)
    decision = decision_from_assessment(assessment)
    contract = build_response_contract(decision)
    validation = validate_candidate(
        candidate_response,
        decision,
        contract,
        vulnerability_signal=sensed.vulnerability_signal,
        exclusivity_signal=sensed.exclusivity_signal,
    )
    final_response = candidate_response if validation.status == "PASS" else None
    return RuntimeResult(sensed, decision, contract, validation, final_response)
