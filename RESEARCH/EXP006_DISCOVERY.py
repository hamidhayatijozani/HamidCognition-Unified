import hashlib
import json
import math
import statistics
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "RESEARCH" / "EXP006_RESULT.json"
SYMBOL = "EURUSD=X"
INTERVAL = "5m"
FRICTION = 0.00020
HORIZON = 6
MIN_BARS = 1200
LOOKBACK = 96


def fetch(period1, period2):
    q = urllib.parse.urlencode({
        "period1": int(period1), "period2": int(period2),
        "interval": INTERVAL, "includePrePost": "false",
        "events": "div,splits,capitalGains",
    })
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(SYMBOL, safe="") + "?" + q
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 HamidCognition-EXP006/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return url, r.read()


def parse(raw):
    p = json.loads(raw.decode())
    if p.get("chart", {}).get("error"):
        raise RuntimeError(str(p["chart"]["error"]))
    result = (p.get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError("Yahoo returned no chart result")
    ts = result.get("timestamp", [])
    closes = ((result.get("indicators", {}).get("quote") or [{}])[0]).get("close", [])
    return sorted((int(t), float(c)) for t, c in zip(ts, closes) if c is not None and math.isfinite(float(c)) and float(c) > 0)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stdev(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def returns(prices):
    return [(prices[i] / prices[i-1]) - 1.0 for i in range(1, len(prices))]


def rolling_mean(xs, n):
    return mean(xs[-n:])


def rolling_vol(xs, n):
    return stdev(xs[-n:])


def signal_pst(prices, i):
    # Original hypothesis: Pressure is abnormal short-term displacement,
    # Connection is agreement across short/medium/long momentum,
    # Tenacity is directional persistence. Trade only when all three align.
    r = returns(prices[:i+1])
    if len(r) < LOOKBACK:
        return 0
    rv = r[-48:]
    vol = rolling_vol(r, 48)
    if vol <= 1e-12:
        return 0
    pressure = abs(sum(rv[-6:])) / (vol * math.sqrt(6))
    m1 = prices[i] / prices[i-6] - 1.0
    m2 = prices[i] / prices[i-24] - 1.0
    m3 = prices[i] / prices[i-72] - 1.0
    connection = sum(1 for x in (m1, m2, m3) if x > 0) - sum(1 for x in (m1, m2, m3) if x < 0)
    recent = [1 if x > 0 else -1 if x < 0 else 0 for x in r[-12:]]
    tenacity = abs(sum(recent)) / 12.0
    if pressure < 1.25 or abs(connection) < 3 or tenacity < 0.50:
        return 0
    direction = 1 if connection > 0 else -1
    return direction


def signal_compression_break(prices, i):
    # Volatility-compression release: a quiet regime followed by a directional break.
    if i < 120:
        return 0
    r = returns(prices[:i+1])
    short_vol = rolling_vol(r, 12)
    base_vol = rolling_vol(r, 96)
    if base_vol <= 1e-12 or short_vol >= base_vol * 0.72:
        return 0
    recent = prices[i-12:i+1]
    hi, lo = max(recent[:-1]), min(recent[:-1])
    if prices[i] > hi:
        return 1
    if prices[i] < lo:
        return -1
    return 0


def signal_shock_reclaim(prices, i):
    # Reversal hypothesis: unusually large move followed by a one-bar reclaim.
    if i < 48:
        return 0
    r = returns(prices[:i+1])
    vol = rolling_vol(r, 48)
    last = r[-1]
    if vol <= 1e-12 or abs(last) < 2.2 * vol:
        return 0
    if last < 0 and prices[i] > prices[i-1] * (1 + 0.10 * vol):
        return 1
    if last > 0 and prices[i] < prices[i-1] * (1 - 0.10 * vol):
        return -1
    return 0


def signal_fast_slow_flip(prices, i):
    # Regime transition: fast momentum crosses the sign of slow momentum.
    if i < 96:
        return 0
    fast = prices[i] / prices[i-6] - 1.0
    slow = prices[i] / prices[i-48] - 1.0
    prev_fast = prices[i-1] / prices[i-7] - 1.0
    prev_slow = prices[i-1] / prices[i-49] - 1.0
    if prev_fast <= prev_slow and fast > slow and fast > 0:
        return 1
    if prev_fast >= prev_slow and fast < slow and fast < 0:
        return -1
    return 0


def baseline_momentum(prices, i):
    if i < 48:
        return 0
    m = prices[i] / prices[i-24] - 1.0
    return 1 if m > 0 else -1 if m < 0 else 0


STRATEGIES = {
    "PST_PRESSURE_CONNECTION_TENACITY": signal_pst,
    "VOL_COMPRESSION_BREAK": signal_compression_break,
    "SHOCK_RECLAIM": signal_shock_reclaim,
    "FAST_SLOW_REGIME_FLIP": signal_fast_slow_flip,
    "BASELINE_24BAR_MOMENTUM": baseline_momentum,
}


def evaluate(prices):
    out = {}
    for name, fn in STRATEGIES.items():
        trades = []
        for i in range(max(LOOKBACK, 120), len(prices) - HORIZON):
            s = fn(prices, i)
            if not s:
                continue
            gross = s * (prices[i + HORIZON] / prices[i] - 1.0)
            net = gross - FRICTION
            trades.append(net)
        equity = 1.0
        peak = 1.0
        max_dd = 0.0
        for x in trades:
            equity *= 1.0 + x
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak - equity) / peak)
        wins = sum(x > 0 for x in trades)
        gains = sum(x for x in trades if x > 0)
        losses = -sum(x for x in trades if x < 0)
        out[name] = {
            "trades": len(trades),
            "win_rate": wins / len(trades) if trades else 0.0,
            "mean_net_return": mean(trades),
            "median_net_return": statistics.median(trades) if trades else 0.0,
            "compound_equity": equity,
            "max_drawdown": max_dd,
            "profit_factor": gains / losses if losses > 0 else (float("inf") if gains > 0 else 0.0),
            "positive_after_friction": bool(trades) and mean(trades) > 0,
        }
    return out


