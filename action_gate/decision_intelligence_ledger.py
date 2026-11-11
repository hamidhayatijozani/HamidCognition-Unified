"""Append-only decision ledger for independent gate and reviewer outcomes.

This module uses only the Python standard library. It provides tamper-evident
hash chaining, explicit disagreement records, and bounded batch analytics.
It is an audit aid, not a cryptographic signature or a substitute for access
controls and durable storage.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"
VALID_RISKS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_DECISIONS = {"ALLOW", "DENY", "HOLD", "ASK", "SANDBOX", "UNKNOWN"}
_LOCK = threading.RLock()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


class LedgerError(ValueError):
    """Raised when a record is invalid or the ledger chain is broken."""


class DecisionLedger:
    """JSONL ledger with hash-linked records; existing records are never rewritten."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read_records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise LedgerError(f"invalid JSON at line {line_number}") from exc
                if not isinstance(item, dict):
                    raise LedgerError(f"record at line {line_number} is not an object")
                records.append(item)
        return records

    def verify(self) -> dict[str, Any]:
        records = self._read_records()
        previous = "GENESIS"
        for index, record in enumerate(records, 1):
            claimed = record.get("record_hash")
            body = {key: value for key, value in record.items() if key != "record_hash"}
            if record.get("previous_hash") != previous:
                raise LedgerError(f"broken previous_hash at record {index}")
            actual = _digest(body)
            if claimed != actual:
                raise LedgerError(f"record hash mismatch at record {index}")
            previous = claimed
        return {"valid": True, "records": len(records), "head_hash": previous}

    def append(
        self,
        *,
        component: str,
        risk: str,
        primary_decision: str,
        reviewer_decision: str,
        evidence: dict[str, Any],
        source_sha: str,
        component_version: str,
        run_id: str | None = None,
        observed_outcome: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not component.strip():
            raise LedgerError("component is required")
        risk = risk.upper()
        primary_decision = primary_decision.upper()
        reviewer_decision = reviewer_decision.upper()
        if risk not in VALID_RISKS:
            raise LedgerError(f"risk must be one of {sorted(VALID_RISKS)}")
        if primary_decision not in VALID_DECISIONS or reviewer_decision not in VALID_DECISIONS:
            raise LedgerError(f"decisions must be one of {sorted(VALID_DECISIONS)}")
        if not isinstance(evidence, dict):
            raise LedgerError("evidence must be an object")
        if not source_sha.strip() or not component_version.strip():
            raise LedgerError("source_sha and component_version are required")

        with _LOCK:
            # Verify before extending, so a damaged history is never silently continued.
            verified = self.verify()
            record = {
                "schema_version": SCHEMA_VERSION,
                "event_id": str(uuid.uuid4()),
                "timestamp_unix": time.time(),
                "component": component,
                "risk": risk,
                "primary_decision": primary_decision,
                "reviewer_decision": reviewer_decision,
                "agreement": primary_decision == reviewer_decision,
                "disposition": (
                    "REVIEW_REQUIRED"
                    if primary_decision != reviewer_decision
                    else "REVIEW_REQUIRED"
                    if risk in {"HIGH", "CRITICAL"} and primary_decision in {"ALLOW", "UNKNOWN"}
                    else "RECORDED"
                ),
                "source_sha": source_sha,
                "component_version": component_version,
                "run_id": run_id,
                "evidence": evidence,
                "observed_outcome": observed_outcome,
                "metadata": metadata or {},
                "previous_hash": verified["head_hash"],
            }
            record["record_hash"] = _digest(record)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            return record.copy()

    def records(self, component: str | None = None) -> list[dict[str, Any]]:
        records = self._read_records()
        if component is not None:
            records = [record for record in records if record.get("component") == component]
        return records

    def report(self, *, component: str | None = None, batch_size: int = 100) -> dict[str, Any]:
        if batch_size < 1:
            raise LedgerError("batch_size must be >= 1")
        records = self.records(component)
        batches = []
        for offset in range(0, len(records), batch_size):
            batch = records[offset : offset + batch_size]
            agreements = sum(bool(item.get("agreement")) for item in batch)
            disagreements = len(batch) - agreements
            batches.append({
                "start_record": offset + 1,
                "end_record": offset + len(batch),
                "decisions": len(batch),
                "agreements": agreements,
                "disagreements": disagreements,
                "agreement_rate": agreements / len(batch) if batch else None,
                "review_required": sum(item.get("disposition") == "REVIEW_REQUIRED" for item in batch),
                "unknown_votes": sum(
                    item.get("primary_decision") == "UNKNOWN" or item.get("reviewer_decision") == "UNKNOWN"
                    for item in batch
                ),
            })
        overall_agreements = sum(bool(item.get("agreement")) for item in records)
        return {
            "schema_version": SCHEMA_VERSION,
            "component": component,
            "total_decisions": len(records),
            "agreement_rate": overall_agreements / len(records) if records else None,
            "disagreements": len(records) - overall_agreements,
            "batches": batches,
        }
