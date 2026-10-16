# Proposed GPU / compute compatibility rules

Issue: #10 · Contract review: #40 · Status: proposed / unverified · Proposal version: 0.1.0

Evidence IDs refer to [gpu-compute.md](../gpu-compute.md), all accessed 2026-10-16. This is a research proposal using the [shared template](../../../templates/rule-proposal.md), not an approved Ruleset. `pass`, `fail`, `unknown`, `skipped` are **outcomes**. `info`, `warning`, `error` are separately **severities**. No rule below is claimed verified joint compatibility: [governance](../../../docs/governance.md) requires a second source or reproducible test. Arithmetic assertions reproduce the proposed formula but do not test a model/runtime on hardware.

## COMPUTE-01: per-device memory feasibility

- Participating kinds, roles, and JSON pointers: model primary `/spec/min_weights_vram_gb`; model selection `/settings/precision`, context_policy selection `/settings/requested_context_tokens` and `/settings/reserved_output_tokens`; accelerator primary `/spec/vram_gb` and selection `/settings/device_count`; compute_profile `/spec/accelerator_ref`, `/spec/accelerator_count`, selection `/settings/instances`; inference_engine version; optional fine_tuned_model `/spec/adapter_only`. ResourceEstimate metrics `inference.estimated_required_vram_gb` and `inference.estimated_peak_per_device_vram_gb` are inputs from an external estimate, not catalog facts. #40 must confirm references to estimate results.
- Applicability condition: enabled model served on a customer-controlled accelerator with a real pinned model/engine/context/profile, complete memory inputs and known per-rank allocation. API-only provider capacity is COMPUTE-05.
- Assertion and source evidence: compare each rank's memory requirement with its usable allocation in identical units. Formula, C11/C14/C15 and exact hardware C01–C09. If a proven resident-weight lower bound alone exceeds allocation, return `fail`. If only an assumed envelope exceeds allocation, return `unknown` with a capacity warning; an uncalibrated model is not proof of hardware impossibility. If the entire conservative scenario fits, the memory-screen assertion can `pass` **only for that stated scenario**; overall compatibility remains unverified pending #11 and runtime evidence.
- Severity: `error` for proven lower-bound failure; `warning` for estimated/unknown fit; passing diagnostic `info`. Separate rules may be needed if #40's approved representation supports one fixed severity per rule.
- Missing-data behavior: `unknown`, never use zero for missing cache/runtime or assume VRAM pools. If free allocation is absent, report an advertised-capacity screen only, not final fit. Rules needing interval data cannot become final v1 rules until #40 chooses representation.
- Explanation and remediation: explain the largest per-rank term and scenario; reduce admitted context/concurrency, use a supported quantization with quality evidence, choose a larger allocation, or validate a sharding/offload plan. Recompute after changes.
- Dependency edges and affected consumers: model/context/adapter/workload/engine/topology → estimate → accelerator/profile fit; cyclic re-evaluation with #6/#7/#11; #9/#31/#39 consume the distinctions.
- Passing example (synthetic): known allocation48GB, conservative scenario upper25GB/rank and supported one-device plan → memory-screen `pass`, `info`; does not prove SLO/runtime.
- Failing example (synthetic): known80GB allocation, exact resident unsharded weights90GB → `fail`, `error` even before KV; not based on marketing parameter labels.
- Unknown / non-applicable example: “7B”, INT4 label, unknown quant metadata or unknown runtime memory → `unknown`, `warning`; model accessed only through hosted API → `skipped`, `info` for local-fit assertion.
- Version and migration impact: conditional research rule; no imported v1 edit. Need interval/usable allocation/topology facts reviewed by #40. Pin estimator version and rerun when any participating version/settings change.

## COMPUTE-02: model, engine and accelerator backend intersection

