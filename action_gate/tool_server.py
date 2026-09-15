from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import hmac
import json
import os

ENFORCEMENT_SECRET = os.getenv("ACTION_GATE_ENFORCEMENT_SECRET", "dev-enforcement-secret")


def attestation(decision_id, action_hash, nonce):
    message = f"{decision_id}:{action_hash}:{nonce}".encode()
    return hmac.new(ENFORCEMENT_SECRET.encode(), message, hashlib.sha256).hexdigest()


class Tool(BaseHTTPRequestHandler):
    def do_POST(self):
        decision_id = self.headers.get("X-HCJ-Decision-ID")
        action_hash = self.headers.get("X-HCJ-Action-Hash")
        nonce = self.headers.get("X-HCJ-Nonce")
        supplied = self.headers.get("X-HCJ-Enforcement-Attestation")
        expected = attestation(decision_id or "", action_hash or "", nonce or "")
        if not decision_id or not action_hash or not nonce or not supplied or not hmac.compare_digest(supplied, expected):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'{"error":"direct_tool_access_rejected"}')
            return
        size = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(size) or b"{}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"tool_executed": True, "received": body}).encode())


ThreadingHTTPServer(("127.0.0.1", 9000), Tool).serve_forever()
