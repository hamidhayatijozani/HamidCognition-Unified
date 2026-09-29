from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_production_edge_routes_mcp_before_dashboard_catch_all():
    caddy = (ROOT / "action_gate" / "Caddyfile").read_text(encoding="utf-8")
    assert caddy.index("handle /mcp*") < caddy.index("handle /api*") < caddy.index("handle / {")


def test_production_compose_contains_customer_console():
    compose = (ROOT / "action_gate" / "docker-compose.production.yml").read_text(encoding="utf-8")
    assert "dashboard:" in compose
    assert "ACTION_GATE_URL: http://action-gate:8000" in compose
    assert 'expose:\n      - "8081"' in compose
    assert "dashboard:8081" in (ROOT / "action_gate" / "Caddyfile").read_text(encoding="utf-8")


def test_dashboard_never_embeds_action_gate_token_in_html():
    html = (ROOT / "dashboard" / "app.py").read_text(encoding="utf-8")
    assert "ACTION_GATE_API_TOKEN" in html
    assert "GATE_TOKEN" in html
    assert "GATE_TOKEN" not in html.split("INDEX =", 1)[1].split("def gate_headers", 1)[0]
