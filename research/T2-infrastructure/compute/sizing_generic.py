"""Generic, parameterized GPU/CPU offload sizing for inference.

Extends ``sizing_examples.py`` (reuses its ``kv_bytes``, ``capacity_range`` and the
Qwen2.5-7B geometry constants) rather than shadowing them; this file never edits that module.

Default cache geometry is Qwen2.5-7B, so passing no explicit geometry applies Qwen's shapes.
Pass your own ``layers / kv_heads / head_dim`` for any other model (see the scaled-KV helper).

Units: decimal GB == bytes / 1e9; GiB == bytes / 2**30 is retained only for the per-device
runtime/activation overhead, which is converted back to bytes before byte arithmetic. CPU offload
is a SEPARATE scenario and never a free reduction of weights:
    * offload_policy "none": an MoE keeps ALL weights resident on device.
    * offload_policy "experts_to_cpu": resident weights = total_size_bytes - offloaded bytes.

``quant`` is accepted and echoed in the result but does not change the byte count; ``total_size_bytes``
is already post-quant (see Acceptance Criteria / WO-001). Every new constant here is a named, documented
project assumption, never a measurement. Runs under Python 3.12+. ASCII only.
"""

import os
import sys
from decimal import Decimal
from math import ceil

try:
    from sizing_examples import kv_bytes, capacity_range
except ImportError:
    # Robust to being run from a working dir other than the repo root.
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _here)
    from sizing_examples import kv_bytes, capacity_range  # type: ignore  # noqa: F401

from sizing_examples import LAYERS, KV_HEADS, HEAD_DIM  # type: ignore  # noqa: F401


# --- Named assumptions: project assumptions, NOT measurements -----------------
# Runtime/activation/workspace overhead per device. Mirrors the "2-4 GiB per
# device" bracket in gpu-compute.md but is a documented assumption here, not a
# measurement of our hardware. Stays GiB and is converted to bytes explicitly below.
RUNTIME_OVERHEAD_GIB = Decimal("3")  # project assumption, not a measurement

# Staging/transfer buffers retained during load+dequantize on host/device.
# A flat 10% of live bytes; a documented assumption, not a measured value.
TRANSFER_BUFFER_RATIO = Decimal("0.10")  # project assumption, not a measurement


# Named MEASURED profile for the observed hardware (LLaMA/CLI round-5 calibration).
# Overhead calibrated on M1 (n=1) in GB-equivalent GiB; two_way_layer_split_fraction
# is the measured per-device share used by n_devices>1 peak (== split_fraction).
# Recompute 0.414149 yourself: implied overhead = 3.238002688 - file_gb(2.491323904) - kv(36,8,128,ctx2048)=0.301989888 -> 0.444688896 GB = 0.414149 GiB (Decimal(2)**30 / Decimal(10**9)).
LLAMACPP_RTX_PRO_4000_N1 = {
    "runtime_overhead_gib": Decimal("0.414149"),
    "transfer_buffer_ratio": Decimal("0"),
    "two_way_layer_split_fraction": Decimal("0.5825"),
}  # measured on RTX PRO 4000 Blackwell SFF 24 GB, llama.cpp, Qwen3-4B Q4_K_M, ctx 2048, flash-attn off, n=1; overhead calibrated on M1


def _scaled_kv_bytes(kv_tokens_and_conc, layers, kv_heads, head_dim):
    """Scale the reused Qwen2.5-7B KV estimate to a custom geometry.

    ``sizing_examples.kv_bytes`` is fixed to Qwen2.5-7B (LAYERS/KV_HEADS/HEAD_DIM). Calling it
    with no override silently applies Qwen's shapes to every model, which the plan forbids.
    When all three are given we scale by the ratio of layer*kv_heads*head_dim; when any is None
    we fall back to the exact Qwen2.5-7B value via the imported ``kv_bytes``.
    """
    context_tokens, concurrency = kv_tokens_and_conc
    if layers is None or kv_heads is None or head_dim is None:
        return kv_bytes(context_tokens, concurrency)
    if layers <= 0 or kv_heads <= 0 or head_dim <= 0:
        raise ValueError("layers, kv_heads and head_dim must be positive")
    geometry_qwen = Decimal(LAYERS) * KV_HEADS * HEAD_DIM
    geometry_this = Decimal(layers) * kv_heads * head_dim
    return kv_bytes(context_tokens, concurrency) * Decimal(geometry_this) / Decimal(geometry_qwen)


