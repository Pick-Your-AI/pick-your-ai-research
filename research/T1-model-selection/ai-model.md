# T1 AI Model

Issue: #6 · Contract: 1.0.0 · Kind: `model`
Status: draft for owner review · Last researched: 2026-10-16

## User decision

Select a particular model release and serving artifact that fits a workload and delivery mode. Preserve identity, access and capability evidence separately from runtime fit and measured quality.

## Broader model-family research

The user expanded this assignment on2026-10-17 beyond LLMs and required citations for new and previous research. [Model taxonomy](model-taxonomy.md) now links sourced comparisons for [language/NLP](language-models.md), [perception/OCR](perception-models.md), [embedding/reranking](retrieval-models.md), [generative media/3D/worlds](generative-media-models.md), [speech/audio/music](audio-models.md) and [predictive/scientific/action models](specialized-models.md). The [research inventory](model-research-inventory.json) and [complete source index](model-research-sources.md) retain exact record-to-source mappings, dates and unknowns. These are research notes, not an alternate production catalog or evidence that every possible checkpoint was enumerated.

Non-token and discriminative tasks require task-specific output/admission semantics. The [T1-TAX1 proposal](model-family-contract-proposal.md) preserves frozen v1 and previously accepted #40 routing; it does not force pixels, seconds, sparse vectors, forecast steps, DNA, meshes or actions into invented text-token fields. #14 still owns embedding catalog work; #10/#11/#30/#36/#39 retain their specialized decisions.

## Original language-model slice (captured2026-10-16)

Evidence IDs refer to [the source register](evidence.md); all facts below are published, not independently benchmarked.

