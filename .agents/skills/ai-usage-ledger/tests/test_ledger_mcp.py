"""MCP transport/protocol and authorization tests using only synthetic local data."""
import io
import json
import subprocess
import sys
import unittest

from test_muse_usage import MuseTests, ROOT, fixture
import ledger_mcp
import muse_usage


class MCPTests(MuseTests):
    # Inherit fixture helpers; loader below selects only this class's own tests.
    def connected(self):
        server = ledger_mcp.Server(self.path)
        response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                  "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "fixture", "version": "1"}}})
        self.assertEqual(response["result"]["protocolVersion"], "2025-11-25")
        server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return server

    def call(self, server, name, arguments=None):
        return server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                              "params": {"name": name, "arguments": {} if arguments is None else arguments}})["result"]

    def test_mcp_discovery_and_all_report_invocations(self):
        self.write(fixture())
        muse_usage.scan(self.config)
        server = self.connected()
        discovery = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {tool["name"] for tool in discovery["result"]["tools"]}
        self.assertEqual(names, set(ledger_mcp.REPORTS))
        for name in names:
            self.assertFalse(self.call(server, name)["isError"])

    def test_mcp_scan_is_absent_and_rejected_until_separately_authorized(self):
        self.write(fixture())
        server = self.connected()
        self.assertTrue(self.call(server, "ledger_scan_sources")["isError"])
        self.config["muse_mesh"]["allow_scan"] = True
        self.save_config()
        self.assertFalse(self.call(server, "ledger_scan_sources")["isError"])
        self.assertTrue(self.call(server, "ledger_scan_sources", {"path": "/etc"})["isError"])
        self.config["muse_mesh"]["collection_consent"] = "revoked"
        self.save_config()
        self.assertTrue(self.call(server, "ledger_scan_sources")["isError"])

    def test_mcp_reporting_revocation_is_immediate_and_not_model_overridable(self):
        self.write(fixture())
        muse_usage.scan(self.config)
        server = self.connected()
        self.config["muse_mesh"]["reporting_enabled"] = False
        self.save_config()
        self.assertTrue(self.call(server, "ledger_usage_summary")["isError"])
        self.assertTrue(self.call(server, "ledger_usage_summary", {"consent": "yes"})["isError"])
        response = server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        self.assertEqual(response["result"]["tools"], [])

    def test_mcp_errors_do_not_disclose_paths_sql_or_source_details(self):
        server = self.connected()
        for args in ({"sql": "SECRET-SQL"}, {"path": "SECRET-PATH"}, []):
            response = self.call(server, "ledger_usage_summary", args)
            self.assertTrue(response["isError"])
            self.assertNotIn("SECRET", json.dumps(response))
            self.assertNotIn(str(self.root), json.dumps(response))

    def test_mcp_initialization_protocol_errors_and_bounded_input(self):
        server = ledger_mcp.Server(self.path)
        self.assertIn("error", server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}))
        self.assertIn("error", server.handle([]))
        output = io.StringIO()
        ledger_mcp.serve(self.path, io.BytesIO(b"{broken\n"), output)
        self.assertEqual(json.loads(output.getvalue())["error"]["code"], -32700)
        output = io.StringIO()
        status = ledger_mcp.serve(self.path, io.BytesIO(b"x" * (ledger_mcp.MAX_MESSAGE + 1)), output)
        self.assertEqual(status, 1)

    def test_mcp_stdio_subprocess_roundtrip_without_optional_mcp_package(self):
        self.write(fixture())
        muse_usage.scan(self.config)
        messages = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "ledger_usage_summary", "arguments": {}}}]
        process = subprocess.run([sys.executable, str(ROOT / "scripts/ledger_mcp.py"), "--config", str(self.path)],
                                 input="".join(json.dumps(m) + "\n" for m in messages), text=True, capture_output=True, timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        responses = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual(len(responses), 3)
        summary = json.loads(responses[-1]["result"]["content"][0]["text"])
        self.assertEqual(summary["rows"][0]["total"], 120)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(MCPTests(name) for name in MCPTests.__dict__ if name.startswith("test_mcp_"))
