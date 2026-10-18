"""Synthetic comparator-input mutations; no estimator or GPU execution."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/mr09_compare_estimators.py"
SPEC = importlib.util.spec_from_file_location("mr09_comparator_inputs", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
MEASUREMENTS = ROOT / "research/market/measurements"
OUTPUTS = MEASUREMENTS / "estimator-comparison-2026-10-18"


class ComparatorInputTests(unittest.TestCase):
    def setUp(self):
        self.raw = (MEASUREMENTS / "mr09-D1-r1.json").read_bytes()
        self.run = json.loads(self.raw)
        self.plan = json.loads((OUTPUTS / "llmfit-256-fp16.json").read_bytes())

    def test_duplicate_keys_are_rejected_at_every_depth(self):
        for raw in (
            '{"status":"failure","status":"success"}',
            '{"status":"success","status":"success"}',
            '{"rows":[{"actual_tokens":{"active_sequences":2,"active_sequences":1}}]}',
            '{"status":"failure","\\u0073tatus":"success"}',
        ):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "duplicate JSON"):
                MODULE.input_json(raw)

    def test_nonfinite_literals_and_overflow_are_rejected_even_if_unused(self):
        for value in ("NaN", "Infinity", "-Infinity", "1e400", "-1e400"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "non-finite|finite numeric"):
                MODULE.input_json('{"unused":{"number":' + value + '}}')
        self.assertEqual(MODULE.input_json('{"flag":true,"value":1.5}'),
                         {"flag": True, "value": 1.5})

    def test_sequence_count_does_not_accept_boolean_or_float_aliases(self):
        for value in (True, 1.0, "1", None, 0, -1, 2):
            run = copy.deepcopy(self.run)
            run["actual_tokens"]["active_sequences"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.compare_payload(self.plan, run, "prefill")

    def test_configured_sequence_count_matches_observed_native_count(self):
        for value in (True, 1.0, "1", None, 0, -1, 2):
            run = copy.deepcopy(self.run)
            run["configuration"]["active_sequences"] = value
            for point in ("prefill", "terminal"):
                with self.subTest(value=value, point=point), self.assertRaises(ValueError):
                    MODULE.measured_payload(run, point)

    def assert_preflight_rejected(self, mutate, message, *, optimized=False):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            records = root / "measurements"
            records.mkdir()
            for cell in ("D1", "D2"):
                for rep in (1, 2, 3):
                    name = f"mr09-{cell}-r{rep}.json"
                    (records / name).write_bytes((MEASUREMENTS / name).read_bytes())
            mutate(records)
            originals = {p.name: p.read_bytes() for p in records.iterdir()}
            output = root / "new-comparison"
            argv = [str(SCRIPT), "--artifact-dir", str(root / "absent-artifacts"),
                    "--measurements", str(records), "--output-dir", str(output)]
            with patch.object(sys, "argv", argv), \
                    patch.object(MODULE.subprocess, "run") as run_tool, \
                    patch.object(MODULE.subprocess, "check_output") as check_tool:
                with self.assertRaisesRegex(ValueError, message):
                    MODULE.main()
                run_tool.assert_not_called()
                check_tool.assert_not_called()
            if optimized:
                result = subprocess.run([sys.executable, "-O", *argv], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ValueError: " + message, result.stderr)
            self.assertFalse(output.exists())
            self.assertEqual(originals, {p.name: p.read_bytes() for p in records.iterdir()})

    @staticmethod
    def mutate_last_record(records, group, field, value):
        path = records / "mr09-D2-r3.json"
        run = json.loads(path.read_bytes())
        target = run if group is None else run[group]
        target[field] = value
        path.write_text(json.dumps(run), encoding="utf-8")

    def test_retained_filename_binds_exact_cell_and_repetition(self):
        for field, values in (("cell", ("D1", "D3", 2, True, None)),
                              ("repetition", (1, 2, 3.0, True, "3", None))):
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_preflight_rejected(
                        lambda records: self.mutate_last_record(records, None, field, value),
                        "measurement identity differs", optimized=True)

    def test_copied_observation_cannot_acquire_six_sample_identities(self):
        def duplicate(records):
            for path in records.iterdir():
                path.write_bytes(self.raw)
        self.assert_preflight_rejected(duplicate, "measurement identity differs", optimized=True)

    def test_fixed_cell_contexts_reject_unsupported_or_swapped_plan_lengths(self):
        for field, values in (("prompt_per_sequence", (1024, 256, 2080)),
                              ("cache_tokens_per_sequence", (1024, 288, 2048))):
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_preflight_rejected(
                        lambda records: self.mutate_last_record(records, "actual_tokens", field, value),
                        "observed context differs", optimized=True)

    def test_declared_workload_counts_and_concurrency_fail_before_execution(self):
        fields = (("configuration", "prompt_tokens_per_sequence", (256, 2048.0, True)),
                  ("configuration", "decode_forwards_per_sequence", (0, 64, 32.0, True)),
                  ("actual_tokens", "decode_forwards_per_sequence", (0, 64, 32.0, True)),
                  ("configuration", "active_sequences", (2, 1.0, True)))
        for group, field, values in fields:
            for value in values:
                message = ("only single-sequence" if field == "active_sequences"
                           else "declared context counts differ")
                with self.subTest(group=group, field=field, value=value):
                    self.assert_preflight_rejected(
                        lambda records: self.mutate_last_record(records, group, field, value),
                        message, optimized=True)

    def test_geometry_requires_integers(self):
        for field in ("layers", "kv_heads", "head_dim"):
            run = copy.deepcopy(self.run)
            run["model_geometry"][field] = float(run["model_geometry"][field])
            with self.subTest(field=field), self.assertRaises(ValueError):
                MODULE.compare_payload(self.plan, run, "prefill")

    def test_contexts_require_positive_integers_even_when_equal(self):
        for point, field in (("prefill", "prompt_per_sequence"),
                             ("terminal", "cache_tokens_per_sequence")):
            for value in (True, 256.0, "256", None, 0, -1):
                plan, run = copy.deepcopy(self.plan), copy.deepcopy(self.run)
                plan["context"] = run["actual_tokens"][field] = value
                with self.subTest(point=point, value=value), self.assertRaises(ValueError):
                    MODULE.compare_payload(plan, run, point)
        self.plan["context"] = 256.0
        with self.assertRaises(ValueError):
            MODULE.compare_payload(self.plan, self.run, "prefill")

    def test_all_current_measurements_retain_hashes_and_bounded_pairs(self):
        records = MODULE.read_measurements(MEASUREMENTS)
        self.assertEqual(len(records), 6)
        for name, (run, checksum) in records.items():
            self.assertEqual(checksum, hashlib.sha256((MEASUREMENTS / name).read_bytes()).hexdigest())
            for point in ("prefill", "terminal"):
                context, _ = MODULE.measured_payload(run, point)
                plan = MODULE.input_json((OUTPUTS / f"llmfit-{context}-fp16.json").read_text())
                pair = MODULE.compare_payload(plan, run, point)
                self.assertEqual(pair["signed_bytes"], 0)
                self.assertIn("no whole-runtime pair", pair["scope"])

    def test_invalid_last_measurement_prevents_all_external_execution_and_output(self):
        for invalid in ("duplicate", "nonfinite", "boolean"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                records = root / "measurements"
                records.mkdir()
                for cell in ("D1", "D2"):
                    for rep in (1, 2, 3):
                        name = f"mr09-{cell}-r{rep}.json"
                        (records / name).write_bytes((MEASUREMENTS / name).read_bytes())
                target = records / "mr09-D2-r3.json"
                text = target.read_text()
                if invalid == "duplicate":
                    text = text.replace('"actual_tokens": {',
                                        '"actual_tokens": {"active_sequences": 2,', 1)
                elif invalid == "nonfinite":
                    text = '{"synthetic_unused":1e400,' + text.lstrip()[1:]
                else:
                    run = json.loads(text)
                    run["actual_tokens"]["active_sequences"] = True
                    text = json.dumps(run)
                target.write_text(text)
                originals = {p.name: p.read_bytes() for p in records.iterdir()}
                output = root / "new-comparison"
                argv = [str(SCRIPT), "--artifact-dir", str(root / "absent-artifacts"),
                        "--measurements", str(records), "--output-dir", str(output)]
                with patch.object(sys, "argv", argv), \
                        patch.object(MODULE.subprocess, "run") as run_tool, \
                        patch.object(MODULE.subprocess, "check_output") as check_tool:
                    with self.assertRaises(ValueError):
                        MODULE.main()
                    run_tool.assert_not_called()
                    check_tool.assert_not_called()
                self.assertFalse(output.exists())
                self.assertEqual(originals, {p.name: p.read_bytes() for p in records.iterdir()})

    def test_raw_input_rejection_survives_optimized_python(self):
        code = (
            "import runpy,sys; m=runpy.run_path(sys.argv[1]); "
            "m['input_json']('{\"value\":1,\"value\":2}')"
        )
        result = subprocess.run([sys.executable, "-O", "-c", code, str(SCRIPT)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate JSON object key", result.stderr)


if __name__ == "__main__":
    unittest.main()
