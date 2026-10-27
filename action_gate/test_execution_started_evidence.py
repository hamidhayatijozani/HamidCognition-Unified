import json
import os
import tempfile
import unittest
from unittest.mock import patch

from storage import (
    finalize_execution,
    init_db,
    load_record,
    reserve_execution,
    save_record,
)
from security_authority import canonical_digest


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def now():
    return "2026-10-27T00:00:00Z"


class ExecutionStartedEvidenceTests(unittest.TestCase):
    def test_finalize_preserves_reserved_execution_started_at(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "action-gate.sqlite3")
            with patch("storage.DATABASE_URL", None), patch("storage.SQLITE_PATH", db_path):
                init_db()
                record = {
                    "decision_id": "decision-reserved",
                    "decision": "ALLOW",
                    "tenant_id": "tenant-test",
                    "trace_id": "trace-test",
                    "action_hash": "action-test",
                    "nonce": "nonce-test",
                }
                save_record(record, "DECISION_CREATED", canonical_digest, canonical, now)

                started_at = "2026-10-27T00:00:01Z"
                self.assertTrue(reserve_execution("decision-reserved", "nonce-test", started_at))

                finalized = finalize_execution(
                    record=record,
                    nonce="nonce-test",
                    consumed_at="2026-10-27T00:00:02Z",
                    digest_fn=canonical_digest,
                    canonical_fn=canonical,
                    now_fn=now,
                    outcome={"status": "success"},
                )

                self.assertIsNotNone(finalized)
                stored = json.loads(load_record("decision-reserved"))
                self.assertEqual(stored.get("execution_started_at"), started_at)
                self.assertEqual(stored["execution"]["status"], "EXECUTED")
                self.assertEqual(stored["consumed_at"], "2026-10-27T00:00:02Z")


if __name__ == "__main__":
    unittest.main()
