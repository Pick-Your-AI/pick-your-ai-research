"""Executable CD-7 cases; no production migration or evidence acceptance."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from t0_migration_prototype import component_modes, project


class MigrationCases(unittest.TestCase):
    def test_documented_cases(self):
        fixture = json.loads((ROOT / 'tests/fixtures/t0-migration.json').read_text())
        self.assertTrue(fixture['synthetic'])
        original = (ROOT / 'contracts/v1/examples/build.json').read_bytes()
        for case in fixture['cases']:
            with self.subTest(case=case['id']):
                before = json.dumps(case, sort_keys=True)
                retained, sidecar = project(original, case['extensions'])
                self.assertEqual(retained, original)
                self.assertEqual(before, json.dumps(case, sort_keys=True))
                result = sidecar['x_t0_migration_projection']
                for key, expected in case['expected'].items():
                    self.assertEqual(result[key], expected)

    def test_legacy_labels_cannot_supply_component_facts(self):
        for mode in ('api', 'managed', 'self_hosted', 'hybrid'):
            legacy = json.dumps({'deployment_mode': mode}).encode()
            _, projected = project(legacy, {'x_t0_migration_inputs': {
                'components': [{'id': 'model', 'kind': 'model'}]}})
            self.assertEqual(projected['x_t0_migration_projection']['overall_mode'], 'unknown')

    def test_all_published_operator_capacity_pairs(self):
        for capacity in ('shared', 'reserved_throughput', 'dedicated_instances', None):
            for operator in ('self', 'provider', None):
                expected = ('self_hosted' if operator == 'self' else
                            'api' if operator == 'provider' and capacity == 'shared' else
                            'managed' if operator == 'provider' and capacity in
                            {'reserved_throughput', 'dedicated_instances'} else 'unknown')
                _, mode = component_modes([{'id': 'm', 'kind': 'model',
                    'deployment': {'runtime_operator': operator, 'capacity': capacity}}])
                self.assertEqual(mode, expected)

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):
            component_modes([{'id': 'm', 'kind': 'model'}] * 2)

    def test_adapter_cycle_is_unknown(self):
        components = [{'id': 'a', 'kind': 'fine_tuned_model', 'artifact_type': 'adapter', 'base_id': 'b'},
                      {'id': 'b', 'kind': 'fine_tuned_model', 'artifact_type': 'adapter', 'base_id': 'a'}]
        self.assertEqual(component_modes(components), ({'b': 'unknown', 'a': 'unknown'}, 'unknown'))

    def test_adapter_does_not_inherit_unrelated_serving_deployment(self):
        # #81 deployment-mode.md: adapters inherit a base model deployment.
        # v1 spec_fine_tuned_model.base_model_ref also names catalog kind model.
        for kind in ('vector_database', 'embedding_model', 'inference_engine'):
            for reverse in (False, True):
                with self.subTest(kind=kind, reverse=reverse):
                    components = [
                        {'id': 'base', 'kind': kind, 'deployment': {
                            'runtime_operator': 'provider', 'capacity': 'shared'}},
                        {'id': 'adapter', 'kind': 'fine_tuned_model',
                         'artifact_type': 'adapter', 'base_id': 'base'}]
                    modes, overall = component_modes(
                        list(reversed(components)) if reverse else components)
                    self.assertEqual(modes['adapter'], 'unknown')
                    self.assertEqual(overall, 'unknown')

    def test_adapter_disabled_base_is_unknown_in_any_order(self):
        for reverse in (False, True):
            components = [
                {'id': 'base', 'kind': 'model', 'enabled': False,
                 'deployment': {'runtime_operator': 'self'}},
                {'id': 'adapter', 'kind': 'fine_tuned_model',
                 'artifact_type': 'adapter', 'base_id': 'base'}]
            self.assertEqual(component_modes(
                list(reversed(components)) if reverse else components),
                ({'adapter': 'unknown'}, 'unknown'))

    def test_v1_historical_evaluation_unchanged(self):
        sys.path.insert(0, str(ROOT / 'contracts/v1/reference'))
        from evaluate import Evaluator
        def load(name):
            return json.loads((ROOT / 'contracts/v1/examples' / name).read_text())
        original = (ROOT / 'contracts/v1/examples/build.json').read_bytes()
        retained, _ = project(original, {'x_t0_migration_inputs': {}})
        def evaluate(raw):
            result = Evaluator(json.loads(raw), load('catalog.json'), load('ruleset.json'),
                cost_estimate=load('cost-estimate.json'), resource_estimate=load('resource-estimate.json')).evaluate()
            return result['result'], result['findings'], result['summary']
        self.assertEqual(evaluate(original), evaluate(retained))
