from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


BASE_URL = os.getenv("MCP_TEST_URL", "http://127.0.0.1:8787")
TOKEN = os.getenv("MCP_BEARER_TOKEN", "")


def request(path: str, *, token: str | None = None) -> tuple[int, str]:
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "ping"},
        separators=(",", ":"),
    ).encode()
    headers = {
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
    }
    if token:
        headers["authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=payload,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def main() -> None:
    if not TOKEN:
        raise SystemExit("MCP_BEARER_TOKEN is required")

    unauth_status, _ = request("/mcp")
    if unauth_status != 401:
        raise SystemExit(f"expected unauthenticated MCP request to return 401, got {unauth_status}")

    metadata_req = urllib.request.Request(
        f"{BASE_URL}/.well-known/oauth-protected-resource/mcp",
        headers={"accept": "application/json"},
    )
    with urllib.request.urlopen(metadata_req, timeout=5) as response:
        metadata = json.loads(response.read().decode())

    expected_resource = f"{BASE_URL}/mcp"
    if metadata.get("resource") != expected_resource:
        raise SystemExit(
            f"protected-resource metadata mismatch: {metadata.get('resource')!r} != {expected_resource!r}"
        )

    if TOKEN in json.dumps(metadata):
        raise SystemExit("bearer token leaked into protected-resource metadata")

    auth_status, _ = request("/mcp", token=TOKEN)
    if auth_status != 200:
        raise SystemExit(f"expected authenticated MCP ping to return 200, got {auth_status}")

    print("MCP_AUTH_BOUNDARY=PASS")


if __name__ == "__main__":
    main()
