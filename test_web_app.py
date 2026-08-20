from soli_sun.web_app import build_model
from soli_sun.model_adapter import DeterministicReferenceModel


def test_reference_web_model_is_available_without_credentials():
    assert isinstance(build_model("reference"), DeterministicReferenceModel)
