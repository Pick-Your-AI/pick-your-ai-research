# MR-09: BGE-M3 dense / Qdrant connector source comparison

Issue: #65 · Contract: 1.0.0, unchanged · Kinds: `embedding_model`, `vector_database`
Status: partial source research for review · Last researched: 2026-10-18

## User decision and coordination

Does a named vector-store connector establish a usable retrieval combination?
This comparison examines the existing BGE-M3 dense and Qdrant catalog candidates
through LangChain's Qdrant connector. It is a separate supplement to the canonical
[validation protocol](rag-validation.md), preserving that file and the existing
writer's work. [Coordination request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65#issuecomment-6246156082)
records this bounded slice; no response or receiving acceptance is inferred.
No new competitor profile, matrix grade or successful workload is asserted.

## Candidate identities and comparison fields

All values below are published documentation/source facts, not measurements.
Matching individual fields is necessary evidence, not whole-stack compatibility.

| Field | Type / unit | Finding | Evidence / unresolved condition |
| --- | --- | --- | --- |
| Embedding identity and representation | revision string; representation enum-like label | BAAI BGE-M3 `5617a9f61b028005a4858fdac845db406aefb181`, dense text vectors only | E1; sparse and ColBERT outputs are outside this selected representation |
| Dense dimension | integer, coordinates per vector | 1024; Qdrant's pinned dense VectorParams permits sizes 1 through 65536 | E1/E2; proposed collection size 1024 must match actual query and document outputs; no outputs generated here |
| Similarity metric | named operation, no unit | BGE card demonstrates dense dot-product scoring; Qdrant exposes `Dot` | E1/E3; this does not prove normalization, score calibration or query/document encoder equivalence |
| Connector identity | package version and commit | `langchain-qdrant` 1.1.0 at `079eb808f8f4c08a44481c770062584ce10323b3` | E4/E5; release-tag source is pinned, installed package bytes and dependency resolution are untested |
| Dense connector defaults | mode, vector name, metric | `DENSE`, unnamed vector (`""`), `COSINE`; validation flags default true | E6; explicitly select `DOT` for this dot-based comparison and the actual collection vector name rather than assuming defaults match |
| Collection validation | conditional source behavior | Fetches collection configuration, validates named/unnamed vector selection, size and requested distance | E6; disabling collection validation bypasses those checks; matching configuration does not identify the embedding model that populated the collection |
| Dependency/API boundary | version ranges and method names | Python >=3.10,<4; qdrant-client >=1.15.1,<2; langchain-core >=1.0,<2; pydantic >=2.7.4,<3. Dense query embeds the query then calls `query_points` using the selected vector name | E5/E6; ranges are not a lockfile or proof of a tested client/server/model combination |
| Remote transport and credentials | selected connection configuration; no unit | Connector forwards URL, HTTP/gRPC preferences, HTTPS and API-key parameters to its client path | E6; actual endpoint, TLS, identity and collection permissions remain unknown; credentials are not supplied or recorded here |

### Important validation and API limits

The pinned connector's dense validation may invoke
`embed_documents(["dummy_text"])` to infer output width, and reads collection
configuration. Construction is therefore not guaranteed to be a pure local
schema check: the chosen embedding implementation and client determine calls,
network access and cost. We inspected source without importing/running it.
The `from_texts` convenience path subsequently adds texts; it is not a read-only
connectivity probe. Error text suggesting `force_recreate` is not permission to
delete/recreate an existing collection. No such action was taken. (E6)

The query path uses `embed_query`; the width probe above uses document embedding.
The source inspection does not establish that both methods use the same pinned
model, normalization, instruction policy or vector width in a user's adapter.
A BGE-specific LangChain Embeddings adapter and its installed dependencies are
not supplied by this note. The 1024/Dot correspondence is a candidate contract
alignment only, not an executed BGE→connector→Qdrant workload. (E1/E6)

Qdrant's current security guide distinguishes open-source defaults from Cloud:
a reachable OSS deployment is unauthenticated by default, whereas Cloud enables
API-key authentication. It documents API-key headers, TLS protection and
collection-level granular permissions. These capabilities do not prove a selected
deployment is configured, that a query is authorized for a particular end user,
or that a payload filter enforces an ACL. No security setting or credential was
created, changed or transmitted. The guide is mutable and is not assumed to be
an exact configuration snapshot of Qdrant 1.19.2. (E7)

## Evidence and rights

