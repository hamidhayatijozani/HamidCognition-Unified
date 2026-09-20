import unittest
from maat import MaatOracle, PriceObservation
from thoth import ThothEngine
from paper_trader import PaperTrader

class MarketLabTests(unittest.TestCase):
    def test_maat_consensus_and_outlier_rejection(self):
        oracle = MaatOracle(max_relative_dispersion=0.01, min_sources=2)
        oracle.submit(PriceObservation("a", "EURUSD", 1.1000, "2026-01-01T00:00:00Z"))
        oracle.submit(PriceObservation("b", "EURUSD", 1.1005, "2026-01-01T00:00:00Z"))
        oracle.submit(PriceObservation("c", "EURUSD", 1.20, "2026-01-01T00:00:00Z"))
        result = oracle.consensus("EURUSD")
        self.assertEqual(result.status, "CONSENSUS")
        self.assertEqual(set(result.rejected_sources), {"c"})
        self.assertAlmostEqual(result.price, 1.10025, places=5)

    def test_maat_refuses_single_source(self):
        oracle = MaatOracle(min_sources=2)
        oracle.submit(PriceObservation("a", "EURUSD", 1.1, "2026-01-01T00:00:00Z"))
        self.assertEqual(oracle.consensus("EURUSD").status, "INSUFFICIENT_SOURCES")

    def test_thoth_is_deterministic(self):
        engine = ThothEngine()
        prices = [100, 100.2, 100.4, 100.8, 101.0]
        self.assertEqual(engine.analyze("BTCUSDT", prices), engine.analyze("BTCUSDT", prices))
        self.assertEqual(engine.analyze("BTCUSDT", prices).signal, "LONG")

    def test_paper_trader_accounts_for_costs(self):
        trader = PaperTrader(starting_cash=1000, fee_rate=0.001, slippage_bps=2)
        trader.step(0, "BTCUSDT", "LONG", 100)
        self.assertLessEqual(trader.mark_to_market(100), 1000)
        self.assertEqual(len(trader.trades), 1)

if __name__ == "__main__":
    unittest.main()
