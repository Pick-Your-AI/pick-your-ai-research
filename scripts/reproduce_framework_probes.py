"""Synthetic probes of three hash-pinned upstream function bodies only.

Reads already fetched source files; makes no network requests or framework imports.
The Agno API module is replaced by a local recorder before its helper is compiled.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from types import ModuleType, SimpleNamespace

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path, help='Directory of the three hash-pinned <key>.txt files listed in the fixture')
    parser.add_argument('--verify', action='store_true', help='Compare the synthetic outputs with the retained fixture')
    args = parser.parse_args()
    root = args.source_dir
    fixture_path = Path(__file__).resolve().parents[1] / 'tests/fixtures/framework-evaluation-probes.json'
    fixture = json.loads(fixture_path.read_text(encoding='utf-8'))
    ledger = {r['key']: r for r in fixture['sources']}
    pins = {
        'crew-evalrunner': '92f917c3294c480b19293a8d83fde40e9b20584a89e00b857d598a4de6bd77a3',
        'agno-init': '5d1c21d50306d56a075ad32bae03b152618cbc6e7821ec4027a17345c0531362',
        'agno-evalutils': '2d5862083f0e2c7cb0b194f2ce6de571316b60fffe995c912caa8405c7c31640',
    }


    def load_function(key, function_name, namespace):
        path = root / (key + '.txt')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != pins[key]:
            raise ValueError('Source pin mismatch: ' + key)
        parsed = ast.parse(data, filename=str(path))
        matches = [n for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef) and n.name == function_name]
        if len(matches) != 1:
            raise ValueError('Ambiguous function: ' + function_name)
        future = ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)
        isolated = ast.Module(body=[future, matches[0]], type_ignores=[])
        ast.fix_missing_locations(isolated)
        exec(compile(isolated, str(path), 'exec'), namespace)
        return namespace[function_name]


    score_check = load_function('crew-evalrunner', '_assert_scores', {})
    cases = [
        ('complete_pass', {'goal': 7.0, 'tools': 7.0}, {'goal': 8.0, 'tools': 8.0}),
        ('known_below_threshold', {'goal': 7.0, 'tools': 7.0}, {'goal': 6.0, 'tools': 8.0}),
        ('missing_expected_metric', {'goal': 7.0, 'tools': 7.0}, {'goal': 8.0}),
        ('no_matching_metric', {'goal': 7.0, 'tools': 7.0}, {'other': 8.0}),
    ]
    score_results = [
        {'case': name, 'expected': expected, 'actual': actual,
         'upstream_result': score_check(None, expected, actual),
         'missing_expected_metrics': sorted(set(expected) - set(actual))}
        for name, expected, actual in cases
    ]

    original_env = os.environ.get('AGNO_TELEMETRY')
    module_name = 'agno.api.evals'
    original_module = sys.modules.get(module_name)
    queued = []
    fake_module = ModuleType(module_name)
    fake_module.EvalRunCreate = lambda **fields: fields
    fake_module.create_eval_run_telemetry = lambda *, eval_run: queued.append(eval_run)
    try:
        os.environ['AGNO_TELEMETRY'] = 'false'
        sys.modules[module_name] = fake_module
        agent = SimpleNamespace(telemetry=True)
        set_telemetry = load_function('agno-init', 'set_telemetry', {'getenv': os.getenv})
        set_telemetry(agent)
        log_eval = load_function('agno-evalutils', 'log_eval_telemetry', {'log_debug': lambda _: None})
        log_eval(run_id='synthetic-run', eval_type='synthetic-reliability', get_data=lambda: {'synthetic': True})
        agno_result = {
            'environment': {'AGNO_TELEMETRY': 'false'},
            'synthetic_agent_initial_telemetry': True,
            'agent_after_set_telemetry': agent.telemetry,
            'direct_eval_helper_stub_calls': len(queued),
            'recorded_stub_payloads': queued,
            'network_requests': 0,
            'boundary': 'Exact isolated helper call; no full evaluator, Agent, package, network or provider execution.',
        }
    finally:
        if original_env is None:
            os.environ.pop('AGNO_TELEMETRY', None)
        else:
            os.environ['AGNO_TELEMETRY'] = original_env
        if original_module is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = original_module

    result = {
        'synthetic': True,
        'executed_at': datetime.now(timezone.utc).isoformat(),
        'python_version': platform.python_version(),
        'method': 'Hash-check fetched sources, extract only named function ASTs without rewriting their bodies, run with synthetic values and an in-process API recorder.',
        'sources': [ledger[key] for key in pins],
        'crew_score_predicate': score_results,
        'agno_telemetry_helpers': agno_result,
        'limitations': [
            'No complete framework or evaluator was installed or executed.',
            'No model, tool, paid API, GPU or network request was executed.',
            'The predicate outputs are not measured agent quality or production privacy evidence.',
        ],
    }
    if args.verify:
        for section in ('crew_score_predicate', 'agno_telemetry_helpers'):
            if result[section] != fixture[section]:
                raise ValueError('Synthetic observation mismatch: ' + section)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
