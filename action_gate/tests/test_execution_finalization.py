import json

import storage


def test_finalize_execution_is_atomic_and_persists_outcome(tmp_path):
    storage.SQLITE_PATH = str(tmp_path / "finalize.db")
    storage.DATABASE_URL = None
    storage.init_db()
    record = {
        "decision_id": "dec-finalize",
        "trace_id": "trace-finalize",
        "tenant_id": "tenant-a",
        "action_hash": "hash-a",
        "nonce": "nonce-finalize",
        "decision": "ALLOW",
        "consumed_at": None,
        "execution_started_at": "2026-09-19T10:00:00+00:00",
    }
    con = storage.connect()
    try:
        con.execute("INSERT INTO records(decision_id, trace_id, record) VALUES (?, ?, ?)",
                    (record["decision_id"], record["trace_id"], json.dumps(record)))
        con.commit()
    finally:
        con.close()

    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
    now = lambda: "2026-09-19T10:01:00+00:00"
    result = storage.finalize_execution(record, "nonce-finalize", now(),
                                        lambda value: "hash:" + canonical(value),
                                        canonical, now, {"status": 200, "ok": True})
    assert result is not None
    assert result["consumed_at"] == now()
    assert result["execution"]["status"] == "EXECUTED"
    assert result["outcome"]["ok"] is True
    stored = json.loads(storage.load_record("dec-finalize"))
    assert stored["consumed_at"] == now()
    assert stored["outcome"]["ok"] is True


def test_finalize_execution_can_only_win_once(tmp_path):
    storage.SQLITE_PATH = str(tmp_path / "finalize-once.db")
    storage.DATABASE_URL = None
    storage.init_db()
    record = {
        "decision_id": "dec-once", "trace_id": "trace-once", "tenant_id": "tenant-a",
        "action_hash": "hash-a", "nonce": "nonce-once", "decision": "ALLOW",
        "consumed_at": None, "execution_started_at": "2026-09-19T10:00:00+00:00",
    }
    con = storage.connect()
    try:
        con.execute("INSERT INTO records(decision_id, trace_id, record) VALUES (?, ?, ?)",
                    (record["decision_id"], record["trace_id"], json.dumps(record)))
        con.commit()
    finally:
        con.close()
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
    now = lambda: "2026-09-19T10:01:00+00:00"
    kwargs = dict(nonce="nonce-once", consumed_at=now(), digest_fn=lambda value: "h:" + canonical(value), canonical_fn=canonical, now_fn=now, outcome={"ok": True})
    assert storage.finalize_execution(record, **kwargs) is not None
    assert storage.finalize_execution(record, **kwargs) is None
