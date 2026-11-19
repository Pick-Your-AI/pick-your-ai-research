# Draft readiness plan: #61 remaining empirical criteria

Refs [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61), parent [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56). Prepared 2026-11-01; reconciled 2026-11-19 against accepted research source `d58106750bb76f72c270653993edf808f29c49bb` and the public decisions linked below. **This is an offline planning proposal, not device authorization, an execution schedule or empirical evidence.** No host inspection, reservation, purchase, download, model call or experiment is included.

## Retained scope and evidence boundary

The [coordinator's full-scope decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6367324704) retains OLMoE M1–M4, the long-context boundary and G1 multi-GPU/per-rank coverage. It approves no specific device, paid compute, download or experiment. The existing spare-local-capacity constraint and preflight guards remain. **G1 is unmet; it is neither deferred nor narrowed by this plan.**

Three empirical criteria remain: vary context/cache precision/concurrency; measure peak allocated and reserved memory; report qualified error bounds and failures without universal fit claims. The [accepted MR09 map](mr09-acceptance.md) and [sizing note](sizing-validation.md) preserve the distinct historical dense, short GM1, native KV component and H1 initialization cohorts. Accepted whole-runtime peak comparison pairs remain zero. Initialization observations and synthetic fixtures cannot fill those missing cells.

A generic Apple-silicon backend is an **unverified investigation option only**. No particular machine, capacity, availability, model support, memory counter, process cap or comparable estimator is established. Backend changes require independently reviewed, backend-specific measurement controls before any later authorized run; no Apple-silicon execution path is adopted here.

## Coverage and missing readiness inputs

| Cell | Retained workload | Required preparation before any separately authorized execution |
| --- | --- | --- |
| Optional H1 continuation | Fixed SmolLM2 F16 GGUF, context 256, initialization only | The [prospective H1 admission launcher](measurements/h1-prospective-admission.md) supports its H1 CUDA configuration only. A new reviewed freeze and device-specific authorization are required; it does not launch M1–M4. |
| M1 | OLMoE BF16, prompt 256, active 1, BF16 KV | Exact artifact/runtime/backend pins, authorized capacity envelope and independently reviewed backend-specific instrumentation, allocator counters, process limits and admission/stop controls. |
| M2 | Prompt 2,048, active 1, BF16 KV | Context coverage under the same explicit evidence and capacity controls. |
| M3 | Prompt 2,048, active 2, BF16 KV | Concurrency coverage and actual per-sequence accounting. |
| M4 | Prompt 2,048, active 1, INT4 KV if supported | Establish backend support and actual packing, metadata, counter semantics and workspace; the [prepared M4 observations](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/503) are unexecuted. |
| Long-context boundary | 8,192 total positions | Review an appropriate model/prompt/cache workload with #7. Pinned OLMoE supports only 4,096 positions and cannot supply this cell. |
| G1 multi-GPU/per-rank | Same pinned dense/MoE, prompt 2,048, active 2, BF16 KV, 32 decode forwards | At least two explicitly authorized devices; topology/interconnect/placement/parallelism; per-rank allocations and separately reviewed multi-rank instrumentation. Existing single-device instrumentation does not execute G1. |

The [OLMoE artifact/copy plan](measurements/mr09-olmoe-artifact-copy-plan-2026-10-19.md) and [machine-readable plan](measurements/mr09-olmoe-artifact-copy-plan-v1.json) provide preparation accounting only. A weight-plus-cache payload floor excludes other resident and transient costs. It establishes neither usable headroom nor fit, and does not authorize a device or justify a capacity recommendation.

## Reviewable execution package still required

1. Record device/session authorization, responsible operator, exact device allocation and model/runtime/backend/driver pins, GPU/host RAM/storage budgets, process caps, topology, run/stop conditions and artifact cleanup. Keep private identities and infrastructure details outside public Git; publish only sanitized authorization scope and evidence locators.
2. Review each backend's measurement semantics: phase-specific allocated/reserved peaks, device-level corroboration, per-rank attribution where applicable, and cleanup evidence. A process footprint or unified-memory observation cannot silently substitute for a CUDA allocator quantity. Unsupported counters remain explicit gaps.
3. Pin comparator inputs and outputs to the same artifact, runtime, weight/KV precision, executed context, active sequences, offload/topology and measured quantity. Review any discrete/unified-memory mapping before admitting a pair. More memory alone does not create comparability. An estimator-error decision tolerance still requires separate #10 review; none is invented here.
4. Review and freeze predictions, source and backend-specific admission controls before any separately authorized experiment. Reserve and retain every actual attempt, including guard refusals and failures; preserve cohort identities. H1's launcher and controls cannot be reused as authorization or measurement controls for M1–M4 or G1.
5. Any later execution needs separate authorization and the unchanged applicable guards. The current task permits offline preparation and synthetic fixtures only. No runtime execution command is supplied here.
6. A future result needs its own evidence and receiving review. The [#10 ResourceEstimate intake](../T2-infrastructure/compute/resource-estimates/README.md) admits zero current records; actual build/selection bindings, units, schema eligibility and record-specific review remain required.

## Safe offline readiness checks

With the existing Python 3.12 environment and pinned dependencies, from the repository root:

```bash
python scripts/validate_mr09_olmoe_plan.py
python -m unittest discover -s tests -p test_mr09_olmoe_plan.py -v
python -m unittest discover -s tests -p test_mr09_comparator_inputs.py -v
```

These commands inspect committed metadata and synthetic CPU fixtures. They perform no model download or GPU measurement and cannot complete the three empirical criteria. Do not use device preflight or model/native runners as offline readiness checks. The summarizer CLI writes a summary even without `--sanitize`; inspect retained evidence in memory or a temporary copy when a new summary is needed.
