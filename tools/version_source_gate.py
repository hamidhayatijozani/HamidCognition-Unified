#!/usr/bin/env python3
"""Verify the canonical product-version source.

The gate scans all tracked text, but distinguishes product-version-bearing
documents from historical records and CI/tooling metadata. A semver-like
token in a classified historical/CI file is not a product-version authority.
"""
from __future__ import annotations
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PRODUCT" / "VERSION_SOURCES.json"
VERSION_LIKE = re.compile(r"(?<![A-Za-z0-9])v?\d+\.\d+(?:\.\d+)?(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?(?![A-Za-z0-9])")

def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item for item in output.decode().split("\0") if item]

def main() -> int:
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical = spec["canonical"]
    derived = set(spec["derived"])
    ignored = set(spec.get("ignored", []))
    offenders: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative == canonical or relative == "PRODUCT/VERSION_SOURCES.json" or relative in derived or relative in ignored:
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if VERSION_LIKE.search(text):
            offenders.append(relative)
    if offenders:
        print("UNDECLARED_VERSION_SOURCES")
        print("\n".join(sorted(offenders)))
        return 1
    print(f"VERSION_SOURCE_OK canonical={canonical} derived={len(derived)} ignored={len(ignored)} scanned=all-tracked-text")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
