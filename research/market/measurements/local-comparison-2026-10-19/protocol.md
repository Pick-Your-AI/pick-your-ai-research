# Local H1 comparison protocol — 2026-10-19

Refs #61. The user explicitly requested a hardware check and the first comparable
estimator/runtime measurement using spare local capacity only. This is a new
prospective cohort. It preserves the original criteria, owners, historical
observations and the separate estimator implementation now in progress.

The existing [comparison specification](../mr09-comparison-spec-2026-10-18.md)
and [coordinator dispositions](../mr09-comparison-dispositions-2026-10-19.md)
define a supplemental initialization managed-device-buffer quantity. A result
here cannot substitute for whole-runtime allocated/reserved peaks, the three
named third-party estimators, varied MoE, cache precision or multi-GPU coverage.
No tolerance, ResourceEstimate, compatibility rule or acceptance is implied.

## Prospective cell and order

H1: the same 270,885,952-byte SmolLM2 F16 GGUF, SHA-256
`f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57`;
llama.cpp b11669 / `620d2225cc436ab0b001e3200e590e3b286ef9ab`;
total context capacity256, batch/ubatch128, sequence capacity1, F16 K/V,
Flash Attention disabled, mmap, offload31, CUDA0 only, four CPU threads,
extra buffer types disabled, no backend samplers/embedding outputs.
Expected graph output capacity128, initial host logits readback1 row;
actual native readback must agree. Zero populated cache positions, active
inference requests, generated tokens and warmup forwards.

The new fixed H1 harness differs from the historical harness only in its label
and fixed context/batch/ubatch tuple plus matching getters/event. All admission,
graph-denial and cleanup controls remain. Commit the exact native source before
building and record compiler/header/source/executable/DLL identities. Run the
existing synthetic CPU quota test. Freeze an actually built estimator's exact
source/patch/build/command/effective controls/raw prediction before any native
model observation. The unmodified GPUStack v0.26.4 baseline remains ineligible.
Missing or mismatched estimator controls admit no numerical comparison.

Then perform three serial fresh processes, preserving every attempt. Each child
first runs the fixed 8 MiB allocation/clear/free and pre-call cap+1 denial probe,
then model/context initialization, synchronization, native breakdown export and
cleanup. No decoder/encoder API is loaded and graph dispatch is refused.
Record native self's integer-MiB interval as primary; reconcile with the exact
live admission ledger. Do not sum rounded model/context/compute components.

## Capacity and stop conditions

Before downloads and each child: one visible GPU, nvidia-smi free>=4096MiB,
available RAM>=12GiB, temporary disk>=6,412,308,016 bytes. Inside the child:
CUDA free>=4GiB, managed request cap<=min(2,136,809,472 bytes, device bytes/8).
Keep the original device/driver pins and reject drift. Child deadline90seconds;
post-run telemetry deadline10seconds. Persist native outcome before telemetry.
Stop after any guard, artifact, cap, runtime or telemetry failure; do not evict
workloads, reduce guards, adjust power, change drivers/packages or retry under
changed hidden settings. No paid compute or additional device is authorized.

This cap covers default managed CUDA0 buffer requests during instrumented
initialization, not opaque library/context allocations or whole-process VRAM.
The free-callback wrapper changes CUDA buffer identity/copy paths. Disclose this
instrumented boundary and retain unexplained effects as unmatched. Resource
screens are observations, not a reservation. OLMoE's >12.8GiB BF16 weights alone
exceed this process cap and currently observed spare memory; it is unexecuted.

## Reporting and retention

Keep raw sanitized logs, exact pins, guard values, failure phases and every
repetition. Use exact integer/rational error intervals from the specification;
describe observed differences without pass/fail or a universal error bound.
Eligibility and receiving acceptance are distinct states. No new owner response
is inferred from user execution authority or coordinator preparation direction.
Keep models, binaries, headers and archives in task-owned external temporary
storage, never Git. Remove only that verified task directory after evidence is
captured; retain hashes/locators and a cleanup receipt.

The first preparation attempt failed before download because a sandbox-private
temporary path did not exist in the host execution context. No GPU child ran.
The separately created host task directory passed a fresh unchanged screen;
the initial read-only inventory and screen are preserved separately.
