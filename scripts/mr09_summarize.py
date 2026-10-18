"""Summarize sanitized MR-09 real-run counters without inventing failure errors."""

import argparse
import csv
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
    """Base model/code/protocol/workload pins must match, including failures."""
    for field in PIN_FIELDS:
        if not isinstance(run.get(field), str) or not run[field]:
            raise ValueError(f"missing pin: {field}")
    if not isinstance(run.get("configuration"), dict):
        raise ValueError("configuration must be an object")
    return tuple(run[field] for field in PIN_FIELDS) + (
        json.dumps(run["configuration"], sort_keys=True, separators=(",", ":"), allow_nan=False),
    )


def cohort_signature(run):
    """Pin recorded conditions for successful numerical observations.

    Availability, phase counters/timings and publication metadata may vary.
    This checks recorded identities, not artifact truth or physical-device UUIDs.
    """
    inputs = {}
    for field in ("model_geometry", "workload", "actual_tokens"):
        value = run.get(field)
        if not isinstance(value, dict) or not value:
            raise ValueError(f"successful run requires observed {field}")
        inputs[field] = value
    environment = run.get("environment")
    if not isinstance(environment, dict):
        raise ValueError("successful run requires environment pins")
    if any(not isinstance(environment.get(key), str) or not environment[key]
           for key in ("python", "torch", "cuda_build")):
        raise ValueError("successful run requires Python/Torch/CUDA pins")
    packages = environment.get("packages")
    if not isinstance(packages, dict) or not packages or any(
            not isinstance(key, str) or not key
            or not isinstance(value, str) or not value
            for key, value in packages.items()):
        raise ValueError("successful run requires package pins")

    hardware = run.get("hardware")
    if not isinstance(hardware, dict):
        raise ValueError("successful run requires hardware pins")
    for key in ("gpu", "properties", "allocator_backend"):
        if not isinstance(hardware.get(key), str) or not hardware[key]:
            raise ValueError(f"successful run requires hardware pin: {key}")
    for key in ("count", "driver_total_bytes", "process_allocator_limit_bytes"):
        value = hardware.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"successful run requires hardware pin: {key}")

    smi = hardware.get("nvidia_smi_csv")
    if not isinstance(smi, str) or not smi:
        raise ValueError("successful run requires NVIDIA driver/device pins")
    try:
        smi_rows = [
            {key.strip(): value.strip() for key, value in row.items()}
            for row in csv.DictReader(smi.splitlines())
        ]
    except (AttributeError, TypeError, csv.Error) as error:
        raise ValueError("invalid NVIDIA driver/device pins") from error
    smi_fields = ("index", "name", "driver_version", "pci.bus_id")
    if len(smi_rows) != hardware["count"] or any(
            any(not row.get(key) for key in smi_fields) for row in smi_rows):
        raise ValueError("successful run requires NVIDIA driver/device pins")
    device_pins = sorted(tuple(row[key] for key in smi_fields) for row in smi_rows)
    stable_hardware = {
        key: hardware[key] for key in
        ("gpu", "count", "driver_total_bytes",
         "process_allocator_limit_bytes", "allocator_backend")
    }
    stable_hardware["properties"] = re.sub(
        r"uuid=[^,]*, ", "", hardware["properties"])
    stable_hardware["nvidia_devices"] = device_pins

    manifest = run.get("artifact_manifest")
    if not isinstance(manifest, dict) or any(
            manifest.get(key) != run[key] for key in ("model_id", "revision")):
        raise ValueError("successful run requires matching artifact manifest")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("successful run requires artifact identities")
    artifact_pins = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise ValueError("invalid artifact identity")
        name, size, checksum = (
            artifact.get("file"), artifact.get("bytes"), artifact.get("sha256"))
        if (not isinstance(name, str) or not name
                or not isinstance(size, int) or isinstance(size, bool) or size < 0
                or not isinstance(checksum, str)
                or re.fullmatch(r"[0-9a-f]{64}", checksum) is None):
            raise ValueError("invalid artifact identity")
        artifact_pins.append((name, size, checksum))
    if len({item[0] for item in artifact_pins}) != len(artifact_pins):
        raise ValueError("duplicate artifact identity")

    return json.dumps(
        {"environment": environment, "hardware": stable_hardware,
         "artifacts": sorted(artifact_pins), "observed_inputs": inputs},
        sort_keys=True, separators=(",", ":"), allow_nan=False,
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
    cohort_signatures = {}
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
            cohort = cohort_signature(result)
            if cell in cohort_signatures and cohort != cohort_signatures[cell]:
                raise ValueError(f"incompatible measurement cohort: {cell}")
            cohort_signatures[cell] = cohort
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
