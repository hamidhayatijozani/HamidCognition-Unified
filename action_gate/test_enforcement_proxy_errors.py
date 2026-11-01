import io
import json
import urllib.error
from unittest.mock import patch

from enforcement_proxy import HTTPHandler, MCPHandler, send_gate_http_error


class FakeHandler:
    def __init__(self):
        self.status = None
        self.headers = {}
        self.wfile = io.BytesIO()

    def send_response(self, status):
        self.status = status

    def send_header(self, name, value):
        self.headers[name] = value

    def end_headers(self):
        pass


def test_preserves_gate_conflict_status_and_body():
    body = b'{"detail":"decision_nonce_already_consumed"}'
    error = urllib.error.HTTPError(
        "http://action-gate.local/reserve",
        409,
        "Conflict",
        {},
        io.BytesIO(body),
    )
    handler = FakeHandler()

    send_gate_http_error(handler, error)

    assert handler.status == 409
    assert handler.headers["Content-Type"] == "application/json"
    assert handler.wfile.getvalue() == body


def test_uses_safe_json_when_gate_error_body_is_empty():
    error = urllib.error.HTTPError(
        "http://action-gate.local/reserve",
        409,
        "Conflict",
        {},
        io.BytesIO(b""),
    )
    handler = FakeHandler()

    send_gate_http_error(handler, error)

    assert handler.status == 409
    assert handler.wfile.getvalue() == b'{"error":"action_gate_request_rejected"}'


def test_preserves_body_already_consumed_for_upstream_diagnostics():
    body = b'{"detail":"decision_nonce_already_consumed"}'
    error = urllib.error.HTTPError(
        "http://action-gate.local/reserve",
        409,
        "Conflict",
        {},
        io.BytesIO(b""),
    )
    error._action_gate_body = body
    handler = FakeHandler()

    send_gate_http_error(handler, error)

    assert handler.status == 409
    assert handler.wfile.getvalue() == body


class Headers(dict):
    def get(self, key, default=None):
        return super().get(key, default)


def handler_for(cls, payload, headers):
    raw = json.dumps(payload).encode()
    handler = cls.__new__(cls)
    handler.rfile = io.BytesIO(raw)
    handler.wfile = io.BytesIO()
    handler.headers = Headers({**headers, "Content-Length": str(len(raw))})
    handler.path = "/execute"
    handler.request_version = "HTTP/1.1"
    handler.protocol_version = "HTTP/1.1"
    handler.requestline = "POST /execute HTTP/1.1"
    handler.client_address = ("127.0.0.1", 0)
    handler.command = "POST"
    handler.close_connection = True
    return handler


def response_json(handler):
    raw = handler.wfile.getvalue()
    body = raw.split(b"\r\n\r\n", 1)[1]
    status = int(raw.split(b" ", 2)[1])
    return status, json.loads(body)


def gate_http_error(status, detail):
    body = json.dumps({"detail": detail}).encode()
    error = urllib.error.HTTPError(
        "http://127.0.0.1:8000/v1/action/evaluate",
        status,
        "error",
        {},
        io.BytesIO(body),
    )
    error._action_gate_body = body
    return error


COMMON = {
    "X-Tenant-ID": "tenant",
    "X-Actor-ID": "actor",
    "X-Session-ID": "session",
    "X-Agent-ID": "agent",
    "X-Action": "read_public_file",
    "X-Action-Target": "/public/info.txt",
}


def test_http_and_mcp_preserve_policy_evaluation_503_and_do_not_call_tool():
    calls = []

    def post_json(url, payload, headers=None):
        calls.append(url)
        raise gate_http_error(503, "policy_evaluation_unavailable")

    message = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}}
    with patch("enforcement_proxy.post_json", post_json):
        http = handler_for(HTTPHandler, {}, COMMON)
        http.do_POST()
        mcp = handler_for(MCPHandler, message, COMMON)
        mcp.do_POST()
    http_status, http_body = response_json(http)
    mcp_status, mcp_body = response_json(mcp)
    assert http_status == 503 and http_body["detail"] == "policy_evaluation_unavailable"
    assert mcp_status == 503 and mcp_body["detail"] == "policy_evaluation_unavailable"
    assert all(url.endswith("/v1/action/evaluate") for url in calls)
    assert not any("/execution" in url or url.endswith(":9000") for url in calls)


def test_gate_disconnect_stays_502_on_http_and_mcp():
    def post_json(url, payload, headers=None):
        raise urllib.error.URLError("connection refused")

    message = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}}
    with patch("enforcement_proxy.post_json", post_json):
        http = handler_for(HTTPHandler, {}, COMMON)
        http.do_POST()
        mcp = handler_for(MCPHandler, message, COMMON)
        mcp.do_POST()
    assert response_json(http) == (502, {"error": "action_gate_or_tool_unreachable"})
    assert response_json(mcp) == (502, {"error": "action_gate_or_tool_unreachable"})


def test_incomplete_allow_does_not_execute_on_http_or_mcp():
    def post_json(url, payload, headers=None):
        if not str(url).endswith("/v1/action/evaluate"):
            raise AssertionError(url)
        return 200, {"decision": "ALLOW"}

    message = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "read_public_file", "arguments": {"target": "/public/info.txt"}}}
    with patch("enforcement_proxy.post_json", post_json):
        http = handler_for(HTTPHandler, {}, COMMON)
        http.do_POST()
        mcp = handler_for(MCPHandler, message, COMMON)
        mcp.do_POST()
    assert response_json(http)[0] == 502 and response_json(http)[1]["error"] == "action_gate_response_untrusted"
    mcp_status, mcp_body = response_json(mcp)
    assert mcp_status == 502 and mcp_body["error"] == "action_gate_response_untrusted"
