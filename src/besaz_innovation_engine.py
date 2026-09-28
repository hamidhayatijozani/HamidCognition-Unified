"""BESAZ Innovation Engine.

Turns observed architecture gaps and experiment results into bounded,
testable innovation candidates. It never promotes candidates to production.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from hashlib import sha256
from typing import Any, Iterable
import json
import time


class InnovationKind(str, Enum):
    COMBINE = "COMBINE"
    EXTEND = "EXTEND"
    REVERSE = "REVERSE"
    REMOVE = "REMOVE"
    REORDER = "REORDER"
    TRANSFER = "TRANSFER"
    CONTRADICTION = "CONTRADICTION"
    EMERGENT = "EMERGENT"


class CandidateStatus(str, Enum):
    PROPOSED = "PROPOSED"
    TESTABLE = "TESTABLE"
    TESTED = "TESTED"
    REJECTED = "REJECTED"
    CANDIDATE = "CANDIDATE"


@dataclass(frozen=True)
class InnovationCandidate:
    candidate_id: str
    kind: InnovationKind
    title: str
    hypothesis: str
    source_components: tuple[str, ...]
    experiment: str
    success_criteria: tuple[str, ...]
    risks: tuple[str, ...]
    status: CandidateStatus = CandidateStatus.PROPOSED

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["kind"] = self.kind.value
        value["status"] = self.status.value
        value["source_components"] = list(self.source_components)
        value["success_criteria"] = list(self.success_criteria)
        value["risks"] = list(self.risks)
        return value


@dataclass(frozen=True)
class ExperimentResult:
    candidate_id: str
    outcome: str
    metrics: dict[str, float]
    observations: tuple[str, ...]
    failures: tuple[str, ...]
    repeatable: bool
    evidence: tuple[str, ...]
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["observations"] = list(self.observations)
        value["failures"] = list(self.failures)
        value["evidence"] = list(self.evidence)
        return value


def _id(*parts: str) -> str:
    raw = "|".join(parts).encode()
    return "IN-" + sha256(raw).hexdigest()[:16]


def generate_candidates(
    components: Iterable[dict[str, Any]],
    experiment_history: Iterable[dict[str, Any]] = (),
) -> list[InnovationCandidate]:
    """Generate bounded hypotheses from architecture state.

    This is deliberately deterministic: the same evidence produces the same
    candidate set, making the innovation layer auditable and reproducible.
    """
    items = list(components)
    history = list(experiment_history)
    ids = [str(x.get("component_id", "")) for x in items if x.get("component_id")]
    gaps = [
        str(x.get("component_id"))
        for x in items
        if x.get("component_id")
        and (
            not x.get("evidence_refs")
            or str(x.get("maturity", "")) in {"SPECIFIED", "PROTOTYPE"}
        )
    ]
    candidates: list[InnovationCandidate] = []

    def add(
        kind: InnovationKind,
        title: str,
        hypothesis: str,
        sources: list[str],
        experiment: str,
        criteria: list[str],
        risks: list[str],
    ) -> None:
        cid = _id(kind.value, title, *sources)
        if any(c.candidate_id == cid for c in candidates):
            return
        candidates.append(
            InnovationCandidate(
                cid,
                kind,
                title,
                hypothesis,
                tuple(sources),
                experiment,
                tuple(criteria),
                tuple(risks),
            )
        )

    if len(ids) >= 2:
        a, b = ids[0], ids[1]
        add(
            InnovationKind.COMBINE,
            f"Cross-link {a} + {b}",
            f"Combining observations from {a} and {b} may expose a capability neither reveals alone.",
            [a, b],
            "Run both observation paths on the same synthetic scenario and compare signal coverage.",
            ["combined coverage increases", "no new unsupported claim is introduced"],
            ["false correlation", "duplicated evidence"],
        )

    if gaps:
        a = gaps[0]
        add(
            InnovationKind.EXTEND,
            f"Extend evidence path for {a}",
            f"Adding a verification step to {a} may convert an architectural assumption into evidence.",
            [a],
            "Attach one measurable verification probe and run it against a controlled fixture.",
            ["probe produces a traceable result", "failure is explicitly recorded"],
            ["overfitting to fixture", "measurement bias"],
        )

        add(
            InnovationKind.REVERSE,
            f"Reverse assumption around {a}",
            f"Testing the opposite of the current assumption for {a} may reveal a hidden boundary condition.",
            [a],
            "Run the same fixture with the target assumption inverted and compare outcomes.",
            ["difference is measurable", "both outcomes remain auditable"],
            ["invalid inversion", "misleading edge case"],
        )

    if len(ids) >= 3:
        a, b, c = ids[:3]
        add(
            InnovationKind.REORDER,
            f"Reorder {a} -> {b} -> {c}",
            "Changing component order may reduce unnecessary work or expose an earlier detection point.",
            [a, b, c],
            "Execute two equivalent synthetic pipelines with the order swapped; compare latency and evidence.",
            ["functional result remains equivalent", "measured cost changes or remains stable"],
            ["hidden dependency", "non-equivalent pipelines"],
        )

        add(
            InnovationKind.REMOVE,
            f"Ablation of {b}",
            f"Temporarily remove {b} in a sandbox to determine whether it contributes unique value.",
            [a, b, c],
            "Run baseline and ablated synthetic pipelines; compare correctness and evidence coverage.",
            ["loss of capability is measurable", "no production state is touched"],
            ["false negative from weak fixture"],
        )

    if history:
        failed = [x for x in history if x.get("outcome") in {"FAIL", "INCONCLUSIVE"}]
        if failed:
            add(
                InnovationKind.CONTRADICTION,
                "Turn a failed experiment into a boundary test",
                "A failed or inconclusive experiment may encode a useful constraint rather than useless noise.",
                [str(failed[0].get("candidate_id", "unknown"))],
                "Reproduce the failure with one controlled variable changed at a time.",
                ["failure boundary becomes explicit", "result is repeatable or explained"],
                ["confounded variables"],
            )

    add(
        InnovationKind.EMERGENT,
        "Generate a cross-layer probe",
        "A signal observed in one layer may become informative when tested against another layer's evidence.",
        ids[:4],
        "Select one observable from two layers, correlate them only inside a synthetic fixture, and test whether the relation survives a changed fixture.",
        ["relation is reproducible or explicitly rejected", "no causal claim is inferred from correlation"],
        ["spurious correlation", "scope leakage"],
    )

    return candidates


def run_sandbox(candidate: InnovationCandidate, fixture: dict[str, Any]) -> ExperimentResult:
    """Run a deterministic bounded experiment, not arbitrary code execution."""
    required = {"baseline", "variant"}
    missing = required - fixture.keys()
    if missing:
        return ExperimentResult(
            candidate.candidate_id,
            "INCONCLUSIVE",
            {},
            (),
            (f"missing fixture fields: {sorted(missing)}",),
            False,
            (),
            "repair_fixture",
        )

    baseline = fixture["baseline"]
    variant = fixture["variant"]
    if not isinstance(baseline, dict) or not isinstance(variant, dict):
        return ExperimentResult(
            candidate.candidate_id,
            "INCONCLUSIVE",
            {},
            (),
            ("baseline and variant must be objects",),
            False,
            (),
            "repair_fixture",
        )

    baseline_score = float(baseline.get("score", 0.0))
    variant_score = float(variant.get("score", 0.0))
    delta = variant_score - baseline_score
    result = "PASS" if delta > 0 else "FAIL" if delta < 0 else "INCONCLUSIVE"
    repeatable = bool(fixture.get("repeatable", False))

    return ExperimentResult(
        candidate.candidate_id,
        result,
        {"baseline_score": baseline_score, "variant_score": variant_score, "delta": delta},
        (f"score_delta={delta}",),
        () if result == "PASS" else (f"variant did not improve baseline: {delta}",),
        repeatable,
        tuple(str(x) for x in fixture.get("evidence", [])),
        "retain_candidate" if result == "PASS" and repeatable else "revise_or_reject",
    )


def innovation_report(
    components: list[dict[str, Any]],
    experiment_history: list[dict[str, Any]] = (),
) -> dict[str, Any]:
    candidates = generate_candidates(components, experiment_history)
    return {
        "project": "BESAZ",
        "mode": "INNOVATION_SANDBOX",
        "authority": "NONE",
        "generated_at": int(time.time()),
        "candidate_count": len(candidates),
        "candidates": [c.to_dict() for c in candidates],
        "hard_boundary": [
            "sandbox only",
            "no production mutation",
            "no self-granted authority",
            "no invented evidence",
            "failure must remain visible",
            "promotion requires explicit verification and approval",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(innovation_report([]), indent=2, ensure_ascii=False))
