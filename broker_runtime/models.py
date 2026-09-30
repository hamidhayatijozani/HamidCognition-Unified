from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class BrokerEnvironment(str, Enum):
    PRACTICE = "practice"
    LIVE = "live"


class BrokerExecutionState(str, Enum):
    BLOCKED = "BLOCKED"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MarketOrder:
    operation_id: str
    instrument: str
    units: Decimal
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.operation_id.strip():
            raise ValueError("operation_id is required")
        if not self.instrument.strip():
            raise ValueError("instrument is required")
        if self.units == 0:
            raise ValueError("units must be non-zero")


@dataclass(frozen=True)
class BrokerResult:
    state: BrokerExecutionState
    broker_order_id: str | None
    broker_trade_id: str | None
    request_id: str | None
    raw: dict
    reason: str | None = None

    @property
    def requires_reconciliation(self) -> bool:
        """UNKNOWN means the remote side effect may have happened."""
        return self.state is BrokerExecutionState.UNKNOWN
