"""Maintenance command for consumed execution-authority nonces.

Run from a trusted maintenance environment, for example:
python scripts/cleanup_authority_nonces.py --older-than-seconds 86400
"""
from __future__ import annotations

import argparse

from action_gate.storage import init_db, purge_authority_nonces


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--older-than-seconds", type=int, required=True)
    args = parser.parse_args()
    init_db()
    deleted = purge_authority_nonces(args.older_than_seconds)
    print(f"Deleted {deleted} expired execution-authority nonce records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
