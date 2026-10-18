# T3: Vector Database

Issue: #15 · Assignees: @zabyxc01, @appletechie · Status: partial decision record for review · Access date: 2026-10-18

## User decision and candidate set

Decide whether retrieval needs a vector index, then choose its representation, access boundary and operations. This is source-checked desk research; no database was deployed and no throughput, recall, latency or tenant isolation was measured.

| Candidate | Index/representation facts | Deployment and operating boundary | Unknowns before catalog intake |
| --- | --- | --- | --- |
| PostgreSQL + pgvector | Exact and approximate search; HNSW and IVFFlat. Documented HNSW `vector` ceiling 2,000 dimensions, `halfvec` 4,000; these are index/type-specific, not universal storage limits [V1] | Self-operated PostgreSQL or a separately evidenced hosted offering; SQL policies and index tuning are separate concerns | Extension pinned below to v0.8.7; PostgreSQL version/operator class, provider meters/region and operational sizing still required |
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
| VDB-02 | Any protected read, or any write/delete/administrative operation, on a selected store: bind the authenticated principal to the trusted resource/namespace/row/payload scope **and** require that principal's permission for the requested action on that resource | `error` / `block` | Authorized principal, scope and action pass; a reader attempting delete fails even in the correct tenant; caller-controlled unvalidated tenant key fails; missing scope/action-policy evidence is unknown. Public anonymous read-only retrieval with no confidentiality requirement is skipped, but public-store mutations/administration still evaluate. Enforce action authorization as well as data scoping; indexing alone grants neither |
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

@zabyxc01/@appletechie retain candidate/ACL decisions. Before completion, pin actual product releases/offerings, obtain complete dimension/index/filter and license/price evidence, and record consumer acceptance. The pgvector software CatalogItem below contains only sourced required fields and scoped license facts; no Pricebook is invented. This bounded draft does not replace or claim completion of the active #65 interoperability validation.

## Pinned pgvector software proposal (2026-10-18)

[Catalog proposal](../../catalog/proposals/t3-vector-database-pgvector.json): `vector_database.pgvector`, version `0.8.7`. The publisher tag resolves to commit `f37c13f68b57d2c3472b2214fbcff699d6d34876`. This is the self-operated extension, not a hosting offering. Sources below were retrieved from that commit on 2026-10-18; claims are published and source checked, not runtime measurements.

| Field | Pinned evidence and scope |
| --- | --- |
| Runtime dependency | PostgreSQL 13+ in the pinned README; actual deployment PostgreSQL version remains a separate choice |
| Canonical metrics | Euclidean, dot, cosine map to documented L2, inner product and cosine distance. SQL `<#>` returns **negative** inner product for ascending index scans, so a raw distance must not be presented as similarity without conversion |
| Index admission | HNSW and IVFFlat `vector` indexes support up to 2,000 dimensions, `halfvec` up to 4,000. Storage of a `vector` value allows up to 16,000 dimensions; that does not grant ANN index support at that width |
| Filters and recall | Approximate-index filtering occurs after scanning and may return fewer matches; iterative scanning/configuration requires workload evaluation. This is not an ACL assurance |
| License/billing scope | PostgreSQL license permits software use/modification/distribution without fee subject to required notices/disclaimers. `free` describes the extension software, not compute, database hosting, storage, backup or operational charges |

