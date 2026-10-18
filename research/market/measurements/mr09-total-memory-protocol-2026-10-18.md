# MR-09 total-memory setup proposal — 2026-10-18

Refs #61. **Historical preparation: GPU execution was not qualified or enabled.** This protocol
was written after CPU estimator preparation and before any native GPU run.
It proposes a semantically matched **managed device-buffer snapshot** comparison;
it does not silently replace #61's peak-allocated-memory question or establish
whole-process GPU peaks. Existing dense/GM1 observations remain unchanged.

Live co-owners: @Mattycodes69 and @appletechie. #10/#11 review quantity and runtime
instrumentation, #7 reviews capacity versus demanded-token semantics, and
@CompleteDotTech reviews evidence/scope and any decision tolerance. Adding the
independent estimator below and accepting a snapshot target require their
explicit disposition. This is a reviewable proposal, not their approval. No
contract, ResourceEstimate, catalog, assignment, triage or #59 ledger is changed.
The named llmfit/ModelFit/Local AI Planner comparisons remain separate; this
candidate does not manufacture missing outputs for those tools.

The [native qualification continuation](native-qualification-2026-10-18/qualification.md)
records three subsequent initialization-only trials. The original setup and CPU
preparation remain immutable and disabled; inference and process-wide caps,
output-reservation matching and accepted estimator comparisons remain open.

## Selected pair and artifact

| Part | Exact pin / scope |
| --- | --- |
| Independent estimator | GPUStack `gguf-parser-go` **v0.26.4**, commit `637cd9a7a03993ab30ace3c53dd8af5c37f46a94`; Windows amd64 executable SHA-256 `8da9ae6b8968d5d2dee4eaf48dbc24ed48bf3de02794c8dbe0b2a9443b12c92c`, locally verified against release digest |
| Proposed runtime | ggml-org `llama.cpp` **b11669**, commit `620d2225cc436ab0b001e3200e590e3b286ef9ab` (v0.7.0 resolves to this nightly); planned Windows CUDA 13.4 x64 archive and cudart identities in [setup.json](total-memory-setup-2026-10-18/setup.json). Publisher digests checked as metadata only; archives/DLLs not downloaded or executed |
| Exact common file | `bartowski/SmolLM2-135M-Instruct-GGUF`, revision `09816acd5d99df7be770d85ea30822623dab342c`, `SmolLM2-135M-Instruct-f16.gguf`, **270,885,952 bytes**, SHA-256 `f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57`; local file size/hash matched publisher metadata |
| Workload/capacity | Context **capacity 512**, logical batch 256, physical batch 256, one sequence, native F16 K and V, Flash Attention disabled, mmap enabled, one CUDA0 device, layer offload 31 (30 blocks plus output), no tensor overrides, adapters, draft model or RPC |
| First proposed observation | After model/context initialization and scheduler allocation, with no warmup or generation. Three serial fresh processes after qualification. This is initialization capacity, not observed prefill/decode/load-transient peak |

The estimator reads tensor sizes/types from that GGUF, rather than a model-name
catalog entry or nominal parameter count. The native runtime must load **the
same hashed file**. The F16 GGUF may include other tensor types; do not substitute
`parameters × 2`. Its metadata reports llama architecture, 30 blocks, 3 KV heads,
64-dimensional keys, and 134,515,008 parameters. The converter lineage to the
historical HF safetensors revision is unverified: this is a new artifact/runtime
cohort, not a rerun or pooled extension of those measurements. Publisher/GGUF
metadata label Apache-2.0; source accuracy and permitted reuse still need review.

## Exact target and exclusions

The estimator JSON field is `estimate.items[0].vrams[0].nonuma`, in **integer
bytes**. Its pinned `SummarizeItem` adds platform footprint + GPU bootstrap +
weights + KV + compute. This preparation explicitly sets `--platform-footprint
0,0`: platform/CUDA/library overhead is **outside the chosen buffer target**,
not asserted to be zero in reality. This exclusion is declared before runtime
measurement, not tuned after seeing its error. For this ordinary decoder, the
estimator's output/logit buffer is host memory, excluded from VRAM; its source
has a separate special-case device output placement for speculator architectures.
No such architecture is used here.

The runtime target is the `self` field of the CUDA0 `fit_memory_breakdown` event,
from **allocated** context buffers. At the pinned source,
`llama_context::memory_breakdown()` accounts model buffers, KV/context buffers
and backend scheduler compute buffers; `common_memory_breakdown_print` groups
host buffers separately and sets `self = model + context + compute` per device.
Backend alignment, scratch sizing and model-placement assumptions are hypotheses
to test, not reasons to force equal estimates. Verify input-embedding and output
placement rather than interpreting `fullOffloaded` as proof that every tensor
and host buffer resides on GPU.

These quantities are candidates for matching the full **modeled managed-buffer
footprint**. They exclude untracked CUDA contexts/library pools, driver/other
processes, host RAM and transient/high-water memory. `unaccounted` is retained
as a device-wide residual, never attributed to this process. Do not sum device
`free` deltas or allocator reserved/allocated counters into this target. The
standard event is an instantaneous allocation report; no process-wide peak or
statistical confidence claim follows.

