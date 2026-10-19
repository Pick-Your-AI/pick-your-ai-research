"""Exact, uncalibrated inference-memory arithmetic for research scenarios.

This helper models post-quant resident weights, a specified full-attention KV
component, and explicit overhead/buffer assumptions for ONE model replica. It
does not estimate a complete runtime peak, admit a build, recommend a device
count, or emit a ResourceEstimate. Recurrent/SSM state, host RAM, latency,
adapters, other workloads and actual placement support remain unknown.

Supply all five cache fields, or explicitly choose the named Qwen example from
``sizing_examples.py``. Context is the reserved prompt-plus-output envelope per
admitted sequence; concurrency counts independent resident sequences, including
beams/parallel continuations. No prefix sharing, eviction or allocated-pool
savings are inferred. Other cache architectures need a different derivation.

Bytes and counts require Python ints (not bools or integer-looking floats).
Dimensionless ratios and GB/GiB quantities accept finite Decimal, Fraction or
int values. All returned numeric arithmetic is exact int/Fraction; decimal GB
is bytes/10**9 and GiB is bytes/2**30. No float/string coercion is performed.

Multiple devices describe ONLY a hypothetical joint partition of weights, KV
and transfer buffers by explicit payload fractions. Every device keeps its own
runtime-overhead copy. This is not an implementation of TP/PP/EP/DP or proof
that a runtime can realize those fractions. The aggregate payload quotient is
a lower bound, never a sufficient device count. See gpu-compute.md and the
separate memory_screen.py for the required evidence/reserve/domain boundaries.
"""

from decimal import Decimal
from fractions import Fraction
import json


GB = 10**9
GIB = 2**30
QWEN_EXAMPLE = "qwen2.5-7b-bf16-block16"
# Same explicit example as sizing_examples.py; this is not a generic fallback.
# Model revision: d1e200fcf95ef0d4326873ddf63e5562d5f1fdbb (gpu-compute.md C11).
# The 16-token block and workload/domain choices remain scenario assumptions.
_QWEN_GEOMETRY = (28, 4, 128, 2, 16)
_GEOMETRY_FIELDS = ("layers", "kv_heads", "head_dim", "kv_element_bytes", "block_tokens")


def _integer(name, value, *, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}, without coercion")
    return value


def _quantity(name, value, *, positive=False):
    if type(value) is int:
        result = Fraction(value)
    elif isinstance(value, Decimal) and value.is_finite():
        result = Fraction(value)
    elif isinstance(value, Fraction):
        result = value
    else:
        raise ValueError(f"{name} must be a finite int, Decimal or Fraction")
    if result < 0 or (positive and result == 0):
        domain = "positive" if positive else "nonnegative"
        raise ValueError(f"{name} must be {domain}")
    return result


def _geometry(example, supplied):
    if example is not None:
        if type(example) is not str or example != QWEN_EXAMPLE:
            raise ValueError("geometry_example must name the supported Qwen example")
        if any(value is not None for value in supplied):
            raise ValueError("geometry_example cannot be combined with explicit geometry")
        return dict(zip(_GEOMETRY_FIELDS, _QWEN_GEOMETRY))
    if any(value is None for value in supplied):
        raise ValueError("complete explicit geometry or geometry_example is required")
    return {name: _integer(name, value, minimum=1)
            for name, value in zip(_GEOMETRY_FIELDS, supplied)}


def _partition(n_devices, fractions):
    _integer("n_devices", n_devices, minimum=1)
    if fractions is None and n_devices == 1:
        return (Fraction(1),)
    if not isinstance(fractions, (tuple, list)) or len(fractions) != n_devices:
        raise ValueError("device_payload_fractions must contain one share per device")
    shares = tuple(_quantity(f"device_payload_fractions[{i}]", value, positive=True)
                   for i, value in enumerate(fractions))
    if sum(shares) != 1:
        raise ValueError("device_payload_fractions must sum exactly to one")
    return shares


