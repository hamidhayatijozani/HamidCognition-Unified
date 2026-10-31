"""Private, evidence-bounded multi-model perspective memory for BESAZ.

The repository contains code and schemas only. Runtime records default to an
ignored local data directory and must never be committed to a public repository.
This module stores model assessments, not hidden chain-of-thought or claims of
objective truth about a person.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

STORE_ENV = "BESAZ_MOTHER_MEMORY_DIR"
STORE_VERSION = "1.0.0"
FILES = {
    "memory": "memory.json",
    "concepts": "concepts.json",
    "sessions": "sessions.json",
    "emergence": "emergence.json",
    "governance": "governance.json",
    "manifest": "manifest.json",
}
DEFAULT_GOVERNANCE = {
    "consent_required": True,
    "store_raw_transcripts": False,
    "store_hidden_chain_of_thought": False,
    "allow_sensitive_trait_inference": False,
    "require_model_provenance": True,
    "require_evidence_references": True,
    "require_uncertainty": True,
    "public_repository_records_allowed": False,
    "human_review_required_for_profile_changes": True,
}
FORBIDDEN_KEYS = {"chain_of_thought", "hidden_reasoning", "private_reasoning", "raw_transcript"}


class MemoryValidationError(ValueError):
    """Raised when an assessment violates the memory contract."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _empty_state() -> dict[str, Any]:
    return {
        "memory": {"schema_version": STORE_VERSION, "assessments": []},
        "concepts": {"schema_version": STORE_VERSION, "items": []},
        "sessions": {"schema_version": STORE_VERSION, "items": []},
        "emergence": {"schema_version": STORE_VERSION, "items": []},
        "governance": dict(DEFAULT_GOVERNANCE),
        "manifest": {
            "store_version": STORE_VERSION,
            "created_at": _now(),
            "subject_key": "creator",
            "privacy": "LOCAL_PRIVATE_DATA",
            "files": dict(FILES),
        },
    }


