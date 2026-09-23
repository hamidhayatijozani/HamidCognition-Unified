#!/usr/bin/env python3
"""Record-ready Action Gate demo using only real API responses."""

from __future__ import annotations

import json
import os
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
    decision_id = result["decision_id"]
    signature = result.get("decision_signature", "")
    checks = result.get("policy_checks", [])
    evidence = request("GET", f"/v1/evidence/{decision_id}?tenant_id={TENANT}")

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
    print(f"    Risk:       {result['risk_assessment']['level']}")
    for check in checks[:2]:
        print(f"    Policy:     {check.get('policy', 'n/a')} -> {check.get('result', 'n/a')}")
    print(color(f"  ↓ Verdict: {decision}", BOLD + decision_color))
    print(f"    Reason:     {result.get('reason', checks[0].get('reason', 'n/a') if checks else 'n/a')}")
    print(f"    Signature:  {signature[:12]}…")
    print(f"    Decision:   {decision_id}")

    if decision == "ASK":
        print("    approval_request: required (real API does not emit a separate request object)")
        print(f"      status: pending")
        print(f"      approve endpoint: /v1/action/{decision_id}/approve")
        print(f"      current approval: {evidence.get('approval')}")
    else:
        print(f"    approval:    {evidence.get('approval')}")

    print("    evidence_chain:")
    for key in ("schema_version", "action_hash", "policy_hash", "evidence_hash", "audit_event_hash"):
        if key in evidence:
            print(f"      {key}: {evidence[key]}")
    print(f"    Replay:     {BASE}/v1/replay/{decision_id}?tenant_id={TENANT}")
    pause()


def main() -> int:
    print(color("╔══════════════════════════════════════════════════════╗", BOLD + CYAN))
    print(color("║              ACTION GATE — 90s DEMO                 ║", BOLD + CYAN))
    print(color("╚══════════════════════════════════════════════════════╝", BOLD + CYAN))
    print("Real API. Real policy. Real signed decision records.")
    print(color("No mocked NED/HAIS/DRS scores: those metrics are not exposed by the current API.", DIM))
    print()

    try:
        health = request("GET", "/health")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(color(f"Action Gate is not reachable at {BASE}: {exc}", RED))
        return 1

    print(color(f"Gate: {health.get('product')} v{health.get('version')}", BOLD))
    print(f"Policy: {health.get('policy_version')}  |  Environment: {health.get('environment')}")
    print(color("Three decisions. One gate.", BOLD))
    pause(1.0)

    scenarios = [
        (
            "NORMAL READ",
            "Read /public/info.txt",
            {
                "tenant_id": TENANT,
                "agent_id": AGENT,
                "actor_id": "demo-actor",
                "session_id": "demo-session-allow",
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
                "actor_id": "demo-actor",
                "session_id": "demo-session-ask",
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
                "actor_id": "demo-actor",
                "session_id": "demo-session-deny",
                "action": "delete_file",
                "target": "/production/data.db",
            },
        ),
    ]

    for index, (title, action_text, payload) in enumerate(scenarios, start=1):
        try:
            result = request("POST", "/v1/action/evaluate", payload)
            show_result(index, len(scenarios), title, action_text, result)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError) as exc:
            print(color(f"Scenario {index} failed: {exc}", RED))
            return 1

    print()
    print(color("DEMO COMPLETE", BOLD + GREEN))
    print("The recording above is the shipped API behavior, not a fabricated verdict.")
    print(color("Note: transfer_funds is currently SANDBOX under builtin-v1, so the demo does not pretend it is DENY.", DIM))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
