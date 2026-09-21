from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os

from security_authority import Authority, AuthorityError, verify_authority

SIGNING_SECRET = os.getenv("ACTION_GATE_SIGNING_SECRET")
USED_NONCES: set[str] = set()


class Tool(BaseHTTPRequestHandler):
    def do_POST(self):
        if not SIGNING_SECRET:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'{"error":"tool_authority_verification_not_configured"}')
            return

        token = self.headers.get("X-HCJ-Execution-Authority")
        action_hash = self.headers.get("X-HCJ-Action-Hash")
        tenant_id = self.headers.get("X-Tenant-ID")
        if not token or not action_hash or not tenant_id:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'{"error":"direct_tool_access_rejected"}')
            return

        try:
            authority = Authority.from_token(token)
            if authority.action_digest != action_hash:
                raise AuthorityError("action_binding_mismatch")
            verify_authority(
                authority=authority,
                secret=SIGNING_SECRET.encode(),
                tenant_id=tenant_id,
                action={"authority_action_digest": action_hash},
                policy={"authority_policy_digest": authority.policy_digest},
                used_nonces=USED_NONCES,
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


ThreadingHTTPServer(("0.0.0.0", 9000), Tool).serve_forever()
