# T3: Embedding Model

Issue: #14 · Assignees: @zabyxc01, @PUSHINGSQUARES · Status: receiving interfaces accepted with conditions; reviewed delivery pending · Access date: 2026-10-18

## User decision

Select a representation for the actual retrieval task and preserve its identity from document indexing to query encoding. Reuse the broader [T1 retrieval inventory](../T1-model-selection/retrieval-models.md); this note owns ingestion/index compatibility. The engineering scope selected for this handoff is text-first dense retrieval, with API, managed and self-operated candidate paths. This bounds the initial comparison; it does not assert that a text encoder satisfies an image, audio or video workload. Sparse, multivector and multimodal paths retain their own shape, scoring and evaluation requirements. Keyword-only retrieval needs no embedding model.

## Candidate options and sourced fields

The values below are publisher statements, not observed capacity or quality. Sources E1–E3 were checked 2026-10-18; BGE-M3 and E5 have repository pins below. Hosted aliases remain mutable and require route-specific capture before catalog admission.

| Candidate | Representation and published limit | Access and terms | Conditions |
| --- | --- | --- | --- |
| OpenAI text-embedding-3-small / large | Dense text; default 1,536 / 3,072 dimensions respectively; API `dimensions` can reduce output [E1] | Hosted API; proprietary service, no weights/license grant inferred | Record actual output length, model alias, route, tokenizer and input/batch limits independently. Language-specific quality and throughput unknown |
| BAAI/bge-m3 | Dense 1,024 dimensions; published sequence length 8,192 tokens; also sparse and multivector outputs [E2] | Public model card declares MIT; self-operated weights or separately evidenced hosted offering | Multilingual capability is a publisher claim; dense width does not describe sparse/multivector storage. Card demonstrates dense dot-product scoring |
| intfloat/multilingual-e5-large | Dense text, 1,024 dimensions; card truncates at 512 tokens [E3] | Pinned model card declares MIT; self-operated candidate; a hosted offering needs separate evidence | Preserve query/passage prefixes and normalization from the card. A successful truncated request does not prove full-document representation |
| Qwen/Qwen3-Embedding-4B, the existing T1 pinned candidate | Text embedding; card publishes up to 2,560 dimensions and task-specific query instructions [E6] | Card declares Apache-2.0; self-operated weights, or the separately documented Hugging Face dedicated TEI endpoint path [E7] | A managed deployment is a candidate, not an admitted endpoint: selected artifact revision, runtime, operator, capacity, region, terms and rate must still be captured |

Self-operated inference is `self_hosted`; a provider offering requires operator/capacity evidence to classify `api` versus `managed`. Hosted list-price observations are recorded below; region-specific applicability, throughput and workload-specific quality remain unknown; no zero-price or unlimited-throughput inference is made from public weights. API pricebooks and self-hosted compute/storage costs remain separate #39 inputs.

## Comparison field contract

| Field | Type/unit | Required scope/evidence |
| --- | --- | --- |
| model/provider/revision | strings | Artifact hash or API route/alias/access date; no unversioned equivalence |
| modalities/languages | sets with coverage status | Card and workload-specific evaluation; undocumented language is unknown |
| representation | dense, sparse, multivector | Output schema, dtype, pooling, normalization, query/document instructions |
| dimensions | positive integer or shape | Actual selected output setting; sparse nonzero count and multivector cardinality separately |
| input limits | tokens per item and per batch separately | Selected tokenizer, special tokens, instructions, truncation/rejection behavior |
| distance/scoring | metric enum + normalization policy | Encoder training/use instructions and selected index operator |
| license/terms | URL + revision + scope | Weights, code and hosted service evaluated separately by #30/#60 |
| price/throughput | currency per meter; items/tokens per second | Dated route-specific pricebook; measured workload for throughput, otherwise unknown |

## Rules proposed to #40

The complete [EMB-01–04 proposals](rules/embedding-rules.md) now use the [shared rule template](../../templates/rule-proposal.md), retaining the four IDs and fixed `error` / `review` policy. Revision 0.2 replaces the earlier compressed rows as a research proposal; it does not modify frozen v1, release a Ruleset or execute an embedding service. Each proposal separates source-checked mechanisms from project policy and supplies participants, actual pointers, applicability, assertion, unknown behavior, remediation, consumers, synthetic cases and migration impact.

