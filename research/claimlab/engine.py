from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib, json
from typing import Any


class ClaimType(str, Enum):
    OBSERVATION="OBSERVATION"; INFERENCE="INFERENCE"; EXPLANATION="EXPLANATION"; ONTOLOGY="ONTOLOGY"


class EvidenceRelation(str, Enum):
    SUPPORT="SUPPORT"; CONTRADICT="CONTRADICT"; NEUTRAL="NEUTRAL"; MISSING="MISSING"; STALE="STALE"; CONFLICTED="CONFLICTED"


class Verdict(str, Enum):
    VALID="VALID"; WEAK="WEAK"; INVALID="INVALID"; UNKNOWN="UNKNOWN"; OVERCLAIM="OVERCLAIM"


class EpistemicState(str, Enum):
    """Evidence state of a claim assessment, not a claim about truth."""
    ESTABLISHED="ESTABLISHED"
    SUPPORTED="SUPPORTED"
    CONTESTED="CONTESTED"
    UNRESOLVED="UNRESOLVED"
    UNOBSERVED="UNOBSERVED"
    OVERCLAIMED="OVERCLAIMED"


@dataclass(frozen=True)
class Evidence:
    evidence_id:str
    relation:EvidenceRelation
    source:str
    statement:str
    strength:float=1.0
    fresh:bool=True
    independent:bool=True


@dataclass(frozen=True)
class Claim:
    statement:str
    claim_type:ClaimType
    scope:dict[str,Any]=field(default_factory=dict)
    source:str=""
    assumptions:tuple[str,...]=()
    counterclaim:str=""
    claim_id:str=""
    def __post_init__(self):
        if not self.claim_id:
            payload={"statement":self.statement,"type":self.claim_type.value,"scope":self.scope,"source":self.source}
            object.__setattr__(self,"claim_id","CLM-"+hashlib.sha256(_canonical(payload)).hexdigest()[:16].upper())


@dataclass(frozen=True)
class ClaimAssessment:
    claim_id:str
    verdict:Verdict
    epistemic_state:EpistemicState
    unknown_reason:str
    support:float
    contradiction:float
    unresolved:float
    evidence_coverage:float
    evidence_quality:float
    evidence_quality_components:dict[str,Any]
    overclaim_flags:tuple[str,...]
    counterclaim:str
    next_tests:tuple[str,...]
    fingerprint:str
    def to_dict(self):
        return asdict(self)|{"verdict":self.verdict.value,"epistemic_state":self.epistemic_state.value}


