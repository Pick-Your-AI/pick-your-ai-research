"""Offline regressions for the per-device power record and its artifact checker.

No test here reads the real capture files; they are not stored in this
repository. The recompute logic lives in scripts/check_t2_sff_power_artifacts.py
and these tests run that same code against a clearly synthetic fixture and
corrupted controls. A pass here does not recompute the real captures: that needs
the checker run with --artifact-dir on the supplied files, and its own result
file. The checks never verify acquisition, workload, timezone, the original
unredacted captures or calibrated physical power.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research/T2-infrastructure/measurements/rtx-pro-4000-blackwell-sff-power-2026-10-19.json"
FIXTURES = ROOT / "tests/fixtures/synthetic-sff-power"
SPEC = importlib.util.spec_from_file_location(
    "check_t2_sff_power_artifacts", ROOT / "scripts/check_t2_sff_power_artifacts.py")
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)
SYNTHETIC_FILES = ("synthetic-capture-A.csv", "synthetic-capture-IDLE.csv")
SYNTHETIC_RECORD = FIXTURES / "synthetic-record.json"
A_NAME = "raw-capture-A-20261018T235741Z.csv"
IDLE_NAME = "raw-capture-IDLE-20261019T000959Z.csv"


def synthetic_pins(contents):
    return {n: {"sha256": CHECKER.sha256_hex(d), "bytes": len(d)} for n, d in contents.items()}


def failing(record, captures):
    return {c["check"] for c in CHECKER.check_record(record, captures).failed()}


class SyntheticBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(SYNTHETIC_RECORD.read_text())
        cls.captures = {n: (FIXTURES / n).read_bytes() for n in SYNTHETIC_FILES}

    def mutated_record(self):
        return deepcopy(self.record)

    def mutated_captures(self, name, old, new, count=1):
        data = dict(self.captures)
        text = data[name].decode()
        self.assertGreaterEqual(text.count(old), 1, "mutation target missing: " + old)
        data[name] = text.replace(old, new, count).encode()
        return data


class SyntheticRecompute(SyntheticBase):
    """The same checker logic, run on invented values (1.00 W, 2.00 W ...)."""

    def test_fixture_is_clearly_synthetic(self):
        self.assertIn("synthetic", self.record["synthetic"].lower())
        self.assertEqual(self.record["card"]["name"], "SYNTHETIC TEST DEVICE")
        for name, data in self.captures.items():
            self.assertTrue(name.startswith("synthetic-"))
            self.assertNotIn(b"GPU-", data)
            self.assertNotIn(b"NVIDIA", data)
            self.assertLess(len(data), 4000)

    def test_synthetic_record_passes_every_check(self):
        result = CHECKER.check_record(self.record, self.captures)
        self.assertEqual(result.failed(), [])
        self.assertGreaterEqual(len(result.checks), 60)

    def test_idle_statistics_recompute_from_csv(self):
        res = CHECKER.check_record(self.record, self.captures)
        self.assertEqual(res.values["idle.samples"], 3)
        self.assertAlmostEqual(res.values["idle.power_min"], 1.0)
        self.assertAlmostEqual(res.values["idle.power_mean"], 2.0)
        self.assertAlmostEqual(res.values["idle.power_median"], 2.0)
        self.assertAlmostEqual(res.values["idle.power_max"], 3.0)

    def test_idle_filter_and_excluded_rows_match_telemetry(self):
        res = CHECKER.check_record(self.record, self.captures)
        self.assertEqual(res.values["idle.excluded_count"], 2)
        self.assertEqual(res.values["idle.excluded_rows"], self.record["idle"]["excluded_rows"]["rows"])
        self.assertEqual(res.values["idle.predicate_pstate"], ["P5"])

    def test_load_series_recompute_from_csv(self):
        res = CHECKER.check_record(self.record, self.captures)
        for name, rec in self.record["load"]["series"].items():
            self.assertEqual(res.values["series.%s.total" % name], rec["samples_total"])
            self.assertEqual(res.values["series.%s.samples_used" % name], rec["samples_used"])
            self.assertEqual(res.values["series.%s.above_limit" % name], rec["samples_above_limit"])
            self.assertAlmostEqual(res.values["series.%s.mean" % name], rec["mean_w"])
        self.assertAlmostEqual(res.values["load.range_low"], 3.0)
        self.assertAlmostEqual(res.values["load.range_high"], 8.0)
        self.assertAlmostEqual(res.values["load.max_sample"], 10.0)

    def test_limits_and_identity_match_csv(self):
        res = CHECKER.check_record(self.record, self.captures)
        names = [c["check"] for c in res.checks if c["check"].startswith("limits_identity.")]
        self.assertEqual(len(names), 6)
        self.assertEqual(failing(self.record, self.captures), set())

    def test_published_csvs_carry_no_gpu_uuid(self):
        for name in SYNTHETIC_FILES:
            self.assertNotIn("GPU-", self.captures[name].decode())
        bad = self.mutated_captures("synthetic-capture-A.csv", "REDACTED",
                                    "GPU-SYNTHETIC-ID")
        failed = failing(self.record, bad)
        self.assertIn("synthetic-capture-A.csv.no_gpu_uuid_string", failed)
        self.assertIn("synthetic-capture-A.csv.uuid_column_redacted", failed)


class CorruptedControls(SyntheticBase):
    """Each corruption of one field class must trip its own assertion."""

    def test_wrong_boundary_text_idle(self):
        record = self.mutated_record()
        record["idle"]["first_sample_reported_utc"] = "2000-01-01T00:00:01.001Z"
        self.assertEqual(failing(record, self.captures), {"idle.boundary_first"})

    def test_wrong_boundary_text_series_and_windows(self):
        record = self.mutated_record()
        record["load"]["series"]["SYN_A_index_1"]["last_sample_reported_utc"] = "2000-01-01T00:10:03.000Z"
        record["reported_observed_utc"]["load_series_last_sample"] = "2000-01-01T00:10:03.000Z"
        record["reported_observed_utc"]["idle_window_end"] = "2000-01-01T00:00:04.000Z"
        failed = failing(record, self.captures)
        for name in ("series.SYN_A_index_1.boundary_last", "window.load_series_last_sample",
                     "window.idle_window_end"):
            self.assertIn(name, failed)

    def test_series_boundary_is_the_full_capture_not_the_last_qualifying_row(self):
        # SYN_A_index_0 ends with a below-80-percent row at 00:10:03.000. The
        # last QUALIFYING row is 00:10:02.000; recording that must fail.
        record = self.mutated_record()
        self.assertEqual(record["load"]["series"]["SYN_A_index_0"]["last_sample_reported_utc"],
                         "2000-01-01T00:10:03.000Z")
        record["load"]["series"]["SYN_A_index_0"]["last_sample_reported_utc"] = "2000-01-01T00:10:02.000Z"
        self.assertEqual(failing(record, self.captures), {"series.SYN_A_index_0.boundary_last"})

    def test_wrong_total(self):
        record = self.mutated_record()
        record["load"]["series"]["SYN_IDLE_index_1"]["samples_total"] = 5
        self.assertEqual(failing(record, self.captures), {"series.SYN_IDLE_index_1.total"})

    def test_wrong_selected_count(self):
        record = self.mutated_record()
        record["idle"]["samples"] = 4
        record["load"]["series"]["SYN_A_index_0"]["samples_used"] = 3
        failed = failing(record, self.captures)
        self.assertIn("idle.samples", failed)
        self.assertIn("series.SYN_A_index_0.samples_used", failed)

    def test_negative_excluded_count(self):
        record = self.mutated_record()
        record["idle"]["excluded_rows"]["count"] = -1
        record["load"]["series"]["SYN_A_index_0"]["samples_excluded_below_80pct"] = -1
        failed = failing(record, self.captures)
        for name in ("idle.excluded_count", "idle.excluded_rows_listed", "series.SYN_A_index_0.excluded_count"):
            self.assertIn(name, failed)

    def test_invented_excluded_power(self):
        record = self.mutated_record()
        record["idle"]["excluded_rows"]["rows"][0]["power_draw_w"] = 4.5
        self.assertEqual(failing(record, self.captures), {"idle.excluded_rows"})

    def test_invented_extra_excluded_row(self):
        record = self.mutated_record()
        record["idle"]["excluded_rows"]["rows"].append(
            {"utilization_pct": 0.0, "memory_used_mib": 1.0, "pstate": "P0", "power_draw_w": 1.0})
        record["idle"]["excluded_rows"]["count"] = 3
        failed = failing(record, self.captures)
        self.assertIn("idle.excluded_count", failed)
        self.assertIn("idle.excluded_rows", failed)

    def test_wrong_statistic_beyond_tolerance_only(self):
        record = self.mutated_record()
        record["idle"]["power_draw_w"]["mean"] = 2.02
        self.assertEqual(failing(record, self.captures), {"idle.power_mean"})
        record["idle"]["power_draw_w"]["mean"] = 2.005  # inside 0.01 W: still passes
        self.assertEqual(failing(record, self.captures), set())

    def test_wrong_above_limit_count(self):
        record = self.mutated_record()
        record["load"]["series"]["SYN_A_index_1"]["samples_above_limit"] = 2
        self.assertEqual(failing(record, self.captures), {"series.SYN_A_index_1.above_limit"})

    def test_series_identity_wrong_pci_in_record(self):
        record = self.mutated_record()
        record["load"]["series"]["SYN_A_index_1"]["device"]["pci_bus_id"] = "FAKE:00.0"
        self.assertIn("series.SYN_A_index_1.device_pci", failing(record, self.captures))

    def test_series_identity_wrong_index_in_record(self):
        record = self.mutated_record()
        record["load"]["series"]["SYN_A_index_1"]["device"]["index"] = "0"
        self.assertIn("series.SYN_A_index_1.device_pci", failing(record, self.captures))

    def test_series_identity_pci_changed_inside_capture(self):
        data = self.mutated_captures("synthetic-capture-A.csv", "FAKE:01.0", "FAKE:09.0", count=1)
        self.assertIn("synthetic-capture-A.csv.device_identities", failing(self.record, data))

    def test_idle_device_pci_wrong(self):
        record = self.mutated_record()
        record["idle"]["device"]["pci_bus_id"] = "FAKE:01.0"
        self.assertIn("idle.device_pci", failing(record, self.captures))

    def test_wrong_limit_or_identity(self):
        record = self.mutated_record()
        record["card"]["power_limit_w"] = 6.0
        record["card"]["driver"] = "9.9.9"
        failed = failing(record, self.captures)
        self.assertIn("limits_identity.power_limit", failed)
        self.assertIn("limits_identity.driver", failed)

    def test_idle_capture_with_no_row_meeting_the_predicate_fails_that_check(self):
        # Every device-0 row is made P0, so the leading low-activity run is empty.
        data = self.mutated_captures(
            "synthetic-capture-IDLE.csv", "100 MiB, P5", "100 MiB, P0", count=3)
        result = CHECKER.check_record(self.record, data)
        failed = {c["check"]: c["detail"] for c in result.failed()}
        self.assertEqual(set(failed), {"idle.nonempty_run"})
        self.assertIn("no rows satisfy", failed["idle.nonempty_run"])

    def test_boolean_is_not_accepted_as_an_integer_count(self):
        # samples_excluded_below_80pct is 1 in the fixture; True == 1 in Python.
        record = self.mutated_record()
        series = record["load"]["series"]["SYN_A_index_0"]
        self.assertEqual(series["samples_excluded_below_80pct"], 1)
        series["samples_excluded_below_80pct"] = True
        self.assertEqual(failing(record, self.captures), {"series.SYN_A_index_0.excluded_count"})

    def test_boolean_is_not_accepted_inside_an_excluded_row(self):
        # utilization_pct is 1.0 in the fixture; True == 1.0 in Python.
        record = self.mutated_record()
        row = record["idle"]["excluded_rows"]["rows"][0]
        self.assertEqual(row["utilization_pct"], 1.0)
        row["utilization_pct"] = True
        self.assertEqual(failing(record, self.captures), {"idle.excluded_rows"})

    def test_string_is_not_accepted_as_a_number(self):
        record = self.mutated_record()
        record["load"]["series"]["SYN_A_index_0"]["samples_excluded_below_80pct"] = "1"
        record["idle"]["samples"] = "3"
        self.assertEqual(failing(record, self.captures),
                         {"series.SYN_A_index_0.excluded_count", "idle.samples"})

    def test_boolean_is_not_accepted_by_the_tolerance_comparison(self):
        record = self.mutated_record()
        record["idle"]["power_draw_w"]["min"] = True   # recomputed min is 1.0
        self.assertEqual(failing(record, self.captures), {"idle.power_min"})

    def test_whole_number_float_and_int_still_match(self):
        record = self.mutated_record()
        record["load"]["series"]["SYN_A_index_0"]["samples_excluded_below_80pct"] = 1.0
        record["idle"]["excluded_rows"]["rows"][0]["utilization_pct"] = 1
        self.assertEqual(failing(record, self.captures), set())

    def test_malformed_record_fails_a_check_instead_of_crashing(self):
        record = self.mutated_record()
        record["idle"]["first_sample_reported_utc"] = "not a time"
        self.assertIn("idle.boundary_first", failing(record, self.captures))


def set_record(path, change):
    """Corruption of one record value: path is a tuple of keys / list indexes."""
    def mutate(record, captures):
        node = record
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = change(node[path[-1]])
        return record, captures
    return mutate


def edit_capture(name, old, new, count=1):
    """Corruption of one synthetic capture: replace text in that file only."""
    def mutate(record, captures):
        text = captures[name].decode()
        if old not in text:
            raise AssertionError("corruption target %r not in %s" % (old, name))
        captures[name] = text.replace(old, new, count).encode()
        return record, captures
    return mutate


def edit_cell(name, column, new, data_row=1):
    """Replace one cell (by header name) of one data row of a synthetic capture."""
    def mutate(record, captures):
        lines = captures[name].decode().split("\n")
        header = [c.strip() for c in lines[0].split(",")]
        cells = lines[data_row].split(",")
        cells[header.index(column)] = " " + new
        lines[data_row] = ",".join(cells)
        captures[name] = "\n".join(lines).encode()
        return record, captures
    return mutate


def extra_cell(name):
    """Append an unheaded cell to one data row."""
    def mutate(record, captures):
        lines = captures[name].decode().split("\n")
        lines[1] += ", 1"
        captures[name] = "\n".join(lines).encode()
        return record, captures
    return mutate


def duplicate_header(name):
    """Give the second power.draw column's slot the name of the first (same width)."""
    def mutate(record, captures):
        text = captures[name].decode()
        captures[name] = text.replace("power.limit [W]", "power.draw [W]", 1).encode()
        return record, captures
    return mutate


