# T3: Knowledge & Retrieval

Issue: #12 · Assignees: @Mattycodes69, @zabyxc01 · Status: research complete ([workstream acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/12#issuecomment-6256396687)) · Updated: 2026-10-18

T3 is optional in a build. Knowledge access does not inherently require embeddings or a vector database. The workload's declared knowledge need and chosen retrieval method determine which components apply; missing evidence remains unknown.

## Decision records

| Issue | Record | Current scope and limitation |
| --- | --- | --- |
| #13 | [Knowledge base](knowledge-base.md) | Research complete: source/connector/storage taxonomy plus Azure Blob indexer and S3/Bedrock comparison, with scoped receiving acceptance ([#395](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/395), [criterion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13#issuecomment-6254983749)); source-specific admission, permissions/refresh/deletion execution and versioned runtime adoption remain separate |
| #14 | [Embedding model](embedding-model.md) | Research complete: sourced text-embedding comparison and pinned artifacts, with scoped receiving acceptance ([#384](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/384), [criterion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14#issuecomment-6254446207)); selected-route quality, pricing applicability and versioned contract/runtime adoption remain separate |
| #15 | [Vector database](vector-database.md) | Research complete: pgvector, Qdrant and Chroma software pins ([#151](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/151)), index-specific limits and not-needed criteria, with scoped receiving acceptance ([#387](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/387), [criterion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/15#issuecomment-6254402784)); deployment enforcement, source-use rights, deletion/recovery execution and versioned runtime adoption remain separate |
| #16 | [RAG and retrieval](rag-retrieval.md) | Research complete: conditional backend, enforcement, context and evaluation decision `rag-retrieval-decision/0.2.0` delivered through [#406](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/406), with [criterion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16#issuecomment-6256151952) and [six constrained receiving decisions](rag-retrieval.md#outgoing-review-packet-and-named-follow-ups); selected-workload execution, source-use rights and versioned runtime adoption remain separate |

## Consolidated decisions

The [delivered retrieval decision](rag-retrieval.md#recommendation-and-rationale) combines the accepted knowledge, embedding and vector inputs:

- Omit retrieval when it is unnecessary; use an authorized direct lookup for authoritative structured facts. For document search without stronger evidence, compare keyword/BM25 first. Dense, hybrid and graph paths need a justified workload and their actual operation, representation/index, authorization and evaluation evidence. No dedicated vector service is required by default.
- Bind protected retrieval to the trusted caller, resource, action and current mandatory permission scope before any reranker, model, tool, derived artifact, cache or trace exposure. An optional filter or successful connector call does not establish authorization. Training rights and memory purposes remain separate decisions.
- Count the complete serialized generation request after permitted transformations and each actual round, with the selected output reservation. The retrieval subtotal is only a screen. Whole-chunk removal requires the accepted content-preservation conditions; missing fit evidence cannot authorize silent removal of required content or reduced required output.
- Keep ANN fidelity, labelled relevance, answer quality, citation support and permission checks separate. Count actual encoding, retrieval, reranking, generation, refresh and storage events with their eligible units and rates; a stage label supplies neither a measured result nor a charge multiplier.

The current proposals still require the bound `rag_pipeline` route, including tool-only retrieval, until #40 adopts a versioned actual-path representation. This summary does not remove that limitation. Completed [#65 desk research](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65#issuecomment-6250267864) supplies its scoped interoperability input; it is not a runtime experiment to repeat or an authority to broaden access.

## Proposed rules and contract routing

- KB-01–KB-04: requester authorization, derived-copy deletion, complete chunk admission and separate training permission.
- EMB-01–EMB-04: output/index width, representation identity, scoring/normalization and truncation behavior.
- VDB-01–VDB-04: index/type admission, trusted access scoping, deletion lineage and evaluation configuration.
- [RAG-01–RAG-06](rules/retrieval-rules.md): retrieval-budget screen, authorization before exposure, reranker limits, selected hybrid support, filtered approximate-search risk and citation support. Reconcile overlapping deletion and dimension concerns centrally; do not publish duplicate independent gates.

These are research proposals for #40. Conceptual operands need a versioned representation and fixtures before execution; frozen v1 is unchanged. Fixed severity, outcome and unknown policy stay separate. Passing source-checked documentation does not establish independently reproduced behavior.

## Handoffs and open decisions

| Consumer | Required disposition | Status |
| --- | --- | --- |
| #7 | Retrieval, memory and output budgets within the actual model/context semantics | [#16's outgoing content-preservation policy accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6255280691); the separate incoming counting receipt retains its direction. Complete-request recount, required content and output reservation remain required |
| #9/#10/#11 | Storage/operator/capacity and runtime assumptions for the chosen pipeline | Pending scoped evidence |
| #16 | Ingestion authorization, embedding/index identity, and when vector storage is unnecessary | Incoming #13–#15 research interfaces accepted with the conditions in their criterion receipts above and integrated in [#406](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/406); #16's separate criterion receipt above records its completed research |
| #25 | Tool/native retrieval interface; authorization and connector existence versus successful execution | [#16 input accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25#issuecomment-6255402398): actual bound path, before-exposure authorization, per-round complete context and actual cost events. Earlier T4 receiving scope retains its original revision |
| #27 | MCP transport and authorization for an actual retrieval-tool path | Completed #65 supplies the desk input above; this summary supplies no additional MCP receiving decision or runtime result |
| #28 | Reuse selected storage by link/role; consent, retention and derived deletion remain memory semantics | [#16 input accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/28#issuecomment-6255403076): separately bound memory purpose, implementation/index and event/layer lifecycle evidence. W-R11 declaration remains separate from M1 recovery |
| #32 | Shared source identity and separate training-use rights, privacy and lineage | [#13 R5 input accepted](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/395#pullrequestreview-5564840530); selected-source training permission and actual dataset use remain separately evidenced |
| #35/#36 | Enforcement and workload-specific retrieval evaluation | [#35 authorization interface](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6255403750) and [#36 evaluation protocol](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36#issuecomment-6255284787) accepted with constraints; actual enforcement, denominators, observations and workload thresholds remain separate |
| #39 | Ingestion, embedding, re-indexing, storage and query meters | [#16 event/unit/coverage input accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6255288507); selected route, region, price and quantity evidence remain required for an actual total |
| #40/#41 | Versioned rule fields, source grades and freshness | The child decision records retain their accepted research-format inputs and source-policy boundaries; executable adoption and source-specific qualification remain separate |

These are the linked reviewers' actual component-level receiving decisions on their stated source revisions. This summary records them without extending their scope, attributing replies to absent assignees or treating incoming and outgoing directions as interchangeable.

The conditional architecture choices above are decided research inputs. Selected source instances, multimodal representations, backend configuration, permission propagation, workload quality and eligible cost evidence retain the [named follow-up owners](rag-retrieval.md#outgoing-review-packet-and-named-follow-ups). [Parent #12 is complete](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/12#issuecomment-6256396687): all four child decision records meet their research criteria, the four research ownership interfaces listed in #12 are accepted with their stated constraints, and the merged summary records the decisions, rules and open questions. Its completion receipt retains the delivered revision, independent review and default-branch validation. The named consumer follow-ups remain separately scoped.
