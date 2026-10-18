"""Offline qualification checks for the proposed MR-09 native total-buffer setup.

This tool never downloads artifacts or launches a GPU runtime. A prepared setup
is reviewable while native allocation/capture qualification remains outstanding.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

DIRECTORY = Path("research/market/measurements/total-memory-setup-2026-10-18")
MIB = 2**20

# These are the reviewed preparation's bindings, not runtime qualification.
# A different pin or effective configuration needs a separately reviewed setup.
REVIEWED_SETUP = {
    "status": "prepared_not_gpu_qualified", "execution_enabled": False,
    "estimator": {
        "name": "gpustack/gguf-parser-go", "version": "v0.26.4",
        "commit": "637cd9a7a03993ab30ace3c53dd8af5c37f46a94",
        "windows_exe_sha256": "8da9ae6b8968d5d2dee4eaf48dbc24ed48bf3de02794c8dbe0b2a9443b12c92c",
        "platform_footprint_mib": [0, 0],
    },
    "runtime": {
        "name": "ggml-org/llama.cpp", "release": "b11669",
        "commit": "620d2225cc436ab0b001e3200e590e3b286ef9ab",
        "planned_archive": "llama-b11669-bin-win-cuda-13.4-x64.zip",
        "planned_archive_sha256": "3b92d5c064f5032e603e531d3ec8961f3bd6613e5dfad047399a92dec8e95dbc",
        "archive_verification": "publisher release digest only; not downloaded or executed",
        "planned_cudart_archive": "cudart-llama-bin-win-cuda-13.4-x64.zip",
        "planned_cudart_sha256": "738f8c251ac22b70c3ae6f83a10cf222725df0395246a2cf58f32bdb85fbe668",
        "device": "CUDA0", "devices": 1, "auto_fit": False, "graphs": False,
        "offload_layers": 31,
    },
    "artifact": {
        "repo": "bartowski/SmolLM2-135M-Instruct-GGUF",
        "revision": "09816acd5d99df7be770d85ea30822623dab342c",
        "file": "SmolLM2-135M-Instruct-f16.gguf", "bytes": 270885952,
        "sha256": "f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57",
    },
    "configuration": {
        "context_capacity": 512, "logical_batch": 256, "physical_batch": 256,
        "active_sequences": 1, "kv_key": "f16", "kv_value": "f16",
        "flash_attention": False, "mmap": True, "tensor_split": [1],
        "main_gpu": 0, "warmup": False, "generation_forwards": 0,
    },
    "comparison": {
        "metric": "managed_device_buffers_snapshot",
        "estimator_path": "estimate.items[0].vrams[0].nonuma",
        "runtime_field": "fit_memory_breakdown.rows[kind=device,name=CUDA0].self",
        "runtime_source_unit": "MiB_floor",
        "includes": ["model device buffers", "allocated context/KV buffers at configured capacity",
                     "compute/scheduler buffers"],
        "excludes": ["CUDA context and library allocations outside reported buffers",
                     "driver and other processes", "host RAM",
                     "whole-process high-water and transient allocation peaks"],
        "whole_process_peak_equivalent": False, "component_pair_count": 0,
        "total_buffer_pair_count": 0, "approved_tolerance": None,
    },
    "envelope": {
        "preparation_min_gpu_free_mib": 4096,
        "preparation_min_host_ram_bytes": 12884901888,
        "preparation_min_temp_disk_bytes": 6412308016,
        "cap_enforcement": "not implemented/qualified for native runtime; PyTorch allocator cap does not apply",
        "repetitions_after_qualification": 3, "spare_local_only": True, "paid_compute": False,
    },
}

def require_bindings(value, expected, label):
    """Match declared fields recursively, including exact JSON scalar types."""
    if type(value) is not type(expected):
        raise ValueError("binding type mismatch: " + label)
    if isinstance(expected, dict):
        for key, item in expected.items():
            if key not in value:
                raise ValueError("missing binding: " + label + "." + key)
            require_bindings(value[key], item, label + "." + key)
    elif isinstance(expected, list):
        if len(value) != len(expected):
            raise ValueError("binding length mismatch: " + label)
        for index, (actual, item) in enumerate(zip(value, expected)):
            require_bindings(actual, item, f"{label}[{index}]")
    elif value != expected:
        raise ValueError("unreviewed binding: " + label)

def strict_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("non-finite JSON number: " + value)
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("non-finite or overflowing JSON number")
        return number
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=invalid, parse_float=finite_float)

def positive_int(value, label, zero=False):
    if type(value) is not int or value < (0 if zero else 1):
        raise ValueError("invalid integer " + label)
    return value

def managed_snapshot_interval(event, device="CUDA0"):
    """Only a native allocated-buffer event qualifies; not no_alloc projection.

    The caller must still independently qualify artifact/config/build/capture.
    This helper cannot certify physical execution or turn a log into a peak.
    """
    if event.get("metric") != "managed_device_buffers_snapshot" or event.get("no_alloc") is not False:
        raise ValueError("allocated managed-buffer snapshot required, not peak or no_alloc")
    if event.get("unit") != "MiB":
        raise ValueError("pinned native logger emits floored MiB")
    rows = [r for r in event["rows"] if r.get("kind") == "device" and r.get("name") == device]
    if len(rows) != 1 or len([r for r in event["rows"] if r.get("kind") == "device"]) != 1:
        raise ValueError("exactly one CUDA0 device row required")
    row = rows[0]
    total = positive_int(row["self"], "self")
    components = sum(positive_int(row[k], k, zero=True) for k in ("model", "context", "compute"))
    if not components <= total <= components + 2:
        raise ValueError("inconsistent independently floored component totals")
    # Do not sum floored components; the logger floors self after summing bytes.
    return total * MIB, (total + 1) * MIB - 1

def error_interval(estimate_bytes, measured_interval):
    """Exact integer-byte/relative endpoints; observed resolution, not fit bounds."""
    estimate = positive_int(estimate_bytes, "estimate")
    low, high = measured_interval
    positive_int(low, "measured low")
    positive_int(high, "measured high")
    if high < low:
        raise ValueError("inverted interval")
    signed_low, signed_high = estimate - high, estimate - low
    abs_low = 0 if signed_low <= 0 <= signed_high else min(abs(signed_low), abs(signed_high))
    rel_low, rel_high = Fraction(100 * signed_low, high), Fraction(100 * signed_high, low)
    return {"signed_bytes": [signed_low, signed_high],
            "absolute_bytes": [abs_low, max(abs(signed_low), abs(signed_high))],
            "signed_relative_percent_exact": [str(rel_low), str(rel_high)],
            "scope": "measurement rounding interval only; no tolerance/pass/fail or universal bound"}

def validate_setup(directory):
    setup = strict_json(directory / "setup.json")
    preparation = strict_json(directory / "preparation.json")
    require_bindings(setup, REVIEWED_SETUP, "setup")
    for group in ("estimator", "runtime", "configuration", "comparison"):
        if set(setup[group]) != set(REVIEWED_SETUP[group]):
            raise ValueError("unreviewed fields in " + group)
    artifact, config, runtime = setup["artifact"], setup["configuration"], setup["runtime"]
    require_bindings(preparation, {
        "artifact_sha256": artifact["sha256"], "artifact_bytes": artifact["bytes"],
        "estimator_exe_sha256": setup["estimator"]["windows_exe_sha256"],
        "estimator_version": "gguf-parser.exe version v0.26.4", "exit_code": 0,
        "estimate_file": "gguf-parser-estimate.json", "runtime_execution": "unexecuted",
        "argv": ["$GGUF_PARSER", "--path", "$GGUF_FILE", "--ctx-size", "512",
                 "--batch-size", "256", "--ubatch-size", "256", "--parallel-size", "1",
                 "--gpu-layers", "31", "--tensor-split", "1", "--main-gpu", "0",
                 "--cache-type-k", "f16", "--cache-type-v", "f16", "--no-flash-attention",
                 "--platform-footprint", "0,0", "--skip-tokenizer", "--json"],
    }, "preparation")
    raw_path = directory / preparation["estimate_file"]
    if hashlib.sha256(raw_path.read_bytes()).hexdigest() != preparation["estimate_sha256"]:
        raise ValueError("estimator output hash drift")
    raw = strict_json(raw_path)
    gates = setup["qualification_gates"]
    if type(gates) is not list or not gates or any(type(gate) is not str or not gate.strip() for gate in gates):
        raise ValueError("retain explicit qualification gates")
    cap = positive_int(setup["envelope"]["future_managed_allocation_cap_bytes"], "cap")
    if cap > 2136809472:
        raise ValueError("unreviewed budget increase")
    est = raw["estimate"]
    require_bindings(est, {
        "contextSize": config["context_capacity"], "logicalBatchSize": config["logical_batch"],
        "physicalBatchSize": config["physical_batch"], "flashAttention": config["flash_attention"],
        "noMMap": not config["mmap"],
    }, "effective estimate")
    require_bindings(raw["metadata"], {"fileSize": artifact["bytes"], "fileTypeDetail": "F16"}, "GGUF metadata")
    require_bindings(raw["architecture"], {"blockCount": 30, "attentionHeadCountKV": 3,
                                           "attentionKeyLength": 64}, "GGUF geometry")
    if type(est["items"]) is not list or len(est["items"]) != 1:
        raise ValueError("exactly one offload configuration required")
    item = est["items"][0]
    require_bindings(item, {"offloadLayers": runtime["offload_layers"], "fullOffloaded": True}, "placement")
    if type(item["vrams"]) is not list or len(item["vrams"]) != runtime["devices"]:
        raise ValueError("full single-device layer placement required")
    gpu = item["vrams"][0]
    require_bindings(gpu, {"position": config["main_gpu"], "remote": False,
                           "handleOutputLayer": True}, "device placement")
    estimate = positive_int(gpu["nonuma"], "estimate")
    require_bindings(preparation["managed_device_estimate_bytes"], estimate, "estimate ledger")
    return {"status":"prepared_not_gpu_qualified", "estimated_managed_device_bytes":estimate,
            "runtime_observations":0, "total_buffer_pairs":0, "whole_process_peak_pairs":0,
            "execution_enabled":False, "outstanding_gates":setup["qualification_gates"]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory",type=Path,default=DIRECTORY)
    args = parser.parse_args()
    print(json.dumps(validate_setup(args.directory),indent=2,allow_nan=False))

if __name__ == "__main__":
    main()
