# MR-09 comparison specification — proposal 1, 2026-10-18

Refs #61. **Proposed for owner review; no estimator correction or new execution.**
Decision record: [sizing-validation.md](../sizing-validation.md). Base main:
`d761200a5dd94f069c2a7c94ac1bb4f9df67581b`. Live issue/owner readback and
existing receipts checked on 2026-10-18. This is a research protocol, not a
canonical schema, product sizing model, acceptance receipt or scope waiver.

## Decision and recommendation

Can an explicitly versioned estimator model the same device-buffer quantity,
artifact, output reservations and initialization stage as the qualified native
harness? Recommend a **supplemental initialization-buffer comparison** with
separate host-readback and device-graph output accounting. Retain #61's original
third-party peak-memory question and all its broader coverage requirements.
The owners must accept the supplemental target/candidate before any pair is
reported as accepted. Writing or merging this proposal does not provide that
acceptance, an error tolerance or permission to extend the native workload.

## Comparison tracks

| Track | Estimator quantity and observation | Present state / permitted conclusion |
| --- | --- | --- |
| Original #61 question | Exact third-party model/runtime/context/KV/concurrency estimate versus matching measured phase/device peaks; allocated and reserved counters stay separate | Zero accepted whole-runtime peak pairs. Existing dense/GM1 cohorts and named llmfit, ModelFit and Local AI Planner requirements remain; a snapshot cannot replace them |
| Proposed supplemental comparison | Modeled model + context/KV + compute device buffers at completed native initialization versus native CUDA0 managed-buffer snapshot | Candidate proposed below; no accepted total-buffer pair. Tests only this instrumented path and this quantity |
| Existing component check | Conventional two-byte KV payload at identical cached lengths/storage layout | Twelve bounded payload pairs remain separate. No total-memory, dtype numerics or backend-equivalence inference |

The original GPUStack v0.26.4 prediction is an **ineligible baseline**, not a
numerical error sample: its count agrees but its host-capacity/output-placement
semantics do not. A corrected project derivative must be labeled experimental
and separately versioned. Its results cannot be attributed to the unmodified
third-party release or counted as independent validation of that release.

## Proposed quantity and observation boundary

Use the existing research label `managed_device_buffers_snapshot`, in **bytes**,
at one synchronization point after model load, context/KV allocation and
scheduler/compute reservation, before freeing context/model. The native JSON
`fit_memory_breakdown.rows[kind=device,name=CUDA0].self` is the proposed primary
reference. Keep the exact default-buffer admission ledger as a corroborating
observation with its own instrumentation scope; do not silently substitute a
process-wide or high-water metric.

| Included | Excluded / separately reported |
| --- | --- |
| Actual model device buffers on CUDA0 | CPU-mapped embedding view and all host buffers, including CUDA_Host readback/compute |
| Allocated context/KV capacity, even with zero populated prompt positions | Driver/context/library allocations outside the reported buffers; other processes |
| Reserved scheduler/compute buffers at the effective graph-output capacity | Operator VMM/scratch paths reached during inference; no graph executes in this harness |
| The same allocator/accounting boundary on estimator and observation | Whole-device/process memory, transient peaks, throughput, headroom or a guaranteed-fit claim |

Native nonnegative buffer fields are independently floored to integer MiB.
For native self `s`, retain `[s*2^20, (s+1)*2^20-1]` bytes. Never sum rounded
components to reconstruct self. Signed `unaccounted` is excluded and negative
values truncate toward zero. The exact admission ledger must reconcile with
this interval before an observation is eligible; neither ledger nor rounded
self proves a physical process-wide cap. The separate host-output log uses
two-decimal rounding, not this integer-MiB flooring convention.

The historical default-buffer cap and free-callback wrapper instrument the
runtime. The wrapper changes CUDA identity detection/copy fast paths; a future
estimator must disclose whether its allocation model covers this instrumented
path. Unexplained buffer/copy-path effects leave the pair unmatched. Do not
claim equivalence to an ordinary uninstrumented runtime. Replacing the wrapper
or metric requires a new source/build/capture qualification and cohort.

## Development case and fixed controls

The following pins describe the already observed **development case**. They
are not a fresh hardware discovery, reservation or executable authorization.
Existing setup/preparation/capture/source records remain immutable.

