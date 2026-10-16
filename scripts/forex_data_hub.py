"""Resilient pull-based FX data hub for BESAZ.

Priority: OANDA pricing (requires account ID + token), Twelve Data, Alpha Vantage,
then Yahoo Finance chart endpoint as a best-effort public fallback. Availability,
entitlements, latency, and redistribution rights depend on each provider/account.
This is polling, not a guaranteed real-time streaming feed.
"""
from __future__ import annotations

import json
import math
import os
import sqlite3
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data/awareness/forex_data.db"
JSONL_PATH = ROOT / "data/awareness/forex_data.jsonl"
PAIR_MAP = {"EURUSD": "EUR_USD", "GBPUSD": "GBP_USD", "USDJPY": "USD_JPY",
            "AUDUSD": "AUD_USD", "USDCAD": "USD_CAD", "USDCHF": "USD_CHF",
            "NZDUSD": "NZD_USD"}


def _get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 12) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "BESAZ-Forex-Data-Hub/1.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP_{response.status}")
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Provider response is not a JSON object")
    return data


def _bar(source: str, symbol: str, timestamp: str, o: Any, h: Any, low: Any, close: Any,
         volume: Any = None, bid: Any = None, ask: Any = None) -> dict[str, Any]:
    values = [float(o), float(h), float(low), float(close)]
    if not all(math.isfinite(v) and v > 0 for v in values):
        raise ValueError("invalid OHLC values")
    if values[1] < max(values[0], values[2], values[3]) or values[2] > min(values[0], values[1], values[3]):
        raise ValueError("inconsistent OHLC range")
    return {"source": source, "symbol": symbol.upper(), "timestamp": timestamp,
            "open": values[0], "high": values[1], "low": values[2], "close": values[3],
            "volume": None if volume is None else float(volume),
            "bid": None if bid is None else float(bid), "ask": None if ask is None else float(ask),
            "received_at": datetime.now(timezone.utc).isoformat(), "evidence_scope": "PROVIDER_RESPONSE_NOT_INDEPENDENTLY_VERIFIED"}


def _fetch_oanda(pair: str) -> dict[str, Any]:
    token, account = os.getenv("OANDA_API_KEY"), os.getenv("OANDA_ACCOUNT_ID")
    if not token or not account:
        raise RuntimeError("OANDA_API_KEY and OANDA_ACCOUNT_ID are required")
    instrument = PAIR_MAP[pair]
    data = _get_json(f"https://api-fxpractice.oanda.com/v3/accounts/{urllib.parse.quote(account)}/pricing?instruments={instrument}",
                     {"Authorization": f"Bearer {token}"})
    prices = data.get("prices") or []
    if not prices:
        raise RuntimeError("OANDA returned no prices")
    p = prices[0]
    bids, asks = p.get("bids") or [], p.get("asks") or []
    bid = float(bids[0]["price"]) if bids else None
    ask = float(asks[0]["price"]) if asks else None
    mid = (bid + ask) / 2 if bid is not None and ask is not None else None
    if mid is None:
        raise RuntimeError("OANDA response missing bid/ask")
    return {"source": "oanda_practice", "symbol": pair, "timestamp": p.get("time"),
            "bid": bid, "ask": ask, "mid": mid, "received_at": datetime.now(timezone.utc).isoformat(),
            "evidence_scope": "BROKER_PRACTICE_PRICE_NOT_LIVE_EXECUTION"}


def _fetch_twelvedata(pair: str) -> dict[str, Any]:
    key = os.getenv("TWELVE_DATA_API_KEY")
    if not key:
        raise RuntimeError("TWELVE_DATA_API_KEY not configured")
    data = _get_json("https://api.twelvedata.com/time_series?" + urllib.parse.urlencode(
        {"symbol": pair[:3] + "/" + pair[3:], "interval": "1min", "outputsize": 1, "apikey": key}))
    if data.get("status") == "error" or not data.get("values"):
        raise RuntimeError("Twelve Data: " + str(data.get("message", "no values")))
    v = data["values"][0]
    return _bar("twelve_data", pair, str(v["datetime"]), v["open"], v["high"], v["low"], v["close"], v.get("volume"))