def drop_first(rows):
    return rows[1:]


def plus_one(value):
    return value + 1


def other_clock(_value):
    return "2001-01-01T00:00:00.000Z"


A_FILE, IDLE_FILE = SYNTHETIC_FILES[0], SYNTHETIC_FILES[1]
SERIES = ("SYN_A_index_0", "SYN_A_index_1", "SYN_IDLE_index_1")

CORRUPTING_CASES = {
    A_FILE + ".no_gpu_uuid_string": edit_capture(A_FILE, "REDACTED", "GPU-SYNTHETIC-ID"),
    IDLE_FILE + ".no_gpu_uuid_string": edit_capture(IDLE_FILE, "REDACTED", "GPU-SYNTHETIC-ID"),
    A_FILE + ".uuid_column_redacted": edit_capture(A_FILE, "REDACTED", "NOT-REDACTED"),
    IDLE_FILE + ".uuid_column_redacted": edit_capture(IDLE_FILE, "REDACTED", "NOT-REDACTED"),
    A_FILE + ".csv_shape": extra_cell(A_FILE),
    IDLE_FILE + ".csv_shape": duplicate_header(IDLE_FILE),
    A_FILE + ".cell_units": edit_cell(A_FILE, "power.draw [W]", "2.00 kW"),
    IDLE_FILE + ".cell_units": edit_cell(IDLE_FILE, "memory.used [MiB]", "10 GiB"),
    A_FILE + ".device_identities": edit_capture(A_FILE, "FAKE:01.0", "FAKE:09.0"),
    IDLE_FILE + ".device_identities": edit_capture(IDLE_FILE, "FAKE:01.0", "FAKE:09.0"),
    "limits_identity.power_limit": set_record(("card", "power_limit_w"), plus_one),
    "limits_identity.power_min_limit": set_record(("card", "power_min_limit_w"), plus_one),
    "limits_identity.power_max_limit": set_record(("card", "power_max_limit_w"), plus_one),
    "limits_identity.driver": set_record(("card", "driver"), lambda v: v + "x"),
    "limits_identity.vbios": set_record(("card", "vbios"), lambda v: v + "x"),
    "limits_identity.name": set_record(("card", "name"), lambda v: v + "x"),
    # Same-state IDLE capture in which no device-0 row meets the idle predicate.
    "idle.nonempty_run": edit_capture(IDLE_FILE, "100 MiB, P5", "100 MiB, P0", count=3),
    "idle.device_pci": set_record(("idle", "device", "pci_bus_id"), lambda v: "FAKE:77.0"),
    "idle.samples": set_record(("idle", "samples"), plus_one),
    "idle.power_min": set_record(("idle", "power_draw_w", "min"), plus_one),
    "idle.power_mean": set_record(("idle", "power_draw_w", "mean"), plus_one),
    "idle.power_median": set_record(("idle", "power_draw_w", "median"), plus_one),
    "idle.power_max": set_record(("idle", "power_draw_w", "max"), plus_one),
    "idle.boundary_first": set_record(("idle", "first_sample_reported_utc"), other_clock),
    "idle.boundary_last": set_record(("idle", "last_sample_reported_utc"), other_clock),
    "window.idle_window_start": set_record(("reported_observed_utc", "idle_window_start"), other_clock),
    "window.idle_window_end": set_record(("reported_observed_utc", "idle_window_end"), other_clock),
    "window.load_series_first_sample": set_record(("reported_observed_utc", "load_series_first_sample"), other_clock),
    "window.load_series_last_sample": set_record(("reported_observed_utc", "load_series_last_sample"), other_clock),
    "idle.excluded_count": set_record(("idle", "excluded_rows", "count"), plus_one),
    "idle.excluded_rows_listed": set_record(("idle", "excluded_rows", "rows"), drop_first),
    "idle.excluded_rows": set_record(("idle", "excluded_rows", "rows", 0, "power_draw_w"), plus_one),
    "load.range_low": set_record(("load", "range_of_series_means_w", "low"), plus_one),
    "load.range_high": set_record(("load", "range_of_series_means_w", "high"), plus_one),
    "load.max_sample": set_record(("load", "max_sample_w"), plus_one),
}
for _name in SERIES:
    for _check, _path, _change in (
            ("device_pci", ("device", "pci_bus_id"), lambda v: "FAKE:77.0"),
            ("total", ("samples_total",), plus_one),
            ("excluded_count", ("samples_excluded_below_80pct",), plus_one),
            ("samples_used", ("samples_used",), plus_one),
            ("boundary_first", ("first_sample_reported_utc",), other_clock),
            ("boundary_last", ("last_sample_reported_utc",), other_clock),
            ("min", ("min_w",), plus_one),
            ("mean", ("mean_w",), plus_one),
            ("max", ("max_w",), plus_one),
            ("above_limit", ("samples_above_limit",), plus_one)):
        CORRUPTING_CASES["series.%s.%s" % (_name, _check)] = set_record(("load", "series", _name) + _path, _change)