- Participating kinds, roles, and JSON pointers: model primary `/spec/model_formats`, `/spec/supported_precisions`, `/spec/access_modes`; accelerator primary `/spec/backends`, `/spec/precisions`; inference_engine primary `/spec/backends`, `/spec/model_formats`, `/spec/supported_precisions`; selected model precision and exact artifact/quantization/engine versions. Architecture, OS/driver and quantization implementation currently require supporting note evidence.
- Applicability condition: customer-controlled engine loads the selected artifact; provider-only API builds skip local backend checking.
- Assertion and source evidence: require a documented joint path for format, architecture, dtype, quantization implementation, backend and hardware/driver. Nonempty array intersections are necessary, not sufficient. C01–C05/C12 establish hardware and **historical vLLM0.10.2** support claims. Consult [#11's current engine record](../inference-engine.md) for newer versions; never apply the historical table to another release without checking.
- Severity: `error` for a documented unsupported combination; `warning` for unverified joint combinations; `info` for the scoped passed check.
- Missing-data behavior: `unknown`. If documentation conflicts, retain both claims/conditions and return unknown until resolved. A vendor-supported matrix row remains unverified compatibility under governance until corroborated/tested.
- Explanation and remediation: report which layer lacks support, exact version and primary source; change supported engine/backend/artifact, or obtain reproducible evidence. Do not infer compatibility from native arithmetic precision.
- Dependency edges and affected consumers: model ↔ engine ↔ accelerator; #6/#10/#11/#33/#40; recompute all three after any selection change, not a sequential blocker.
- Passing example (synthetic policy test): exact artifact/engine/driver/hardware combination independently reproduced with matching format/dtype/backends → scoped joint-support `pass`, `info`; this submission contains no such real reproduced deployment.
- Failing example (documented historical claim, still pending central verification): vLLM0.10.2 + AMD GPU + AWQ; C12 explicitly lists unsupported. Proposed result `fail`, `error`; do not generalize to all future engines or all INT4 algorithms.
- Unknown / non-applicable example: generic FP8 model+MI300X with unspecified FP8 format/kernel → `unknown`, `warning`; API-only model without local engine → `skipped`, `info`.
- Version and migration impact: version-pin claims; namespaced notes are not canonical architecture/kernel fields. #40 review needed to represent all participating metadata; no final ruleset issued here.

## COMPUTE-03: context and KV capacity

- Participating kinds, roles, and JSON pointers: context_policy `/settings/requested_context_tokens` and `/settings/reserved_output_tokens`; model `/spec/context_window_tokens`; workload `/spec/concurrency`; accelerator allocation; engine version and cache implementation; model cache geometry from artifact evidence.
- Applicability condition: full-attention decoder-only model using explicit resident KV; other attention architectures need their own derivation.
- Assertion and source evidence: reserve prompt+output for every admitted sequence and round allocation to real cache blocks; calculate keys+values using KV heads. Check model/context limit independently of device memory. C11/C14 plus C15 mechanisms and reproducible arithmetic script. Hypothesis is that the assumed 2–4GiB runtime bracket suffices; it is **not** verified. No claim of universal overhead.
- Severity: `error` for known context-limit violation; `warning` for unknown cache geometry/capacity; `info` for passed scoped arithmetic assertion.
- Missing-data behavior: unknown for missing geometry, cache dtype/layout, active admission or context; no automatic default from model family name. A wrong formula for MLA is not “close enough”.
- Explanation and remediation: show cache bytes/token, context and sequence count; lower budget/admission or use a supported cache strategy and re-estimate. A queue can wait without device KV, so do not multiply by every pending HTTP request.
- Dependency edges and affected consumers: #2/#6/#7/#10/#11/#16/#28; context and workload changes invalidate estimate. T3 retrieval/ACL and T4 memory semantics are not changed.
- Passing example (synthetic formula test): L28,Hkv4,D128,BF16KV,1sequence8192tokens →469,762,048cache bytes; correct calculation `pass`, `info`, conditional on those assumptions.
- Failing example (synthetic policy test): context policy requests32768prompt+4096output against a32768model maximum →`fail`,`error` regardless of available GPU RAM.
- Unknown / non-applicable example: no KV-head count/cache architecture →`unknown`,`warning`; provider-managed opaque cache →`skipped` for local formula and unknown provider capacity.
- Version and migration impact: #40 needs architecture/cache dtype/strategy metadata and estimation assumptions; preserve v1. #6/#7 approve context independently; current model main must not silently replace historical artifact settings.

## COMPUTE-04: multi-GPU allocation and count consistency

- Participating kinds, roles, and JSON pointers: accelerator selection `/settings/device_count`; compute_profile `/spec/accelerator_ref`, `/spec/accelerator_count` and selection `/settings/instances`; engine `/spec/supports_multi_gpu`; model version; ResourceEstimate per-device peak. Explicit TP/PP/DP/EP plan, node/fabric and KV partitioning are note inputs pending #40.
- Applicability condition: more than one selected device, multiple instances/replicas, or model requiring a partitioned placement.
- Assertion and source evidence: reconcile provisioned device inventory with the selected plan; compare max rank requirement to actual per-rank allocation. DP replicates weights, TP/PP have distinct partitions and synchronization costs (C15); physical link differs by variant (C01–C03). `supports_multi_gpu=true` alone cannot verify a particular plan.
- Severity: `error` for a known inventory contradiction; `warning` for absent/untested topology; `info` for a reproduced scoped plan.
- Missing-data behavior: unknown; never total VRAM pooling by default. Missing selected engine support is not false by omission.
- Explanation and remediation: show devices per replica and replica count separately. Obtain an engine-supported plan, adequate interconnect and per-rank peak estimate; choose one host/device SKU if a multi-node path is unknown.
- Dependency edges and affected consumers: #9/#10/#11/#31/#39/#40; a profile or replica-count change invalidates sizing/cost assumptions. Training topology remains #31's separate task.
- Passing example (synthetic): one documented1-GPU profile instance, selected count1, known one-device model plan → inventory `pass`,`info` only.
- Failing example (synthetic): one instance with profile accelerator_count1 but selected plan requires2simultaneous physical GPUs →`fail`,`error`; buying2DP replicas does not fix2-wayTP for one model.
- Unknown / non-applicable example: two48GB GPUs,90GB estimated total, no per-rank plan →`unknown`,`warning`; one-device deployment with no parallelism question →`skipped`,`info` for parallelism assertion.
- Version and migration impact: proposed fields and inventory semantics require #40 review; no schema mutation or universal approved boolean.

## COMPUTE-05: API-owned compute applicability

- Participating kinds, roles, and JSON pointers: deployment_mode `/spec/mode`; model `/spec/access_modes`; local accelerator/compute_profile/inference_engine selection presence and enabled flags.
- Applicability condition: model served exclusively through provider-managed API; hybrid builds check each served route separately.
- Assertion and source evidence: [canonical component guide](../../../contracts/v1/docs/COMPONENTS.md) permits API-only builds to omit local GPU/runtime. No provider capacity, hidden GPU model or batching is inferred. This is a contract applicability proposal, not a vendor capability claim.
- Severity: `info` when skipped; `warning` if a caller requests a local capacity recommendation without control/visibility.
- Missing-data behavior: unknown deployment path →`unknown`, not automatic skip. A managed endpoint with dedicated user-visible GPU may need local sizing rather than a skip.
- Explanation and remediation: ask provider/service evaluation (#5/#9) for quota, limits and measurement conditions; select an explicit dedicated compute profile if the user controls capacity.
- Dependency edges and affected consumers: #3/#5/#9/#10/#39/#40; deployment mode and routing changes trigger recomputation.
- Passing example (synthetic): API route is explicit and no local capacity is claimed → applicability `pass`,`info`, followed by local-memory check `skipped`.
- Failing example (synthetic assertion misuse): API model name is used to assert “fits one local L40S” without weights/runtime → reject claimed evidence; support outcome remains`unknown`,`warning`, not a physical incompatibility verdict.
- Unknown / non-applicable example: hybrid route ownership unspecified →`unknown`,`warning`; fully self-hosted route → this API-only rule`skipped`,`info` and apply COMPUTE-01–04.
- Version and migration impact: no contract change for applicability; route-level hybrid semantics may need #3/#40 design. No native blocker relationship is introduced.
