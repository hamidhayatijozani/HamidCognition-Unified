from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GATE_URL = os.getenv("GATE_URL", "http://127.0.0.1:8000")
TOOL_URL = os.getenv("TOOL_URL", "http://127.0.0.1:9000")


def post_json(url, payload, headers=None):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read())


def get_json(url):
    with urllib.request.urlopen(url) as r:
        return r.status, json.loads(r.read())


def permitted(decision_id: str) -> bool:
    try:
        _, record = get_json(GATE_URL + "/v1/evidence/" + decision_id)
        return record.get("decision") in {"ALLOW", "SANDBOX"}
    except Exception:
        return False


class HTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size)
        payload = json.loads(body or b"{}")
        action = self.headers.get("X-Action", "http_post")
        target = self.headers.get("X-Action-Target", self.path)
        decision_id = self.headers.get("X-HCJ-Decision-ID")
        if decision_id:
            if not permitted(decision_id):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'{"error":"action_gate_denied"}')
                return
            try:
                status, out = post_json(TOOL_URL + self.path, payload)
            except urllib.error.HTTPError as e:
                status, out = e.code, {"error": e.read().decode(errors="replace")}
            self.send_response(status)
            self.end_headers()
            self.wfile.write(json.dumps(out).encode())
            return
        result = post_json(GATE_URL + "/v1/action/evaluate", {"agent_id": self.headers.get("X-Agent-ID", "unknown"), "action": action, "target": target, "parameters": payload})[1]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"enforced": result["decision"] in {"ALLOW", "SANDBOX"}, "decision": result}).encode())


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        message = json.loads(self.rfile.read(size) or b"{}")
        if message.get("method") != "tools/call":
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "MCP demo proxy only permits tools/call"}).encode())
            return
        params = message.get("params", {})
        tool = params.get("name", "unknown")
        args = params.get("arguments", {})
        result = post_json(GATE_URL + "/v1/action/evaluate", {"agent_id": self.headers.get("X-Agent-ID", "unknown"), "action": tool, "target": args.get("target"), "parameters": args})[1]
        if result["decision"] not in {"ALLOW", "SANDBOX"}:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"jsonrpc": "2.0", "id": message.get("id"), "result": {"blocked_by_action_gate": True, "decision": result}}).encode())
            return
        status, out = post_json(TOOL_URL, message)
        self.send_response(status)
        self.end_headers()
        self.wfile.write(json.dumps(out).encode())


if __name__ == "__main__":
    mode = os.getenv("MODE", "mcp").lower()
    handler = MCPHandler if mode == "mcp" else HTTPHandler
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), handler).serve_forever()
