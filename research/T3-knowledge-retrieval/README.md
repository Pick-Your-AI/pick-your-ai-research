# T3: Knowledge & Retrieval

Issue: #12 · Assignees: @Mattycodes69, @zabyxc01 · Status: partial workstream summary for review · Updated: 2026-10-18

T3 is optional in a build. Knowledge access does not inherently require embeddings or a vector database. The workload's declared knowledge need and chosen retrieval method determine which components apply; missing evidence remains unknown.

## Decision records

| Issue | Record | Current scope and limitation |
| --- | --- | --- |
| #13 | [Knowledge base](knowledge-base.md) | Draft source/connector/storage taxonomy, permissions, chunking and deletion propagation; source-specific configuration and consumer acceptance pending |
| #14 | [Embedding model](embedding-model.md) | Draft sourced text-embedding candidates and representation/index contract; release/route pins, quality, pricing and consumer review pending |
| #15 | [Vector database](vector-database.md) | Draft index-specific candidate comparison, not-needed criteria and trusted tenant boundaries; offering-specific limits and consumer review pending |
| #16 | [RAG and retrieval](rag-retrieval.md) | Merged partial record from [#119](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/119); backend, ACL and receiving-owner decisions remain separate |

## Proposed rules and contract routing

- KB-01–KB-04: requester authorization, derived-copy deletion, complete chunk admission and separate training permission.
- EMB-01–EMB-04: output/index width, representation identity, scoring/normalization and truncation behavior.
- VDB-01–VDB-04: index/type admission, trusted access scoping, deletion lineage and evaluation configuration.
- Existing [retrieval proposals](rules/retrieval-rules.md) retain their own identifiers and evidence. Reconcile overlapping deletion and dimension concerns centrally; do not publish duplicate independent gates.

These are research proposals for #40. Conceptual operands need a versioned representation and fixtures before execution; frozen v1 is unchanged. Fixed severity, outcome and unknown policy stay separate. Passing source-checked documentation does not establish independently reproduced behavior.

## Handoffs and open decisions

| Consumer | Required disposition | Status |
| --- | --- | --- |
| #7 | Retrieval, memory and output budgets within the actual model/context semantics | Pending owner acceptance |
| #9/#10/#11 | Storage/operator/capacity and runtime assumptions for the chosen pipeline | Pending scoped evidence |
| #16 | Ingestion authorization, embedding/index identity, and when vector storage is unnecessary | Drafted in #13–#15; acceptance pending |
| #25/#27 | Tool/native retrieval interface; auth and connector existence versus successful execution | Preserve active [#65](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65) work; no new experiment claimed |
| #28 | Reuse selected storage by link/role; consent, retention and derived deletion remain memory semantics | Pending T3/T4 receiving dispositions |
| #32 | Retrieval permission does not establish training permission | Pending source-specific rights review |
| #35/#36 | Enforcement and workload-specific retrieval evaluation | Pending acceptance; no quality threshold invented |
| #39 | Ingestion, embedding, re-indexing, storage and query meters | Pending route/region/price evidence |
| #40/#41 | Versioned rule fields, source grades and freshness | Follow merged partial policy records; final dispositions remain open |

Assignees retain decisions on initial sources, multimodal scope, candidate breadth and default backend. No child issue is complete until its evidence, merged deliverable and required handoffs satisfy its acceptance criteria. This summary records existing and proposed work; it does not certify interoperability or complete #12.
