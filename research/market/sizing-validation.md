# MR-09: Validate GPU sizing against pinned runtime measurements

Issue: [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61). Owner: @Mattycodes69. Status: empirical partial research; evidence and handoff acceptance pending. Last researched: 2026-10-16. Live Project fields are authoritative; this note does not change them.

## Question
Where do planning estimates fail under real runtime conditions?

## Starting evidence
[technical-feasibility.md](technical-feasibility.md). This note is not a new canonical component catalog or completed competitor-estimator validation.

## Protocol and acceptance
- [x] Design dense and MoE measurement matrix
- [x] Vary context cache precision and concurrency (dense D1–D5; MoE variation remains a gap)
- [x] Measure peak allocated and reserved memory (executed dense cases; pending unexecuted cases)
- [ ] Report error bounds and failures without universal fit claims
- [ ] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain affected-owner review and accepted handoff.

## Next action
Finish the bounded matrix and the separately recorded coverage gaps; obtain context, sizing and runtime-owner review. The original protocol checklist remains above, with completion claimed only where supported below.

## Result
Partial real GPU inference has been executed. This does not complete independent validation of competitor sizing estimates or establish universal fit. No raw customer content, paid API output, weights or raw datasets are committed. Consumers: #7, #10, #11.

## Prepared protocol, inputs and inventory

The dated [pre-execution protocol](measurements/mr09-protocol-2026-10-16.md)
defines architecture/context/cache/concurrency coverage, synchronization and
phase resets, failure categories, repetition policy, comparison targets, and
the error denominator. [Inventory](measurements/mr09-inventory-2026-10-16.json)
separates discovery from inference. It found one shared RTX 5070 Ti (16,303 MiB
reported total, NVIDIA driver 595.97), with approximately 4 GiB reported free
by `nvidia-smi` during initial discovery. Availability changes; no exclusive
device reservation or second GPU exists for these experiments.

The default Python has CPU-only PyTorch. Reuse of an existing Python 3.12.11 /
PyTorch 2.10.0+cu130 / Transformers 5.0.0 environment enabled actual CUDA
inference without changing the user's installed packages or other workloads.
Every run pins package/build versions and native allocator backend. Small
public pretrained SmolLM2-135M-Instruct was chosen to fit a process allocator
cap of at most 2 GiB while preserving spare capacity. The
[artifact ledger](measurements/mr09-smollm2-artifacts.json) records revision
`12fd25f77366fa6b3b4b768ec3050bf629380bac`, exact public URLs and SHA-256
for config/tokenizer/BF16 safetensors; weights stay outside Git. The publisher
labels this model Apache-2.0. Quantized KV, where exercised, uses separately
inspected `optimum-quanto==0.2.7` unpacked only in a temporary task directory.
BF16 model weights remain unchanged when KV precision changes.

The [concrete OLMoE plan](measurements/mr09-moe-plan.json) pins a trained MoE,
its metadata, exact revision, licensing and four context/cache/concurrency
cells. Its 13,838,323,712-byte BF16 weight payload alone exceeds the current
bounded process cap and spare capacity; it was not downloaded or executed.
This establishes a limitation of that selected configuration and current
reservation, not a claim that this GPU can never run any MoE. No random model
or synthetic fixture supplies missing empirical coverage. Multi-GPU placement,
rank peaks and topology remain unexecuted because only one GPU is available.

## What the memory counters mean

Allocator allocated bytes are live tensors owned by this measurement process;
reserved bytes include allocator backing blocks and already contain allocated
memory. They must not be added. Driver/device memory can include other
processes, context and library allocations, and is recorded separately. Phase
peaks use synchronized PyTorch allocator counters, with a reset immediately
before loading, warm-up, prefill and decode. No cache is cleared within a
measured phase. Own warm-up outputs/cache are released, synchronized and the
allocator emptied before measured prefill; loaded model weights remain.
CUDA graphs and compilation are disabled, so no graph capture measurement is
claimed. The post-decode snapshot is an instantaneous live-cache observation,
not a stable serving regime. Shared-device timings do not establish an SLO.