# Checks that cannot fail independently of the selection they verify.
EXEMPT = {
    "idle.predicate_pstate": "the run is selected by this very pstate, so every selected row matches by construction",
    "idle.predicate_memory": "the run is selected by this very memory value, so every selected row matches by construction",
    "idle.predicate_utilization": "the run is selected by this very utilization value, so every selected row matches by construction",
}


class EveryCheckHasACorruptingCase(SyntheticBase):
    """Each check the checker emits must be able to fail, on its own name."""

    def emitted(self):
        return [c["check"] for c in CHECKER.check_record(self.record, self.captures).checks]

    def test_every_emitted_check_has_a_corrupting_case_or_an_exemption(self):
        for name in self.emitted():
            with self.subTest(check=name):
                self.assertTrue(name in CORRUPTING_CASES or name in EXEMPT,
                                "check %s has no corrupting case" % name)

    def test_every_exempt_check_is_emitted_and_has_a_reason(self):
        emitted = set(self.emitted())
        for name, reason in EXEMPT.items():
            with self.subTest(exempt=name):
                self.assertIn(name, emitted, "exempt check is not in the checker output")
                self.assertTrue(reason.strip())
                self.assertNotIn(name, CORRUPTING_CASES, "exempt check also has a case")

    def test_every_corrupting_case_names_an_emitted_check(self):
        emitted = set(self.emitted())
        for name in CORRUPTING_CASES:
            with self.subTest(case=name):
                self.assertIn(name, emitted, "case for a check the checker no longer emits")

    def test_each_corruption_fails_its_own_check(self):
        for name in self.emitted():
            if name not in CORRUPTING_CASES:
                continue
            with self.subTest(check=name):
                record, captures = deepcopy(self.record), dict(self.captures)
                record, captures = CORRUPTING_CASES[name](record, captures)
                self.assertTrue(record != self.record or captures != self.captures,
                                "corruption changed nothing")
                self.assertIn(name, failing(record, captures))

    def test_uncorrupted_fixture_fails_nothing(self):
        self.assertEqual(failing(self.record, self.captures), set())