class MotherMemory:
    """Local JSON store for attributed model perspectives and evidence metadata."""

    def __init__(self, root: str | Path | None = None):
        configured = root or os.environ.get(STORE_ENV)
        self.root = Path(configured).expanduser() if configured else Path("data/mother_memory")
        self.root.mkdir(parents=True, exist_ok=True)
        self._ensure_store()

    def _path(self, key: str) -> Path:
        return self.root / FILES[key]

    def _ensure_store(self) -> None:
        for key, value in _empty_state().items():
            path = self._path(key)
            if not path.exists():
                _atomic_json(path, value)
        audit = self.root / "audit.jsonl"
        audit.touch(exist_ok=True)

    def _read(self, key: str) -> dict[str, Any]:
        with self._path(key).open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise MemoryValidationError(f"{key} store must contain a JSON object")
        return value

    def _write(self, key: str, value: dict[str, Any]) -> None:
        _atomic_json(self._path(key), value)

    def governance(self) -> dict[str, Any]:
        return self._read("governance")

    def _audit(self, action: str, record_id: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        path = self.root / "audit.jsonl"
        previous = ""
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        previous = json.loads(line)["event_hash"]
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": _now(),
            "action": action,
            "record_id": record_id,
            "metadata": metadata or {},
            "previous_hash": previous,
        }
        event["event_hash"] = _hash(event)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event

    @staticmethod
    def _validate_assessment(payload: dict[str, Any], consent: bool) -> dict[str, Any]:
        if not consent:
            raise MemoryValidationError("explicit user consent is required before storing a model assessment")
        if not isinstance(payload, dict):
            raise MemoryValidationError("assessment must be a JSON object")
        if FORBIDDEN_KEYS.intersection(payload):
            raise MemoryValidationError("raw transcripts and hidden reasoning are not accepted")
        model = payload.get("model")
        if not isinstance(model, dict) or not all(str(model.get(k, "")).strip() for k in ("provider", "name", "version")):
            raise MemoryValidationError("model.provider, model.name and model.version are required")
        scope = payload.get("scope")
        if not isinstance(scope, str) or not scope.strip():
            raise MemoryValidationError("scope is required")
        observations = payload.get("observations", [])
        interpretations = payload.get("interpretations", [])
        evidence = payload.get("evidence_refs", [])
        uncertainty = payload.get("uncertainty")
        if not isinstance(observations, list) or not isinstance(interpretations, list) or not isinstance(evidence, list):
            raise MemoryValidationError("observations, interpretations and evidence_refs must be arrays")
        if not uncertainty or not isinstance(uncertainty, str):
            raise MemoryValidationError("uncertainty must explicitly describe what is unknown")
        if not evidence:
            raise MemoryValidationError("at least one evidence reference is required; do not store unsupported impressions")
        for item in observations:
            if not isinstance(item, dict) or not str(item.get("text", "")).strip():
                raise MemoryValidationError("each observation needs non-empty text")
            if item.get("kind", "OBSERVATION") != "OBSERVATION":
                raise MemoryValidationError("observations must be explicitly classified OBSERVATION")
        for item in interpretations:
            if not isinstance(item, dict) or not str(item.get("text", "")).strip():
                raise MemoryValidationError("each interpretation needs non-empty text")
            if item.get("kind") not in ("INFERENCE", "INTERPRETATION"):
                raise MemoryValidationError("interpretations must be INFERENCE or INTERPRETATION")
            confidence = item.get("confidence")
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
                raise MemoryValidationError("interpretation confidence must be numeric in [0, 1]")
            if not str(item.get("basis", "")).strip():
                raise MemoryValidationError("every interpretation needs an explicit basis")
        clean = dict(payload)
        clean["model"] = {k: str(model[k]).strip() for k in ("provider", "name", "version")}
        clean["subject_key"] = "creator"
        clean["created_at"] = str(payload.get("created_at") or _now())
        clean["assessment_id"] = str(payload.get("assessment_id") or uuid.uuid4())
        clean["status"] = "ACTIVE"
        clean["review_status"] = "UNREVIEWED"
        clean["observations"] = observations
        clean["interpretations"] = interpretations
        clean["evidence_refs"] = [str(x) for x in evidence]
        clean["uncertainty"] = uncertainty
        clean["record_hash"] = _hash({k: v for k, v in clean.items() if k != "record_hash"})
        return clean

    def record_assessment(self, payload: dict[str, Any], *, consent: bool = False) -> dict[str, Any]:
        record = self._validate_assessment(payload, consent)
        state = self._read("memory")
        if any(x["assessment_id"] == record["assessment_id"] for x in state["assessments"]):
            raise MemoryValidationError("assessment_id already exists")
        state["assessments"].append(record)
        self._write("memory", state)
        self._audit("ASSESSMENT_RECORDED", record["assessment_id"], {"model": record["model"], "scope": record["scope"]})
        return record

    def list_assessments(self, *, model: str | None = None, status: str = "ACTIVE") -> list[dict[str, Any]]:
        records = self._read("memory").get("assessments", [])
        return [
            item for item in records
            if item.get("status") == status and (model is None or item.get("model", {}).get("name") == model)
        ]

    def review_assessment(self, assessment_id: str, *, status: str, reviewer_note: str = "") -> dict[str, Any]:
        if status not in ("ACCEPTED", "DISPUTED", "NEEDS_REVISION"):
            raise MemoryValidationError("review status must be ACCEPTED, DISPUTED or NEEDS_REVISION")
        state = self._read("memory")
        record = next((x for x in state["assessments"] if x["assessment_id"] == assessment_id), None)
        if record is None or record.get("status") != "ACTIVE":
            raise MemoryValidationError("active assessment not found")
        record["review_status"] = status
        record["reviewer_note"] = reviewer_note
        record["reviewed_at"] = _now()
        record["record_hash"] = _hash({k: v for k, v in record.items() if k != "record_hash"})
        self._write("memory", state)
        self._audit("ASSESSMENT_REVIEWED", assessment_id, {"review_status": status})
        return record

    def delete_assessment(self, assessment_id: str) -> bool:
        state = self._read("memory")
        before = len(state.get("assessments", []))
        state["assessments"] = [x for x in state.get("assessments", []) if x["assessment_id"] != assessment_id]
        if len(state["assessments"]) == before:
            return False
        self._write("memory", state)
        self._audit("ASSESSMENT_DELETED", assessment_id, {"content_removed": True})
        return True

    def add_session(self, *, model: dict[str, str], source_ref: str, scope: str) -> dict[str, Any]:
        if not all(str(model.get(k, "")).strip() for k in ("provider", "name", "version")):
            raise MemoryValidationError("session model provenance is incomplete")
        if not source_ref.strip() or not scope.strip():
            raise MemoryValidationError("source_ref and scope are required")
        item = {"session_id": str(uuid.uuid4()), "model": model, "source_ref": source_ref, "scope": scope, "created_at": _now()}
        state = self._read("sessions")
        state["items"].append(item)
        self._write("sessions", state)
        self._audit("SESSION_ADDED", item["session_id"], {"model": model})
        return item

    def compare_models(self) -> dict[str, Any]:
        active = self.list_assessments()
        by_model: dict[str, list[dict[str, Any]]] = {}
        for item in active:
            name = item["model"]["name"]
            by_model.setdefault(name, []).append(item)
        scopes: dict[str, list[dict[str, Any]]] = {}
        for item in active:
            scopes.setdefault(item["scope"], []).append(item)
        comparisons = []
        for scope, group in scopes.items():
            model_names = sorted({x["model"]["name"] for x in group})
            if len(model_names) < 2:
                continue
            comparisons.append({
                "scope": scope,
                "models": model_names,
                "assessment_ids": [x["assessment_id"] for x in group],
                "review_statuses": {x["assessment_id"]: x["review_status"] for x in group},
                "comparison_status": "HUMAN_COMPARISON_REQUIRED",
                "note": "Different model perspectives are retained separately; semantic agreement is not inferred from similar wording.",
            })
        return {"model_count": len(by_model), "assessment_count": len(active), "comparisons": comparisons}

    def detect_emergence(self, *, min_providers: int = 2) -> list[dict[str, Any]]:
        """Find exact recurring pattern labels across providers; never infer semantic similarity."""
        if min_providers < 2:
            raise MemoryValidationError("min_providers must be at least 2")
        grouped: dict[tuple[str, str], dict[str, Any]] = {}
        for item in self.list_assessments():
            provider = item["model"]["provider"]
            for raw_pattern in item.get("patterns", []):
                pattern = " ".join(str(raw_pattern).casefold().split())
                if not pattern:
                    continue
                key = (item["scope"], pattern)
                entry = grouped.setdefault(key, {"scope": item["scope"], "pattern": pattern, "providers": set(), "assessment_ids": []})
                entry["providers"].add(provider)
                entry["assessment_ids"].append(item["assessment_id"])
        candidates = []
        state = self._read("emergence")
        existing = {(x.get("scope"), x.get("pattern"), tuple(sorted(x.get("assessment_ids", [])))) for x in state.get("items", [])}
        for entry in grouped.values():
            if len(entry["providers"]) < min_providers:
                continue
            providers = sorted(entry["providers"])
            assessment_ids = sorted(set(entry["assessment_ids"]))
            identity = (entry["scope"], entry["pattern"], tuple(assessment_ids))
            if identity in existing:
                continue
            candidate = {
                "candidate_id": str(uuid.uuid4()),
                "scope": entry["scope"],
                "pattern": entry["pattern"],
                "providers": providers,
                "assessment_ids": assessment_ids,
                "status": "REVIEW_REQUIRED",
                "method": "EXACT_LABEL_RECURRENCE",
                "interpretation": "Repeated exact labels only; this does not establish semantic agreement, model independence, or a stable personal trait.",
                "created_at": _now(),
            }
            state["items"].append(candidate)
            candidates.append(candidate)
        if candidates:
            self._write("emergence", state)
            self._audit("EMERGENCE_CANDIDATES_CREATED", candidates[0]["candidate_id"], {"count": len(candidates)})
        return candidates

    def verify_audit_chain(self) -> dict[str, Any]:
        path = self.root / "audit.jsonl"
        previous = ""
        count = 0
        if not path.exists():
            return {"valid": True, "events": 0}
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                event = json.loads(line)
                supplied = event.pop("event_hash", None)
                if event.get("previous_hash") != previous or supplied != _hash(event):
                    return {"valid": False, "events": count, "failed_line": line_number}
                previous = supplied
                count += 1
        return {"valid": True, "events": count, "head": previous}

    def snapshot(self) -> dict[str, Any]:
        return {
            "manifest": self._read("manifest"),
            "governance": self.governance(),
            "assessment_count": len(self.list_assessments()),
            "comparison": self.compare_models(),
            "audit": self.verify_audit_chain(),
            "storage_path": str(self.root.resolve()),
        }


def default_store() -> MotherMemory:
    return MotherMemory()
