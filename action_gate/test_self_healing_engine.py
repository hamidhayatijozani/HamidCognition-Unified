import unittest

from action_gate.self_healing_engine import (
    HCFMapper,
    OEROptimizer,
    PatchCandidate,
    SelfHealingEngine,
    TRLELoop,
)


class SelfHealingEngineTests(unittest.TestCase):
    def test_gsrp_detects_unbound_name_without_mutating_source(self):
        source = "def f():\n    return Authority.from_token('x')\n"
        result = SelfHealingEngine().diagnose({"tests/example.py": source})
        self.assertEqual(result.status, "HOLD")
        self.assertTrue(any(f.code == "UNBOUND_NAME_CANDIDATE" for f in result.findings))
        self.assertEqual(source, "def f():\n    return Authority.from_token('x')\n")

    def test_hcf_mapping_is_deterministic(self):
        graph = HCFMapper().map({"a.py": "import b\n", "b.py": "x = 1\n"})
        self.assertEqual(graph["a.py"], ("b",))

    def test_oer_is_explicitly_ranked_by_risk(self):
        items = [
            PatchCandidate("high", "large", ("a.py",), 0.9, ("all",)),
            PatchCandidate("low", "small", ("a.py",), 0.1, ("targeted",)),
        ]
        self.assertEqual(OEROptimizer().rank(items)[0].patch_id, "low")

    def test_trle_replay_is_repeatable(self):
        loop = TRLELoop()
        inputs = (1, 2, 3)
        d1, out1 = loop.replay(inputs, lambda x: x * 2)
        d2, out2 = loop.replay(inputs, lambda x: x * 2)
        self.assertEqual(d1, d2)
        self.assertEqual(out1, out2)


if __name__ == "__main__":
    unittest.main()