A true peak-allocated/process-footprint study is a separate retained #61 gate:
record every relevant allocation/free (including transient workspace, VMM and
library allocations) or qualify another per-process high-water instrument, and
select an estimator quantity that predicts that same scope. Shared WDDM device
free-memory subtraction and these startup snapshots cannot satisfy it. If owners
retain only the peak question, this candidate remains supplemental rather than
an accepted substitute. Full MoE, concurrency, quantized-KV and multi-GPU scope
is not waived.

## What was actually executed

A readonly capacity screen passed GPU free **8,328 MiB**, available RAM
**28,720,410,624 bytes**, and temporary disk **40,463,028,224 bytes**, at
2026-10-18T06:08:29Z. This reused the unchanged 4,096 MiB / 12 GiB /
6,412,308,016-byte preparation thresholds from the existing preflight tool's
`granite31` profile; its name does not establish a native-runtime experiment or
fit guarantee. The [preparation screen](total-memory-setup-2026-10-18/preparation-preflight.json)
permits bounded download preparation only and must not be reused as a later
inference admission record. Existing workloads were preserved.

Downloaded the official 9,592,832-byte estimator binary and pinned GGUF to a
fresh external temporary directory. Checked both SHA-256 values against
publisher metadata, ran estimator `--version`/`--help`, and then ran **CPU-only
file parsing/estimation** with the exact command below. The estimator does not
launch llama.cpp or allocate model buffers on a GPU.

```powershell
& $GGUF_PARSER --path $GGUF_FILE --ctx-size 512 --batch-size 256 --ubatch-size 256 --parallel-size 1 --gpu-layers 31 --tensor-split 1 --main-gpu 0 --cache-type-k f16 --cache-type-v f16 --no-flash-attention --platform-footprint '0,0' --skip-tokenizer --json
```

It exited 0 and produced **288,499,968 bytes** of modeled NonUMA VRAM. This is a
real estimator output, **not measured usage or an approved capacity budget**.
The raw small [JSON](total-memory-setup-2026-10-18/gguf-parser-estimate.json),
[command/hash ledger](total-memory-setup-2026-10-18/preparation.json),
[GGUF manifest](../../../evidence/mr09-smollm2-f16-gguf.json), and
[estimator manifest](../../../evidence/mr09-gguf-parser-v0264.json) retain pins.
Both artifact copies are removed after preparation; the cleanup receipt records
only this task's directory. No model output, weights, source tree, raw dataset,
credentials or binary is committed. Runtime observations and total-memory
pairs remain **0**; no error or fit verdict is fabricated.

## Native qualification and capture recipe

The next executor must satisfy every [machine-readable gate](total-memory-setup-2026-10-18/setup.json)
before allocating native model buffers:

1. Obtain precise #61/#10/#11 dispositions on the new estimator and snapshot
   scope; preserve coordinator tolerance/scope decisions and #7 context review.
2. Verify official runtime and cudart archives locally; record executable/DLL
   hashes, actual build/backend/driver identity and RTX 5070 Ti support. CUDA
   13.4 compatibility with the local driver is **not yet verified**. Do not
   update a driver or substitute another build/backend silently. A mismatch
   requires a newly pinned proposal/record, not a fallback measurement.
3. Implement and qualify a native managed-allocation cap no greater than
   **min(2,136,809,472 bytes, 2 GiB, 12.5% of freshly reported device memory)**.
   The first term preserves the historical dense device envelope. PyTorch's cap
   does not constrain llama.cpp. `--fit-target`, expected size, free-memory
   polling and killing a process after an overshoot do not enforce this cap.
   Native CUDA allocator/VMM/scratch paths must be covered before execution.
4. Freeze actual context/device parameters and qualify capture. Proposed native
   initializer: use `llama_model_load_from_file` for the pinned GGUF, then
   `llama_init_from_model`; explicitly set `n_gpu_layers=31`, split mode NONE,
   main GPU 0, mmap true, `n_ctx=512`, `n_batch=256`, `n_ubatch=256`,
   `n_seq_max=1`, F16 `type_k/type_v`, Flash Attention disabled, KQV/op offload
   enabled. Disable graphs in the verified build/backend and auto-fit; record
   effective values and buffer-device placement. No `no_alloc` context is a
   measurement. No warmup, tokens or network server is needed for the first
   initialization snapshot. The custom capture/exporter and graph-disable path
   are **not implemented/qualified by this preparation**.
5. Freshly recheck GPU/RAM/disk guards before each of three serial processes.
   After successful allocated initialization, synchronize the device, export
   the allocated buffer report before freeing the context, then exit/cleanup.
   Record success/failure plus phase; preserve all attempts. Stop after any
   error, cap failure or pin drift, with no retry under changed settings.

