"""Synthetic exact-number regressions; no estimator, GPU, or network execution."""

import contextlib
import copy
from decimal import Decimal, FloatOperation, InvalidOperation, localcontext
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/mr09_compare_estimators.py"
SPEC = importlib.util.spec_from_file_location("mr09_payload_precision", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
MEASUREMENTS = ROOT / "research/market/measurements"
PLANS = MEASUREMENTS / "estimator-comparison-2026-10-18"
MARKER = "synthetic numeric token; never research evidence"


def replace_numeric_token(document, container, key, token):
    altered = copy.deepcopy(document)
    target = altered
    for item in container:
        target = target[item]
    target[key] = MARKER
    text = json.dumps(altered)
    return text.replace(json.dumps(MARKER), token)


class PayloadPrecisionTests(unittest.TestCase):
    def setUp(self):
        self.run = json.loads((MEASUREMENTS / "mr09-D1-r1.json").read_text())
        self.plans = {
            point: json.loads((PLANS / f"llmfit-{context}-fp16.json").read_text())
            for point, context in (("prefill", 256), ("terminal", 288))
        }

    def observed(self, token, point="prefill"):
        container, key = ((["native_kv_prefill_payload"], "measured_bytes")
                          if point == "prefill" else ([], "native_kv_steady_payload_bytes"))
        return MODULE.input_json(replace_numeric_token(self.run, container, key, token))

    def plan(self, token):
        return MODULE.input_json(replace_numeric_token(
            self.plans["prefill"], ["kv_alternatives", 0], "kv_cache_gb", token))

    def test_original_fractional_bytes_cannot_become_integral_observations(self):
        for point in ("prefill", "terminal"):
            for token in ("5898240.0000000001", "5898240.000000000000000000000001"):
                with self.subTest(point=point, token=token), self.assertRaisesRegex(
                        ValueError, "integral payload bytes"):
                    MODULE.compare_payload(self.plans[point], self.observed(token, point), point)

    def test_wide_integral_decimal_and_exponent_spellings_keep_every_byte(self):
        values = {
            "5898240.0": 5898240,
            "5.898240e6": 5898240,
            "9007199254740993.0": 9007199254740993,
            "9.007199254740993e15": 9007199254740993,
            "100000000000000000000001.0": 100000000000000000000001,
            "1e23": 10**23,
        }
        for point in ("prefill", "terminal"):
            estimate = MODULE.kv_component(self.plans[point])
            for token, expected in values.items():
                with self.subTest(point=point, token=token):
                    result = MODULE.compare_payload(
                        self.plans[point], self.observed(token, point), point)
                    self.assertIs(type(result["measured_payload_bytes"]), int)
                    self.assertEqual(result["measured_payload_bytes"], expected)
                    self.assertEqual(result["signed_bytes"], estimate - expected)
                    self.assertEqual(result["absolute_bytes"], abs(estimate - expected))

    def test_fractional_gib_cannot_round_to_a_whole_byte_during_scaling(self):
        for token in ("8388608.1", "0.005493164062500000000000000001"):
            with self.subTest(token=token), self.assertRaisesRegex(
                    ValueError, "integral payload bytes"):
                MODULE.kv_component(self.plan(token))

    def test_gib_scaling_preserves_low_bits_beyond_binary64_precision(self):
        values = {
            "0.000000000931322574615478515625": 1,
            "0.0054931640625": 5898240,
            "8388608.000000000931322574615478515625": 2**53 + 1,
            "8.388608000000000931322574615478515625e6": 2**53 + 1,
            "1e23": 10**23 * MODULE.GIB,
        }
        for token, expected in values.items():
            with self.subTest(token=token):
                self.assertEqual(MODULE.kv_component(self.plan(token)), expected)

    def test_one_byte_error_survives_wide_exact_inputs(self):
        result = MODULE.compare_payload(
            self.plan("8388608.0"), self.observed("9007199254740993.0"), "prefill")
        self.assertEqual(result["estimated_payload_bytes"], 2**53)
        self.assertEqual(result["measured_payload_bytes"], 2**53 + 1)
        self.assertEqual(result["signed_bytes"], -1)
        self.assertEqual(result["absolute_bytes"], 1)
        self.assertLess(result["signed_relative_percent"], 0)

    def test_decimal_context_cannot_round_away_a_fraction_or_low_bit(self):
        with localcontext() as context:
            context.prec = 3
            context.Emax = 9
            context.Emin = -9
            context.traps[FloatOperation] = True
            self.assertEqual(MODULE.kv_component(self.plan(
                "8388608.000000000931322574615478515625")), 2**53 + 1)
            with self.assertRaises(ValueError):
                MODULE.kv_component(self.plan("0.005493164062500000000000000001"))
            self.assertEqual(MODULE.measured_payload(
                self.observed("100000000000000000000001.0"), "prefill")[1],
                100000000000000000000001)

    def test_nonfinite_boolean_zero_and_tiny_values_still_have_no_byte_result(self):
        for token in ("true", "false", "null", '"1"', "0", "0.0", "-0.0",
                      "0e-1000000000", "-1.0", "1e-1000000000", "-1e-1000000000",
                      "1e-999999999999999999999999999999999999"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                MODULE.measured_payload(self.observed(token), "prefill")
            with self.subTest(gib_token=token), self.assertRaises(ValueError):
                MODULE.kv_component(self.plan(token))
        for token in ("NaN", "Infinity", "-Infinity", "1e400", "-1e400",
                      "1e999999999999999999999999999999999999",
                      "-1e999999999999999999999999999999999999"):
            with self.subTest(nonfinite=token), self.assertRaises(ValueError):
                MODULE.input_json('{"unused":' + token + '}')

    def test_nontrapping_decimal_context_cannot_admit_nonfinite_metadata(self):
        with localcontext() as context:
            context.prec = 3
            context.traps[FloatOperation] = True
            context.traps[InvalidOperation] = False
            for token in ("1e-999999999999999999999999999999999999",
                          "-1e-999999999999999999999999999999999999",
                          "0e-999999999999999999999999999999999999",
                          "-0e-999999999999999999999999999999999999",
                          "0e999999999999999999999999999999999999",
                          "-0e999999999999999999999999999999999999"):
                with self.subTest(token=token), self.assertRaisesRegex(
                        ValueError, "exact decimal range"):
                    MODULE.input_json('{"unused":' + token + '}')
            for token in ("5898240.0", "9007199254740993.0", "1e23",
                          "0.12345678901234567890123456789", "-0.0"):
                with self.subTest(finite_control=token):
                    number = MODULE.input_json('{"unused":' + token + '}')["unused"]
                    self.assertIs(type(number), Decimal)
                    self.assertTrue(number.is_finite())
                    self.assertEqual(number, Decimal(token))
            ordinary = MODULE.input_json('{"ratio":1.5}', exact_numbers=False)
            self.assertIs(type(ordinary["ratio"]), float)
            self.assertEqual(ordinary["ratio"], 1.5)

    def test_fractional_last_input_stops_the_real_cli_before_artifact_access(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                records = root / "measurements"
                records.mkdir()
                for cell in ("D1", "D2"):
                    for repetition in (1, 2, 3):
                        name = f"mr09-{cell}-r{repetition}.json"
                        (records / name).write_bytes((MEASUREMENTS / name).read_bytes())
                last = records / "mr09-D2-r3.json"
                original = json.loads(last.read_text())
                last.write_text(replace_numeric_token(
                    original, ["native_kv_prefill_payload"], "measured_bytes",
                    "47185920.0000000001"), encoding="utf-8")
                before = {path.name: path.read_bytes() for path in records.iterdir()}
                output = root / "new-comparison"
                command = [sys.executable, *(["-O"] if optimized else []), str(SCRIPT),
                           "--artifact-dir", str(root / "absent-artifacts"),
                           "--measurements", str(records), "--output-dir", str(output)]
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("integral payload bytes", result.stderr)
                self.assertNotIn("FileNotFoundError", result.stderr)
                self.assertFalse(output.exists())
                self.assertEqual(before, {path.name: path.read_bytes() for path in records.iterdir()})

    def test_main_preserves_exact_plan_numbers_and_unrelated_audit_metadata(self):
        """Only the external processes are synthetic; run the complete CLI logic."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifacts = root / "synthetic-artifacts"
            artifacts.mkdir()
            pins = {}
            catalog = [{"name": MODULE.MODEL, "parameters_raw": 135000000.0,
                        "num_hidden_layers": 30, "num_key_value_heads": 3,
                        "head_dim": 64, "format": "synthetic", "quantization": "BF16"}]
            for name in MODULE.PINS:
                path = artifacts / name
                path.parent.mkdir(parents=True, exist_ok=True)
                data = json.dumps(catalog) if name == "hf_models.json" else "synthetic artifact"
                path.write_text(data, encoding="utf-8")
                pins[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            captured = {}

            def external(command, **kwargs):
                if command[0] == str(artifacts / "llmfit.exe"):
                    context = int(command[command.index("--context") + 1])
                    precision = command[command.index("--kv-quant") + 1]
                    name = f"llmfit-{context}-{precision}.json"
                    plan = json.loads((PLANS / name).read_text())
                    plan["synthetic_metadata"] = {"ratio": MARKER, "text": "123.4"}
                    raw = json.dumps(plan, indent=2).replace(
                        json.dumps(MARKER), "0.12345678901234567890123456789") + "\n"
                    captured[name] = raw
                    return SimpleNamespace(returncode=0, stdout=raw, stderr="")
                return SimpleNamespace(returncode=0, stdout=json.dumps(
                    {"exactModelMatches": [], "ratio": 1.5, "synthetic": True}), stderr="")

            output = root / "new-comparison"
            argv = [str(SCRIPT), "--artifact-dir", str(artifacts), "--measurements",
                    str(MEASUREMENTS), "--output-dir", str(output)]
            originals = {path.name: path.read_bytes() for path in MEASUREMENTS.glob("mr09-D[12]-r*.json")}
            with patch.object(MODULE, "PINS", pins), patch.object(sys, "argv", argv), \
                    patch.object(MODULE.subprocess, "run", side_effect=external) as run_tool, \
                    patch.object(MODULE.subprocess, "check_output", return_value="synthetic 1.0\n"), \
                    contextlib.redirect_stdout(io.StringIO()):
                MODULE.main()
            self.assertEqual(run_tool.call_count, 7)
            self.assertEqual(len(captured), 6)
            for name, raw in captured.items():
                self.assertEqual((output / name).read_text(), raw)
                parsed = json.loads((output / name).read_text(), parse_float=Decimal)
                self.assertEqual(parsed["synthetic_metadata"]["ratio"],
                                 Decimal("0.12345678901234567890123456789"))
            ledger = json.loads((output / "comparison.json").read_text())
            self.assertEqual(ledger["component_pair_count"], 12)
            self.assertTrue(all(pair["signed_bytes"] == 0 for pair in ledger["component_pairs"]))
            self.assertIs(type(ledger["catalog_geometry"]["parameters_raw"]), float)
            self.assertIs(type(json.loads((output / "modelfit-audit.json").read_text())["ratio"]), float)
            self.assertEqual(originals, {path.name: path.read_bytes() for path in MEASUREMENTS.glob("mr09-D[12]-r*.json")})

    def test_main_preserves_legacy_driver_capacity_number_spellings(self):
        """Recorded capacity is audit metadata, outside exact payload arithmetic."""
        for token in ("17094475776", "17094475776.0", "1.7094475776e10",
                      "17094475776.125", "9007199254740993.0", "1e23",
                      "-0.0", "1e-1000000000", '"17094475776"'):
            with self.subTest(token=token), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                records = root / "measurements"
                records.mkdir()
                for path in MEASUREMENTS.glob("mr09-D[12]-r*.json"):
                    (records / path.name).write_bytes(path.read_bytes())
                first = records / "mr09-D1-r1.json"
                first.write_text(replace_numeric_token(
                    self.run, ["hardware"], "driver_total_bytes", token), encoding="utf-8")
                before = {path.name: path.read_bytes() for path in records.iterdir()}
                artifacts = root / "synthetic-artifacts"
                artifacts.mkdir()
                catalog = [{"name": MODULE.MODEL, "parameters_raw": 135000000,
                            "num_hidden_layers": 30, "num_key_value_heads": 3,
                            "head_dim": 64, "format": "synthetic", "quantization": "BF16"}]
                pins = {}
                for name in MODULE.PINS:
                    path = artifacts / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(catalog) if name == "hf_models.json"
                                    else "synthetic artifact", encoding="utf-8")
                    pins[name] = hashlib.sha256(path.read_bytes()).hexdigest()
                node_arguments = []

                def external(command, **kwargs):
                    if command[0] == str(artifacts / "llmfit.exe"):
                        context = command[command.index("--context") + 1]
                        precision = command[command.index("--kv-quant") + 1]
                        raw = (PLANS / f"llmfit-{context}-{precision}.json").read_text()
                    else:
                        node_arguments.append(command[-1])
                        raw = '{"exactModelMatches":[]}'
                    return SimpleNamespace(returncode=0, stdout=raw, stderr="")

                output = root / "new-comparison"
                argv = [str(SCRIPT), "--artifact-dir", str(artifacts), "--measurements",
                        str(records), "--output-dir", str(output)]
                with patch.object(MODULE, "PINS", pins), patch.object(sys, "argv", argv), \
                        patch.object(MODULE.subprocess, "run", side_effect=external) as run_tool, \
                        patch.object(MODULE.subprocess, "check_output", return_value="synthetic 1.0\n"), \
                        contextlib.redirect_stdout(io.StringIO()), localcontext() as context:
                    context.prec = 3
                    context.traps[FloatOperation] = True
                    context.traps[InvalidOperation] = False
                    if token.startswith('"'):
                        with self.assertRaises(TypeError):
                            MODULE.main()
                    else:
                        MODULE.main()
                self.assertEqual(before, {path.name: path.read_bytes() for path in records.iterdir()})
                if token.startswith('"'):
                    self.assertEqual(node_arguments, [])
                    self.assertFalse((output / "comparison.json").exists())
                    continue
                self.assertEqual(run_tool.call_count, 7)
                self.assertEqual(node_arguments, [str(json.loads(token) / 1e9)])
                ledger = json.loads((output / "comparison.json").read_text())
                self.assertEqual(ledger["component_pair_count"], 12)
                self.assertTrue(all(pair["signed_bytes"] == 0 for pair in ledger["component_pairs"]))


if __name__ == "__main__":
    unittest.main()
