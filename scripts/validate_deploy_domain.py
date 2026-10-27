#!/usr/bin/env python3
"""Validate a deployment hostname before it is interpolated into SSH commands."""
from __future__ import annotations

import re
import sys

_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")


def is_valid_dns_name(value: str) -> bool:
    if not value or len(value) > 253:
        return False
    labels = value.split(".")
    return all(len(label) <= 63 and _LABEL.fullmatch(label) is not None for label in labels)


def self_test() -> int:
    valid = ["gate.example.com", "localhost", "a-b.example", "A1.example"]
    invalid = [
        "", ".example.com", "example.com.", "example..com", "-bad.example",
        "bad-.example", "example.com;id", "$(id).example.com", "example.com$()",
        "example.com|id", "example.com value", "example.com/health", "user@example.com",
        "x" * 64 + ".example", ".".join(["x" * 63] * 5),
    ]
    failures = [value for value in valid if not is_valid_dns_name(value)]
    failures.extend(value for value in invalid if is_valid_dns_name(value))
    if failures:
        print("deployment-domain validator self-test failed")
        return 1
    print(f"deployment-domain validator self-test passed ({len(valid) + len(invalid)} cases)")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) != 1 or not is_valid_dns_name(argv[0]):
        print("Invalid deployment domain: expected a DNS hostname with valid labels.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
