import json
import os
import tempfile
import unittest
from unittest.mock import patch

from action_gate import storage
from action_gate.security_authority import canonical_digest


class SQLiteRecordUpsertIntegrityTests(unittest.TestCase):
    def test_updating_record_preserves_row_identity_and_audit_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "action-gate.sqlite3")
            with patch.object(storage, "DATABASE_URL", None), patch.object(storage, "SQLITE_PATH", db_path):
                storage.init_db()

                def canonical(value):
                    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

                def record(decision_id, decision, trace_id):
                    return {
                        "decision_id": decision_id,
                        "decision": decision,
                        "tenant_id": "tenant-test",
                        "trace_id": trace_id,
                        "action_hash": f"action-{decision_id}",
                    }

                now = lambda: "2026-10-26T00:00:00Z"
                storage.save_record(record("decision-a", "ALLOW", "trace-a1"), "DECISION_CREATED", canonical_digest, canonical, now)
                storage.save_record(record("decision-b", "ALLOW", "trace-b1"), "DECISION_CREATED", canonical_digest, canonical, now)

                con = storage.connect()
                try:
                    original_rowid = con.execute("SELECT rowid FROM records WHERE decision_id=?", ("decision-a",)).fetchone()[0]
                finally:
                    con.close()

                storage.save_record(record("decision-a", "DENY", "trace-a2"), "DECISION_UPDATED", canonical_digest, canonical, now)

                con = storage.connect()
                try:
                    updated_rowid, raw_record = con.execute(
                        "SELECT rowid, record FROM records WHERE decision_id=?", ("decision-a",)
                    ).fetchone()
                    versions = con.execute(
                        "SELECT COUNT(*) FROM record_versions WHERE decision_id=?", ("decision-a",)
                    ).fetchone()[0]
                    events = con.execute(
                        "SELECT COUNT(*) FROM audit_events WHERE decision_id=?", ("decision-a",)
                    ).fetchone()[0]
                finally:
                    con.close()

                self.assertEqual(updated_rowid, original_rowid)
                self.assertEqual(json.loads(raw_record)["decision"], "DENY")
                self.assertEqual(versions, 2)
                self.assertEqual(events, 2)


if __name__ == "__main__":
    unittest.main()
