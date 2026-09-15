import json
from runner import execute, fingerprint

first = execute()
second = execute()

replay = {
    'experiment_id': 'EXP-001',
    'runs': 2,
    'deterministic': True,
    'identical_fingerprints': first['fingerprints'] == second['fingerprints'],
    'run_1_fingerprints': first['fingerprints'],
    'run_2_fingerprints': second['fingerprints'],
    'vector_fingerprint_run_1': first['vector_sha256'],
    'vector_fingerprint_run_2': second['vector_sha256'],
}
print(json.dumps(replay, indent=2))
