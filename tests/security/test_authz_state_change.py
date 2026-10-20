#!/usr/bin/env python3
"""Deterministic reference scenario for stale agent authorization.

This is a self-contained test fixture, not an integration test of BESAZ or OASB.
It models the invariant: a decision is valid only for the exact action and
context version that were authorized; missing context fails closed.
"""
from dataclasses import dataclass
import hashlib
import json
import unittest


def action_digest(action: dict) -> str:
    encoded = json.dumps(action, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Decision:
    allowed: bool
    action_sha256: str
    context_version: str


def authorize(action: dict, context_version: str) -> Decision:
    # Fixture policy: only actions explicitly marked safe are allowed.
    return Decision(
        allowed=action.get("safe") is True,
        action_sha256=action_digest(action),
        context_version=context_version,
    )


def execute(decision: Decision, action: dict, current_context_version: str | None) -> bool:
    """Return True only if authorization still binds to the action and state."""
    if current_context_version is None:
        return False  # unknown state must fail closed
    if not decision.allowed:
        return False
    if decision.context_version != current_context_version:
        return False
    if decision.action_sha256 != action_digest(action):
        return False
    return True


class AuthorizationToExecutionTests(unittest.TestCase):
    def setUp(self):
        self.action = {"tool": "write_record", "record_id": "demo-17", "safe": True}
        self.decision = authorize(self.action, "state-A")

    def test_stale_context_is_blocked(self):
        self.assertFalse(execute(self.decision, self.action, "state-B"))

    def test_unchanged_context_executes(self):
        self.assertTrue(execute(self.decision, self.action, "state-A"))

    def test_action_substitution_is_blocked(self):
        substituted = {**self.action, "record_id": "other-record"}
        self.assertFalse(execute(self.decision, substituted, "state-A"))

    def test_unknown_context_fails_closed(self):
        self.assertFalse(execute(self.decision, self.action, None))

    def test_policy_denial_cannot_execute(self):
        unsafe = {"tool": "delete_all", "safe": False}
        denied = authorize(unsafe, "state-A")
        self.assertFalse(execute(denied, unsafe, "state-A"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
