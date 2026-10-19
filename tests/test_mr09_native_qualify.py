"""Synthetic launcher failures; no native child, driver query or model is run."""
import contextlib
import copy
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
    import mr09_preflight as preflight_cli
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
        self.runtime_ledger_bytes = (ROOT / launcher.DIRECTORY / "runtime-artifacts.json").read_bytes()
        self.runtime_artifacts = json.loads(self.runtime_ledger_bytes)["files"]
        (self.directory / "runtime-artifacts.json").write_bytes(self.runtime_ledger_bytes)
        self.child_stdout = f"synthetic child stdout {self.model}\n"
        self.child_stderr = f"synthetic child stderr {self.runtime}\n"

    def exercise(self, *, code=0, child_timeout=False, driver=DRIVER_CSV,
                 preflight_screen=DEFAULT_PREFLIGHT, reject_preflight=False,
                 reject_runtime_ledger=False, mutate_ledger_after_checks=False):
        original_checksum, original_stat = launcher.checksum, Path.stat
        runtime_pins = {self.runtime / item["file"]: item["sha256"] for item in self.runtime_artifacts}
        checked_runtime = []
        screen = preflight_screen if preflight_screen is not DEFAULT_PREFLIGHT else {"guards": {
            "nvidia_smi_free_mib": True,
            "available_host_ram_bytes": True,
            "temporary_volume_free_bytes": True,
        }}

        def checksum(path):
            if path.parent == self.runtime:
                checked_runtime.append(path.name)
            return {
                self.base / "native-init.exe": "a" * 64,
                self.model: launcher.MODEL_SHA,
                **runtime_pins,
            }.get(path) or original_checksum(path)

        def stat(path, *args, **kwargs):
            # Admit a fictional artifact without creating/downloading any weights.
            return SimpleNamespace(st_size=270885952) if path == self.model else original_stat(path, *args, **kwargs)

        def run(argv, **kwargs):
            if argv[1] == "scripts/mr09_preflight.py":
                self.preflight.write_text(json.dumps(screen))
                if mutate_ledger_after_checks:
                    (self.directory / "runtime-artifacts.json").write_text('{"files": []}')
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
              contextlib.redirect_stdout(io.StringIO()),
              contextlib.redirect_stderr(io.StringIO()) as diagnostics):
            if reject_runtime_ledger:
                with self.assertRaises(SystemExit) as rejected:
                    launcher.main()
                self.assertEqual(rejected.exception.code, 2)
                self.assertIn("pinned runtime artifact ledger mismatch; no launch", diagnostics.getvalue())
            elif reject_preflight:
                with self.assertRaisesRegex(RuntimeError, "fresh spare-capacity guard failed; no launch"):
                    launcher.main()
            else:
                returned = launcher.main()
        if reject_runtime_ledger:
            native.assert_not_called()
            telemetry.assert_not_called()
            self.assertEqual(checked_runtime, [], "reject the ledger before trusting any listed runtime identity")
            self.assertFalse(self.preflight.exists())
            self.assertFalse(self.output.exists())
            return
        self.assertEqual(checked_runtime, [item["file"] for item in self.runtime_artifacts])
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

    def test_runtime_ledger_rejects_every_unpinned_shape_inventory_and_identity_before_launch(self):
        ledger = json.loads(self.runtime_ledger_bytes)
        invalid = [None, [], True, 1, "synthetic", {},
                   *({"files": value} for value in ([], {}, "", None))]
        for index in range(len(ledger["files"])):
            changed = copy.deepcopy(ledger)
            changed["files"].pop(index)
            invalid.append(changed)
        for change in ("duplicate", "extra", "bytes", "hash", "archive", "metadata"):
            changed = copy.deepcopy(ledger)
            if change == "duplicate":
                changed["files"].append(copy.deepcopy(changed["files"][0]))
            elif change == "extra":
                changed["files"].append({"file": "synthetic-unexpected.dll", "bytes": 1, "sha256": "f" * 64})
            elif change == "bytes":
                changed["files"][0]["bytes"] += 1
            elif change == "hash":
                changed["files"][0]["sha256"] = "f" * 64
            elif change == "archive":
                changed["archives"][0]["source_url"] = "https://example.invalid/synthetic-fixture"
            else:
                changed["synthetic-unreviewed-metadata"] = True
            invalid.append(changed)
        raw_cases = [json.dumps(value).encode() for value in invalid]
        raw_cases.extend((json.dumps(ledger).encode(), b'{"files": [], "files": []}', b'not JSON'))
        manifest = self.directory / "runtime-artifacts.json"
        for index, raw in enumerate(raw_cases):
            with self.subTest(case=index):
                self.reset_observation()
                manifest.write_bytes(raw)
                self.exercise(reject_runtime_ledger=True)
                self.assertEqual(manifest.read_bytes(), raw)

    def test_exact_retained_runtime_ledger_checks_the_complete_inventory_before_launch(self):
        self.assertEqual(hashlib.sha256(self.runtime_ledger_bytes).hexdigest(),
                         "d788e18ba59ab6f210c1ceb61599f39269440a774664c8f515ffca9a7041cfcd")
        returned, record = self.exercise()
        self.assertEqual(returned, 0)
        self.assertEqual(record["runtime_artifact_ledger_sha256"], hashlib.sha256(self.runtime_ledger_bytes).hexdigest())
        self.assertEqual((self.directory / "runtime-artifacts.json").read_bytes(), self.runtime_ledger_bytes)

    def test_admitted_runtime_ledger_identity_survives_later_ledger_file_change(self):
        returned, record = self.exercise(mutate_ledger_after_checks=True)
        self.assertEqual(returned, 0)
        self.assertEqual(record["runtime_artifact_ledger_sha256"], hashlib.sha256(self.runtime_ledger_bytes).hexdigest())
        self.assertNotEqual((self.directory / "runtime-artifacts.json").read_bytes(), self.runtime_ledger_bytes)

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


