#!/usr/bin/env python3
"""Verify that action_gate/VERSION is the only authoritative version source."""
from __future__ import annotations
import fnmatch, json, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PRODUCT" / "VERSION_SOURCES.json"
SEMVER = re.compile(r"(?<![A-Za-z0-9])v?(\d+\.\d+\.\d+)(?![A-Za-z0-9])")
def tracked_files():
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item for item in output.decode().split("\0") if item]
def main():
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical = spec["canonical"]
    derived = set(spec["derived"])
    offenders = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative == canonical or relative == "PRODUCT/VERSION_SOURCES.json" or not path.is_file():
            continue
        if not any(fnmatch.fnmatch(relative, pattern) for pattern in spec["version_bearing_source_classes"]):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if SEMVER.search(text) and relative not in derived:
            offenders.append(relative)
    if offenders:
        print("UNDECLARED_VERSION_SOURCES")
        print("\n".join(sorted(offenders)))
        return 1
    print(f"VERSION_SOURCE_OK canonical={canonical} derived={len(derived)}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