def _fetch_alpha(pair: str) -> dict[str, Any]:
    key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not key:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY not configured")
    params = {"function": "FX_INTRADAY", "from_symbol": pair[:3], "to_symbol": pair[3:],
              "interval": "1min", "outputsize": "compact", "apikey": key}
    data = _get_json("https://www.alphavantage.co/query?" + urllib.parse.urlencode(params))
    series_key = "Time Series FX (1min)"
    if series_key not in data:
        raise RuntimeError("Alpha Vantage response lacks intraday series: " + str(data.get("Note") or data.get("Information") or data.get("Error Message") or "unknown response"))
    stamp, v = max(data[series_key].items())
    return _bar("alpha_vantage", pair, stamp, v["1. open"], v["2. high"], v["3. low"], v["4. close"])


def _fetch_yahoo(pair: str) -> dict[str, Any]:
    ticker = pair + "=X"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1m"
    data = _get_json(url)
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        raise RuntimeError("Yahoo chart returned no result")
    r = result[0]
    timestamps, quotes = r.get("timestamp") or [], (r.get("indicators") or {}).get("quote") or []
    if not timestamps or not quotes:
        raise RuntimeError("Yahoo chart missing timestamps or quotes")
    q = quotes[0]
    idx = next((i for i in range(len(timestamps)-1, -1, -1) if all(q.get(k) and q[k][i] is not None for k in ("open", "high", "low", "close"))), None)
    if idx is None:
        raise RuntimeError("Yahoo chart has no complete OHLC bar")
    stamp = datetime.fromtimestamp(timestamps[idx], timezone.utc).isoformat()
    return _bar("yahoo_chart_best_effort", pair, stamp, q["open"][idx], q["high"][idx], q["low"][idx], q["close"][idx],
                q.get("volume", [None] * len(timestamps))[idx])


PROVIDERS = [("oanda_practice", _fetch_oanda), ("twelve_data", _fetch_twelvedata),
             ("alpha_vantage", _fetch_alpha), ("yahoo_chart_best_effort", _fetch_yahoo)]


def fetch_latest(pair: str = "EURUSD") -> dict[str, Any]:
    pair = pair.upper().replace("/", "")
    if pair not in PAIR_MAP:
        raise ValueError(f"Unsupported pair {pair}; supported: {', '.join(PAIR_MAP)}")
    failures = []
    for name, provider in PROVIDERS:
        try:
            result = provider(pair)
            result["fallback_failures"] = failures
            return result
        except Exception as exc:
            failures.append({"provider": name, "error": f"{type(exc).__name__}: {str(exc)[:240]}"})
    raise RuntimeError("All FX providers failed: " + json.dumps(failures, ensure_ascii=False))


def persist_tick(tick: dict[str, Any]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(tick, sort_keys=True, ensure_ascii=False, allow_nan=False)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS fx_ticks (
            source TEXT NOT NULL, symbol TEXT NOT NULL, timestamp TEXT NOT NULL,
            received_at TEXT NOT NULL, payload TEXT NOT NULL,
            PRIMARY KEY(source, symbol, timestamp))""")
        conn.execute("INSERT OR REPLACE INTO fx_ticks VALUES (?, ?, ?, ?, ?)",
                     (tick["source"], tick["symbol"], tick["timestamp"], tick["received_at"], encoded))
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        f.write(encoded + "\n")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--once", action="store_true", help="Fetch one sample and exit")
    args = parser.parse_args()
    if args.interval_seconds < 15:
        parser.error("interval-seconds must be >= 15 to avoid aggressive polling")
    while True:
        try:
            tick = fetch_latest(args.symbol)
            persist_tick(tick)
            print(json.dumps({"status": "DATA_RECEIVED", "tick": tick}, ensure_ascii=False, allow_nan=False))
        except Exception as exc:
            print(json.dumps({"status": "DATA_UNAVAILABLE", "error": str(exc), "time": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False))
            if args.once:
                raise
        if args.once:
            break
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
