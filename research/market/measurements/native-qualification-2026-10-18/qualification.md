# Native cap, CUDA and capture qualification — 2026-10-18

Refs #61. **Three real initialization-only trials completed; receiving review
and accepted estimator comparison remain outstanding.** This continuation
qualifies a specific managed-buffer boundary, not a process-wide GPU cap,
VMM/scratch inference paths or total-memory accuracy. Existing dense/GM1 and
CPU-estimator preparation records are unchanged.

The user requested this qualification continuation. No paid compute, additional
device, driver/package installation, workload eviction or model generation was
used. #61 co-owners @Mattycodes69/@appletechie, #7/#10/#11 receivers and coordinator
@CompleteDotTech retain evidence/quantity/scope/tolerance review. These trials do
not provide their receiving receipts or a scope waiver.

## Observed results and exact scope

| Check | Observed evidence | Qualified boundary / remaining limit |
| --- | --- | --- |
| Native admission counter | Compiled CPU fixtures: exact-limit success, one-byte/overflow rejection, rollback/underflow handling, 8 threads and 16,000 successful concurrent admissions | Counter arithmetic/admission mechanism; synthetic fixtures stay under `tests/native/`, not GPU measurement evidence |
| Actual CUDA/backend probe | 8,388,608-byte CUDA0 buffer allocated, cleared/synchronized and freed; request cap+1 rejected without a second native allocator call | Exact pinned backend's default buffer allocator, before native allocation. This is an admission rejection, not an induced device OOM |
| Graph boundary | One intentional graph-dispatch probe rejected before native dispatch; zero additional graph attempts during each model/context initialization | No decode/encode API is loaded. Graph execution, CUDA graph scratch and VMM pools remain unqualified and disabled for this harness |
| Capture | Native CUDA0 `self=319 MiB`; admission ledger **334,511,360 live bytes** in each of three processes | Same nonnegative managed-buffer total reconciles within native rounding. No CUDA context/library/driver or whole-process peak claim |
| Cleanup | Tracked live buffers 0 after every probe and model/context cleanup; child exits | Only this child's resources; no other workload is altered |

| Trial | Cap bytes | Exact admitted live / peak buffer bytes | Native self byte interval | Model graph dispatches | Final tracked bytes |
| --- | --- | --- | --- | --- | --- |
| 1 | 2,136,809,472 | 334,511,360 / 334,511,360 | [334,495,744, 335,544,319] | 0 | 0 |
| 2 | 2,136,809,472 | 334,511,360 / 334,511,360 | [334,495,744, 335,544,319] | 0 | 0 |
| 3 | 2,136,809,472 | 334,511,360 / 334,511,360 | [334,495,744, 335,544,319] | 0 | 0 |

Each fresh child performs the same fixed 8 MiB probe and frees it **before**
loading the model. There is no model warmup or token generation; these are not
cold CUDA-context observations. All repeated values describe these samples,
not confidence bounds or guaranteed fit. The native row's model/context/compute
values are 256/11/51 independently truncated MiB, which sum to 318 while self is 319:
do not reconstruct self by adding rounded components.

[Qualification summary](qualification-summary.json) hashes all three published
records. Each links a fresh GPU/RAM/disk preflight, exact executable/source ref,
launcher, model hash and runtime ledger. Original screen limits remain GPU
>=4,096 MiB, RAM >=12 GiB, disk >=6,412,308,016 bytes. The native child separately
requires CUDA-reported free >=4 GiB and clamps the cap to min(the historical
2,136,809,472-byte envelope, freshly reported device bytes/8). Windows CUDA and
system GPU free figures still disagree; neither supplies an exclusive reservation
or additional safe capacity. No guard/cap was relaxed.

## CUDA and runtime identity

The two **b11669** archives and every extracted file were locally checked;
[runtime ledger](runtime-artifacts.json) retains exact hashes. Both official
archive digests match the publisher. Actual device: RTX5070Ti / CUDA0,
compute capability12.0, driver **610.88**. Native backend loading, device buffer
allocation/clear and three actual F16 model/context initializations succeeded.
This is narrower than matrix kernels, throughput, every CUDA13.4 feature, or
future driver compatibility.

