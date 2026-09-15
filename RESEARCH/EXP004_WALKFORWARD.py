import hashlib, json, platform, random, statistics, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'RESEARCH' / 'EXP004RESULT.json'
SYMBOL = 'EURUSD=X'
INTERVAL = '5m'
YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(SYMBOL, safe='')
HORIZONS_MIN = (5, 10, 20)
LOOKBACK_BARS = 20
FRICTION = 0.0002
MIN_OBS = 500
BOOTSTRAP_RESAMPLES = 1000
PERMUTATION_RESAMPLES = 1000
SOURCE_REPO = 'https://github.com/hamidhayatijozani/hamidcognition-realtime/blob/main/models/predictor.py'
AUDITED_SOURCE_SHA = 'df584043edb5fa5a2037adbc72f1bf90568ac9da'


def sha(b): return hashlib.sha256(b).hexdigest()


def fetch(period1, period2):
    params = urllib.parse.urlencode({'period1': int(period1), 'period2': int(period2), 'interval': INTERVAL, 'includePrePost': 'false', 'events': 'div,splits,capitalGains'})
    url = YAHOO + '?' + params
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 HamidCognition-EXP004/2.3'})
    with urllib.request.urlopen(req, timeout=30) as r: return url, r.read()


def parse(raw):
    payload = json.loads(raw.decode('utf-8'))
    chart = payload.get('chart', {})
    if chart.get('error'): raise RuntimeError(str(chart['error']))
    result = (chart.get('result') or [None])[0]
    if not result: raise RuntimeError('Yahoo returned no chart result')
    ts = result.get('timestamp', [])
    closes = ((result.get('indicators', {}).get('quote') or [{}])[0]).get('close', [])
    return sorted({int(t): float(c) for t, c in zip(ts, closes) if c is not None}.items())


def slope(xs):
    n = len(xs); mx = (n - 1) / 2.0; my = sum(xs) / n
    den = sum((i - mx) ** 2 for i in range(n))
    return sum((i - mx) * (y - my) for i, y in enumerate(xs)) / den


def predictor_direction(window, minute, current):
    predicted = current + slope(window) * minute  # cognitive_bias = 0
    if abs(predicted - current) < current * 0.0001: return 0
    return 1 if predicted > current else -1


def majority_direction(prices):
    dirs = [1 if prices[i] > prices[i-1] else -1 for i in range(1, len(prices))]
    return 1 if sum(dirs) >= 0 else -1


def persistence_direction(prices): return 1 if prices[-1] > prices[-2] else -1


def bootstrap_ci(values, seed=20260915, n=BOOTSTRAP_RESAMPLES):
    rng = random.Random(seed); m = len(values)
    means = [sum(rng.choices(values, k=m)) / m for _ in range(n)]
    means.sort()
    return [means[int(0.025 * (n - 1))], means[int(0.975 * (n - 1))]]


def permutation_pvalue(values, seed=20260915, n=PERMUTATION_RESAMPLES):
    rng = random.Random(seed); observed = abs(sum(values) / len(values)); extreme = 0
    for _ in range(n):
        total = sum(v if rng.getrandbits(1) else -v for v in values)
        if abs(total / len(values)) >= observed - 1e-15: extreme += 1
    return (extreme + 1) / (n + 1)


def evaluate(rows):
    prices = [c for _, c in rows]; timestamps = [t for t, _ in rows]; result = {}
    for minute in HORIZONS_MIN:
        horizon = minute // 5; model_correct, base_correct, pers_correct = [], [], []; cost_return = 0.0
        for i in range(LOOKBACK_BARS, len(prices) - horizon):
            current = prices[i]; actual_move = prices[i+horizon] - current
            if actual_move == 0: continue
            actual = 1 if actual_move > 0 else -1
            pred = predictor_direction(prices[i-LOOKBACK_BARS:i], minute, current)
            base = majority_direction(prices[:i]); pers = persistence_direction(prices[:i])
            model_correct.append(1 if pred == actual else 0); base_correct.append(1 if base == actual else 0); pers_correct.append(1 if pers == actual else 0)
            if pred == 1: cost_return += actual_move - FRICTION
            elif pred == -1: cost_return += -actual_move - FRICTION
        if not model_correct: raise RuntimeError(f'no evaluation folds for +{minute}m')
        deltas = [m - b for m, b in zip(model_correct, base_correct)]
        result[str(minute)] = {
            'n': len(model_correct), 'model_accuracy': sum(model_correct) / len(model_correct),
            'majority_baseline_accuracy': sum(base_correct) / len(base_correct), 'persistence_baseline_accuracy': sum(pers_correct) / len(pers_correct),
            'accuracy_delta_vs_majority': sum(deltas) / len(deltas),
            'accuracy_delta_bootstrap_95ci': bootstrap_ci(deltas) if minute == 5 else None,
            'paired_sign_flip_p_value': permutation_pvalue(deltas) if minute == 5 else None,
            'cost_aware_return': cost_return,
            'integrity': {'chronological': all(timestamps[i] < timestamps[i+1] for i in range(len(timestamps)-1)), 'future_features_used': False, 'test_tuning': False},
        }
    return result


