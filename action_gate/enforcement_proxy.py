from __future__ import annotations

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GATE_URL = os.getenv("GATE_URL", "http://127.0.0.1:8000")
TOOL_URL = os.getenv("TOOL_URL", "http://127.0.0.1:9000")


def gate(payload):
    req = urllib.request.Request(GATE_URL + "/v1/action/evaluate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


class HTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size)
        payload = json.loads(body or b"{}")
        decision_id = self.headers.get("X-HCJ-Decision-ID")
        if decision_id:
            target = TOOL_URL + self.path
            req = urllib.request.Request(target, data=body, headers={"Content-Type": self.headers.get("Content-Type", "application/json")})
            with urllib.request.urlopen(req) as r:
                out = r.read()
                self.send_response(r.status)
                self.end_headers()
                self.wfile.write(out)
            return
        result = gate({"agent_id": self.headers.get("X-Agent-ID", "unknown"), "action": "http_post", "target": self.path, "parameters": payload})
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


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
        result = gate({"agent_id": self.headers.get("X-Agent-ID", "unknown"), "action": tool, "target": params.get("arguments", {}).get("target"), "parameters": params.get("arguments", {})})
        if result["decision"] not in {"ALLOW", "SANDBOX"}:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"jsonrpc": "2.0", "id": message.get("id"), "result": {"blocked_by_action_gate": True, "decision": result}}).encode())
            return
        req = urllib.request.Request(TOOL_URL, data=json.dumps(message).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            out = r.read()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(out)


if __name__ == "__main__":
    mode = os.getenv("MODE", "mcp").lower()
    handler = MCPHandler if mode == "mcp" else HTTPHandler
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), handler).serve_forever()
