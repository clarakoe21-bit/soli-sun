from soli_sun.personality import SoliMode, choose_mode, instructions_for


def test_serious_mode_turns_off_playfulness():
    state = choose_mode(safety_signal=True, vulnerability_signal=False)
    assert state.mode == SoliMode.SERIOUS
    assert state.playfulness == 0.0


def test_close_mode_preserves_warmth_without_exclusivity_instruction():
    state = choose_mode(safety_signal=False, vulnerability_signal=True)
    text = instructions_for(state)
    assert state.mode == SoliMode.CLOSE
    assert "without exclusivity" in text
