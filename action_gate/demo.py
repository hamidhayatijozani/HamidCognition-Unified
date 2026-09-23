#!/usr/bin/env python3
"""Record-ready 90-second Action Gate demo.

Uses the real Action Gate HTTP API. No mocked verdicts or invented metrics.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.getenv("ACTION_GATE_API_TOKEN")
TENANT = os.getenv("ACTION_GATE_TENANT_ID", "demo-tenant")
AGENT = os.getenv("ACTION_GATE_AGENT_ID", "demo-agent")

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def headers() -> dict[str, str]:
    result = {"Accept": "application/json", "Content-Type": "application/json"}
    if TOKEN:
        result["Authorization"] = f"Bearer {TOKEN}"
    return result


def request(method: str, path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=body, headers=headers(), method=method)
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read())


def pause(seconds: float = 0.7) -> None:
    time.sleep(seconds)


def show_result(number: int, total: int, title: str, action_text: str, result: dict) -> None:
    decision = result["decision"]
    risk = result["risk_assessment"]["level"]
    decision_id = result["decision_id"]
    signature = result.get("decision_signature", "")
    checks = result.get("policy_checks", [])

    decision_color = {
        "ALLOW": GREEN,
        "ASK": YELLOW,
        "DENY": RED,
        "SANDBOX": YELLOW,
    }.get(decision, CYAN)

    print()
    print(color(f"[{number}/{total}] {title}", BOLD + CYAN))
    print(f'  Agent:  "{action_text}"')
    pause()
    print(color("  ↓ Action Gate", BOLD))
    print(f"    Risk:       {risk}")
    for check in checks[:2]:
        print(f"    Policy:     {check.get('policy', 'n/a')} -> {check.get('result', 'n/a')}")
    print(color(f"  ↓ Verdict: {decision}", BOLD + decision_color))
    print(f"    Reason:     {checks[0].get('reason', 'recorded by policy') if checks else 'recorded'}")
    print(f"    Signature:  {signature[:12]}…")
    print(f"    Replay:     {BASE}/v1/replay/{decision_id}?tenant_id={TENANT}")
    pause()


def main() -> int:
    print(color("╔══════════════════════════════════════════════════════╗", BOLD + CYAN))
    print(color("║              ACTION GATE — 90s DEMO                 ║", BOLD + CYAN))
    print(color("╚══════════════════════════════════════════════════════╝", BOLD + CYAN))
    print("Real API. Real policy. Real signed decision records.")
    print(color("No mocked NED/HAIS/DRS scores: the current API does not expose those metrics.", DIM))
    print()

    try:
        health = request("GET", "/health")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(color(f"Action Gate is not reachable at {BASE}: {exc}", RED))
        print("Start it first, for example: uvicorn app:app --reload")
        return 1

    print(color(f"Gate: {health.get('product')} v{health.get('version')}", BOLD))
    print(f"Policy: {health.get('policy_version')}  |  Environment: {health.get('environment')}")
    print()
    print(color("Three decisions. One gate.", BOLD))
    pause(1.0)

    scenarios = [
        (
            "NORMAL READ",
            "Read /public/info.txt",
            {
                "tenant_id": TENANT,
                "agent_id": AGENT,
                "action": "read_public_file",
                "target": "/public/info.txt",
            },
        ),
        (
            "SENSITIVE ACTION",
            "Send an email to a customer",
            {
                "tenant_id": TENANT,
                "agent_id": AGENT,
                "action": "send_email",
                "target": "customer@example.com",
            },
        ),
        (
            "DESTRUCTIVE PRODUCTION ACTION",
            "Delete /production/data.db",
            {
                "tenant_id": TENANT,
                "agent_id": AGENT,
                "action": "delete_file",
                "target": "/production/data.db",
            },
        ),
    ]

    for index, (title, action_text, payload) in enumerate(scenarios, start=1):
        try:
            result = request("POST", "/v1/action/evaluate", payload)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            print(color(f"Scenario {index} failed: {exc}", RED))
            return 1
        show_result(index, len(scenarios), title, action_text, result)

    print()
    print(color("DEMO COMPLETE", BOLD + GREEN))
    print("ALLOW  → ordinary action can proceed.")
    print("ASK    → human approval is required before execution.")
    print("DENY   → destructive production action is blocked.")
    print()
    print(color("Note: transfer_funds is currently classified as SANDBOX by the shipped policy,", DIM))
    print(color("not DENY. The demo deliberately does not falsify that behavior.", DIM))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
