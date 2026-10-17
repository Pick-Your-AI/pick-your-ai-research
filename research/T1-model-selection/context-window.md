# Context window: request budgets, provider limits and uncertainty

Issue: [#7](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7) · Contract: 1.0.0 · Kind: `context_policy`
Status: research follow-up for owner review; required consumer confirmations pending · Vendor research: 2026-10-16 · Central review reconciled: 2026-10-17

## User decision

Will the complete request and reserved generation fit the selected model **on the selected route**, and what uncertainty, price condition and capacity inputs must the user see? The recommendation is to compare documented limits separately from task quality. A fitting request is not evidence that a model will reliably use every token or meet a latency target. No inference, paid service, token-count API or benchmark was run for this research.

This bounded candidate set covers direct APIs, a Bedrock API route and self-hosted weights. Managed coverage is the conditional dedicated endpoint route in [Model Provider](model-provider.md), whose model and runtime ceilings need exact offering evidence. Under #3's [owner position](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), provider-operated shared Bedrock on-demand is API; managed requires dedicated/reserved capacity. Hybrid applies independently to serving components; a local retrieval service does not make remote generation KV cache local. RAG assembly stays with #16 and sizing with #10.

## Candidate options

All limits below are **published** specifications, not measurements. Numbers are tokens. `Unknown` is not zero. The sources are linked in the evidence register; descriptions of effective quality remain vendor claims unless independently measured.

| Offering / version | Input / output / combined limit | Override and counting conditions | Evidence |
| --- | --- | --- | --- |
| OpenAI API `gpt-5.4-2026-03-05` | No separate maximum input established here; output 128,000; combined 1,050,000 | Combined budget includes input, generated output and reasoning. Reserve generation before allocating input; do not count reasoning twice inside a generation reserve. A snapshot identifies the model, not account entitlement. | CW01, CW02 |
| Claude API `claude-sonnet-5-5`, standard single request | Input shares the window; output 128,000; combined 1,000,000 | Thinking consumes generation budget; retained thinking/history and cached input still consume context. Standard 1M context needs no beta header. The separate Batch beta's 300,000 output allowance is not this route's default. | CW03, CW04 |
| Google Gemini Developer API `gemini-2.5-flash` | Input 1,048,576; output 65,536; **separate budgets**, no combined scalar asserted | Existing active users only at access date; publisher says not deprecated. Do not recommend access for a new project without eligibility. Do not turn independent limits into a sum or treat input capacity as combined capacity. | CW06, CW07 |
| Amazon Bedrock `anthropic.claude-sonnet-4-6`, `bedrock-runtime` | Shared window 1,000,000; AWS lists maximum output 64K (64,000 using publisher decimal notation) | AWS's route-specific value differs from Anthropic's same-model page, which lists 128K output. Keep both provenance records and prefer the serving route's documented cap as a conservative research screen, pending account/API confirmation. For a US route the page lists `us.anthropic.claude-sonnet-4-6`; region/profile entitlement remains a separate check. | CW09, CW10, CW04 |
| Self-hosted `Qwen/Qwen3-8B`, revision `b968826d9c46dd6066d109eabc6255188de91218` | Published native context 32,768; 131,072 with YaRN; independent output cap unknown | Config `max_position_embeddings=40960` is a configuration value, not proof of native quality at that length. The card's 32,768 output recommendation is not a universal output maximum. Runtime/configuration and cache capacity determine admission; YaRN is conditional, not automatic. | CW11, CW12 |

Bedrock versus direct Claude 4.6 demonstrates why an offering identity needs provider, endpoint family, model/version, region/inference profile, feature headers and service tier. Never overwrite the family-wide limit with an observed override or transfer a 4.6 limit to 5.5. The conflicting documents are retained rather than claimed to prove an actual API rejection.

## Comparison fields and contract mapping

The [frozen catalog](../../contracts/v1/schemas/catalog-item.schema.json), [selection schema](../../contracts/v1/schemas/selection.schema.json) and [field guide](../../contracts/v1/docs/COMPONENTS.md) are authoritative. A `context_policy` catalog fact differs from a user's selected token budget. Research-only fields below are proposed vocabulary, not extra v1 `spec` properties.

| Field / location | Type and unit | Evidence requirement / interpretation |
| --- | --- | --- |
| Model `/spec/context_window_tokens` | Integer >=1, tokens | Publisher version and route, **combined** semantics for the baseline sum check. Do not silently map Gemini's separate input limit here. |
| Model `/spec/max_output_tokens` | Integer >=1, tokens | Actual published cap and route, including reasoning semantics; Qwen recommendation is insufficient. |
| Context policy `/spec/max_allowed_tokens` | Optional integer >=1, tokens | Evidenced policy ceiling; never synthesize a vendor policy from a user's preference. |
| Context policy `/spec/supported_truncation` | Optional unique array: `reject`, `truncate_oldest`, `summarize`, `sliding_window` | Documented component support, not permission to discard arbitrary content. |
| Selection `/settings/requested_context_tokens` | Required integer >=1, tokens | Prompt/input budget including instructions, history, retrieved text, memory, tool schemas/results and modality overhead. |
| Selection `/settings/reserved_output_tokens` | Required integer >=0, tokens | Total generation reservation; retain visible/thinking allocation assumptions separately. |
| Selection `/settings/truncation_strategy` | Optional enum | Must be supported; truncation/summarization changes the request and requires recounting and consumer agreement. |
| Selection `/settings/kv_cache_precision` | Optional enum: `fp32`, `bf16`, `fp16`, `fp8`, `int8`, `int4` | Selected cache precision, requiring exact engine support; does not establish layout, scale overhead or actual runtime allocation. |
| `max_input_tokens`, `context_semantics` (proposed CD-11 fields) | Positive integer tokens; enum `shared` / `separate` | Endpoint documentation; separate budgets do not imply an invented combined limit. Unknown semantics remains unresolved research, not a proposed enum value. |
| `provider_override` (research) | Structured record, not boolean | Provider/model/version/endpoint/region/profile/header/tier plus overridden fields, source and access date. Conflicting values remain visible. |
| `tokenizer_id` / revision / chat template (research) | Strings or unknown | Exact model-specific tokenizer artifact/revision, or provider counting endpoint + model/API version. No undocumented tokenizer name invented for proprietary models. |
| `input_estimate` / bounds / basis (research) | Integers, tokens; method string; unknown bound permitted | Exact serialized input and modality settings, counter version, sampling conditions, error method and uncounted segments. No arbitrary confidence percentage. |
| `context_price_tiers` (research; Pricebook owner #39) | Threshold integer + comparator, billing basis, decimal rate/currency/unit, service scope | Primary pricing page and access date; whole-request/session versus marginal tier meaning. |
| `kv_cache_method_ref` / scenario (research) | URI or relative path + version; typed inputs below | Method owned by #10, engine conditions by #11; no GPU fit inferred from context length. |
| Workload `quality_target` and comparable results (research; #81 W-R10) | Optional protocol/metric/reference/degradation target with task-specific measurement envelope | Check only when a target is set; #36 defines comparability and acceptance. Without a target, skip quality checking without an always-on unknown diagnostic. No universal vendor-derived usable-context scalar. |
| Source record | URL, publisher, ISO access date, version, region/currency when priced, grade | Every numeric fact labelled published, measured or estimated. Unknowns carry a named follow-up owner. |

**#40 follow-up:** the [central owner's PR #88 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), accessed 2026-10-17, routes independent budgets through #81 CD-11: proposed model `context_semantics` (`shared` or `separate`) and `max_input_tokens`, with route overrides on the offering. Existing `max_allowed_tokens` retains its total-budget meaning. Gemini 2.5 is a concrete counterexample to treating all context as input-plus-output; no combined limit is invented. Estimate/tokenizer inputs use #81's proposed `input_tokens` {mean, max} and `tokenizer_assumption`; context-policy/model link roles remain CD-6 and pipeline per-stage budgets CD-5. These positions await versioning/migration under CD-7 and affected-owner review; historical v1 records retain their existing meaning. No frozen files are changed. Two `catalog/proposals/t1-context-*.json` records capture only the corresponding GPT-5.4/Sonnet5.5 published ceilings. They are not user budgets or universal policies; their exact model-binding relation/adoption remains with #40. Supported truncation is omitted rather than invented.

Apply #41's [interim checked/verified and conflict policy](evidence.md#evidence-policy-and-gaps). Publisher documentation may support a scoped constraint outcome while its provenance remains unverified. The selected serving route's specific limit wins over a different route's overview; same-scope disagreements follow the policy before remaining unknown. K/M notations in this note use decimal normalization of the publisher's displayed token quantities; no endpoint call independently measured those ceilings.

## Token estimation method and uncertainty

Proposed method, not a measured implementation:

1. Freeze model/route and the full planned request. Include system/developer instructions, role/template markers, retained history/thinking, tools and their results, RAG and memory, media settings and the generation reserve. Count after assembly; recount after edits, compaction, tool rounds, model changes or tokenizer/template changes. Budget future tool results separately until their payloads exist.
2. Prefer the provider's supported request counter for that exact model/API. Claude accepts structured message inputs but currently rejects many server tools, MCP connector inputs and URL/file media sources; unsupported portions remain unknown (CW05). Gemini `count_tokens` counts input, not future generation (CW07). Bedrock advertises Count tokens support for the scoped 4.6 route (CW09); no call was made. OpenAI documents tiktoken-based string estimation (CW02); this note does not establish an exact GPT-5.4 tokenizer mapping or exact whole-request local count.
3. For Qwen, tokenize with the pinned repository's tokenizer and chat template, retaining `enable_thinking` and generation-prompt settings (CW11). Exactness applies to the resulting local token sequence only if the serving runtime uses that same serialization; it does not establish output length or quality.
4. If only text size is known, keep a rough estimate labelled **Estimate**, with tokenizer/language/modality assumptions. A characters-per-token heuristic is not a universal bound. Without calibration, report an unknown error bound and return `unknown` near any limit, not an asserted fit. Do not apply a text ratio to images, audio or video.
5. For a later authorized calibration, compare estimates with provider usage over representative languages, code, tool payloads and media settings. Record signed residuals (`actual - estimate`), sample count, minimum/maximum and empirical quantiles per stratum. Use an upper residual envelope only within the calibrated scope; distinguish an observed sample envelope from a confidence interval or guaranteed bound. Recalibrate after route/tokenizer changes. No residuals or numeric safety margin are invented in this submission.
6. If valid lower/upper input bounds exist, decide conservatively on the upper bound: within every applicable budget is a scoped pass; exceeding any known cap is fail. When the interval straddles the cap, flag the fail **may not fit** and show the range, following the central owner's PR #88 review. This is an estimated screen, not a measured API rejection. With unbounded omitted content, fit is unknown. An unbounded point estimate can support a labelled planning scenario but never an unconditional pass.

For unknown long-context extension configuration, evaluate the limit predicate against the evidenced native limit. Qwen's 100,000-token request without YaRN evidence therefore fails its published native 32,768-token limit; evidence an extended configuration or reduce the request. Independent runtime/memory predicates can remain unknown for review. A native-limit pass never proves runtime support, memory fit or quality.

Thinking is part of generation reservation for the scoped Claude route (CW04). OpenAI includes reasoning in context (CW02). Do not add a reported output total and its reasoning subset again. Cached input may cost less but still occupies context. Reserve length is an admission/planning quantity, not a prediction of billed generated tokens.

## Pricing and capacity

These are **published** context conditions, accessed 2026-10-16, for public standard API pricing in USD; no regional procurement quote or tax-inclusive total is implied. Actual dated rates belong in #39's Pricebooks and must reference exact catalog versions.

| Offering | Context price condition | Cost-estimate handoff |
| --- | --- | --- |
| GPT-5.4 | Input above 272,000 tokens: 2x input and 1.5x output price for the full session on standard/batch/flex; regional processing adds 10% (CW01) | Preserve `>` boundary, session scope and residency condition. Do not apply only to tokens above the threshold; clarify session accounting with #39. |
| Claude Sonnet 5.5 | Standard input USD2 and output USD10 per million tokens; 1M long context uses standard pricing (CW03, CW04) | No older Claude long-context surcharge carried forward. Cache/batch/service charges need their own scoped rate. |
| Gemini 2.5 Flash | Standard text/image/video input USD0.30, audio input USD1.00, output including thinking USD2.50 per million tokens; listed Flash standard rows have no context-length tier (CW08) | Distinguish modality and service tier. Do not copy Pro's threshold to Flash. |
| Gemini 2.5 Pro, price-tier comparison only | Standard prompts <=200,000: input USD1.25/output USD10; >200,000: input USD2.50/output USD15 per million tokens (CW08) | Tier predicate is prompt length and affects both input and output rate. This pricing comparison is not an eligibility recommendation or model catalog addition. |
| Bedrock Sonnet 4.6 | AWS routes pricing to its own Bedrock page (CW09) | Exact regional/profile/service-rate intake remains #5/#39; direct Anthropic rates are not substituted. |
| Self-hosted Qwen | No universal per-token model rate established | #10 supplies capacity and #39 combines actual host/storage/load costs. More nominal context does not specify throughput or latency. |

### Proposed KV-cache handoff to #10

Use [T2's method](../T2-infrastructure/gpu-compute.md) as a proposal to reconcile, not proof of agreement or a benchmark. T1 supplies the following input manifest; T2 owns formulas, units, engine allocation and per-device capacity:

| Input | Type / unit | T1 value or requirement |
| --- | --- | --- |
| Model artifact + config + tokenizer/template | Immutable URI/revision strings | Qwen revision above; API hidden geometry stays unknown |
| Layer count / KV heads / head dimension | Positive integer counts | Qwen published config: 36 / 8 / 128 (CW12); Q heads 32 (CW11). These are model facts, not a complete runtime allocation. |
| Input occupancy and reserved generation | Integer tokens per sequence; lower/upper scenario bounds | Planned full input and generation reserve from the method above; no specific user workload invented |
| Concurrent admitted resident sequences / replicas | Positive integer counts and scenario labels | Engine launch admission is supplied by #11/#10, counting beams/parallel samples; #2 supplies peak in-flight demand. Unknown admission sizes at peak demand under #3's current position; queued requests affect latency, not resident KV allocation. |
| KV dtype and layout / quantization | Named format, effective bytes and scale metadata | Must be supplied by exact runtime #11; weight BF16 does not imply KV BF16 |
| Attention/cache behavior | Window sizes, layer pattern, shared-prefix policy, speculative branches, allocation blocks | Runtime evidence required; unsupported values unknown, not zero |
| Parallel placement | TP/PP/DP/EP and per-rank KV replication/sharding | #10/#11-owned; no division by device count without placement evidence |
| Method version / outputs | Reference + version; GB/GiB with explicit conversion; estimated bounds | #10 returns per-device peak, assumptions and unknowns. No memory formula or SLO is adopted here. |

Token count may constrain a local cache calculation; it is not a latency or quality estimate. For API-only routes, local KV sizing is `skipped`, with provider hardware unknown. Managed dedicated deployments that expose hardware/runtime need the same manifest as self-hosted. A hypothetical fully occupied sequence includes prompt and generation; it is a conservative scenario, not an observed workload. #10/@Mattycodes69 must explicitly agree this input definition before that acceptance item is complete.

## Compatibility proposals and recommendation

[Fit and route rules](rules/context-fit.md) cover shared versus separate limits, output caps, missing inputs and conditional estimates. [Quality, truncation and price warnings](rules/context-warnings.md) cover the decision boundaries. Both follow #40's template and remain proposals. Source-backed numeric constraints are distinguished from proposed policies; no approved Ruleset or universal compatibility boolean is emitted.

Expose advertised/model and serving-route limits with provenance. Check quality separately only when the workload selects `quality_target`, under #81 W-R10 (`error`, `on_unknown: review`); no selected target skips this check without an always-on unknown diagnostic. When a target is set and comparable protocol-specific evidence is missing, the quality result is unknown. Documentation about context degradation (CW04) and Qwen's static-YaRN caveat (CW11) establish reasons to test, not a numeric usable threshold. No primary benchmark matching a particular user's task was established here; #36 still owns evaluation/acceptance policy, with #40 owning versioned operands. Prefer reject-and-explain when exact semantics or required content cannot be preserved; any later summarization/truncation requires #16/#28 agreement and recounting before fit/cost/capacity results are reused. Strategy support uses existing v1 `truncation_strategy`/`supported_truncation` independently of a quality target.

## Evidence

Every source below was opened and inspected on **2026-10-16**. Grade is **Primary documentation** for limits/configuration/prices; qualitative performance statements are **Vendor claim**. Sources are mutable unless a revision is pinned. Public readability is not permission to mirror full documents or datasets; this note records limited factual paraphrases and URLs. No raw downloads or model weights are included. #41 owns freshness and reuse policy.

| ID | Publisher and source | Version / scope | Limitation |
| --- | --- | --- | --- |
| CW01 | OpenAI, [GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4) | `gpt-5.4-2026-03-05`; API; USD context multipliers | Account access not tested |
| CW02 | OpenAI, [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state) | Current API context/token estimation guidance | Generic guidance does not identify exact GPT-5.4 local tokenizer |
| CW03 | Anthropic, [Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) | `claude-sonnet-5-5`; standard API, USD list pricing | Batch beta is a separate condition |
| CW04 | Anthropic, [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) | Current Claude API; 5.5 and 4.6 semantics | Context degradation discussion is not a calibrated usable limit |
| CW05 | Anthropic, [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) | Current counter API; supported input restrictions | Described, not invoked |
| CW06 | Google, [Gemini 2.5 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash) | `gemini-2.5-flash`; Developer API | Existing-user eligibility required |
| CW07 | Google, [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens) | Separate budgets explicitly documented for Gemini 2.5/3 | API versions/model families have different semantics |
| CW08 | Google, [API pricing](https://ai.google.dev/gemini-api/docs/pricing) | Standard paid Developer API; 2.5 Flash/Pro; USD public rates, no regional discount assumed | Not a Vertex AI price quote; additional cache/tool costs excluded |
| CW09 | AWS, [Bedrock Claude Sonnet 4.6](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html) | `bedrock-runtime`, `anthropic.claude-sonnet-4-6`; US inference profile example | Published 64K output differs from Anthropic; no API verification |
| CW10 | Anthropic, [Sonnet 4.6](https://platform.claude.com/docs/en/models/sonnet-4-6/overview) | Direct API current standard limit; legacy active model | 128K is not automatically a Bedrock cap |
| CW11 | Qwen, [pinned model card](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/README.md) | `Qwen3-8B` exact revision | Native/YaRN claim and recommended output; no measured effective context |
| CW12 | Qwen, [pinned config](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/config.json) | Same revision | Model geometry/configuration, not measured runtime allocation |

## Open questions, handoffs and acceptance assessment

Live issue assignees were read on 2026-10-16. No owner confirmation is claimed; root integration must record actual comment/review URLs and exact reviewed revision.

| Required consumer / owner | Decision requested | State |
| --- | --- | --- |
| #10 / @Mattycodes69 | Agree KV manifest, upper occupancy scenarios, API skip and unknown geometry semantics | Pending; required acceptance gate |
| #16 / @zabyxc01 | Accept complete assembled-input budget, preserved instructions, post-transform recount and independent quality check | Pending |
| #28 / @CompleteDotTech | Accept counting retrieved memory/history/thinking, loss warning and recount after summarization | Pending |
| #39 / @PUSHINGSQUARES | Accept prompt-threshold versus output-rate predicate, full-session GPT multiplier, exact version/route/currency conditions | Pending |
| #40 / @tynamite | Review proposed rules and separate-budget/override/tokenizer fields; retain v1 meaning during migration | Pending central review |
| #7 / @zwright8 with #36 / @PUSHINGSQUARES | Approve unknown usable-context display and task-specific evidence protocol | Open product/evaluation follow-up |

| Live #7 criterion | Artifact / section | Assessment |
| --- | --- | --- |
| Fit / warning / unknown rules in #40 format | Linked rule files | Supplied as proposals; central approval pending |
| Token method with stated uncertainty | Token estimation method | Supplied; no invented calibration |
| KV definition agreed with #10 | KV manifest / handoff | Definition supplied; agreement **unmet** |
| Decision record merged at required path | This file | **Unmet** until reviewed canonical merge |
| API / managed / self-hosted coverage | Candidate table | Supplied, hybrid component scope explicit |
| Typed/unit comparison fields and evidence | Comparison table | Supplied; schema gaps explicit |
| Shared-format rules and evidence/hypothesis distinction | Rule files | Supplied as proposals |
| Primary claims with date/version/conditions | CW01-CW12 | Supplied for independent review; no runtime measurement claimed |
| Every required consuming owner confirms | Handoff table | **Unmet**; all four required confirmations pending |
| Named open-question owners | Handoff table / #40 proposal | Supplied |

Validation of the integrated submission must use all commands in `docs/RESEARCH_WORKFLOW.md` under Python 3.12. Automation checks shape/import/reference consistency; it cannot prove source truth, rights, runtime admission, usable quality, owner acceptance or merge. This note and its proposals alone do not close #7.
