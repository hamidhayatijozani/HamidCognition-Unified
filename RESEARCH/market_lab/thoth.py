from __future__ import annotations
from dataclasses import dataclass
from statistics import mean
import math

@dataclass(frozen=True)
class ThothSignal:
    symbol: str
    signal: str
    confidence: float
    momentum: float
    volatility: float
    observation_count: int
    reason: str

class ThothEngine:
    """Deterministic bounded-window research signal engine, not a predictor."""
    def __init__(self, window: int = 20, momentum_threshold: float = 0.001):
        if window < 3 or momentum_threshold <= 0:
            raise ValueError("invalid Thoth configuration")
        self.window = window
        self.momentum_threshold = momentum_threshold

    def analyze(self, symbol: str, prices: list[float]) -> ThothSignal:
        clean = [float(x) for x in prices if math.isfinite(float(x)) and float(x) > 0][-self.window:]
        if len(clean) < 3:
            return ThothSignal(symbol, "HOLD", 0.0, 0.0, 0.0, len(clean), "insufficient_history")
        momentum = (clean[-1] / clean[0]) - 1.0
        returns = [(b / a) - 1.0 for a, b in zip(clean, clean[1:]) if a > 0]
        volatility = math.sqrt(mean([r * r for r in returns])) if returns else 0.0
        signal = "HOLD" if abs(momentum) < self.momentum_threshold else ("LONG" if momentum > 0 else "SHORT")
        confidence = min(1.0, abs(momentum) / max(self.momentum_threshold * 4.0, 1e-12))
        return ThothSignal(symbol, signal, confidence, momentum, volatility, len(clean), "window_momentum")