| Candidate / identity | Delivery, lifecycle and capability | Architecture / license / context |
| --- | --- | --- |
| OpenAI GPT-5.4 / `gpt-5.4-2026-03-05` | Direct API; named snapshot still documented at capture. Text/image input to text; function calling and structured output documented; this model does not support fine-tuning (O1). | Closed API offering; weights, parameter count, internal architecture/precision and tokenizer internals not established here. Published context/output 1,050,000/128,000 tokens. Service terms require offering-level evidence (O3); privacy/retention uses O2. |
| Claude Sonnet 5.5 / `claude-sonnet-5-5` | Direct API and Bedrock on-demand API offering; active release. Text/image input to text (A1); tool use explicitly documented in the [models overview](https://platform.claude.com/docs/en/models/overview), A7, rechecked2026-10-17. Dateless fixed snapshot, not rolling latest (A2). | No downloadable-weight artifact established by these sources; internal parameters/precision unknown. Published standard context/output 1M/128K; distinct batch beta excluded (A1). Serving API/retention arrangements differ by route (A4/B2). |
| Gemini 2.5 Flash / `gemini-2.5-flash` | Legacy-access API candidate, existing active users only, not deprecated (G1). Text/image/video/audio input to text; publisher tool/schema claims. | Independent input 1,048,576 and output 65,536 budgets; no invented combined limit. Closed internals unknown. Note-only until context semantics map accepted by #40. Paid/unpaid terms differ (G2). |
| Qwen3-8B / immutable repository revision | Self-hosted text-generation checkpoint; Apache-2.0 weights in public ungated source (Q1/Q3/Q4). Card claims agent/tool capability; not a measured end-to-end tool workflow. | 8.2B total dense parameters; 6.95B non-embedding is not active-parameter count. `Qwen3ForCausalLM`, BF16, Safetensors source. 36 layers, 32 query/8 KV heads, head dimension 128. Native 32,768 vs YaRN 131,072; config 40,960 is a separate field (Q1/Q2). |

Bedrock on-demand is a second API offering of the same publisher release, not a claim of a different model or dedicated capacity. Managed coverage is the conditional dedicated Hugging Face endpoint candidate (H1/H2), with exact artifact/engine/instance support still required. Hybrid builds keep per-serving-component modes; no fictitious hybrid model is introduced. These four earlier examples are preserved for their source/date scope; they are not the boundary of the expanded model-family research or a list of current default recommendations.

## Identity and versioning decision proposal

1. Keep publisher, family, exact release/snapshot, serving route and derivative artifact separate. Stable family names support discovery but never pin reproducibility alone.
2. API identity uses the published immutable release ID where available. Record aliases as lookup inputs plus their resolved snapshot and check date. A2 demonstrates that the presence of a date is not a reliable alias test.
3. Open weights use publisher repository plus immutable revision. Pin tokenizer/config/chat-template/license to that revision. A converted or quantized artifact needs its own source/revision, base lineage, format, precision and license evidence; never relabel an arbitrary GGUF as the original BF16 checkpoint.
4. v1 `model.spec.provider_ref` is a single serving/source reference, and build `provided_by` links already bind a selected model to its provider. Following the [#40 owner's PR #88 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), accessed 2026-10-17, no new relation is needed for that binding. Catalog IDs distinguish route-specific model records and notes retain shared publisher identity; richer endpoint identity/alias policy, region and tier use #81's proposed configuration key. This avoids treating an API limit as a universal model fact while versioning the remaining metadata through #40.
5. Intake currently allows one version per catalog ID. Retain historical facts in notes until a reviewed multi-version intake exists; price references always target the exact submitted item version. Do not use the capture date to replace an actual model snapshot.

## Comparison fields

Every field needs a primary URL/access date and version/route conditions. Optional unknowns are omitted from structured proposals and remain explicit in this note.

| Field / JSON pointer or note | Type / unit | Evidence requirement |
| --- | --- | --- |
| `id`, family, publisher ID | Stable string; family note-only | Publisher naming, aliases and canonical mapping. |
| `version`, immutable snapshot/revision | String | O1/A2/Q4; separate capture date from release version. |
| `status`, release/deprecation dates | Enum active/preview/deprecated/retired; ISO dates in notes | Current lifecycle documentation. Gemini's access restriction is not retirement; Anthropic's earliest retirement promise is not an actual deprecation date. |
| `spec.modalities_in/out`, `model_type` | Enum arrays / enum | Exact model and route docs, not family-level advertising. |
| `supports_tool_calling`, `supports_json_schema` | Optional boolean with claim grade | A documented API capability is not a demonstrated workflow or reliable output score. Qwen structured JSON guarantees remain unknown. |
| `spec.supports_fine_tuning` on model and provider | Optional boolean with scoped evidence | Existing v1 technical capability; explicit false on either rejects fine-tuning, independently of license answers. Missing is not false. Model/provider true is necessary capability evidence, not account/region entitlement. |
| `license_ref`, license restrictions | Opaque string plus primary license/terms in notes | Actual checkpoint license, conditions, modification/redistribution/access; #30 confirms sufficiency. Custom/ambiguous terms require a named decision, not assumed permission. |
| Separate NOTICE-file presence (proposed, note-only) | Boolean only for a complete, exact distribution inventory; otherwise unknown | [Pinned checkpoint notice evidence](artifact-notices.md) records the inspected Qwen revision. This supplies no v1 field or blanket derivative permission. |
| `license_conditions` / `licence_answers` (proposed, not v1) | Typed conditions and selection-bound answers; #81 D-R2a/b | Eligibility answers resolve met/not_met or a recorded grant; obligation answers resolve acknowledged/not_acknowledged. Answer/storage/version policy remains with #30/#40; do not write these fields into v1 proposals. |
| `access_modes`, `weight_access` | Enum arrays / optional open/restricted/none | Distinguish service access, actual weights, gating and agreement. No source weights downloaded. |
| Total / active parameters | Integer count, note-only | Q1 total 8.2B is publisher-rounded; active count unknown rather than copying non-embedding count. Closed-model counts remain unknown. |
| Architecture / layers / heads / head dimension | Strings and integers, note-only | Q2 immutable config; KV geometry handed to #10 without asserting GPU fit. |
| `model_formats`, `supported_precisions` | Enum arrays | Exact source artifact and actual runtime support; conversion claims need separate evidence. |
| Tokenizer / template / revisions | Repository IDs/hashes, note-only | Qwen same revision; closed API counting belongs to provider method, not guessed open tokenizer. |
| `context_window_tokens`, `max_output_tokens` | Positive integer tokens | Semantics reconciled with #7. Unsupported separate/conditional budgets stay note-only. |
| Deprecation date | Date or explicit unknown in notes | Source schedule, not inference from model age or release minimum lifetime. |

## Compatibility proposals

See [model/offering rules and shared-family inputs](rules/model-offering.md) and [context research](context-window.md). Former T1-M1/M2 IDs are retired into the #75 joint-support family (COMPUTE-02/ENGINE-02/D-R3) and memory-fit family (COMPUTE-01/W-R6). T1 supplies pinned artifact/geometry/precision/context inputs; T2 owns engine/backend/version support and resource methodology. Missing resource evidence is unknown with `on_unknown: review`, not blocking. Model-format/precision agreement is necessary evidence, not sufficient proof of fit; #36 owns measured quality against a selected target. No quality score, latency number or universal best model is asserted.

## Pricing and capacity

Prices belong to the [provider record](model-provider.md) and Pricebook, not intrinsic model facts. Qwen's published architecture is an input to #10, not a memory guarantee. Native context, selected sequence budget, batch/concurrency, KV dtype, engine overhead and per-device allocation are separate. No local GPU workload or paid API call was run.

## License and access conditions for #30

O3 is the OpenAI Services Agreement effective January 1, 2026: it grants service access rather than model ownership. Section3.3(e) restricts use of output to develop competing models subject to defined Permitted Exceptions; those include specified non-distributed categorization/classification/organization models and customization through OpenAI services. This does not make GPT-5.4 fine-tuning available: O1 expressly says unsupported. The meaning of competition for a concrete proposed training use is a #30/#40 decision, not inferred here.

A6 is Anthropic's Commercial Terms effective June17,2025: sectionsA/B cover service permission and customer input/output rights. D.4(a) addresses competing products/model training/resale and contains an express-approval qualification; D.4(b) separately restricts reverse engineering or duplication. No approval exception for clause(b) is inferred. Customer output rights are not a license to model weights or generic training permission. Route/account-specific agreements and policies still apply; Bedrock delivery does not automatically inherit the direct API agreement.

Qwen Q3 supplies this exact checkpoint's Apache-2.0 license; source conditions/notices and derivative lineage must travel with an artifact. G2 supplies Gemini API terms, including paid/unpaid and geographic distinctions. These linked sources and the typed field table supply #30's requested facts; #30 must confirm sufficiency and decide the proposed action. No agreement was accepted and no legal suitability determination was made during research.

The #40 owner's PR #88 review separates answerable license conditions (#81 D-R2a eligibility and D-R2b obligations) from technical offering capability. The proposed `license_conditions` and `licence_answers` resolve once the user answers the reviewed condition; they are not permanently unknown. Their content, binding and migration still need #30/#40 review. GPT-5.4's existing `supports_fine_tuning: false` rejects a direct fine-tuning request on v1 fields alone; a license acknowledgement cannot override that capability failure.

## Structured artifacts

The [2026-10-18 NOTICE inventory](artifact-notices.md) addresses the separate
file-presence gap identified in [@appletechie's #30 review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6245639699).
That review accepts/narrows T1's licence/access field sufficiency with the
normalization, obligation-answer and inheritance constraints it states. The
Qwen repository result does not resolve notices for every expanded candidate or
downstream distribution, and no proposed field is added to frozen v1.

Complete API record proposals: `catalog/proposals/t1-model-gpt54-openai.json` and `t1-model-sonnet55-anthropic.json`. Internal architecture, unknown precision, or unsupported optional flags are not invented. v1 accepts the necessary model fields without requiring proprietary internals.

Qwen remains a real researched candidate in notes: an example's `max_new_tokens` is not a universal required `max_output_tokens`. Gemini remains note-only because its independent budgets do not justify an invented combined context ceiling. #40 must reconcile these cases rather than weakening frozen v1. OpenAI/Claude model-API formatting does not imply arbitrary third-party protocol compatibility.

## Recommendation and rationale

Expose evidence-qualified filters and conditional compatibility. Favor snapshot IDs over marketing families, source-specific access facts over assumptions, and unknown over silent extrapolation. Evaluate task quality separately before a product recommendation.

## Open questions and handoffs

[Handoff ledger](handoffs.md): [#30's scoped sufficiency review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6245639699) now exists, with normalized licence identifiers, obligation answers, inheritance and distribution-specific NOTICE evidence still requiring their stated treatment. #10/#11 reconcile architecture, format/precision, runtime and context inputs; #16/#25/#35/#36/#39 retain their own modality/capability/quality/pricing decisions. Ambiguous licences go to #30/#40, lifecycle/refresh to #41, context-schema gaps to #40. The receipt's scope is not broader research acceptance, an adopted field or a permission grant.
