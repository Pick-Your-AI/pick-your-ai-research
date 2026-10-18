"""Supplemental GM1 Granite3.1 measurement under the unchanged 2026-10-16 protocol.

Import has no ML dependency. Runtime packages and model artifacts stay outside Git.
See research/market/measurements/mr09-granite31-protocol-2026-10-16.md before execution.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
import urllib.request


MODEL_ID = "ibm-granite/granite-3.1-1b-a400m-instruct"
REVISION = "0da7a48b0276d500ce5922fd2b33944091fc6c09"
MODEL_FILES = ("config.json", "generation_config.json", "tokenizer.json",
               "tokenizer_config.json", "special_tokens_map.json", "model.safetensors")
GIB = 2 ** 30


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def errors(estimate: int | float, measured: int | float) -> dict:
    """For already semantically comparable positive measurements only."""
    if not math.isfinite(estimate) or not math.isfinite(measured):
        raise ValueError("finite values required")
    if estimate < 0 or measured <= 0:
        raise ValueError("nonnegative estimate and positive measurement required")
    signed = estimate - measured
    return {"signed_bytes": signed, "absolute_bytes": abs(signed),
            "signed_relative_percent": 100 * signed / measured}


def kv_payload_bytes(layers: int, kv_heads: int, head_dim: int,
                     cache_tokens: int, active_sequences: int, element_bytes: int) -> int:
    values = (layers, kv_heads, head_dim, cache_tokens, active_sequences, element_bytes)
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in values):
        raise ValueError("positive integer geometry required")
    return 2 * math.prod(values)


def classify_failure(error: Exception, phase: str, is_oom: bool = False) -> str:
    if is_oom:
        return "OOM_" + phase
    if isinstance(error, (ImportError, NotImplementedError)):
        return "unsupported"
    return "runtime_error"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sanitized(value, args):
    """Retain executable/package pins while avoiding personal filesystem locators."""
    replacements = [(str(args.model_dir.resolve()), "$MODEL_DIR"),
                    (str(Path(__file__).resolve().parents[1]), "$REPO"),
                    (str(Path(sys.executable).resolve()), "$CUDA_PYTHON"),
                    (str(Path.home()), "$USER_HOME")]
    if isinstance(value, str):
        for old, new in replacements:
            value = value.replace(old, new).replace(old.replace("\\", "/"), new)
        return value
    if isinstance(value, list):
        return [sanitized(item, args) for item in value]
    if isinstance(value, dict):
        return {key: sanitized(item, args) for key, item in value.items()}
    return value


def prepare(model_dir: Path) -> dict:
    """Download only the pinned protocol whitelist into a fresh external directory."""
    repo = Path(__file__).resolve().parents[1]
    resolved = model_dir.resolve()
    if resolved == repo or repo in resolved.parents:
        raise ValueError("model artifacts must remain outside the repository")
    model_dir.mkdir(parents=True, exist_ok=True)
    if any(model_dir.iterdir()):
        raise ValueError("use a fresh artifact directory; existing files are never overwritten")
    artifacts = []
    expected_weight_size = 2_669_283_096
    expected_weight_hash = "ac02591061f1344027a7e7b11dbb4143f75f166c47dc09b742f5de3ab1dde1d1"
    for filename in MODEL_FILES:
        url = f"https://huggingface.co/{MODEL_ID}/resolve/{REVISION}/{filename}"
        path = model_dir / filename
        partial = path.with_suffix(path.suffix + ".part")
        limit = expected_weight_size if filename == "model.safetensors" else 10 * 1024**2
        with urllib.request.urlopen(url, timeout=90) as response, partial.open("wb") as out:
            size = 0
            while block := response.read(1024**2):
                size += len(block)
                if size > limit:
                    raise ValueError("artifact exceeds pinned weight size or small-file cap")
                out.write(block)
        checksum = sha256_file(partial)
        if filename == "model.safetensors" and (
                size != expected_weight_size or checksum != expected_weight_hash):
            raise ValueError("weight size/hash differs from pinned publisher metadata")
        partial.replace(path)
        artifacts.append({"file": filename, "bytes": size, "sha256": checksum,
                          "source_url": url})
    manifest = {"model_id": MODEL_ID, "revision": REVISION, "license": "Apache-2.0",
                "license_source_url": f"https://huggingface.co/{MODEL_ID}/blob/{REVISION}/README.md",
                "reuse": "publisher labels Apache-2.0; weights not redistributed",
                "publisher": "IBM Granite", "access_date": "2026-10-18",
                "evidence_class": "pinned publisher metadata plus local hash/size checks",
                "model_format": "safetensors", "artifacts": artifacts}
    write_json(model_dir / "mr09-manifest.json", manifest)
    return manifest


def measurement(args: argparse.Namespace) -> dict:
    result = {"classification": "independent project measurement; bounded configuration",
              "cell": args.cell, "repetition": args.repetition,
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "command_argv": [str(value) for value in sys.argv],
              "model_id": MODEL_ID, "revision": REVISION, "status": "unexecuted",
              "phases": [], "error_comparisons": [],
              "configuration": {"weight_dtype": "bfloat16", "weight_quantization": "none",
                                "kv_cache": args.cache, "prompt_tokens_per_sequence": args.prompt_tokens,
                                "decode_forwards_per_sequence": args.decode_tokens,
                                "active_sequences": args.active_sequences, "queued_requests": 0,
                                "seed": 6109, "attention_backend": "sdpa", "graph_capture": False,
                                "compile": False, "device_map": {"": "cuda:0"}, "offload": False,
                                "tensor_parallel_size": 1, "pipeline_parallel_size": 1},
              "script_sha256": sha256_file(Path(__file__))}
    protocol = Path(__file__).resolve().parents[1] / "research/market/measurements/mr09-granite31-protocol-2026-10-16.md"
    result["protocol_sha256"] = sha256_file(protocol)
    phase = "discovery"
    torch = None
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache, QuantizedCache

        result["environment"] = {"python": sys.version, "torch": torch.__version__,
                                 "cuda_build": torch.version.cuda,
                                 "packages": {name: importlib.metadata.version(name) for name in
                                              ("transformers", "accelerate", "safetensors", "numpy",
                                               "huggingface-hub", "tokenizers")}}
        if args.cache == "int4":
            result["environment"]["packages"]["optimum-quanto"] = importlib.metadata.version("optimum-quanto")
        if not torch.cuda.is_available():
            raise NotImplementedError("CUDA unavailable; no CPU substitution")
        if torch.cuda.device_count() != 1:
            raise NotImplementedError("protocol requires exactly one visible device")
        torch.cuda.init()
        torch.cuda.synchronize()
        free, total = torch.cuda.mem_get_info()
        cap = 3 * GIB
        result["hardware"] = {"gpu": torch.cuda.get_device_name(0), "count": 1,
                               "properties": str(torch.cuda.get_device_properties(0)),
                               "initial_driver_free_bytes": free, "driver_total_bytes": total,
                               "process_allocator_limit_bytes": cap,
                               "allocator_backend": torch.cuda.get_allocator_backend()}
        smi = subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,memory.free,driver_version,pci.bus_id",
                              "--format=csv"], capture_output=True, text=True, timeout=30)
        result["hardware"]["nvidia_smi_csv"] = smi.stdout.strip()
        if free < 4 * GIB:
            result["status"] = "unexecuted"
            result["reason"] = "preflight requires at least 4 GiB device free; preserve unrelated workloads"
            return result
        torch.cuda.set_per_process_memory_fraction(cap / total, 0)
        torch.manual_seed(6109)

        def snapshot(name: str, started: float) -> None:
            torch.cuda.synchronize()
            mem_free, mem_total = torch.cuda.mem_get_info()
            result["phases"].append({"phase": name, "elapsed_seconds": time.perf_counter() - started,
                "current_allocated_bytes": torch.cuda.memory_allocated(),
                "current_reserved_bytes": torch.cuda.memory_reserved(),
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
                "driver_free_bytes": mem_free, "driver_total_bytes": mem_total})

        def begin(name: str) -> float:
            nonlocal phase
            phase = name
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            return time.perf_counter()

        start = begin("baseline")
        snapshot("baseline", start)
        manifest_path = args.model_dir / "mr09-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["model_id"] != MODEL_ID or manifest["revision"] != REVISION:
            raise ValueError("artifact manifest model/revision mismatch")
        for item in manifest["artifacts"]:
            if sha256_file(args.model_dir / item["file"]) != item["sha256"]:
                raise ValueError("artifact checksum mismatch: " + item["file"])
        result["artifact_manifest"] = manifest
        phase = "loading"
        tokenizer = AutoTokenizer.from_pretrained(args.model_dir, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(args.model_dir, local_files_only=True,
                                                    dtype=torch.bfloat16, attn_implementation="sdpa",
                                                    use_safetensors=True, trust_remote_code=False)
        model.eval()
        start = begin("loading")
        model.to("cuda:0")
        snapshot("loading", start)
        result["model_geometry"] = {"layers": model.config.num_hidden_layers,
                                     "kv_heads": model.config.num_key_value_heads,
                                     "head_dim": model.config.hidden_size // model.config.num_attention_heads,
                                     "max_position_embeddings": model.config.max_position_embeddings,
                                     "actual_unique_parameter_elements": sum(p.numel() for p in model.parameters()),
                                     "actual_parameter_payload_bytes": sum(p.numel() * p.element_size() for p in model.parameters())}
        words = "The red bird rests near a quiet tree. Water flows past green fields. "
        tokens = tokenizer.encode(words, add_special_tokens=False)
        prompt = (tokens * ((args.prompt_tokens + len(tokens) - 1) // len(tokens)))[:args.prompt_tokens]
        result["workload"] = {"text": words, "add_special_tokens": False,
                              "prompt_token_ids_sha256": hashlib.sha256(json.dumps(prompt).encode()).hexdigest(),
                              "generation": "greedy argmax, no EOS early stop; only counters retained"}
        input_ids = torch.tensor([prompt] * args.active_sequences, dtype=torch.long, device="cuda")

        def new_cache():
            if args.cache == "int4":
                return QuantizedCache(backend="quanto", config=model.config, nbits=4,
                                      axis_key=0, axis_value=0, q_group_size=64, residual_length=128)
            return DynamicCache(config=model.config)

        def int4_cache_payload(cache):
            seen = set()
            categories = {"packed_bytes": 0, "scale_bytes": 0, "shift_bytes": 0, "residual_bytes": 0}

            def add(tensor, category):
                # Quanto wrapper tensors expose logical sizes, not physical packing.
                # Descend into PackedTensor._data rather than counting its public numel.
                if hasattr(tensor, "_data"):
                    add(tensor._data, category)
                    return
                storage = tensor.untyped_storage()
                key = (str(tensor.device), storage.data_ptr(), storage.nbytes())
                if key not in seen:
                    seen.add(key)
                    categories[category] += storage.nbytes()

            for layer in cache.layers:
                for residual in (layer.keys, layer.values):
                    add(residual, "residual_bytes")
                for quantized in (layer._quantized_keys, layer._quantized_values):
                    add(quantized._data, "packed_bytes")
                    add(quantized._scale, "scale_bytes")
                    add(quantized._shift, "shift_bytes")
            return {**categories, "total_physical_storage_bytes": sum(categories.values()),
                    "method": "unique physical backing storages of Quanto packed data/scales/shifts plus BF16 residual; no workspace/pool"}

        with torch.inference_mode():
            start = begin("warmup")
            warm_cache = new_cache()
            warm = model(input_ids=input_ids[:, :64], past_key_values=warm_cache,
                         use_cache=True, logits_to_keep=1)
            warm_next = warm.logits[:, -1].argmax(dim=-1, keepdim=True)
            warm = model(input_ids=warm_next, past_key_values=warm_cache,
                         use_cache=True, logits_to_keep=1)
            snapshot("warmup", start)
            del warm, warm_cache, warm_next
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            result["warmup_reset"] = "released own outputs/cache, synchronize then empty_cache before prefill; weights preserved"
            cache = new_cache()
            start = begin("prefill")
            output = model(input_ids=input_ids, past_key_values=cache, use_cache=True, logits_to_keep=1)
            next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
            snapshot("prefill", start)
            del output
            if args.cache == "bf16":
                observed = sum(layer.keys.numel() * layer.keys.element_size() +
                               layer.values.numel() * layer.values.element_size() for layer in cache.layers)
                geometry = result["model_geometry"]
                estimate = kv_payload_bytes(geometry["layers"], geometry["kv_heads"], geometry["head_dim"],
                                            args.prompt_tokens, args.active_sequences, 2)
                result["native_kv_prefill_payload"] = {"measured_bytes": observed, "estimated_bytes": estimate,
                    "target": "native KV tensor payload only; excludes workspace/allocator/runtime",
                    "estimator": "model-config dense KV formula, not competitor calibration",
                    "errors": errors(estimate, observed)}
            else:
                result["int4_kv_prefill_payload"] = int4_cache_payload(cache)
            start = begin("decode")
            for _ in range(args.decode_tokens):
                output = model(input_ids=next_token, past_key_values=cache, use_cache=True, logits_to_keep=1)
                next_token = output.logits[:, -1].argmax(dim=-1, keepdim=True)
                del output
            snapshot("decode", start)
            start = begin("steady_state")
            snapshot("steady_state", start)
            result["actual_tokens"] = {"prompt_per_sequence": input_ids.shape[1],
                                       "decode_forwards_per_sequence": args.decode_tokens,
                                       "greedy_tokens_produced_per_sequence": args.decode_tokens + 1,
                                       "cache_tokens_per_sequence": cache.get_seq_length(),
                                       "active_sequences": input_ids.shape[0], "queued_requests": 0,
                                       "note": "prefill predicts first token;32 decode forwards predict32 more;last prediction not in cache"}
            if args.cache == "bf16":
                result["native_kv_steady_payload_bytes"] = sum(layer.keys.numel() * layer.keys.element_size() +
                    layer.values.numel() * layer.values.element_size() for layer in cache.layers)
            else:
                result["int4_kv_steady_payload"] = int4_cache_payload(cache)
        result["status"] = "success"
    except Exception as error:
        is_oom = torch is not None and isinstance(error, torch.cuda.OutOfMemoryError)
        result["status"] = classify_failure(error, phase, is_oom)
        result["failure"] = {"phase": phase, "type": type(error).__name__, "message": str(error),
                             "traceback": traceback.format_exc(limit=7)}
    finally:
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--cell", choices=("GM1",), default="GM1")
    parser.add_argument("--repetition", type=int, default=1)
    parser.add_argument("--prompt-tokens", type=int, default=256)
    parser.add_argument("--decode-tokens", type=int, default=32)
    parser.add_argument("--active-sequences", type=int, choices=(1,), default=1)
    parser.add_argument("--cache", choices=("bf16",), default="bf16")
    args = parser.parse_args()
    if args.prompt_tokens != 256 or args.decode_tokens != 32 or args.repetition not in (1, 2, 3):
        parser.error("supplemental protocol permits GM1 prompt256/active1/BF16,decode32,repetitions1..3")
    if args.output.exists():
        parser.error("output exists; preserve observations and choose a fresh directory")
    preflight_path = args.model_dir.parent / f"granite31-preflight-{args.repetition}.json"
    subprocess.run([sys.executable, str(Path(__file__).with_name("mr09_preflight.py")),
                    "--profile", "granite31", "--temporary-dir", str(args.model_dir.parent),
                    "--output", str(preflight_path)], check=True)
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    guards = preflight.get("guards") if type(preflight) is dict else None
    required_guards = {"nvidia_smi_free_mib", "available_host_ram_bytes",
                       "temporary_volume_free_bytes"}
    if (type(guards) is not dict or set(guards) != required_guards
            or any(value is not True for value in guards.values())):
        raise RuntimeError("unchanged spare-capacity guards failed; no download/run")
    result = prepare(args.model_dir) if args.prepare else measurement(args)
    result["fresh_preflight"] = preflight
    if not args.prepare:
        result["dense_instrument_source_sha256"] = sha256_file(Path(__file__).with_name("mr09_measure.py"))
    write_json(args.output, sanitized(result, args))
    print(json.dumps({"output": str(args.output), "status": result.get("status", "prepared"),
                      "failure": result.get("failure")}, indent=2))
    return 0 if result.get("status", "prepared") in ("success", "prepared", "unsupported", "unexecuted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
