# MR-09 estimator comparison execution — 2026-10-18

Refs #61. Partial research, pending co-owner/coordinator evidence review.
This continuation executes third-party estimators against **existing** pinned
SmolLM2 observations; it launches no model inference and downloads no weights.
Base main: `b9694364b6f0a3d1e9c6b37189cc007778fc54bc`.
[PR #251](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/251) was initially a
separate open MoE contribution; it merged during this continuation at main
`2ecfa005a93b3944e6832bdb6a168d535e5efca6`. Integration preserves that cohort
unchanged. No GM1 result enters this estimator-pair set or is claimed accepted
by this contribution. Live #61 co-owners remain @Mattycodes69 and
@appletechie; @CompleteDotTech retains evidence/scope review. #7/#10/#11 retain
receiving-owner review. Assignments, triage, #59 ledgers and v1 are unchanged.

## What ran and what can be compared

| Estimator identity | Executed/observed inputs and output | Comparison disposition |
| --- | --- | --- |
| llmfit v1.1.17, commit `9781270c1cd907971ce071517041edb55702b3ff`; official Windows binary | Six unmodified `plan` executions for exact `HuggingFaceTB/SmolLM2-135M-Instruct`, BF16 weight override, contexts 256/288/2,048/2,080 with FP16 KV; additional q4_0 probes at 2,048/2,080 | Four native KV component estimates can be checked against D1/D2 payload snapshots; total hardware requirement and q4_0 are excluded from numerical runtime error |
| ModelFit CLI `@wecko-ai/modelfit` 1.5.3, commit `8c1df5f00e8f21edd0f0c7b4a12230b838e0b433` | Execute unmodified `getRecommendations` with pinned 156-record dataset and recorded GPU capacity; exact 135M matches = 0, related entry = SmolLM2 360M | Missing exact model and API workload/runtime inputs; no replacement model, no numerical error |
| Local AI Planner, Logarithmic Spirals deployed page, author's browser inspection dated 2026-10-18 | Author reports expanding Advanced Options/Custom Model Data and reading runtime, precision and context controls; no retained capture locator or independent corroboration is supplied | Author-reported runtimes GGUF/llama.cpp or MLX, minimum selectable context 4,096 and no visible admitted-sequence input; independent confirmation remains pending. No exact estimate executed and no numerical error |

All six llmfit commands returned JSON with exit 0. Full outputs are retained in
[the execution directory](estimator-comparison-2026-10-18/); exact arguments,
executable/source/data hashes, UTC timestamps, Node version and runner hash are
in [comparison.json](estimator-comparison-2026-10-18/comparison.json).
The exact [historical executed runner](estimator-comparison-2026-10-18/mr09_compare_estimators.executed.py)
retains that recorded source hash. The current runner's later byte-count guards
were reviewed offline; these estimator outputs were not regenerated with them.
The release archive hash matched its publisher sidecar before execution; the
executable hash is additionally pinned. Local source/data copies were unmodified.
No model/catalog injection, alternate formula or unsupported context was used to
turn an unavailable comparison into success.

**Whole-runtime/peak-allocated comparable pairs remain 0.** llmfit estimates
hardware requirements using a planning formula and a fixed runtime allowance;
it neither pins this Transformers/safetensors artifact nor emits a PyTorch
phase-peak prediction. ModelFit's port lacks artifact revision, runtime, context,
KV layout and admitted concurrency arguments. The author's Planner report supplies
no matching estimate, and its transient control facts still await independent
corroboration. These are quantity/input mismatches or missing evidence, not proof
that either an estimator or model failed.
Neither a `Perfect` fit label nor an estimated TPS is independently validated.
Today's free-capacity fields in llmfit output are read-only discovery samples,
not the historical runtime capacity, a reservation or a new hardware test.

## Narrow native KV component check

The pre-existing protocol permits comparison of like payload quantities. Pinned
llmfit `models.rs::kv_cache_gb` uses full-attention geometry and **divides bytes by
1,073,741,824**, despite its `kv_cache_gb` label. Only that field is converted
back with 2^30. `disk_size_gb` uses decimal GB and total requirements mix planning
terms; this contribution does not apply the KV conversion to those other fields.

The catalog geometry is 30 layers × 3 KV heads × 64 head dimension, equal to the
observed pinned model geometry. D1/D2 native BF16 cache uses two bytes per element;
llmfit's FP16 cache also uses two bytes. Thus only the conventional, uncompressed
KV storage footprint is comparable at identical cached lengths and one sequence.
This is a **storage-width/layout comparison**, not equivalence of FP16 and BF16
numerics, backend support, artifact lineage or runtime behavior. There is no
sequence multiplier added to a raw competitor output.

| Cell / point | Cached tokens | llmfit native KV bytes | Measured bytes in each of 3 repetitions | Signed / absolute bytes; relative error |
| --- | --- | --- | --- | --- |
| D1 prefill | 256 | 5,898,240 | 5,898,240 | 0 / 0; 0% |
| D1 terminal | 288 | 6,635,520 | 6,635,520 | 0 / 0; 0% |
| D2 prefill | 2,048 | 47,185,920 | 47,185,920 | 0 / 0; 0% |
| D2 terminal | 2,080 | 47,923,200 | 47,923,200 | 0 / 0; 0% |

Signed error = estimate − measured; absolute = abs(signed); signed relative
error = 100 × signed / positive measured bytes. Across **12 component pairs**,
min/median/max signed and absolute bytes and signed relative percent are all 0.
The 12 pairs are two snapshots from six existing processes, two workload cells,
and four deterministic estimator configurations. They are not 12 independent
estimator trials, new GPU runs, a confidence interval or a guaranteed bound.
The [pair ledger](estimator-comparison-2026-10-18/comparison.json) names and hashes
each runtime file and estimator output. Original runtime records, instrument,
protocol and summary are unchanged.

D3 is excluded because `plan` does not express the two admitted sequences. D4/D5
remain excluded: the q4_0 output uses a nominal 0.5-byte KV element, while the
measured Quanto representation includes group scales, shifts and BF16 residual
storage. Matching a four-bit label does not match that layout. Its raw estimates
are retained as mismatch probes; no relative error or unsafe-fit count is
assigned. MoE/multi-GPU and estimator fit/tolerance acceptance remain open.

## ModelFit and planner readback

[ModelFit execution](estimator-comparison-2026-10-18/modelfit-audit.json) feeds the
recorded 17,094,475,776-byte GPU capacity as **17.094475776 decimal GB** to the
port's `ramGb` input for PC mode. This is a deliberate recorded-input audit,
not today's hardware detection or 17 GB of system RAM. Its budget ratio 0.7
produces 11.9661330432 labelled GB; this is the CLI port's behavior, not an
endorsed GPU capacity or a refreshed website result. It returns zero exact
135M matches; the 360M entry is not substituted. Dataset attribution: ModelFit
Local LLM Hardware Compatibility Dataset, [modelfit.io](https://modelfit.io/),
CC BY 4.0. Only bounded execution facts are retained, no dataset redistribution.

[Planner browser observation](estimator-comparison-2026-10-18/planner-observation.json)
records the author's inspected controls, pending independent corroboration or an
accessible retained capture. Direct HTTP retrieval of the page and historical
asset returned 403; the browser page was accessible without challenge solving or
authentication. No fresh bundle hash is available and the old bundle identity is
not claimed reverified. No unseen API capability is inferred from visible controls.
The historical bundle analysis remains historical. This inspection neither
forces unsupported values into the page nor substitutes a 4,096-token result.

## Reproduction, evidence and next gate

[Runner](../../../scripts/mr09_compare_estimators.py) accepts a fresh output
directory, a directory containing the four pinned external files and Node.
It rejects an existing output directory or artifact hash drift before executing.
The current runner additionally rejects boolean, fractional, nonpositive and
nonfinite payload byte counts at either observation point, before calculating an
error. Its source identity differs from the archived executed runner; a future
execution records its own source hash and timestamps rather than rewriting the
historical comparison ledger. Offline tests recompute the unchanged finite pairs
with the guarded helper and verify the historical source against its recorded hash.
Download the external artifacts using the exact manifest locators; extract
`llmfit.exe` from the official checked archive. Place the ModelFit engine beside
`data/models.json`; place llmfit's pinned `hf_models.json` in the artifact root.
Review public source code before execution. Then, from the repository root:

```powershell
python scripts/mr09_compare_estimators.py --artifact-dir $ArtifactDir --output-dir $FreshOutputDir
```

The runner performs six read-only llmfit plans, one ModelFit engine call and
hash-bound comparisons against existing D1/D2 records. Browser inspection is
separate and must be repeated as a new dated observation if the UI changes.
No llmfit `bench`, model download/run or server/dashboard command is invoked.
Temporary binaries, source and metadata are removed after the session; the
cleanup receipt records scope/file counts without personal paths. Reproduction
may produce different discovery/TPS fields as local conditions change; only the
pinned KV component and matched payload quantities enter this comparison.

| Primary source, publisher; accessed 2026-10-18 | Evidence / confidence / reuse limit |
| --- | --- |
| AlexsJones: [v1.1.17 release](https://github.com/AlexsJones/llmfit/releases/tag/v1.1.17), [models.rs](https://github.com/AlexsJones/llmfit/blob/9781270c1cd907971ce071517041edb55702b3ff/llmfit-core/src/models.rs#L1426), [catalog](https://github.com/AlexsJones/llmfit/blob/9781270c1cd907971ce071517041edb55702b3ff/llmfit-core/data/hf_models.json) | Primary pinned code/metadata plus actual binary output. High confidence in inspected unit/layout arithmetic; predictive peak accuracy unverified. MIT code, dataset/model rights separate; source/binary/data remain external. [Archive manifest](../../../evidence/mr09-llmfit-v1117-windows.json), [catalog manifest](../../../evidence/mr09-llmfit-v1117-catalog.json). |
| Wecko-ai / ModelFit: [engine](https://github.com/Wecko-ai/modelfit/blob/8c1df5f00e8f21edd0f0c7b4a12230b838e0b433/src/engine.mjs), [data](https://github.com/Wecko-ai/modelfit/blob/8c1df5f00e8f21edd0f0c7b4a12230b838e0b433/src/data/models.json) | Unmodified local CLI execution, distinct from web release. High confidence in bounded output/model absence at this pin; unverified predictive accuracy. MIT code / attributed CC BY 4.0 dataset. [Engine manifest](../../../evidence/mr09-modelfit-v153-engine.json), [data manifest](../../../evidence/mr09-modelfit-v153-data.json). |
| Logarithmic Spirals: [deployed planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/) | Author-reported interactive controls, pending an accessible capture or independent reviewer corroboration; no independently established confidence in the transient options, immutable deployed-code pin or output reproduction. Other interfaces/rights remain unknown. Link and bounded report, no bundle or source text redistributed. |
| Project: original [protocol](mr09-protocol-2026-10-16.md), [D1/D2 runtime observations](./) | Actual project GPU measurements dated 2026-10-16, exact model/runtime/artifact and code pins retained. High confidence in stored counters, subject to their shared-device/pilot caveats and human validity review. No new GPU measurements here. |

Next whole-runtime gate: #61 co-owners and #10/#11 must agree a specific estimator
output quantity and a workload/runtime/artifact it can express, then pin an
eligible measurement protocol or explicitly narrow the question. Hardware alone
cannot resolve an unexpressed quantity. Coordinator approval of any decision
tolerance remains separate; no threshold, scope waiver, runtime fit verdict,
ResourceEstimate, compatibility rule or closure is created by these component
checks. Required repository validation and human evidence review remain distinct.
