"""Numerical and CLI contract tests for the shipped exact bridge calculator."""

from copy import deepcopy
from decimal import Decimal
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "flux-analysis/scripts/decompose.py"
SPEC = importlib.util.spec_from_file_location("decompose", SCRIPT)
BRIDGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BRIDGE)


def product(segment, quantity, price):
    return {"segment": segment, "quantity": quantity, "price": price}


def rate(segment, weight, value):
    return {"segment": segment, "weight": weight, "rate": value}


class RevenueBridgeTests(unittest.TestCase):
    def test_simultaneous_price_and_quantity_change_keeps_interaction(self):
        result = BRIDGE.revenue_bridge([product("x", 100, 10)], [product("x", 110, 12)])
        self.assertEqual(result, {"baseline": 1000, "actual": 1320, "quantity": 100,
                                  "mix": 0, "price": 220, "change": 320})

    def test_multi_product_bridge_with_offsetting_drivers(self):
        result = BRIDGE.revenue_bridge(
            [product("a", 60, 10), product("b", 40, 20)],
            [product("a", 40, 12), product("b", 80, 18)])
        self.assertEqual(result, {"baseline": 1400, "actual": 1920, "quantity": 280,
                                  "mix": 320, "price": -80, "change": 520})

    def test_seeded_bridges_follow_ordered_counterfactual_totals(self):
        rng = random.Random(731)
        for _ in range(500):
            baseline = [product(str(i), rng.randint(1, 500), rng.randint(-20, 80))
                        for i in range(rng.randint(1, 12))]
            actual = [product(row["segment"], rng.randint(0, 500), rng.randint(-20, 80))
                      for row in baseline]
            if not any(row["quantity"] for row in actual):
                actual[0]["quantity"] = 1
            untouched = deepcopy((baseline, actual))
            result = BRIDGE.revenue_bridge(baseline, actual)
            scale = F(sum(row["quantity"] for row in actual),
                      sum(row["quantity"] for row in baseline))
            at_base_prices = sum(b["price"] * a["quantity"]
                                 for b, a in zip(baseline, actual))
            self.assertEqual(result["baseline"] + result["quantity"],
                             scale * result["baseline"])
            self.assertEqual(result["baseline"] + result["quantity"] + result["mix"],
                             at_base_prices)
            self.assertEqual(result["baseline"] + result["quantity"] + result["mix"]
                             + result["price"], result["actual"])
            self.assertEqual(result["change"], result["actual"] - result["baseline"])
            self.assertEqual(result, BRIDGE.revenue_bridge(baseline[::-1], actual[::-1]))
            self.assertEqual((baseline, actual), untouched)

    def test_new_and_discontinued_products_require_explicit_prices(self):
        result = BRIDGE.revenue_bridge(
            [product("old", 10, 5), product("new", 0, 8)],
            [product("old", 0, 5), product("new", 10, 9)])
        self.assertEqual((result["quantity"], result["mix"], result["price"]), (0, 30, 10))
        self.assertEqual(result["change"], 40)

    def test_paid_fte_periods_and_cost_reconcile(self):
        result = BRIDGE.revenue_bridge(
            [product("paid-fte-months", "10.5", "1000")],
            [product("paid-fte-months", "12.25", "1100")])
        self.assertEqual((result["quantity"], result["price"], result["change"]),
                         (1750, 1225, 2975))


