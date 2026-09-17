from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping


OBSERVATION_BOUNDARY_VERSION = "OB-0.1"
REQUIRED_FIELDS = (
    "timestamp",
    "symbol",
    "bid",
    "ask",
    "tick_id",
    "broker_timestamp",
    "local_timestamp",
    "connection_status",
)
ALLOWED_CONNECTION_STATES = {"CONNECTED", "DEGRADED", "DISCONNECTED"}


@dataclass(frozen=True)
class ObservationBoundaryResult:
    permitted: bool
    decision: str
    reasons: tuple[str, ...]
    observation_hash: str | None
    boundary_version: str = OBSERVATION_BOUNDARY_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "permitted": self.permitted,
            "decision": self.decision,
            "reasons": list(self.reasons),
            "observation_hash": self.observation_hash,
            "boundary_version": self.boundary_version,
        }


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def canonicalize_observation(observation: Mapping[str, Any]) -> bytes:
    """Canonical bytes for hashing; caller must validate before trust."""
    return json.dumps(
        dict(observation),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def observation_hash(observation: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonicalize_observation(observation)).hexdigest()


def validate_observation(
    observation: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_age_seconds: float = 5.0,
    seen_tick_ids: set[str] | None = None,
    previous_sequence: int | None = None,
) -> ObservationBoundaryResult:
    reasons: list[str] = []
    if not isinstance(observation, Mapping):
        return ObservationBoundaryResult(False, "DENY", ("observation_not_mapping",), None)

    missing = [field for field in REQUIRED_FIELDS if field not in observation]
    if missing:
        reasons.append("missing_required_fields:" + ",".join(missing))

    timestamp = _parse_timestamp(observation.get("timestamp"))
    broker_timestamp = _parse_timestamp(observation.get("broker_timestamp"))
    local_timestamp = _parse_timestamp(observation.get("local_timestamp"))
    current = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)

    if timestamp is None:
        reasons.append("invalid_timestamp")
    if broker_timestamp is None:
        reasons.append("invalid_broker_timestamp")
    if local_timestamp is None:
        reasons.append("invalid_local_timestamp")

    if timestamp is not None:
        age = (current - timestamp).total_seconds()
        if age > max_age_seconds:
            reasons.append("stale_observation")
        if age < 0:
            reasons.append("future_observation")

    connection = observation.get("connection_status")
    if connection not in ALLOWED_CONNECTION_STATES:
        reasons.append("invalid_connection_status")
    elif connection != "CONNECTED":
        reasons.append("connection_not_connected")

    symbol = observation.get("symbol")
    if not isinstance(symbol, str) or not symbol.strip():
        reasons.append("invalid_symbol")

    tick_id = observation.get("tick_id")
    if not isinstance(tick_id, str) or not tick_id.strip():
        reasons.append("invalid_tick_id")
    elif seen_tick_ids is not None and tick_id in seen_tick_ids:
        reasons.append("duplicate_tick_id")

    sequence = observation.get("sequence")
    if sequence is not None:
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            reasons.append("invalid_sequence")
        elif previous_sequence is not None and sequence != previous_sequence + 1:
            reasons.append("sequence_gap")

    try:
        bid = float(observation.get("bid"))
        ask = float(observation.get("ask"))
        if bid <= 0 or ask <= 0:
            reasons.append("non_positive_price")
        elif ask < bid:
            reasons.append("negative_spread")
    except (TypeError, ValueError):
        reasons.append("invalid_price")

    if reasons:
        decision = "SAFE_MODE" if any(
            reason in reasons
            for reason in ("stale_observation", "future_observation", "connection_not_connected", "duplicate_tick_id", "sequence_gap")
        ) else "DENY"
        return ObservationBoundaryResult(False, decision, tuple(reasons), None)

    return ObservationBoundaryResult(True, "ALLOW", tuple(), observation_hash(observation))
