"""Fetch real EUR/USD observations for BESAZ evidence; never synthesize or silently downgrade data scope.

Modes:
- live: Twelve Data 5-minute observations only; requires TWELVEDATA_API_KEY.
- historical: Stooq daily observations only; explicitly not live or intraday.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

FIELDS = ["timestamp", "symbol", "open", "high", "low", "close", "volume", "provider", "data_scope"]
DEFAULT_OUTPUT = Path("data/awareness/forex_data.csv")
DEFAULT_EVIDENCE = Path("data/awareness/forex-data-evidence.json")


class FeedError(RuntimeError):
    """Raised when a provider response cannot be treated as valid evidence."""


def _get_text(url: str, timeout: int = 15) -> str:
    request = Request(url, headers={"User-Agent": "BESAZ-EvidenceHub/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise FeedError(f"provider returned HTTP {response.status}")
            return response.read().decode("utf-8")
    except FeedError:
        raise
    except Exception as exc:
        raise FeedError(f"provider request failed: {type(exc).__name__}: {exc}") from exc


def _number(value: object, field: str) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise FeedError(f"invalid numeric field: {field}") from exc
    if number != number or number in (float("inf"), float("-inf")):
        raise FeedError(f"non-finite numeric field: {field}")
    return format(number, ".10g")


def _validate_ohlc(row: dict, timestamp: str, provider: str, scope: str) -> dict:
    if not timestamp:
        raise FeedError("missing timestamp")
    values = {key: _number(row.get(key), key) for key in ("open", "high", "low", "close")}
    o, h, l, c = (float(values[k]) for k in ("open", "high", "low", "close"))
    if min(o, h, l, c) <= 0 or h < max(o, c, l) or l > min(o, c, h):
        raise FeedError("invalid OHLC relationship")
    volume_raw = row.get("volume", "")
    volume = "" if volume_raw in (None, "", "null") else _number(volume_raw, "volume")
    return {
        "timestamp": timestamp, "symbol": "EUR/USD", **values, "volume": volume,
        "provider": provider, "data_scope": scope,
    }


def fetch_live(api_key: str, outputsize: int = 30) -> list[dict]:
    if not api_key.strip():
        raise FeedError("TWELVEDATA_API_KEY is required for live mode")
    query = urlencode({
        "symbol": "EUR/USD", "interval": "5min", "outputsize": str(outputsize),
        "format": "JSON", "apikey": api_key.strip(),
    })
    payload = json.loads(_get_text(f"https://api.twelvedata.com/time_series?{query}"))
    if not isinstance(payload, dict) or "values" not in payload:
        message = payload.get("message", "unexpected provider response") if isinstance(payload, dict) else "invalid JSON shape"
        raise FeedError(f"Twelve Data did not return observations: {message}")
    values = payload["values"]
    if not isinstance(values, list) or not values:
        raise FeedError("Twelve Data returned no observations")
    rows = []
    for item in values:
        if not isinstance(item, dict):
            raise FeedError("invalid observation shape")
        rows.append(_validate_ohlc(item, str(item.get("datetime", "")), "twelvedata", "LIVE_5M"))
    return sorted(rows, key=lambda x: x["timestamp"])


def fetch_historical() -> list[dict]:
    # Stooq's daily bars are historical context, never a substitute for a live feed.
    text = _get_text("https://stooq.com/q/d/l/?s=eurusd&i=d")
    reader = csv.DictReader(text.splitlines())
    required = {"Date", "Open", "High", "Low", "Close"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise FeedError("Stooq response is missing expected daily OHLC columns")
    rows = []
    for item in reader:
        rows.append(_validate_ohlc({
            "open": item.get("Open"), "high": item.get("High"), "low": item.get("Low"),
            "close": item.get("Close"), "volume": item.get("Volume", ""),
        }, str(item.get("Date", "")), "stooq", "HISTORICAL_DAILY"))
    if not rows:
        raise FeedError("Stooq returned no historical observations")
    return rows


def write_evidence(rows: list[dict], output: Path, evidence_path: Path, mode: str) -> dict:
    if not rows:
        raise FeedError("refusing to write empty evidence")
    expected_scope = "LIVE_5M" if mode == "live" else "HISTORICAL_DAILY"
    if any(row.get("data_scope") != expected_scope for row in rows):
        raise FeedError("mixed or unexpected data scope; refusing to write")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "project": "BESAZ", "symbol": "EUR/USD", "mode": mode,
        "data_scope": expected_scope, "provider": rows[0]["provider"],
        "observation_count": len(rows), "first_timestamp": rows[0]["timestamp"],
        "last_timestamp": rows[-1]["timestamp"],
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "synthetic_fallback": False,
        "claim_boundary": "Data retrieval only; no predictive edge or trading performance is implied.",
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("live", "historical"), required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--outputsize", type=int, default=30)
    args = parser.parse_args(argv)
    if not 1 <= args.outputsize <= 5000:
        parser.error("--outputsize must be between 1 and 5000")
    try:
        if args.mode == "live":
            rows = fetch_live(os.environ.get("TWELVEDATA_API_KEY", ""), args.outputsize)
        else:
            rows = fetch_historical()
        metadata = write_evidence(rows, args.output, args.evidence, args.mode)
    except (FeedError, json.JSONDecodeError, OSError) as exc:
        print(f"FEED_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
