# T3: Knowledge Base

Issue: #13 · Assignees: @tynamite, @zabyxc01 · Status: partial decision record for review · Access date: 2026-10-18

## User decision and scope

Choose which user sources may supply knowledge, and how their content, permissions and deletion state reach retrieval. Catalog collection is #41; action credentials are #26/#27; training permission is #32. This note proposes requirements, not an exercised connector or permission grant.

## Candidate options

| Candidate | Source and storage taxonomy | Sync and transformation | Boundary |
| --- | --- | --- | --- |
| Application-owned ingestion | Files, object storage, database snapshots/change feeds, wiki/SaaS exports; immutable source revisions plus derived chunk/index records (proposal) | Explicit parser/chunker version, checkpoint and tombstone processing | Self-operated path; connector-specific auth, formats and deletion support remain evidence requirements |
| Azure AI Search indexers | Publisher-documented data-source/indexer/index split [K1] | One source per indexer; multiple indexers may populate an index; skillsets can chunk/vectorize [K1] | Do not infer document ACL propagation from successful ingestion |
| Amazon Bedrock Knowledge Bases | Source ingestion with parsing, chunking, embedding and a vector-store destination [K3] | Incremental synchronization handles added/changed/deleted documents [K3] | A successful sync is not proof that unrelated agent memory, backups or application caches were erased |

Classify each serving component by operator/capacity using [T0's mode definition](../T0-configuration/deployment-mode.md). An API interface alone does not distinguish shared API capacity from dedicated managed capacity. Application-owned processing can be self-hosted; cloud service capacity/region needs an offering-specific record.

## Comparison fields

All fields below are proposed research fields; no additions to frozen v1 are implied. Missing evidence is `unknown`, never an empty supported set.

| Field | Type/unit | Evidence required |
| --- | --- | --- |
| source identity/type/revision | strings; file, object, relational, wiki, SaaS | Connector documentation and exact source revision/checkpoint |
| auth and credential binding | method enum + opaque reference, never secret | Authorized principal, scopes, connector version; authentication does not prove content-use permission |
| supported formats | set with completeness flag | Parser version, MIME types and OCR limitations; undocumented format is unknown |
| sync mode/freshness | full, incremental, event; timestamp and seconds | Trigger, watermark, retry/idempotency and observed lag; no invented freshness SLA |
| chunking | parser/chunker revision, tokenizer, integer token budget and overlap | Exact configuration and #14 input limits; no universal chunk size |
| metadata | source ID, revision, chunk ID, tenant, permission version, derivation edges | Identity stability across updates and re-chunking |
| ACL support | predicate specification and enforcement location | Source-to-principal mapping, revocation and query enforcement tests |
| deletion support | tombstone, acknowledgement, remaining destinations | Source→chunks→embeddings/index→cache/memory lineage and retention exceptions |
| storage | backend ID/version, region, operator, encryption reference | #9 offering evidence; each derived destination separately |

## Compatibility proposals for #40

These are hypotheses with fixed severities, not approved executable rules. Paths below are conceptual next-version operands, not existing v1 JSON pointers. Participants: `data_source`, `knowledge_base`, linked `embedding_model`, `vector_database`, `rag_pipeline`, and `memory_store`.

| ID | Applicability and assertion | Severity / unknown policy | Synthetic cases and remediation |
| --- | --- | --- | --- |
| KB-01 | When protected source content is retrieved, the authenticated requester must satisfy the source-derived access predicate before content is returned to the model | `error` / `block`; missing mapping or enforcement evidence → `unknown` | Allowed user with enforced mapping → pass; known unrestricted retrieval → fail; missing evidence → unknown; public source with no protection requirement → skipped. Implement trusted enforcement, not a caller-supplied tenant string |
| KB-02 | When a source is deleted/revoked, all active derived serving copies must be tombstoned or excluded before serving; acknowledgements cover each lineage edge | `error` / `block` | All active destinations acknowledged → pass; known stale serving chunk → fail; untracked memory copy → unknown; no deletion event → skipped. Reconcile lineage and record separately governed backups |
| KB-03 | When embedding ingestion is selected, each complete chunk including instructions/special tokens fits the selected tokenizer/input policy | `error` / `review` | In-budget chunk → pass; known over-limit chunk without allowed split → fail; unknown tokenizer → unknown; lexical-only pipeline → skipped. Re-chunk; do not silently truncate |
| KB-04 | When training reuse is requested, retrieval authorization alone must not be treated as training permission; require the separate #32 disposition | `error` / `review` | Explicit applicable permission → pass; explicit prohibition → fail; missing scope → unknown; no training reuse → skipped |

K2 supplies a concrete reason to require deletion configuration: Azure Storage change detection does not imply deletion detection. Its soft-delete policy must be configured from the first indexing run; one-to-many indexing requires explicit index deletion requests. The proposed lineage requirement generalizes this concern; it has not been reproduced here.

## Evidence

All sources below were read 2026-10-18, are mutable publisher documentation and are **source checked, not independently verified**. No prices, runtime measurements or commercial rights decisions are established.

- K1 — Microsoft, [Indexer overview](https://learn.microsoft.com/en-us/azure/search/search-indexer-overview): source/indexer/index relationship and transformation support; account-specific connector support untested.
- K2 — Microsoft, [Changed and deleted Azure Storage content](https://learn.microsoft.com/en-us/azure/search/search-how-to-index-azure-blob-changed-deleted): deletion policy, initial-run and one-to-many limitations; scoped to the documented Storage indexers.
- K3 — AWS, [Knowledge Base synchronization](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html): incremental re-ingestion and deletion; metadata-only optimization is conditional, so do not charge every metadata edit as a full re-embed.

## Recommendation, handoffs and open questions

Keep source identity, credential identity, access policy and derived storage separate. Choose the simplest ingestion path that can demonstrate authorization, replayable updates and deletion propagation for the actual source. Managed ingestion reduces implementation work but does not supply evidence of every downstream control.

Receiving dispositions are pending: #14 chunk/tokenizer contract; #15 index identity/deletion; #16 trusted retrieval filtering; #28 memory derivation and deletion; #32 separate training rights; #35 enforcement. The existing [T0/#13 response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13) accepts provider-identity separation only; it does not establish T3 ACL behavior. @zabyxc01 owns the T3 source/ACL decision, @tynamite the shared identity boundary. #9 owners confirm storage/operator/region; #39 owners confirm ingestion, re-embedding and storage meters.

No CatalogItem is supplied: connector-version fields, complete format coverage, permission evidence and deletion tests remain incomplete. Acceptance is partial until source-specific candidates and receiving owners review these rules. No customer content or credentials were collected, and active #65 interoperability work is unchanged.
