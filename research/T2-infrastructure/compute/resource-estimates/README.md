# Proposed ResourceEstimate intake for #10

Proposed placement: `research/T2-infrastructure/compute/resource-estimates/`.
Decision record: [gpu-compute.md](../../gpu-compute.md#headroom-and-measurement-handoff-disposition-2026-10-18).
Live #10 co-owners @Mattycodes69 and @appletechie must accept the placement and
consumer before records are submitted. This README adds no runtime record.

The [frozen v1 schema](../../../../contracts/v1/schemas/resource-estimate.schema.json)
is build-bound. It requires `build_id`, `build_revision`, `generated_at`,
estimator identity/version, confidence, assumptions and nonempty
`selection_ids`. Its memory metrics are
`inference.estimated_required_vram_gb` and
`inference.estimated_peak_per_device_vram_gb`; it has no measured allocated
or reserved memory metric. Sources: schema and
[submission workflow](../../../../docs/RESEARCH_WORKFLOW.md), inspected
2026-10-18; this is contract mapping, not measured capacity.

| Evidence or output | Placement and handling |
| --- | --- |
| Existing #61 allocator observations | Keep [original records](../../../market/measurements/) and [measurement note](../../../market/sizing-validation.md); link them as bounded evidence |
| Arithmetic without a real build | Keep in the #10 decision note/calculation script; no invented build or selection identities |
| Future qualifying estimate | Submit here only after the owners agree consumer/placement and real pinned inputs exist |
| New measured metric, interval or topology field | Propose a versioned extension through #40; preserve imported v1 |
| Synthetic example/test | Keep under `tests/`; never represent it as research evidence |

A future submission needs all of the following:

1. Resolve the real BuildSnapshot revision and every referenced selection to exact
   catalog versions. Retain model/artifact, workload/context, engine/backend,
   device allocation, adapter and topology inputs in the source note.
2. Declare units, per-device live-memory terms, headroom and its capacity basis.
   Reconcile allocator versus whole-device quantities and demand versus pool.
   Apply reserve once. Retain the full scenario range and source evidence.
3. Use `estimated` for the uncalibrated #10 method. A successful run or a native KV
   payload match does not justify `calibrated` or `verified`. Unsupported metrics
   stay absent; missing measurements do not become zero. The proposed total-sum
   versus maximum-rank scalar convention still requires #40 review.
4. Validate every new file explicitly against the matching schema, then check
   actual build/selection resolution and units. The general intake validator
   does not ingest arbitrary ResourceEstimate JSON automatically.
5. Obtain the relevant #10/#11/#39 receiving dispositions, evidence review and
   #40 review where semantics change. Schema validity is separate from acceptance.

For each real file, the PR must add explicit matching-schema validation coverage
using `contracts/v1/reference/validate_payload.py` and run the complete current
[workflow](../../../../docs/RESEARCH_WORKFLOW.md). Do not run the measurement
runner or download weights to validate a JSON estimate.

The existing 15 dense observations have no real BuildSnapshot/selection binding
and no matched competitor/runtime error cohort. They remain note-only evidence;
this proposed directory is not a reason to relabel them.


The [research memory screen](../memory_screen.py) is arithmetic support for the
proposal above, not an intake validator or ResourceEstimate generator. Its
caller-provided confidence/domain assertions do not establish evidence eligibility.
The [2026-10-18 appletechie response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221)
accepts explicit headroom and note-only observations from that co-owner scope.
It does not accept future placement, waive #61 coverage or bind a real build;
Mattycodes69's disposition and the placement agreement remain required.
