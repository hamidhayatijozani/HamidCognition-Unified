#!/usr/bin/env python3
"""Verify release-truth lineage without upgrading claims.

This verifier deliberately distinguishes:
  current source SHA
  immutable published release SHA
  optional production runtime state

It never treats a green CI run on another SHA as evidence for the current SHA.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRUTH = ROOT / "PRODUCT" / "RELEASE_TRUTH_RECORD.md"
CONTROL = ROOT / "PRODUCT" / "PRODUCT_COMPLETION_CONTROL.md"
SHA_RE = re.compile(r"\b[0-9a-f]{40}\b")
DIGEST_RE = re.compile(r"sha256:([0-9a-f]{64})")


def first_sha(text: str, label: str) -> str:
    m = re.search(label + r".*?([0-9a-f]{40})", text, re.I | re.S)
    if not m:
        raise ValueError(f"missing {label}")
    return m.group(1)


def first_digest(text: str) -> str:
    m = DIGEST_RE.search(text)
    if not m:
        raise ValueError("missing sha256 digest")
    return m.group(1)


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def probe_runtime(base_url: str) -> dict:
    base = base_url.rstrip("/")
    result = {"configured": True, "url": base}
    try:
        with urllib.request.urlopen(base + "/health", timeout=20) as r:
            body = r.read().decode("utf-8")
            result["health_http"] = r.status
            result["health_body"] = json.loads(body)
        with urllib.request.urlopen(base + "/", timeout=20) as r:
            result["root_http"] = r.status
        health = result["health_body"]
        result["verified"] = (
            health.get("status") == "ok"
            and health.get("state_oracle", {}).get("status") == "ready"
        )
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        result["verified"] = False
        result["error"] = str(exc)
    return result


def main() -> int:
    current = os.environ.get("GITHUB_SHA") or git_head()
    current = current.lower()
    if not SHA_RE.fullmatch(current):
        raise SystemExit(f"invalid current SHA: {current!r}")

    truth = TRUTH.read_text(encoding="utf-8")
    control = CONTROL.read_text(encoding="utf-8")

    release_sha = first_sha(truth, r"Release source commit:")
    release_digest = first_digest(truth)

    version_match = re.search(r"Current published technical release:\s*([^\s]+)", truth)
    version = version_match.group(1) if version_match else "UNKNOWN"

    same_sha = current == release_sha
    production_url = os.environ.get("PRODUCTION_BASE_URL", "").strip()

    report = {
        "schema": "evidence-chain-integrity/v1",
        "current_source_sha": current,
        "published_release": {
            "version": version,
            "source_sha": release_sha,
            "artifact_sha256": release_digest,
            "same_sha_as_current": same_sha,
        },
        "claims": {
            "current_main_is_published_release": same_sha,
            "release_truth_record_present": True,
            "completion_control_present": bool(control.strip()),
        },
        "production": (
            probe_runtime(production_url)
            if production_url
            else {"configured": False, "verified": False, "state": "BLOCKED"}
        ),
    }

    # Integrity of the immutable release record itself.
    if not SHA_RE.fullmatch(release_sha):
        raise SystemExit("invalid release source SHA")
    if not re.fullmatch(r"[0-9a-f]{64}", release_digest):
        raise SystemExit("invalid release artifact digest")

    out = Path(os.environ.get("EVIDENCE_OUTPUT", "evidence/evidence-chain-integrity.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    # Do not fail merely because main moved beyond the published release.
    # Fail only on malformed provenance or an explicitly configured unhealthy runtime.
    if production_url and not report["production"]["verified"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
