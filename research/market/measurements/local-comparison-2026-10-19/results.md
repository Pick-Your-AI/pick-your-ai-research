# First prospective H1 buffer comparison — 2026-10-19

Refs #61. **One configuration, three fresh-process observations; technically
comparable experimental results with a bounded supplemental receiving disposition
recorded below.**

The user authorized spare local capacity only. The [predeclared protocol](protocol.md)
retains the original issue scope and guards. The [prediction freeze](prediction-freeze.json)
was written at 07:10:56.951244 UTC and committed at `355765e` before the first
native observation at 07:12:16 UTC. No prediction was fitted after capture.
These retained times and Git history establish the recorded ordering; they are
not an independent attestation of the host clock or physical process.

## Results and meaning

| Repetition | Estimator bytes | Native self byte interval, primary | Exact admission ledger, corroborating |
| --- | ---: | --- | ---: |
| H1-r1 | 300,885,760 | [300,941,312,301,989,887] | 301,674,752 |
| H1-r2 | 300,885,760 | [300,941,312,301,989,887] | 301,674,752 |
| H1-r3 | 300,885,760 | [300,941,312,301,989,887] | 301,674,752 |

Every native self value is **287 MiB**, floored by the pinned logger. Its actual
integer-byte interval is 287×2^20 through 288×2^20−1; do not add separately rounded
components. The prediction is 286.947021484375 MiB. The exact ledger is
287.699462890625 MiB, inside the primary interval in every trial.

Signed error means estimate minus observation. **For managed buffers only**, the
primary signed interval is
**[−1,104,127,−55,552] bytes**, or approximately **[−0.3656172%,−0.0184594%]**.
Thus the prediction is low throughout that managed-buffer rounding interval;
the relative-error denominator is the observed value. The separate
ledger difference is −788,992 bytes / −0.2615373%. The [summary](comparison-summary.json)
retains exact rational endpoints and each observation/hash. All three ledger
values are bit-identical: min=median=max = 301,674,752 bytes. This is repeatability
at the retained resolution for one configuration, not a variance estimate,
guaranteed error bound, confidence interval or fit test.
No cause is assigned from rounded component differences.

The native target is the initialized **managed CUDA0 device-buffer snapshot**.
The comparison includes device weights, allocated KV capacity and reserved
scheduler/compute buffers. It excludes host-mapped/readback/compute buffers,
opaque CUDA/library/context memory, other processes, transient peaks and
inference/VMM scratch. The free-callback wrapper changes CUDA identity/copy paths;
these are instrumented initialization observations. No graph, prompt, decode,
warmup or generation workload ran.
The [first CUDA0 breakdown](H1-r1.json) separately reports `unaccounted: 1265` MiB.
That logger category is outside the managed-buffer comparison; it does not
establish isolated process usage, a whole-runtime peak or a default reserve.

## Source, execution and safety evidence

- Actual artifact: [pinned SmolLM2 F16 GGUF](../../../../evidence/mr09-smollm2-f16-gguf.json),270,885,952 bytes,
  SHA-256 `f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57`.
  Local download and SHA-256 match recorded 2026-10-19. This is source-checked
  evidence under [the accepted source policy](../../../T0-configuration/catalog-data-sources.md),
  not a verified provenance grade. Publisher labels Apache-2.0; converter lineage
  remains unverified. No weights are redistributed.
