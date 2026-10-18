# MR-09: Validate GPU sizing against pinned runtime measurements

Issue: [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61). Live co-owners (refreshed 2026-10-18): @Mattycodes69 and @appletechie. Status: empirical partial research; evidence and handoff acceptance pending. Last researched: 2026-10-18. Live Project fields are authoritative; this note does not change them.

## Question
Where do planning estimates fail under real runtime conditions?

## Starting evidence
[technical-feasibility.md](technical-feasibility.md). This note is not a new canonical component catalog or completed competitor-estimator validation.

## Coverage and authority disposition (2026-10-18)

**Retain the full empirical acceptance scope recorded in the live issue.**
This research follow-up documents the hardware needed for the existing dense,
MoE, multi-GPU and comparable-estimator requirements. It supplies no new
device, reservation, download or cost authorization. Sources inspected on 2026-10-18:
[live #61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61),
[Zwright8's scoped receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6242699281)
and the committed protocols/results at main
`ecd5f66d758e8bf89eafbeacfe8eae87ce9b4999`. The hardware checklist below was
prepared without execution; the separately dated GM1 continuation now records
fresh preflight, pinned download and three bounded local runs under the existing
spare-capacity authorization. No paid compute or new device was used.

| Gate | Available evidence | Exact remaining action / accountable owner |
| --- | --- | --- |
| Dense observations | D1–D5: five configurations, three fresh-process runs each; separate allocated/reserved counters | #61 co-owners and coordinator review the bounded observations and provenance caveats |
| MoE variations | Three supplemental GM1 runs; pinned OLMoE matrix remains unexecuted | @Mattycodes69/@appletechie identify an authorized envelope for remaining cells and rerun unchanged preflight guards before any download; short Granite alone does not replace the varied OLMoE matrix |
| Multi-GPU/per-rank coverage | Designed case; no second authorized device or executed topology | #61 co-owners with @CompleteDotTech identify authorized devices and per-rank instrumentation before execution |
| Comparable estimator errors | Zero matching competitor/runtime pairs | #61 co-owners pin matching estimator/model/runtime/quantity inputs first; coordinator and #10 agree the decision tolerance before testing it; report observed errors without inventing an accepted threshold |
| Headroom | Dense allocator counters and historical availability samples | #10 co-owners review [explicit scenario reserve](../T2-infrastructure/gpu-compute.md#headroom-and-measurement-handoff-disposition-2026-10-18); no universal percentage or whole-device calibration follows from these runs |
| ResourceEstimate consumption | No real BuildSnapshot/selection binding; no measured allocator metric in v1 | Offer observations as note-only #10 evidence; future build-bound estimates use the [proposed intake](../T2-infrastructure/compute/resource-estimates/README.md) only after owner agreement |

The prior spare-local-capacity-only constraint and GPU/RAM/disk/process caps
remain in force. The 2026-10-16 Granite3.1 failure is a historical observation,
not a current hardware reservation or a new availability measurement. Paid
compute, another device, or a different capacity envelope needs explicit
authorization. Capacity failure is not evidence of model/runtime incompatibility.

An alternative narrowing decision must name the retained question, exact
deferred/removed cells and comparison claims, approvers and reviewed revision,
and the acceptance criteria it changes. It requires the live #61 co-owners and
coordinator's explicit disposition; a general PR approval or the #7/#11 interface
receipt does not supply it. Until then the full criteria remain open.

Zwright8's receipt accepts actual prompt/cache/predicted lengths, active-sequence
versus queued-request accounting, runtime pins and separate allocator phases for
#7/#11. It supplies no new run or error bound. Appletechie's #7 and Mattycodes69's
#11 co-owner responses remain distinct. [Appletechie's #10 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221)
accepts the note-only placement policy and explicit headroom methodology at reviewed
main `66b46d4`; it explicitly accepts no runtime result, these new GM1 observations, another co-owner's scope
or future ResourceEstimate placement. Preserve
#59's single writer for `handoffs.md`/`handoffs.json`.

## Hardware required for full-scope continuation (2026-10-18)

[PR #200](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/200) delivered
the bounded accounting proposal and cohort-integrity guard to main at
`5df5c8c017a4bc775b0702e436eaa8b281bda339`. Its publication review does not
allocate experiment hardware. Identifying and authorizing the hardware path
for the existing full scope remains an action for
@Mattycodes69/@appletechie with @CompleteDotTech.

The following requirements are transcribed or derived from the existing dated
protocols, inspected 2026-10-18. These are not fresh availability observations
or measured fit claims. GiB = 2^30 bytes; MiB = 2^20 bytes.

| Coverage | Hardware and preserved limits | What is still needed |
| --- | --- | --- |
| D1–D5 dense reproduction | Original single RTX 5070 Ti / pinned CUDA runtime; [dense wrapper](../../scripts/mr09_run_matrix.ps1) requires one valid `nvidia-smi` sample and at least 2,048 MiB free before each run; the runner separately requires CUDA-reported free >=2 GiB. [Original protocol](measurements/mr09-protocol-2026-10-16.md) caps this process at min(2 GiB, 12.5% of reported device memory) | Fresh safe spare-capacity check and temporary artifact storage before any rerun; prior observations are already recorded, so rerunning them does not fill missing MoE/topology/comparison cells |
| Supplemental Granite3.1 GM1 | [Separate short-case protocol](measurements/mr09-granite31-protocol-2026-10-16.md): GPU free >=4,096 MiB; available physical host RAM >=12 GiB; temporary-volume free >=6,412,308,016 bytes; own allocator cap <=3 GiB. Recheck GPU guard before each of three serial fresh processes | Completed three bounded runs in the dated GM1 continuation below after fresh passing guards. GM1 is supplemental short MoE coverage only; it does not replace M1–M4 |
| OLMoE M1–M4 | [Pinned plan](measurements/mr09-moe-plan.json): BF16 resident weight tensors alone are 13,838,323,712 bytes. M1/M2: prompts 256/2,048, active1, BF16 KV; M3: prompt2,048, active2, BF16 KV; M4: prompt2,048, active1, INT4 if supported | Named authorized GPU allocation and reviewed process cap covering all resident experts, cache, prefill/routing workspace, allocator/context and explicit reserve. The existing 2 GiB dense cap cannot admit these weights. Full-resident and separately pinned offload designs are distinct scenarios |
| Long-context boundary | [Original protocol](measurements/mr09-protocol-2026-10-16.md) defers a larger 8,192-total-position boundary to a reserved session | Review the exact model/prompt/cache/predicted lengths with #7 and establish a safe device/host envelope before adding this cell. Pinned OLMoE has only 4,096 positions; do not apply the 8,192 boundary to it or deliberately cause contention/OOM on the shared device |
| G1 multi-GPU/per-rank | [Original matrix](measurements/mr09-protocol-2026-10-16.md): same pinned dense/MoE, prompt2,048, active2, native BF16 KV, 32 decode forwards; at least two authorized GPUs and an explicit per-rank placement/topology plan | Name each device and allocation, interconnect, parallelism strategy, runtime/backend and per-rank memory budget. Add separately hashed multi-rank instrumentation/protocol: the existing wrapper and [runner](../../scripts/mr09_measure.py) accept exactly one visible device and do not execute G1 |
| Matched estimator pairs | Same model/artifact, runtime, weight/KV precision, actual context, active sequences, offload/topology and measured quantity | Pin matching estimator execution/outputs and a reviewed decision tolerance. More GPU memory alone does not create a comparable pair or approve an error threshold |

For the OLMoE native BF16 case, the pinned geometry gives
`2 * 16 layers * 16 KV heads * 128 head_dim * 2 bytes = 131,072 bytes`
per cached token per active sequence. M3's terminal cache at
`(2,048 + 32) * 2` positions is therefore **545,259,520 bytes**.
Weights plus this cache are **14,383,583,232 bytes** before workspace,
allocator/library/context costs, loading transients, communication or reserve.
This is a derived payload floor, not a GPU capacity recommendation or measured
peak; it does not justify a particular 16/24/48 GB card or a new memory guard.
M4's packing/metadata/backend support must be checked separately.

OLMoE host-RAM and disk minima remain **unquantified**. Before authorizing that
session, pin shard file sizes/hashes, loader/offload strategy and simultaneous
host copies, then declare RAM and storage guards including metadata,
download/staging/copies and cleanup headroom. The index's tensor-byte count is
not an exact download/storage requirement. Do not reuse Granite3.1's smaller
guards for OLMoE or lower any existing profile's guards.

A reviewable hardware authorization must record the host/session owner and
location, device IDs/models/count and per-rank allocation, host RAM and temporary
storage budgets, exact model/runtime/driver/backend pins, permitted process caps,
topology, run/stop conditions and artifact retention/cleanup. Identify whether
the session uses existing spare local capacity or a newly approved reservation.
A second device, larger reservation/cap or paid compute needs explicit
authorization; this hardware checklist provides none of those permissions.
Keep pre-existing workloads untouched. No new probe, download or experiment
was performed to prepare this hardware checklist; the separate GM1 continuation below records subsequent execution.

## Offline evidence integrity and continuation guard (2026-10-18)

An independent read-only audit at main
`ecd5f66d758e8bf89eafbeacfe8eae87ce9b4999` matched all 15 result-file
SHA-256 values to the committed summary, matched instrument/protocol hashes to
the recorded sources, and independently recomputed all 480 phase/counter
`n/min/median/max` summary fields. It found no mismatch. It checked phase
uniqueness and allocator inequalities and found a consistent recorded
environment/hardware/artifact cohort. This was in-memory file/hash arithmetic,
not Python execution, new inference, current hardware inventory or validation
of downloaded model bytes. Original pilot/preflight caveats remain below.

The audit found a continuation defect: the summarizer's existing grouping pins
covered model/code/protocol/configuration but could pool successful repetitions
with changed environment, device conditions or artifact contents. The updated
[summarizer](../../scripts/mr09_summarize.py) compares recorded runtime/package,
allocator/device/driver and artifact identity pins before any optional
sanitization writes. It permits changing free-memory observations, timings,
artifact-list order and publication metadata. Early failures without discovery
metadata remain recorded and excluded from numerical aggregates.

Successful repetitions also pin the observed model geometry, tokenized workload
(including the prompt digest) and actual token counts. Matching requested
configuration alone cannot make different executed inputs one measurement
cohort. Missing observed inputs on a successful record are rejected; early
failures remain recorded without contributing numeric samples.

The [regression tests](../../tests/test_mr09_measure.py) cover mismatched cohorts,
allowed availability variation, early failures and unchanged reproduction of the
committed summary. These checks do not establish physical-device UUID identity,
artifact truth, estimator comparability or empirical calibration. The original
measurement instrument, dated protocol, raw observations and summary are unchanged.

### Counter and comparison intake boundary (2026-10-18)

An offline review of the summarizer at
[`09fc94e`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/09fc94e08075ce0180a77e62dfcda767abb74d48/scripts/mr09_summarize.py)
reproduced two input-validation failures using synthetic test records: arbitrary
`error_comparisons` lengths could be reported as comparable competitor pairs,
and a nonnumeric optional KV payload could become a byte statistic. The
[`current instrument`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/09fc94e08075ce0180a77e62dfcda767abb74d48/scripts/mr09_measure.py)
initializes an empty comparison list and implements no competitor intake.
Inspected 2026-10-18; these are code findings, not new empirical observations.

The summarizer now validates optional native/INT4 KV byte counters as nonnegative
integers and rejects malformed or nonempty successful-run comparison lists.
A future nonempty competitor comparison needs a separately reviewed intake
that establishes matching artifact/runtime/quantity pins and error arithmetic;
list length cannot supply that evidence. Failure diagnostics remain excluded
from numerical summaries. Nonfinite JSON constants are rejected anywhere in the
batch. All sanitized bytes, summary arithmetic and output serialization are
prepared before optional sanitization changes any input, so malformed later
failure metadata or an arithmetic overflow cannot rewrite earlier evidence.
This does not promise rollback after a publication I/O failure. Regression tests
preserve all input bytes on preparation errors and reproduce the committed
15-run summary unchanged. No error pair, estimator tolerance or additional
architecture coverage is created by this validation correction.

A follow-up review at
[`b7c9f07`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/b7c9f07e7ef82ac9ee80c974df86aee02575d2a2/scripts/mr09_summarize.py)
reproduced another raw-input ambiguity: duplicate status keys could become a
success and sanitization removed the contradictory original value. The reader
now rejects duplicate keys at every object level, including identical duplicates,
optional counters and non-numerical failure diagnostics, before any input rewrite.
Synthetic regressions check preservation of every original input byte with
sanitization both enabled and disabled. Existing measured observations, instrument
pins and the committed summary are unchanged; this is an input-integrity fix.

## Protocol and acceptance
- [x] Design dense and MoE measurement matrix
- [x] Vary context cache precision and concurrency (dense D1–D5; MoE variation remains a gap)
- [x] Measure peak allocated and reserved memory (executed dense cases; pending unexecuted cases)
- [ ] Report error bounds and failures without universal fit claims
- [ ] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain affected-owner review and accepted handoff.

## Next action
Review the new GM1 evidence, reconcile scoped receiving receipts and identify authorized capacity plus comparable estimator quantities before further experiments. Retain the full missing MoE/topology/comparison work unless the accountable owners explicitly narrow it. The original protocol checklist remains above, with completion claimed only where supported below.

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

## Supplemental GM1 execution — 2026-10-18

**Three successful fresh-process runs of one short MoE configuration**, in
addition to the historical 15 dense observations. These are separate cohorts,
not 18 repetitions of one experiment. Full #61 acceptance remains open.

Evidence: [passing capacity screen](measurements/mr09-granite31-preflight-2026-10-18.json),
[unchanged pre-execution protocol](measurements/mr09-granite31-protocol-2026-10-16.md),
[separate instrument](../../scripts/mr09_granite31_measure.py),
[three result files and summary](measurements/granite31-2026-10-18/),
[artifact ledger](measurements/granite31-2026-10-18/mr09-granite31-artifacts.json)
and [external artifact manifest](../../evidence/mr09-granite31-1b-a400m-instruct.json).
Access/measurement date: 2026-10-18. Evidence class: independent project allocator
observations; pinned publisher architecture/license metadata and local artifact
hash checks are separate support. Confidence is high for these recorded counters
and low for generalizing beyond this exact workload; human validity/reuse review
remains pending. No model weights, output text or user content are redistributed.

The pinned IBM Granite `granite-3.1-1b-a400m-instruct` revision is
`0da7a48b0276d500ce5922fd2b33944091fc6c09`. Downloaded safetensors were
2,669,283,096 bytes, SHA-256
`ac02591061f1344027a7e7b11dbb4143f75f166c47dc09b742f5de3ab1dde1d1`,
matching pinned publisher metadata before loading. Actual parameter elements:
1,334,628,352. All resident experts are included; active parameters alone do not
represent the resident weight allocation. The source locator, six file hashes,
size checks and publisher Apache-2.0 label are recorded in the linked manifests.

GM1 uses BF16 weights/native BF16 KV, 256 actual prompt tokens, one active
sequence, zero queued requests, 32 decode forwards, 33 greedy predictions and
288 terminal cache positions. SDPA/eager, seed 6109, TP1/PP1, no offload,
compilation or graph capture. Each process retains the protocol's **3 GiB
allocator cap**. The initial and every per-process screen passed unchanged
GPU >=4,096 MiB, available RAM >=12 GiB and temporary disk >=6,412,308,016-byte
guards. The instrument also checks CUDA free >=4 GiB before loading. No existing
workload was stopped and no guard/cap was relaxed.

Runtime: Python 3.12.11, PyTorch 2.10.0+cu130/CUDA build 13.0,
Transformers 5.0.0, Accelerate 1.13.0, Safetensors 0.7.0, NumPy 2.4.1,
Hugging Face Hub 1.3.5 and Tokenizers 0.22.2. One RTX 5070 Ti, native allocator,
driver **610.88**. The older dense driver was 595.97: these observations are
summarized in their own directory and never pooled with that cohort.
Both system GPU and CUDA memory samples are retained. For example, repetition 1
records 7,435 MiB free from `nvidia-smi` while CUDA reports 15,769,534,464 free
bytes. These disagree on this shared Windows device; neither is evidence of an
exclusive reservation, whole-device peak or safely available capacity for a
larger case. Passing guards is a bounded admission screen, not a fit guarantee.

| Phase | Peak allocated bytes, min / median / max (n=3) | Peak reserved bytes, min / median / max (n=3) |
| --- | --- | --- |
| Baseline | 0 / 0 / 0 | 0 / 0 / 0 |
| Loading | 2,669,257,728 / 2,669,257,728 / 2,669,257,728 | 2,675,965,952 / 2,675,965,952 / 2,675,965,952 |
| Warmup | 2,686,198,272 / 2,686,198,272 / 2,686,198,272 | 2,707,423,232 / 2,707,423,232 / 2,707,423,232 |
| Prefill | 2,711,454,720 / 2,711,454,720 / 2,711,454,720 | 2,740,977,664 / 2,740,977,664 / 2,740,977,664 |
| Decode | 2,697,602,048 / 2,697,602,048 / 2,697,602,048 | 2,740,977,664 / 2,740,977,664 / 2,740,977,664 |
| Steady state | 2,691,935,744 / 2,691,935,744 / 2,691,935,744 | 2,740,977,664 / 2,740,977,664 / 2,740,977,664 |

Identical extrema across three repetitions describe these samples only; they
are not a statistical confidence interval or universal bound. All three record
12,582,912 bytes of prefill KV payload and 14,155,776 terminal KV bytes. The
prefill geometry calculation matches the tensor payload (zero byte difference);
this excludes allocator/workspace/runtime costs and is **not** a competitor
sizing error. GM1 runtime failures/OOMs: zero. Comparable competitor/runtime
pairs across this contribution: **zero**. No accepted error threshold or
numerical competitor-error range is available.

An administrative shell readback failed after successful repetition 1 because
its JSON device-map key is empty. That recorded observation was retained and
validated; the wrapper readback used `ConvertFrom-Json -AsHashtable` for
repetitions 2 and 3. No observation was rerun, instrument changed or limit
increased. The instrument and protocol hashes are recorded in each result.

Reproduction requires the named authorized spare-capacity envelope and existing
pinned CUDA runtime; the following commands are a recipe, not fresh permission:

```powershell
# $CudaPython: pinned external Python; $ModelDir: fresh external task directory.
# $OutputDir: fresh result directory. Stop after any non-success or guard failure.
& $CudaPython scripts/mr09_granite31_measure.py --prepare --model-dir $ModelDir --output "$OutputDir/mr09-granite31-artifacts.json"
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed; stop' }
foreach ($rep in 1..3) {
  $resultPath = "$OutputDir/mr09-GM1-r$rep.json"
  & $CudaPython scripts/mr09_granite31_measure.py --model-dir $ModelDir --output $resultPath --repetition $rep
  if ($LASTEXITCODE -ne 0) { throw 'Run failed; stop' }
  $result = Get-Content -Raw -LiteralPath $resultPath | ConvertFrom-Json -AsHashtable
  if ($result.status -ne 'success') { throw 'Non-success; stop without retry' }
}
python scripts/mr09_summarize.py --directory $OutputDir --sanitize
```

Temporary task-owned weights/config/tokenizer files were removed after the
experiment; [cleanup receipt](measurements/granite31-2026-10-18/cleanup.json)
records the checked scope, byte/file counts and absent session directory.
Existing CUDA packages and unrelated artifacts were left intact. Published
results remove local filesystem paths and hardware UUIDs; pins/counters remain.

The varied OLMoE M1–M4, longer boundary, MoE INT4/concurrency, multi-GPU/per-rank
and matched llmfit/ModelFit/Local AI Planner comparisons remain unexecuted. This
single short cell supplies no waiver, approved tolerance, new device/cost
permission, ResourceEstimate, or compatibility rule. #7/#10/#11 owners and the
coordinator must review this new evidence separately from their earlier scoped
receipts. Frozen v1 and #59's handoff ledgers are unchanged.

## Historical executed dense results — 15 real runs (2026-10-16)

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

## Historical access screens and remaining architecture coverage

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
disk 7,418,503,168 bytes passed. Both historical failed Granite3.1 records are preserved;
no further GPU checks or MoE attempts were made in that 2026-10-16 submission. No workloads
were evicted and no Granite weights were downloaded in that historical session.
The separate 2026-10-18 GM1 execution above supersedes the no-execution state
for this short supplemental cell only.

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
| #7 | Actual prompt/cache/predicted-token counts, context and active concurrency differ from queue length | @zwright8, @appletechie | [Zwright8 narrowed acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6242699281) of accounting interface only; appletechie's disposition and empirical acceptance remain pending |
| #10 | Allocated/reserved phase peaks and KV-payload observations, with zero comparable competitor pairs | @Mattycodes69, @appletechie | [Appletechie scoped acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221) for the earlier note-only policy/headroom methodology; no runtime-result acceptance; new GM1 evidence, other co-owner disposition and future placement remain pending |
| #11 | Exact Transformers/CUDA/allocator pins, supported or failed optional cache backend and phase reset procedure | @zwright8, @Mattycodes69 | [Zwright8 narrowed acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6242699281) of runtime accounting interface only; Mattycodes69's disposition and empirical acceptance remain pending |

No ResourceEstimate, canonical catalog item, Pricebook or compatibility boolean
is manufactured. #40 remains the review entry for any contract/rule change;
v1 is unchanged. Agent reproducibility review can identify defects and support
the submission; it does not accept the above owner handoffs. #61 remains open
until its coverage, relevant evidence review and acceptance gates are met.
Automation checks structure, unit arithmetic, failure handling and consistency;
human reviewers still assess experimental validity, source accuracy, reuse
rights, freshness, completeness and evidence acceptance. The integrated
submission validation report records the repository checks separately.
