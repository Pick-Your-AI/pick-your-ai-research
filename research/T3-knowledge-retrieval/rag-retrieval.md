# RAG and retrieval backends

Issue: [#16](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16) · Contract: 1.0.0 · Kinds: `rag_pipeline`
Status: engineering decision `rag-retrieval-decision/0.2.0` offered for independent receiving review; actual incoming decisions and outstanding delivery gates are recorded below · Last researched: 2026-10-18 (targeted supplement; older source dates retained)

## User decision

How will the system retrieve and cite relevant knowledge at query time, and which retrieval backend fits? The note covers the pipeline (query processing, retrieval, reranking, context assembly, citations), the backend decision, where source permissions are enforced, the context budget against #7, and retrieval evaluation criteria for #36.

Boundaries follow [DEPENDENCIES.md](../../docs/DEPENDENCIES.md). #16 owns the backend **choice**. #13 owns knowledge storage semantics, ACL metadata, rights and sync. #14 owns embedding models. #15 owns vector database products. This decision consumes the accepted embedding/vector interfaces below; it does not repeat their product evaluations. pgvector appears for its documented filter behaviour (R05/R35). Agent orchestration stays with #25 and the evaluation harness with #36.

RAG is an optional capability ([#12](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/12)). An evidenced build without retrieval needs no retrieval diagnostic. The current proposals mechanically skip without an enabled `rag_pipeline`; that is an implementation limitation for a tool-only retrieval path, not an authorization or compatibility exemption. The accepted #14/#15 interface requires the existing bound-pipeline route until #40 adopts and implements explicit actual-path binding. Inventory the chosen path: a framework name or an omitted selection does not establish that retrieval, embeddings or a vector leg are absent.

Wording follows the interim #41 definition from the [PR #75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75). **Source checked** means the claim was confirmed against the cited primary source on its access date. Nothing here is **verified**, meaning independently reproduced. No connector, index, reranker or API was exercised, and no paid API or account was used.

## Pipeline stages

| Stage | What happens | Owner of the inputs | Notes |
| --- | --- | --- | --- |
| Query processing | Rewrite, decompose or route the query; derive metadata filters | #16 (decisions), #25 for agentic retrieval | Bedrock query decomposition can issue multiple queries (R12). LangChain distinguishes 2-step, agentic and hybrid RAG; agentic RAG lets the LLM decide when to retrieve, so latency varies (R16). |
| Retrieval | Keyword, vector, hybrid, graph or direct lookup | #16; vector product #15; embeddings #14 | See the decision guide. |
| Permission enforcement | Bind the authenticated caller to the resource/read action and mandatory scope before model or tool exposure | #16 (enforcement point); #13 (ACL metadata and sync) | See [Permission enforcement](#permission-enforcement-points); a service credential or optional search filter is insufficient. |
| Fusion and reranking | Merge result lists (RRF), then optionally rerank with a cross-encoder | #16; reranker model identity needs a contract decision (#40) | RRF score is a sum of 1/(rank_constant + rank); Elasticsearch's default `rank_constant` is 60 (R03). |
| Context assembly | Order, deduplicate, truncate or drop chunks; attach source identifiers | #16 with #7 budget rules | Position matters: performance "can degrade significantly when changing the position of relevant information" (R22). |
| Citation | Return source pointers with the answer | #16; display with the builder | See [Citations](#citations). |

## Backend decision guide

These conditions implement the scoped engineering choice in [Recommendation and rationale](#recommendation-and-rationale); they make no universal performance claim. **Hypothesis** marks project reasoning that no source in this note establishes. MTEB found that "no particular text embedding method dominates across all tasks" (R21), and BEIR found BM25 "a robust baseline" across 18 zero-shot datasets (R20). Neither replaces a workload-specific test (#36).

| Backend | Fits when | Requires | Failure modes | v1 `retrieval_mode` |
| --- | --- | --- | --- | --- |
| **Keyword / BM25** | Exact identifiers, product codes, names, jargon, dates. Azure names these as cases where keyword search "perform[s] better" (R10). A first comparison baseline (R20); actual cost remains unpriced. | Inverted index and analyzer; BM25 scoring (Elasticsearch default k1=1.2, b=0.75, R02). No embedding model or vector store. | Vocabulary mismatch and paraphrase (hypothesis). PostgreSQL's built-in `ts_rank`/`ts_rank_cd` "do not use any global information" (R06), so treat them as term-frequency ranking, not BM25. | `keyword` (`sparse` is ambiguous; see contract gap G2) |
| **Vector (dense)** | Conceptual similarity without shared keywords (R10); multilingual matching when the embedding space covers it (R10). | The selected #14 query/document representation profiles and #15 index generation: actual field width, role-specific encoding, normalization, operator, scoring/sign/order and supported representation must agree. Matching dimension and a metric name alone do not establish compatibility. | Filtered approximate search can return fewer eligible results (R05/R35, R08). A changed representation needs a qualified migration/re-indexing plan (#14/#15). Shared ANN populations can affect another tenant's recall and speed (R05/R35). Quality and score thresholds remain separate from representation compatibility. | `dense` |
| **Hybrid** | Mixed query types, where both exact matches and paraphrases matter. Azure reports benefits for hybrid retrieval with a semantic ranker in its own testing (R10, vendor claim). | Both qualified retrieval legs and the selected fusion operation (RRF, R03/R10). Bind backend, store, operation, API/adapter version, fields and query configuration. | Bedrock's guide and API reference disagree about supported stores (R12/R34); this is unresolved documentation, not an observed fallback. Evaluate each leg as well as fusion under the selected workload (project decision). | `hybrid` |
| **Graph** | Holistic, whole-corpus questions (GraphRAG global search), or entity-centred questions needing related facts (local/DRIFT search) (R14). | LLM-built knowledge graph and community reports; LLM calls at index and query time (R14). | "GraphRAG indexing can be an expensive operation" (R13). The repository says it "is not an officially supported Microsoft offering" (R13). Global search is "resource-intensive" (R14). | none (gap G1) |
| **Direct lookup / SQL / API** | Structured facts with an authoritative key or query: account state, inventory, prices (hypothesis). | Database or API with its own authorization. PostgreSQL row security restricts rows per user, with default-deny when enabled and no policy exists (R07). Live API calls are T4 tools (#26/#27). | Superusers, `BYPASSRLS` roles and table owners bypass RLS by default (R07). Generated SQL needs read-only, least-privilege credentials (hypothesis; #35). | none (gap G1); may be a `tool` instead |
| **Long context, no retrieval** | The whole permitted corpus fits the request budget with output reserved, and every reader may see all of it (hypothesis). | Passes CTX-01 for the complete assembled input ([context-fit.md](../T1-model-selection/rules/context-fit.md)). | Cost and latency grow with tokens (#39). The position effect still applies (R22). Per-user ACL subsetting becomes the application's job before assembly. | no `rag_pipeline` selected |

**When a vector store is unnecessary.** A chosen keyword-only, direct-lookup or whole-context path with no vector operation needs no vector database. A graph-only path qualifies only when its complete selected plan has no vector leg; GraphRAG's name does not establish that, and its documented basic search uses vectors (R14). Reuse an existing qualified store where appropriate; do not force a new dedicated instance. The baseline dependency graph currently marks `rag_pipeline → embedding_model` and `rag_pipeline → vector_database` as `requires` under `rag_enabled` ([core-dependency-graph.json](../../contracts/v1/baseline/core-dependency-graph.json)), while `rule.rag.dense.dependencies` limits the requirement to `dense`/`hybrid`. Gap G3 remains with #40; this note does not patch frozen v1 or claim the optional-path limitation is implemented away.

## Candidate options

Licences and versions were taken from the GitHub repository API on 2026-10-17 (latest release, or latest tag when there was no release). Prices were not collected. Pricing semantics belong to #39.

| Candidate | Mode | Version / licence | Backends documented | Permission mechanism | Evidence |
| --- | --- | --- | --- | --- | --- |
| Elasticsearch | Self-hosted (Elastic Cloud not evaluated) | v9.5.5; default triple licence AGPL-3.0-only / SSPL-1.0 / Elastic License 2.0 per file header | BM25 (default similarity), kNN, hybrid `bool` and RRF | Document-level security role query (read-only restriction). kNN `filter` is a pre-filter; other query filters are post-filters (R01) | R01–R04 |
| OpenSearch | Self-hosted (managed service not evaluated) | 3.9.0; Apache-2.0 | BM25, k-NN | Efficient k-NN filtering during search; post-filtering "may return significantly fewer than `k` results" (R08). DLS restricts reads, not writes; multiple role queries are combined with OR (R09) | R08–R09 |
| PostgreSQL full-text search + RLS | Self-hosted | 18 (docs 18.6); PostgreSQL License | Full-text search with `ts_rank`/`ts_rank_cd` (not BM25, R06). Vector leg via an extension such as pgvector (product detail is #15's) | Row security policies (R07) | R05–R07 |
| Vespa | Self-hosted (Vespa Cloud not evaluated) | v8.763.13; Apache-2.0 | `nearestNeighbor` combined with filters and query terms in YQL (R15) | Filter strategies: pre-filtering is the default, configurable with `approximate-threshold` / `post-filter-threshold` (R15) | R15 |
| Microsoft GraphRAG | Self-hosted library | v3.3.0; MIT | Graph: local, global, DRIFT and basic vector search (R14) | Not documented in the pages checked: **unknown** | R13–R14 |
| LlamaIndex | Self-hosted framework | v0.14.25; MIT | Vector, keyword-table, knowledge-graph (keyword/embedding/hybrid modes) and summary retrievers (R17) | Delegated to the backend: unknown per integration | R17 |
| LangChain | Self-hosted framework | langchain-core 1.6.12; MIT | Retriever interface; 2-step, agentic and hybrid RAG architectures (R16) | Delegated to the backend: unknown | R16 |
| Haystack | Self-hosted framework | v3.4.0 (docs 3.4); Apache-2.0 | BM25 sparse, dense embedding, hybrid via `DocumentJoiner`, `FilterRetriever` (R18) | Filter policies; enforcement delegated to the document store: unknown | R18 |
| Azure AI Search | Managed | Docs ms.date 2026-08-21 / 2026-08-31 / 2026-08-08; REST 2026-04-01 (GA), 2026-08-01-preview | BM25 and vector hybrid with RRF; optional semantic ranker; `vectorFilterMode` pre/post (R10) | Security-filter string trimming (GA, API-agnostic). Native Entra ACL/RBAC, SharePoint ACL and Purview label enforcement are **preview** (R11) | R10–R11 |
| Amazon Bedrock Knowledge Bases | Managed | User guide accessed 2026-10-17; no version shown | SEMANTIC or HYBRID (store-dependent), metadata filters, reranking, query decomposition (R12) | Metadata filters on the request (R12). Whether filters are a security boundary is **unknown** in this source | R12 |
| OpenAI file search | API | Guide accessed 2026-10-17 | Hosted "semantic and keyword search" over vector stores; attribute filters; `max_num_results` (R19) | Attribute filters (R19). A security-boundary claim is **unknown** | R19 |
| Cohere Rerank | API (reranker) | Model names `rerank-v4.0-pro`, `rerank-v4.0-fast`, `rerank-v3.5`, `rerank-english-v3.0`, `rerank-multilingual-v3.0` (R23) | Reranker only | n/a | R23 |
| BAAI bge-reranker-v2-m3 | Self-hosted weights (reranker) | Apache-2.0 model card | Cross-encoder; example uses `max_length=512`; sigmoid-normalised score optional (R24) | n/a | R24 |

**Deployment modes.** The table retains its dated product/access labels; those labels alone do not classify a selected build. Apply [#9's accepted operating boundary](../T2-infrastructure/hosting.md#hosting-taxonomy-and-deployment-mode-mapping-owner-reviewed-proposal) per serving component: customer-operated runtime is self-hosted; provider-operated dedicated instances or reserved throughput are managed; provider-operated shared capacity is API. Thus this comparison covers a shared provider retrieval/rerank path, a provider-operated dedicated serving path (qualified through #9/#15), and a customer-operated engine/reranker path. Exact operator/capacity evidence is required for the chosen offer. HTTP transport, monthly billing, customer cloud-account placement or a framework licence cannot supply it. A framework may compose several modes; MCP/tools/storage retain their own operator/location checks without independently setting build mode. No new host, serving component or deployment object is invented here. Managed vector-product selection remains #15's.

Elastic's subscription matrix text alone did not resolve DLS/RRF tiers (R04). The [pinned-code supplement](#source-gap-resolution-2026-10-18) now identifies the v9.5.5 feature gates: Platinum for DLS/FLS and Enterprise for RRF. These are code-level requirements, not a claim about an account's entitlement or Cloud plan.

## Permission enforcement points

Ranked from the earliest to the latest point in the pipeline. The ranking is a project proposal; each row's mechanism is source checked.

| Point | Mechanism (example) | Candidate-count boundary | Risk |
| --- | --- | --- | --- |
| P1. Source-native, at query time | Azure token in `x-ms-query-source-authorization`, compared with synchronised ACL, RBAC or Purview metadata (R11, preview) | Depends on selected engine/query and eligible population | Changes in source permissions require synchronized index metadata (R11). Permission freshness and revocation must be qualified; source-native naming alone cannot prove current authorization. |
| P2. Index pre-filter | Elasticsearch kNN `filter` (R01); OpenSearch efficient filtering (R08); Azure security filters (R11); PostgreSQL RLS (R07); Vespa default pre-filtering (R15) | Avoids the documented unmitigated post-scan pattern under the engine's applicable conditions; no cross-product k or recall guarantee | ACL fields must be current and complete. Azure's string-based security-filter pattern does not authenticate the principal (R11). Filter support and caller authorization are distinct. |
| P3. Engine post-filter | Filters outside the kNN clause (R01); pgvector after an approximate scan (R05/R35); OpenSearch post-filtering (R08) | Can return fewer than k; applicable iterative/expanded scanning can mitigate but remains bounded | Coverage can affect answer correctness. Security requires the entire pre-filter path and all derived outputs to stay within the authorized boundary; the filter stage alone proves neither security nor quality. |
| P4. Application post-filter before model/tool exposure | The trusted application drops unauthorised hits before any reranker/model call, agent tool response or other exposure outside its authorized boundary | Can return fewer than k; measure under the selected candidate/effort limits | Scores, counts, facets, snippets, traces or shared caches can leak if exposed before trimming (project inference). Azure's performance comparison remains a vendor claim (R11). |
| P5. After generation, or none | — | — | **Always fails** RAG-02. Unauthorised text would already be in the model's context. |

**ACL propagation (handed to #13).** Chunking must copy document permissions to every chunk. Azure states that with a chunking skillset, ACL fields "move from indexer field mappings to index projections", and that without projecting labels to each chunk row, "chunk-level references aren't filtered" (R11). Engine DLS controls reads, not writes (R01, R09). OpenSearch advises that users with DLS roles should not have write access (R09). In Elasticsearch, alias filters act as pre-filters (R01).

**Receiving-review clarification (2026-10-18).** The stage names above locate enforcement; they do not establish caller authorization. [RAG-02](rules/retrieval-rules.md#rag-02-caller-authorization-precedes-model-and-tool-exposure) now carries the R29–R31 supplement's trusted caller/store/action binding, non-replaceable mandatory scope and derived-artifact coverage into its assertion and synthetic counterexamples. A known wrong-tenant filter fails even when the index applies that filter correctly. Missing binding or permission-revision evidence remains unknown and blocks protected retrieval. This is a proposed engineering policy for #40/#35, not a deployed security result.

## Citations

Citation support records the required source granularity and exact request composition. It is not a boolean or an assumed total ordering between page and character/block spans:

- `none`
- `document_id`: OpenAI `file_citation` annotations carry `file_id` and `filename` (R19). Bedrock citations need the `$output_format_instructions$` placeholder (R12).
- `span` or `page`: Anthropic Citations return `char_location`, `page_location` or `content_block_location` with `cited_text` (R25).

Anthropic's pointer guarantee applies to the supplied documents (R25/R36). Pointer validity, semantic claim support, answer completeness, factual correctness and permission to expose the source are separate checks. Preserve document/chunk revision identity and the mapping from transformed context to the original source; do not relabel a page, span or filename after dropping, deduplication or reordering. Anthropic's current guide prohibits the exact combination of citation-enabled document/search-result inputs with structured output through `output_config.format` (R36). That restriction does not establish a provider-wide or tool-wide incompatibility. Select a supported model/route/input/output combination and evaluate the resulting attribution under #36.

## Context budget with #7

**Actual incoming disposition: accepted with constraints.** The [#7 → #16 receiving decision of 2026-10-18](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6253273759) accepts the counting interface below. That decision is attributed to the delegated coordinating reviewer, not an absent co-assignee. It accepts neither a backend nor a whole-chunk drop policy, and it does not supply the separate #16 → #7 policy decision. The [later #6 → #16 identity receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6254086817) preserves these same counting limits without claiming runtime or quality evidence.

1. In RAG-01, P is the configured input allowance at `context_policy` `/settings/requested_context_tokens`. The complete input count or eligible bound used by CTX-01 is a separate quantity. It includes instructions, template framing, history, tools/results, retrieved content, source/citation metadata, memory and supported media after the selected generation tokenizer/template and serialization are applied. [CTX-01](../T1-model-selection/rules/context-fit.md) remains authoritative for full request fit, with the applicable output reservation and route/model limits checked separately from this retrieval subtotal.
2. RAG-01 is a pre-assembly screen. M × S bounds retrieved payload only when M (`max_chunks`) and S (`chunk_size_tokens`) are applicable enforced bounds in the generation tokenizer/template. H is an eligible bound for the retrieval-related citation/header overhead in that serialization. Missing H leaves the screen unresolved; zero is usable only when measured as zero for that serialization. An embedding-tokenizer chunk size, an arbitrary sum of independently tokenized fragments or unevidenced template overhead cannot establish this bound. Recount or provide an eligible bound for the actual serialization; no subtotal pass establishes complete request fit.
3. Proposed content-preservation policy (hypothesis, owner decision): when over budget, drop whole lowest-ranked chunks rather than cutting through a chunk, never drop instructions, and recount after every transform. This is the post-transform recount that [context-warnings.md](../T1-model-selection/rules/context-warnings.md) requires. Mid-chunk truncation would break `cited_text` spans.
4. A fit is not a quality check. The position effect (R22) and the absence of a universal usable-context threshold (#7, CW04) both mean quality has to be measured by #36.

**Synthetic counting example:** M=5, S=400 and H=100 give a retrieval subtotal of 2,100 tokens against an 8,000-token input allowance. If the separately counted complete serialized request is 8,200 tokens, the request exceeds that allowance even though the retrieval screen passes. This is arithmetic, not an executed tokenizer or request. Every permitted transform requires a new complete-request count or eligible bound while preserving required content and citation identities. Summarization, extraction and reranking calls retain their own selected-model input limits, output reservations where applicable, and costs.

**T2 inputs** ([handoffs.md](../T2-infrastructure/handoffs.md), [inference-engine.md](../T2-infrastructure/inference-engine.md)). Proposed: accept with constraints. Generation, embedding and reranking models are separate selections with their own tokenizers and limits. In 2-step RAG, retrieval completes before generation starts streaming. Agentic retrieval interleaves with tool rounds and #25 owns that (R16). An engine's streaming or batching documentation is not a retrieval-quality claim.

**Outgoing content-preservation decision for #7.** The four-point counting record above is preserved from [PR #391](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/391), including its historical proposed policy and incoming-only acceptance. This revision offers the narrower engineering policy for a new receiving decision: dropping whole lowest-ranked chunks is permitted only by a documented strategy that the selected workload allows. Required instructions, required evidence/content and source identities must survive. After each permitted transformation, recount the complete serialized request or supply an eligible bound, retain the applicable output reservation, and rerun CTX-01. If the required minimum still cannot fit, report incompatibility or an unresolved fit; do not silently summarize, reduce the required output reservation or discard required content. Summarization/extraction is a separately selected call with its own model, limits, permission boundary and cost, and requires an explicit workload transformation policy. It is not a free context-budget repair. The actual incoming #7 and #6 receipts do not pre-accept this outgoing policy.

## Comparison fields

| Field / JSON pointer | Type and unit | Evidence requirement | Status |
| --- | --- | --- | --- |
| backend type → catalog `/spec/retrieval_mode` | enum `dense`/`sparse`/`hybrid`/`keyword` | Backend documentation naming the retrieval method, version-pinned | v1. Graph and lookup missing (G1); `sparse` undefined (G2) |
| required components | list of canonical kinds | Derived from baseline rules and dependency graph | Note-only. G3 dependency conflict |
| reranker → `/spec/supports_rerank`, selection `/settings/rerank_enabled` | boolean | Reranker documentation or model card, with input limit | v1 booleans. Reranker identity and input limit have no operand (G4) |
| citation support | proposed enum `none`/`document_id`/`span`/`page` | API or framework documentation showing the output fields | Note-only (G5) |
| permission enforcement point | proposed enum `source_native`/`index_prefilter`/`engine_postfilter`/`app_postfilter`/`none` | Engine security or filter documentation; preview vs GA status | Note-only (G5) |
| ACL sync lag | duration, minutes | Source-specific sync documentation, or measured | Note-only. #13 owns sync; KB `/settings/refresh_minutes` exists |
| latency contributors | list: query rewrite, query embedding, ANN, BM25, filter, fusion, rerank, graph map-reduce, LLM calls | Measured p50/p95 per stage under stated load (#36/#38). No vendor figure adopted | Note-only |
| complete context input used | integer count or eligible token bounds under #7 | Complete serialized request counted with the selected generation tokenizer/template, including all required inputs and framing | CTX-01 input; not bounded by M × S alone |
| retrieval subtotal bound | M × S + H, generation-model tokens | Applicable enforced M/S and eligible serialization-specific H; unknown overhead is not zero | RAG-01 screen against configured `/settings/requested_context_tokens`; separate from complete context input |
| top_k → selection `/settings/top_k` | integer ≥1 | Configuration | v1 |
| supported chunking → `/spec/supported_chunking` | enum list | Framework or service documentation | v1. Chunk settings are #13's |
| deployment mode | API / managed / self-hosted | Hosting documentation (#9 definitions) | Envelope plus hosting refs |
| selected retrieval path | operation/configuration record; identities and revisions, no numeric unit | Actual participating components, endpoint/store/adapter and query, each retrieval leg, fusion, and applicable support evidence | Note-only; no actual-path operand added to frozen v1 |
| reranker input policy | model/route/runtime and tokenizer/template identities; complete encoded input count or eligible bound in that tokenizer's tokens; item/query/pair/batch limits in their stated units | Model/endpoint evidence plus actual truncation/chunking configuration and required-content disposition | Note-only G4; `/spec/supports_rerank` is insufficient |
| citation request and mapping | required granularity, input/output formats, source/chunk revisions and resolvable location records; no common numeric unit | Exact request-composition support and mappings after allowed transforms | Note-only G5; page and span are not interchangeable ordinals |
| caller authorization scope | principal/resource/action binding, mandatory scope, permission/revocation revision and derived-artifact coverage | Trusted implementation binding and source/ACL policy; stage name and a service credential alone cannot satisfy it | Note-only; #13/#35 retain lifecycle and security ownership |
| evaluation protocol | dataset/query/qrels/configuration revisions; k/counts as integers, ratios with explicit denominators, latency in ms | Eligible corpus and permission scope, aggregation protocol, judge/rubric where used, actual observations and exclusions | Note-only handoff to #36; no new `EvaluationReport` representation |
| billed retrieval events | distinct operation/event IDs and quantities in the actual meter's unit; rate scope and billing period | Traceable quantity, eligible rate, route/item/region/currency/date/account/plan and allowance/minimum conditions | Note-only handoff to #39; no fabricated Pricebook entry |

Counts and ratios above are proposed measurement fields, not observations. Preserve published limits with their source/model/operation conditions; label any calculated bound or scenario as an estimate with its method. Unknown source support, quantity, rate or denominator cannot be replaced by zero.

## Compatibility proposals

[rules/retrieval-rules.md](rules/retrieval-rules.md) defines RAG-01 to RAG-06 in the #40 format, with outcome separate from severity and unknown never passing:

- RAG-01: retrieved upper bound fits the input budget. `error`.
- RAG-02: caller authorization precedes model and tool exposure. `error`.
- RAG-03: a reranker is identified and its input limit is respected. `warning`.
- RAG-04: requested hybrid mode is honoured by the backend. `warning`.
- RAG-05: filtered approximate search can return fewer than k results. `warning`.
- RAG-06: citations are required but unsupported. `warning`.

All six are proposals. None is a verified rule.

**Contract gaps for #40.** None of these are patched here.

- G1: no `retrieval_mode` value for graph or direct lookup.
- G2: `sparse` and `keyword` are both enum values with no definition separating them (BM25 vs learned sparse).
- G3: `dep.rag_pipeline.embedding_model` and `dep.rag_pipeline.vector_database` are `requires` edges under `rag_enabled`, which conflicts with keyword mode.
- G4: no reranker kind or role, and no reranker input limit.
- G5: no fields for enforcement point, citation level or ACL sync lag.

## Retrieval evaluation criteria (handoff to #36)

Proposed `evaluation_suite` `/spec/metric_names` for `rag_pipeline` targets. BEIR's framework computes nDCG@k, MAP@k, Recall@k, Precision@k and MRR at k ∈ {1, 3, 5, 10, 100, 1000} (R20b).

| Metric | Stage | Why | Source |
| --- | --- | --- | --- |
| ANN fidelity against exact eligible neighbours | Retrieval implementation | Separates approximation/candidate coverage from labelled relevance and downstream answer quality; requires an eligible exact reference under the same permission/filter and representation scope | Proposed #36 measurement, consuming #15's comparability boundary; no measured value supplied |
| Recall@k, with k = configured `top_k` | Retrieval | A document that was not retrieved cannot be recovered by reranking or generation (hypothesis) | R20b |
| nDCG@10 | Retrieval/rerank | Rank-sensitive; reported across the benchmarks in R20 and R21 | R20, R20b, R21 |
| MRR@k | Retrieval/rerank | First relevant hit, for single-answer lookups | R20b |
| Filtered-k shortfall rate | Retrieval | Separately records candidate-count shortfall under the selected filter/search-effort configuration; does not measure recall | Project metric; motivates RAG-05 |
| Permission leakage count (target 0) | All exposure points | Adversarial ACL/revocation cases, including derived data, caches, traces and pre-generation reranker/tool exposure | Project target, not a proof of universal security |
| Faithfulness | Generation | Fraction of answer claims supported by retrieved context, range 0–1 (Ragas) | R26/R37; judge and extraction protocol must be recorded |
| Citation support vs pointer validity | Generation | Valid pointers (R25) do not imply support | Project metric |
| Context tokens used; per-stage latency p50/p95 | Ops | Inputs to #7, #39 and #38 | Measured only |

**Proposed receiving protocol.** Bind each result to the selected plan, corpus/query/qrels revisions, document/chunk granularity, source-use rights, caller scope, model/tokenizer/index generations, filter, ANN effort, reranker and fusion settings. Record k, relevance labels, rank deduplication/tie treatment, denominators and aggregation. Queries without eligible judgments cannot be silently counted as successful or removed from the disclosed case totals. Public BEIR/MTEB results retain their original datasets and model conditions; they are not acceptance evidence for a user's corpus. #36 owns qrels, the harness and workload quality thresholds.

For ANN fidelity, bind the exact eligible-neighbour reference, distance/tie policy, permission/filter scope and denominator separately from labelled qrels. A missing reference or zero/unknown denominator is unavailable under this proposed protocol, not a perfect score. For filtered-k shortfall, report eligible population evidence and actual returned count separately. The proposed rate's denominator is the number of eligible evaluated queries known to have at least k permitted candidates; its numerator is those that returned fewer than k under the fixed configuration. Queries with a smaller eligible population are reported separately; unknown population leaves this rate unresolved. Fewer returned results alone does not establish that relevant results were missed, while returning k does not establish high recall. R35's iterative scan limits and RAG-02 authorization continue to apply. RAG-05 skips an evidenced exhaustive exact plan without an earlier candidate cutoff; that does not skip returned-count, relevance or permission evaluation.

For answer evaluation, keep pointer resolution, citation support, attribution coverage, faithfulness and answer correctness separate. A faithful statement can still omit a necessary answer or repeat a source's factual error (project reasoning). R37 supplies the supported-claim fraction; this proposed protocol additionally records claim extraction, judge/model/prompt/rubric versions, calibration against reviewed examples, failed judgments and uncertainty. A zero or unknown claim denominator is unavailable under this protocol, not an automatic perfect score. A finite leakage panel with a zero target tests only its recorded cases; it does not certify the service's security.

Record per-stage and complete-request latency in milliseconds, with actual sample counts, p50/p95 calculation, time window, hardware/route, concurrency/load, warm/cold and cache state. Distinguish whole-request latency from overlapping/interleaved stage durations; do not sum overlapping timings as elapsed time. Record failed/retried/excluded cases and the reason for exclusion. These are proposed evaluation requirements; this research ran no retrieval workload, benchmark or model-based judge.

## Pricing and capacity

No new prices, usage measurements or throughput measurements were collected. The following is the engineering accounting handoff to [#39](../T6-deployment-operations/cost-estimate.md); #10 retains capacity and #9/#15 retain hosting/vector offer scope.

| Event or cost family | Required quantity/conditions | Accounting boundary |
| --- | --- | --- |
| Document embedding, chunk/index writes, re-embedding and rebuild | Actual inputs/writes and selected meter; representation/index generation and refresh/rebuild trigger | Separate initial ingestion, incremental refresh and full rebuild; dimension count is not a billing quantity |
| Query rewrite/embedding, retrieval, fusion and reranking | Actual operation/event identity, selected route, attempts and billed requests/documents/tokens or other eligible unit | A rerank result count is not its billed input count; batch/chunk/retry behavior needs its own evidence (R27/R32/R33) |
| Graph indexing and query generation | Actual indexing/extraction/community and query map/reduce model events; selected-model usage and any billed infrastructure | GraphRAG documents work at indexing and query time (R13/R14); a stage name provides no traffic multiplier or token quantity |
| Context assembly, summaries, memory and generation | Actual separately executed calls, serialized inputs/output usage and source identity; cache reads/writes under the selected rate terms | Count real repeated calls/serialization; deduplicate only multiple labels for the same billed event. A reservation is not a usage forecast |
| Persistent storage, indexes, caches, transfer and held capacity | Actual storage/unit-duration/requests/egress and operating period; provisioned floors, allowances and eligible shared allocation | Held or idle capacity bills only under its actual terms, and cannot disappear merely because query count is zero. Reusing an ID does not prove a shared instance or entitlement |

Each admitted rate must bind the real item/version, provider/route/operation, meter/unit, region, currency, access/validity date, account/plan conditions and billing period. Keep one-time and recurring costs separate, respect rate minima/allowances, and disclose the allocation of shared infrastructure or memory. Missing stages or unsupported unit conversions produce a partial estimate with the omitted coverage visible; they cannot establish a budget pass. No generic stage-to-graph-traffic conversion is adopted. The actual quantities and price evidence belong in #39's accepted cost protocol, not invented values in this research note.

The accepted [#7 → #39 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6253295884) retains both sides of applicable context/billing thresholds and the eligible higher-tier budget screen. Required output reservation remains distinct from expected output usage; a billing-sensitivity factor is not a context-fit bound. This handoff does not choose new prices, currency/FX defaults, a throughput rate or a v1 wire representation. Separate retained models and indexes need actual capacity evidence; a framework's low source footprint does not establish serving fit.

## Recommendation and rationale

Revision `rag-retrieval-decision/0.2.0` makes these conditional engineering decisions under the user's project authorization, subject to the independent receiving reviews below. It attributes no response to an absent assignee and adopts no production rule or workload result.

1. **Start from the actual information need.** Omit retrieval when it is unnecessary. Prefer an authorized direct lookup for authoritative structured facts. For a document-search workload without stronger evidence, compare keyword/BM25 first, using R20's baseline finding as motivation rather than a quality or cost guarantee. Existing qualified local storage/search can be reused; no dedicated vector service is required by default.
2. **Add dense or hybrid retrieval only for a qualified workload.** Use the selected #14/#15 representation/index profiles and compare the relevant semantic, language and exact-match cases under #36. Hybrid must bind both retrieval legs and fusion; an advertised capability or unresolved R12/R34 conflict cannot certify the chosen operation. The decision is conditional on measured quality, latency, cost and operating constraints, with those results still unknown here.
3. **Keep graph retrieval optional.** Choose it for a justified relationship/global-question workload only with explicit indexing/query costs, a selected plan and qualified authorization of derived entities/reports (R13/R14/R29). A GraphRAG or framework label supplies neither vector-free execution nor a security boundary. Multimodal retrieval likewise requires evidenced source representations, modality-specific limits and eligible relevance/citation evaluation; a text-only comparison cannot certify it (#13/#14/#36).
4. **Use whole context only when eligible.** The complete permitted source set, instructions, history, tools, media and framing must satisfy CTX-01 with the required output reservation and selected route limits. Apply the outgoing conditional content-preservation policy above before changing content. Passing a subtotal never establishes full fit or usable-context quality.
5. **Prefer early permission enforcement.** Select P1/P2 where the chosen path actually establishes trusted caller/resource/action binding, current mandatory scope and permission propagation. P3/P4 are eligible only when the entire pre-filter path and every derived exposure remain within that same authorized boundary before any reranker/model/tool/cache/trace exposure. A RAG-05 warning alone cannot satisfy RAG-02. Known stale/unauthorized scope fails; missing binding evidence stays unknown and blocks protected retrieval.
6. **Keep operating tradeoffs explicit.** API/managed paths reduce the application's runtime-operation scope but still require eligible account, location, capacity, permissions and billing evidence; self-hosted paths add runtime/index operation and recovery responsibilities (#9/#13/#15). Select reranking and citation output only when the exact input/request composition is qualified. Evaluation, source freshness and pricing coverage remain visible conditions, not implied by a successful request or source check.

## Structured artifacts

No `CatalogItem` was proposed. A `rag_pipeline` catalog entry would need a modelling decision on what a single item represents: a framework, a managed service, or a backend configuration. Most decision-relevant fields (enforcement point, citation level, reranker identity) have no v1 operand. Publishing items with only `retrieval_mode` would hide those unknowns. No Pricebook or evidence manifest was added.

## Evidence

R01–R26 below retain their 2026-10-17 access dates. R27–R37 are separately dated 2026-10-18 supplements; a later reading does not silently refresh every historical claim. Grades: PD = primary documentation, VC = vendor claim, IM = independent measurement (published paper; not reproduced here). Synthetic examples and project decisions are not measurements. Reuse is short paraphrase with links under #41's policy; source/code licence does not establish permission to reuse a user's corpus. No price is supplied here, so currency is not applicable; service region/account eligibility stays unknown unless explicitly evidenced for the selected route.

| ID | Publisher and URL | Version / region | Grade | Limitations |
| --- | --- | --- | --- | --- |
| R01 | Elastic, [kNN query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query); [document-level security](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/controlling-access-at-document-field-level) | Current docs ("Generally available"); nested pre-filter GA since 9.2 | PD | Section version labels mostly absent |
| R02 | Elastic, [similarity settings](https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity) | Current docs | PD | — |
| R03 | Elastic, [RRF](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) | Current docs | PD | Tier not stated |
| R04 | Elastic, [subscriptions](https://www.elastic.co/subscriptions); [licence](https://github.com/elastic/elasticsearch/blob/v9.5.5/LICENSE.txt) | v9.5.5 | PD | Tier checkmarks not readable as text: tier unknown |
| R05 | pgvector, [README](https://github.com/pgvector/pgvector/blob/v0.8.7/README.md) (Filtering, Iterative Index Scans, Multitenancy, Hybrid Search) | v0.8.7 tag; PostgreSQL-style licence | PD | Product evaluation is #15's |
| R06 | PostgreSQL, [Controlling text search](https://www.postgresql.org/docs/18/textsearch-controls.html) | 18.6 | PD | — |
| R07 | PostgreSQL, [Row security policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html) | 18.6 | PD | — |
| R08 | OpenSearch, [Filtering vector search results](https://docs.opensearch.org/latest/vector-search/filter-search-knn/index/) | "latest" docs; release 3.9.0 | PD | Doc version unstated |
| R09 | OpenSearch, [Document-level security](https://docs.opensearch.org/latest/security/access-control/document-level-security/) | "latest" docs | PD | — |
| R10 | Microsoft, [Hybrid search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview) | ms.date 2026-08-31; API 2026-04-01 | PD; relevance-benefit sentence VC | — |
| R11 | Microsoft, [Document-level access control](https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview); [security filters](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search) | ms.date 2026-08-08 / 2026-08-21; native ACL preview 2026-08-01-preview | PD; performance claim VC | Preview has no SLA |
| R12 | AWS, [Bedrock KB query configuration](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html) | "latest" user guide; region not stated | PD | Security semantics of filters not stated |
| R13 | Microsoft, [GraphRAG README](https://github.com/microsoft/graphrag/blob/v3.3.0/README.md) | v3.3.0, MIT | PD | Cost unquantified |
| R14 | Microsoft, [GraphRAG query overview](https://microsoft.github.io/graphrag/query/overview/) | Current docs | PD | — |
| R15 | Vespa, [nearest neighbor search](https://docs.vespa.ai/en/querying/nearest-neighbor-search.html); [HNSW](https://docs.vespa.ai/en/querying/approximate-nn-hnsw.html) | Current docs; release v8.763.13, Apache-2.0 | PD | Threshold selection logic not on page |
| R16 | LangChain, [Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) | Current docs; langchain-core 1.6.12, MIT | PD | No BM25 or ensemble on this page |
| R17 | LlamaIndex, [Retriever modes](https://developers.llamaindex.ai/python/framework/module_guides/querying/retriever/retriever_modes/) | Current docs; v0.14.25, MIT | PD | — |
| R18 | deepset, [Haystack retrievers](https://docs.haystack.deepset.ai/docs/retrievers) | Docs 3.4; v3.4.0, Apache-2.0 | PD | — |
| R19 | OpenAI, [File search](https://developers.openai.com/api/docs/guides/tools-file-search) | Current guide | PD | Ranking internals not documented |
| R20 | Thakur et al., [BEIR, arXiv:2104.08663v4](https://arxiv.org/abs/2104.08663) | v4, 2021-10-21; NeurIPS 2021 D&B | IM | Zero-shot public datasets |
| R20b | BEIR, [README](https://github.com/beir-cellar/beir/blob/v2.2.0/README.md) | v2.2.0, Apache-2.0 | PD | — |
| R21 | Muennighoff et al., [MTEB, arXiv:2210.07316v3](https://arxiv.org/abs/2210.07316) | v3, 2023-03-19 | IM | Leaderboard values not adopted |
| R22 | Liu et al., [Lost in the Middle, arXiv:2307.03172v3](https://arxiv.org/abs/2307.03172) | v3, 2023-11-20; TACL | IM | Models tested predate current releases |
| R23 | Cohere, [Rerank overview](https://docs.cohere.com/docs/rerank-overview) | v2 API docs, undated | PD | Token and document limits not on page: unknown |
| R24 | BAAI, [bge-reranker-v2-m3 model card](https://huggingface.co/BAAI/bge-reranker-v2-m3) | Apache-2.0 | PD | 512 is an example value, not a documented maximum |
| R25 | Anthropic, [Citations](https://platform.claude.com/docs/en/build-with-claude/citations) | GA (page metadata) | PD | — |
| R26 | Ragas, [Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) | Stable docs (footer 2025-12-09); release v0.4.3, Apache-2.0 | PD | Legacy API deprecation noted |

## Open questions and handoffs

The incoming decisions below were read as actual comments/reviews on 2026-10-18. Their original source pins, direction and limits remain authoritative. The new outgoing packet is the complete revision `rag-retrieval-decision/0.2.0` in this note and its six rule proposals. Independent reviewers must identify that concrete source and the receiving scope; earlier receipts do not accept unseen amendments. A delegated reviewer can make an explicit engineering disposition under the user's project authorization without impersonating an absent assignee. Mere co-assignment, silence or a previous generic T4 acknowledgement is not a new receiving decision.

### Accepted information inputs

| Input | Actual record and disposition | Retained boundary |
| --- | --- | --- |
| #7 context counting | [6253273759](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6253273759), incoming counting accepted with constraints; [#391](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/391) carries the clarification | P is configured allowance; M × S + H is a qualified retrieval screen; complete CTX-01 accounting remains separate. No reverse content-loss policy acceptance is inferred |
| #6 model identity | [6254086817](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6254086817), incoming identity receipt | Selected model/provider/runtime limits and complete-request counting remain bound to their actual scope; no quality/runtime result follows |
| #14 embeddings | [6253659087](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14#issuecomment-6253659087), accepted with constraints at original reviewed `94fcf3da` | Role-aware query/document profiles, encoding, width, normalization/operator and index generation; embedding, generation and reranker tokenizers differ. Preserve the real bound-pipeline gate and all relevant EMB/VDB checks |
| #15 vector interface R1 | [5564586116](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/387#pullrequestreview-5564586116), exact reviewed `4438baf7`; [later source-preservation review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/387#pullrequestreview-5564635693) retains its scope | Optional no-vector paths require actual inventory; reuse of an existing qualified instance is allowed. Complete request/authorization precedes every exposure, and representation comparability does not establish a quality target |
| #65 interoperability desk input | [Completed #65](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65), [actual receiving receipt 6250267864](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65#issuecomment-6250267864), delivered by [#332](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/332) | The protocol and conditional Bedrock disagreement are desk research; no API execution or general negative capability is supplied. Its positive optional UserContext scope remains separate |

### Outgoing review packet and named follow-ups

| To / owner | Request | Status |
| --- | --- | --- |
| #16 @zabyxc01 | Conditional backend, enforcement and operating decision above | Concrete coordinating decision offered in this revision; actual independent receiving dispositions and protected delivery remain to be recorded |
| #7 @zwright8 | New outgoing conditional content-preservation policy; unchanged accepted RAG-01 counting block and fixed blocking unknown policy | Pending review of this revision; incoming acceptance above is not the reverse handoff |
| #13 @tynamite, @zabyxc01 | Actual ACL metadata/revision propagation, rights, sync/revocation and derived-artifact lifecycle | Follow-up for selected implementations; `acl_enforced` or an enforcement-stage enum does not prove caller authorization |
| #14 @zabyxc01, @PUSHINGSQUARES | Preserve accepted representation/tokenizer input; qualify any selected reranker model/route later | Input accepted above; remaining route-specific gaps are explicit unknowns, not a re-request of that completed input |
| #15 @zabyxc01, @appletechie | Preserve R1 and product-specific filter/iteration boundaries | Input accepted above; selected query/effort and measured coverage still need their own evidence |
| #25 @CompleteDotTech, @Mattycodes69 | Bind tool/agentic retrieval to the real pipeline path, authorize before every model/tool exposure, and retain per-round complete context/cost | [Earlier bounded T4 input](../T4-agents-integrations/agent-framework.md#t3-retrieval-receiving-review-2026-10-18) retained; new complete packet pending explicit receiving disposition |
| #28 @CompleteDotTech, @PUSHINGSQUARES | Reuse retrieval infrastructure without conflating application memory, knowledge, index generations, consent, retention or erasure | [Earlier bounded T4 input](../T4-agents-integrations/agent-memory.md#t3-storage-and-retrieval-receiving-review-2026-10-18) retained; new packet pending. Current permission and memory-lifecycle evidence remains independent of storage-ID reuse |
| #35 @appletechie, @PUSHINGSQUARES | Trusted caller/store/action binding, mandatory scope, retrieved-text prompt injection and least-privilege lookup; cover rerankers, tools, traces, caches and graph summaries | New packet pending. Retrieved content is data, not authority to change instructions, permissions or tool scope; no deployed security claim |
| #36 @appletechie, @PUSHINGSQUARES | Adopt the scoped metric/protocol handoff above with distinct retrieval, answer, citation, leakage and operational evidence | New packet pending. Workload gates, qrels and harness implementation remain #36's; no dataset score or universal quality target supplied |
| #39 @appletechie, @PUSHINGSQUARES | Adopt actual-event accounting, eligible meter/rate binding, graph/refresh/cache/capacity coverage and unresolved-budget semantics | New packet pending. No stage traffic multiplier, new price, currency default or capacity estimate supplied |
| #40 @zwright8, @tynamite | Versioned RAG-01–06 adoption, G1–G5, actual-path binding and any new request/evidence operands | Central adoption remains separate from research completion; no schema, generated artifact, severity or runtime implementation changed |
| #41 @tynamite, @PUSHINGSQUARES | Selected-account entitlement, current source qualification/rights and preview refresh scope | Follow-up for eligible catalog/production claims; dated primary-code/doc evidence and unresolved conflicts remain explicit |
| #65 @zabyxc01, @appletechie, @itisSomeone | Preserve completed desk input; pass any selected runtime experiment to its actual implementation/evaluation owner | Completed input above. This revision starts no #65 experiment and does not reopen it |

Remaining implementation evidence is named rather than hidden: #16/#14 qualify the selected reranker and backend operation; #13/#35 qualify actual permission propagation and graph/filter enforcement; #36 measures the selected workload; #9/#15/#39 qualify entitlement, capacity and billing. A source disagreement or absent account-specific result stays unknown. These future implementation decisions do not erase completed research inputs or supply the still-required actual outgoing receipts.


## Source-gap resolution (2026-10-18)

All entries below are primary documentation or source inspection, not executed behavior or independent measurements. Their access date is 2026-10-18. They support the conditional project decision above without independently supplying a receiving-owner response. Product/model limits and source disagreements retain the exact scope described; no account/region entitlement or price is established.

### Reranker input boundaries

Cohere's [v2 Rerank reference](https://docs.cohere.com/v2/reference/rerank) (R27, mutable documentation, accessed 2026-10-18) documents `POST /v2/rerank`: more than 1,000 documents is discouraged for performance, not stated as a hard rejection threshold. `max_tokens_per_doc` defaults to 4,096 and longer documents are truncated. `top_n` controls returned results, not how many documents are supplied. These endpoint parameters alone do not establish each model's query-plus-document ceiling. Keep selected model/tokenizer and actual truncation settings with the configuration; a required passage removed from retained input cannot be recovered merely by returning more results (project inference).

R32 — Cohere's [Rerank model guide](https://docs.cohere.com/docs/rerank), mutable guide, supplies a published 4,096-token model window for the named v3.5/v3.0 models and describes query/document accounting and automatic document chunking. R33 — its [reranking best practices](https://docs.cohere.com/docs/reranking-best-practices), mutable guide, describes the v4 pro/fast window as 32,768 tokens with four reserved tokens and the v3 document chunk size as 4,093. These are distinct model/configuration claims, not interchangeable limits or measurements. R33's generic query table states 2,048 tokens, while its v4-specific paragraph describes 16,384; its `max_chunks_per_doc` description is not the same as R27's v2 parameter surface. The selected model/route must resolve applicable query, pair, document and batch constraints rather than inheriting the most permissive value. This note preserves known documented limits while leaving unresolved route conflicts unknown.

R24's BGE model-card example was rechecked on 2026-10-18: `max_length=512` is applied by the tokenizer to query/document pairs with truncation enabled. It establishes an example's joint encoded-input setting, not a provider/model-wide maximum or a separate 512-token document allowance before adding a query. RAG-03 therefore requires actual joint accounting (or an eligible bound), framing, applicable request limits and an explicit required-content/truncation disposition. Neither the BGE example nor a successful Cohere request proves that all required text survives. No model or reranker was executed.

### Elastic feature entitlement

R28 — Elasticsearch v9.5.5, commit `48acba663b09e70b115dd879329141506c377890`, source checked 2026-10-18:

- [SecurityField.java](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/security/SecurityField.java) declares `DOCUMENT_LEVEL_SECURITY_FEATURE` and `FIELD_LEVEL_SECURITY_FEATURE` with minimum operation mode `PLATINUM`.
- [RRFRankPlugin.java](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/x-pack/plugin/rank-rrf/src/main/java/org/elasticsearch/xpack/rank/rrf/RRFRankPlugin.java) declares `RANK_RRF_FEATURE` with `ENTERPRISE`; [RRFRetrieverBuilder.java](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/x-pack/plugin/rank-rrf/src/main/java/org/elasticsearch/xpack/rank/rrf/RRFRetrieverBuilder.java) checks that feature against the shared license state when parsing the retriever.

Do not infer feature entitlement from source-code availability or the top-level license choice. Check the selected distribution/version and active license separately; trial and hosted-plan entitlements need their own evidence. This settles the pinned implementation's gate, without inventing a subscription price or assuming a Cloud plan matches it.

### GraphRAG derived-data authorization

R29 — GraphRAG v3.3.0, commit `5faaaf4f5685fa2056fa8c3bf9342cb089f2942f`, [global search implementation](https://github.com/microsoft/graphrag/blob/5faaaf4f5685fa2056fa8c3bf9342cb089f2942f/packages/graphrag/graphrag/query/structured_search/global_search/search.py), inspected 2026-10-18. Its search entry point receives a query and conversation history, builds context through the supplied context builder, and maps over community summaries before reduction. This inspected path does not itself establish an authenticated caller-to-document ACL check. This is a scoped observation, not proof that every GraphRAG integration lacks authorization.

The integration policy in this revision restricts derived entities, relationships and community reports as well as source chunks before any model call. Filtering citations after generation cannot remove information already summarized across private documents. Use separately authorized graph artifacts or a reviewed context builder with permission propagation; until that implementation and leakage tests exist, shared mixed-permission graph retrieval remains authorization-unknown. #16 owns the integration decision with #13/#35; this note performs no #65 experiment.

### Hosted filters and trusted authorization

R30 — AWS [knowledge-base service-role permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html), mutable guide accessed 2026-10-18. AWS states that ingestion uses the role bound to the knowledge base; a data-source manager can ingest locations that role can read and query them without holding S3 permissions. Restricting the service role and privileged ingestion actions is therefore separate from authorizing an application's end user. R12's request metadata filters and implicit model-generated filters establish selection mechanisms, not caller identity or source ACL inheritance.

R31 — OpenAI [file-search guide](https://developers.openai.com/api/docs/guides/tools-file-search), Responses API, mutable guide accessed 2026-10-18. The application supplies `vector_store_ids` and optional file-attribute `filters`. The demonstrated category filter is a search predicate; it is not evidence of an authenticated user-to-file permission check.

The engineering policy for both services is that the trusted application authenticates the caller, authorizes the requested store/knowledge base and operation, derives mandatory ACL scope from trusted metadata, and intersects optional user search constraints with it. Do not let user input or model-generated filters replace mandatory scope. A known unauthorized store, untrusted replacement filter or stale permission state fails; missing eligible ACL/binding evidence remains unknown and blocks protected retrieval. Validate revocation and mixed-permission cases before claiming P2 enforcement. A service credential's ability to retrieve data does not by itself authorize the end user. Deployed security remains unverified and this revision's receiving decisions must be recorded separately.

### Hybrid support and the Bedrock documentation conflict

R34 — AWS's [KnowledgeBaseVectorSearchConfiguration API reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_KnowledgeBaseVectorSearchConfiguration.html), mutable API documentation, lists HYBRID for OpenSearch Serverless with a filterable text field and SEMANTIC for other vector stores. The separately reread R12 user guide lists RDS, OpenSearch Serverless and MongoDB for HYBRID with that field condition. The two pages do not establish an aligned store/operation/version scope for an arbitrary selected request. Preserve this conflict for RDS/MongoDB qualification; do not turn either page into a universally observed fallback. A separately eligible exact-operation incompatibility fails RAG-04; an unresolved conflict or omission from an incomplete support list remains unknown. #65's completed desk review supplies no runtime response, and this supplement made no Bedrock request.

### Filtered ANN and bounded mitigation

R35 — pgvector v0.8.7 [README at commit `f37c13f68b57d2c3472b2214fbcff699d6d34876`](https://github.com/pgvector/pgvector/blob/f37c13f68b57d2c3472b2214fbcff699d6d34876/README.md), Filtering / Iterative Index Scans / Multitenancy sections, primary source inspection. Approximate scans can apply filters after candidate scanning. Iterative scans search further until enough results are found or applicable scan/probe limits are reached. Strict distance ordering concerns returned ordering; it does not establish perfect recall. Its multitenancy guidance also distinguishes shared ANN populations from per-tenant approaches.

R01's current [Elasticsearch kNN query reference](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query) was separately rechecked on 2026-10-18: the filter's position determines whether it applies within kNN candidate search or after it. This mutable query documentation does not pin all behavior to the candidate table's v9.5.5 or establish account feature entitlement. RAG-05's engineering screen asks whether an applicable mitigation is actually configured. Observed returned count, relevance, permission enforcement and cost remain separate evidence; a bounded iterative configuration does not promise k results.

### Citation request composition and faithfulness

R36 — Anthropic's [Citations guide](https://platform.claude.com/docs/en/build-with-claude/citations), mutable documentation, rechecked for supported document types, location representations and structured-output restrictions. It distinguishes PDF pages, plain-text character locations and custom-content blocks, and disallows citation-enabled document/search-result inputs together with `output_config.format`. Qualify that exact request composition and selected model route. No citation-enabled request was run. RAG-06 and the metric protocol separate format/pointer support from semantic support, completeness, factual correctness and authorization.

R37 — Ragas's [Faithfulness metric](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/), mutable stable documentation, defines a score from 0 to 1 as supported response claims divided by total response claims. It is a metric definition, not a score measured here. The disclosed-judge, calibration, case-accounting and zero-denominator rules in the proposed #36 protocol are project decisions; no Ragas example, model judge or benchmark was executed. R26's earlier release/date metadata is preserved without claiming it identifies this mutable page's current software revision.

## Literal acceptance and delivery record

The following preserves the ten literal criteria from the actual issue read on 2026-10-18. It maps the prepared artifact without marking unreceived or unmerged work complete. Actual source review, receiving dispositions, required validation, protected merge/default verification and issue/Project reconciliation must be recorded at their real revisions.

| Literal #16 criterion | Artifact and current evidence boundary |
| --- | --- |
| Backend decision guide with conditions | Backend guide and six conditional engineering decisions above; source review pending for this revision |
| Context-budget rule agreed with #7 | Actual incoming counting receipt and unchanged #391 counting block; new outgoing content-preservation decision awaiting explicit #7 receiving review |
| Retrieval evaluation criteria handed to #36 | Metrics, denominators, configuration/quality boundaries and no-execution limits prepared for #36; actual receiving disposition pending |
| Decision record merged at `research/T3-knowledge-retrieval/rag-retrieval.md` following the research method | Existing record is merged; this substantive completion revision still requires reviewed delivery |
| Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | Dated candidates and per-component operator/capacity qualification; selected offer entitlement remains separate |
| Comparison fields defined with type, unit, and evidence requirement | Typed comparison table, separate exact-path/request/evaluation/cost evidence; no fabricated v1 operands |
| Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | Six rule proposals with fixed severity, explicit unknown/applicability and synthetic cases; central adoption and runtime implementation remain separate |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | R01–R37, preserved historical dates and claim conditions, pinned-source supplements, no new prices or execution measurements; independent evidence review pending |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | Five outgoing consumers #25/#28/#35/#36/#39 and the separate #7 compatibility review require concrete-source dispositions; earlier receipts retain their original scope |
| Open questions recorded with a named follow-up owner | Named selected-model/operation, permissions, quality, billing and central-adoption follow-ups above; no implicit reopening of completed #65 |
