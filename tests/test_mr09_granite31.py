"""Synthetic guard tests and real committed-record integrity; no GPU or downloads."""
import hashlib
import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/mr09_granite31_measure.py"
SPEC = importlib.util.spec_from_file_location("mr09_granite31", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SupplementalProtocolGuards(unittest.TestCase):
    def test_existing_artifacts_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            marker = root / "existing-file"
            marker.write_text("synthetic fixture")
            with patch.object(MODULE.urllib.request, "urlopen") as request:
                with self.assertRaises(ValueError):
                    MODULE.prepare(root)
                request.assert_not_called()
            self.assertEqual(marker.read_text(), "synthetic fixture")

    def test_repository_is_not_a_model_download_destination(self):
        with patch.object(MODULE.urllib.request, "urlopen") as request:
            with self.assertRaises(ValueError):
                MODULE.prepare(SCRIPT.parents[1])
            request.assert_not_called()

    def test_out_of_scope_cells_rejected_before_preflight(self):
        for options in (("--cell", "M1"), ("--prompt-tokens", "2048"),
                        ("--active-sequences", "2"), ("--cache", "int4"),
                        ("--repetition", "4"), ("--decode-tokens", "64")):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / "result.json"
                proc = subprocess.run([sys.executable, str(SCRIPT),
                    "--model-dir", str(Path(temp) / "model"),
                    "--output", str(output), *options], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 2)
                self.assertNotIn("Traceback", proc.stderr)
                self.assertFalse(output.exists())

    def test_existing_result_is_preserved_before_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "result.json"
            output.write_text("synthetic existing observation")
            proc = subprocess.run([sys.executable, str(SCRIPT),
                "--model-dir", str(Path(temp) / "model"), "--output", str(output)],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(output.read_text(), "synthetic existing observation")


class CommittedGM1Integrity(unittest.TestCase):
    """Validate recorded evidence without executing or manufacturing observations."""
    def test_real_cohort_pins_guards_artifacts_and_summary(self):
        repo = SCRIPT.parents[1]
        directory = repo / "research/market/measurements/granite31-2026-10-18"
        sys.path.insert(0, str(repo / "scripts"))
        try:
            from mr09_summarize import summarize
            summary = summarize(directory)
        finally:
            sys.path.pop(0)
        self.assertEqual(summary, json.loads((directory / "mr09-results-summary.json").read_text()))
        self.assertEqual(summary["run_count"], 3)
        self.assertEqual(summary["status_counts"], {"success": 3})
        self.assertEqual(summary["comparable_competitor_error_pairs"], 0)
        protocol = repo / "research/market/measurements/mr09-granite31-protocol-2026-10-16.md"
        artifact_ledger = json.loads((directory / "mr09-granite31-artifacts.json").read_text())
        weight = next(a for a in artifact_ledger["artifacts"] if a["file"] == "model.safetensors")
        self.assertEqual(weight["bytes"], 2669283096)
        self.assertEqual(weight["sha256"], "ac02591061f1344027a7e7b11dbb4143f75f166c47dc09b742f5de3ab1dde1d1")
        for rep in (1, 2, 3):
            run = json.loads((directory / f"mr09-GM1-r{rep}.json").read_text())
            self.assertEqual(run["script_sha256"], hashlib.sha256(SCRIPT.read_bytes()).hexdigest())
            self.assertEqual(run["protocol_sha256"], hashlib.sha256(protocol.read_bytes()).hexdigest())
            self.assertEqual(run["dense_instrument_source_sha256"], hashlib.sha256((repo / "scripts/mr09_measure.py").read_bytes()).hexdigest())
            self.assertEqual(run["model_id"], MODULE.MODEL_ID)
            self.assertEqual(run["revision"], MODULE.REVISION)
            self.assertEqual(run["cell"], "GM1")
            self.assertEqual(run["repetition"], rep)
            self.assertTrue(all(run["fresh_preflight"]["guards"].values()))
            self.assertEqual(run["hardware"]["process_allocator_limit_bytes"], 3 * 2**30)
            self.assertEqual(run["actual_tokens"]["prompt_per_sequence"], 256)
            self.assertEqual(run["actual_tokens"]["cache_tokens_per_sequence"], 288)
            self.assertEqual(run["actual_tokens"]["active_sequences"], 1)
            self.assertEqual(run["configuration"]["kv_cache"], "bf16")
            self.assertEqual(run["native_kv_prefill_payload"]["measured_bytes"], 12582912)
            self.assertEqual(run["native_kv_steady_payload_bytes"], 14155776)
            self.assertTrue(all(p["peak_reserved_bytes"] <= 3 * 2**30 for p in run["phases"]))
            self.assertNotIn("uuid=", run["hardware"]["properties"])
        self.assertFalse(json.loads((directory / "cleanup.json").read_text())["target_exists"])


if __name__ == "__main__":
    unittest.main()
