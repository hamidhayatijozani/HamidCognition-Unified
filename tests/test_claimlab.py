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
