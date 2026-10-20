"""Synthetic plan-admission cases only; no downloads, models or device tests."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_mr09_olmoe_plan.py"
SPEC = importlib.util.spec_from_file_location("mr09_olmoe_plan", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class OLMoEPlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = CHECKER.strict_json(ROOT / CHECKER.PLAN)

    def validate(self, plan=None):
        return CHECKER.validate_plan(self.plan if plan is None else plan)

    def copy_support(self, root):
        for relative in (CHECKER.SCHEMA, CHECKER.HISTORICAL_PLAN, Path("schemas/evidence-manifest.schema.json")):
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, root / relative)
        (root / "evidence").mkdir()
        for shard in self.plan["weight_shards"]:
            name = shard["external_manifest"]
            shutil.copyfile(ROOT / "evidence" / name, root / "evidence" / name)

    def test_committed_plan_preserves_unexecuted_accounting(self):
        result = self.validate()
        self.assertEqual(result, {
            "classification": "selected_offline_design_not_executed",
            "execution_status": "unexecuted",
            "load_artifact_bytes": 13841132070,
            "storage_budget_bytes": 29829747788,
            "host_budget_bytes": 32508883880,
        })
        self.assertEqual([cell["derived_bf16_kv_payload_bytes"] for cell in self.plan["cells"]],
                         [37748736, 272629760, 545259520, None])

    def test_row_order_does_not_change_inventory_or_budget(self):
        expected = self.validate()
        for field in ("weight_shards", "metadata_files", "cells", "retained_unknowns"):
            self.plan[field].reverse()
        self.plan["loader"]["source_files"].reverse()
        self.assertEqual(self.validate(), expected)

    def test_larger_explicit_allowances_remain_consistent(self):
        screens = self.plan["screens"]
        screens["complete_artifact_copies"] = 3
        screens["storage_budget_bytes"] += self.plan["totals"]["load_artifact_bytes"]
        screens["minimum_available_storage_bytes"] = screens["storage_budget_bytes"]
        screens["host_process_reserve_bytes"] += CHECKER.GIB
        screens["host_budget_bytes"] += CHECKER.GIB
        screens["minimum_available_host_bytes"] = screens["host_budget_bytes"]
        result = self.validate()
        self.assertEqual(result["storage_budget_bytes"], 43670879858)
        self.assertEqual(result["host_budget_bytes"], 33582625704)

    def test_duplicate_named_rows_cannot_hide_missing_inventory(self):
        cases = (("weight_shards", "file"), ("metadata_files", "file"), ("cells", "id"))
        for field, key in cases:
            candidate = copy.deepcopy(self.plan)
            candidate[field][1][key] = candidate[field][0][key]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "duplicate"):
                self.validate(candidate)
        self.plan["loader"]["source_files"][1]["path"] = self.plan["loader"]["source_files"][0]["path"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.validate()

    def test_exact_integer_policy_applies_to_every_numeric_role(self):
        paths = (("weight_shards", 0, "bytes"), ("geometry", "layers"),
                 ("cells", 0, "active_sequences"), ("screens", "complete_artifact_copies"),
                 ("metadata_observation", "api_bytes"), ("loader", "visible_device_count"))
        for path in paths:
            for invalid in (True, False, 1.0, float("nan"), float("inf"), -1, 2 ** 64):
                candidate = copy.deepcopy(self.plan)
                parent = candidate
                for part in path[:-1]:
                    parent = parent[part]
                parent[path[-1]] = invalid
                with self.subTest(path=path, invalid=invalid), self.assertRaises(ValueError):
                    self.validate(candidate)

    def test_each_derived_total_is_checked(self):
        for field in self.plan["totals"]:
            candidate = copy.deepcopy(self.plan)
            candidate["totals"][field] -= 1
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "inconsistent arithmetic"):
                self.validate(candidate)

    def test_budget_totals_and_selected_minimums_cannot_be_understated(self):
        fields = ("complete_artifact_copies", "storage_reserve_bytes", "host_file_mapping_allowance_bytes",
                  "host_parameter_allowance_bytes", "host_conversion_allowance_bytes", "host_process_reserve_bytes",
                  "storage_budget_bytes", "host_budget_bytes")
        for field in fields:
            candidate = copy.deepcopy(self.plan)
            candidate["screens"][field] -= 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(candidate)
        for available, budget in (("minimum_available_storage_bytes", "storage_budget_bytes"),
                                  ("minimum_available_host_bytes", "host_budget_bytes")):
            candidate = copy.deepcopy(self.plan)
            candidate["screens"][available] = candidate["screens"][budget] - 1
            with self.subTest(field=available), self.assertRaisesRegex(ValueError, "below the planned budget"):
                self.validate(candidate)

    def test_each_historical_workload_and_cache_floor_is_bound(self):
        for index in range(4):
            for field in ("prompt_tokens", "decode_forwards", "active_sequences",
                          "terminal_cache_positions_per_sequence", "derived_bf16_kv_payload_bytes",
                          "derived_weights_plus_kv_floor_bytes"):
                candidate = copy.deepcopy(self.plan)
                current = candidate["cells"][index][field]
                candidate["cells"][index][field] = 1 if current is None else current + 1
                with self.subTest(index=index, field=field), self.assertRaises(ValueError):
                    self.validate(candidate)
        candidate = copy.deepcopy(self.plan)
        candidate["cells"][3]["kv_cache"] = "bf16"
        with self.assertRaisesRegex(ValueError, "historical cache policy"):
            self.validate(candidate)

    def test_unknowns_cannot_be_promoted_to_measurement_or_authorization(self):
        changes = (("metadata_observation", "weights_downloaded", True),
                   ("metadata_observation", "tokenizer_payload_downloaded", True),
                   ("screens", "gpu_process_cap_bytes", 20 * CHECKER.GIB),
                   ("screens", "gpu_workspace_allowance_bytes", CHECKER.GIB),
                   ("screens", "authorized_device_receipt", "synthetic"),
                   ("screens", "future_runner_sha256", "a" * 64))
        for section, field, value in changes:
            candidate = copy.deepcopy(self.plan)
            candidate[section][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(candidate)
        for field in ("classification", "execution_status"):
            candidate = copy.deepcopy(self.plan)
            candidate[field] = "measured"
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(candidate)
        candidate = copy.deepcopy(self.plan)
        candidate["cells"][0]["status"] = "measured"
        with self.assertRaises(ValueError):
            self.validate(candidate)
        self.plan["retained_unknowns"].pop()
        with self.assertRaises(ValueError):
            self.validate()

    def test_metadata_checksum_scope_is_specific_to_each_file(self):
        for index, row in enumerate(self.plan["metadata_files"]):
            candidate = copy.deepcopy(self.plan)
            candidate["metadata_files"][index]["observed_sha256"] = "a" * 64 if row["observed_sha256"] is None else None
            with self.subTest(file=row["file"]), self.assertRaisesRegex(ValueError, "checksum observation scope"):
                self.validate(candidate)
            candidate = copy.deepcopy(self.plan)
            candidate["metadata_files"][index]["observation"] = (
                "small_file_read_and_git_blob_matched" if row["file"] == "tokenizer.json"
                else "publisher_git_metadata_only")
            with self.subTest(file=row["file"], mode="scope"), self.assertRaisesRegex(ValueError, "observation scope"):
                self.validate(candidate)

    def test_manifest_linkage_is_checked_on_actual_local_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_support(root)
            CHECKER.validate_plan(self.plan, root)
            path = root / "evidence/mr09-olmoe-0924-instruct-shard-01.json"
            original = CHECKER.strict_json(path)
            for field, value in (("sha256", "a" * 64), ("version", "b" * 40), ("id", "synthetic"),
                                 ("uri", original["uri"] + "?token=synthetic")):
                changed = dict(original, **{field: value})
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, "differs from plan"):
                    CHECKER.validate_plan(self.plan, root)
            path.write_text(json.dumps(original), encoding="utf-8")
            CHECKER.validate_plan(self.plan, root)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "not a regular JSON file"):
                CHECKER.validate_plan(self.plan, root)

    def test_unknown_historical_cache_is_not_assumed_to_mean_int4(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_support(root)
            prior = CHECKER.strict_json(root / CHECKER.HISTORICAL_PLAN)
            prior["planned_cells"][3]["kv"] = "synthetic unrecognized cache"
            (root / CHECKER.HISTORICAL_PLAN).write_text(json.dumps(prior), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unrecognized historical cache policy"):
                CHECKER.validate_plan(self.plan, root)

    def test_manifest_names_hash_widths_and_closed_structure_are_strict(self):
        mutations = (
            lambda p: p["weight_shards"][0].update(external_manifest=p["weight_shards"][1]["external_manifest"]),
            lambda p: p["weight_shards"][0].update(external_manifest="../synthetic.json"),
            lambda p: p["weight_shards"][0].update(publisher_sha256=p["weight_shards"][0]["publisher_sha256"] + "\n"),
            lambda p: p["metadata_files"][0].update(publisher_git_blob="A" * 40),
            lambda p: p["loader"]["environment"].update(HF_DEACTIVATE_ASYNC_LOAD="0"),
            lambda p: p["loader"]["from_pretrained"].update(experts_implementation="grouped_mm"),
            lambda p: p.update(measured_peak_bytes=1),
        )
        for index, mutate in enumerate(mutations):
            candidate = copy.deepcopy(self.plan)
            mutate(candidate)
            with self.subTest(index=index), self.assertRaises(ValueError):
                self.validate(candidate)

    def test_observation_date_is_calendar_valid_and_utc(self):
        cases = (("access_date", "2026-02-30"),
                 ("api_observed_at", "2026-10-19T18:14:16"),
                 ("api_observed_at", "2026-10-19T18:14:16+01:00"),
                 ("api_observed_at", "2026-10-18T18:14:16Z"),
                 ("api_observed_at", "2026-10-19T18:14:16Z\n"))
        for field, value in cases:
            candidate = copy.deepcopy(self.plan)
            parent = candidate if field == "access_date" else candidate["metadata_observation"]
            parent[field] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.validate(candidate)

    def test_strict_reader_rejects_ambiguous_and_oversized_input(self):
        invalid = (b'{"nested":{"bytes":1,"bytes":2}}', b'{"x":NaN}', b'{"x":Infinity}',
                   b'{"x":1.0}', b'{"x":1e0}', b'{"x":1e999}', b'\xff',
                   b' ' * (CHECKER.MAX_JSON_BYTES + 1))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.json"
            for index, raw in enumerate(invalid):
                path.write_bytes(raw)
                with self.subTest(index=index), self.assertRaises(ValueError):
                    CHECKER.strict_json(path)

    def test_actual_cli_retains_semantic_checks_under_python_optimization(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = copy.deepcopy(self.plan)
            candidate["screens"]["host_budget_bytes"] -= 1
            path = Path(directory) / "synthetic-understated-budget.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            for mode in ("normal", "flag", "environment"):
                environment = os.environ.copy()
                environment.pop("PYTHONOPTIMIZE", None)
                command = [sys.executable]
                if mode == "flag":
                    command.append("-O")
                elif mode == "environment":
                    environment["PYTHONOPTIMIZE"] = "1"
                for valid in (True, False):
                    args = command + [str(SCRIPT)] + ([] if valid else ["--plan", str(path)])
                    result = subprocess.run(args, cwd=directory, env=environment, text=True,
                                            capture_output=True, timeout=30)
                    with self.subTest(mode=mode, valid=valid):
                        self.assertEqual(result.returncode, 0 if valid else 1, result.stderr)
                        if valid:
                            self.assertEqual(json.loads(result.stdout.splitlines()[0])["execution_status"], "unexecuted")
                            self.assertIn("no weight verification, runtime fit or measurement", result.stdout)
                            self.assertEqual(result.stderr, "")
                        else:
                            self.assertIn("host budget arithmetic differs", result.stderr)
                            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
