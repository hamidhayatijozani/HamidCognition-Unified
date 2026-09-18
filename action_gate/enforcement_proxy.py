from __future__ import annotations

import hashlib
import hmac
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GATE_URL = os.getenv("GATE_URL", "http://127.0.0.1:8000")
TOOL_URL = os.getenv("TOOL_URL", "http://127.0.0.1:9000")
API_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
ENFORCEMENT_SECRET = os.getenv("ACTION_GATE_ENFORCEMENT_SECRET", "dev-enforcement-secret")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def action_hash(tenant_id, actor_id, action, target, parameters):
    return hashlib.sha256(canonical({"tenant_id": tenant_id, "actor_id": actor_id, "action": action.lower(), "target": target, "parameters": parameters}).encode()).hexdigest()


def attestation(decision_id, action_hash_value, nonce):
    return hmac.new(ENFORCEMENT_SECRET.encode(), f"{decision_id}:{action_hash_value}:{nonce}".encode(), hashlib.sha256).hexdigest()


def auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}


def post_json(url, payload, headers=None):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", **auth_headers(), **(headers or {})})
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read())


def get_json(url):
    req = urllib.request.Request(url, headers=auth_headers())
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read())


def permitted(decision_id: str, tenant_id: str, expected_action_hash: str) -> dict | None:
    try:
        _, record = get_json(GATE_URL + "/v1/evidence/" + urllib.parse.quote(decision_id, safe="") + "?tenant_id=" + urllib.parse.quote(tenant_id, safe=""))
        if record.get("tenant_id") != tenant_id or record.get("decision") != "ALLOW" or record.get("action_hash") != expected_action_hash:
            return None
        return record
    except Exception:
        return None


def reserve_execution(decision_id: str, tenant_id: str, actor_id: str | None, action_hash_value: str, nonce: str):
    return post_json(GATE_URL + f"/v1/action/{urllib.parse.quote(decision_id, safe='')}/execution/reserve",
                     {"tenant_id": tenant_id, "actor_id": actor_id, "action_hash": action_hash_value, "nonce": nonce})[1]


def record_execution(decision_id: str, tenant_id: str, actor_id: str | None, action_hash_value: str, nonce: str, outcome: dict):
    return post_json(GATE_URL + f"/v1/action/{urllib.parse.quote(decision_id, safe='')}/execution", {"tenant_id": tenant_id, "actor_id": actor_id, "action_hash": action_hash_value, "nonce": nonce, "outcome": outcome})


def tool_headers(decision_id, action_hash_value, nonce):
    return {"X-HCJ-Decision-ID": decision_id, "X-HCJ-Action-Hash": action_hash_value, "X-HCJ-Nonce": nonce, "X-HCJ-Enforcement-Attestation": attestation(decision_id, action_hash_value, nonce)}


class HTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0")); body = self.rfile.read(size); payload = json.loads(body or b"{}")
            tenant_id = self.headers.get("X-Tenant-ID", "default"); actor_id = self.headers.get("X-Actor-ID"); agent_id = self.headers.get("X-Agent-ID", "unknown")
            action = self.headers.get("X-Action", "http_post"); target = self.headers.get("X-Action-Target", self.path); decision_id = self.headers.get("X-HCJ-Decision-ID")
            expected_hash = action_hash(tenant_id, actor_id, action, target, payload)
            if decision_id:
                record = permitted(decision_id, tenant_id, expected_hash)
                if not record:
                    self.send_response(403); self.end_headers(); self.wfile.write(b'{"error":"action_gate_denied_or_binding_mismatch"}'); return
                try:
                    reserve_execution(decision_id, tenant_id, actor_id, expected_hash, record["nonce"])
                except Exception:
                    self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"evidence_recording_failed_closed"}'); return
                status, out = post_json(TOOL_URL + self.path, payload, tool_headers(decision_id, expected_hash, record["nonce"]))
                try:
                    record_execution(decision_id, tenant_id, actor_id, expected_hash, record["nonce"], {"http_status": status, "tool_response": out})
                except Exception:
                    self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"evidence_recording_failed_closed"}'); return
                self.send_response(status); self.end_headers(); self.wfile.write(json.dumps(out).encode()); return
            result = post_json(GATE_URL + "/v1/action/evaluate", {"agent_id": agent_id, "actor_id": actor_id, "tenant_id": tenant_id, "action": action, "target": target, "parameters": payload})[1]
            result["enforcement_action_hash"] = expected_hash
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"enforced": result["decision"] == "ALLOW", "decision": result}).encode())
        except Exception:
            self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"action_gate_or_tool_unreachable"}')


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0")); message = json.loads(self.rfile.read(size) or b"{}")
            if message.get("method") != "tools/call":
                self.send_response(400); self.end_headers(); self.wfile.write(json.dumps({"error": "MCP adapter permits tools/call only"}).encode()); return
            params = message.get("params", {}); tool = params.get("name", "unknown"); args = params.get("arguments", {})
            tenant_id = self.headers.get("X-Tenant-ID", "default"); actor_id = self.headers.get("X-Actor-ID"); agent_id = self.headers.get("X-Agent-ID", "unknown"); target = args.get("target")
            result = post_json(GATE_URL + "/v1/action/evaluate", {"agent_id": agent_id, "actor_id": actor_id, "tenant_id": tenant_id, "action": tool, "target": target, "parameters": args})[1]
            if result["decision"] != "ALLOW":
                self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"jsonrpc": "2.0", "id": message.get("id"), "result": {"blocked_by_action_gate": True, "decision": result}}).encode()); return
            try:
                reserve_execution(result["decision_id"], tenant_id, actor_id, result["action_hash"], result["nonce"])
            except Exception:
                self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"evidence_recording_failed_closed"}'); return
            status, out = post_json(TOOL_URL, message, tool_headers(result["decision_id"], result["action_hash"], result["nonce"]))
            try:
                record_execution(result["decision_id"], tenant_id, actor_id, result["action_hash"], result["nonce"], {"http_status": status, "tool_response": out, "protocol": "MCP", "method": "tools/call", "tool": tool})
            except Exception:
                self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"evidence_recording_failed_closed"}'); return
            self.send_response(status); self.end_headers(); self.wfile.write(json.dumps(out).encode())
        except Exception:
            self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"action_gate_or_tool_unreachable"}')


if __name__ == "__main__":
    mode = os.getenv("MODE", "mcp").lower(); handler = MCPHandler if mode == "mcp" else HTTPHandler
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), handler).serve_forever()
