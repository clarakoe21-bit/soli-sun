from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .decision import Decision, DecisionOutcome
from .content_policy import assess_content, ContentDecision
from .reason_codes import ReasonCode


class ActionType(str, Enum):
    DISCUSS = "DISCUSS"
    PREPARE_COMMUNICATION = "PREPARE_COMMUNICATION"
    COVERT_MESSAGE_ACCESS = "COVERT_MESSAGE_ACCESS"
    COVERT_TRACKING = "COVERT_TRACKING"
    CONFRONTATION_PLANNING = "CONFRONTATION_PLANNING"
    PORNOGRAPHIC_GENERATION = "PORNOGRAPHIC_GENERATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ActionAssessment:
    action_id: str
    action_type: ActionType
    affects_third_party: bool
    authorization_required: bool
    authorization_present: bool
    permission: str
    reason_codes: tuple[str, ...] = ()
    underlying_goal: str | None = None


_COVERT_MESSAGE = (
    r"heimlich.*nachrichten",
    r"nachrichten.*heimlich",
    r"handy.*kontroll",
    r"private messages",
)
_COVERT_TRACKING = (r"heimlich.*standort", r"standort.*heimlich", r"track.*without", r"covert track")
_CONFRONTATION = (r"auf ihn warten", r"abfangen", r"hinterhalt")
_PORN = (r"erstelle.*porno", r"mach.*porno", r"schreib.*porno", r"generier.*porno", r"pornografische.*geschichte", r"generate.*porn", r"write.*porn")
_COMMUNICATION = (r"nachricht schreiben", r"gespräch vorbereiten", r"mit .* reden", r"ansprechen")


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(re.search(pattern, lowered) for pattern in patterns)


def classify_action(text: str) -> ActionType:
    content = assess_content(text)
    if content.decision == ContentDecision.DENY_GENERATION or _matches(text, _PORN):
        return ActionType.PORNOGRAPHIC_GENERATION
    if _matches(text, _COVERT_MESSAGE):
        return ActionType.COVERT_MESSAGE_ACCESS
    if _matches(text, _COVERT_TRACKING):
        return ActionType.COVERT_TRACKING
    if _matches(text, _CONFRONTATION):
        return ActionType.CONFRONTATION_PLANNING
    if _matches(text, _COMMUNICATION):
        return ActionType.PREPARE_COMMUNICATION
    return ActionType.DISCUSS


def assess_action(text: str, *, action_id: str = "a1", authorization_present: bool = False) -> ActionAssessment:
    action_type = classify_action(text)

    if action_type in {ActionType.COVERT_MESSAGE_ACCESS, ActionType.COVERT_TRACKING}:
        return ActionAssessment(
            action_id,
            action_type,
            affects_third_party=True,
            authorization_required=True,
            authorization_present=authorization_present,
            permission="DENIED" if not authorization_present else "ALLOWED",
            reason_codes=() if authorization_present else (ReasonCode.AGN01_NONCONSENSUAL_MONITORING.value,),
            underlying_goal="clarity_or_reassurance",
        )

    if action_type == ActionType.CONFRONTATION_PLANNING:
        return ActionAssessment(
            action_id,
            action_type,
            affects_third_party=True,
            authorization_required=False,
            authorization_present=True,
            permission="SAFETY",
            reason_codes=(ReasonCode.SAF02_VIOLENCE_OVERRIDE.value,),
            underlying_goal="resolve_conflict",
        )

    if action_type == ActionType.PORNOGRAPHIC_GENERATION:
        return ActionAssessment(
            action_id,
            action_type,
            affects_third_party=False,
            authorization_required=False,
            authorization_present=True,
            permission="DENIED",
            reason_codes=(ReasonCode.CNT01_PORNOGRAPHIC_GENERATION.value,),
            underlying_goal="sexual_content_generation",
        )

    return ActionAssessment(
        action_id,
        action_type,
        affects_third_party=action_type == ActionType.PREPARE_COMMUNICATION,
        authorization_required=False,
        authorization_present=True,
        permission="ALLOWED",
    )


def decision_from_assessment(assessment: ActionAssessment) -> Decision:
    if assessment.permission == "SAFETY":
        return Decision(assessment.action_id, DecisionOutcome.SAFETY, assessment.reason_codes, terminal=True)
    if assessment.permission == "DENIED":
        return Decision(
            assessment.action_id,
            DecisionOutcome.REDIRECT if assessment.underlying_goal else DecisionOutcome.DENIED,
            assessment.reason_codes,
            terminal=True,
            legitimate_goal_preserved=bool(assessment.underlying_goal),
        )
    return Decision(assessment.action_id, DecisionOutcome.ALLOW, assessment.reason_codes, terminal=False)
