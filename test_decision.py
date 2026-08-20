import pytest

from soli_sun.decision import Decision, DecisionOutcome, DecisionTransitionError, validate_decision_transition


def test_denied_cannot_become_allow():
    old = Decision("a1", DecisionOutcome.DENIED, terminal=True)
    new = Decision("a1", DecisionOutcome.ALLOW)
    with pytest.raises(DecisionTransitionError, match="POL01_DENIED_TO_ALLOW"):
        validate_decision_transition(old, new)


def test_safety_cannot_be_downgraded():
    old = Decision("a1", DecisionOutcome.SAFETY, terminal=True)
    new = Decision("a1", DecisionOutcome.DENIED, terminal=True)
    with pytest.raises(DecisionTransitionError, match="SAF01_TERMINAL_DECISION_DOWNGRADE"):
        validate_decision_transition(old, new)
