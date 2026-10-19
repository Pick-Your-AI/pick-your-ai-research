"""Synthetic regressions for the explicit SFF capture-integrity checker.

Every CSV row below is generated test data, never contributor telemetry or
hardware evidence. CI needs no raw captures, downloads, network or GPU. Actual
capture checks require a separate explicit --artifact-dir execution and receipt.
"""
import copy
import csv
from datetime import datetime, timedelta
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_t2_sff_power_record.py"
SPEC = importlib.util.spec_from_file_location("sff_power_integrity", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def synthetic_capture(idle):
    """Two synthetic devices, 90 rows each; constants make expectations explicit."""
    output = io.StringIO(newline="")
    fields = ["timestamp", "index", "name", "uuid", "pci.bus_id", "driver_version",
              "vbios_version", "power.draw [W]", "power.limit [W]", "power.min_limit [W]",
              "power.max_limit [W]", "utilization.gpu [%]", "memory.used [MiB]", "pstate"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    start = datetime(2001, 1, 1) if idle else datetime(2000, 12, 31, 23)
    for sample in range(90):
        for index in range(2):
            power, utilization, memory, pstate = 70, 80, 1000, "P0"
            if idle and index == 0:
                power, utilization, memory, pstate = ((5, 0, 244, "P5") if sample < 86
                                                      else (10, 1, 300, "P0"))
            elif idle:
                power, utilization = (60, 80) if sample < 89 else (4, 0)
            elif index == 0:
                power, utilization = (80, 80) if sample < 71 else (2, 0)
            stamp = start + timedelta(seconds=sample, milliseconds=index)
            writer.writerow({
                "timestamp": stamp.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3],
                "index": str(index), "name": "SYNTHETIC test device",
                "uuid": "REDACTED", "pci.bus_id": "00000000:01:00.0" if index == 0 else "00000000:05:00.0",
                "driver_version": "synthetic-driver", "vbios_version": "synthetic-vbios",
                "power.draw [W]": f"{power:.2f} W", "power.limit [W]": "70.00 W",
                "power.min_limit [W]": "60.00 W", "power.max_limit [W]": "70.00 W",
                "utilization.gpu [%]": f"{utilization} %", "memory.used [MiB]": f"{memory} MiB",
                "pstate": pstate,
            })
    return output.getvalue().encode("utf-8")


class PowerRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-sff-power-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.record_path = self.directory / "synthetic-record.json"
        self.record = json.loads(CHECKER.RECORD.read_text())
        self.record["fixture_kind"] = "generated synthetic input; never research evidence"
        self.record["card"].update(name="SYNTHETIC test device", driver="synthetic-driver", vbios="synthetic-vbios")
        idle = self.record["idle"]
        idle["power_draw_w"] = dict(min=5, mean=5, median=5, max=5)
        idle["excluded_rows"]["rows"] = [dict(utilization_pct=1, memory_used_mib=300,
                                               pstate="P0", power_draw_w=10) for _ in range(4)]
        idle["first_sample_reported_utc"] = "2001-01-01T00:00:00.000Z"
        idle["last_sample_reported_utc"] = "2001-01-01T00:01:25.000Z"
        self.record["reported_observed_utc"] = {
            "idle_window_start": "2001-01-01T00:00:00.000Z",
            "idle_window_end": "2001-01-01T00:01:25.000Z",
            "load_series_first_sample": "2000-12-31T23:00:00.000Z",
            "load_series_last_sample": "2001-01-01T00:01:29.001Z",
        }
        load = self.record["load"]
        load["range_of_series_means_w"].update(low=60, high=80)
        load["max_sample_w"] = 80
        for name, power, above, first, last in (
            ("A_gpu_index_0", 80, 71, "2000-12-31T23:00:00.000Z", "2000-12-31T23:01:29.000Z"),
            ("A_gpu_index_1", 70, 0, "2000-12-31T23:00:00.001Z", "2000-12-31T23:01:29.001Z"),
            ("IDLE_gpu_index_1", 60, 0, "2001-01-01T00:00:00.001Z", "2001-01-01T00:01:29.001Z"),
        ):
            load["series"][name].update(min_w=power, mean_w=power, max_w=power,
                                        samples_above_limit=above,
                                        first_sample_reported_utc=first, last_sample_reported_utc=last)
        for entry in self.record["raw_evidence"]["files"]:
            data = synthetic_capture(entry["path"] == CHECKER.IDLE_NAME)
            (self.directory / entry["path"]).write_bytes(data)
            entry.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                         original_sha256="0" * 64,
                         original_repository_path="synthetic-only/" + entry["path"])
        self.record["raw_evidence"]["preservation"] = "Generated synthetic fixture; no original capture exists."
        self.save()

    def save(self):
        self.record_path.write_text(json.dumps(self.record, indent=2) + "\n")

    def verify(self):
        return CHECKER.verify_record(self.record_path, self.directory)

    def repin_synthetic_bytes(self, name, data):
        (self.directory / name).write_bytes(data)
        entry = next(item for item in self.record["raw_evidence"]["files"] if item["path"] == name)
        entry.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        self.save()

    def test_synthetic_controls_execute_all_ten_original_integrity_groups(self):
        receipt = self.verify()
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(len(receipt["integrity_checks"]), 10)
        self.assertEqual(len(receipt["artifacts"]), 2)
        self.assertIn("arithmetic only", receipt["scope"])
        self.assertEqual(receipt["record_sha256"], hashlib.sha256(self.record_path.read_bytes()).hexdigest())

    def test_missing_capture_fails_before_any_csv_parsing(self):
        (self.directory / CHECKER.LOAD_NAME).unlink()
        with patch.object(CHECKER, "read_rows", side_effect=AssertionError("CSV parser ran")):
            with self.assertRaisesRegex(ValueError, "regular supplied capture file"):
                self.verify()

    def test_hash_mismatch_fails_before_any_csv_parsing(self):
        path = self.directory / CHECKER.LOAD_NAME
        data = path.read_bytes()
        path.write_bytes(data[:-1] + b" ")
        with patch.object(CHECKER, "read_rows", side_effect=AssertionError("CSV parser ran")):
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                self.verify()

    def test_byte_length_mismatch_fails_before_any_csv_parsing(self):
        with (self.directory / CHECKER.IDLE_NAME).open("ab") as handle:
            handle.write(b"extra")
        with patch.object(CHECKER, "read_rows", side_effect=AssertionError("CSV parser ran")):
            with self.assertRaisesRegex(ValueError, "byte length mismatch"):
                self.verify()

    def test_missing_explicit_directory_never_falls_back_to_repository_captures(self):
        with self.assertRaises(OSError):
            CHECKER.verify_record(self.record_path, self.directory / "absent")
        result = subprocess.run([sys.executable, str(SCRIPT), "--record", str(self.record_path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--artifact-dir", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_duplicate_or_escaping_capture_entries_are_rejected(self):
        original = copy.deepcopy(self.record)
        for bad in (self.record["raw_evidence"]["files"][0]["path"], "../capture.csv", "/capture.csv"):
            with self.subTest(path=bad):
                self.record = copy.deepcopy(original)
                self.record["raw_evidence"]["files"][1]["path"] = bad
                self.save()
                with self.assertRaisesRegex(ValueError, "distinct expected basenames"):
                    self.verify()

    def test_symlink_is_not_admitted_as_a_supplied_regular_capture(self):
        path = self.directory / CHECKER.LOAD_NAME
        renamed = path.with_suffix(".saved")
        path.rename(renamed)
        path.symlink_to(renamed)
        with self.assertRaisesRegex(ValueError, "regular supplied capture file"):
            self.verify()

    def test_duplicate_json_keys_and_nonfinite_numbers_are_rejected(self):
        original = self.record_path.read_text()
        for replacement in ('"samples": 87, "samples": 86', '"samples": NaN', '"samples": 1e9999'):
            with self.subTest(replacement=replacement):
                self.record_path.write_text(original.replace('"samples": 86', replacement, 1))
                with self.assertRaisesRegex(ValueError, "duplicate|non-finite|finite numeric"):
                    self.verify()

    def test_all_recorded_clock_boundaries_reject_false_clock_text(self):
        original = copy.deepcopy(self.record)
        paths = [("reported_observed_utc", key) for key in self.record["reported_observed_utc"]]
        paths += [("idle", key) for key in ("first_sample_reported_utc", "last_sample_reported_utc")]
        paths += [("load", "series", name, key) for name in self.record["load"]["series"]
                  for key in ("first_sample_reported_utc", "last_sample_reported_utc")]
        for path in paths:
            with self.subTest(path=path):
                self.record = copy.deepcopy(original)
                target = self.record
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = "1999-01-01T00:00:00.000Z"
                self.save()
                with self.assertRaises(ValueError):
                    self.verify()

    def test_total_used_excluded_and_above_limit_counts_are_checked(self):
        original = copy.deepcopy(self.record)
        paths = [("idle", "samples"), ("idle", "excluded_rows", "count")]
        paths += [("load", "series", name, key) for name in self.record["load"]["series"]
                  for key in ("samples_total", "samples_used", "samples_excluded_below_80pct", "samples_above_limit")]
        for path in paths:
            with self.subTest(path=path):
                self.record = copy.deepcopy(original)
                target = self.record
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] += 1
                self.save()
                with self.assertRaises(ValueError):
                    self.verify()

    def test_count_aliases_cannot_pass_python_boolean_or_decimal_equality(self):
        for value in (False, 0.0):
            with self.subTest(value=value):
                self.record["load"]["series"]["A_gpu_index_1"]["samples_excluded_below_80pct"] = value
                self.save()
                with self.assertRaisesRegex(ValueError, "integer tokens"):
                    self.verify()

    def test_every_excluded_idle_value_is_checked(self):
        original = copy.deepcopy(self.record)
        for row in range(4):
            for key, wrong in (("utilization_pct", 99), ("memory_used_mib", 999),
                               ("power_draw_w", 999), ("pstate", "P9")):
                with self.subTest(row=row, key=key):
                    self.record = copy.deepcopy(original)
                    self.record["idle"]["excluded_rows"]["rows"][row][key] = wrong
                    self.save()
                    with self.assertRaises(ValueError):
                        self.verify()

    def test_wrong_statistics_and_device_or_capture_bindings_are_rejected(self):
        for path, value in ((("idle", "power_draw_w", "mean"), 999),
                            (("load", "series", "A_gpu_index_0", "device", "index"), "1"),
                            (("load", "series", "A_gpu_index_1", "device", "pci_bus_id"), "wrong"),
                            (("load", "series", "IDLE_gpu_index_1", "source_file"), CHECKER.LOAD_NAME)):
            with self.subTest(path=path):
                original = copy.deepcopy(self.record)
                target = self.record
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                self.save()
                with self.assertRaises(ValueError):
                    self.verify()
                self.record = original

    def test_verified_context_or_cross_device_aggregation_is_not_invented(self):
        for section, key in (("context_verification", "utc_timezone_verified"),
                             ("context_verification", "workload_verified"),
                             ("aggregation", "summed_across_devices")):
            with self.subTest(section=section, key=key):
                self.record[section][key] = True
                self.save()
                with self.assertRaises(ValueError):
                    self.verify()
                self.record[section][key] = False

    def test_hash_checked_csv_still_rejects_duplicate_headers_and_short_rows(self):
        original = (self.directory / CHECKER.IDLE_NAME).read_bytes()
        corruptions = [original.replace(b"driver_version", b"index", 1),
                       original.replace(b",synthetic-driver", b"", 1)]
        for data in corruptions:
            with self.subTest(data=data[:100]):
                self.repin_synthetic_bytes(CHECKER.IDLE_NAME, data)
                with self.assertRaisesRegex(ValueError, "headers|column count"):
                    self.verify()

    def test_every_numeric_column_requires_its_actual_unit(self):
        cases = (
            (CHECKER.IDLE_NAME, b"5.00 W", b"5.00 kW"),
            (CHECKER.LOAD_NAME, b"80 %", b"80 bananas"),
            (CHECKER.IDLE_NAME, b"300 MiB", b"300 GiB"),
        )
        originals = {name: (self.directory / name).read_bytes() for name in (CHECKER.IDLE_NAME, CHECKER.LOAD_NAME)}
        for name, original, wrong in cases:
            with self.subTest(name=name, wrong=wrong):
                for restore_name, data in originals.items():
                    self.repin_synthetic_bytes(restore_name, data)
                self.repin_synthetic_bytes(name, originals[name].replace(original, wrong, 1))
                with self.assertRaisesRegex(ValueError, "exact .* unit"):
                    self.verify()

    def test_displayed_idle_summary_matches_the_selected_rows(self):
        original = copy.deepcopy(self.record)
        for key, value in (("pstate", "P0"), ("utilization_pct", 99),
                           ("memory_used_mib", 999), ("utilization_pct", False)):
            with self.subTest(key=key, value=value):
                self.record = copy.deepcopy(original)
                self.record["idle"][key] = value
                self.save()
                with self.assertRaises(ValueError):
                    self.verify()

    def test_limit_records_cannot_round_into_matching_display_values(self):
        original = copy.deepcopy(self.record)
        for field, value in (("power_min_limit_w", 60.004), ("power_max_limit_w", 70.004)):
            with self.subTest(field=field):
                self.record = copy.deepcopy(original)
                self.record["card"][field] = value
                self.save()
                with self.assertRaises(ValueError):
                    self.verify()

    def test_explicit_cli_returns_only_input_bound_integrity_result(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--record", str(self.record_path),
                                 "--artifact-dir", str(self.directory)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(len(receipt["integrity_checks"]), 10)
        self.assertIn("No acquisition", receipt["limits"])


if __name__ == "__main__":
    unittest.main()
