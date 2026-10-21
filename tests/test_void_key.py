"""Unit and property-style tests for the KIRGANDE reference metrics."""
import math
import unittest

from kirgande.void_key import (
    MetricsError,
    calculate_chaos,
    calculate_drs,
    calculate_hais,
    canonical_sha256,
    make_chaos_snapshot,
)


class MetricsTests(unittest.TestCase):
    def test_hais_baseline_bounds_and_weight_sum(self):
        self.assertAlmostEqual(calculate_hais(1, 0, 1, 1, 0), 1.0)
        self.assertAlmostEqual(calculate_hais(0, 1, 0, 0, 1), 0.0)
        for x in (0.0, 0.1, 0.5, 0.9, 1.0):
            score = calculate_hais(x, x, x, x, x)
            self.assertTrue(0.0 <= score <= 1.0)

    def test_hais_chaos_blend_requires_explicit_value(self):
        with self.assertRaises(MetricsError):
            calculate_hais(0.5, 0.5, 0.5, 0.5, 0.5, chaos_weight=0.2)
        score = calculate_hais(
            0.5, 0.5, 0.5, 0.5, 0.5,
            chaos_normalized=1.0, chaos_weight=0.2,
        )
        self.assertTrue(0.0 <= score <= 1.0)

    def test_drs_normalized_bounds_and_extremes(self):
        self.assertAlmostEqual(calculate_drs(1, 1, 1, 1), 1.0)
        self.assertAlmostEqual(calculate_drs(0, 0, 0, 0), 0.0)
        self.assertTrue(0.0 <= calculate_drs(0.4, 0.3, 0.2, 0.1) <= 1.0)

    def test_chaos_formula_bounds(self):
        self.assertEqual(calculate_chaos(0.4, 0.4, 1.0, 1.0), 0.0)
        self.assertEqual(calculate_chaos(1.0, 0.0, 1.0, 1.0), 1.0)
        self.assertAlmostEqual(calculate_chaos(0.9, 0.1, 0.5, 0.5), 0.2)

    def test_invalid_inputs_rejected(self):
        for value in (-0.1, 1.1, math.nan, math.inf, -math.inf, True, None):
            with self.subTest(value=value):
                with self.assertRaises(MetricsError):
                    calculate_chaos(value, 0.5, 0.5, 0.5)

    def test_deterministic_canonical_hash(self):
        self.assertEqual(
            canonical_sha256({"b": 2, "a": 1}),
            canonical_sha256({"a": 1, "b": 2}),
        )
        self.assertNotEqual(canonical_sha256({"a": 1}), canonical_sha256({"a": 2}))

    def test_snapshot_provenance_and_repeatability(self):
        args = dict(
            window="2026-10-21T00:00Z/2026-10-21T00:05Z",
            input_artifacts={"fixture": "fixture-001", "version": 1},
            direct=0.9,
            inverse=0.1,
            entropy_normalized=0.5,
            confidence_product=0.5,
        )
        first = make_chaos_snapshot(**args)
        second = make_chaos_snapshot(**args)
        self.assertEqual(first, second)
        self.assertEqual(first.snapshot_sha256, second.snapshot_sha256)
        self.assertEqual(first.chaos_normalized, 0.2)

    def test_missing_data_fails_closed(self):
        with self.assertRaises(MetricsError):
            make_chaos_snapshot(
                window="test",
                input_artifacts={},
                direct=0.5,
                inverse=0.5,
                entropy_normalized=0.5,
                confidence_product=0.5,
                missing_data=True,
            )

    def test_empty_claim_population_not_silently_scored(self):
        # EAS/OCR denominators are not part of these normalized primitives.
        # A caller must not encode an empty population as a fabricated score.
        with self.assertRaises(MetricsError):
            calculate_hais(None, 0.0, 0.0, 0.0, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
