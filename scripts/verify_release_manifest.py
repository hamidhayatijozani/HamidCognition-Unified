#!/usr/bin/env python3
"""Fail-closed verification for an Action Gate release candidate manifest.

This validates artifact consistency. It does not replace GitHub's source-SHA,
tag-resolution, or workflow-run identity checks.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[.-][0-9A-Za-z.-]+)?$")


def parse_manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line or raw_line.startswith("#"):
            continue
        if "=" not in raw_line:
            raise ValueError(f"malformed manifest line: {raw_line!r}")
        key, value = raw_line.split("=", 1)
        if not key or key in values:
            raise ValueError(f"empty or duplicate manifest key: {key!r}")
        values[key] = value
    return values


def read_readiness_sha(path: Path) -> str:
    if not path.is_file():
        raise ValueError("readiness evidence file is missing")
    value = path.read_text(encoding="utf-8").strip()
    if not SHA_RE.fullmatch(value):
        raise ValueError("readiness evidence does not contain one full lowercase Git SHA")
    return value


def verify(manifest_path: Path, archive_path: Path, checksum_path: Path,
           expected_sha: str, expected_version: str, readiness_sha: str) -> None:
    manifest = parse_manifest(manifest_path)
    required = {
        "product", "version", "commit", "release_readiness_run_id",
        "image", "archive", "generated_at",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise ValueError(f"missing manifest fields: {', '.join(missing)}")

    source_sha = manifest["commit"]
    if not SHA_RE.fullmatch(source_sha):
        raise ValueError("manifest commit is not a full lowercase Git SHA")
    if not SHA_RE.fullmatch(expected_sha) or not SHA_RE.fullmatch(readiness_sha):
        raise ValueError("expected/readiness SHA is malformed")
    if source_sha != expected_sha or source_sha != readiness_sha:
        raise ValueError("manifest source SHA does not match readiness evidence")
    if not VERSION_RE.fullmatch(manifest["version"]):
        raise ValueError("manifest version is malformed")
    if manifest["version"] != expected_version:
        raise ValueError("manifest version does not match source version")
    if manifest["product"] != "HamidCognition Action Gate":
        raise ValueError("unexpected product identity")
    if manifest["archive"] != archive_path.name:
        raise ValueError("manifest archive name does not match artifact")
    if manifest["image"] != f"action-gate:{manifest['version']}":
        raise ValueError("manifest image tag does not match version")
    if not manifest["release_readiness_run_id"].isdigit():
        raise ValueError("readiness run ID is malformed")
    if not archive_path.is_file() or not checksum_path.is_file():
        raise ValueError("archive or checksum file is missing")

    checksum_lines = checksum_path.read_text(encoding="utf-8").splitlines()
    if len(checksum_lines) != 1:
        raise ValueError("checksum file must contain exactly one record")
    match = re.fullmatch(r"([0-9a-f]{64})\s+\*?(.+)", checksum_lines[0])
    if not match:
        raise ValueError("checksum record is malformed")
    recorded_hash, recorded_name = match.groups()
    if recorded_name != archive_path.name:
        raise ValueError("checksum filename does not match archive")
    actual_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if recorded_hash != actual_hash:
        raise ValueError("archive SHA-256 mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--checksum", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--readiness-file", type=Path, required=True)
    args = parser.parse_args()
    try:
        readiness_sha = read_readiness_sha(args.readiness_file)
        verify(args.manifest, args.archive, args.checksum,
               args.expected_sha, args.expected_version, readiness_sha)
    except (OSError, ValueError) as exc:
        print(f"RELEASE_ARTIFACT_REJECTED: {exc}", file=sys.stderr)
        return 1
    print("RELEASE_ARTIFACT_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
