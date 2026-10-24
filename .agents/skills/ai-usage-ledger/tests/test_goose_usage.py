"""Goose normalization, privacy, discovery and real scanner/store/report contracts."""
import hashlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import ExitStack, closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import anonymize  # noqa: E402
import compile_ai_logs as compiler  # noqa: E402
import detect_hosts  # noqa: E402
import goose_usage as goose  # noqa: E402
import ledger  # noqa: E402
import ledger_query  # noqa: E402
import ledger_store  # noqa: E402
import run_pipeline  # noqa: E402
import scoped_report  # noqa: E402
from goose_fixtures import PRIVATE, STAMP, database, export_header, invocation, pricing  # noqa: E402


class GooseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "sessions" / "sessions.db"
        self.conn = database(self.db)
        self.addCleanup(self.conn.close)

    def collect(self):
        return goose.collect("fixture=" + str(self.db), "fixture-host")

    def test_one_invocation_cache_subsets_and_privacy(self):
        invocation(self.conn)
        events, info = self.collect()
        self.assertEqual(len(events), 1)
        e = events[0]
        self.assertEqual((e["input_uncached"], e["cache_read"], e["cache_write"], e["output"], e["total"]), (700, 200, 100, 50, 1050))
        self.assertEqual(e["provider"], "synthetic-provider-a")
        self.assertEqual(e["provider_confidence"], "inferred_unique_message_usage")
        self.assertEqual(e["session"], "fixture:20261012_1")
        self.assertEqual(info["status"], "ok")
        self.assertNotIn(PRIVATE, json.dumps([events, info]))
        self.assertIsNone(e["src"])

    def test_missing_sqlite_json_functions_preserve_usage(self):
        invocation(self.conn)
        original = goose.snapshot

        class WithoutJSON:
            def __init__(self, conn):
                self.conn = conn

            def execute(self, sql):
                if "json_extract" in sql:
                    raise sqlite3.OperationalError("no such function: json_extract")
                return self.conn.execute(sql)

        @contextmanager
        def without_json(db):
            with original(db) as conn:
                yield WithoutJSON(conn)

        with mock.patch.object(goose, "snapshot", side_effect=without_json):
            events, info = self.collect()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["total"], 1050)
        self.assertIsNone(events[0]["provider"])
        self.assertEqual(info["status"], "ok")
        self.assertEqual(info["provider_inference_status"], "sqlite_json_functions_unavailable")

    def test_source_inventory_includes_wal_but_not_shm(self):
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA wal_autocheckpoint=0")
        invocation(self.conn)
        wal = Path(str(self.db) + "-wal")
        expected_bytes = self.db.stat().st_size + wal.stat().st_size
        events, info = self.collect()
        self.assertEqual(len(events), 1)
        self.assertEqual(info["files"], 2)
        self.assertEqual(info["bytes"], expected_bytes)

    def test_anonymized_events_and_inventory_remove_nested_native_ids(self):
        namespace, sid = "PRIVATE_SOURCE_ALIAS", "PRIVATE_NATIVE_SESSION"
        invocation(self.conn, sid=sid)
        invocation(self.conn, sid=sid, model=None, cost_source="carried_forward", message=False)
        events, info = goose.collect(namespace + "=" + str(self.db), "fixture-host")
        before = json.dumps([events, info], sort_keys=True)
        anonymizer = anonymize.Anonymizer("synthetic-private-salt")
        anonymous = anonymizer.event(events[0])
        inv = anonymizer.inventory({"host": "fixture-host", "roots": [info]})
        encoded = json.dumps([anonymous, inv])
        for private in (namespace, sid, str(self.db), "source_namespace", "native_session_id", "usage_id", "provider_request_id"):
            self.assertNotIn(private, encoded)
        self.assertEqual(anonymous["total"], events[0]["total"])
        self.assertEqual(anonymous["goose"]["native_tokens"], events[0]["goose"]["native_tokens"])
        self.assertEqual(inv["roots"][0]["sessions"][0]["counters"]["accumulated_total_tokens"], 2100)
        self.assertEqual(before, json.dumps([events, info], sort_keys=True))
        # Exercise the publication CLI as well as direct transformations.
        src, dst = self.root / "source.jsonl", self.root / "anon.jsonl"
        src.write_text(json.dumps(events[0]) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "scripts/anonymize.py"), "--salt", "synthetic-private-salt", "--in", str(src), "--out", str(dst)], check=True, capture_output=True)
        self.assertEqual(json.loads(dst.read_text(encoding="utf-8")), anonymous)

    def test_multiple_invocations_same_usage_are_not_collapsed(self):
        invocation(self.conn)
        invocation(self.conn)
        events, _ = self.collect()
        self.assertEqual(len({e["request_id"] for e in events}), 2)
        self.assertEqual(sum(e["total"] for e in events), 2100)
        self.assertTrue(all(e["provider"] is None for e in events))

    def test_multiple_sessions_and_model_switch(self):
        invocation(self.conn)
        invocation(self.conn, model="synthetic-model-b", provider="provider-b", input_tokens=1200)
        invocation(self.conn, sid="20261012_2", model="synthetic-model-b", provider="provider-c")
        events, _ = self.collect()
        self.assertEqual([e["provider"] for e in events], ["synthetic-provider-a", "provider-b", "provider-c"])
        self.assertEqual(len({e["session"] for e in events}), 2)
        self.assertEqual([e["model"] for e in events], ["synthetic-model-a", "synthetic-model-b", "synthetic-model-b"])

    def test_same_model_provider_switch_ambiguous_is_unknown(self):
        invocation(self.conn, provider="provider-a")
        invocation(self.conn, provider="provider-b")
        events, _ = self.collect()
        self.assertTrue(all(e["provider"] is None for e in events))

    def test_no_session_provider_fallback(self):
        invocation(self.conn, provider="new-provider", message=False)
        events, _ = self.collect()
        self.assertIsNone(events[0]["provider"])
        self.assertEqual(events[0]["provider_confidence"], "unavailable")

    def test_missing_cache_and_reasoning_are_not_claimed_observed_zero(self):
        invocation(self.conn, cache_read=None, cache_write=None)
        events, _ = self.collect()
        e = events[0]
        self.assertEqual(e["input_uncached"], 1000)
        self.assertEqual(e["total"], 1050)
        self.assertIsNone(e["goose"]["native_tokens"]["cache_read_tokens"])
        self.assertIsNone(e["goose"]["native_tokens"]["reasoning_tokens"])
        self.assertEqual(e["reasoning"], 0)  # Legacy arithmetic sentinel, not additional tokens.

    def test_unpersisted_reasoning_metadata_is_not_invented(self):
        invocation(self.conn)
        self.conn.execute("UPDATE messages SET metadata_json=json_set(metadata_json, '$.usage.reasoningTokens', 37)")
        self.conn.commit()
        e = self.collect()[0][0]
        self.assertEqual(e["total"], 1050)
        self.assertIsNone(e["goose"]["native_tokens"]["reasoning_tokens"])

    def test_missing_input_stays_nonbillable_metadata(self):
        invocation(self.conn, input_tokens=None)
        events, info = self.collect()
        self.assertEqual(events, [])
        self.assertEqual(info["excluded_usage"][0]["native_tokens"]["output_tokens"], 50)
        self.assertEqual(info["excluded_rows"], {"missing_input_or_output": 1})

    def test_inconsistent_categories_and_totals_are_not_clamped(self):
        invocation(self.conn, input_tokens=1)
        invocation(self.conn)
        self.conn.execute("UPDATE usage_ledger SET total_tokens=999999 WHERE id=2")
        self.conn.commit()
        events, info = self.collect()
        self.assertEqual(events, [])
        self.assertEqual(info["excluded_rows"], {"inconsistent_token_categories": 2})

    def test_negative_or_nonnumeric_tokens_are_excluded(self):
        invocation(self.conn)
        for invalid in (-1, "one", 1.5):
            with self.subTest(invalid=invalid):
                self.conn.execute("UPDATE usage_ledger SET input_tokens=?", (invalid,))
                self.conn.commit()
                self.assertEqual(self.collect()[0], [])

    def test_cost_observation_and_estimate_are_separate_from_pricing(self):
        invocation(self.conn, cost=0, cost_source="provider_reported")
        invocation(self.conn, model="synthetic-model-b", cost=2, cost_source="estimated")
        events, _ = self.collect()
        self.assertEqual([e["goose"]["native_cost"]["source"] for e in events], ["provider_reported", "estimated"])
        self.assertEqual(events[0]["goose"]["native_cost"]["amount"], 0)
        self.assertIsNone(events[0]["goose"]["native_cost"]["currency"])
        self.assertNotIn("cost_usd", events[0])
        self.assertAlmostEqual(compiler.price_event(events[1], pricing())[0], .00219)

    def test_carried_forward_and_session_counters_are_not_calls(self):
        invocation(self.conn, model=None, cost_source="carried_forward", message=False, input_tokens=700)
        invocation(self.conn)
        events, info = self.collect()
        self.assertEqual(len(events), 1)
        self.assertEqual(info["excluded_rows"], {"carried_forward": 1})
        self.assertEqual(info["sessions"][0]["counters"]["accumulated_total_tokens"], 1800)
        self.assertEqual(info["sessions"][0]["collected_native_tokens"]["total_tokens"], 1050)
        self.assertEqual(info["excluded_usage"][0]["native_tokens"]["total_tokens"], 750)

    def test_compaction_survives_missing_messages(self):
        invocation(self.conn, compaction=True)
        self.conn.execute("DELETE FROM messages")
        self.conn.commit()
        events, _ = self.collect()
        self.assertEqual(events[0]["kind"], "compaction")
        self.assertEqual(events[0]["total"], 1050)

    def test_old_and_future_schema_are_coverage_only(self):
        invocation(self.conn)
        for version in (14, 15, 16, 18):
            with self.subTest(version=version):
                self.conn.execute("UPDATE schema_version SET version=?", (version,))
                self.conn.commit()
                events, info = self.collect()
                self.assertEqual(events, [])
                self.assertEqual(info["status"], "unsupported_schema")
                self.assertEqual(info["sessions"][0]["counters"]["accumulated_total_tokens"], 1050)

    def test_corrupt_and_missing_database(self):
        missing = self.root / "missing.db"
        self.assertEqual(goose.collect(str(missing), "h")[1]["status"], "missing_database")
        missing.write_bytes(b"not sqlite " + PRIVATE.encode())
        result = goose.collect(str(missing), "h")
        self.assertEqual(result[1]["status"], "unreadable_or_corrupt_source")
        self.assertNotIn(PRIVATE, json.dumps(result))

    def test_inaccessible_source(self):
        with mock.patch.object(goose, "_fingerprint", side_effect=PermissionError("secret path")):
            events, info = self.collect()
        self.assertEqual(events, [])
        self.assertEqual(info["errors"], 1)
        self.assertNotIn("secret path", json.dumps(info))

    def test_locked_rollback_database_is_retryable(self):
        invocation(self.conn)
        self.conn.execute("BEGIN EXCLUSIVE")
        self.conn.execute("UPDATE sessions SET name='pending'")
        events, info = self.collect()
        self.assertEqual(events, [])
        self.assertEqual(info["status"], "rollback_journal_retry")
        self.conn.rollback()
        self.assertEqual(len(self.collect()[0]), 1)

    def test_source_database_and_files_unchanged(self):
        invocation(self.conn)
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.db.parent.iterdir()}
        self.collect()
        after = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.db.parent.iterdir()}
        self.assertEqual(before, after)

    def test_closed_wal_database_does_not_create_source_sidecars(self):
        self.conn.close()
        self.db.unlink()
        self.conn = database(self.db, wal=True)
        invocation(self.conn)
        self.conn.close()
        self.assertFalse(Path(str(self.db) + "-wal").exists())
        self.assertEqual(len(self.collect()[0]), 1)
        self.assertEqual([p.name for p in self.db.parent.iterdir()], ["sessions.db"])

    def test_live_wal_committed_and_uncommitted_usage(self):
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA wal_autocheckpoint=0")
        invocation(self.conn)
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.db.parent.iterdir()}
        self.assertEqual(len(self.collect()[0]), 1)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.db.parent.iterdir()})
        invocation(self.conn, commit=False)
        self.assertEqual(len(self.collect()[0]), 1)
        self.conn.commit()
        self.assertEqual(len(self.collect()[0]), 2)

    def test_concurrent_commit_during_copy_retries_without_partial_events(self):
        self.conn.execute("PRAGMA journal_mode=WAL")
        invocation(self.conn)
        original = goose._fingerprint
        changed = False

        def copy_then_commit(source, destination=None):
            nonlocal changed
            result = original(source, destination)
            if destination is not None and not changed:
                changed = True
                invocation(self.conn)
            return result

        with mock.patch.object(goose, "_fingerprint", side_effect=copy_then_commit):
            events, info = self.collect()
        self.assertEqual(len(events), 2)
        self.assertEqual(info["status"], "ok")

    def test_continuous_source_change_fails_closed_and_cleans_snapshot(self):
        invocation(self.conn)
        original = goose._fingerprint
        temp_root = self.root / "private-tmp"
        temp_root.mkdir()

        def moving_source(source, destination=None):
            result = original(source, destination)
            if destination is not None:
                invocation(self.conn)
            return result

        with mock.patch.object(goose, "_fingerprint", side_effect=moving_source), mock.patch.object(tempfile, "tempdir", str(temp_root)):
            events, info = self.collect()
        self.assertEqual(events, [])
        self.assertEqual(info["status"], "source_changed_retry")
        self.assertEqual(list(temp_root.iterdir()), [])

    def test_separate_writer_commits_between_snapshot_reads(self):
        self.conn.execute("PRAGMA journal_mode=WAL")
        invocation(self.conn)
        original = goose._fingerprint
        start, done = threading.Event(), threading.Event()
        failures = []

        def writer():
            try:
                if not start.wait(10):
                    raise AssertionError("snapshot never reached the writer barrier")
                with closing(sqlite3.connect(self.db)) as conn:
                    invocation(conn, model="synthetic-model-b")
            except BaseException as ex:
                failures.append(ex)
            finally:
                done.set()

        thread = threading.Thread(target=writer)
        thread.start()
        triggered = False

        def capture(source, destination=None):
            nonlocal triggered
            result = original(source, destination)
            if destination is not None and not triggered:
                triggered = True
                start.set()
                self.assertTrue(done.wait(10))
            return result

        try:
            with mock.patch.object(goose, "_fingerprint", side_effect=capture):
                events, info = self.collect()
        finally:
            start.set()
            thread.join(10)
        self.assertFalse(thread.is_alive())
        self.assertEqual(failures, [])
        self.assertEqual((len(events), info["status"]), (2, "ok"))
        self.assertEqual(sum(e["total"] for e in events), 2100)

    def test_late_provider_metadata_never_creates_a_new_identity(self):
        invocation(self.conn)
        metadata = self.conn.execute("SELECT metadata_json FROM messages").fetchone()[0]
        self.conn.execute("UPDATE messages SET metadata_json='{}'")
        self.conn.commit()
        old = self.collect()[0][0]
        self.assertIsNone(old["provider"])
        self.conn.execute("UPDATE messages SET metadata_json=?", (metadata,))
        self.conn.commit()
        new = self.collect()[0][0]
        self.assertEqual(old["request_id"], new["request_id"])
        self.assertEqual(new["provider_confidence"], "inferred_unique_message_usage")

    def test_native_cost_never_becomes_an_unverified_usd_charge(self):
        invocation(self.conn, cost_source="provider_reported")
        event = self.collect()[0][0]
        value = compiler.price_event(event, pricing())
        self.assertAlmostEqual(value[0], .00219)
        self.assertIn("native cost evidence is separate", value[3])
        logged = {"models": {event["model"]: {"use_logged_cost": True}}}
        value = compiler.price_event(event, logged)
        self.assertIsNone(value[2])
        self.assertIn("no currency-verified", value[3])

    def test_snapshot_connection_rejects_writes(self):
        invocation(self.conn)
        with goose.snapshot(self.db) as conn:
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("DELETE FROM usage_ledger")

    def test_replicas_share_explicit_namespace_only(self):
        invocation(self.conn)
        copied = self.root / "copy.db"
        shutil.copyfile(self.db, copied)
        original = self.collect()[0][0]
        replica = goose.collect("fixture=" + str(copied), "fixture-host")[0][0]
        self.assertEqual(original["request_id"], replica["request_id"])
        self.assertNotEqual(goose.collect(str(self.db), "h")[0][0]["request_id"], goose.collect(str(copied), "h")[0][0]["request_id"])
        self.assertEqual(goose.split_root(str(self.db))[0], goose.split_root(str(self.db.parent))[0])

    def test_legacy_totals_grow_without_billable_events(self):
        path = self.root / "legacy" / "20261012_1.jsonl"
        path.parent.mkdir()
        for total in (1050, 1050, 1550):
            path.write_text(json.dumps(export_header(total=total)) + "\n" + json.dumps({"content": PRIVATE}) + "\n", encoding="utf-8")
            events, info = goose.collect(str(path.parent), "h")
            self.assertEqual(events, [])
            self.assertEqual(info["legacy"][0]["counters"]["accumulated_total_tokens"], total)
            self.assertNotIn(PRIVATE, json.dumps(info))

    def test_exports_and_legacy_are_not_generic_calls(self):
        exports = self.root / "exports"
        exports.mkdir()
        node = export_header()
        node["conversation"] = [{"metadata": {"usage": {"input_tokens": 1000, "output_tokens": 50}}, "content": PRIVATE}]
        (exports / "goose.json").write_text(json.dumps(node), encoding="utf-8")
        (exports / "old.jsonl").write_text(json.dumps(export_header()) + "\n" + json.dumps(node["conversation"][0]) + "\n", encoding="utf-8")
        out = io.StringIO()
        compiler.scan_generic(str(exports), "h", out, compiler.Stats(), [], io.StringIO(), "generic")
        self.assertEqual(out.getvalue(), "")
        events, info = goose.collect(str(exports / "goose.json"), "h")
        self.assertEqual(events, [])
        self.assertIn("export_not_billable", info["status"])

    def test_ordinary_generic_records_still_work(self):
        exports = self.root / "other-agent"
        exports.mkdir()
        (exports / "usage.json").write_text(json.dumps({"model": "other-model", "usage": {"input_tokens": 20, "output_tokens": 10}}), encoding="utf-8")
        out = io.StringIO()
        compiler.scan_generic(str(exports), "h", out, compiler.Stats(), [], io.StringIO(), "other")
        self.assertEqual(json.loads(out.getvalue())["total"], 30)

    def test_invalid_roots_and_credentials_are_refused(self):
        for spec in ("relative", "../sessions", "bad namespace=" + str(self.db), str(self.root / "auth.json"), "x=" + str(self.root) + "/../outside"):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                goose.split_root(spec)
        secret = self.db.parent / "credentials.jsonl"
        secret.write_text(PRIVATE, encoding="utf-8")
        invocation(self.conn)
        with mock.patch.object(goose, "_legacy_header", wraps=goose._legacy_header) as reader:
            self.collect()
        reader.assert_not_called()

    @unittest.skipIf(os.name == "nt", "Windows symlink privilege is not assumed")
    def test_symlink_database_is_not_followed(self):
        invocation(self.conn)
        link = self.root / "symlink.db"
        link.symlink_to(self.db)
        self.assertEqual(goose.collect(str(link), "h")[1]["status"], "non_regular_source")


