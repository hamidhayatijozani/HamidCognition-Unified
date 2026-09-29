import json


def test_besaz_innovate_uses_contract_without_runtime_evidence(monkeypatch, tmp_path):
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
