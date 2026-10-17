"""Synthetic optionality checks for research proposals, not product certification."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'contracts/v1'
SPEC = importlib.util.spec_from_file_location('t4_evaluator', CONTRACT / 'reference/evaluate.py')
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)
KINDS = {'agent_framework', 'tool', 'integration', 'mcp_server', 'memory_store'}


class T4Optionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = json.loads((CONTRACT / 'examples/build.json').read_text())
        cls.catalog = json.loads((CONTRACT / 'examples/catalog.json').read_text())
        cls.rules = json.loads((CONTRACT / 'examples/ruleset.json').read_text())
        cls.proposals = []
        for name, count in [('agent-framework', 4), ('tools-apis', 10), ('mcp-servers', 6), ('agent-memory', 4)]:
            note = (ROOT / f'research/T4-agents-integrations/{name}.md').read_text(encoding='utf-8')
            rules = [json.loads(block) for block in re.findall(r'```json\s*\n(.*?)\n```', note, re.S)]
            rules = [rule for rule in rules if rule.get('id', '').startswith('rule.t4.')]
            if len(rules) != count:
                raise AssertionError(f'{name}: expected {count} executable research proposals, got {len(rules)}')
            cls.proposals.extend(rules)
        cls.rules['rules'] = cls.proposals
        schemas = [json.loads(p.read_text()) for p in (CONTRACT / 'schemas').glob('*.schema.json')]
        registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in schemas)
        schema = next(s for s in schemas if s['$id'].endswith('/ruleset.schema.json'))
        Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).validate(cls.rules)

    def test_absent_or_disabled_t4_does_not_activate_proposals(self):
        for mode in ['absent', 'disabled']:
            with self.subTest(mode=mode):
                build = copy.deepcopy(self.build)
                if mode == 'absent':
                    removed = {s['id'] for s in build['selections'] if s['kind'] in KINDS}
                    build['selections'] = [s for s in build['selections'] if s['kind'] not in KINDS]
                    build['links'] = [link for link in build.get('links', []) if link['from_selection_id'] not in removed and link['to_selection_id'] not in removed]
                else:
                    for selection in build['selections']:
                        if selection['kind'] in KINDS:
                            selection['enabled'] = False
                findings = EVALUATOR.Evaluator(build, self.catalog, self.rules).evaluate()['findings']
                self.assertEqual(len(findings), len(self.proposals))
                self.assertTrue(all(f['outcome'] == 'skipped' for f in findings), findings)


if __name__ == '__main__':
    unittest.main()