The archive names advertise CUDA13.4; bundled cudart file version is
`6,14,11,13040`, but both `cuDriverGetVersion` and the bundled dynamic
`cudaRuntimeGetVersion` queries returned **13030**. The loaded dynamic DLL path
and hash were verified against the pinned directory. These observations are
retained in [cuda-versions.json](cuda-versions.json); their cause is not inferred.
The native ggml-cuda binary statically links its runtime, so a query against the
separate dynamic cudart does not establish the version of that static runtime.

[NVIDIA release notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html),
accessed2026-10-18, state CUDA13.x minor compatibility has a minimum driver branch
580; CUDA13.4 new features/platforms can require R615. The actual initialization
probe is the evidence for this narrow workload. Neither the archive label nor
that compatibility table replaces runtime testing. No driver was changed.

## What the cap enforces

[Project-owned native quota](../native/mr09_quota.hpp) reserves requested bytes
under a mutex **before** forwarding to the backend allocator, counts in-flight
reservations, rolls back failed allocations and releases charges after native
free. The initialization harness replaces the CUDA0 default buffer-type
allocation callback in its own child process; the pinned implementation forwards
that requested size unchanged to its device allocator. It checks returned size,
tracks each buffer/free callback and verifies zero outstanding records on exit.

The harness disables extra/repacked buffer types, requests only CUDA0 and
single-device split mode, and guards every CUDA backend created through the
selected device interface by refusing graph/graph-plan compute. It does not
load a decoder API. Model/context allocation and scheduler reservation can
therefore be qualified without executing a GPU graph. `GGML_CUDA_DISABLE_GRAPHS`
is set only in the child, as supported by the pinned backend source.

This is a cap on the **initialization-only default managed buffer requests**.
It is not a general hook over all driver allocations. Native VMM scratch pools
and library-internal allocations are not covered by this callback. Graph work
which could enter those operator scratch paths is refused before dispatch;
inference stays disabled. Do not reuse this harness as an inference cap or
claim that all memory charged by Windows/CUDA is bounded by it. Extending the
workload requires a new source/build and allocation-path qualification, including
VMM/scratch/library scopes as applicable. `--fit-target` is not substituted for
this boundary, and no global API injection or driver patch is used.

## Capture and effective settings

[Native harness](../native/mr09_native_init.cpp) uses pinned public model/context
headers and the native backend-interface header. Existing MSVC2019 Build Tools
14.29.30133 compile it without installing a CUDA toolkit or changing system
packages. [Build receipt](build-loader-v2.json) pins headers, project sources,
flags, executable and the retained source commit. Only that frozen executable
was used for the successful probe and all three model trials. Later source edits
must create a new record/cohort; PE binaries are not assumed bit-reproducible.

For each model case: same verified F16 GGUF SHA-256
`f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57`,
context512, batch/ubatch256, one sequence, F16 K/V, Flash Attention disabled,
mmap, offload31 (30 blocks + output), threads4, no extra buffer types,
no model warmup/generation. Native logs confirm mmap,31/31 layers offloaded,
512 KV cells and F16 K/V. Disabling alternate buffer types is an explicit
instrumentation choice, not an implied property of all standard llama.cpp runs.
The runtime retains a 54 MiB CPU-mapped token embedding view and host output/
compute buffers; those are logged and excluded from the CUDA0 device target.
31/31 layer offload does not mean all tensors or all process memory are on GPU.
The original proposal's broad no-host-fallback gate is therefore not treated as
satisfied or waived by these initialization observations.

**New target-affecting readback:** the runtime reports `n_outputs_max=256` and
`n_outputs_max_per_seq=1`, and reserves a graph with up to256 outputs. The prior
estimator CLI did not expose these as explicit arguments. Reconcile its output
reservation/compute assumptions with these exact observed defaults before a
numerical error comparison. No matching setting is invented or changed after
seeing these three captures. This is one reason accepted estimator pairs remain0.

The harness calls the pinned native `common_memory_breakdown_print` export,
with JSON logging enabled and flushed before freeing context/model. The native
event reports `unit=MiB` and **nonnegative self/model/context/compute values
floored to integers**. Negative signed `unaccounted` values instead truncate
toward zero in C++; the positive-self interval arithmetic is unchanged.
The exact admission-ledger live bytes lie inside the native self interval in
all three trials, providing a capture cross-check without relabelling a rounded
value as an exact measurement.

