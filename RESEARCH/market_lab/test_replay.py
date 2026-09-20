import json
import unittest
from pathlib import Path
from RESEARCH.market_lab.maat import PriceObservation
from RESEARCH.market_lab.experiment import run_snapshot_experiment

class ReplayTests(unittest.TestCase):
    def test_fixture_replay_is_identical(self):
        fixture = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "maat_thoth_snapshot.json").read_text(encoding="utf-8"))
        observations = [PriceObservation(**row) for row in fixture["observations"]]
        a = run_snapshot_experiment(observations, fixture["symbol"])
        b = run_snapshot_experiment(observations, fixture["symbol"])
        self.assertEqual(a["fingerprint"], b["fingerprint"])

if __name__ == "__main__":
    unittest.main()
