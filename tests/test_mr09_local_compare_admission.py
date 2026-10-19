"""CPU-only prospective H1 admission tests; no estimator, model or GPU executes.

The fixture copies the reviewed current source, replays historical numerical
terms only, and builds a separately labeled synthetic current-package packet.
Tiny non-executable stand-ins and explicit model/ledger pin substitutions keep
every driver/preflight/native response mocked. No historical record is changed
or presented as a current estimator execution. Separate Python processes exercise
durable fences without ever reaching those responses.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, ExitStack
from datetime import datetime, timedelta, timezone
import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest import mock

SOURCE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_ROOT / "scripts"))
try:
    import mr09_local_compare_admission as admission
finally:
    sys.path.pop(0)
from test_mr09_local_compare_run import DRIVER, synthetic_record

kernel = admission.kernel
HISTORICAL = SOURCE_ROOT / "research/market/measurements/local-comparison-2026-10-19"


class ProspectiveAdmissionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        # Production resolves ROOT and admitted paths; keep every fixture and
        # mock in that physical namespace when the temporary parent is aliased.
        self.base = Path(temp.name).resolve()
        self.root = self.base / "reviewed-repository"
        self.root.mkdir()
        self.temporary = self.base / "synthetic-runtime"
        self.temporary.mkdir()
        self.sources = admission.REQUIRED_GUARD_SOURCES | admission.PACKAGE_SOURCES | kernel.REQUIRED_SOURCES
        for relative in self.sources:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE_ROOT / relative, target)
        (self.temporary / "native-init.exe").write_bytes(b"synthetic executable; never execute")
        self.estimator = self.temporary / "synthetic-estimator.exe"
        self.estimator.write_bytes(b"synthetic estimator; never execute")
        (self.temporary / "runtime").mkdir()
        (self.temporary / "runtime/fixture.dll").write_bytes(b"synthetic runtime; never load")
        self.model = self.temporary / kernel.MODEL
        self.model.write_bytes(b"synthetic artifact; not model weights")
        self.original_sha, self.original_stat = kernel.sha, Path.stat
        self.serial = 0
        self.directory = self.make_cohort()

        def fixture_sha(path):
            return kernel.MODEL_SHA if Path(path) == self.model else self.original_sha(path)

        def fixture_stat(path, *args, **kwargs):
            if path == self.model:
                return SimpleNamespace(st_size=270885952)
            return self.original_stat(path, *args, **kwargs)

        self.stack = self.enterContext(ExitStack())
        self.stack.enter_context(mock.patch.object(admission, "ROOT", self.root))
        self.stack.enter_context(mock.patch.object(kernel, "ROOT", self.root))
        self.stack.enter_context(mock.patch.object(kernel, "__file__", str(self.root / "scripts/mr09_local_compare_run.py")))
        self.stack.enter_context(mock.patch.object(kernel, "RUNTIME_LEDGER_SHA", self.original_sha(self.directory / "runtime-artifacts.json")))
        self.stack.enter_context(mock.patch.object(kernel, "sha", side_effect=fixture_sha))
        self.stack.enter_context(mock.patch.object(Path, "stat", new=fixture_stat))
        # Any unconfigured external invocation is a failing test, never a real
        # hardware or model action. Popen is used only for the Python witnesses.
        self.children = self.stack.enter_context(mock.patch.object(kernel.subprocess, "run", side_effect=AssertionError("unconfigured subprocess")))
        self.queries = self.stack.enter_context(mock.patch.object(kernel.subprocess, "check_output", side_effect=AssertionError("unconfigured driver query")))

    def make_cohort(self):
        self.serial += 1
        directory = self.root / "records" / f"synthetic-cohort-{self.serial}"
        directory.mkdir(parents=True)
        classification = "synthetic prospective H1 packet fixture; no estimator, model or GPU execution"
        (directory / "protocol.md").write_text(
            "# Synthetic future H1 fixture\n\nNo prediction or native execution.\n", encoding="utf-8")
        build = {"runtime_commit": kernel.RUNTIME_COMMIT, "harness_git_ref": "a" * 40,
                 "source_files": {name: self.original_sha(self.root / name) for name in kernel.REQUIRED_SOURCES},
                 "executables": {"native-init.exe": self.original_sha(self.temporary / "native-init.exe")}}
        self.save(directory / "build.json", build)
        self.save(directory / "runtime-artifacts.json", {"files": [
            {"file": "fixture.dll", "sha256": self.original_sha(self.temporary / "runtime/fixture.dll")} ]})
        source_manifest = kernel.read_json(self.root / admission.PACKAGE / "source-manifest.json")
        self.assertEqual(source_manifest["identity"], admission.ESTIMATOR_ID)
        package_commit = "c" * 40  # Synthetic join key, not a real source/review attribution.
        package_hashes = {name: self.original_sha(self.root / name) for name in admission.PACKAGE_SOURCES}
        candidate_sha = self.original_sha(self.estimator)
        self.save(directory / "estimator-source-preparation.json", {
            "classification": classification, "package_commit": package_commit,
            "upstream_commit": admission.UPSTREAM_COMMIT, "package_sha256": package_hashes})
        self.save(directory / "estimator-manifest.json", {
            "classification": classification, "manifest": {
                "upstream_commit": admission.UPSTREAM_COMMIT, "upstream_tree": admission.UPSTREAM_TREE,
                "package_sha256": source_manifest["package_sha256"],
                "candidate_executable_sha256": candidate_sha,
                "candidate_executable_bytes": self.estimator.stat().st_size}})
        # The preparation script itself is unchanged by the .2 parser fix.
        # This copied adaptation is a test input, not another preparation run.
        adaptation = kernel.read_json(HISTORICAL / "estimator-windows-adaptation.json")
        adaptation["classification"] = classification
        self.save(directory / "estimator-windows-adaptation.json", adaptation)
        self.save(directory / "semantic-review.json", {
            "classification": classification, "candidate_commit": package_commit,
            "reviewed_profile": admission.H1_PROFILE,
            "disposition": "synthetic boundary-test declaration; no real source/build approval"})
        self.save(directory / "estimator-profile.json", admission.H1_PROFILE)
        # Replay only the existing numerical/control fixture. The current
        # identity and synthetic receipt are not historical .2 predictions.
        prediction = kernel.read_json(HISTORICAL / "estimator-prediction.json")
        prediction.update(classification=classification, identity=admission.ESTIMATOR_ID)
        self.save(directory / "estimator-prediction.json", prediction)
        receipt = kernel.read_json(HISTORICAL / "prediction-receipt.json")
        frozen = datetime.now(timezone.utc) - timedelta(seconds=2)
        receipt.update(classification=classification,
                       estimator_package_commit=package_commit,
                       candidate_executable_sha256=candidate_sha,
                       raw_prediction_sha256=self.original_sha(directory / "estimator-prediction.json"),
                       stdin="synthetic fixture input; no estimator read",
                       aggregation_basis="retained .1 numerical fixture terms; no current estimator execution",
                       started_utc=(frozen - timedelta(seconds=2)).isoformat(),
                       finished_utc=(frozen - timedelta(seconds=1)).isoformat())
        self.save(directory / "prediction-receipt.json", receipt)
        freeze = {"classification": "synthetic future-freeze fixture; not evidence",
                  "observed_utc": frozen.isoformat(), "native_model_observations_before_freeze": 0,
                  "managed_device_estimate_bytes": receipt["managed_device_estimate_bytes"],
                  "prediction_file": (directory / "estimator-prediction.json").relative_to(self.root).as_posix()}
        self.save(directory / "prediction-freeze.json", freeze)
        self.refreeze(directory)
        return directory

    @staticmethod
    def save(path, value):
        path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def refreeze(self, directory=None):
        directory = directory or self.directory
        freeze = kernel.read_json(directory / "prediction-freeze.json")
        names = self.sources | {(directory / name).relative_to(self.root).as_posix() for name in admission.PACKET_FILES}
        freeze["files"] = {name: self.original_sha(self.root / name) for name in sorted(names)}
        self.save(directory / "prediction-freeze.json", freeze)

    def attempt(self, repetition=1, directory=None):
        return kernel.read_json((directory or self.directory) / f"H1-r{repetition}-attempt.json")

    def screen(self):
        return {"classification": "read-only capacity screen; not inference or a fit guarantee",
                "profile": "granite31", "observed_utc": datetime.now(timezone.utc).isoformat(),
                "thresholds": kernel.PREFLIGHT_THRESHOLDS, "methods": kernel.PREFLIGHT_METHODS,
                "observed": dict(kernel.PREFLIGHT_THRESHOLDS),
                "guards": {key: True for key in kernel.PREFLIGHT_THRESHOLDS},
                "status": "admitted_to_download_screen_only",
                "reason": "all screens satisfied; recheck before inference"}

    @contextmanager
    def hardware(self, *, native=None, driver=DRIVER, screen_mutation=None, native_gate=None):
        native = synthetic_record() if native is None else native
        counts = {"native": 0, "preflight": 0, "driver": 0}

        def reserved():
            lock = kernel.read_json(self.directory / admission.COHORT_LOCK)
            attempt = self.attempt(lock["repetition"])
            self.assertEqual(attempt["attempt_id"], lock["attempt_id"])
            self.assertEqual(attempt["status"], "pending")
            self.assertEqual(attempt["phase"], "guarded_kernel")
            self.assertEqual(set(attempt["guard_sources"]), admission.REQUIRED_GUARD_SOURCES)

        def run(argv, **kwargs):
            reserved()
            if len(argv) > 1 and argv[1] == str(self.root / "scripts/mr09_preflight.py"):
                counts["preflight"] += 1
                value = self.screen()
                if screen_mutation:
                    screen_mutation(value)
                kernel.write(Path(argv[argv.index("--output") + 1]), value)
                return subprocess.CompletedProcess(argv, 0, "", "")
            self.assertEqual(argv[0], str(self.temporary / "native-init.exe"))
            counts["native"] += 1
            if native_gate:
                native_gate()
            if isinstance(native, Exception):
                raise native
            return subprocess.CompletedProcess(argv, native["exit_code"], native["stdout"], native["stderr"])

        def query(argv, **kwargs):
            reserved()
            self.assertEqual(argv[0], "nvidia-smi")
            counts["driver"] += 1
            if isinstance(driver, Exception):
                raise driver
            return driver

        with (mock.patch.object(kernel.subprocess, "run", side_effect=run),
              mock.patch.object(kernel.subprocess, "check_output", side_effect=query)):
            yield counts

    def assert_failed_and_blocked(self, *, phase, error_type, repetition=1):
        attempt = self.attempt(repetition)
        self.assertEqual(attempt["status"], "failed")
        self.assertEqual(attempt["phase"], phase)
        self.assertEqual(attempt["error_type"], error_type)
        lock = (self.directory / admission.COHORT_LOCK).read_bytes()
        for later in (1, 2, 3):
            with self.assertRaises((ValueError, FileExistsError)):
                admission.run(self.temporary, later, self.directory)
        self.assertEqual((self.directory / admission.COHORT_LOCK).read_bytes(), lock)

    def test_complete_future_packet_runs_real_admission_and_three_serial_mocked_trials(self):
        with self.hardware() as counts:
            for repetition in (1, 2, 3):
                result = admission.run(self.temporary, repetition, self.directory)
                self.assertEqual(result["status"], "native_initialization_completed")
                attempt = self.attempt(repetition)
                self.assertEqual(attempt["status"], "completed")
                self.assertEqual(attempt["output_sha256"], kernel.sha(self.directory / f"H1-r{repetition}.json"))
                self.assertEqual(attempt["prediction_freeze_sha256"], result["prediction_freeze_sha256"])
                self.assertFalse((self.directory / admission.COHORT_LOCK).exists())
        self.assertEqual(counts, {"native": 3, "preflight": 3, "driver": 6})

    def test_each_missing_guard_packet_or_package_binding_stops_before_hardware(self):
        for relative in sorted(self.sources):
            with self.subTest(relative=relative):
                self.directory = self.make_cohort()
                freeze = kernel.read_json(self.directory / "prediction-freeze.json")
                del freeze["files"][relative]
                self.save(self.directory / "prediction-freeze.json", freeze)
                with self.assertRaisesRegex(ValueError, "complete source"):
                    admission.run(self.temporary, 1, self.directory)
                self.assert_failed_and_blocked(phase="source_closure", error_type="ValueError")
        for name in sorted(admission.PACKET_FILES):
            with self.subTest(name=name):
                self.directory = self.make_cohort()
                freeze = kernel.read_json(self.directory / "prediction-freeze.json")
                del freeze["files"][(self.directory / name).relative_to(self.root).as_posix()]
                self.save(self.directory / "prediction-freeze.json", freeze)
                with self.assertRaisesRegex(ValueError, "complete source"):
                    admission.run(self.temporary, 1, self.directory)
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_hash_drift_and_unbound_historical_freeze_stop_before_hardware(self):
        freeze = kernel.read_json(self.directory / "prediction-freeze.json")
        freeze["files"]["scripts/mr09_preflight.py"] = "0" * 64
        self.save(self.directory / "prediction-freeze.json", freeze)
        with self.assertRaisesRegex(ValueError, "artifact drift"):
            admission.run(self.temporary, 1, self.directory)
        self.assert_failed_and_blocked(phase="source_closure", error_type="ValueError")
        self.directory = self.make_cohort()
        shutil.copyfile(HISTORICAL / "prediction-freeze.json", self.directory / "prediction-freeze.json")
        with self.assertRaisesRegex(ValueError, "complete source"):
            admission.run(self.temporary, 1, self.directory)
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_historical_package_hashes_cannot_be_retagged_as_current(self):
        # Keep the current synthetic prediction identity and valid freeze,
        # but insert coherent old preparation/build/review identities. Old
        # package hashes must still fail before any external call.
        old = {}
        for name in ("estimator-source-preparation.json", "estimator-manifest.json", "semantic-review.json"):
            value = kernel.read_json(HISTORICAL / name)
            value["classification"] = "synthetic negative replay of historical package metadata"
            old[name] = value
            self.save(self.directory / name, value)
        receipt = kernel.read_json(self.directory / "prediction-receipt.json")
        receipt.update(estimator_package_commit=old["estimator-source-preparation.json"]["package_commit"],
                       candidate_executable_sha256=old["estimator-manifest.json"]["manifest"]["candidate_executable_sha256"])
        self.save(self.directory / "prediction-receipt.json", receipt)
        self.refreeze()
        with self.assertRaisesRegex(ValueError, "not completely bound"):
            admission.run(self.temporary, 1, self.directory)
        self.assert_failed_and_blocked(phase="source_closure", error_type="ValueError")
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_typed_profile_prediction_identity_and_controls_are_required(self):
        mutations = [
            ("estimator-profile.json", lambda p: p.update(sequence_capacity=True)),
            ("estimator-profile.json", lambda p: p.update(sequence_capacity=1.0)),
            ("estimator-profile.json", lambda p: p.update(context_size=512)),
            ("estimator-prediction.json", lambda p: p["declared_profile"].update(cache_key="q8_0")),
            ("estimator-prediction.json", lambda p: p.update(identity="upstream-release")),
            ("estimator-prediction.json", lambda p: p.update(identity="gguf-parser-go-v0.26.4+mr09-output.1-experimental")),
            ("estimator-prediction.json", lambda p: p.update(upstream_commit="b" * 40)),
            ("estimator-prediction.json", lambda p: p.update(artifact_sha256="b" * 64)),
            ("estimator-prediction.json", lambda p: p.update(artifact_bytes=270885952.0)),
            ("estimator-prediction.json", lambda p: p.update(declared_active_requests=True)),
            ("estimator-prediction.json", lambda p: p.pop("estimate")),
            ("estimator-prediction.json", lambda p: p["estimate"].update(contextSize=512)),
            ("estimator-prediction.json", lambda p: p["estimate"]["devices"][1].update(remote=True)),
            ("estimator-prediction.json", lambda p: p["estimate"]["devices"][1]["computation"].update(graph=True)),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name, mutation=mutate):
                self.directory = self.make_cohort()
                value = kernel.read_json(self.directory / name)
                mutate(value)
                self.save(self.directory / name, value)
                self.refreeze()
                with self.assertRaises((ValueError, KeyError)):
                    admission.run(self.temporary, 1, self.directory)
                self.assertEqual(self.attempt()["phase"], "source_closure")
                self.assertEqual(self.attempt()["status"], "failed")
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_receipt_build_review_package_and_chronology_must_join(self):
        mutations = [
            ("prediction-receipt.json", lambda p: p.update(raw_prediction_sha256="0" * 64)),
            ("prediction-receipt.json", lambda p: p.update(managed_device_estimate_bytes=1)),
            ("prediction-receipt.json", lambda p: p["extraction_terms_bytes"].update(footprint=True)),
            ("prediction-receipt.json", lambda p: p.update(exit_code=False)),
            ("prediction-receipt.json", lambda p: p.update(candidate_executable_sha256="0" * 64)),
            ("prediction-receipt.json", lambda p: p.update(estimator_package_commit="0" * 40)),
            ("prediction-receipt.json", lambda p: p.update(native_execution="completed")),
            ("prediction-receipt.json", lambda p: p.update(finished_utc=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())),
            ("estimator-manifest.json", lambda p: p["manifest"].update(upstream_tree="0" * 40)),
            ("estimator-manifest.json", lambda p: p["manifest"]["package_sha256"].pop(admission.PREPARER)),
            ("estimator-source-preparation.json", lambda p: p["package_sha256"].pop(admission.PREPARER)),
            ("estimator-windows-adaptation.json", lambda p: p.update(original_runner_sha256="0" * 64)),
            ("estimator-windows-adaptation.json", lambda p: p.update(unified_diff="")),
            ("semantic-review.json", lambda p: p.update(candidate_commit="0" * 40)),
            ("semantic-review.json", lambda p: p["reviewed_profile"].update(context_size=512)),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name, mutation=mutate):
                self.directory = self.make_cohort()
                value = kernel.read_json(self.directory / name)
                mutate(value)
                self.save(self.directory / name, value)
                self.refreeze()
                with self.assertRaises(ValueError):
                    admission.run(self.temporary, 1, self.directory)
                self.assertEqual(self.attempt()["phase"], "source_closure")
        for field, value in (("native_model_observations_before_freeze", False),
                             ("native_model_observations_before_freeze", 1),
                             ("managed_device_estimate_bytes", 300885760.0),
                             ("observed_utc", (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())):
            with self.subTest(field=field, value=value):
                self.directory = self.make_cohort()
                freeze = kernel.read_json(self.directory / "prediction-freeze.json")
                freeze[field] = value
                self.save(self.directory / "prediction-freeze.json", freeze)
                with self.assertRaises(ValueError):
                    admission.run(self.temporary, 1, self.directory)
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_missing_temporary_directory_and_initial_admission_failure_are_retained(self):
        with self.assertRaises(FileNotFoundError):
            admission.run(self.base / "absent-private-path", 1, self.directory)
        self.assert_failed_and_blocked(phase="temporary_directory", error_type="FileNotFoundError")
        self.assertNotIn("absent-private-path", (self.directory / "H1-r1-attempt.json").read_text())
        self.directory = self.make_cohort()
        with mock.patch.object(kernel, "admit", side_effect=ValueError("sensitive input /private/model")):
            with self.assertRaises(ValueError):
                admission.run(self.temporary, 1, self.directory)
        self.assert_failed_and_blocked(phase="guarded_kernel", error_type="ValueError")
        self.assertNotIn("sensitive", (self.directory / "H1-r1-attempt.json").read_text())
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_wrong_driver_and_initial_query_exception_are_durable_without_child(self):
        for driver in (DRIVER.replace("5070 Ti", "5090"), DRIVER.replace("610.88", "595.97"),
                       subprocess.CalledProcessError(7, ["private-driver-argv"], output="private-output")):
            with self.subTest(driver=type(driver).__name__):
                self.directory = self.make_cohort()
                with self.hardware(driver=driver) as counts:
                    with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                        admission.run(self.temporary, 1, self.directory)
                self.assertEqual(counts, {"native": 0, "preflight": 0, "driver": 1})
                self.assert_failed_and_blocked(phase="guarded_kernel", error_type="CalledProcessError" if isinstance(driver, Exception) else "ValueError")
                self.assertNotIn("private-", (self.directory / "H1-r1-attempt.json").read_text())

    def test_failed_preflight_never_reaches_mocked_native_child(self):
        for mutation in (lambda p: p.update(profile="other"),
                         lambda p: p["guards"].update(nvidia_smi_free_mib=False),
                         lambda p: p.update(observed_utc=(datetime.now(timezone.utc) - timedelta(seconds=31)).isoformat())):
            with self.subTest(mutation=mutation):
                self.directory = self.make_cohort()
                with self.hardware(screen_mutation=mutation) as counts:
                    with self.assertRaises(ValueError):
                        admission.run(self.temporary, 1, self.directory)
                self.assertEqual(counts, {"native": 0, "preflight": 1, "driver": 1})
                self.assertTrue((self.directory / "H1-r1-preflight.json").is_file())
                self.assert_failed_and_blocked(phase="guarded_kernel", error_type="ValueError")

    def test_simultaneous_same_and_distinct_repetitions_allow_only_one_mocked_native_call(self):
        entered, release = threading.Event(), threading.Event()

        def hold_native():
            entered.set()
            if not release.wait(5):
                raise AssertionError("test did not release synthetic native response")

        with self.hardware(native_gate=hold_native) as counts, ThreadPoolExecutor(max_workers=1) as workers:
            winner = workers.submit(admission.run, self.temporary, 1, self.directory)
            try:
                self.assertTrue(entered.wait(5), "first invocation never reached mocked native response")
                original = (self.directory / "H1-r1-attempt.json").read_bytes()
                for repetition in (1, 2, 3):
                    with self.assertRaises((ValueError, FileExistsError)):
                        admission.run(self.temporary, repetition, self.directory)
                self.assertEqual((self.directory / "H1-r1-attempt.json").read_bytes(), original)
                self.assertFalse((self.directory / "H1-r2-attempt.json").exists())
            finally:
                release.set()
            self.assertEqual(winner.result(timeout=5)["status"], "native_initialization_completed")
        self.assertEqual(counts, {"native": 1, "preflight": 1, "driver": 2})

    def test_failed_native_result_stays_retained_and_blocks_every_later_repetition(self):
        native = synthetic_record()
        native["exit_code"] = 8
        with self.hardware(native=native) as counts:
            result = admission.run(self.temporary, 1, self.directory)
        self.assertEqual(result["status"], "qualification_failure")
        self.assertEqual(kernel.read_json(self.directory / "H1-r1.json")["stdout"], native["stdout"])
        self.assertEqual(self.attempt()["status"], "failed")
        self.assertEqual(self.attempt()["native_status"], "qualification_failure")
        self.assertTrue((self.directory / admission.COHORT_LOCK).is_file())
        for later in (1, 2, 3):
            with self.assertRaises((ValueError, FileExistsError)):
                admission.run(self.temporary, later, self.directory)
        self.assertEqual(counts["native"], 1)

    def test_predecessors_need_terminal_receipts_exact_output_and_matching_freeze(self):
        for mutation in (lambda d: (d / "H1-r1-attempt.json").unlink(),
                         lambda d: self.mutate_attempt(d, status="pending"),
                         lambda d: self.mutate_attempt(d, schema_version=True),
                         lambda d: self.mutate_attempt(d, prediction_freeze_sha256="0" * 64),
                         lambda d: (d / "H1-r1.json").write_text('{"status":"native_initialization_completed"}')):
            with self.subTest(mutation=mutation):
                self.directory = self.make_cohort()
                with self.hardware():
                    admission.run(self.temporary, 1, self.directory)
                mutation(self.directory)
                with mock.patch.object(kernel, "run") as child:
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        admission.run(self.temporary, 2, self.directory)
                child.assert_not_called()
                self.assertEqual(self.attempt(2)["phase"], "prior_attempts")
                self.assertEqual(self.attempt(2)["status"], "failed")
        self.directory = self.make_cohort()
        shutil.copyfile(HISTORICAL / "H1-r1.json", self.directory / "H1-r1.json")
        original = (self.directory / "H1-r1.json").read_bytes()
        with self.assertRaises(FileNotFoundError):
            admission.run(self.temporary, 2, self.directory)
        self.assertEqual((self.directory / "H1-r1.json").read_bytes(), original)

    def mutate_attempt(self, directory, **updates):
        attempt = self.attempt(directory=directory)
        attempt.update(updates)
        self.save(directory / "H1-r1-attempt.json", attempt)

    def test_reservation_fsync_and_pending_write_failures_keep_a_blocking_fence(self):
        original_fsync = os.fsync
        for fail_call in (1, 2):
            with self.subTest(fsync_call=fail_call):
                self.directory = self.make_cohort()
                calls = 0

                def failing_fsync(fd):
                    nonlocal calls
                    calls += 1
                    if calls == fail_call:
                        raise OSError("synthetic disk sync failure")
                    return original_fsync(fd)

                with mock.patch.object(admission.os, "fsync", side_effect=failing_fsync):
                    with self.assertRaises(OSError):
                        admission.run(self.temporary, 1, self.directory)
                self.assertTrue((self.directory / admission.COHORT_LOCK).exists())
                with self.assertRaises((ValueError, FileExistsError)):
                    admission.run(self.temporary, 2, self.directory)
        self.directory = self.make_cohort()
        with mock.patch.object(kernel, "write", side_effect=OSError("synthetic disk full")):
            with self.assertRaises(OSError):
                admission.run(self.temporary, 1, self.directory)
        self.assertEqual(self.attempt()["status"], "pending")
        self.assertTrue((self.directory / admission.COHORT_LOCK).exists())
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_terminal_receipt_write_failure_cannot_release_fence_or_erase_child(self):
        original_write = kernel.write

        def fail_terminal(path, value):
            if path.name.endswith("-attempt.json") and value.get("status") in ("completed", "failed"):
                raise OSError("synthetic terminal receipt persistence failure")
            return original_write(path, value)

        with self.hardware() as counts, mock.patch.object(kernel, "write", side_effect=fail_terminal):
            with self.assertRaises(OSError):
                admission.run(self.temporary, 1, self.directory)
        self.assertEqual(self.attempt()["status"], "pending")
        self.assertEqual(self.attempt()["phase"], "result_binding")
        self.assertEqual(kernel.read_json(self.directory / "H1-r1.json")["status"], "native_initialization_completed")
        self.assertTrue((self.directory / admission.COHORT_LOCK).exists())
        with self.assertRaises(FileExistsError):
            admission.run(self.temporary, 2, self.directory)
        self.assertEqual(counts["native"], 1)

    def python_witness(self, mode, repetition=1):
        # This program can only call a mocked kernel or exit during source
        # admission. It contains no model/GPU/estimator invocation or download.
        source = """