A real discovery during D1 is that `torch.cuda.mem_get_info()` reported
15,769,534,464 free bytes while the same run's `nvidia-smi` snapshot reported
3,823 MiB free. Their meanings cannot be treated as interchangeable on this
host. The cause (including a Windows memory-budget explanation) is unconfirmed.
The subsequent [serial wrapper](../../scripts/mr09_run_matrix.ps1) adds an
`nvidia-smi` free-memory guard of 2,048 MiB before every launched process,
alongside the runner's CUDA-reported guard and small allocator cap. Neither
number is a guarantee of future allocation success. No other process is
evicted or altered. Per-phase CUDA-reported free values are observations, not
additional headroom or demanded KV memory.

## Comparison target and error discipline

The existing PR #75 sizing arithmetic at
`9e66622a4b2698a9305274f05da9c15ae5d90b8c` remains a Qwen-specific,
uncalibrated reference. It is not imported wholesale and does not become real
measurement evidence. Its model constants and device-budget/headroom scenarios
cannot be silently substituted for these SmolLM2 allocator measurements.

The competitor observations and pinned versions in
[technical-feasibility.md](technical-feasibility.md#assumptions-actually-inspected)
do not provide a matching model artifact, runtime condition and measurement
quantity for these runs. ModelFit's missing 135M catalog entry and absent
context/KV/concurrency inputs are recorded as mismatches. llmfit's GGUF/F16
planning model is not this BF16 Transformers allocation; the web planner also
does not reproduce this serving configuration. Comparable competitor/runtime
error pairs: **0**. Their numerical error range is therefore **not available**;
it is neither zero nor a pass. Estimator rejection/missing inputs remains
separate from model-runtime success or OOM.

For the native dynamic BF16 KV tensor payload only, the transparent dense
formula is `2 × 30 layers × 3 KV heads × 64 head dimension × 2 bytes ×
cache tokens × active sequences`. Its agreement with measured native tensors
is a layout sanity check, not calibration of total VRAM, allocator peaks,
runtime overhead or competitor predictions. INT4 accounting includes actual
packed storage, scales, shifts and BF16 residual rather than pretending every
cache byte uses four bits. Allocator reservations and transient dequantization
workspace remain separate. Signed relative error uses the positive measured
quantity as denominator; failures and mismatches have no fabricated errors.
No coordinator-approved MVP tolerance exists. Observed sample extremes may
be reported, but cannot be described as guaranteed bounds.

## Executed dense results — 15 real runs

D1–D5 each completed three fresh-process repetitions: **15 successful real GPU
inference runs, zero observed loading/prefill/decode OOM and zero model-runtime
errors**. All five use the same pinned trained model and BF16 weights. The
[machine-readable summary](measurements/mr09-results-summary.json) links every
sanitized input checksum and reports min/median/max with sample counts for all
six phases. Individual `mr09-D*-r*.json` files retain exact bytes and actual
tokens; INT4 records retain packed/scales/shifts/residual storage separately.

Values below are **peak allocated / peak reserved MiB**, MiB=2^20 bytes. For
each cell/phase/counter, n=3 and **min=median=max=the value shown**, so the
observed repetition range is [value,value] and width 0 MiB. Byte counters are
identical across these repetitions; device-free observations and timings are
not asserted identical. Zero observed allocator variation is not a confidence
interval or a guaranteed error bound.

| Cell: prompt / KV / active | Warm-up | Prefill | Decode | Instantaneous post-decode |
| --- | --- | --- | --- | --- |
| D1: 256 / BF16 / 1 | 267.515 / 290 | 279.472 / 298 | 273.389 / 298 | 271.046 / 298 |
| D2: 2,048 / BF16 / 1 | 267.528 / 290 | 681.265 / 736 | 328.159 / 736 | 310.435 / 736 |
| D3: 2,048 / BF16 / 2 | 270.310 / 292 | 1,083.298 / 1,178 | 392.295 / 1,178 | 358.596 / 1,178 |
| D4: 2,048 / INT4+BF16 residual / 1 | 266.579 / 290 | 650.421 / 690 | 297.339 / 690 | 278.091 / 690 |
| D5: 2,048 / INT4+BF16 residual / 2 | 268.411 / 292 | 1,018.517 / 1,078 | 328.957 / 1,080 | 291.466 / 1,080 |

Baseline is allocated/reserved 0/0 in every cell (n=3; min/median/max 0). Loading
is allocated 256.590 / reserved 288 MiB in every cell (n=3; identical range for
each). Baseline0 measures this process's tensor allocator after initialization,
not zero total GPU/runtime memory. Graph capture is not applicable because the
protocol uses eager execution. All repetitions produce exactly 33 predictions
per sequence from 32 decode forwards; terminal cache positions are 288 for D1
and 2,080 for D2–D5. Active batch 2 means two simultaneous independent sequences,
not two queued requests. These are model-forward workloads, not a serving
scheduler or a quality benchmark.

Native prefill KV payload is 5,898,240 bytes in D1, 47,185,920 in D2 and 94,371,840
in D3. Against that **same tensor-payload target**, the dense formula has nine
observations with signed/absolute/relative error 0; this establishes layout
consistency only. Competitor calibration remains n=0 and error unavailable.
For D4, INT4 prefill storage is 11,796,480 packed + 737,280 scales + 737,280 shifts
= 13,271,040 bytes, then adds 737,280 BF16 residual bytes after 32 forwards.
D5 doubles those physical payloads to 26,542,080 and 28,016,640 bytes.

The bounded empirical finding is that prefill can dominate the instantaneous
post-decode live allocation: D2 peaks at 681.265 MiB versus 310.435 MiB post-decode,
while its 736 MiB pool persists into decode. Cache quantization reduces the
measured cache payload but does not remove prefill workspace or allocator
reservation. D4's 13.271 MB cache is therefore not a prediction of its 650.421 MiB
prefill peak. D5's reserved peak also rises from 1,078 MiB at prefill to 1,080 MiB
during decode. A weight-plus-demanded-cache number alone cannot substitute for
these runtime-specific counters. No unsafe-fit or conservative-fit frequency
is claimed because there is no matching estimator prediction cohort.

## Remaining architecture and access coverage

The user requested spare local capacity only. The first
[supplemental trained Granite3.0 MoE plan](measurements/mr09-moe-supplement-2026-10-16.md)
was screened after the dense matrix at 14:01:41 UTC. GPU reported 4,132 MiB free
and host available 17,017,819,136 bytes passed; temporary-volume free 7,223,148,544
bytes failed its predeclared 12 GiB guard. The
[failed preflight](measurements/mr09-moe-preflight.json) is retained and its
5.54 GB FP32 source shards were not downloaded.

A [separate Granite3.1 BF16 profile](measurements/mr09-granite31-protocol-2026-10-16.md)
pins an official 2,669,283,096-byte trained MoE artifact with smaller transfer
and disk requirements; this is a justified candidate change, not a relabeling
of the first case. Its first [preflight](measurements/mr09-granite31-preflight.json)
at 14:03:43 UTC passed host RAM and the artifact-specific 6,412,308,016-byte disk
guard, but `nvidia-smi` free 4,033 MiB failed the unchanged 4,096 MiB GPU guard.
No weights were downloaded or MoE inference claimed at that screen. The single
[final availability screen](measurements/mr09-granite31-preflight-final.json)
after independent review, at 14:06:50 UTC, still failed the same GPU guard:
3,935 MiB free against 4,096 MiB required. Host RAM 17,015,889,920 bytes and
disk 7,418,503,168 bytes passed. Both failed Granite3.1 records are preserved;
no further GPU checks or MoE attempts are made in this submission. No workloads
were evicted and no Granite weights were downloaded.

The selected OLMoE context/cache/concurrency matrix remains unexecuted, and
Granite3.1's prepared short-case profile cannot stand in for its
unexecuted 2,048-token/active 2/INT4 MoE variations. Multi-GPU cases lack a second
authorized GPU and per-rank topology. Graph capture, paged continuous batching,
offload, FP8 and weight quantization remain explicit exclusions. @Mattycodes69
and @CompleteDotTech must arrange a reserved safe envelope/artifact storage
or accept a narrower research scope through human review. No coverage waiver
or completion is inferred from these access constraints.

## Execution provenance and administrative failures

All 15 dense runs record runner SHA-256
`d33c45c5d13a93816cb71175b73ec35938805c99b3e3969fe73eae86c83ccfe8`
and protocol SHA-256
`d0e64816de896d19d764ff5a1302e8ee7b9678e098f8929886fa6c239a4c0735`.
The unchanged runner and original dated protocol are retained in this submission.
The execution timestamp and package/hardware conditions are in each file.

D1-r1 is a direct-run pilot retained in the three-repetition D1 cohort because
its model/configuration/instrument source matches the later repetitions. It
has a pre-inference runtime `nvidia-smi` sample 3,823 MiB and a small allocator
cap, but no separately enforced wrapper guard. D1-r2 passed the wrapper's
4,032 MiB console guard and completed inference; a subsequent PowerShell JSON
parse error (empty device-map key) prevented that wrapper ledger entry being
retained. Its preflight UTC is unknown and is not fabricated. D1-r3 onward
uses recorded serial preflight guards. The archived BF16 wrapper body
[mr09-wrapper-bf16-v1.ps1](measurements/mr09-wrapper-bf16-v1.ps1) was reconstructed
from the applied command/patch history after execution; no pre-execution hash
is claimed for that administrative wrapper. It is not the memory instrument.

The wrapper was corrected to use `ConvertFrom-Json -AsHashtable`; after D4-r1
another administrative singleton-array/hashtable accumulation error stopped
the next launch before inference. Explicit array typing, array JSON output
and ledger reload now preserve earlier entries. A synthetic add/reload/add
check passed. No model-runtime failure, OOM or extra successful repetition is
invented from either administrative error; each real repetition has its own
result. [BF16](measurements/mr09-bf16-execution-ledger.json) and
[INT4](measurements/mr09-int4-execution-ledger.json) ledgers retain available
guard observations. Focused synthetic tests cover unit/error arithmetic,
failure categories, pinned artifact identity rejection, and summary provenance.
The first sandbox attempt to write temporary test fixtures failed due denied
TEMP access; the same tests passed with normal temporary-directory permission.

The [cleanup readback](measurements/mr09-temporary-cleanup.json) records removal
of only this task's temporary SmolLM2 model/config files (271,172,949 bytes),
isolated Quanto package (666,353 bytes) and wheel (165,285 bytes), after all
measurement processes exited and hashes were published. Resolved targets were
verified within the intended temporary root, with reparse points refused;
all three paths were absent on readback. Preexisting caches, models, installed
environments and user files were preserved. Reproduction requires redownloading
the exact permitted model artifact using its published manifest.

## Reproduction and evidence boundaries

Use the protocol's exact model revision, public artifact checksums and pinned
runtime versions. The instrumented [runner](../../scripts/mr09_measure.py)
validates local file hashes before loading and rejects unexplained existing
artifacts during preparation. Each repetition runs in a fresh process. Synthetic
non-sensitive prompts drive a real trained model, seed 6109, greedy decoding,
no EOS stopping, exact token counts and equal-length active batch 1 or 2.
There are zero queued requests and no prefix sharing or offload. Prefill
predicts one token; 32 decode forwards predict another 32, giving 33 predictions
and prompt+32 cache positions. No output text or customer content is stored.

Set `$CUDA_PYTHON` to the pinned CUDA-enabled interpreter, `$MODEL_DIR` to a
fresh temporary model directory outside Git, and `$QUANTO_DIR` to a fresh
isolated optional-package directory. For replication, the optional package can
be prepared with `& $CUDA_PYTHON -m pip install --no-deps --target $QUANTO_DIR optimum-quanto==0.2.7`;
this leaves the shared interpreter's installed packages unchanged. Use a fresh
result directory so existing committed observations are not skipped or overwritten.
From the repository root, in PowerShell:

```powershell
$RESULT_DIR = Join-Path $env:TEMP ('mr09-replication-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $RESULT_DIR | Out-Null
& $CUDA_PYTHON scripts/mr09_measure.py --prepare --model-dir $MODEL_DIR --output (Join-Path $RESULT_DIR 'mr09-smollm2-artifacts.json')
& ./scripts/mr09_run_matrix.ps1 -CudaPython $CUDA_PYTHON -ModelDir $MODEL_DIR -OutputDir $RESULT_DIR -Group bf16
& ./scripts/mr09_run_matrix.ps1 -CudaPython $CUDA_PYTHON -ModelDir $MODEL_DIR -QuantoDir $QUANTO_DIR -OutputDir $RESULT_DIR -Group int4
python scripts/mr09_summarize.py --directory $RESULT_DIR --sanitize
```

The summary derives minima/medians/maxima and input checksums from individual
run records; it omits failed measurements from numerical aggregates and
preserves failure categories. Published outputs replace private filesystem
locators with named placeholders and omit hardware UUIDs; measurement counters,
conditions and hashes are unchanged. Existing completed result files are
preserved by the wrapper; use a fresh output directory for independent replication.

| Evidence | Publisher / locator | Access / version | Class and confidence | Limits and reuse |
| --- | --- | --- | --- | --- |
| M61-I | [Local inventory](measurements/mr09-inventory-2026-10-16.json) | 2026-10-16; exact packages/hardware in file | Project discovery; high for successful command observations | Changing availability; denied CIM and unavailable per-process counters retained; sanitized project data |
| M61-D | [Pinned SmolLM2 card](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/blob/12fd25f77366fa6b3b4b768ec3050bf629380bac/README.md), [config](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/blob/12fd25f77366fa6b3b4b768ec3050bf629380bac/config.json) | 2026-10-16; revision above; region not applicable | Primary documentation; high for transcribed geometry/license, no capacity claim | Apache-2.0 label; artifact hashes in ledger, weights outside Git |
| M61-A | [PyTorch CUDA memory management](https://docs.pytorch.org/docs/2.10/notes/cuda.html#cuda-memory-management) | 2026-10-16; v2.10 | Primary documentation; high for allocator API semantics | Allocator counters exclude some CUDA/library and other-process allocations; own paraphrase, no redistribution of docs |
| M61-K | [Transformers cache guide](https://huggingface.co/docs/transformers/v5.0.0/en/kv_cache) | 2026-10-16; v5.0.0 | Primary documentation plus installed source inspection; high for configured cache semantics | Backend support needs actual execution; no quality claim; own summary |
| M61-M | [Pinned OLMoE card/config/index](measurements/mr09-moe-plan.json) | 2026-10-16; revision in plan | Primary documentation; high metadata confidence; fit unverified | Apache-2.0 label; no weights downloaded or runtime execution |
| M61-G | [Granite3.0](measurements/mr09-moe-supplement-2026-10-16.md), [Granite3.1](measurements/mr09-granite31-protocol-2026-10-16.md), and linked pinned publisher sources | 2026-10-16; exact revisions in profiles | Primary metadata and project-derived capacity screens; high transcription confidence, fit unverified | Apache-2.0 labels; publisher hashes are not local download checks; no weights downloaded; card/config architecture prose discrepancy retained |
| M61-R | [Published run ledger and summary](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/codex/mr09-feasibility-validation/research/market/measurements) / this project's MR-09 research | 2026-10-16; model, runner and protocol hashes recorded in every result; integrated submission records commit | Independent project measurement; high confidence in these allocator observations; uncalibrated for competitor estimates | One model/device/runtime envelope, three repeats per cell, shared device, no MoE/multi-GPU execution; sanitized project counters are permitted to reproduce; source weights remain outside Git |

## Handoff review and completion

| Consumer | Finding offered | Receiving owner | Disposition / unresolved next action |
| --- | --- | --- | --- |
| #7 | Actual prompt/cache/predicted-token counts, context and active concurrency differ from queue length | Live owner recorded in [handoffs.md](handoffs.md) | Pending human review; confirm context-policy assumptions and untested boundaries |
| #10 | Allocated/reserved phase peaks and KV-payload observations, with zero comparable competitor pairs | Live owner recorded in [handoffs.md](handoffs.md) | Pending human review; agree calibration targets and future ResourceEstimate consumer/placement |
| #11 | Exact Transformers/CUDA/allocator pins, supported or failed optional cache backend and phase reset procedure | Live owner recorded in [handoffs.md](handoffs.md) | Pending human review; accept instrumentation scope and required runtime extensions |

No ResourceEstimate, canonical catalog item, Pricebook or compatibility boolean
is manufactured. #40 remains the review entry for any contract/rule change;
v1 is unchanged. Agent reproducibility review can identify defects and support
the submission; it does not accept the above owner handoffs. #61 remains open
until its coverage, relevant evidence review and acceptance gates are met.
Automation checks structure, unit arithmetic, failure handling and consistency;
human reviewers still assess experimental validity, source accuracy, reuse
rights, freshness, completeness and evidence acceptance. The integrated
submission validation report records the repository checks separately.
