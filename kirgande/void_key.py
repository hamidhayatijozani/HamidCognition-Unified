"""Deterministic, dependency-free reference metrics for KIRGANDE RFC-0003.

This is an evaluation utility, not an authorization credential or a production
policy engine. Callers must enforce authorization independently.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Mapping


class MetricsError(ValueError):
    """Raised when a metric input is missing, non-finite, or out of range."""


def _unit(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MetricsError(f"{name} must be a number in [0, 1]")
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise MetricsError(f"{name} must be finite and in [0, 1]")
    return result


def calculate_hais(
    eas: float,
    ned: float,
    cps: float,
    cqm: float,
    ocr: float,
    *,
    chaos_normalized: float | None = None,
    chaos_weight: float = 0.0,
) -> float:
    """Calculate normalized HAIS candidate score.

    Baseline weights sum to 1.0. Chaos is reported separately by default;
    optional blending is allowed only with an explicit weight in [0, 1].
    This formula is not empirically validated.
    """
    values = {
        "eas": _unit("eas", eas),
        "ned": _unit("ned", ned),
        "cps": _unit("cps", cps),
        "cqm": _unit("cqm", cqm),
        "ocr": _unit("ocr", ocr),
    }
    baseline = (
        0.30 * values["eas"]
        + 0.20 * (1.0 - values["ned"])
        + 0.20 * values["cps"]
        + 0.15 * values["cqm"]
        + 0.15 * (1.0 - values["ocr"])
    )
    weight = _unit("chaos_weight", chaos_weight)
    if weight == 0.0:
        return baseline
    if chaos_normalized is None:
        raise MetricsError("chaos_normalized is required when chaos_weight > 0")
    chaos = _unit("chaos_normalized", chaos_normalized)
    return (1.0 - weight) * baseline + weight * chaos


def calculate_drs(
    impact: float,
    authorization_risk: float,
    replay_risk: float,
    uncertainty: float,
    *,
    chaos_normalized: float | None = None,
    chaos_weight: float = 0.0,
) -> float:
    """Calculate normalized DRS candidate score; higher means more risk.

    The four submitted weights are normalized by their sum (1.10).
    Component definitions and thresholds require separate validation.
    """
    vals = {
        "impact": _unit("impact", impact),
        "authorization_risk": _unit("authorization_risk", authorization_risk),
        "replay_risk": _unit("replay_risk", replay_risk),
        "uncertainty": _unit("uncertainty", uncertainty),
    }
    baseline = (
        0.30 * vals["impact"]
        + 0.25 * vals["authorization_risk"]
        + 0.25 * vals["replay_risk"]
        + 0.20 * vals["uncertainty"]
    ) / 1.10
    weight = _unit("chaos_weight", chaos_weight)
    if weight == 0.0:
        return baseline
    if chaos_normalized is None:
        raise MetricsError("chaos_normalized is required when chaos_weight > 0")
    chaos = _unit("chaos_normalized", chaos_normalized)
    return (1.0 - weight) * baseline + weight * chaos


def calculate_chaos(
    direct: float,
    inverse: float,
    entropy_normalized: float,
    confidence_product: float,
) -> float:
    """Return bounded candidate chaos score in [0, 1].

    All inputs are required to be normalized to [0, 1]. No non-zero floor or
    non-zero asymptotic limit is assumed.
    """
    direct_value = _unit("direct", direct)
    inverse_value = _unit("inverse", inverse)
    entropy = _unit("entropy_normalized", entropy_normalized)
    confidence = _unit("confidence_product", confidence_product)
    return abs(direct_value - inverse_value) * entropy * confidence


def canonical_sha256(payload: Any) -> str:
    """Hash JSON-compatible data using deterministic canonical JSON."""
    try:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MetricsError(f"payload is not canonical JSON data: {exc}") from exc
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ChaosSnapshot:
    schema_version: str
    algorithm_version: str
    window: str
    input_sha256: str
    direct: float
    inverse: float
    entropy_normalized: float
    confidence_product: float
    chaos_normalized: float
    missing_data: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return stable, JSON-compatible snapshot content."""
        return asdict(self)

    @property
    def snapshot_sha256(self) -> str:
        return canonical_sha256(self.to_dict())


def make_chaos_snapshot(
    *,
    window: str,
    input_artifacts: Mapping[str, Any],
    direct: float,
    inverse: float,
    entropy_normalized: float,
    confidence_product: float,
    schema_version: str = "1.0.0",
    algorithm_version: str = "1.0.0",
    missing_data: bool = False,
) -> ChaosSnapshot:
    """Build a provenance-bound snapshot from caller-supplied observable data."""
    if not isinstance(window, str) or not window.strip():
        raise MetricsError("window must be a non-empty string")
    if not isinstance(missing_data, bool):
        raise MetricsError("missing_data must be boolean")
    if missing_data:
        raise MetricsError("cannot compute a numeric snapshot with missing data")
    input_hash = canonical_sha256(input_artifacts)
    score = calculate_chaos(direct, inverse, entropy_normalized, confidence_product)
    return ChaosSnapshot(
        schema_version=schema_version,
        algorithm_version=algorithm_version,
        window=window,
        input_sha256=input_hash,
        direct=_unit("direct", direct),
        inverse=_unit("inverse", inverse),
        entropy_normalized=_unit("entropy_normalized", entropy_normalized),
        confidence_product=_unit("confidence_product", confidence_product),
        chaos_normalized=score,
        missing_data=False,
    )
