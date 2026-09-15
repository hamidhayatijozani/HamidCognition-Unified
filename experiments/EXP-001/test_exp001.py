import json
from runner import execute

R = execute()
assert len(R['results']) == 4
assert len(R['results']['V-A']) == 10
assert len(R['results']['V-B']) == 10
assert len(R['results']['V-C']) == 10
assert len(R['results']['V-D']) == 10
assert len(set(R['fingerprints'].values())) == 4
assert all(not x['exact_state_match'] for x in R['pairwise'].values())
print('EXP-001 structural checks: PASS')
