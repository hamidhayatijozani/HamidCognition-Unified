"""Contract-first primitives for the HHJ-CSG vertical slice.

The digest is an integrity identifier, not an authenticity proof. HMAC is the
separate authenticity mechanism and is computed over the exact canonical bytes.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any, Mapping

CANONICALIZATION_VERSION = "JCS-LITE-0.1"
REQUEST_CONTRACT_VERSION = "PR-0.1"
DECISION_CONTRACT_VERSION = "DO-0.1"
SIGNATURE_ALGORITHM = "HMAC-SHA256"
SCHEMA_DIR = Path(__file__).with_name("contracts")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def hmac_sha256(value: Any, secret: bytes | str) -> str:
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    return hmac.new(key, canonical_bytes(value), hashlib.sha256).hexdigest()


def verify_hmac(value: Any, signature: str, secret: bytes | str) -> bool:
    if not isinstance(signature, str) or len(signature) != 64:
        return False
    expected = hmac_sha256(value, secret)
    return hmac.compare_digest(expected, signature)


def load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def decision_signing_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    """Return immutable Decision Object fields covered by HMAC.

    ``replayed`` is transport metadata added by the idempotency endpoint after
    the signed Decision Object is constructed. It is deliberately excluded from
    authenticity and digest calculations because it is not decision authority.
    """
    return {k: decision[k] for k in decision if k not in {"signature", "replayed"}}