def main():
    now = int(time.time())
    windows = [('snapshot_A', now - 27*86400, now - 2*86400), ('snapshot_B', now - 55*86400, now - 30*86400)]
    snapshots = {}
    for label, p1, p2 in windows:
        url, raw = fetch(p1, p2); rows = parse(raw)
        if len(rows) < MIN_OBS: raise SystemExit(f'{label}: insufficient real Yahoo 5m observations: {len(rows)}')
        snapshots[label] = {'source_url': url, 'raw_sha256': sha(raw), 'raw_bytes': len(raw), 'observations': len(rows),
                            'first_timestamp_utc': datetime.fromtimestamp(rows[0][0], timezone.utc).isoformat(),
                            'last_timestamp_utc': datetime.fromtimestamp(rows[-1][0], timezone.utc).isoformat(), 'metrics': evaluate(rows)}
    primary = [snapshots[x]['metrics']['5'] for x in snapshots]
    deltas = [x['accuracy_delta_vs_majority'] for x in primary]; costs = [x['cost_aware_return'] for x in primary]
    survives = all(x['integrity']['chronological'] and not x['integrity']['future_features_used'] and not x['integrity']['test_tuning'] and x['accuracy_delta_vs_majority'] > 0 and x['cost_aware_return'] > 0 for x in primary)
    result = {
        'experiment': 'EXP-004', 'status': 'EXECUTED_REAL_EXTERNAL_WALK_FORWARD', 'source_provider': 'Yahoo Finance', 'source_symbol': SYMBOL, 'source_interval': INTERVAL,
        'source_repo': SOURCE_REPO, 'audited_source_sha': AUDITED_SOURCE_SHA, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
        'predictor_mapping': {'implementation': 'hamidcognition-realtime/models/predictor.py', 'direction_path': 'ForexPredictor.predict_future -> 20-bar LinearRegression slope', 'window_size_bars': LOOKBACK_BARS, 'cognitive_bias': 0.0, 'horizons_minutes': list(HORIZONS_MIN)},
        'protocol': {'walk_forward': 'expanding chronological origin; no future rows enter features', 'primary_metric': 'directional accuracy at +5 minutes', 'primary_baseline': 'majority direction from training prefix', 'secondary_baseline': 'previous-direction persistence', 'friction_round_trip': FRICTION, 'independent_snapshots': 2, 'permutation_resamples': PERMUTATION_RESAMPLES, 'bootstrap_resamples': BOOTSTRAP_RESAMPLES},
        'snapshots': snapshots,
        'primary_summary': {'snapshot_deltas_vs_majority': deltas, 'mean_delta_vs_majority': statistics.mean(deltas), 'min_delta_vs_majority': min(deltas), 'cost_aware_returns': costs, 'all_snapshots_positive': survives},
        'integrity': {'chronological': True, 'future_features_used': False, 'test_tuning': False, 'snapshot_fingerprints_present': True, 'snapshots_disjoint': True},
        'interpretation': 'SURVIVES_PRELIMINARY' if survives else 'FAILS_PRIMARY_GATE',
        'promotion': 'BLOCKED_PENDING_INDEPENDENT_REPRODUCTION' if survives else 'CLAIM_FALSIFIED_UNDER_PREREGISTERED_GATE',
        'scientific_scope': 'Real 5-minute EUR/USD data are used because the audited predictor produces +5/+10/+20 minute forecasts. This evaluates predictive direction only and does not establish live execution quality.',
        'python_version': platform.python_version(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8'); print(json.dumps(result, indent=2, sort_keys=True)); return 0


if __name__ == '__main__': raise SystemExit(main())
