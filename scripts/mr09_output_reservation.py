"""Offline, source-bound output-reservation audit. Never runs or corrects an estimator.

This is diagnostic research, not the product sizing model or accepted calibration.
The source interpretations are manually audited and bound to source-audit.json.
"""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from mr09_native_capture import summarize
from mr09_total_memory_setup import strict_json, validate_setup

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path("research/market/measurements/output-reservation-2026-10-18")
INPUT_SHA256 = {'research/market/measurements/total-memory-setup-2026-10-18/setup.json': 'c624de6fbc60201d66c70e5e758320ba1880f7e6ca75f6126a62f577c1016b59',
 'research/market/measurements/total-memory-setup-2026-10-18/preparation.json': '2c479fff9a61a753d61d7c579cdaa122fadefb4a9b1dd19b012655c258848004',
 'research/market/measurements/total-memory-setup-2026-10-18/gguf-parser-estimate.json': '19bb9b673ed757ad4d1bab29656bfb5bf6f6340094310b17687efa8e3c7655af',
 'research/market/measurements/native-qualification-2026-10-18/init-r1.json': '0da6cbbcbdb46f90eb8684aa174de10ce06c9f5b7e76e60588be4fdce1cc17a1',
 'research/market/measurements/native-qualification-2026-10-18/init-r2.json': 'b24f78b0aefa564228453b2b115354f7c338e7739ffd790a452d837ea44d22e3',
 'research/market/measurements/native-qualification-2026-10-18/init-r3.json': 'd6f822f92c21d03d841c30de335f6db46ecff13364f713deab272c753e00cf2d',
 'research/market/measurements/native-qualification-2026-10-18/qualification-summary.json': '5f4bfec024860c418f2f9c5e6252cd5548c2f64e5ed80431b09ee855d5cf7ba5',
 'research/market/measurements/output-reservation-2026-10-18/source-audit.json': 'ad1eaaff27f21fb40fe0762bb535d836a35dad62e75f0206724f2be59678c12c'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_readback(record):
    """Read observed host-output and reservation dimensions without conflating them."""
    stderr = record["stderr"]
    def one(pattern):
        values = re.findall(pattern, stderr, re.MULTILINE)
        if len(values) != 1:
            raise ValueError("missing or ambiguous runtime reservation readback")
        return values[0]
    maximum = int(one(r"^llama_context: n_outputs_max\s*=\s*(\d+)\s*$"))
    per_seq = int(one(r"^llama_context: n_outputs_max_per_seq\s*=\s*(\d+)\s*$"))
    host_mib = one(r"^llama_context:\s+CUDA_Host\s+output buffer size =\s*([0-9]+\.[0-9]{2}) MiB$")
    reservations = [tuple(map(int, t)) for t in re.findall(
        r"^graph_reserve: reserving a graph for ubatch with n_tokens =\s*(\d+), n_seqs =\s*(\d+), n_outputs =\s*(\d+)\s*$", stderr, re.MULTILINE)]
    if not reservations or any(n != 1 for _, n, _ in reservations):
        raise ValueError("unknown graph reservation cohort")
    graph = max(reservations)
    if (maximum, per_seq, host_mib, graph) != (256, 1, "0.19", (256, 1, 256)):
        raise ValueError("unreviewed effective output reservation")
    # Native %.2f is rounded, unlike the separate integer-MiB JSON logger.
    host_interval_mib = [str(Decimal(host_mib)-Decimal("0.005")),
                         str(Decimal(host_mib)+Decimal("0.005"))]
    return {"n_outputs_max": maximum, "n_outputs_max_per_seq": per_seq,
            "prompt_graph": {"tokens": graph[0], "sequences": graph[1], "outputs": graph[2]},
            "observed_host_output_mib_text": host_mib,
            "host_output_rounding_enclosure_mib": host_interval_mib}


def verify_source_copies(directory, audit):
    """Optional fresh local copies; checks bytes/fragments, not their interpretation."""
    for item in audit["files"]:
        path = directory/item["file"]
        if sha(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise ValueError("pinned external source drift")
        lines = path.read_bytes().splitlines(keepends=True)
        for fragment in item["inspected_fragments"]:
            start, end = fragment["lines"]
            if hashlib.sha256(b"".join(lines[start-1:end])).hexdigest() != fragment["sha256"]:
                raise ValueError("inspected source fragment drift")


def analyze(root=ROOT, source_directory=None):
    # Bind exact pre-existing evidence before parsing, and never rewrite it.
    for relative, expected in INPUT_SHA256.items():
        if sha(root/relative) != expected:
            raise ValueError("historical input or source audit drift: " + relative)
    validate_setup(root/"research/market/measurements/total-memory-setup-2026-10-18")
    native = root/"research/market/measurements/native-qualification-2026-10-18"
    summary = summarize(native)
    audit = strict_json(root/DIRECTORY/"source-audit.json")
    if source_directory is not None:
        verify_source_copies(source_directory, audit)
    raw = strict_json(root/"research/market/measurements/total-memory-setup-2026-10-18/gguf-parser-estimate.json")
    a, e = raw["architecture"], raw["estimate"]
    outputs = min(e["contextSize"], e["physicalBatchSize"])
    vocab, embedding = a["vocabularyLength"], a["embeddingLength"]
    observed = [runtime_readback(strict_json(native/f"init-r{r}.json")) for r in (1,2,3)]
    if any(item != observed[0] for item in observed):
        raise ValueError("mixed output reservation cohort")
    return {
        "classification": "source-derived diagnostic bound to existing observations; no new estimator/GPU execution",
        "status": "count_matches_but_output_placement_and_host_capacity_do_not",
        "input_sha256": INPUT_SHA256,
        "estimator_source_interpretation": {
            "architecture": a["architecture"], "output_rows": outputs,
            "dedicated_output_reservation_control": False,
            "output_projection_computation_placement": "host for llama; device exception only eagle3",
            "modeled_host_output_footprint_bytes": (vocab+embedding)*outputs*4,
        },
        "runtime": observed[0],
        "source_derived_tensor_geometry_not_measurements": {
            "vocabulary": vocab, "embedding_width": embedding, "float_bytes": 4,
            "initial_host_logits_rows": 1,
            "initial_host_logits_payload_bytes": vocab*4,
            "prompt_graph_logits_rows": outputs,
            "prompt_graph_logits_payload_bytes": vocab*outputs*4,
            "scheduler_placement_expectation": "CUDA0 output-weight backend; source inference, not a per-tensor allocation trace",
        },
        "reservation_count_match": outputs == observed[0]["prompt_graph"]["outputs"],
        "host_readback_capacity_match": False,
        "device_output_computation_placement_match": False,
        "numerical_error_comparison_admitted": False,
        "accepted_estimator_pairs": 0, "whole_process_peak_pairs": 0,
        "reused_initialization_trials": summary["initialization_trials"],
        "remaining_gates": [
            "independently pinned estimator/runtime pair with matching host readback and device graph-output semantics",
            "allocation alignment, scheduler reuse and remaining compute-model differences",
            "receiving-owner estimator/quantity acceptance and coordinator evidence/tolerance review",
            "inference/VMM/scratch cap and whole-process peaks; broader empirical coverage",
        ],
    }


def validate_published(result, published):
    if json.dumps(result, sort_keys=True) != json.dumps(published, sort_keys=True):
        raise ValueError("published matching report differs from bound inputs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-directory", type=Path)
    args = parser.parse_args()
    result = analyze(source_directory=args.source_directory)
    validate_published(result, strict_json(ROOT/DIRECTORY/"matching-report.json"))
    print(json.dumps({k: result[k] for k in ("status", "reservation_count_match", "numerical_error_comparison_admitted", "accepted_estimator_pairs")}))


if __name__ == "__main__":
    main()
