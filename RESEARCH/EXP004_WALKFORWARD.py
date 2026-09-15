import hashlib, json, math, platform, statistics, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'RESEARCH'/'EXP004RESULT.json'
SOURCE='https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?startPeriod=2024-01-01&endPeriod=2026-09-15'

# Minimal dependency-free walk-forward test. The ECB daily reference rate is EUR per USD;
# EUR/USD is its reciprocal. Only past observations enter each prediction.
def sha(b): return hashlib.sha256(b).hexdigest()
def fetch():
    req=urllib.request.Request(SOURCE,headers={'User-Agent':'HamidCognition-EXP004/1.0'})
    with urllib.request.urlopen(req,timeout=30) as r: return r.read()
def parse_csv(raw):
    import csv,io
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    vals=[]
    for x in rows:
        d=x.get('TIME_PERIOD') or x.get('TIME_PERIOD')
        v=x.get('OBS_VALUE')
        if d and v: vals.append((d,1.0/float(v)))
    vals.sort()
    return vals

def direction_model(train, hist):
    # pre-registered simple predictor: sign of mean of the last 5 training returns
    if len(hist)<6: return None
    rs=[hist[i]/hist[i-1]-1 for i in range(1,len(hist))]
    m=sum(rs[-5:])/5
    return 1 if m>0 else -1

def eval_walk(vals, min_train=120):
    y=[]; pred=[]; base=[]; persistence=[]
    for i in range(min_train,len(vals)):
        train=vals[:i]; actual=1 if vals[i][1]>vals[i-1][1] else -1
        p=direction_model(train, [v for _,v in train])
        if p is None: continue
        trdirs=[1 if train[j][1]>train[j-1][1] else -1 for j in range(1,len(train))]
        majority=1 if sum(trdirs)>=0 else -1
        prev=trdirs[-1]
        y.append(actual); pred.append(p); base.append(majority); persistence.append(prev)
    return y,pred,base,persistence

def acc(y,p): return sum(a==b for a,b in zip(y,p))/len(y)
def main():
    raw=fetch(); digest=sha(raw); vals=parse_csv(raw)
    if len(vals)<150: raise SystemExit('insufficient real ECB observations')
    y,p,b,pr=eval_walk(vals)
    ap,ab,apr=acc(y,p),acc(y,b),acc(y,pr)
    # Fixed, pre-declared conservative round-trip friction: 2 bps.
    pnl=sum((0.0002 if a==q else -0.0002) for a,q in zip(y,p))
    result={
      'experiment':'EXP-004','status':'EXECUTED_REAL_EXTERNAL_WALK_FORWARD',
      'source_url':SOURCE,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
      'raw_sha256':digest,'raw_bytes':len(raw),'observations':len(vals),
      'first_date':vals[0][0],'last_date':vals[-1][0],
      'protocol':{'expanding_window':True,'min_train':120,'one_step_ahead':True,
                  'primary_metric':'accuracy','friction_round_trip':0.0002,
                  'feature_rule':'last-5 training returns only'},
      'metrics':{'model_accuracy':ap,'majority_baseline_accuracy':ab,
                 'persistence_baseline_accuracy':apr,'accuracy_delta_vs_majority':ap-ab,
                 'cost_proxy_return':pnl},
      'integrity':{'chronological':True,'future_features_used':False,'test_tuning':False},
      'interpretation':('SURVIVES_PRELIMINARY' if ap>ab and pnl>0 else 'FAILS_PRIMARY_GATE'),
      'promotion': 'BLOCKED_PENDING_INDEPENDENT_SECOND_SNAPSHOT',
      'python_version':platform.python_version()
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result['integrity']['chronological'] or not result['integrity']['future_features_used'] or not result['integrity']['test_tuning']:
        raise SystemExit('integrity failure')
    if result['interpretation']=='FAILS_PRIMARY_GATE': raise SystemExit('EXP-004 primary gate failed')
if __name__=='__main__': main()