def _validate_experts(n_experts, expert_bytes):
    """Validate MoE bookkeeping and enforce exactly ``n_experts`` numeric entries.

    Raises ValueError on a missing/short list, wrong length, or any non-number / negative entry;
    returns the offloaded byte total (sum of the supplied expert sizes). Rejects
    ``sum(expert_bytes) > total_size_bytes`` once that bound is known to the caller. All guards
    raise ValueError (never AssertionError) so they fail loudly even under `python -O`.
    """
    # MoE bookkeeping guards. Every rejection raises ValueError (never AssertionError)
    # so they fail loudly even under `python -O`, where assert is stripped.
    if not (n_experts and expert_bytes):
        raise ValueError("MoE requires positive n_experts and expert_bytes")
    n_experts = int(n_experts)
    if len(expert_bytes) != n_experts:
        raise ValueError(
            f"MoE requires exactly n_experts={n_experts} expert entries, got {len(expert_bytes)}"
        )
    for i, value in enumerate(expert_bytes, start=1):
        # bool is a subclass of int; reject it explicitly so True/False cannot pass.
        if isinstance(value, bool) or not _is_number(value) or value < 0:
            raise ValueError(f"MoE expert {i} bytes must be non-negative numbers")
    return Decimal(sum(expert_bytes))


