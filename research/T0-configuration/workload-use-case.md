# T0: Workload / Use Case

Issue: #2 · Contract: v1 1.0.0 (adopted in PR #44; inspected at `a222013`) · Kinds: `workload`
Status: draft, revision 4 (after three internal reviews) · Last researched: 2026-10-16
Deliverable path: `research/T0-configuration/workload-use-case.md` · Companion note: [`research/T0-configuration/deployment-mode.md`](deployment-mode.md)

Labels used in this note:
- **Evidence grades** (from the research method): Primary documentation, Vendor claim, Independent measurement, Estimate.
- **Proposal:** a design choice made in this note, not a sourced fact.
- **C-** IDs cite the v1 contract; **E-** IDs cite external sources; **CD-** IDs are open contract decisions (see [Open contract decisions](#open-contract-decisions)); **EV-1** is the evidence eligibility predicate defined in the companion note.

## Scope

This note is written **local-first**: the T0 owner has chosen to prioritise running open-weight models on hardware the user owns or rents. This is a choice of emphasis, not a claim that other paths matter less. The contract shows why it is useful: 17 of its 45 baseline rules apply only to self-hosted builds (C3).

The workload profile applies in every deployment mode. Only the examples and depth favour self-hosting. The other workstream owners should confirm this emphasis.

## Summary

- The builder asks about eleven groups of inputs. It can start filtering as soon as any of them is answered, and refines the results as more arrive. The groups are:
  - task;
  - number of turns;
  - interaction pattern;
  - modalities and output format;
  - capability needs;
  - load and lengths;
  - performance targets;
  - quality;
  - hardware;
  - network and data constraints;
  - budget.
- **Main finding.** In the v1 contract, the workload profile does not drive any rule.
  - These fields are not read by any baseline rule, by the reference evaluator, or by the cost and resource schemas (C1, C3, C7): `workload_type`, `modalities`, `concurrency`, `requests_per_day`, `avg_input_tokens`, `avg_output_tokens`, `latency_budget_ms` and `uptime_target_pct`.
  - Their copies in `build.objectives` are not read either.
  - Rules do read `objectives.region`, `objectives.data_classification` and `objectives.monthly_budget_amount`.
  - The evaluator also reads the context policy's `requested_context_tokens` and `reserved_output_tokens` (C7).
- **Proposals:**
  - Output-based task axes.
  - A field dictionary covering local hardware fit: separate input and output lengths, a quality target, available hardware including CPU-only servers, and network isolation.
  - The workload stored as a profile owned by the build.
  - No silent substitution for unknown answers.
  - Ten rule proposals, all hypotheses.
- **Not settled here.** Several design questions are recorded as open contract decisions for #40 and #41 rather than settled in this note. Examples are how unknown answers are represented to the evaluator (CD-1), shared memory pools (CD-2) and per-stage loads (CD-5).

## User decision

What is the user building, and which goals and constraints should filter and rank every later choice, above all the model artifact, inference engine and hardware?

## Candidate options

| Option | Description | Assessment |
| --- | --- | --- |
| A. v1 as-is | One `workload_type` enum, one `modalities` array, and load and latency fields (C1) | The values mix concepts (see [Taxonomy](#taxonomy-proposal)), and no rule reads them (C3). The workload profile lacks input/output length extremes, a quality target and available hardware. Context tokens exist separately on the context policy (C2). |
| **B. Independent profile** (recommended) | The axes and field dictionary below | Each field has a defined type and drives a named downstream decision (Proposal) |
| C. Named presets only | The user picks a template | Rejected as the only mechanism. Kept as a way to fill in values, which are then shown and editable (Proposal). |

**Deployment modes.** The profile is the same for every mode; the mode is decided per component in the companion note. Load, lengths and performance targets feed device sizing for self-hosted and dedicated capacity (#10, #11), and provider limits and cost for APIs (#5, #39). Performance evidence uses an identity appropriate to each mode (see W-R7).

## Design principle: targets, not methods

The profile records what the user needs, not how to achieve it. It does not record a quantization method, an engine, an offloading strategy or a kernel.

Methods change quickly:
- vLLM's minor releases v0.28.0 to v0.31.0 were published between 26 August and 5 October 2026, about two weeks apart (E13).
- llama.cpp's repository has 17 build tags whose commits are dated 16 October 2026 (UTC), from `b11676` at 01:58 to `b11696` at 08:51; not every tag became a published release (E13).
- vLLM's quantization chart says it "is subject to change as vLLM continues to evolve" (E12).

The answers should stay valid while the builder re-checks fit.

**One deliberate exception.** `precision_preference` records a method preference, such as "nothing below 4 bits per weight". It is labelled as a preference and never stands in for quality evidence (W-R9, W-R10).

## Taxonomy (Proposal)

### Why not the v1 enum

v1's `workload_type` takes one of `chat`, `completion`, `rag`, `agentic`, `embedding`, `fine_tuning`, `batch` or `multimodal` (C1). These values describe different things:
- an interaction style: `chat`;
- tasks: `completion`, `embedding`;
- architectures: `rag`, `agentic`;
- customisation: `fine_tuning`;
- a traffic pattern: `batch`;
- a modality: `multimodal`.

One workload often matches several. Nightly classification of scanned invoices against a product list is batch, multimodal and retrieval-backed at once.

### Axis 1: task, classified by output

The **primary task** is the output the user acts on. Other outputs go in `secondary_tasks`.

| Value | Output | Boundary examples |
| --- | --- | --- |
| `extraction_classification` | Structured fields or labels | Invoice field extraction; ticket routing; duplicate/not-duplicate labels |
| `retrieval_ranking` | Items ranked or matched from a corpus; may generate no text | Document search; "find similar tickets" |
| `code` | Source code or machine-executed queries | IDE assistant, including a conversational one (Axis 2); text-to-SQL |
| `generation_transformation` | Free-form content | Drafting, summarisation, translation, transcription |
| `other` | Anything else; requires `task_description` | — |

**How the overlaps resolve:**
- A conversational coding assistant is `code` with `turns: multi`.
- A speaker-labelled transcript whose user reads the text is `generation_transformation`, with `extraction_classification` as a secondary task.
- Duplicate detection is `retrieval_ranking` if it returns similar items, and `extraction_classification` if it returns a label.

**Questions answered from the user's documents** are a capability need (Axis 5), not a task.

**Embedding-only builds.** v1 can represent an embedding model as a `model` selection, because `model_type` includes `embedding`. `rule.required.foundation` requires a `model` selection, not a generative one (C1, C3). Such a build can pass through `model`, but not through the separate `embedding_model` kind, and it must still carry `model` fields such as `max_output_tokens` (Q3).

### Axis 2: turns

`single` or `multi`. Multi-turn workloads carry conversation history, which raises input length.

### Axis 3: interaction pattern

| Value | Definition | Sized for | Example |
| --- | --- | --- | --- |
| `interactive` | A person waits for the response, often streamed | Latency per request | Chat UI, IDE completion |
| `background` | System-to-system with no person waiting; seconds to minutes | Latency, with slack | Enriching records on a webhook |
| `batch` | Large sets processed offline; hours | Throughput and a completion window | Nightly re-classification |

MLPerf Inference measures these patterns differently (E1):
- Its Server/Interactive scenario sends queries on a Poisson schedule. It reports the maximum throughput that meets a latency bound at the 99th percentile, qualified by an early-stopping rule.
- Its Offline scenario reports throughput.

NVIDIA defines system throughput separately from per-request latency (E3).

### Axis 4: modalities and output format

- **`modalities_in` and `modalities_out`** describe the workload's external interface: what the user sends and receives. Each is a subset of the v1 enum (C1).
  - A pipeline (for example, speech-to-text followed by a text model) can meet the interface even when no single model can (W-R1).
- **`output_format`** is one of `free`, `json` or `json_schema`.
  - `json` requires syntactically valid JSON.
  - `json_schema` requires JSON that conforms to a supplied schema.
  - Both need a declared enforcement mechanism. Either the final model is declared to support schema-constrained output (`supports_json_schema`, C1), or the pipeline declares an `output_enforcement` of `constrained_decoding` or `validate_and_retry` (Proposal). v1 has no capability flag for plain JSON.
  - Proposal: keep v1's `structured` modality for structured inputs such as tables; #40 to confirm.

Open-weight models differ here, even within one family. According to their 2026 model cards:
- Gemma 4 takes text and image input across the family, adds audio input only on the E2B, E4B and 12B sizes, and generates text (E7).
- Qwen3.8-27B supports image and video understanding (E8).
- DeepSeek-V4.1-Flash natively processes images and text and generates text (E18).
- Voxtral Mini 4B Realtime transcribes speech (E9).
- Qwen3-TTS generates speech from text (E10).

### Axis 5: capability needs

| Field | Values | Recommends |
| --- | --- | --- |
| `knowledge` | Set of `reference_documents` and/or `structured_lookup`; or exactly `none`; or `unknown` | T3, or a declared alternative per capability (W-R2) |
| `actions` | `none`, `read_only`, `write` | T4 (W-R3); guardrails for `write` (W-R4) |
| `customisation` | `none`, `prompt_only`, `fine_tune` | T5 (W-R5) |

## Field dictionary

The proposed location is a `workload` object owned by the build (Recommendation 1), referenced below as `/workload/...`. How answer states are encoded is open (CD-1); see [Unknown and missing answers](#unknown-and-missing-answers-proposal). Items that are still open contract decisions are marked CD-n rather than presented as complete.

| Field | Type, units, allowed values | Constraints | Applies when | Evidence requirement | v1 today |
| --- | --- | --- | --- | --- | --- |
| `task` | enum (Axis 1) | Required; `other` needs `task_description` (1–500 characters) | Always | User input | `workload_type` (different values) |
| `secondary_tasks` | set of Axis 1 values | Excludes the primary task | Always | User input | — |
| `turns` | enum `single`, `multi` | — | Always | User input | — |
| `interaction_pattern` | enum `interactive`, `background`, `batch` | — | Always | User input | `batch` value only |
| `modalities_in`, `modalities_out` | non-empty sets of the v1 modality enum | — | Always | Model support from model cards (E7–E10, E18) | `spec_workload.modalities` (single array) |
| `output_format` | enum `free`, `json`, `json_schema` | `json_schema` needs `output_schema` (a JSON Schema document) | Always | User input | — |
| `knowledge` | set (Axis 5) | `none` and `unknown` are exclusive | Always | User input | — |
| `knowledge_implementation` | object keyed by capability: `{via: rag \| knowledge_base \| long_context \| tool \| direct_lookup, selection_ids: [IDs], justification: string}` | One entry per capability in `knowledge`; `long_context` and `direct_lookup` need a justification | When `knowledge` has values | User input, reviewed against #7 and #16 | — |
| `actions` | enum `none`, `read_only`, `write` | — | Always | User input | — |
| `customisation` | enum `none`, `prompt_only`, `fine_tune` | — | Always | User input | `fine_tuning` value only |
| `requests` | `{count: integer ≥ 0, period: day \| month}`, unit: requests | — | Always | User input or preset | `requests_per_day` (three copies) |
| `peak_concurrency` | integer ≥ 1, requests in flight | — | Always | User input or preset | `concurrency` / `max_concurrency` |
| `input_tokens` | `{mean: decimal, max: integer}`, tokens per request | 1 ≤ mean ≤ max; includes history when `turns` is `multi` | Text input | User input; any conversion from words is an Estimate (E6) | `avg_input_tokens`; context policy `requested_context_tokens` (C2) |
| `output_tokens` | `{mean: decimal, max: integer}` or `not_applicable` | 0 ≤ mean ≤ max | Whenever generated tokens are expected, whatever the task; `not_applicable` only when the serving operation generates no tokens (see below) | User input | `avg_output_tokens`; context policy `reserved_output_tokens` (C2) |
| `native_input_units`, `native_output_units` | `{images_per_request, audio_seconds, video_seconds}`, each as `{mean: decimal, max}`; `max` is an integer for image counts and a decimal for durations | All values ≥ 0; mean ≤ max | Non-text input or output | User input; token conversion is per model (#7) | — |
| `tokenizer_assumption` | string: a tokenizer or model ID, or `model_native` | — | When counts are in tokens | User input | — |
| `latency_targets` | list of `{metric: ttft \| tpot \| e2e, value_ms: integer ≥ 1, percentile: 50 \| 90 \| 95 \| 99}` | At most one entry per metric | `interactive`, `background` | Metric definitions per E2, E3 | `latency_budget_ms` |
| `throughput_target` | `{value: decimal > 0, unit: output_tokens_per_second \| requests_per_second \| items_per_hour, scope: aggregate \| per_request}` | — | Mainly `batch` | E1, E3 | — |
| `completion_window_hours` | decimal > 0 | — | `batch` | User input | — |
| `availability_target` | `{percent: decimal 0–100, period: day \| month \| year}` | — | Always | User input | `uptime_target_pct` |
| `quality_target` | `{protocol_id, metric_id, direction: higher_better \| lower_better, reference_result_id, max_degradation: {value: decimal ≥ 0, kind: absolute \| relative_percent}}` | `relative_percent` not allowed when the reference value is 0 | Optional | Bound to a #36 evaluation protocol (W-R10) | — |
| `precision_preference` | `{min_stored_bits_per_weight: decimal > 0}` | — | Optional | Artifact card (E17) | — |
| `hardware` | See the next table | — | Always | User input; details detected by the reporting harness where possible | `spec_accelerator.vram_gb` only (C1) |
| `network` | enum `online`, `private_network`, `air_gapped` | — | Always | User input | `network_isolation` on hosting selections (C2) |
| `data_classification` | v1 enum | Level definitions open (Q1) | Always | User input | `objectives.data_classification` (C5) |
| `data_categories` | set of `personal_data`, `special_category`; or exactly `none` / `unknown` | Exclusive values as stated | Always | Definitions per E23 | — |
| `residency.processing`, `residency.storage` | each: a list of jurisdiction codes, or `none` (unconstrained), or `unknown` | Evaluated independently (D-R6 in the companion note); codes per ISO 3166 (E25); containment hierarchy and named groups to be set by #41 (CD-9) | Always | User input | `objectives.region` (one string) |
| `budgets` | list of `{amount: decimal ≥ 0, currency: ISO 4217 alpha code, period: one_off \| month \| year, scope: hardware \| operating \| total}` | An empty list means no budget constraint | Always | Currency per E24 | `objectives.monthly_budget_amount` |

`mean` is the expected mean per request, used for throughput and cost. It is a decimal, because the mean of whole counts needn't be whole: one request with 1 output token and one with 2 have a mean of 1.5. `max` is used for memory sizing.

**When output tokens are `not_applicable`.** Only when the serving operation generates no tokens, such as an embedding call or a classifier head that returns scores. The task label doesn't decide it. A generative model that returns a JSON label is still `extraction_classification`, but it generates tokens, and those count toward cost, the context reservation and service-level measurements. If the operation hasn't been chosen yet, record the expected output load. Per-stage loads for pipelines are CD-5.

**`hardware` in detail:**

| Field | Type and units | Constraints | Notes |
| --- | --- | --- | --- |
| `mode` | enum `use_existing`, `acquire`, `undecided` | Required | Describes the user's situation; it doesn't switch rules on or off (W-R6) |
| `devices[]` | list | At least 1 when `use_existing` | CPU-only servers are valid devices |
| `devices[].device_id` | string, stable within the build | Unique | Selected devices reference it, so the inventory and selections can be reconciled (CD-6) |
| `devices[].kind` | enum `gpu`, `cpu`, `npu`, `other` | — | — |
| `devices[].catalog_ref` | accelerator catalog ID | Optional | From #10's catalog |
| `devices[].model_name` | string | Required | — |
| `devices[].memory_gb` | decimal > 0, gigabytes (10⁹ bytes) per device | — | For CPUs: system memory available to inference |
| `devices[].memory_pool_id` | string | Devices sharing physical memory share an ID | Unified memory: the CPU and GPU share one pool (E14); full semantics in CD-2 |
| `devices[].memory_bandwidth` | `{value_gb_per_s: decimal > 0, basis: vendor_peak \| measured}`, gigabytes (10⁹ bytes) per second | Optional | Often the limiting factor for single-batch generation (E19–E21) |
| `devices[].isa_features` | set, e.g. `avx2`, `avx512f`, `amx`, `neon`, `sve` | Optional | CPUs only |
| `reserved_memory_gb` | decimal ≥ 0 per memory pool | — | Memory kept for the OS and other uses, counted once per pool |
| `location` | `{jurisdiction: ISO 3166 code, site_label: string}` | `jurisdiction` required when residency is constrained | Replaces a cloud region for owned hardware (E25) |

### Unknown and missing answers (Proposal)

**Intended semantics:**
- **`provided`:** a value. Preset values are `provided` but carry `source: "preset:<name>"` and are shown as editable assumptions.
- **`unknown`:** the user answered "I don't know".
- **`missing`:** not yet asked.

Both `unknown` and `missing` must evaluate as unresolved, giving the outcome `unknown` in compatibility rules (C4).

**This is not existing contract behaviour.**
- In the pinned reference evaluator, an absent value is unresolved, but the string `"unknown"` is an ordinary known value.
- A probe confirmed this. `network == "air_gapped"` evaluates to `false` for the string `"unknown"`, which would skip a rule, but is unresolved for an absent key (C7).
- A typed answer-state representation and an evaluator normalisation step are therefore needed, including for nested fields (CD-1).

**Policy:**
1. **No substitution.** Filtering never assumes a value. Filters that need an unresolved input are not applied, and results say "not checked against <input>".
2. **Compatibility rules** (W-R1, W-R6, W-R7, W-R8, W-R10) are written so that an unresolved input makes the applicability or assertion unresolved, giving `unknown`. They don't treat "answered" as a precondition.
3. **Recommendation rules** (W-R2 to W-R5) only recommend. Their applicability is "the answer is known and …", so an unresolved answer makes them `skipped`. This is a deliberate exception, needed so that they don't nag. CD-1 must let the evaluator distinguish "not relevant", "not yet known" and "not selected".
4. **Interface:** `missing` prompts the builder to ask; `unknown` is listed as an open assumption.

**Load presets** are order-of-magnitude bands. The boundaries are design choices, to be calibrated with #10 and #39:

| Preset | `requests.count` per day |
| --- | --- |
| `personal` | fewer than 1,000 |
| `team` | 1,000–100,000 |
| `production` | more than 100,000 |

**Words to tokens.** OpenAI gives approximately 4 characters, or three-quarters of a word, per token for English as estimates. Counts vary by model, encoding and language (E6).

## Why context, quality and hardware are front-door inputs

**Context length and concurrency set memory use, alongside the weights.**
- The PagedAttention paper calculates the KV cache of OPT-13B at 800 KB per token in FP16, and up to 1.6 GB for one 2,048-token request. It notes that the cache grows during generation (E4).
- Its authors report that the existing systems they profiled used only 20.4%–38.2% of KV cache memory for token states (E5, Vendor claim). Memory needs therefore depend on the engine too.

**Separate input and output lengths.**
- The v1 evaluator adds `requested_context_tokens` and `reserved_output_tokens` (C7).
- Proposed mapping for simple text generation: `requested_context_tokens` ← `input_tokens.max`, and `reserved_output_tokens` ← `output_tokens.max`. This avoids counting output twice.
- Pipelines with several stages need per-stage loads (CD-5).

**Usable context is a deployment setting.** Qwen3.8-27B's card gives 262,144 tokens natively, "extensible up to 1,000,000 tokens" (E8). What fits locally depends on memory left after the weights (E4).

**Precision variants change memory, engine choice and possibly quality. Quality therefore has its own evidence-based target.**
- Google publishes Gemma 4 quantization-aware-trained checkpoints as a Q4_0 GGUF, as w4a16 compressed-tensors for vLLM, and as a mobile scheme. It states that QAT preserves "similar quality to bfloat16" (E7, Vendor claim).
- Qwen publishes an official FP8 Qwen3.8-27B with "performance metrics … nearly identical to those of the original model" (E8, Vendor claim).
- NVIDIA reports benchmarks for Nemotron 3.5 Super VL in both BF16 and NVFP4 (E11, Vendor claim).
- Ternary Bonsai 2 27B is a third-party ternary derivative of Qwen3.8-27B (E17):

  | Representation | Bits per weight | Language-model size |
  | --- | --- | --- |
  | Ideal ternary (logical) | 1.72 | — |
  | PTQ1_0 packing (stored) | 1.75 | 5.95 GB |
  | PQ2_0 packing (stored) | 2.13 | 7.21 GB |
  | FP16 baseline | 16 | about 54 GB |

  An optional 0.63 GB vision component is separate. Memory estimates use stored sizes plus any components loaded.

None of these is an independent measurement, and none sets a general ordering of quality. `quality_target` is evaluated only against comparable evaluation evidence (W-R10). `precision_preference` is a separate preference (W-R9).

**Hardware, including servers people already own.**
- **Unified memory:** MLX describes a model in which arrays live in shared memory (E14). IBM publishes Granite 4.2 as separate bf16, 8-bit and 4-bit MLX repositories "for native inference on Apple Silicon" (E15; its memory guidance is not relied on).
- **Offloading:** Qwen describes Qwen3.8-Flash-Next's 51B of n-gram embeddings as "more amenable to offloading than Mixture-of-Experts" (E16).
- **CPU-only servers are valid devices.**
  - Arm and NVIDIA describe token generation (decode) as memory-bound (E19, E20, Vendor claims).
  - The SqueezeLLM paper reports memory bandwidth as the main bottleneck for single-batch generation (E21).
  - How far this holds for a given CPU, batch size or offload split is for measured fit records to show, not for this note to assume.
  - The useful front-door answers are system memory size, CPU model and, if known, memory bandwidth. The companion note covers CPU engines and offload; #10 owns sizing.

**Data notes.**
- The v1 `data_classification` levels are undefined (Q1).
- FIPS 199 is cited only for contrast, as a three-level US federal scheme (E22).
- `data_categories` align with the GDPR definitions (E23). Classification is a design choice, not legal advice.

**Latency notes.**
- MLPerf's Server/Interactive scenario uses a 99th-percentile bound with an early-stopping qualification (E1). For LLMs, the bound is stated as benchmark-specific TTFT/TPOT pairs: for Llama2-70b, 2000 ms/200 ms ("Conversational") and 450 ms/40 ms ("Interactive") (E2).
- NVIDIA cautions that results are comparable only when definitions match (E3).

## Mapping: inputs to downstream decisions

| Input | Drives | Consumer issues | v1 today |
| --- | --- | --- | --- |
| `task`, `secondary_tasks` | Model ranking; evaluation criteria | #6, #36 | `workload_type`; no rule |
| `turns` | Context growth | #7 | — |
| `interaction_pattern` | Latency vs throughput sizing; cost | #10, #11, #39 | `batch` value; no rule |
| `modalities_*`, `output_format` | Pipeline filter (W-R1) | #6, #13 | Modalities; no rule |
| `knowledge`, `actions`, `customisation` | Recommend T3, T4, T5 (W-R2 to W-R5) | #13, #16, #25–#28, #30–#33, #35 | — |
| `requests`, `peak_concurrency`, lengths | Memory, device count, cost | #10, #11, #39 | No rule |
| `latency_targets`, `throughput_target`, `completion_window_hours` | Model, quantization, device and engine choice; monitoring; evaluation | #6, #10, #11, #36, #38 | `latency_budget_ms`; no rule |
| `quality_target` | Which artifacts qualify, once comparable evidence exists | #36 | — |
| `precision_preference` | Labelled preference filter | #11 | — |
| `hardware` | Whole-build memory fit (W-R6) | #10, #9 | — |
| `network` | Isolation check (W-R8) | #3, #9, #37 | No rule |
| `availability_target` | Redundancy; monitoring | #9, #37, #38 | No rule |
| `data_classification`, `data_categories` | Provider and host terms; guardrails; access control; redaction | #3, #5, #13, #35, #38 | Classification read by two rules (C3) |
| `residency` | Processing and storage locations, including external destinations | #3, #9, #37 | `objectives.region`, read by two rules (C3) |
| `budgets` | Hardware and operating cost checks | #39 | Monthly cap only (C3) |

## Activation rules for T3, T4 and T5 (Proposal)

Selections remain authoritative, as in v1 (C4). The answers recommend tiers, and W-R2 to W-R5 report gaps as warnings. Each knowledge capability is satisfied separately:

| Need | Satisfied by |
| --- | --- |
| `knowledge` includes `reference_documents` | A `knowledge_base` or `rag_pipeline` selection, or a `long_context` implementation with a justification |
| `knowledge` includes `structured_lookup` | A `rag_pipeline` or `tool` selection, or a `direct_lookup` implementation with a justification |
| `actions` is `read_only` or `write` | An `agent_framework`, `tool` or `mcp_server` |
| `actions` is `write` | Also a `guardrail` |
| `customisation` is `fine_tune` | A `fine_tuned_model` or `training_framework` |

When an answer is `none`, the tier is collapsed (the user can still add it). When an answer is unresolved, the tier is shown as optional and the rules are `skipped`.

## Compatibility proposals

All rules are hypotheses for #40 review, using the v1 separation of severity (`info`/`warning`/`error`) from outcome (`pass`/`fail`/`unknown`/`skipped`).
- Each rule has one fixed severity, as the ruleset schema requires (C10).
- A known violation is `fail`. Ineligible, missing or conflicting evidence leaves the dependent value unresolved, so the outcome is `unknown`.
- Examples are synthetic.
- None of these rules is approved or executable yet. All of them need CD-1 and the new fields. The evidence-based rules (W-R6, W-R7, W-R10) also need CD-3 and CD-8.

**Template fields.** Each proposal covers the fields of the repository's rule-proposal template (C9). Fields that are the same for every rule are stated once here rather than repeated:
- **Severity and missing-data policy:** the table below.
- **Explanation:** the builder shows the rule's title, the part of the assertion that failed or couldn't be resolved, and the inputs involved. Each rule's remediation follows.
- **Affected consumers:** the builder's compatibility results, #40's ruleset, and the issues under each rule's dependencies.
- **Version and migration impact:** CD-7, for every rule.
- **Source evidence:** cited in the assertion or examples.

| ID | Rule | Severity | `on_unknown` |
| --- | --- | --- | --- |
| W-R1 | Modalities and output format fit the pipeline | `error` | `review` |
| W-R2 | Each knowledge need has an implementation | `warning` | `defer` |
| W-R3 | Actions need a T4 component | `warning` | `defer` |
| W-R4 | Write actions need a guardrail | `warning` | `defer` |
| W-R5 | Customisation need is met | `warning` | `defer` |
| W-R6 | Components resident together fit each memory pool | `error` | `review` |
| W-R7 | Performance evidence matches the configuration and workload | `error` | `review` |
| W-R8 | Air-gapped builds have no external connections | `error` | `block` |
| W-R9 | Precision preference respected | `warning` | `defer` |
| W-R10 | Quality target backed by comparable evidence | `error` | `review` |

**Migration.** These rules depend on new build-level fields and on CD-1. Whether that is additive or a replacement, and which contract version it needs, is for #40 to decide (CD-7).

### W-R1 Modalities and output format fit the pipeline

- **Roles and pointers:**
  - build: `/workload/modalities_in`, `/workload/modalities_out`, `/workload/output_format`;
  - build: `/pipeline`, an ordered list of selection IDs of kind `model` or `fine_tuned_model` (Proposal; defaults to the primary model);
  - build: `/output_enforcement` (Proposal);
  - catalog `model`: `/spec/modalities_in`, `/spec/modalities_out`, `/spec/supports_json_schema` (C1);
  - catalog `fine_tuned_model`: v1 has no modality or schema-support fields; it names its base through `/spec/base_model_ref` and marks adapters with `/spec/adapter_only` (C1).
- **Applies when:** at least one pipeline stage is selected.
- **Assertion:** all of the following hold:
  - the workload inputs are a subset of the first stage's inputs;
  - each stage's outputs intersect the next stage's inputs;
  - the workload outputs are a subset of the last stage's outputs;
  - if `output_format` is `json` or `json_schema`, the last stage has `supports_json_schema: true`, or `output_enforcement` is `constrained_decoding` or `validate_and_retry`.
- **Fine-tuned stages.** A full fine-tuned model or an adapter on its base can be a stage. How its effective modalities and schema support are derived, for example whether they are inherited from the base model, is left to CD-6 with #6 and #33. Until then they are unresolved, so a fine-tuned stage gives `unknown` rather than borrowing the base model's values.
- **Missing data:** unresolved modalities or capabilities give `unknown`.
- **Remediation:** choose models with the needed modalities, add a stage, or declare output enforcement.
- **Dependencies:** #6, #33, #40; CD-6.
- **Examples:**
  - Pass: audio → text, with pipeline [speech model, LLM].
  - Fail: the same workload with pipeline [LLM].
  - Fail: `output_format: json` with `output_enforcement: none` and no schema support.
  - Unknown: `json` required and enforcement not recorded.
  - Unknown: the last stage is a fine-tuned model, whose effective capabilities aren't defined yet (CD-6).
  - Skipped: no model selected.

### W-R2 Each knowledge need has an implementation

- **Roles and pointers:** build `/workload/knowledge`, `/workload/knowledge_implementation`; selections of `knowledge_base`, `rag_pipeline`, `tool`.
- **Applies when:** `knowledge` is known and has values.
- **Assertion:** for each capability in `knowledge`, an implementation exists per the activation table, and any `long_context` or `direct_lookup` implementation has a justification.
- **Missing data:** `skipped` if `knowledge` is unresolved; `unknown` if a referenced selection doesn't resolve.
- **Remediation:** add T3, or declare and justify an alternative (#7, #16).
- **Dependencies:** #7, #13, #16.
- **Examples:**
  - Pass: documents through a RAG pipeline, plus structured lookup through a tool.
  - Pass: documents through `long_context`, plus `direct_lookup`, each justified.
  - Fail: both needs, with only a `knowledge_base` (which covers documents but not structured lookup).
  - Skipped: `knowledge` is `unknown`.

### W-R3 Actions need a T4 component

- **Roles and pointers:** build `/workload/actions`; selections of kind `agent_framework`, `tool`, `mcp_server`.
- **Applies when:** `actions` is known and is `read_only` or `write`.
- **Assertion:** an `agent_framework`, `tool` or `mcp_server` is selected.
- **Missing data:** `skipped`.
- **Remediation:** add an agent framework, tool or MCP server, or correct the `actions` answer.
- **Dependencies:** #25–#27.
- **Examples:**
  - Pass: `write` with a tool.
  - Fail: `read_only` with no T4 component.
  - Skipped: `actions` missing.

### W-R4 Write actions need a guardrail

- **Roles and pointers:** build `/workload/actions`; selections of kind `guardrail`.
- **Applies when:** `actions` is known and is `write`.
- **Assertion:** a `guardrail` is selected.
- **Missing data:** `skipped`.
- **Remediation:** add a guardrail.
- **Dependencies:** #35. If #35 wants `error` in production, that is a separate production-only rule, not a conditional severity.
- **Examples:**
  - Pass: a guardrail is selected.
  - Fail: none is selected.
  - Skipped: `actions` is `none`.

### W-R5 Customisation need is met

- **Roles and pointers:** build `/workload/customisation`; selections of kind `fine_tuned_model`, `training_framework`.
- **Applies when:** `customisation` is known and is `fine_tune`.
- **Assertion:** a `fine_tuned_model` or `training_framework` is selected.
- **Missing data:** `skipped`.
- **Remediation:** select a fine-tuned model or a training framework, or change the answer to `prompt_only`.
- **Dependencies:** #30–#33.
- **Examples:**
  - Pass: a `fine_tuned_model` is selected.
  - Fail: neither is selected.
  - Skipped: the answer is `unknown`.

### W-R6 Components resident together fit each memory pool

- **Roles and pointers:**
  - device selections linked to components (companion note, through `build.links`);
  - `/workload/hardware/devices[].memory_pool_id` and `reserved_memory_gb`;
  - eligible measurements or memory estimates (EV-1 in the companion note).
- **Applies when:** any component has a concrete device placement, whatever `hardware.mode` is. Devices acquired or rented for the build are included.
- **Assertion:** for each memory pool, the peak memory of all components that can be resident at the same time, plus that pool's `reserved_memory_gb`, is at most the pool's capacity.
  - Peak memory comes from eligible measurements or estimates at the workload's maximum lengths and peak concurrency. Estimates must meet the build's `min_resource_confidence` (C5). If eligible evidence for a component disagrees about whether the pool fits, its peak is unresolved (EV-1).
  - Until CD-2 defines co-residency scenarios, components marked `on_demand` are counted as resident (a conservative maximum).
  - Devices sharing a `memory_pool_id`, such as unified memory, are summed together.
- **Missing data:** `unknown`. It never passes without eligible evidence for every resident component.
- **Remediation:** smaller artifacts, different placement, less context or concurrency, or more hardware.
- **Dependencies:** #10, #11; CD-2; extends `rule.vram.estimate.fit` and `rule.vram.per.device.fit` (C3).
- **Examples:**
  - Pass: a 24 GB GPU holding a 14 GB generator, a 6 GB embedder and 2 GB reserved.
  - Fail: an 18 GB generator and an 8 GB embedder on the same 24 GB GPU.
  - Fail: on a 24 GB unified-memory machine, 18 GB used by the CPU path and 8 GB by the GPU path. They share one pool.
  - Unknown: the embedder has no eligible measurement or estimate.
  - Skipped: no device placement yet.

### W-R7 Performance evidence matches the configuration and workload

- **Roles and pointers:** the `/workload` targets, lengths, concurrency and `interaction_pattern`; eligible measurements (EV-1 in the companion note); build `/policy/min_resource_confidence` (C5).
- **Applies when:** a latency or throughput target is set.
- **Assertion:** every eligible measurement meets the target. `pass` needs at least one eligible measurement, all meeting the target; `fail` means all of them miss it. A measurement counts only if it:
  - uses the configuration identity that suits the component's mode: the full self-hosted key, or the opaque-endpoint key for API and managed components;
  - was measured under the same workload distribution (input and output length distributions, concurrency, arrival process) and serving protocol;
  - uses the target's metric definition and percentile (per E2, E3);
  - meets the build's confidence policy.

  There is no generic "at least as demanding" comparison. For example, higher concurrency can increase aggregate throughput (E20).

  Memory estimates don't count here; latency and throughput need `service_level` measurements.

  **No transfers yet.** A measurement from another workload distribution isn't used. A transfer model validated by #10 and #36 could later produce a derived estimate, with its own identity (the source measurements and the model version). CD-3 decides how such an estimate is assessed. Until then the outcome is `unknown`.
- **Missing data:** `unknown`. This includes eligible measurements that disagree about whether the target is met. A pass can't rest on one favourable result while another eligible one fails; selection and aggregation are left to CD-3 and #41's acceptance policy.
- **Remediation:** measure with the matching protocol, relax the target, or change the configuration.
- **Dependencies:** #10, #11, #36, #62; CD-3, CD-8.
- **Examples:**
  - Pass: a measured p95 TTFT of 600 ms against an 800 ms p95 target, on the same configuration and workload distribution.
  - Fail: measured 1,200 ms.
  - Unknown: the evidence used a different arrival process, reports p50, or is kernel-throughput output such as `llama-bench`.
  - Unknown: two eligible measurements on the same key and protocol, at 600 ms and 1,200 ms against an 800 ms target.
  - Unknown: the only evidence comes from a different length distribution.
  - Skipped: no target.

### W-R8 Air-gapped builds have no external connections

- **Roles and pointers:** `/workload/network`; every component's `external_connections` and artifact readiness (companion note; boundary model in CD-4).
- **Applies when:** `network` is `air_gapped`. An unresolved `network` gives `unknown` once CD-1 is in place.
- **Assertion:** for every component, both of the following hold:
  - no connection that is enabled at runtime leaves the isolation boundary;
  - every runtime artifact is present inside the boundary.

  Deployment mode is not used: a provider-run installation inside the boundary can pass, and a self-operated server reached over the internet fails.
- **Missing data:** `unknown`. An absent connection inventory is unresolved, not an empty list.
- **Remediation:** disable or replace external connections; pre-stage artifacts.
- **Dependencies:** #9, #37; CD-4.
- **Examples:**
  - Pass: every component is local, and optional telemetry is recorded as disabled.
  - Fail: a runner with a cloud feature enabled.
  - Unknown: the vector database has no connection inventory.
  - Skipped: `network` is `online`.

### W-R9 Precision preference respected

- **Roles and pointers:** build `/workload/precision_preference`; the selected artifact's `/quantization/stored_bits_per_weight` (a companion-note field).
- **Applies when:** a preference is set and a quantized artifact is selected.
- **Assertion:** stored bits per weight ≥ `min_stored_bits_per_weight`.
- **Missing data:** `unknown`. v1 records no bit-width (C2).
- **Remediation:** choose an artifact with more stored bits per weight, or relax the preference.
- **Dependencies:** #11.
- **Examples:**
  - Pass: an 8-bit artifact against a 4-bit minimum.
  - Fail: Bonsai PTQ1_0, stored at 1.75 bits (E17).
  - Unknown: a GGUF artifact recorded without bits.
  - Skipped: no preference.

### W-R10 Quality target backed by comparable evidence

- **Roles and pointers:** `/workload/quality_target`; evaluation results. v1's measured-results schema records the evaluation suite selection, evaluator version, dataset revision and sample size (C11).
- **Applies when:** a quality target is set and an artifact is selected.
- **Assertion:** there is a result for the selected artifact (and engine build, where it matters) that:
  - was produced under the target's `protocol_id`, meaning the same suite, evaluator version, dataset revision and prompt protocol as `reference_result_id`;
  - has an adequate sample size;
  - shows degradation within `max_degradation`, in the metric's direction and units, under #36's uncertainty and acceptance policy.

  Bit-width is never used as a proxy.
- **Missing data:** `unknown`, including when the results come from different protocols, or when eligible results under the same protocol disagree about whether the target is met.
- **Remediation:** evaluate the selected artifact under the target's protocol, choose another artifact, or relax the target.
- **Dependencies:** #36; CD-3.
- **Examples:**
  - Pass: a 0.4-point drop against a 1-point allowance, under the same protocol.
  - Fail: a 3-point drop under the same protocol.
  - Unknown: only vendor claims exist, or the dataset revisions differ.
  - Skipped: no target.

## Open contract decisions

These are recorded as decisions for #40 and #41 rather than solved here. The full list is in the companion note; the ones this note depends on are:

| ID | Decision | Accountable |
| --- | --- | --- |
| CD-1 | A typed answer-state representation, and how the evaluator normalises it (including nested fields and the "not relevant / not yet known / not selected" distinction) | #40 |
| CD-2 | Physical memory pools, device instances, and co-residency scenarios | #40, with #10 |
| CD-3 | Benchmark protocol identity, the canonical configuration key, result schemas for kernel throughput vs service-level latency, derived estimates from transfer models, and how conflicting eligible results are selected or aggregated | #41, with #10, #62 |
| CD-4 | The isolation-boundary model, connection lifecycle, and artifact readiness | #40 |
| CD-5 | Per-stage load and length records for pipelines | #40, with #10 |
| CD-6 | Reconciling the hardware inventory with device selections; the effective capabilities of fine-tuned stages and adapter/base compositions (W-R1) | #40, with #6, #33 |
| CD-7 | The migration strategy: what is additive vs replacement, adapters, deprecation, and the version | #40 |
| CD-8 | The acceptance policy that lets community evidence decide verdicts (W-R6, W-R7, W-R10) | #41 |
| CD-9 | The jurisdiction hierarchy, containment rules, and named groups | #41 |

## Pricing and capacity

This note sets no prices. Budgets combine one-off hardware caps with operating caps; aggregation belongs to #39.

## Recommendation and rationale

1. **Make the workload a profile owned by the build, not a catalog item.** Catalog items need provenance with a public URL (C1, C6), and a user's answers have none. Keep catalog `workload` items only as presets.
2. **Adopt the output-based axes,** the field dictionary, and per-capability knowledge implementations.
3. **Store the workload inputs once.** v1 repeats them three times with different names (C1, C2, C5).
4. **Adopt the answer-state policy,** and implement it through CD-1 rather than by assuming the current evaluator supports it.
5. **Keep one primary workload per build** (`cardinality: "one"`, C8). Several workloads sharing a machine are left open (Q7).
6. **Adopt W-R1 to W-R10 after #40 review,** together with CD-1 to CD-9.

## Structured artifacts

None. A workload is not a catalog fact (Recommendation 1).

## Open questions and handoffs

Each question has one accountable issue (its assignee is the owner); others are consulted.

| # | Question | Accountable | Consulted |
| --- | --- | --- | --- |
| Q1 | Define the `data_classification` levels | #40 | #35 |
| Q2 | When can long context replace retrieval, given the KV cache cost? | #16 | #7 |
| Q3 | How should embedding-only builds be represented, and which `model` fields become optional? | #40 | #14 |
| Q4 | Calibrate the load presets and per-tokenizer conversions | #10 | #39 |
| Q5 | What latency defaults should the builder use? | #36 | #10, #11 |
| Q6 | Which protocols and metrics can a `quality_target` use? | #36 | #11 |
| Q7 | How should several workloads sharing one machine be represented? | #42 | #10 |

Handoffs to confirm (none confirmed yet): #3, #6, #7, #10, #11, #13, #16, #33, #35, #36, #39, #40, #41, #42, #62.

## Acceptance criteria coverage

| Criterion (issue #2) | Where | Status |
| --- | --- | --- |
| Taxonomy with definitions and boundary examples | [Taxonomy](#taxonomy-proposal) | Reviewer: met |
| Mapping table | [Mapping](#mapping-inputs-to-downstream-decisions) | Reviewer: met at proposal level |
| Types, units, ranges, `unknown` handling | [Field dictionary](#field-dictionary), [Unknown and missing answers](#unknown-and-missing-answers-proposal), CD-1 | Revised: output tokens follow the serving operation; means are decimals; representation open as CD-1 |
| Activation rules for T3/T4/T5 | [Activation rules](#activation-rules-for-t3-t4-and-t5-proposal) | Revised: per capability |
| Deployment-mode coverage | [Candidate options](#candidate-options), W-R7 | Revised: mode-appropriate evidence identity |
| Comparison fields | [Field dictionary](#field-dictionary), W-R7 | Revised: evidence checked by type (EV-1); conflicting results are `unknown`; remaining items recorded as CDs |
| Rules in the shared format; hypotheses separated | [Compatibility proposals](#compatibility-proposals) | Revised: common template fields; fine-tuned stages in W-R1 |
| Primary sources with access dates | [Evidence](#evidence) | Revised: contract cited as adopted; E23 re-checked |
| Handoffs confirmed | [Open questions](#open-questions-and-handoffs) | Open |
| Open questions with owners | [Open questions](#open-questions-and-handoffs) | Reviewer: met |
| Decision record merged | — | Open |

## Evidence

All sources were accessed on 2026-10-16. Relative "updated" labels are not used as versions. No prices are recorded.

**Contract (v1, adopted in PR #44).** Links are pinned to the inspected revision `a222013c1f0106159132564d05e5d24666ad6342`. Its file tree is identical to the merge commit `9769fcd9ea380b1211669b2753181c7782444178`. C- entries are Primary documentation.

| ID | Source | Location |
| --- | --- | --- |
| C1 | [`contracts/v1/schemas/catalog-item.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/catalog-item.schema.json) | `$defs/spec_workload`, `spec_model` (`model_type`, `modalities_*`, `supports_json_schema`), `spec_fine_tuned_model` (`base_model_ref`, `adapter_only`), `spec_accelerator`; `properties/provenance` (`minItems: 1`) |
| C2 | [`contracts/v1/schemas/selection.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/selection.schema.json) | `settings_workload`, `settings_model`, `settings_inference_engine`, `settings_hosting_platform`, `settings_context_policy` |
| C3 | [`contracts/v1/baseline/core-ruleset.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/baseline/core-ruleset.json) | 45 rules, 17 gated on `mode == "self_hosted"`; rules cited in the text |
| C4 | [`contracts/v1/docs/DEPENDENCIES.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/docs/DEPENDENCIES.md) | Line 13 (activation); line 60 (three-valued evaluation) |
| C5 | [`contracts/v1/schemas/build.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/build.schema.json) | `objectives`, `policy`, `links` |
| C6 | [`docs/RESEARCH_WORKFLOW.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/docs/RESEARCH_WORKFLOW.md) | Line 26 (public source URL per provenance entry) |
| C7 | [`contracts/v1/reference/evaluate.py`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/reference/evaluate.py), [`cost-estimate.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/cost-estimate.schema.json), [`resource-estimate.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/resource-estimate.schema.json) | Context tokens summed (lines 83–88); `UNKNOWN` sentinel (line 14) versus ordinary strings, confirmed by an expression probe; workload fields not read (text search) |
| C8 | [`contracts/v1/schemas/component-registry.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/component-registry.json) | `kinds/workload` |
| C9 | [`templates/rule-proposal.md`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/templates/rule-proposal.md) | Rule proposal fields |
| C10 | [`contracts/v1/schemas/ruleset.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/ruleset.schema.json) | One `severity` per rule; `on_unknown` enum (`block` / `review` / `defer`) |
| C11 | [`contracts/v1/schemas/quality-evaluation-run.schema.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/a222013c1f0106159132564d05e5d24666ad6342/contracts/v1/schemas/quality-evaluation-run.schema.json) | Required `evaluation_suite_selection_id`, `evaluator_version`, `dataset_revision`, `sample_size` |

**External sources.**

| ID | Publisher, title and URL | Version / date shown | Evidence grade | Limitations |
| --- | --- | --- | --- | --- |
| E1 | MLCommons, "MLPerf Inference Rules", §3: <https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc#3-scenarios> | Master branch; refers to MLPerf 6.1 submissions | Primary documentation | Benchmark rules; commit not pinned |
| E2 | Same document, LLM latency constraints | As E1 | Primary documentation | Benchmark-specific |
| E3 | NVIDIA, "Metrics", NIM Benchmarking: <https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html> | "LLM 2.0.0 (Latest)" | Primary documentation | NVIDIA's definitions |
| E4 | Kwon et al., PagedAttention, SOSP 2023, §3: <https://arxiv.org/abs/2309.06180> | arXiv v1 | Primary documentation (worked calculation) | OPT-13B, FP16 |
| E5 | Same paper, §1 and Fig. 2 | As E4 | Vendor claim (author-reported result about competing systems) | Not reproduced here |
| E6 | OpenAI Help Center, "Understanding and counting tokens": <https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens> | Accessed 2026-10-16 | Primary documentation (approximation) | English only |
| E7 | Google DeepMind, Gemma 4: <https://huggingface.co/google/gemma-4-26B-A4B-it>; QAT Q4_0 GGUF: <https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf> | Created 2026-03-11 and 2026-06-05 | Primary documentation; Vendor claim (QAT quality) | Licence metadata: apache-2.0 |
| E8 | Qwen, Qwen3.8-27B: <https://huggingface.co/Qwen/Qwen3.8-27B>; FP8: <https://huggingface.co/Qwen/Qwen3.8-27B-FP8> | Created 2026-08-05 and 2026-08-13 | Primary documentation; Vendor claim (FP8 quality) | — |
| E9 | Mistral AI, Voxtral Mini 4B Realtime 2602: <https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602> | Created 2026-01-21 | Primary documentation | — |
| E10 | Qwen, Qwen3-TTS-12Hz-1.7B-CustomVoice: <https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice> | Created 2026-01-21 | Primary documentation | — |
| E11 | NVIDIA, Nemotron-3.5-Super-VL-120B-A12B-NVFP4: <https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-NVFP4> | Created 2026-10-12 | Primary documentation; Vendor claim (benchmarks) | Licence metadata: other |
| E12 | vLLM project, "Quantization": <https://docs.vllm.ai/en/latest/features/quantization/> | "Last update: September 14, 2026" | Primary documentation | vLLM only |
| E13 | vLLM releases: <https://github.com/vllm-project/vllm/releases>; llama.cpp build tags read with git from <https://github.com/ggml-org/llama.cpp> | Tag inventory checked 2026-10-16: `b11676`–`b11696`, with `b11686`, `b11689`, `b11692` and `b11694` absent; commit times in UTC | Primary documentation (release and repository metadata) | Commit timestamps, not release-publication timestamps; frequency is not scope of change |
| E14 | ml-explore (Apple), MLX README: <https://github.com/ml-explore/mlx/blob/b6642e604843776705b57b1eaecb6f57e519b793/README.md> | Commit `b6642e6` | Primary documentation | — |
| E15 | IBM, Granite 4.2 MLX: <https://huggingface.co/ibm-granite/granite-4.2-30b-q4-mlx> | Created 2026-09-01 | Primary documentation (variants) | Memory guidance not relied on |
| E16 | Qwen, Qwen3.8-Flash-Next: <https://huggingface.co/Qwen/Qwen3.8-Flash-Next> | Created 2026-08-24 | Primary documentation; Vendor claim (offloading) | Licence metadata: other |
| E17 | Prism ML, Ternary-Bonsai-2-27B-gguf: <https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf> | Created 2026-09-16; last modified 2026-09-25 | Primary documentation; Vendor claim (quality, speed; not relied on) | Third-party derivative |
| E18 | DeepSeek, DeepSeek-V4.1-Flash: <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash> | Created 2026-09-10 | Primary documentation | Licence metadata: mit |
| E19 | Arm Learning Paths, "Explore llama.cpp architecture and the inference workflow": <https://learn.arm.com/learning-paths/servers-and-cloud-computing/llama_cpp_streamline/2_llama.cpp_intro/>; parent learning path: <https://learn.arm.com/learning-paths/servers-and-cloud-computing/llama_cpp_streamline/> | Parent page "Last updated: 17 Sep 2026" | Vendor claim | Says "memory-bound" |
| E20 | NVIDIA Technical Blog, "Mastering LLM Techniques: Inference Optimization": <https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/> | Published 17 Nov 2023; modified 27 Dec 2025 | Vendor claim | GPU-focused; also explains batching effects |
| E21 | Kim et al., "SqueezeLLM" (ICML 2024): <https://arxiv.org/abs/2306.07629> | arXiv v4, 5 Jun 2024 | Independent measurement (author-reported) | GPU; single-batch scope |
| E22 | NIST, FIPS PUB 199: <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.199.pdf> | February 2004 | Primary documentation | Contrast only |
| E23 | EUR-Lex, GDPR Art. 4(1), 9(1): <https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679> | OJ L 119/1, 4.5.2016 | Primary documentation (legal text) | Text of Art. 4(1) and 9(1) checked at the cited URL on 2026-10-16. Not legal advice. |
| E24 | ISO, "ISO 4217 Currency codes": <https://www.iso.org/iso-4217-currency-codes.html>; standard record: <https://www.iso.org/standard/64758.html> | ISO 4217:2015; the record shows the 2021 review | Primary documentation | — |
| E25 | ISO, "ISO 3166 Country Codes": <https://www.iso.org/iso-3166-country-codes.html> | As shown at access | Primary documentation | Containment semantics are a project decision (CD-9) |
