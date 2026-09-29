from research.claimlab import ClaimLab, Claim, Evidence, Verdict
from research.claimlab.engine import ClaimType, EvidenceRelation

def ev(i,relation,statement,source="test",independent=True,fresh=True):
    return Evidence(i,relation,source,statement,independent=independent,fresh=fresh)

def test_claim_dna_is_deterministic():
    c=Claim("EURUSD rose after the transition",ClaimType.INFERENCE,{"horizon":"10m"},source="PST")
    assert c.claim_id.startswith("CLM-")
    assert Claim("EURUSD rose after the transition",ClaimType.INFERENCE,{"horizon":"10m"},source="PST").claim_id==c.claim_id
def test_contradicting_evidence_prevents_valid_verdict():
    c=Claim("The transition causes positive returns",ClaimType.EXPLANATION)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"association observed"),ev("x1",EvidenceRelation.CONTRADICT,"counterexample observed")])
    assert result.verdict in {Verdict.INVALID,Verdict.OVERCLAIM}; assert result.contradiction==1.0
def test_unknown_is_not_invalid():
    result=ClaimLab().assess(Claim("A novel regime is profitable",ClaimType.INFERENCE),[])
    assert result.verdict==Verdict.UNKNOWN
def test_overclaim_is_explicit():
    result=ClaimLab().assess(Claim("The mechanism causes the outcome",ClaimType.EXPLANATION),[ev("s1",EvidenceRelation.SUPPORT,"positive association")])
    assert result.verdict==Verdict.OVERCLAIM and result.overclaim_flags
def test_counterclaim_generates_falsification_path():
    c=Claim("PST transition is associated with positive returns",ClaimType.INFERENCE,{"symbol":"EURUSD"},counterclaim="Momentum alone explains the effect")
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"association observed",source="feed-A"),ev("s2",EvidenceRelation.SUPPORT,"association replicated",source="feed-B")])
    assert result.counterclaim.startswith("Momentum")
    assert "out_of_sample" in " ".join(result.next_tests)
def test_neutral_evidence_does_not_count_as_independent_support():
    c=Claim("The transition predicts positive returns",ClaimType.INFERENCE)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"association observed",source="feed-A"),ev("n1",EvidenceRelation.NEUTRAL,"no relevant signal",source="feed-B")])
    assert result.verdict==Verdict.WEAK
def test_duplicate_source_does_not_create_independent_support():
    c=Claim("The transition predicts positive returns",ClaimType.INFERENCE)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"association observed",source="feed-A"),ev("s2",EvidenceRelation.SUPPORT,"association replicated",source="feed-A")])
    assert result.verdict==Verdict.WEAK
def test_two_independent_support_sources_can_be_valid():
    c=Claim("The transition predicts positive returns",ClaimType.INFERENCE)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"association observed",source="feed-A"),ev("s2",EvidenceRelation.SUPPORT,"association replicated",source="feed-B")])
    assert result.verdict==Verdict.VALID
def test_coverage_and_quality_are_distinct():
    c=Claim("The transition predicts positive returns",ClaimType.INFERENCE)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"fresh support",source="feed-A"),ev("s2",EvidenceRelation.SUPPORT,"fresh support",source="feed-B"),ev("n1",EvidenceRelation.NEUTRAL,"irrelevant context",source="feed-C")])
    assert result.evidence_coverage==1.0
    assert result.evidence_quality==1.0
def test_stale_support_reduces_quality_without_increasing_support():
    c=Claim("The transition predicts positive returns",ClaimType.INFERENCE)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"stale support",source="feed-A",fresh=False),ev("s2",EvidenceRelation.SUPPORT,"fresh support",source="feed-B")])
    assert result.support==1.0
    assert result.evidence_quality==0.5
    assert result.verdict==Verdict.WEAK


def test_unknown_produces_evidence_collection_action():
    result=ClaimLab().assess(Claim("An unobserved regime predicts positive returns",ClaimType.INFERENCE,{"symbol":"EURUSD"}),[])
    assert result.verdict==Verdict.UNKNOWN
    assert "collect_minimum_independent_evidence_for_claim_scope" in result.next_tests

from research.claimlab.engine import EpistemicState


def test_unknown_exposes_explicit_epistemic_state_and_reason():
    result=ClaimLab().assess(Claim("An unobserved regime predicts positive returns",ClaimType.INFERENCE,{"symbol":"EURUSD"}),[])
    assert result.verdict==Verdict.UNKNOWN
    assert result.epistemic_state==EpistemicState.UNOBSERVED
    assert result.unknown_reason=="no_usable_evidence_for_claim_scope"


