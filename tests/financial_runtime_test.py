import unittest
from decimal import Decimal

from financial_runtime.canonical import bank_row_to_event
from financial_runtime.decision import decide
from financial_runtime.idempotency import IdempotencyVault
from financial_runtime.models import DecisionState, ExecutionState, MatchCandidate
from financial_runtime.runtime import ControlledFinancialRuntime

class FakeDestination:
    name = "fake-accounting"
    def __init__(self, fail=False, verify=True):
        self.fail = fail
        self.verify_result = verify
        self.calls = 0
    def execute(self, event, candidate):
        self.calls += 1
        if self.fail:
            raise TimeoutError("simulated timeout after dispatch")
        return {"external_id": f"doc-{self.calls}"}
    def verify(self, execution):
        return {"verified": self.verify_result, "external_id": execution["external_id"]}

class FinancialRuntimeTests(unittest.TestCase):
    def test_canonical_bank_event(self):
        event = bank_row_to_event({"transaction_id": "TX-1", "date": "2026-09-26", "amount": "1000", "currency": "irr"})
        self.assertEqual(event.amount, Decimal("1000.00"))
        self.assertEqual(event.currency, "IRR")

    def test_similarity_does_not_authorize(self):
        candidate = MatchCandidate("bank-1", "doc-1", Decimal("0.97"), ("text_similarity",))
        decision, _ = decide((candidate,), evidence_complete=True, already_executed=False, policy_allows=True)
        self.assertEqual(decision, DecisionState.ASK)

    def test_exact_candidate_can_authorize(self):
        candidate = MatchCandidate("bank-1", "doc-1", Decimal("1.000"), ("amount_exact", "currency_exact", "reference_exact"))
        decision, _ = decide((candidate,), evidence_complete=True, already_executed=False, policy_allows=True)
        self.assertEqual(decision, DecisionState.ALLOW)

    def test_duplicate_is_blocked_before_second_dispatch(self):
        source = bank_row_to_event({"transaction_id": "TX-1", "date": "2026-09-26", "amount": "1000"})
        candidate = MatchCandidate("TX-1", "DOC-1", Decimal("1.000"), ("amount_exact",))
        destination = FakeDestination()
        runtime = ControlledFinancialRuntime(IdempotencyVault())
        first = runtime.execute(operation_id="OP-1", source=source, candidate=candidate, destination=destination)
        second = runtime.execute(operation_id="OP-1", source=source, candidate=candidate, destination=destination)
        self.assertEqual(first.state, ExecutionState.VERIFIED)
        self.assertEqual(second.decision, DecisionState.DENY)
        self.assertEqual(destination.calls, 1)

    def test_timeout_becomes_unknown_not_failed(self):
        source = bank_row_to_event({"transaction_id": "TX-2", "date": "2026-09-26", "amount": "1000"})
        candidate = MatchCandidate("TX-2", "DOC-2", Decimal("1.000"), ("amount_exact",))
        destination = FakeDestination(fail=True)
        runtime = ControlledFinancialRuntime(IdempotencyVault())
        result = runtime.execute(operation_id="OP-2", source=source, candidate=candidate, destination=destination)
        self.assertEqual(result.state, ExecutionState.UNKNOWN)
        self.assertEqual(destination.calls, 1)

if __name__ == "__main__":
    unittest.main()
