from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "integrated/research/epistemic-filter/poc/benchmark_suite.py"
)
SPEC = importlib.util.spec_from_file_location("hhj_benchmark_suite", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

CURRENT_DECISIONS = MODULE.CURRENT_DECISIONS
EventGenerator = MODULE.EventGenerator
ScenarioType = MODULE.ScenarioType
write_jsonl = MODULE.write_jsonl


def test_synthetic_benchmark_is_exactly_200_and_balanced():
    rows = EventGenerator(seed=42).generate_all_events()
    assert len(rows) == 200
    assert [sum(r["scenario"] == s.value for r in rows) for s in ScenarioType] == [40] * 5
    assert all(r["expected_decision"] in CURRENT_DECISIONS for r in rows)


def test_synthetic_benchmark_is_reproducible():
    assert EventGenerator(seed=123).generate_all_events() == EventGenerator(seed=123).generate_all_events()


def test_different_seed_changes_synthetic_dataset():
    assert EventGenerator(seed=123).generate_all_events() != EventGenerator(seed=124).generate_all_events()


def test_jsonl_output_is_replayable(tmp_path):
    rows = EventGenerator(seed=7).generate_all_events()
    output = tmp_path / "events.jsonl"
    write_jsonl(rows, output)
    replayed = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert replayed == rows
