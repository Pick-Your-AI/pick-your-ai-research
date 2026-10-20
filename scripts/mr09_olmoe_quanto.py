"""Fixed, prospective OLMoE M4 Quanto profile and physical-storage observer.

Only standard-library modules are imported at module load. The optional backend
is imported exclusively by load_backend during an admitted measurement. Runtime
metadata/source inspection performs no ML import, installation or model access.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.metadata
import os
from pathlib import Path
import stat

import mr09_olmoe_artifacts as artifacts

SCHEMA = "mr09-olmoe-run-admission/v2"
SCRIPT = "mr09_olmoe_quanto.py"
DISTRIBUTION = "optimum-quanto"
VERSION = "0.2.7"
TRANSFORMERS_COMMIT = "08810b1e278938278c50153ee1edfd7a20a759da"
QUANTO_COMMIT = "089d86ef7954996440ca770b678be353d7a7d6cd"
PROFILE = {"backend": "quanto", "nbits": 4, "axis_key": 0, "axis_value": 0,
           "q_group_size": 64, "residual_length": 128}
CELL = {"id": "M4", "prompt_tokens": 2048, "decode_forwards": 32,
        "active_sequences": 1, "kv_cache": "int4_if_supported",
        "terminal_cache_positions_per_sequence": 2080,
        "derived_bf16_kv_payload_bytes": None,
        "derived_weights_plus_kv_floor_bytes": None, "status": "unexecuted"}
# Selected upstream source bytes checked 2026-10-20. These pins cover the exact
# observed cache/layout path; the distribution RECORD is not a full binary audit.
# URLs are the immutable commit/path links in the companion M4 appendix.
SOURCE_FILES = (
    ('transformers/cache_utils.py', 60432,
     '6c123bbe3d23500462f0b617119a8231aa054b6d5475b295443a45f34466e6bc'),
    ('optimum/quanto/tensor/weights/quantization.py', 3076,
     '46d97e12f0634ab6b731e7728b398b6f70652c1735a89f3b28480f991b438448'),
    ('optimum/quanto/tensor/weights/qbits.py', 12583,
     '67bce0cb3576b8926a8267ef94e16fd0b20dcc5011d7f9eeff360ce2632b580f'),
    ('optimum/quanto/tensor/qbits.py', 2190,
     '867c4b6fd7087e94f8aed2892f83d082069a841c55dbbb5614eaf40b7243d154'),
    ('optimum/quanto/tensor/packed.py', 6193,
     '40094ce1e5d08b46ba475f028a06b09adfb5c7eaf8f6d237af37653eee0a2b19'),
    ('optimum/quanto/tensor/grouped.py', 2183,
     'be70d4b2484bd903d2ebad587087df423218d31031d466d26b4005d14f0f8c83'),
    ('optimum/quanto/tensor/optimizers/affine_optimizer.py', 2473,
     'bc1743b65f091a428a0d80b79854c51900baa35d6345eb86792229a2f5deba4e'),
    ('optimum/quanto/tensor/optimizers/max_optimizer.py', 1312,
     '62e8610a2f54d6c468740ef45d217dde69c036caf9a01b8a8d87e49306d87163'),
    ('optimum/quanto/tensor/qtensor.py', 3251,
     '1b38673bda1ef17e78af24f07a2206a5e309f8f3dbeb3b73d1d05c535a9ed788'),
    ('optimum/quanto/__init__.py', 764,
     '81dacefb245fd8ff2413d27a037cf30e62ba9c09eb21f1b4f1ab2978275bc00f'),
    ('optimum/quanto/tensor/__init__.py', 813,
     '2224cb2ea2b6a1636bcb9267d663bc935e36194fcf7d11b4bf5c3a34b69f284c'),
    ('optimum/quanto/tensor/weights/__init__.py', 71,
     'a04f71e13906cf7a2b3927de1b09ceb4633a065376ef7bb3d7a2a2f88a158db4'),
    ('optimum/quanto/tensor/optimizers/__init__.py', 789,
     '488423437ecc6c748dd7bd5d86e9a0483393f25f763cfc57ea5fc204a4c15890'),
    ('optimum/quanto/tensor/qtype.py', 1931,
     'd5ead57e3545fd8714a6147878e99105dd431c7149d003b0a4c9e1978a69915c'),
    ('optimum/quanto/library/quantize.py', 3047,
     '9270c2de9dbe5ec8b1446523951908b604552b5ee2dc2d5b247aea07cd14194f'),
)


class CacheLayoutError(NotImplementedError):
    """The observed cache does not have the selected physical layout."""


class CacheAllowanceExceeded(ValueError):
    """A retained live-cache sample exceeds the explicitly reviewed allowance."""


def validate_cell(cell: dict) -> None:
    # Typed JSON equality preserves the original nulls and fixed workload.
    import json
    if json.dumps(cell, sort_keys=True, allow_nan=False) != json.dumps(CELL, sort_keys=True):
        raise ValueError("the fixed OLMoE M4 cell is required")


def required_capacity(plan: dict, device: dict) -> int:
    allowance = device.get("gpu_cache_allowance_bytes")
    if type(allowance) is not int or not 0 < allowance < 2 ** 64:
        raise ValueError("M4 requires an explicit positive integer cache allowance")
    return (plan["totals"]["tensor_payload_bytes"] + allowance
            + device["gpu_workspace_allowance_bytes"])


def _source_digest(path: Path, expected_bytes: int, expected_sha: str) -> str:
    """Read one bounded, unchanged regular source file; never follow a FIFO swap."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size != expected_bytes:
        raise ValueError("selected M4 source length/type mismatch")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags | getattr(os, "O_NONBLOCK", 0))
    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
                value.st_mtime_ns, value.st_ctime_ns)
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if identity(before) != identity(opened):
            raise ValueError("selected M4 source changed before read")
        raw = stream.read(expected_bytes + 1)
        after = os.fstat(stream.fileno())
    if (identity(opened) != identity(after) or identity(after) != identity(path.lstat())
            or len(raw) != expected_bytes):
        raise ValueError("selected M4 source changed during read")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha:
        raise ValueError("selected M4 source differs from pinned upstream")
    return actual


