import hashlib, json, math, statistics, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"RESEARCH"/"EXP007_RESULT.json"
SYMBOLS=["EURUSD=X","GBPUSD=X","AUDUSD=X","USDJPY=X"]
TARGET="EURUSD=X"
INTERVAL="5m"
HORIZON=12
LOOKBACK=12
FRICTION=0.00020
MIN_BARS=1200

def fetch(symbol,p1,p2):
    q=urllib.parse.urlencode({"period1":int(p1),"period2":int(p2),"interval":INTERVAL,"includePrePost":"false","events":"div,splits,capitalGains"})
    url="https://query1.finance.yahoo.com/v8/finance/chart/"+urllib.parse.quote(symbol,safe="")+"?"+q
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 HamidCognition-EXP007/1.0"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return url,r.read()

def parse(raw):
    p=json.loads(raw.decode())
    result=(p.get("chart",{}).get("result") or [None])[0]
    if not result: raise RuntimeError("no chart result")
    ts=result.get("timestamp",[])
    closes=((result.get("indicators",{}).get("quote") or [{}])[0]).get("close",[])
    return {int(t):float(c) for t,c in zip(ts,closes) if c is not None and math.isfinite(float(c)) and float(c)>0}

def eval_window(series):
    common=sorted(set.intersection(*(set(series[s]) for s in SYMBOLS)))
    prices={s:[series[s][t] for t in common] for s in SYMBOLS}
    trades=[]; baseline=[]
    for i in range(LOOKBACK,len(common)-HORIZON):
        target_m=prices[TARGET][i]/prices[TARGET][i-LOOKBACK]-1
        dirs=[]
        for s in SYMBOLS:
            m=prices[s][i]/prices[s][i-LOOKBACK]-1
            dirs.append(1 if m>0 else -1 if m<0 else 0)
        direction=1 if target_m>0 else -1 if target_m<0 else 0
        confirmations=sum(d==direction for d in dirs[1:])
        if direction and confirmations>=2:
            future=prices[TARGET][i+HORIZON]/prices[TARGET][i]-1
            trades.append(direction*future-FRICTION)
        if direction:
            future=prices[TARGET][i+HORIZON]/prices[TARGET][i]-1
            baseline.append(direction*future-FRICTION)
    def stats(xs):
        if not xs: return {"trades":0,"mean_net_return":0.0,"win_rate":0.0,"compound_equity":1.0,"max_drawdown":0.0}
        eq=peak=1.0;dd=0.0
        for x in xs:
            eq*=1+x;peak=max(peak,eq);dd=max(dd,(peak-eq)/peak)
        return {"trades":len(xs),"mean_net_return":sum(xs)/len(xs),"median_net_return":statistics.median(xs),"win_rate":sum(x>0 for x in xs)/len(xs),"compound_equity":eq,"max_drawdown":dd}
    a,b=stats(trades),stats(baseline)
    return {"common_timestamps":len(common),"cross_asset_consensus":a,"target_momentum_baseline":b,
            "delta_mean_net_return":a["mean_net_return"]-b["mean_net_return"]}

def main():
    now=int(time.time())
    windows={"recent":(now-28*86400,now-2*86400),"older":(now-58*86400,now-32*86400)}
    result_windows={}
    for label,(p1,p2) in windows.items():
        series={}; sources={}
        for s in SYMBOLS:
            url,raw=fetch(s,p1,p2); series[s]=parse(raw)
            sources[s]={"url":url,"raw_sha256":hashlib.sha256(raw).hexdigest(),"observations":len(series[s])}
        if any(v["observations"]<MIN_BARS for v in sources.values()):
            raise RuntimeError(f"{label}: insufficient observations")
        result_windows[label]={"sources":sources,"metrics":eval_window(series)}
    a=result_windows["recent"]["metrics"]["cross_asset_consensus"]
    b=result_windows["older"]["metrics"]["cross_asset_consensus"]
    ba=result_windows["recent"]["metrics"]["target_momentum_baseline"]
    bb=result_windows["older"]["metrics"]["target_momentum_baseline"]
    result={"experiment":"EXP-007","status":"EXECUTED_REAL_EXTERNAL_DISCOVERY",
      "hypothesis":"A target FX move becomes more selective and more useful when independent directional pressure from three related FX pairs confirms it; fixed cross-asset confirmation should reduce false signals without tuning on evaluation data.",
      "target":TARGET,"symbols":SYMBOLS,"interval":INTERVAL,"lookback_bars":LOOKBACK,"horizon_bars":HORIZON,"friction":FRICTION,
      "windows":result_windows,
      "decision":{"both_windows_positive":a["mean_net_return"]>0 and b["mean_net_return"]>0,
                  "beats_baseline_both_windows":a["mean_net_return"]>ba["mean_net_return"] and b["mean_net_return"]>bb["mean_net_return"],
                  "mean_delta":statistics.mean([result_windows["recent"]["metrics"]["delta_mean_net_return"],result_windows["older"]["metrics"]["delta_mean_net_return"]])},
      "integrity":{"future_features_used":False,"parameter_tuning_on_evaluation":False,"windows_disjoint":True,"cross_asset_confirmation_requires_two_of_three":True},
      "scope":"Exploratory real-market evidence only; positive execution does not establish future profitability.",
      "retrieved_at_utc":datetime.now(timezone.utc).isoformat()}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