def _canonical(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()


class ClaimLab:
    """Deterministic claim-integrity engine for research, not a truth oracle."""

    def assess(self,claim:Claim,evidence:list[Evidence])->ClaimAssessment:
        support_evidence=[e for e in evidence if e.relation==EvidenceRelation.SUPPORT and e.fresh]
        contradiction=sum(max(0,e.strength) for e in evidence if e.relation==EvidenceRelation.CONTRADICT and e.fresh)
        unresolved=sum(max(0,e.strength) for e in evidence if e.relation in {EvidenceRelation.MISSING,EvidenceRelation.STALE,EvidenceRelation.CONFLICTED})
        support=sum(max(0,e.strength) for e in support_evidence)
        usable=[e for e in evidence if e.relation!=EvidenceRelation.MISSING]
        independent_support_sources={e.source for e in support_evidence if e.independent and e.source}
        independent_support_count=len(independent_support_sources)
        coverage=min(1.0,len(usable)/max(1,len(evidence))) if evidence else 0.0
        quality,quality_components=self._evidence_quality(evidence)
        flags=self._overclaim_flags(claim,support,contradiction,evidence)
        total=support+contradiction+unresolved
        if not evidence or total==0:
            verdict=Verdict.UNKNOWN
            unknown_reason="no_usable_evidence_for_claim_scope"
        elif flags:
            verdict=Verdict.OVERCLAIM
            unknown_reason=""
        elif contradiction>support:
            verdict=Verdict.INVALID
            unknown_reason=""
        elif support>0 and contradiction==0 and unresolved==0 and independent_support_count>=2:
            verdict=Verdict.VALID
            unknown_reason=""
        else:
            verdict=Verdict.WEAK
            unknown_reason=""
        epistemic_state=self._epistemic_state(verdict, support, contradiction, unresolved, quality)
        tests=self._next_tests(claim,evidence,flags,quality)
        fingerprint=hashlib.sha256(_canonical({"claim":asdict(claim),"evidence":[asdict(e) for e in evidence]})).hexdigest()
        return ClaimAssessment(
            claim.claim_id,verdict,epistemic_state,unknown_reason,
            round(support,10),round(contradiction,10),round(unresolved,10),
            round(coverage,10),round(quality,10),quality_components,
            tuple(flags),claim.counterclaim,tuple(tests),fingerprint
        )

    def _epistemic_state(self,verdict,support,contradiction,unresolved,quality):
        if verdict==Verdict.VALID:
            return EpistemicState.ESTABLISHED
        if verdict==Verdict.OVERCLAIM:
            return EpistemicState.OVERCLAIMED
        if verdict==Verdict.INVALID:
            return EpistemicState.CONTESTED
        if verdict==Verdict.UNKNOWN:
            return EpistemicState.UNOBSERVED
        if contradiction>0:
            return EpistemicState.CONTESTED
        if unresolved>0 or quality<1.0:
            return EpistemicState.UNRESOLVED
        return EpistemicState.SUPPORTED

    def _evidence_quality(self,evidence:list[Evidence])->tuple[float,dict[str,Any]]:
        scored=[e for e in evidence if e.relation in {EvidenceRelation.SUPPORT,EvidenceRelation.CONTRADICT}]
        if not scored:
            return 0.0,{"scored_evidence":0,"freshness":0.0,"independent_source_factor":0.0}
        fresh=sum(1 for e in scored if e.fresh)/len(scored)
        independent_sources=len({e.source for e in scored if e.independent and e.source})
        source_factor=min(1.0,independent_sources/2)
        quality=fresh*source_factor
        return quality,{
            "scored_evidence":len(scored),
            "freshness":round(fresh,10),
            "independent_sources":independent_sources,
            "independent_source_factor":round(source_factor,10),
        }

    def _overclaim_flags(self,claim,support,contradiction,evidence):
        flags=[]; text=claim.statement.lower()
        if claim.claim_type in {ClaimType.EXPLANATION,ClaimType.ONTOLOGY} and not any("causal" in e.statement.lower() for e in evidence if e.relation==EvidenceRelation.SUPPORT):
            flags.append("causal_or_explanatory_strength_exceeds_recorded_evidence")
        if any(w in text for w in ("guarantee","always","never","certain","will profit","causes")) and contradiction>0:
            flags.append("universal_or_causal_wording_conflicts_with_counterevidence")
        if claim.claim_type==ClaimType.OBSERVATION and claim.assumptions:
            flags.append("observation_contains_assumptions")
        if support>0 and not any(e.independent for e in evidence if e.relation==EvidenceRelation.SUPPORT):
            flags.append("support_has_no_independent_source")
        return flags

    def _next_tests(self,claim,evidence,flags,quality):
        tests=[]
        if not evidence:
            tests.append("collect_minimum_independent_evidence_for_claim_scope")
        elif flags:
            tests.append("restate_claim_at_the_strength_supported_by_observation")
        if any(e.relation==EvidenceRelation.CONTRADICT for e in evidence):
            tests.append("run_counterclaim_against_same_scope")
        if claim.scope:
            tests.append("run_out_of_sample_or_unseen_scope_test")
        if quality<1.0:
            tests.append("improve_evidence_freshness_and_source_independence")
        if not tests:
            tests.append("attempt_falsification_with_pre_registered_failure_condition")
        return tests

    def claim_dna(self,claim,evidence):
        assessment=self.assess(claim,evidence)
        return {"claim_id":claim.claim_id,"statement":claim.statement,"type":claim.claim_type.value,"scope":claim.scope,"assessment":assessment.to_dict()}
