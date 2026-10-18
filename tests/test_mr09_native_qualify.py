"""Synthetic launcher failures; no native child, driver query or model is run."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import mr09_native_qualify as launcher
    import mr09_native_capture as capture
finally:
    sys.path.pop(0)

DRIVER_CSV = ('name,driver_version,memory.total [MiB],memory.free [MiB]\n'
              'Synthetic GPU,synthetic-driver,16303 MiB,10134 MiB\n')
DEFAULT_PREFLIGHT = object()


class NativeLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.directory = self.base / "records"
        self.directory.mkdir()
        self.runtime = self.base / "runtime"
        self.runtime.mkdir()
        self.output = self.directory / "init-r1.json"
        self.preflight = self.directory / "init-r1-preflight.json"
        self.model = self.base / launcher.MODEL
        (self.directory / "build-loader-v2.json").write_text(json.dumps({
            "executables": {"native-init.exe": "a" * 64},
            "harness_git_ref": "b" * 40,
        }))
        (self.directory / "runtime-artifacts.json").write_text(json.dumps({
            "files": [{"file": "synthetic.dll", "sha256": "c" * 64}],
        }))
        self.child_stdout = f"synthetic child stdout {self.model}\n"
        self.child_stderr = f"synthetic child stderr {self.runtime}\n"

    def exercise(self, *, code=0, child_timeout=False, driver=DRIVER_CSV,
                 preflight_screen=DEFAULT_PREFLIGHT, reject_preflight=False):
        original_checksum, original_stat = launcher.checksum, Path.stat
        screen = preflight_screen if preflight_screen is not DEFAULT_PREFLIGHT else {"guards": {
            "nvidia_smi_free_mib": True,
            "available_host_ram_bytes": True,
            "temporary_volume_free_bytes": True,
        }}

        def checksum(path):
            return {
                self.base / "native-init.exe": "a" * 64,
                self.model: launcher.MODEL_SHA,
                self.runtime / "synthetic.dll": "c" * 64,
            }.get(path) or original_checksum(path)

        def stat(path, *args, **kwargs):
            # Admit a fictional artifact without creating/downloading any weights.
            return SimpleNamespace(st_size=270885952) if path == self.model else original_stat(path, *args, **kwargs)

        def run(argv, **kwargs):
            if argv[1] == "scripts/mr09_preflight.py":
                self.preflight.write_text(json.dumps(screen))
                return subprocess.CompletedProcess(argv, 0, "", "")
            self.assertEqual(argv, [str(self.base / "native-init.exe"), str(self.runtime), "2136809472", str(self.model)])
            self.assertEqual(kwargs["timeout"], 90)
            if child_timeout:
                raise subprocess.TimeoutExpired(argv, 90, output=self.child_stdout.encode(), stderr=self.child_stderr.encode())
            return subprocess.CompletedProcess(argv, code, self.child_stdout, self.child_stderr)

        def query(argv, **kwargs):
            # This read happens at the real post-child boundary, before the
            # mocked driver call returns, raises, or would otherwise hang.
            self.assertTrue(self.output.is_file(), "child capture must already be durable")
            retained = json.loads(self.output.read_text())
            self.assertEqual(retained["stdout"], "synthetic child stdout $GGUF_FILE\n")
            self.assertIn("synthetic child stderr $RUNTIME_DIR\n", retained["stderr"])
            self.assertEqual(retained["exit_code"], -1 if child_timeout else code)
            self.assertEqual(retained["driver_readback"]["status"], "pending")
            self.assertNotEqual(retained["status"], "native_initialization_completed")
            self.assertEqual(kwargs["timeout"], launcher.DRIVER_QUERY_TIMEOUT_SECONDS)
            self.assertEqual(argv[0], "nvidia-smi")
            if isinstance(driver, Exception):
                raise driver
            return driver

        with (mock.patch.object(launcher, "DIRECTORY", self.directory),
              mock.patch.object(launcher, "checksum", side_effect=checksum),
              mock.patch.object(Path, "stat", new=stat),
              mock.patch.object(launcher.subprocess, "run", side_effect=run) as native,
              mock.patch.object(launcher.subprocess, "check_output", side_effect=query) as telemetry,
              mock.patch.object(sys, "argv", ["synthetic-launcher", "--temporary-dir", str(self.base), "--repetition", "1"]),
              contextlib.redirect_stdout(io.StringIO())):
            if reject_preflight:
                with self.assertRaisesRegex(RuntimeError, "fresh spare-capacity guard failed; no launch"):
                    launcher.main()
            else:
                returned = launcher.main()
        if reject_preflight:
            self.assertEqual(native.call_count, 1, "only the capacity screen may run")
            telemetry.assert_not_called()
            self.assertFalse(self.output.exists(), "no child observation may be manufactured")
            self.assertEqual(json.loads(self.preflight.read_text()), screen)
            return
        self.assertEqual(native.call_count, 2, "one preflight and one child, with no retry")
        self.assertEqual(telemetry.call_count, 1)
        result = json.loads(self.output.read_text())
        self.assertEqual(result["harness_sha256"], "a" * 64)
        self.assertEqual(result["model_sha256"], launcher.MODEL_SHA)
        self.assertEqual(result["preflight_sha256"], original_checksum(self.preflight))
        self.assertEqual(result["stdout"], "synthetic child stdout $GGUF_FILE\n")
        self.assertIn("synthetic child stderr $RUNTIME_DIR\n", result["stderr"])
        return returned, result

    def reset_observation(self):
        self.output.unlink(missing_ok=True)
        self.preflight.unlink(missing_ok=True)

    def assert_incomplete(self, returned, record):
        self.assertEqual(returned, 1)
        self.assertEqual(record["status"], "qualification_failure")
        self.assertEqual(record["driver_readback"]["status"], "failed")
        with self.assertRaisesRegex(ValueError, "successful initialization-only"):
            capture.validate_capture(record)

    def test_completed_and_failed_children_survive_driver_command_failure(self):
        for code in (0, 7):
            with self.subTest(child_exit=code):
                self.reset_observation()
                failure = subprocess.CalledProcessError(9, ["nvidia-smi"], output=b"partial telemetry", stderr=b"synthetic driver error")
                returned, record = self.exercise(code=code, driver=failure)
                self.assert_incomplete(returned, record)
                self.assertEqual(record["exit_code"], code)
                self.assertEqual(record["native_status"], "completed" if code == 0 else "failed")
                self.assertEqual(record["driver_readback"]["exit_code"], 9)
                self.assertEqual(record["driver_readback"]["stdout"], "partial telemetry")
                self.assertEqual(record["driver_readback"]["stderr"], "synthetic driver error")

    def test_driver_timeout_preserves_completed_or_timed_out_child(self):
        for child_timeout in (False, True):
            with self.subTest(child_timeout=child_timeout):
                self.reset_observation()
                failure = subprocess.TimeoutExpired(["nvidia-smi"], 10, output=b"partial telemetry", stderr=b"telemetry timeout")
                returned, record = self.exercise(child_timeout=child_timeout, driver=failure)
                self.assert_incomplete(returned, record)
                self.assertEqual(record["exit_code"], -1 if child_timeout else 0)
                self.assertEqual(record["native_status"], "timed_out" if child_timeout else "completed")
                self.assertEqual(record["driver_readback"]["error_type"], "TimeoutExpired")
                self.assertEqual(record["driver_readback"]["stdout"], "partial telemetry")
                if child_timeout:
                    self.assertIn("child killed; stop without retry", record["stderr"])

    def test_missing_or_malformed_driver_readback_retains_the_child(self):
        for driver in (FileNotFoundError("synthetic missing telemetry executable"), "not a valid driver CSV"):
            with self.subTest(driver=str(driver)):
                self.reset_observation()
                returned, record = self.exercise(driver=driver)
                self.assert_incomplete(returned, record)
                self.assertEqual(record["exit_code"], 0)

    def test_successful_telemetry_does_not_replace_native_failure_or_timeout(self):
        for code, timeout in ((0, False), (7, False), (0, True)):
            with self.subTest(code=code, timeout=timeout):
                self.reset_observation()
                returned, record = self.exercise(code=code, child_timeout=timeout)
                self.assertEqual(record["driver_readback"]["status"], "completed")
                self.assertEqual(record["driver_csv"], DRIVER_CSV.strip())
                successful = code == 0 and not timeout
                self.assertEqual(returned, 0 if successful else 1)
                self.assertEqual(record["status"], "native_initialization_completed" if successful else "qualification_failure")

    def test_failed_atomic_update_keeps_the_previous_capture(self):
        original = {"stdout": "synthetic retained child", "status": "post_run_telemetry_pending"}
        launcher.write(self.output, original)
        before = self.output.read_bytes()
        with mock.patch.object(launcher.os, "replace", side_effect=OSError("synthetic replace failure")):
            with self.assertRaises(OSError):
                launcher.write(self.output, {**original, "status": "qualification_failure"})
        self.assertEqual(self.output.read_bytes(), before)
        self.assertEqual(list(self.directory.glob("*.tmp")), [])

    def test_existing_incomplete_record_cannot_be_overwritten_or_retried(self):
        self.output.write_text('{"status":"post_run_telemetry_pending"}\n')
        original = self.output.read_bytes()
        with (mock.patch.object(launcher, "DIRECTORY", self.directory),
              mock.patch.object(launcher, "checksum") as checksum,
              mock.patch.object(launcher.subprocess, "run") as run,
              mock.patch.object(sys, "argv", ["synthetic-launcher", "--temporary-dir", str(self.base), "--repetition", "1"]),
              contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit)):
            launcher.main()
        checksum.assert_not_called()
        run.assert_not_called()
        self.assertEqual(self.output.read_bytes(), original)

    def test_preflight_requires_every_named_guard_and_literal_true_before_launch(self):
        good = {
            "nvidia_smi_free_mib": True,
            "available_host_ram_bytes": True,
            "temporary_volume_free_bytes": True,
        }
        invalid = [{}, {"guards": {}}, {"guards": {"unrelated": True}},
                   {"guards": {**good, "unexpected": True}}]
        invalid.extend((None, [], True, "true", 1))
        invalid.extend({"guards": value} for value in (None, [], True, "true"))
        for key in good:
            invalid.append({"guards": {name: value for name, value in good.items() if name != key}})
            for value in (1, 1.0, "false", [True], False, None):
                invalid.append({"guards": {**good, key: value}})
        for screen in invalid:
            with self.subTest(screen=screen):
                self.reset_observation()
                self.exercise(preflight_screen=screen, reject_preflight=True)
        self.reset_observation()
        returned, record = self.exercise(preflight_screen={"guards": good})
        self.assertEqual(returned, 0)
        self.assertEqual(record["native_status"], "completed")

    def test_executed_launcher_remains_bound_to_all_historical_captures(self):
        directory = ROOT / capture.DIRECTORY
        historical = directory / "mr09_native_qualify.executed.py"
        digest = hashlib.sha256(historical.read_bytes()).hexdigest()
        self.assertEqual(digest, "6a645f212c3b947789345dc739d88d554f3e083021db3cc0f7abfebc8ff1f8b8")
        for repetition in (1, 2, 3):
            self.assertEqual(json.loads((directory / f"init-r{repetition}.json").read_text())["launcher_sha256"], digest)
        self.assertNotEqual(hashlib.sha256((ROOT / "scripts/mr09_native_qualify.py").read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
