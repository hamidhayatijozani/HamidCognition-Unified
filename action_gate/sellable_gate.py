from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(__file__)
PORT = "8011"
TOKEN = "sellable-gate-token"
DB = "/tmp/action-gate-sellable-gate.db"
ENV = os.environ.copy()
ENV.update({
    "ACTION_GATE_ENV": "production",
    "ACTION_GATE_API_TOKEN": TOKEN,
    "ACTION_GATE_SIGNING_SECRET": "sellable-signing-secret",
    "ACTION_GATE_APPROVAL_SECRET": "sellable-approval-secret",
    "ACTION_GATE_REQUIRE_SESSION_BINDING": "1",
    "ACTION_GATE_DB": DB,
    "PYTHONPATH": ROOT,
})


def request(method: str, path: str, payload: dict | None = None, token: str | None = TOKEN):
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            data = json.loads(raw)
        except Exception:
            data = {"raw": raw.decode(errors="replace")}
        return exc.code, data


def wait_for_health(proc: subprocess.Popen) -> None:
    for _ in range(40):
        if proc.poll() is not None:
            raise AssertionError(f"action-gate exited early: {proc.returncode}")
        try:
            status, body = request("GET", "/health", token=TOKEN)
            if status == 200 and body["status"] == "ok" and body["storage"]["status"] == "ok":
                return
        except Exception:
            pass
        time.sleep(0.25)
    raise AssertionError("production health did not become ready")


def main() -> int:
    try:
        os.remove(DB)
    except FileNotFoundError:
        pass
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", PORT], cwd=ROOT, env=ENV)
    try:
        wait_for_health(proc)

        status, _ = request("GET", "/v1/evidence/nonexistent?tenant_id=sellable-tenant", token=None)
        assert status == 401, "production authentication must be mandatory on protected endpoints"

        evaluate_payload = {
            "tenant_id": "sellable-tenant",
            "agent_id": "sellable-agent",
            "actor_id": "sellable-actor",
            "session_id": "sellable-session",
            "action": "read_public_file",
            "target": "/public/info.txt",
            "parameters": {"probe": "sellable-gate"},
        }
        status, decision = request("POST", "/v1/action/evaluate", evaluate_payload)
        assert status == 200 and decision["decision"] == "ALLOW"
        decision_id = decision["decision_id"]

        status, cross_tenant = request("GET", f"/v1/evidence/{decision_id}?tenant_id=other-tenant")
        assert status == 404 and cross_tenant.get("detail") == "decision_not_found"

        status, replay = request("GET", f"/v1/replay/{decision_id}?tenant_id=sellable-tenant")
        assert status == 200 and replay["match"] is True and replay["action_hash_match"] is True and replay["policy_hash_match"] is True

        status, evidence = request("GET", f"/v1/evidence/{decision_id}?tenant_id=sellable-tenant")
        assert status == 200 and evidence["decision_signature"] and evidence["nonce"]

        execution = {
            "tenant_id": "sellable-tenant",
            "actor_id": decision["actor_id"],
            "session_id": decision["session_id"],
            "action_hash": decision["action_hash"],
            "nonce": decision["nonce"],
            "outcome": {"status": "synthetic-success", "gate": "sellable"},
        }
        status, reserved = request("POST", f"/v1/action/{decision_id}/execution/reserve", execution)
        assert status == 200 and reserved["execution"]["status"] == "RESERVED"
        status, executed = request("POST", f"/v1/action/{decision_id}/execution", execution)
        assert status == 200 and executed["execution"]["status"] == "EXECUTED"

        status, replayed_execution = request("POST", f"/v1/action/{decision_id}/execution", execution)
        assert status == 409 and replayed_execution.get("detail") == "decision_nonce_already_consumed"

        ask_payload = {**evaluate_payload, "action": "send_email", "target": "external"}
        status, ask = request("POST", "/v1/action/evaluate", ask_payload)
        assert status == 200 and ask["decision"] == "ASK"
        approval = {
            "approver_id": "human-1",
            "approved": True,
            "reason": "sellable-gate approval test",
            "action_hash": ask["action_hash"],
            "tenant_id": ask["tenant_id"],
            "policy_version": ask["policy_version"],
        }
        status, approved = request("POST", f"/v1/action/{ask['decision_id']}/approve", approval)
        assert status == 200 and approved["decision"] == "ALLOW"

        print(json.dumps({
            "gate": "SELLABLE_PRODUCT_READINESS",
            "result": "PASS",
            "production_authentication": True,
            "tenant_isolation": True,
            "decision_signature": True,
            "decision_replay": True,
            "single_use_nonce": True,
            "human_approval": True,
            "persistent_storage": True,
            "scope": "API/runtime readiness only; does not establish downstream business outcome safety or universal policy correctness.",
        }, indent=2, sort_keys=True))
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
