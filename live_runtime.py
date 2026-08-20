from __future__ import annotations

from dataclasses import dataclass
import uuid

from .agentia import assess_action, decision_from_assessment
from .model_adapter import TextModel, ModelError
from .observability import EventStore, EventStatus, Severity, make_event
from .personality import PersonalityState, choose_mode, instructions_for
from .reflexio import ReflexioResult, validate_candidate
from .response_contract import ResponseContract, build_response_contract
from .sensus import SensusResult, analyze


@dataclass(frozen=True)
class LiveTurnResult:
    run_id: str
    sensus: SensusResult
    personality: PersonalityState
    contract: ResponseContract
    candidate_response: str | None
    validation: ReflexioResult
    final_response: str
    model_error: str | None = None


def _contract_text(contract: ResponseContract) -> str:
    return (
        f"Decision objective: {contract.objective.value}. "
        f"Required behaviors: {', '.join(contract.required_behaviors) or 'none'}. "
        f"Forbidden behaviors: {', '.join(contract.forbidden_behaviors) or 'none'}. "
        f"Preserve legitimate goal: {contract.preserve_legitimate_goal}."
    )


def safe_fallback(user_text: str, contract: ResponseContract) -> str:
    if contract.objective.value == "DEESCALATE":
        return (
            "Ich helfe dir nicht dabei, die Konfrontation vorzubereiten. Schaffe Abstand zur Situation "
            "und zu Gegenständen, mit denen jemand verletzt werden könnte. Wir können stattdessen den nächsten sicheren Schritt planen."
        )
    if contract.objective.value == "REDIRECT":
        return (
            "Bei dieser Methode helfe ich nicht. Wenn dein eigentliches Ziel Klarheit oder eine Lösung ist, "
            "können wir einen Weg wählen, der die Rechte anderer respektiert."
        )
    if contract.objective.value == "CLARIFY":
        return "Mir fehlt eine Information, die für eine verlässliche Entscheidung wirklich nötig ist."
    return "Ich kann gerade keine verlässliche Modellantwort erzeugen. Ich erfinde deshalb nichts und bleibe bei dem, was sicher feststeht."


def process_live_turn(
    user_text: str,
    model: TextModel,
    *,
    events: EventStore | None = None,
    build_requested: bool = False,
) -> LiveTurnResult:
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    event_store = events or EventStore()
    sensed = analyze(user_text)
    assessment = assess_action(user_text)
    decision = decision_from_assessment(assessment)
    contract = build_response_contract(decision)
    personality = choose_mode(
        safety_signal=sensed.safety_signal or decision.outcome.value == "SAFETY",
        vulnerability_signal=sensed.vulnerability_signal,
        build_requested=build_requested,
    )

    system_instructions = instructions_for(personality) + "\n" + _contract_text(contract)
    candidate: str | None = None
    error: str | None = None
    try:
        candidate = model.generate(instructions=system_instructions, input_text=user_text)
    except ModelError as exc:
        error = str(exc)
    except Exception as exc:
        error = f"unexpected model error: {exc}"

    if candidate is None:
        validation = ReflexioResult("UNVERIFIED", "FALLBACK", ("MODEL_UNAVAILABLE",))
        final = safe_fallback(user_text, contract)
        event_store.append(
            make_event(
                run_id=run_id,
                component="MODEL",
                event_type="MODEL_GENERATION_FAILED",
                status=EventStatus.UNVERIFIED,
                reason_codes=("MODEL_UNAVAILABLE",),
                severity=Severity.S2,
            )
        )
    else:
        validation = validate_candidate(
            candidate,
            decision,
            contract,
            vulnerability_signal=sensed.vulnerability_signal,
            exclusivity_signal=sensed.exclusivity_signal,
        )
        if validation.status == "PASS":
            final = candidate
        else:
            final = safe_fallback(user_text, contract)
        event_store.append(
            make_event(
                run_id=run_id,
                component="REFLEXIO",
                event_type="FINAL_VALIDATION",
                status=EventStatus.PASS if validation.status == "PASS" else EventStatus.FAIL,
                reason_codes=validation.reason_codes,
                severity=Severity.NONE if validation.status == "PASS" else Severity.S4,
            )
        )

    return LiveTurnResult(
        run_id=run_id,
        sensus=sensed,
        personality=personality,
        contract=contract,
        candidate_response=candidate,
        validation=validation,
        final_response=final,
        model_error=error,
    )