import json, os, pathlib, sys, time
sys.path.insert(0, sys.argv[1])
import mr09_local_compare_admission as a
root, directory, temporary = [pathlib.Path(p) for p in sys.argv[2:5]]
mode, repetition = sys.argv[5], int(sys.argv[6])
a.ROOT = a.kernel.ROOT = root
def no_external(*args, **kwargs):
    raise AssertionError('CPU fence witness forbids external calls')
a.kernel.subprocess.run = a.kernel.subprocess.check_output = no_external
if mode == 'crash_before_kernel':
    a.guard_source_closure = lambda directory: os._exit(73)
elif mode == 'hold':
    def hold(directory):
        (directory / 'witness-reserved').write_text('synthetic CPU witness')
        deadline = time.monotonic() + 5
        while not (directory / 'witness-release').exists():
            if time.monotonic() > deadline:
                raise TimeoutError('synthetic witness hold expired')
            time.sleep(0.01)
        raise ValueError('synthetic witness stops before kernel')
    a.guard_source_closure = hold
elif mode == 'crash_after_child_record':
    def synthetic_kernel(temporary, repetition, directory):
        a.kernel.write(directory / f'H1-r{repetition}.json',
                       {'classification':'synthetic CPU witness; no native child',
                        'status':'post_run_telemetry_pending'})
        os._exit(74)
    a.kernel.run = synthetic_kernel