class ExactCountsAndShape(SyntheticBase):
    """Slice 7: exact above-limit count, exact recorded counts, strict CSV shape."""

    def run_texts(self, record_text=None, captures=None):
        captures = captures or self.captures
        with tempfile.TemporaryDirectory() as tmp:
            for name, data in captures.items():
                (Path(tmp) / name).write_bytes(data)
            record = Path(tmp) / "record.json"
            record.write_text(record_text if record_text is not None else SYNTHETIC_RECORD.read_text())
            result = CHECKER.run(tmp, record, pins=synthetic_pins(captures))
        return {c["check"] for c in result["checks"] if not c["passed"]}

    # --- G: above_limit is counted on exact decimals --------------------
    def limit_captures(self, draws):
        """Series SYN_A_index_1 with limit 5.20 W and the given selected draws."""
        text = self.captures[A_FILE].decode()
        lines = text.split("\n")
        header = [c.strip() for c in lines[0].split(",")]
        k = 0
        for n, line in enumerate(lines[1:], 1):
            cells = line.split(",")
            if len(cells) == len(header):
                cells[header.index("power.limit [W]")] = " 5.20 W"
                if cells[1].strip() == "1" and k < len(draws):
                    cells[header.index("power.draw [W]")] = " " + draws[k] + " W"; k += 1
                lines[n] = ",".join(cells)
        captures = dict(self.captures); captures[A_FILE] = "\n".join(lines).encode()
        return captures

    def limit_record(self, count, limit="5.20"):
        record = SYNTHETIC_RECORD.read_text().replace('"power_limit_w": 5.0', '"power_limit_w": %s' % limit, 1)
        data = json.loads(record)
        want = data["load"]["series"]["SYN_A_index_1"]["samples_above_limit"]
        key = '"SYN_A_index_1": {'
        i = record.index(key); j = record.index('"samples_above_limit": %d' % want, i)
        return record[:j] + '"samples_above_limit": %s' % count + record[j + len('"samples_above_limit": %d' % want):]

    def failed_ignoring_stats(self, text, captures):
        return {f for f in self.run_texts(text, captures)
                if f.endswith("SYN_A_index_1.above_limit")}

    def test_strict_count_is_two_not_one(self):
        draws = ["3.00", "5.200000000000000001", "7.00"]
        captures = self.limit_captures(draws)
        self.assertEqual(self.failed_ignoring_stats(self.limit_record(2), captures), set())
        self.assertEqual(self.failed_ignoring_stats(self.limit_record(1), captures), {"series.SYN_A_index_1.above_limit"})

    def test_at_limit_and_just_below_are_not_counted(self):
        for draws in (["3.00", "5.20", "7.00"], ["3.00", "5.199999999999999999", "7.00"]):
            with self.subTest(draws=draws):
                captures = self.limit_captures(draws)
                self.assertEqual(self.failed_ignoring_stats(self.limit_record(1), captures), set())
                self.assertEqual(self.failed_ignoring_stats(self.limit_record(2), captures), {"series.SYN_A_index_1.above_limit"})

    def test_non_number_limit_fails_the_count_cleanly(self):
        record = self.mutated_record()
        record["card"]["power_limit_w"] = True
        self.assertIn("series.SYN_A_index_1.above_limit", failing(record, self.captures))

    # --- H: recorded counts keep their exact written value ---------------
    def count_text(self, key, written):
        text = SYNTHETIC_RECORD.read_text()
        needle = '"%s": ' % key
        i = text.index(needle)
        j = i + len(needle)
        end = j
        while text[end] in "0123456789.": end += 1
        return text[:j] + written + text[end:]

    def test_non_integral_counts_beyond_binary64_fail_end_to_end(self):
        # Each written value is the TRUE count plus 1e-18: binary64 rounds it back
        # to the true count, so a float comparison accepts it.
        for written in ("3.000000000000000001", "2.999999999999999999"):
            self.assertEqual(float(written), 3.0)
        cases = (("samples_total", "3.000000000000000001", "series.SYN_A_index_0.total"),
                 ("samples_used", "2.000000000000000001", "series.SYN_A_index_0.samples_used"),
                 ("samples_excluded_below_80pct", "1.000000000000000001", "series.SYN_A_index_0.excluded_count"),
                 ("samples", "3.000000000000000001", "idle.samples"),
                 ("count", "2.000000000000000001", "idle.excluded_count"))
        for key, written, check in cases:
            with self.subTest(key=key):
                text = self.count_text(key, written)
                self.assertNotEqual(text, SYNTHETIC_RECORD.read_text())
                self.assertIn(check, self.run_texts(text))
        with self.subTest(key="samples_above_limit"):
            # series SYN_A_index_1 has the true count 1
            text = self.limit_record("1.000000000000000001", limit="5.0")
            self.assertIn("series.SYN_A_index_1.above_limit", self.run_texts(text))

    def test_float_and_int_spellings_of_the_same_count_stay_equal(self):
        for written in ("3", "3.0", "3.00"):
            with self.subTest(written=written):
                self.assertEqual(self.run_texts(self.count_text("samples_total", written)), set())

    def test_boolean_and_string_counts_fail(self):
        for bad in (True, "3"):
            with self.subTest(bad=bad):
                record = self.mutated_record()
                record["load"]["series"]["SYN_A_index_0"]["samples_total"] = bad
                self.assertIn("series.SYN_A_index_0.total", failing(record, self.captures))

    def test_count_value_unit(self):
        D = CHECKER.Decimal
        self.assertEqual([CHECKER.count_value(v) for v in (2, 2.0, D("2"), D("2.0"))], [2, 2, 2, 2])
        for bad in (True, False, 2.5, D("2.000000000000000001"), float("nan"), float("inf"), "2", None, D("NaN")):
            with self.subTest(bad=bad):
                self.assertIsNone(CHECKER.count_value(bad))

    # --- I: CSV shape before the lossy zip -------------------------------
    def test_extra_unheaded_cell_fails_the_run(self):
        captures = dict(self.captures); text = captures[A_FILE].decode().split("\n")
        text[2] += ", 99"; captures[A_FILE] = "\n".join(text).encode()
        self.assertEqual(failing(self.record, captures), {A_FILE + ".csv_shape"})
        self.assertIn(A_FILE + ".csv_shape", self.run_texts(None, captures))

    def test_duplicate_header_fails_the_run(self):
        captures = dict(self.captures)
        captures[A_FILE] = captures[A_FILE].decode().replace("power.limit [W]", "power.draw [W]", 1).encode()
        self.assertEqual(failing(self.record, captures), {A_FILE + ".csv_shape"})
        self.assertIn(A_FILE + ".csv_shape", self.run_texts(None, captures))

    def test_short_and_empty_rows_fail_without_a_crash(self):
        lines = self.captures[A_FILE].decode().split("\n")
        for label, row in (("short", ",".join(lines[1].split(",")[:5])), ("blank-cells", ",,,")):
            with self.subTest(case=label):
                mutated = list(lines); mutated[1] = row
                captures = dict(self.captures); captures[A_FILE] = "\n".join(mutated).encode()
                self.assertEqual(failing(self.record, captures), {A_FILE + ".csv_shape"})

    def test_shape_failure_stops_before_any_value_is_used(self):
        captures = dict(self.captures); text = captures[A_FILE].decode().split("\n")
        text[1] += ", 1"; captures[A_FILE] = "\n".join(text).encode()
        result = CHECKER.check_record(self.record, captures)
        self.assertEqual({c["check"] for c in result.checks}, {A_FILE + ".csv_shape", IDLE_FILE + ".csv_shape"})

    def test_clean_fixture_has_no_shape_problem(self):
        for name in SYNTHETIC_FILES:
            self.assertEqual(CHECKER.shape_violations(self.captures[name]), [])


