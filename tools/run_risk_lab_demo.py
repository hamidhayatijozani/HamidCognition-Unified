#!/usr/bin/env python3
"""Reproducible Agent Action Risk Lab demo against the repository's real HTTP tool."""
from __future__ import annotations
import json, os, socket, subprocess, sys, threading, time, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
TENANT, ACTOR, SESSION = "risk-lab-tenant", "risk-lab-actor", "risk-lab-session"
ACTION, TARGET, TOKEN = "read_public_file", "/public/risk-lab.txt", "ci-test-token"

class BaselineHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(size) or b"{}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"tool_executed": True, "mode": "baseline-unprotected-reference", "received": body}).encode())
    def log_message(self, *_):
        return

def request(url, payload, headers=None):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json", **(headers or {})}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raw=e.read().decode()
        try: body=json.loads(raw)
        except json.JSONDecodeError: body=raw
        return e.code, body

def _port_ready(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.connect(("127.0.0.1", port))
            return True
        except OSError:
            return False

def run():
    baseline = ThreadingHTTPServer(("127.0.0.1", 9100), BaselineHandler)
    threading.Thread(target=baseline.serve_forever, daemon=True).start()
    env=os.environ.copy()
    env.update({"ACTION_GATE_API_TOKEN":TOKEN,"ACTION_GATE_ENV":"development","ACTION_GATE_AUTHORITY_SECRET":"ci-authority-secret","ACTION_GATE_SIGNING_SECRET":"mcp-signing-secret","ACTION_GATE_DEBUG_AUTHORITY":"1","TOOL_NONCE_DB":"/tmp/risk-lab-tool-authority.db"})
    stack=subprocess.Popen([sys.executable,str(ROOT/"action_gate"/"mcp_integration.py")],cwd=str(ROOT/"action_gate"),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if all(_port_ready(port) for port in (8000, 9000, 8081)):
                break
            if stack.poll() is not None:
                output = stack.stdout.read() if stack.stdout else ""
                raise RuntimeError(f"mcp_integration.py exited early with code {stack.returncode}: {output[-4000:]}")
            time.sleep(0.5)
        else:
            output = stack.stdout.read() if stack.stdout else ""
            raise RuntimeError(f"Risk Lab stack did not become ready within 30s: {output[-4000:]}")

        payload={"target":TARGET,"purpose":"risk-lab-demo"}
        b_status,b_body=request("http://127.0.0.1:9100/tool",payload)

        evaluate={"agent_id":"risk-lab-agent","actor_id":ACTOR,"session_id":SESSION,"tenant_id":TENANT,"action":ACTION,"target":TARGET,"parameters":payload}
        _,ev=request("http://127.0.0.1:8000/v1/action/evaluate",evaluate,{"Authorization":f"Bearer {TOKEN}"})
        assert ev["decision"]=="ALLOW",ev
        reserve={"tenant_id":TENANT,"actor_id":ACTOR,"session_id":SESSION,"action_hash":ev["action_hash"],"nonce":ev["nonce"],"world_version":ev.get("world_version")}
        _,res=request(f"http://127.0.0.1:8000/v1/action/{ev['decision_id']}/execution/reserve",reserve,{"Authorization":f"Bearer {TOKEN}"})
        headers={"X-HCJ-Execution-Authority":res["execution_authority"],"X-HCJ-Action-Hash":ev["action_hash"],"X-HCJ-Policy-Hash":ev["policy_hash"],"X-Tenant-ID":TENANT}
        g_status,g_body=request("http://127.0.0.1:9000/tool",payload,headers)
        bypass_status,bypass_body=request("http://127.0.0.1:9000/tool",payload)
        replay_status,replay_body=request("http://127.0.0.1:9000/tool",payload,headers)

        scenarios=[
          {"id":"B01","name":"baseline_direct_execution","path":"unprotected reference endpoint","status":b_status,"executed":b_body.get("tool_executed") is True,"response":b_body,"result":"OBSERVED"},
          {"id":"G01","name":"governed_authorized_execution","path":"Action Gate -> protected tool","status":g_status,"executed":g_body.get("tool_executed") is True,"response":g_body,"result":"PASS" if g_status==200 and g_body.get("tool_executed") is True else "FAIL"},
          {"id":"G02","name":"direct_bypass","path":"direct protected-tool call without authority","status":bypass_status,"response":bypass_body,"result":"PASS" if bypass_status==403 else "FAIL"},
          {"id":"G03","name":"authority_replay","path":"same Gate-issued authority submitted twice","status":replay_status,"response":replay_body,"result":"PASS" if replay_status==403 else "FAIL"},
        ]
        report={"schema":"agent-action-risk-lab-demo-1.0","source":"HamidCognition-Unified","timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"scenarios":scenarios,"binding":{"tenant_id":TENANT,"actor_id":ACTOR,"session_id":SESSION,"action":ACTION,"target":TARGET,"decision_id":ev["decision_id"],"action_hash":ev["action_hash"],"policy_hash":ev["policy_hash"]},"interpretation":"Observed evidence only. B01 is a disposable local reference without an authorization boundary. G01-G03 exercise the repository's real protected HTTP tool. This report does not claim universal security, attack prevention, compliance, or ROI."}
        jp=ARTIFACTS/"risk-lab-demo.json"; mp=ARTIFACTS/"risk-lab-demo.md"
        jp.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        lines=["# Agent Action Risk Lab — Before/After Evidence","","| ID | Scenario | Path | HTTP | Result |","|---|---|---|---:|---|"]
        lines += [f"| {s['id']} | {s['name']} | {s['path']} | {s['status']} | {s['result']} |" for s in scenarios]
        lines += ["","","## Binding","",f"- Decision: {ev['decision_id']}",f"- Action hash: {ev['action_hash']}",f"- Policy hash: {ev['policy_hash']}","","## Interpretation","",report["interpretation"],""]
        mp.write_text("\n".join(lines),encoding="utf-8")
        failed=[s["id"] for s in scenarios if s["result"]=="FAIL"]
        print(json.dumps({"status":"PASS" if not failed else "FAIL","json":str(jp),"markdown":str(mp),"failed":failed},indent=2))
        return 0 if not failed else 1
    finally:
        baseline.shutdown(); stack.terminate()
        try: stack.wait(timeout=5)
        except subprocess.TimeoutExpired: stack.kill(); stack.wait(timeout=5)

if __name__=="__main__":
    raise SystemExit(run())