- Estimator: [PR #474](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/474), exact source
  `7e97353beffaad7945189a1b953ad4b4f5a3aa56`, experimental project derivative of
  GPUStack `637cd9a7a03993ab30ace3c53dd8af5c37f46a94`. The original upstream
  output remains ineligible; this is not an accuracy claim for that release.
  The captured output is explicitly `gguf-parser-go-v0.26.4+mr09-output.1-experimental`.
  This derivative already separates initial host readback from device output
  computation following the [#267 matching diagnosis](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267)
  and [source interpretation](../output-reservation-2026-10-18/matching.md).
  Its H1 prediction preceded these H1 observations; this was not a blind test of
  the unchanged upstream release. The later `.2` source/package is separate and
  is not substituted for the captured `.1` executable or prediction.
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
  Actual MSVC 19.29.30153/linker 14.29.30153.0; Go 1.22.9 Windows/amd64. The downloaded
  Go toolchain, archives and generated binaries stayed in task-only storage;
  the existing MSVC installation, inference environments and drivers were unchanged.
- Actual readback: context/per-sequence context 256, logical/physical batch 128,
  sequence capacity 1, global graph outputs 128/per-sequence maximum 1, 31/31 layers
  offloaded, F16 K/V, mmap. Separate host output 0.19 MiB and host compute 1.44 MiB
  remain excluded. These capacity values are not active requests or populated
  cache positions. [Source/control review](semantic-review.json) preceded capture;
  independent postcapture review checked the full logs and matching semantics.
- Safety: fresh nvidia-smi free 8,451/8,465/8,508 MiB, host RAM at least
  25,082,621,952 bytes, disk at least 27,579,523,072 bytes. All unchanged guards
  passed before each process. Native CUDA reports a different device-free value;
  neither report is a reservation or isolated process usage. Cap 2,136,809,472 bytes;
  actual live/peak admitted 301,674,752 bytes; zero tracked bytes after cleanup.
  The fixed 8 MiB probe was freed, cap+1 was rejected before forwarding, and the
  intentional graph probe was refused. Model graph dispatches 0. No native model
  launch failed; no runtime error, OOM, retry, workload eviction, power change
  or paid compute occurred.

The retained preflight records use the inherited identifiers `profile:"granite31"`
and `admitted_to_download_screen_only`. Those are labels of the reused capacity
screen, not the identity of this SmolLM2 H1 model or evidence that download-only
screening authorizes an unrestricted native run. The recorded numerical guards,
freshness, pinned H1 controls and separate native cap remain the actual checks;
the original labels and captured bytes are preserved.

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
semantic failures, then passed 5 Go methods/37 subcases and 10 CLI cases; module
verification and embedded build information were retained. The preparation
helper ran with Python optimization 1, while its CLI child actually recorded 0;
no optimization 1 CLI result is claimed for this Windows execution.

The prospective admission unit tests use synthetic files and mocked driver,
preflight and native responses. Their fixture root is resolved to the same
physical namespace as the production launcher, including when a temporary
directory parent is an alias such as macOS `/var` → `/private/var`. The original
admission assertions remain enabled on every platform; an additional directory-alias
regression skips only when Windows explicitly denies symlink privilege
(`winerror 1314`). The `.exe` fixture names do not execute Windows binaries or
justify skipping the suite on other platforms. These tests qualify the fixture
and admission behavior, not another hardware measurement.

Root and independent in-session reviewers checked source/control matching,
actual raw captures, freeze chronology, all guards, cleanup and exact arithmetic.
This is review of the actual execution, not another physical reproduction or a
separate-account approval. Existing named-owner dispositions retain their scopes.
The [07:58:08 UTC receiving review5568505386](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/476#pullrequestreview-5568505386)
at `df877a7030849fca939cc7e257be972100006e45` accepts these three observations as
supplemental, note-only initialization-buffer evidence for the bounded #61 → #7,
#10 and #11 interfaces. It is CompleteDotTech's actual delegated in-session
engineering disposition, not a named historical co-owner's reply or a broader
acceptance of the runtime. Its conditions and unchanged accepted-pair counter
are also recorded in the [current sizing note](../../sizing-validation.md#spare-local-h1-initialization-comparison--2026-10-19).
Accepted pairs remain 0.

The prospective reservation/failure-fence and four-guard source-binding findings
were corrected separately by [#480](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/480)
and received in [ad70da8](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/ad70da8423b72a7afc5c1c1769a4f12567750831).
Future cohorts use the [prospective admission route](../h1-prospective-admission.md).
The original thirteen-file freeze still omits four delegated guard bindings;
the correction does not backdate a new freeze or enlarge the historical capture
qualification. [Appletechie's later review5570207495](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/476#pullrequestreview-5570207495)
is a separate postmerge COMMENT with no required follow-up; these fixture/prose
clarifications preserve that disposition and add no physical observation.

Whole-runtime peak pairs remain 0. These three technically matched supplemental
observations do not complete the original three empirical criteria: context/KV/
concurrency and varied MoE coverage, allocated/reserved peak coverage, and
qualified whole-runtime error/failure reporting. No tolerance, default reserve,
ResourceEstimate, compatibility rule or issue/Project completion is published.

After capture, publication checks and independent verification, [cleanup](cleanup.json)
removed only the explicitly verified task directory:17,144 files/2,050,616,677
bytes, with target absence read back. No model, executable, SDK, header cache or
temporary validation environment remains from this session. Existing installed
toolchains, inference environments, drivers and unrelated workloads were preserved.

## Offline receipt type correction — 2026-10-25

The offline report now compares the recomputed native-validation receipt with
JSON-type-sensitive equality. Its integer byte counters, interval endpoints and
zero cleanup/dispatch counters cannot be replaced by Boolean or floating-point
aliases. Object-member order remains irrelevant, while array order, field
presence and values remain part of the receipt identity.

A synthetic copy of this cohort reproduced the previous false match through
the ordinary `summarize()` API: changing only the copied first trial's
`cleanup_live_bytes` to `false` and `model_graph_dispatches` to `0.0` still produced
three technical pairs. No integrity, native-readback or chronology check was
mocked or disabled. The regression tests alter only temporary copies and also
exercise all three trial positions, reordered members and correction/retry.
The existing historical report remains byte-identical; captured inputs, native
traces, source freezes and launchers are unchanged. This software correction
adds no measurement, accepted pair, fit decision or empirical criterion result.
