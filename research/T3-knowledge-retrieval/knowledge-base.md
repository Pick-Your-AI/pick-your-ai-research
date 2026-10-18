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

## Source-specific connector comparison (2026-10-18)

This bounded comparison selects **Azure Blob → Azure AI Search indexer** and **S3 → Amazon Bedrock Knowledge Bases** for document ingestion. It does not claim coverage of every connector, Foundry knowledge-source workflow, or the separate Bedrock Managed Knowledge Base offering. Application-owned ingestion remains the self-operated candidate above. API transport does not determine T0 capacity mode. These are published capabilities, source checked on 2026-10-18, not exercised integrations, measured freshness or authorization tests. The source pages are mutable; the cited API/preview labels describe the documented surface, not a pinned deployed service build.

| Dimension | Azure Blob indexer | Amazon S3 data source |
| --- | --- | --- |
| API/configuration identity | `azureblob` data source, container and optional virtual folder; index/indexer examples use `api-version=2026-04-01` [K4] | `CreateDataSource`, `dataSourceConfiguration.type=S3`, bucket ARN/owner and optional inclusion prefixes; `vectorIngestionConfiguration` describes ingestion [K5, K10]. AWS reference is a dated documentation observation, not a claimed immutable API release |
| Ingestion authentication | Managed identity with Storage Blob Data Reader; also account-key or SAS connection strings. SAS needs read/list and renewal [K4]. Credentials are not saved-build evidence | KB-bound IAM service role needs scoped S3 list/get permissions, plus applicable KMS decryption; data-source management uses that existing role [K6]. No credentials requested or provisioned |
| Document format scope | Selected published text-extraction formats: PDF, DOC/DOCX, TXT, HTML, Markdown, CSV and JSON; not an exhaustive list. Tier extraction limits still apply [K4] | Published document list: UTF-8 TXT/MD/HTML, DOC/DOCX, CSV, XLS/XLSX, PDF; document quota 50 MB [K7]. This row excludes audio/video/image workflows rather than assuming document limits apply to them |
| Parser/chunk configuration | Text extraction and skillsets/vectorization are separate configuration; metadata fields must exist in the index or their extracted values are discarded [K4] | Default parser extracts text; advanced Data Automation/model parsers handle richer content and can incur separate charges [K8]. Fixed-size token/overlap, hierarchical, semantic or no-chunking choices need explicit configuration [K9] |
| Metadata identity | Define source path/key and required source/permission fields in the index; a searchable source URL does not establish viewer access [K4; project requirement] | Same-location `filename.extension.metadata.json`, at most 10 KB; attributes can be included in embeddings or retained only for filtering [K5]. Preserve source revision and selected representation as project lineage requirements |
| Change processing | New/updated content uses storage timestamps; scheduled or on-demand runs [K4]. Deletion needs a separately configured policy [K2] | Invoke sync after changes; incremental processing updates changed content and removes deleted documents from the vector store [K3]. A completed job is not a universal immediate-query-visibility guarantee |
| Deletion scope | Configure deletion detection before the first run. Native soft-delete requires blob versioning disabled and processing within retention; one-to-many scenarios need explicit index deletion requests [K2] | Ordinary source-document deletion during sync is separate from resource deletion. `dataDeletionPolicy=DELETE/RETAIN` controls embeddings when deleting the KB/data-source resource; it does not delete the vector-store resource [K10] |
| Retrieval authorization | Ordinary read credentials prove ingestion access only. Optional RBAC inheritance is a separate preview path with caller permission checks [K11] | AWS warns that ingested content is retrievable by principals with `bedrock:Retrieve`, including originally access-controlled source content [K5]. Source ACL preservation must not be inferred |

### Permission and lifecycle implications

**Azure preview boundary [K11].** The RBAC-scope ingestion page identifies indexer support from `2025-05-01-preview`; its current examples use `2026-08-01-preview`. It requires managed-identity configuration, permission metadata/index fields and query-time caller identity through `x-ms-query-source-authorization`. Container RBAC inheritance is not Azure ABAC support. For indexer-based ingestion the page requires default parsing mode and `indexerPermissionOptions` containing `rbacScope`. This capability cannot be generalized to arbitrary parsers, legacy API versions or skill pipelines. KB-01 remains unknown for an unexamined configuration; a metadata field alone is not enforcement.

**Bedrock role boundary [K6].** AWS says `CreateDataSource`, `UpdateDataSource` and `StartIngestionJob` do not pass a role for an `iam:PassRole` check: ingestion uses the role already associated with the KB. Someone managing sources can ingest locations that role can read without separately holding S3 permissions. Therefore the proposed acceptance check must examine data-source administration, role bucket/prefix scope and retrieval access together. An inclusion prefix is not a replacement for IAM scope. K5 also requires the S3 bucket and KB to share a Region and limits this connector to general-purpose buckets.

