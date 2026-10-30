import re
from pathlib import Path

import pytest

from scripts.classify_release_tag_target import classify_release_tag_target


TARGET = "a" * 40
OTHER = "b" * 40


def test_exact_tag_target_is_a_release_candidate():
    assert classify_release_tag_target(TARGET, "commit", TARGET) == "MATCH"


def test_existing_tag_for_older_release_is_not_a_candidate():
    assert classify_release_tag_target(TARGET, "commit", OTHER) == "MISMATCH"


@pytest.mark.parametrize("tag_type", ["tag", "tree", "blob", "null"])
def test_non_commit_tag_target_fails_closed(tag_type):
    with pytest.raises(ValueError, match="release_tag_did_not_resolve_to_commit"):
        classify_release_tag_target(TARGET, tag_type, TARGET)


@pytest.mark.parametrize("target_sha,tag_sha", [("bad", TARGET), (TARGET, "bad"), ("g" * 40, TARGET)])
def test_malformed_sha_fails_closed(target_sha, tag_sha):
    with pytest.raises(ValueError, match="invalid_commit_sha"):
        classify_release_tag_target(target_sha, "commit", tag_sha)


def test_readiness_workflow_uses_control_sha_for_classifier():
    from pathlib import Path

    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "release-readiness-gate.yml"
    source = workflow.read_text(encoding="utf-8")
    assert "ref: ${{ github.sha }}" in source
    assert 'TARGET_SHA="${{ github.event.workflow_run.head_sha }}"' in source
    assert "python scripts/classify_release_tag_target.py" in source


REQUIRED_MAIN_WORKFLOWS = {
    "Action Gate Product Gates": ".github/workflows/product-gates.yml",
    "Action Gate Product Integrity": ".github/workflows/action-gate-product-integrity.yml",
    "Action Gate Clean-Room Verification": ".github/workflows/action-gate-clean-room.yml",
    "Action Gate Production E2E Smoke": ".github/workflows/production-e2e-smoke.yml",
    "Action Gate Security Authority Gate": ".github/workflows/security-authority-gate.yml",
    "Product Verification": ".github/workflows/product-verification.yml",
    "Security History Secret Scan": ".github/workflows/security-history-secret-scan.yml",
    "Action Gate MVP": ".github/workflows/action-gate-mvp.yml",
    "Canonical Gates": ".github/workflows/gates-canonical.yml",
    "Canonical gates-local proof": ".github/workflows/gates-local-proof.yml",
    "Evidence Chain Integrity": ".github/workflows/evidence-chain-integrity.yml",
}


def test_every_required_release_workflow_runs_on_main_push():
    root = Path(__file__).resolve().parents[1]
    readiness = (root / ".github/workflows/release-readiness-gate.yml").read_text(encoding="utf-8")
    for name, relative in REQUIRED_MAIN_WORKFLOWS.items():
        assert f'"{name}"' in readiness
        source = (root / relative).read_text(encoding="utf-8")
        match = re.search(r"(?m)^  push:\s*\n((?:^    .*\n)+)", source)
        assert match is not None, f"{name} has no push trigger"
        branches = re.search(r"(?m)^    branches:\s*\[(.*?)\]", match.group(1))
        assert branches is not None and "main" in branches.group(1).strip("'\" "), f"{name} does not run on main"
