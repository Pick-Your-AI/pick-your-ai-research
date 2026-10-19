# First prospective H1 buffer comparison — 2026-10-19

Refs #61. **One configuration, three fresh-process observations; technically
comparable experimental results, receiving-owner acceptance pending.**

The user authorized spare local capacity only. The [predeclared protocol](protocol.md)
retains the original issue scope and guards. The [prediction freeze](prediction-freeze.json)
was written at07:10:56.951244UTC and committed at `355765e` before the first
native observation at07:12:16UTC. No prediction was fitted after capture.

## Results and meaning

| Repetition | Estimator bytes | Native self byte interval, primary | Exact admission ledger, corroborating |
| --- | ---: | --- | ---: |
| H1-r1 | 300,885,760 | [300,941,312,301,989,887] | 301,674,752 |
| H1-r2 | 300,885,760 | [300,941,312,301,989,887] | 301,674,752 |
| H1-r3 | 300,885,760 | [300,941,312,301,989,887] | 301,674,752 |

Every native self value is **287MiB**, floored by the pinned logger. Its actual
integer-byte interval is287×2^20 through288×2^20−1; do not add separately rounded
components. The prediction is286.947021484375MiB. The exact ledger is
287.699462890625MiB, inside the primary interval in every trial.

Signed error means estimate minus observation. The primary signed interval is
**[−1,104,127,−55,552] bytes**, or approximately **[−0.3656172%,−0.0184594%]**.
Thus the prediction is low throughout the native rounding interval. The separate
ledger difference is−788,992bytes /−0.2615373%. The [summary](comparison-summary.json)
retains exact rational endpoints and each observation/hash. All three ledger
values are identical: min=median=max301,674,752bytes. This is observed resolution
and repetition, not a guaranteed error bound, confidence interval or fit test.
No cause is assigned from rounded component differences.

The native target is the initialized **managed CUDA0 device-buffer snapshot**.
The comparison includes device weights, allocated KV capacity and reserved
scheduler/compute buffers. It excludes host-mapped/readback/compute buffers,
opaque CUDA/library/context memory, other processes, transient peaks and
inference/VMM scratch. The free-callback wrapper changes CUDA identity/copy paths;
these are instrumented initialization observations. No graph, prompt, decode,
warmup or generation workload ran.

## Source, execution and safety evidence

- Actual artifact: [pinned SmolLM2 F16 GGUF](../../../../evidence/mr09-smollm2-f16-gguf.json),270,885,952bytes,
  SHA-256 `f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57`.
  Locally downloaded/verified2026-10-19. Publisher labels Apache-2.0; converter
  lineage remains unverified. No weights are redistributed.
- Estimator: [PR #474](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/474), exact source
  `7e97353beffaad7945189a1b953ad4b4f5a3aa56`, experimental project derivative of
  GPUStack `637cd9a7a03993ab30ace3c53dd8af5c37f46a94`. The original upstream
  output remains ineligible; this is not an accuracy claim for that release.
  [Windows build manifest](estimator-manifest.json), [source preparation](estimator-source-preparation.json),
  [explicit Windows wrapper adaptation](estimator-windows-adaptation.json),
  [20-field profile](estimator-profile.json), [raw prediction](estimator-prediction.json)
  and [receipt/aggregation terms](prediction-receipt.json) retain exact identities.
  Binary SHA-256 `00dedf6a4ca646e93552adaf56f8fdd754003c9d1440b5905c8128bbaa437b3c`.
  The unmodified published packet/patch/tests remain exact. Only preparation's
  tar-mode verification and Windows executable name were adapted separately.
- Runtime: llama.cpp b11669 / `620d2225cc436ab0b001e3200e590e3b286ef9ab`, exact
  [runtime artifacts](runtime-artifacts.json), [native build](build.json) and
  [losslessly serialized compiler output](build-log.json). Native executable
  SHA-256 `19bc3077df2137bddd30b7fff3189a4d6e2a462faab9f1f83d0e0cfed1188083`.
  Actual MSVC19.29.30153/linker14.29.30153.0; Go1.22.9 Windows/amd64. Toolchains
  and archives stayed in task-only storage; installed inference environments
  and drivers were unchanged.
- Actual readback: context/per-sequence context256, logical/physical batch128,
  sequence capacity1, global graph outputs128/per-sequence maximum1,31/31 layers
  offloaded, F16 K/V, mmap. Separate host output0.19MiB and host compute1.44MiB
  remain excluded. These capacity values are not active requests or populated
  cache positions. [Source/control review](semantic-review.json) preceded capture;
  independent postcapture review checked the full logs and matching semantics.
- Safety: fresh nvidia-smi free8,451/8,465/8,508MiB, host RAM at least
  25,082,621,952bytes, disk at least27,579,523,072bytes. All unchanged guards
  passed before each process. Native CUDA reports a different device-free value;
  neither report is a reservation or isolated process usage. Cap2,136,809,472bytes;
  actual live/peak admitted301,674,752bytes; zero tracked bytes after cleanup.
  The fixed8MiB probe was freed, cap+1 was rejected before forwarding, and the
  intentional graph probe was refused. Model graph dispatches0. No failed launch,
  runtime error, OOM, retry, workload eviction, power change or paid compute occurred.

The three [raw records](H1-r1.json), [second](H1-r2.json), [third](H1-r3.json)
retain full sanitized native traces and separate preflight/checksum bindings.
An exact-path Git attribute preserves the original captured CRLF preflight
bytes; no postcapture checksum or measurement normalization is hidden.

## Reproduction, review and remaining scope

`python scripts/mr09_local_compare_report.py` reproduces offline identity,
chronology, guard, capture and exact arithmetic checks. It starts no GPU process.
The launcher deliberately refuses occupied repetitions. A future physical cohort
requires its own declared output path, source/build identities, prediction freeze
and fresh guards; these three records cannot be overwritten to create a rerun.

[Validation](validation.md) retains the original non-green Windows full-suite
result separately from successful hosted validation and the scoped UTF-8 check.
The new Windows estimator run independently reproduced the original three
semantic failures, then passed5 Go methods/37 subcases and10 CLI cases; module
verification and embedded build information were retained. The preparation
helper ran with Python optimization1, while its CLI child actually recorded0;
no optimization1 CLI result is claimed for this Windows execution.

Root and independent in-session reviewers checked source/control matching,
actual raw captures, freeze chronology, all guards, cleanup and exact arithmetic.
This is review of the actual execution, not another physical reproduction or a
separate-account approval. Existing named-owner dispositions retain their scopes.
Request #61/#10/#11 and #7 receiving review plus coordinator evidence review for
this exact new package. Accepted pairs remain0 until that disposition.

Whole-runtime peak pairs remain0. These three technically matched supplemental
observations do not complete the original three empirical criteria: context/KV/
concurrency and varied MoE coverage, allocated/reserved peak coverage, and
qualified whole-runtime error/failure reporting. No tolerance, default reserve,
ResourceEstimate, compatibility rule or issue/Project completion is published.
