import hashlib, json
from runner import execute, VECTOR

print('VECTOR_SHA256', hashlib.sha256(json.dumps(VECTOR, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
for variant, trajectory in execute()['results'].items():
    print(variant, hashlib.sha256(json.dumps(trajectory, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
