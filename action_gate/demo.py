import json
import os
import urllib.request

BASE = os.getenv("ACTION_GATE_URL", "http://127.0.0.1:8000")


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


scenarios = [
    {"name": "delete production file", "payload": {"agent_id": "demo-agent", "action": "delete_file", "target": "/production/data.db"}},
    {"name": "external customer email", "payload": {"agent_id": "demo-agent", "action": "send_email", "target": "customer@example.com"}},
    {"name": "financial transfer", "payload": {"agent_id": "demo-agent", "action": "transfer_funds", "target": "account_123", "parameters": {"amount": 1000}}},
]

for item in scenarios:
    result = post("/v1/action/evaluate", item["payload"])
    print(item["name"], "=>", result["decision"], result["risk_assessment"]["level"], result["decision_id"])
