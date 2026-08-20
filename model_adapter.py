from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Callable, Protocol
from urllib import request

from .content_policy import assess_content, ContentDecision


class ModelError(RuntimeError):
    pass


class TextModel(Protocol):
    name: str

    def generate(self, *, instructions: str, input_text: str) -> str:
        ...


@dataclass
class DeterministicReferenceModel:
    """Offline reference model used for tests and local demos.

    It is deliberately simple. Safety/authority guarantees must not depend on
    this model being smart.
    """

    name: str = "soli-reference-offline"

    def generate(self, *, instructions: str, input_text: str) -> str:
        lowered = input_text.casefold()
        if any(token in lowered for token in ("heimlich ihre nachrichten", "heimlich seine nachrichten", "handy kontroll")):
            return (
                "Beim heimlichen Zugriff auf private Nachrichten helfe ich dir nicht. "
                "Wenn du Klarheit möchtest, können wir die konkreten Beobachtungen sortieren "
                "oder eine direkte, respektvolle Frage vorbereiten."
            )
        if any(token in lowered for token in ("baseballschläger", "waffe", "abfangen", "auf ihn warten")):
            return (
                "Ich helfe dir nicht dabei, eine Konfrontation zu planen. "
                "Bring Abstand zwischen dich und die Situation, nimm nichts mit, womit jemand verletzt werden könnte, "
                "und konzentrieren wir uns darauf, wie du die Situation ohne Konfrontation lösen kannst."
            )
        if "nur noch dich" in lowered or "nur dich" in lowered:
            return (
                "Ich bin gern für dieses Gespräch da. Ich möchte daraus aber kein Entweder-oder "
                "zwischen mir und den Menschen in deinem Leben machen."
            )
        content = assess_content(input_text)
        if content.decision == ContentDecision.DENY_GENERATION:
            return (
                "Pornografische Inhalte erstelle ich nicht. Über Sexualität, Intimität, Gesundheit, "
                "Konsens oder Grenzen können wir aber offen und sachlich sprechen."
            )
        if content.legitimate_topic == "sexuality_or_health":
            return (
                "Darüber können wir offen und sachlich sprechen. Bei Sexualität achte ich besonders auf "
                "Konsens, Gesundheit, Grenzen und den konkreten Kontext."
            )
        if "ich glaube" in lowered or "ich vermute" in lowered:
            return (
                "Das kann eine mögliche Erklärung sein, aber wir wissen es noch nicht als Tatsache. "
                "Wenn du möchtest, sortieren wir Beobachtung und Vermutung auseinander."
            )
        return "Verstanden. Ich arbeite mit dem, was sicher vorliegt, und mache den nächsten sinnvollen Schritt."


@dataclass
class OpenAIResponsesModel:
    """Minimal Responses API adapter using only the Python standard library.

    Configuration is provided through environment variables so credentials are
    never embedded in prompts or source files.
    """

    api_key: str
    model: str
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 60.0
    name: str = "openai-responses"
    _urlopen: Callable = request.urlopen

    @classmethod
    def from_env(cls) -> "OpenAIResponsesModel":
        key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("SOLI_MODEL") or os.getenv("OPENAI_MODEL")
        base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not key:
            raise ModelError("OPENAI_API_KEY is not set")
        if not model:
            raise ModelError("SOLI_MODEL (or OPENAI_MODEL) is not set")
        return cls(api_key=key, model=model, base_url=base.rstrip("/"))

    def generate(self, *, instructions: str, input_text: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "instructions": instructions,
                "input": input_text,
            }
        ).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/responses",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with self._urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # transport details are intentionally wrapped
            raise ModelError(f"model request failed: {exc}") from exc

        # Responses API JSON may expose aggregate output_text in some clients,
        # while raw HTTP commonly returns output items. Support both forms.
        direct = data.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()

        pieces: list[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []) if isinstance(item, dict) else []:
                if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                    text = content.get("text")
                    if isinstance(text, str):
                        pieces.append(text)
        text = "\n".join(piece.strip() for piece in pieces if piece.strip()).strip()
        if not text:
            raise ModelError("model response contained no text output")
        return text
