from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import sqlite3
import time

try:
    from .security_authority import Authority, AuthorityError, canonical_digest, verify_authority_envelope
except ImportError:  # pragma: no cover - direct script execution
    from security_authority import Authority, AuthorityError, canonical_digest, verify_authority_envelope

AUTHORITY_SECRET = os.getenv("ACTION_GATE_AUTHORITY_SECRET")
TOOL_NONCE_DB = os.getenv("TOOL_NONCE_DB", "/data/tool_authority.db")


def _claim_nonce(nonce: str, decision_id: str, expires_at: int) -> None:
    os.makedirs(os.path.dirname(TOOL_NONCE_DB) or ".", exist_ok=True)
    con = sqlite3.connect(TOOL_NONCE_DB, timeout=5)
    try:
        con.execute("PRAGMA busy_timeout=5000")
        con.execute("CREATE TABLE IF NOT EXISTS used_authorities (nonce TEXT PRIMARY KEY, decision_id TEXT NOT NULL, expires_at INTEGER NOT NULL, used_at INTEGER NOT NULL)")
        now = int(time.time())
        con.execute("DELETE FROM used_authorities WHERE expires_at <= ?", (now,))
        con.execute("INSERT INTO used_authorities(nonce, decision_id, expires_at, used_at) VALUES (?,?,?,?)", (nonce, decision_id, expires_at, now))
        con.commit()
    except sqlite3.IntegrityError as exc:
        con.rollback()
        raise AuthorityError("nonce_reuse") from exc
    finally:
        con.close()


def verify_execution_authority(token: str | None, tenant_id: str | None, payload: dict) -> None:
    if not AUTHORITY_SECRET:
        raise AuthorityError("tool_authority_verification_not_configured")
    if not token or not tenant_id:
        raise AuthorityError("direct_tool_access_rejected")
    if not isinstance(payload.get("action"), dict) or not isinstance(payload.get("policy"), dict):
        raise AuthorityError("action_and_policy_binding_required")
    authority = Authority.from_token(token)
    secret = AUTHORITY_SECRET.encode()
    verify_authority_envelope(
        authority=authority,
        secret=secret,
        tenant_id=tenant_id,
        action_digest=canonical_digest(payload["action"]),
        used_nonces=None,
    )
    if authority.policy_digest != canonical_digest(payload["policy"]):
        raise AuthorityError("policy_binding_mismatch")
    if payload.get("tenant_id") != tenant_id:
        raise AuthorityError("tenant_mismatch")
    _claim_nonce(authority.nonce, authority.decision_id, authority.expires_at)


class Tool(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(size) or b"{}")
            if not isinstance(body, dict):
                raise AuthorityError("invalid_json_object")
        except (ValueError, json.JSONDecodeError, AuthorityError):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid_json"}')
            return
        try:
            verify_execution_authority(
                self.headers.get("X-HCJ-Execution-Authority"),
                self.headers.get("X-Tenant-ID"),
                body,
            )
        except AuthorityError:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'{"error":"execution_authority_invalid"}')
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"tool_executed": True, "received": body}).encode())


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "9000"))), Tool).serve_forever()
