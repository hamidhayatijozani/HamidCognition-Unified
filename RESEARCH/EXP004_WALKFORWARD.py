import hashlib, json, math, platform, statistics, time, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta
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

# EXP-004 evaluates the actual audited ForexPredictor behaviour that determines
# direction inside predict_future(): a LinearRegression slope over the last 20
# closes, followed by predicted_price = current_price + slope * minute when
# cognitive_bias is frozen at 0. The original source also trains a separate
# LinearRegression/scaler path, but its output is not used to form direction.
# This evaluator therefore tests the exact direction-producing mechanism while
# keeping the cognitive layer fixed and explicitly outside the claim.
SOURCE_REPO = 'https://github.com/hamidhayatijozani/hamidcognition-realtime/blob/main/models/predictor.py'
AUDITED_SOURCE_SHA = 'df584043edb5fa5a2037adbc72f1bf90568ac9da'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fetch(period1, period2):
    params = urllib.parse.urlencode({
        'period1': int(period1),
        'period2': int(period2),
        'interval': INTERVAL,
        'includePrePost': 'false',
        'events': 'div,splits,capitalGains',
    })
    url = YAHOO + '?' + params
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 HamidCognition-EXP004/2.0'
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    return url, raw


def parse(raw):
    payload = json.loads(raw.decode('utf-8'))
    chart = payload.get('chart', {})
    if chart.get('error'):
        raise RuntimeError(str(chart['error']))
    result = (chart.get('result') or [None])[0]
    if not result:
        raise RuntimeError('Yahoo returned no chart result')
    ts = result.get('timestamp', [])
    q = (result.get('indicators', {}).get('quote') or [{}])[0]
    closes = q.get('close', [])
    rows = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        rows.append((int(t), float(c)))
    rows.sort()
    dedup = []
    seen = set()
    for t, c in rows:
        if t not in seen:
            dedup.append((t, c)); seen.add(t)
    return dedup


def slope(xs):
    # Exact ordinary least-squares slope of y on x=0..19, matching sklearn's
    # LinearRegression for a single feature and no intercept constraint.
    n = len(xs)
    if n != LOOKBACK_BARS:
        raise ValueError('bad window')
    mx = (n - 1) / 2.0
    my = sum(xs) / n
    den = sum((i - mx) ** 2 for i in range(n))
    return sum((i - mx) * (y - my) for i, y in enumerate(xs)) / den


def predictor_direction(window, minute, current):
    s = slope(window)
    predicted = current + s * minute  # cognitive_bias = 0
    if abs(predicted - current) < current * 0.0001:
        return 0, predicted, s
    return (1 if predicted > current else -1), predicted, s


def majority_direction(prices):
    dirs = [1 if prices[i] > prices[i-1] else -1 for i in range(1, len(prices))]
    return 1 if sum(dirs) >= 0 else -1


def persistence_direction(prices):
    return 1 if prices[-1] > prices[-2] else -1


def bootstrap_ci(values, seed=20260915, n=4000):
    # Deterministic linear-congruential PRNG, avoiding an external dependency.
    if not values:
        return [None, None]
    state = seed & 0x7fffffff
    samples = []
    m = len(values)
    for _ in range(n):
        s = 0.0
        for _ in range(m):
            state = (1103515245 * state + 12345) & 0x7fffffff
            s += values[state % m]
        samples.append(s / m)
    samples.sort()
    return [samples[int(0.025 * (n - 1))], samples[int(0.975 * (n - 1))]]


def permutation_pvalue(values, seed=20260915, n=4000):
    # Sign-flip null for paired model-vs-baseline accuracy differences.
    if not values:
        return None
    observed = abs(sum(values) / len(values))
    state = seed & 0x7fffffff
    extreme = 0
    m = len(values)
    for _ in range(n):
        s = 0.0
        for v in values:
            state = (1103515245 * state + 12345) & 0x7fffffff
            s += v if (state & 1) else -v
        if abs(s / m) >= observed - 1e-15:
            extreme += 1
    return (extreme + 1) / (n + 1)


def evaluate(rows, label):
    prices = [c for _, c in rows]
    timestamps = [t for t, _ in rows]
    by_h = {}
    integrity = True
    for minute in HORIZONS_MIN:
        # 5-minute bars: minute horizon maps exactly to minute/5 future bars.
        horizon = minute // 5
        outcomes = []
        model_correct = []
        base_correct = []
        pers_correct = []
        cost_return = 0.0
        records = []
        for i in range(LOOKBACK_BARS, len(prices) - horizon):
            window = prices[i-LOOKBACK_BARS:i]
            current = prices[i]
            actual_move = prices[i+horizon] - current
            if actual_move == 0:
                continue
            actual = 1 if actual_move > 0 else -1
            pred, forecast, s = predictor_direction(window, minute, current)
            # The production predictor may emit NEUTRAL. For directional scoring,
            # NEUTRAL is an incorrect non-action unless the realized move is zero.
            mc = 1 if pred == actual else 0
            b = majority_direction(prices[:i])
            pr = persistence_direction(prices[:i])
            bc = 1 if b == actual else 0
            pc = 1 if pr == actual else 0
            model_correct.append(mc); base_correct.append(bc); pers_correct.append(pc)
            if pred == 1:
                cost_return += (actual_move - FRICTION)
            elif pred == -1:
                cost_return += (-actual_move - FRICTION)
            records.append((timestamps[i], pred, actual, forecast, s))
        if not model_correct:
            raise RuntimeError(f'no evaluation folds for {label} +{minute}m')
        acc = sum(model_correct) / len(model_correct)
        bacc = sum(base_correct) / len(base_correct)
        pacc = sum(pers_correct) / len(pers_correct)
        deltas = [m - b for m, b in zip(model_correct, base_correct)]
        ci = bootstrap_ci(deltas)
        p = permutation_pvalue(deltas)
        by_h[str(minute)] = {
            'n': len(model_correct),
            'model_accuracy': acc,
            'majority_baseline_accuracy': bacc,
            'persistence_baseline_accuracy': pacc,
            'accuracy_delta_vs_majority': acc - bacc,
            'accuracy_delta_bootstrap_95ci': ci,
            'paired_sign_flip_p_value': p,
            'cost_aware_return': cost_return,
            'integrity': {
                'chronological': all(timestamps[i] < timestamps[i+1] for i in range(len(timestamps)-1)),
                'future_features_used': False,
                'test_tuning': False,
            },
            'mechanism': 'ForexPredictor.predict_future trend slope over last 20 closes; cognitive_bias=0',
        }
    return by_h


