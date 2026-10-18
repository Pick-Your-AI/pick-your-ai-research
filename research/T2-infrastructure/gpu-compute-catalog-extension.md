# Blackwell contribution: sizing and observation disposition

Status: reviewed-source preparation for #10; empirical acceptance remains
separate under #61. This note receives the incoming
[63aac759 contribution](https://github.com/MrTrenchTrucker/pick-your-ai-research/commit/63aac7598a441f364b7701fa5d86e9c8cb47a65a)
and records the corrections required by
[its independent review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6256134314).
The accepted [sizing method](gpu-compute.md#reproducible-inference-sizing-method),
original examples, frozen contracts and existing empirical records retain their
own identities and dispositions.

## What is received

The thirteen [hardware proposals](blackwell-accelerators.md) contain dated,
source-checked reference facts. Their complete native precision assessment and
variant distinctions are documented there. Source checking is not independent
runtime verification, and billing stays unknown.

The incoming arithmetic helper is a research calculation. Its correction makes
cache geometry and quantity domains explicit, treats every device's fixed
overhead separately, and labels a capacity quotient as a lower bound. Results
must expose their assumptions and omitted terms. They do not decide production
compatibility, select a sufficient device count or establish an empirical error
interval. The original M1 residual fit and M3 observed memory share are not an
independent calibration dataset.

The [intake review JSON](measurements/blackwell-intake-review-2026-10-18.json)
links and hashes the original files. It is a research disposition record,
not a ResourceEstimate or a second runtime schema.

## Original reported observations

The original
[measurement JSON](measurements/rtx-pro-4000-blackwell-sff-measurements-2026-10-18.json)
is preserved byte-for-byte as a contributor report. Its embedded `executed`
status, hardware identity, metric names and timestamp describe the author's
submission; this review supplies no new execution. The report names two RTX
PRO 4000 Blackwell SFF cards, driver 580.126.09 and an unpinned llama.cpp server.
All three scenarios report concurrency 1 and f16 KV.

| Scenario | Contributor's model/configuration label | Loaded / generation process memory, MiB | Reported output tokens/s |
| --- | --- | ---: | ---: |
| M1 | Qwen3 4B, Q4_K_M, context 2048, one card | 3078 / 3088 | 28.4 |
| M2 | Qwen-Agentworld35BA3B, Q4_K_M, context 1024, expert offload | 2994 / 3004 | 7.3 |
| M3 | M1 with a two-card split | 3578 / 3598 total; generation 2096 + 1502 by device | 23.5 |

These are reported per-process driver samples. The largest device value in M3's
generation sample is a cross-device maximum at that sample, not the maximum
over the runtime's phases. Preserve the stated MiB unit before conversion:
3088 MiB is 3.238002688 decimal GB; 3004 MiB is 3.149922304 GB;
3598 MiB is 3.772776448 GB. Rounded displays must not replace original counters.

NVIDIA's [nvidia-smi documentation](https://docs.nvidia.com/deploy/nvidia-smi/index.html)
describes the compute-process memory counter as GPU context memory. That counter
does not supply separate allocator allocated/reserved peaks. The submitted
loaded/generation pairs have no original timestamped trace or sample-interval
manifest. No independent raw-output audit or artifact-bound reproduction is
claimed. The host 8.4 GB value and latency observations retain the author's stated
measurement scope; they are not predictions from the helper.

M1 and M2 differ in model, architecture and context as well as offload. Their
timing difference cannot isolate the cost of CPU offload. The report's hybrid
SSM/full-attention label does not provide a complete recurrent-state derivation
at arbitrary context or concurrency.

## Arithmetic defects and corrected boundary

The original helper's generic signature hid a Qwen2.5 cache fallback whenever
any custom geometry field was absent. It also applied `int()` before validating
counts and quantities, allowing fractional or Boolean inputs to change meaning.
Several negative self-checks reached the default zero-context rejection before
their intended invalid argument.

Its device-count equation used only a single-device total. Independent
substitution with 40,000,000,000 weight bytes, context 16, concurrency 1 and two
24 GB cards gave a reported count of two, while the same call's own per-device
result was 25.2217300992 GB. An aggregate quotient is insufficient without a
supported partition plan, replicated/per-rank overhead and the other live terms.
A single-card `fits` Boolean also did not represent the supplied topology or
the separate sensitivity range.

The corrected helper preserves post-quant storage inputs without quantizing them
again, and counts all resident MoE weights when offload is absent. Offloading
expert bytes does not establish host RAM capacity, loading/staging peaks or
latency. A complete cache formula requires its explicit architecture, dtype,
block size and admitted sequences. Hybrid/recurrent, quantized-cache metadata,
workspace and topology terms must be modeled explicitly or remain unknown.

### Corrected helper usage and explicit assumptions

Use `size_model` from `research/T2-infrastructure/compute/sizing_generic.py`.
Counts and bytes require actual Python integers; Boolean values, floats and
coercible strings are rejected. Capacity, overhead and ratios accept finite
`int`, `Decimal` or `Fraction` values. Arithmetic uses exact rational values,
including comparisons beyond binary64's exact integer range. Decimal GB is
bytes divided by 10^9; GiB is bytes divided by 2^30.

Supply all five fields (`layers`, `kv_heads`, `head_dim`, `kv_element_bytes`,
`block_tokens`) or explicitly choose the one pinned example. That example's
28 layers, four KV heads, head dimension 128, two-byte cache elements and
16-token blocks reproduce the accepted Qwen2.5 example; they are not a generic
architecture fallback. Context reserves prompt plus output for each independent
admitted sequence, and each sequence is rounded to complete cache blocks.

For example, from the helper's directory:

```python
from decimal import Decimal
from fractions import Fraction
from sizing_generic import size_model, capacity_sensitivity

scenario = size_model(
    40_000_000_000, "already-quantized",
    ctx=16, concurrency=1, card_vram_gb=24,
    runtime_overhead_gib=3, transfer_buffer_ratio=Decimal("0.1"),
    geometry_example="qwen2.5-7b-bf16-block16",
    n_devices=2,
    device_payload_fractions=(Fraction(1, 2), Fraction(1, 2)),
)
reserved_scenario = capacity_sensitivity(
    scenario["modeled_per_device_bytes"],
    reserve_fraction=Fraction(1, 5),
)
```

This is an assumed equal partition of weights, attention cache and transfer
buffers. Each card also retains its entire 3 GiB overhead. The payload's device
lower bound is two, but each device's modeled total is 25.2217300992 decimal GB
and exceeds the supplied 24 GB capacity. A supported runtime partition and
omitted state remain unqualified. `admission` is always `unknown`; no `fits`,
sufficient-device recommendation, calibrated output or ResourceEstimate is
emitted. The separate 20% reserve example is a caller-selected sensitivity
calculation, with no measured confidence or universal reserve claim. Its input
must be the modeled live bytes before that reserve, not an already reduced pool.

For explicit MoE offload, `is_moe=True`, `offload_policy="experts_to_cpu"` and
`offloaded_expert_bytes` assert one aggregate byte amount bounded by the supplied
total. No equal-size expert population or supported CPU-transfer path is inferred.
With no offload policy, every supplied weight byte remains resident. The M2
demonstration counts only its asserted full-attention component; recurrent state,
host memory and actual peaks stay unknown. M3's demonstration uses a hypothetical
equal split, not the reported device memory ratio.

The command-line demo prints three explicitly unverified arithmetic scenarios.
It preserves the original labels and asserted inputs without using the process
memory samples as calibration targets, tolerances or estimator-pair evidence.

## ResourceEstimate and #61 intake decision

The submitted ResourceEstimate is **not admitted**. Its build ID has no matching
real BuildSnapshot in the contribution, and the distinct scenarios repeat generic
selection IDs without bindings. Every metric was labeled `calibrated`, although
the M1 overhead is fitted on M1 and M3's split fraction is taken from M3.
Those facts do not establish holdout residuals or a validated 10–15% error range.

The exact original ResourceEstimate remains linked by commit/blob/hash from
the intake review, but is omitted from the current tree. No replacement build,
selection set, confidence grade or runtime artifact is manufactured. The
existing accepted future placement under #381 remains intact; a location
decision does not admit this record.

This contribution adds **zero eligible whole-runtime peak-allocated/reserved
estimator pairs** to #61. Admission still needs exact engine/build/binary and
model/config/tokenizer/artifact pins; complete workload and phase/sampling
protocols; original outputs and repeated whole-runtime allocated/reserved
peaks; and semantically matched pinned llmfit, ModelFit and Planner comparisons.
The existing dense, MoE and KV-component results keep their separate scope.
A failed or unavailable measurement is not replaced by a synthetic estimate.

## Validation and receiving boundary

The source review read all incoming files and current primary hardware sources.
The independent arithmetic reviewer also read the complete helper and accepted
method before executing bounded offline regression checks. No GPU workload,
model download, paid service, provisioning, participant work or additional
hosted job was started for this review.

The arithmetic author's original-source probe ran eight cases: one passed,
six failed and one errored. The corrected helper's 29 focused tests then passed
under Python 3.12.14 both normally and with `-O`; the eight existing
`memory_screen` tests also passed without source changes. The independent
Android reviewer and root reviewer read the full corrected helper and all
29 test methods; those source reviews are separate from the author's test runs.
The failures in the original probe remain original failures, not corrected-run
successes. Tests cover missing/partial geometry, one-field invalid inputs,
exact units and capacity boundaries, MoE residency/offload, replicated overhead,
partition conservation, reserve sensitivity and unverified demo labeling.

Repository validators check schema/identity/import/source-shape integrity.
They do not reproduce the contributor's observations, retrieve hardware
sources, establish source/use permission or qualify a runtime tuple.

### Actual composed-source repository checks

The root reviewer ran the complete required Research workflow on corrected
tree `ed75a67cb5d2cf0697ae8b394d2363320f92acf4`, based on accepted main
`0d2e34d76cc6ac3e56165b7e72f4bbe0b8b87cb2`, from
2026-10-18 23:08:23 through 23:11:51 UTC. Python was 3.12.14 and all seven
installed dependencies exactly matched `requirements-research.txt`.

| Actual command | Result |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed; 0.467 seconds in the unittest summary. |
| `python -m unittest discover -s tests -v` | 1,067 passed, including all 29 new arithmetic regressions; 206.173 seconds in the unittest summary. |
| `python scripts/validate_research.py` | Passed: 124 catalog proposals and three Pricebooks, plus external evidence metadata. |
| `python scripts/validate_market_research.py` | Passed: 39 entities, 1,872 cells and 20 issues. |
| `python scripts/validate_handoff_audit.py` | Passed: 101 rows and 98 declared pairs; human acceptance is not certified. |
| `python prompts/mobile/validate_prompts.py` | Passed: two Projects, 258 issues, 36 epic prompts, 906 criteria, 880 steps and seven accepted placement coordinates. |
| `git diff --cached --check` | Passed. |

The complete original contract log is 2,681 bytes, SHA-256
`c0e3c5c6271a19dab80f9241f42ff024e0289c97f0b665ef01260ace9cac48e9`.
The complete original repository-test log is 190,647 bytes, SHA-256
`16209ae7c4c197f18e29d71e2047d02b2e4c0d898a5034edddcf2d3b0d95c34a`.
All seven commands returned zero. The two multiline test descriptions remain
two passed methods; they are not missing or duplicated cases.

The tested tree preserved all 716 unrelated base leaves and all original
accepted sizing-method content. Its 737 leaves add the reviewed contribution
and regressions, with only a bounded link/disposition append to the existing
method. The original measurement-report blob remains
`f26fe59a53b4d2914a4dd5bbf21ed4ecbdfde05c`.

This documentary receipt is added after that exact run. It supplies no new
execution at a later composition, and does not turn the contributor's own
reported checks into these independently run results. Commit-specific
receiving review and the actual publication checks remain required.
