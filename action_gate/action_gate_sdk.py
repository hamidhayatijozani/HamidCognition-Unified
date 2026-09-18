from __future__ import annotations

import hashlib
import hmac
import json
import os
import urllib.request
from typing import Any


class ActionGateError(RuntimeError):
    pass


class ActionGateClient:
    """Small dependency-free client for the Action Gate HTTP contract."""

    def __init__(self, base_url: str, token: str | None = None, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.token = token or os.getenv("ACTION_GATE_API_TOKEN")
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.base_url + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read())
        except Exception as exc:
            raise ActionGateError(str(exc)) from exc

    def evaluate(self, *, tenant_id: str, agent_id: str, actor_id: str | None, session_id: str | None = None, action: str,
                 target: str | None = None, parameters: dict[str, Any] | None = None,
                 context: dict[str, Any] | None = None, evidence: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return self._request("POST", "/v1/action/evaluate", {
            "tenant_id": tenant_id, "agent_id": agent_id, "actor_id": actor_id, "session_id": session_id,
            "action": action, "target": target, "parameters": parameters or {},
            "context": context or {}, "evidence": evidence or [],
        })

    def self_audit(self, *, tenant_id: str, actor_id: str, session_id: str, action: str,
                   target: str | None = None, claim: str | None = None,
                   evidence: list[dict[str, Any]] | None = None,
                   external_side_effect: bool = False, mutating: bool = False,
                   requires_model_internal_access: bool = False) -> dict[str, Any]:
        return self._request("POST", "/v1/self-audit", {
            "tenant_id": tenant_id, "actor_id": actor_id, "session_id": session_id,
            "action": action, "target": target, "claim": claim,
            "evidence": evidence or [], "external_side_effect": external_side_effect,
            "mutating": mutating, "requires_model_internal_access": requires_model_internal_access,
        })

    def evidence(self, decision_id: str, tenant_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/evidence/{decision_id}?tenant_id={tenant_id}")

    def replay(self, decision_id: str, tenant_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/replay/{decision_id}?tenant_id={tenant_id}")


def verify_hmac_attestation(decision_id: str, action_hash: str, nonce: str, attestation: str, secret: str) -> bool:
    message = f"{decision_id}:{action_hash}:{nonce}".encode()
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, attestation)
