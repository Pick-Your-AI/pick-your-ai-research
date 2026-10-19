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
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import platform
import re
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


def shape_violations(data):
    """Problems in the CSV's own shape, found on the raw rows before any mapping.

    parse_csv maps cells to headers with zip, which silently drops extra
    unheaded cells and lets a repeated header name overwrite an earlier column.
    So: header names must be unique and every row must have exactly as many
    cells as the header.
    """
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""))
    header = [cell.strip() for cell in next(reader, [])]
    problems = []
    repeated = sorted({h for h in header if header.count(h) > 1})
    if repeated:
        problems.append("duplicate header names: %s" % ", ".join(repr(h) for h in repeated))
    for number_, row in enumerate(reader, 1):
        if len(row) != len(header):
            problems.append("row %d has %d cells, header has %d" % (number_, len(row), len(header)))
    return problems


def column_unit(column):
    """The unit text a header such as 'power.draw [W]' declares, or None."""
    match = re.search(r" \[([^\]]+)\]$", column)
    return match.group(1) if match else None


# Every column of the published captures that carries a number plus a unit.
UNIT_COLUMNS = {
    "power.draw [W]": "W", "power.limit [W]": "W", "power.min_limit [W]": "W",
    "power.max_limit [W]": "W", "utilization.gpu [%]": "%", "memory.used [MiB]": "MiB",
    "memory.total [MiB]": "MiB", "clocks.current.sm [MHz]": "MHz",
    "clocks.current.memory [MHz]": "MHz",
}


def unit_violations(rows):
    """Problems that make a capture unusable, found before any value is used.

    Every unit column must exist, and every cell in it must be one number
    followed by one space and exactly the unit text the header declares:
    no other unit, no missing unit, no extra text. Row width and duplicate
    header names are checked earlier, on the raw rows, by shape_violations.
    """
    problems = []
    if not rows:
        return ["no data rows"]
    for column, unit in UNIT_COLUMNS.items():
        if column not in rows[0]:
            problems.append("missing column %r" % column)
            continue
        pattern = re.compile(r"-?[0-9]+(?:\.[0-9]+)?" + re.escape(" " + unit))
        for number_, row in enumerate(rows, 1):
            if not pattern.fullmatch(row.get(column, "")):
                problems.append("row %d column %r: %r is not a number followed by ' %s'"
                                % (number_, column, row.get(column), unit))
                break
    return problems


def number(cell):
    return float(cell.split()[0])


def clock(text, fmt):
    return datetime.strptime(text, fmt)


def cell_decimal(cell):
    """The exact decimal value of a cell's number (the unit was validated before)."""
    return Decimal(cell.split()[0])


