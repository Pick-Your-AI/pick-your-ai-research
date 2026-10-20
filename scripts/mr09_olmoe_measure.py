"""Prospective, local-only OLMoE M1-M4 measurement preparation.

No ML library is imported by plan, admission parsing, or runtime identity reads.
The accepted plan is not device authorization. A concrete, separately reviewed
admission must bind the source, runtime, executable, one device and explicit
capacity inputs. No hardware input is supplied by this repository.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid

import mr09_olmoe_artifacts as artifacts
from mr09_measure import errors, kv_payload_bytes, publish_result

GIB = 2 ** 30
WORDS = "The red bird rests near a quiet tree. Water flows past green fields. "
SCRIPTS = ("mr09_olmoe_artifacts.py", "mr09_olmoe_measure.py", "mr09_measure.py")
RUNTIME_NAMES = ("torch", "transformers", "safetensors")
ADMISSION_KEYS = {
    "schema_version", "authorization_reference", "valid_until_utc", "model_id",
    "revision", "plan_sha256", "scripts_sha256", "runtime", "device", "cell",
    "repetition", "output_file",
}
DEVICE_KEYS = {
    "uuid", "driver_total_bytes", "gpu_allocator_cap_bytes",
    "gpu_workspace_allowance_bytes", "gpu_spare_bytes",
}


def m4_support():
    # Preserve the v1 path: the optional helper imports no ML, and is only needed
    # for M4 plan/runtime/admission/measurement preparation.
    import mr09_olmoe_quanto
    return mr09_olmoe_quanto


def source_identity(cell_name: str = "M1") -> dict:
    selected = SCRIPTS + ("mr09_olmoe_quanto.py",) if cell_name == "M4" else SCRIPTS
    return {name: artifacts.sha256_file(Path(__file__).with_name(name)) for name in selected}


def exact(left, right) -> bool:
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(
        right, sort_keys=True, allow_nan=False)


def runtime_identity(plan: dict, cell_name: str = "M1") -> dict:
    """Bind observed package metadata and the five actual installed loader sources.

    RECORD hashes identify distribution manifests, not a complete audit of every
    installed binary or transitive dependency. No ML import or installation occurs.
    """
    selected = plan["loader"]
    if platform.python_version() != selected["python"]:
        raise ValueError("selected Python 3.12.11 required before ML imports")
    versions, records, distributions = {}, {}, {}
    for name in RUNTIME_NAMES:
        dist = importlib.metadata.distribution(name)
        versions[name] = dist.version
        if dist.version != selected[name]:
            raise ValueError("selected runtime version required: " + name)
        record_files = [f for f in (dist.files or ()) if str(f).endswith(".dist-info/RECORD")]
        if len(record_files) != 1:
            raise ValueError("one installed distribution RECORD required: " + name)
        records[name] = artifacts.sha256_file(Path(dist.locate_file(record_files[0])))
        distributions[name] = dist
    sources = {}
    for item in selected["source_files"]:
        path = Path(distributions["transformers"].locate_file(item["path"].removeprefix("src/")))
        if path.is_symlink() or not path.is_file() or path.stat().st_size != item["bytes"]:
            raise ValueError("installed loader source length/type mismatch")
        digest = artifacts.sha256_file(path)
        if digest != item["sha256"]:
            raise ValueError("installed loader source differs from selected upstream")
        sources[item["path"]] = digest
    result = {"python": platform.python_version(),
              "python_executable_sha256": artifacts.sha256_file(Path(sys.executable).resolve()),
              "versions": versions, "distribution_records_sha256": records,
              "transformers_sources_sha256": sources}
    if cell_name == "M4":
        result["m4_backend"] = m4_support().runtime_identity()
    return result


def cell_spec(plan: dict, cell: str) -> dict:
    if cell not in ("M1", "M2", "M3", "M4"):
        raise NotImplementedError("only fixed M1-M4 cells are prepared; no multi-GPU or workload substitution")
    selected = next(item for item in plan["cells"] if item["id"] == cell)
    if cell == "M4":
        m4_support().validate_cell(selected)
    return selected


def required_capacity(plan: dict, cell: dict, device: dict) -> int:
    if cell["id"] == "M4":
        return m4_support().required_capacity(plan, device)
    return cell["derived_weights_plus_kv_floor_bytes"] + device["gpu_workspace_allowance_bytes"]


def validate_admission(value: dict, plan: dict, cell: dict, repetition: int,
                       runtime: dict, output: Path, now: datetime | None = None) -> dict:
    if type(value) is not dict or set(value) != ADMISSION_KEYS:
        raise ValueError("closed OLMoE admission fields required")
    version = m4_support().SCHEMA if cell["id"] == "M4" else "mr09-olmoe-run-admission/v1"
    if value["schema_version"] != version:
        raise ValueError("unsupported admission version")
    artifacts.reference(value["authorization_reference"])
    for key, wanted in (("model_id", artifacts.MODEL_ID), ("revision", artifacts.REVISION),
                        ("plan_sha256", artifacts.PLAN_SHA256), ("cell", cell["id"]),
                        ("output_file", output.name)):
        if value[key] != wanted:
            raise ValueError("admission identity mismatch: " + key)
    if type(repetition) is not int or repetition not in (1, 2, 3):
        raise ValueError("integer repetition 1, 2 or 3 required")
    if type(value["repetition"]) is not int or value["repetition"] != repetition:
        raise ValueError("admission repetition mismatch")
    if output.name != f"{cell['id']}-r{repetition}.json":
        raise ValueError("output must name the declared cell and repetition")
    if not exact(value["scripts_sha256"], source_identity(cell["id"])) or not exact(value["runtime"], runtime):
        raise ValueError("admission must bind actual scripts, executable and installed runtime identity")
    expiry = value["valid_until_utc"]
    if (type(expiry) is not str
            or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", expiry)):
        raise ValueError("explicit UTC admission expiry required")
    deadline = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
    if (now or datetime.now(timezone.utc)) >= deadline:
        raise ValueError("admission expired; no load or automatic renewal")
    device = value["device"]
    device_keys = DEVICE_KEYS | {"gpu_cache_allowance_bytes"} if cell["id"] == "M4" else DEVICE_KEYS
    if type(device) is not dict or set(device) != device_keys:
        raise ValueError("complete closed device admission required")
    if (type(device["uuid"]) is not str
            or not re.fullmatch(r"GPU-[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", device["uuid"])):
        raise ValueError("one concrete full GPU UUID required; no index, MIG or device list")
    for name in device_keys - {"uuid"}:
        if type(device[name]) is not int or not 0 < device[name] < 2 ** 64:
            raise ValueError("explicit positive integer byte capacity required: " + name)
    if device["gpu_allocator_cap_bytes"] < required_capacity(plan, cell, device):
        raise ValueError("allocator cap is below declared payload plus workspace allowance")
    if device["gpu_allocator_cap_bytes"] + device["gpu_spare_bytes"] > device["driver_total_bytes"]:
        raise ValueError("declared cap and spare capacity exceed the device")
    # These are caller-supplied, separately reviewed inputs, not proof of a current
    # reservation, fit, rights or a whole-process GPU cap.
    return device


def available_host_bytes() -> int:
    if sys.platform == "linux":
        values = {}
        for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
            fields = line.split()
            if fields and fields[0] == "MemAvailable:":
                if len(fields) != 3 or fields[2] != "kB" or not fields[1].isdigit():
                    raise ValueError("unknown Linux physical-memory observation")
                values[fields[0]] = int(fields[1]) * 1024
        if len(values) != 1:
            raise ValueError("MemAvailable observation required")
        return values["MemAvailable:"]
    if sys.platform == "win32":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        *[(name, ctypes.c_ulonglong) for name in (
                            "total_physical", "available_physical", "total_page",
                            "available_page", "total_virtual", "available_virtual", "extended")]]
        value = MemoryStatus()
        value.length = ctypes.sizeof(value)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):
            raise OSError("physical-memory observation failed")
        return value.available_physical
    raise NotImplementedError("fresh physical-memory observation unavailable on this host")


def driver_observation(device: dict) -> dict:
    completed = subprocess.run([
        "nvidia-smi", "--id=" + device["uuid"],
        "--query-gpu=uuid,memory.total,memory.free,driver_version",
        "--format=csv,noheader,nounits",
    ], check=True, capture_output=True, text=True, timeout=30)
    rows = list(csv.reader(io.StringIO(completed.stdout)))
    if len(rows) != 1 or len(rows[0]) != 4:
        raise ValueError("one complete selected-device driver record required")
    uid, total, free, driver = [field.strip() for field in rows[0]]
    if uid != device["uuid"] or not total.isascii() or not total.isdigit() or not free.isascii() or not free.isdigit():
        raise ValueError("driver identity or integer MiB observation mismatch")
    total_bytes, free_bytes = int(total) * 2 ** 20, int(free) * 2 ** 20
    if not driver or total_bytes != device["driver_total_bytes"] or not 0 <= free_bytes <= total_bytes:
        raise ValueError("driver observation disagrees with admission")
    return {"uuid": uid, "driver_total_bytes": total_bytes, "driver_free_bytes": free_bytes,
            "driver_version": driver, "scope": "whole selected GPU, not this process"}


def preflight(plan: dict, device: dict, directory: Path) -> dict:
    host = available_host_bytes()
    disk = shutil.disk_usage(directory).free
    gpu = driver_observation(device)
    guards = {
        "physical_host": host >= plan["screens"]["minimum_available_host_bytes"],
        "available_storage": disk >= plan["screens"]["minimum_available_storage_bytes"],
        "selected_device_free": gpu["driver_free_bytes"] >= device["gpu_allocator_cap_bytes"] + device["gpu_spare_bytes"],
    }
    return {"observed_utc": datetime.now(timezone.utc).isoformat(),
            "available_physical_host_bytes": host, "available_storage_bytes": disk,
            "driver": gpu, "guards": guards,
            "scope": "fresh physical host/whole GPU availability; not process peaks, container quota or fit assurance"}


def prepare_environment(device: dict, cell_name: str = "M1") -> None:
    prefixes = ("torch", "transformers", "optimum.quanto") if cell_name == "M4" else ("torch", "transformers")
    if any(name == prefix or name.startswith(prefix + ".")
           for name in sys.modules for prefix in prefixes):
        raise ValueError("fresh process required; ML libraries must not already be imported")
    settings = {"HF_DEACTIVATE_ASYNC_LOAD": "1", "HF_HUB_OFFLINE": "1",
                "CUDA_VISIBLE_DEVICES": device["uuid"]}
    for name, expected in settings.items():
        if name in os.environ and os.environ[name] != expected:
            raise ValueError("conflicting loader environment: " + name)
    os.environ.update(settings)


def loader_kwargs(torch) -> dict:
    return {"local_files_only": True, "use_safetensors": True, "trust_remote_code": False,
            "dtype": torch.bfloat16, "attn_implementation": "sdpa",
            "experts_implementation": "eager"}


def verify_loaded_model(model, torch, plan: dict) -> dict:
    config = model.config
    geometry = {
        "layers": config.num_hidden_layers, "hidden_size": config.hidden_size,
        "attention_heads": config.num_attention_heads, "kv_heads": config.num_key_value_heads,
        "head_dim": config.hidden_size // config.num_attention_heads,
        "experts": config.num_experts, "experts_per_token": config.num_experts_per_tok,
        "intermediate_size": config.intermediate_size, "vocabulary_size": config.vocab_size,
        "max_positions": config.max_position_embeddings,
    }
    if not exact(geometry, plan["geometry"]):
        raise ValueError("loaded model geometry differs from selected inventory")
    if config._attn_implementation != "sdpa" or config._experts_implementation != "eager":
        raise ValueError("loaded attention/expert backend differs from selected profile")
    count, payload = 0, 0
    for parameter in model.parameters():
        if parameter.device.type != "cpu" or parameter.dtype != torch.bfloat16:
            raise ValueError("CPU conversion with BF16 parameters required before transfer")
        count += parameter.numel()
        payload += parameter.numel() * parameter.element_size()
    if count != plan["totals"]["stored_parameter_elements"] or payload != plan["totals"]["tensor_payload_bytes"]:
        raise ValueError("loaded complete stored parameter payload differs from inventory")
    return {**geometry, "actual_unique_parameter_elements": count,
            "actual_parameter_payload_bytes": payload}


def cache_payload(cache, torch) -> int:
    result = 0
    for layer in cache.layers:
        for tensor in (layer.keys, layer.values):
            if tensor.dtype != torch.bfloat16 or tensor.device.type != "cuda":
                raise ValueError("native CUDA BF16 cache required")
            result += tensor.numel() * tensor.element_size()
    return result


def exercise(model, tokenizer, torch, cache_factory, cell: dict, begin, snapshot,
             observe_quantized=None) -> dict:
    """The historical prompt +32 forwards contract, with a fresh cache after warmup."""
    quantized = cell["id"] == "M4"
    if quantized:
        m4_support().validate_cell(cell)
    if quantized != (observe_quantized is not None):
        raise ValueError("M4 requires its separate retained physical-storage observer")
    tokens = tokenizer.encode(WORDS, add_special_tokens=False)
    if (not tokens or any(type(token) is not int or not 0 <= token < 50304 for token in tokens)):
        raise ValueError("valid nonempty selected tokenizer output required")
    prompt = (tokens * ((cell["prompt_tokens"] + len(tokens) - 1) // len(tokens)))[:cell["prompt_tokens"]]
    inputs = torch.tensor([prompt] * cell["active_sequences"], dtype=torch.long, device="cuda:0")
    with torch.inference_mode():
        started = begin("warmup")
        warm_cache = cache_factory()
        warm = model(input_ids=inputs[:, :64], past_key_values=warm_cache, use_cache=True, logits_to_keep=1)
        warm_next = warm.logits[:, -1].argmax(dim=-1, keepdim=True)
        warm = model(input_ids=warm_next, past_key_values=warm_cache, use_cache=True, logits_to_keep=1)
        snapshot("warmup", started)
        del warm, warm_cache, warm_next
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        cache = cache_factory()
        started = begin("prefill")
        output = model(input_ids=inputs, past_key_values=cache, use_cache=True, logits_to_keep=1)
        next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
        snapshot("prefill", started)
        del output
        if quantized:
            observe_quantized(cache, "prefill", cell["prompt_tokens"])
        else:
            observed_prefill = cache_payload(cache, torch)
            estimate_prefill = kv_payload_bytes(16, 16, 128, cell["prompt_tokens"], cell["active_sequences"], 2)
            if int(cache.get_seq_length()) != cell["prompt_tokens"] or observed_prefill != estimate_prefill:
                raise ValueError("observed prefill cache geometry differs from selected cell")
        started = begin("decode")
        for _ in range(cell["decode_forwards"]):
            output = model(input_ids=next_token, past_key_values=cache, use_cache=True, logits_to_keep=1)
            next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
            del output
        snapshot("decode", started)
        terminal = int(cache.get_seq_length())
        if quantized:
            observe_quantized(cache, "post_decode", terminal)
        else:
            observed_terminal = cache_payload(cache, torch)
            if (terminal != cell["terminal_cache_positions_per_sequence"]
                    or observed_terminal != cell["derived_bf16_kv_payload_bytes"]):
                raise ValueError("observed terminal cache differs from prompt plus 32 forwards")
        started = begin("steady_state")
        snapshot("steady_state", started)
    result = {
        "workload": {"text": WORDS, "add_special_tokens": False,
                     "prompt_token_ids_sha256": hashlib.sha256(json.dumps(prompt).encode()).hexdigest(),
                     "generation": "greedy argmax without EOS early stop; no generated text retained"},
        "warmup_reset": "own warmup output/cache released, synchronized and empty_cache before fresh prefill",
        "actual_tokens": {"prompt_per_sequence": inputs.shape[1],
                          "decode_forwards_per_sequence": cell["decode_forwards"],
                          "greedy_tokens_produced_per_sequence": cell["decode_forwards"] + 1,
                          "cache_tokens_per_sequence": terminal,
                          "active_sequences": inputs.shape[0], "queued_requests": 0},
    }
    if quantized:
        result["comparison_scope"] = "actual unique quantized cache backing storage; no BF16 or estimator comparison"
    else:
        result.update({
            "native_kv_prefill_payload": {"measured_bytes": observed_prefill, "estimated_bytes": estimate_prefill,
                                          "errors": errors(estimate_prefill, observed_prefill)},
            "native_kv_steady_payload_bytes": observed_terminal,
            "comparison_scope": "native KV tensor payload only; no competitor estimator or whole-process comparison",
        })
    return result


def native_allocator_fraction(cap: int, property_total: int) -> tuple[float, int]:
    """Match the pinned native allocator's double multiplication, never exceed cap."""
    if (type(cap) is not int or type(property_total) is not int
            or not 0 < cap < property_total < 2 ** 64):
        raise ValueError("positive cap below actual device-property total required")
    fraction = cap / property_total
    effective = int(fraction * float(property_total))
    while effective > cap:
        fraction = math.nextafter(fraction, 0.0)
        effective = int(fraction * float(property_total))
    if not 0 < fraction < 1 or effective <= 0:
        raise ValueError("bounded native allocator fraction unavailable")
    return fraction, effective


