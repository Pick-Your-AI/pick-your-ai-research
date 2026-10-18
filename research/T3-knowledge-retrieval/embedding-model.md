# T3: Embedding Model

Issue: #14 · Assignees: @zabyxc01, @PUSHINGSQUARES · Status: partial decision record for review · Access date: 2026-10-18

## User decision

Select a representation for the actual retrieval task and preserve its identity from document indexing to query encoding. Reuse the broader [T1 retrieval inventory](../T1-model-selection/retrieval-models.md); this note owns ingestion/index compatibility, not a duplicate universal model ranking. Multimodal scope remains an owner decision. Keyword-only retrieval needs no embedding model.

## Candidate options and sourced fields

The values below are publisher statements, not observed capacity or quality. Sources E1–E3 were checked 2026-10-18; BGE-M3 is pinned below. Other mutable model aliases/cards require an artifact or route pin before a complete catalog proposal.

| Candidate | Representation and published limit | Access and terms | Conditions |
| --- | --- | --- | --- |
| OpenAI text-embedding-3-small / large | Dense text; default 1,536 / 3,072 dimensions respectively; API `dimensions` can reduce output [E1] | Hosted API; proprietary service, no weights/license grant inferred | Record actual output length, model alias, route, tokenizer and input/batch limits independently. Language-specific quality and throughput unknown |
| BAAI/bge-m3 | Dense 1,024 dimensions; published sequence length 8,192 tokens; also sparse and multivector outputs [E2] | Public model card declares MIT; self-operated weights or separately evidenced hosted offering | Multilingual capability is a publisher claim; dense width does not describe sparse/multivector storage. Card demonstrates dense dot-product scoring |
| intfloat/multilingual-e5-large | Text embeddings; card truncates long text at 512 tokens [E3] | Open model candidate; exact selected artifact/license and host need intake review | Preserve query/passage prefixes and normalization from the card. A successful truncated request does not prove full-document representation |

Self-operated inference is `self_hosted`; a provider offering requires operator/capacity evidence to classify `api` versus `managed`. Price/rate, region, throughput and workload-specific quality remain unknown in this record; no zero-price or unlimited-throughput inference is made from public weights. API pricebooks and self-hosted compute/storage costs remain separate #39 inputs.

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

All are hypotheses, with conceptual next-version operands. Participants: selected `embedding_model` and linked `vector_database`/`rag_pipeline`; `knowledge_base` supplies chunk configuration. No frozen-v1 change is proposed by this note alone.

| ID | Applicability / assertion | Fixed severity / unknown policy | Synthetic decision cases |
| --- | --- | --- | --- |
| EMB-01 | Dense vector retrieval selected: actual encoder output width equals the selected index field width | `error` / `review` | 1,024→1,024 pass; 1,024→768 fail; missing output setting unknown; lexical-only skipped |
| EMB-02 | Vector retrieval selected: query and document encoders share the same representation contract, or an explicitly evidenced compatible dual-encoder pairing | `error` / `review` | Same pinned encoder/pooling/normalization/instructions pass; known unrelated same-width models fail; alias drift without provenance unknown; lexical-only skipped |
| EMB-03 | Vector retrieval selected: selected index metric/operator and normalization satisfy the encoder's documented scoring requirements | `error` / `review` | Matching normalized scoring pass; documented incompatible operator fail; undocumented normalization unknown; lexical-only skipped |
| EMB-04 | Ingestion selected: no required source content is silently dropped by truncation | `error` / `review` | Complete in-budget chunk pass; known truncation despite full-content requirement fail; unknown tokenization unknown; no embedding ingestion skipped |

Remediation: re-encode/re-index under a new explicit representation revision, or select a compatible index. Equal dimensions alone never prove compatibility. Sparse or late-interaction representations need their own operators and shapes; do not coerce them into a dense-width boolean. Changes in model, pooling, normalization, instruction template or dimension setting trigger a compatibility review before reusing an index.

## Re-indexing and cost

Proposed estimate: re-embedding work equals the sum of billed input units for affected chunks, including configured overlap/instructions and any billed retries. Add index writes/build work, temporary parallel index storage, query-encoder migration and eventual old-index cleanup. This is a method, not a measured price. Metadata-only edits may avoid re-embedding when the selected ingestion system documents that behavior; [AWS's conditional optimization](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html) is one example, not a general guarantee (read 2026-10-18).

## Evidence and quality boundary

- E1 — OpenAI, [Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings), mutable API documentation, accessed 2026-10-18. Default dimensions and shortening are source checked; no API call was made.
- E2 — BAAI, [bge-m3 model card](https://huggingface.co/BAAI/bge-m3/raw/5617a9f61b028005a4858fdac845db406aefb181/README.md), repository revision `5617a9f61b028005a4858fdac845db406aefb181`, accessed 2026-10-18. The [publisher repository metadata](https://huggingface.co/api/models/BAAI/bge-m3) resolved that revision. Published dense width/sequence, alternate representations and MIT card declaration are scoped to this card; no weights downloaded or benchmark reproduced.
- E3 — intfloat, [multilingual-e5-large card](https://huggingface.co/intfloat/multilingual-e5-large), mutable card, accessed 2026-10-18. Prefix, normalization and truncation instructions; no ranking against other candidates is claimed.

Publisher benchmark tables do not establish quality on the user's corpus. #36 must pin corpus/license, queries, relevance judgments, split/leakage controls, preprocessing, retrieval depth, metric and uncertainty before comparisons. The existing #65 experiment remains with its active contributors.

## Recommendation and outstanding acceptance

Choose representation and index together after fixing the task, language and data boundary. Keep #13 chunking, #15 dimensions/metrics, #16 scoring, #28 memory representation reuse and #39 re-indexing meters as explicit handoffs. @zabyxc01/@PUSHINGSQUARES own this record; consumer dispositions and exact runtime/version/price fields remain pending. No CatalogItem is fabricated to fill missing values. Multimodal candidates remain in the T1 inventory until T3 owners select scope and representation-specific evidence.

## BGE-M3 representation pin

For the self-operated BGE-M3 candidate, use repository revision `5617a9f61b028005a4858fdac845db406aefb181` for both document and query artifacts. The pinned E2 card declares 1,024 dense dimensions and an 8,192-token sequence length, demonstrates dense dot-product scoring and says query instructions are unnecessary. Preserve the actual tokenizer, pooling, normalization, runtime revision and configured maximum length in the representation identity; the repository pin alone does not specify the complete serving stack. Smaller configured lengths must not silently discard required content (EMB-04).

The card separately exposes sparse weights and multivector scoring; those outputs are not interchangeable with the dense field. Its MIT declaration concerns the model artifact, not automatically the ingestion corpus or a hosted offering. Remaining admission work is runtime/configuration evidence and provider/catalog linkage, with #14 owners retaining multimodal scope and #30/#60 retaining applicable rights review. This pin removes the mutable-card ambiguity, without claiming quality, throughput, a default backend or full issue completion.
