# Proposed T1 model and offering rules

Issues: #5, #6 · Contract review: #40 · Status: proposed, not an approved ruleset

Evidence IDs resolve in [evidence](../evidence.md). Existing v1 facts can supply necessary constraints; offering/account/region and architecture relations that lack fields remain note-level proposals. Checked publisher documentation is distinguished from proposed builder policy and independently verified behavior. These rules do not certify measured quality or deployment approval. This follow-up applies the [#40 owner's PR #88 review at `dbfa7dd`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), accessed 2026-10-17; central positions remain distinct from approved contract changes and affected-owner acceptance.

## T1-O1: route and model identity

- Participating kinds/roles/pointers: `model_provider` selected supplier `id`; `model` generation `spec.provider_ref`, `id`, `version`; existing build `/links` relation `provided_by` binds the model to its serving/source provider. The richer endpoint configuration key is proposed in #81, not a new v1 relation.
- Applicability: a model and a serving/source provider are selected.
- Assertion/evidence: the model reference must resolve to the selected serving/source provider and the intended route-specific release. O1/A1/A2 establish different published identifiers; the filtering policy is proposed. Publisher identity alone cannot equate first-party and Bedrock offerings.
- Severity: `error` (fixed). Missing alias evidence changes the outcome to unknown; it does not change severity.
- Missing data: unknown for unresolved aliases or missing provider/release evidence. No final compatibility boolean.
- Explanation/remediation: select the actual provider-specific release; preserve publisher canonical identity separately.
- Edges/consumers: provider <-> model, #6/#7/#30/#37/#39.
- Synthetic pass: selected OpenAI source and GPT-5.4 OpenAI snapshot's matching provider_ref.
- Synthetic fail: Anthropic direct record selected with an AWS-only serving binding; identical marketing name is insufficient.
- Unknown/non-applicable: unresolved model alias -> unknown; optional absent local engine -> engine condition skipped, not provider failure.
- Version/migration: reference comparison and `provided_by` fit v1. Route-specific endpoint type/model ID/revision or alias policy/region/tier belongs to #81's proposed opaque-endpoint key; account/terms conditions and richer lineage use CD-6, with migration under CD-7. No frozen bytes changed.

## Joint-support family: T1 inputs to COMPUTE-02 / ENGINE-02 / D-R3

The former separate T1-M1 proposal is retired into the family accepted into the #40 queue in the [PR #75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927): [COMPUTE-02](../../T2-infrastructure/rules/compute-capacity.md#compute-02-model-engine-and-accelerator-backend-intersection), [ENGINE-02](../../T2-infrastructure/rules/engine-compatibility.md), and #81's D-R3 quantization case. Do not emit a duplicate T1 rule ID or evaluate this necessary input check as a second independent compatibility verdict.

- T1 supplies pinned model/artifact/revision, architecture/geometry, source format, selected precision/quantization and derivative lineage (Q1/Q2); v1 `model.spec.model_formats` and `supported_precisions` are necessary inputs, not sufficient joint support.
- #10/#11 own exact engine build/backend/hardware support evidence. The family applies per local serving component, including hybrid; API-only opaque runtime skips local support checking. A managed customer-supplied runtime is checked in its actual scope.
- The shared family uses fixed `error` severity and `on_unknown: review`. Eligible versioned primary support documentation can pass with an **unverified** label until reproduced. Explicit unsupported evidence, or omission from a list evidenced complete, fails. Missing support or omission from an unmarked list yields unknown; resolve competing claims by #41's conflict order before leaving a genuine tie unknown.
- Synthetic examples: a documented matching artifact/engine/backend tuple passes; an explicitly unsupported GGUF loader tuple fails; generic Safetensors support without architecture coverage is unknown; remote API with opaque runtime is skipped. These are policy examples, not reproduced deployments.
- Recompute after any tuple change; choose a supported artifact/runtime or obtain scoped evidence. Joint tuple, coverage metadata and lineage need CD-3/CD-6/CD-7 review before executable use. The T2 source notes may retain their pre-review wording until their own follow-up; the linked owner disposition governs this T1 reconciliation.

## Memory-fit family: T1 inputs to COMPUTE-01 / W-R6

The former separate T1-M2 proposal is retired into [COMPUTE-01](../../T2-infrastructure/rules/compute-capacity.md#compute-01-per-device-memory-feasibility) and #81's W-R6, as requested in the [PR #88 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868). The [PR #75 disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) defines one family for per-rank fit and co-residency in each memory pool, including CPU/unified memory. Do not create a duplicate T1 rule ID.

- T1 supplies model/artifact/revision, Q2's pinned geometry, selected precision, complete context budgets and [KV manifest](../context-window.md#proposed-kv-cache-handoff-to-10). #10 owns formula/calibration, confidence and per-rank/per-pool allocation; #11 supplies runtime/cache/admitted-sequence evidence. Parameter count or weights alone never establishes fit.
- Applicability is per serving component: local weights and user-selected managed instances are in scope; provider-operated opaque capacity skips local memory fit. Hybrid evaluates its local component independently.
- Fixed severity is `error`, with **`on_unknown: review`**, not blocking. Missing eligible resource evidence yields unknown and a review request; it does not fail the build. A matching estimate meeting the selected minimum resource-confidence policy decides fit. If its range straddles allocation, decide on the upper bound: `fail`, flagged **may not fit**, with the range shown. Label estimated outcomes as estimates, never as measured hardware impossibility.
- Synthetic examples: eligible upper requirement 25 GB versus allocation 48 GB passes the scoped memory screen; requirement range [45,50] GB versus allocation 48 GB fails with **may not fit**; missing cache/placement/runtime inputs yields unknown for review; API-only opaque capacity is skipped.
- Reduce budgets/admission, change a supported artifact/profile or obtain eligible evidence, then recompute. Preserve the ResourceEstimate boundary; interval/configuration/memory-pool metadata needs CD-2/CD-3/CD-7 review. No fabricated measured resource record or universal fit boolean is supplied.

## T1-O2 narrowed: offering fine-tuning capability

- Kinds/roles/pointers: selected `model` and serving `model_provider` both expose existing v1 `/spec/supports_fine_tuning`; model `spec.provider_ref` and build `provided_by` identify the route. Optional T5 selections establish the requested action.
- Applicability: fine-tuning on that offering is selected. When fine-tuning is absent, skip this capability check; unrelated customization is not assumed to be fine-tuning.
- Assertion/evidence: neither model nor provider may explicitly declare `supports_fine_tuning: false`. Both matching true values satisfy this necessary capability check, while account/region eligibility and license conditions remain separate. O1 explicitly excludes fine-tuning for this GPT-5.4 route; its existing catalog record already has false.
- Severity: `error` (fixed). Explicit false on either model or provider fails even if the other value is missing; a broader provider true cannot override model false. If no false is known but a required capability value is absent, the result is unknown, not false.
- Remediation: choose an offering supporting the selected action or obtain scoped capability evidence; do not ask a license answer to override a technical capability failure.
- Edges/consumers: #5/#6 -> #30/#37; model/provider/route changes invalidate the capability result.
- Synthetic examples: model=true/provider=true passes capability only; model=false/provider=true, or model=true/provider=false, fails. The sourced GPT-5.4 direct model=false also rejects fine-tuning using v1 alone. Model=true/provider absent gives unknown; no fine-tuning selected is skipped.
- Version/migration: capability operands exist in v1 and need no new catalog fields. This is a reviewable rule proposal, not a serialized approved Ruleset. #30 still owns training eligibility and license-field sufficiency.

## License conditions: T1 inputs to D-R2a / D-R2b

License/terms interpretation is separate from offering capability. The [#81 deployment proposal at `9786ef6`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/9786ef6f9a7942b21a3cc51a05df741360e3594f/research/T0-configuration/deployment-mode.md#d-r2a-licence-eligibility-conditions-are-met), accessed 2026-10-17, supplies answerable conditions rather than a permanently unknown legal verdict:

- Proposed model `license_conditions` entries identify `condition_id`, text, primary source, `kind: eligibility | obligation`, and a question. Proposed build `licence_answers` bind a `model_selection_id` and condition ID to an answer; eligibility can record a `grant_ref`. These are **not v1 fields**; existing `license_ref`, `access_modes` and `weight_access` remain source inputs.
- D-R2a checks applicable eligibility conditions: `met` or a recorded grant passes; `not_met` without a grant fails; unanswered/unknown yields unknown. Fixed severity is `error`, `on_unknown: review`. Remediation is to answer, record a grant or choose another model.
- D-R2b checks applicable obligations: `acknowledged` passes, `not_acknowledged` fails, unanswered/unknown yields unknown. Fixed severity is `warning`, `on_unknown: defer`. Remediation is to acknowledge or choose another model. Each check skips when its condition kind does not apply; unknown condition coverage does not imply an empty list.
- Synthetic examples use hypothetical reviewed conditions: an eligibility answer `met` resolves pass; `not_met` with no grant resolves fail; an obligation answer `acknowledged` resolves pass; an unanswered applicable condition remains unknown. No actual user answer or approval is invented.
- Q3 and the model/provider notes retain actual license/terms sources; #30 must confirm sufficiency and any ambiguous interpretation. #40 must decide answer storage/link roles (CD-6), answer-state handling (CD-1) and version/migration (CD-7) with affected owners before machine use. A license answer cannot make an unsupported fine-tuning offering pass, and a capability pass cannot satisfy a license condition.
