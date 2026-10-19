"""Verify the SFF contributor record against explicitly supplied capture bytes.

No artifact is downloaded or found implicitly in the repository. Both file
lengths and SHA-256 digests must match before any CSV is parsed. The ten original
integrity groups retain their per-device and timestamp/count assertions.

Success establishes reported-file integrity and arithmetic only. It does not
verify acquisition, timezone, workload, calibration, original-capture hashes,
rights or external artifact placement. Synthetic CI runs are not capture checks.
"""
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re
import statistics
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research/T2-infrastructure/measurements/rtx-pro-4000-blackwell-sff-power-2026-10-19.json"
IDLE_NAME = "raw-capture-IDLE-20261019T000959Z.csv"
LOAD_NAME = "raw-capture-A-20261018T235741Z.csv"
TOLERANCE_W = 0.01
NUMERIC_UNITS = {
    "power.draw [W]": "W", "power.limit [W]": "W", "power.min_limit [W]": "W",
    "power.max_limit [W]": "W", "utilization.gpu [%]": "%", "memory.used [MiB]": "MiB",
}
REQUIRED_COLUMNS = {
    "timestamp", "index", "name", "uuid", "pci.bus_id", "driver_version",
    "vbios_version", "power.draw [W]", "power.limit [W]", "power.min_limit [W]",
    "power.max_limit [W]", "utilization.gpu [%]", "memory.used [MiB]", "pstate",
}


def input_json(text):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key: {key!r}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("JSON number exceeds finite numeric range")
        return result

    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


def read_rows(data):
    """Parse the already hash-checked bytes without silent CSV truncation."""
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""))
    try:
        header = [cell.strip() for cell in next(reader)]
    except StopIteration as error:
        raise ValueError("empty capture CSV") from error
    if len(set(header)) != len(header) or not REQUIRED_COLUMNS.issubset(header):
        raise ValueError("capture CSV needs unique headers and all required columns")
    result = []
    for line, row in enumerate(reader, 2):
        if len(row) != len(header):
            raise ValueError(f"capture CSV row {line} has the wrong column count")
        parsed = dict(zip(header, (cell.strip() for cell in row)))
        for column, unit in NUMERIC_UNITS.items():
            try:
                number(parsed[column], unit)
            except ValueError as error:
                raise ValueError(f"capture CSV row {line}, {column}: {error}") from error
        result.append(parsed)
    return result


def number(cell, unit):
    match = re.fullmatch(r"([+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+))[ \t]+" + re.escape(unit), cell)
    if match is None:
        raise ValueError(f"numeric cell requires its exact {unit} unit")
    result = float(match.group(1))
    if not math.isfinite(result):
        raise ValueError("capture contains a non-finite number")
    return result


def idle_run(rows):
    """Leading rows of GPU 0 with 0 % utilization, 244 MiB and pstate P5."""
    run = []
    for row in (r for r in rows if r["index"] == "0"):
        if (number(row["utilization.gpu [%]"], "%") == 0
                and row["memory.used [MiB]"] == "244 MiB" and row["pstate"] == "P5"):
            run.append(row)
        else:
            break
    return run


def load_powers(rows, index):
    return [number(r["power.draw [W]"], "W") for r in rows
            if r["index"] == index and number(r["utilization.gpu [%]"], "%") >= 80]


def load_artifacts(record, artifact_dir):
    """Validate all exact input byte sequences before parsing any capture."""
    directory = Path(artifact_dir).resolve(strict=True)
    if not directory.is_dir():
        raise ValueError("artifact directory is not a directory")
    entries = record["raw_evidence"]["files"]
    if not isinstance(entries, list) or len(entries) != 2:
        raise ValueError("exactly two capture entries are required")
    names = [entry["path"] for entry in entries]
    if any(type(name) is not str for name in names) or set(names) != {IDLE_NAME, LOAD_NAME}:
        raise ValueError("capture paths must be the two distinct expected basenames")
    result = {}
    for entry in entries:
        name, size, digest = entry["path"], entry["bytes"], entry["sha256"]
        if type(size) is not int or size <= 0:
            raise ValueError(f"{name}: positive integer byte count required")
        if type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError(f"{name}: lowercase SHA-256 required")
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{name}: regular supplied capture file required")
        if path.stat().st_size != size:
            raise ValueError(f"{name}: byte length mismatch")
        data = path.read_bytes()
        if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"{name}: SHA-256 or byte length mismatch")
        result[name] = data
    return result