def runtime_identity() -> dict:
    """Inspect the optional installed backend without importing ML packages."""
    quanto = importlib.metadata.distribution(DISTRIBUTION)
    if quanto.version != VERSION:
        raise ValueError("selected optimum-quanto 0.2.7 required")
    records = [f for f in (quanto.files or ()) if str(f).endswith(".dist-info/RECORD")]
    if len(records) != 1:
        raise ValueError("one installed optimum-quanto RECORD required")
    transformers = importlib.metadata.distribution("transformers")
    sources = {}
    for name, size, digest in SOURCE_FILES:
        distribution = transformers if name.startswith("transformers/") else quanto
        sources[name] = _source_digest(Path(distribution.locate_file(name)), size, digest)
    return {"distribution": DISTRIBUTION, "version": quanto.version,
            "distribution_record_sha256": artifacts.sha256_file(Path(quanto.locate_file(records[0]))),
            "source_files_sha256": sources, "cache_profile": dict(PROFILE)}


@dataclass(frozen=True)
class Backend:
    cache_type: type
    layer_type: type
    weight_type: type
    packed_type: type
    qint4: object


def load_backend() -> Backend:
    """Called only after concrete admission, capacity screens and ML environment."""
    from transformers.cache_utils import QuantizedCache, QuantoQuantizedLayer
    from optimum.quanto.tensor.weights.qbits import WeightQBitsTensor
    from optimum.quanto.tensor.packed import PackedTensor
    from optimum.quanto import qint4
    return Backend(QuantizedCache, QuantoQuantizedLayer, WeightQBitsTensor, PackedTensor, qint4)


def new_cache(backend: Backend, config):
    return backend.cache_type(config=config, **PROFILE)


