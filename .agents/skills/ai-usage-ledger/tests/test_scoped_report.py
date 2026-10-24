#!/usr/bin/env python3
"""Synthetic regression tests for read-only, timezone-aware scoped usage reports."""
import contextlib
import csv
import hashlib
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ledger_store  # noqa: E402
import scoped_report as report  # noqa: E402

UTC = timezone.utc
NOW = datetime(2024, 6, 15, 16, 30, 1, 123456, tzinfo=UTC)
TZ = "America/New_York"


def event(ts="2024-06-15T04:00:00Z", **changes):
    result = {"ts": ts, "tool": "synthetic-tool", "host": "synthetic-host", "session": "synthetic-session",
              "model": "synthetic-model", "input_uncached": 100, "cache_read": 200, "cache_write": 30,
              "cache_write_5m": 10, "cache_write_1h": 20, "output": 40, "reasoning": 10,
              "total": 370, "cost_usd": None, "cwd": "/private/path/never-export",
              "src": "/private/log/never-export", "account_id": "private-account-never-export",
              "text": "private-prompt-never-export"}
    result.update(changes)
    return result


def pricing():
    return {"_as_of": "2024-06-15", "_sources": ["https://example.org/pricing"],
            "models": {"synthetic-model": {"input": 2, "cache_read": .2, "cache_write_5m": 2.5,
                                           "cache_write_1h": 4, "output": 10,
                                           "source": "https://example.org/pricing",
                                           "verified_at": "2024-06-15", "service_tier": "standard"}}}


class BoundsTests(unittest.TestCase):
    def test_today_and_now_use_configured_local_day(self):
        scope = report.parse_scope("today", tz=TZ, now=NOW)
        self.assertEqual(scope.start, datetime(2024, 6, 15, 4, tzinfo=UTC))
        self.assertEqual(scope.end, NOW)
        self.assertTrue(scope.end_inclusive)
        # Shortly after UTC midnight is still the prior New York calendar day.
        early = datetime(2024, 6, 15, 1, tzinfo=UTC)
        self.assertEqual(report.parse_scope("today", tz=TZ, now=early).start,
                         datetime(2024, 6, 14, 4, tzinfo=UTC))

    def test_date_end_includes_local_day_and_excludes_next_midnight(self):
        scope = report.parse_scope("2024-06-15", "2024-06-15", TZ, NOW)
        self.assertEqual(scope.end, datetime(2024, 6, 16, 4, tzinfo=UTC))
        self.assertFalse(scope.end_inclusive)
        self.assertTrue(scope.contains(datetime(2024, 6, 16, 3, 59, 59, 999999, tzinfo=UTC)))
        self.assertFalse(scope.contains(scope.end))

    def test_timestamp_end_is_inclusive_to_microsecond(self):
        scope = report.parse_scope("2024-06-15T00:00:00", "2024-06-15T12:30:01.123456-04:00", TZ, NOW)
        self.assertEqual(scope.end, NOW)
        self.assertTrue(scope.contains(NOW))
        self.assertFalse(scope.contains(NOW.replace(microsecond=123457)))
        same = report.parse_scope("2024-06-15T04:00:00Z", "2024-06-15T00:00:00-04:00", TZ, NOW)
        self.assertTrue(same.contains(same.start))

    def test_dst_days_are_23_and_25_hours(self):
        spring = report.parse_scope("2024-03-10", "2024-03-10", TZ, NOW)
        fall = report.parse_scope("2024-11-03", "2024-11-03", TZ, NOW)
        self.assertEqual((spring.end - spring.start).total_seconds(), 23 * 3600)
        self.assertEqual((fall.end - fall.start).total_seconds(), 25 * 3600)

    def test_naive_dst_gap_and_fold_require_offset(self):
        for stamp, word in (("2024-03-10T02:30:00", "nonexistent"), ("2024-11-03T01:30:00", "ambiguous")):
            with self.subTest(stamp=stamp), self.assertRaisesRegex(ValueError, word):
                report.parse_scope(stamp, "2024-12-01", TZ, NOW)
        first = report.parse_scope("2024-11-03T01:30:00-04:00", "2024-11-03T01:30:00-05:00", TZ, NOW)
        self.assertEqual((first.end - first.start).total_seconds(), 3600)

    def test_bad_or_reversed_bounds_fail(self):
        for since, until, zone in (("yesterday", None, TZ), ("2024-02-30", None, TZ),
                                   ("2024-06-16", "2024-06-14", TZ),
                                   ("2024-06-15T05:00Z", "2024-06-15T04:00Z", TZ),
                                   ("today", None, "Not/A/Timezone"),
                                   ("2024-06-15T04:00:00.1234567Z", None, TZ)):
            with self.subTest(since=since, until=until, zone=zone), self.assertRaises(ValueError):
                report.parse_scope(since, until, zone, NOW)


