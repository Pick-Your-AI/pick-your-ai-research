# Estimator output-reservation matching — 2026-10-18

Refs #61. **The pinned pair does not match output-buffer semantics.** The
estimator and runtime both select 256 prompt-graph output rows, so the count
question is resolved. Their host readback capacity and output-computation
placement differ. The existing totals are not admitted as an estimator error
comparison. Accepted estimator pairs and whole-process peak pairs remain zero.

This is a source audit and offline readback of the three existing native
initialization trials. No estimator binary, model weights or native runtime was
downloaded or executed in this continuation. Only small pinned source files were
read; source copies are removed with the linked cleanup receipt. The original
CPU estimate, native captures, source/executable pins, historical timestamps and
published measurements remain unchanged. Native evidence is still offered for
owner review in #267, not treated as accepted merely because it exists.

## What matches and what fails

| Quantity | GPUStack v0.26.4 source model | llama.cpp b11669 initialization | Finding |
| --- | --- | --- | --- |
| Prompt graph output rows | `min(context 512, ubatch 256)` = 256 | `min(n_tokens = 256, n_outputs_max = 256)` = 256; recorded graph reservations confirm 256 | Cardinality matches for this exact case |
| Per-sequence output maximum | No dedicated setting in inspected CLI/option type | 1, separately from global maximum 256; no backend samplers installed by harness | Does not reduce the reserved prompt graph to one row |
| Initial host readback rows | 256; footprint includes vocabulary and embedding-width terms | `output_reserve(n_seq_max)` with `n_seq_max = 1`; logits enabled, embeddings disabled, no backend sampler | Initial host capacity differs |
| Output computation placement | Host device index 0 for ordinary `llama`; device exception restricted to `eagle3` | Output-weight backend is CUDA0; native graph builds output projection from those weights; scheduler prefers weight backend | Source-based placement expectation differs; no new per-tensor allocation trace is claimed |
| Target device total | Original modeled 288,499,968 bytes | Original admitted 334,511,360 bytes; native self interval retained separately | Different output semantics prevent numerical error admission |

The model's architecture is `llama`, vocabulary 49,152 and embedding width 576,
from the exact hash-bound CPU GGUF record. It does not enter the estimator's
`eagle3` exception. Inspection covered the pinned registered CLI flags and
estimate-option fields: there is no dedicated output-reservation row/placement
control. `--raw` emits GGUF file information and skips estimation; it does not
expose a different output-capacity estimate. Batch/context/offload/tensor
changes would change the reviewed tuple and cannot be applied to old captures.

