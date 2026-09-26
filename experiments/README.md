# ChatGPT-style Action Gate experiment

This experiment places a controlled agent/tool harness in front of the HamidCognition Action Gate. It demonstrates the intended execution boundary:

`Agent/ChatGPT-style client -> Action Gate -> Protected Tool -> Evidence`

It is deliberately honest about the integration boundary. Running the harness does **not** intercept, modify, or control the internal ChatGPT runtime. It provides an executable, reproducible stand-in for a client that submits an action for authorization before a protected tool executes.

Run:

```bash
python experiments/chatgpt_action_gate_harness.py
```

Expected output includes the signed `ALLOW` decision, tenant/action/policy binding, nonce, authority digest, and the explicit `runtime_interception=false` boundary marker.

The next integration step is an actual MCP or HTTP client that submits real tool requests to the running Action Gate. That is the point where the harness can be replaced by a real external agent client without making unsupported claims about ChatGPT internals.