class ExactNumbers(SyntheticBase):
    """Recorded numbers are compared exactly: no bool-as-0, no truncation, no binary64."""

    def run_record_text(self, text, captures=None):
        captures = captures or self.captures
        pins = synthetic_pins(captures)
        with tempfile.TemporaryDirectory() as tmp:
            for name, data in captures.items():
                (Path(tmp) / name).write_bytes(data)
            record = Path(tmp) / "record.json"
            record.write_text(text)
            result = CHECKER.run(tmp, record, pins=pins)
        return {c["check"] for c in result["checks"] if not c["passed"]}

    def test_boolean_idle_utilization_is_not_zero(self):
        for bad in (False, True):
            with self.subTest(bad=bad):
                record = self.mutated_record()
                record["idle"]["utilization_pct"] = bad
                self.assertEqual(failing(record, self.captures), {"idle.nonempty_run"})

    def test_boolean_idle_memory_is_not_a_number(self):
        record = self.mutated_record()
        record["idle"]["memory_used_mib"] = True
        self.assertEqual(failing(record, self.captures), {"idle.nonempty_run"})

    def test_fractional_idle_memory_is_not_truncated(self):
        for bad in (10.5, 10.9, 10.0001):
            with self.subTest(bad=bad):
                record = self.mutated_record()
                record["idle"]["memory_used_mib"] = bad
                self.assertEqual(failing(record, self.captures), {"idle.nonempty_run"})

    def test_fractional_idle_utilization_is_not_truncated(self):
        record = self.mutated_record()
        record["idle"]["utilization_pct"] = 0.5
        self.assertEqual(failing(record, self.captures), {"idle.nonempty_run"})

    def test_whole_number_predicates_still_pass_as_int_or_float(self):
        record = self.mutated_record()
        record["idle"]["memory_used_mib"] = 10.0
        record["idle"]["utilization_pct"] = 0.0
        self.assertEqual(failing(record, self.captures), set())

    def test_limit_beyond_binary64_is_seen_through_the_cli_path(self):
        text = SYNTHETIC_RECORD.read_text()
        self.assertEqual(float("5.0000000000000001"), 5.0)  # float cannot tell
        for key in ("power_limit_w", "power_min_limit_w", "power_max_limit_w"):
            with self.subTest(key=key):
                value = {"power_limit_w": "5.0", "power_min_limit_w": "1.0", "power_max_limit_w": "9.0"}[key]
                needle = '"%s": %s' % (key, value)
                self.assertEqual(text.count(needle), 1, needle)
                bad = text.replace(needle, '"%s": %s0000000000000001' % (key, value))
                self.assertEqual(self.run_record_text(bad), {"limits_identity." + key.replace("_w", "").replace("power_limit", "power_limit")})

    def test_same_value_written_differently_is_equal(self):
        text = SYNTHETIC_RECORD.read_text().replace('"power_limit_w": 5.0', '"power_limit_w": 5.00', 1)
        self.assertEqual(self.run_record_text(text), set())

    def test_high_precision_csv_value_is_compared_exactly(self):
        captures = dict(self.captures)
        for name in SYNTHETIC_FILES:
            captures[name] = captures[name].decode().replace("5.00 W, 1.00 W", "5.0000000000000001 W, 1.00 W").encode()
        self.assertEqual(self.run_record_text(SYNTHETIC_RECORD.read_text(), captures),
                         {"limits_identity.power_limit"})

    def test_bad_unit_in_a_row_later_excluded_by_selection_fails_cell_units(self):
        # The idle run ends before these rows; their units are still checked.
        excluded = self.captures[IDLE_FILE].decode()
        self.assertIn(", 1 %, 20 MiB,", excluded)
        for old, new in ((", 1 %, 20 MiB,", ", 1 bananas, 20 MiB,"), (", 1 %, 20 MiB,", ", 1 %, 20 GiB,"),
                         (", 4.00 W, 5.00 W,", ", 4.00 kW, 5.00 W,")):
            with self.subTest(change=new):
                captures = self.mutated_captures(IDLE_FILE, old, new)
                self.assertEqual(failing(self.record, captures), {IDLE_FILE + ".cell_units"})


