"""Loopback intake for the browser extension. A per-launch token guards mutations."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading

from .engine import execute
from .model import Job
from .providers import plan


def serve(root: Path, port: int = 8765) -> None:
    token = secrets.token_urlsafe(32)
    jobs: dict[str, dict] = {}
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def _json(self, code: int, value: dict):
            data = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _authorized(self) -> bool:
            return secrets.compare_digest(self.headers.get("X-Reference-Suite-Token", ""), token)

        def do_GET(self):
            if self.path == "/health":
                self._json(200, {"status": "ok"})
                return
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            if self.path.startswith("/jobs/"):
                with lock:
                    value = jobs.get(self.path.removeprefix("/jobs/"))
                self._json(200 if value else 404, value or {"error": "not found"})
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            if self.path not in {"/plan", "/jobs"}:
                self._json(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 16384:
                    raise ValueError("invalid request size")
                data = json.loads(self.rfile.read(length))
                data["allow_hosts"] = tuple(data.get("allow_hosts") or ())
                job = Job(**data)
                if job.provider == "local":
                    raise ValueError("local file ingest is available only from the CLI or desktop GUI")
                requests = [request.asdict() for request in plan(job)]
                if self.path == "/plan":
                    self._json(200, {"job": job.asdict(), "requests": requests})
                    return
                job_id = secrets.token_hex(12)
                with lock:
                    jobs[job_id] = {"status": "running", "requests": requests}

                def work():
                    try:
                        result = execute(job, root)
                    except Exception as exc:
                        result = {"status": "failed", "error": str(exc)}
                    with lock:
                        jobs[job_id] = result

                threading.Thread(target=work, daemon=True).start()
                self._json(202, {"job_id": job_id, "requests": requests})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})

        def log_message(self, format, *args):
            return

    http = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Reference Suite listening on http://127.0.0.1:{port}")
    print(f"Browser intake token (this launch only): {token}")
    try:
        http.serve_forever()
    finally:
        http.server_close()