Every source below was opened on **2026-10-18**. Grade: primary publisher
model-card/source/documentation; source-checked, `unverified` for independent
runtime or performance behavior. Confidence is limited to the inspected text and
branches. Regions/currencies are not applicable because this note provides no
hosted-offering or price comparison. Small paraphrases and source links are
recorded; no upstream source file, model weight or customer corpus is redistributed.

| ID | Publisher / primary source | Version and limitation / reuse boundary |
| --- | --- | --- |
| E1 | BAAI, [model card](https://huggingface.co/BAAI/bge-m3/raw/5617a9f61b028005a4858fdac845db406aefb181/README.md) | Exact model repository revision above; card declares MIT and demonstrates dense encoding/scoring. No corpus rights or runtime reproduction follows. |
| E2 | Qdrant, [VectorParams source](https://github.com/qdrant/qdrant/blob/016542aa5deb6c66380bb137badf73d54f742bde/lib/collection/src/operations/types.rs) | Existing v1.19.2 proposal's pinned commit; dense size validation only, not a universal sparse/multivector dimension cap. |
| E3 | Qdrant, [Distance source](https://github.com/qdrant/qdrant/blob/016542aa5deb6c66380bb137badf73d54f742bde/lib/segment/src/types.rs) | Same pinned commit; enum/dispatch evidence, not a claim that distinct metric transforms are interchangeable. Existing Qdrant proposal retains Apache-2.0 software terms. |
| E4 | LangChain, [release-tag ref](https://api.github.com/repos/langchain-ai/langchain/git/ref/tags/langchain-qdrant%3D%3D1.1.0) | Tag resolved to the exact commit above on access date; subsequent branch changes are excluded. |
| E5 | LangChain, [package metadata](https://github.com/langchain-ai/langchain/blob/079eb808f8f4c08a44481c770062584ce10323b3/libs/partners/qdrant/pyproject.toml) | Version 1.1.0, dependency ranges and MIT metadata. Metadata alone is not a distribution compliance review or installed dependency lock. |
| E6 | LangChain, [connector source](https://github.com/langchain-ai/langchain/blob/079eb808f8f4c08a44481c770062584ce10323b3/libs/partners/qdrant/langchain_qdrant/qdrant.py) | Read `__init__`, `from_texts`, `from_existing_collection`, `_validate_collection_for_dense` and dense query path. Source behavior is not an executed integration result. |
| E7 | Qdrant, [security guide](https://qdrant.tech/documentation/security/) | Mutable current guide, no immutable release displayed for the entire page; deployment configuration/authenticated tests remain absent. No hosted-service or content-reuse permission inferred. |

## Recommendation and proposed compatibility checks

Retain **documented connector existence with conditional contract alignment**.
For a candidate dot-product dense path, record 1024-sized collection/vector-name
configuration and explicit DOT in the connector, then require evidence of the
same intended encoder revision/configuration on ingestion and query. Matching
width and metric alone cannot establish semantic compatibility or retrieval
quality. No production compatibility boolean or new catalog record is proposed.

Proposed failure/unknown cases for #40 review, not executed tests: a known dense
size or requested-metric mismatch fails this contract check; missing collection
configuration, encoder identity or authorization evidence remains unknown;
matching size/metric can pass only those narrow checks. Severity and wire format
remain with #40, separately from outcome. Successful configuration introspection
never certifies authorized retrieval or workload quality.

## Pricing, capacity, artifacts and handoffs

Existing proposals are [BGE-M3 dense](../../catalog/proposals/t3-embedding-model-bge-m3-dense.json)
and [Qdrant software](../../catalog/proposals/t3-vector-database-qdrant.json).
Neither is changed. No new pricebook, ResourceEstimate, quality run, external
artifact manifest or runtime result is warranted by this desk review. Compute,
index storage, embedding calls and endpoint costs remain unpriced here.

The live #65 owners/writer retain integration into the canonical protocol.
#14 owns encoder/normalization evidence; #15 collection/metric/auth configuration;
#16 retrieval integration and quality; #25 framework adapter/installed dependency
mapping; #27 any MCP wrapper adds a separate transport/auth contract; #40 owns
versioned rule adoption. Their scoped accept/narrow/reject receipts remain
pending. A selected workload, model/runtime/adapter/client pins, actual collection
configuration, authorized operation tests and retrieval-quality evidence are
required before claiming successful interoperability. None is fabricated here.
