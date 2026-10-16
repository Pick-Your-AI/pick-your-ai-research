"""Summarize sanitized MR-09 real-run counters without inventing failure errors."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import statistics


PHASES = ("baseline", "loading", "warmup", "prefill", "decode", "steady_state")
METRICS = ("peak_allocated_bytes", "peak_reserved_bytes", "current_allocated_bytes", "current_reserved_bytes")
PIN_FIELDS = ("model_id", "revision", "script_sha256", "protocol_sha256")


def range_summary(values):
    if not values:
        return {"n": 0, "min": None, "median": None, "max": None}
    return {"n": len(values), "min": min(values), "median": statistics.median(values), "max": max(values)}


def run_signature(run):
    """A cell cannot pool different artifacts, code, protocols or workloads."""
    for field in PIN_FIELDS:
        if not isinstance(run.get(field), str) or not run[field]:
            raise ValueError(f"missing pin: {field}")
    if not isinstance(run.get("configuration"), dict):
        raise ValueError("configuration must be an object")
    return tuple(run[field] for field in PIN_FIELDS) + (
        json.dumps(run["configuration"], sort_keys=True, separators=(",", ":"), allow_nan=False),
    )


def validate_success(run):
    free = run.get("hardware", {}).get("initial_driver_free_bytes")
    if not isinstance(free, int) or isinstance(free, bool) or free < 0:
        raise ValueError("successful run requires its initial CUDA free-byte observation")
    phases = run.get("phases", [])
    names = [phase.get("phase") for phase in phases]
    if len(names) != len(PHASES) or set(names) != set(PHASES):
        raise ValueError("successful run requires all six unique phases")
    for phase in phases:
        for metric in METRICS:
            value = phase.get(metric)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"invalid byte counter: {phase['phase']}/{metric}")
        if not (phase["current_allocated_bytes"] <= phase["peak_allocated_bytes"] <= phase["peak_reserved_bytes"]
                and phase["current_allocated_bytes"] <= phase["current_reserved_bytes"] <= phase["peak_reserved_bytes"]):
            raise ValueError(f"inconsistent allocator counters: {phase['phase']}")


def summarize(directory, sanitize=False):
    """Validate the complete batch before any optional publication rewrite."""
    groups = defaultdict(list)
    signatures = {}
    repetitions = set()
    records = []
    # Include dense, GM/M0 supplemental MoE and future explicitly named run cells.
    for path in sorted(directory.glob("mr09-*-r*.json")):
        result = json.loads(path.read_text(encoding="utf-8"))
        cell, repetition = result.get("cell"), result.get("repetition")
        if not isinstance(cell, str) or not cell:
            raise ValueError(f"missing cell: {path.name}")
        if not isinstance(repetition, int) or isinstance(repetition, bool) or repetition <= 0:
            raise ValueError(f"invalid repetition: {path.name}")
        if (cell, repetition) in repetitions:
            raise ValueError(f"duplicate repetition: {cell}/{repetition}")
        repetitions.add((cell, repetition))
        signature = run_signature(result)
        if cell in signatures and signature != signatures[cell]:
            raise ValueError(f"incompatible pins/configuration within cell: {cell}")
        signatures[cell] = signature
        if not isinstance(result.get("status"), str) or not result["status"]:
            raise ValueError(f"missing status: {path.name}")
        if result["status"] == "success":
            validate_success(result)
        records.append((path, result))

    inputs = []
    for path, result in records:
        if sanitize:
            props = result.get("hardware", {}).get("properties", "")
            if isinstance(props, str) and props:
                result["hardware"]["properties"] = re.sub(r"uuid=[^,]*, ", "", props)
            result["publication_sanitization"] = "local paths replaced by named placeholders by runner; hardware UUID removed; LF line endings normalized for Git; counters/pins unchanged"
            path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
        groups[result["cell"]].append(result)
        inputs.append({"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    cells = {}
    for cell, runs in sorted(groups.items()):
        successes = [run for run in runs if run["status"] == "success"]
        phases = {}
        for phase in PHASES:
            samples = [item for run in successes for item in run["phases"] if item["phase"] == phase]
            phases[phase] = {metric: range_summary([sample[metric] for sample in samples]) for metric in METRICS}
        cells[cell] = {"status_counts": dict(Counter(run["status"] for run in runs)),
                       "phases": phases, "repetitions": [run["repetition"] for run in runs],
                       **{field: runs[0][field] for field in PIN_FIELDS},
                       "configuration": runs[0]["configuration"],
                       "initial_cuda_reported_free_bytes": range_summary([run["hardware"]["initial_driver_free_bytes"] for run in successes]),
                       "native_kv_prefill_payload_bytes": range_summary([run["native_kv_prefill_payload"]["measured_bytes"] for run in successes
                                                                        if "native_kv_prefill_payload" in run]),
                       "int4_kv_prefill_payload_bytes": range_summary([run["int4_kv_prefill_payload"]["total_physical_storage_bytes"] for run in successes
                                                                      if "int4_kv_prefill_payload" in run]),
                       "failures": [{"repetition": run["repetition"], "status": run["status"],
                                     "detail": run.get("failure", {"reason": run.get("reason")})}
                                    for run in runs if run["status"] != "success"]}
    all_runs = [run for runs in groups.values() for run in runs]
    summary = {"classification": "summary of real model inference; no universal fit/error bounds",
               "status_counts": dict(Counter(run["status"] for run in all_runs)), "run_count": len(all_runs),
               "measured_script_hashes": sorted({run["script_sha256"] for run in all_runs}),
               "protocol_hashes": sorted({run["protocol_sha256"] for run in all_runs}),
               "comparable_competitor_error_pairs": sum(len(run.get("error_comparisons", [])) for run in all_runs
                                                       if run["status"] == "success"),
               "native_kv_errors_scope": "formula versus tensor-payload layout sanity check only; no competitor/runtime calibration",
               "cells": cells, "input_checksums": inputs}
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path("research/market/measurements"))
    parser.add_argument("--sanitize", action="store_true", help="remove hardware UUID only; retain all counters and pins")
    args = parser.parse_args()
    summary = summarize(args.directory, args.sanitize)
    output = args.directory / "mr09-results-summary.json"
    output.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"summary": str(output), "run_count": summary["run_count"], "status_counts": summary["status_counts"]}))


if __name__ == "__main__":
    main()
