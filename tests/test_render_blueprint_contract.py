"""Regression tests for the Render Action Gate secret contract.

These tests intentionally use only the Python standard library so the
deployment contract can be checked in clean CI environments.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER_BLUEPRINT = ROOT / "render.yaml"

REQUIRED_GENERATED_SECRETS = {
    "ACTION_GATE_API_TOKEN",
    "ACTION_GATE_SIGNING_SECRET",
    "ACTION_GATE_AUTHORITY_SECRET",
    "ACTION_GATE_STATE_ORACLE_SECRET",
    "ACTION_GATE_APPROVAL_SECRET",
    "MCP_BEARER_TOKEN",
}


class RenderBlueprintContractTests(unittest.TestCase):
    def test_action_gate_secret_group_generates_all_runtime_secrets(self):
        source = RENDER_BLUEPRINT.read_text(encoding="utf-8")
        self.assertIn("envVarGroups:", source)
        self.assertIn("name: hamidcognition-action-gate-secrets", source)
        group = source.split("envVarGroups:", 1)[1].split("\nservices:", 1)[0]
        generated = set(
            re.findall(
                r"(?m)^\s*- key: ([A-Z0-9_]+)\n\s+generateValue: true\s*$",
                group,
            )
        )
        missing = sorted(REQUIRED_GENERATED_SECRETS - generated)
        self.assertFalse(
            missing,
            "Render Action Gate secret group is missing generated secrets: "
            + ", ".join(missing),
        )

    def test_state_oracle_secret_is_not_a_literal_or_shared_secret(self):
        source = RENDER_BLUEPRINT.read_text(encoding="utf-8")
        match = re.search(
            r"(?m)^\s*- key: ACTION_GATE_STATE_ORACLE_SECRET\n"
            r"\s+generateValue: true\s*$",
            source,
        )
        self.assertIsNotNone(
            match,
            "State-oracle signing secret must be generated independently by Render.",
        )


if __name__ == "__main__":
    unittest.main()
