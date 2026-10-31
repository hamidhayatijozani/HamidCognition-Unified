import json

import pytest

from src.mother_memory import MotherMemory, MemoryValidationError


def assessment(model="GPT-6"):
    return {
        "model": {"provider": "OpenAI", "name": model, "version": "test-version"},
        "scope": "reasoning-patterns",
        "observations": [{"kind": "OBSERVATION", "text": "The subject repeatedly asks for evidence-backed implementation."}],
        "interpretations": [{
            "kind": "INFERENCE",
            "text": "The subject appears to prioritize verifiability.",
            "confidence": 0.72,
            "basis": "Repeated requests in cited conversation records.",
        }],
        "strengths": ["systems thinking"],
        "risks": ["project dispersion"],
        "patterns": ["evidence-first"],
        "evidence_refs": ["conversation:synthetic-fixture-001"],
        "uncertainty": "This is a bounded interpretation of selected conversations, not a stable personality diagnosis.",
    }


def test_store_requires_explicit_consent(tmp_path):
    store = MotherMemory(tmp_path)
    with pytest.raises(MemoryValidationError, match="consent"):
        store.record_assessment(assessment(), consent=False)


def test_store_requires_model_provenance_evidence_and_uncertainty(tmp_path):
    store = MotherMemory(tmp_path)
    bad = assessment()
    bad["model"].pop("version")
    with pytest.raises(MemoryValidationError, match="model.provider"):
        store.record_assessment(bad, consent=True)
    bad = assessment()
    bad["evidence_refs"] = []
    with pytest.raises(MemoryValidationError, match="evidence reference"):
        store.record_assessment(bad, consent=True)
    bad = assessment()
    bad["uncertainty"] = ""
    with pytest.raises(MemoryValidationError, match="uncertainty"):
        store.record_assessment(bad, consent=True)


def test_hidden_reasoning_and_raw_transcripts_are_rejected(tmp_path):
    store = MotherMemory(tmp_path)
    bad = assessment()
    bad["chain_of_thought"] = "private reasoning"
    with pytest.raises(MemoryValidationError, match="hidden reasoning"):
        store.record_assessment(bad, consent=True)
    bad = assessment()
    bad["raw_transcript"] = "full conversation"
    with pytest.raises(MemoryValidationError, match="hidden reasoning"):
        store.record_assessment(bad, consent=True)


def test_models_remain_attributed_and_comparison_is_not_automatic_consensus(tmp_path):
    store = MotherMemory(tmp_path)
    first = store.record_assessment(assessment("GPT-6"), consent=True)
    second = store.record_assessment(assessment("Claude"), consent=True)
    result = store.compare_models()
    assert result["assessment_count"] == 2
    assert result["comparisons"][0]["models"] == ["Claude", "GPT-6"]
    assert result["comparisons"][0]["comparison_status"] == "HUMAN_COMPARISON_REQUIRED"
    assert first["model"]["name"] == "GPT-6"
    assert second["model"]["name"] == "Claude"


def test_review_and_delete_are_audited(tmp_path):
    store = MotherMemory(tmp_path)
    item = store.record_assessment(assessment(), consent=True)
    store.review_assessment(item["assessment_id"], status="DISPUTED", reviewer_note="Evidence does not support a stable trait.")
    assert store.list_assessments()[0]["review_status"] == "DISPUTED"
    assert store.delete_assessment(item["assessment_id"])
    assert store.list_assessments() == []
    audit = store.verify_audit_chain()
    assert audit["valid"] is True
    assert audit["events"] == 3


def test_store_creates_expected_private_files(tmp_path):
    store = MotherMemory(tmp_path)
    assert set(p.name for p in tmp_path.iterdir()) == {
        "memory.json", "concepts.json", "sessions.json", "emergence.json",
        "governance.json", "manifest.json", "audit.jsonl",
    }
    assert store.snapshot()["assessment_count"] == 0
    assert json.loads((tmp_path / "governance.json").read_text())["public_repository_records_allowed"] is False

def test_emergence_requires_multiple_providers_and_never_promotes_trait(tmp_path):
    store = MotherMemory(tmp_path)
    store.record_assessment(assessment("GPT-6"), consent=True)
    assert store.detect_emergence() == []
    other = assessment("Claude")
    other["model"]["provider"] = "Anthropic"
    store.record_assessment(other, consent=True)
    candidates = store.detect_emergence()
    assert len(candidates) == 1
    assert candidates[0]["status"] == "REVIEW_REQUIRED"
    assert candidates[0]["method"] == "EXACT_LABEL_RECURRENCE"
    assert "does not establish" in candidates[0]["interpretation"]
    assert store.detect_emergence() == []
