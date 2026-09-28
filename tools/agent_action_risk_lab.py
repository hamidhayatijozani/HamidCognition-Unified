#!/usr/bin/env python3
"""Agent Action Risk Lab: compare the same tool action with and without a governance boundary.

This utility is deliberately evidence-first. It never invents PASS results.
It accepts two HTTP endpoints:
  --baseline-url  the customer's baseline/protected-tool route without Action Gate
  --governed-url  the same action through Action Gate enforcement

For governed tests, callers may provide a JSON request and headers produced by
their deployment. The utility records HTTP status and response bodies verbatim,
then classifies only the explicit expectations configured by the operator.

No customer data is persisted by this script unless --output is supplied.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Observation:
    case_id: str
    path: str
    status: int | None
    response: Any
    elapsed_ms: float
    status_class: str


def call(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: float) -> Observation:
    started = time.perf_counter()
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = raw
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = raw
        status = exc.code
    except Exception as exc:  # evidence must say UNKNOWN, never pretend
        return Observation(
            case_id="",
            path=url,
            status=None,
            response={"error": f"{type(exc).__name__}: {exc}"},
            elapsed_ms=(time.perf_counter() - started) * 1000,
            status_class="UNKNOWN",
        )
    return Observation(
        case_id="",
        path=url,
        status=status,
        response=body,
        elapsed_ms=(time.perf_counter() - started) * 1000,
        status_class="OBSERVED",
    )


def classify(observation: Observation, expected_status: int | None) -> str:
    if observation.status is None:
        return "UNKNOWN"
    if expected_status is None:
        return "OBSERVED"
    return "PASS" if observation.status == expected_status else "FAIL"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline and governed agent-tool execution.")
    parser.add_argument("--baseline-url", required=True)
    parser.add_argument("--governed-url", required=True)
    parser.add_argument("--payload", required=True, help="JSON object containing the exact tool action.")
    parser.add_argument("--governed-headers", default="{}", help="JSON object of headers required by the governed endpoint.")
    parser.add_argument("--baseline-expected-status", type=int, default=None)
    parser.add_argument("--governed-expected-status", type=int, default=None)
    parser.add_argument("--case-id", default="RISK-LAB-001")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload)
        headers = json.loads(args.governed_headers)
        if not isinstance(payload, dict) or not isinstance(headers, dict):
            raise ValueError("payload and governed-headers must be JSON objects")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"INPUT_ERROR: {exc}", file=sys.stderr)
        return 2

    baseline = call(args.baseline_url, payload, {}, args.timeout)
    baseline.case_id = args.case_id + "-BASELINE"
    baseline.status_class = classify(baseline, args.baseline_expected_status)

    governed = call(args.governed_url, payload, headers, args.timeout)
    governed.case_id = args.case_id + "-GOVERNED"
    governed.status_class = classify(governed, args.governed_expected_status)

    result = {
        "schema": "agent-action-risk-lab-1.0",
        "case_id": args.case_id,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "payload_sha256": __import__("hashlib").sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "observations": [asdict(baseline), asdict(governed)],
        "interpretation": (
            "Measured observations only. A PASS means the configured expected HTTP "
            "status was observed. UNKNOWN means the endpoint could not be observed. "
            "No security or business conclusion is inferred beyond the tested paths."
        ),
    }
    output = json.dumps(result, indent=2, sort_keys=True)
    print(output)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")

    return 0 if "FAIL" not in {baseline.status_class, governed.status_class} else 1


if __name__ == "__main__":
    raise SystemExit(main())