class DiscoveryTests(unittest.TestCase):
    def test_cross_platform_paths_and_overrides(self):
        self.assertEqual(goose.candidate_roots("/home/u", "linux", {}), ["/home/u/.local/share/goose/sessions"])
        self.assertEqual(goose.candidate_roots("/Users/u", "darwin", {}), ["/Users/u/.local/share/goose/sessions"])
        self.assertEqual(goose.candidate_roots("/Users/u", "darwin", {"XDG_DATA_HOME": "/volume/data"}), ["/volume/data/goose/sessions"])
        self.assertEqual(goose.candidate_roots("/u", "linux", {"GOOSE_PATH_ROOT": "/isolated", "XDG_DATA_HOME": "/ignored"}), ["/isolated/data/sessions"])
        self.assertEqual(goose.candidate_roots("/u", "linux", {"GOOSE_PATH_ROOT": "relative", "XDG_DATA_HOME": "relative"}), ["/u/.local/share/goose/sessions"])
        self.assertEqual(goose.candidate_roots(r"C:\Users\u", "win32", {}), [r"C:\Users\u\AppData\Roaming\Block\goose\data\sessions"])
        self.assertEqual(goose.candidate_roots(r"C:\Users\u", "win32", {"APPDATA": r"D:\Roaming"}), [r"D:\Roaming\Block\goose\data\sessions"])
        self.assertEqual(goose.candidate_roots(r"C:\Users\u", "win32", {"GOOSE_PATH_ROOT": r"D:\Goose"}), [r"D:\Goose\data\sessions"])

    def test_detection_respects_profile_env_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            custom = root / "custom"
            (custom / "data" / "sessions").mkdir(parents=True)
            with mock.patch.dict(os.environ, {"GOOSE_PATH_ROOT": str(custom)}, clear=True):
                self.assertEqual(detect_hosts.detect_roots(str(root), use_env=True)[0]["goose_roots"], [str(custom / "data" / "sessions")])
                self.assertNotIn("goose_roots", detect_hosts.detect_roots(str(root), use_env=False)[0])

    def test_manifest_flags_and_disable(self):
        host = {"name": "fixture", "goose_roots": ["local=/synthetic/goose/sessions"]}
        args = run_pipeline.scan_args(host)
        self.assertIn("--no-prompts", args)
        self.assertIn("--goose-root", args)
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / "manifest.json", Path(tmp) / "filtered.json"
            src.write_text(json.dumps({"hosts": [host]}), encoding="utf-8")
            self.assertEqual(ledger.filter_manifest(str(src), str(dst), only=["goose"]), ["fixture"])
            self.assertEqual(ledger.filter_manifest(str(src), str(dst), skip=["goose"]), [])

    def test_detected_goose_has_only_an_unknown_billing_placeholder(self):
        host = {"name": "fixture-host", "kind": "local", "goose_roots": ["/synthetic/goose"]}
        with mock.patch.object(detect_hosts, "read_codex_account", side_effect=AssertionError("credential read")), mock.patch.object(detect_hosts, "read_claude_account", side_effect=AssertionError("credential read")):
            accounts = detect_hosts.draft_accounts([host])
        rule = next(r for r in accounts["rules"] if r["when"].get("tool") == "goose")
        self.assertEqual(rule["when"], {"tool": "goose", "host": "fixture-host"})
        self.assertEqual(rule["billing"], "unknown")
        self.assertEqual(rule["confidence"], "low")
        self.assertEqual(accounts["accounts"][rule["account"]]["provider"], "mixed")
        self.assertFalse(any(r["when"].get("tool") == "goose" for r in detect_hosts.draft_accounts([])["rules"]))

    def test_pricing_compiler_loads_without_preloaded_script_path(self):
        code = "import importlib.util; s=importlib.util.spec_from_file_location('isolated_pricing', %r); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); assert callable(m.price_event)" % str(ROOT / "scripts/compile_ai_logs.py")
        subprocess.run([sys.executable, "-I", "-c", code], check=True, capture_output=True)

    def test_remote_scanner_stages_native_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = {"name": "fixture", "kind": "ssh", "ssh": "user@example.invalid", "remote_tmp": "/tmp/ai-ledger-fixture", "python": "python3", "goose_roots": ["/synthetic/sessions"]}
            with mock.patch.object(run_pipeline, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
                run_pipeline.scan_host(host, tmp)
            self.assertTrue(any(any(str(arg).endswith("/goose_usage.py") for arg in call.args[0]) for call in run.call_args_list))


class EndToEndTests(unittest.TestCase):
    def test_scanner_store_query_price_report_replay_and_growth(self):
        for kind in ("sqlite", "json", "csv"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp, ExitStack() as cleanup:
                root = Path(tmp)
                db = root / "sessions" / "sessions.db"
                conn = database(db, wal=True)
                cleanup.callback(conn.close)
                invocation(conn)
                paths = {"events": root / "work" / "scans" / "fixture-host" / "events.fixture-host.jsonl",
                         "sessions": root / "work" / "scans" / "fixture-host" / "sessions.fixture-host.jsonl"}
                manifest = root / "manifest.json"
                manifest.write_text(json.dumps({"workdir": str(root / "work"), "hosts": [{"name": "fixture-host", "kind": "local", "goose_roots": ["fixture=" + str(db)]}]}), encoding="utf-8")
                store_path = root / ("ledger.db" if kind == "sqlite" else "ledger-store")
                store = ledger_store.Store.open(kind, str(store_path))
                cleanup.callback(store.close)

                def scan():
                    subprocess.run([sys.executable, str(ROOT / "scripts/run_pipeline.py"), "--manifest", str(manifest), "--only", "scan"], check=True, capture_output=True, text=True)
                    return store.ingest_events_file(str(paths["events"]))

                self.assertEqual(scan(), (1, 0))
                self.assertEqual(scan(), (0, 1))
                invocation(conn, model="synthetic-model-b", input_tokens=1500, output_tokens=100, timestamp=STAMP + 60)
                self.assertEqual(scan(), (1, 1))
                self.assertEqual(scan(), (0, 2))
                store.ingest_sessions_file(str(paths["sessions"]))
                query = ledger_query.open_db(kind, str(store_path))
                try:
                    self.assertEqual(query.execute("SELECT COUNT(*), SUM(total) FROM events WHERE tool='goose'").fetchone(), (2, 2650))
                    self.assertEqual(len(query.execute("SELECT model, session, SUM(total) FROM events WHERE tool='goose' GROUP BY model, session").fetchall()), 2)
                finally:
                    query.close()
                price_file = root / "pricing.json"
                price_file.write_text(json.dumps(pricing()), encoding="utf-8")
                if os.name != "nt":
                    price_file.chmod(0o600)
                config = {"workdir": str(root), "store": {"kind": kind, "path": str(store_path)}, "pricing_path": str(price_file), "timezone": "UTC"}
                output, data = scoped_report.generate_report(config, "2026-10-12", "2026-10-12", out=str(root / "report"), now=datetime(2026, 10, 13, tzinfo=timezone.utc))
                self.assertEqual(data["totals"]["total"], 2650)
                self.assertAlmostEqual(data["totals"]["api_equivalent_usd"], .00588)
                self.assertEqual(data["totals"]["calls"], 2)
                self.assertNotIn(PRIVATE, (output / "report.html").read_text(encoding="utf-8"))
                inventory = json.loads((paths["events"].parent / "inventory.fixture-host.json").read_text(encoding="utf-8"))
                self.assertEqual(inventory["roots"][0]["sessions"][0]["counters"]["accumulated_total_tokens"], 2650)
                self.assertFalse((paths["events"].parent / "prompts.fixture-host.jsonl").exists())
                store.close()
                conn.close()


if __name__ == "__main__":
    unittest.main()
