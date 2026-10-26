import unittest

from action_gate.evidence_ledger import EvidenceLedger


class EvidenceLedgerInputIntegrityTests(unittest.TestCase):
    def test_nested_caller_mutation_does_not_change_appended_evidence(self):
        ledger = EvidenceLedger()
        payload = {"context": {"labels": ["approved"]}}
        event = ledger.append("evt-1", "decision", "trace-1", payload)
        original_hash = event.event_hash

        payload["context"]["labels"].append("tampered")

        self.assertEqual(ledger.events()[0].payload["context"]["labels"], ["approved"])
        self.assertEqual(ledger.events()[0].event_hash, original_hash)
        self.assertTrue(ledger.verify_chain())

    def test_duplicate_event_id_is_rejected_without_mutating_chain(self):
        ledger = EvidenceLedger()
        ledger.append("evt-1", "decision", "trace-1", {"decision": "ALLOW"})

        with self.assertRaisesRegex(ValueError, "duplicate_event_id"):
            ledger.append("evt-1", "decision", "trace-2", {"decision": "DENY"})

        self.assertEqual(len(ledger.events()), 1)
        self.assertTrue(ledger.verify_chain())

    def test_non_finite_json_number_is_rejected(self):
        ledger = EvidenceLedger()
        with self.assertRaises(ValueError):
            ledger.append("evt-1", "decision", "trace-1", {"score": float("nan")})

        self.assertEqual(ledger.events(), ())
        self.assertTrue(ledger.verify_chain())


if __name__ == "__main__":
    unittest.main()
