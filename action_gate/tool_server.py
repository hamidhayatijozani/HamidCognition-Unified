from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    from .security_authority import Authority, AuthorityError, canonical_digest, verify_authority_envelope
except ImportError:  # pragma: no cover - direct script execution
    from security_authority import Authority, AuthorityError, canonical_digest, verify_authority_envelope

AUTHORITY_SECRET = os.getenv("ACTION_GATE_AUTHORITY_SECRET")
TOOL_NONCE_DB = os.getenv("TOOL_NONCE_DB", "/data/tool_authority.db")
DEBUG_AUTHORITY = os.getenv("ACTION_GATE_DEBUG_AUTHORITY", "").lower() in {"1", "true", "yes"}
GATE_URL = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000").rstrip("/")

def _validated_gate_url(path: str) -> str:
    """Build a same-origin Gate URL; reject malformed or authority-changing paths."""
    base = urllib.parse.urlsplit(GATE_URL)
    if (
        base.scheme not in {"http", "https"}
        or not base.hostname
        or base.username
        or base.password
        or base.query
        or base.fragment
    ):
        raise AuthorityError("world_revalidation_invalid_url")

    if not isinstance(path, str) or not path.startswith("/") or path.startswith("//") or chr(92) in path:
        raise AuthorityError("world_revalidation_invalid_path")
    target = urllib.parse.urlsplit(path)
    decoded_path = urllib.parse.unquote(target.path)
    if (
        target.scheme
        or target.netloc
        or target.fragment
        or not decoded_path.startswith("/")
        or any(part in {".", ".."} for part in decoded_path.split("/"))
        or chr(92) in decoded_path
    ):
        raise AuthorityError("world_revalidation_invalid_path")

    joined_path = base.path.rstrip("/") + target.path
    return urllib.parse.urlunsplit((base.scheme, base.netloc, joined_path, target.query, ""))
GATE_API_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
WORLD_REVALIDATION_ENABLED = os.getenv("ACTION_GATE_WORLD_REVALIDATION", "0").lower() in {"1", "true", "yes"}

def _fingerprint(value: str | None) -> str | None:
    if value is None:
        return None
    return hashlib.sha256(value.encode()).hexdigest()[:16]

def _nonce_state(nonce: str | None) -> str:
    if not nonce:
        return "missing"
    try:
        os.makedirs(os.path.dirname(TOOL_NONCE_DB) or ".", exist_ok=True)
        con = sqlite3.connect(TOOL_NONCE_DB, timeout=2)
        try:
            con.execute("PRAGMA busy_timeout=2000")
            con.execute("CREATE TABLE IF NOT EXISTS used_authorities (nonce TEXT PRIMARY KEY, decision_id TEXT NOT NULL, expires_at INTEGER NOT NULL, used_at INTEGER NOT NULL)")
            row = con.execute("SELECT decision_id, expires_at FROM used_authorities WHERE nonce = ?", (nonce,)).fetchone()
        finally:
            con.close()
        return "already_claimed" if row else "not_claimed"
    except Exception as exc:  # diagnostic path must never mask the original decision
        print(f"AUTHORITY_DIAGNOSTIC nonce_state_error={type(exc).__name__}", file=sys.stderr, flush=True)
        return "lookup_error"

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

