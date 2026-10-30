#!/usr/bin/env python3
"""Classify whether a version tag names the exact Product Gates source commit."""
from __future__ import annotations

import re
import sys

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def classify_release_tag_target(target_sha: str, tag_type: str, tag_sha: str) -> str:
    if not _SHA_RE.fullmatch(target_sha) or not _SHA_RE.fullmatch(tag_sha):
        raise ValueError("invalid_commit_sha")
    if tag_type != "commit":
        raise ValueError("release_tag_did_not_resolve_to_commit")
    return "MATCH" if tag_sha == target_sha else "MISMATCH"


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: classify_release_tag_target.py TARGET_SHA TAG_TYPE TAG_SHA", file=sys.stderr)
        return 2
    try:
        result = classify_release_tag_target(argv[1], argv[2], argv[3])
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