def test_evidence_quality_components_are_auditable():
    c=Claim("The transition predicts positive returns",ClaimType.INFERENCE)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"support A",source="feed-A"),ev("s2",EvidenceRelation.SUPPORT,"support B",source="feed-B")])
    assert result.evidence_quality==1.0
    assert result.evidence_quality_components["scored_evidence"]==2
    assert result.evidence_quality_components["freshness"]==1.0
    assert result.evidence_quality_components["independent_sources"]==2
    assert result.evidence_quality_components["independent_source_factor"]==1.0


def test_stale_or_conflicted_evidence_is_unresolved_not_unknown():
    c=Claim("The transition predicts positive returns",ClaimType.INFERENCE)
    result=ClaimLab().assess(c,[ev("s1",EvidenceRelation.SUPPORT,"fresh support",source="feed-A"),ev("x1",EvidenceRelation.CONFLICTED,"conflict",source="feed-B")])
    assert result.verdict==Verdict.WEAK
    assert result.epistemic_state==EpistemicState.UNRESOLVED
    assert result.unresolved==1.0


def test_signal_snapshot_is_structured_on_evidence():
    from research.claimlab.engine import SignalSnapshot
    snapshot=SignalSnapshot(0.72,0.61,0.38,0.83,0.37,False,True,False,1)
    evidence=ev("sig-1",EvidenceRelation.SUPPORT,"PST signal snapshot",source="signal-feed")
    evidence=Evidence(evidence.evidence_id,evidence.relation,evidence.source,evidence.statement,signals=snapshot)
    payload=evidence.to_dict()
    assert isinstance(payload["signals"],dict)
    assert payload["signals"] != {}
    for key in ("P","S","T","energy","creativity","loop","jump","escape","signal"):
        assert key in payload["signals"]
    assert payload["signals"]["P"] == 0.72
    assert payload["signals"]["jump"] is True


def test_signal_snapshot_rejects_out_of_range_continuous_values():
    from research.claimlab.engine import SignalSnapshot
    import pytest
    with pytest.raises(ValueError):
        SignalSnapshot(1.01,0.5,0.5,0.5,0.5,False,False,False,0)


def test_signal_snapshot_survives_claim_fingerprint_serialization():
    from research.claimlab.engine import SignalSnapshot
    snapshot=SignalSnapshot(0.9055,0.8062,0.4494,0.8275,0.4494,False,True,False,1)
    evidence=Evidence("sig-1",EvidenceRelation.SUPPORT,"feed","snapshot",signals=snapshot)
    claim=Claim("PST signal snapshot was observed",ClaimType.OBSERVATION)
    result=ClaimLab().assess(claim,[evidence])
    assert result.fingerprint
    assert evidence.to_dict()["signals"] == snapshot.to_dict()


def test_real_http_server_round_trip_persists_exact_signal_snapshot(tmp_path):
    import json
    import threading
    from http.client import HTTPConnection
    from research.claimlab.app_demo import Handler, SignalEvidenceStore
    from http.server import ThreadingHTTPServer

    db=tmp_path / "evidence.sqlite3"
    Handler.store=SignalEvidenceStore(db)
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        snapshot={"P":0.72,"S":0.61,"T":0.38,"energy":0.83,"creativity":0.37,"loop":False,"jump":True,"escape":False,"signal":1}
        request={"id":"evidence-001","relation":"SUPPORT","source":"EURUSD","statement":"signal snapshot","signals":snapshot}
        conn=HTTPConnection("127.0.0.1",server.server_port,timeout=3)
        conn.request("POST","/evidence",body=json.dumps(request),headers={"Content-Type":"application/json"})
        response=conn.getresponse()
        assert response.status==201
        created=json.loads(response.read())
        assert isinstance(created["signals"],dict)
        assert created["signals"] == snapshot

        conn.request("GET","/evidence/evidence-001")
        response=conn.getresponse()
        assert response.status==200
        replayed=json.loads(response.read())
        assert replayed["signals"] == snapshot
        assert replayed["signals"] != {}
        assert "P/S/T" not in replayed.get("statement","")
        assert replayed["signals"]["P"] == 0.72
        assert replayed["signals"]["S"] == 0.61
        assert replayed["signals"]["T"] == 0.38
        assert replayed["signals"]["energy"] == 0.83
        assert replayed["signals"]["loop"] is False
        assert replayed["signals"]["jump"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
