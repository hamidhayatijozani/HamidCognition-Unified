# External-Agent Action Gate Experiment

This experiment exercises the HamidCognition Action Gate at a real HTTP and MCP enforcement boundary:

`External agent -> enforcement proxy -> Action Gate -> execution authority -> protected tool -> evidence`

The harness does **not** intercept, modify, or control the internal ChatGPT runtime. The `runtime_interception=false` marker is intentional. It demonstrates the enforceable external-agent boundary without making an unsupported claim about ChatGPT internals.

## What the harness proves

- A destructive MCP action is denied by policy.
- An allowed MCP action reaches the protected tool.
- The issued execution authority is single-use: replaying the same authority and action hash at the tool is rejected by the tool nonce guard.
- An HTTP decision cannot be rebound to a changed target because the action hash no longer matches.
- The recorded decision can be replayed against its frozen policy and normalized action, with policy and action hashes verified.

Run:

```bash
python experiments/chatgpt_action_gate_harness.py
```

A successful run emits explicit markers for the MCP boundary, replay attack blocking, binding attack blocking, and evidence replay verification. No signing or API secrets are printed.
