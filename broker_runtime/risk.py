from __future__ import annotations

from decimal import Decimal

from .models import MarketOrder


class BrokerPolicy:
    """Deterministic pre-execution limits. Live mode is never implied."""

    def __init__(
        self,
        *,
        allowed_instruments: frozenset[str] = frozenset({"EUR_USD"}),
        max_units: Decimal = Decimal("1000"),
    ) -> None:
        self.allowed_instruments = allowed_instruments
        self.max_units = max_units

    def as_authorization_policy(self) -> dict[str, object]:
        """Canonical policy material bound into Gate-issued broker authority."""
        return {
            "allowed_instruments": sorted(self.allowed_instruments),
            "max_units": str(self.max_units),
        }

    def validate(self, order: MarketOrder) -> None:
        if order.instrument not in self.allowed_instruments:
            raise ValueError("instrument_not_allowed")
        if abs(order.units) > self.max_units:
            raise ValueError("max_units_exceeded")
