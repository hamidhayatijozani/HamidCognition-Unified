from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any

CANONICALIZATION_VERSION = "JCS-LIKE-1"
SIGNATURE_ALGORITHM = "HMAC-SHA256"
KEY_ID = os.getenv("ACTION_GATE_KEY_ID", "hhj-csg-1")


def signing_keys() -> dict[str, str]:
    """Return the configured signing keyring.

    ACTION_GATE_SIGNING_KEYS is a JSON object mapping key IDs to secrets. The
    legacy ACTION_GATE_SIGNING_SECRET remains supported as a single-key
    fallback, which keeps development and existing deployments compatible.
    """
    raw = os.getenv("ACTION_GATE_SIGNING_KEYS")
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and all(isinstance(k, str) and isinstance(v, str) and v for k, v in parsed.items()):
                return parsed
        except json.JSONDecodeError:
            pass
    secret = os.getenv("ACTION_GATE_SIGNING_SECRET")
    return {KEY_ID: secret} if secret else {}


def current_signing_secret() -> str | None:
    return signing_keys().get(KEY_ID)


def signing_secret_for_key(key_id: str) -> str | None:
    return signing_keys().get(key_id)


def canonicalize(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonicalize(value)).hexdigest()


def hmac_sha256(value: Any, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), canonicalize(value), hashlib.sha256).hexdigest()


def verify_hmac(value: Any, signature: str, secret: str) -> bool:
    return hmac.compare_digest(hmac_sha256(value, secret), signature)
