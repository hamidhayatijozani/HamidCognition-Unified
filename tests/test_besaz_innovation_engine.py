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



def test_besaz_innovate_script_generates_report_without_contract_evidence_refs(monkeypatch, tmp_path):
    import json
    import scripts.besaz_innovate as module

    output = tmp_path / "innovation-report.json"
    monkeypatch.setattr(module, "OUT", output)
    module.main()

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["project"] == "BESAZ"
    assert report["mode"] == "INNOVATION_SANDBOX"
    assert report["authority"] == "NONE"
    assert report["candidate_count"] > 0
    assert all(candidate["source_components"] for candidate in report["candidates"])
