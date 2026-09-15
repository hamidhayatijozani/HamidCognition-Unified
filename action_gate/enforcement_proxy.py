from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GATE_URL = os.getenv("GATE_URL", "http://127.0.0.1:8000")
TOOL_URL = os.getenv("TOOL_URL", "http://127.0.0.1:9000")
API_TOKEN = os.getenv("ACTION_GATE_API_TOKEN")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def action_hash(action, target, parameters):
    return hashlib.sha256(canonical({"action": action.lower(), "target": target, "parameters": parameters}).encode()).hexdigest()


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


def permitted(decision_id: str, expected_action_hash: str) -> bool:
    try:
        _, record = get_json(GATE_URL + "/v1/evidence/" + decision_id)
        return record.get("decision") in {"ALLOW", "SANDBOX"} and record.get("action_hash") == expected_action_hash
    except Exception:
        return False


def record_execution(decision_id: str, expected_action_hash: str, outcome: dict):
    return post_json(GATE_URL + f"/v1/action/{decision_id}/execution", {"action_hash": expected_action_hash, "outcome": outcome})


class HTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0")); body = self.rfile.read(size); payload = json.loads(body or b"{}")
            action = self.headers.get("X-Action", "http_post"); target = self.headers.get("X-Action-Target", self.path); decision_id = self.headers.get("X-HCJ-Decision-ID")
            expected_hash = action_hash(action, target, payload)
            if decision_id:
                if not permitted(decision_id, expected_hash):
                    self.send_response(403); self.end_headers(); self.wfile.write(b'{"error":"action_gate_denied_or_binding_mismatch"}'); return
                status, out = post_json(TOOL_URL + self.path, payload)
                try:
                    record_execution(decision_id, expected_hash, {"http_status": status, "tool_response": out})
                except Exception:
                    self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"evidence_recording_failed_closed"}'); return
                self.send_response(status); self.end_headers(); self.wfile.write(json.dumps(out).encode()); return
            result = post_json(GATE_URL + "/v1/action/evaluate", {"agent_id": self.headers.get("X-Agent-ID", "unknown"), "action": action, "target": target, "parameters": payload})[1]
            result["enforcement_action_hash"] = expected_hash
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"enforced": result["decision"] in {"ALLOW", "SANDBOX"}, "decision": result}).encode())
        except Exception:
            self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"action_gate_or_tool_unreachable"}')


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0")); message = json.loads(self.rfile.read(size) or b"{}")
            if message.get("method") != "tools/call":
                self.send_response(400); self.end_headers(); self.wfile.write(json.dumps({"error": "MCP demo proxy only permits tools/call"}).encode()); return
            params = message.get("params", {}); tool = params.get("name", "unknown"); args = params.get("arguments", {}); target = args.get("target")
            result = post_json(GATE_URL + "/v1/action/evaluate", {"agent_id": self.headers.get("X-Agent-ID", "unknown"), "action": tool, "target": target, "parameters": args})[1]
            if result["decision"] not in {"ALLOW", "SANDBOX"}:
                self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"jsonrpc": "2.0", "id": message.get("id"), "result": {"blocked_by_action_gate": True, "decision": result}}).encode()); return
            expected_hash = result["action_hash"]
            status, out = post_json(TOOL_URL, message)
            try:
                record_execution(result["decision_id"], expected_hash, {"http_status": status, "tool_response": out, "protocol": "MCP", "method": "tools/call", "tool": tool})
            except Exception:
                self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"evidence_recording_failed_closed"}'); return
            self.send_response(status); self.end_headers(); self.wfile.write(json.dumps(out).encode())
        except Exception:
            self.send_response(502); self.end_headers(); self.wfile.write(b'{"error":"action_gate_or_tool_unreachable"}')


if __name__ == "__main__":
    mode = os.getenv("MODE", "mcp").lower(); handler = MCPHandler if mode == "mcp" else HTTPHandler
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), handler).serve_forever()
