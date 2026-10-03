#!/usr/bin/env python3
"""Evidence-aware semantic document synchronization."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "PRODUCT" / "DOCUMENT_DEPENDENCY_MAP.yaml"
CANONICAL_RELEASE = ROOT / "PRODUCT" / "COMMERCIAL_RELEASE.json"
STATE_PATH = ROOT / "evidence" / "document-sync-state.json"

VERSION_RE = re.compile(r"\bv(\d+\.\d+\.\d+)\b")
TAG_RE = re.compile(r"(?:GitHub release\s+|published as\s+(?:the\s+)?immutable\s+GitHub release\s+)`?([A-Za-z0-9._-]+)`?", re.I)
VERSION_PATH = ROOT / "action_gate" / "VERSION"

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def git_value(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def published_release_text(text: str) -> str:
    """Select the last validated published-release section, not the dev line."""
    marker = "## Last validated published release"
    if marker in text:
        return text.split(marker, 1)[1]

    # Customer-facing README may carry the published identity; QUICKSTART is intentionally version-free.
    prose = "last validated published commercial release"
    lower = text.lower()
    if prose in lower:
        return text[lower.index(prose):]

    return text

def product_version() -> str:
    version = VERSION_PATH.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("action_gate/VERSION must contain exactly one semantic version")
    return version

def canonical_identity() -> dict[str, str]:
    identity = json.loads(CANONICAL_RELEASE.read_text(encoding="utf-8"))
    required = ("version", "release_tag", "source_commit")
    if any(not identity.get(key) for key in required):
        raise ValueError("Structured commercial release identity is incomplete")
    if not re.fullmatch(r"\d+\.\d+\.\d+", identity["version"]):
        raise ValueError("Commercial release version is invalid")
    if not re.fullmatch(r"[0-9a-f]{40}", identity["source_commit"], re.I):
        raise ValueError("Commercial release source_commit is invalid")
    if identity["version"] != product_version():
        raise ValueError("Commercial release version does not match action_gate/VERSION")
    return {
        "release_version": identity["version"],
        "release_tag": identity["release_tag"],
        "source_commit": identity["source_commit"],
        "canonical_sha256": sha256_text(CANONICAL_RELEASE.read_text(encoding="utf-8")),
    }

def documented_identity(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    source = published_release_text(text)
    result: dict[str, str] = {}
    for key, pattern in (("release_version", VERSION_RE), ("release_tag", TAG_RE)):
        match = pattern.search(source)
        if match:
            result[key] = match.group(1)
    return result

def load_declared_paths() -> list[str]:
    paths: list[str] = []
    for line in MAP_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*- (.+)$", line)
        if match and "/" in match.group(1):
            candidate = match.group(1).strip()
            if candidate.endswith((".md", ".py", ".yml", ".yaml", ".json")):
                paths.append(candidate)
    return sorted(set(paths))

def apply_safe_updates(identity: dict[str, str]) -> list[str]:
    """Update only deterministic release identity in approved AUTO documents."""
    changed: list[str] = []
    for relative in ("README.md",):
        path = ROOT / relative
        original = path.read_text(encoding="utf-8")
        updated = original
        if relative == "README.md":
            updated = re.sub(
                r"current customer-facing release is \*\*v\d+\.\d+\.\d+\*\*",
                f"current customer-facing release is **v{identity['release_version']}**",
                updated,
            )
            updated = re.sub(
                r"published as (?:the immutable\s+)?GitHub release\s+`?[^` )]+`?(?: at source commit `?[0-9a-f]{40}`?)?",
                f"published as the immutable GitHub release `{identity['release_tag']}` at source commit {identity['source_commit']}",
                updated,
            )
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(relative)
    return changed
def build_state() -> dict[str, Any]:
    identity = canonical_identity()
    paths = load_declared_paths()
    fingerprints: dict[str, str] = {}
    missing: list[str] = []
    for relative in paths:
        path = ROOT / relative
        if path.exists():
            fingerprints[relative] = sha256_text(path.read_text(encoding="utf-8"))
        else:
            missing.append(relative)

    stale: list[dict[str, Any]] = []
    for relative in ("README.md",):
        path = ROOT / relative
        if not path.exists():
            stale.append({"document": relative, "reason": "missing"})
            continue
        observed = documented_identity(path)
        mismatches = {key: {"expected": identity[key], "observed": observed.get(key)}
                      for key in ("release_version", "release_tag")
                      if observed.get(key) != identity[key]}
        if mismatches:
            stale.append({"document": relative, "reason": "release_identity_drift",
                          "fields": mismatches})

    return {"schema": "hamidcognition.document-sync.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repository_commit": git_value(["rev-parse", "HEAD"]),
            "canonical_release": identity,
            "declared_source_fingerprints": fingerprints,
            "missing_sources": missing,
            "stale_documents": stale,
            "status": "STALE" if stale or missing else "CURRENT"}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply-safe", action="store_true")
    args = parser.parse_args()
    identity = canonical_identity()
    if args.apply_safe:
        changed = apply_safe_updates(identity)
        if changed:
            print(json.dumps({"safe_updates": changed}))
    state = build_state()
    if args.write_state:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    print(json.dumps(state, indent=2, sort_keys=True))
    if args.check and state["status"] != "CURRENT":
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
