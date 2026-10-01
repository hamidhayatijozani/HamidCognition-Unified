from fastapi.testclient import TestClient
from dashboard.app import app

client = TestClient(app)


def test_console_serves_static_application():
    response = client.get("/")
    assert response.status_code == 200
    assert "Control the action boundary." in response.text
    assert "Browser never receives Gate token" in response.text


def test_console_assets_are_reachable():
    assert client.get("/assets/style.css").status_code == 200
    assert client.get("/assets/app.js").status_code == 200


def test_browser_bundle_does_not_contain_gate_token():
    html = client.get("/").text
    js = client.get("/assets/app.js").text
    assert "ACTION_GATE_API_TOKEN" not in html
    assert "ACTION_GATE_API_TOKEN" not in js


def test_customer_proxy_endpoints_exist():
    routes = {route.path for route in app.routes}
    assert "/api/evaluate" in routes
    assert "/api/evidence/{decision_id}" in routes
    assert "/api/replay/{decision_id}" in routes