The estimator's own [architecture rationale](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_architecture.go#L1461)
and [output-placement rationale](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_estimate__llamacpp.go#L1487)
assume an ordinary decoder reserves a single graph output. That assumption is
stale for the pinned b11669 [prompt-graph reserve](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/llama-context.cpp#L770),
which requests 256 here, and differs from the estimator's own `nOutputs = nTokens`
count. This identifies a concrete version-specific modeling defect; it does not
measure its full numerical effect or establish a correction for other versions.

## Host readback is distinct from graph output

The native constructor initially asks `output_reserve` for one active sequence.
With embeddings and backend samplers absent, the source-derived logits payload
is **49,152 × 1 × 4 = 196,608 bytes**. Every existing trial logs
`CUDA_Host output buffer size = 0.19 MiB`, consistent with that payload. The name
`CUDA_Host` denotes a host buffer, not device VRAM. The two-decimal log has a
rounding enclosure of [0.185,0.195] MiB; it is not an exact-byte observation and
is unrelated to the native JSON logger's integer-MiB flooring rule.

The runtime separately reserves its prompt graph with 256 output rows. Its
`n_outputs_max_per_seq=1` affects backend-sampling chains; with no backend
samplers the reserve helper assigns remaining requested outputs to sequences
without samplers. It therefore does not collapse this graph's 256 outputs.
The recorded graph-reservation lines corroborate that reading. A graph reserved
for hypothetical prompt processing does not show that a prompt was executed:
all three model initialization trials still have zero model graph dispatches
and zero generation.

At this shape the logical F32 graph logits tensor is
**49,152 × 256 × 4 = 50,331,648 bytes (48 MiB)**. This is source-derived tensor
geometry, not a measured allocation, allocator high-water mark or an additional
buffer to add to the captured total. Allocation alignment, live ranges,
scheduler reuse and other tensors affect aggregate compute storage.

The estimator's separately modeled host output footprint includes both
vocabulary and embedding-width terms:
**(49,152 + 576) × 256 × 4 = 50,921,472 bytes**. Its output-computation term is
also charged to the host for this architecture. Keeping a host readback buffer
in system memory does not imply that the graph's output-projection computation
belongs there. This source interpretation explains the matching failure; it
is not a claim that the full difference between totals has been causally
accounted for. Do not add 48 MiB or the estimator's whole host term to the old
device estimate and label the result an upstream prediction.

## Source and evidence binding

[Source audit](source-audit.json) records public immutable URLs, access time,
whole-file SHA-256/size and inspected line ranges with fragment hashes. Source
interpretations are authored findings, not automatically proven by checksums.
The [matching report](matching-report.json) binds exact original setup,
preparation, estimator output, three native captures, native summary and source
audit bytes. It distinguishes observed readbacks from source-derived geometry
and records the failure explicitly. Primary MIT source is summarized without
committing downloaded source copies or binaries.

Primary sources accessed 2026-10-18:

- GPUStack pinned [output count](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_estimate__llamacpp.go#L914) and
  [host footprint](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_estimate__llamacpp.go#L944),
  [output-computation placement](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_estimate__llamacpp.go#L1464),
  [architecture predicate](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_architecture.go#L1460),
  [CLI](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/cmd/gguf-parser/main.go#L57)
  and [option fields](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_estimate_option.go#L12).
- llama.cpp pinned [constructor host reserve](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/llama-context.cpp#L461),
  [prompt graph reserve](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/llama-context.cpp#L770),
  [host buffer sizing/placement](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/llama-context.cpp#L2227),
  [output assignment](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/llama-context.cpp#L2594),
  [llama model output graph](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/models/llama.cpp#L231)
  and [scheduler weight placement](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/ggml/src/ggml-backend.cpp#L1099).

The scheduler statement is a source-based expectation combined with recorded
31/31 layer offload, not an independent per-tensor allocator measurement. The
three whole-buffer captures remain the bounded physical observations. Confidence
is high for pinned-source transcription and arithmetic; empirical accuracy and
receiving acceptance remain unestablished. Sources are version-bound, not a
claim about all newer releases or other architectures/backends.

## Matching path and retained gates

The next estimator candidate must separately model **host readback rows** and
**device graph output rows/placement** for this exact ordinary decoder. Preserve
context 512, batch/ubatch 256, sequence 1, F16 K/V, Flash Attention disabled, output
layer CUDA0, extra buffer types disabled and initialization-only stage. A
versioned estimator correction or another independently pinned implementation
needs review before producing a new prediction. Its tests should distinguish
one-row host readback from 256-row graph reserve, cover ordinary-decoder device
projection, and avoid conflating graph capacity with generated tokens.

Then inspect remaining allocation alignment/scheduler/compute assumptions,
retain the new prediction's source/binary/command identity, and request the
owners' decision on a managed-buffer snapshot comparison. Merely matching a
count, changing the architecture to `eagle3`, moving actual runtime weights,
adding a platform allowance, or applying a post-observation add-back cannot
repair the original estimate's semantics. Reducing native output capacity would
require a separate source/build, cap/capture qualification and new cohort;
it cannot relabel the existing three trials.

#61 co-owners Mattycodes69/appletechie and #10/#11 review estimator/quantity and
runtime scope; #7 reviews capacity/output semantics; CompleteDotTech retains
coordinator evidence and tolerance review. [Zwright8's scoped #7 disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561909720)
accepts with constraints the matching diagnosis as an exclusion gate for this
exact pair. It does not accept a replacement estimator, measured fit, tolerance
or native process-wide cap. [Appletechie's source review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561985132)
corroborates the diagnosis but explicitly does not supply #7/#10/#11 or
coordinator acceptance. Remaining co-owner/consumer and coordinator decisions
remain separate; no broader receiving receipt is inferred. Inference/VMM/scratch, opaque-library and process-wide caps,
whole-process peaks, broader MoE/concurrency/multi-GPU coverage, named original
estimator requirements and ResourceEstimate placement remain separate gates.
Frozen v1, issue ownership/triage and #59 handoff ledgers are unchanged.

Offline integrity reproduction:

```powershell
python scripts/mr09_output_reservation.py
```

Optional fresh source copies with exactly the names/URLs in source-audit.json
can be checked using `--source-directory PATH`; this only verifies bytes and
fragment identities. Automation does not execute an estimator or native graph,
prove source interpretations or supply empirical acceptance. See
[validation](validation.md) and [source-copy cleanup](cleanup.json).

[Current-main integration and evidence-review disposition](review-completion.md)
records subsequent corrections and preserves the earlier validation scopes.