| Rule | Concern | Distinct boundary |
| --- | --- | --- |
| [EMB-01](rules/embedding-rules.md#emb-01-selected-dense-widths-match) | Selected query and document output widths match the actual selected index field | Matching width does not establish a shared representation; #15's backend/type capacity check remains separate |
| [EMB-02](rules/embedding-rules.md#emb-02-query-document-and-index-generation-are-bound) | The query profile is compatible with the document profile that produced this index generation | Role-specific prefixes may legitimately differ; a shared model name or equal width is insufficient |
| [EMB-03](rules/embedding-rules.md#emb-03-scoring-and-normalization-are-compatible) | The selected metric, operator and score transformation implement the evidenced scoring contract | Equivalent ranking does not establish equal score scales or calibrated thresholds |
| [EMB-04](rules/embedding-rules.md#emb-04-input-processing-preserves-the-required-content) | Complete query/document inputs obey their encoding and content-retention policies | The embedding tokenizer and request limits do not replace the generation-model context budget |

Applicability follows the actual retrieval path, including vector-backed memory and retrieval exposed through a tool. An absent primary RAG selection cannot silently exempt an enabled vector path. The shared envelope in the rule file preserves #40's identity preflight, per-selection outcomes, required-presence distinction and evidence eligibility. Backend choice, authorization and corpus quality remain with their existing rules and owners.

## Re-indexing and cost

Proposed estimate: re-embedding work equals the sum of billed input units for affected chunks, including configured overlap/instructions and any billed retries. Add index writes/build work, temporary parallel index storage, query-encoder migration and eventual old-index cleanup. This is a method, not a measured price. Metadata-only edits may avoid re-embedding when the selected ingestion system documents that behavior; [AWS's conditional optimization](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html) is one example, not a general guarantee (read 2026-10-18).

## Evidence and quality boundary

- E1 — OpenAI, [Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings), mutable API documentation, accessed 2026-10-18. Default dimensions and shortening are source checked; no API call was made.
- E2 — BAAI, [bge-m3 model card](https://huggingface.co/BAAI/bge-m3/raw/5617a9f61b028005a4858fdac845db406aefb181/README.md), repository revision `5617a9f61b028005a4858fdac845db406aefb181`, accessed 2026-10-18. The [publisher repository metadata](https://huggingface.co/api/models/BAAI/bge-m3) resolved that revision. Published dense width/sequence, alternate representations and MIT card declaration are scoped to this card; no weights downloaded or benchmark reproduced.
- E3 — intfloat, [multilingual-e5-large card](https://huggingface.co/intfloat/multilingual-e5-large/raw/ab10c1a7f42e74530fe7ae5be82e6d4f11a719eb/README.md), selected repository revision `ab10c1a7f42e74530fe7ae5be82e6d4f11a719eb` (not a claim of latest release), accessed 2026-10-18. Prefix, normalization and truncation instructions; no ranking against other candidates is claimed.

Publisher benchmark tables do not establish quality on the user's corpus. #36 must pin corpus/license, queries, relevance judgments, split/leakage controls, preprocessing, retrieval depth, metric and uncertainty before comparisons. The existing #65 experiment remains with its active contributors.

## Recommendation and outstanding acceptance

Choose representation and index together after fixing the task, language and data boundary. The text-first comparison and complete rule proposals are engineering decisions offered under the user's delegated project mandate. They do not attribute agreement to absent assignees. @zabyxc01/@PUSHINGSQUARES remain the live owners; the dated handoff packet below records the actual scoped receiving decisions. No CatalogItem, pricebook, endpoint, throughput measurement or quality result is fabricated to fill missing values.

For a declared multimodal workload, reuse the T1 inventory and require a separate #14/#15/#36 representation and quality disposition before recommending a path. An unknown modality need remains unknown. This preserves the initial scope decision without turning it into a claim of multimodal compatibility or an automatic future default.

## BGE-M3 representation pin

For the self-operated BGE-M3 candidate, use repository revision `5617a9f61b028005a4858fdac845db406aefb181` for both document and query artifacts. The pinned E2 card declares 1,024 dense dimensions and an 8,192-token sequence length, demonstrates dense dot-product scoring and says query instructions are unnecessary. Preserve the actual tokenizer, pooling, normalization, runtime revision and configured maximum length in the representation identity; the repository pin alone does not specify the complete serving stack. Smaller configured lengths must not silently discard required content (EMB-04).

The card separately exposes sparse weights and multivector scoring; those outputs are not interchangeable with the dense field. Its MIT declaration concerns the model artifact, not automatically the ingestion corpus or a hosted offering. The source-scoped dense artifact and BAAI publisher identity are now proposed in `catalog/proposals/t3-embedding-model-bge-m3-dense.json` and `t1-provider-baai.json`. Required v1 artifact fields come from E2 and the pinned repository file listing; runtime/configuration evidence remains separate. Billing stays unknown and only the declared MIT identifier is recorded, without additional permission booleans. #14 owners retain multimodal scope and #30/#60 retain applicable rights review. This pin removes the mutable-card ambiguity, without claiming quality, throughput, a default backend or full issue completion.

## E5 artifact and encoding contract

Select repository revision `ab10c1a7f42e74530fe7ae5be82e6d4f11a719eb` for both tokenizer and model. E3 declares MIT and demonstrates attention-mask-aware mean pooling, L2 normalization and dot-product scoring. E3's FAQ prescribes `query: ` for queries and `passage: ` for documents in asymmetric retrieval, such as passage retrieval, but `query: ` on both sides for symmetric tasks, including semantic similarity, bitext mining and paraphrase retrieval. Prefixes also apply to non-English text; changing these instructions changes the representation contract. Its multilingual support is a publisher capability claim, not reproduced language-by-language quality.

The pinned [tokenizer configuration](https://huggingface.co/intfloat/multilingual-e5-large/blob/ab10c1a7f42e74530fe7ae5be82e6d4f11a719eb/tokenizer_config.json) names `XLMRobertaTokenizer` and `model_max_length: 512`; the [Sentence Transformers configuration](https://huggingface.co/intfloat/multilingual-e5-large/blob/ab10c1a7f42e74530fe7ae5be82e6d4f11a719eb/sentence_bert_config.json) also sets `max_seq_length: 512` (primary configuration, accessed 2026-10-18). E3's example enables truncation. Proposed ingestion requirement: tokenize the complete prefixed input with special tokens before deciding whether it fits; 512 is not a raw-document allowance plus extra instructions. An over-budget document needs chunking or explicit content-loss acceptance, not a success flag based on returned vectors. The count depends on this tokenizer, not the generation model's tokenizer.

This is a repository/configuration pin, not a downloaded-weight checksum or an executed runtime test. The card license declaration does not settle corpus rights or hosted-service terms. The source-scoped E5 artifact and its intfloat publisher identity are proposed in `catalog/proposals/t3-embedding-model-multilingual-e5-large.json` and `t1-provider-intfloat.json`. Required fields are supported by E3, the two pinned configurations and the repository file listing, all rechecked 2026-10-18. Selected runtime configuration, language/task quality and rights review remain separate; billing is unknown and no extra license-permission booleans are inferred.

## Hosted embedding request boundaries

E4 — OpenAI [Create embeddings reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create), `POST /v1/embeddings`, mutable documentation accessed 2026-10-18. Published limits: 8,192 tokens per input, 300,000 tokens summed over one request, and no empty-string input. The reference separately states an array bound of 2,048; its wording does not precisely distinguish all nested token-array cases, so preserve this uncertainty when implementing pre-tokenized input validation. It is not an output-vector-width bound. The output `dimensions` parameter is supported for text-embedding-3 and later models; the default widths in E1 remain separate facts.

Proposed synthetic boundary cases (arithmetic only, not API observations): an 8,193-token item fails the published per-item limit even in a small batch; 40 items of 8,000 tokens each fit individually but total 320,000 and exceed the request limit. Splitting requests addresses aggregate limits, not oversized individual chunks. Record the actual alias, tokenization, output dimension setting and request grouping; do not treat reduced output dimensions as permission for larger input. Exact hosted snapshot identity, tokenizer validation, account-specific price eligibility and throughput remain follow-ups for #14 owners, with price semantics routed to #39. No API requests, weights downloads or quality measurements were performed.


## Hosted embedding price and unit comparison (2026-10-18)

Published, source-checked list-price observations for the direct OpenAI `POST /v1/embeddings` candidates; no API call or invoice measurement. E5 — [small model page](https://developers.openai.com/api/docs/models/text-embedding-3-small) and [large model page](https://developers.openai.com/api/docs/models/text-embedding-3-large), mutable pages accessed 2026-10-18:

| Model alias | Standard displayed input rate | Meter |
| --- | --- | --- |
| `text-embedding-3-small` | USD 0.02 | Per 1,000,000 input tokens |
| `text-embedding-3-large` | USD 0.13 | Per 1,000,000 input tokens |

Currency is supported by OpenAI's [API-credit currency FAQ](https://help.openai.com/en/articles/10421635-multicurrency-billing), accessed 2026-10-18, which limits API credit purchases to USD. Region: unspecified by these price rows; this is not proof of global availability or applicability to a regional endpoint. Version: model aliases and dated price capture, not an immutable serving snapshot. These are the default displayed rates, without selecting the Batch API pricing toggle; Batch, negotiated contracts, taxes and account credits are outside this comparison. Recheck the applicable route/account terms before a cost decision.

The input-token meter applies separately to document ingestion and query encoding; a vector's output dimension is not the billing unit. Proposed estimate: eligible billed input tokens / 1,000,000 × selected rate, plus separate storage/search and other applicable costs. Re-indexing includes newly encoded document inputs; this formula is an estimate method, not measured consumption. BGE-M3/E5 software license declarations establish no hosted inference rate or zero operational cost.

These observations satisfy the bounded price/unit comparison, but are not a canonical Pricebook: no complete exact-version hosted OpenAI embedding CatalogItems are admitted yet, and regional/account eligibility remains unresolved. #39 owns subsequent eligible rate admission; #14 owners retain candidate choice and receiving-owner confirmations.

## Managed candidate and reproducible configuration (2026-10-18)

E6 — Qwen's [Qwen3-Embedding-4B card](https://huggingface.co/Qwen/Qwen3-Embedding-4B/blob/5cf2132abc99cad020ac570b19d031efec650f2b/README.md), revision `5cf2132abc99cad020ac570b19d031efec650f2b`, accessed 2026-10-18, is the same pinned candidate already recorded by T1. Its retrieval examples use an instruction on the query and no instruction on documents. The Transformers example uses last-token pooling and L2 normalization; those settings belong to that encoding path, not to every library by implication. Its TEI example is a documented deployment recipe, not an executed endpoint or hardware-fit result. The card's advertised limit and an example's configured input length must remain separate observations.

E7 — Hugging Face's [dedicated embedding-endpoint tutorial](https://huggingface.co/docs/inference-endpoints/en/tutorials/embedding), [endpoint configuration](https://huggingface.co/docs/inference-endpoints/en/guides/configuration), and [TEI arguments](https://huggingface.co/docs/text-embeddings-inference/en/cli_arguments), mutable primary documentation, accessed 2026-10-18. The tutorial explicitly uses Qwen3-Embedding-4B with TEI. Endpoint configuration exposes model revision, infrastructure and replica choices; TEI exposes revision, pooling, prompt and batching controls. This supplies a concrete managed candidate for comparison with the direct API and self-operated paths. It supplies no selected region, current deployed image digest, rate, throughput or rights disposition. No service was provisioned, no model was downloaded and no request was made.

Classify the actual operator/capacity arrangement using [#9's accepted hosting boundary](../T2-infrastructure/hosting.md), rather than the model's download permission. A dedicated provider-operated deployment is a managed candidate; running those weights and TEI on user-operated infrastructure is a separate self-hosted configuration. The [actual #9 receiving receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6251909151) already accepts the bounded #9→#14/#15 input. Its source-scoped service, runtime, region and storage conditions still apply. This document does not request that completed input again or infer a deployed endpoint from it.

## Representation profile and index-generation record

The following is a **research field dictionary**, not a new JSON schema or a v1 extension. It joins existing fields to the additional evidence needed to reproduce a selected retrieval path. A profile describes one role's encoding behavior; a compatibility record joins the query profile to the document profile and selected index generation. It need not require identical query and document instructions: the pinned E5 asymmetric pair is an explicit counterexample to that shortcut.

| Record | Existing frozen-v1 anchor | Additional scoped evidence or proposed operand |
| --- | --- | --- |
| Selection and component identity | Selection `/id`, `/kind`, `/role`, `/enabled`, `/catalog_item_id`, `/catalog_item_version`; CatalogItem `/id`, `/version` | Bind every participating selection and actual index field/namespace; unresolved or ambiguous links stay unresolved under #40/CD-6 |
| Artifact or service | Embedding CatalogItem `/spec/provider_ref`; selected `/settings/region` when supplied | Model/tokenizer artifact revision and available hashes, or exact hosted route/alias/access date and known snapshot. An alias is not an immutable weight identity |
| Role and task | Selection `/role` identifies a build role; it does not encode an entire query/document recipe | Query/document role within the path, task, modality and language scope, instruction template and preprocessing. Keep distinct role profiles when the documented encoder is asymmetric |
| Shape | Catalog `/spec/embedding_dimensions`; selection `/settings/output_dimensions`; index `/settings/index_dimension` | Actual selected output width and its evidence; dense dtype or sparse/multivector shape. A published default is usable only when its applicability to the selected configuration is established |
| Scoring | Embedding `/spec/similarity_metrics`; vector database `/spec/supported_metrics`; selected index `/settings/similarity_metric` | Pooling, normalization, selected operator, score transformation and ordering direction; threshold calibration is an additional #16/#36 decision |
| Input processing | Embedding `/spec/max_input_tokens`; knowledge base `/settings/chunk_size_tokens` and `/settings/chunk_overlap_tokens` when supplied | Exact tokenizer/version, role-specific instruction and special-token accounting, selected item/request limits, truncation behavior and declared content-loss policy |
| Serving configuration | Referenced hosting/runtime components and their selected settings | Runtime/version, precision, relevant overrides, batching/concurrency and host/service configuration. Record an unknown field instead of inferring it from the model card |
| Index generation | Vector selection `/settings/index_name` when supplied | Generation identity, document-profile identity, source/chunk revision mapping, selected field/namespace and population state. An index name alone does not prove which encoder populated it |
| Evidence and price identity | Catalog `/provenance`; existing catalog/version and pricebook boundaries | Exact source scope, access date and evidence status; applicable route/account/region/meter/period for a separately admitted rate. No raw credentials or private documents belong in this research record |

No profile is made complete by copying an unknown service snapshot into a model-version string. Preserve the known alias and capture date, qualify the missing serving identity, and resolve only the assertions supported by eligible evidence. Likewise, a model/runtime change triggers compatibility review, not an automatic assertion that every vector changed. An evidenced equivalent implementation or documented compatible dual encoder can retain compatibility; otherwise the proposed migration is a new generation with controlled re-encoding and cutover.

## Quantity and migration handoff to #39

For a selected period, count query encodings, newly indexed document chunks, changed chunks and deliberate rebuilds separately. Each billable encoding event uses that encoder's complete tokenized input, including any billed instructions, overlap and retries. Sum each real event once: labeling the same operation as both retrieval and memory does not create a second charge. Whether a failed or retried request is billable needs the applicable service terms; neither zero nor automatic full billing is assumed.

For an eligible input-token rate, the existing estimate remains `billed input tokens / published unit quantity × rate`. An unchanged index queried without re-encoding its documents does not incur a new document-embedding event merely because a query ran. Query encoding may still be billable. An output-width change affects compatibility and possibly storage; it does not change a token-meter unit by itself. A character or byte corpus size needs an evidenced conversion before it becomes tokens. The embedding tokenizer cannot stand in for the generation tokenizer in #7/#16's assembled prompt.

For self-hosted or dedicated managed capacity, retain instance/replica count, allocated time, start-up and idle floors, applicable commitments and the measured workload used for any throughput conversion. Unknown throughput means an unknown time estimate, not zero time or a provider-guaranteed tokens/second figure. Add separately scoped index writes/building, live and migration storage, backups, search, egress and operations where applicable. During a migration, record old/new generation overlap and cutover/recovery conditions. Deleting the old index is a separate observed lifecycle event; planned cleanup does not prove source deletion or physical purge. These inputs feed [#39's unit, coverage and uncertainty rules](../T6-deployment-operations/cost-estimate.md); no new rate or total is introduced here.

## Concrete receiving packet and completion boundary

The [actual delegated receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14#issuecomment-6253659087), posted by CompleteDotTech at 2026-10-18T18:40:42Z, accepts all six interfaces below with retained conditions. The reviewer independently read the packet and the actual consumer records under the user's project engineering mandate; this does not attribute a response to absent named assignees. The receipt identifies the locally committed source `94fcf3dad35b243a2358a21e600964ef8084260d`, tree `5428d4909c3e51849d3c53a3a5e8c9874e9ba378`, before its PR publication, and both exact document blobs. These rows record that actual decision without changing the reviewed input interfaces. Source review and receiving acceptance remain separately attributed; neither establishes a runtime result or contract adoption.

| Consumer | Input supplied here | Actual receiving decision and retained conditions |
| --- | --- | --- |
| #13 Knowledge Base | Role-aware tokenizer/item/request limits, explicit content-loss handling and source/chunk→index-generation lineage | Accepted: count complete encoded input; successful truncation cannot satisfy full-content requirements. Preserve KB authorization/deletion and the documented conditions on metadata-only re-embedding exemptions |
| #15 Vector Database | EMB-01 selected field width, EMB-02 generation binding and EMB-03 operator/normalization contract | Accepted: keep VDB-01 backend/type capacity separate and bind the actual field/namespace. Another primary database or equal dimension supplies no fit, permission or quality evidence |
| #16 RAG / Retrieval | Query/document profiles, score direction/transformation, independent generation-token budget and per-path applicability | Accepted with the existing tool-path gap retained: an enabled bound `rag_pipeline` or separately adopted #40 path binding is still required to cover the current no-pipeline gate. Preserve trusted authorization before exposure and separate threshold, reranker, context and quality decisions |
| #28 Agent Memory | Reuse suitable database selections and product identities with explicit memory index/profile bindings | Accepted consistently with the [existing memory storage boundary](../T4-agents-integrations/agent-memory.md#when-vector-search-is-warranted): bind the memory index/namespace; nonvector and application/framework paths gain no universal vector-store requirement. Consent, authorization, retention and history/cache/backup erasure remain separate |
| #39 Cost Estimate | Distinct encoding-event quantities, dated token rates versus capacity time, partial-cost coverage and migration overlap | Accepted: count each actual eligible event once, preserve exact units and unresolved billing/throughput/region. These observations admit no new Pricebook, deployment or complete operating total |
| #40 Component Schema & Compatibility | Complete EMB-01–04 revision 0.2, actual v1 pointers and explicitly conceptual profile/link/generation operands | Accepted as research proposals, including identity preflight, universal versus required-presence scope and conservative disputed limits. Executable adapters, schema/wire location, adopted Rulesets and versioned migration remain separate |

The #28 record is already delivered; this packet proposes an additional compatible representation input and does not undo that receipt or reopen its completed research. Its [actual T3 storage receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13#issuecomment-6245648522) permitted a suitable shared database selection with a separate index/namespace. It did not grant an ACL, residency or universal compatibility claim. #5/#9's provider and hosting decisions, #13's current source/chunk constraints and the accepted #40 semantics remain inputs, not new assertions of recipient assent.

Follow-up ownership remains the live issue assignees: #14 for the selected task and representation evidence; #15/#16 for index/operator and retrieval behavior; #28 for the memory path; #39 for eligible price/quantity intake; #40 for contract adoption; #36 for corpus-specific quality. A known multimodal need requires its own representation-specific review using T1's inventory. A concrete deployment still needs route/runtime/region/terms and workload evidence. This research proposal establishes neither measured quality nor successful inference. The receiving decision is now recorded; final current-main composition, normal validation, reviewed merge and the literal #14 completion assessment remain delivery gates.