def check_count_types(record):
    """Boolean and decimal aliases cannot certify recorded row counts."""
    counts = [record["idle"]["samples"], record["idle"]["excluded_rows"]["count"]]
    for series in record["load"]["series"].values():
        counts.extend(series[key] for key in (
            "samples_total", "samples_used", "samples_excluded_below_80pct", "samples_above_limit"))
    if any(type(value) is not int or value < 0 for value in counts):
        raise ValueError("row counts must be nonnegative JSON integer tokens")
    for key in ("utilization_pct", "memory_used_mib"):
        value = record["idle"][key]
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("idle summary values must be finite numbers")
    for row in record["idle"]["excluded_rows"]["rows"]:
        for key in ("utilization_pct", "memory_used_mib", "power_draw_w"):
            value = row[key]
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError("excluded-row values must be finite numbers")


class PowerRecordChecks(unittest.TestCase):
    """Reusable original integrity assertions; discovery runs synthetic callers."""
    def __init__(self, record, artifacts):
        super().__init__()
        self.record = record
        self.artifacts = artifacts
        self.idle_rows = read_rows(artifacts[IDLE_NAME])
        self.load_rows = read_rows(artifacts[LOAD_NAME])

    def assertClose(self, actual, expected, label):
        self.assertIs(type(expected) in (int, float), True, label + " numeric type")
        self.assertTrue(math.isfinite(expected), label + " finite number")
        self.assertAlmostEqual(actual, expected, delta=TOLERANCE_W,
                               msg="%s: recomputed %s, record says %s" % (label, actual, expected))

    def assertReportedTimestampMatchesRow(self, reported, row):
        # Compare clock text only. The contributor's literal Z label is not
        # evidence that the offset-free capture was acquired in UTC.
        self.assertEqual(datetime.strptime(reported, "%Y-%m-%dT%H:%M:%S.%fZ"),
                         datetime.strptime(row["timestamp"], "%Y/%m/%d %H:%M:%S.%f"))

    def test_idle_statistics_recompute_from_csv(self):
        run = idle_run(self.idle_rows)
        power = [number(r["power.draw [W]"], "W") for r in run]
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
        rec = self.record["idle"]
        self.assertEqual({r["pstate"] for r in run}, {rec["pstate"]})
        self.assertEqual({number(r["utilization.gpu [%]"], "%") for r in run},
                         {rec["utilization_pct"]})
        self.assertEqual({number(r["memory.used [MiB]"], "MiB") for r in run},
                         {rec["memory_used_mib"]})
        excluded = self.record["idle"]["excluded_rows"]
        gpu0 = [r for r in self.idle_rows if r["index"] == "0"]
        self.assertEqual(len(gpu0) - len(run), excluded["count"], "excluded row count")
        self.assertEqual(len(excluded["rows"]), excluded["count"])
        self.assertEqual({number(r["utilization.gpu [%]"], "%") for r in run}, {0.0})
        actual = [{"utilization_pct": number(r["utilization.gpu [%]"], "%"),
                   "memory_used_mib": number(r["memory.used [MiB]"], "MiB"),
                   "pstate": r["pstate"], "power_draw_w": number(r["power.draw [W]"], "W")}
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
                        if number(r["utilization.gpu [%]"], "%") < 80]
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
        for column, field in (("power.limit [W]", "power_limit_w"),
                              ("power.min_limit [W]", "power_min_limit_w"),
                              ("power.max_limit [W]", "power_max_limit_w")):
            self.assertIs(type(card[field]) in (int, float), True, field + " numeric type")
            self.assertTrue(math.isfinite(card[field]), field + " finite number")
            self.assertEqual({number(r[column], "W") for r in rows}, {card[field]})
        self.assertEqual({r["driver_version"] for r in rows}, {card["driver"]})
        self.assertEqual({r["vbios_version"] for r in rows}, {card["vbios"]})
        self.assertEqual({r["name"] for r in rows}, {card["name"]})

    def test_csv_hashes_match_record(self):
        listed = {Path(f["path"]).name: f["sha256"] for f in self.record["raw_evidence"]["files"]}
        for name, data in self.artifacts.items():
            digest = hashlib.sha256(data).hexdigest()
            self.assertEqual(digest, listed[name], "sha256 of " + name)
        self.assertEqual(len(listed), 2)

    def test_published_csvs_carry_no_gpu_uuid(self):
        for name, data in self.artifacts.items():
            text = data.decode("utf-8")
            self.assertNotIn("GPU-", text, "GPU uuid left in " + name)
            rows = read_rows(data)
            self.assertEqual(len(rows), 180, name)
            self.assertEqual({r["uuid"] for r in rows}, {"REDACTED"}, name)

    def test_redaction_is_declared_with_original_hashes(self):
        raw = self.record["raw_evidence"]
        self.assertIs(raw["original_capture_hashes_verified"], False)
        # A formatted digest is a declaration; these bytes are not available here.
        self.assertTrue(raw["published_hash_scope"])
        self.assertTrue(raw["redaction"])
        for entry in raw["files"]:
            self.assertRegex(entry["original_sha256"], r"^[0-9a-f]{64}$")
            self.assertNotEqual(entry["original_sha256"], entry["sha256"])
            self.assertEqual(entry["bytes"], len(self.artifacts[entry["path"]]), entry["path"])

    def test_datasheet_power_matches_quote_and_driver_limit(self):
        card = self.record["card"]
        quoted = re.findall(r"(\d+)\s*W\b", card["datasheet"]["quote"])
        self.assertEqual(len(quoted), 1, "datasheet quote must hold exactly one 'N W' figure")
        self.assertEqual(card["datasheet_total_board_power_w"], int(quoted[0]), "datasheet figure vs quote")
        self.assertEqual(card["datasheet_total_board_power_w"], card["power_limit_w"], "datasheet figure vs driver limit")

    def test_series_bind_to_actual_capture_and_device_without_aggregation(self):
        captures = {IDLE_NAME: self.idle_rows, LOAD_NAME: self.load_rows}
        observed = {("0", "00000000:01:00.0"), ("1", "00000000:05:00.0")}
        for rows in captures.values():
            self.assertEqual({(r["index"], r["pci.bus_id"]) for r in rows}, observed)
        declared = {(d["index"], d["pci_bus_id"])
                    for d in self.record["observed_device_identifiers"]}
        self.assertEqual(declared, observed)
        expected = {"A_gpu_index_0": (LOAD_NAME, "0"),
                    "A_gpu_index_1": (LOAD_NAME, "1"),
                    "IDLE_gpu_index_1": (IDLE_NAME, "1")}
        self.assertEqual(set(self.record["load"]["series"]), set(expected))
        for name, (filename, index) in expected.items():
            series = self.record["load"]["series"][name]
            self.assertEqual(series["source_file"], filename)
            self.assertEqual(series["device"]["index"], index)
        entries = [self.record["idle"], *self.record["load"]["series"].values()]
        self.assertEqual(self.record["idle"]["source_file"], IDLE_NAME)
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


