import hashlib, json
from pathlib import Path

ROOT = Path(__file__).parent
VECTOR = json.loads((ROOT / 'inputs/vector-001.json').read_text())

SOURCE_SHA = {
    'V-A': '1c71fd77b7bf3cde5665a7eb413d3a55aac0e402',
    'V-B': '3cf67fec9a95198a1045dab98ee0ce6016d90e54',
    'V-C': '226c748173c98017d65446735c0fe87f09506073',
    'V-D': '589ab1e0e0330d0efaff088ef67bb79a8e86f04d',
}


def energy(p, s, t, cap=None):
    value = (p * s) / (1.1 - t + 1e-9) * (1 - t / (p + s + 1e-9))
    if cap is not None:
        value = min(max(value, 0), cap)
    return value


def run_a(v):
    p, s, t = (v['initial_state'][k] for k in ('P', 'S', 'T'))
    out = []
    for x in v['steps']:
        p = min(max(p + .05*x['pressure']*(1-t), .1), .95)
        s = min(max(s + .04*x['novelty']*(1-abs(p-s)), .1), .95)
        t = min(max(t + .03*(s/(p+1e-9))*(1+x['pressure']), .1), .8)
        phase = 'RUPTURE_IMMINENT' if abs(p-s)<.15 else 'UNSTABLE_CREATIVITY' if t<.45 else 'SYNTHESIS_PEAK' if p>.85 and s>.8 else 'STEADY_EXPLORATION'
        out.append({'P':round(p,4),'S':round(s,4),'T':round(t,4),'energy':round(energy(p,s,t,1.5),4),'phase':phase})
    return out


def run_b(v):
    p, s, t = (v['initial_state'][k] for k in ('P', 'S', 'T'))
    out = []
    for x in v['steps']:
        volatility = x['pressure']/1.5
        momentum = x['novelty']/2.0
        pressure = min(1.0, volatility*1.5)
        novelty = min(1.0, abs(momentum)*2.0)
        p = min(max(p + .05*pressure*(1-t), .1), .95)
        s = min(max(s + .04*novelty*(1-abs(p-s)), .1), .95)
        t = min(max(t + .03*(s/(p+1e-9))*(1+pressure), .1), .85)
        phase = 'RUPTURE_IMMINENT' if abs(p-s)<.12 else 'UNSTABLE_CREATIVITY' if t<.40 else 'SYNTHESIS_PEAK' if p>.80 and s>.75 else 'STEADY_EXPLORATION'
        out.append({'P':round(p,3),'S':round(s,3),'T':round(t,3),'energy':round(min(energy(p,s,t),2),3),'phase':phase})
    return out


def run_c(v):
    p, s, t = (v['initial_state'][k] for k in ('P', 'S', 'T'))
    out = []
    for x in v['steps']:
        p += .05*x['pressure']*(1-t)
        s += .04*x['novelty']*(1-abs(p-s))
        t += .03*(s/(p+1e-9))*(1+x['pressure'])
        p=min(max(p,0),1); s=min(max(s,0),1); t=min(max(t,0),1)
        phase='rupture_imminent' if abs(p-s)<.1 else 'unstable_creativity' if t<.45 else 'synthesis_peak' if p>.85 and s>.8 else 'steady_exploration'
        out.append({'P':round(p,4),'S':round(s,4),'T':round(t,4),'energy':round(energy(p,s,t),4),'phase':phase})
    return out


def run_d(v):
    p, s, t = (v['initial_state'][k] for k in ('P', 'S', 'T'))
    freedom = v['mapping']['variant_d_freedom']
    out = []
    for x in v['steps']:
        p=max(0,p*x['pressure']); s=max(0,s*x['novelty']); t=min(1,max(0,t/freedom))
        hp, hs, ht = p>1.5, s>1.5, t>.3
        if hp and hs and not ht: phase='Synthesis'
        elif hp and not hs and ht: phase='Stabilization'
        elif not hp and hs and not ht: phase='Rupture/Exploration'
        elif not hp and not hs and ht: phase='Stagnation/Review'
        elif hp and hs and ht: phase='Overload/Rigid Synthesis'
        elif not hp and not hs and not ht: phase='Dormancy/Reset'
        else: phase='Transition'
        out.append({'P':p,'S':s,'T':t,'energy':energy(p,s,t),'phase':phase})
    return out


def fingerprint(value):
    payload=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(payload).hexdigest()


def distance(a,b):
    return max((sum((x[k]-y[k])**2 for k in ('P','S','T'))**0.5) for x,y in zip(a,b))


def execute():
    results={'V-A':run_a(VECTOR),'V-B':run_b(VECTOR),'V-C':run_c(VECTOR),'V-D':run_d(VECTOR)}
    fingerprints={k:fingerprint(v) for k,v in results.items()}
    pairs={}
    names=list(results)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            pairs[f'{a} vs {b}']={'max_state_euclidean_divergence':round(distance(results[a],results[b]),8),'exact_state_match':results[a]==results[b]}
    return {'experiment_id':'EXP-001','vector_id':VECTOR['vector_id'],'vector_sha256':fingerprint(VECTOR),'source_sha':SOURCE_SHA,'fingerprints':fingerprints,'pairwise':pairs,'results':results}


if __name__ == '__main__':
    print(json.dumps(execute(), indent=2, ensure_ascii=False))
