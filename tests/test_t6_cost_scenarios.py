"""Regression checks for the research calculator; fixtures below are synthetic."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'research/T6-deployment-operations/cost-scenarios.py'
SPEC = SCRIPT.with_name('cost-estimate.scenarios.json')
loader = importlib.util.spec_from_file_location('cost_scenarios', SCRIPT)
calculator = importlib.util.module_from_spec(loader)
loader.loader.exec_module(calculator)


class CostScenarioTests(unittest.TestCase):
    def run_spec(self, expected):
        spec = {'cases': {'low': {}}, 'scenarios': [
            {'id': 'synthetic', 'steps': [['cost', '1']], 'report': ['cost'],
             'expect': {'cost': {'low': expected}}}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.json'
            path.write_text(json.dumps(spec), encoding='utf-8')
            return subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                  capture_output=True, text=True)

    def test_published_scenario_arithmetic(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(SPEC)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('checked 273 quoted figures', result.stdout)

    def test_mismatch_fails(self):
        result = self.run_spec(2)
        self.assertEqual(result.returncode, 1)
        self.assertIn('MISMATCH:', result.stdout)

    def test_nonfinite_expectations_fail(self):
        for expected in (float('nan'), float('inf'), -float('inf')):
            with self.subTest(expected=expected):
                result = self.run_spec(expected)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('all quoted figures match', result.stdout)
                self.assertIn('non-finite number', result.stderr)

    def test_overflowing_json_number_fails(self):
        with self.assertRaisesRegex(ValueError, 'non-finite number'):
            json.loads('{"expected": 1e999}',
                       parse_float=calculator.finite_json_float)

    def test_expression_restrictions(self):
        for expression in ('().__class__', '__import__("os")',
                           '[x for x in (1,)]', 'max(*[1, 2])',
                           'round(1.2, ndigits=1)', 'True'):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    calculator.calc(expression, {})
        self.assertEqual(calculator.calc('ceil(tokens / 2) + max(1, 3)',
                                         {'tokens': 5}), 6)

    def test_rounding_is_half_up(self):
        self.assertEqual(calculator.sf(32500, 2), 33000)
        self.assertEqual(calculator.sf(-32500, 2), -33000)


if __name__ == '__main__':
    unittest.main()