| Control | Exact binding / required interpretation |
| --- | --- |
| GGUF | bartowski/SmolLM2-135M-Instruct-GGUF revision `09816acd5d99df7be770d85ea30822623dab342c`; SmolLM2-135M-Instruct-f16.gguf; 270,885,952 bytes; SHA-256 `f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57` |
| Original estimator | GPUStack gguf-parser-go v0.26.4, commit `637cd9a7a03993ab30ace3c53dd8af5c37f46a94`; official binary/output/argv pins retained in preparation.json |
| Runtime | llama.cpp b11669, commit `620d2225cc436ab0b001e3200e590e3b286ef9ab`; both archive and extracted DLL hashes in the existing runtime ledger |
| Executed native harness | Source `7805816b3b59f973ec9e87a03b8c807511641700`; executable SHA-256 `07c2f8587b58a6dbe557d7e7f395f765ec03c18122386f6456333338f832f09e`; exact compiler/header/source bindings in build-loader-v2.json |
| Historical device | CUDA0, RTX 5070 Ti, driver 610.88; CUDA API/archive-label discrepancy remains recorded, not resolved by this proposal |
| Context and batching | Total context capacity 512; logical batch 256; physical microbatch 256; reserved sequence capacity 1 |
| Placement | CUDA0 only; main GPU 0; split mode NONE; all 31 layers including output offloaded; mmap; extra/repacked buffer types disabled; host-mapped embedding remains disclosed |
| Cache / compute | F16 K/V; Flash Attention disabled; KQV/op offload enabled; four CPU threads; no backend samplers or embedding-output mode |
| Allocation / graph controls | `no_alloc=false`, `vocab_only=false`; CUDA graphs disabled in the child; native graph/graph-plan dispatch refused, not merely absent from a warmup setting |
| Execution stage | Initialization only; no warmup, decode/encode call or model graph dispatch; the fixed 8 MiB probe precedes model loading and is freed before capture |
| Capacity versus demand | One reserved sequence is not one active inference request. Zero prompts are processed and zero output tokens generated; the reserved graph size is not actual prompt length or generation budget |
| Historical results | Three fresh processes: native self 319 MiB, exact admitted live bytes 334,511,360 each, zero tracked bytes after cleanup. These observed development results are already known and are not held-out validation |

The original setup's `active_sequences: 1` field is preserved as historical
preparation metadata. For this initialization comparison the meaningful native
control is sequence **capacity**; no admitted request is demonstrated. Always
report capacity, populated cache positions, actual prompt tokens, active
requests and generated tokens separately. No fields in frozen v1 are changed.

## Output-reservation requirements for the correction

| Distinct concept | Required development-case semantics | Admission requirement |
| --- | --- | --- |
| Host readback | Constructor requests `output_reserve(n_seq_max)`; one logits row; embeddings/backend sampling outputs absent | Model actual enabled host-buffer terms separately; no unconditional embedding-output allocation and no device charge for host-pinned storage |
| Prompt graph output capacity | `min(min(n_ctx,n_ubatch),n_outputs_max)` = 256 rows | Treat as graph-allocation capacity even though no prompt executes |
| Global / per-sequence maxima | Effective `n_outputs_max=256`, `n_outputs_max_per_seq=1`; no backend samplers | Per-sequence sampling maximum must not reduce the sampler-free graph to one row |
| Projection computation | Output-weight backend CUDA0 for this ordinary llama architecture | Host readback location does not imply host computation; do not switch the artifact to eagle3 to force a different estimator branch |
| Aggregate device compute | Respect graph tensor shapes, backend placement, allocator alignment/lifetimes and scheduler reuse | A logical logits tensor is not an independent additive peak; document any unresolved approximation rather than promising exact allocation equivalence |

The known 196,608-byte host logits payload, 50,331,648-byte logical graph logits
tensor and 50,921,472-byte old modeled host footprint are **source-derived
geometry**, not newly measured buffers. None may be added to the old device
prediction as a correction calibrated to the known total. Keep the original
288,499,968-byte estimate unchanged and exclude it from numerical error admission.

A proposed local derivative may use a distinct label such as
`v0.26.4+mr09-output.1` **only after it exists**; this is not an upstream release
or a current result. Retain its upstream base, complete patch/source commit,
build compiler/dependencies, executable hash, command, effective controls and
raw output. Those identities are currently unavailable because no correction
is implemented. Default-inferred controls must be echoed with their pinned
source basis; missing/mismatched controls cannot be treated as a match.

**Source revision note — 2026-10-19:** The preceding paragraph records the
pre-implementation proposal. The [current derivative source](gguf-parser-mr09/README.md)
uses `gguf-parser-go-v0.26.4+mr09-output.2-experimental` for the split-count
allocation correction. Historical `.1` packages and predictions retain their
original identities and receipts. A `.2` build and any future prediction need
their own exact pins; the pair-admission and empirical requirements below remain
unchanged.

Before actual comparison, proposed synthetic CPU tests should distinguish
one-row host readback from 256-row graph reservation, preserve the global versus
per-sequence distinction without samplers, and reject the wrong output backend,
artifact/tuple drift and no_alloc projections. Label the derivative's supported
architecture/configuration scope; test that the original implementation fails
the targeted semantic fixture and the correction passes. Do not turn a generic
component formula test into proof of full allocator accuracy. Fixtures remain
under tests, and this proposal records no such test as already implemented.