**Chunk and sync boundary [K9, K10, K3].** The API disallows changing `chunkingConfiguration` after creating the connector. No-chunking treats a document as one chunk and loses page-number citations/filtering. These text strategies do not define multimodal chunking. Metadata-only resync avoids embedding calls only under documented conditions: content unchanged, non-CSV content and no custom transformation Lambda. CSV metadata changes require re-ingestion. Record that condition when estimating #39 re-embedding costs; do not assume every metadata update is free or every update re-embeds.

**Project acceptance examples (synthetic, not product tests):**

| Scenario | Proposed interpretation under existing KB rules |
| --- | --- |
| Successful ingestion with no demonstrated caller-specific enforcement | KB-01 unknown; a successful job proves no source ACL mapping |
| Bedrock callers known to retrieve protected content outside their source permissions | KB-01 fail; add an authorized retrieval boundary or separate appropriately scoped resources |
| Azure one-to-many derived records with only a blob soft-delete assumption | KB-02 unknown until explicit deletion coverage is evidenced; a known surviving serving chunk fails |
| Metadata field omitted from Azure index schema | Required lineage/permission evidence is missing; no empty/public default |
| Unchanged non-CSV content, metadata-only update, no custom Lambda | Eligible for K3's documented optimization; actual billed work still needs observation/price scope |

### Additional claim sources

All links below were opened and read on **2026-10-18**. Evidence grade: primary documentation, **source checked / unverified**, not independent runtime evidence. Numeric limits are publisher values with the scopes above. Sources are paraphrased; neither documentation access nor connector authentication grants commercial source-data reuse, training rights or redistribution. #32/#60 retain those decisions.

- K4 — Microsoft, [Blob indexer](https://learn.microsoft.com/en-us/azure/search/search-how-to-index-azure-blob-storage): basic connector/auth/format/metadata behavior; REST examples `2026-04-01`.
- K5 — AWS, [S3 connector](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html): bucket/prefix/region constraints, metadata sidecars and retrieval-permission warning; mutable user guide.
- K6 — AWS, [KB service role](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html): S3/KMS access and data-source administration boundary; mutable user guide.
- K7 — AWS, [Document prerequisites](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html): document format list and 50 MB quota; multimodal limits are separate.
- K8 — AWS, [Parsing options](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html): text-only default and advanced parser distinction. No rate or total-cost claim supplied.
- K9 — AWS, [Chunking](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html): strategy and citation boundaries; chosen tokenizer/runtime compatibility remains #14/#16 evidence.
- K10 — AWS, [CreateDataSource API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_CreateDataSource.html): configuration immutability and resource-deletion policy; build-time endpoint `PUT /knowledgebases/{knowledgeBaseId}/datasources/`.
- K11 — Microsoft, [Blob RBAC scope ingestion](https://learn.microsoft.com/en-us/azure/search/search-blob-indexer-role-based-access): preview configuration and query permission boundary; preview and ordinary-indexer capabilities kept distinct.

The original K2/K3 links above supply the detailed deletion/sync conditions. No API request, customer content, infrastructure allocation or #65 experiment was performed. Remaining evidence is configuration-specific parser/chunker fidelity, revocation/deletion propagation and actual lag, plus selected region/terms/cost. #13 owners retain connector scope; #14 receives tokenization, #15 source-to-index deletion identity, #16/#35 trusted retrieval enforcement, #28 downstream memory lineage and #32 separate reuse rights. Those receiving dispositions remain outstanding.

## Synthetic deletion-lineage examples for KB-02

The [test-only projection](../../tests/kb_deletion_prototype.py) and
[regression cases](../../tests/test_kb_deletion.py) make KB-02's proposed
pass/fail/unknown/skipped boundary executable over synthetic normalized receipts.
They do not implement ingestion, deletion, graph discovery or a contract reader.
No actual connector, credential or customer content is involved.

A receipt represents one source-to-derived-destination edge with an unambiguous
identity and an observation bound to the selected deletion/revocation event.
Source revision, tenant, event identity, trustworthy observation and scope
completeness must already have been established by the caller. These tests do
not establish them. Duplicate/missing edge identities are ambiguous rather than
silently merged. Unknown event applicability is unknown; only an explicitly
inapplicable event skips the rule. Severity remains fixed at error.

- A known current stale serving copy fails even if unrelated destinations or
  full lineage coverage remain unknown.
- Incomplete lineage, an untracked memory copy, an unknown destination state or
  a receipt for an older/unbound event cannot establish a pass.
- Complete scope with every current destination tombstoned or excluded from
  serving passes this proposed serving predicate. A separately governed backup
  may remain retained only when its current non-serving classification is
  established; this is not an erasure, retention-policy or legal-compliance pass.
- An empty derived scope passes only with positive completeness evidence, not
  merely an empty list. The test assumes that evidence, rather than measuring it.

These examples illustrate existing KB-02 requirements; they add no publisher
capability claim or frozen-v1 field. Real revocation/deletion propagation, scope
completeness and receiving decisions from #15/#16/#28/#35 remain outstanding;
#40 retains final rule/identity encoding and adoption.