class UnitsAreEnforced(SyntheticBase):
    """Every numeric cell carries exactly the unit its header declares."""

    UNIT_COLUMNS = {
        "power.draw [W]": ("W", "2.00 kW"), "power.limit [W]": ("W", "5.00 kW"),
        "power.min_limit [W]": ("W", "1.00 mW"), "power.max_limit [W]": ("W", "9.00 kW"),
        "utilization.gpu [%]": ("%", "100 bananas"), "memory.used [MiB]": ("MiB", "10 GiB"),
        "memory.total [MiB]": ("MiB", "100 GiB"), "clocks.current.sm [MHz]": ("MHz", "1 GHz"),
        "clocks.current.memory [MHz]": ("MHz", "1 GHz"),
    }

    def run_with(self, name, mutation):
        record, captures = mutation(deepcopy(self.record), dict(self.captures))
        return failing(record, captures)

    def test_unit_column_list_matches_the_header(self):
        header = self.captures[A_FILE].decode().split("\n")[0].split(",")
        declared = {c.strip() for c in header if CHECKER.column_unit(c.strip())}
        self.assertEqual(declared, set(self.UNIT_COLUMNS))
        self.assertEqual(declared, set(CHECKER.UNIT_COLUMNS))
        for column, (unit, _bad) in self.UNIT_COLUMNS.items():
            self.assertEqual(CHECKER.UNIT_COLUMNS[column], unit)

    def test_wrong_unit_in_every_unit_column_fails_the_run(self):
        for name in SYNTHETIC_FILES:
            for column, (_unit, bad) in self.UNIT_COLUMNS.items():
                with self.subTest(file=name, column=column):
                    self.assertEqual(self.run_with(name, edit_cell(name, column, bad)), {name + ".cell_units"})

    def test_missing_unit_extra_text_and_bad_spacing_fail(self):
        for label, bad in (("missing unit", "2.00"), ("extra text", "2.00 W extra"),
                           ("lowercase", "2.00 w"), ("two spaces", "2.00  W"),
                           ("empty", ""), ("not a number", "abc W"), ("nan", "nan W")):
            with self.subTest(case=label):
                self.assertEqual(self.run_with(A_FILE, edit_cell(A_FILE, "power.draw [W]", bad)),
                                 {A_FILE + ".cell_units"})

    def test_reported_cases_each_fail(self):
        # idle draw 1.00 W -> 1.00 kW; load utilization 100 % -> 100 bananas;
        # excluded idle memory 20 MiB -> 20 GiB. All three used to pass.
        self.assertEqual(self.run_with(IDLE_FILE, edit_capture(IDLE_FILE, "1.00 W", "1.00 kW")), {IDLE_FILE + ".cell_units"})
        self.assertEqual(self.run_with(A_FILE, edit_capture(A_FILE, "100 %", "100 bananas")), {A_FILE + ".cell_units"})
        self.assertEqual(self.run_with(IDLE_FILE, edit_capture(IDLE_FILE, "20 MiB", "20 GiB")), {IDLE_FILE + ".cell_units"})

    def test_unit_check_runs_before_values_are_used(self):
        # A cell that cannot be read as a number must fail a check, not crash.
        result = CHECKER.check_record(self.record, self.mutated_captures(
            A_FILE, "2.00 W", "garbage"))
        self.assertEqual({c["check"] for c in result.failed()}, {A_FILE + ".cell_units"})
        self.assertNotIn("idle.power_mean", result.values)

    def test_missing_unit_column_fails_instead_of_crashing(self):
        text = self.captures[A_FILE].decode().replace("memory.used [MiB]", "memory.used")
        captures = dict(self.captures, **{A_FILE: text.encode()})
        self.assertEqual(failing(self.record, captures), {A_FILE + ".cell_units"})

    def test_short_row_fails(self):
        lines = self.captures[A_FILE].decode().split("\n")
        lines[1] = ",".join(lines[1].split(",")[:10])
        captures = dict(self.captures, **{A_FILE: "\n".join(lines).encode()})
        self.assertEqual(failing(self.record, captures), {A_FILE + ".csv_shape"})

    def test_untouched_fixture_has_no_unit_problem(self):
        for name in SYNTHETIC_FILES:
            self.assertEqual(CHECKER.unit_violations(CHECKER.parse_csv(self.captures[name])), [])


