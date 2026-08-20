import io
import json

import pytest

from soli_sun.model_adapter import DeterministicReferenceModel, OpenAIResponsesModel, ModelError


def test_reference_model_respects_porn_boundary_and_allows_legitimate_topic_redirect():
    model = DeterministicReferenceModel()
    text = model.generate(instructions="", input_text="Mach mir einen Porno")
    assert "Pornografische Inhalte" in text
    assert "Gesundheit" in text


def test_openai_responses_adapter_extracts_raw_http_output():
    payload = {
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "Hallo von SOLI"}]}
        ]
    }

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(payload).encode()

    captured = {}
    def fake_open(req, timeout=0):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data.decode())
        return FakeResponse()

    model = OpenAIResponsesModel(api_key="test", model="example", _urlopen=fake_open)
    out = model.generate(instructions="rules", input_text="hi")
    assert out == "Hallo von SOLI"
    assert captured["url"].endswith("/responses")
    assert captured["body"]["model"] == "example"


def test_openai_model_requires_key_and_model(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SOLI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    with pytest.raises(ModelError):
        OpenAIResponsesModel.from_env()