def main():
    now = int(time.time())
    # Two disjoint real-data windows. Parameters are frozen before retrieval.
    windows = {
        "recent": (now - 28 * 86400, now - 2 * 86400),
        "older": (now - 58 * 86400, now - 32 * 86400),
    }
    snapshots = {}
    for label, (p1, p2) in windows.items():
        url, raw = fetch(p1, p2)
        rows = parse(raw)
        if len(rows) < MIN_BARS:
            raise RuntimeError(f"{label}: insufficient observations: {len(rows)}")
        prices = [x[1] for x in rows]
        snapshots[label] = {
            "source_url": url,
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "observations": len(rows),
            "first_timestamp_utc": datetime.fromtimestamp(rows[0][0], timezone.utc).isoformat(),
            "last_timestamp_utc": datetime.fromtimestamp(rows[-1][0], timezone.utc).isoformat(),
            "metrics": evaluate(prices),
        }

    robust = {}
    for name in STRATEGIES:
        a = snapshots["recent"]["metrics"][name]
        b = snapshots["older"]["metrics"][name]
        robust[name] = {
            "both_windows_positive": a["mean_net_return"] > 0 and b["mean_net_return"] > 0,
            "recent_mean": a["mean_net_return"],
            "older_mean": b["mean_net_return"],
            "mean_across_windows": mean([a["mean_net_return"], b["mean_net_return"]]),
            "recent_equity": a["compound_equity"],
            "older_equity": b["compound_equity"],
        }

    ranked = sorted(robust.items(), key=lambda kv: kv[1]["mean_across_windows"], reverse=True)
    result = {
        "experiment": "EXP-006",
        "status": "EXECUTED_REAL_EXTERNAL_DISCOVERY",
        "hypothesis": "Novel regime-aware signals can outperform a simple fixed momentum baseline without parameter tuning on the evaluation windows.",
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "horizon_bars": HORIZON,
        "friction_per_round_trip": FRICTION,
        "strategies": list(STRATEGIES),
        "windows": snapshots,
        "robust_comparison": robust,
        "ranking": [{"strategy": k, **v} for k, v in ranked],
        "promotion_rule": "A candidate is interesting only if both disjoint windows are positive after friction and it beats the baseline on mean net return across both windows. This is a discovery filter, not proof of future profitability.",
        "data_integrity": {"future_features_used": False, "parameter_tuning_on_evaluation": False, "windows_disjoint": True},
        "scientific_scope": "Real Yahoo Finance EUR/USD 5-minute observations. Results are exploratory and require independent reproduction on unseen periods and preferably independent feeds.",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
