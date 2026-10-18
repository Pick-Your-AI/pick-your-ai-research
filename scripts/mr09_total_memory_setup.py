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
# Freeze the entire reviewed proposal/execution tuple (timestamps excluded).
# Canonical JSON preserves bool/int/float distinctions and rejects added fields.
# Later qualification records do not rewrite this historical CPU preparation.
REVIEWED_SETUP_SHA256 = "dcc7b8693896bc0ad996378dbdb006357132c98741673148156c3954ca1ecc16"
REVIEWED_PREPARATION_SHA256 = "4f6d8255398aa3ce4b40a7d75cb3a776ed6f1c977e9fcc005160767af8a3a2b6"

def require_reviewed_binding(value, ignored, expected, label):
    material = {k:v for k,v in value.items() if k not in ignored}
    actual = hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",", ":"),allow_nan=False).encode()).hexdigest()
    if actual != expected:
        raise ValueError("reviewed " + label + " binding drift; explicit proposal review required")

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
    require_reviewed_binding(setup, {"prepared_utc"}, REVIEWED_SETUP_SHA256, "setup")
    require_reviewed_binding(preparation, {"recorded_utc"}, REVIEWED_PREPARATION_SHA256, "preparation")
    raw_path = directory / preparation["estimate_file"]
    if hashlib.sha256(raw_path.read_bytes()).hexdigest() != preparation["estimate_sha256"]:
        raise ValueError("estimator output hash drift")
    raw = strict_json(raw_path)
    artifact, config, runtime = setup["artifact"], setup["configuration"], setup["runtime"]
    if (artifact["sha256"] != preparation["artifact_sha256"] or artifact["bytes"] != preparation["artifact_bytes"]
            or setup["estimator"]["windows_exe_sha256"] != preparation["estimator_exe_sha256"]):
        raise ValueError("prepared artifact/executable identity mismatch")
    if setup["execution_enabled"] is not False or setup["status"] != "prepared_not_gpu_qualified":
        raise ValueError("this proposal is not an execution authorization")
    if (preparation["runtime_execution"] != "unexecuted"
            or setup["comparison"]["total_buffer_pair_count"] != 0
            or setup["comparison"]["component_pair_count"] != 0):
        raise ValueError("prepared record cannot acquire fabricated runtime pairs")
    if not setup["qualification_gates"] or setup["comparison"]["approved_tolerance"] is not None:
        raise ValueError("retain qualification gates and unknown tolerance")
    if setup["comparison"]["whole_process_peak_equivalent"] is not False:
        raise ValueError("snapshot is not a whole-process peak")
    if (config["context_capacity"],config["logical_batch"],config["physical_batch"],config["active_sequences"]) != (512,256,256,1):
        raise ValueError("unreviewed workload change")
    if (config["kv_key"],config["kv_value"],config["flash_attention"],runtime["auto_fit"],runtime["graphs"],runtime["devices"]) != ("f16","f16",False,False,False,1):
        raise ValueError("unreviewed native configuration change")
    if setup["estimator"]["platform_footprint_mib"] != [0,0]:
        raise ValueError("platform allowance would change the target quantity")
    cap = positive_int(setup["envelope"]["future_managed_allocation_cap_bytes"], "cap")
    if cap > 2136809472 or setup["comparison"]["metric"] != "managed_device_buffers_snapshot":
        raise ValueError("unreviewed budget or target change")
    est = raw["estimate"]
    if (est["contextSize"],est["logicalBatchSize"],est["physicalBatchSize"],est["flashAttention"],est["noMMap"]) != (512,256,256,False,False):
        raise ValueError("effective estimator settings mismatch")
    if raw["metadata"]["fileSize"] != artifact["bytes"] or raw["metadata"]["fileTypeDetail"] != "F16":
        raise ValueError("GGUF format/size mismatch")
    if (raw["architecture"]["blockCount"],raw["architecture"]["attentionHeadCountKV"],raw["architecture"]["attentionKeyLength"]) != (30,3,64):
        raise ValueError("GGUF geometry mismatch")
    if len(est["items"]) != 1:
        raise ValueError("exactly one offload configuration required")
    item = est["items"][0]
    if item["offloadLayers"] != 31 or item["fullOffloaded"] is not True or len(item["vrams"]) != 1:
        raise ValueError("full single-device layer placement required")
    gpu = item["vrams"][0]
    if gpu["position"] != 0 or gpu["remote"] or not gpu["handleOutputLayer"]:
        raise ValueError("local output-layer placement required")
    estimate = positive_int(gpu["nonuma"], "estimate")
    if estimate != preparation["managed_device_estimate_bytes"]:
        raise ValueError("estimate ledger mismatch")
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
