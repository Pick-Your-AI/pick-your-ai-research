"""Check arithmetic and expression safety, not vendor rates or price eligibility."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'research/T6-deployment-operations'
SCRIPT = DIRECTORY / 'cost-scenarios.py'
SPEC = DIRECTORY / 'cost-estimate.scenarios.json'
loader = importlib.util.spec_from_file_location('t6_cost_scenarios', SCRIPT)
calculator = importlib.util.module_from_spec(loader)
loader.loader.exec_module(calculator)


class CostScenarioTests(unittest.TestCase):
    def run_spec(self, path):
        return subprocess.run([sys.executable, str(SCRIPT), str(path)],
                              capture_output=True, text=True, timeout=30)

    def test_published_scenarios_recompute(self):
        spec = json.loads(SPEC.read_text())
        self.assertTrue(spec['scenarios'])
        for scenario in spec['scenarios']:
            with self.subTest(scenario=scenario['id']):
                self.assertTrue(scenario['expect'])
                for expected in scenario['expect'].values():
                    self.assertEqual(set(expected) - {'sf'}, set(spec['cases']))
        result = self.run_spec(SPEC)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('all quoted figures match', result.stdout)

    def test_changed_quote_fails_validation(self):
        spec = json.loads(SPEC.read_text())
        scenario = spec['scenarios'][0]
        quantity = next(iter(scenario['expect']))
        case = next(iter(spec['cases']))
        scenario['expect'][quantity][case] += 1000000
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'changed-quote.json'
            path.write_text(json.dumps(spec))
            result = self.run_spec(path)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('MISMATCH:', result.stdout)
        self.assertIn(f"{scenario['id']} {quantity} {case}", result.stdout)

    def test_expression_whitelist_rejects_python_execution(self):
        expressions = ["__import__('os')", '(1).__class__', '[x for x in [1]]',
                       '(lambda: 1)()', 'x[0]', "'1'", 'True', '_hidden',
                       'round(1, ndigits=2)']
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    calculator.calc(expression, {'x': [1], '_hidden': 2})

    def test_permitted_arithmetic_and_rounding(self):
        self.assertEqual(calculator.calc('ceil(tokens / batch) * price',
                                        {'tokens': 11, 'batch': 5, 'price': 2}), 6)
        self.assertEqual(calculator.calc('max(2, 3) + sqrt(16) - -1', {}), 8)
        self.assertEqual(calculator.sf(32500, 2), 33000)
        self.assertEqual(calculator.sf(-32500, 2), -33000)
