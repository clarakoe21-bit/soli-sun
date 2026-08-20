from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DecisionOutcome(str, Enum):
    ALLOW = "ALLOW"
    REDIRECT = "REDIRECT"
    DENIED = "DENIED"
    SAFETY = "SAFETY"
    ASK = "ASK"


@dataclass(frozen=True)
class Decision:
    action_id: str
    outcome: DecisionOutcome
    reason_codes: tuple[str, ...] = ()
    terminal: bool = False
    legitimate_goal_preserved: bool = True


class DecisionTransitionError(ValueError):
    pass


def validate_decision(decision: Decision) -> None:
    if decision.outcome == DecisionOutcome.SAFETY and not decision.terminal:
        raise DecisionTransitionError("SAFETY_MUST_BE_TERMINAL")


def validate_decision_transition(old: Decision, new: Decision) -> None:
    validate_decision(old)
    validate_decision(new)
    if old.terminal and new.outcome == DecisionOutcome.ALLOW:
        raise DecisionTransitionError("POL01_DENIED_TO_ALLOW")
    if old.outcome == DecisionOutcome.SAFETY and new.outcome != DecisionOutcome.SAFETY:
        raise DecisionTransitionError("SAF01_TERMINAL_DECISION_DOWNGRADE")
