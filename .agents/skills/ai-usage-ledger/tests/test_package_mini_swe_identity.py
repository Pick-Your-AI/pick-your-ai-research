"""Observed-provider identity regression; synthetic data and real ledger stores."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import compile_ai_logs as scanner  # noqa: E402
import ledger_store  # noqa: E402
import mini_swe_usage as usage  # noqa: E402


def response(provider=None):
    return {"id": "shared-response-id", "model": "shared-model", "provider": provider,
            "created": 1780000000,
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}}


def trajectory(*responses):
    return {"trajectory_format": usage.TRAJECTORY,
            "info": {"config": {"model_type": "minisweagent.models.litellm_model.LitellmModel",
                                "model": {"model_name": "routing-alias"}}},
            "messages": [{"role": "assistant", "extra": {"response": value}} for value in responses]}


class MiniSweProviderIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def snapshot(self, observed=None, **kwargs):
        return usage.usage_snapshot(response(observed), backend="litellm",
                                    requested_model=kwargs.pop("requested_model", "routing-alias"), **kwargs)

    def event(self, snapshot):
        return usage.normalize(snapshot, "test-host", self.root / "run.traj.json")

    def scan(self):
        output, stats = io.StringIO(), scanner.Stats()
        usage.scan(str(self.root), "test-host", output, stats, [], set())
        return [json.loads(line) for line in output.getvalue().splitlines()], stats

    def test_different_observed_providers_do_not_collide(self):
        for requested, configured in (("routing-alias", None), ("openai/shared-model", None),
                                      ("routing-alias", "custom-endpoint")):
            with self.subTest(requested=requested, configured=configured):
                left = self.event(self.snapshot("provider-a", requested_model=requested, provider=configured))
                right = self.event(self.snapshot("provider-b", requested_model=requested, provider=configured))
                self.assertNotEqual(left["request_id"], right["request_id"])
                self.assertEqual(left["provider"], right["provider"])
                self.assertEqual((left["upstream_provider"], right["upstream_provider"]),
                                 ("provider-a", "provider-b"))

    def test_observed_provider_not_routing_alias_namespaces_identity(self):
        left = self.event(self.snapshot("provider-a", provider="route-a"))
        right = self.event(self.snapshot("provider-a", provider="route-b"))
        self.assertEqual(left["request_id"], right["request_id"])
        self.assertEqual((left["provider"], right["provider"]), ("route-a", "route-b"))
        self.assertEqual(left["request_id"], "mini-swe:" + usage.digest(
            "provider", "provider-a", "shared-model", "shared-response-id"))

    def test_missing_or_invalid_observed_provider_preserves_fallback(self):
        for observed in (None, "", "https://invalid.example/?secret=no", {"not": "an identifier"}):
            with self.subTest(observed=observed):
                event = self.event(self.snapshot(observed, provider="configured-provider"))
                self.assertEqual(event["request_id"], "mini-swe:" + usage.digest(
                    "provider", "configured-provider", "shared-model", "shared-response-id"))
                self.assertIsNone(event["upstream_provider"])

    def test_export_trajectory_copies_and_resume_share_namespace(self):
        document = trajectory(response("provider-a"), response("provider-b"))
        (self.root / "run.traj.json").write_text(json.dumps(document), encoding="utf-8")
        (self.root / "resumed.traj.json").write_text(json.dumps(document), encoding="utf-8")
        for provider in ("provider-a", "provider-b"):
            snapshot = self.snapshot(provider)
            snapshot.update(invocation_id=provider + "-invocation", session_id="resumed-session", status="completed")
            (self.root / (provider + ".usage.json")).write_text(json.dumps(snapshot), encoding="utf-8")
        original = {path.name: path.read_bytes() for path in self.root.iterdir()}
        events, stats = self.scan()
        self.assertEqual((len(events), stats.dedup), (2, 4))
        self.assertEqual({event["upstream_provider"] for event in events}, {"provider-a", "provider-b"})
        self.assertEqual(sum(event["total"] for event in events), 240)
        replay, replay_stats = self.scan()
        self.assertEqual(events, replay)
        self.assertEqual(replay_stats.dedup, 4)
        self.assertEqual(original, {path.name: path.read_bytes() for path in self.root.iterdir()})

    def test_distinct_providers_survive_all_stores_and_repeated_scans(self):
        (self.root / "run.traj.json").write_text(json.dumps(
            trajectory(response("provider-a"), response("provider-b"))), encoding="utf-8")
        for kind in ("sqlite", "json", "csv"):
            with self.subTest(store=kind):
                store = ledger_store.Store.open(kind, str(self.root / ("store-" + kind)))
                try:
                    for expected in ((2, 0), (0, 2)):
                        events, _ = self.scan()
                        output = self.root / "events.jsonl"
                        output.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
                        self.assertEqual(store.ingest_events_file(str(output)), expected)
                    stored = list(store.iter_events())
                    self.assertEqual(len(stored), 2)
                    self.assertEqual(len({event["request_id"] for event in stored}), 2)
                    self.assertEqual(sum(event["total"] for event in stored), 240)
                finally:
                    store.close()

    def test_invocation_fallback_unchanged_without_response_id(self):
        ids = []
        for provider in ("provider-a", "provider-b", None):
            snapshot = self.snapshot(provider)
            snapshot.update(source_request_id=None, invocation_id="one-export-invocation")
            event = self.event(snapshot)
            self.assertEqual(event["identity_provenance"], "export_invocation_id")
            ids.append(event["request_id"])
        self.assertEqual(len(set(ids)), 1)


if __name__ == "__main__":
    unittest.main()
