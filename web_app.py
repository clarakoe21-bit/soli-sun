from __future__ import annotations

import hmac
import json
import mimetypes
import os
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from urllib.parse import urlparse

from .live_runtime import process_live_turn
from .memory import Memory, MemoryType
from .model_adapter import DeterministicReferenceModel, OpenAIResponsesModel
from .sqlite_store import SQLiteStore


STATIC_ROOT = files("soli_sun").joinpath("static")


class AlphaHandler(BaseHTTPRequestHandler):
    model = DeterministicReferenceModel()
    db_path = ":memory:"
    access_token: str | None = None
    owner_id = "mobile_user"

    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    }

    def _send_headers(self) -> None:
        for k, v in self.security_headers.items():
            self.send_header(k, v)

    def _json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self._send_headers()
        self.end_headers()
        self.wfile.write(data)

    def _authorized(self) -> bool:
        if not self.access_token:
            return True
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {self.access_token}"
        return hmac.compare_digest(supplied, expected)

    def _require_auth(self) -> bool:
        if self._authorized():
            return True
        self._json(401, {"error": "unauthorized"})
        return False

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("request_too_large")
        return json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    def _store(self) -> SQLiteStore:
        return SQLiteStore(self.db_path)

    def _serve_static(self, path: str) -> bool:
        rel = "index.html" if path == "/" else path.lstrip("/")
        if ".." in Path(rel).parts:
            return False
        resource = STATIC_ROOT.joinpath(rel)
        try:
            data = resource.read_bytes()
        except (FileNotFoundError, IsADirectoryError):
            return False
        ctype, _ = mimetypes.guess_type(rel)
        if rel.endswith(".webmanifest"):
            ctype = "application/manifest+json"
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache" if rel in {"index.html", "sw.js"} else "public, max-age=3600")
        self._send_headers()
        self.end_headers()
        self.wfile.write(data)
        return True

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/config":
            self._json(200, {"auth_required": bool(self.access_token), "model": getattr(self.model, "name", "unknown"), "pwa": True})
            return
        if path == "/api/health":
            if not self._require_auth(): return
            self._json(200, {"status": "ok", "model": getattr(self.model, "name", "unknown")})
            return
        if path == "/api/memories":
            if not self._require_auth(): return
            store = self._store()
            try:
                memories = [
                    {"memory_id": m.memory_id, "memory_type": m.memory_type.value, "content": m.content, "source_type": m.source_type, "sensitivity": m.sensitivity}
                    for m in store.list_active_memories(self.owner_id)
                ]
            finally:
                store.close()
            self._json(200, {"memories": memories})
            return
        if path.startswith("/api/"):
            self._json(404, {"error": "not_found"})
            return
        if self._serve_static(path):
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self):  # noqa: N802
        path = urlparse(self.path).path
        if not self._require_auth(): return
        try:
            payload = self._body()
            if path == "/api/chat":
                message = str(payload.get("message", "")).strip()
                if not message:
                    self._json(400, {"error": "message_required"}); return
                result = process_live_turn(message, self.model, build_requested=message.casefold() in {"los", "weiter", "mach weiter"})
                explanation = self._explanation(result)
                self._json(200, {"run_id": result.run_id, "response": result.final_response, "mode": result.personality.mode.value, "validation": result.validation.status, "explanation": explanation})
                return
            if path == "/api/memories":
                content = str(payload.get("content", "")).strip()
                if not content:
                    self._json(400, {"error": "content_required"}); return
                try:
                    mem_type = MemoryType(str(payload.get("memory_type", "PREFERENCE")))
                except ValueError:
                    self._json(400, {"error": "invalid_memory_type"}); return
                memory = Memory(memory_id=f"mem_{uuid.uuid4().hex[:12]}", owner_id=self.owner_id, memory_type=mem_type, content=content[:1000], source_type="USER_EXPLICIT")
                store = self._store()
                try: store.write_memory(memory)
                finally: store.close()
                self._json(201, {"memory_id": memory.memory_id, "status": "ACTIVE"})
                return
            self._json(404, {"error": "not_found"})
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except Exception:
            self._json(500, {"error": "internal_error"})

    def do_DELETE(self):  # noqa: N802
        path = urlparse(self.path).path
        if not self._require_auth(): return
        prefix = "/api/memories/"
        if not path.startswith(prefix):
            self._json(404, {"error": "not_found"}); return
        memory_id = path[len(prefix):].strip()
        if not memory_id:
            self._json(400, {"error": "memory_id_required"}); return
        store = self._store()
        try: store.delete_memory(memory_id)
        finally: store.close()
        self._json(200, {"memory_id": memory_id, "status": "DELETED"})

    @staticmethod
    def _explanation(result) -> str:
        if result.validation.status != "PASS":
            return "Die Kandidatenantwort hat die Endprüfung nicht bestanden; deshalb wurde eine sichere Fallback-Antwort verwendet."
        if result.contract.objective.value == "REDIRECT":
            return "Die angefragte Methode wurde begrenzt, während ein legitimes zugrunde liegendes Ziel erhalten bleibt."
        if result.contract.objective.value == "DEESCALATE":
            return "Die Situation wurde als sicherheitsrelevant eingeordnet; deshalb priorisiert SOLI Abstand und Deeskalation."
        if result.sensus.claims:
            return "SOLI trennt Aussagen, Vermutungen und Beobachtungen, bevor sie daraus eine Antwort bildet."
        return "SOLI hat die Anfrage im normalen Hilfepfad verarbeitet und die Antwort vor der Ausgabe validiert."

    def log_message(self, format: str, *args) -> None:
        return


def build_model(provider: str):
    if provider == "openai":
        return OpenAIResponsesModel.from_env()
    return DeterministicReferenceModel()


def serve(host: str = "127.0.0.1", port: int = 8765, provider: str = "reference", *, db_path: str | None = None, access_token: str | None = None) -> None:
    AlphaHandler.model = build_model(provider)
    AlphaHandler.db_path = db_path or os.getenv("SOLI_DB_PATH", "soli-sun.db")
    AlphaHandler.access_token = access_token if access_token is not None else os.getenv("SOLI_ACCESS_TOKEN")
    AlphaHandler.owner_id = os.getenv("SOLI_OWNER_ID", "mobile_user")
    server = ThreadingHTTPServer((host, port), AlphaHandler)
    print(f"SOLI SUN Mobile Alpha listening on http://{host}:{port} using {AlphaHandler.model.name}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
