"""Recompute the per-device power record from an explicit artifact directory.

The two published capture files are not stored in this repository. This checker
takes the directory that holds them, rejects a missing, wrong-size or
hash-mismatched file BEFORE any byte is parsed, then recomputes every record
statistic, count, boundary text, excluded row and device identity from those
bytes. The same logic (check_record) is what the offline tests run against
clearly synthetic fixtures and corrupted controls.

Scope: claim-to-file arithmetic only. A pass does not verify acquisition,
workload, timezone, the original unredacted captures or calibrated power.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import platform
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = (ROOT / "research/T2-infrastructure/measurements/"
                  "rtx-pro-4000-blackwell-sff-power-2026-10-19.json")
PINS = {
    "raw-capture-A-20261018T235741Z.csv": {
        "sha256": "81302e7ddcd3ba97170b426d0f192952e8fc029c2133fa110dac943d5ee9cf5f",
        "bytes": 38786},
    "raw-capture-IDLE-20261019T000959Z.csv": {
        "sha256": "607163c0349a88ff07aa2646eb7f6ed01ef84e5b808d517724b019667a5147f9",
        "bytes": 38266},
}
TOLERANCE_W = 0.01
LOAD_UTILIZATION_PCT = 80
CSV_TIME_FORMAT = "%Y/%m/%d %H:%M:%S.%f"
REPORTED_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class ArtifactError(Exception):
    """An input file is missing, the wrong size, or does not match its pin."""


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def verify_artifacts(directory, pins=PINS):
    """Return {name: bytes} for every pinned file; parse nothing.

    Every file is checked (present, size, sha256) before the caller may parse
    any of them, so one bad file rejects the whole directory.
    """
    directory = Path(directory)
    contents = {}
    for name, pin in pins.items():
        path = directory / name
        if not path.is_file():
            raise ArtifactError("external artifact missing: " + name)
        data = path.read_bytes()
        if len(data) != pin["bytes"]:
            raise ArtifactError("external artifact size mismatch: " + name)
        if sha256_hex(data) != pin["sha256"]:
            raise ArtifactError("external artifact hash mismatch: " + name)
        contents[name] = data
    return contents


def parse_csv(data):
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""))
    header = [cell.strip() for cell in next(reader)]
    return [dict(zip(header, [cell.strip() for cell in row])) for row in reader]


def number(cell):
    return float(cell.split()[0])


def clock(text, fmt):
    return datetime.strptime(text, fmt)


def idle_run(rows, index, utilization, memory_mib, pstate):
    """Leading rows of one device that all satisfy the low-activity predicate."""
    run = []
    for row in (r for r in rows if r["index"] == index):
        if (number(row["utilization.gpu [%]"]) == utilization
                and row["memory.used [MiB]"] == "%d MiB" % memory_mib
                and row["pstate"] == pstate):
            run.append(row)
        else:
            break
    return run


def strict_equal(actual, recorded):
    """Equality that never lets a boolean stand in for a number (1 == True in Python).

    Lists and dicts are compared element by element; 1 and 1.0 still match, a
    string never matches a number.
    """
    if isinstance(actual, bool) != isinstance(recorded, bool):
        return False
    if isinstance(actual, dict) and isinstance(recorded, dict):
        return actual.keys() == recorded.keys() and all(strict_equal(actual[k], recorded[k]) for k in actual)
    if isinstance(actual, (list, tuple)) and isinstance(recorded, (list, tuple)):
        return len(actual) == len(recorded) and all(strict_equal(a, r) for a, r in zip(actual, recorded))
    return actual == recorded


class Results:
    """Collect named checks; an unexpected error is a failed check, not a crash."""

    def __init__(self):
        self.checks = []
        self.values = {}

    def check(self, name, function):
        try:
            outcome = function()
            passed, detail = (outcome if isinstance(outcome, tuple) else (bool(outcome), ""))
        except Exception as error:  # a malformed record must fail, not abort
            passed, detail = False, "error: %s: %s" % (type(error).__name__, error)
        self.checks.append({"check": name, "passed": bool(passed), "detail": detail})

    def equal(self, name, actual, recorded):
        self.values[name] = actual
        self.check(name, lambda: (strict_equal(actual, recorded), "recomputed %r, record %r" % (actual, recorded)))

    def close(self, name, actual, recorded):
        self.values[name] = actual
        self.check(name, lambda: (not isinstance(recorded, bool) and not isinstance(actual, bool)
                                  and abs(actual - recorded) <= TOLERANCE_W + 1e-12,
                                  "recomputed %r, record %r" % (actual, recorded)))

    def failed(self):
        return [c for c in self.checks if not c["passed"]]


def check_record(record, captures):
    """Recompute and compare. `captures` maps file name -> raw bytes."""
    res = Results()
    rows = {name: parse_csv(data) for name, data in captures.items()}
    card = record["card"]

    for name, data in captures.items():
        res.check(name + ".no_gpu_uuid_string", lambda d=data: (b"GPU-" not in d, "a GPU- string is present" if b"GPU-" in d else ""))
        res.check(name + ".uuid_column_redacted",
                  lambda n=name: ({r.get("uuid") for r in rows[n]} == {"REDACTED"},
                                  "uuid column values: %r" % sorted({str(r.get("uuid")) for r in rows[n]})))
    declared = {(d["index"], d["pci_bus_id"]) for d in record["observed_device_identifiers"]}
    for name in captures:
        observed = {(r["index"], r["pci.bus_id"]) for r in rows[name]}
        res.check(name + ".device_identities", lambda o=observed: (o == declared, "file %r, record %r" % (sorted(o), sorted(declared))))
    every = [r for rs in rows.values() for r in rs]
    for label, column, key, fmt in (
            ("power_limit", "power.limit [W]", "power_limit_w", "%.2f W"),
            ("power_min_limit", "power.min_limit [W]", "power_min_limit_w", "%.2f W"),
            ("power_max_limit", "power.max_limit [W]", "power_max_limit_w", "%.2f W"),
            ("driver", "driver_version", "driver", "%s"),
            ("vbios", "vbios_version", "vbios", "%s"),
            ("name", "name", "name", "%s")):
        res.check("limits_identity." + label,
                  lambda c=column, k=key, f=fmt: ({r[c] for r in every} == {f % card[k]},
                                                  "file %r, record %r" % (sorted({r[c] for r in every}), f % card[k])))

    # Low-activity series.
    idle = record["idle"]
    idle_rows = rows[idle["source_file"]]
    idx, pci = idle["device"]["index"], idle["device"]["pci_bus_id"]
    run = idle_run(idle_rows, idx, idle["utilization_pct"], idle["memory_used_mib"], idle["pstate"])
    res.check("idle.nonempty_run", lambda: (bool(run), "no rows satisfy the selected predicate"))
    if not run:
        return res  # nothing to recompute; the failed check above is the result
    device = [r for r in idle_rows if r["index"] == idx]
    res.equal("idle.device_pci", sorted({r["pci.bus_id"] for r in device}), [pci])
    res.equal("idle.samples", len(run), idle["samples"])
    res.equal("idle.predicate_pstate", sorted({r["pstate"] for r in run}), [idle["pstate"]])
    res.equal("idle.predicate_memory", sorted({r["memory.used [MiB]"] for r in run}), ["%d MiB" % idle["memory_used_mib"]])
    res.equal("idle.predicate_utilization", sorted({number(r["utilization.gpu [%]"]) for r in run}), [float(idle["utilization_pct"])])
    power = [number(r["power.draw [W]"]) for r in run]
    for stat, fn in (("min", min), ("mean", statistics.mean), ("median", statistics.median), ("max", max)):
        res.close("idle.power_" + stat, fn(power), idle["power_draw_w"][stat])
    for which, row, key in (("first", run[0], "first_sample_reported_utc"), ("last", run[-1], "last_sample_reported_utc")):
        res.check("idle.boundary_" + which,
                  lambda r=row, k=key: (clock(idle[k], REPORTED_TIME_FORMAT) == clock(r["timestamp"], CSV_TIME_FORMAT),
                                        "record %r, file clock text %r" % (idle[k], r["timestamp"])))
    reported = record["reported_observed_utc"]
    for key, row in (("idle_window_start", run[0]), ("idle_window_end", run[-1])):
        res.check("window." + key,
                  lambda k=key, r=row: (clock(reported[k], REPORTED_TIME_FORMAT) == clock(r["timestamp"], CSV_TIME_FORMAT),
                                        "record %r, file clock text %r" % (reported[k], r["timestamp"])))
    later = device[len(run):]
    excluded = idle["excluded_rows"]
    res.equal("idle.excluded_count", len(later), excluded["count"])
    res.equal("idle.excluded_rows_listed", len(excluded["rows"]), excluded["count"])
    actual_rows = [{"utilization_pct": number(r["utilization.gpu [%]"]), "memory_used_mib": number(r["memory.used [MiB]"]),
                    "pstate": r["pstate"], "power_draw_w": number(r["power.draw [W]"])} for r in later]
    res.equal("idle.excluded_rows", actual_rows, excluded["rows"])

    # High-utilization series.
    limit = card["power_limit_w"]
    series_rows, means, maxima = {}, [], []
    for name, rec in record["load"]["series"].items():
        d_rows = [r for r in rows[rec["source_file"]] if r["index"] == rec["device"]["index"]]
        series_rows[name] = d_rows
        res.equal("series.%s.device_pci" % name, sorted({r["pci.bus_id"] for r in d_rows}), [rec["device"]["pci_bus_id"]])
        qualifying = [r for r in d_rows if number(r["utilization.gpu [%]"]) >= LOAD_UTILIZATION_PCT]
        below = [r for r in d_rows if number(r["utilization.gpu [%]"]) < LOAD_UTILIZATION_PCT]
        p = [number(r["power.draw [W]"]) for r in qualifying]
        res.equal("series.%s.total" % name, len(d_rows), rec["samples_total"])
        res.equal("series.%s.excluded_count" % name, len(below), rec["samples_excluded_below_80pct"])
        res.equal("series.%s.samples_used" % name, len(qualifying), rec["samples_used"])
        for which, row, key in (("first", d_rows[0], "first_sample_reported_utc"), ("last", d_rows[-1], "last_sample_reported_utc")):
            res.check("series.%s.boundary_%s" % (name, which),
                      lambda r=row, k=key, rc=rec: (clock(rc[k], REPORTED_TIME_FORMAT) == clock(r["timestamp"], CSV_TIME_FORMAT),
                                                    "record %r, file clock text %r" % (rc[k], r["timestamp"])))
        res.close("series.%s.min" % name, min(p), rec["min_w"])
        res.close("series.%s.mean" % name, statistics.mean(p), rec["mean_w"])
        res.close("series.%s.max" % name, max(p), rec["max_w"])
        res.equal("series.%s.above_limit" % name, sum(x > limit for x in p), rec["samples_above_limit"])
        means.append(statistics.mean(p))
        maxima.append(max(p))
    all_rows = [r for rs in series_rows.values() for r in rs]
    for key, row in (("load_series_first_sample", min(all_rows, key=lambda r: r["timestamp"])),
                     ("load_series_last_sample", max(all_rows, key=lambda r: r["timestamp"]))):
        res.check("window." + key,
                  lambda k=key, r=row: (clock(reported[k], REPORTED_TIME_FORMAT) == clock(r["timestamp"], CSV_TIME_FORMAT),
                                        "record %r, file clock text %r" % (reported[k], r["timestamp"])))
    rng = record["load"]["range_of_series_means_w"]
    res.close("load.range_low", min(means), rng["low"])
    res.close("load.range_high", max(means), rng["high"])
    res.close("load.max_sample", max(maxima), record["load"]["max_sample_w"])
    return res


def run(artifact_dir, record_path=DEFAULT_RECORD, pins=None):
    """Verify inputs first, then check. Raises ArtifactError before any parse."""
    contents = verify_artifacts(artifact_dir, PINS if pins is None else pins)
    record_bytes = Path(record_path).read_bytes()
    res = check_record(json.loads(record_bytes), contents)
    failed = res.failed()
    return {
        "classification": "real-artifact execution of check_t2_sff_power_artifacts.py on supplied files; "
                          "claim-to-file arithmetic only, not acquisition, workload, timezone or calibration",
        "inputs": [{"name": n, "sha256": sha256_hex(d), "bytes": len(d)} for n, d in contents.items()],
        "pinned_sha256_verified_before_parsing": True,
        "record": {"name": Path(record_path).name, "sha256": sha256_hex(record_bytes)},
        "script_sha256": sha256_hex(Path(__file__).read_bytes()),
        "python": platform.python_version(),
        "checks_total": len(res.checks),
        "checks_failed": len(failed),
        "all_passed": not failed,
        "recomputed": res.values,
        "checks": res.checks,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.output and args.output.exists():
        parser.error("output exists; never overwrite evidence: " + args.output.name)
    try:
        result = run(args.artifact_dir, args.record)
    except ArtifactError as error:
        parser.error(str(error))
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
