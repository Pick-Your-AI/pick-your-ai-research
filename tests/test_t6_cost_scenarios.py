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
        spec = json.loads(SPEC.read_text())
        self.assertTrue(spec['scenarios'])
        for scenario in spec['scenarios']:
            with self.subTest(scenario=scenario['id']):
                self.assertTrue(scenario['expect'])
                for expected in scenario['expect'].values():
                    self.assertEqual(set(expected) - {'sf'}, set(spec['cases']))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'results.json'
            result = subprocess.run([sys.executable, str(SCRIPT), str(SPEC), '--json', str(output)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            results = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(
            {case: values['monthly'] for case, values in results['W1-gemini'].items()},
            {'low': 10800, 'expected': 12000, 'high': 31200},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('checked 273 quoted figures', result.stdout)

    def test_evaluated_and_rounded_overflow_fail_before_export(self):
        # Finite JSON inputs can still overflow during evaluation or rounding.
        for expression, quantity in (('quantity * 2', 1e308),
                                     ('min(quantity * 2, 2)', 1e308),
                                     ('quantity', 1.79e308)):
            with self.subTest(expression=expression), tempfile.TemporaryDirectory() as directory:
                spec = {'cases': {'low': {}}, 'shared': {'quantity': quantity},
                        'scenarios': [{'id': 'synthetic', 'steps': [['cost', expression]],
                                       'report': ['cost'], 'expect': {'cost': {'low': 2}}}]}
                source = Path(directory) / 'synthetic-overflow.json'
                output = Path(directory) / 'results.json'
                source.write_text(json.dumps(spec), encoding='utf-8')
                result = subprocess.run([sys.executable, str(SCRIPT), str(source), '--json', str(output)],
                                        capture_output=True, text=True, timeout=30)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('non-finite number', result.stderr)
                self.assertNotIn('all quoted figures match', result.stdout)
                self.assertFalse(output.exists())

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
