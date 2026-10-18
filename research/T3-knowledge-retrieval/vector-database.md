# T3: Vector Database

Issue: #15 · Assignees: @zabyxc01, @appletechie · Status: partial decision record for review · Access date: 2026-10-18

## User decision and candidate set

Decide whether retrieval needs a vector index, then choose its representation, access boundary and operations. This is source-checked desk research; no database was deployed and no throughput, recall, latency or tenant isolation was measured.

| Candidate | Index/representation facts | Deployment and operating boundary | Unknowns before catalog intake |
| --- | --- | --- | --- |
| PostgreSQL + pgvector | Exact and approximate search; HNSW and IVFFlat. Documented HNSW `vector` ceiling 2,000 dimensions, `halfvec` 4,000; these are index/type-specific, not universal storage limits [V1] | Self-operated PostgreSQL or a separately evidenced hosted offering; SQL policies and index tuning are separate concerns | Pin extension/PostgreSQL release and operator class; provider meters/region, license and operational sizing |
| Qdrant | Each named vector can have its own dimension and metric; documented metrics include Dot, Cosine, Euclid and Manhattan [V2] | Self-operated or separately evidenced cloud offering; tenant payload filtering is distinct from storage optimization [V3] | Release-specific dimension/index limits, cloud capacity/operator, pricing and rights |
| Pinecone | Index schema supports dense/sparse fields; externally supplied vectors or integrated embedding; namespaces scope operations [V4] | Hosted offering; verify plan/capacity rather than deriving mode from API transport | Exact plan limits, metric/schema, regional rates and terms; no self-hosted offering established here |
| Chroma | Documented HNSW and SPANN configuration; l2/cosine/ip metric choices depend on configuration; cloud SPANN settings are not freely customizable [V5] | Confirm deployment/backend before applying a configuration | Release/backend dimension limits, authentication/tenancy, pricing and license |

Known capability lists are scoped to the cited page, not exhaustive compatibility matrices. No universal ranking or default store is recommended. Follow [T0 operator/capacity semantics](../T0-configuration/deployment-mode.md) for each serving component.

## When a dedicated vector database is unnecessary

Proposed #16 decision criteria: lexical-only or direct structured lookup requires no embeddings/vector store; a corpus supplied directly within an evidenced context budget may need no retrieval index; an existing database with the required vector extension may avoid a separate service. These are architecture options, not performance claims. Corpus size alone is not sufficient: test recall, filtering, authorization, update/delete behavior and latency against workload requirements before choosing a topology.

## Comparison fields and units

| Field | Type/unit | Evidence |
| --- | --- | --- |
| product/version/deployment | strings + per-component mode | Exact release, extension and offering/operator/capacity |
| dimensions | integer bound keyed by representation/index/dtype | Published index-specific limits; unknown stays unknown |
| metrics/index types | sets with completeness flag | Operator compatibility and approximation parameters |
| filtering/hybrid search | predicate and execution stage; fusion/scoring method | Versioned API behavior; connector presence is not successful retrieval |
| tenancy/ACL | namespace/row/payload boundary + trusted principal binding | Queries, writes, fetch, delete and administrative access considered separately |
| scaling/recovery | shard/replica/partition configuration, backup scope | Offering documentation and workload evidence; no inferred SLA |
| pricing unit/license | meter and dated terms URL | #39 pricebook with region/currency; #60 permission, no free-use inference |

## Proposed compatibility rules

Conceptual operands below require #40 review and versioned fields. Participants: `vector_database`, linked `embedding_model`, `rag_pipeline`, and optional `memory_store`. All rules are hypotheses; no new rule is silently inserted into v1.

