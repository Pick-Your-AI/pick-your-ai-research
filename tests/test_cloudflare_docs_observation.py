"""Offline integrity checks for a dated public-endpoint observation, not live qualification."""

import hashlib
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/cloudflare-docs-mcp-2026-10-18"
SDK_FIXTURES = ROOT / "tests/fixtures/mcp-protocol-2026-10-18"
SCRIPT_SHA = "6fec10c644ec3e311dd4c81d3590fe0e63ba124355e3c154151a2c8f6a5886b8"
SOURCE_COMMIT = "e4cf085520ea7286af77abf938d645c610ef1580"
SOURCE_TREE = "b6b2aa67cd932bf2b11692a34779389ccaaf05a6"
HOST = "https://docs.mcp.cloudflare.com"
QUERY = "How does Streamable HTTP differ from the deprecated HTTP+SSE transport for MCP?"
TUPLES = {
    "v1": ("1.30.0", "legacy", "2025-11-25", "/mcp"),
    "v2": ("2.3.0", "auto", "2026-07-28", "/mcp"),
    "sse-alias": ("2.3.0", "auto", "2026-07-28", "/sse"),
}


class CloudflareDocsObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((FIXTURES / "observation.json").read_text())
        cls.rows = cls.record["observations"]

    def test_dated_client_tuples_remain_bound_to_the_executed_driver(self):
        self.assertEqual(self.record["probe_script_sha256"], SCRIPT_SHA)
        self.assertEqual(
            hashlib.sha256((ROOT / "tests/reproduce_cloudflare_docs_mcp.py").read_bytes()).hexdigest(),
            SCRIPT_SHA,
        )
        self.assertEqual(set(self.rows), {*TUPLES, "sse-get"})
        for name, (sdk, mode, protocol, route) in TUPLES.items():
            with self.subTest(observation=name):
                row = self.rows[name]
                self.assertEqual(row["script_sha256"], SCRIPT_SHA)
                self.assertEqual(row["client_sdk"], sdk)
                self.assertEqual(row["mode"], mode)
                self.assertEqual(row["protocol_version"], protocol)
                self.assertEqual(row["endpoint"], HOST + route)
                self.assertTrue(row["observed_at"].startswith("2026-10-18T"))
                self.assertEqual(row["transport"], "streamable_http")
                self.assertEqual(row["status"], "passed")
                self.assertEqual(row["worker_exit_code"], 0)
                self.assertEqual(row["worker_stderr_bytes"], 0)
                self.assertNotIn("errors", row)

    def test_retained_requests_have_the_exact_credential_free_operation_scope(self):
        methods = {
            "v1": ["initialize", "notifications/initialized", "tools/list"],
            "v2": ["server/discover", "tools/list", "tools/call"],
            "sse-alias": ["server/discover", "tools/list"],
        }
        for name, expected in methods.items():
            row = self.rows[name]
            with self.subTest(observation=name):
                self.assertEqual([r["rpc_method"] for r in row["http_requests"]], expected)
                self.assertEqual(len(row["http_responses"]), len(expected))
                for request, response in zip(row["http_requests"], row["http_responses"], strict=True):
                    self.assertEqual(request["url"], row["endpoint"])
                    self.assertEqual(response["url"], row["endpoint"])
                    self.assertEqual(request["method"], "POST")
                    self.assertEqual(response["method"], "POST")
                    self.assertIs(request["credential_headers"], False)
                    self.assertIs(response["session_header_present"], False)
                    self.assertIsNone(response["protocol_header"])
                    self.assertRegex(request["request"]["sha256"], r"\A[0-9a-f]{64}\Z")
                    self.assertGreater(request["request"]["bytes"], 0)

    def test_sse_response_bodies_and_the_sse_alias_do_not_become_legacy_sse_evidence(self):
        self.assertEqual(
            [(r["status"], r["content_type"]) for r in self.rows["v1"]["http_responses"]],
            [(200, "text/event-stream"), (202, None), (200, "text/event-stream")],
        )
        self.assertIs(self.rows["v1"]["session_id_present"], False)
        for name in ("v2", "sse-alias"):
            self.assertTrue(all(
                (r["status"], r["content_type"]) == (200, "application/json")
                for r in self.rows[name]["http_responses"]
            ))

    def test_complete_listings_keep_both_tools_and_do_not_imply_both_were_called(self):
        expected = {
            "search_cloudflare_documentation": "e31d79affd315385776b80806c03bfc7988472adb80a800bdd93f0aff7778b00",
            "migrate_pages_to_workers_guide": "93ab7499dc3c616f8db8780fed0d9f69270803cda913882ad2ef3943db8d7225",
        }
        for name in TUPLES:
            row = self.rows[name]
            with self.subTest(observation=name):
                self.assertIsNone(row["next_cursor"])
                self.assertEqual(len(row["tools"]), 2)
                self.assertEqual({t["name"]: t["input_schema"]["sha256"] for t in row["tools"]}, expected)
                self.assertTrue(all(t["read_only_hint"] is True for t in row["tools"]))
                self.assertEqual(row["server_info"], {"name": "docs-ai-search", "version": "0.4.13"})
        self.assertEqual(self.rows["v2"]["listing"], self.rows["sse-alias"]["listing"])
        self.assertNotIn("search", self.rows["v1"])
        self.assertNotIn("search", self.rows["sse-alias"])

    def test_search_success_keeps_the_fixed_query_and_metadata_only_receipt(self):
        search = self.rows["v2"]["search"]
        self.assertEqual(set(search), {"query", "is_error", "result", "result_count", "urls"})
        self.assertEqual(search["query"], QUERY)
        self.assertIs(search["is_error"], False)
        self.assertEqual(search["result_count"], 13)
        self.assertEqual(len(search["urls"]), 13)
        for url in search["urls"]:
            parsed = urlsplit(url)
            self.assertEqual((parsed.scheme, parsed.netloc), ("https", "developers.cloudflare.com"))
        self.assertEqual(search["result"], {
            "bytes": 55445,
            "sha256": "56ae836deb773f778b191847d15def59f99329402f019f26841bb9d27288124e",
        })
        # The result preimage was not retained. This checks its recorded identity,
        # not a re-hash, search quality, a followed URL, or a deployed source revision.

    def test_denied_get_is_preserved_without_a_success_or_migration_receipt(self):
        row = self.rows["sse-get"]
        self.assertEqual((row["method"], row["url"], row["request_accept"]),
                         ("GET", HOST + "/sse", "text/event-stream"))
        self.assertIs(row["credential_headers"], False)
        self.assertEqual(row["status"], 403)
        self.assertEqual(row["headers"]["content-type"], "text/html; charset=UTF-8")
        self.assertIsNone(row["headers"]["link"])
        self.assertEqual(row["response_body_bytes"], 7184)
        self.assertEqual(row["response_body_sha256"],
                         "8e8a34a7e8e3851f6b93c782f2271f9e97409d6d32980f1f5ae95ab2222e2c8b")
        self.assertNotIn("protocol_version", row)
        self.assertNotIn("tools", row)

    def test_source_manifest_keeps_the_independently_inspected_immutable_identities(self):
        data = (FIXTURES / "source-identity.json").read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "6f5bd10bdfc578beb60aad7f758dc73b6bf6f7d482f3b6fc863ebd23732e6717")
        manifest = json.loads(data)
        self.assertEqual(self.record["source_commit"], SOURCE_COMMIT)
        self.assertEqual(self.record["source_tree"], SOURCE_TREE)
        self.assertEqual(manifest["commit"], SOURCE_COMMIT)
        self.assertEqual(manifest["tree"], SOURCE_TREE)
        self.assertEqual(len(manifest["files"]), 10)
        self.assertEqual(len({f["path"] for f in manifest["files"]}), 10)
        for source in manifest["files"]:
            self.assertEqual(source["url"],
                             f"https://raw.githubusercontent.com/cloudflare/mcp-server-cloudflare/{SOURCE_COMMIT}/{source['path']}")
            self.assertRegex(source["git_blob"], r"\A[0-9a-f]{40}\Z")
            self.assertRegex(source["sha256"], r"\A[0-9a-f]{64}\Z")
            self.assertGreater(source["bytes"], 0)
        # Full source bytes were checked separately against the remote tree.
        # CI preserves the manifest; it does not repeat a network/source inspection.

    def test_prior_sdk_preparation_locks_and_synthetic_observation_remain_unchanged(self):
        for name, expected in {
            "observation.json": "5750469236508d9dc1012f7b3925ebe8ffd378e7be7cadec5d7933f1a12a8385",
            "preparation.json": "5b18535a9d11f302644a1997001734a8ad6ecf3aed4e643db06f7377bf70039e",
        }.items():
            self.assertEqual(hashlib.sha256((SDK_FIXTURES / name).read_bytes()).hexdigest(), expected)
        preparation = json.loads((SDK_FIXTURES / "preparation.json").read_text())
        self.assertEqual({(p["package"], p["version"]) for p in preparation["packages"]},
                         {("mcp", "1.30.0"), ("mcp", "2.3.0"), ("mcp-types", "2.3.0")})
        self.assertEqual({lock["file"] for lock in preparation["dependency_locks"]},
                         {"requirements-v1.txt", "requirements-v2.txt"})
        for lock in preparation["dependency_locks"]:
            self.assertEqual(hashlib.sha256((SDK_FIXTURES / lock["file"]).read_bytes()).hexdigest(),
                             lock["sha256"])


if __name__ == "__main__":
    unittest.main()
