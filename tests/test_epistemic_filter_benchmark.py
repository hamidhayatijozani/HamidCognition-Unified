from __future__ import annotations

import json

from integrated.research.epistemic_filter.poc.benchmark_suite import (
    CURRENT_DECISIONS,
    EventGenerator,
    ScenarioType,
    write_jsonl,
)


def test_synthetic_benchmark_is_exactly_200_and_balanced():
    rows = EventGenerator(seed=42).generate_all_events()
    assert len(rows) == 200
    assert [sum(r["scenario"] == s.value for r in rows) for s in ScenarioType] == [40] * 5
    assert all(r["expected_decision"] in CURRENT_DECISIONS for r in rows)


def test_synthetic_benchmark_is_reproducible():
    a = EventGenerator(seed=123).generate_all_events()
    b = EventGenerator(seed=123).generate_all_events()
    assert a == b


def test_different_seed_changes_synthetic_dataset():
    a = EventGenerator(seed=123).generate_all_events()
    b = EventGenerator(seed=124).generate_all_events()
    assert a != b


def test_jsonl_output_is_replayable(tmp_path):
    rows = EventGenerator(seed=7).generate_all_events()
    output = tmp_path / "events.jsonl"
    write_jsonl(rows, output)
    replayed = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert replayed == rows