| ID | Applicability / assertion | Severity / unknown policy | Synthetic cases and remediation |
| --- | --- | --- | --- |
| VDB-01 | Vector retrieval enabled: configured representation/dtype/dimensions fit the selected index's documented limits | `error` / `review` | Dense 1,024 under an evidenced 2,000 bound passes; 3,072 exceeds that bound and fails for that index/type only; missing bound unknown; lexical-only skipped. Select a compatible type/index or approved encoder reduction |
| VDB-02 | Any protected store is selected, including single-tenant stores: every data-access operation binds a trusted principal to its authorized namespace/row/payload scope | `error` / `block` | Enforced authorized scope passes; caller-controlled unvalidated tenant key fails; untested boundary unknown; public read-only retrieval without a confidentiality requirement skips this confidentiality predicate; writes/deletes/administration still require separate authorization. Add trusted enforcement for direct fetch, write, delete and administrative operations as well as retrieval; indexing alone cannot authorize |
| VDB-03 | Deletion/revocation event affects indexed content: serving queries exclude every derived record and acknowledgement covers the source-to-index mapping | `error` / `block` | All affected chunks excluded pass; known surviving visible chunk fails; missing lineage unknown; no event skipped. Reconcile with KB-02 and #28 rather than create a second deletion policy |
| VDB-04 | A quality requirement depends on ANN/hybrid retrieval: evidence uses the actual filter/index/scoring configuration and selected corpus | `warning` / `review` | Matching scoped evaluation passes; knowingly mismatched evaluation fails; no eligible evidence unknown; no quality claim skipped. Obtain #36 protocol evidence |

VDB-01 complements EMB-01: a store can admit a dimension while the configured index field still mismatches the encoder. Neither proves semantic compatibility. Proposed synthetic example: 3,072-dimensional output cannot use the cited pgvector HNSW `vector` bound; a documented compatible `halfvec` path may satisfy dimensional admission but still needs precision/quality evidence. Never silently truncate a vector.

## Security and lifecycle findings

Qdrant's `is_tenant` option optimizes storage layout; its documentation separately applies tenant filters [V3]. A shard or payload index is not an access grant. Pinecone namespace selection also needs trusted application binding [V4]. PostgreSQL row-level security is not enabled by default; table owners normally bypass it, and whole-table operations are outside its row-policy scope [V6]. These facts motivate VDB-02; none proves a deployed configuration is secure.

A vector-backed memory store should link to the existing database selection with an explicit role. Database retention does not establish #28 memory consent, scope or semantic deletion. Preserve source/chunk/representation revision identifiers so #13 can trace deletion and #14 can plan re-indexing.

## Evidence

All read 2026-10-18. Primary documentation, source checked only; mutable pages are not release-pinned runtime evidence. Numeric limits are published, not measured.

- V1 — pgvector maintainers, [README](https://github.com/pgvector/pgvector): index/type limits, operators and search options; current README install example names v0.8.7. Pin the chosen release before deployment or catalog intake.
- V2 — Qdrant, [Collections](https://qdrant.tech/documentation/manage-data/collections/): vector field dimension/metric contract.
- V3 — Qdrant, [Multitenancy](https://qdrant.tech/documentation/manage-data/multitenancy/): tenant filtering and optional `is_tenant` optimization.
- V4 — Pinecone, [Indexing overview](https://docs.pinecone.io/guides/index-data/indexing-overview): representations, integrated/external embeddings and namespace-scoped operations.
- V5 — Chroma, [Collection configuration](https://docs.trychroma.com/docs/collections/configure): backend-specific index and metric configuration.
- V6 — PostgreSQL, [Row security policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html): version 18 documentation, policy defaults and bypass boundaries.

## Recommendation, handoffs and remaining acceptance

Start with the required retrieval/access contract, then compare operational burden and measured quality. Dedicated storage is an option, not an obligatory T3 component. #16 owners decide the not-needed criteria; #14 owns representation/metric compatibility; #28 owns vector-backed memory semantics; #39 owns meters and rates; #9 owns hosting/recovery evidence; #35 owns policy enforcement. All receiving dispositions remain pending.

@zabyxc01/@appletechie retain candidate/ACL decisions. Before completion, pin actual product releases/offerings, obtain complete dimension/index/filter and license/price evidence, and record consumer acceptance. No CatalogItem or Pricebook is added with invented required fields. This bounded draft does not replace or claim completion of the active #65 interoperability validation.
