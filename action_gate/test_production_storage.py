import json
import os
import tempfile
from pathlib import Path


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
    runtime_dir = Path(__file__).resolve().parent
    compose = (runtime_dir / "docker-compose.production.yml").read_text(encoding="utf-8")
    caddy = (runtime_dir / "Caddyfile").read_text(encoding="utf-8")
    assert "postgres:17-alpine" in compose
    assert "ACTION_GATE_DATABASE_URL: postgresql://" in compose
    assert '"443:443"' in compose
    assert "reverse_proxy enforcement:8080" in caddy


def test_postgres_audit_mutation_triggers_are_installed_when_configured():
    """Regression check for PostgreSQL append-only audit protection.

    This is read-only: it inspects trigger metadata and does not alter audit rows.
    """
    import pytest

    database_url = os.getenv("ACTION_GATE_DATABASE_URL", "")
    if not database_url.startswith(("postgresql://", "postgres://")):
        pytest.skip("requires the PostgreSQL integration environment")

    import storage

    # A prior SQLite test may already have imported the module with no database URL.
    storage.DATABASE_URL = database_url
    con = storage.connect()
    try:
        table = con.execute("SELECT to_regclass('audit_events')").fetchone()
        assert table and table[0] == "audit_events", "PostgreSQL audit_events table is missing"

        triggers = {
            row[0]
            for row in con.execute(
                "SELECT tgname FROM pg_trigger "
                "WHERE tgrelid = 'audit_events'::regclass AND NOT tgisinternal"
            ).fetchall()
        }
        assert {"audit_events_no_update", "audit_events_no_delete"} <= triggers

        definition = con.execute(
            "SELECT pg_get_functiondef("
            "'action_gate_prevent_audit_mutation()'::regprocedure)"
        ).fetchone()
        assert definition and "audit_events_are_append_only" in definition[0]
    finally:
        con.close()

