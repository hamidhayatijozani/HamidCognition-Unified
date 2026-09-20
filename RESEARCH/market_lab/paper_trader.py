from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class PaperTrade:
    index: int
    symbol: str
    signal: str
    price: float
    quantity: float
    fee: float
    cash_after: float
    position_after: float

class PaperTrader:
    """Deterministic long-only simulator with explicit fee and slippage costs."""
    def __init__(self, starting_cash: float = 1000.0, fee_rate: float = 0.001, slippage_bps: float = 2.0):
        if starting_cash <= 0 or fee_rate < 0 or slippage_bps < 0:
            raise ValueError("invalid paper trader configuration")
        self.starting_cash = float(starting_cash)
        self.cash = float(starting_cash)
        self.position = 0.0
        self.fee_rate = float(fee_rate)
        self.slippage_bps = float(slippage_bps)
        self.trades: list[PaperTrade] = []

    def step(self, index: int, symbol: str, signal: str, price: float) -> PaperTrade | None:
        if price <= 0:
            raise ValueError("price must be positive")
        if signal == "LONG" and self.position == 0:
            execution_price = price * (1 + self.slippage_bps / 10000)
            qty = self.cash / (execution_price * (1 + self.fee_rate))
            notional = qty * execution_price
            fee = notional * self.fee_rate
            self.cash -= notional + fee
            self.position = qty
        elif signal == "SHORT" and self.position > 0:
            execution_price = price * (1 - self.slippage_bps / 10000)
            notional = self.position * execution_price
            fee = notional * self.fee_rate
            self.cash += notional - fee
            self.position = 0.0
            qty = 0.0
        else:
            return None
        trade = PaperTrade(index, symbol, signal, execution_price, qty, fee, self.cash, self.position)
        self.trades.append(trade)
        return trade

    def mark_to_market(self, price: float) -> float:
        return self.cash + self.position * price

    def run(self, symbol: str, prices: list[float], signals: list[str]) -> dict:
        for i, (price, signal) in enumerate(zip(prices, signals)):
            self.step(i, symbol, signal, float(price))
        last_price = float(prices[-1]) if prices else 0.0
        return {"starting_cash": self.starting_cash, "ending_equity": self.mark_to_market(last_price), "trade_count": len(self.trades), "trades": [asdict(t) for t in self.trades]}
