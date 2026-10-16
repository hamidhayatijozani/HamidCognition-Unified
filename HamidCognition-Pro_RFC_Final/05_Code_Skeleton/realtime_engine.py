"""Provider-neutral market-data interface. No network connection is made here."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Tick:
    symbol: str
    timestamp: datetime
    bid: float
    ask: float


class RealTimeEngine:
    def __init__(self, provider):
        self.provider = provider

    def ingest(self) -> Tick:
        tick = self.provider.next_tick()
        if not isinstance(tick, Tick):
            raise TypeError("provider must return Tick")
        if tick.bid <= 0 or tick.ask < tick.bid:
            raise ValueError("invalid bid/ask")
        if tick.timestamp.tzinfo is None:
            raise ValueError("tick timestamp must be timezone-aware")
        return tick
