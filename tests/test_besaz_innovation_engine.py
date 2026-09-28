from src.besaz_innovation_engine import (
    CandidateStatus,
    InnovationKind,
    generate_candidates,
    run_sandbox,
)


def components():
    return [
        {"component_id": "COGNITION", "maturity": "PROTOTYPE", "evidence_refs": []},
        {"component_id": "EXECUTION", "maturity": "VERIFIED", "evidence_refs": ["e1"]},
        {"component_id": "FEEDBACK", "maturity": "SPECIFIED", "evidence_refs": []},
        {"component_id": "VERIFICATION", "maturity": "VERIFIED", "evidence_refs": ["e2"]},
    ]


def test_generates_multiple_innovation_modes():
    result = generate_candidates(components())
    kinds = {c.kind for c in result}
    assert len(result) >= 5
    assert InnovationKind.COMBINE in kinds
    assert InnovationKind.EXTEND in kinds
    assert InnovationKind.REVERSE in kinds
    assert InnovationKind.REMOVE in kinds
    assert InnovationKind.REORDER in kinds
    assert InnovationKind.EMERGENT in kinds
    assert all(c.status == CandidateStatus.PROPOSED for c in result)


def test_sandbox_records_failure_instead_of_hiding_it():
    candidate = generate_candidates(components())[0]
    result = run_sandbox(candidate, {
        "baseline": {"score": 0.8},
        "variant": {"score": 0.7},
        "repeatable": True,
        "evidence": ["fixture-1"],
    })
    assert result.outcome == "FAIL"
    assert result.metrics["delta"] == -0.1
    assert result.failures
    assert result.next_action == "revise_or_reject"


def test_sandbox_requires_controlled_fixture():
    candidate = generate_candidates(components())[0]
    result = run_sandbox(candidate, {"baseline": {"score": 1}})
    assert result.outcome == "INCONCLUSIVE"
    assert result.next_action == "repair_fixture"
