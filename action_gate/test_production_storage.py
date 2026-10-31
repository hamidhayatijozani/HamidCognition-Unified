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
    gate_service = compose.split("  action-gate:", 1)[1].split("\n  tool:", 1)[0]
    approval_binding = "ACTION_GATE_APPROVAL_SECRET: ${ACTION_GATE_APPROVAL_SECRET:?set ACTION_GATE_APPROVAL_SECRET}"
    assert approval_binding in gate_service
    assert approval_binding in compose.split("  dashboard:", 1)[1].split("\n  action-gate:", 1)[0]
    assert '"443:443"' in compose
    assert "reverse_proxy enforcement:8080" in caddy


def test_postgres_audit_chain_sequence_is_monotonic_for_equal_timestamps():
    """Exercise the production PostgreSQL chain ordering under a tied timestamp."""
    import hashlib
    import uuid
    import pytest

    database_url = os.getenv("ACTION_GATE_DATABASE_URL", "")
    if not database_url.startswith(("postgresql://", "postgres://")):
        pytest.skip("requires the PostgreSQL integration environment")

    import storage

    storage.DATABASE_URL = database_url
    storage.init_db()
    prefix = "audit-sequence-" + uuid.uuid4().hex
    stamp = "2026-10-28T00:00:00+00:00"

    def canonical(value):
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        )

    def digest(value):
        return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

    con = storage.connect()
    try:
        previous = con.execute(
            "SELECT event_hash FROM audit_events ORDER BY sequence_id DESC LIMIT 1"
        ).fetchone()
        expected_previous = previous[0] if previous else "GENESIS"
    finally:
        con.close()

    ids = [prefix + "-a", prefix + "-b"]
    for decision_id in ids:
        record = {
            "decision_id": decision_id,
            "trace_id": decision_id,
            "tenant_id": "integration-test",
            "decision": "ALLOW",
            "action_hash": digest({"decision_id": decision_id}),
        }
        storage.save_record(record, "AUDIT_SEQUENCE_TEST", digest, canonical, lambda: stamp)

    con = storage.connect()
    try:
        rows = con.execute(
            "SELECT decision_id, previous_hash, event_hash FROM audit_events "
            "WHERE decision_id IN (%s, %s) ORDER BY sequence_id ASC",
            (ids[0], ids[1]),
        ).fetchall()
    finally:
        con.close()

    assert [row[0] for row in rows] == ids
    assert rows[0][1] == expected_previous
    assert rows[1][1] == rows[0][2]


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

