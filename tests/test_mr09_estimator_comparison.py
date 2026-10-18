"""Offline eligibility regression fixtures and integrity checks, no estimators/GPU."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/mr09_compare_estimators.py"
SPEC = importlib.util.spec_from_file_location("mr09_comparison", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
DIRECTORY = ROOT / "research/market/measurements/estimator-comparison-2026-10-18"

class EligibilityTests(unittest.TestCase):
    """Mutated/small fixtures here are synthetic, never research observations."""
    def setUp(self):
        self.plan = json.loads((DIRECTORY / "llmfit-256-fp16.json").read_text())
        self.run = json.loads((ROOT / "research/market/measurements/mr09-D1-r1.json").read_text())

    def test_only_kv_gib_field_is_converted(self):
        self.assertEqual(MODULE.kv_component(self.plan), 5898240)
        altered = copy.deepcopy(self.plan)
        altered["minimum"]["vram_gb"] = 99999
        altered["disk_size_gb"] = 99999
        self.assertEqual(MODULE.compare_payload(altered, self.run, "prefill")["signed_bytes"], 0)

    def test_unmatched_context_rejected(self):
        self.plan["context"] = 288
        with self.assertRaises(ValueError):
            MODULE.compare_payload(self.plan, self.run, "prefill")

    def test_concurrency_and_quanto_not_silently_adapted(self):
        for cache, sequences in (("bf16",2),("int4",1)):
            altered = copy.deepcopy(self.run)
            altered["configuration"]["kv_cache"] = cache
            altered["actual_tokens"]["active_sequences"] = sequences
            with self.subTest(cache=cache, sequences=sequences), self.assertRaises(ValueError):
                MODULE.compare_payload(self.plan, altered, "prefill")

    def test_wrong_geometry_revision_or_failure_rejected(self):
        for key, value in (("revision","synthetic-wrong-revision"),("status","OOM_prefill")):
            altered = copy.deepcopy(self.run)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                MODULE.compare_payload(self.plan, altered, "prefill")
        self.run["model_geometry"]["kv_heads"] = 9
        with self.assertRaises(ValueError):
            MODULE.compare_payload(self.plan, self.run, "prefill")

    def test_invalid_payload_has_no_relative_error(self):
        self.run["native_kv_prefill_payload"]["measured_bytes"] = 0
        with self.assertRaises(ValueError):
            MODULE.compare_payload(self.plan, self.run, "prefill")
        for invalid in (0,-1,float("nan"),float("inf")):
            self.plan["kv_alternatives"][0]["kv_cache_gb"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                MODULE.kv_component(self.plan)

    def test_nonzero_error_uses_measured_denominator(self):
        self.run["native_kv_prefill_payload"]["measured_bytes"] = 2949120
        result = MODULE.compare_payload(self.plan, self.run, "prefill")
        self.assertEqual(result["signed_bytes"], 2949120)
        self.assertEqual(result["absolute_bytes"], 2949120)
        self.assertEqual(result["signed_relative_percent"], 100)

    def test_existing_output_preserved_before_external_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "existing"
            output.mkdir()
            marker = output / "marker"
            marker.write_text("synthetic existing result")
            proc = subprocess.run([sys.executable,str(SCRIPT),"--artifact-dir",str(Path(temp)/"absent"),"--output-dir",str(output)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2)
            self.assertIn("fresh output",proc.stderr)
            self.assertEqual(marker.read_text(),"synthetic existing result")

class RecordedComparisonIntegrity(unittest.TestCase):
    def test_committed_outputs_and_pairs_recompute(self):
        ledger = json.loads((DIRECTORY / "comparison.json").read_text())
        self.assertEqual(ledger["script_sha256"], hashlib.sha256(SCRIPT.read_bytes()).hexdigest())
        self.assertEqual(ledger["whole_runtime_pairs"],0)
        self.assertIsNone(ledger["approved_tolerance"])
        self.assertEqual(ledger["component_pair_count"],12)
        self.assertEqual(ledger["independent_workload_cells"],2)
        self.assertEqual(len(ledger["estimator_executions"]),6)
        for output in ledger["estimator_executions"] + [ledger["modelfit"]]:
            self.assertEqual(output["sha256"],hashlib.sha256((DIRECTORY/output["file"]).read_bytes()).hexdigest())
        identities = set()
        for pair in ledger["component_pairs"]:
            path = ROOT / "research/market/measurements" / pair["measurement_file"]
            self.assertEqual(pair["measurement_sha256"],hashlib.sha256(path.read_bytes()).hexdigest())
            run = json.loads(path.read_text())
            plan = json.loads((DIRECTORY/pair["estimator_file"]).read_text())
            computed = MODULE.compare_payload(plan,run,pair["point"])
            for key, value in computed.items():
                self.assertEqual(pair[key],value)
            identities.add((pair["measurement_file"],pair["point"]))
        self.assertEqual(len(identities),12)
        model = json.loads((DIRECTORY/"modelfit-audit.json").read_text())
        self.assertEqual(model["exactModelMatches"],[])
        self.assertEqual(model["datasetRecords"],156)

if __name__ == "__main__":
    unittest.main()
