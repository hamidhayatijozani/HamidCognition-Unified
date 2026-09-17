import json
import os
import tempfile


def test_sqlite_storage_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ.pop("ACTION_GATE_DATABASE_URL", None)
        os.environ["ACTION_GATE_DB"] = os.path.join(tmp, "gate.db")
        import storage

        storage.init_db()
        record = {
            "decision_id": "dec_test",
            "trace_id": "trace_test",
            "tenant_id": "tenant_a",
            "decision": "ALLOW",
            "action_hash": "a" * 64,
        }
        storage.save_record(
            record,
            "DECISION_CREATED",
            lambda x: "b" * 64,
            lambda x: json.dumps(x, sort_keys=True),
            lambda: "2026-01-01T00:00:00+00:00",
        )
        loaded = storage.load_record("dec_test")
        assert json.loads(loaded)["tenant_id"] == "tenant_a"


def test_production_compose_uses_postgres_and_tls():
    compose = open("docker-compose.production.yml", encoding="utf-8").read()
    caddy = open("Caddyfile", encoding="utf-8").read()
    assert "postgres:17-alpine" in compose
    assert "ACTION_GATE_DATABASE_URL: postgresql://" in compose
    assert '"443:443"' in compose
    assert "reverse_proxy enforcement:8080" in caddy
