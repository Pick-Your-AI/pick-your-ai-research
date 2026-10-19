"""CPU-only completed-record retention fixtures; never measurement evidence."""

import contextlib
import copy
import errno
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MODULES = []
for name in ("mr09_measure", "mr09_granite31_measure"):
    spec = importlib.util.spec_from_file_location(name + "_publication", ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    MODULES.append(module)


class CompletedResultPublicationTests(unittest.TestCase):
    @contextlib.contextmanager
    def exercise(self, module, *, prepare=False, status="success", occupant=None,
                 early=False, fault=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            model = root / "model"
            output = root / "mr09-M1-r1.json"
            original = b'{"classification":"synthetic occupying observation"}\n'
            target = root / "occupying-target.json"
            if occupant in ("link", "dangling"):
                probe = root / "link-capability-probe"
                try:
                    probe.symlink_to(target)
                except OSError as error:
                    if sys.platform == "win32" and getattr(error, "winerror", None) == 1314:
                        self.skipTest("symbolic-link fixture unavailable (Windows privilege not held; winerror 1314)")
                    raise
                else:
                    probe.unlink()

            def occupy():
                if occupant == "file":
                    output.write_bytes(original)
                elif occupant == "directory":
                    output.mkdir()
                    (output / "observation.json").write_bytes(original)
                elif occupant in ("link", "dangling"):
                    if occupant == "link":
                        target.write_bytes(original)
                    output.symlink_to(target)

            if early:
                occupy()
            record = {
                "classification": "synthetic; no native or model execution",
                "attempt": "distinct completed attempt",
                "failure": "runtime_error" if status == "runtime_error" else None,
                "failure_phase": "prefill" if status == "runtime_error" else None,
                "phases": [{"phase": "synthetic", "peak_allocated_bytes": 17}],
                "locators": [str(model), str(ROOT), str(Path(sys.executable).resolve()),
                             {"home": str(Path.home())}],
            }
            if status is not None:
                record["status"] = status
            expected = module.sanitized(copy.deepcopy(record), SimpleNamespace(model_dir=model))
            screen = {"guards": {"nvidia_smi_free_mib": True,
                                  "available_host_ram_bytes": True,
                                  "temporary_volume_free_bytes": True}}
            granite = module is MODULES[1]
            if granite:
                expected["fresh_preflight"] = screen
                if not prepare:
                    expected["dense_instrument_source_sha256"] = hashlib.sha256(
                        (ROOT / "scripts/mr09_measure.py").read_bytes()).hexdigest()

            def action(*args):
                if not early:
                    occupy()
                return copy.deepcopy(record)

            def preflight(argv, **kwargs):
                self.assertTrue(granite)
                self.assertEqual(Path(argv[1]).name, "mr09_preflight.py")
                self.assertEqual(kwargs, {"check": True})
                (root / "granite31-preflight-1.json").write_text(json.dumps(screen), encoding="utf-8")
                return SimpleNamespace(returncode=0)

            stdout, stderr = io.StringIO(), io.StringIO()
            argv = [str(module.__file__), "--model-dir", str(model), "--output", str(output)]
            if prepare:
                argv.append("--prepare")
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(sys, "argv", argv))
                download = stack.enter_context(patch.object(module, "prepare", side_effect=action))
                measure = stack.enter_context(patch.object(module, "measurement", side_effect=action))
                child = stack.enter_context(patch.object(module.subprocess, "run", side_effect=preflight))
                stack.enter_context(patch.object(module.subprocess, "check_output", side_effect=AssertionError("no driver")))
                stack.enter_context(patch.object(module.subprocess, "Popen", side_effect=AssertionError("no child")))
                stack.enter_context(patch.object(module.urllib.request, "urlopen", side_effect=AssertionError("no network")))
                stack.enter_context(contextlib.redirect_stdout(stdout))
                stack.enter_context(contextlib.redirect_stderr(stderr))
                if fault:
                    fault(stack, root, output, expected)
                try:
                    code = module.main()
                except SystemExit as error:
                    code = error.code
            expected_calls = int(not early)
            self.assertEqual(download.call_count, expected_calls * int(prepare))
            self.assertEqual(measure.call_count, expected_calls * int(not prepare))
            self.assertEqual(child.call_count, expected_calls * int(granite))
            self.assertFalse(model.exists())
            yield SimpleNamespace(root=root, output=output, target=target, original=original,
                                  expected=expected, code=code, stdout=stdout.getvalue(),
                                  stderr=stderr.getvalue())

    def recovery(self, case):
        files = list(case.root.glob(".mr09-unpublished-*.json"))
        self.assertEqual(len(files), 1, "the completed attempt needs one distinct retained file")
        self.assertEqual(json.loads(files[0].read_text(encoding="utf-8")), case.expected)
        self.assertIn(str(files[0]), case.stderr)
        self.assertNotIn(str(case.root / "model"), files[0].read_text(encoding="utf-8"))
        self.assertIn("complete unpublished result retained at", case.stderr)
        self.assertIn("no retry", case.stderr)
        self.assertEqual(case.code, 2)
        self.assertEqual(case.stdout, "")
        return files[0]

    def assert_occupant(self, case, kind):
        if kind == "directory":
            self.assertTrue(case.output.is_dir())
            self.assertEqual((case.output / "observation.json").read_bytes(), case.original)
        elif kind == "dangling":
            self.assertTrue(case.output.is_symlink())
            self.assertEqual(case.output.readlink(), case.target)
            self.assertFalse(case.target.exists())
        else:
            self.assertEqual(case.output.read_bytes(), case.original)
            if kind == "link":
                self.assertTrue(case.output.is_symlink())
                self.assertEqual(case.output.readlink(), case.target)
                self.assertEqual(case.target.read_bytes(), case.original)

    def test_late_collisions_retain_complete_sanitized_success_and_failure_for_both_actions(self):
        for module in MODULES:
            for prepare in (False, True):
                for status in ("success", "runtime_error"):
                    for kind in ("file", "directory", "link", "dangling"):
                        with self.subTest(module=module.__name__, prepare=prepare, status=status, kind=kind):
                            with self.exercise(module, prepare=prepare, status=status, occupant=kind) as case:
                                retained = self.recovery(case)
                                self.assert_occupant(case, kind)
                                self.assertIn("output exists; preserve observations and choose a fresh path", case.stderr)
                                self.assertNotIn(retained, case.root.glob("mr09-*-r*.json"))

    def test_fresh_results_keep_status_content_and_leave_no_recovery_duplicate(self):
        for module in MODULES:
            for prepare in (False, True):
                for status in (None, "success", "runtime_error", "unsupported", "unexecuted"):
                    with self.subTest(module=module.__name__, prepare=prepare, status=status):
                        with self.exercise(module, prepare=prepare, status=status) as case:
                            self.assertEqual(case.code, int(status == "runtime_error"))
                            self.assertEqual(json.loads(case.output.read_text(encoding="utf-8")), case.expected)
                            self.assertEqual(list(case.root.glob(".mr09-unpublished-*")), [])
                            self.assertEqual(json.loads(case.stdout)["status"], status or "prepared")
                            self.assertEqual(case.stderr, "")

    def test_initial_occupants_stop_before_actions_and_recovery_creation(self):
        for module in MODULES:
            for prepare in (False, True):
                for kind in ("file", "directory", "link", "dangling"):
                    with self.subTest(module=module.__name__, prepare=prepare, kind=kind):
                        with self.exercise(module, prepare=prepare, occupant=kind, early=True) as case:
                            self.assertEqual(case.code, 2)
                            self.assertEqual(case.stdout, "")
                            self.assertEqual(list(case.root.glob(".mr09-unpublished-*")), [])
                            self.assert_occupant(case, kind)

    def test_noncollision_publication_failure_retains_record_without_retry(self):
        def fail(stack, root, output, expected):
            stack.enter_context(patch("os.link", side_effect=OSError(errno.EIO, "synthetic publication failure")))

        for module in MODULES:
            for prepare in (False, True):
                for status in ("success", "runtime_error"):
                    with self.subTest(module=module.__name__, prepare=prepare, status=status):
                        with self.exercise(module, prepare=prepare, status=status, fault=fail) as case:
                            self.recovery(case)
                            self.assertFalse(case.output.exists())
                            self.assertIn("result publication failed", case.stderr)

    def test_completed_file_is_synced_before_no_replace_publication(self):
        real_link, real_sync = os.link, os.fsync
        for module in MODULES:
            with self.subTest(module=module.__name__):
                observed = []

                def inspect(stack, root, output, expected):
                    sync = stack.enter_context(patch("os.fsync", wraps=real_sync))

                    def link(source, destination):
                        self.assertEqual(sync.call_count, 1)
                        self.assertEqual(Path(destination), output)
                        self.assertEqual(json.loads(Path(source).read_text(encoding="utf-8")), expected)
                        self.assertEqual(list(root.glob("mr09-*-r*.json")), [])
                        observed.append(Path(source))
                        return real_link(source, destination)

                    stack.enter_context(patch("os.link", side_effect=link))

                with self.exercise(module, fault=inspect) as case:
                    self.assertEqual(case.code, 0)
                    self.assertEqual(len(observed), 1)
                    self.assertFalse(observed[0].exists())

    def test_write_flush_and_sync_failures_never_claim_complete_recovery_or_publish(self):
        real_fdopen = os.fdopen
        for module in MODULES:
            for phase in ("write", "flush", "fsync"):
                with self.subTest(module=module.__name__, phase=phase):
                    links = []

                    def fail(stack, root, output, expected):
                        links.append(stack.enter_context(patch("os.link")))
                        if phase == "fsync":
                            stack.enter_context(patch("os.fsync", side_effect=OSError(errno.EIO, "synthetic sync failure")))
                            return

                        class FaultyStream:
                            def __init__(self, *args, **kwargs):
                                self.stream = real_fdopen(*args, **kwargs)

                            def __enter__(self):
                                return self

                            def __exit__(self, *args):
                                return self.stream.__exit__(*args)

                            def write(self, text):
                                if phase == "write":
                                    self.stream.write(text[:9])
                                    self.stream.flush()
                                    raise OSError(errno.ENOSPC, "synthetic partial write")
                                return self.stream.write(text)

                            def flush(self):
                                raise OSError(errno.EIO, "synthetic flush failure")

                        stack.enter_context(patch("os.fdopen", side_effect=FaultyStream))

                    with self.exercise(module, fault=fail) as case:
                        self.assertEqual(case.code, 2)
                        self.assertEqual(case.stdout, "")
                        self.assertFalse(case.output.exists())
                        links[0].assert_not_called()
                        retained = list(case.root.glob(".mr09-unpublished-*"))
                        self.assertEqual(len(retained), 1)
                        self.assertIn(str(retained[0]), case.stderr)
                        self.assertIn("no complete recovery record is confirmed", case.stderr)
                        self.assertNotIn("complete unpublished result retained at", case.stderr)
                        if phase == "write":
                            with self.assertRaises(json.JSONDecodeError):
                                json.loads(retained[0].read_text(encoding="utf-8"))

    def test_failure_before_temporary_creation_reports_no_recovery_file(self):
        def fail(stack, root, output, expected):
            stack.enter_context(patch("tempfile.mkstemp", side_effect=OSError(errno.ENOSPC, "synthetic creation failure")))

        for module in MODULES:
            with self.subTest(module=module.__name__):
                with self.exercise(module, fault=fail) as case:
                    self.assertEqual(case.code, 2)
                    self.assertEqual(case.stdout, "")
                    self.assertFalse(case.output.exists())
                    self.assertEqual(list(case.root.glob(".mr09-unpublished-*")), [])
                    self.assertIn("no recovery file was created", case.stderr)

    def test_cleanup_failure_identifies_published_result_and_retained_duplicate(self):
        real_unlink = Path.unlink

        def fail(stack, root, output, expected):
            def unlink(path, *args, **kwargs):
                if path.name.startswith(".mr09-unpublished-"):
                    raise OSError(errno.EACCES, "synthetic cleanup failure")
                return real_unlink(path, *args, **kwargs)
            stack.enter_context(patch.object(Path, "unlink", unlink))

        for module in MODULES:
            with self.subTest(module=module.__name__):
                with self.exercise(module, fault=fail) as case:
                    self.assertEqual(case.code, 2)
                    self.assertEqual(case.stdout, "")
                    self.assertEqual(json.loads(case.output.read_text()), case.expected)
                    retained = list(case.root.glob(".mr09-unpublished-*"))
                    self.assertEqual(len(retained), 1)
                    self.assertEqual(retained[0].read_bytes(), case.output.read_bytes())
                    self.assertIn("result was published", case.stderr)
                    self.assertIn(str(case.output), case.stderr)
                    self.assertIn(str(retained[0]), case.stderr)
                    self.assertIn("cleanup failed; no retry", case.stderr)


    def test_removed_temporary_name_after_link_keeps_the_published_success(self):
        real_link = os.link
        for module in MODULES:
            with self.subTest(module=module.__name__):
                linked = []

                def remove_extra_name(stack, root, output, expected):
                    def link(source, destination):
                        result = real_link(source, destination)
                        Path(source).unlink()
                        linked.append(Path(destination))
                        return result
                    stack.enter_context(patch("os.link", side_effect=link))

                with self.exercise(module, fault=remove_extra_name) as case:
                    self.assertEqual(linked, [case.output])
                    self.assertEqual(case.code, 0)
                    self.assertEqual(json.loads(case.output.read_text()), case.expected)
                    self.assertEqual(list(case.root.glob(".mr09-unpublished-*")), [])
                    self.assertEqual(json.loads(case.stdout)["status"], "success")
                    self.assertEqual(case.stderr, "")


if __name__ == "__main__":
    unittest.main()
