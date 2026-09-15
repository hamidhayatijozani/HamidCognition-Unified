"""Executable guard for research contradictions.

Input: a JSON ledger with entries containing id, claim, evidence, status and resolution.
The validator does not decide truth. It prevents unresolved contradictions from being
silently promoted to verified/canonical status.
"""
import json
import sys
from pathlib import Path

PROMOTION_BLOCKERS = {"UNRESOLVED", "CONTRADICTED", "OVERCLAIM"}
PROMOTABLE = {"VERIFIED", "IMPLEMENTED", "HYPOTHESIS", "UNKNOWN", "FALSIFIED", "SUPERSEDED"}


def validate(entries):
    errors = []
    ids = set()
    for e in entries:
        ident = e.get("id")
        if not ident or ident in ids:
            errors.append(f"invalid_or_duplicate_id:{ident}")
        ids.add(ident)
        if not e.get("claim"):
            errors.append(f"missing_claim:{ident}")
        if e.get("status") not in PROMOTABLE:
            errors.append(f"invalid_status:{ident}")
        if e.get("contradiction") and not e.get("resolution"):
            errors.append(f"unresolved_contradiction:{ident}")
        if e.get("promotion_blocked") and e.get("status") == "VERIFIED":
            errors.append(f"blocked_claim_marked_verified:{ident}")
    return errors


def main(path="RESEARCH/CONTRADICTION_LEDGER.yaml.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate(data.get("entries", []))
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "RESEARCH/CONTRADICTION_LEDGER.yaml.json"))
