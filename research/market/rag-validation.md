# MR-09: Review RAG interoperability market claims

Issue: [#65](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65). Current desk review: **2026-10-18**. Live assignees at this read: zabyxc01, appletechie and itisSomeone. Status: **source findings prepared; independent evidence and five receiving decisions, final source review, checks and canonical delivery remain required.**

## Decision and scope

**A connector name establishes neither a configured integration nor a successful retrieval workload.** The reviewed dense BGE-M3/Qdrant path has a conditional dimensional and metric correspondence, with concrete adapter checks and remaining encoder, dependency, endpoint and authorization gaps. Bedrock's documented hybrid behavior is conditional on the selected store, and its current user guide and API type reference disagree on the eligible set. These findings answer the desk question without certifying a deployed combination, retrieval quality or privacy.

This continuation uses the issue's existing desk-review methodology and [published execution scope](../../prompts/market/issue-065.md#4-separate-connector-existence-from-workload-success). It preserves the [original writer reservation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65#issuecomment-6220176751), [#245 coordination](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65#issuecomment-6246156082) and [current continuation notice](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65#issuecomment-6250002620). The original protocol is retained verbatim at the end. No response from those writers is inferred. This is a source and receiving reconciliation; an existing contributor's possible runtime work remains separately attributable.

No model, vendor package, service, account, credential or paid API was exercised. No embedding, document index, retrieval result or customer corpus was generated. Passing the repository's synthetic fixtures is not RAG execution evidence. Retrieval component choices stay with #14–#16, agent/MCP behavior with #25/#27, and rules with #40.

## Claim inventory and evidence boundary

The [matrix at main `78cc8874`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/78cc8874b930b54fe43edfffa570dce8aaa9e2ff/research/market/features.json) contains **99 cells** for `embeddings`, `vector_db` and `rag` across 33 resources: **95 Unknown and four Documented**. All embedding-model selection and configured-vector-store cells are Unknown. The four documented RAG cells below describe narrower capabilities; none records the matrix's required observed retrieval/evaluation scenario. The matrix's original dates, grades and evidence objects are unchanged.

| Existing matrix claim | Current primary-page recheck | What remains unestablished |
| --- | --- | --- |
| Dify `rag`: document processing and retrieval connections | [Dify](https://dify.ai/) describes chunking, indexing and testing retrieval before connecting knowledge to workflows. | This marketing description does not identify a configured embedding revision, store, metric, endpoint or successful query. |
| Langflow `rag`: RAG application construction | [Langflow](https://www.langflow.org/) describes reusable flows and lists model/vector-store integrations. | A listed product or flow is not a pinned model–adapter–store tuple or proof of its authorization and workload result. |
| Ragas `rag`: evaluation support | [Ragas documentation](https://docs.ragas.io/en/stable/) lists RAG evaluation procedures and metrics. | Evaluation tooling is distinct from a retrieval builder; no fixed evaluation input/output was executed in this pass. |
| LlamaIndex `rag`: indexing/retrieval pipelines | [LlamaIndex](https://www.llamaindex.ai/) describes chunking, embedding and retrieval in its document products. | The current product description supplies no selected implementation lock or measured connector outcome here. |

These four mutable pages were read on 2026-10-18; their present descriptions are publisher claims or documentation, not retroactive observations of the 2026-10-16 matrix. Unknown cells are not absence findings. The concrete implementation comparison comes from the separately merged [#245 supplement](rag-bge-qdrant-source-comparison.md), whose seven exact primary locators were rechecked for this continuation. Its [earlier source reviews](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/245#pullrequestreview-5561648966) and signed-main contribution are preserved; those reviews did not constitute #65 receiving acceptance. The [#119 retrieval contribution](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/119) supplies the Bedrock question, not an observed fallback result.

## Pinned dense contract findings

E1–E7 refer to the exact sources in the supplement's [evidence table](rag-bge-qdrant-source-comparison.md#evidence-and-rights), individually reopened on 2026-10-18. These are source facts, with runtime verification still `unverified`.

| Boundary | Inspected identity and documentary finding | Condition retained |
| --- | --- | --- |
| Model representation | BAAI BGE-M3 revision `5617a9f61b028005a4858fdac845db406aefb181`: the card specifies 1,024-dimensional vectors and demonstrates dense dot-product scoring (E1). | Only the dense representation is selected for this comparison. Sparse/ColBERT outputs and their index contracts are separate. Actual output, normalization and adapter behavior remain unmeasured. |
| Store dimension and distance | Qdrant v1.19.2 source at `016542aa5deb6c66380bb137badf73d54f742bde`: dense `VectorParams` accepts size 1–65,536; its distance enum includes `Dot` (E2/E3). | A candidate 1,024/Dot configuration is expressible. This range is not a universal limit for sparse or multivector data, and expressibility is not successful ingestion or search. |
| Adapter identity and defaults | `langchain-qdrant` 1.1.0 tag resolves to `079eb808f8f4c08a44481c770062584ce10323b3`. The constructor defaults to dense, unnamed vector and COSINE, with validation enabled (E4–E6). | The selected dot-based comparison must explicitly request DOT and the actual vector name. This does not establish that cosine is universally unsuitable for BGE; any claimed transformation or normalization equivalence needs its own evidence. |
| Ingestion/query identity | Source uses document embeddings for inserted texts and query embeddings for search; dense search calls `query_points` with the selected vector name (E6). | Equal width does not identify the collection's original encoder or establish matching query/document instruction and normalization policy. No BGE-specific wrapper is supplied here. |
| Dependencies | Package metadata permits Python >=3.10,<4, qdrant-client >=1.15.1,<2, langchain-core >=1,<2 and pydantic >=2.7.4,<3 (E5). | Ranges are not installed-package hashes, a lockfile or a tested client/server combination. |

The inspected adapter reads collection configuration and checks vector name, dimension and requested distance. Its width probe may call `embed_documents(["dummy_text"])`; construction can therefore invoke the configured embedder and remote service. `from_texts` adds data, and `force_recreate` can delete a collection. The source was inspected without importing or calling it. No constructor is presented as a free, local-only, read-only validation command. (E6)

Known configuration mismatches produce the inspected adapter's exceptions; missing identities/configuration remain unknown. Those source branches do not create a new project rule or an approved compatibility verdict. The existing T3 rule proposals and #40's versioned review remain authoritative; the frozen v1 contract and all catalog proposals are unchanged.

## Transport, authentication and authorization

For the pinned Qdrant adapter, the connection paths accept HTTP/gRPC preferences, URL/host, HTTPS and API-key configuration (E6). The [current Qdrant security guide](https://qdrant.tech/documentation/security/) documents the `api-key` header, TLS and collection-scoped permissions. It distinguishes reachable self-hosted defaults without authentication from Cloud's default authentication (E7). This mutable guide is not an observed configuration of the pinned server. No endpoint, certificate, selected principal or permitted collection operation was tested.

A service credential and an optional payload filter do not by themselves establish the application's caller-to-document permission mapping. This is an engineering inference about the missing selected integration, not a claim that every Qdrant deployment lacks authorization. The concrete integration must preserve trusted identity, mandatory scope and any revocation/ACL metadata before protected content reaches a model; #13/#16/#35 retain that implementation and validation work.

For Bedrock, the [IAM guide](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html) documents identity credentials, signed programmatic requests and policy evaluation. The separate [API-key guide](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html) documents bearer-token authentication with associated IAM permissions. These general mechanisms are not an executed authentication path for the selected retrieval endpoint or evidence that every SDK/operation supports the same mechanism. The actual caller credentials, Region, endpoint, operation permissions and installed SDK remain unspecified.

The [knowledge-base service-role guide](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html) says ingestion uses the role already bound to the knowledge base: a data-source manager can ingest readable locations and later query them without holding S3 permissions. Treat this service/ingestion authority separately from application end-user authorization. No policy or account entitlement was inspected or changed.

## Bedrock hybrid and user-context findings

The current [Retrieve API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) specifies `POST /knowledgebases/{knowledgeBaseId}/retrieve`, a required query and optional retrieval configuration. Its response includes retrieved content, locations, metadata, scores and possible pagination; the declared 403/400 errors distinguish missing permissions from invalid input. These are API-document facts, not observed calls or quality measurements.

| Source, accessed 2026-10-18 | Documentary result | Decision consequence |
| --- | --- | --- |
| [Query configuration user guide](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html) | HYBRID is documented for RDS, OpenSearch Serverless and MongoDB vector stores with a filterable text field; otherwise the guide says the query uses semantic search. It describes `retrievalConfiguration.vectorSearchConfiguration.overrideSearchType`; omission lets Bedrock choose. | The original #119 fallback concern is supported as a conditional publisher statement. No actual fallback was observed, and HYBRID is not a universal connector capability. |
| [Vector search API type](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_KnowledgeBaseVectorSearchConfiguration.html) | Its `overrideSearchType` text names only OpenSearch Serverless with a filterable text field and says other configurations allow SEMANTIC only. | The two current primary documents disagree on the broader eligible set. Preserve the conflict; do not silently adopt their union or infer which page is stale. A selected service/store/version/Region needs conclusive evidence before a hybrid claim. |
| [Retrieve](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) and [UserContext](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_UserContext.html) | `userContext` is optional on Retrieve; when supplied, UserContext requires `userId`. AWS describes it as user-identity input for access-control filtering. | This is positive documentation of an ACL-related feature. Do not generalize an earlier optional-metadata-filter observation into absence of all Bedrock access control. Its selected knowledge-base applicability, trusted caller binding, indexed permissions and revocation behavior remain untested. |

The selected Bedrock embedding model, vector dimensions/metric and actual backing-store configuration are unknown in #119's offered claim; no identity is filled from a product name. Requesting HYBRID or receiving scored chunks would not alone prove both retrieval legs executed. Optional user-supplied or model-generated metadata filters remain distinct from trusted authorization. This review offers the new source discrepancy and positive UserContext evidence to #16; it does not change that owner's canonical decision or assert a deployed security guarantee.

## Evidence and limits

The inspected corpus is the existing 99 matrix cells, their four documented RAG source pages, the seven-source pinned #245 path and the Bedrock input above. This is a bounded review of that material, not an exhaustive audit of every product integration or a new feature-matrix regrade. Confidence is high in the exact source declarations and branch conditions read; confidence in installed configuration, retrieval success, quality and security remains unestablished. A stable commit identifies code, not executed behavior or the right to reuse an upstream corpus.

The seven E1–E7 locators retain their exact publisher, URL and revision mapping in the unchanged supplement. All additional pages are linked at each claim above and were read on 2026-10-18; they are mutable publisher documentation/marketing without a release lock for the full page. No hosted rate, quote or capacity measurement is supplied. Region/currency are not applicable to the source comparison; the selected Region remains an explicit missing input for any later service claim. A failed attempt to open the guessed `security_iam_authentication.html` URL supplied no evidence; the actual IAM guide linked above was successfully read.

Only short factual paraphrases and source links are added. No upstream source file, weights, benchmark content, customer text or credentials are redistributed. Existing #60/#41 intended-use and source-eligibility boundaries remain in force; code/model licence declarations in #245 are not a new corpus or hosted-service grant.

## Offered receiving scopes

These are requests for actual accept/narrow/reject decisions on this exact note, not recorded acceptance. The live co-assignees below are preserved. A new delegated in-session engineering review, if provided under the project mandate, must identify its actual reviewer/input and must not be attributed to an absent named assignee.

| Consumer and live co-assignees | Offered finding | Remaining owner work |
| --- | --- | --- |
| #14 — zabyxc01, PUSHINGSQUARES | The pinned dense width/dot example and explicit separation of representation, encoder identity, query/document policy and normalization. | Select and validate the actual encoder/wrapper; retain model/input rights and other representations. |
| #15 — zabyxc01, appletechie | Qdrant's pinned configuration checks, vector-name/metric requirements and deployment-dependent transport/auth capabilities. | Establish the actual collection/index configuration, client lock and permitted operation scope; no selected database or universal fit is adopted. |
| #16 — zabyxc01, appletechie | Connector/configuration/workload separation, Bedrock hybrid documentation conflict and positive UserContext documentation. | Resolve effective search mode and caller-bound ACL behavior for a concrete integration; retrieval quality, default backend and #7/#36 handoffs keep their own gates. |
| #25 — CompleteDotTech, Mattycodes69 | Pinned adapter metadata, query/document method distinction and constructor/insertion side effects. | Pin installed framework/dependencies and embedding wrapper before execution; no general agent behavior or framework selection is accepted by the source comparison. |
| #27 — CompleteDotTech, tynamite | A vector-store adapter is not evidence of an MCP server/client integration; the operation and credential boundaries need a separate wrapper identity. | Preserve protocol negotiation, transport/auth, capability/trust and tool-argument validation requirements; no MCP workload or wrapper was inspected here. |

## Literal acceptance map

| Live #65 criterion, unchanged | Current evidence | Remaining gate |
| --- | --- | --- |
| Inspect model embedding dimension and metric contracts | Pinned dense contract table, E1–E6 source inspection and explicit Bedrock identity gaps. | Independent evidence acceptance of this bounded desk finding. |
| Check API and authentication boundaries | Adapter methods/dependencies, Qdrant security, Bedrock API/IAM/service-role/UserContext sources. | No runtime authentication pass is inferred; selected deployment work stays with the consumers. |
| Separate connector existence from successful workloads | Claim inventory, three distinct evidence levels and explicit unexecuted conditions throughout. | No matrix full pass, successful workload or universal compatibility assertion. |
| Hand findings to existing retrieval owners | Five exact offered receiving scopes above, including the #119 follow-up. | Actual receiving dispositions and canonical receipt reconciliation. |
| Deliverable links every significant conclusion to evidence or an explicit hypothesis. | Exact E1–E7 pins, linked current publisher pages, immutable matrix input and labelled engineering inferences. | Final independent source/evidence review. |
| Relevant technical owners review handoffs; unresolved decisions are named. | Current live co-assignees and owner-specific questions above. | Five actual scoped decisions, preserving all historical receipt objects. |
| Repository checks pass; reviewer accepts the evidence before Done. | Required current-revision checks and source/receiving reviews will be attached to the delivery PR. | Guarded canonical merge, signed-main content/check readback and issue/Project reconciliation only after all literal criteria are satisfied. |

## Historical protocol checkpoint

The following is the complete earlier protocol, preserved verbatim. Its protocol-only status, owner text and unchecked boxes describe that checkpoint; the dated findings and actual later receipts govern this continuation.

```markdown
# MR-09: Review RAG interoperability market claims

Issue: [#65](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65). Owner: @zabyxc01. Status: protocol only; validation has not been completed. Readiness: Ready.

## Question
Do advertised RAG integrations establish usable cross-component compatibility?

## Starting evidence
[technical-feasibility.md](technical-feasibility.md). This note is not a new canonical component catalog or a completed measurement.

## Protocol and acceptance
- [ ] Inspect model embedding dimension and metric contracts
- [ ] Check API and authentication boundaries
- [ ] Separate connector existence from successful workloads
- [ ] Hand findings to existing retrieval owners
- [ ] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain affected-owner review and accepted handoff.

## Next action
Execute the documented validation protocol; initial research findings are starting inputs, not completed validation.

## Result
No completed independent validation is claimed. No raw customer data, benchmark artifact or paid API output was collected. Consumers: #14, #15, #16, #25, #27.
```
