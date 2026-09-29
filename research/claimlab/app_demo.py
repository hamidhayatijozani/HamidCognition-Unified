from __future__ import annotations

import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .engine import Evidence, EvidenceRelation, SignalSnapshot


class SignalEvidenceStore:
    """Small real HTTP demo store proving structured signal persistence and replay."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS evidence "
                "(evidence_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            db.commit()

    def put(self, evidence: Evidence) -> dict[str, Any]:
        payload = evidence.to_dict()
        if payload["signals"] is None:
            raise ValueError("signal_snapshot evidence requires structured signals")
        with sqlite3.connect(self.db_path) as db:
            db.execute(
                "INSERT OR REPLACE INTO evidence(evidence_id,payload) VALUES(?,?)",
                (evidence.evidence_id, json.dumps(payload, sort_keys=True)),
            )
            db.commit()
        return payload

    def get(self, evidence_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as db:
            row = db.execute(
                "SELECT payload FROM evidence WHERE evidence_id=?", (evidence_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None


class Handler(BaseHTTPRequestHandler):
    store: SignalEvidenceStore

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok"})
            return
        prefix = "/evidence/"
        if self.path.startswith(prefix):
            evidence_id = self.path[len(prefix):]
            payload = self.store.get(evidence_id)
            self._json(200 if payload else 404, payload or {"error": "not_found"})
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/evidence":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length))
            signals = SignalSnapshot(**request["signals"])
            evidence = Evidence(
                evidence_id=request["id"],
                relation=EvidenceRelation(request.get("relation", "SUPPORT")),
                source=request.get("source", "signal-feed"),
                statement=request.get("statement", "signal snapshot"),
                strength=float(request.get("strength", 1.0)),
                fresh=bool(request.get("fresh", True)),
                independent=bool(request.get("independent", True)),
                signals=signals,
            )
            self._json(201, self.store.put(evidence))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8789, db_path: str = "claimlab-evidence.sqlite3"):
    Handler.store = SignalEvidenceStore(db_path)
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"ClaimLab signal evidence server listening on http://{host}:{port}", flush=True)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8789)
    parser.add_argument("--db", default="claimlab-evidence.sqlite3")
    args = parser.parse_args()
    serve(args.host, args.port, args.db)


if __name__ == "__main__":
    main()
