#!/usr/bin/env python3
"""Validate the HamidCognition model-weight admission registry."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REGISTRY = Path("MODEL/WEIGHT_REGISTRY.json")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_FORMATS = {
    "safetensors", "onnx", "gguf", "pytorch_state_dict",
    "tensorflow_checkpoint", "other",
}
REQUIRED = {
    "model_id", "source_repository", "source_revision", "artifact_path",
    "artifact_sha256", "weight_format", "runtime", "license",
    "verified_at", "release_binding",
}


def fail(message: str) -> None:
    print(f"MODEL-WEIGHT-REGISTRY: FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    if not REGISTRY.is_file():
        fail(f"missing {REGISTRY}")

    raw = REGISTRY.read_bytes()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")

    if data.get("schema_version") != "1.0.0":
        fail("unsupported schema_version")

    models = data.get("models")
    if not isinstance(models, list):
        fail("models must be a list")

    seen = set()
    for index, model in enumerate(models):
        if not isinstance(model, dict):
            fail(f"models[{index}] must be an object")

        missing = sorted(REQUIRED - model.keys())
        if missing:
            fail(f"models[{index}] missing fields: {', '.join(missing)}")

        model_id = model["model_id"]
        if not isinstance(model_id, str) or not model_id or model_id in seen:
            fail(f"models[{index}] has invalid or duplicate model_id")
        seen.add(model_id)

        digest = model["artifact_sha256"]
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            fail(f"{model_id}: artifact_sha256 must be a 64-character lowercase SHA-256")

        if model["weight_format"] not in ALLOWED_FORMATS:
            fail(f"{model_id}: unsupported weight_format")

        for field in ("source_repository", "source_revision", "artifact_path",
                      "runtime", "license", "verified_at", "release_binding"):
            if not isinstance(model[field], str) or not model[field].strip():
                fail(f"{model_id}: {field} must be non-empty")

        if model["source_revision"] in {"main", "master", "latest", "HEAD"}:
            fail(f"{model_id}: mutable source revision is forbidden")

    registry_sha256 = hashlib.sha256(raw).hexdigest()
    print("MODEL-WEIGHT-REGISTRY: PASS")
    print(f"models={len(models)}")
    print(f"registry_sha256={registry_sha256}")


if __name__ == "__main__":
    main()
