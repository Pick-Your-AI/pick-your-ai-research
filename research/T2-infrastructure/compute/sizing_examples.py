"""Reproduce gpu-compute.md arithmetic. No runtime or vendor capacity measurement.

Model metadata source: Qwen/Qwen2.5-7B-Instruct, revision
d1e200fcf95ef0d4326873ddf63e5562d5f1fdbb; see evidence C11 in the note.
All overhead, headroom and hypothetical quantization/adapter scenarios are project
assumptions, not calibration data. Run under Python3.12 from the repository root.
"""

from decimal import Decimal, ROUND_CEILING
import json


GB = Decimal(10**9)
GIB = Decimal(2**30)
WEIGHT_BYTES = Decimal(15_231_233_024)
LAYERS = 28
KV_HEADS = 4
HEAD_DIM = 3584 // 28
KV_ELEMENT_BYTES = 2
BLOCK_TOKENS = 16


def kv_bytes(context_tokens: int, concurrency: int) -> Decimal:
    """Dense full-attention BF16 KV, independent active sequences, no sharing."""
    if context_tokens <= 0 or concurrency <= 0:
        raise ValueError("context and concurrency must be positive")
    blocks = (context_tokens + BLOCK_TOKENS - 1) // BLOCK_TOKENS
    tokens = blocks * BLOCK_TOKENS * concurrency
    return Decimal(2 * LAYERS * KV_HEADS * HEAD_DIM * KV_ELEMENT_BYTES * tokens)


def capacity_range(weights: Decimal, cache: Decimal, adapters: Decimal = Decimal(0)) -> dict:
    """Sensitivity endpoints, not a confidence interval or runtime error bound."""
    live_payload = weights + cache + adapters
    low = (live_payload + 2 * GIB) / Decimal("0.9") / GB
    high = (live_payload + 4 * GIB) / Decimal("0.8") / GB
    return {"lower_scenario_gb": str(low), "upper_scenario_gb": str(high)}


def main() -> None:
    short_kv = kv_bytes(8192, 1)
    loaded_kv = kv_bytes(32768, 8)
    # Reproducible formula cross-checks, not measurements or deployment tests.
    assert HEAD_DIM == 128
    assert kv_bytes(1, 1) == kv_bytes(16, 1)
    assert short_kv == 469_762_048
    assert loaded_kv == 15_032_385_536
    assert kv_bytes(32768, 8) == kv_bytes(8192, 1) * 32

    # Clearly hypothetical: every BF16 element packed toINT4 plus10% metadata.
    nominal_elements = WEIGHT_BYTES / 2
    hypothetical_quant_bytes = nominal_elements / 2 * Decimal("1.10")

    # Clearly hypothetical: Q and V targets only,rank16,BF16,4resident adapters.
    one_lora = Decimal(28 * 16 * ((3584 + 3584) + (3584 + 512)) * 2)
    all_lora = one_lora * 4
    assert one_lora == 10_092_544
    assert all_lora == 40_370_176

    two_device_peak = (Decimal(70) + 8 + 4) / Decimal("0.9")
    four_device_peak = (Decimal(35) + 4 + 4) / Decimal("0.9")
    assert two_device_peak > 80
    assert four_device_peak < 80

    result = {
        "classification": "project estimates; no device execution or calibrated error range",
        "estimator_id": "t2-dense-kv-memory",
        "estimator_version": "0.1.0",
        "A_bf16_short": capacity_range(WEIGHT_BYTES, short_kv),
        "B_bf16_loaded": capacity_range(WEIGHT_BYTES, loaded_kv),
        "C_hypothetical_int4": capacity_range(hypothetical_quant_bytes, loaded_kv),
        "D_hypothetical_lora": capacity_range(WEIGHT_BYTES, short_kv, all_lora),
        "aws_ram_gb": str(32 * GIB / GB),
        "synthetic_two_gpu_peak_gb": str(two_device_peak),
        "synthetic_four_gpu_peak_gb": str(four_device_peak),
        "aggregate_weight_only_gpu_lower_bound": int(
            (Decimal(140) / 80).to_integral_value(rounding=ROUND_CEILING)
        ),
        "throughput_tokens_per_second": "unknown",
        "latency_ms": "unknown",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
