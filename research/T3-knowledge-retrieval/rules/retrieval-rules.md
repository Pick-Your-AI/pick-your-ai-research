# Retrieval rule proposals

Issue: #16 · Contract review: #40 · Status: proposed

Evidence IDs refer to [rag-retrieval.md](../rag-retrieval.md). These proposals are not an approved Ruleset. `pass`/`fail`/`unknown`/`skipped` are outcomes; `info`/`warning`/`error` are severities and are fixed per rule. An unknown outcome never counts as a pass. Every rule is `skipped` when no enabled `rag_pipeline` selection exists. The examples are synthetic.

Evidence basis per rule: **source checked** means the mechanism in the assertion is documented in a cited primary source. **Hypothesis** means it is project reasoning awaiting #36 or #40 evidence.

## RAG-01: retrieved upper bound fits the input budget

- Participating kinds, roles, and JSON pointers: `rag_pipeline` primary `/settings/max_chunks` (M); `knowledge_base` primary `/settings/chunk_size_tokens` (S); `context_policy` primary `/settings/requested_context_tokens` (P). Tokenizer identity for S is a research operand pending #40 (gap G5).
- Applicability condition: enabled `rag_pipeline` with a `context_policy` selection.
- Assertion and source evidence: M × S + H ≤ P. H is the per-chunk citation/header overhead × M, and is 0 only if it has been measured as 0. This is necessary, not sufficient. CTX-01 (#7) on the complete assembled input remains authoritative. Basis: arithmetic on #7's definition of P, which includes retrieved text. Source checked against [context-window.md](../../T1-model-selection/context-window.md).
- Severity: `error`.
- Missing-data behaviour: M, S or P absent → `unknown`, `on_unknown: block`. If S was counted with a tokenizer other than the generation model's, the outcome is `unknown` (`review`) until recounted.
- Explanation and remediation: report M, S, H and P. Lower `max_chunks` or chunk size, or raise P after CTX-01 passes. Do not truncate silently.
- Dependency edges and affected consumers: #13 chunking, #14 tokenizer, #7 fit, #39 token cost, #28 memory budget.
- Passing example: M=5, S=400, H=5×20, P=8,000 → 2,100 ≤ 8,000.
- Failing example: M=20, S=512, H=0 (measured), P=8,000 → 10,240 > 8,000.
- Unknown / non-applicable: S counted with the embedding tokenizer only → unknown. No `rag_pipeline` selection → skipped.
- Version and migration impact: needs a tokenizer-identity operand and an H operand. The existing v1 fields are unchanged.

## RAG-02: caller authorization precedes model and tool exposure

- Participating kinds, roles, and JSON pointers: `knowledge_base` `/spec/supports_acl`, `/settings/acl_enforced`; build `/objectives/data_classification`; proposed `rag_pipeline` enforcement point E ∈ {`source_native`, `index_prefilter`, `engine_postfilter`, `app_postfilter`, `none`} (G5). Authenticated caller, requested resource/action, mandatory authorized scope and ACL/revocation revision are conceptual evidence operands pending #40; no frozen-v1 boolean proves them.
- Applicability condition: knowledge base with ACL-bearing sources, or classification `restricted`/`confidential`. This extends baseline `rule.knowledge.restricted.acl`, which checks enforcement exists but not where it happens.
- Assertion: the trusted application binds the authenticated caller to the selected store and requested read action, derives mandatory scope from current authorized metadata, and intersects optional user/model search constraints with that scope. E must apply that scope to every returned chunk and permission-bearing derived artifact before any reranker/model call, agent tool response, or exposure outside the authorized enforcement boundary. Scope cannot be replaced by a caller-supplied tenant key or model-generated filter. `none`, a known unauthorized resource/action, a known stale permission state, or post-generation trimming fails. A stage enum plus projected group IDs alone cannot pass.
- Source evidence and policy basis: R11 documents token enforcement and chunk projection; R01/R08 filtering; R07 row security; R01/R09 read-only DLS scope. R30 distinguishes the Bedrock ingestion service role from an end user's source permission; R31 demonstrates caller-supplied file-search selection filters. R29's graph context includes derived community summaries. The mandatory binding, derived-data coverage and earliest-exposure requirements are project policy proposals inferred from those boundaries, not publisher guarantees or measured enforcement. Ranking `app_postfilter` as acceptable but weakest remains a hypothesis and only applies when the entire pre-filter path stays inside the authorized boundary.
- Severity: `error`.
- Missing-data behaviour: missing evidence for caller/resource/action binding, mandatory scope, enforcement stage, permission revision, or chunk/derived-artifact propagation → `unknown`, `on_unknown: block`.
- Explanation and remediation: name the first stage where unauthorized data could leave the enforcement boundary, including reranking, tool results, caches, traces and graph summaries. Authenticate and authorize the request, enforce mandatory scope at P1/P2 where possible, propagate permissions through derived data, and test revocation before making an enforcement claim (#13/#35/#36).
- Dependency edges and affected consumers: #13, #15 (filter and action authorization), #25 (retrieval tool boundary), #35 guardrails, #36 leakage tests, #28.
- Passing example: authenticated principal A may read store S; the trusted adapter intersects A's current authorized document scope with optional query filters, and the index applies it to every chunk before any reranker or tool result. Evidence binds this path and its ACL revision to the selected configuration.
- Failing examples: E=`index_prefilter` but the request chooses another tenant's unvalidated group ID; a user without read access selects a service-readable store; private candidates reach an external reranker before P4 trims them; or E=`none` relies on a model instruction to "ignore restricted documents".
- Unknown / non-applicable: a framework retriever with undocumented principal binding or derived-summary permissions → unknown even if filtering is advertised. A public-only corpus with no ACLs → skipped for this protected-read rule; writes, deletes and administration still require separate action authorization under VDB-02/#35.
- Version and migration impact: the stage, binding and revision operands require versioned representation and fixtures through #40. ACL sync lag remains a separate monitoring concern for #13, but known stale or unproven permission state cannot make this protected-read rule pass.

## RAG-03: a reranker is identified and its input limit is respected

- Participating kinds, roles, and JSON pointers: `rag_pipeline` `/settings/rerank_enabled`, `/spec/supports_rerank`. Reranker identity and input limit L have no v1 operand (G4).
- Applicability condition: `rerank_enabled=true`.
- Assertion and source evidence: `supports_rerank=true`, a reranker is identified, and S plus query tokens ≤ L. Source checked: cross-encoders take question and document together, and the BGE example truncates at `max_length=512` (R24). Cohere limits are not on the overview page (R23).
- Severity: `warning`. Over-limit input is truncated and loses content (hypothesis).
- Missing-data behaviour: missing L or reranker identity → `unknown`, `on_unknown: review`.
- Explanation and remediation: show the truncated share. Use smaller chunks or a reranker with a larger evidenced limit.
- Dependency edges and affected consumers: #14 (separate model selection), #11 serving, #39 cost.
- Passing example: S=300, query 30 tokens, L=512.
- Failing example: S=1,024, L=512.
- Unknown / non-applicable: an API reranker with an undocumented limit → unknown. `rerank_enabled=false` → skipped.
- Version and migration impact: needs a reranker reference (a `model` role or a new kind) via #40.

## RAG-04: requested hybrid mode is honoured by the backend

- Participating kinds, roles, and JSON pointers: `rag_pipeline` `/spec/retrieval_mode`; backend store identity (`vector_database` or managed service).
- Applicability condition: `retrieval_mode=hybrid`.
- Assertion and source evidence: the selected backend documents hybrid support for this store configuration. Source checked: Bedrock falls back to semantic search unless the store is RDS, OpenSearch Serverless or MongoDB with a filterable text field (R12). Azure, Elasticsearch and Haystack document hybrid paths (R10, R01, R18).
- Severity: `warning`.
- Missing-data behaviour: backend support undocumented → `unknown`, `on_unknown: review`.
- Explanation and remediation: report the actual mode that will run. Change the store or the mode.
- Dependency edges and affected consumers: #15, #65 interoperability tests.
- Passing example: Bedrock KB on OpenSearch Serverless with a filterable text field, HYBRID requested.
- Failing example: Bedrock KB on a store outside the documented list, HYBRID requested.
- Unknown / non-applicable: an unlisted framework integration → unknown. Mode `keyword` → skipped.
- Version and migration impact: needs a backend-capability operand; `vector_database` `/spec/supports_hybrid_search` partly covers it.

## RAG-05: filtered approximate search can return fewer than k results

- Participating kinds, roles, and JSON pointers: `rag_pipeline` `/settings/top_k`; proposed E (RAG-02); backend filter strategy.
- Applicability condition: dense or hybrid retrieval with metadata or ACL filters.
- Assertion and source evidence: the filter is applied during the search (pre-filter or efficient filtering), or iterative/expanded scanning is enabled. Otherwise the outcome is `fail`. Source checked: R01, R05 (iterative scans since pgvector 0.8.0), R08, R15.
- Severity: `warning`. Correctness is unaffected; recall drops for restricted users.
- Missing-data behaviour: filter strategy undocumented → `unknown`, `on_unknown: review`.
- Explanation and remediation: report the possible shortfall. Use the kNN `filter`, efficient filtering or iterative scans, or partition per tenant (R05).
- Dependency edges and affected consumers: #15, #36 (shortfall metric).
- Passing example: Elasticsearch kNN with an ACL `filter` inside the kNN clause.
- Failing example: an ACL filter outside the kNN clause, k=10.
- Unknown / non-applicable: no filters → skipped.
- Version and migration impact: needs a filter-strategy operand.

## RAG-06: citations are required but unsupported

- Participating kinds, roles, and JSON pointers: a workload/build citation requirement (no v1 field); proposed citation level C ∈ {`none`, `document_id`, `span`, `page`} (G5).
- Applicability condition: the user requires source attribution.
- Assertion and source evidence: C ≠ `none`, and C meets the required level. Source checked: R19, R25, R12. Pointer validity (R25) is not evidence of support; that is measured by #36.
- Severity: `warning`.
- Missing-data behaviour: C unknown → `unknown`, `on_unknown: review`.
- Explanation and remediation: pick a pipeline or API that returns source pointers, and preserve chunk identity through context assembly.
- Dependency edges and affected consumers: #36, #25 (agent output), builder display.
- Passing example: required `document_id`; the API returns `file_citation` with `file_id`.
- Failing example: required `span`; the pipeline returns only answer text.
- Unknown / non-applicable: no citation requirement → skipped.
- Version and migration impact: new workload and pipeline operands via #40.