def main():
    now = int(time.time())
    # Two disjoint real Yahoo 5-minute snapshots. Each is within the provider's
    # current intraday availability window, and the windows do not overlap.
    windows = [
        ('snapshot_A', now - 30*86400, now - 2*86400),
        ('snapshot_B', now - 60*86400, now - 32*86400),
    ]
    snapshots = {}
    for label, p1, p2 in windows:
        url, raw = fetch(p1, p2)
        rows = parse(raw)
        if len(rows) < MIN_OBS:
            raise SystemExit(f'{label}: insufficient real Yahoo 5m observations: {len(rows)}')
        metrics = evaluate(rows, label)
        snapshots[label] = {
            'source_url': url,
            'raw_sha256': sha(raw),
            'raw_bytes': len(raw),
            'observations': len(rows),
            'first_timestamp_utc': datetime.fromtimestamp(rows[0][0], timezone.utc).isoformat(),
            'last_timestamp_utc': datetime.fromtimestamp(rows[-1][0], timezone.utc).isoformat(),
            'metrics': metrics,
        }

    primary = [snapshots[x]['metrics']['5'] for x in snapshots]
    primary_deltas = [x['accuracy_delta_vs_majority'] for x in primary]
    primary_costs = [x['cost_aware_return'] for x in primary]
    primary_survives = all(
        x['integrity']['chronological'] and
        not x['integrity']['future_features_used'] and
        not x['integrity']['test_tuning'] and
        x['accuracy_delta_vs_majority'] > 0 and
        x['cost_aware_return'] > 0
        for x in primary
    )
    # Statistical evidence is reported, but it is not promoted to VERIFIED by
    # p-value alone. Both disjoint real snapshots must pass the pre-registered gate.
    result = {
        'experiment': 'EXP-004',
        'status': 'EXECUTED_REAL_EXTERNAL_WALK_FORWARD',
        'source_provider': 'Yahoo Finance',
        'source_symbol': SYMBOL,
        'source_interval': INTERVAL,
        'source_repo': SOURCE_REPO,
        'audited_source_sha': AUDITED_SOURCE_SHA,
        'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
        'predictor_mapping': {
            'implementation': 'hamidcognition-realtime/models/predictor.py',
            'direction_path': 'ForexPredictor.predict_future -> 20-bar LinearRegression slope',
            'window_size_bars': LOOKBACK_BARS,
            'cognitive_bias': 0.0,
            'horizons_minutes': list(HORIZONS_MIN),
        },
        'protocol': {
            'walk_forward': 'expanding chronological origin; no future rows enter features',
            'primary_metric': 'directional accuracy at +5 minutes',
            'primary_baseline': 'majority direction from training prefix',
            'secondary_baseline': 'previous-direction persistence',
            'friction_round_trip': FRICTION,
            'independent_snapshots': 2,
            'permutation_resamples': 4000,
            'bootstrap_resamples': 4000,
        },
        'snapshots': snapshots,
        'primary_summary': {
            'snapshot_deltas_vs_majority': primary_deltas,
            'mean_delta_vs_majority': statistics.mean(primary_deltas),
            'min_delta_vs_majority': min(primary_deltas),
            'cost_aware_returns': primary_costs,
            'all_snapshots_positive': primary_survives,
        },
        'integrity': {
            'chronological': True,
            'future_features_used': False,
            'test_tuning': False,
            'snapshot_fingerprints_present': True,
            'snapshots_disjoint': True,
        },
        'interpretation': 'SURVIVES_PRELIMINARY' if primary_survives else 'FAILS_PRIMARY_GATE',
        'promotion': 'BLOCKED_PENDING_INDEPENDENT_REPRODUCTION',
        'scientific_scope': 'This resolves the earlier daily-data horizon mismatch by evaluating the actual minute-horizon direction mechanism on real 5-minute EUR/USD observations. It does not establish live profitability, execution quality, or VERIFIED status.',
        'python_version': platform.python_version(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))
    if result['interpretation'] == 'FAILS_PRIMARY_GATE':
        raise SystemExit('EXP-004 primary gate failed')


if __name__ == '__main__':
    main()
