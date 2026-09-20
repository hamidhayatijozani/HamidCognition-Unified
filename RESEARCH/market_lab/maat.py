from __future__ import annotations
from dataclasses import dataclass, asdict
from statistics import median
from typing import Iterable
import hashlib, json, math

@dataclass(frozen=True)
class PriceObservation:
    source_id: str
    symbol: str
    price: float
    timestamp: str
    source_kind: str = "external_snapshot"
    provenance: str = ""

    def canonical(self) -> dict:
        return asdict(self)

@dataclass(frozen=True)
class ConsensusResult:
    symbol: str
    price: float | None
    status: str
    source_count: int
    dispersion: float | None
    accepted_sources: tuple[str, ...]
    rejected_sources: tuple[str, ...]
    evidence_hash: str

class MaatOracle:
    """Deterministic multi-source consensus for research snapshots.

    A transformed or poetic representation is not treated as authentication.
    Authenticity requires provenance or cryptographic evidence at the source boundary.
    """
    def __init__(self, max_relative_dispersion: float = 0.005, min_sources: int = 2):
        if max_relative_dispersion <= 0 or min_sources < 1:
            raise ValueError("invalid consensus configuration")
        self.max_relative_dispersion = max_relative_dispersion
        self.min_sources = min_sources
        self._observations: list[PriceObservation] = []

    def submit(self, observation: PriceObservation) -> None:
        if not observation.source_id or not observation.symbol:
            raise ValueError("source_id and symbol are required")
        if not math.isfinite(observation.price) or observation.price <= 0:
            raise ValueError("price must be a finite positive number")
        self._observations.append(observation)

    @staticmethod
    def _fingerprint(observations: Iterable[PriceObservation]) -> str:
        payload = [o.canonical() for o in sorted(observations, key=lambda x: (x.source_id, x.timestamp))]
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def consensus(self, symbol: str) -> ConsensusResult:
        obs = [o for o in self._observations if o.symbol == symbol]
        if not obs:
            return ConsensusResult(symbol, None, "INSUFFICIENT_DATA", 0, None, (), (), self._fingerprint(obs))
        latest: dict[str, PriceObservation] = {}
        for item in obs:
            if item.source_id not in latest or item.timestamp > latest[item.source_id].timestamp:
                latest[item.source_id] = item
        values = list(latest.values())
        if len(values) < self.min_sources:
            return ConsensusResult(symbol, None, "INSUFFICIENT_SOURCES", len(values), None, (), tuple(sorted(latest)), self._fingerprint(values))
        center = median([x.price for x in values])
        relative = {x.source_id: abs(x.price - center) / center for x in values}
        accepted = tuple(sorted(k for k, v in relative.items() if v <= self.max_relative_dispersion))
        rejected = tuple(sorted(k for k, v in relative.items() if v > self.max_relative_dispersion))
        dispersion = max(relative.values()) if relative else 0.0
        if len(accepted) < self.min_sources:
            return ConsensusResult(symbol, None, "DISAGREEMENT", len(values), dispersion, accepted, rejected, self._fingerprint(values))
        return ConsensusResult(symbol, median([latest[k].price for k in accepted]), "CONSENSUS", len(values), dispersion, accepted, rejected, self._fingerprint(values))
