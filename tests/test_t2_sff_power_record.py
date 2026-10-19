"""Check the per-card power record against its raw nvidia-smi captures.

Claim-to-source integrity only: the record's numbers must be reproducible from
the stored CSV files, and every series must retain its capture/device identity.
These checks do not verify acquisition, workload, timezone, original captures
or calibrated physical power.
"""
import csv
from datetime import datetime
import hashlib
import json
import re
from pathlib import Path
import statistics
import unittest

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "research/T2-infrastructure/measurements"
RECORD = MEASUREMENTS / "rtx-pro-4000-blackwell-sff-power-2026-10-19.json"
IDLE_CSV = MEASUREMENTS / "raw/raw-capture-IDLE-20261019T000959Z.csv"
LOAD_CSV = MEASUREMENTS / "raw/raw-capture-A-20261018T235741Z.csv"
TOLERANCE_W = 0.01


def read_rows(path):
    with open(path, newline="") as handle:
        reader = csv.reader(handle)
        header = [cell.strip() for cell in next(reader)]
        return [dict(zip(header, [cell.strip() for cell in row])) for row in reader]


def number(cell):
    return float(cell.split()[0])


def idle_run(rows):
    """Leading rows of GPU 0 with 0 % utilization, 244 MiB and pstate P5."""
    run = []
    for row in (r for r in rows if r["index"] == "0"):
        if (number(row["utilization.gpu [%]"]) == 0
                and row["memory.used [MiB]"] == "244 MiB" and row["pstate"] == "P5"):
            run.append(row)
        else:
            break
    return run


def load_powers(rows, index):
    return [number(r["power.draw [W]"]) for r in rows
            if r["index"] == index and number(r["utilization.gpu [%]"]) >= 80]


class PowerRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = RECORD.read_text()
        cls.record = json.loads(cls.text)
        cls.idle_rows = read_rows(IDLE_CSV)
        cls.load_rows = read_rows(LOAD_CSV)

    def assertClose(self, actual, expected, label):
        self.assertAlmostEqual(actual, expected, delta=TOLERANCE_W,
                               msg="%s: recomputed %s, record says %s" % (label, actual, expected))

    def assertReportedTimestampMatchesRow(self, reported, row):
        # Compare clock text only. The contributor's literal Z label is not
        # evidence that the offset-free capture was acquired in UTC.
        self.assertEqual(datetime.strptime(reported, "%Y-%m-%dT%H:%M:%S.%fZ"),
                         datetime.strptime(row["timestamp"], "%Y/%m/%d %H:%M:%S.%f"))

    def test_idle_statistics_recompute_from_csv(self):
        run = idle_run(self.idle_rows)
        power = [number(r["power.draw [W]"]) for r in run]
        rec = self.record["idle"]
        self.assertEqual(len(run), rec["samples"], "idle sample count")
        self.assertReportedTimestampMatchesRow(rec["first_sample_reported_utc"], run[0])
        self.assertReportedTimestampMatchesRow(rec["last_sample_reported_utc"], run[-1])
        reported = self.record["reported_observed_utc"]
        self.assertReportedTimestampMatchesRow(reported["idle_window_start"], run[0])
        self.assertReportedTimestampMatchesRow(reported["idle_window_end"], run[-1])
        self.assertClose(min(power), rec["power_draw_w"]["min"], "idle min")
        self.assertClose(statistics.mean(power), rec["power_draw_w"]["mean"], "idle mean")
        self.assertClose(statistics.median(power), rec["power_draw_w"]["median"], "idle median")
        self.assertClose(max(power), rec["power_draw_w"]["max"], "idle max")

    def test_idle_filter_and_excluded_rows_match_telemetry(self):
        run = idle_run(self.idle_rows)
        self.assertTrue(run)
        self.assertEqual({r["pstate"] for r in run}, {"P5"})
        self.assertEqual({r["memory.used [MiB]"] for r in run}, {"244 MiB"})
        excluded = self.record["idle"]["excluded_rows"]
        gpu0 = [r for r in self.idle_rows if r["index"] == "0"]
        self.assertEqual(len(gpu0) - len(run), excluded["count"], "excluded row count")
        self.assertEqual(len(excluded["rows"]), excluded["count"])
        self.assertEqual({number(r["utilization.gpu [%]"]) for r in run}, {0.0})
        actual = [{"utilization_pct": number(r["utilization.gpu [%]"]),
                   "memory_used_mib": number(r["memory.used [MiB]"]),
                   "pstate": r["pstate"], "power_draw_w": number(r["power.draw [W]"])}
                  for r in gpu0[len(run):]]
        self.assertEqual(actual, excluded["rows"])

    def test_load_series_recompute_from_csv(self):
        sources = {"A_gpu_index_0": (self.load_rows, "0"),
                   "A_gpu_index_1": (self.load_rows, "1"),
                   "IDLE_gpu_index_1": (self.idle_rows, "1")}
        means = []
        for name, (rows, index) in sources.items():
            power = load_powers(rows, index)
            rec = self.record["load"]["series"][name]
            device_rows = [r for r in rows if r["index"] == index]
            excluded = [r for r in device_rows
                        if number(r["utilization.gpu [%]"]) < 80]
            self.assertEqual(len(device_rows), rec["samples_total"], name + " total")
            self.assertEqual(len(excluded), rec["samples_excluded_below_80pct"],
                             name + " excluded")
            # The recorded boundaries describe the full per-device capture,
            # while the power statistics use only the qualifying rows.
            self.assertReportedTimestampMatchesRow(
                rec["first_sample_reported_utc"], device_rows[0])
            self.assertReportedTimestampMatchesRow(
                rec["last_sample_reported_utc"], device_rows[-1])
            self.assertEqual(len(power), rec["samples_used"], name + " samples used")
            self.assertClose(min(power), rec["min_w"], name + " min")
            self.assertClose(statistics.mean(power), rec["mean_w"], name + " mean")
            self.assertClose(max(power), rec["max_w"], name + " max")
            self.assertEqual(sum(p > 70.0 for p in power), rec["samples_above_limit"], name + " above limit")
            means.append(statistics.mean(power))
        all_series_rows = [r for rows, index in sources.values()
                           for r in rows if r["index"] == index]
        reported = self.record["reported_observed_utc"]
        self.assertReportedTimestampMatchesRow(
            reported["load_series_first_sample"],
            min(all_series_rows, key=lambda r: r["timestamp"]))
        self.assertReportedTimestampMatchesRow(
            reported["load_series_last_sample"],
            max(all_series_rows, key=lambda r: r["timestamp"]))
        rng = self.record["load"]["range_of_series_means_w"]
        self.assertClose(min(means), rng["low"], "load range low")
        self.assertClose(max(means), rng["high"], "load range high")
        every = [p for rows, index in sources.values() for p in load_powers(rows, index)]
        self.assertClose(max(every), self.record["load"]["max_sample_w"], "load max sample")

    def test_limits_and_identity_match_csv(self):
        rows = self.idle_rows + self.load_rows
        card = self.record["card"]
        self.assertEqual({r["power.limit [W]"] for r in rows}, {"%.2f W" % card["power_limit_w"]})
        self.assertEqual({r["power.min_limit [W]"] for r in rows}, {"%.2f W" % card["power_min_limit_w"]})
        self.assertEqual({r["power.max_limit [W]"] for r in rows}, {"%.2f W" % card["power_max_limit_w"]})
        self.assertEqual({r["driver_version"] for r in rows}, {card["driver"]})
        self.assertEqual({r["vbios_version"] for r in rows}, {card["vbios"]})
        self.assertEqual({r["name"] for r in rows}, {card["name"]})

    def test_csv_hashes_match_record(self):
        listed = {Path(f["path"]).name: f["sha256"] for f in self.record["raw_evidence"]["files"]}
        for path in (IDLE_CSV, LOAD_CSV):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, listed[path.name], "sha256 of " + path.name)
        self.assertEqual(len(listed), 2)

    def test_published_csvs_carry_no_gpu_uuid(self):
        for path in (IDLE_CSV, LOAD_CSV):
            text = path.read_text()
            self.assertNotIn("GPU-", text, "GPU uuid left in " + path.name)
            rows = read_rows(path)
            self.assertEqual(len(rows), 180, path.name)
            self.assertEqual({r["uuid"] for r in rows}, {"REDACTED"}, path.name)

    def test_redaction_is_declared_with_original_hashes(self):
        raw = self.record["raw_evidence"]
        self.assertIs(raw["original_capture_hashes_verified"], False)
        # A formatted digest is a declaration; these bytes are not available here.
        self.assertTrue(raw["published_hash_scope"])
        self.assertTrue(raw["redaction"])
        for entry in raw["files"]:
            self.assertRegex(entry["original_sha256"], r"^[0-9a-f]{64}$")
            self.assertNotEqual(entry["original_sha256"], entry["sha256"])
            self.assertEqual(entry["bytes"], (ROOT / entry["path"]).stat().st_size, entry["path"])

    def test_datasheet_power_matches_quote_and_driver_limit(self):
        card = self.record["card"]
        quoted = re.findall(r"(\d+)\s*W\b", card["datasheet"]["quote"])
        self.assertEqual(len(quoted), 1, "datasheet quote must hold exactly one 'N W' figure")
        self.assertEqual(card["datasheet_total_board_power_w"], int(quoted[0]), "datasheet figure vs quote")
        self.assertEqual(card["datasheet_total_board_power_w"], card["power_limit_w"], "datasheet figure vs driver limit")

    def test_series_bind_to_actual_capture_and_device_without_aggregation(self):
        captures = {IDLE_CSV.name: self.idle_rows, LOAD_CSV.name: self.load_rows}
        observed = {("0", "00000000:01:00.0"), ("1", "00000000:05:00.0")}
        for rows in captures.values():
            self.assertEqual({(r["index"], r["pci.bus_id"]) for r in rows}, observed)
        declared = {(d["index"], d["pci_bus_id"])
                    for d in self.record["observed_device_identifiers"]}
        self.assertEqual(declared, observed)
        expected = {"A_gpu_index_0": (LOAD_CSV.name, "0"),
                    "A_gpu_index_1": (LOAD_CSV.name, "1"),
                    "IDLE_gpu_index_1": (IDLE_CSV.name, "1")}
        self.assertEqual(set(self.record["load"]["series"]), set(expected))
        for name, (filename, index) in expected.items():
            series = self.record["load"]["series"][name]
            self.assertEqual(series["source_file"], filename)
            self.assertEqual(series["device"]["index"], index)
        entries = [self.record["idle"], *self.record["load"]["series"].values()]
        self.assertEqual(self.record["idle"]["source_file"], IDLE_CSV.name)
        self.assertEqual(self.record["idle"]["device"]["index"], "0")
        for entry in entries:
            rows = [r for r in captures[entry["source_file"]]
                    if r["index"] == entry["device"]["index"]]
            self.assertTrue(rows)
            self.assertEqual({r["pci.bus_id"] for r in rows},
                             {entry["device"]["pci_bus_id"]})
        aggregation = self.record["aggregation"]
        self.assertEqual(aggregation["unit"], "per-device series")
        for key in ("pooled_across_devices", "summed_across_devices",
                    "cross_device_scaling_claim"):
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