def observe_cache(cache, torch, backend: Backend, phase: str, positions: int) -> dict:
    """Observe full unique ordinary leaf storages, never logical wrapper bytes.

    Only metadata is read on the two exact wrapper classes. Tensor operations,
    storage access and contiguity checks occur only after a plain Tensor type
    check. No dequantization, unpack, clone, device transfer or pointer output.
    """
    expected_positions = {"prefill": 2048, "post_decode": 2080}
    if phase not in expected_positions or type(positions) is not int or positions != expected_positions[phase]:
        raise CacheLayoutError("unsupported M4 observation phase or token count")
    if type(cache) is not backend.cache_type or type(getattr(cache, "layers", None)) is not list or len(cache.layers) != 16:
        raise CacheLayoutError("exact sixteen-layer Quanto cache required")
    if getattr(cache, "offloading", False) is not False:
        raise CacheLayoutError("offloaded cache is outside the selected M4 profile")
    residual_positions = positions - 2048
    residual_shape = (0,) if residual_positions == 0 else (1, 16, residual_positions, 128)
    logical_shape, grouped_shape = (1, 16, 2048, 128), (65536, 64)
    component_bytes = {name: 0 for name in ("packed_data", "scales", "shifts", "residual")}
    storage_counts = dict(component_bytes)
    references = dict(component_bytes)
    seen, addresses = {}, {}

    def selected_device(value):
        return value.device.type == "cuda" and value.device.index == 0

    def leaf(tensor, category, shape, dtype):
        if type(tensor) is not torch.Tensor:
            raise CacheLayoutError("ordinary tensor required for " + category)
        if (tuple(tensor.shape) != shape or tensor.dtype != dtype or not selected_device(tensor)
                or tensor.layout != torch.strided or not tensor.is_contiguous()):
            raise CacheLayoutError("unexpected plain tensor geometry/dtype/device for " + category)
        references[category] += 1
        storage = tensor.untyped_storage()
        size, pointer = storage.nbytes(), storage.data_ptr()
        offset, elements, width = tensor.storage_offset(), tensor.numel(), tensor.element_size()
        if (type(size) is not int or not 0 <= size < 2 ** 64
                or type(pointer) is not int or pointer < 0
                or storage.device.type != "cuda" or storage.device.index != 0
                or type(offset) is not int or offset < 0
                or (offset + elements) * width > size or (size > 0 and pointer == 0)):
            raise CacheLayoutError("invalid physical backing storage for " + category)
        if size == 0:
            return
        address = (storage.device.type, storage.device.index, pointer)
        if address in addresses and addresses[address] != size:
            raise CacheLayoutError("inconsistent backing extent at one live address")
        addresses[address] = size
        identity = (*address, size)
        if identity in seen:
            if seen[identity] != category:
                raise CacheLayoutError("unsupported backing alias across cache components")
            return
        seen[identity] = category
        component_bytes[category] += size
        storage_counts[category] += 1

    for layer in cache.layers:
        if (type(layer) is not backend.layer_type or getattr(layer, "is_initialized", False) is not True
                or type(getattr(layer, "cumulative_length", None)) is not int or layer.cumulative_length != positions):
            raise CacheLayoutError("every layer must capture the selected logical token count")
        for key, expected in PROFILE.items():
            if key != "backend" and (type(getattr(layer, key, None)) is not int or getattr(layer, key) != expected):
                raise CacheLayoutError("every layer must retain the selected Quanto profile")
        if getattr(layer, "qtype", None) is not backend.qint4:
            raise CacheLayoutError("every layer must use the selected qint4 type")
        for name in ("keys", "values"):
            quantized = getattr(layer, "_quantized_" + name, None)
            if type(quantized) is not backend.weight_type:
                raise CacheLayoutError("exact WeightQBitsTensor layout required")
            if (tuple(quantized.shape) != logical_shape or quantized.dtype != torch.bfloat16
                    or not selected_device(quantized) or getattr(quantized, "_qtype", None) is not backend.qint4
                    or type(getattr(quantized, "_axis", None)) is not int or quantized._axis != 0
                    or type(getattr(quantized, "_group_size", None)) is not int or quantized._group_size != 64):
                raise CacheLayoutError("quantized logical shape/profile differs from M4 prefix")
            packed = getattr(quantized, "_data", None)
            if (type(packed) is not backend.packed_type or type(getattr(packed, "_bits", None)) is not int or packed._bits != 4
                    or tuple(packed.shape) != grouped_shape or packed.dtype != torch.uint8
                    or not selected_device(packed)):
                raise CacheLayoutError("exact grouped PackedTensor metadata required")
            leaf(getattr(packed, "_data", None), "packed_data", (32768, 64), torch.uint8)
            leaf(getattr(quantized, "_scale", None), "scales", (65536, 1), torch.bfloat16)
            leaf(getattr(quantized, "_shift", None), "shifts", (65536, 1), torch.bfloat16)
            leaf(getattr(layer, name, None), "residual", residual_shape, torch.bfloat16)
    return {"phase": phase, "status": "observed", "cache_tokens_per_sequence": positions,
            "validated_layers": 16, "validated_key_value_tensors": 32,
            "quantized_prefix_shape": list(logical_shape), "residual_shape": list(residual_shape),
            "component_bytes": component_bytes, "unique_backing_storages": storage_counts,
            "plain_tensor_references": references,
            "total_unique_backing_bytes": sum(component_bytes.values()),
            "scope": "whole unique live tensor backing allocations; excludes Python objects, transient workspace and allocator pools"}


def retain_observation(history: list, cache, torch, backend: Backend,
                       phase: str, positions: int, allowance: int) -> None:
    """Retain each observation before a budget stop or any later forward call."""
    try:
        sample = observe_cache(cache, torch, backend, phase, positions)
    except CacheLayoutError as error:
        history.append({"phase": phase, "status": "unsupported", "reason": str(error)})
        raise
    sample["reviewed_allowance_bytes"] = allowance
    sample["within_allowance"] = sample["total_unique_backing_bytes"] <= allowance
    history.append(sample)
    if not sample["within_allowance"]:
        raise CacheAllowanceExceeded("observed retained cache exceeds the reviewed allowance")
