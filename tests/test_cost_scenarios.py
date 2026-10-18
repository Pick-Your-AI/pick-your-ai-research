"""Calculator regressions; synthetic inputs are not price or benchmark evidence."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CALCULATOR = ROOT / "research/T6-deployment-operations/cost-scenarios.py"
SCENARIOS = CALCULATOR.with_name("cost-estimate.scenarios.json")
SPEC = importlib.util.spec_from_file_location("cost_scenarios", CALCULATOR)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CostScenarios(unittest.TestCase):
    def run_calculator(self, path, *args):
        return subprocess.run(
            [sys.executable, str(CALCULATOR), str(path), *map(str, args)],
            capture_output=True, text=True, timeout=30, check=False,
        )

    def test_arithmetic_precedence_and_allowed_functions(self):
        examples = {
            "units * rate + 2 ** 3": 14,
            "-units + +rate": -1,
            "7 // 2 + 7 % 2": 4,
            "ceil(7 / 2) + floor(7 / 2)": 7,
            "sqrt(16) + min(3, 7) + max(3, 7)": 14,
            "round(2.345, 2)": 2.35,
        }
        for expression, expected in examples.items():
            with self.subTest(expression=expression):
                self.assertAlmostEqual(MODULE.calc(expression, {"units": 3, "rate": 2}), expected)

    def test_rejects_python_execution_and_non_arithmetic_syntax(self):
        expressions = (
            "__import__('os')", "open('synthetic.txt', 'w')",
            "(1).__class__.__base__.__subclasses__()", "x[0]",
            "[x for x in (1, 2)]", "(lambda: 1)()", "1 if x else 2",
            "x == 1", "x and 1", "True", "'text'", "[1, 2]",
            "round(1, ndigits=2)", "max(*x)", "missing", "_private",
            "callback()",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    MODULE.calc(expression, {"x": [1], "_private": 1, "callback": lambda: 1})

    def test_significant_figures_use_half_up_rounding(self):
        for value, digits, expected in ((32500, 2, 33000), (-32500, 2, -33000),
                                        (0.0125, 2, 0.013), (0, 2, 0)):
            with self.subTest(value=value):
                self.assertEqual(MODULE.sf(value, digits), expected)

    def test_all_recorded_scenario_expectations_and_json_export(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results.json"
            result = self.run_calculator(SCENARIOS, "--json", output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("checked 273 quoted figures", result.stdout)
            self.assertIn("all quoted figures match", result.stdout)
            results = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                {case: values["monthly"] for case, values in results["W1-gemini"].items()},
                {"low": 10800, "expected": 12000, "high": 31200},
            )

    def test_changed_expectation_fails_with_identified_scenario(self):
        # Mutate a temporary copy only: prove the CLI fails on a bad quote,
        # rather than merely printing a successful arithmetic report.
        spec = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        scenario = next(item for item in spec["scenarios"] if item["id"] == "W1-gemini")
        scenario["expect"]["monthly"]["expected"] = 999999
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-mismatch.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            result = self.run_calculator(path)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("MISMATCH:", result.stdout)
        self.assertIn("W1-gemini monthly expected", result.stdout)
        self.assertNotIn("all quoted figures match", result.stdout)

    def test_nonfinite_quotes_inputs_and_results_fail_before_export(self):
        # Literal 1e999 is valid JSON, but overflows a Python float just as
        # the nonstandard Infinity token does. All fixtures are synthetic.
        base = ('{"cases":{"expected":{}},"shared":{"quantity":1},'
                '"scenarios":[{"id":"synthetic","steps":[["total","quantity * 2"]],'
                '"report":["total"],"expect":{"total":{"expected":2}}}]}')
        variants = {
            "nan_quote": base.replace('"expected":2', '"expected":NaN'),
            "infinite_quote": base.replace('"expected":2', '"expected":Infinity'),
            "overflow_quote": base.replace('"expected":2', '"expected":1e999'),
            "nan_input": base.replace('"quantity":1', '"quantity":NaN'),
            "negative_infinite_input": base.replace('"quantity":1', '"quantity":-Infinity'),
            "overflow_input": base.replace('"quantity":1', '"quantity":1e999'),
            "evaluated_overflow": base.replace('"quantity":1', '"quantity":1e308'),
            "masked_intermediate_overflow": base.replace('"quantity":1', '"quantity":1e308')
                                                .replace('quantity * 2', 'min(quantity * 2, 2)'),
            "rounded_overflow": base.replace('"quantity":1', '"quantity":1.79e308')
                                    .replace('quantity * 2', 'quantity'),
        }
        for name, content in variants.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "synthetic-nonfinite.json"
                output = Path(directory) / "results.json"
                source.write_text(content, encoding="utf-8")
                result = self.run_calculator(source, "--json", output)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("nonfinite number", result.stderr)
                self.assertNotIn("all quoted figures match", result.stdout)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
