from __future__ import annotations

import json
import os
from typing import Mapping


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
    secret = os.getenv("ACTION_GATE_SIGNING_SECRET")
    if secret:
        return {os.getenv("ACTION_GATE_KEY_ID", "hhj-csg-poc-1"): secret}
    return {}


def current_key_id() -> str:
    configured = _configured_keys()
    key_id = os.getenv("ACTION_GATE_KEY_ID", "hhj-csg-poc-1")
    if configured and key_id not in configured:
        raise RuntimeError("action_gate_current_key_id_not_configured")
    return key_id


def current_secret() -> str | None:
    keys = _configured_keys()
    if not keys:
        return None
    return keys.get(current_key_id())


def verify_with_keyring(payload: Mapping[str, object], signature: str, key_id: str) -> bool:
    keys = _configured_keys()
    secret = keys.get(key_id)
    if not secret:
        return False
    import hmac
    import hashlib
    import json
    canonical = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    expected = hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def configured_key_ids() -> list[str]:
    return sorted(_configured_keys())