The [capture validator](../../../../scripts/mr09_native_capture.py) checks native
event uniqueness, effective settings/types, admission/graph denial counters,
cleanup, full layer placement, mmap/KV evidence, output-reservation settings,
cohort pins, fresh preflight hashes, hardware/driver consistency and interval
reconciliation. It does not infer receiving-owner acceptance or physical truth
from record shape alone.

## Failure preservation and publication

The [first probe](cuda-cap-probe.json) exited before CUDA initialization because
its DLL-loader path was not normalized for the restricted Windows search flags.
That administrative loader failure and original source/executable identity are
retained. A separately committed path-normalization fix produced the [second
probe](cuda-cap-probe-v2.json), which succeeded with the same runtime archives,
guards and cap. No model trial was rerun or hidden. All three model trials used
the successful second build and the same launcher.

Published stderr omits only repetitive `llama_graph_n_input_tensors` input-node
diagnostics matching the recorded exact pattern. Each record retains omitted
line count and original sanitized-stderr SHA-256. Native events, counters,
placement, warnings and errors remain; original sanitized traces were held only
in task-owned external storage until cleanup. Preflight JSON is normalized to
LF and its parent checksum refreshed for Git's newline policy. These publication
changes do not alter numerical observations or executable/source pins.

[Cleanup receipt](cleanup.json) covers only this task's private runtime/model,
compiler outputs, header copies and trace backups. Existing runtime packages,
drivers and unrelated files/workloads remain untouched. No weights, binary,
large source archive or customer content enters Git.

## Current disposition and reproducibility

The historical `total-memory-setup-2026-10-18/setup.json` and actual CPU estimate
remain immutable, including their original unqualified/disabled status. Current
main already contains the #259 correction binding reviewed runtime/configuration,
preparation exit/version/argv and exact JSON scalar types. Integration retains
that checker and its seventeen tests unchanged, including its conservative
reduced future-cap rule. The intermediate full-record hash checker from this
branch is superseded by the merged correction, not claimed as the final design.
Qualification evidence is added separately rather than rewriting history.

Reproduction inputs are the manifest-pinned archives/GGUF, external headers at
runtime commit620d2225cc436ab0b001e3200e590e3b286ef9ab, the recorded MSVC x64
flags `/std:c++17 /EHsc /O2 /MD /UNDEBUG`, and project source at the recorded
harness ref. CPU fixtures are under `tests/native/`. Compile outside Git, verify
every executable/header/DLL identity and the successful bounded probe before
model qualification. The [serial launcher](../../../../scripts/mr09_native_qualify.py)
refuses an existing repetition, verifies artifacts, rechecks capacity and captures
one initialization-only process with a 90-second timeout. It kills only that child
on timeout, records failure and stops rather than changing settings/retrying.
The three committed repetitions are evidence, not a new standing reservation or
permission to bypass future scope/cap review.

Offline reproduction of record integrity:

```powershell
python scripts/mr09_total_memory_setup.py
python scripts/mr09_native_capture.py
```

**Retained gates:** #61/#10/#11 acceptance of estimator/quantity and native cap
scope; #7 capacity/output semantics; coordinator evidence/tolerance review;
output-reservation matching; inference/VMM/scratch and process-wide peak
instrumentation; remaining MoE/concurrency/multi-GPU scope. There is no numerical
fit verdict, ResourceEstimate, compatibility rule, scope waiver or issue closure.
All source/physical evidence/reuse decisions remain human review tasks.

Primary source inspection, accessed 2026-10-18, uses the pinned
[CUDA backend](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/ggml/src/ggml-cuda/ggml-cuda.cu),
[backend interface](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/ggml/src/ggml-backend-impl.h),
[context allocation](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/llama-context.cpp),
and [native logger](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/common/fit.cpp).
The source interpretation is distinct from actual project observations above;
MIT code and NVIDIA redistributable rights remain separate. Manifests record
locators and hashes without redistributing runtime binaries or external headers.

[Submission validation](validation.md) separates automated integrity checks from
actual native observations and outstanding human evidence review.
