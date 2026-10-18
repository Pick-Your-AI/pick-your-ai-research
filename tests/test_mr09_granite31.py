"""Synthetic guard tests and real committed-record integrity; no GPU or downloads."""
import contextlib
import hashlib
import io
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
    def exercise_capacity_screen(self, screen, *, prepare, reject):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model, output = root / "model", root / "result.json"
            preflight = root / "granite31-preflight-1.json"
            raw = json.dumps(screen)

            def run(argv, **kwargs):
                self.assertEqual(Path(argv[1]).name, "mr09_preflight.py")
                self.assertTrue(kwargs["check"])
                preflight.write_text(raw, encoding="utf-8")
                return subprocess.CompletedProcess(argv, 0)

            argv = [str(SCRIPT), "--model-dir", str(model), "--output", str(output)]
            if prepare:
                argv.append("--prepare")
            with (patch.object(sys, "argv", argv),
                  patch.object(MODULE.subprocess, "run", side_effect=run) as screen_call,
                  patch.object(MODULE, "prepare", return_value={"classification": "synthetic fixture"}) as download,
                  patch.object(MODULE, "measurement", return_value={"status": "success", "classification": "synthetic fixture"}) as measurement,
                  contextlib.redirect_stdout(io.StringIO())):
                if reject:
                    with self.assertRaisesRegex(RuntimeError, "unchanged spare-capacity guards failed; no download/run"):
                        MODULE.main()
                    download.assert_not_called()
                    measurement.assert_not_called()
                    self.assertFalse(output.exists())
                else:
                    self.assertEqual(MODULE.main(), 0)
                    self.assertEqual(download.call_count, int(prepare))
                    self.assertEqual(measurement.call_count, int(not prepare))
                    self.assertEqual(json.loads(output.read_text())["fresh_preflight"], screen)
            self.assertEqual(screen_call.call_count, 1)
            self.assertEqual(preflight.read_text(), raw)
            self.assertFalse(model.exists(), "no real download or model execution is part of this test")

    def test_capacity_guards_reject_malformed_shapes_and_truthy_aliases_before_either_action(self):
        good = {"nvidia_smi_free_mib": True, "available_host_ram_bytes": True,
                "temporary_volume_free_bytes": True}
        invalid = [{}, {"guards": {}}, {"guards": {"unrelated": True}},
                   {"guards": {**good, "unexpected": True}}, None, [], True, "true", 1]
        invalid.extend({"guards": value} for value in (None, [], True, "true"))
        for key in good:
            invalid.append({"guards": {name: value for name, value in good.items() if name != key}})
            invalid.extend({"guards": {**good, key: value}} for value in (1, 1.0, "false", [True], False, None))
        for prepare in (False, True):
            for screen in invalid:
                with self.subTest(prepare=prepare, screen=screen):
                    self.exercise_capacity_screen(screen, prepare=prepare, reject=True)

    def test_complete_boolean_capacity_screen_preserves_prepare_and_measurement_recovery(self):
        screen = {"guards": {"nvidia_smi_free_mib": True, "available_host_ram_bytes": True,
                             "temporary_volume_free_bytes": True}}
        for prepare in (False, True):
            with self.subTest(prepare=prepare):
                self.exercise_capacity_screen(screen, prepare=prepare, reject=False)

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
        executed = directory / "mr09_granite31_measure.executed.py"
        executed_sha = hashlib.sha256(executed.read_bytes()).hexdigest()
        self.assertEqual(executed_sha, "338ebb6a197712b655c5c2f69d6b1dbc0a51265455773b58c32ea2bc87c13974")
        self.assertNotEqual(hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), executed_sha)
        for rep in (1, 2, 3):
            run = json.loads((directory / f"mr09-GM1-r{rep}.json").read_text())
            self.assertEqual(run["script_sha256"], executed_sha)
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
