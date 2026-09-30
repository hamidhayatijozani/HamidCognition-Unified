import json

import storage


def _setup(tmp_path, decision_id="dec-reconcile"):
    storage.SQLITE_PATH = str(tmp_path / "reconcile.db")
    storage.DATABASE_URL = None
    storage.init_db()
    record = {
        "decision_id": decision_id,
        "trace_id": "trace-reconcile",
        "tenant_id": "tenant-a",
        "action_hash": "hash-a",
        "nonce": "nonce-reconcile",
        "decision": "ALLOW",
        "consumed_at": None,
        "execution_started_at": "2026-09-30T10:00:00+00:00",
        "execution": {"status": "RESERVED", "nonce": "nonce-reconcile", "action_hash": "hash-a"},
    }
    con = storage.connect()
    try:
        con.execute("INSERT INTO records(decision_id, trace_id, record) VALUES (?, ?, ?)",
                    (decision_id, record["trace_id"], json.dumps(record)))
        con.commit()
    finally:
        con.close()
    return record


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def test_unknown_reconciliation_is_persistent_and_append_only(tmp_path):
    record = _setup(tmp_path)
    now = lambda: "2026-09-30T10:05:00+00:00"
    result = storage.reconcile_execution(
        record,
        "nonce-reconcile",
        now(),
        "CONFIRMED_FILLED",
        {"broker_order_id": "42", "request_id": "REQ-42"},
        lambda value: "h:" + _canonical(value),
        _canonical,
        now,
    )
    assert result is not None
    assert result["execution"]["status"] == "RECONCILED"
    assert result["reconciliation"]["status"] == "CONFIRMED_FILLED"
    assert result["reconciliation"]["requires_reconciliation"] is False
    assert result["consumed_at"] == now()

    stored = json.loads(storage.load_record("dec-reconcile"))
    assert stored["reconciliation"]["status"] == "CONFIRMED_FILLED"
    assert stored["outcome"]["broker_order_id"] == "42"

    con = storage.connect()
    try:
        row = con.execute("SELECT resolution, decision_id FROM execution_reconciliations WHERE decision_id=?", ("dec-reconcile",)).fetchone()
        assert row == ("CONFIRMED_FILLED", "dec-reconcile")
        events = con.execute("SELECT event_type FROM audit_events WHERE decision_id=? ORDER BY rowid", ("dec-reconcile",)).fetchall()
        assert events[-1][0] == "EXECUTION_RECONCILED"
    finally:
        con.close()


def test_reconciliation_can_only_win_once(tmp_path):
    record = _setup(tmp_path, "dec-once")
    now = lambda: "2026-09-30T10:06:00+00:00"
    kwargs = dict(
        nonce="nonce-reconcile",
        resolved_at=now(),
        resolution="CONFIRMED_NOT_EXECUTED",
        outcome={"broker_order_id": None},
        digest_fn=lambda value: "h:" + _canonical(value),
        canonical_fn=_canonical,
        now_fn=now,
    )
    assert storage.reconcile_execution(record, **kwargs) is not None
    assert storage.reconcile_execution(record, **kwargs) is None


def test_invalid_reconciliation_resolution_is_rejected(tmp_path):
    record = _setup(tmp_path, "dec-invalid")
    now = lambda: "2026-09-30T10:07:00+00:00"
    try:
        storage.reconcile_execution(
            record, "nonce-reconcile", now(), "UNKNOWN", {},
            lambda value: "h:" + _canonical(value), _canonical, now,
        )
    except ValueError as exc:
        assert str(exc) == "invalid_reconciliation_resolution"
    else:
        raise AssertionError("invalid resolution was accepted")
