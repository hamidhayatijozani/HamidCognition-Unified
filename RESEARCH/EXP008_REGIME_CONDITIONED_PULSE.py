import hashlib,json,math,statistics,time,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"RESEARCH"/"EXP008_RESULT.json"
SYMBOLS=["EURUSD=X","GBPUSD=X","AUDUSD=X","USDJPY=X"]; TARGET="EURUSD=X"; INTERVAL="5m"
LOOKBACK=12; HORIZON=12; VOL_SHORT=24; VOL_LONG=288; FRICTION=.00020; MIN_BARS=1200

def fetch(s,p1,p2):
 q=urllib.parse.urlencode({"period1":int(p1),"period2":int(p2),"interval":INTERVAL,"includePrePost":"false","events":"div,splits,capitalGains"})
 u="https://query1.finance.yahoo.com/v8/finance/chart/"+urllib.parse.quote(s,safe="")+"?"+q
 req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 HamidCognition-EXP008/1.0"})
 with urllib.request.urlopen(req,timeout=30) as r:return u,r.read()
def parse(raw):
 p=json.loads(raw.decode()); z=(p.get("chart",{}).get("result") or [None])[0]
 if not z: raise RuntimeError("no chart result")
 ts=z.get("timestamp",[]); cs=((z.get("indicators",{}).get("quote") or [{}])[0]).get("close",[])
 return {int(t):float(c) for t,c in zip(ts,cs) if c is not None and math.isfinite(float(c)) and float(c)>0}
def vol(xs,n):
 r=[xs[i]/xs[i-1]-1 for i in range(1,len(xs))]
 return statistics.pstdev(r[-n:]) if len(r)>=n+1 else 0.0
def eval_window(series):
 common=sorted(set.intersection(*(set(series[s]) for s in SYMBOLS)))
 px={s:[series[s][t] for t in common] for s in SYMBOLS}; variants={"STORM":[], "QUIET":[]}
 for i in range(max(VOL_LONG,LOOKBACK),len(common)-HORIZON):
  d=[]
  for s in SYMBOLS:
   m=px[s][i]/px[s][i-LOOKBACK]-1; d.append(1 if m>0 else -1 if m<0 else 0)
  target=d[0]; confirm=sum(x==target for x in d[1:])
  if not target or confirm<2: continue
  sv=vol(px[TARGET][:i+1],VOL_SHORT); lv=vol(px[TARGET][:i+1],VOL_LONG)
  if lv<=0: continue
  ret=target*(px[TARGET][i+HORIZON]/px[TARGET][i]-1)-FRICTION
  variants["STORM" if sv>lv else "QUIET"].append(ret)
 def stats(xs):
  if not xs:return {"trades":0,"mean_net_return":0,"median_net_return":0,"win_rate":0,"compound_equity":1}
  eq=1
  for x in xs:eq*=1+x
  return {"trades":len(xs),"mean_net_return":sum(xs)/len(xs),"median_net_return":statistics.median(xs),"win_rate":sum(x>0 for x in xs)/len(xs),"compound_equity":eq}
 return {"common_timestamps":len(common),"variants":{k:stats(v) for k,v in variants.items()}}
def main():
 now=int(time.time()); windows={"recent":(now-28*86400,now-2*86400),"older":(now-58*86400,now-32*86400)}; out={}
 for label,(a,b) in windows.items():
  series={}; src={}
  for s in SYMBOLS:
   u,raw=fetch(s,a,b); series[s]=parse(raw); src[s]={"url":u,"sha256":hashlib.sha256(raw).hexdigest(),"observations":len(series[s])}
  if any(x["observations"]<MIN_BARS for x in src.values()):raise RuntimeError("insufficient data")
  out[label]={"sources":src,"metrics":eval_window(series)}
 variants={}
 for v in ["STORM","QUIET"]:
  r=out["recent"]["metrics"]["variants"][v]; o=out["older"]["metrics"]["variants"][v]
  variants[v]={"both_windows_positive":r["mean_net_return"]>0 and o["mean_net_return"]>0,"recent":r,"older":o,"mean_across_windows":(r["mean_net_return"]+o["mean_net_return"])/2}
 ranked=sorted(variants.items(),key=lambda x:x[1]["mean_across_windows"],reverse=True)
 result={"experiment":"EXP-008","status":"EXECUTED_REAL_EXTERNAL_DISCOVERY",
 "hypothesis":"Cross-asset confirmation may only become useful in a matching volatility regime; test both high-volatility (STORM) and low-volatility (QUIET) activation without selecting parameters from evaluation outcomes.",
 "target":TARGET,"symbols":SYMBOLS,"interval":INTERVAL,"lookback_bars":LOOKBACK,"horizon_bars":HORIZON,
 "volatility_regimes":{"short_bars":VOL_SHORT,"long_bars":VOL_LONG,"storm":"short_vol > long_vol","quiet":"short_vol <= long_vol"},"friction":FRICTION,
 "windows":out,"comparison":variants,"ranking":[{"variant":k,**v} for k,v in ranked],
 "integrity":{"future_features_used":False,"parameter_tuning_on_evaluation":False,"windows_disjoint":True,"regime_rule_fixed":True},
 "promotion_rule":"Only a variant positive after friction in both disjoint windows is promoted to an independent unseen-period retest. Otherwise falsify and move on.",
 "scope":"Exploratory real-market evidence only.","retrieved_at_utc":datetime.now(timezone.utc).isoformat()}
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8"); print(json.dumps(result,indent=2,sort_keys=True)); return 0
if __name__=="__main__":raise SystemExit(main())
