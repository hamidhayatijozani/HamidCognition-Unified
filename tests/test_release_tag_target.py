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
