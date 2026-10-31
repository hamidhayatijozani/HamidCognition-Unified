import io
import urllib.error

from enforcement_proxy import send_gate_http_error


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
