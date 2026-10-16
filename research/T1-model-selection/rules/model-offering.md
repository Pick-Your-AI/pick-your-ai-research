# Proposed T1 model and offering rules

Issues: #5, #6 · Contract review: #40 · Status: proposed, not an approved ruleset

Evidence IDs resolve in [evidence](../evidence.md). Existing v1 facts can supply necessary constraints; offering/account/region and architecture relations that lack fields remain note-level proposals. Checked publisher documentation is distinguished from proposed builder policy and independently verified behavior. These rules do not certify measured quality or deployment approval.

## T1-O1: route and model identity

- Participating kinds/roles/pointers: `model_provider` selected supplier `id`; `model` generation `spec.provider_ref`, `id`, `version`; proposed offering relation (no v1 pointer).
- Applicability: a model and a serving/source provider are selected.
- Assertion/evidence: the model reference must resolve to the selected serving/source provider and the intended route-specific release. O1/A1/A2 establish different published identifiers; the filtering policy is proposed. Publisher identity alone cannot equate first-party and Bedrock offerings.
- Severity: `error` (fixed). Missing alias evidence changes the outcome to unknown; it does not change severity.
- Missing data: unknown for unresolved aliases or missing provider/release evidence. No final compatibility boolean.
- Explanation/remediation: select the actual provider-specific release; preserve publisher canonical identity separately.
- Edges/consumers: provider <-> model, #6/#7/#30/#37/#39.
- Synthetic pass: selected OpenAI source and GPT-5.4 OpenAI snapshot's matching provider_ref.
- Synthetic fail: Anthropic direct record selected with an AWS-only serving binding; identical marketing name is insufficient.
- Unknown/non-applicable: unresolved model alias -> unknown; optional absent local engine -> engine condition skipped, not provider failure.
- Version/migration: reference comparison fits v1; cross-route publisher/offering identity needs reviewed #40 versioning. No frozen bytes changed.

## T1-M1: model format and engine support

- Kinds/roles/pointers: `model` generation `spec.model_formats`, `spec.supported_precisions`, `version`; `inference_engine` serving `spec.model_formats`, `spec.supported_precisions`, `version`.
- Applicability: self-hosted weights are actually served by a selected engine, including the local component of a hybrid build. API-only remote serving skips the local-engine condition.
- Assertion/evidence: chosen artifact format and precision must be supported for its architecture by that engine version/backend. Q1 publishes Qwen deployment examples, Q2 source architecture/dtype; T2's version-specific evidence is still required. No broad support claim follows from a generic file format.
- Severity: `error` (fixed); unsupported tuples fail, insufficiently documented conversion conditions remain unknown at the same severity.
- Missing data: unknown for missing chosen precision, architecture implementation or exact engine/backend evidence. An omitted optional field is not false.
- Remediation: choose a supported artifact/runtime or verify the implementation; preserve conversion lineage.
- Edges/consumers: model <-> engine <-> accelerator; #10/#11/#25/#30/#36.
- Synthetic pass: exact artifact/engine/backend evidence explicitly supports the selected tuple (illustrative, not a claim about a real build).
- Synthetic fail: selected GGUF artifact with an engine version explicitly rejecting GGUF.
- Unknown/skipped: generic Safetensors support without architecture support -> unknown; remote API with no local engine -> skipped.
- Migration: full architecture/artifact/serving relation is not in v1; submit #40 extensions and reconcile with #11 before serialized final rules.

## T1-M2: GPU fit requires scoped resource evidence

- Kinds/roles/pointers: `model` generation `id/version/spec`; `accelerator` and `compute_profile` serving selections; `context_policy`; version-pinned ResourceEstimate, as defined by #10.
- Applicability: local weights use a selected compute profile. Remote API-only model does not require the user's GPU.
- Assertion/evidence: a weights-only lower bound cannot establish capacity. Q2 supplies architecture inputs; the adopted pricing/capacity guidance and T2 research require context, KV precision, concurrency, runtime overhead and per-device allocation. T1 supplies inputs, #10 owns the formula/calibration.
- Severity: `error` (fixed); missing-confidence handling follows the accepted #10/#40 policy, proposed blocking unknown rather than pass.
- Missing data: unknown until a matching build/model/artifact/runtime/context revision has adequate resource evidence.
- Remediation: reduce budgets/concurrency, change artifact or compute profile, or obtain an appropriately scoped estimate. Do not infer fit from parameter count alone.
- Edges/consumers: model <-> compute <-> engine; #10/#11/#39.
- Synthetic pass/fail: scoped capacity evidence sufficient/insufficient respectively under its declared assumptions. Synthetic unknown: only aggregate GPU VRAM and parameter count supplied. API-only absence of accelerator: skipped.
- Migration: use existing ResourceEstimate boundary; architecture/lineage additions need #40 review. No measured resource record is fabricated.

## T1-O2: license and offering permission

- Kinds/roles/pointers: `model.spec.license_ref`, `access_modes`, optional `weight_access`, provider offering terms in notes; selected `training_framework` in optional T5.
- Applicability: a selection requires model weights or customization.
- Assertion/evidence: source license, access and current offering/model/region eligibility must permit the requested action. Q3 supplies this checkpoint's license; O1 explicitly excludes fine-tuning for GPT-5.4. Interpretation and policy require #30/#40 review.
- Severity: `error` (fixed). Contradictory restrictions fail; unresolved conditional permission is unknown rather than a change in severity.
- Missing data: unknown for custom/ambiguous terms or unverified entitlement; API tool availability is not permission to train.
- Remediation: satisfy documented conditions, select another eligible offering or obtain the responsible owner's decision.
- Edges/consumers: #5/#6 -> #30/#35/#37; privacy/retention requirements also depend on offering terms, never family-wide assumptions.
- Synthetic pass: owner-reviewed licensed artifact and permitted action. Synthetic fail: GPT-5.4 direct fine-tuning requested despite O1. Unknown: no published custom-model training terms. No optional training selected: training branch skipped.
- Migration: v1 opaque license_ref does not encode a permission decision; richer conditions need #40. #30's approval remains pending.