class AggregationTests(unittest.TestCase):
    def collect(self, events, prices=None, until=None):
        return report.collect(events, report.parse_scope("today", until, TZ, NOW), prices or pricing(), NOW)

    def test_scope_excludes_before_midnight_and_after_exact_cutoff(self):
        events = [event("2024-06-15T03:59:59.999999Z"), event(), event("2024-06-15T12:30:01.123456-04:00"),
                  event("2024-06-15T16:30:01.123457Z"), event("2024-06-16T04:00:00Z")]
        data, selected = self.collect(events)
        self.assertEqual(data["totals"]["calls"], 2)
        self.assertEqual(data["totals"]["total"], 740)
        self.assertEqual(data["freshness"]["latest_in_scope_event_utc"], NOW.isoformat())
        self.assertEqual(data["freshness"]["latest_recorded_event_utc"], "2024-06-16T04:00:00+00:00")
        self.assertEqual(len(selected), 2)

    def test_scope_is_applied_before_token_validation_and_pricing(self):
        invalid_outside = event("2024-06-14T12:00:00Z", total=-123, input_uncached="invalid")
        data, _ = self.collect([invalid_outside, event()])
        self.assertEqual(data["totals"]["calls"], 1)

    def test_exact_arithmetic_and_cache_write_ttls(self):
        data, selected = self.collect([event()])
        self.assertAlmostEqual(data["totals"]["api_equivalent_usd"], .000745, places=12)
        self.assertAlmostEqual(data["totals"]["without_cache_usd"], .00106, places=12)
        self.assertAlmostEqual(data["totals"]["cache_savings_usd"], .000315, places=12)
        self.assertEqual(selected[0]["cache_write_1h"], 20)
        fallback_ttl, _ = self.collect([event(cache_write_5m=None, cache_write_1h=None)])
        self.assertAlmostEqual(fallback_ttl["totals"]["api_equivalent_usd"], .000715, places=12)

    def test_unknown_fallback_is_assumed_even_without_note_and_unpriced_is_not_free(self):
        prices = pricing()
        prices["fallback_by_tool"] = {"synthetic-tool": {"model": "synthetic-model"}}
        events = [event(), event(model="undocumented"), event(model="missing", tool="unsupported-tool")]
        data, selected = self.collect(events, prices)
        totals = data["totals"]
        self.assertEqual((totals["calls"], totals["priced_calls"], totals["unpriced_calls"], totals["assumed_calls"]),
                         (3, 2, 1, 1))
        self.assertEqual(totals["unpriced_tokens"], 370)
        self.assertEqual(data["pricing"]["assumed_share_of_priced_cost"], .5)
        self.assertIsNone(selected[-1]["api_equivalent_usd"])
        self.assertEqual({row["status"] for row in data["pricing"]["exceptions"]}, {"assumed", "unpriced"})

    def test_explicit_assumed_rate_and_provider_alias(self):
        prices = pricing()
        data, _ = self.collect([event(model="provider/synthetic-model")], prices)
        self.assertEqual(data["totals"]["assumed_calls"], 0)
        prices["models"]["synthetic-model"]["assumed"] = "Synthetic model-family assumption"
        data, _ = self.collect([event(model="provider/synthetic-model")], prices)
        self.assertEqual(data["totals"]["assumed_calls"], 1)
        self.assertEqual(data["pricing"]["assumed_share_of_priced_cost"], 1)

    def test_logged_cost_is_excluded_from_standard_api_equivalent(self):
        prices = pricing()
        prices["models"]["logged-only"] = {"use_logged_cost": True}
        data, selected = self.collect([event(model="logged-only", cost_usd=999)], prices)
        self.assertEqual(data["totals"]["unpriced_calls"], 1)
        self.assertEqual(data["totals"]["api_equivalent_usd"], 0)
        self.assertIsNone(selected[0]["api_equivalent_usd"])

    def test_shared_pricer_applies_long_context(self):
        prices = pricing()
        prices["models"]["synthetic-model"]["long_context"] = {"input_tokens_gt": 329, "input": 4,
            "cache_read": .4, "cache_write_5m": 5, "cache_write_1h": 8, "output": 20}
        data, _ = self.collect([event()], prices)
        self.assertAlmostEqual(data["totals"]["api_equivalent_usd"], .00149, places=12)

    def test_stored_replay_handling_is_not_reapplied(self):
        # Both are true stored child calls, even when their timestamps and usage match.
        data, _ = self.collect([event(session="child"), event(session="child")])
        self.assertEqual(data["totals"]["calls"], 2)
        self.assertEqual(data["sessions"], 1)
        self.assertEqual(data["totals"]["total"], 740)

    def test_invalid_timestamps_are_counted_without_guessing_timezone(self):
        data, _ = self.collect([event(), event("2024-06-15T04:00:00"), event(None), event("invalid")])
        self.assertEqual(data["totals"]["calls"], 1)
        self.assertEqual(data["limitations"]["records_with_unusable_timestamps"], 3)

    def test_invalid_token_totals_and_rates_fail(self):
        for bad in (event(total=999), event(reasoning=999), event(cache_write_1h=21),
                    event(cache_write_5m=None, cache_write_1h=20), event(input_uncached=-1)):
            with self.subTest(event=bad), self.assertRaises(ValueError):
                self.collect([bad])
        for bad_rate in (float("nan"), -1, "2"):
            prices = pricing()
            prices["models"]["synthetic-model"]["input"] = bad_rate
            with self.subTest(rate=bad_rate), self.assertRaises(ValueError):
                self.collect([event()], prices)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.prices = self.base / "prices.json"
        self.prices.write_text(json.dumps(pricing()), encoding="utf-8")
        self.report_config = self.base / "report-config.json"
        self.report_config.write_text(json.dumps({"branding": {"name": "Synthetic brand", "eyebrow": "Synthetic brand",
                                                               "footer": "Internal synthetic report"},
                                                  "theme_default": "dark"}), encoding="utf-8")

    def config(self, events, kind="sqlite"):
        path = self.base / ("store-" + kind + (".sqlite" if kind == "sqlite" else ""))
        if kind == "sqlite":
            db = sqlite3.connect(path)
            db.execute("CREATE TABLE events (%s, extra TEXT)" % ", ".join(ledger_store.EVENT_COLUMNS))
            for index, item in enumerate(events):
                row = dict(item, id="record-%d" % index, seq=index, date="1900-01-01", extra="private-prompt-never-export")
                keys = ledger_store.EVENT_COLUMNS + ["extra"]
                db.execute("INSERT INTO events VALUES (%s)" % ",".join("?" for _ in keys), [row.get(k) for k in keys])
            db.commit()
            db.close()
        else:
            path.mkdir()
            if kind == "json":
                (path / "events.jsonl").write_text("".join(json.dumps(item) + "\n" for item in events), encoding="utf-8")
            else:
                with (path / "events.csv").open("w", encoding="utf-8", newline="") as fh:
                    writer = csv.DictWriter(fh, fieldnames=list(events[0]) if events else list(report.READ_FIELDS))
                    writer.writeheader()
                    writer.writerows(events)
            # A reporting command must not parse either unrelated file.
            (path / "prompts.jsonl").write_text("unparseable private-prompt-never-export", encoding="utf-8")
            (path / "sessions.jsonl").write_text("unparseable sessions", encoding="utf-8")
        return {"store": {"kind": kind, "path": str(path)}, "timezone": TZ, "workdir": str(self.base / "work"),
                "pricing_path": str(self.prices), "report_config_path": str(self.report_config)}

    def generate(self, config, **kwargs):
        return report.generate_report(config, "today", now=NOW, **kwargs)

    def test_all_backends_identical_and_never_query_prompts(self):
        results = []
        for kind in ("sqlite", "json", "csv"):
            cfg = self.config([event(), event("2024-06-15T01:00:00Z")], kind)
            before = {str(p): p.read_bytes() for p in self.base.rglob("*") if p.is_file()}
            out, data = self.generate(cfg)
            results.append(data["totals"])
            self.assertEqual(out.parent, self.base / "work" / "reports")
            for name, original in before.items():
                self.assertEqual(Path(name).read_bytes(), original, name)
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])

    def test_no_default_query_limit(self):
        cfg = self.config([event(session="session-%d" % i) for i in range(120)])
        _, data = self.generate(cfg)
        self.assertEqual(data["totals"]["calls"], 120)
        self.assertEqual(data["sessions"], 120)

    def test_override_is_report_only_and_artifacts_are_private_and_hash_bound(self):
        cfg = self.config([event()])
        replacement = pricing()
        replacement["models"]["synthetic-model"]["output"] = 20
        override = self.base / "override.json"
        override.write_text(json.dumps(replacement), encoding="utf-8")
        config_copy = json.dumps(cfg, sort_keys=True)
        original = {p: p.read_bytes() for p in (self.prices, override, Path(cfg["store"]["path"]))}
        out, data = self.generate(cfg, pricing_path=override)
        self.assertAlmostEqual(data["totals"]["api_equivalent_usd"], .001145, places=12)
        self.assertEqual(json.loads((out / "pricing.json").read_text()), replacement)
        self.assertEqual(json.dumps(cfg, sort_keys=True), config_copy)
        for p, blob in original.items():
            self.assertEqual(p.read_bytes(), blob)
        self.assertEqual({p.name for p in out.iterdir()}, {"report.html", "report-data.json", "pricing.json", "events.csv", "SHA256SUMS"})
        for line in (out / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split("  ")
            self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest)
        for p in out.iterdir():
            contents = p.read_text(encoding="utf-8")
            for private in ("private-prompt-never-export", "private-account-never-export", "/private/path/never-export",
                            "/private/log/never-export", "synthetic-session"):
                self.assertNotIn(private, contents)
            if os.name != "nt":
                self.assertEqual(p.stat().st_mode & 0o077, 0)
        if os.name != "nt":
            self.assertEqual(out.stat().st_mode & 0o077, 0)
        with (out / "events.csv").open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertNotIn("session", rows[0])
        self.assertNotIn("src", rows[0])
        self.assertEqual(len(rows), 1)

    def test_output_reuse_refused_and_empty_directory_allowed(self):
        cfg = self.config([event()])
        target = self.base / "explicit-report"
        target.mkdir()
        out, _ = self.generate(cfg, out=target)
        original = (out / "report.html").read_bytes()
        with self.assertRaisesRegex(ValueError, "new or empty"):
            self.generate(cfg, out=target)
        self.assertEqual((out / "report.html").read_bytes(), original)
        one, _ = self.generate(cfg)
        two, _ = self.generate(cfg)
        self.assertNotEqual(one, two)

    def test_output_symlink_refused(self):
        target = self.base / "target"
        target.mkdir()
        link = self.base / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks unavailable for this test user")
        cfg = self.config([event()])
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.generate(cfg, out=link)
        self.assertFalse(any(target.iterdir()))

    def test_html_and_csv_escape_record_fields_and_preserve_brand_theme(self):
        hostile = '<script>alert("x")</script>|\n# fake heading'
        cfg = self.config([event(model=hostile, tool="=SUM(1,2)")])
        out, _ = self.generate(cfg)
        page = (out / "report.html").read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn('<script>alert("x")</script>', page)
        self.assertNotIn("<h1>fake heading", page)
        self.assertIn("Synthetic brand", page)
        self.assertIn('var DEF="dark"', page)
        self.assertIn("Content-Security-Policy", page)
        self.assertIn("API equivalent (priced calls only)", page)
        self.assertIn("No same-period provider-counter comparison is performed", page)
        self.assertNotIn("Subscriptions actually paid", page)
        with (out / "events.csv").open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(rows[0]["tool"], "'=SUM(1,2)")
        self.assertEqual(rows[0]["model"], hostile)
        self.assertEqual(rows[0]["api_equivalent_usd"], "")

    def test_empty_interval_is_a_valid_zero_usage_report(self):
        cfg = self.config([event("2024-06-14T00:00:00Z")])
        out, data = self.generate(cfg)
        self.assertEqual(data["totals"]["calls"], 0)
        self.assertIsNone(data["freshness"]["latest_in_scope_event_utc"])
        self.assertIn("$0.00", (out / "report.html").read_text())
        with (out / "events.csv").open(newline="") as fh:
            self.assertEqual(list(csv.DictReader(fh)), [])

    def test_main_reads_old_config_without_migration(self):
        cfg = self.config([event()])
        cfg.update(version=1, _reconcile_wsl=True, manifest_path=str(self.base / "manifest.json"))
        (self.base / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
        (self.base / "manifest.json").write_text('{"hosts": ["unrelated manifest"]}', encoding="utf-8")
        originals = {p: p.read_bytes() for p in self.base.iterdir() if p.is_file()}
        with mock.patch.dict(os.environ, {"AI_USAGE_LEDGER_HOME": str(self.base)}), contextlib.redirect_stdout(io.StringIO()):
            result = report.main(["--since", "2024-06-15", "--until", "2024-06-15", "--tz", TZ])
        self.assertEqual(result, 0)
        for p, blob in originals.items():
            self.assertEqual(p.read_bytes(), blob)


if __name__ == "__main__":
    unittest.main(verbosity=2)
