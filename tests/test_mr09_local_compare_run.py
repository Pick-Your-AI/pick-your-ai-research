"""Synthetic H1 launcher failures/chronology; never runs a GPU or model."""
from datetime import datetime, timedelta, timezone
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import mr09_local_compare_run as launcher
finally:
    sys.path.pop(0)

DRIVER = ("name,driver_version,memory.total [MiB],memory.free [MiB]\n"
          "NVIDIA GeForce RTX 5070 Ti,610.88,16303 MiB,10134 MiB\n")


def synthetic_record():
    # Construct a clearly synthetic native trace in tests, never real evidence.
    live = 300 * 2**20 + 16
    cap = {"mr09_event": "cap", "cap_bytes": launcher.CAP_BYTES,
           "admission_denials": 1, "graph_denials": 1}
    events = [
        {"mr09_event": "qualification", "status": "probe_passed", "device": "CUDA0",
         "driver_total_bytes": 17094475776, "cuda_reported_free_bytes": 12 * 2**30,
         "graphs_disabled": True, "decode_api_loaded": False},
        {**cap, "stage": "after_probe", "live_bytes": 0, "peak_admitted_bytes": 8388608, "native_allocator_calls": 1},
        {"mr09_event": "effective", "no_alloc": False, "context": 256, "batch": 128,
         "ubatch": 128, "sequences": 1, "generation_forwards": 0, "warmup": False, "extra_buffer_types": False},
        {**cap, "stage": "before_capture", "live_bytes": live, "peak_admitted_bytes": live, "native_allocator_calls": 4},
        {"type": "fit_memory_breakdown", "data": {"unit": "MiB", "rows": [
            {"kind": "device", "name": "CUDA0", "self": 300, "total": 16302, "free": 12000,
             "model": 256, "context": 5, "compute": 39, "unaccounted": 0},
            {"kind": "host", "name": "Host", "self": 1, "model": 1, "context": 0, "compute": 0}]}},
        {**cap, "stage": "after_cleanup", "live_bytes": 0, "peak_admitted_bytes": live, "native_allocator_calls": 4},
        {"mr09_event": "result", "status": "initialization_qualified"}]
    return {"exit_code": 0, "stdout": "\n".join(json.dumps(e) for e in events),
            "stderr": "offloaded 31/31 layers to GPU\n(load_mode = mmap)\nK (f16) V (f16)\n"
                      "llama_context: n_outputs_max = 128\nllama_context: n_outputs_max_per_seq = 1\n"}


class LocalCompareLauncherTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.directory = self.base / "records"
        self.directory.mkdir()
        self.output = self.directory / "H1-r1.json"
        self.preflight = self.directory / "H1-r1-preflight.json"
        self.identities = {"harness_sha256": "a" * 64, "prediction_freeze_sha256": "b" * 64}
        self.frozen = datetime.now(timezone.utc) - timedelta(minutes=1)

    def screen(self):
        return {"classification": "read-only capacity screen; not inference or a fit guarantee",
                "profile": "granite31", "observed_utc": datetime.now(timezone.utc).isoformat(),
                "thresholds": launcher.PREFLIGHT_THRESHOLDS,
                "methods": launcher.PREFLIGHT_METHODS,
                "observed": dict(launcher.PREFLIGHT_THRESHOLDS),
                "guards": {k: True for k in launcher.PREFLIGHT_THRESHOLDS},
                "status": "admitted_to_download_screen_only",
                "reason": "all screens satisfied; recheck before inference"}

    def exercise(self, *, native=None, telemetry=DRIVER, screen_mutation=None):
        native = synthetic_record() if native is None else native

        def run(argv, **kwargs):
            if argv[1] == str(ROOT / "scripts/mr09_preflight.py"):
                screen = self.screen()
                if screen_mutation:
                    screen_mutation(screen)
                self.preflight.write_text(json.dumps(screen))
                return subprocess.CompletedProcess(argv, 0, "", "")
            self.assertEqual(kwargs["timeout"], 90)
            if isinstance(native, Exception):
                raise native
            return subprocess.CompletedProcess(argv, native["exit_code"], native["stdout"], native["stderr"])

        def query(argv, **kwargs):
            if not self.output.exists():
                return DRIVER
            retained = json.loads(self.output.read_text())
            self.assertEqual(retained["driver_readback"]["status"], "pending")
            self.assertNotEqual(retained["status"], "native_initialization_completed")
            self.assertEqual(kwargs["timeout"], 10)
            if isinstance(telemetry, Exception):
                raise telemetry
            return telemetry

        with (mock.patch.object(launcher, "admit", return_value=(self.identities, self.frozen)),
              mock.patch.object(launcher.subprocess, "run", side_effect=run) as children,
              mock.patch.object(launcher.subprocess, "check_output", side_effect=query) as queries):
            result = launcher.run(self.base, 1, self.directory)
        self.assertEqual(children.call_count, 2)
        self.assertEqual(queries.call_count, 2)
        return result

    def reset(self):
        self.output.unlink(missing_ok=True)
        self.preflight.unlink(missing_ok=True)

    def test_native_success_is_saved_before_bounded_telemetry(self):
        result = self.exercise()
        self.assertEqual(result["status"], "native_initialization_completed")
        self.assertEqual(result["prediction_freeze_sha256"], "b" * 64)
        self.assertEqual(result["native_validation"]["cleanup_live_bytes"], 0)

    def test_telemetry_failure_and_timeout_preserve_completed_child(self):
        for failure in (subprocess.CalledProcessError(7, ["nvidia-smi"], output=b"partial", stderr=b"failed"),
                        subprocess.TimeoutExpired(["nvidia-smi"], 10, output=b"partial"),
                        FileNotFoundError("synthetic missing driver query"), "malformed CSV"):
            with self.subTest(error=str(failure)):
                self.reset()
                result = self.exercise(telemetry=failure)
                self.assertEqual(result["status"], "qualification_failure")
                self.assertEqual(result["exit_code"], 0)
                self.assertEqual(result["stdout"], synthetic_record()["stdout"])

    def test_successful_telemetry_cannot_override_failure_or_timeout(self):
        failure = synthetic_record()
        failure["exit_code"] = 8
        for native in (failure, subprocess.TimeoutExpired(["synthetic-child"], 90, output=b"partial native", stderr=b"native timeout")):
            with self.subTest(native=str(native)):
                self.reset()
                result = self.exercise(native=native)
                self.assertEqual(result["status"], "qualification_failure")
                self.assertEqual(result["driver_readback"]["status"], "completed")
                with mock.patch.object(launcher.subprocess, "run") as later:
                    with self.assertRaises(ValueError):
                        launcher.run(self.base, 2, self.directory)
                later.assert_not_called()

    def test_failed_guard_or_stale_screen_launches_no_child(self):
        for mutation in (lambda s: s["guards"].update(nvidia_smi_free_mib=False),
                         lambda s: s["observed"].update(nvidia_smi_free_mib=4095),
                         lambda s: s.update(observed_utc=(datetime.now(timezone.utc)-timedelta(seconds=31)).isoformat()),
                         lambda s: s["observed"].update(nvidia_smi_free_mib=True)):
            with self.subTest(mutation=mutation):
                self.reset()
                with self.assertRaises(ValueError):
                    self.exercise(screen_mutation=mutation)
                self.assertFalse(self.output.exists())
                self.assertTrue(self.preflight.exists())
                with mock.patch.object(launcher.subprocess, "run") as later:
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        launcher.run(self.base, 2, self.directory)
                later.assert_not_called()

    def test_existing_pending_record_and_failed_previous_trial_prevent_launch(self):
        self.output.write_text('{"status":"post_run_telemetry_pending"}')
        original = self.output.read_bytes()
        with mock.patch.object(launcher.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                launcher.run(self.base, 1, self.directory)
            with self.assertRaises(ValueError):
                launcher.run(self.base, 2, self.directory)
        run.assert_not_called()
        self.assertEqual(original, self.output.read_bytes())

    def test_tuple_cleanup_graph_and_counter_mutations_are_rejected(self):
        record = synthetic_record()
        self.assertEqual(launcher.validate_h1(record)["model_graph_dispatches"], 0)
        events = [json.loads(line) for line in record["stdout"].splitlines()]
        for index, field, value in ((2, "context", 512), (2, "sequences", True),
                                    (3, "graph_denials", 2), (5, "live_bytes", 1),
                                    (0, "cuda_reported_free_bytes", 4095)):
            with self.subTest(index=index, field=field):
                mutated = copy.deepcopy(events)
                mutated[index][field] = value
                with self.assertRaises(ValueError):
                    launcher.validate_h1({**record, "stdout": "\n".join(json.dumps(e) for e in mutated)})

    def test_artifact_traversal_and_hash_drift_are_rejected(self):
        fixture = self.base / "synthetic.txt"
        fixture.write_bytes(b"synthetic fixture")
        digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
        launcher.verify_files(self.base, {"synthetic.txt": digest})
        for files in ({"synthetic.txt": "0" * 64}, {"../synthetic.txt": digest},
                      {"synthetic.txt": True}, {}):
            with self.subTest(files=files), self.assertRaises(ValueError):
                launcher.verify_files(self.base, files)

    def test_missing_prediction_freeze_or_mismatched_driver_prevents_launch(self):
        with mock.patch.object(launcher.subprocess, "run") as child:
            with self.assertRaises(FileNotFoundError):
                launcher.run(self.base, 1, self.directory)
        child.assert_not_called()
        for driver in (DRIVER.replace("610.88", "595.97"), DRIVER.replace("5070 Ti", "5090")):
            with self.subTest(driver=driver):
                with (mock.patch.object(launcher, "admit", return_value=(self.identities, self.frozen)),
                      mock.patch.object(launcher.subprocess, "check_output", return_value=driver),
                      mock.patch.object(launcher.subprocess, "run") as child):
                    with self.assertRaises(ValueError):
                        launcher.run(self.base, 1, self.directory)
                child.assert_not_called()

    def test_missing_native_source_and_incomplete_runtime_ledger_are_rejected(self):
        sources = {path: launcher.sha(ROOT / path) for path in launcher.REQUIRED_SOURCES}
        executable = self.base / "native-init.exe"
        executable.write_bytes(b"synthetic executable; not runnable")
        build = {"runtime_commit": launcher.RUNTIME_COMMIT, "harness_git_ref": "a" * 40,
                 "source_files": sources, "executables": {"native-init.exe": launcher.sha(executable)}}
        (self.directory / "runtime-artifacts.json").write_text('{"files": []}')
        (self.directory / "prediction-freeze.json").write_text('{}')
        for omitted in sources:
            with self.subTest(omitted=omitted):
                (self.directory / "build.json").write_text(json.dumps({**build, "source_files": {k: v for k, v in sources.items() if k != omitted}}))
                with self.assertRaisesRegex(ValueError, "H1 harness and quota"):
                    launcher.admit(self.base, self.directory)
        (self.directory / "build.json").write_text(json.dumps(build))
        model = self.base / launcher.MODEL
        model.write_bytes(b"synthetic artifact; not model weights")
        original_sha, original_stat = launcher.sha, Path.stat

        def sha(path):
            return launcher.MODEL_SHA if path == model else original_sha(path)

        def stat(path, *args, **kwargs):
            return SimpleNamespace(st_size=270885952) if path == model else original_stat(path, *args, **kwargs)

        with (mock.patch.object(launcher, "sha", side_effect=sha), mock.patch.object(Path, "stat", new=stat)):
            with self.assertRaisesRegex(ValueError, "complete pinned runtime artifact ledger"):
                launcher.admit(self.base, self.directory)

    def test_nondictionary_native_event_and_boolean_repetition_are_rejected(self):
        record = synthetic_record()
        lines = record["stdout"].splitlines()
        lines[0] = '[]'
        with self.assertRaisesRegex(ValueError, "seven-event"):
            launcher.validate_h1({**record, "stdout": "\n".join(lines)})
        with self.assertRaisesRegex(ValueError, "integer repetitions"):
            launcher.run(self.base, True, self.directory)


if __name__ == "__main__":
    unittest.main()