The official `llama-fit-params --fit-print on` path uses `no_alloc` and reports
projected buffers. It can be a secondary same-code control after qualification;
it must **never** fill an actual-runtime observation or be counted as independent
estimator validation. This preparation does not provide an enabled GPU launcher.
The offline checker intentionally reports `execution_enabled: false`.

## Units, rounding and pairing gates

The pinned runtime JSON logger **floors nonnegative buffer values to integer
MiB**, even for structured output. Its signed `unaccounted` residual uses C++
integer division, which truncates a negative value toward zero; that residual
does not enter this process-buffer comparison. For a reported `self = s`, the actual integer-byte value is
in `[s × 2^20, (s+1) × 2^20 − 1]`. Do not call `s × 2^20` an exact measurement,
or reconstruct `self` by adding independently rounded model/context/compute.
An exact-byte exporter would require a separately hashed source/build and
qualification; no upstream metric is silently relabelled here.

Given positive actual byte interval `[L,U]` and estimate `E`, signed error is
`[E−U,E−L]`; signed relative percent is
`[100×(E−U)/U,100×(E−L)/L]`. Absolute error can include zero when the estimate is
inside the interval. These are measurement-resolution intervals for a future
observation, not experimental or universal error bounds. No approved tolerance
exists. The [offline helper](../../../scripts/mr09_total_memory_setup.py) retains
integer/rational endpoints and rejects no_alloc, wrong-metric, nonpositive,
multiple-device and unit-mismatched inputs. Its tests use clearly synthetic
future logs, not promoted research evidence.

Before a pair can exist, bind the same GGUF bytes, runtime/build/DLL hashes,
full effective configuration, actual CUDA device/driver, cap and preflight,
allocated observation stage and source log/exporter hash. A normalized event's
`no_alloc=false` is an assertion requiring independent capture evidence, not
proof on its own. Missing evidence leaves `unexecuted` or `mismatch`; a source
estimate or a schema-valid synthetic fixture cannot replace it.

Run the **offline** prepared-record check from the repository root:

```powershell
python scripts/mr09_total_memory_setup.py
```

The prepared-record checker binds the reviewed estimator/runtime source and
archive identities, exact GGUF repository/revision/file/size/hash, every declared
runtime and workload control, recorded estimator command, target fields/units
and scope, and the existing preparation guards. It compares exact JSON types,
including numeric array members: `true`, `1` and `1.0` are not interchangeable.
Missing or additional estimator/runtime/configuration/comparison fields require
review; matching edits to a preparation receipt cannot silently replace the
reviewed artifact identity. Effective estimator fields and placement must agree
with those bindings. The proposed future cap may decrease, but cannot increase
or enable execution. Synthetic mutations exercise the rejected alternatives;
the original CPU output, preparation, preflight and cleanup bytes are unchanged.

These checks establish local record consistency, not the truth of source-check
or local-verification annotations, completeness of the qualification decisions,
fresh hardware admission, downloaded runtime identity or physical execution.
Those evidence and receiving-owner gates remain independently reviewable.

## Primary evidence and confidence

All sources accessed **2026-10-18**. Region/currency not applicable. High
confidence in the pinned bytes, metadata fields, CPU output and inspected source
arithmetic; predictive accuracy, physical runtime validity and reusable fit
advice remain unverified. Public source availability does not settle all rights.

| Primary locator / publisher | Claim and review boundary |
| --- | --- |
| GPUStack [v0.26.4 release](https://github.com/gpustack/gguf-parser-go/releases/tag/v0.26.4), [estimator source](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/file_estimate__llamacpp.go#L2271), [CLI](https://github.com/gpustack/gguf-parser-go/blob/637cd9a7a03993ab30ace3c53dd8af5c37f46a94/cmd/gguf-parser/main.go) | Exact output, units, platform term, context/batch/cache/offload controls; independent codebase, not physical validation. MIT code, no binary/source redistribution. |
| ggml-org [b11669 release](https://github.com/ggml-org/llama.cpp/releases/tag/b11669), [buffer accounting](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/src/llama-context.cpp#L3700), [logger](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/common/fit.cpp#L906), [no_alloc control](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/common/fit.h) | Proposed runtime/build pin, reported-buffer semantics and MiB truncation; source inspection only, archives/driver/cap/capture unqualified. MIT code, no runtime distribution. |
| bartowski [pinned artifact metadata](https://huggingface.co/api/models/bartowski/SmolLM2-135M-Instruct-GGUF/revision/09816acd5d99df7be770d85ea30822623dab342c?blobs=true), [pinned card](https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF/blob/09816acd5d99df7be770d85ea30822623dab342c/README.md) | Publisher metadata plus local artifact verification; Apache-2.0 label, exact converter/base lineage not established; no weights redistribution. |

Repository validation checks structure, source/output hashes, pairing logic and
synthetic failure cases. Owners must still review estimator/quantity selection,
source rights/freshness, backend compatibility, native-cap coverage, capture
validity and empirical scope. A merged setup proposal is not a GPU result,
whole-process calibration, compatibility rule or completed #61 acceptance.
