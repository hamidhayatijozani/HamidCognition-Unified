#!/usr/bin/env python3
"""STI-001 synthetic benchmark.

Research artifact only. It does not establish scientific validity.
Ground truth is generated independently from evaluator outputs.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Callable


FAILURES = (
    "valid",
    "unsupported_level_jump",
    "provenance_corruption",
    "semantic_drift",
    "common_mode_validator_failure",
    "missing_evidence",
    "contradictory_evidence",
    "correct_outcome_wrong_transition",
)


@dataclass(frozen=True)
class Trajectory:
    case_id: str
    failure: str
    initial_state: int
    observed_states: tuple[int, ...]
    final_state: int
    target_state: int
    evidence_complete: bool
    evidence_aligned: bool
    provenance_valid: bool
    semantic_consistent: bool
    uncertainty_preserved: bool
    transition_stable: bool
    confidence: float
    common_mode_corrupted: bool

    @property
    def failed(self) -> bool:
        return self.failure != "valid"


def make_case(case_id: int, failure: str) -> Trajectory:
    initial = 0
    target = 3
    normal = (0, 1, 2, 3)
    flags = {
        "evidence_complete": True,
        "evidence_aligned": True,
        "provenance_valid": True,
        "semantic_consistent": True,
        "uncertainty_preserved": True,
        "transition_stable": True,
        "common_mode_corrupted": False,
        "confidence": 0.93,
        "states": normal,
        "final": target,
    }

    if failure == "unsupported_level_jump":
        flags["states"] = (0, 3)
        flags["transition_stable"] = False
    elif failure == "provenance_corruption":
        flags["provenance_valid"] = False
    elif failure == "semantic_drift":
        flags["semantic_consistent"] = False
    elif failure == "common_mode_validator_failure":
        flags["common_mode_corrupted"] = True
        flags["evidence_aligned"] = False
        flags["confidence"] = 0.91
    elif failure == "missing_evidence":
        flags["evidence_complete"] = False
        flags["evidence_aligned"] = False
        flags["uncertainty_preserved"] = False
        flags["confidence"] = 0.89
    elif failure == "contradictory_evidence":
        flags["evidence_aligned"] = False
        flags["uncertainty_preserved"] = False
        flags["confidence"] = 0.88
    elif failure == "correct_outcome_wrong_transition":
        flags["states"] = (0, 2, 0, 3)
        flags["transition_stable"] = False
    elif failure != "valid":
        raise ValueError(f"unknown failure: {failure}")

    return Trajectory(
        case_id=f"sti001-{case_id:04d}",
        failure=failure,
        initial_state=initial,
        observed_states=tuple(flags["states"]),
        final_state=flags["final"],
        target_state=target,
        evidence_complete=flags["evidence_complete"],
        evidence_aligned=flags["evidence_aligned"],
        provenance_valid=flags["provenance_valid"],
        semantic_consistent=flags["semantic_consistent"],
        uncertainty_preserved=flags["uncertainty_preserved"],
        transition_stable=flags["transition_stable"],
        confidence=flags["confidence"],
        common_mode_corrupted=flags["common_mode_corrupted"],
    )


def generate(seed: int, repetitions: int) -> list[Trajectory]:
    rng = random.Random(seed)
    rows: list[Trajectory] = []
    for rep in range(repetitions):
        order = list(FAILURES)
        rng.shuffle(order)
        for failure in order:
            rows.append(make_case(rep * len(FAILURES) + len(rows) + 1, failure))
    return rows


def outcome_only(t: Trajectory) -> bool:
    return t.final_state != t.target_state


def confidence_only(t: Trajectory) -> bool:
    return t.confidence < 0.90


def provenance_only(t: Trajectory) -> bool:
    return not t.provenance_valid


def explicit_sti(t: Trajectory) -> bool:
    return not all(
        (
            t.evidence_complete,
            t.evidence_aligned,
            t.provenance_valid,
            t.semantic_consistent,
            t.uncertainty_preserved,
            t.transition_stable,
            not t.common_mode_corrupted,
        )
    )


EVALUATORS: dict[str, Callable[[Trajectory], bool]] = {
    "outcome_only": outcome_only,
    "confidence_only": confidence_only,
    "provenance_only": provenance_only,
    "explicit_sti": explicit_sti,
}


def rates(rows: list[Trajectory], evaluator: Callable[[Trajectory], bool]) -> dict[str, float]:
    tp = fp = tn = fn = 0
    for row in rows:
        pred = evaluator(row)
        actual = row.failed
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
        elif not pred and not actual:
            tn += 1
        else:
            fn += 1
    total = len(rows)
    return {
        "n": total,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "tpr": tp / (tp + fn) if tp + fn else math.nan,
        "fpr": fp / (fp + tn) if fp + tn else math.nan,
    }


def by_failure(rows: list[Trajectory], evaluator: Callable[[Trajectory], bool]) -> dict[str, float]:
    result = {}
    for failure in FAILURES:
        subset = [r for r in rows if r.failure == failure]
        result[failure] = sum(evaluator(r) for r in subset) / len(subset)
    return result


def fingerprint(rows: list[Trajectory], seed: int, repetitions: int) -> str:
    payload = json.dumps([asdict(r) for r in rows], sort_keys=True).encode()
    return sha256(
        b"sti-001|"
        + str(seed).encode()
        + b"|"
        + str(repetitions).encode()
        + b"|"
        + payload
    ).hexdigest()


def run(seed: int, repetitions: int) -> dict:
    rows = generate(seed, repetitions)
    return {
        "protocol": "STI-001",
        "status": "SYNTHETIC_RESEARCH_ARTIFACT",
        "seed": seed,
        "repetitions": repetitions,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_fingerprint": fingerprint(rows, seed, repetitions),
        "evaluators": {
            name: {
                "overall": rates(rows, evaluator),
                "by_failure": by_failure(rows, evaluator),
            }
            for name, evaluator in EVALUATORS.items()
        },
        "interpretation_boundary": (
            "Synthetic discrimination only. Results do not establish general "
            "cognitive validity, real-world performance, novelty, or priority."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260924)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.seed, args.repetitions)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