else:
    a.guard_source_closure = no_external
try:
    a.run(temporary, repetition, directory)
except BaseException as error:
    print(type(error).__name__, flush=True)
    sys.exit(2)
raise AssertionError('witness must never complete a native run')
"""
        process = subprocess.Popen([sys.executable, "-c", source, str(SOURCE_ROOT / "scripts"),
                                    str(self.root), str(self.directory), str(self.temporary), mode, str(repetition)],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)

        def cleanup():
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

        self.addCleanup(cleanup)
        return process

    def test_process_death_preserves_pending_fence_before_kernel_and_after_child_record(self):
        for mode, code, phase, output_exists in (("crash_before_kernel", 73, "source_closure", False),
                                                ("crash_after_child_record", 74, "guarded_kernel", True)):
            with self.subTest(mode=mode):
                self.directory = self.make_cohort()
                process = self.python_witness(mode)
                stdout, stderr = process.communicate(timeout=5)
                self.assertEqual((process.returncode, stdout, stderr), (code, "", ""))
                self.assertEqual(self.attempt()["status"], "pending")
                self.assertEqual(self.attempt()["phase"], phase)
                self.assertEqual(self.attempt()["native_status"], "not_recorded")
                self.assertEqual((self.directory / "H1-r1.json").exists(), output_exists)
                self.assertTrue((self.directory / admission.COHORT_LOCK).is_file())
                for repetition in (1, 2, 3):
                    with self.assertRaises((ValueError, FileExistsError)):
                        admission.run(self.temporary, repetition, self.directory)
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_separate_processes_share_exclusive_cohort_reservation(self):
        winner = self.python_witness("hold")
        deadline = time.monotonic() + 5
        while not (self.directory / "witness-reserved").exists() and winner.poll() is None:
            if time.monotonic() > deadline:
                self.fail("CPU witness never reserved the cohort")
            time.sleep(0.01)
        self.assertTrue((self.directory / "witness-reserved").exists())
        original = (self.directory / "H1-r1-attempt.json").read_bytes()
        for repetition, error in ((1, "ValueError"), (2, "FileExistsError")):
            contender = self.python_witness("must_not_enter", repetition)
            stdout, stderr = contender.communicate(timeout=5)
            self.assertEqual((contender.returncode, stdout.strip(), stderr), (2, error, ""))
        self.assertEqual((self.directory / "H1-r1-attempt.json").read_bytes(), original)
        self.assertFalse((self.directory / "H1-r2-attempt.json").exists())
        (self.directory / "witness-release").write_text("release CPU test only")
        stdout, stderr = winner.communicate(timeout=5)
        self.assertEqual((winner.returncode, stdout.strip(), stderr), (2, "ValueError", ""))
        self.assert_failed_and_blocked(phase="source_closure", error_type="ValueError")

    def test_existing_records_and_foreign_reservation_are_never_overwritten(self):
        for name in ("H1-r1.json", "H1-r1-preflight.json", "H1-r1-attempt.json", admission.COHORT_LOCK):
            with self.subTest(name=name):
                self.directory = self.make_cohort()
                path = self.directory / name
                path.write_bytes(b"existing record; preserve exact bytes")
                with self.assertRaises((ValueError, FileExistsError)):
                    admission.run(self.temporary, 1, self.directory)
                self.assertEqual(path.read_bytes(), b"existing record; preserve exact bytes")
        self.children.assert_not_called()
        self.queries.assert_not_called()

    def test_changed_lock_during_completion_remains_blocked_and_retains_child(self):
        foreign = {"classification": "synthetic foreign reservation"}

        def replace_lock():
            self.save(self.directory / admission.COHORT_LOCK, foreign)

        # Replace only when release is attempted, after all hardware mocks have
        # observed the original reservation. The foreign record must survive.
        release = admission.release_owned_lock

        def changed_release(path, identity):
            replace_lock()
            return release(path, identity)

        with self.hardware(), mock.patch.object(admission, "release_owned_lock", side_effect=changed_release):
            with self.assertRaises(ValueError):
                admission.run(self.temporary, 1, self.directory)
        self.assertEqual(kernel.read_json(self.directory / admission.COHORT_LOCK), foreign)
        self.assertEqual(self.attempt()["status"], "failed")
        self.assertEqual(self.attempt()["phase"], "reservation_release")
        self.assertEqual(kernel.read_json(self.directory / "H1-r1.json")["status"], "native_initialization_completed")

    def test_cli_sanitizes_exception_text_and_does_not_emit_private_traceback(self):
        argv = ["admission", "--temporary-dir", str(self.temporary), "--cohort-dir", str(self.directory), "--repetition", "1"]
        with (mock.patch.object(sys, "argv", argv),
              mock.patch.object(admission, "run", side_effect=subprocess.CalledProcessError(7, ["private-argv"], output="private-output")),
              mock.patch("sys.stdout", new_callable=io.StringIO) as output,
              mock.patch("sys.stderr", new_callable=io.StringIO) as error):
            self.assertEqual(admission.main(), 1)
        self.assertEqual(json.loads(output.getvalue()), {"status": "admission_failed", "error_type": "CalledProcessError"})
        self.assertEqual(error.getvalue(), "")


class AdmissionTemporaryRootTests(unittest.TestCase):
    def test_original_admission_guards_under_aliased_temporary_root(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            physical = base / "physical"
            physical.mkdir()
            alias = base / "alias"
            try:
                alias.symlink_to(physical, target_is_directory=True)
            except OSError as error:
                if os.name == "nt" and getattr(error, "winerror", None) == 1314:
                    self.skipTest("directory symlink fixture unavailable "
                                  "(Windows privilege not held; winerror 1314)")
                raise
            self.assertNotEqual(alias, alias.resolve())
            self.assertEqual(alias.resolve(), physical)
            methods = (
                "test_complete_future_packet_runs_real_admission_and_three_serial_mocked_trials",
                "test_each_missing_guard_packet_or_package_binding_stops_before_hardware",
                "test_failed_preflight_never_reaches_mocked_native_child",
                "test_wrong_driver_and_initial_query_exception_are_durable_without_child",
                "test_failed_native_result_stays_retained_and_blocks_every_later_repetition",
            )
            # Run the original assertions with fresh fixtures through the same
            # directory-alias condition that /var supplies on macOS. Each case
            # retains its own cleanup and unconfigured-external-call rejection.
            with mock.patch.object(tempfile, "tempdir", str(alias)):
                for method in methods:
                    with self.subTest(admission_case=method):
                        result = unittest.TestResult()
                        ProspectiveAdmissionTests(method).run(result)
                        self.assertEqual(result.testsRun, 1)
                        self.assertEqual(result.skipped, [])
                        self.assertTrue(result.wasSuccessful(), result.failures + result.errors)


if __name__ == "__main__":
    unittest.main()
