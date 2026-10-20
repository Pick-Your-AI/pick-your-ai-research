"""Synthetic raw-input checks for proposal intake; no source or price claims."""
from decimal import Decimal
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path("scripts/validate_research.py")
SUCCESS = "Validated 1 catalog proposals and"
TOKEN = "synthetic raw numeric token"


class IntakeNumericPrecision(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        shutil.copytree(ROOT / "contracts/v1/schemas",
                        self.root / "contracts/v1/schemas")
        for relative in (SCRIPT, Path("schemas/evidence-manifest.schema.json")):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.item = {
            "schema_version": "1.0.0", "id": "test.workload", "kind": "workload",
            "tier": "T0", "name": "Synthetic workload", "version": "1",
            "status": "active", "billing_class": "unknown",
            "spec": {"workload_type": "chat", "modalities": ["text"],
                     "concurrency": 1, "uptime_target_pct": 99},
            "provenance": [{
                "source_uri": "https://github.com/Pick-Your-AI/pick-your-ai-research",
                "checked_at": "2026-10-16T09:00:00Z", "verification_status": "unverified",
            }],
            "updated_at": "2026-10-16T09:00:00Z",
        }
        self.book = {
            "schema_version": "1.0.0", "id": "test.prices", "revision": 1,
            "captured_at": "2026-10-16T09:00:00Z",
            "rates": [{
                "id": "test.rate", "catalog_item_id": "test.workload",
                "catalog_item_version": "1", "meter": "request",
                "unit_price": {"amount": "0.1", "currency": "USD"},
                "valid_from": "2026-10-16T09:00:00Z",
                "provenance": self.item["provenance"][0], "price_type": "estimate",
            }],
        }
        self.manifest = {
            "id": "test.artifact", "uri": "s3://test-bucket/data", "version": "1",
            "sha256": "a" * 64, "access": "restricted",
            "description": "Synthetic test only", "rights": "Test only",
        }
        self.install()

    def write(self, relative, payload, token=None):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(payload)
        if token is not None:
            self.assertEqual(text.count(json.dumps(TOKEN)), 1)
            text = text.replace(json.dumps(TOKEN), token)
        target.write_text(text + "\n", encoding="utf-8")
        return target

    def install(self, target=None, token=None):
        item = json.loads(json.dumps(self.item))
        book = json.loads(json.dumps(self.book))
        manifest = json.loads(json.dumps(self.manifest))
        if target == "revision":
            book["revision"] = TOKEN
        elif target in {"concurrency", "uptime_target_pct"}:
            item["spec"][target] = TOKEN
        elif target == "manifest":
            manifest["description"] = TOKEN
        self.write("catalog/proposals/item.json", item,
                   token if target in {"concurrency", "uptime_target_pct"} else None)
        self.write("pricing/proposals/prices.json", book,
                   token if target == "revision" else None)
        self.write("evidence/artifact.json", manifest,
                   token if target == "manifest" else None)

    def run_cli(self, optimized):
        before = {str(path.relative_to(self.root)): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        command = [sys.executable, "-B", *(["-O"] if optimized else []),
                   str(self.root / SCRIPT)]
        result = subprocess.run(
            command, cwd=self.root, capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        after = {str(path.relative_to(self.root)): path.read_bytes()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after, "Validation must not rewrite its input tree")
        return result

    def assert_valid(self, result, books=1):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"{SUCCESS} {books} pricebooks", result.stdout)
        self.assertEqual(result.stderr, "")

    def assert_invalid(self, result, field):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("INVALID:", result.stdout)
        self.assertIn(field, result.stdout)
        self.assertNotIn(SUCCESS, result.stdout)
        self.assertEqual(result.stderr, "")

    def test_pricebook_revision_cannot_round_to_an_admitted_integer(self):
        for optimized in (False, True):
            for token in ("1.0000000000000001", "0.99999999999999999",
                          "9007199254740992.1", "123456789012345678901234567890.1"):
                with self.subTest(optimized=optimized, token=token):
                    self.install("revision", token)
                    self.assert_invalid(self.run_cli(optimized), "/revision")

    def test_catalog_integer_and_number_bounds_keep_original_value(self):
        cases = (("concurrency", "1.0000000000000001"),
                 ("concurrency", "0.99999999999999999"),
                 ("uptime_target_pct", "100.00000000000000001"),
                 ("uptime_target_pct", "-1e-1000"))
        for optimized in (False, True):
            for field, token in cases:
                with self.subTest(optimized=optimized, field=field, token=token):
                    self.install(field, token)
                    self.assert_invalid(self.run_cli(optimized), "/spec/" + field)

    def test_distinct_wide_revisions_do_not_collapse_to_duplicate_identity(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.install("revision", "9007199254740992")
                second = {**self.book, "revision": TOKEN}
                self.write("pricing/proposals/second.json", second, "9007199254740993.0")
                self.assert_valid(self.run_cli(optimized), books=2)

    def test_equivalent_numeric_revision_spellings_remain_duplicates(self):
        for optimized in (False, True):
            for token in ("1.0", "1.00e0"):
                with self.subTest(optimized=optimized, token=token):
                    self.install()
                    second = {**self.book, "revision": TOKEN}
                    self.write("pricing/proposals/second.json", second, token)
                    self.assert_invalid(self.run_cli(optimized), "duplicate pricebook revision")

    def test_valid_integer_spellings_and_fractional_numbers_still_pass(self):
        cases = (("revision", "1.0"), ("revision", "1.00e2"),
                 ("revision", "9007199254740993.0"),
                 ("revision", "1" + "0" * 400),
                 ("concurrency", "2.0"), ("uptime_target_pct", "0.1"),
                 ("uptime_target_pct", "1e-1000"),
                 ("uptime_target_pct", "0e999999999999999999999999999999"),
                 ("uptime_target_pct", "-0.0"), ("uptime_target_pct", "100.00"))
        for optimized in (False, True):
            for field, token in cases:
                with self.subTest(optimized=optimized, field=field, token=token):
                    self.install(field, token)
                    self.assert_valid(self.run_cli(optimized))

    def test_nonfinite_overflow_and_original_type_rejections_remain(self):
        for optimized in (False, True):
            for target, token, diagnostic in (
                    ("revision", "true", "/revision"),
                    ("revision", "null", "/revision"),
                    ("revision", '"1"', "/revision"),
                    ("revision", "0.0", "/revision"),
                    ("uptime_target_pct", "1e400", "finite"),
                    ("uptime_target_pct", "-1e400", "finite"),
                    ("manifest", "NaN", "finite"),
                    ("manifest", "Infinity", "finite"),
                    ("manifest", "-Infinity", "finite")):
                with self.subTest(optimized=optimized, target=target, token=token):
                    self.install(target, token)
                    self.assert_invalid(self.run_cli(optimized), diagnostic)

    def test_unrepresentable_exact_numbers_fail_through_input_diagnostics(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.install("uptime_target_pct", "1e-999999999999999999999999999999")
                self.assert_invalid(self.run_cli(optimized), "exact decimal range")

    def test_duplicate_keys_remain_rejected_before_numeric_admission(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.install("revision", "1, \"revision\": 2")
                self.assert_invalid(self.run_cli(optimized), "duplicate JSON object key")

    def test_default_reader_and_shared_validator_keep_legacy_number_types(self):
        spec = importlib.util.spec_from_file_location("intake_legacy_control", ROOT / SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        raw = '{"decimal":1.00e2,"tiny":-1e-1000,"wide":9007199254740993,"text":"0.1"}'
        value = module.intake_json(raw)
        self.assertIs(type(value["decimal"]), float)
        self.assertIs(type(value["tiny"]), float)
        self.assertIs(type(value["wide"]), int)
        self.assertEqual(json.dumps(value), json.dumps(json.loads(raw)))
        self.assertFalse(Draft202012Validator.TYPE_CHECKER.is_type(Decimal("1.0"), "integer"))


if __name__ == "__main__":
    unittest.main()