def _verify_live_world_binding(authority: Authority, tenant_id: str) -> None:
    """Fail closed unless the signed decision is bound to the current execution world."""
    if not WORLD_REVALIDATION_ENABLED:
        raise AuthorityError("world_revalidation_not_configured")
    if not GATE_API_TOKEN:
        raise AuthorityError("world_revalidation_not_configured")

    def get_gate_json(path: str) -> dict:
        endpoint = _validated_gate_url(path)
        req = urllib.request.Request(
            endpoint,
            headers={"Authorization": f"Bearer {GATE_API_TOKEN}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                value = json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise AuthorityError("world_revalidation_unavailable") from exc
        if not isinstance(value, dict):
            raise AuthorityError("world_revalidation_invalid_response")
        return value

    evidence_path = (
        "/v1/evidence/"
        + urllib.parse.quote(authority.decision_id, safe="")
        + "?tenant_id="
        + urllib.parse.quote(tenant_id, safe="")
    )
    record = get_gate_json(evidence_path)
    if record.get("tenant_id") != tenant_id or record.get("decision") != "ALLOW":
        raise AuthorityError("world_revalidation_evidence_mismatch")
    if record.get("nonce") != authority.nonce or record.get("decision_id") != authority.decision_id:
        raise AuthorityError("world_revalidation_authority_mismatch")

    issued_world = record.get("world_version")
    if not isinstance(issued_world, (str, int)) or isinstance(issued_world, bool) or str(issued_world) == "":
        raise AuthorityError("world_version_missing")
    current = get_gate_json("/v1/state/current")
    current_world = current.get("world_version")
    if current_world is None or current_world != issued_world:
        raise AuthorityError("execution_world_state_changed")


def verify_execution_authority(token: str | None, tenant_id: str | None, payload: dict, action_digest: str | None = None, policy_digest: str | None = None) -> None:
    if not AUTHORITY_SECRET:
        raise AuthorityError("tool_authority_verification_not_configured")
    if not token or not tenant_id:
        raise AuthorityError("direct_tool_access_rejected")
    authority = Authority.from_token(token)
    secret = AUTHORITY_SECRET.encode()
    if isinstance(payload.get("action"), dict) and isinstance(payload.get("policy"), dict):
        bound_action_digest = canonical_digest(payload["action"])
        bound_policy_digest = canonical_digest(payload["policy"])
    elif action_digest and policy_digest:
        bound_action_digest = action_digest
        bound_policy_digest = policy_digest
    else:
        raise AuthorityError("action_and_policy_binding_required")
    verify_authority_envelope(
        authority=authority,
        secret=secret,
        tenant_id=tenant_id,
        action_digest=bound_action_digest,
        used_nonces=None,
    )
    if bound_policy_digest is not None and authority.policy_digest != bound_policy_digest:
        raise AuthorityError("policy_binding_mismatch")
    if "tenant_id" in payload and payload.get("tenant_id") != tenant_id:
        raise AuthorityError("tenant_mismatch")
    _verify_live_world_binding(authority, tenant_id)
    _claim_nonce(authority.nonce, authority.decision_id, authority.expires_at)

class Tool(BaseHTTPRequestHandler):
    def _reject(self, reason: str, token: str | None, tenant_id: str | None, nonce: str | None = None) -> None:
        print(
            "AUTHORITY_REJECT"
            f" reason={reason}"
            f" tenant={tenant_id or 'missing'}"
            f" token_present={bool(token)}"
            f" authority_secret_present={bool(AUTHORITY_SECRET)}"
            f" authority_secret_fp={_fingerprint(AUTHORITY_SECRET) if DEBUG_AUTHORITY else 'redacted'}"
            f" token_secret_fp={_fingerprint(token) if DEBUG_AUTHORITY and token else 'redacted'}"
            f" nonce_state={_nonce_state(nonce) if DEBUG_AUTHORITY else 'redacted'}",
            file=sys.stderr,
            flush=True,
        )
        self.send_response(403)
        if DEBUG_AUTHORITY:
            self.send_header("X-HCJ-Authority-Diagnostic", reason)
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "execution_authority_invalid",
            "diagnostic": reason if DEBUG_AUTHORITY else "redacted",
        }).encode())

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
        token = self.headers.get("X-HCJ-Execution-Authority")
        tenant_id = self.headers.get("X-Tenant-ID")
        action_digest = self.headers.get("X-HCJ-Action-Hash")
        policy_digest = self.headers.get("X-HCJ-Policy-Hash")
        try:
            verify_execution_authority(token, tenant_id, body, action_digest, policy_digest)
        except AuthorityError as exc:
            authority_nonce = None
            try:
                authority_nonce = Authority.from_token(token).nonce if token else None
            except Exception:
                pass
            self._reject(str(exc), token, tenant_id, authority_nonce)
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"tool_executed": True, "received": body}).encode())

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "9000"))), Tool).serve_forever()
