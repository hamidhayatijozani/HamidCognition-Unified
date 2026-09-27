from __future__ import annotations
import hashlib
import json
from typing import Any

def evidence_hash(record: dict[str, Any]) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def build_evidence(*, operation_id: str, source_events: list[dict[str, Any]], candidates: list[dict[str, Any]], decision: str, execution_state: str, destination: str, verification: dict[str, Any] | None = None) -> dict[str, Any]:
    record = {
        "schema_version": "financial-evidence-1.0",
        "operation_id": operation_id,
        "source_events": source_events,
        "candidates": candidates,
        "decision": decision,
        "execution_state": execution_state,
        "destination": destination,
        "verification": verification,
    }
    record["evidence_hash"] = evidence_hash(record)
    return record
