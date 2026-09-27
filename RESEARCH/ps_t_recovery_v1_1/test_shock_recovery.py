import hashlib
import json

from shock_recovery import trajectory

def test_no_shock():
    rows = trajectory([0, 0, 0, 0, 0])
    assert all(abs(x["T"] - 0.5) < 1e-12 for x in rows)
    assert all(x["R"] == 0 for x in rows)

def test_single_shock_degrades():
    rows = trajectory([10])
    assert abs(rows[-1]["T"] - 0.31818182) < 1e-12
    assert rows[-1]["R"] == 0

def test_persistent_shock_no_recovery():
    rows = trajectory([10] * 10)
    assert all(x["R"] == 0 for x in rows)
    assert all(rows[i]["T"] <= (rows[i-1]["T"] if i else 0.5) for i in range(len(rows)))
    assert rows[-1]["T"] == 0.01

def test_shock_removal_recovery():
    rows = trajectory([10, 10, 0, 0, 0, 0])
    recovery = [x["T"] for x in rows[2:]]
    assert all(x["R"] == 1 for x in rows[2:])
    assert recovery == sorted(recovery)
    assert recovery[-1] > recovery[0]

def test_replay_sha256():
    d = [10, 10, 0, 0, 0, 0]
    a = trajectory(d)
    b = trajectory(d)
    payload = json.dumps(a, sort_keys=True, separators=(",", ":"))
    assert a == b
    assert hashlib.sha256(payload.encode()).hexdigest() == "99dc3e16b014e9f433c3dbdc60557c21d1633dde3c6879d1dd7e45cedcd0a3eb"