def size_model(total_size_bytes, quant, *, ctx, concurrency, card_vram_gb,
               runtime_overhead_gib, transfer_buffer_ratio,
               geometry_example=None, layers=None, kv_heads=None, head_dim=None,
               kv_element_bytes=None, block_tokens=None, is_moe=False,
               offload_policy="none", offloaded_expert_bytes=None,
               n_devices=1, device_payload_fractions=None):
    """Return a bounded arithmetic scenario, with admission always unknown.

    total_size_bytes is an asserted post-quant resident tensor byte count, not
    a parameter count or proof that a file loads without repacking. quant is an
    opaque nonempty label; it never multiplies or divides those bytes again.

    With no offload, all MoE weights remain resident, including inactive
    experts. experts_to_cpu requires an explicitly asserted aggregate expert
    byte amount no larger than total_size_bytes. It does not invent equal
    per-expert sizes, select experts, or establish host/transfer feasibility.

    Let P = resident weights + modeled KV + assumed transfer buffers and H be
    the explicit per-device overhead. Device i models share[i]*P + H. Every
    omitted term remains unknown; an arithmetic capacity excess is useful,
    but its absence is not an admitted fit or a measured upper bound. The
    payload lower bound ceil(P/card_capacity) excludes per-device overhead,
    placement, reserve and unmodeled state. It need not be sufficient.
    """
    total = _integer("total_size_bytes", total_size_bytes)
    context = _integer("ctx", ctx, minimum=1)
    sequences = _integer("concurrency", concurrency, minimum=1)
    if type(quant) is not str or not quant.strip():
        raise ValueError("quant must be a nonempty label for the supplied post-quant bytes")
    if type(is_moe) is not bool:
        raise ValueError("is_moe must be bool")
    if offload_policy not in ("none", "experts_to_cpu"):
        raise ValueError("offload_policy must be none or experts_to_cpu")
    if offload_policy == "none":
        if offloaded_expert_bytes is not None:
            raise ValueError("offloaded_expert_bytes requires experts_to_cpu")
        offloaded = 0
    else:
        if not is_moe:
            raise ValueError("experts_to_cpu requires is_moe=True")
        offloaded = _integer("offloaded_expert_bytes", offloaded_expert_bytes)
        if offloaded > total:
            raise ValueError("offloaded_expert_bytes must not exceed total_size_bytes")

    geometry = _geometry(geometry_example, (layers, kv_heads, head_dim,
                                           kv_element_bytes, block_tokens))
    shares = _partition(n_devices, device_payload_fractions)
    capacity_gb = _quantity("card_vram_gb", card_vram_gb, positive=True)
    overhead = _quantity("runtime_overhead_gib", runtime_overhead_gib) * GIB
    buffer_ratio = _quantity("transfer_buffer_ratio", transfer_buffer_ratio)
    block = geometry["block_tokens"]
    reserved_tokens = ((context + block - 1) // block) * block * sequences
    cache = (2 * geometry["layers"] * geometry["kv_heads"] * geometry["head_dim"]
             * geometry["kv_element_bytes"] * reserved_tokens)
    resident_weights = total - offloaded
    buffers = buffer_ratio * (resident_weights + cache)
    payload = resident_weights + cache + buffers
    per_device = tuple(share * payload + overhead for share in shares)
    pool = sum(per_device)
    payload_quotient = payload / (capacity_gb * GB)
    lower_bound = -(-payload_quotient.numerator // payload_quotient.denominator)

    return {
        "classification": "uncalibrated arithmetic scenario; no runtime measurement",
        "admission": "unknown",
        "geometry": geometry,
        "geometry_example": geometry_example,
        "context_tokens_per_sequence": context,
        "assumed_admitted_independent_sequences": sequences,
        "rounded_reserved_tokens": reserved_tokens,
        "quant": quant,
        "offload_policy": offload_policy,
        "post_quant_weight_bytes": total,
        "offloaded_expert_bytes": offloaded,
        "resident_weight_bytes": resident_weights,
        "modeled_attention_kv_bytes": cache,
        "assumed_transfer_buffer_bytes": buffers,
        "assumed_runtime_bytes_per_device": overhead,
        "assumed_devices_per_replica": n_devices,
        "device_payload_fractions": shares,
        "modeled_per_device_bytes": per_device,
        "modeled_pool_vram_gb": pool / GB,
        "modeled_peak_per_device_vram_gb": max(per_device) / GB,
        "card_vram_gb": capacity_gb,
        "capacity_basis": "caller-supplied decimal GB; allocatable/free-memory bounds unverified",
        "modeled_bytes_exceed_card_capacity": tuple(
            value > capacity_gb * GB for value in per_device),
        "modeled_payload_device_lower_bound": lower_bound,
        "lower_bound_scope": "modeled payload only; not sufficient devices or topology approval",
        "topology_assumption": "joint weight/KV/buffer partition; overhead replicated per device",
        "unmodeled_recurrent_state_bytes": None,
        "host_ram_bytes": None,
        "latency_ms": None,
        "runtime_peak_allocated_bytes": None,
        "runtime_peak_reserved_bytes": None,
        "limitations": (
            "Only the specified full-attention KV component is modeled; recurrent/SSM state is unknown.",
            "Runtime overhead and transfer buffers are assumptions without a coverage/error guarantee.",
            "Adapters, other workloads, real placement and replicated KV/workspaces are unresolved.",
            "No reserve, confidence eligibility, free-memory bound or runtime support is established.",
        ),
    }


def capacity_sensitivity(per_device_modeled_bytes, *, reserve_fraction):
    """Apply one explicit hypothetical reserve, separately from live arithmetic.

    Inputs must be modeled live bytes BEFORE this reserve, not an already reduced
    engine pool. This helper cannot verify that assertion. It returns a separate
    scenario, not a confidence interval, measured upper bound or admission. Vary
    the overhead/buffer assumptions through separate size_model calls as needed.
    """
    if not isinstance(per_device_modeled_bytes, (tuple, list)) or not per_device_modeled_bytes:
        raise ValueError("per_device_modeled_bytes must be a nonempty list or tuple")
    live = tuple(_quantity(f"per_device_modeled_bytes[{i}]", value)
                 for i, value in enumerate(per_device_modeled_bytes))
    reserve = _quantity("reserve_fraction", reserve_fraction)
    if reserve >= 1:
        raise ValueError("reserve_fraction must be less than one")
    required = tuple(value / (1 - reserve) for value in live)
    return {
        "classification": "hypothetical sensitivity; not a measured or confidence bound",
        "capacity_basis": "before_reserve",
        "reserve_fraction": reserve,
        "scenario_required_gb_per_device": tuple(value / GB for value in required),
        "scenario_required_pool_gb": sum(required) / GB,
    }


def reported_scenario_demonstrations():
    """Three unverified input demonstrations; no fitted measurement comparison.

    The model/context/byte figures are retained from contributor snapshot
    63aac7598a441f364b7701fa5d86e9c8cb47a65a. Exact model/build pins and eligible
    peak-allocated/reserved records were not supplied. The reported M1/M2/M3
    process-memory samples are NOT used as calibration targets or acceptance
    tests. The numerical overhead, buffers and M3 equal partition below are
    hypothetical assumptions, not inferred from those observations. M2's KV
    is only its asserted attention component; its recurrent state is unknown.
    """
    common = dict(quant="Q4_K_M", concurrency=1, card_vram_gb=24,
                  runtime_overhead_gib=3, transfer_buffer_ratio=Decimal("0.10"),
                  kv_element_bytes=2, block_tokens=16)
    dense = dict(total_size_bytes=2_491_323_904, ctx=2048,
                 layers=36, kv_heads=8, head_dim=128)
    scenarios = (
        ("M1_dense_fit", dense),
        ("M2_moe_offload", dict(total_size_bytes=22_313_814_528, ctx=1024,
                                layers=10, kv_heads=2, head_dim=256, is_moe=True,
                                offload_policy="experts_to_cpu",
                                offloaded_expert_bytes=19_769_655_296)),
        ("M3_multigpu", dict(**dense, n_devices=2,
                             device_payload_fractions=(Decimal("0.5"), Decimal("0.5")))),
    )
    return [{
        "reported_scenario_id": label,
        "input_basis": "unverified contributor-supplied scenario; not a pinned runtime artifact",
        "assumption_basis": (
            "24 decimal GB/card, 3 GiB/device, 10% payload buffer, 16-token blocks; hypothetical only"
        ),
        "model_artifact_pin": None,
        "engine_build_pin": None,
        "eligible_peak_measurement_pair": False,
        "arithmetic": size_model(**common, **inputs),
    } for label, inputs in scenarios]


def main():
    # JSON strings preserve exact rational quantities; no hardware or file I/O.
    print(json.dumps(reported_scenario_demonstrations(), indent=2, default=str))


if __name__ == "__main__":
    main()
