"""Behavior checks for local analytical helpers; no network or model calls."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


profile = load("profile_csv").profile_csv
check = load("check_evidence").check_evidence


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "orders.csv"

    def write(self, text):
        self.path.write_text(text, encoding="utf-8")

    def test_missing_invalid_zero_and_textual_ids_remain_distinct(self):
        self.write("id,revenue\n001,0\n1,10\n001,\n2,broken\n,20\n")
        result = profile(self.path, numeric=["revenue"], key=["id"])
        stats = result["numeric"]["revenue"]
        self.assertEqual(result["row_count"], 5)
        self.assertEqual(result["key"]["duplicate_rows_after_first"], 1)
        self.assertEqual(result["key"]["rows_with_missing_key"], 1)
        self.assertEqual(stats["valid_numeric_count"], 3)
        self.assertEqual(stats["missing_count"], 1)
        self.assertEqual(stats["invalid_numeric_count"], 1)
        self.assertEqual(stats["sum"], 30)
        self.assertEqual(stats["mean"], 10)
        self.assertEqual(stats["sample_stddev"], 10)

    def test_missing_tokens_are_explicit(self):
        self.write("value\nNA\n0\n")
        default = profile(self.path, numeric=["value"])["numeric"]["value"]
        configured = profile(self.path, numeric=["value"], missing=["NA"])["numeric"][
            "value"
        ]
        self.assertEqual(default["invalid_numeric_count"], 1)
        self.assertEqual(configured["missing_count"], 1)
        self.assertEqual(configured["valid_numeric_count"], 1)

    def test_nonfinite_currency_and_thousands_are_not_coerced(self):
        self.write('value\nNaN\nInfinity\n1e999\n"1,000"\n$20\n2.5\n')
        result = profile(self.path, numeric=["value"])["numeric"]["value"]
        self.assertEqual(result["invalid_numeric_count"], 5)
        self.assertEqual(result["sum"], 2.5)

    def test_composite_key_and_quoted_fields(self):
        self.write('region,id,note\nEast,01,"a,b"\nWest,01,"two\nlines"\nEast,01,c\n')
        result = profile(self.path, key=["region", "id"])
        self.assertEqual(result["row_count"], 3)
        self.assertEqual(result["key"]["duplicate_rows_after_first"], 1)

    def test_bom_and_empty_numeric_population(self):
        self.write('\ufeffid,value\na,""\nb," "\n')
        result = profile(self.path, numeric=["value"])
        self.assertEqual(result["columns"], ["id", "value"])
        self.assertIsNone(result["numeric"]["value"]["sum"])
        self.assertIsNone(result["numeric"]["value"]["mean"])

    def test_bad_schema_and_rows_fail_instead_of_silently_losing_data(self):
        for content in (
            "id,id\na,b\n",
            "id,\na,b\n",
            "id,value\na\n",
            "id,value\na,2,3\n",
            " id,value\na,1\n",
        ):
            with self.subTest(content=content):
                self.write(content)
                with self.assertRaises(ValueError):
                    profile(self.path)

    def test_row_limit_and_unknown_columns_are_explicit(self):
        self.write("id,value\na,1\nb,2\n")
        with self.assertRaises(ValueError):
            profile(self.path, max_rows=1)
        with self.assertRaises(ValueError):
            profile(self.path, numeric=["missing"])

    def test_cli_outputs_json_and_preserves_input(self):
        self.write("id,value\n001,3\n002,5\n")
        original = self.path.read_bytes()
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/profile_csv.py"),
                str(self.path),
                "--numeric",
                "value",
                "--key",
                "id",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["numeric"]["value"]["mean"], 4)
        self.assertEqual(self.path.read_bytes(), original)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "assets/evidence.example.json").read_text())

    def test_valid_structure_preserves_unverified_and_conditional_findings(self):
        result = check(self.document)
        self.assertTrue(result["structure_valid"])
        self.assertEqual(result["review_required"], ["C2", "C3"])
        self.assertIn("Structural checks only", result["limitations"])

    def test_duplicate_ids_and_unknown_citations_are_errors(self):
        self.document["sources"].append(copy.deepcopy(self.document["sources"][0]))
        self.document["claims"].append(copy.deepcopy(self.document["claims"][0]))
        self.document["claims"][0]["source_ids"] = ["not-found"]
        result = check(self.document)
        self.assertFalse(result["structure_valid"])
        self.assertTrue(any("Duplicate source" in error for error in result["errors"]))
        self.assertTrue(any("Duplicate claim" in error for error in result["errors"]))
        self.assertTrue(any("unknown source" in error for error in result["errors"]))

    def test_forecast_cannot_be_promoted_to_observed_fact_status(self):
        self.document["claims"][1]["status"] = "supported"
        self.assertFalse(check(self.document)["structure_valid"])

    def test_derived_claim_needs_basis_and_conditionality_needs_assumptions(self):
        claim = self.document["claims"][1]
        claim.pop("basis")
        claim.pop("assumptions")
        claim.pop("limitations")
        self.assertEqual(len(check(self.document)["errors"]), 3)

    def test_supported_claim_needs_a_source_and_source_needs_a_real_date(self):
        self.document["claims"][0]["source_ids"] = []
        self.document["sources"][0]["accessed_on"] = "2026-02-30"
        self.assertEqual(len(check(self.document)["errors"]), 2)

    def test_malformed_input_types_fail_without_crashing(self):
        for document in (
            [],
            {},
            {"sources": [3], "claims": [None]},
            {"sources": {}, "claims": "text"},
        ):
            with self.subTest(document=document):
                self.assertFalse(check(document)["structure_valid"])
        for field in ("kind", "status", "source_ids", "assumptions"):
            document = copy.deepcopy(self.document)
            document["claims"][1][field] = {}
            with self.subTest(field=field):
                self.assertFalse(check(document)["structure_valid"])

    def test_empty_ledger_does_not_pass_as_a_completed_analysis(self):
        self.assertFalse(check({"sources": [], "claims": []})["structure_valid"])

    def test_cli_rejects_duplicate_json_keys_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            for text in ('{"sources": [], "sources": []}', '{"value": NaN}'):
                path.write_text(text)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts/check_evidence.py"),
                        str(path),
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(json.loads(result.stdout)["structure_valid"])

    def test_cli_exit_status_distinguishes_valid_and_invalid_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            for valid in (True, False):
                if not valid:
                    self.document["claims"][0]["source_ids"] = ["missing"]
                path.write_text(json.dumps(self.document))
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts/check_evidence.py"),
                        str(path),
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0 if valid else 1, result.stderr)
                self.assertEqual(json.loads(result.stdout)["structure_valid"], valid)


if __name__ == "__main__":
    unittest.main()
