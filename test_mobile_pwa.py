import json
import threading
from http.server import ThreadingHTTPServer
from urllib import request, error

from soli_sun.model_adapter import DeterministicReferenceModel
from soli_sun.web_app import AlphaHandler


def _server(tmp_path, token=None):
    AlphaHandler.model = DeterministicReferenceModel()
    AlphaHandler.db_path = str(tmp_path / "mobile.db")
    AlphaHandler.access_token = token
    AlphaHandler.owner_id = "test_user"
    server = ThreadingHTTPServer(("127.0.0.1", 0), AlphaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def _json(url, method="GET", body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, data=data, method=method, headers=headers)
    with request.urlopen(req, timeout=3) as r:
        return r.status, json.loads(r.read().decode())


def test_pwa_manifest_and_shell_are_served(tmp_path):
    server, base = _server(tmp_path)
    try:
        with request.urlopen(base + "/", timeout=3) as r:
            html = r.read().decode()
            assert "manifest.webmanifest" in html
            assert "Mobile Alpha v0.2.0" in html
            assert r.headers["Content-Security-Policy"]
        with request.urlopen(base + "/manifest.webmanifest", timeout=3) as r:
            manifest = json.loads(r.read().decode())
            assert manifest["display"] == "standalone"
            assert manifest["name"] == "SOLI SUN"
        with request.urlopen(base + "/sw.js", timeout=3) as r:
            assert "soli-shell-v020" in r.read().decode()
    finally:
        server.shutdown(); server.server_close()


def test_access_token_protects_api_but_not_config(tmp_path):
    server, base = _server(tmp_path, token="secret-token")
    try:
        status, cfg = _json(base + "/api/config")
        assert status == 200 and cfg["auth_required"] is True
        try:
            _json(base + "/api/health")
            assert False, "expected 401"
        except error.HTTPError as exc:
            assert exc.code == 401
        status, health = _json(base + "/api/health", token="secret-token")
        assert status == 200 and health["status"] == "ok"
    finally:
        server.shutdown(); server.server_close()


def test_mobile_memory_write_list_delete_roundtrip(tmp_path):
    server, base = _server(tmp_path)
    try:
        status, created = _json(base + "/api/memories", method="POST", body={"content": "Ich mag konkrete Beispiele.", "memory_type": "PREFERENCE"})
        assert status == 201
        memory_id = created["memory_id"]
        status, listed = _json(base + "/api/memories")
        assert [m["memory_id"] for m in listed["memories"]] == [memory_id]
        status, deleted = _json(base + f"/api/memories/{memory_id}", method="DELETE")
        assert deleted["status"] == "DELETED"
        status, listed = _json(base + "/api/memories")
        assert listed["memories"] == []
    finally:
        server.shutdown(); server.server_close()


def test_chat_returns_mobile_explanation(tmp_path):
    server, base = _server(tmp_path)
    try:
        status, body = _json(base + "/api/chat", method="POST", body={"message": "Ich glaube, Mia ist sauer auf mich."})
        assert status == 200
        assert body["validation"] in {"PASS", "UNVERIFIED"}
        assert body["explanation"]
        assert "response" in body
    finally:
        server.shutdown(); server.server_close()
