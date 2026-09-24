from RESEARCH.experiments.sti_001 import (
    FAILURES,
    explicit_sti,
    generate,
    outcome_only,
    provenance_only,
    confidence_only,
    rates,
)


def test_synthetic_ground_truth_is_balanced():
    rows = generate(seed=7, repetitions=3)
    assert len(rows) == len(FAILURES) * 3
    assert sum(r.failed for r in rows) == (len(FAILURES) - 1) * 3


def test_outcome_only_misses_correct_outcome_wrong_transition():
    rows = generate(seed=11, repetitions=1)
    target = next(r for r in rows if r.failure == "correct_outcome_wrong_transition")
    assert outcome_only(target) is False
    assert explicit_sti(target) is True


def test_provenance_only_cannot_detect_semantic_drift():
    rows = generate(seed=11, repetitions=1)
    target = next(r for r in rows if r.failure == "semantic_drift")
    assert provenance_only(target) is False
    assert explicit_sti(target) is True


def test_confidence_only_misses_high_confidence_transition_failure():
    rows = generate(seed=11, repetitions=1)
    target = next(r for r in rows if r.failure == "unsupported_level_jump")
    assert confidence_only(target) is False
    assert explicit_sti(target) is True


def test_metrics_are_deterministic():
    rows = generate(seed=123, repetitions=2)
    assert rates(rows, explicit_sti) == rates(generate(seed=123, repetitions=2), explicit_sti)
