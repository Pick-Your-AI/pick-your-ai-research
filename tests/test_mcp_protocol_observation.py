"""Offline integrity guards for the bounded synthetic-peer observation."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mcp_protocol_probe", ROOT / "tests/reproduce_mcp_protocols.py")
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)
FIXTURES = ROOT / "tests/fixtures/mcp-protocol-2026-10-18"


class ProtocolObservationTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((FIXTURES / "observation.json").read_text())

    def test_recorded_rows_cover_the_exact_matrix(self):
        rows = self.record["observations"]
        self.assertEqual(len(rows), len(PROBE.CASES))
        self.assertTrue(self.record["expectations_satisfied"])
        for row, case in zip(rows, PROBE.CASES, strict=True):
            self.assertTrue(row["matches_expected"])
            self.assertTrue(PROBE.matches_expected(row, case))

    def test_host_timeouts_do_not_become_protocol_incompatibility(self):
        restricted = json.loads((FIXTURES / "host-restricted-trial.json").read_text())
        for row, case in zip(restricted["observations"], PROBE.CASES, strict=True):
            self.assertFalse(PROBE.matches_expected(row, case))
        row = deepcopy(self.record["observations"][-1])
        row["errors"][0]["code"] = -32001
        self.assertFalse(PROBE.matches_expected(row, PROBE.CASES[-1]))

    def test_wrong_version_or_peer_cannot_pass_a_successful_worker(self):
        original = self.record["observations"][3]
        for path, value in [("protocol_version", "2025-11-25"), ("server_sdk", "1.30.0"),
                            ("mode", "legacy"), ("worker_exit_code", 1),
                            ("worker_stderr_bytes", 1), ("tools", []),
                            ("echo", {"echo": PROBE.SYNTHETIC_TEXT, "server_sdk": "1.30.0"})]:
            with self.subTest(field=path):
                row = deepcopy(original)
                row[path] = value
                self.assertFalse(PROBE.matches_expected(row, PROBE.CASES[3]))

    def test_pinned_client_adoption_is_not_reported_as_a_successful_exchange(self):
        row = deepcopy(self.record["observations"][-1])
        row["protocol_version"] = "2026-07-28"
        self.assertFalse(PROBE.matches_expected(row, PROBE.CASES[-1]))

    def test_success_cannot_retain_an_error_or_skip_the_echo(self):
        for mutation in [{"errors": [{"type": "MCPError", "code": -32602}]},
                         {"echo": None}, {"status": "failed"}]:
            row = deepcopy(self.record["observations"][0])
            row.update(mutation)
            self.assertFalse(PROBE.matches_expected(row, PROBE.CASES[0]))


if __name__ == "__main__":
    unittest.main()
