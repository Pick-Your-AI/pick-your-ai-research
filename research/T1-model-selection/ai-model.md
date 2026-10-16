# T1 AI Model

Issue: #6 · Contract: 1.0.0 · Kind: `model`
Status: draft for owner review · Last researched: 2026-10-16

## User decision

Select a particular model release and serving artifact that fits a workload and delivery mode. Preserve identity, access and capability evidence separately from runtime fit and measured quality.

## Candidate options

Evidence IDs refer to [the source register](evidence.md); all facts below are published, not independently benchmarked.

| Candidate / identity | Delivery, lifecycle and capability | Architecture / license / context |
| --- | --- | --- |
| OpenAI GPT-5.4 / `gpt-5.4-2026-03-05` | Direct API; named snapshot still documented at capture. Text/image input to text; function calling and structured output documented; this model does not support fine-tuning (O1). | Closed API offering; weights, parameter count, internal architecture/precision and tokenizer internals not established here. Published context/output 1,050,000/128,000 tokens. Service terms require offering-level evidence (O2). |
| Claude Sonnet 5.5 / `claude-sonnet-5-5` | Direct API and Bedrock on-demand API offering; active release. Text/image input to text and tool use documented (A1, models overview linked by A1). Dateless fixed snapshot, not rolling latest (A2). | No downloadable-weight artifact established by these sources; internal parameters/precision unknown. Published standard context/output 1M/128K; distinct batch beta excluded (A1). Serving API/retention arrangements differ by route (A4/B2). |
| Gemini 2.5 Flash / `gemini-2.5-flash` | Legacy-access API candidate, existing active users only, not deprecated (G1). Text/image/video/audio input to text; publisher tool/schema claims. | Independent input 1,048,576 and output 65,536 budgets; no invented combined limit. Closed internals unknown. Note-only until context semantics map accepted by #40. Paid/unpaid terms differ (G2). |
| Qwen3-8B / immutable repository revision | Self-hosted text-generation checkpoint; Apache-2.0 weights in public ungated source (Q1/Q3/Q4). Card claims agent/tool capability; not a measured end-to-end tool workflow. | 8.2B total dense parameters; 6.95B non-embedding is not active-parameter count. `Qwen3ForCausalLM`, BF16, Safetensors source. 36 layers, 32 query/8 KV heads, head dimension 128. Native 32,768 vs YaRN 131,072; config 40,960 is a separate field (Q1/Q2). |

Bedrock on-demand is a second API offering of the same publisher release, not a claim of a different model or dedicated capacity. Managed coverage is the conditional dedicated Hugging Face endpoint candidate (H1/H2), with exact artifact/engine/instance support still required. Hybrid builds keep per-serving-component modes; no fictitious hybrid model is introduced. Candidate breadth is bounded by these contrasting cases; new releases do not trigger a perpetual crawl.

## Identity and versioning decision proposal

1. Keep publisher, family, exact release/snapshot, serving route and derivative artifact separate. Stable family names support discovery but never pin reproducibility alone.
2. API identity uses the published immutable release ID where available. Record aliases as lookup inputs plus their resolved snapshot and check date. A2 demonstrates that the presence of a date is not a reliable alias test.
3. Open weights use publisher repository plus immutable revision. Pin tokenizer/config/chat-template/license to that revision. A converted or quantized artifact needs its own source/revision, base lineage, format, precision and license evidence; never relabel an arbitrary GGUF as the original BF16 checkpoint.
4. v1 `model.spec.provider_ref` is a single serving/source reference. Until #40 approves a richer offering relation, catalog IDs distinguish route-specific model records and notes retain the shared publisher identity. This avoids treating an API limit as a universal model fact.
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
| `license_ref`, license restrictions | Opaque string plus primary license/terms in notes | Actual checkpoint license, conditions, modification/redistribution/access; #30 confirms sufficiency. Custom/ambiguous terms require a named decision, not assumed permission. |
| `access_modes`, `weight_access` | Enum arrays / optional open/restricted/none | Distinguish service access, actual weights, gating and agreement. No source weights downloaded. |
| Total / active parameters | Integer count, note-only | Q1 total 8.2B is publisher-rounded; active count unknown rather than copying non-embedding count. Closed-model counts remain unknown. |
| Architecture / layers / heads / head dimension | Strings and integers, note-only | Q2 immutable config; KV geometry handed to #10 without asserting GPU fit. |
| `model_formats`, `supported_precisions` | Enum arrays | Exact source artifact and actual runtime support; conversion claims need separate evidence. |
| Tokenizer / template / revisions | Repository IDs/hashes, note-only | Qwen same revision; closed API counting belongs to provider method, not guessed open tokenizer. |
| `context_window_tokens`, `max_output_tokens` | Positive integer tokens | Semantics reconciled with #7. Unsupported separate/conditional budgets stay note-only. |
| Deprecation date | Date or explicit unknown in notes | Source schedule, not inference from model age or release minimum lifetime. |

