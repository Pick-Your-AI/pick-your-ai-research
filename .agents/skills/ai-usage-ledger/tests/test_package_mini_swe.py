"""Synthetic, offline integration contract; runnable with only Python stdlib."""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import anonymize  # noqa: E402
import compile_ai_logs as scanner  # noqa: E402
import detect_hosts  # noqa: E402
import ledger_store  # noqa: E402
import mini_swe_export as exporter  # noqa: E402
import mini_swe_usage as usage  # noqa: E402
import run_pipeline  # noqa: E402


def response(id="call-1", model="model-a", **counts):
    return {"id": id, "model": model, "created": 1780000000, "usage": {
        "prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, **counts},
        "choices": [{"message": {"role": "assistant", "content": "PRIVATE-COMPLETION"}}]}


def trajectory(*responses, backend="minisweagent.models.litellm_model.LitellmModel"):
    return {"trajectory_format": usage.TRAJECTORY, "info": {"config": {
        "model": {"model_name": "openai/model-a", "api_key": "PRIVATE-KEY"}, "model_type": backend}},
        "messages": [{"role": "user", "content": "PRIVATE-PROMPT"}] + [
            {"role": "assistant", "extra": {"response": r, "cost": 0.012}, "content": "PRIVATE-OUTPUT"} for r in responses]}


class FormatError(Exception):
    def __init__(self):
        self.messages = [{"role": "user", "extra": {"interrupt_type": "FormatError"}}]


class NativeShape:
    """Deterministic adapter double; live adapter behavior is tested separately."""
    def __init__(self, *, model_name="openai/model-a", mode="completed", input_tokens=100, **kwargs):
        self.config = SimpleNamespace(model_name=model_name, model_kwargs={})
        self.mode, self.input_tokens, self.attempts = mode, input_tokens, 0
        self.returned = None

    def _query(self, messages, **kwargs):
        self.attempts += 1
        if self.mode == "network_error" or self.mode == "retry" and self.attempts == 1:
            raise ConnectionError("PRIVATE-KEY-NETWORK-ERROR")
        self.returned = response(id=kwargs.get("id", "call-1"), model=self.config.model_name,
                                 prompt_tokens=self.input_tokens, total_tokens=self.input_tokens + 20)
        return self.returned

    def _calculate_cost(self, value):
        if self.mode == "cost_error":
            raise RuntimeError("PRIVATE-PRICING-ERROR")
        if self.mode == "portkey_mutation":
            value["usage"]["prompt_tokens"] = -20
        if self.mode == "cancelled":
            raise KeyboardInterrupt()
        return {"cost": 0 if self.mode == "local" else 0.012}

    def query(self, messages, **kwargs):
        try:
            value = self._query(messages, **kwargs)
        except ConnectionError:
            if self.mode != "retry":
                raise
            value = self._query(messages, **kwargs)
        cost = self._calculate_cost(value)
        if self.mode == "format_error":
            error = FormatError()
            error.messages[0]["extra"].update(response=value, **cost)
            raise error
        if self.mode == "post_response_error":
            raise RuntimeError("global cost limit remains enforced")
        return {"role": "assistant", "extra": {"response": value, **cost}}


class MiniSweTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.addCleanup(self.tmp.cleanup)

    def collect(self, documents):
        for name, data in documents.items():
            (self.root / name).write_text(json.dumps(data), encoding="utf-8")
        out, stats, sessions = io.StringIO(), scanner.Stats(), []
        usage.scan(str(self.root), "test-host", out, stats, sessions, set())
        return [json.loads(line) for line in out.getvalue().splitlines()], stats

    def normalize(self, raw=None, **kwargs):
        snap = usage.usage_snapshot(raw or response(), backend=kwargs.pop("backend", "litellm"),
                                   requested_model="openai/model-a", **kwargs)
        return usage.normalize(snap, "test-host", self.root / "run.traj.json")

    def test_backend_shapes(self):
        for backend in ("litellm", "litellm_textbased", "litellm_response", "openrouter", "openrouter_textbased",
                        "openrouter_response", "portkey", "portkey_response", "requesty", "custom"):
            with self.subTest(backend=backend):
                raw = response()
                if "response" in backend:
                    raw["usage"] = {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120}
                e = self.normalize(raw, backend=backend)
                self.assertEqual((e["input_uncached"], e["output"], e["total"]), (100, 20, 120))
                if backend.startswith(("openrouter", "portkey", "requesty")):
                    self.assertEqual(e["provider"], backend.split("_")[0])

    def test_cache_read_write_reasoning_not_double_counted(self):
        e = self.normalize(response(prompt_tokens_details={"cached_tokens": 30, "cache_write_tokens": 10},
                                    completion_tokens_details={"reasoning_tokens": 7}))
        self.assertEqual([e[k] for k in ("input_uncached", "cache_read", "cache_write", "output", "reasoning", "total")],
                         [60, 30, 10, 20, 7, 120])

    def test_responses_categories(self):
        r = response()
        r["usage"] = {"input_tokens": 100, "output_tokens": 20, "input_tokens_details": {"cached_tokens": 40},
                      "output_tokens_details": {"reasoning_tokens": 5}}
        e = self.normalize(r, backend="litellm_response")
        self.assertEqual([e[k] for k in ("input_uncached", "cache_read", "reasoning", "total")], [60, 40, 5, 120])

    def test_native_anthropic_exclusive_cache_and_ttl(self):
        r = response()
        r["usage"] = {"input_tokens": 60, "output_tokens": 20, "cache_read_input_tokens": 30,
                      "cache_creation_input_tokens": 10, "cache_creation": {"ephemeral_5m_input_tokens": 6, "ephemeral_1h_input_tokens": 4}}
        e = self.normalize(r, backend="custom")
        self.assertEqual((e["input_uncached"], e["total"], e["cache_write_5m"], e["cache_write_1h"]), (60, 120, 6, 4))

    def test_litellm_normalized_cache_creation(self):
        e = self.normalize(response(cache_creation_input_tokens=10, cache_read_input_tokens=30,
                                    prompt_tokens_details={"cached_tokens": 30, "cache_creation_tokens": 10}))
        self.assertEqual((e["input_uncached"], e["cache_write"], e["total"]), (60, 10, 120))

    def test_missing_and_malformed_totals_never_rewrite_prompt(self):
        for total in (None, 0, -5, "120", True, float("nan"), 10**100):
            with self.subTest(total=repr(total)):
                e = self.normalize(response(total_tokens=total))
                self.assertEqual((e["input_uncached"], e["output"], e["total"]), (100, 20, 120))
                self.assertEqual(e["total_provenance"], "sum_components")

    def test_partial_custom_metadata_and_total_only(self):
        for fields, expected in (({"output_tokens": 9}, (0, 9, 9)), ({"total_tokens": 17}, (0, 0, 17))):
            e = self.normalize({"usage": fields})
            self.assertEqual((e["input_uncached"], e["output"], e["total"]), expected)
            self.assertTrue(e["partial"])
            self.assertIsNone(e["ts"])
        self.assertEqual(e["unclassified_tokens"], 17)

    def test_malformed_counts_and_conflicting_cache_preserve_evidence(self):
        for bad in (-1, 1.5, True, "100", float("inf"), 10**100):
            e = self.normalize(response(prompt_tokens=bad))
            self.assertEqual(e["input_uncached"], 0)
            self.assertIn("invalid:prompt_tokens", e["usage_warnings"])
        e = self.normalize(response(prompt_tokens_details={"cached_tokens": 150}))
        self.assertEqual((e["total"], e["input_uncached"]), (120, 100))
        self.assertEqual(e["reported_usage"]["prompt_tokens_details"]["cached_tokens"], 150)
        self.assertIn("cache_categories_exceed_input", e["usage_warnings"])

    def test_cost_independent_tokens_and_no_price_database(self):
        for cost in (None, 0, 0.034, -1, float("nan")):
            e = self.normalize(response(cost=cost))
            self.assertEqual(e["total"], 120)
            self.assertEqual(e["provider_reported_cost"], cost if cost is not None and cost >= 0 and cost == cost else None)
        pricing = {"models": {"model-a": {"input": 2, "output": 4, "cache_read": 1, "cache_write_5m": 3, "cache_write_1h": 4}}}
        e = self.normalize(response(cost=99))
        result = scanner.price_event(e, pricing)
        self.assertAlmostEqual(result[0], 0.00028)
        self.assertNotEqual(result[0], 99)

    def test_no_usage_no_fabricated_event(self):
        for raw in ({}, {"error": "network failure"}, {"usage": {"cost": 10}}, {"usage": {"input_tokens": -10}}):
            self.assertIsNone(usage.usage_snapshot(raw))

    def test_format_error_and_responses_trajectory(self):
        t = trajectory(response())
        t["messages"][1]["role"] = "user"
        t["messages"][1]["extra"]["interrupt_type"] = "FormatError"
        r = response(id="resp-2", model="model-b")
        r.update(object="response", output=[{"text": "PRIVATE-RESPONSES"}])
        t["messages"].append(r)
        events, _ = self.collect({"format.traj.json": t})
        self.assertEqual(len(events), 2)
        self.assertEqual([e["execution_status"] for e in events], ["format_error", "completed"])
        self.assertEqual([e["model"] for e in events], ["model-a", "model-b"])
        self.assertNotIn("PRIVATE", json.dumps(events))

    def test_duplicates_copies_resumed_and_multiple_models(self):
        t = trajectory(response(), response(id="call-2", model="model-b"))
        events, stats = self.collect({"old.traj.json": trajectory(response()), "resumed.traj.json": t, "copy.traj.json": t})
        self.assertEqual((len(events), stats.dedup), (2, 3))
        self.assertEqual(sum(e["total"] for e in events), 240)
        self.assertEqual({e["model"] for e in events}, {"model-a", "model-b"})

    def test_no_id_no_time_independent_runs_not_collapsed(self):
        r = {"usage": {"input_tokens": 10, "output_tokens": 5}}
        events, _ = self.collect({"a.traj.json": trajectory(r, r), "b.traj.json": trajectory(r)})
        self.assertEqual(len(events), 3)
        self.assertEqual(len({e["request_id"] for e in events}), 3)

    def test_malformed_file_and_jsonl_does_not_abort_scan(self):
        (self.root / "broken.traj.json").write_text('{"messages": [', encoding="utf-8")
        snap = usage.usage_snapshot(response(), backend="litellm", requested_model="openai/model-a")
        (self.root / "run.usage.jsonl").write_text(json.dumps(snap) + "\nINVALID\n" + json.dumps({**snap, "source_request_id": "call-2"}), encoding="utf-8")
        events, stats = self.collect({})
        self.assertEqual((len(events), stats.errors), (2, 2))

    def test_consent_default_and_generic_duplicate_exclusion(self):
        source = self.root / "run.traj.json"
        source.write_text(json.dumps(trajectory(response())), encoding="utf-8")
        original = source.read_bytes()
        out = self.root / "out"
        cmd = [sys.executable, str(ROOT / "scripts/compile_ai_logs.py"), "scan", "--host", "test-host", "--no-prompts", "--out-dir", str(out)]
        subprocess.run(cmd + ["--generic-root", "generic=" + str(self.root)], check=True, capture_output=True)
        self.assertEqual((out / "events.test-host.jsonl").read_text(), "")
        subprocess.run(cmd + ["--mini-swe-root", str(source)], check=True, capture_output=True)
        self.assertEqual(len((out / "events.test-host.jsonl").read_text().splitlines()), 1)
        self.assertFalse((out / "prompts.test-host.jsonl").exists())
        self.assertEqual(source.read_bytes(), original)

    def test_discovery_is_candidate_only(self):
        directory = self.root / ".config/mini-swe-agent"
        directory.mkdir(parents=True)
        (directory / "last_mini_run.traj.json").write_text("{}")
        manifest, found = detect_hosts.detect_roots(str(self.root))
        self.assertNotIn("mini_swe_roots", manifest)
        self.assertTrue(any("mini-SWE-agent candidate" in item for item in found))
        args = run_pipeline.scan_args({"name": "test-host", "mini_swe_roots": [str(directory)]}, False)
        self.assertIn("--mini-swe-root", args)
        self.assertIn("--no-prompts", args)

    def test_repeated_ingestion_all_stores(self):
        events, _ = self.collect({"run.traj.json": trajectory(response(), response(id="call-2"))})
        path = self.root / "events.jsonl"
        path.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        for kind in ("sqlite", "json", "csv"):
            with self.subTest(kind=kind):
                store = ledger_store.Store.open(kind, str(self.root / ("store-" + kind)))
                try:
                    self.assertEqual(store.ingest_events_file(str(path)), (2, 0))
                    self.assertEqual(store.ingest_events_file(str(path)), (0, 2))
                    rows = list(store.iter_events())
                    self.assertEqual(sum(r["total"] for r in rows), 240)
                    self.assertEqual(rows[0]["reported_usage"]["prompt_tokens"], 100)
                finally:
                    store.close()

    def test_export_disabled_does_not_add_metadata_or_files(self):
        model = exporter.usage_model(NativeShape)()
        result = model.query([])
        self.assertNotIn("mini_swe_usage", result["extra"])
        self.assertEqual(list(self.root.iterdir()), [])

    def model(self, mode="completed", **kwargs):
        return exporter.usage_model(NativeShape)(usage_export_dir=str(self.root / "usage"), usage_provider="openai", mode=mode, **kwargs)

    def test_export_success_error_cancel_and_limit_semantics(self):
        for mode, error, status in (("completed", None, "completed"), ("cost_error", RuntimeError, "cost_error"),
                                   ("format_error", FormatError, "format_error"), ("cancelled", KeyboardInterrupt, "cancelled"),
                                   ("post_response_error", RuntimeError, "post_response_error"), ("local", None, "completed")):
            with self.subTest(mode=mode):
                model = self.model(mode)
                if error:
                    with self.assertRaises(error):
                        model.query([], id=mode)
                else:
                    result = model.query([], id=mode)
                    self.assertIn("mini_swe_usage", result["extra"])
                records = [json.loads(p.read_text()) for p in (self.root / "usage").glob("*.usage.json")]
                record = next(r for r in records if r["source_request_id"] == mode)
                self.assertEqual((record["status"], record["usage"]["prompt_tokens"]), (status, 100))
                self.assertNotIn("PRIVATE", json.dumps(record))
                if mode == "local":
                    self.assertEqual(record["calculated_cost"], 0)

    def test_response_saved_before_pricing_mutates_usage(self):
        model = self.model("portkey_mutation")
        result = model.query([])
        self.assertEqual(result["extra"]["response"]["usage"]["prompt_tokens"], -20)
        self.assertEqual(result["extra"]["mini_swe_usage"]["usage"]["prompt_tokens"], 100)
        events, _ = self.collect({"mutated.traj.json": {"trajectory_format": usage.TRAJECTORY, "messages": [result]}})
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["input_uncached"], 100)

    def test_retry_and_network_failure(self):
        model = self.model("retry")
        model.query([])
        self.assertEqual(model.attempts, 2)
        self.assertEqual(len(list((self.root / "usage").glob("*.usage.json"))), 1)
        with self.assertRaises(ConnectionError):
            self.model("network_error").query([])
        self.assertEqual(len(list((self.root / "usage").glob("*.usage.json"))), 1)

    def test_export_trajectory_overlap_and_resumed_model_change(self):
        first = self.model().query([])
        second = self.model(model_name="other/model-b").query([first], id="call-2")
        self.assertEqual(first["extra"]["mini_swe_usage"]["session_id"], second["extra"]["mini_swe_usage"]["session_id"])
        events, stats = self.collect({"resumed.traj.json": {"trajectory_format": usage.TRAJECTORY, "messages": [first, second]}})
        self.assertEqual((len(events), stats.dedup), (2, 2))
        self.assertEqual({e["model"] for e in events}, {"openai/model-a", "other/model-b"})

    def test_concurrent_agents_same_export_directory(self):
        # Directory setup is done before concurrent invocations, as in real configuration.
        model = self.model()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: model.query([], id="parallel-" + str(i)), range(32)))
        records = [r["extra"]["mini_swe_usage"] for r in results]
        self.assertEqual(len({r["run_id"] for r in records}), 32)
        self.assertEqual(len(list((self.root / "usage").glob("*.usage.json"))), 32)
        events, _ = self.collect({})
        self.assertEqual((len(events), sum(e["total"] for e in events)), (32, 3840))

    def test_atomic_export_permissions_and_no_temp_leftovers(self):
        self.model().query([])
        files = list((self.root / "usage").iterdir())
        self.assertEqual(len(files), 1)
        if os.name != "nt":
            self.assertEqual(files[0].stat().st_mode & 0o777, 0o600)
            self.assertEqual(files[0].parent.stat().st_mode & 0o777, 0o700)

    def test_io_failure_does_not_retry_provider(self):
        model = self.model()
        (self.root / "usage").rmdir()
        with self.assertLogs("mini_swe_export", level="WARNING"):
            result = model.query([])
        self.assertEqual(model.attempts, 1)
        self.assertEqual(result["extra"]["mini_swe_usage"]["usage"]["prompt_tokens"], 100)

    def test_anonymization_and_strict_allowlist(self):
        raw = response()
        raw["usage"]["credentials"] = {"api_key": "PRIVATE-KEY"}
        snap = usage.usage_snapshot(raw, backend="litellm", requested_model="openai/model-a")
        snap.update(invocation_id="id-123", session_id="my-session", run_id="run-123", agent_id="agent-123", prompt="PRIVATE-PROMPT")
        clean = usage.sanitize_snapshot(snap)
        e = usage.normalize(clean, "private-host", self.root / "run.traj.json")
        anon = anonymize.Anonymizer("test-salt").event(e)
        self.assertNotIn("PRIVATE", json.dumps(anon))
        for key in ("source_request_id", "invocation_id", "run_id", "agent_id"):
            self.assertNotEqual(anon[key], e[key])
        self.assertNotIn("src", anon)

    def test_file_size_limit_and_symlink_not_followed(self):
        if os.name == "nt":
            self.skipTest("Windows symlink permissions vary")
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "hidden.traj.json").write_text(json.dumps(trajectory(response())))
        root = self.root / "source"
        root.mkdir()
        (root / "link.traj.json").symlink_to(outside / "hidden.traj.json")
        (root / "linked-directory").symlink_to(outside, target_is_directory=True)
        output, stats = io.StringIO(), scanner.Stats()
        usage.scan(str(root), "test-host", output, stats, [], set())
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