class WeightedRateBridgeTests(unittest.TestCase):
    def test_gross_margin_mix_and_rate_are_fractional_rates(self):
        result = BRIDGE.weighted_rate_bridge(
            [rate("x", 500, "0.6"), rate("y", 500, "0.4")],
            [rate("x", 400, "0.5"), rate("y", 600, "0.3")])
        self.assertEqual(result, {"baseline": F("0.5"), "actual": F("0.38"),
                                  "mix": F("-0.02"), "rate": F("-0.1"),
                                  "change": F("-0.12")})
        self.assertEqual(100 * result["change"], -12)  # percentage points

    def test_denominator_scaling_does_not_change_rate_effects(self):
        base = [rate("a", 2, "-0.2"), rate("b", 3, "1.2")]
        end = [rate("a", 7, "0.1"), rate("b", 1, "0.6")]
        scaled = [rate(row["segment"], row["weight"] * 1000, row["rate"]) for row in end]
        self.assertEqual(BRIDGE.weighted_rate_bridge(base, end),
                         BRIDGE.weighted_rate_bridge(base, scaled))

    def test_seeded_rate_bridges_reconcile_and_preserve_mix_then_rate_order(self):
        rng = random.Random(903)
        for _ in range(500):
            base = [rate(str(i), rng.randint(1, 100), F(rng.randint(-50, 150), 100))
                    for i in range(rng.randint(1, 12))]
            end = [rate(row["segment"], rng.randint(1, 100), F(rng.randint(-50, 150), 100))
                   for row in base]
            result = BRIDGE.weighted_rate_bridge(base, end)
            changed_mix_total = sum(a["weight"] * b["rate"] for b, a in zip(base, end))
            changed_mix_rate = changed_mix_total / sum(row["weight"] for row in end)
            self.assertEqual(result["baseline"] + result["mix"], changed_mix_rate)
            self.assertEqual(result["baseline"] + result["mix"] + result["rate"],
                             result["actual"])
            self.assertEqual(result["mix"] + result["rate"], result["change"])
            self.assertEqual(result, BRIDGE.weighted_rate_bridge(base[::-1], end[::-1]))


class InputContractTests(unittest.TestCase):
    def test_invalid_inputs_fail_without_inventing_missing_values(self):
        good = [product("a", 10, 2)]
        invalid_periods = [None, [], [42], [product("", 1, 2)], good + good,
                           [{"segment": "a", "quantity": 10}], [product("b", 10, 2)],
                           [product("a", -1, 2)], [product("a", 0, 2)]]
        invalid_numbers = [True, None, 1.1, "NaN", "Infinity", "1/0", [], {}]
        invalid_periods += [[product("a", value, 2)] for value in invalid_numbers]
        invalid_periods += [[product("a", 10, value)] for value in invalid_numbers]
        for invalid in invalid_periods:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                BRIDGE.revenue_bridge(good, invalid)

    def test_weight_contract_matches_revenue_contract(self):
        good = [rate("a", 1, "0.5")]
        for invalid in ([rate("a", 0, "0.5")], [rate("a", -1, "0.5")],
                        [rate("b", 1, "0.5")], [{"segment": "a", "weight": 1}]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                BRIDGE.weighted_rate_bridge(good, invalid)

    def test_decimal_objects_and_strings_are_exact(self):
        result = BRIDGE.revenue_bridge(
            [product("a", Decimal("0.1"), "0.2")], [product("a", "0.3", Decimal("0.4"))])
        self.assertEqual(result["change"], F("0.1"))

    def test_cli_preserves_inputs_and_emits_exact_rational_strings(self):
        raw = '{"baseline":[{"segment":"a","quantity":0.1,"price":0.2}],"actual":[{"segment":"a","quantity":0.3,"price":0.4}]}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(raw, encoding="utf-8")
            run = subprocess.run([sys.executable, str(SCRIPT), "--mode", "revenue", "--input", str(path)],
                                 capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(run.stdout)["change"], "1/10")
            self.assertEqual(path.read_text(encoding="utf-8"), raw)

    def test_cli_rejects_bad_envelopes_and_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for raw in ('[]', '{}', 'invalid-json',
                        '{"baseline":[{"segment":"a","quantity":1,"price":NaN}],"actual":[]}'):
                path.write_text(raw, encoding="utf-8")
                run = subprocess.run([sys.executable, str(SCRIPT), "--mode", "revenue", "--input", str(path)],
                                     capture_output=True, text=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertEqual(run.stdout, "")

    def test_cli_weighted_rate_mode_uses_denominator_weights(self):
        data = {"baseline": [rate("x", 500, "0.6"), rate("y", 500, "0.4")],
                "actual": [rate("x", 400, "0.5"), rate("y", 600, "0.3")]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            run = subprocess.run([sys.executable, str(SCRIPT), "--mode", "weighted-rate", "--input", str(path)],
                                 capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(run.stdout), {"baseline": "1/2", "actual": "19/50",
                                                      "mix": "-1/50", "rate": "-1/10",
                                                      "change": "-3/25"})


if __name__ == "__main__":
    unittest.main()
