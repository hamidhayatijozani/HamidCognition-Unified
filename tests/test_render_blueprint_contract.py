"""Regression tests for the Render Action Gate secret contract."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER_BLUEPRINT = ROOT / "render.yaml"

EXPECTED_GROUPS = {
    "action-gate-api-auth": {"ACTION_GATE_API_TOKEN"},
    "action-gate-authority": {"ACTION_GATE_AUTHORITY_SECRET"},
    "action-gate-runtime-signing": {
        "ACTION_GATE_SIGNING_SECRET",
        "ACTION_GATE_STATE_ORACLE_SECRET",
    },
    "action-gate-approval": {"ACTION_GATE_APPROVAL_SECRET"},
    "action-gate-mcp-auth": {"MCP_BEARER_TOKEN"},
}

EXPECTED_SERVICE_GROUPS = {
    "hamidcognition-action-gate": {
        "action-gate-api-auth",
        "action-gate-authority",
        "action-gate-runtime-signing",
        "action-gate-approval",
    },
    "hamidcognition-protected-tool": {
        "action-gate-api-auth",
        "action-gate-authority",
    },
    "hamidcognition-enforcement": {"action-gate-api-auth"},
    "hamidcognition-action-gate-console": {
        "action-gate-api-auth",
        "action-gate-approval",
    },
    "hamidcognition-action-gate-mcp": {
        "action-gate-api-auth",
        "action-gate-mcp-auth",
    },
}


def section_after(source: str, marker: str, stop: str) -> str:
    start = source.index(marker) + len(marker)
    ends = [
        position
        for boundary in (stop, "\nservices:")
        if (position := source.find(boundary, start)) >= 0
    ]
    if not ends:
        raise AssertionError(f"Section terminator not found after {marker!r}")
    return source[start:min(ends)]


def generated_keys_for_group(source: str, group_name: str) -> set[str]:
    section = section_after(
        source,
        f"  - name: {group_name}\n    envVars:\n",
        "\n  - name: ",
    )
    return set(
        re.findall(
            r"(?m)^      - key: ([A-Z0-9_]+)\n        generateValue: true$",
            section,
        )
    )


def groups_for_service(source: str, service_name: str) -> set[str]:
    match = re.search(
        rf"(?ms)^  - type: [^\n]+\n    name: {re.escape(service_name)}\n"
        rf"(?P<body>.*?)(?=^  - type: |^databases:|\Z)",
        source,
    )
    if match is None:
        raise AssertionError(f"Render service is missing: {service_name}")
    return set(
        re.findall(r"(?m)^      - fromGroup: ([a-z0-9-]+)$", match.group("body"))
    )


class RenderBlueprintContractTests(unittest.TestCase):
    def test_each_secret_group_contains_only_its_required_secret(self):
        source = RENDER_BLUEPRINT.read_text(encoding="utf-8")
        for group_name, expected_keys in EXPECTED_GROUPS.items():
            with self.subTest(group=group_name):
                self.assertEqual(
                    generated_keys_for_group(source, group_name),
                    expected_keys,
                    f"Unexpected or missing generated secret in {group_name}",
                )

    def test_services_receive_only_the_secret_groups_they_need(self):
        source = RENDER_BLUEPRINT.read_text(encoding="utf-8")
        for service_name, expected_groups in EXPECTED_SERVICE_GROUPS.items():
            with self.subTest(service=service_name):
                self.assertEqual(
                    groups_for_service(source, service_name),
                    expected_groups,
                    f"Unexpected secret-group assignment for {service_name}",
                )


if __name__ == "__main__":
    unittest.main()
