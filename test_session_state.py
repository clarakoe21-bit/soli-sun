from soli_sun.decision import Decision, DecisionOutcome
from soli_sun.session_state import SessionStateModel


def test_session_state_is_separate_and_safety_is_contextual():
    state = SessionStateModel("s1", "u1")
    state.record_decision(Decision("a1", DecisionOutcome.SAFETY, terminal=True))
    assert state.safety_active is True

    safe = Decision("a2", DecisionOutcome.ALLOW)
    state.clear_safety_if_current_turn_is_safe(safe)
    assert state.safety_active is False
