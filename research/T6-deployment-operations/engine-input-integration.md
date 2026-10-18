# Engine inputs for deployment and monitoring

Issues: #11 → #37/#38. Source recheck: **2026-10-18**. Status: source-checked integration proposal; no engine, container, GPU job or metrics scrape was run.

This record addresses the concrete integration work in [appletechie's #11 receiving response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245668428). That response accepted deployment inputs with integration pending and narrowed monitoring acceptance to labels/evidence requirements. It reviewed main `66b46d4`; it is not acceptance of this later record or a response by another co-owner.

The input is the [#11 engine record](../T2-infrastructure/inference-engine.md) and [ENGINE-01–04 proposals](../T2-infrastructure/rules/engine-compatibility.md), read from research main `481d7703ca663e7cc10e077a4625426c8f3f6a6b`. Their fixed-severity clauses, evidence status, per-component applicability and central #40 decisions remain authoritative for this proposal. This document maps research inputs to the existing #37/#38 records. It publishes no executable rule, contract field, selected configuration or deployment approval.

## 1. Deployment trace from #11

| #11 input | Existing #37 locations | What the integration requires | Remaining evidence |
| --- | --- | --- | --- |
| ENGINE-01: loader and architecture | S42/S43; R5/R29 | Pin the engine/build/plugins and model artifact. Use its documented loader format, architecture and conversion requirements. A matching extension or flat format intersection is insufficient. | The selected binary/image digest, artifact/conversion lineage and loading result. |
| ENGINE-02: joint backend/precision support | S40/S41/S44/S48; R28/R31 | Use the same scoped support family as COMPUTE-02 and T0 D-R3. Keep weight, activation and KV dtypes, backend/kernel/driver and per-device placement separate. Do not add duplicate final rule IDs or infer support from a capacity estimate. | Exact build/device/artifact support and #10's capacity evidence; runtime load/SLO evidence remains separate. |
| ENGINE-03: adapter lineage and loading | S43/S44; R20/R29 | Carry #33's immutable base/tokenizer and adapter manifest plus #11's selected loading/routing mode. A merged checkpoint is a full artifact; an omitted `adapter_only` value is not evidence of a merge. | Exact adapter/base compatibility, conversion and residency evidence for the selected engine. |
| ENGINE-04: required API contract | S44/S48; R17/R22/R29 | Carry the actual endpoint, template/parser, schema/strictness and streaming/error/cancellation requirements. Use the [FC-1–FC-7 consumer specifications](../../tests/fixtures/t4-engine-consumer.md) where applicable; their existence is not an executed result. | Actual request/response and applicable #36 gate results for the selected tuple. |
| Engine access and egress evidence; no new ENGINE group | S45; R30; #35 G-R25/G-R26 | The pinned vLLM security source limits `--api-key` protection to named prefixes and requires additional endpoint isolation [ET6-S6]. R30 is the engine endpoint check; R18 remains the separate tool/MCP credential check. | Authorized gateway/endpoint and outbound-connection tests on the deployed configuration. |

A documentation-supported `pass` at fixed `error` severity is not a failure and remains labelled unverified unless independently corroborated or reproduced. An evidenced contradiction can fail; absence from an unmarked support list remains unknown after the #41 conflict order. These research clauses do not supply a final Ruleset or replace its approved `on_unknown` policy. Applicability is per serving component, including a known local engine in a hybrid configuration. A known opaque provider route does not establish a local engine version; missing scope must not be silently skipped.

### Loader policy correction for S43

The earlier S43 wording applied a Safetensors-only policy across self-hosted engines. That would reject the documented direct-loader format of llama.cpp `v0.7.0`, which requires GGUF and treats conversion from other formats as a separate step [ET6-S4]. S43 now applies the reviewed format policy to the selected engine: the existing Safetensors/pickle-exclusion policy belongs to a supported Safetensors path; llama.cpp uses a pinned GGUF artifact and its conversion/source lineage. vLLM's conditional GGUF plugin path still requires the separate plugin/build evidence in #11.

This is not a general approval of GGUF contents, arbitrary conversion code or additional formats. Artifact checksums identify bytes; a signature identifies its stated signing identity. Neither establishes compatible architecture, benign content, redistribution rights or successful execution. Preserve #35's unsafe-loading controls and #33's artifact distinctions. The current catalog's conservative format subsets are unchanged.

## 2. Exact research identities

| Engine | Examined release and source commit | Monitoring evidence read | Scope |
| --- | --- | --- | --- |
| vLLM | `v0.31.0` · `db9527a46873454610df6dbedf79a36d6bf1a7f6` | Metrics guide and V1 logger source, ET6-S1/S2 | Source registrations and documented endpoint; no selected wheel/image/plugin or exposed series verified. |
| llama.cpp | `v0.7.0` · `620d2225cc436ab0b001e3200e590e3b286ef9ab` | Server reference and model-format guide, ET6-S3/S4 | Published endpoint, metric names/types and loader requirement; no binary flags or scrape verified. |
| TGI | `v3.3.7` · `dfb3fbe78e0d1d69251bd33065591c61bafdfaa8` | Pinned metric reference, ET6-S5 | Published names/types; #11 retains maintenance/archival evidence and its bounded candidate recommendation. |

These reuse #11's researched identities, not an independently refreshed latest-release inventory. The same engine name behind NIM, KServe or a managed endpoint does not prove this revision, route, metric set or configuration. Each selected service needs its own package/build and metric evidence.

## 3. Monitoring reconciliation

The table reconciles the existing #38 SG70–SG76 scope. Names below are source-level registrations or publisher documentation, not a transcript from a running service.

| #38 signal | Exact vLLM v0.31.0 identifier(s) | Source type / unit | Interpretation and remaining limit |
| --- | --- | --- | --- |
| SG70 | `vllm:time_to_first_token_seconds` | Histogram; seconds | The V1 logger uses `model_name` and `engine` labels. Do not assume every wrapper exposes or preserves them. ET6-S2. |
| SG71 | `vllm:inter_token_latency_seconds`; `vllm:request_time_per_output_token_seconds` | Histograms; seconds | Inter-token samples and per-request time per output token remain different distributions. No client/network or percentile equivalence is inferred. ET6-S2. |
| SG72 | `vllm:e2e_request_latency_seconds`; `vllm:request_queue_time_seconds` | Histograms; seconds | The latter measures the engine's waiting phase; it is not an application's complete end-to-end queue. ET6-S2. |
| SG73 | `vllm:num_requests_waiting`; `vllm:num_requests_waiting_by_reason`; `vllm:num_requests_running` | Gauges; requests | The reason-specific registration adds a `reason` label. Waiting and admitted/running work remain separate from workload demand and allocated KV capacity. ET6-S2. |
| SG74 | `vllm:kv_cache_usage_perc`; `vllm:num_preemptions` | Gauge, ratio where 1 means full KV use; Counter, events | KV occupancy is not total device memory utilization. The preemption identifier is the registered counter base; the selected scrape must confirm its exposition form, including `_total`. ET6-S2. |
| SG75 | `vllm:prompt_tokens`; `vllm:generation_tokens` | Counters; processed tokens | These are the registered bases. SG75's published `_total` recording-rule names still need selected-exporter confirmation; rates require valid observation windows and reset handling. Processed tokens are not an invoice or measured capacity guarantee. ET6-S2. |

ET6-S1 documents `/metrics` and a deprecation cycle: metrics deprecated in X.Y become hidden in X.Y+1 (temporarily exposed with the documented version flag), then are removed in X.Y+2. This is a source-described migration rule; do not assume an old dashboard or a “stable” URL matches a selected build. The source guide expands generated metric sections, so ET6-S2 supplies the exact V1 registrations instead of treating the unexpanded Markdown as a complete name list.

| Engine / #38 scope | Pinned published mapping | What remains separate |
| --- | --- | --- |
| TGI v3.3.7, SG76 | `/metrics`; `tgi_queue_size` is a request-count gauge; `tgi_request_duration`, `tgi_request_mean_time_per_token_duration` and `tgi_request_queue_duration` are second-valued histograms. ET6-S5. | TGI's mean-per-token histogram does not become vLLM's individual inter-token distribution. The #38 concurrency-limit claim retains its earlier launcher source/date; this pass does not recheck it or run that configuration. |
| llama.cpp v0.7.0, corresponding throughput/queue inputs for #38 | `/metrics` requires `--metrics`. In router mode the reference requires `?model={model_id}`. It lists `llamacpp:prompt_tokens_total` / `llamacpp:tokens_predicted_total` as counters, `llamacpp:prompt_tokens_seconds` / `llamacpp:predicted_tokens_seconds` as throughput gauges, and `llamacpp:requests_processing` / `llamacpp:requests_deferred` as gauges. ET6-S3. | Preserve the publisher's names and semantics; do not rename them to vLLM series. This bounded endpoint table does not establish a TTFT histogram or KV-occupancy series for the selected llama.cpp build. None is invented to satisfy R31. New #38 signal IDs, alert expressions and actual exposure remain a receiving decision. |

### Selected-service evidence needed by #38

Record the exact engine/release/source revision and deployed binary/image, backend and enabled plugins; the metrics endpoint/wrapper and exporter version; the actual enabled metric names, types, units and bounded label set; and the configuration affecting admission, context, cache or adapter residency. Keep these in the deployment/evidence record. Their presence there does not mean the engine emits all of them as metric labels.

A later authorized observation must bind the scrape to that record and show startup versus steady state, counter reset behavior, relevant request/queue/cache signals and collection failures. A missing series is unavailable, not measured zero. Histograms, gauges, cumulative counters, derived rates and client-side latency remain distinct. No threshold, alert delay, resource headroom or current service-health result is derived from this desk check.

Do not add prompts, retrieved text, tool arguments, credentials or unrestricted user labels just to correlate a metric. Apply #35/#38's content, cardinality, access and retention decisions. vLLM/TGI telemetry and request-logging switches (SG92/SG93) retain their original evidence; this metrics-name pass does not certify their configured values or absence of other sensitive output.

## 4. Primary sources

Each source was read through the public GitHub API on **2026-10-18**, at the full immutable commit above. Evidence class: primary publisher documentation or source. Source checking is not independent runtime verification. Git blob identities below identify inspected files; they are not model/package hashes, runtime receipts or permission grants.

| ID | Primary file | Git blob | Finding scope |
| --- | --- | --- | --- |
| ET6-S1 | [vLLM metrics guide](https://github.com/vllm-project/vllm/blob/db9527a46873454610df6dbedf79a36d6bf1a7f6/docs/usage/metrics.md) | `8254a7f4207e5304d606c69956680e4b4e317bea` | Endpoint, generated-section boundary and deprecation cycle. |
| ET6-S2 | [vLLM V1 metrics logger](https://github.com/vllm-project/vllm/blob/db9527a46873454610df6dbedf79a36d6bf1a7f6/vllm/v1/metrics/loggers.py) | `26a4142df9f1023f8d43633b30b85adf745eba41` | The twelve named registrations above, their Gauge/Counter/Histogram constructors and labels. |
| ET6-S3 | [llama.cpp server reference](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/tools/server/README.md) | `4e4472ec24bd0822be30e327aecd549cc15a2bc8` | Metrics flag/router condition and bounded published metrics list. |
| ET6-S4 | [llama.cpp model-format guide](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/docs/models.md) | `eee5952634be3dbf7133f68c7be831d8bc69f6c7` | GGUF requirement and separate conversion path. |
| ET6-S5 | [TGI metrics reference](https://github.com/huggingface/text-generation-inference/blob/dfb3fbe78e0d1d69251bd33065591c61bafdfaa8/docs/source/reference/metrics.md) | `d34d38eab7d94563cb54949c28c6ad044305a672` | Endpoint and the four SG76 names, types and units. |
| ET6-S6 | [vLLM security guide](https://github.com/vllm-project/vllm/blob/db9527a46873454610df6dbedf79a36d6bf1a7f6/docs/usage/security.md) | `a6c986775522c1f7a583514fb9126573a88b0891` | Restricted API-key scope and additional endpoint-isolation requirement. |

## 5. Receiving disposition still required

For #37, the concrete follow-up is the ENGINE group-to-step/readiness map and the engine-scoped S43 correction above. For #38, it is the exact-release name/type reconciliation, including the exporter/scrape limits and the additional bounded llama.cpp mapping. The earlier #11 receipt is preserved as history; the actual #37/#38 owners must accept, narrow or reject this later revision, with its exact research pin.

#11 retains selected-runtime support and candidate decisions; #10 retains capacity; #33 retains artifact lineage; #35 retains trust/privacy controls; #36 retains executed evaluation evidence; #40 retains the versioned contract and executable ruleset. The content integration and ordinary repository checks do not complete those issues or claim a new operational result.
