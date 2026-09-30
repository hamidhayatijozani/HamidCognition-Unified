from __future__ import annotations

import json
import os


def _configured_keys() -> dict[str, str]:
    raw = os.getenv("ACTION_GATE_SIGNING_KEYS")
    if raw:
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict) or not parsed:
                raise ValueError("ACTION_GATE_SIGNING_KEYS must be a non-empty object")
            keys = {str(k): str(v) for k, v in parsed.items() if str(v)}
            if not keys:
                raise ValueError("ACTION_GATE_SIGNING_KEYS contains no usable keys")
            return keys
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise RuntimeError("invalid_action_gate_signing_keys") from exc

    secret = os.getenv("ACTION_GATE_SIGNING_SECRET") or os.getenv("ACTION_GATE_AUTHORITY_SECRET")
    if secret:
        return {os.getenv("ACTION_GATE_KEY_ID", "hhj-action-gate-1"): secret}
    return {}


def current_key_id() -> str:
    configured = _configured_keys()
    key_id = os.getenv("ACTION_GATE_KEY_ID", "hhj-action-gate-1")
    if configured and key_id not in configured:
        raise RuntimeError("action_gate_current_key_id_not_configured")
    return key_id


def current_secret() -> str | None:
    return _configured_keys().get(current_key_id())


def secret_for_key_id(key_id: str) -> str | None:
    return _configured_keys().get(key_id)


def verify_with_keyring(payload, signature: str, key_id: str) -> bool:
    secret = secret_for_key_id(key_id)
    if not secret:
        return False
    import hmac
    import hashlib
    canonical = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    expected = hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def configured_key_ids() -> list[str]:
    return sorted(_configured_keys())
