#!/usr/bin/env python3
"""Verify the canonical product-version source.

The gate scans all tracked text, but distinguishes product-version-bearing
documents from historical records and CI/tooling metadata. A semver-like
token in a classified historical/CI file is not a product-version authority.
"""
from __future__ import annotations
import fnmatch, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PRODUCT" / "VERSION_SOURCES.json"
VERSION_LIKE = re.compile(r"(?<![A-Za-z0-9])v?\d+\.\d+(?:\.\d+)?(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?(?![A-Za-z0-9])")

def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item for item in output.decode().split("\0") if item]

def path_matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)

def has_product_context(text: str, start: int, end: int, window: int = 100) -> bool:
    context = re.compile(
        r"(?:product\s+version|version\s+source|current\s+(?:customer-facing\s+)?release"
        r"|release\s+(?:version|tag)|published\s+as|semantic\s+version"
        r"|(?:current|latest|canonical)\s+version)\\b",
        re.IGNORECASE,
    )
    before = text[max(0, start - window):start]
    after = text[end:min(len(text), end + window)]
    return bool(context.search(before) or context.search(after))

def main() -> int:
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical = spec["canonical"]
    derived = set(spec["derived"])
    ignored = set(spec.get("ignored", []))
    env_metadata = spec.get("env_metadata", [])
    offenders: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if (relative == canonical or relative == "PRODUCT/VERSION_SOURCES.json" or relative in derived
                or relative in ignored or path_matches(relative, env_metadata)):
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(has_product_context(text, m.start(), m.end()) for m in VERSION_LIKE.finditer(text)):
            offenders.append(relative)
    if offenders:
        print("UNDECLARED_VERSION_SOURCES")
        print("\n".join(sorted(offenders)))
        return 1
    print(f"VERSION_SOURCE_OK canonical={canonical} derived={len(derived)} ignored={len(ignored)} env_metadata={len(env_metadata)} scanned=all-tracked-text")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
