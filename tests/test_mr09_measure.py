"""Synthetic arithmetic/failure fixtures only; these are not GPU observations."""

import importlib.util
import contextlib
import copy
import hashlib
import io
import json
import re
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("mr09_measure", Path(__file__).resolve().parents[1] / "scripts/mr09_measure.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SUMMARY_SPEC = importlib.util.spec_from_file_location("mr09_summarize", Path(__file__).resolve().parents[1] / "scripts/mr09_summarize.py")
SUMMARY = importlib.util.module_from_spec(SUMMARY_SPEC)
SUMMARY_SPEC.loader.exec_module(SUMMARY)


def synthetic_run(repetition=1, value=10, cell="D-synthetic"):
    """Complete fake record for summary tests; never written into research/."""
    return {
        "cell": cell, "repetition": repetition, "status": "success",
        "model_id": "synthetic-model", "revision": "synthetic-model-revision",
        "script_sha256": "synthetic-script-fixture",
        "protocol_sha256": "synthetic-protocol-fixture",
        "configuration": {
            "fixture": "synthetic; never research evidence", "active_sequences": 1},
        "environment": {
            "python": "synthetic-python", "torch": "synthetic-torch",
            "cuda_build": "synthetic-cuda",
            "packages": {"transformers": "synthetic-transformers"}},
        "hardware": {
            "gpu": "Synthetic GPU", "count": 1,
            "properties": "synthetic, uuid=fixture-identity, fake=true",
            "initial_driver_free_bytes": 1000, "driver_total_bytes": 2000,
            "process_allocator_limit_bytes": 500, "allocator_backend": "native",
            "nvidia_smi_csv": (
                "index, name, memory.total [MiB], memory.used [MiB], "
                "memory.free [MiB], driver_version, pci.bus_id\n"
                "0, Synthetic GPU, 2 MiB, 1 MiB, 1 MiB, "
                "synthetic-driver, 00000000:02:00.0")},
        "artifact_manifest": {
            "model_id": "synthetic-model", "revision": "synthetic-model-revision",
            "artifacts": [
                {"file": "config.json", "bytes": 10, "sha256": "a" * 64},
                {"file": "model.safetensors", "bytes": 20, "sha256": "b" * 64}]},
        "phases": [
            {"phase": phase, "peak_allocated_bytes": value,
             "peak_reserved_bytes": value + 2,
             "current_allocated_bytes": value - 2,
             "current_reserved_bytes": value + 2}
            for phase in SUMMARY.PHASES],
        "error_comparisons": [],
    }

def write_synthetic_run(root, run, suffix=None):
    name = suffix or str(run["repetition"])
    path = root / f"mr09-{run['cell']}-r{name}.json"
    path.write_text(json.dumps(run), encoding="utf-8")
    return path


class MeasurementArithmeticTests(unittest.TestCase):
    def test_kv_units_and_scaling(self):
        self.assertEqual(MODULE.GIB, 1_073_741_824)
        self.assertEqual(MODULE.kv_payload_bytes(30, 3, 64, 2048, 1, 2), 47_185_920)
        self.assertEqual(MODULE.kv_payload_bytes(30, 3, 64, 2048, 2, 2), 94_371_840)

    def test_signed_relative_measurement_denominator(self):
        self.assertEqual(MODULE.errors(90, 100), {
            "signed_bytes": -10, "absolute_bytes": 10, "signed_relative_percent": -10.0})
        self.assertEqual(MODULE.errors(120, 100)["signed_relative_percent"], 20)
        for measured in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                MODULE.errors(100, measured)

    def test_invalid_geometry(self):
        for invalid in (0, -1, 2.5, True):
            with self.assertRaises(ValueError):
                MODULE.kv_payload_bytes(30, 3, 64, invalid, 1, 2)

    def test_failure_classification_has_no_numerical_error(self):
        self.assertEqual(MODULE.classify_failure(RuntimeError("fixture"), "prefill", True), "OOM_prefill")
        self.assertEqual(MODULE.classify_failure(ImportError("fixture"), "warmup"), "unsupported")
        self.assertEqual(MODULE.classify_failure(RuntimeError("fixture"), "decode"), "runtime_error")

    def test_unexplained_existing_artifact_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(MODULE.urllib.request, "urlopen") as network:
            root = Path(directory)
            (root / "config.json").write_text("synthetic fixture", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "trusted pinned manifest"):
                MODULE.prepare(root)
            network.assert_not_called()

    def test_wrong_revision_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(MODULE.urllib.request, "urlopen") as network:
            root = Path(directory)
            (root / "mr09-manifest.json").write_text(json.dumps({
                "model_id": MODULE.MODEL_ID, "revision": "synthetic-wrong-revision", "artifacts": []}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "different model/revision"):
                MODULE.prepare(root)
            network.assert_not_called()

    def test_corrupt_existing_artifact_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(MODULE.urllib.request, "urlopen") as network:
            root = Path(directory)
            (root / "config.json").write_text("synthetic fixture", encoding="utf-8")
            (root / "mr09-manifest.json").write_text(json.dumps({
                "model_id": MODULE.MODEL_ID, "revision": MODULE.REVISION,
                "artifacts": [{"file": "config.json", "sha256": "synthetic-wrong-hash",
                               "source_url": f"https://huggingface.co/{MODULE.MODEL_ID}/resolve/{MODULE.REVISION}/config.json"}]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match trusted pinned manifest"):
                MODULE.prepare(root)
            network.assert_not_called()

    def test_summary_excludes_failures_and_hashes_published_sanitized_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for repetition, value in ((1, 10), (2, 30), (3, None)):
                run = synthetic_run(repetition, value or 9999)
                if value is None:
                    run["status"] = "OOM_prefill"
                    run["phases"] = [run["phases"][3]]
                    run["error_comparisons"] = [{"synthetic_failure_error_must_not_be_aggregated": 9999}]
                    run["failure"] = {"phase": "prefill", "message": "synthetic OOM fixture"}
                write_synthetic_run(root, run)
            with patch.object(sys, "argv",
                              ["mr09_summarize.py", "--directory", str(root), "--sanitize"]), contextlib.redirect_stdout(io.StringIO()):
                SUMMARY.main()
            summary = json.loads((root / "mr09-results-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status_counts"], {"success": 2, "OOM_prefill": 1})
            self.assertEqual(summary["cells"]["D-synthetic"]["phases"]["prefill"]["peak_allocated_bytes"],
                             {"n": 2, "min": 10, "median": 20.0, "max": 30})
            self.assertEqual(summary["comparable_competitor_error_pairs"], 0)
            self.assertEqual(summary["cells"]["D-synthetic"]["failures"][0]["status"], "OOM_prefill")
            for item in summary["input_checksums"]:
                raw = (root / item["file"]).read_bytes()
                self.assertNotIn(b"uuid=", raw)
                self.assertNotIn(b"\r\n", raw, "published hashes must survive Git LF normalization")
                self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertNotIn(b"\r\n", (root / "mr09-results-summary.json").read_bytes())

    def test_summary_rejects_mixed_pins_or_configuration_before_sanitizing(self):
        changes = {"model_id": "another-synthetic-model", "revision": "another-revision",
                   "script_sha256": "another-script", "protocol_sha256": "another-protocol",
                   "configuration": {"fixture": "synthetic; never research evidence", "active_sequences": 2}}
        for field, value in changes.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                original = write_synthetic_run(root, synthetic_run())
                first_bytes = original.read_bytes()
                second = synthetic_run(2)
                second[field] = value
                write_synthetic_run(root, second)
                with self.assertRaisesRegex(ValueError, "incompatible pins/configuration"):
                    SUMMARY.summarize(root, sanitize=True)
                self.assertEqual(original.read_bytes(), first_bytes)

    def test_summary_rejects_changed_measurement_cohort_before_sanitizing(self):
        changes = [
            (("environment", "python"), "another-python"),
            (("environment", "torch"), "another-torch"),
            (("environment", "cuda_build"), "another-cuda"),
            (("environment", "packages", "transformers"), "another-transformers"),
            (("hardware", "gpu"), "Another GPU"),
            (("hardware", "properties"), "another synthetic GPU property"),
            (("hardware", "driver_total_bytes"), 3000),
            (("hardware", "process_allocator_limit_bytes"), 600),
            (("hardware", "allocator_backend"), "cudaMallocAsync"),
            (("hardware", "nvidia_smi_csv"),
             synthetic_run()["hardware"]["nvidia_smi_csv"].replace(
                 "synthetic-driver", "another-driver")),
            (("hardware", "nvidia_smi_csv"),
             synthetic_run()["hardware"]["nvidia_smi_csv"].replace(
                 "00000000:02:00.0", "00000000:03:00.0")),
            (("artifact_manifest", "artifacts", 0, "file"), "another-config.json"),
            (("artifact_manifest", "artifacts", 0, "bytes"), 11),
            (("artifact_manifest", "artifacts", 0, "sha256"), "c" * 64),
        ]
        for path, value in changes:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                first_path = write_synthetic_run(root, synthetic_run())
                first_bytes = first_path.read_bytes()
                second = synthetic_run(2)
                target = second
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                second_path = write_synthetic_run(root, second)
                second_bytes = second_path.read_bytes()
                with self.assertRaisesRegex(ValueError, "incompatible measurement cohort"):
                    SUMMARY.summarize(root, sanitize=True)
                self.assertEqual(first_path.read_bytes(), first_bytes)
                self.assertEqual(second_path.read_bytes(), second_bytes)

    def test_summary_allows_availability_timing_and_manifest_order_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = synthetic_run(value=10)
            second = synthetic_run(2, value=30)
            second["started_utc"] = "synthetic-later-time"
            second["hardware"]["initial_driver_free_bytes"] = 900
            second["hardware"]["nvidia_smi_csv"] = (
                second["hardware"]["nvidia_smi_csv"].replace(
                    "1 MiB, 1 MiB", "0 MiB, 2 MiB"))
            second["hardware"]["properties"] = re.sub(
                r"uuid=[^,]*, ", "", second["hardware"]["properties"])
            second["artifact_manifest"]["artifacts"].reverse()
            second["artifact_manifest"]["access_date"] = "synthetic-later-date"
            for phase in second["phases"]:
                phase["elapsed_seconds"] = 123.0
                phase["driver_free_bytes"] = 800
            paths = [write_synthetic_run(root, run) for run in (first, second)]
            before = [path.read_bytes() for path in paths]
            summary = SUMMARY.summarize(root)
            self.assertEqual(
                summary["cells"]["D-synthetic"]["phases"]["prefill"]["peak_allocated_bytes"],
                {"n": 2, "min": 10, "median": 20.0, "max": 30})
            self.assertEqual([path.read_bytes() for path in paths], before)

    def test_summary_keeps_early_failure_without_success_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_synthetic_run(root, synthetic_run())
            failure = synthetic_run(2)
            failure["status"] = "unsupported"
            failure["phases"] = []
            failure["failure"] = {"phase": "discovery", "message": "synthetic"}
            for key in ("environment", "hardware", "artifact_manifest"):
                failure.pop(key)
            write_synthetic_run(root, failure)
            summary = SUMMARY.summarize(root)
            self.assertEqual(summary["status_counts"], {"success": 1, "unsupported": 1})
            self.assertEqual(
                summary["cells"]["D-synthetic"]["phases"]["prefill"]
                ["peak_allocated_bytes"]["n"], 1)
            self.assertEqual(
                summary["cells"]["D-synthetic"]["failures"][0]["status"], "unsupported")

    def test_summary_rejects_missing_success_identity(self):
        for field in ("environment", "hardware", "artifact_manifest"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                run = synthetic_run()
                run.pop(field)
                write_synthetic_run(root, run)
                with self.assertRaisesRegex(ValueError, "successful run requires"):
                    SUMMARY.summarize(root)

    def test_summary_preserves_committed_measurement_cohort(self):
        root = Path(__file__).resolve().parents[1] / "research/market/measurements"
        expected = json.loads(
            (root / "mr09-results-summary.json").read_text(encoding="utf-8"))
        before = {
            item["file"]: hashlib.sha256((root / item["file"]).read_bytes()).hexdigest()
            for item in expected["input_checksums"]}
        self.assertEqual(SUMMARY.summarize(root), expected)
        self.assertEqual(
            {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
             for name in before}, before)

    def test_summary_rejects_duplicate_repetition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = synthetic_run()
            write_synthetic_run(root, run)
            write_synthetic_run(root, run, suffix="duplicate")
            with self.assertRaisesRegex(ValueError, "duplicate repetition"):
                SUMMARY.summarize(root)

    def test_summary_rejects_missing_duplicate_or_unexpected_success_phase(self):
        for variant in ("missing", "duplicate", "unexpected"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                run = synthetic_run()
                if variant == "missing":
                    run["phases"].pop()
                elif variant == "duplicate":
                    run["phases"][-1] = copy.deepcopy(run["phases"][0])
                else:
                    run["phases"][-1]["phase"] = "synthetic-extra-phase"
                write_synthetic_run(root, run)
                with self.assertRaisesRegex(ValueError, "six unique phases"):
                    SUMMARY.summarize(root)

    def test_summary_keeps_supplemental_moe_profiles_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_synthetic_run(root, synthetic_run())
            for cell, value in (("GM-synthetic", 50), ("M0-synthetic", 70)):
                run = synthetic_run(value=value, cell=cell)
                run["model_id"] = "synthetic-moe"
                run["revision"] = "synthetic-moe-revision"
                run["artifact_manifest"]["model_id"] = run["model_id"]
                run["artifact_manifest"]["revision"] = run["revision"]
                write_synthetic_run(root, run)
            summary = SUMMARY.summarize(root)
            self.assertEqual(summary["run_count"], 3)
            self.assertEqual(summary["cells"]["GM-synthetic"]["model_id"], "synthetic-moe")
            self.assertEqual(summary["cells"]["M0-synthetic"]["phases"]["prefill"]["peak_allocated_bytes"]["median"], 70)
            self.assertEqual(summary["cells"]["D-synthetic"]["phases"]["prefill"]["peak_allocated_bytes"]["n"], 1)

    def test_summary_rejects_inconsistent_allocator_counters(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = synthetic_run()
            run["phases"][3]["peak_reserved_bytes"] = 1
            write_synthetic_run(root, run)
            with self.assertRaisesRegex(ValueError, "inconsistent allocator counters"):
                SUMMARY.summarize(root)


if __name__ == "__main__":
    unittest.main()
