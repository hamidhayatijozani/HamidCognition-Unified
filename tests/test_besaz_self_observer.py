from src.besaz_self_observer import observe

def test_self_observer_is_non_authoritative():
    report=observe()
    assert report["project"]=="BESAZ"
    assert report["mode"]=="SELF_OBSERVE_ONLY"
    assert report["authority"]=="NONE"
    assert report["hard_boundary"].startswith("self-observation cannot")

def test_self_observer_sees_all_components():
    report=observe()
    assert len(report["components"])==15
    assert len(report["bindings"])==15
    assert report["proposals"]


def test_observed_verified_maturity_requires_runtime_evidence():
    payload = observe()
    for component in payload["components"]:
        if component["maturity"] in {"VERIFIED", "PRODUCTION"}:
            assert component["evidence_refs"], component["component_id"]