## Compatibility proposals

See [model/offering/engine rules](rules/model-offering.md) and [context research](context-window.md). Model-format/precision agreement is necessary evidence, not sufficient proof of fit. T2 owns engine/backend/version support and calibrated resource methodology; #36 owns measured task quality. No quality score, latency number or universal best model is asserted.

## Pricing and capacity

Prices belong to the [provider record](model-provider.md) and Pricebook, not intrinsic model facts. Qwen's published architecture is an input to #10, not a memory guarantee. Native context, selected sequence budget, batch/concurrency, KV dtype, engine overhead and per-device allocation are separate. No local GPU workload or paid API call was run.

## License and access conditions for #30

O3 is the OpenAI Services Agreement effective January 1, 2026: it grants service access rather than model ownership. Section3.3(e) restricts use of output to develop competing models subject to defined Permitted Exceptions; those include specified non-distributed categorization/classification/organization models and customization through OpenAI services. This does not make GPT-5.4 fine-tuning available: O1 expressly says unsupported. The meaning of competition for a concrete proposed training use is a #30/#40 decision, not inferred here.

A6 is Anthropic's Commercial Terms effective June17,2025: sectionsA/B cover service permission and customer input/output rights, and D.4 restricts competing products/models and reverse engineering absent the stated approval. Customer output rights are not a license to model weights or a generic training permission. Route/account-specific agreements and policies still apply; Bedrock delivery does not automatically inherit the direct API agreement.

Qwen Q3 supplies this exact checkpoint's Apache-2.0 license; source conditions/notices and derivative lineage must travel with an artifact. G2 supplies Gemini API terms, including paid/unpaid and geographic distinctions. These linked sources and the typed field table supply #30's requested facts; #30 must confirm sufficiency and decide the proposed action. No agreement was accepted and no legal suitability determination was made during research.

## Structured artifacts

Complete API record proposals: `catalog/proposals/t1-model-gpt54-openai.json` and `t1-model-sonnet55-anthropic.json`. Internal architecture, unknown precision, or unsupported optional flags are not invented. v1 accepts the necessary model fields without requiring proprietary internals.

Qwen remains a real researched candidate in notes: an example's `max_new_tokens` is not a universal required `max_output_tokens`. Gemini remains note-only because its independent budgets do not justify an invented combined context ceiling. #40 must reconcile these cases rather than weakening frozen v1. OpenAI/Claude model-API formatting does not imply arbitrary third-party protocol compatibility.

## Recommendation and rationale

Expose evidence-qualified filters and conditional compatibility. Favor snapshot IDs over marketing families, source-specific access facts over assumptions, and unknown over silent extrapolation. Evaluate task quality separately before a product recommendation.

## Open questions and handoffs

[Handoff ledger](handoffs.md): #30's owner must confirm license/weight-access sufficiency; #10/#11 must reconcile architecture, format/precision, runtime and context inputs; #16/#25/#35/#36/#39 consume modality/capability/limits/quality/pricing boundaries. Ambiguous licenses go to #30/#40, lifecycle/refresh to #41, context-schema gap to #40. Receiving-owner acceptance and independent research review are pending, not satisfied by authoring this record.
