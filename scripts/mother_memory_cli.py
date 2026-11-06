"""Command-line interface for the local BESAZ Mother Memory store."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from src.mother_memory import MotherMemory, MemoryValidationError


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Manage a private, local multi-model perspective memory.")
    parser.add_argument("--store", help="Private store directory (or set BESAZ_MOTHER_MEMORY_DIR).")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize the local store.")
    add = sub.add_parser("add", help="Import one structured model assessment JSON file.")
    add.add_argument("--file", required=True, help="Path to the model assessment JSON file.")
    add.add_argument("--consent", action="store_true", help="Confirm the user explicitly consented to storing this assessment.")
    listing = sub.add_parser("list", help="List active model assessments.")
    listing.add_argument("--model")
    sub.add_parser("compare", help="Compare attributed assessments without auto-consensus.")
    sub.add_parser("emergence", help="Find exact recurring pattern labels across model providers for human review.")
    sub.add_parser("audit", help="Verify the metadata-only audit hash chain.")
    review = sub.add_parser("review", help="Review an assessment.")
    review.add_argument("--id", required=True)
    review.add_argument("--status", required=True, choices=["ACCEPTED", "DISPUTED", "NEEDS_REVISION"])
    review.add_argument("--note", default="")
    delete = sub.add_parser("delete", help="Delete assessment content while retaining a metadata-only deletion event.")
    delete.add_argument("--id", required=True)

    args = parser.parse_args(argv)
    try:
        store = MotherMemory(args.store)
        if args.command == "init":
            emit(store.snapshot())
        elif args.command == "add":
            if not args.consent:
                raise MemoryValidationError("pass --consent only after explicit user consent")
            payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
            emit(store.record_assessment(payload, consent=True))
        elif args.command == "list":
            emit(store.list_assessments(model=args.model))
        elif args.command == "compare":
            emit(store.compare_models())
        elif args.command == "emergence":
            emit(store.detect_emergence())
        elif args.command == "audit":
            emit(store.verify_audit_chain())
        elif args.command == "review":
            emit(store.review_assessment(args.id, status=args.status, reviewer_note=args.note))
        elif args.command == "delete":
            emit({"deleted": store.delete_assessment(args.id)})
        return 0
    except (OSError, ValueError, json.JSONDecodeError, MemoryValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