class NativeOutputPublicationTests(unittest.TestCase):
    def exercise(self, *, arrival=None, kind="file", code=0, child_timeout=False,
                 link_failure=False):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            directory, runtime = base / "records", base / "runtime"
            directory.mkdir()
            runtime.mkdir()
            output, preflight = directory / "init-r1.json", directory / "init-r1-preflight.json"
            target = directory / "synthetic-link-target.json"
            model = base / launcher.MODEL
            (directory / "build-loader-v2.json").write_text(json.dumps({
                "executables": {"native-init.exe": "a" * 64}, "harness_git_ref": "b" * 40,
            }))
            ledger = (ROOT / launcher.DIRECTORY / "runtime-artifacts.json").read_bytes()
            (directory / "runtime-artifacts.json").write_bytes(ledger)
            runtime_files = json.loads(ledger)["files"]
            hashes = {base / "native-init.exe": "a" * 64, model: launcher.MODEL_SHA,
                      **{runtime / item["file"]: item["sha256"] for item in runtime_files}}
            original = b'{"synthetic":"retained original observation"}\n'
            occupied_path = preflight if arrival in ("early_preflight", "before_preflight", "during_preflight") else output

            def occupy():
                if kind == "file":
                    occupied_path.write_bytes(original)
                elif kind == "directory":
                    occupied_path.mkdir()
                    (occupied_path / "retained.json").write_bytes(original)
                else:
                    if kind == "live_symlink":
                        target.write_bytes(original)
                    occupied_path.symlink_to(target)

            if arrival in ("early_output", "early_preflight"):
                occupy()
            calls = {"preflight": 0, "capacity": 0, "child": 0, "driver": 0}
            checked_runtime = []
            original_checksum, original_stat = launcher.checksum, Path.stat
            original_link, original_fsync, original_replace = launcher.os.link, launcher.os.fsync, launcher.os.replace

            def checksum(path):
                if path.parent == runtime:
                    checked_runtime.append(path.name)
                return hashes[path] if path in hashes else original_checksum(path)

            def stat(path, *args, **kwargs):
                return SimpleNamespace(st_size=270885952) if path == model else original_stat(path, *args, **kwargs)

            def memory(pointer):
                pointer._obj.ullAvailPhys = 64 * 2**30
                return 1

            def run(argv, **kwargs):
                if argv[0] == "nvidia-smi":
                    calls["capacity"] += 1
                    self.assertEqual(kwargs["timeout"], 30)
                    if arrival == "during_preflight":
                        occupy()
                    return subprocess.CompletedProcess(argv, 0, "8192\n", "")
                if argv[1] == "scripts/mr09_preflight.py":
                    calls["preflight"] += 1
                    if arrival == "before_preflight":
                        occupy()
                    screen_stdout, screen_stderr = io.StringIO(), io.StringIO()
                    with (mock.patch.object(sys, "argv", [argv[1], *argv[2:]]),
                          contextlib.redirect_stdout(screen_stdout), contextlib.redirect_stderr(screen_stderr)):
                        try:
                            preflight_cli.main()
                        except SystemExit as error:
                            raise subprocess.CalledProcessError(error.code, argv, screen_stdout.getvalue(), screen_stderr.getvalue()) from error
                    return subprocess.CompletedProcess(argv, 0, screen_stdout.getvalue(), screen_stderr.getvalue())
                calls["child"] += 1
                self.assertEqual(argv, [str(base / "native-init.exe"), str(runtime), "2136809472", str(model)])
                self.assertEqual(kwargs["timeout"], 90)
                if arrival == "during_child":
                    occupy()
                if child_timeout:
                    raise subprocess.TimeoutExpired(argv, 90, output=b"synthetic child stdout", stderr=b"synthetic child stderr")
                return subprocess.CompletedProcess(argv, code, "synthetic child stdout", "synthetic child stderr")

            def link(source, destination):
                retained = json.loads(Path(source).read_text())
                self.assertEqual(destination, output)
                self.assertEqual(synced.call_count, 1, "fully flush the first child capture before publishing")
                self.assertEqual(retained["driver_readback"]["status"], "pending")
                self.assertEqual(retained["exit_code"], -1 if child_timeout else code)
                self.assertEqual(calls["driver"], 0)
                if link_failure:
                    raise OSError("synthetic filesystem does not support hard links")
                return original_link(source, destination)

            def driver(argv, **kwargs):
                calls["driver"] += 1
                self.assertEqual(kwargs["timeout"], 10)
                self.assertEqual(json.loads(output.read_text())["driver_readback"]["status"], "pending")
                return DRIVER_CSV

            stdout, stderr = io.StringIO(), io.StringIO()
            returned, failure = None, None
            with (mock.patch.object(launcher, "DIRECTORY", directory),
                  mock.patch.object(launcher, "checksum", side_effect=checksum),
                  mock.patch.object(Path, "stat", new=stat),
                  mock.patch.object(launcher.subprocess, "run", side_effect=run),
                  mock.patch.object(launcher.subprocess, "check_output", side_effect=driver),
                  mock.patch.object(preflight_cli.ctypes, "windll", SimpleNamespace(kernel32=SimpleNamespace(GlobalMemoryStatusEx=memory)), create=True),
                  mock.patch.object(preflight_cli.shutil, "disk_usage", return_value=SimpleNamespace(free=128 * 2**30)),
                  mock.patch.object(launcher.os, "link", side_effect=link) as linked,
                  mock.patch.object(launcher.os, "fsync", wraps=original_fsync) as synced,
                  mock.patch.object(launcher.os, "replace", wraps=original_replace) as replaced,
                  mock.patch.object(sys, "argv", ["synthetic-launcher", "--temporary-dir", str(base), "--repetition", "1"]),
                  contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr)):
                try:
                    returned = launcher.main()
                except (SystemExit, RuntimeError, OSError, subprocess.CalledProcessError) as error:
                    failure = error
            preserved = False
            if arrival:
                if kind == "directory":
                    preserved = occupied_path.is_dir() and (occupied_path / "retained.json").read_bytes() == original
                elif kind in ("live_symlink", "dangling_symlink"):
                    preserved = (occupied_path.is_symlink() and occupied_path.readlink() == target
                                 and (target.read_bytes() == original if kind == "live_symlink" else not target.exists()))
                else:
                    preserved = occupied_path.is_file() and occupied_path.read_bytes() == original
            unpublished = {path.name: json.loads(path.read_text()) for path in directory.glob("init-r1.json.unpublished-*.json")}
            return {"returned": returned, "failure": failure, "calls": calls,
                    "preserved": preserved, "unpublished": unpublished,
                    "output_exists": output.exists() or output.is_symlink(),
                    "output": json.loads(output.read_text()) if output.is_file() else None,
                    "stdout": stdout.getvalue(), "stderr": stderr.getvalue(),
                    "link_calls": linked.call_count, "replace_calls": replaced.call_count,
                    "fsync_calls": synced.call_count, "checked_runtime": checked_runtime,
                    "expected_runtime": [item["file"] for item in runtime_files],
                    "temporary_files": list(directory.glob("*.tmp")), "model_exists": model.exists()}

    def test_existing_result_or_preflight_paths_reject_before_any_launch(self):
        for arrival in ("early_output", "early_preflight"):
            for kind in ("file", "directory", "live_symlink", "dangling_symlink"):
                with self.subTest(arrival=arrival, kind=kind):
                    result = self.exercise(arrival=arrival, kind=kind)
                    self.assertIsInstance(result["failure"], SystemExit)
                    self.assertEqual(result["failure"].code, 2)
                    self.assertTrue(result["preserved"])
                    self.assertEqual(result["calls"], {"preflight": 0, "capacity": 0, "child": 0, "driver": 0})
                    self.assertEqual(result["checked_runtime"], [])
                    self.assertEqual(result["unpublished"], {})
                    self.assertEqual(result["stdout"], "")

    def test_preflight_paths_arriving_after_launcher_admission_stop_before_child(self):
        for arrival in ("before_preflight", "during_preflight"):
            for kind in ("file", "directory", "live_symlink", "dangling_symlink"):
                with self.subTest(arrival=arrival, kind=kind):
                    result = self.exercise(arrival=arrival, kind=kind)
                    self.assertIsInstance(result["failure"], subprocess.CalledProcessError)
                    self.assertEqual(result["failure"].returncode, 2)
                    self.assertIn("output exists; preserve observations and choose a fresh path", result["failure"].stderr)
                    self.assertTrue(result["preserved"])
                    self.assertEqual(result["calls"], {"preflight": 1, "capacity": int(arrival == "during_preflight"), "child": 0, "driver": 0})
                    self.assertEqual(result["checked_runtime"], result["expected_runtime"])
                    self.assertFalse(result["output_exists"])
                    self.assertEqual(result["unpublished"], {})
                    self.assertEqual(result["stdout"], "")

    def assert_unpublished(self, result, code, child_timeout):
        self.assertIsInstance(result["failure"], RuntimeError)
        self.assertIn("complete unpublished child capture retained", str(result["failure"]))
        self.assertIn("no telemetry or retry", str(result["failure"]))
        self.assertEqual(result["calls"], {"preflight": 1, "capacity": 1, "child": 1, "driver": 0})
        self.assertEqual(len(result["unpublished"]), 1)
        name, record = next(iter(result["unpublished"].items()))
        self.assertIn(name, str(result["failure"]))
        self.assertEqual(record["stdout"], "synthetic child stdout")
        self.assertIn("synthetic child stderr", record["stderr"])
        self.assertEqual(record["exit_code"], -1 if child_timeout else code)
        self.assertEqual(record["driver_readback"]["status"], "pending")
        self.assertEqual(record["native_status"], "timed_out" if child_timeout else ("completed" if code == 0 else "failed"))
        self.assertNotEqual(record["status"], "native_initialization_completed")
        with self.assertRaisesRegex(ValueError, "successful initialization-only"):
            capture.validate_capture(record)
        self.assertEqual(record["runtime_artifact_ledger_sha256"], launcher.RUNTIME_ARTIFACT_LEDGER_SHA256)
        self.assertEqual(result["checked_runtime"], result["expected_runtime"])
        self.assertEqual((result["link_calls"], result["replace_calls"], result["fsync_calls"]), (1, 0, 1))
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["temporary_files"], [])
        self.assertFalse(result["model_exists"])

    def test_result_arriving_during_child_preserves_both_observations_and_stops_telemetry(self):
        for kind in ("file", "directory", "live_symlink", "dangling_symlink"):
            for code, timeout in ((0, False), (7, False), (0, True)):
                with self.subTest(kind=kind, code=code, timeout=timeout):
                    result = self.exercise(arrival="during_child", kind=kind, code=code, child_timeout=timeout)
                    self.assert_unpublished(result, code, timeout)
                    self.assertTrue(result["preserved"])

    def test_unsupported_first_publication_retains_the_complete_child_without_fallback(self):
        for code, timeout in ((0, False), (7, False), (0, True)):
            with self.subTest(code=code, timeout=timeout):
                result = self.exercise(code=code, child_timeout=timeout, link_failure=True)
                self.assert_unpublished(result, code, timeout)
                self.assertFalse(result["output_exists"])

    def test_fresh_paths_recover_with_one_exclusive_publication_and_one_atomic_update(self):
        for code, timeout in ((0, False), (7, False), (0, True)):
            with self.subTest(code=code, timeout=timeout):
                result = self.exercise(code=code, child_timeout=timeout)
                self.assertIsNone(result["failure"])
                self.assertEqual(result["returned"], 0 if code == 0 and not timeout else 1)
                self.assertEqual(result["calls"], {"preflight": 1, "capacity": 1, "child": 1, "driver": 1})
                self.assertEqual((result["link_calls"], result["replace_calls"], result["fsync_calls"]), (1, 1, 2))
                self.assertEqual(result["output"]["driver_readback"]["status"], "completed")
                self.assertEqual(result["checked_runtime"], result["expected_runtime"])
                self.assertEqual(result["unpublished"], {})
                self.assertEqual(result["temporary_files"], [])
                self.assertFalse(result["model_exists"])


if __name__ == "__main__":
    unittest.main()
