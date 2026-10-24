"""Synthetic usage, consent, replay, concurrency and existing-backend contracts."""
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import compile_ai_logs
import ledger_mcp
import ledger_store
import muse_usage as mu
import scoped_report

ROOT = Path(__file__).resolve().parents[1]


def fixture(**overrides):
    event = {
        "schema": "mu-usage/1", "source_id": "synthetic-mu", "provider": "synthetic-gateway",
        "configured_model": "fixture-model", "model": "fixture-model", "invocation_id": str(uuid.uuid4()),
        "response_id": hashlib.sha256(b"native-response").hexdigest(), "session_id": "a" * 64, "run_id": "b" * 64,
        "id_mode": "hmac-sha256", "operation": "agent", "invocation_ordinal": 1, "retry_of": None,
        "status": "completed", "started_at": "2026-10-12T12:00:00Z", "timestamp": "2026-10-12T12:00:00Z",
        "timestamp_source": "provider_created", "usage_source": "openai_chat_response_usage",
        "input_tokens": 100, "cache_read_tokens": 40, "cache_write_tokens": None, "output_tokens": 20,
        "total_tokens": 120, "reasoning_tokens": 5, "input_semantics": "openai-chat",
        "capture_incomplete": False, "reported_charge_usd": 0.015, "charge_source": "gateway_usage_cost",
    }
    event.update(overrides)
    return event


class MuseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spool = self.root / "usage"
        self.spool.mkdir(mode=0o700)
        self.prices = self.root / "pricing.json"
        self.prices.write_text(json.dumps({"_as_of": "synthetic", "models": {"fixture-model": {
            "input": 2, "cache_read": 0.5, "output": 8, "cache_write_5m": 3, "cache_write_1h": 4}}}))
        self.source = {"id": "synthetic-mu", "path": str(self.spool), "provider": "synthetic-gateway"}
        self.config = {"version": 3, "store": {"kind": "sqlite", "path": str(self.root / "ledger.sqlite")},
                       "pricing_path": str(self.prices), "muse_mesh": {"version": 1, "collection_enabled": True,
                       "collection_consent": "local-usage-metadata", "reporting_enabled": True,
                       "reporting_consent": "share-usage-aggregates", "allow_scan": False, "sources": [self.source]}}
        self.path = self.root / "config.json"
        self.save_config()

    def save_config(self):
        self.path.write_text(json.dumps(self.config))
        self.path.chmod(0o600)

    def write(self, event):
        path = self.spool / (event["invocation_id"] + ".usage.json")
        path.write_text(json.dumps(event))
        path.chmod(0o600)
        return path

    def rows(self):
        store = ledger_store.Store.open("sqlite", self.config["store"]["path"])
        try:
            return list(store.iter_events())
        finally:
            store.close()

    def test_normalization_and_charge_provenance(self):
        event = mu.normalize(fixture(), self.source)
        self.assertEqual((event["input_uncached"], event["cache_read"], event["output"], event["total"]), (60, 40, 20, 120))
        self.assertIsNone(event["cache_write"])
        self.assertEqual(event["cost_usd"], 0.015)
        self.assertEqual(event["charge_source"], "gateway_usage_cost")
        self.assertTrue(event["usage_pricing_eligible"])

    def test_provider_and_model_attribution_are_not_inferred_from_name(self):
        source = dict(self.source, provider="other")
        event = mu.normalize(fixture(provider="other", model="provider/model"), source)
        self.assertEqual(event["provider"], "other")
        self.assertEqual(event["model"], "provider/model")

    def test_missing_counts_stay_null_despite_sdk_zero_defaults(self):
        event = mu.normalize(fixture(input_tokens=None, total_tokens=None, cache_read_tokens=None), self.source)
        self.assertIsNone(event["input_uncached"])
        self.assertIsNone(event["total"])
        self.assertIsNone(event["input_tokens"])
        self.assertFalse(event["usage_pricing_eligible"])

    def test_explicit_zero_is_a_measurement(self):
        event = mu.normalize(fixture(input_tokens=0, cache_read_tokens=0, output_tokens=0, total_tokens=0, reasoning_tokens=0), self.source)
        self.assertEqual(event["total"], 0)
        self.assertTrue(event["usage_pricing_eligible"])

    def test_missing_cache_partition_does_not_invent_uncached_tokens_or_price(self):
        event = mu.normalize(fixture(cache_read_tokens=None), self.source)
        self.assertIsNone(event["input_uncached"])
        self.assertEqual(event["input_tokens"], 100)
        self.assertEqual(event["total"], 120)
        self.assertIsNone(compile_ai_logs.price_event(event, json.loads(self.prices.read_text()))[2])

    def test_inclusive_cache_write_extension(self):
        event = mu.normalize(fixture(input_semantics="inclusive-cache", cache_write_tokens=10), self.source)
        self.assertEqual(event["input_uncached"], 50)
        self.assertEqual(event["cache_write"], 10)
        self.assertAlmostEqual(compile_ai_logs.price_event(event, json.loads(self.prices.read_text()))[0], 0.00031)

    def test_estimates_never_enter_observed_token_totals(self):
        event = mu.normalize(fixture(usage_source="estimated"), self.source)
        self.assertEqual(event["estimated_usage"]["input_tokens"], 100)
        self.assertIsNone(event["input_tokens"])
        self.assertIsNone(event["total"])
        self.assertFalse(event["usage_pricing_eligible"])

    def test_invalid_counts_and_totals_rejected(self):
        for change in ({"input_tokens": True}, {"output_tokens": -1}, {"output_tokens": 1.5},
                       {"input_tokens": 2**53}, {"total_tokens": 130}, {"cache_read_tokens": 101},
                       {"reasoning_tokens": 21}, {"reported_charge_usd": float("nan")},
                       {"reported_charge_usd": -1}, {"cache_write_tokens": 1}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                mu.normalize(fixture(**change), self.source)

    def test_schema_source_provenance_and_identity_validation(self):
        for change in ({"schema": "future"}, {"provider": "other"}, {"source_id": "other"},
                       {"invocation_id": "../../file"}, {"timestamp": "2026-10-12"}, {"timestamp_source": "scan"},
                       {"usage_source": "guessed"}, {"id_mode": "literal"}, {"session_id": "unredacted"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                mu.normalize(fixture(**change), self.source)

    def test_unknown_fields_prompts_headers_and_secrets_never_stored(self):
        event = fixture(prompt="SECRET-PROMPT", completion="SECRET-REPLY", headers={"Authorization": "SECRET-KEY"}, error="SECRET-ERROR")
        self.write(event)
        mu.scan(self.config)
        serialized = json.dumps(self.rows())
        self.assertNotIn("SECRET", serialized)
        self.assertNotIn(str(self.spool), serialized)

    def test_replay_and_overlapping_scans(self):
        event = fixture()
        self.write(event)
        first = mu.scan(self.config)
        self.assertEqual(first["added"], 1)
        self.assertEqual(mu.scan(self.config)["added"], 0)
        self.write(dict(event, invocation_id=str(uuid.uuid4()), run_id="c" * 64, invocation_ordinal=2))
        self.assertEqual(mu.scan(self.config)["added"], 0)
        self.assertEqual(len(self.rows()), 1)

    def test_no_native_id_uses_persisted_pre_request_identity(self):
        event = fixture(response_id=None)
        self.write(event)
        self.assertEqual(mu.scan(self.config)["added"], 1)
        self.assertEqual(mu.scan(self.config)["added"], 0)
        self.write(dict(event, invocation_id=str(uuid.uuid4())))
        self.assertEqual(mu.scan(self.config)["added"], 1)

    def test_new_native_retry_attempt_is_separate(self):
        self.write(fixture())
        self.write(fixture(response_id="d" * 64, invocation_ordinal=2))
        self.assertEqual(mu.scan(self.config)["added"], 2)

    def test_conflicting_retry_is_atomic_and_not_a_silent_skip(self):
        first = fixture()
        self.write(first)
        mu.scan(self.config)
        self.write(fixture(response_id="d" * 64))
        self.write(dict(first, invocation_id=str(uuid.uuid4()), output_tokens=25, total_tokens=125))
        with self.assertRaisesRegex(ValueError, "conflicting"):
            mu.scan(self.config)
        self.assertEqual(len(self.rows()), 1)

    def test_conflict_in_first_batch_leaves_no_rows(self):
        first = fixture()
        self.write(first)
        self.write(dict(first, invocation_id=str(uuid.uuid4()), reported_charge_usd=99))
        with self.assertRaisesRegex(ValueError, "conflicting"):
            mu.scan(self.config)
        self.assertEqual(self.rows(), [])

    def test_completion_status_change_conflicts_after_ingestion(self):
        for status in ("interrupted", "failed", "cancelled"):
            for reverse in (False, True):
                with self.subTest(status=status, reverse=reverse):
                    original = fixture(status=status)
                    completed = dict(original, invocation_id=str(uuid.uuid4()), status="completed")
                    first, second = (completed, original) if reverse else (original, completed)
                    first, second = (mu.normalize(row, self.source) for row in (first, second))
                    self.assertEqual(first["request_id"], second["request_id"])
                    self.assertNotEqual(first["evidence_sha256"], second["evidence_sha256"])
                    self.assertNotEqual(first["usage_pricing_eligible"], second["usage_pricing_eligible"])
                    path = str(self.root / (status + str(reverse) + ".sqlite"))
                    store = ledger_store.Store.open("sqlite", path)
                    try:
                        self.assertEqual(store.ingest_verified_events([first]), (1, 0))
                    finally:
                        store.close()
                    store = ledger_store.Store.open("sqlite", path)
                    try:
                        extra = mu.normalize(fixture(response_id="d" * 64), self.source)
                        with self.assertRaisesRegex(ValueError, "conflicting"):
                            store.ingest_verified_events([extra, second])
                        rows = list(store.iter_events())
                        self.assertEqual(len(rows), 1)
                        self.assertEqual(rows[0]["status"], first["status"])
                        self.assertEqual(rows[0]["usage_pricing_eligible"], first["usage_pricing_eligible"])
                        self.assertEqual(store.ingest_verified_events([first]), (0, 1))
                    finally:
                        store.close()

    def test_completion_status_change_conflicts_in_first_batch(self):
        for status in ("interrupted", "failed", "cancelled"):
            for reverse in (False, True):
                with self.subTest(status=status, reverse=reverse):
                    original = fixture(status=status)
                    completed = dict(original, invocation_id=str(uuid.uuid4()), status="completed")
                    records = [completed, original] if reverse else [original, completed]
                    path = str(self.root / (status + str(reverse) + ".sqlite"))
                    store = ledger_store.Store.open("sqlite", path)
                    try:
                        with self.assertRaisesRegex(ValueError, "conflicting"):
                            store.ingest_verified_events([mu.normalize(row, self.source) for row in records])
                        self.assertEqual(list(store.iter_events()), [])
                    finally:
                        store.close()

    def test_inflight_marker_is_coverage_not_a_zero_cost_event(self):
        event = fixture()
        marker = self.spool / (event["invocation_id"] + ".started.json")
        marker.write_text(json.dumps({"status": "started"}))
        self.assertEqual(mu.scan(self.config)["unfinished_invocations"], 1)
        self.assertEqual(len(self.rows()), 0)
        self.write(event)
        self.assertEqual(mu.scan(self.config)["unfinished_invocations"], 0)

    def test_failed_and_interrupted_usage_are_preserved(self):
        self.write(fixture(status="interrupted"))
        self.write(fixture(response_id=None, status="failed", usage_source="unavailable", input_tokens=None,
                           output_tokens=None, total_tokens=None, cache_read_tokens=None, reasoning_tokens=None,
                           reported_charge_usd=None, charge_source=None))
        self.assertEqual(mu.scan(self.config)["added"], 2)
        self.assertEqual({r["status"] for r in self.rows()}, {"interrupted", "failed"})

    def test_concurrent_duplicate_ingestion(self):
        self.write(fixture())
        # Establish schema first; each thread then uses its own real connection.
        store = ledger_store.Store.open("sqlite", self.config["store"]["path"])
        store.close()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: mu.scan(self.config), range(24)))
        self.assertEqual(sum(r["added"] for r in results), 1)
        self.assertEqual(len(self.rows()), 1)

    def test_storage_failure_then_recovery(self):
        self.write(fixture())
        with patch.object(ledger_store.SqliteStore, "ingest_verified_events", side_effect=sqlite3.OperationalError("disk full")):
            with self.assertRaises(sqlite3.OperationalError):
                mu.scan(self.config)
        self.assertEqual(mu.scan(self.config)["added"], 1)
        self.assertEqual(mu.scan(self.config)["added"], 0)

    def test_all_legacy_backends_accept_normalized_export_and_replay(self):
        exported = self.root / "events.jsonl"
        exported.write_text(json.dumps(mu.normalize(fixture(), self.source)) + "\n")
        for kind in ("sqlite", "json", "csv"):
            store = ledger_store.Store.open(kind, str(self.root / ("store-" + kind)))
            try:
                self.assertEqual(store.ingest_events_file(exported), (1, 0))
                self.assertEqual(store.ingest_events_file(exported), (0, 1))
                row = next(iter(store.iter_events()))
                self.assertEqual(row["provider"], "synthetic-gateway")
                self.assertEqual(row["total"], 120)
            finally:
                store.close()

    def test_live_file_backend_is_explicitly_refused(self):
        self.config["store"]["kind"] = "json"
        self.save_config()
        with self.assertRaisesRegex(ValueError, "SQLite"):
            mu.load_config(self.path)

    def test_collection_disabled_does_not_open_sources_or_store(self):
        for change in ({"collection_enabled": False}, {"collection_consent": "not-approved"}):
            config = copy.deepcopy(self.config)
            config["muse_mesh"].update(change)
            with patch.object(mu, "safe_path", side_effect=AssertionError("must not touch sources")):
                with self.assertRaises(PermissionError):
                    mu.scan(config)
        self.assertFalse(Path(self.config["store"]["path"]).exists())

    @unittest.skipIf(os.name == "nt", "POSIX owner-mode contract")
    def test_shared_config_or_source_file_refused(self):
        self.path.chmod(0o644)
        with self.assertRaises(PermissionError):
            mu.load_config(self.path)
        path = self.write(fixture())
        path.chmod(0o666)
        with self.assertRaises(PermissionError):
            mu.scan(self.config)

    @unittest.skipIf(os.name == "nt", "symlink creation may need elevation")
    def test_symlink_source_and_special_files_refused(self):
        target = self.root / "target"
        target.write_text("PRIVATE")
        path = self.spool / (str(uuid.uuid4()) + ".usage.json")
        path.symlink_to(target)
        with self.assertRaises(ValueError):
            mu.scan(self.config)
        path.unlink()
        os.mkfifo(path, 0o600)
        with self.assertRaises(ValueError):
            mu.scan(self.config)

    def test_partial_temporary_files_are_not_imported(self):
        (self.spool / ".incomplete.tmp").write_text('{"secret":"NEVER-READ"')
        self.assertEqual(mu.scan(self.config)["added"], 0)

    def test_config_load_never_migrates_or_changes_bytes(self):
        before = self.path.read_bytes()
        mu.load_config(self.path)
        self.assertEqual(self.path.read_bytes(), before)

    def test_existing_pricer_and_report_with_complete_and_missing_usage(self):
        self.write(fixture())
        self.write(fixture(response_id="d" * 64, cache_read_tokens=None))
        mu.scan(self.config)
        cost = mu.report(self.config, "ledger_cost_breakdown", {})
        self.assertAlmostEqual(cost["api_equivalent_usd"], 0.0003)
        self.assertAlmostEqual(cost["observed_reported_charge_usd"], 0.03)
        self.assertEqual((cost["priced_records"], cost["unpriced_records"]), (1, 1))
        class Scope:
            def contains(self, _): return True
            def as_dict(self): return {}
        data, events = scoped_report.collect(scoped_report.iter_stored_events("sqlite", self.config["store"]["path"]),
                                            Scope(), json.loads(self.prices.read_text()), datetime.now(timezone.utc))
        self.assertEqual(data["totals"]["total"], 240)
        self.assertEqual(data["totals"]["unpriced_calls"], 1)
        self.assertIsNone([e for e in events if e["pricing_status"] == "unpriced"][0]["api_equivalent_usd"])

    def test_report_filters_and_readonly_store(self):
        self.write(fixture())
        mu.scan(self.config)
        before = Path(self.config["store"]["path"]).read_bytes()
        for name in ledger_mcp.REPORTS:
            mu.report(self.config, name, {})
        self.assertEqual(mu.report(self.config, "ledger_usage_summary", {"since": "2026-10-13"})["rows"][0]["calls"], 0)
        self.assertEqual(Path(self.config["store"]["path"]).read_bytes(), before)
        for args in ({"sql": "DROP TABLE events"}, {"path": "/etc/passwd"}, {"limit": True}, {"limit": 10000},
                     {"since": "invalid"}, {"since": "2026-10-13", "until": "2026-10-12"}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                mu.report(self.config, "ledger_usage_summary", args)

    def test_cli_real_store(self):
        self.write(fixture())
        run = subprocess.run([sys.executable, str(ROOT / "scripts/muse_usage.py"), "scan", "--config", str(self.path)],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["added"], 1)


if __name__ == "__main__":
    unittest.main()
