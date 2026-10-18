# RAG and retrieval backends

Issue: [#16](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16) · Contract: 1.0.0 · Kinds: `rag_pipeline`
Status: partial decision record for review; #7 context-counting input accepted with constraints, other receiving decisions remain scoped below · Last researched: 2026-10-18 (targeted supplement; older source dates retained)

## User decision

How will the system retrieve and cite relevant knowledge at query time, and which retrieval backend fits? The note covers the pipeline (query processing, retrieval, reranking, context assembly, citations), the backend decision, where source permissions are enforced, the context budget against #7, and retrieval evaluation criteria for #36.

Boundaries follow [DEPENDENCIES.md](../../docs/DEPENDENCIES.md). #16 owns the backend **choice**. #13 owns knowledge storage semantics, ACL metadata, rights and sync. #14 owns embedding models. #15 owns vector database products. A vector store is referenced here only as the `dense` backend category, and pgvector appears only for its documented filter behaviour (R05). The #15 draft is being offered by another contributor and is not pre-empted. Agent orchestration stays with #25 and the evaluation harness with #36.

RAG is an optional capability ([#12](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/12)). When no `rag_pipeline` is selected, every rule below is `skipped`, and no "no retrieval configured" diagnostic is proposed. This matches the T4 memory draft's rejection of that noise in [PR #72](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/72).

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

These are conditions for a proposed default, not universal performance claims. **Hypothesis** marks project reasoning that no source in this note establishes. MTEB found that "no particular text embedding method dominates across all tasks" (R21), and BEIR found BM25 "a robust baseline" across 18 zero-shot datasets (R20). Neither replaces a workload-specific test (#36).

| Backend | Fits when | Requires | Failure modes | v1 `retrieval_mode` |
| --- | --- | --- | --- | --- |
| **Keyword / BM25** | Exact identifiers, product codes, names, jargon, dates. Azure names these as cases where keyword search "perform[s] better" (R10). A cheap, robust first baseline (R20). | Inverted index and analyzer; BM25 scoring (Elasticsearch default k1=1.2, b=0.75, R02). No embedding model or vector store. | Vocabulary mismatch and paraphrase (hypothesis). PostgreSQL's built-in `ts_rank`/`ts_rank_cd` "do not use any global information" (R06), so treat them as term-frequency ranking, not BM25. | `keyword` (`sparse` is ambiguous; see contract gap G2) |
| **Vector (dense)** | Conceptual similarity without shared keywords (R10); multilingual matching when the embedding space covers it (R10). | Embedding model (#14) and vector index (#15); matching dimension and metric (baseline `rule.embedding.dimension`, `rule.vector.distance.support`). | Approximate indexes that filter after the scan return fewer results (R05, R07, R08). Embedding drift after a model change requires re-indexing (baseline remediation text). Shared ANN indexes let one tenant affect another's recall and speed (R05). | `dense` |
| **Hybrid** | Mixed query types, where both exact matches and paraphrases matter. Azure reports benefits for hybrid retrieval with a semantic ranker in its own testing (R10, vendor claim). | Both indexes plus a fusion step (RRF, R03/R10). Bedrock HYBRID only works on RDS, OpenSearch Serverless and MongoDB stores with a filterable text field (R12). | **Silent downgrade:** on other Bedrock stores "the query uses semantic search" (R12). Fusion hides each list's recall, so evaluate both legs (hypothesis). | `hybrid` |
| **Graph** | Holistic, whole-corpus questions (GraphRAG global search), or entity-centred questions needing related facts (local/DRIFT search) (R14). | LLM-built knowledge graph and community reports; LLM calls at index and query time (R14). | "GraphRAG indexing can be an expensive operation" (R13). The repository says it "is not an officially supported Microsoft offering" (R13). Global search is "resource-intensive" (R14). | none (gap G1) |
| **Direct lookup / SQL / API** | Structured facts with an authoritative key or query: account state, inventory, prices (hypothesis). | Database or API with its own authorization. PostgreSQL row security restricts rows per user, with default-deny when enabled and no policy exists (R07). Live API calls are T4 tools (#26/#27). | Superusers, `BYPASSRLS` roles and table owners bypass RLS by default (R07). Generated SQL needs read-only, least-privilege credentials (hypothesis; #35). | none (gap G1); may be a `tool` instead |
| **Long context, no retrieval** | The whole permitted corpus fits the request budget with output reserved, and every reader may see all of it (hypothesis). | Passes CTX-01 for the complete assembled input ([context-fit.md](../T1-model-selection/rules/context-fit.md)). | Cost and latency grow with tokens (#39). The position effect still applies (R22). Per-user ACL subsetting becomes the application's job before assembly. | no `rag_pipeline` selected |

**When a vector store is unnecessary.** Keyword, graph-only, direct lookup and long-context builds need no vector database. The baseline dependency graph currently marks `rag_pipeline → embedding_model` and `rag_pipeline → vector_database` as `requires` under `rag_enabled` ([core-dependency-graph.json](../../contracts/v1/baseline/core-dependency-graph.json)). That contradicts keyword mode, while `rule.rag.dense.dependencies` correctly limits the requirement to `dense`/`hybrid`. See contract gap G3.

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

**Deployment modes.** API (OpenAI file search, Cohere Rerank), managed (Azure AI Search, Bedrock Knowledge Bases) and self-hosted (engines, libraries, BGE weights) are all represented. Managed offerings of Elasticsearch, OpenSearch and Vespa exist but were not evaluated. Managed vector-database services belong to #15.

Elastic's subscription matrix text alone did not resolve DLS/RRF tiers (R04). The [pinned-code supplement](#source-gap-resolution-2026-10-18) now identifies the v9.5.5 feature gates: Platinum for DLS/FLS and Enterprise for RRF. These are code-level requirements, not a claim about an account's entitlement or Cloud plan.

## Permission enforcement points

Ranked from the earliest to the latest point in the pipeline. The ranking is a project proposal; each row's mechanism is source checked.

| Point | Mechanism (example) | Returns k? | Risk |
| --- | --- | --- | --- |
| P1. Source-native, at query time | Azure token in `x-ms-query-source-authorization`, compared with synchronised ACL, RBAC or Purview metadata (R11, preview) | Engine-managed | Changes in the source system "are only reflected in search results after that metadata is synchronized to the index" (R11). Freshness lag is a leak window. |
| P2. Index pre-filter | Elasticsearch kNN `filter` (R01); OpenSearch efficient filtering (R08); Azure security filters (R11); PostgreSQL RLS (R07); Vespa default pre-filtering (R15) | Yes, when enough matches exist (R01, R08) | The filter is only as current and complete as the ACL fields #13 propagates. In the Azure filter pattern, the principal "is just a string" with no authentication (R11). |
| P3. Engine post-filter | Filters outside the kNN clause (R01); pgvector after an approximate scan (R05); OpenSearch post-filtering (R08) | **No.** Fewer than k results, even when enough matches exist (R01, R05, R08) | Recall loss for restricted users. Still secure if applied before results leave the engine (hypothesis). |
| P4. Application post-filter before model/tool exposure | The trusted application drops unauthorised hits before any reranker/model call, agent tool response or other exposure outside its authorized boundary | No | Scores, counts, facets, snippets, traces or shared caches can leak if exposed before trimming (hypothesis). Azure lists performance as a benefit of native filtering over post-query trimming (R11, vendor claim). |
| P5. After generation, or none | — | — | **Always fails** RAG-02. Unauthorised text would already be in the model's context. |

**ACL propagation (handed to #13).** Chunking must copy document permissions to every chunk. Azure states that with a chunking skillset, ACL fields "move from indexer field mappings to index projections", and that without projecting labels to each chunk row, "chunk-level references aren't filtered" (R11). Engine DLS controls reads, not writes (R01, R09). OpenSearch advises that users with DLS roles should not have write access (R09). In Elasticsearch, alias filters act as pre-filters (R01).

**Receiving-review clarification (2026-10-18).** The stage names above locate enforcement; they do not establish caller authorization. [RAG-02](rules/retrieval-rules.md#rag-02-caller-authorization-precedes-model-and-tool-exposure) now carries the R29–R31 supplement's trusted caller/store/action binding, non-replaceable mandatory scope and derived-artifact coverage into its assertion and synthetic counterexamples. A known wrong-tenant filter fails even when the index applies that filter correctly. Missing binding or permission-revision evidence remains unknown and blocks protected retrieval. This is a proposed engineering policy for #40/#35, not a deployed security result.

## Citations

Citation support is a field with distinct levels, not a boolean:

- `none`
- `document_id`: OpenAI `file_citation` annotations carry `file_id` and `filename` (R19). Bedrock citations need the `$output_format_instructions$` placeholder (R12).
- `span` or `page`: Anthropic Citations return `char_location`, `page_location` or `content_block_location` with `cited_text` (R25).

Anthropic states that its citations "are guaranteed to contain valid pointers to the provided documents" (R25). A valid pointer is **not** evidence that the cited text supports the claim. #36 must therefore measure citation support separately from pointer validity. Citations must keep the identity of the chunk after context truncation or reordering.

## Context budget with #7

**Actual incoming disposition: accepted with constraints.** The [#7 → #16 receiving decision of 2026-10-18](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6253273759) accepts the counting interface below. That decision is attributed to the delegated coordinating reviewer, not an absent co-assignee. It accepts neither a backend nor a whole-chunk drop policy, and it does not supply the separate #16 → #7 policy decision. The [later #6 → #16 identity receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6254086817) preserves these same counting limits without claiming runtime or quality evidence.

1. In RAG-01, P is the configured input allowance at `context_policy` `/settings/requested_context_tokens`. The complete input count or eligible bound used by CTX-01 is a separate quantity. It includes instructions, template framing, history, tools/results, retrieved content, source/citation metadata, memory and supported media after the selected generation tokenizer/template and serialization are applied. [CTX-01](../T1-model-selection/rules/context-fit.md) remains authoritative for full request fit, with the applicable output reservation and route/model limits checked separately from this retrieval subtotal.
2. RAG-01 is a pre-assembly screen. M × S bounds retrieved payload only when M (`max_chunks`) and S (`chunk_size_tokens`) are applicable enforced bounds in the generation tokenizer/template. H is an eligible bound for the retrieval-related citation/header overhead in that serialization. Missing H leaves the screen unresolved; zero is usable only when measured as zero for that serialization. An embedding-tokenizer chunk size, an arbitrary sum of independently tokenized fragments or unevidenced template overhead cannot establish this bound. Recount or provide an eligible bound for the actual serialization; no subtotal pass establishes complete request fit.
3. Proposed content-preservation policy (hypothesis, owner decision): when over budget, drop whole lowest-ranked chunks rather than cutting through a chunk, never drop instructions, and recount after every transform. This is the post-transform recount that [context-warnings.md](../T1-model-selection/rules/context-warnings.md) requires. Mid-chunk truncation would break `cited_text` spans.
4. A fit is not a quality check. The position effect (R22) and the absence of a universal usable-context threshold (#7, CW04) both mean quality has to be measured by #36.

**Synthetic counting example:** M=5, S=400 and H=100 give a retrieval subtotal of 2,100 tokens against an 8,000-token input allowance. If the separately counted complete serialized request is 8,200 tokens, the request exceeds that allowance even though the retrieval screen passes. This is arithmetic, not an executed tokenizer or request. Every permitted transform requires a new complete-request count or eligible bound while preserving required content and citation identities. Summarization, extraction and reranking calls retain their own selected-model input limits, output reservations where applicable, and costs.

**T2 inputs** ([handoffs.md](../T2-infrastructure/handoffs.md), [inference-engine.md](../T2-infrastructure/inference-engine.md)). Proposed: accept with constraints. Generation, embedding and reranking models are separate selections with their own tokenizers and limits. In 2-step RAG, retrieval completes before generation starts streaming. Agentic retrieval interleaves with tool rounds and #25 owns that (R16). An engine's streaming or batching documentation is not a retrieval-quality claim.

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
| Recall@k, with k = configured `top_k` | Retrieval | A document that was not retrieved cannot be recovered by reranking or generation (hypothesis) | R20b |
| nDCG@10 | Retrieval/rerank | Rank-sensitive; reported across the benchmarks in R20 and R21 | R20, R20b, R21 |
| MRR@k | Retrieval/rerank | First relevant hit, for single-answer lookups | R20b |
| Filtered-k shortfall rate | Retrieval | Detects P3 behaviour (R01, R05, R08) | Project metric |
| Permission leakage count (target 0) | Retrieval | Adversarial ACL test set per enforcement point | Project metric, owner policy |
| Faithfulness | Generation | Fraction of answer claims supported by retrieved context, range 0–1 (Ragas) | R26 |
| Citation support vs pointer validity | Generation | Valid pointers (R25) do not imply support | Project metric |
| Context tokens used; per-stage latency p50/p95 | Ops | Inputs to #7, #39 and #38 | Measured only |

Public benchmark scores (BEIR, MTEB) are not acceptance evidence for a user's corpus. #36 owns qrels, the harness and gates.

## Pricing and capacity

No prices or measurements were collected. These items are unpriced: managed search units, reranker calls, embedding calls, GraphRAG indexing LLM calls (R13), and vector storage (#15/#9). #39 owns pricing; #10 owns capacity.

## Recommendation and rationale

This is a proposal for @zabyxc01 to decide on, not a decision:

1. **Default backend:** keyword/BM25 as the baseline, with hybrid (BM25 + dense, fused by RRF) offered when the workload has paraphrase-heavy queries. This is supported by R20 and R10. That BM25 is enough for a given workload remains a hypothesis to be tested by #36.
2. Dense-only is not the default.
3. Graph is optional, for holistic questions, and only after the user accepts the indexing cost (R13).
4. Direct lookup goes through T4 tools when authoritative structured data exists.
5. Long context with no retrieval is used only when CTX-01 passes and every reader is entitled to the whole corpus.
6. **Enforcement:** require P1 or P2 for restricted content. P3 is acceptable only with the RAG-05 warning shown.

## Structured artifacts

No `CatalogItem` was proposed. A `rag_pipeline` catalog entry would need a modelling decision on what a single item represents: a framework, a managed service, or a backend configuration. Most decision-relevant fields (enforcement point, citation level, reranker identity) have no v1 operand. Publishing items with only `retrieval_mode` would hide those unknowns. No Pricebook or evidence manifest was added.

## Evidence

All entries were accessed on 2026-10-17. Grades: PD = primary documentation, VC = vendor claim, IM = independent measurement (published paper; not reproduced here). Reuse: short paraphrase with links, per the interim #41 position.

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

The actual incoming #7 counting decision is linked above; the T4 component owner's bounded receiving decisions for #25/#28 are linked below. Incoming and outgoing directions, the remaining policy choices and co-owner dispositions stay separate. The original drafter's co-assignment on #7, #15, #35, #36 and #39 is not itself an independent consuming-owner acknowledgement; no absent person's response is inferred.

| To / owner | Request | Status |
| --- | --- | --- |
| #16 @zabyxc01 | Decide the default backend and T2 retrieval inputs; adopt the enforcement-point and content-preservation policies | Open; the incoming #7 counting interface alone is accepted with constraints above |
| #7 @zwright8 | Review the outgoing whole-chunk drop/content-preservation policy and any later change to RAG-01 | Pending; [incoming #7 → #16 counting acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6253273759) does not accept this separate policy or reverse the handoff direction |
| #13 @tynamite, @zabyxc01 | ACL metadata per chunk, sync lag, rights; whether `acl_enforced` implies P1/P2 | Pending |
| #14 @zabyxc01, @PUSHINGSQUARES | Embedding tokenizer vs generation tokenizer for chunk budgets; reranker as a separate model | Pending |
| #15 @zabyxc01, @appletechie (Stormxftw offered draft) | Filtered ANN shortfall and pre/post-filter support per product; no product evaluation here | Pending |
| #25 @CompleteDotTech, @Mattycodes69 | Retrieval as a tool vs a 2-step pipeline (PR #69 `rule.t4.rag.integration`) | [Accepted with constraints for T4's component-owner scope](../T4-agents-integrations/agent-framework.md#t3-retrieval-receiving-review-2026-10-18); @Mattycodes69's separate scope remains pending |
| #28 @CompleteDotTech, @PUSHINGSQUARES | Retrieval-backed memory reuses this guide; memory semantics stay with #28 (PR #72) | [Accepted with constraints for T4's component-owner scope](../T4-agents-integrations/agent-memory.md#t3-storage-and-retrieval-receiving-review-2026-10-18); @PUSHINGSQUARES's separate scope remains pending |
| #35 @appletechie, @PUSHINGSQUARES | Retrieval-target guardrails: prompt injection in retrieved text; least-privilege SQL | Pending |
| #36 @appletechie, @PUSHINGSQUARES | Adopt the metric list, leakage test set and per-stage latency | Pending |
| #39 @appletechie, @PUSHINGSQUARES | Price units for search, rerank and graph indexing | Pending |
| #40 @zwright8, @tynamite | Review RAG-01 to RAG-06 and gaps G1–G5 | Pending |
| #41 @tynamite, @PUSHINGSQUARES | Elastic tier evidence; refresh window for preview features | Pending |
| #65 @zabyxc01, @appletechie, @itisSomeone | Bedrock hybrid fallback as a concrete interoperability claim to test | Pending |

The supplement below resolves specific source gaps without certifying deployed authorization. Remaining work: account-specific entitlement, model-specific rerank query/context ceilings, concrete GraphRAG authorization integration, and caller-bound Bedrock/OpenAI filtering tests. #16 owners retain these follow-ups; #65 retains its active experiment.


## Source-gap resolution (2026-10-18)

All entries below are primary documentation or source inspection, not executed behavior or independent measurements. They supplement the earlier candidate table; no default-backend or receiving-owner decision is implied.

### Reranker input boundaries

Cohere's [v2 Rerank reference](https://docs.cohere.com/v2/reference/rerank) (R27, mutable documentation, accessed 2026-10-18) documents `POST /v2/rerank`: more than 1,000 documents is discouraged for performance, not stated as a hard rejection threshold. `max_tokens_per_doc` defaults to 4,096 and longer documents are truncated. `top_n` controls returned results, not how many documents are supplied. These endpoint parameters do not establish each model's query-plus-document context ceiling. Keep the selected model/tokenizer and actual truncation setting with the evaluation configuration; an important passage outside the retained text cannot be recovered by asking for more returned results (project inference). Remaining model-specific ceilings belong to #16/#14; price units to #39.

### Elastic feature entitlement

R28 — Elasticsearch v9.5.5, commit `48acba663b09e70b115dd879329141506c377890`, source checked 2026-10-18:

- [SecurityField.java](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/security/SecurityField.java) declares `DOCUMENT_LEVEL_SECURITY_FEATURE` and `FIELD_LEVEL_SECURITY_FEATURE` with minimum operation mode `PLATINUM`.
- [RRFRankPlugin.java](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/x-pack/plugin/rank-rrf/src/main/java/org/elasticsearch/xpack/rank/rrf/RRFRankPlugin.java) declares `RANK_RRF_FEATURE` with `ENTERPRISE`; [RRFRetrieverBuilder.java](https://github.com/elastic/elasticsearch/blob/48acba663b09e70b115dd879329141506c377890/x-pack/plugin/rank-rrf/src/main/java/org/elasticsearch/xpack/rank/rrf/RRFRetrieverBuilder.java) checks that feature against the shared license state when parsing the retriever.

Do not infer feature entitlement from source-code availability or the top-level license choice. Check the selected distribution/version and active license separately; trial and hosted-plan entitlements need their own evidence. This settles the pinned implementation's gate, without inventing a subscription price or assuming a Cloud plan matches it.

### GraphRAG derived-data authorization

R29 — GraphRAG v3.3.0, commit `5faaaf4f5685fa2056fa8c3bf9342cb089f2942f`, [global search implementation](https://github.com/microsoft/graphrag/blob/5faaaf4f5685fa2056fa8c3bf9342cb089f2942f/packages/graphrag/graphrag/query/structured_search/global_search/search.py), inspected 2026-10-18. Its search entry point receives a query and conversation history, builds context through the supplied context builder, and maps over community summaries before reduction. This inspected path does not itself establish an authenticated caller-to-document ACL check. This is a scoped observation, not proof that every GraphRAG integration lacks authorization.

Proposed integration requirement: restrict derived entities, relationships and community reports as well as source chunks before any model call. Filtering citations after generation cannot remove information already summarized across private documents. Use separately authorized graph artifacts or a reviewed context builder with permission propagation; until that implementation and leakage tests exist, shared mixed-permission graph retrieval remains authorization-unknown. #16 owns the integration decision with #13/#35; this note performs no #65 experiment.

### Hosted filters and trusted authorization

R30 — AWS [knowledge-base service-role permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html), mutable guide accessed 2026-10-18. AWS states that ingestion uses the role bound to the knowledge base; a data-source manager can ingest locations that role can read and query them without holding S3 permissions. Restricting the service role and privileged ingestion actions is therefore separate from authorizing an application's end user. R12's request metadata filters and implicit model-generated filters establish selection mechanisms, not caller identity or source ACL inheritance.

R31 — OpenAI [file-search guide](https://developers.openai.com/api/docs/guides/tools-file-search), Responses API, mutable guide accessed 2026-10-18. The application supplies `vector_store_ids` and optional file-attribute `filters`. The demonstrated category filter is a search predicate; it is not evidence of an authenticated user-to-file permission check.

Proposed policy for both services: the trusted application authenticates the caller, authorizes the requested store/knowledge base and operation, derives mandatory ACL scope from trusted metadata, and intersects optional user search constraints with it. Do not let user input or model-generated filters replace mandatory scope. Missing ACL metadata, an untrusted filter, an unauthorized store, or stale permission state must block protected retrieval pending review. Validate revocation and mixed-permission cases before claiming P2 enforcement. A service credential's ability to retrieve data does not by itself authorize the end user. This is an engineering policy proposal; deployed security remains unverified and receiving-owner decisions remain pending.
