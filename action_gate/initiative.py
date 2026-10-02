"""Bounded initiative engine.

Constructs non-duplicated, evidence-grounded next-action proposals from an
observed state. It never executes an external side effect.

Important epistemic boundary:
- "novel" here means not an exact repeat of supplied prior action fingerprints.
- It does not prove semantic originality or absence of prior art.
- Proposals are candidates; Action Gate remains the execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any
import hashlib
import json


class InitiativeMode(str, Enum):
    EXPLORE = "EXPLORE"
    REPAIR = "REPAIR"
    VERIFY = "VERIFY"
    ALTERNATE = "ALTERNATE"
    DEFER = "DEFER"


@dataclass(frozen=True)
class InitiativeRequest:
    goal: str
    state: dict[str, Any]
    evidence: tuple[dict[str, Any], ...] = ()
    prior_actions: tuple[dict[str, Any], ...] = ()
    constraints: tuple[str, ...] = ()
    allow_external_side_effect: bool = False
    max_candidates: int = 3


@dataclass(frozen=True)
class InitiativeCandidate:
    action: str
    rationale: str
    mode: InitiativeMode
    requires_gate: bool
    evidence_refs: tuple[str, ...]
    fingerprint: str


@dataclass(frozen=True)
class InitiativeResult:
    candidates: tuple[InitiativeCandidate, ...]
    status: str
    reasoning_trace: tuple[str, ...]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _evidence_refs(evidence: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
    refs = []
    for item in evidence:
        if item.get("verified") is True:
            refs.append(str(item.get("source", "verified-evidence")))
    return tuple(dict.fromkeys(refs))


def _prior_fingerprints(actions: tuple[dict[str, Any], ...]) -> set[str]:
    result = set()
    for action in actions:
        if action.get("fingerprint"):
            result.add(str(action["fingerprint"]))
        else:
            result.add(_fingerprint({
                "action": action.get("action"),
                "target": action.get("target"),
                "parameters": action.get("parameters", {}),
            }))
    return result


def _candidate(action: str, rationale: str, mode: InitiativeMode,
               requires_gate: bool, evidence_refs: tuple[str, ...]) -> InitiativeCandidate:
    payload = {
        "action": action,
        "rationale": rationale,
        "mode": mode.value,
        "evidence_refs": evidence_refs,
    }
    return InitiativeCandidate(
        action=action,
        rationale=rationale,
        mode=mode,
        requires_gate=requires_gate,
        evidence_refs=evidence_refs,
        fingerprint=_fingerprint(payload),
    )


def propose(request: InitiativeRequest) -> InitiativeResult:
    if not request.goal.strip():
        return InitiativeResult((), "DEFER", ("goal_missing",))

    if request.max_candidates <= 0:
        return InitiativeResult((), "DEFER", ("max_candidates_invalid",))

    refs = _evidence_refs(request.evidence)
    prior = _prior_fingerprints(request.prior_actions)
    candidates: list[InitiativeCandidate] = []
    trace: list[str] = []

    state = request.state
    blockers = tuple(str(x) for x in state.get("blockers", ()))
    unknowns = tuple(str(x) for x in state.get("unknowns", ()))
    contradictions = tuple(str(x) for x in state.get("contradictions", ()))
    missing = tuple(str(x) for x in state.get("missing_evidence", ()))
    goal = request.goal.strip()

    def add(action: str, rationale: str, mode: InitiativeMode, gate: bool = False) -> None:
        item = _candidate(action, rationale, mode, gate, refs)
        if item.fingerprint not in prior and all(x.fingerprint != item.fingerprint for x in candidates):
            candidates.append(item)
        else:
            trace.append(f"duplicate_candidate_rejected:{mode.value}")

    if blockers:
        add(
            f"diagnose_blocker:{blockers[0]}",
            "The current state contains a blocker; diagnose it before attempting the blocked path again.",
            InitiativeMode.REPAIR,
        )

    if missing:
        add(
            f"collect_evidence:{missing[0]}",
            "A required evidence item is explicitly missing; gather or verify it before strengthening the claim.",
            InitiativeMode.VERIFY,
        )

    if contradictions:
        add(
            f"test_contradiction:{contradictions[0]}",
            "A contradiction is present; design a discriminating test instead of choosing a preferred explanation.",
            InitiativeMode.EXPLORE,
        )

    if unknowns:
        add(
            f"probe_unknown:{unknowns[0]}",
            "An unknown state is available for bounded exploration without treating it as a failure or a fact.",
            InitiativeMode.EXPLORE,
        )

    if not candidates:
        add(
            f"decompose_goal:{goal}",
            "No blocker, missing evidence, contradiction, or unknown supplied; decompose the goal into a bounded verification step.",
            InitiativeMode.VERIFY,
        )

    if len(candidates) < request.max_candidates and request.state.get("alternate_path"):
        add(
            f"test_alternate_path:{request.state['alternate_path']}",
            "The observed state supplies an alternate path; test it independently rather than replaying the previous route.",
            InitiativeMode.ALTERNATE,
        )

    # External effects are proposals only. They always require the execution gate.
    for item in candidates:
        if any(token in item.action.lower() for token in ("send_", "delete_", "deploy_", "transfer_", "publish_", "modify_")):
            object.__setattr__(item, "requires_gate", True)

    if not refs:
        trace.append("no_verified_evidence:proposal_is_not_evidence")
    else:
        trace.append(f"verified_evidence_refs:{len(refs)}")

    trace.append("exact_duplicate_filter:enabled")
    trace.append("semantic_novelty_not_proven")
    trace.append("execution_authority:action_gate")

    if request.allow_external_side_effect:
        trace.append("external_side_effects_requested:still_gate_bound")
    else:
        trace.append("external_side_effects_disabled")

    return InitiativeResult(
        tuple(candidates[:request.max_candidates]),
        "PROPOSED" if candidates else "DEFER",
        tuple(trace),
    )
