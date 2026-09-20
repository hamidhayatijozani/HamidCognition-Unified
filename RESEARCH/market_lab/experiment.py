from __future__ import annotations
import hashlib, json
from dataclasses import asdict
from .maat import MaatOracle, PriceObservation
from .thoth import ThothEngine
from .paper_trader import PaperTrader

def fingerprint(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def run_snapshot_experiment(observations: list[PriceObservation], symbol: str = "EURUSD") -> dict:
    oracle = MaatOracle()
    for item in observations:
        oracle.submit(item)
    consensus = oracle.consensus(symbol)
    prices = [o.price for o in sorted(observations, key=lambda x: x.timestamp) if o.symbol == symbol]
    thoth = ThothEngine().analyze(symbol, prices)
    trader = PaperTrader()
    trading = trader.run(symbol, prices, [thoth.signal] * len(prices)) if prices else {"trade_count": 0}
    payload = {"observations": [asdict(o) for o in observations], "consensus": asdict(consensus), "signal": asdict(thoth), "paper_trading": trading}
    return {"experiment": "MAAT-THOTH-PAPER-001", "status": "RESEARCH_ONLY", "fingerprint": fingerprint(payload), "result": payload, "claims_not_verified": ["live_market_predictive_skill", "profitability", "external_provider_integrity", "live_trading_safety"]}
