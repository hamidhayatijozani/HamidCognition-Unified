import hashlib
import json
from pathlib import Path

from shock_recovery import trajectory

ROOT = Path(__file__).parent
scenarios = {
    "no_shock": [0, 0, 0, 0, 0],
    "single_shock": [10],
    "persistent_shock": [10] * 10,
    "shock_removal": [10, 10, 0, 0, 0, 0],
}
results = {name: trajectory(values) for name, values in scenarios.items()}
payload = json.dumps(results["shock_removal"], sort_keys=True, separators=(",", ":"))
print(json.dumps({
    "tests": "see test_shock_recovery.py",
    "shock_removal_trajectory_sha256": hashlib.sha256(payload.encode()).hexdigest(),
    "results": results,
}, indent=2, sort_keys=True))