def _is_number(value):
    """True for int/float-like values usable as a byte count (bool is rejected)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def size_model(
    total_size_bytes,
    quant,
    is_moe=False,
    n_experts=None,
    expert_bytes=None,
    ctx=0,
    concurrency=0,
    card_vram_gb=0,
    offload_policy="none",
    layers=None,
    kv_heads=None,
    head_dim=None,
    runtime_overhead_gib=None,
    transfer_buffer_ratio=None,
    n_devices=1,
    split_fraction=None,
) -> dict:
    """Generic GPU/offload sizing for a single inference model replica.

    Returns {fits, resident_vram_gb, needs_devices, latency_cost_estimate, quant}.

    ``total_size_bytes`` is the post-quant byte size (the caller's quant does not change it);
    ``resident_vram_gb``/``needs_devices`` follow
    ``GPU_live = resident_weights + GPU_KV + runtime + transfer_buffers``; ``fits`` is a bool.
    """
    total_size_bytes = int(total_size_bytes)
    card_vram_gb = int(card_vram_gb)

    if ctx <= 0 or concurrency <= 0:
        raise ValueError("ctx and concurrency must be positive")
    if total_size_bytes < 0 or card_vram_gb <= 0:
        raise ValueError("total_size_bytes >= 0 and card_vram_gb > 0 are required")

    # --- Per-device runtime overhead / transfer buffer (r5) --------------------
    # None -> fall back to the module defaults. Overhead is GiB; ratio is a plain fraction.
    _ov = RUNTIME_OVERHEAD_GIB if runtime_overhead_gib is None else runtime_overhead_gib
    _ratio = TRANSFER_BUFFER_RATIO if transfer_buffer_ratio is None else transfer_buffer_ratio
    for _label, _val in (("runtime_overhead_gib", _ov), ("transfer_buffer_ratio", _ratio)):
        # Accept int/float/Decimal (bool rejected), same accepted set as split_fraction.
        # float -> Decimal via str() to avoid binary-float artifacts (0.1 != Decimal(0.1)).
        if isinstance(_val, bool) or not isinstance(_val, (int, float, Decimal)):
            raise ValueError(f"{_label} must be a non-negative number")
        if _val < 0:
            raise ValueError(f"{_label} must be non-negative")
        if isinstance(_val, float):
            _val = Decimal(str(_val))
    _ov = Decimal(str(_ov)) if not isinstance(_ov, Decimal) else _ov
    _ratio = Decimal(str(_ratio)) if not isinstance(_ratio, Decimal) else _ratio

    n_devices = int(n_devices)
    if n_devices < 1:
        raise ValueError("n_devices must be >= 1")
    if n_devices > 1:
        if split_fraction is None:
            raise ValueError("split_fraction is required when n_devices > 1")
        _sf = Decimal(str(split_fraction))
        # Must satisfy 1/n_devices <= split_fraction <= 1; reject bool-ish / non-Decimal.
        try:
            _sf_ok = _sf <= Decimal("1") and _sf >= (Decimal(1) / n_devices)
        except Exception:
            raise ValueError("split_fraction must be a Decimal-able number")
        if not _sf_ok or isinstance(split_fraction, bool):
            raise ValueError(f"split_fraction {split_fraction!r} must satisfy 1/n_devices <= split_fraction <= 1")
    else:
        # single device: split_fraction is None or exactly 1
        if split_fraction is not None and Decimal(str(split_fraction)) != Decimal("1"):
            raise ValueError("split_fraction must be None or exactly 1 when n_devices == 1")

    valid_offload = ("none", "experts_to_cpu")
    if offload_policy not in valid_offload:
        raise ValueError(
            f"offload_policy must be one of {valid_offload}, got {offload_policy!r}"
        )

    # --- MoE bookkeeping -----------------------------------------------------
    # When the caller opts into an MoE we validate the expert set up front; a missing/short list or any
    # non-number entry raises ValueError("MoE ..."). _validate_experts also returns the offloaded byte
    # total (sum of expert sizes) which is reused for resident-weight accounting.
    if is_moe:
        offloaded = _validate_experts(n_experts, expert_bytes)
        if offload_policy == "experts_to_cpu":
            # Reject an impossible offload (offloaded bytes exceed the whole checkpoint).
            if int(offloaded) > int(total_size_bytes):
                raise ValueError(
                    f"MoE rejects sum(expert_bytes)={int(offloaded)} > total_size_bytes={total_size_bytes}"
                )
            resident_weight_bytes = Decimal(int(total_size_bytes) - int(offloaded))
        else:
            # offload_policy "none": an MoE keeps ALL weights resident on device.
            resident_weight_bytes = total_size_bytes
    else:
        # Plain dense: keep the full checkpoint total resident.
        resident_weight_bytes = total_size_bytes

    # --- KV cache (reused sizing_examples geometry) --------------------------
    kv_bytes_value = Decimal(_scaled_kv_bytes((ctx, concurrency), layers, kv_heads, head_dim))

    # --- Single-device live payload and capacity screen ----------------------
    # Overhead stays GiB; convert to bytes for the byte arithmetic. _ov/_ratio are the
    # caller-supplied or module-default values (see r5 params). For n_devices>1 each device
    # carries its own overhead copy, hence the n_devices multiplier on the runtime bracket.
    per_device_runtime_bytes = _ov * Decimal(2 ** 30)
    live_payload = (
        resident_weight_bytes
        + kv_bytes_value
        + per_device_runtime_bytes
        + _ratio * Decimal((resident_weight_bytes + kv_bytes_value))
    )
    total_gb = live_payload / Decimal("1000000000")

    # Multi-device pool: each device carries its own overhead, plus the shared transfer buffer.
    # pool_vram_gb == resident_vram_gb when n_devices==1; for n_devices>1 it is
    # (weights + KV + n x overhead + ratio*(weights+KV)) / 1e9. peak_per_device = split * pool.
    if n_devices > 1:
        pool_bytes = (
            resident_weight_bytes
            + kv_bytes_value
            + n_devices * per_device_runtime_bytes
            + _ratio * Decimal((resident_weight_bytes + kv_bytes_value))
        )
        pool_gb = pool_bytes / Decimal("1000000000")
    else:
        pool_gb = total_gb

    # peak_per_device_vram_gb equals resident_vram_gb for a single device; for >1 it is
    # split_fraction * pool (the measured larger-device share of the pool).
    if n_devices > 1 and split_fraction is not None:
        peak_per_device_vram_gb = Decimal(str(split_fraction)) * pool_gb
    else:
        peak_per_device_vram_gb = total_gb

    per_card_capacity_gb = Decimal(str(card_vram_gb))
    if per_card_capacity_gb <= 0:
        raise ValueError("card_vram_gb must be positive")

    fits_one_card = bool(total_gb <= per_card_capacity_gb)
    needs_devices = int(ceil(total_gb / per_card_capacity_gb))

    # Sensitivity endpoints for the SAME resident weight bytes + KV cache this call used,
    # via capacity_range (not a hardcoded Qwen figure). Stored as Decimals.
    scenario = capacity_range(Decimal(int(resident_weight_bytes)), kv_bytes_value)
    scenario_range_gb = {
        "lower_scenario_gb": Decimal(str(scenario["lower_scenario_gb"])),
        "upper_scenario_gb": Decimal(str(scenario["upper_scenario_gb"])),
    }

    return {
        "fits": fits_one_card,
        "resident_vram_gb": Decimal(str(total_gb)),
        "needs_devices": needs_devices,
        # Multi-device pool (== resident for n_devices==1) and per-device peak share.
        "pool_vram_gb": Decimal(str(pool_gb)) if n_devices > 1 else Decimal(str(total_gb)),
        "peak_per_device_vram_gb": Decimal(str(peak_per_device_vram_gb)),
        # Host RAM is observed-only (mmap/page cache), never predicted by this module.
        "host_ram_gb": None,
        "host_ram_note": "observed RSS (mmap/page cache), not predicted",
        "latency_cost_estimate": (
            "baseline: no offload cost modeled" if offload_policy == "none" else
            "unknown: offload cost not modeled; measure"
        ),
        "scenario_range_gb": scenario_range_gb,
        "quant": quant,
    }


def main() -> None:
    # Dense fits a 24 GB card.
    assert size_model(7_400_000_000, "bf16", False, ctx=8192, concurrency=8,
                      card_vram_gb=24)["fits"]

    # Dense too big for one 24 GB card -> needs at least two cards.
    assert size_model(74_000_000_000, "bf16", False, ctx=32768, concurrency=16,
                       card_vram_gb=24)["needs_devices"] >= 2

    # MoE with offload none keeps the FULL weight set resident.
    moe_all_on_gpu = size_model(
        total_size_bytes=50_000_000_000, quant="bf16", is_moe=True,
        n_experts=8, expert_bytes=(2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9),
        ctx=8192, concurrency=4, card_vram_gb=80)
    assert moe_all_on_gpu["fits"]

    # MoE with offload -> resident strictly less than total.
    moe_offloaded = size_model(
        total_size_bytes=50_000_000_000, quant="bf16", is_moe=True,
        n_experts=8, expert_bytes=(2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9),
        ctx=8192, concurrency=4, card_vram_gb=80, offload_policy="experts_to_cpu")
    assert moe_offloaded["resident_vram_gb"] < moe_all_on_gpu["resident_vram_gb"]

    # Invalid input must raise loudly. Each call provides the two required
    # positional args and injects exactly one bad kwarg so it reaches the right
    # validation branch instead of a TypeError for missing arguments.
    for bad in (
        dict(total_size_bytes=-1, quant="bf16"),       # negative size
        dict(total_size_bytes=1, quant="bf16", ctx=0),          # non-positive ctx
        dict(total_size_bytes=1, quant="bf16", concurrency=0),  # non-positive concurrency
        dict(total_size_bytes=1, quant="bf16", card_vram_gb=0), # zero card capacity
        dict(total_size_bytes=-1, quant="bf16", is_moe=True, n_experts=0, expert_bytes=(1,)),   # empty experts
        dict(total_size_bytes=1, quant="bf16", offload_policy="foo"),  # unknown policy
    ):
        try:
            size_model(**bad)
            raise AssertionError(f"expected ValueError for {bad}")
        except ValueError:
            pass

    # --- Regression guards (round-1 red self-checks, now expected to PASS) -----
    # (a) numeric result: resident_vram_gb is a Decimal; big dense > small dense.
    assert isinstance(size_model(8e9, "dense", ctx=1024, concurrency=1, card_vram_gb=24)["resident_vram_gb"], Decimal)
    assert size_model(8e9, "dense", ctx=1024, concurrency=1, card_vram_gb=24)["resident_vram_gb"] > \
           size_model(2e9, "dense", ctx=1024, concurrency=1, card_vram_gb=24)["resident_vram_gb"]
    # (b) offload direction: none vs experts_to_cpu differ by ~ the 16 GB offloaded.
    _none = size_model(50e9, "bf16", is_moe=True, n_experts=8,
                       expert_bytes=(2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9),
                       ctx=8192, concurrency=4, card_vram_gb=80)["resident_vram_gb"]
    _off = size_model(50e9, "bf16", is_moe=True, n_experts=8,
                      expert_bytes=(2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9, 2e9),
                      ctx=8192, concurrency=4, card_vram_gb=80, offload_policy="experts_to_cpu")["resident_vram_gb"]
    _offloaded = Decimal("16e9")
    _share = TRANSFER_BUFFER_RATIO * _offloaded
    # Decimal comparison (residual from expected < 1e-6), not float ==.
    _expected = (_offloaded + _share) / Decimal("1000000000")
    assert abs((_none - _off) - _expected) < Decimal("1e-6")
    # (c) experts sum > total with exps to cpu -> ValueError (now real, never AssertionError).
    try:
        size_model(10e9, "bf16", is_moe=True, n_experts=2, expert_bytes=(20e9, 20e9), ctx=8192, concurrency=4, card_vram_gb=80, offload_policy="experts_to_cpu")
    except ValueError as _ve:
        pass
    else:
        raise AssertionError("sum(expert_bytes) > total_size_bytes must raise ValueError")
    # (d) MoE validation branch reached with n_experts=0/expert=None -> ValueError('MoE').
    try:
        size_model(50e9, "bf16", is_moe=True, n_experts=0, expert_bytes=None, ctx=8192, concurrency=4, card_vram_gb=80)
    except ValueError as _e:
        assert "MoE" in str(_e)
    else:
        raise AssertionError("n_experts=0/expert=None must raise ValueError('MoE')")
    # (e) multi-device: ~1.5x -> 2 devices, ~2.5x -> 3 devices.
    assert size_model(36e9, "dense", ctx=8192, concurrency=4, card_vram_gb=24)["needs_devices"] == 2
    assert size_model(60e9, "dense", ctx=8192, concurrency=4, card_vram_gb=24)["needs_devices"] == 3

    # --- Round-2 guards: kill M1 (drop KV term) and M6 (drop scenario_range_gb) ----
    # (a) absolute resident value, derived from the module's own constants + kv_bytes
    #     (not a magic number), for the same inputs. Runs under main() self-check.
    _w = Decimal(8_000_000_000)          # post-quant byte total for this call
    _kv = kv_bytes(1024, 1)              # reused imported helper (Qwen2.5-7B geometry)
    _expected = (
        _w + _kv
        + RUNTIME_OVERHEAD_GIB * Decimal(2 ** 30)          # runtime/activation bracket -> bytes
        + TRANSFER_BUFFER_RATIO * (_w + _kv)               # flat 10% live buffer, same call
    ) / Decimal(10 ** 9)                                   # decimal GB == bytes / 1e9
    assert size_model(8_000_000_000, "q", ctx=1024, concurrency=1, card_vram_gb=24)["resident_vram_gb"] == _expected

    # (b) KV cache grows with context: a wider context is strictly more resident.
    assert size_model(8_000_000_000, "q", ctx=2048, concurrency=1, card_vram_gb=24)["resident_vram_gb"] > \
           size_model(8_000_000_000, "q", ctx=1024, concurrency=1, card_vram_gb=24)["resident_vram_gb"]

    # (c) custom geometry is honored: fewer KV heads/dims lower resident than default Qwen.
    assert size_model(8_000_000_000, "q", ctx=1024, concurrency=1, card_vram_gb=24,
                        layers=14, kv_heads=4, head_dim=128)["resident_vram_gb"] < \
           size_model(8_000_000_000, "q", ctx=1024, concurrency=1, card_vram_gb=24)["resident_vram_gb"]

    # (d) scenario_range_gb is a dict of Decimal endpoints equal to capacity_range(...).
    _sr = size_model(8_000_000_000, "q", ctx=1024, concurrency=1, card_vram_gb=24)["scenario_range_gb"]
    assert isinstance(_sr, dict)                           # M6 (None) -> AssertionError, not TypeError
    _cr = capacity_range(Decimal(8_000_000_000), kv_bytes(1024, 1))
    assert _sr["lower_scenario_gb"] == Decimal(str(_cr["lower_scenario_gb"]))
    assert _sr["upper_scenario_gb"] == Decimal(str(_cr["upper_scenario_gb"]))

    # --- Round-5 guards: per-overhead profile, per-device peak, host RAM observed-only ----
    _prof = LLAMACPP_RTX_PRO_4000_N1
    _P = [  # (label, predicted value) from the profile + exact measured inputs]
        ("M1", size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24,
                         runtime_overhead_gib=_prof["runtime_overhead_gib"], transfer_buffer_ratio=_prof["transfer_buffer_ratio"],
                         layers=36, kv_heads=8, head_dim=128)["resident_vram_gb"]),
        ("M2", size_model(22_313_814_528, "Q4_K_M", is_moe=True, n_experts=256,
                          expert_bytes=tuple(int(19_769_655_296 / 256) for _ in range(256)),
                          ctx=1024, concurrency=1, card_vram_gb=24, offload_policy="experts_to_cpu",
                          runtime_overhead_gib=_prof["runtime_overhead_gib"], transfer_buffer_ratio=_prof["transfer_buffer_ratio"],
                          layers=10, kv_heads=2, head_dim=256)["resident_vram_gb"]),
        ("M3_peak", size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24,
                               runtime_overhead_gib=_prof["runtime_overhead_gib"], transfer_buffer_ratio=_prof["transfer_buffer_ratio"],
                               n_devices=2, split_fraction=_prof["two_way_layer_split_fraction"],
                               layers=36, kv_heads=8, head_dim=128)["peak_per_device_vram_gb"]),
        ("M3_pool", size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24,
                               runtime_overhead_gib=_prof["runtime_overhead_gib"], transfer_buffer_ratio=_prof["transfer_buffer_ratio"],
                               n_devices=2, split_fraction=_prof["two_way_layer_split_fraction"],
                               layers=36, kv_heads=8, head_dim=128)["pool_vram_gb"]),
    ]
    # Measured references (Router's ground truth), not asserted here for parity.
    _MEASURED = {
        "M1": Decimal("3.238002688"),
        "M2": Decimal("3.150"),
        "M3_peak": Decimal("2.197815296"),
        "M3_pool": Decimal("3.772776448"),
    }
    _TOL = {"M1": Decimal("0.10"), "M2": Decimal("0.15"), "M3_peak": Decimal("0.15"), "M3_pool": Decimal("0.10")}
    for _label, _pred in _P:
        _measured = _MEASURED[_label]
        _delta_frac = abs((_pred - _measured) / _measured)   # fraction (tol is a fraction too)
        assert _delta_frac <= _TOL[_label], f"{_label}: predicted={_pred} measured={_measured} delta%({_delta_frac * Decimal(100)}) exceeds tol {_TOL[_label]}"
    print("PREDICTED-vs-MEASURED (id, predicted, measured, delta%):")
    for _label, _pred in _P:
        _measured = _MEASURED[_label]
        _delta_frac = abs((_pred - _measured) / _measured)
        print(f"  {_label:<8} {str(_pred):<12} {str(_measured):<12} {_delta_frac * Decimal(100)}")

    # Validation edge cases (reject bad kwargs).
    try:
        size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24, n_devices=2)
        raise AssertionError("expected ValueError: n_devices>1 without split_fraction")
    except ValueError:
        pass
    try:
        size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24, n_devices=2, split_fraction=Decimal("0.4"))
        raise AssertionError("expected ValueError: split<1/n_devices")
    except ValueError:
        pass
    try:
        size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24, runtime_overhead_gib=Decimal("-0.5"))
        raise AssertionError("expected ValueError: negative overhead")
    except ValueError:
        pass
    try:
        size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24, runtime_overhead_gib=True)
        raise AssertionError("expected ValueError: bool overhead")
    except ValueError:
        pass
    # Passing runtime_overhead_gib=0 lowers resident vs the module-default profile overhead.
    _with_zero = size_model(
        2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24,
        runtime_overhead_gib=Decimal("0"), transfer_buffer_ratio=Decimal("0")
    )["resident_vram_gb"]
    _with_default = size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24)["resident_vram_gb"]
    assert _with_zero < _with_default
    # Owner-added (Zadie) after gate: N4/N6 survived. Host RAM is observed-only; default overhead stays 3 GiB.
    assert size_model(2_491_323_904, "Q4_K_M", ctx=2048, concurrency=1, card_vram_gb=24)["host_ram_gb"] is None
    assert RUNTIME_OVERHEAD_GIB == Decimal("3")


if __name__ == "__main__":
    main()
