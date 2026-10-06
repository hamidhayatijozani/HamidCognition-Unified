#!/usr/bin/env python3
"""Aggregate the currently executable research lines into one evidence run.

This is an execution harness, not a scientific-validity claim.  External-data
experiments are required to execute successfully when this script is run in CI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "RESEARCH" / "RESEARCH_COMPLETION_RESULT.json"

COMMANDS = [
    ("algorithm_orchestrator", [sys.executable, "-m", "RESEARCH.algorithm_orchestrator"]),
    ("exp003_external_replay", [sys.executable, "RESEARCH/EXP003EXTERNAL_REPLAY.py"]),
    (
        "sti001",
        [
            sys.executable,
            "RESEARCH/experiments/sti_001.py",
            "--seed",
            "20260924",
            "--repetitions",
            "10",
            "--output",
            "/tmp/sti001.json",
        ],
    ),
    ("market_lab", [sys.executable, "-m", "RESEARCH.market_lab.run"]),
    ("exp004_walkforward", [sys.executable, "RESEARCH/EXP004_WALKFORWARD.py"]),
    ("exp004_validator", [sys.executable, "RESEARCH/EXP004_VALIDATOR.py"]),
    ("exp005_adversarial", [sys.executable, "RESEARCH/EXP005_ADVERSARIAL.py"]),
]


def run(name: str, command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=900,
        check=False,
    )
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "status": "EXECUTED_SUCCESS" if completed.returncode == 0 else "EXECUTION_FAILED",
    }


def main() -> int:
    results = [run(name, command) for name, command in COMMANDS]
    payload = {
        "harness": "HHJ-RESEARCH-COMPLETION-001",
        "status": (
            "COMPLETE_AT_EXECUTION_BOUNDARY"
            if all(x["returncode"] == 0 for x in results)
            else "INCOMPLETE_EXECUTION"
        ),
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_head": "resolved_by_ci_checkout",
        "runs": results,
        "scope": {
            "includes": [x[0] for x in COMMANDS],
            "research_only": True,
            "scientific_validity_established": False,
            "live_trading_safety_established": False,
            "execution_authority_from_research_established": False,
        },
    }
    OUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if payload["status"] == "COMPLETE_AT_EXECUTION_BOUNDARY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