- [Pinned README](https://github.com/pgvector/pgvector/blob/f37c13f68b57d2c3472b2214fbcff699d6d34876/README.md)
- [Pinned license](https://github.com/pgvector/pgvector/blob/f37c13f68b57d2c3472b2214fbcff699d6d34876/LICENSE)
- [Publisher release tag](https://github.com/pgvector/pgvector/tree/v0.8.7)

The v1 proposal intentionally omits optional `max_dimensions`, `supports_acl`, `supports_hybrid_search`, `regions` and `hosting_ref`: a single product-wide dimensional ceiling loses the distinction above; the remaining properties require deployment/configuration evidence. The three canonical metrics are supported members, not a claim that other publisher metrics do not exist. No pricebook or hosting reference is fabricated. #40 owns richer index/type bounds, #14/#16 consume scoring/index semantics, #9 owns the actual database deployment, #35 owns trusted access enforcement and #39 owns operational cost. Their dispositions remain pending; this proposal does not complete #15.

## Pinned Qdrant and Chroma software candidates (2026-10-18)

The following are source-checked self-operated releases, not cloud offerings or measured deployments. Their required v1 metric fields are supported, so the [Qdrant](../../catalog/proposals/t3-vector-database-qdrant.json) and [Chroma](../../catalog/proposals/t3-vector-database-chroma.json) proposals no longer depend on mutable documentation alone. Optional deployment-wide fields remain omitted rather than guessed. Both pinned LICENSE files declare Apache-2.0; `free` describes software licensing, not operational cost or hosted-service prices.

| Candidate / revision | Sourced facts and decision consequence |
| --- | --- |
| Qdrant 1.19.2 / `016542aa5deb6c66380bb137badf73d54f742bde` | `Distance` supports Cosine, Euclid, Dot and Manhattan. `VectorParams.size` validates 1–65,536 for dense-vector configuration; this is not a universal sparse/multivector bound or evidence of practical capacity. Each named vector's configured width must still match its encoder |
| Qdrant access model at that revision | Collection roles distinguish read, read/write and point read/write access. The legacy `payload` constraint is deprecated and its validator rejects supplied values. Do not copy older payload-constrained credential examples as a current authorization guarantee. VDB-02 still requires trusted resource scope and action permission for the actual runtime |
| Chroma 1.5.9 / `11f3c7435e71024aa0a2b53710a28d3289d922d1` | The pinned code maps `l2`, `cosine`, `ip` to metric families. Its scalar L2 path returns squared Euclidean distance; IP returns `1 - dot`. These monotone score transforms do not give cross-store scores shared units. Retain transform and normalization in the retrieval contract before applying thresholds |
| Chroma configuration at that revision | HNSW and SPANN settings are alternatives; the parser rejects supplying both. A configuration type does not establish a hosted plan's availability, tenant enforcement or universal dimensional ceiling |

Pinned sources, all read 2026-10-18:

- Qdrant [release](https://github.com/qdrant/qdrant/releases/tag/v1.19.2), [distance types](https://github.com/qdrant/qdrant/blob/016542aa5deb6c66380bb137badf73d54f742bde/lib/segment/src/types.rs), [vector parameters](https://github.com/qdrant/qdrant/blob/016542aa5deb6c66380bb137badf73d54f742bde/lib/collection/src/operations/types.rs), [access-role definitions](https://github.com/qdrant/qdrant/blob/016542aa5deb6c66380bb137badf73d54f742bde/lib/storage/src/rbac/mod.rs), [license](https://github.com/qdrant/qdrant/blob/016542aa5deb6c66380bb137badf73d54f742bde/LICENSE).
- Chroma [release](https://github.com/chroma-core/chroma/releases/tag/1.5.9), [distance implementation](https://github.com/chroma-core/chroma/blob/11f3c7435e71024aa0a2b53710a28d3289d922d1/rust/distance/src/types.rs), [collection configuration](https://github.com/chroma-core/chroma/blob/11f3c7435e71024aa0a2b53710a28d3289d922d1/chromadb/api/collection_configuration.py), [license](https://github.com/chroma-core/chroma/blob/11f3c7435e71024aa0a2b53710a28d3289d922d1/LICENSE).

No runtime assertion is promoted to independently verified. #14/#16 receive the dimension and score-transform constraints; #35 receives the release-specific access warning; #9/#39 retain hosted offering, region, recovery and operational meters. These are bounded evidence additions; the owners' receiving dispositions remain outstanding.


## Hosted scaling and pricing-unit comparison (2026-10-18)

Primary publisher documentation, source checked on 2026-10-18. These are offering-specific operating models and meters, not measured capacity or normalized prices. Cloud offering documentation is mutable; it is separate from the pinned open-source releases above.

| Offering | Published scaling model | Pricing units and cost boundary |
| --- | --- | --- |
| Pinecone serverless | Provider-managed serverless indexes; storage and compute are separated. Dedicated read nodes are a distinct capacity choice [V7] | Read units (RU), write units (WU), GB of index storage per month, and GB returned on in-scope reads. Imports, backup/restore, embedding and reranking are separately metered [V8]. RU is not universally one query: namespace size affects query units. Plan minimums/allowances and dedicated-read-node rules must be selected before calculating cost |
| Qdrant Cloud Standard | Dedicated cluster resources with vertical and horizontal scaling [V9] | CPU, memory and disk resource usage; billed monthly for previous usage [V10]. Exact rate and resource/time granularity require the chosen cluster/cloud/region calculator quote; no per-query meter is inferred. Free-tier topology is not the Standard production topology |
| Chroma Cloud Starter/Team | Publisher describes the cloud service as serverless; usage grows with operations/data [V11] | GiB written, GiB stored per month, TiB queried, GiB returned, plus the selected plan's monthly base fee/credits. Enterprise dedicated/single-tenant and BYOC offerings require separate terms. Customer-set or service-set usage limits can pause service; serverless does not mean unlimited throughput |
| PostgreSQL + pgvector, self-operated | Capacity is the selected PostgreSQL host/storage/replication configuration | Extension software rights do not price hosting, storage, backup, replicas or operations. No specific managed PostgreSQL offering is selected here, so inventing a hosted rate would conflate software and service |

- V7 — Pinecone [architecture](https://docs.pinecone.io/guides/core-concepts/architecture).
- V8 — Pinecone [cost model](https://docs.pinecone.io/guides/manage-cost/understanding-cost).
- V9 — Qdrant [Cloud pricing/offering comparison](https://qdrant.tech/pricing/).
- V10 — Qdrant [billing and payments](https://qdrant.tech/documentation/cloud-pricing-payments/).
- V11 — Chroma [pricing and plan conditions](https://www.trychroma.com/pricing).

No vector-service rate is normalized here: region/currency/rate selection remains explicit before a #39 Pricebook. Keep publisher GB, GiB and TiB units distinct; do not equate a read unit with a returned byte, an embedding token or a reserved CPU. A provider-operated serverless offering and a provider-operated dedicated cluster have different capacity commitments under T0; API transport alone does not classify deployment mode. Benchmark the selected plan/configuration before claiming recall, latency or sustainable throughput. #9/#39 receive this operational/meter comparison; receiving dispositions remain pending.
