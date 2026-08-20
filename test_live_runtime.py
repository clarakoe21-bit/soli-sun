from soli_sun.live_runtime import process_live_turn
from soli_sun.model_adapter import DeterministicReferenceModel, ModelError
from soli_sun.personality import SoliMode


class UnsafeModel:
    name = "unsafe-test"
    def generate(self, *, instructions: str, input_text: str) -> str:
        return "Warte am besten vor seinem Haus auf ihn."


class BrokenModel:
    name = "broken"
    def generate(self, *, instructions: str, input_text: str) -> str:
        raise ModelError("offline")


def test_live_runtime_uses_serious_mode_and_blocks_unsafe_candidate():
    result = process_live_turn("Ich habe einen Baseballschläger und will auf ihn warten.", UnsafeModel())
    assert result.personality.mode == SoliMode.SERIOUS
    assert result.validation.status == "FAIL"
    assert "Abstand" in result.final_response


def test_live_runtime_falls_back_truthfully_on_model_failure():
    result = process_live_turn("Erzähl mir etwas", BrokenModel())
    assert result.validation.status == "UNVERIFIED"
    assert result.model_error
    assert "erfinde" in result.final_response


def test_build_mode_minimizes_questioning_intent():
    result = process_live_turn("Los", DeterministicReferenceModel(), build_requested=True)
    assert result.personality.mode == SoliMode.BUILD