def measure(directory: Path, plan: dict, cell: dict, device: dict, result: dict) -> None:
    # Both offline/sequential controls and selected visibility are set before these imports.
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

    if torch.__version__ != plan["loader"]["torch"] or not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise NotImplementedError("selected one-device CUDA runtime unavailable; no substitution")
    torch.cuda.init()
    torch.cuda.synchronize()
    properties = torch.cuda.get_device_properties(0)
    observed_uuid = bytes(properties.uuid.bytes)
    if observed_uuid != uuid.UUID(device["uuid"][4:]).bytes:
        raise ValueError("CUDA UUID differs from the explicitly admitted device")
    result["cuda_device_uuid"] = "GPU-" + str(uuid.UUID(bytes=observed_uuid))
    free, total = torch.cuda.mem_get_info(0)
    # cudaMemGetInfo reports this CUDA context; nvidia-smi reports a device
    # quantity in MiB. Preserve both domains instead of equating rounded values.
    required = device["gpu_allocator_cap_bytes"] + device["gpu_spare_bytes"]
    if not 0 <= free <= total or total < required or free < required:
        raise ValueError("fresh CUDA-context free/total capacity failed")
    result["cuda_context_observation"] = {
        "free_bytes": free, "total_bytes": total,
        "scope": "cudaMemGetInfo context observation; separate from driver device MiB",
    }
    if torch.cuda.get_allocator_backend() != "native":
        raise NotImplementedError("only the native PyTorch allocator is prepared for this limit")
    fraction, effective = native_allocator_fraction(
        device["gpu_allocator_cap_bytes"], properties.total_memory)
    if effective < required_capacity(plan, cell, device):
        raise ValueError("effective allocator ceiling falls below declared payload/workspace")
    torch.cuda.set_per_process_memory_fraction(fraction, 0)
    torch.manual_seed(6109)
    result["allocator"] = {
        "backend": "native", "requested_limit_bytes": device["gpu_allocator_cap_bytes"],
        "device_property_total_bytes": properties.total_memory,
        "fraction": fraction, "effective_limit_bytes": effective,
        "scope": "pinned native allocator double multiplication; not a whole-process GPU cap",
    }
    result["host_peak_bytes"] = None
    result["whole_process_gpu_peak_bytes"] = None

    def begin(name):
        result["current_phase"] = name
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        return time.perf_counter()

    def snapshot(name, started):
        torch.cuda.synchronize()
        current_free, current_total = torch.cuda.mem_get_info(0)
        result["phases"].append({
            "phase": name, "elapsed_seconds": time.perf_counter() - started,
            "current_allocated_bytes": torch.cuda.memory_allocated(),
            "current_reserved_bytes": torch.cuda.memory_reserved(),
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            "cuda_context_free_bytes": current_free, "cuda_context_total_bytes": current_total,
            "host_peak_bytes": None,
        })

    backend = m4_support().load_backend() if cell["id"] == "M4" else None
    if backend is not None:
        result["quantized_cache"] = {"profile": dict(m4_support().PROFILE), "observations": [],
                                     "allowance_scope": "reviewed retained cache budget; not a prediction of transient fit"}

    started = begin("baseline")
    snapshot("baseline", started)
    started = begin("cpu_loading")
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(directory, **loader_kwargs(torch))
    model.eval()
    result["model_geometry"] = verify_loaded_model(model, torch, plan)
    snapshot("cpu_loading", started)
    started = begin("gpu_loading")
    model.to("cuda:0")
    snapshot("gpu_loading", started)
    if backend is None:
        result.update(exercise(model, tokenizer, torch, lambda: DynamicCache(config=model.config),
                               cell, begin, snapshot))
    else:
        def observe(cache, phase, positions):
            m4_support().retain_observation(result["quantized_cache"]["observations"], cache, torch,
                                            backend, phase, positions, device["gpu_cache_allowance_bytes"])
        result.update(exercise(model, tokenizer, torch, lambda: m4_support().new_cache(backend, model.config),
                               cell, begin, snapshot, observe_quantized=observe))
    result["status"] = "measurement_completed_pending_evidence_review"