## Pair admission and reporting

For every candidate prediction and observation, require the same artifact
bytes, full runtime/backend/source build, device/driver, effective controls,
output/placement semantics, managed-buffer boundary and capture stage. An
estimator describes the pinned runtime, not merely a model family. Bind exact
bytes parsed to checksums; reject duplicate JSON keys, non-finite/overflow
numbers, Boolean/numeric aliases, ambiguous CSV identity and contradictory
screens/events. Preserve inputs and existing outputs on rejection.

Keep these states distinct in research notes: proposed, unexecuted, failed,
unmatched, eligible-but-unaccepted and accepted with named scope/receipt.
A source patch, successful exit, matching field names or passing CI supplies
none of the other states automatically. Unknown evidence stays unknown.
A `no_alloc` sizing projection cannot qualify as an allocated observation; bind
`no_alloc=false` to the actual native build/capture, not an asserted log field
alone. No synthetic result enters real evidence or pair counts.

For a positive estimate `E` and positive observed byte interval `[L,U]`, propose:

- Signed byte difference: `[E-U,E-L]`, positive meaning overestimate.
- Absolute byte difference: zero minimum when `E` lies in `[L,U]`; otherwise
  the smaller endpoint magnitude; maximum is the larger endpoint magnitude.
- Signed relative percent: `[100*(E-U)/U,100*(E-L)/L]`.

Use exact integer/rational arithmetic and disclose the rounding interval.
This is resolution of an observation, not a confidence interval, tolerated error
or universal bound. Store each repetition separately; report min/median/max
only within the same cell/metric/cohort, without pooling dense, MoE, KV payload
or whole-process observations. Three repetitions do not turn one configuration
into three independent coverage cases. If an exact-ledger deviation is shown
secondarily, label it separately and require explicit agreement on its boundary;
it cannot replace the primary native-self interval without a recorded decision.

No tolerance is selected here. Co-owners/coordinator must record any decision
threshold and its purpose before evaluating future validation outputs. Until
then, even an eligible comparison supports descriptive differences only, with
no pass/fail, fit, default-headroom or ResourceEstimate claim. Accepted
estimator pairs and whole-process peak pairs remain zero in this proposal.

## Prospective validation cells and order

Freeze the correction's source/build and record predictions **before** looking
at new native captures. Preserve the known development case and the original
prediction separately. The following proposed cells are not executed or
reserved, and become held-out tests only when predictions/configurations are
frozen before their new observations. No blank result is filled with zero.

| Proposed cell | Total context | Logical / physical batch | Sequence capacity | Expected prompt-graph output capacity | Purpose |
| --- | --- | --- | --- | --- | --- |
| H1 | 256 | 128 / 128 | 1 | 128 | Change output rows independently of the known 256-row case |
| H2 | 1,024 | 256 / 256 | 1 | 256 | Change context/KV capacity while preserving graph-output rows |
| H3 | 512 | 256 / 256 | 2 | 256 | Change initial host readback/sequence capacity without claiming two active requests or doubling the total context |

These are proposed derived capacities under the pinned defaults; every actual
native getter/log value must be checked. Read back per-sequence context: H3
must not be advertised as 512 tokens per sequence just because total context is
512. Keep the same GGUF/F16 KV, single GPU, mmap, output-device placement and
other controls above unless a separately reviewed change is recorded.

The current native executable/launcher hard-code the development tuple and
must not be used to imply these cells ran. Any held-out native experiment needs
a separately pinned harness/build, qualified cap/allocation paths and capture
readback for that tuple. Propose three serial fresh-process repetitions per
admitted cell, each with the same fixed bounded probe and no model warmup or
generation. If safe spare capacity is unavailable, retain an unexecuted cell;
never reduce a guard, evict another workload or swap in a CPU result.

Keep the prior screens: GPU free >=4,096 MiB, available host RAM >=12 GiB,
temporary free disk >=6,412,308,016 bytes; native free >=4 GiB. Cap managed
requests at no more than min(2,136,809,472 bytes, 2 GiB, fresh device bytes/8).
A failed screen admits no launch. Persist native failure/timeout before bounded
post-run telemetry; failed or pending telemetry does not qualify a trial.
Retain all failures and stop rather than tuning settings and rerunning a cell
under the same identity. No hardware, paid compute, package installation or
execution is authorized by this proposal.

Inference/phase peaks require their own allocator-path coverage including VMM,
operator scratch and opaque-library limitations. An initialization admission
quota is not an inference/process-wide cap. No inference plan is executed or
silently approved here. Varied MoE, long-context and multi-GPU/per-rank cases
remain in the original #61 matrix and need their own authorized hardware and
measurement protocol; H1-H3 do not satisfy those requirements.