def exact(value):
    """A recorded number as an exact Decimal, or None if it is not a real number.

    A boolean is not a number. A float is taken by its shortest repr, so a record
    parsed with parse_float=Decimal (which keeps every written digit) and a plain
    float give the same value when no digits were lost.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value if value.is_finite() else None
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        try:
            result = Decimal(repr(value))
        except InvalidOperation:
            return None
        return result if result.is_finite() else None
    return None


def idle_run(rows, index, utilization, memory_mib, pstate):
    """Leading rows of one device that all satisfy the low-activity predicate.

    The recorded utilization and memory are compared as exact decimals against
    the numbers the CSV declares: a boolean is not a number, and 20.5 MiB is not
    20 MiB.
    """
    want_util, want_mem = exact(utilization), exact(memory_mib)
    run = []
    for row in (r for r in rows if r["index"] == index):
        if (want_util is not None and want_mem is not None
                and cell_decimal(row["utilization.gpu [%]"]) == want_util
                and cell_decimal(row["memory.used [MiB]"]) == want_mem
                and row["pstate"] == pstate):
            run.append(row)
        else:
            break
    return run


def strict_equal(actual, recorded):
    """Equality that never lets a boolean stand in for a number (1 == True in Python).

    Lists and dicts are compared element by element; 1 and 1.0 still match, a
    string never matches a number. Numeric comparison normalizes the actual
    float without rounding an exact parsed recorded number to binary64.
    """
    if isinstance(actual, bool) != isinstance(recorded, bool):
        return False
    if isinstance(actual, dict) and isinstance(recorded, dict):
        return actual.keys() == recorded.keys() and all(strict_equal(actual[k], recorded[k]) for k in actual)
    if isinstance(actual, (list, tuple)) and isinstance(recorded, (list, tuple)):
        return len(actual) == len(recorded) and all(strict_equal(a, r) for a, r in zip(actual, recorded))
    if isinstance(actual, (int, float, Decimal)) and not isinstance(actual, bool):
        actual_number = exact(actual)
        return actual_number is not None and actual_number == exact(recorded)
    return actual == recorded


def count_value(recorded):
    """The integer a recorded count stands for, or None if it is not an integer value."""
    if isinstance(recorded, bool):
        return None
    if isinstance(recorded, int):
        return recorded
    if isinstance(recorded, float):
        return int(recorded) if recorded - recorded == 0 and recorded == int(recorded) else None
    if isinstance(recorded, Decimal):
        return int(recorded) if recorded.is_finite() and recorded == recorded.to_integral_value() else None
    return None


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

    def count(self, name, actual, recorded):
        """A recomputed integer count against a recorded count, exactly.

        The recorded value must be an actual integer value: 2 and 2.0 are the
        same count, 2.000000000000000001 and True are not counts at all.
        """
        self.values[name] = actual
        wanted = count_value(recorded)
        self.check(name, lambda: (wanted is not None and actual == wanted,
                                  "recomputed %r, record %r" % (actual, recorded)))

    def close(self, name, actual, recorded):
        self.values[name] = actual
        self.check(name, lambda: (not isinstance(recorded, bool) and not isinstance(actual, bool)
                                  and abs(actual - recorded) <= TOLERANCE_W + 1e-12,
                                  "recomputed %r, record %r" % (actual, recorded)))

    def failed(self):
        return [c for c in self.checks if not c["passed"]]


def check_record(record, captures, exact_record=None):
    """Recompute and compare. `captures` maps file name -> raw bytes."""
    res = Results()
    rows = {name: parse_csv(data) for name, data in captures.items()}
    card = record["card"]
    # exact_record is the same record parsed with parse_float=Decimal, so the
    # digits written in the JSON survive; without it the parsed values are used.
    exact_record = record if exact_record is None else exact_record
    exact_card, exact_idle = exact_record["card"], exact_record["idle"]

    # CSV shape, then units, are checked before any value is read.
    shape_problems = {name: shape_violations(data) for name, data in captures.items()}
    for name in captures:
        res.check(name + ".csv_shape",
                  lambda p=shape_problems[name]: (not p, "; ".join(p[:3]) + (" ..." if len(p) > 3 else "")))
    if any(shape_problems.values()):
        return res  # the mapping to columns cannot be trusted
    unit_problems = {name: unit_violations(rows[name]) for name in captures}
    for name in captures:
        res.check(name + ".cell_units",
                  lambda p=unit_problems[name]: (not p, "; ".join(p[:3]) + (" ..." if len(p) > 3 else "")))
    if any(unit_problems.values()):
        return res  # no value from a capture with a bad unit is used

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
    # The driver limits are compared as numbers, exactly: no rounding or
    # formatting of the recorded value first.
    for label, column, key in (
            ("power_limit", "power.limit [W]", "power_limit_w"),
            ("power_min_limit", "power.min_limit [W]", "power_min_limit_w"),
            ("power_max_limit", "power.max_limit [W]", "power_max_limit_w")):
        res.check("limits_identity." + label,
                  lambda c=column, k=key: (
                      exact(exact_card[k]) is not None
                      and {cell_decimal(r[c]) for r in every} == {exact(exact_card[k])},
                      "file %s, record %r" % (sorted(str(cell_decimal(r[c])) for r in every)[:3], exact_card[k])))
    for label, column, key in (
            ("driver", "driver_version", "driver"),
            ("vbios", "vbios_version", "vbios"),
            ("name", "name", "name")):
        res.check("limits_identity." + label,
                  lambda c=column, k=key: ({r[c] for r in every} == {card[k]},
                                           "file %r, record %r" % (sorted({r[c] for r in every}), card[k])))

    # Low-activity series.
    idle = record["idle"]
    idle_rows = rows[idle["source_file"]]
    idx, pci = idle["device"]["index"], idle["device"]["pci_bus_id"]
    run = idle_run(idle_rows, idx, exact_idle["utilization_pct"], exact_idle["memory_used_mib"], idle["pstate"])
    res.check("idle.nonempty_run", lambda: (bool(run), "no rows satisfy the selected predicate"))
    if not run:
        return res  # nothing to recompute; the failed check above is the result
    device = [r for r in idle_rows if r["index"] == idx]
    res.equal("idle.device_pci", sorted({r["pci.bus_id"] for r in device}), [pci])
    res.count("idle.samples", len(run), exact_idle["samples"])
    res.equal("idle.predicate_pstate", sorted({r["pstate"] for r in run}), [idle["pstate"]])
    res.check("idle.predicate_memory",
              lambda: ({cell_decimal(r["memory.used [MiB]"]) for r in run} == {exact(exact_idle["memory_used_mib"])},
                       "file %s, record %r" % (sorted({r["memory.used [MiB]"] for r in run}), exact_idle["memory_used_mib"])))
    res.check("idle.predicate_utilization",
              lambda: ({cell_decimal(r["utilization.gpu [%]"]) for r in run} == {exact(exact_idle["utilization_pct"])},
                       "file %s, record %r" % (sorted({r["utilization.gpu [%]"] for r in run}), exact_idle["utilization_pct"])))
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
    res.count("idle.excluded_count", len(later), exact_idle["excluded_rows"]["count"])
    res.count("idle.excluded_rows_listed", len(excluded["rows"]), exact_idle["excluded_rows"]["count"])
    actual_rows = [{"utilization_pct": number(r["utilization.gpu [%]"]), "memory_used_mib": number(r["memory.used [MiB]"]),
                    "pstate": r["pstate"], "power_draw_w": number(r["power.draw [W]"])} for r in later]
    res.equal("idle.excluded_rows", actual_rows, exact_idle["excluded_rows"]["rows"])

    # High-utilization series.
    limit = exact(exact_card["power_limit_w"])  # exact Decimal; None if not a number
    series_rows, means, maxima = {}, [], []
    for name, rec in record["load"]["series"].items():
        exact_rec = exact_record["load"]["series"][name]
        d_rows = [r for r in rows[rec["source_file"]] if r["index"] == rec["device"]["index"]]
        series_rows[name] = d_rows
        res.equal("series.%s.device_pci" % name, sorted({r["pci.bus_id"] for r in d_rows}), [rec["device"]["pci_bus_id"]])
        # The selection is a discrete count: compare exact decimals, never floats
        # (79.999999999999999999 % is below 80 even though float() rounds it to 80).
        threshold = Decimal(LOAD_UTILIZATION_PCT)
        qualifying = [r for r in d_rows if cell_decimal(r["utilization.gpu [%]"]) >= threshold]
        below = [r for r in d_rows if cell_decimal(r["utilization.gpu [%]"]) < threshold]
        p = [number(r["power.draw [W]"]) for r in qualifying]
        res.count("series.%s.total" % name, len(d_rows), exact_rec["samples_total"])
        res.count("series.%s.excluded_count" % name, len(below), exact_rec["samples_excluded_below_80pct"])
        res.count("series.%s.samples_used" % name, len(qualifying), exact_rec["samples_used"])
        for which, row, key in (("first", d_rows[0], "first_sample_reported_utc"), ("last", d_rows[-1], "last_sample_reported_utc")):
            res.check("series.%s.boundary_%s" % (name, which),
                      lambda r=row, k=key, rc=rec: (clock(rc[k], REPORTED_TIME_FORMAT) == clock(r["timestamp"], CSV_TIME_FORMAT),
                                                    "record %r, file clock text %r" % (rc[k], r["timestamp"])))
        res.close("series.%s.min" % name, min(p), rec["min_w"])
        res.close("series.%s.mean" % name, statistics.mean(p), rec["mean_w"])
        res.close("series.%s.max" % name, max(p), rec["max_w"])
        above = (sum(cell_decimal(r["power.draw [W]"]) > limit for r in qualifying)
                 if limit is not None else None)
        res.count("series.%s.above_limit" % name, above, exact_rec["samples_above_limit"])
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
    res = check_record(json.loads(record_bytes), contents,
                       exact_record=json.loads(record_bytes, parse_float=Decimal))
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
        try:
            with args.output.open("x", encoding="utf-8", newline="\n") as output:
                output.write(text)
        except FileExistsError:
            parser.error("output exists; never overwrite evidence: " + args.output.name)
    print(text, end="")
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