class DriverLimitsAreExact(SyntheticBase):
    LIMITS = (("limits_identity.power_limit", "power_limit_w"),
              ("limits_identity.power_min_limit", "power_min_limit_w"),
              ("limits_identity.power_max_limit", "power_max_limit_w"))

    def test_a_sub_tolerance_drift_on_each_limit_fails_its_own_check(self):
        for check, key in self.LIMITS:
            for drift in (0.004, -0.004, 0.0001):
                with self.subTest(check=check, drift=drift):
                    record = self.mutated_record()
                    record["card"][key] += drift
                    failed = failing(record, self.captures)
                    self.assertIn(check, failed)
                    # power_limit_w also feeds the above-limit counts; nothing else may fail.
                    self.assertTrue(all(f == check or f.endswith(".above_limit") for f in failed), failed)

    def test_boolean_and_string_limits_fail(self):
        for check, key in self.LIMITS:
            for bad in (True, str(self.record["card"][key])):
                with self.subTest(check=check, bad=bad):
                    record = self.mutated_record()
                    record["card"][key] = bad
                    self.assertIn(check, failing(record, self.captures))

    def test_whole_number_limit_as_int_still_passes(self):
        record = self.mutated_record()
        for _check, key in self.LIMITS:
            record["card"][key] = int(record["card"][key])
        self.assertEqual(failing(record, self.captures), set())

    def test_series_statistics_keep_their_tolerance(self):
        record = self.mutated_record()
        record["idle"]["power_draw_w"]["mean"] = 2.005
        record["load"]["series"]["SYN_A_index_0"]["mean_w"] = 3.005
        self.assertEqual(failing(record, self.captures), set())


