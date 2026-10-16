"""Fetch and evaluate public historical OHLCV data without claiming predictive edge.

Stooq's public CSV endpoint is used as a no-key research data source. This is
historical daily data, not a broker execution feed or proof of live tradability.
"""
from __future__ import annotations

import csv
import io
import json
import math
import sqlite3
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

USER_AGENT = "BESAZ-Operational-Evidence/1.0 (research; contact repository owner)"


def parse_ohlcv_csv(text: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if start > end:
        raise ValueError("start_date must be on or before end_date")
    reader = csv.DictReader(io.StringIO(text))
    required = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise ValueError("CSV is missing required OHLCV columns")
    rows = []
    for raw in reader:
        try:
            day = date.fromisoformat(raw["Date"])
            values = {k.lower(): float(raw[k]) for k in ("Open", "High", "Low", "Close", "Volume")}
        except (TypeError, ValueError, KeyError) as exc:
            raise ValueError("Invalid OHLCV row") from exc
        if not all(math.isfinite(v) for v in values.values()):
            raise ValueError("Non-finite OHLCV value")
        if min(values["open"], values["high"], values["low"], values["close"]) <= 0 or values["volume"] < 0:
            raise ValueError("OHLCV values outside valid range")
        if values["high"] < max(values["open"], values["low"], values["close"]):
            raise ValueError("High is inconsistent with OHLC")
        if values["low"] > min(values["open"], values["high"], values["close"]):
            raise ValueError("Low is inconsistent with OHLC")
        if start <= day <= end:
            rows.append({"date": day.isoformat(), **values})
    rows.sort(key=lambda x: x["date"])
    if len({r["date"] for r in rows}) != len(rows):
        raise ValueError("Duplicate daily bars detected")
    if len(rows) < 2:
        raise ValueError("At least two in-range daily bars are required")
    return rows


def fetch_stooq_daily(symbol: str, start_date: str, end_date: str, timeout: int = 20) -> list[dict[str, Any]]:
    if not symbol or not all(c.isalnum() or c in ".-_" for c in symbol):
        raise ValueError("Invalid symbol")
    # Stooq US equities convention: AAPL -> aapl.us. Explicit suffixes are preserved.
    upper_symbol = symbol.upper()\n    fx_symbols = {"EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"}\n    normalized = symbol.lower() if "." in symbol or upper_symbol in fx_symbols else f"{symbol.lower()}.us"
    url = f"https://stooq.com/q/d/l/?s={normalized}&i=d"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"Market data provider returned HTTP {status}")
        payload = response.read().decode("utf-8-sig")
    if not payload.strip() or "No data" in payload:
        raise RuntimeError("Market data provider returned no usable data")
    return parse_ohlcv_csv(payload, start_date, end_date)


def calculate_buy_hold_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) < 2:
        raise ValueError("At least two bars are required")
    closes = [float(row["close"]) for row in rows]
    if any(not math.isfinite(x) or x <= 0 for x in closes):
        raise ValueError("Close prices must be finite and positive")
    returns = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    for ret in returns:
        equity *= 1 + ret
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, (peak - equity) / peak)
    gains = sum(x for x in returns if x > 0)
    losses = -sum(x for x in returns if x < 0)
    return {
        "benchmark": "BUY_AND_HOLD_CLOSE_TO_CLOSE",
        "bars": len(rows),
        "first_date": rows[0]["date"],
        "last_date": rows[-1]["date"],
        "first_close": closes[0],
        "last_close": closes[-1],
        "total_return": closes[-1] / closes[0] - 1,
        "max_drawdown": max_drawdown,
        "profit_factor_daily_returns": gains / losses if losses > 0 else None,
        "positive_day_fraction": sum(x > 0 for x in returns) / len(returns),
        "predictive_edge": "NOT_TESTED",
        "live_execution": "NOT_TESTED",
        "limitations": [
            "historical daily bars only",
            "buy-and-hold benchmark, not a predictive strategy",
            "no fees, slippage, dividends, or execution simulation",
            "historical results do not establish future performance",
        ],
    }


def persist_evidence(record: dict[str, Any], jsonl_path: Path, db_path: Path) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False, allow_nan=False)
    with jsonl_path.open("a", encoding="utf-8") as stream:
        stream.write(encoded + "\n")
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                experiment_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                result TEXT NOT NULL,
                evidence_json TEXT NOT NULL
            )
        """)
        conn.execute(
            "INSERT OR REPLACE INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(record["run_id"]), str(record["timestamp"]),
                str(record["experiment_type"]), str(record["symbol"]),
                str(record["start_date"]), str(record["end_date"]),
                str(record["result"]), encoded,
            ),
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