def run(directory: Path, admission_path: Path, output: Path, cell_name: str, repetition: int) -> dict:
    plan = artifacts.load_plan()
    cell = cell_spec(plan, cell_name)
    directory = artifacts.external_directory(directory)
    output = artifacts.fresh_output(output, directory)
    admission, admission_sha = artifacts.read_control(admission_path)
    runtime = runtime_identity(plan, cell_name)
    device = validate_admission(admission, plan, cell, repetition, runtime, output)
    claim = {"attempt_id": str(uuid.uuid4()), "cell": cell_name, "repetition": repetition,
             "started_utc": datetime.now(timezone.utc).isoformat(),
             "admission_sha256": admission_sha}
    pending = output.with_name(output.name + ".pending")
    with artifacts.reservation(pending, claim):
        result = {**claim, "classification": "prospective MR09 observation; pending independent evidence review",
                  "status": "unexecuted", "model_id": artifacts.MODEL_ID, "revision": artifacts.REVISION,
                  "plan_sha256": artifacts.PLAN_SHA256, "scripts_sha256": source_identity(cell_name),
                  "runtime": runtime, "cell": cell_name, "repetition": repetition,
                  "configuration": {key: value for key, value in cell.items() if key != "status"},
                  "selected_loader": plan["loader"], "phases": [], "current_phase": "artifact_verification",
                  "authorization_reference": admission["authorization_reference"],
                  "authorization_scope": "operator-supplied external decision; not authenticated by this script",
                  "host_peak_bytes": None, "whole_process_gpu_peak_bytes": None}
        try:
            result["artifacts"] = artifacts.verify(directory)
            result["current_phase"] = "preflight"
            result["fresh_preflight"] = preflight(plan, device, directory)
            if not all(result["fresh_preflight"]["guards"].values()):
                raise ValueError("fresh capacity screen failed; retain observed failed guards")
            # Complete artifact hashing can take minutes. Rebind the exact parsed
            # control bytes and current runtime before any ML import or model load.
            result["current_phase"] = "admission_recheck"
            _, current_admission_sha = artifacts.read_control(admission_path)
            if current_admission_sha != admission_sha:
                raise ValueError("admission bytes changed during artifact verification")
            current_runtime = runtime_identity(plan, cell_name)
            validate_admission(admission, plan, cell, repetition, current_runtime, output)
            prepare_environment(device, cell_name)
            result["current_phase"] = "runtime_import"
            measure(directory, plan, cell, device, result)
        except Exception as error:
            phase = result["current_phase"]
            oom = type(error).__name__ in ("OutOfMemoryError", "MemoryError")
            result["status"] = ("OOM_" + phase if oom else
                                "unsupported" if isinstance(error, (ImportError, NotImplementedError))
                                else "unexecuted" if phase in ("artifact_verification", "preflight", "admission_recheck", "runtime_import")
                                else "runtime_error")
            if cell_name == "M4" and isinstance(error, m4_support().CacheAllowanceExceeded):
                result["status"] = "cache_allowance_exceeded"
            result["failure"] = {"phase": phase, "type": type(error).__name__}
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
        publish_result(output, json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("plan", "inspect-runtime", "run"))
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cell", default="M1")
    parser.add_argument("--repetition", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        plan = artifacts.load_plan()
        if args.operation == "plan":
            result = {"status": "unexecuted", "plan_sha256": artifacts.PLAN_SHA256,
                      "scripts_sha256": source_identity(args.cell), "cells": plan["cells"],
                      "admission_fields": sorted(ADMISSION_KEYS), "device_fields": sorted(DEVICE_KEYS),
                      "runtime_identity": "inspect-runtime in the separately installed pinned environment",
                      "unknowns": plan["retained_unknowns"]}
            if args.cell == "M4":
                result.update(admission_version=m4_support().SCHEMA,
                              device_fields=sorted(DEVICE_KEYS | {"gpu_cache_allowance_bytes"}),
                              cache_profile=dict(m4_support().PROFILE),
                              optional_backend={m4_support().DISTRIBUTION: m4_support().VERSION})
            print(json.dumps(result, indent=2))
            return 0
        if args.operation == "inspect-runtime":
            cell_spec(plan, args.cell)
            print(json.dumps(runtime_identity(plan, args.cell), indent=2))
            return 0
        cell_spec(plan, args.cell)
        if any(value is None for value in (args.model_dir, args.admission, args.output)):
            raise ValueError("run requires local artifacts, concrete external admission and a fresh output")
        result = run(args.model_dir, args.admission, args.output, args.cell, args.repetition)
        print(json.dumps({"status": result["status"], "cell": result["cell"],
                          "repetition": result["repetition"], "failure": result.get("failure")}))
        return 0 if result["status"] == "measurement_completed_pending_evidence_review" else 1
    except NotImplementedError:
        print(json.dumps({"status": "unsupported", "reason": "selected cell or runtime is unsupported; no substitute or multi-GPU execution"}))
        return 0
    except (ValueError, OSError, RuntimeError, importlib.metadata.PackageNotFoundError) as error:
        print(json.dumps({"status": "operation_error", "error_type": type(error).__name__,
                          "reason": "operation failed; inspect retained attempt/result before any retry"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