class ArtifactGate(SyntheticBase):
    """Missing and mismatched inputs are rejected before any parsing."""

    def stage(self, directory, overrides=None, omit=None):
        for name, data in self.captures.items():
            if name != omit:
                (Path(directory) / name).write_bytes((overrides or {}).get(name, data))

    def guard_parse(self):
        return mock.patch.object(CHECKER, "parse_csv", side_effect=AssertionError("parsed before verification"))

    def test_good_directory_passes_and_reports_inputs(self):
        pins = synthetic_pins(self.captures)
        with tempfile.TemporaryDirectory() as tmp:
            self.stage(tmp)
            result = CHECKER.run(tmp, SYNTHETIC_RECORD, pins=pins)
        self.assertTrue(result["all_passed"])
        self.assertTrue(result["pinned_sha256_verified_before_parsing"])
        self.assertEqual({i["name"]: i["sha256"] for i in result["inputs"]},
                         {n: p["sha256"] for n, p in pins.items()})
        self.assertEqual(result["checks_failed"], 0)

    def test_missing_file_rejected_before_parsing(self):
        pins = synthetic_pins(self.captures)
        with tempfile.TemporaryDirectory() as tmp, self.guard_parse() as parser:
            self.stage(tmp, omit="synthetic-capture-IDLE.csv")
            with self.assertRaisesRegex(CHECKER.ArtifactError, "missing: synthetic-capture-IDLE.csv"):
                CHECKER.run(tmp, SYNTHETIC_RECORD, pins=pins)
            parser.assert_not_called()

    def test_hash_mismatch_same_size_rejected_before_parsing(self):
        pins = synthetic_pins(self.captures)
        original = self.captures["synthetic-capture-A.csv"]
        changed = original.replace(b"2.00 W", b"3.00 W", 1)
        self.assertEqual(len(changed), len(original))
        self.assertNotEqual(changed, original)
        with tempfile.TemporaryDirectory() as tmp, self.guard_parse() as parser:
            self.stage(tmp, {"synthetic-capture-A.csv": changed})
            with self.assertRaisesRegex(CHECKER.ArtifactError, "hash mismatch: synthetic-capture-A.csv"):
                CHECKER.run(tmp, SYNTHETIC_RECORD, pins=pins)
            parser.assert_not_called()

    def test_size_mismatch_rejected_before_parsing(self):
        pins = synthetic_pins(self.captures)
        with tempfile.TemporaryDirectory() as tmp, self.guard_parse() as parser:
            self.stage(tmp, {"synthetic-capture-A.csv": self.captures["synthetic-capture-A.csv"] + b"\n"})
            with self.assertRaisesRegex(CHECKER.ArtifactError, "size mismatch: synthetic-capture-A.csv"):
                CHECKER.run(tmp, SYNTHETIC_RECORD, pins=pins)
            parser.assert_not_called()

    def test_one_bad_file_rejects_the_whole_directory(self):
        pins = synthetic_pins(self.captures)
        bad = b"x" * len(self.captures["synthetic-capture-IDLE.csv"])
        with tempfile.TemporaryDirectory() as tmp, self.guard_parse() as parser:
            self.stage(tmp, {"synthetic-capture-IDLE.csv": bad})
            with self.assertRaises(CHECKER.ArtifactError):
                CHECKER.run(tmp, SYNTHETIC_RECORD, pins=pins)
            parser.assert_not_called()

    def test_empty_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, self.guard_parse() as parser:
            with self.assertRaises(CHECKER.ArtifactError):
                CHECKER.run(tmp, SYNTHETIC_RECORD, pins=synthetic_pins(self.captures))
            parser.assert_not_called()

    def test_cli_requires_artifact_dir_and_rejects_an_empty_one(self):
        with self.assertRaises(SystemExit) as raised, mock.patch("sys.stderr"):
            CHECKER.main([])
        self.assertEqual(raised.exception.code, 2)
        with tempfile.TemporaryDirectory() as tmp, self.guard_parse() as parser, mock.patch("sys.stderr"):
            with self.assertRaises(SystemExit) as raised:
                CHECKER.main(["--artifact-dir", tmp])
            self.assertEqual(raised.exception.code, 2)
            parser.assert_not_called()

    def test_cli_refuses_to_overwrite_an_output_file(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch("sys.stderr"):
            out = Path(tmp) / "result.json"
            out.write_text("keep")
            with self.assertRaises(SystemExit):
                CHECKER.main(["--artifact-dir", tmp, "--output", str(out)])
            self.assertEqual(out.read_text(), "keep")

    def test_cli_preserves_an_output_created_during_validation(self):
        # Another writer creates the output after main's early existence check,
        # while validation runs. main must refuse and leave those bytes alone.
        pins = synthetic_pins(self.captures)
        with tempfile.TemporaryDirectory() as tmp, mock.patch("sys.stderr"):
            self.stage(tmp)
            out = Path(tmp) / "result.json"
            sentinel = b"completed evidence from the competing writer\n"
            real_run = CHECKER.run

            def run_then_compete(*args, **kwargs):
                result = real_run(*args, **kwargs)
                out.write_bytes(sentinel)
                return result

            with mock.patch.object(CHECKER, "PINS", pins), \
                    mock.patch.object(CHECKER, "run", side_effect=run_then_compete):
                with self.assertRaises(SystemExit) as raised:
                    CHECKER.main(["--artifact-dir", tmp, "--record", str(SYNTHETIC_RECORD),
                                  "--output", str(out)])
            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(out.read_bytes(), sentinel)

    def test_cli_creates_a_new_output_file_exactly_once(self):
        pins = synthetic_pins(self.captures)
        with tempfile.TemporaryDirectory() as tmp, mock.patch("sys.stdout"):
            self.stage(tmp)
            out = Path(tmp) / "result.json"
            with mock.patch.object(CHECKER, "PINS", pins):
                code = CHECKER.main(["--artifact-dir", tmp, "--record", str(SYNTHETIC_RECORD),
                                     "--output", str(out)])
            self.assertEqual(code, 0)
            self.assertTrue(json.loads(out.read_text())["all_passed"])

    def test_real_pins_name_the_published_redacted_files(self):
        self.assertEqual(set(CHECKER.PINS), {A_NAME, IDLE_NAME})
        for pin in CHECKER.PINS.values():
            self.assertRegex(pin["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(pin["bytes"], 0)

    def test_no_real_capture_is_stored_in_the_repository(self):
        raw = ROOT / "research/T2-infrastructure/measurements/raw"
        self.assertEqual(sorted(raw.glob("*.csv")) if raw.exists() else [], [])
        for name in CHECKER.PINS:
            self.assertEqual(list((ROOT / "research").rglob(name)), [], name)


class RecordStructure(unittest.TestCase):
    """Checks that need no capture bytes."""

    @classmethod
    def setUpClass(cls):
        cls.text = RECORD.read_text()
        cls.record = json.loads(cls.text)

    def test_csv_hashes_match_record(self):
        listed = {f["manifest_id"]: f for f in self.record["raw_evidence"]["files"]}
        by_name = {"power-raw-capture-A": A_NAME, "power-raw-capture-IDLE": IDLE_NAME}
        self.assertEqual(set(listed), set(by_name))
        for manifest_id, name in by_name.items():
            self.assertEqual(listed[manifest_id]["sha256"], CHECKER.PINS[name]["sha256"], name)
            self.assertEqual(listed[manifest_id]["bytes"], CHECKER.PINS[name]["bytes"], name)
        self.assertEqual(len(listed), 2)

    def test_record_names_no_repository_capture_path_or_url(self):
        raw = self.record["raw_evidence"]
        self.assertNotIn("research/T2-infrastructure/measurements/raw", self.text)
        for entry in raw["files"]:
            for key in ("path", "uri", "url"):
                self.assertNotIn(key, entry)
        self.assertNotIn("http", json.dumps(raw))

    def test_published_csvs_carry_no_gpu_uuid(self):
        # The capture bytes are not in the repository; this only checks that the
        # record keeps declaring the redaction. The bytes are checked by the
        # checker (no_gpu_uuid_string / uuid_column_redacted) on supplied files.
        self.assertIn("uuid", self.record["raw_evidence"]["redaction"].lower())

    def test_redaction_is_declared_with_original_hashes(self):
        raw = self.record["raw_evidence"]
        self.assertIs(raw["original_capture_hashes_verified"], False)
        # A formatted digest is a declaration; these bytes are not available here.
        self.assertTrue(raw["published_hash_scope"])
        self.assertTrue(raw["redaction"])
        for entry in raw["files"]:
            self.assertRegex(entry["original_sha256"], r"^[0-9a-f]{64}$")
            self.assertNotEqual(entry["original_sha256"], entry["sha256"])

    def test_datasheet_power_matches_quote_and_driver_limit(self):
        card = self.record["card"]
        quoted = re.findall(r"(\d+)\s*W\b", card["datasheet"]["quote"])
        self.assertEqual(len(quoted), 1, "datasheet quote must hold exactly one 'N W' figure")
        self.assertEqual(card["datasheet_total_board_power_w"], int(quoted[0]), "datasheet figure vs quote")
        self.assertEqual(card["datasheet_total_board_power_w"], card["power_limit_w"], "datasheet figure vs driver limit")

    def test_series_bind_to_actual_capture_and_device_without_aggregation(self):
        declared = {(d["index"], d["pci_bus_id"]) for d in self.record["observed_device_identifiers"]}
        self.assertEqual(declared, {("0", "00000000:01:00.0"), ("1", "00000000:05:00.0")})
        expected = {"A_gpu_index_0": (A_NAME, "0"), "A_gpu_index_1": (A_NAME, "1"),
                    "IDLE_gpu_index_1": (IDLE_NAME, "1")}
        self.assertEqual(set(self.record["load"]["series"]), set(expected))
        for name, (filename, index) in expected.items():
            series = self.record["load"]["series"][name]
            self.assertEqual(series["source_file"], filename)
            self.assertEqual(series["device"]["index"], index)
            self.assertIn((series["device"]["index"], series["device"]["pci_bus_id"]), declared)
        self.assertEqual(self.record["idle"]["source_file"], IDLE_NAME)
        self.assertEqual(self.record["idle"]["device"]["index"], "0")
        self.assertIn(("0", self.record["idle"]["device"]["pci_bus_id"]), declared)
        aggregation = self.record["aggregation"]
        self.assertEqual(aggregation["unit"], "per-device series")
        for key in ("pooled_across_devices", "summed_across_devices", "cross_device_scaling_claim"):
            self.assertIs(aggregation[key], False, key)

    def test_record_states_observed_wording_and_status(self):
        self.assertEqual(self.record["evidence_disposition"], "unverified_contributor_report")
        self.assertEqual(self.record["status"], "contributor_reported_execution")
        for key in ("workload_verified", "model_residency_verified",
                    "utc_timezone_verified", "physical_power_calibration_verified"):
            self.assertIs(self.record["context_verification"][key], False, key)
        self.assertNotIn("observed_utc", self.record)
        self.assertTrue(self.record["timestamp_provenance"])
        for section in [self.record["idle"], *self.record["load"]["series"].values()]:
            self.assertNotIn("first_sample_utc", section)
            self.assertNotIn("last_sample_utc", section)
            self.assertTrue(section["first_sample_reported_utc"])
            self.assertTrue(section["last_sample_reported_utc"])
        for key in ("workload_pinned", "model_pinned", "engine_pinned"):
            self.assertIs(self.record["load"][key], False, key)


if __name__ == "__main__":
    unittest.main()
