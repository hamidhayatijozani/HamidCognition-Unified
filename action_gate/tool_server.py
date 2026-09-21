from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os

from security_authority import Authority, AuthorityError, verify_authority_envelope

SIGNING_SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET")
USED_NONCES: set[str] = set()


def verify_execution_authority(token: str | None, tenant_id: str | None, action_hash: str | None) -> None:
    if not SIGNING_SECRET:
        raise AuthorityError("tool_authority_verification_not_configured")
    if not token or not action_hash or not tenant_id:
        raise AuthorityError("direct_tool_access_rejected")
    authority = Authority.from_token(token)
    verify_authority_envelope(
        authority=authority,
        secret=SIGNING_SECRET.encode(),
        tenant_id=tenant_id,
        action_digest=action_hash,
        used_nonces=USED_NONCES,
    )


class Tool(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            verify_execution_authority(
                self.headers.get("X-HCJ-Execution-Authority"),
                self.headers.get("X-Tenant-ID"),
                self.headers.get("X-HCJ-Action-Hash"),
            )
        except AuthorityError:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'{"error":"execution_authority_invalid"}')
            return

        size = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(size) or b"{}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"tool_executed": True, "received": body}).encode())


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "9000"))), Tool).serve_forever()