def verify_record(record_path, artifact_dir):
    """Return a byte-bound integrity receipt, or fail without a success receipt."""
    source = Path(record_path).read_bytes()
    record = input_json(source.decode("utf-8"))
    try:
        check_count_types(record)
        artifacts = load_artifacts(record, artifact_dir)
        checks = PowerRecordChecks(record, artifacts)
        completed = []
        for name in sorted(name for name in dir(checks) if name.startswith("test_")):
            try:
                getattr(checks, name)()
            except AssertionError as error:
                raise ValueError(f"{name}: {error}") from error
            completed.append(name)
    except (KeyError, TypeError, IndexError, UnicodeError, csv.Error) as error:
        raise ValueError(f"invalid power-record/capture structure: {error}") from error
    return {
        "status": "passed",
        "scope": "supplied capture byte integrity and reported per-device arithmetic only",
        "record_sha256": hashlib.sha256(source).hexdigest(),
        "artifacts": [{"filename": name, "bytes": len(data),
                       "sha256": hashlib.sha256(data).hexdigest()}
                      for name, data in sorted(artifacts.items())],
        "integrity_checks": completed,
        "evidence_disposition": record["evidence_disposition"],
        "limits": "No acquisition, timezone, workload, calibration, original-capture, rights or external-placement verification.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", required=True,
                        help="Explicit directory containing the two hash-pinned capture files")
    parser.add_argument("--record", type=Path, default=RECORD,
                        help="Power record JSON (defaults to the dated contributor report)")
    args = parser.parse_args(argv)
    try:
        receipt = verify_record(args.record, args.artifact_dir)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Power record verification failed: {error}\n")
    print(json.dumps(receipt, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
