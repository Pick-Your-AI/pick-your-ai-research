# Monitoring: signals to watch for an active build

Issue: #38 · Contract: 1.0.0 · Kinds: `monitoring_stack`
Status: draft for review · Last researched: 2026-10-17 · Research owners: @appletechie, @PUSHINGSQUARES (live GitHub assignees)

## User decision

Which signals must be watched once the build runs? The builder needs to show, for each **active** component, which health, latency, usage, cost, quality, safety and freshness signals apply, where each one comes from, and what may be logged about users. Thresholds are workload-specific. This note says where each threshold must come from. It sets no numbers.

Out of scope (per #38): operating a monitoring stack. Nothing here was deployed, scraped or measured. Every metric name below is taken from release-pinned publisher documentation or source, and has the status **source checked** (the #41 interim definition, from the [PR #75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927)). Nothing is independently verified.

### Deployment modes covered

Mode is decided per serving component, following the #3 owner position used in T2 [hosting.md](../T2-infrastructure/hosting.md). Monitoring does not set the mode itself.

| Mode | What the builder can observe | Not observable / skipped |
| --- | --- | --- |
| `api` (provider-operated shared capacity) | Client-side spans/metrics (OTel GenAI [M5–M7]), the provider's response `usage` body and rate-limit headers [M10–M13] | Engine queue, KV cache and GPU signals. They are `skipped` because the provider runs the runtime |
| `managed` (provider-operated dedicated) | The client-side signals, plus whatever engine/host metrics the offering exposes | Exposure varies by offering and was not researched for any managed product. It stays `unknown` per offering (handoff to #37/#9) |
| `self_hosted` | Everything: engine `/metrics` [M1–M3], GPU via DCGM [M4], host via node_exporter [M15], plus the client-side signals | — |
| `hybrid` | Each serving component is evaluated under its own mode | — |

## Candidate options

Candidate stacks are compared as **collection components**. They are not a single product recommendation.

| Candidate | Role | Version checked (2026-10-17) | Licence (source checked) | Content capture default | Evidence |
| --- | --- | --- | --- | --- | --- |
| Prometheus | Metrics scrape/storage; exposition format | v3.15.0 | Apache-2.0 | n/a (metrics only) | M14, M16 |
| NVIDIA DCGM Exporter | GPU telemetry → Prometheus | 4.8.4 | Apache-2.0 | n/a | M4 |
| Prometheus node_exporter | Host CPU/memory/filesystem/network | v1.12.1 | Apache-2.0 | n/a | M15 |
| OpenTelemetry GenAI semantic conventions | Vendor-neutral span/metric names (OTLP) | `open-telemetry/semantic-conventions-genai` at `f3c6d0c9` (no release tag exists). Status **Development** | Apache-2.0 | Content is **Opt-In**, and instrumentations "SHOULD NOT capture them by default" | M5–M7 |
| OpenLLMetry (Traceloop) | OTel instrumentations + SDK | 0.62.4 | Apache-2.0 | **On by default**: "logs prompts, completions, and embeddings to span attributes". Disabled with `TRACELOOP_TRACE_CONTENT=false` | M8, M17 |
| Langfuse | LLM trace store/UI | v4.63.0 | Open core: MIT outside `ee/` directories, commercial Enterprise License inside them | Client-side masking hooks (`mask_otel_spans`) are available. Whether masking is on by default was not established | M9, M18 |
| Arize Phoenix | LLM trace store/UI | arize-phoenix-v20.23.0 | Elastic License 2.0. Not OSI open source, and the licence forbids providing it to third parties "as a hosted or managed service" | Not established | M19 |
| TGI built-in metrics | Engine metrics | v3.3.7. Repository `archived=true`, README declares maintenance mode (T2 E20/E26) | Apache-2.0 | n/a | M2 |

Grafana and MLflow, both named in the unmerged PR #74 prompt, were not researched. They remain open candidates.

## Signal catalog per component

Column legend: **Type**: M = metric, T = trace/span, L = log/header. **Signal enum** is the closest existing `spec_monitoring_stack.signals` value; `—` means v1 has no matching enum. Threshold sources are mapped in [Thresholds](#thresholds-deferred).

### Model API (provider route, any mode with a remote provider)

| Signal ID | Metric / field | Unit | Source / exporter | Collection | Type | Signal enum | Privacy notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `api.latency` | `gen_ai.client.inference.duration` (also listed in this commit: `gen_ai.client.operation.duration`) | s, histogram | OTel GenAI client instrumentation [M5, M6] | Per request, OTLP | M | `latency` | No content needed |
| `api.ttft` | `gen_ai.client.inference.time_to_first_chunk` | s, histogram | OTel [M6] | Per streamed request | M | `latency` | — |
| `api.tokens` | `gen_ai.client.inference.usage.input_tokens`, `.output_tokens`, `.cache_read.input_tokens`, `.cache_write.input_tokens`, `.reasoning.output_tokens` | `{token}`, counter | OTel [M7], fed from the provider `usage` body. OpenAI: `input_tokens`, `output_tokens`, `input_tokens_details.cached_tokens`, `output_tokens_details.reasoning_tokens` [M12]. Anthropic: `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` [M13] | Per response | M | `token_usage` | Counts only |
| `api.ratelimit_headroom` | OpenAI `x-ratelimit-{limit,remaining,reset}-{requests,tokens}` (+ `-project-tokens` when applicable), `Retry-After` [M10]. Anthropic `anthropic-ratelimit-{requests,tokens,input-tokens,output-tokens}-{limit,remaining,reset}`, `retry-after` [M11] | requests, tokens. Reset is a duration string for OpenAI (e.g. `6m0s`) and an RFC 3339 time for Anthropic | Response headers | Per response | L→M | — | Anthropic rounds `tokens-remaining` to the nearest thousand [M11]. Anthropic's spend-cap 429 never carries `retry-after` [M11] |
| `api.errors` | HTTP status (429/5xx), OTel `error.type` | count | Client [M6] | Per request | M/T | `errors` | — |
| `api.provider_retention` | Provider-side retention/abuse-monitoring terms | duration + exceptions | T1 O2 (OpenAI), A4 (Anthropic) | Per account/route review | Policy | `security` | OpenAI abuse monitoring can retain up to 30 days. Anthropic ZDR is feature- and model-specific (T1 evidence). This is outside the builder's own logs, but it is part of the logged-data footprint |

### Inference engine (self-hosted or managed with exposed runtime)

All names come from the T2 #11 release set. Labels must carry engine version/build/config (T2 handoff #11→#38).

| Signal ID | vLLM v0.31.0 [M1] | TGI v3.3.7 [M2] | llama.cpp v0.7.0 [M3] | Unit | Signal enum |
| --- | --- | --- | --- | --- | --- |
| `engine.ttft` | `vllm:time_to_first_token_seconds` | No TTFT metric in the documented table: **unknown** | No TTFT metric documented: **unknown** | s, histogram | `latency` |
| `engine.itl` | `vllm:inter_token_latency_seconds`, `vllm:request_time_per_output_token_seconds` | `tgi_request_mean_time_per_token_duration` | `llamacpp:predicted_tokens_seconds` (average tokens/s gauge, not a per-request distribution) | s (tokens/s for llama.cpp) | `latency` |
| `engine.e2e` | `vllm:e2e_request_latency_seconds` | `tgi_request_duration` | not documented: **unknown** | s, histogram | `latency` |
| `engine.queue_depth` | `vllm:num_requests_waiting` (+ `_by_reason`) | `tgi_queue_size` | `llamacpp:requests_deferred` | requests, gauge | — |
| `engine.queue_time` | `vllm:request_queue_time_seconds` | `tgi_request_queue_duration` | not documented | s, histogram | `latency` |
| `engine.running` | `vllm:num_requests_running` | `tgi_batch_current_size` | `llamacpp:requests_processing`, `llamacpp:n_busy_slots_per_decode` | requests | — |
| `engine.kv_cache` | `vllm:kv_cache_usage_perc` ("1 means 100 percent") | not documented: **unknown** | `llamacpp:n_tokens_max` (context high watermark, a counter. It is not KV utilisation) | fraction 0–1 | — |
| `engine.preemption` | `vllm:num_preemptions` | n/a | n/a | count | `errors` |
| `engine.tokens` | `vllm:prompt_tokens`, `vllm:generation_tokens` (counters) | `tgi_request_input_length`, `tgi_request_generated_tokens` (histograms) | `llamacpp:prompt_tokens_total`, `llamacpp:tokens_predicted_total` | tokens | `token_usage` |
| `engine.success` | `vllm:request_success` (label `finished_reason`) | `tgi_request_success`, `tgi_request_count` | not documented | count | `errors` |
| Exposure | `/metrics` on the OpenAI-compatible API server | `/metrics` Prometheus endpoint | `/metrics` only with `--metrics`. `/slots` is **on by default** | — | — |

The exposed sample names of Prometheus counters (for example a `_total` suffix on `vllm:prompt_tokens`) must be confirmed against a live scrape. Only the registered names were checked. vLLM's server metrics also match the OTel server conventions conceptually (`gen_ai.server.time_to_first_token`, `gen_ai.server.time_per_output_token`, `gen_ai.server.request.duration` [M5]), but no mapping between the two is published.

Separate startup/load from steady-state signals (T2 #11 handoff). No load-failure metric exists in any of the three tables, so those signals are log-derived and **unknown** as metrics.

### GPU and host (self-hosted only)

| Signal ID | Metric | Unit | Source | Signal enum |
| --- | --- | --- | --- | --- |
| `gpu.util` | `DCGM_FI_DEV_GPU_UTIL`; profiling `DCGM_FI_PROF_GR_ENGINE_ACTIVE`, `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` | %; ratio | DCGM Exporter default counters [M4] | `gpu_utilization` |
| `gpu.memory` | `DCGM_FI_DEV_FB_USED`, `DCGM_FI_DEV_FB_FREE`, `DCGM_FI_DEV_FB_RESERVED` | MiB | [M4] | `gpu_utilization` |
| `gpu.errors` | `DCGM_FI_DEV_XID_ERRORS` (last XID value), `DCGM_FI_DEV_ROW_REMAP_FAILURE`, `DCGM_FI_DEV_UNCORRECTABLE_REMAPPED_ROWS`, `DCGM_FI_DEV_PCIE_REPLAY_COUNTER` | code; count | [M4] | `errors` |
| `gpu.thermal_power` | `DCGM_FI_DEV_GPU_TEMP`, `DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION` | °C; W; mJ since driver reload | [M4] | — (energy may feed #39) |
| `host.*` | node_exporter `cpu`, `meminfo`, `filesystem`, `diskstats`, `netdev` collectors (port 9100 default) | per collector | [M15] | — |

DCGM covers NVIDIA only. Monitoring for AMD (the MI300X in T2) and Apple accelerators was not researched and stays **unknown**. Device memory used by the engine is distinct from KV utilisation (T2 gpu-compute.md).

### RAG retrieval (only when `rag_pipeline` / `vector_database` is selected)

| Signal ID | Source | Notes |
| --- | --- | --- |
| `rag.retrieval_span` | OTel `retrieval` operation span [M6] | `gen_ai.retrieval.documents` (ids + scores) and `gen_ai.retrieval.query.text` are **Opt-In** [M6]. Log document IDs/scores, not text |
| `rag.embedding_span` | OTel embeddings span [M6] | Token counts only |
| `rag.index_freshness`, `rag.ingestion_failures`, `rag.retrieval_quality` | **No primary convention found** | Owned by #16/#13. Quality maps to the `quality` enum and is measured by #36 |

### Agents and tools (only when `agent_framework` / `tool` / `mcp_server` is selected)

| Signal ID | Metric / span | Unit | Source |
| --- | --- | --- | --- |
| `agent.duration` | `gen_ai.invoke_agent.duration`, `gen_ai.invoke_workflow.duration` | s | [M5] |
| `agent.inference_calls` | `gen_ai.invoke_agent.inference_calls` | `{inference_call}` | [M5] |
| `agent.tool_calls` | `gen_ai.invoke_agent.tool_calls` | `{tool_call}` | [M5] |
| `tool.duration` | `gen_ai.execute_tool.duration`; `execute_tool` span | s | [M5, M6] |
| `memory.ops` | `create_memory` / `search_memory` / `update_memory` / `delete_memory` spans | — | [M6]. `gen_ai.memory.records` and `gen_ai.memory.query.text` are Opt-In |

Retries, human-approval events and task success have no convention in the checked docs. They are owned by #25/#28 and stay **unknown**. `gen_ai.tool.definitions` "may contain sensitive information" [M6].

### Guardrails (only when `guardrail` is selected)

The checked OTel GenAI docs contain no guardrail convention. Guardrail trigger, block and failure counts map to the `security` enum, but their names, units and sources depend on #35's product choice and remain **unknown**.

### Cost

No primary source defines a cost metric. Cost is **derived**: token counters (`api.tokens`, `engine.tokens`) × the dated #39 Pricebook rate, plus GPU/host time × the compute rate. It maps to the `cost` enum. Provider usage/cost admin APIs were not researched, so they stay **unknown**. Budget burn uses `objectives.monthly_budget_amount` (v1) or #81 `budgets` (proposed).

### Fine-tuned model drift (only when `fine_tuned_model` is selected)

T5 [fine-tuned-model.md](../T5-training-fine-tuning/fine-tuned-model.md) records that fine-tuning can cause safety regression against the base model (Q1 there). Monitoring cannot measure that from runtime metrics. `drift`/`quality` signals need a scheduled #36 evaluation run against the base, with its result referenced from monitoring. The suite and threshold are owned by #36.

## Privacy requirements for logs

Status: proposals from primary sources. They are not legal advice. Legal-basis decisions need the build owner's review.

1. **No content by default.** Prompts, responses, system instructions, tool definitions/arguments, retrieved text and memory records are not logged by default. This matches OTel: "SHOULD NOT capture them by default", with content attributes Opt-In [M6]. The engine signals above need no content (T2 #11 handoff). OpenLLMetry's default is the opposite [M17], so a build using it must set `TRACELOOP_TRACE_CONTENT=false` unless content capture was approved.
2. **Engine log levels.** vLLM `--enable-log-requests` logs request ID/params at INFO and **prompt inputs at DEBUG** [M1-args]. It is off by default. llama.cpp `/slots` is on by default and returns per-slot state including sampling parameters [M3]. Disable it (`--no-slots`) or protect it where slots may reveal request data. vLLM's `--api-key` does not protect every endpoint (T2 E06), so `/metrics` exposure needs network controls.
3. **When content is approved**, prefer OTel's production pattern: store content externally and record references on spans [M6]. Apply masking before export (for example Langfuse `mask_otel_spans` [M18]).
4. **No identifiers in labels.** Prometheus: "Do not use labels to store … user IDs, email addresses" [M16]. Use pseudonymous trace IDs.
5. **Minimisation and retention.** Personal data must be "adequate, relevant and limited to what is necessary" and kept "for no longer than is necessary" (GDPR Art. 5(1)(c), 5(1)(e); Recital 39 asks for time limits for erasure or review) [M20]. Disclose the storage period or the criteria for it (Art. 13(2)(a)). Every monitoring selection that stores user-linked data must set `retention_days`. Data protection by design/default (Art. 25) and security of processing (Art. 32) apply [M20].
6. **Consent is one lawful basis among six** (Art. 6(1)) [M20]. Whether consent, contract or legitimate interests applies is a per-deployment legal decision, so it stays a recorded owner decision. Do not hard-code it.
7. **Provider-side retention is separate.** Abuse-monitoring and application-state retention at the provider (T1 O2/A4) happen even when the builder logs nothing. Show both footprints.

## Comparison fields

| Field / JSON pointer | Type and unit | Finding | Evidence | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `signal` (note-only ID, e.g. `engine.ttft`) | string | Catalog above | M1–M7 | v1 has no per-signal field |
| `component` | canonical kind from the registry | Mapped per table | registry | — |
| `metric_name` | string, release-pinned | Above | M1–M7 | Must carry source version |
| `unit` | UCUM/base unit (s, bytes, `{token}`) | Prometheus recommends base units [M16]; OTel uses UCUM [M5] | M5, M16 | llama.cpp tokens/s gauge and DCGM MiB are not base units |
| `type` | enum metric / trace / log | Above | — | — |
| `collection_method` | enum scrape / OTLP push / header / derived | Above | M1–M4, M10–M11 | — |
| `threshold_source` | JSON pointer to an objective or "none" | [Thresholds](#thresholds-deferred) | #2, #81 | No numeric defaults |
| `privacy_notes` | content class: none / counts / identifiers / content | Above | M6, M16, M20 | — |
| `/spec/signals` | enum array, ≥1 | Maps 9 enums. Missing: queue/saturation, KV cache, rate-limit headroom, availability, freshness | catalog schema | Contract gap → #40 |
| `/spec/pii_redaction` | boolean | Cannot distinguish "content never captured" from "captured with masking" | catalog schema | Contract gap → #40 |
| `/spec/retention_days`, selection `/settings/retention_days` | integer days ≥0 | Must be set when user-linked data is stored | M20 | Product default retention not researched |
| `/spec/exporter` | `otlp` / `prometheus` / `vendor_api` / `none` | A single value; real stacks combine Prometheus + OTLP | catalog schema | Contract gap → #40 |
| selection `/settings/sample_rate` | number 0–1 | Trace sampling | selection schema | Applies to traces, not counters |

## Mapping to the v1 contract

- **`spec_monitoring_stack`**: only `signals` is required. Proposal (to #40): the builder derives the required set of signal enums from the active kinds (tables above). The selected stack's `signals` must cover that set (MON-01).
- **Baseline rules preserved**: `rule.restricted.monitoring.redaction` (error, `on_unknown: block`) and `rule.production.gates` (error, `on_unknown: block`) require redaction for restricted data and evaluation/monitoring/guardrail selections for production, respectively. Production alone does not require `pii_redaction=true`. This note adds proposals without changing either rule.
- **Dependency graph**: v1 has `dep.monitoring_stack.{deployment_target,model,compute_profile}`. The signal set also changes with `inference_engine`, `rag_pipeline`, `agent_framework`, `tool`, `mcp_server`, `guardrail` and `fine_tuned_model`. Proposed edges go to #40.
- **`event.schema.json`**: this schema defines **build-lifecycle integration events** (`build.selection.upserted`, `build.deployed`, …), which are secret-free and idempotent. It is not runtime telemetry, and v1 has no runtime telemetry schema. Use: a `build.selection.upserted` or `build.deployed` event whose `payload.affected_kinds` intersects the kinds above should trigger re-evaluation of MON-01. `payload.note` is free text and must never carry prompt/response content. A runtime alert/telemetry record would be a new contract proposal for #40, and none is drafted here.

## Compatibility proposals

These are proposals for #40 in the [rule-proposal](../../templates/rule-proposal.md) format. All are hypotheses. None is executable or verified. Outcome (`pass/fail/unknown/skipped`) is kept separate from severity (`info/warning/error`). Examples are synthetic.

### MON-01: required signal coverage per active component

- Kinds/pointers: `monitoring_stack` primary `/spec/signals`; enabled selections of `model`, `inference_engine`, `compute_profile`, `rag_pipeline`, `agent_framework`, `tool`, `mcp_server`, `guardrail`, `fine_tuned_model`.
- Applicability: a monitoring stack is selected and at least one listed kind is enabled. Kinds not enabled are `skipped`. Engine/GPU signals are `skipped` for a serving component in `api` mode.
- Assertion: `/spec/signals` ⊇ the derived set (model → `latency`,`errors`,`token_usage`,`cost`; selected compute with a GPU → adds `gpu_utilization`; CPU-only compute skips GPU coverage; agents/tools/RAG → adds `traces`; guardrail → adds `security`; fine-tuned model → adds `drift`,`quality`).
- Severity: `warning`. Missing-data: absent `signals` or an unknown mode gives `unknown`, `on_unknown: review`. **Unknown never passes.**
- Remediation: add an exporter/instrumentation that covers the missing signal, or record an accepted gap.
- Pass: API model + stack signals `[latency, errors, token_usage, cost]`. Fail: self-hosted vLLM on a GPU + `[latency]` → missing `gpu_utilization`, `token_usage`, `errors`, `cost`. Unknown: engine mode not recorded. Skipped: no RAG selected → retrieval signals skipped.
- Version impact: needs the derived-set table to be versioned in a ruleset. The enum gaps (queue, KV, rate-limit) need a v1.x proposal.

### MON-02: content capture requires redaction and retention

- Kinds/pointers: `monitoring_stack` `/spec/pii_redaction`, `/spec/retention_days`, selection `/settings/retention_days`; build `/objectives/data_classification`.
- Applicability: `data_classification` ∈ {`confidential`, `restricted`} and the stack captures content. v1 has no content-capture field, so for now this cannot be determined, and the result is `unknown`.
- Assertion: `pii_redaction == true` AND `retention_days` is set (selection or spec).
- MON-02 has fixed severity `error` and applies only to `restricted` data with content capture. MON-02b is a separate candidate with fixed severity `warning`, applying only to `confidential` data with content capture and the same assertion. Both use `on_unknown: review`; unknown capture state gives `unknown`, and known no capture gives `skipped`.
- Pass: confidential, redaction true, retention set. Fail: restricted, redaction false. Unknown: content capture not recorded.
- Version impact: a proposed `content_capture` enum (`none`/`reference`/`masked`/`full`) goes to #40.

### MON-03: threshold provenance

- Assertion: every alert threshold references a build objective pointer (`/objectives/max_latency_ms`, `/objectives/monthly_budget_amount`, `/objectives/max_concurrency`, `spec_workload` `/latency_budget_ms`, `/uptime_target_pct`, or #81's `latency_targets`/`throughput_target`/`availability_target`/`budgets`) or a reviewed #36 result. No literal default constant is allowed.
- Severity: `warning`. A missing objective gives `unknown` with `on_unknown: defer`, and the alert is shown as "no threshold". It is not given an invented value.

### MON-04: engine signal gaps

- Applicability: selected `inference_engine` is TGI v3.3.7 or llama.cpp v0.7.0 and the workload sets a TTFT target.
- Assertion: the engine exposes a TTFT metric. Neither documents one [M2, M3], so client-side `gen_ai.client.inference.time_to_first_chunk` [M6] is required instead.
- Severity: fixed `warning`. Outcome is `pass` when client TTFT is configured, `fail` when known absent, and `unknown` with `missing_evidence` and `on_unknown: review` when configuration cannot be determined. The rule also carries the TGI maintenance-mode note (T2 E20).

### MON-05: provider rate-limit headroom

- Applicability: a serving component in `api` mode with an OpenAI or Anthropic route.
- Assertion: the stack records the remaining requests/tokens headers [M10, M11]. Numeric limits are account-specific (T1 A5), so headroom can be monitored but not pre-validated.
- Severity: `info`. Unknown when the header capture is not recorded.

## Thresholds (deferred)

No numeric threshold is set. Each alert's source is mapped below, and the decision is deferred to #2/#36 as questions for @PUSHINGSQUARES:

| Signal | Threshold source | Owner |
| --- | --- | --- |
| `api.ttft` / `engine.ttft`, `engine.itl`, `*.e2e` | #81 `latency_targets` (metric ttft/tpot/e2e + percentile), v1 `max_latency_ms` / `latency_budget_ms` | #2 @tynamite; #36 |
| `engine.queue_depth`, `engine.kv_cache`, `gpu.memory` | #10 admission/headroom (open in T2 gpu-compute.md) | #10 @Mattycodes69 |
| `api.ratelimit_headroom` | Account-specific provider limits (T1 A5, B3) | #5 |
| throughput | #81 `throughput_target` | #2 |
| availability / errors | v1 `uptime_target_pct`; #81 `availability_target` | #2 |
| cost burn | `monthly_budget_amount`; #81 `budgets`; #39 aggregation | #39 |
| `drift`, `quality` | #36 evaluation suite and baseline | #36 |

## Pricing and capacity

Not applicable. No prices were collected. Monitoring product pricing (Langfuse Cloud, Arize) is out of scope here and belongs in #39 Pricebooks. Collection overhead was not measured, so it stays **unknown**.

## Recommendation and rationale

This is a research recommendation, not an approved default. Use **OTel GenAI conventions over OTLP** for client/agent/RAG spans, **Prometheus** for engine/GPU/host metrics (vLLM `/metrics`, DCGM, node_exporter), and keep **content capture off by default**. Reasons: the conventions are vendor-neutral and default to no content [M6]. All three engines expose Prometheus metrics [M1–M3]. A trace store (Langfuse, Phoenix, or another) stays a user choice, because licences differ (MIT core + EE, versus ELv2 with a hosted-service restriction). Risk: the OTel GenAI conventions are in **Development** status and moved repositories without a release tag, so signal names may change. Pin the commit and re-check.

## Structured artifacts

None. No `monitoring_stack` CatalogItem is proposed. The candidates above are collection components, not stacks with a defined `signals` set. `pii_redaction` cannot be stated as a product fact, because masking is user-configured (M17, M18). Claiming `signals` for a single product would turn a configuration into a catalog fact. A stack-level item needs MON-01's derived set and the `content_capture` proposal first.

## Evidence

Access date 2026-10-17 for all M entries. Grade: **Primary documentation** (publisher docs/source at the named version). Status: source checked, not independently verified. No currency or region applies.

| ID | Publisher and URL | Version | Limitations |
| --- | --- | --- | --- |
| M1 | vLLM [metrics usage](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/metrics.md), [metric registration source](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py); M1-args [engine args](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/engine/arg_utils.py) | v0.31.0 | The doc table is generated, so names were read from source |
| M2 | Hugging Face [TGI metrics](https://github.com/huggingface/text-generation-inference/blob/v3.3.7/docs/source/reference/metrics.md) | v3.3.7; repository archived | Maintenance mode |
| M3 | ggml-org [llama.cpp server README](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/tools/server/README.md) (`/metrics`, `/slots`, `--metrics`) | v0.7.0 | Same doc as T2 E14 |
| M4 | NVIDIA [DCGM Exporter default counters](https://github.com/NVIDIA/dcgm-exporter/blob/4.8.4/etc/default-counters.csv), [README](https://github.com/NVIDIA/dcgm-exporter/blob/4.8.4/README.md) | 4.8.4 | NVIDIA only; DCGM version pairing required |
| M5 | OpenTelemetry [GenAI metrics](https://github.com/open-telemetry/semantic-conventions-genai/blob/f3c6d0c9bb66ebd474668a3a0be25c61226f02c2/docs/gen-ai/gen-ai-metrics.md); [moved notice in semantic-conventions v1.44.0](https://github.com/open-telemetry/semantic-conventions/blob/v1.44.0/docs/gen-ai/README.md) | commit `f3c6d0c9` (2026-10-14); status Development | No release tag |
| M6 | OpenTelemetry [GenAI spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/f3c6d0c9bb66ebd474668a3a0be25c61226f02c2/docs/gen-ai/gen-ai-spans.md), [client inference](https://github.com/open-telemetry/semantic-conventions-genai/blob/f3c6d0c9bb66ebd474668a3a0be25c61226f02c2/docs/gen-ai/client-inference.md) | same | Development |
| M7 | OpenTelemetry [GenAI token metrics](https://github.com/open-telemetry/semantic-conventions-genai/blob/f3c6d0c9bb66ebd474668a3a0be25c61226f02c2/docs/gen-ai/gen-ai-token-metrics.md) | same | Development |
| M8 | Traceloop [OpenLLMetry repository](https://github.com/traceloop/openllmetry) | 0.62.4; Apache-2.0 | — |
| M9 | Langfuse [LICENSE](https://github.com/langfuse/langfuse/blob/v4.63.0/LICENSE), [ee/LICENSE](https://github.com/langfuse/langfuse/blob/v4.63.0/ee/LICENSE) | v4.63.0 | Open core |
| M10 | OpenAI [rate limits](https://developers.openai.com/api/docs/guides/rate-limits) | current page | Header samples are illustrative |
| M11 | Anthropic [rate limits](https://platform.claude.com/docs/en/api/rate-limits) | current page | Tier-dependent |
| M12 | OpenAI [Responses create reference](https://developers.openai.com/api/reference/resources/responses/methods/create) | current page | Usage field names only |
| M13 | Anthropic [Messages API](https://platform.claude.com/docs/en/api/messages) | current page | Usage field names only |
| M14 | Prometheus [releases](https://github.com/prometheus/prometheus/releases/tag/v3.15.0) | v3.15.0; Apache-2.0 | — |
| M15 | Prometheus [node_exporter README](https://github.com/prometheus/node_exporter/blob/v1.12.1/README.md) | v1.12.1 | Collector list only; metric names not pinned |
| M16 | Prometheus [metric and label naming](https://prometheus.io/docs/practices/naming/) | current page | — |
| M17 | Traceloop [OpenLLMetry privacy: traces](https://www.traceloop.com/docs/openllmetry/privacy/traces) | current page | — |
| M18 | Langfuse [masking](https://langfuse.com/docs/observability/features/masking) | current page | Default state not established |
| M19 | Arize [Phoenix LICENSE](https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.23.0/LICENSE) | arize-phoenix-v20.23.0; ELv2 | — |
| M20 | EUR-Lex [Regulation (EU) 2016/679 (GDPR)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679) Recital 39, Arts. 5, 6, 13, 25, 32 | Original act, CELEX 32016R0679 | Not legal advice; UK GDPR/ICO guidance not checked |

T1 (O2, A4, A5, B3), T2 (E06, E14, E20, E26) and T5 (Q1) entries are reused with their own access dates (2026-10-16).

## Open questions and handoffs

| # | Question / handoff | Owner | Status |
| --- | --- | --- | --- |
| Q1 | Numeric latency/TTFT/availability thresholds from #2 targets | @PUSHINGSQUARES with #2 @tynamite | Open, deferred |
| Q2 | Quality/drift thresholds and evaluation cadence for fine-tuned models | @PUSHINGSQUARES (#36), @appletechie (#33) | Open, deferred |
| Q3 | Add enums (queue, KV cache, rate-limit, availability, freshness), a `content_capture` field, multi-exporter, a runtime telemetry record and dependency edges | #40 @tynamite, @zwright8 | Proposal |
| Q4 | Which managed offerings expose engine/GPU metrics | #37 @PUSHINGSQUARES, #9 @Mattycodes69 | Unknown |
| Q5 | RAG freshness/ingestion signals | #16 @zabyxc01 | Unknown |
| Q6 | Agent retry/approval/task-success signals | #25/#28 @CompleteDotTech | Unknown |
| Q7 | Guardrail trigger signals | #35 @PUSHINGSQUARES | Unknown |
| Q8 | Cost derivation and provider usage/cost APIs | #39 @PUSHINGSQUARES | Unknown |
| Q9 | Lawful basis and default retention for logged content | @PUSHINGSQUARES; #35/#38, using CD-12 organisation attestations for the lawful-basis reference | Open |
| Q10 | AMD/Apple accelerator telemetry; Grafana/MLflow | @PUSHINGSQUARES | Not researched |
| H1 | Accept the #11→#38 signal mapping above (release labels, queue/KV/device memory) | @Mattycodes69 | Pending |
| H2 | Confirm the threshold source pointers | @tynamite (#2) | Pending |

No handoff has been confirmed yet. A review request does not count as a confirmation.
