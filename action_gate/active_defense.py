"""Active-defense telemetry for Action Gate enforcement failures."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

SUSPICIOUS_CODES = frozenset({
    "invalid_signature", "malformed_authority", "nonce_reuse",
    "tenant_mismatch", "action_binding_mismatch", "policy_binding_mismatch",
})

@dataclass(frozen=True)
class SecuritySignal:
    event_type: str
    severity: str
    reason: str
    decision_id: str | None
    tenant_id: str | None
    nonce_fingerprint: str | None
    observed_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

def classify_enforcement_failure(
    *,
    error_code: str,
    decision_id: str | None = None,
    tenant_id: str | None = None,
    nonce_fingerprint: str | None = None,
    now: datetime | None = None,
) -> SecuritySignal | None:
    """Turn high-signal enforcement failures into structured telemetry."""
    if error_code not in SUSPICIOUS_CODES:
        return None
    observed = now or datetime.now(timezone.utc)
    return SecuritySignal(
        event_type="SECURITY_SIGNAL_ENFORCEMENT_ANOMALY",
        severity="HIGH" if error_code in {"invalid_signature", "nonce_reuse"} else "MEDIUM",
        reason=error_code,
        decision_id=decision_id,
        tenant_id=tenant_id,
        nonce_fingerprint=nonce_fingerprint,
        observed_at=observed.isoformat(),
    )
