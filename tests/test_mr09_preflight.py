"""Direct capacity-screen CLI tests with CPU-only operating-system doubles."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from mr09_fixture_support import symlink_or_skip

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import mr09_preflight as screen
finally:
    sys.path.pop(0)


class PreflightOutputPreservationTests(unittest.TestCase):
    def exercise(self, *, preserve=True, occupied=None, arrival=False,
                 profile="granite31", smi="8192\n", serialization_failure=False):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "synthetic-screen.json"
            target = directory / "synthetic-link-target.json"
            original = b'{"synthetic":"retained original screen"}\n'
            prepared_link = directory / "synthetic-pending-link"
            if occupied in ("live_symlink", "dangling_symlink"):
                # Capability skips must happen outside the producer's broad
                # error handler, while the output still arrives at its hook.
                symlink_or_skip(prepared_link, target)

            def occupy():
                if occupied == "file":
                    output.write_bytes(original)
                elif occupied == "directory":
                    output.mkdir()
                    (output / "retained.json").write_bytes(original)
                else:
                    if occupied == "live_symlink":
                        target.write_bytes(original)
                    self.assertFalse(output.exists() or output.is_symlink(),
                                     "synthetic arrival must not overwrite a prior entry")
                    prepared_link.rename(output)

            if occupied and not arrival:
                occupy()

            def run(argv, **kwargs):
                self.assertEqual(argv, ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"])
                self.assertEqual(kwargs["timeout"], 30)
                if occupied and arrival:
                    occupy()
                return subprocess.CompletedProcess(argv, 0, smi, "")

            def memory(pointer):
                pointer._obj.ullAvailPhys = 64 * 2**30
                return 1

            argv = ["synthetic-preflight", "--temporary-dir", str(directory),
                    "--output", str(output), "--profile", profile]
            if preserve:
                argv.append("--preserve-output")
            stdout, stderr = io.StringIO(), io.StringIO()
            returned, failure = None, None
            with (mock.patch.object(sys, "argv", argv),
                  mock.patch.object(screen.subprocess, "run", side_effect=run) as gpu,
                  mock.patch.object(screen.ctypes, "windll", SimpleNamespace(kernel32=SimpleNamespace(
                      GlobalMemoryStatusEx=mock.Mock(side_effect=memory))), create=True) as windows,
                  mock.patch.object(screen.shutil, "disk_usage", return_value=SimpleNamespace(free=128 * 2**30)) as disk,
                  contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr),
                  contextlib.ExitStack() as stack):
                if serialization_failure:
                    stack.enter_context(mock.patch.object(screen.json, "dumps", side_effect=ValueError("synthetic serialization failure")))
                try:
                    returned = screen.main()
                except (SystemExit, ValueError) as error:
                    failure = error
            preserved = False
            if occupied == "directory":
                preserved = output.is_dir() and (output / "retained.json").read_bytes() == original
            elif occupied in ("live_symlink", "dangling_symlink"):
                preserved = (output.is_symlink() and output.readlink() == target
                             and (target.read_bytes() == original if occupied == "live_symlink" else not target.exists()))
            elif occupied == "file":
                preserved = output.is_file() and output.read_bytes() == original
            raw = output.read_bytes() if output.is_file() else None
            return {"returned": returned, "failure": failure, "stdout": stdout.getvalue(),
                    "stderr": stderr.getvalue(), "gpu_calls": gpu.call_count,
                    "memory_calls": windows.kernel32.GlobalMemoryStatusEx.call_count,
                    "disk_calls": disk.call_count, "preserved": preserved,
                    "output_exists": output.exists() or output.is_symlink(), "raw": raw}

    def assert_rejected(self, result):
        self.assertIsInstance(result["failure"], SystemExit)
        self.assertEqual(result["failure"].code, 2)
        self.assertIn("output exists; preserve observations and choose a fresh path", result["stderr"])
        self.assertEqual(result["stdout"], "")
        self.assertTrue(result["preserved"])

    def test_preserve_mode_rejects_every_occupied_path_before_capacity_queries(self):
        for kind in ("file", "directory", "live_symlink", "dangling_symlink"):
            with self.subTest(kind=kind):
                result = self.exercise(occupied=kind)
                self.assert_rejected(result)
                self.assertEqual((result["gpu_calls"], result["memory_calls"], result["disk_calls"]), (0, 0, 0))

    def test_preserve_mode_rejects_paths_arriving_during_capacity_queries(self):
        for kind in ("file", "directory", "live_symlink", "dangling_symlink"):
            with self.subTest(kind=kind):
                result = self.exercise(occupied=kind, arrival=True)
                self.assert_rejected(result)
                self.assertEqual((result["gpu_calls"], result["memory_calls"], result["disk_calls"]), (1, 1, 1))

    def test_preserve_mode_serializes_before_creating_a_result(self):
        result = self.exercise(serialization_failure=True)
        self.assertIsInstance(result["failure"], ValueError)
        self.assertEqual(str(result["failure"]), "synthetic serialization failure")
        self.assertFalse(result["output_exists"])
        self.assertEqual(result["stdout"], "")

    def test_fresh_preserve_mode_keeps_both_profiles_and_failed_screen_semantics(self):
        for profile in ("granite30", "granite31"):
            for smi in ("8192\n", "1024\n"):
                with self.subTest(profile=profile, smi=smi):
                    result = self.exercise(profile=profile, smi=smi)
                    self.assertIsNone(result["failure"])
                    screen_value = json.loads(result["raw"])
                    self.assertEqual(json.loads(result["stdout"]), screen_value)
                    self.assertEqual(screen_value["profile"], profile)
                    self.assertEqual(screen_value["thresholds"]["temporary_volume_free_bytes"],
                                     12 * 2**30 if profile == "granite30" else 2 * 2_669_283_096 + 2**30)
                    self.assertEqual(screen_value["guards"]["nvidia_smi_free_mib"], smi == "8192\n")
                    self.assertEqual(screen_value["status"],
                                     "admitted_to_download_screen_only" if smi == "8192\n" else "unexecuted")

    def test_default_refresh_still_replaces_the_old_or_arriving_screen(self):
        for arrival in (False, True):
            with self.subTest(arrival=arrival):
                result = self.exercise(preserve=False, occupied="file", arrival=arrival)
                self.assertIsNone(result["failure"])
                self.assertFalse(result["preserved"])
                self.assertEqual(json.loads(result["raw"])["status"], "admitted_to_download_screen_only")
                self.assertEqual((result["gpu_calls"], result["memory_calls"], result["disk_calls"]), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
