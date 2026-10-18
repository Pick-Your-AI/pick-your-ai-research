"""Actual local process regressions; no optional MCP SDK or network required."""

from contextlib import contextmanager
import ctypes
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mcp_cleanup_probe", ROOT / "tests/reproduce_mcp_protocols.py")
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


@contextmanager
def adopt_fixture_orphans():
    """This test process adopts/reaps its own fixture peers, then restores state."""
    prctl = ctypes.CDLL(None, use_errno=True).prctl
    prctl.argtypes = [ctypes.c_int] + [ctypes.c_ulong] * 4
    prctl.restype = ctypes.c_int
    previous = ctypes.c_int()
    if prctl(37, ctypes.addressof(previous), 0, 0, 0) != 0:  # PR_GET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "Cannot inspect fixture subreaper state")
    if prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER; process-local only
        raise OSError(ctypes.get_errno(), "Cannot adopt fixture peers")
    try:
        yield
    finally:
        if prctl(36, previous.value, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), "Cannot restore fixture subreaper state")


class WorkerCleanupTests(unittest.TestCase):
    def test_unsupported_platform_fails_before_launching(self):
        with patch.object(PROBE.sys, "platform", "win32"), patch.object(PROBE.subprocess, "Popen") as launch:
            with self.assertRaisesRegex(RuntimeError, "Linux parent-death"):
                PROBE.run_worker([], {})
            launch.assert_not_called()

    @unittest.skipUnless(sys.platform == "linux", "requires Linux parent-death cleanup")
    def test_parent_binding_rejects_invalid_and_changed_parent(self):
        for parent in (None, True, 0, -1, "123"):
            with self.subTest(parent=parent), self.assertRaisesRegex(RuntimeError, "expected probe parent"):
                PROBE.bind_parent_lifetime(parent)
        with patch.object(PROBE.os, "getppid", return_value=101), patch.object(PROBE.ctypes, "CDLL") as libc:
            with self.assertRaisesRegex(RuntimeError, "no longer present"):
                PROBE.bind_parent_lifetime(102)
            libc.assert_not_called()
        with patch.object(PROBE.os, "getppid", side_effect=[101, 102]), patch.object(PROBE.ctypes, "CDLL") as libc:
            libc.return_value.prctl.return_value = 0
            with self.assertRaisesRegex(RuntimeError, "exited during setup"):
                PROBE.bind_parent_lifetime(101)
        with patch.object(PROBE.os, "getppid", return_value=101), patch.object(PROBE.ctypes, "CDLL") as libc:
            libc.return_value.prctl.return_value = -1
            with self.assertRaises(OSError):
                PROBE.bind_parent_lifetime(101)

    @unittest.skipUnless(sys.platform == "linux", "requires Linux parent-death cleanup")
    def test_worker_result_preserves_output_and_exit_status(self):
        code = "import os,sys;print(os.getpid()==os.getpgrp());print('diagnostic',file=sys.stderr);sys.exit(7)"
        result = PROBE.run_worker([sys.executable, "-I", "-c", code],
                                  PROBE.clean_environment(sys.executable))
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.stdout, "True\n")
        self.assertEqual(result.stderr, "diagnostic\n")

    @unittest.skipUnless(sys.platform == "linux", "requires Linux parent-death cleanup")
    def test_timeout_stops_peer_holding_pipes_and_spares_unrelated_process(self):
        for separate_session in (False, True):
            with self.subTest(separate_session=separate_session):
                self.check_timeout(separate_session)

    def check_timeout(self, separate_session):
        with adopt_fixture_orphans(), tempfile.TemporaryDirectory(prefix="pyai-mcp-cleanup-") as temporary:
            record = Path(temporary) / "owned.json"
            ready = Path(temporary) / "peer-ready.json"
            worker = Path(temporary) / "worker.py"
            peer = "import json,os,pathlib,runpy,signal,sys,time;"
            if separate_session:
                peer += f"runpy.run_path({str(PROBE.SELF)!r})['bind_parent_lifetime'](int(sys.argv[1]));"
            peer += "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
            peer += f"pathlib.Path({str(ready)!r}).write_text(json.dumps({{'pid':os.getpid(),'parent':os.getppid(),'group':os.getpgrp()}}));time.sleep(60)"
            worker.write_text(
                "import json,os,pathlib,subprocess,sys,time\n"
                f"peer=subprocess.Popen([sys.executable,'-I','-c',{peer!r},str(os.getpid())],start_new_session={separate_session!r})\n"
                f"pathlib.Path({str(record)!r}).write_text(json.dumps({{'worker':os.getpid(),'group':os.getpgrp(),'peer':peer.pid}}))\n"
                "time.sleep(60)\n")
            sentinel = subprocess.Popen([sys.executable, "-I", "-c", "import time;time.sleep(60)"],
                                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL, start_new_session=True)
            try:
                original = PROBE.run_worker
                def short_deadline(command, environment):
                    return original(command, environment, timeout=2)
                with patch.object(PROBE, "SELF", worker), patch.object(PROBE, "CASES", PROBE.CASES[:1]), \
                        patch.object(PROBE, "run_worker", side_effect=short_deadline), \
                        self.assertRaises(subprocess.TimeoutExpired):
                    PROBE.observe(sys.executable, sys.executable)
                owned = json.loads(record.read_text())
                established = json.loads(ready.read_text())
                self.assertEqual(owned["worker"], owned["group"])
                self.assertEqual(established["pid"], owned["peer"])
                self.assertEqual(established["parent"], owned["worker"])
                self.assertEqual(established["group"], owned["peer"] if separate_session else owned["group"])
                deadline = time.monotonic() + 2
                reaped, status = os.waitpid(owned["peer"], os.WNOHANG)
                while reaped == 0 and time.monotonic() < deadline:
                    time.sleep(0.02)
                    reaped, status = os.waitpid(owned["peer"], os.WNOHANG)
                self.assertEqual(reaped, owned["peer"], "owned peer survived the hard worker deadline")
                self.assertEqual(os.waitstatus_to_exitcode(status), -signal.SIGKILL)
                with self.assertRaises(ChildProcessError, msg="run_worker did not reap its worker"):
                    os.waitpid(owned["worker"], os.WNOHANG)
                self.assertIsNone(sentinel.poll(), "cleanup signalled an unrelated process")
            finally:
                # Only signal a still-unreaped direct/adopted fixture child.
                # Already reaped IDs may be recycled and are never signalled.
                if record.exists():
                    owned = json.loads(record.read_text())
                    for pid in (owned["worker"], owned["peer"]):
                        try:
                            reaped, _ = os.waitpid(pid, os.WNOHANG)
                            if reaped == 0:
                                os.kill(pid, signal.SIGKILL)
                                os.waitpid(pid, 0)
                        except ChildProcessError:
                            pass
                sentinel.kill()
                sentinel.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
