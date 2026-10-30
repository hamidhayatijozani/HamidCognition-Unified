import sqlite3

import pytest

from action_gate import storage


def test_sqlite_insert_or_replace_cannot_bypass_audit_delete_trigger(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATABASE_URL", None)
    monkeypatch.setattr(storage, "SQLITE_PATH", str(tmp_path / "audit.db"))
    storage.init_db()

    con = storage.connect()
    try:
        assert con.execute("PRAGMA recursive_triggers").fetchone()[0] == 1
        con.execute(
            "INSERT INTO audit_events VALUES (?,?,?,?,?,?,?)",
            ("evt-1", "dec-1", "DECISION", '{"decision":"ALLOW"}', "GENESIS", "a" * 64, "2026-10-30T00:00:00Z"),
        )
        con.commit()

        with pytest.raises(sqlite3.IntegrityError, match="audit_events_are_append_only"):
            con.execute(
                "INSERT OR REPLACE INTO audit_events VALUES (?,?,?,?,?,?,?)",
                ("evt-1", "dec-1", "DECISION", '{"decision":"DENY"}', "GENESIS", "b" * 64, "2026-10-30T00:00:01Z"),
            )
        con.rollback()

        row = con.execute("SELECT event FROM audit_events WHERE event_id=?", ("evt-1",)).fetchone()
        assert row == ('{"decision":"ALLOW"}',)
    finally:
        con.close()