## Decisions requested and existing authority

| Decision | Proposed disposition | Required reviewers / current status |
| --- | --- | --- |
| D61-01: target and scope | Add the bounded initialization-buffer track; retain the original peak-memory question and named estimators | #61 co-owners Mattycodes69/appletechie, #10/#11 and coordinator CompleteDotTech; pending |
| D61-02: candidate identity | Treat a minimal versioned GPUStack derivative as an experimental project estimator; keep original output ineligible | Same affected owners/coordinator; candidate/version acceptance pending |
| D61-03: metric and exclusions | Native-self interval primary, exact admission ledger corroborating; disclose host and callback/copy-path exclusions; explicitly narrow the original proposal's broad no-host-fallback gate if accepting this track | #10 Mattycodes69/appletechie and #11 zwright8/Mattycodes69 with coordinator scope review; pending, no gate silently waived |
| D61-04: capacity semantics | Distinguish host rows, graph rows, sequence capacity, active requests and generation | #7 zwright8/appletechie with #11 runtime review; prospective controls pending |
| D61-05: validation and decision tolerance | Freeze prospective H1-H3 predictions before new observations; specify any tolerance before assessment | #61 co-owners/coordinator and #10; pending, no tolerance invented |

[Zwright8's earlier #7 acceptance with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561909720)
covers the exact **exclusion diagnosis**, not this replacement candidate or
prospective protocol. [CompleteDotTech's PR #267 approval](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5562100233)
accepts publication of bounded initialization research and source-derived
exclusion findings; it explicitly grants no replacement estimator, tolerance,
process-wide cap, other-owner acceptance or full #61 completion. #11 being
closed as research does not accept this new runtime comparison automatically.
Record every new disposition with reviewer, exact revision, date, accepted/
narrowed/rejected scope and remaining conditions. No receipt is pre-filled.

Recommendation: review these five decisions, then prepare the minimal source
correction and its synthetic CPU tests, keeping actual artifact/runtime runs
behind their separate evidence and resource gates. This contribution changes
no estimator, measurement, old launcher, schema, issue owner/triage or #59 ledger.
It publishes no CatalogItem, Pricebook, compatibility rule or ResourceEstimate;
#10 owns future consumption and #40 owns any contract change.

## Evidence and integrity reproduction

Sources accessed/read 2026-10-18. Primary-source interpretations retain their
pinned audit/rights limits; no new third-party source was downloaded here.

| Evidence | Locator / scope |
| --- | --- |
| Original issue and retained scope | [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61), live co-owners and criteria; repository metadata is not empirical acceptance |
| Historical estimator/tuple | [setup](total-memory-setup-2026-10-18/setup.json), [CPU command/output receipt](total-memory-setup-2026-10-18/preparation.json) and [original output](total-memory-setup-2026-10-18/gguf-parser-estimate.json) |
| Actual native development case | [qualification](native-qualification-2026-10-18/qualification.md), [build](native-qualification-2026-10-18/build-loader-v2.json), [runtime ledger](native-qualification-2026-10-18/runtime-artifacts.json) and [three-observation summary](native-qualification-2026-10-18/qualification-summary.json) |
| Source-derived mismatch and arithmetic | [matching narrative](output-reservation-2026-10-18/matching.md), [source audit with immutable publisher URLs/hashes](output-reservation-2026-10-18/source-audit.json), [bound report](output-reservation-2026-10-18/matching-report.json); MIT upstream source summaries, not new physical measurements |
| Metric/rounding arithmetic | [historical protocol](mr09-total-memory-protocol-2026-10-18.md#units-rounding-and-pairing-gates) and existing offline helper; no new metric enum is introduced |
| Existing component comparison | [dated execution/eligibility note](mr09-estimator-comparison-2026-10-18.md); original named tool limitations retained |

Existing integrity checks:

```powershell
python scripts/mr09_total_memory_setup.py
python scripts/mr09_native_capture.py
python scripts/mr09_output_reservation.py
```

These inspect retained evidence and arithmetic, not acceptance of this proposal.
The required repository workflow checks must also pass. Automation does not
establish physical validity, source truth/rights/freshness, independence from
known development observations, future hardware availability or owner consent.

## Submission validation — 2026-10-18

On the recorded base with this documentation-only proposal, Python 3.12.14 and
workflow-pinned requirements: 21 contract tests passed; 551 repository tests
completed (547 passed, four skipped: three Linux parent-death cleanup cases on
Windows and the absent portable C++ compiler case). Research, market,
handoff-audit and mobile validators and the three evidence helpers above pass.
Local links and whitespace pass. No helper, schema, fixture or existing CPU/
native evidence file is changed; no estimator or native GPU process ran.
These checks certify structure/arithmetic and retained record consistency,
not prospective comparison eligibility, source rights or any owner decision.
