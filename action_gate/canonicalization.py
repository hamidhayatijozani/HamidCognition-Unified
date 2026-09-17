from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any

CANONICALIZATION_VERSION = "JCS-LIKE-1"
SIGNATURE_ALGORITHM = "HMAC-SHA256"
KEY_ID = os.getenv("ACTION_GATE_KEY_ID", "hhj-csg-poc-1")


def canonicalize(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonicalize(value)).hexdigest()


def hmac_sha256(value: Any, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), canonicalize(value), hashlib.sha256).hexdigest()


def verify_hmac(value: Any, signature: str, secret: str) -> bool:
    return hmac.compare_digest(hmac_sha256(value, secret), signature)
