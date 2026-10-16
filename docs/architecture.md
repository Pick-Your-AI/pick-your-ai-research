# Architecture and scope

Planning-stage description. Components and behaviours below are targets for research, not shipped functionality.

## Seven configuration tiers

| Tier | Name | Optional | Covers |
|---|---|---|---|
| T0 | Configuration | No | Workload / use case, deployment mode, plus builder-level schema, catalog sources and saved builds |
| T1 | Model Selection | No | Provider, model, context window |
| T2 | Infrastructure | No | Hosting, GPU / compute, inference engine |
| T3 | Knowledge & Retrieval | Yes | Knowledge base, embedding model, vector database, RAG |
| T4 | Agents & Integrations | Yes | Agent framework, tools and APIs, MCP servers, memory |
| T5 | Training & Fine-Tuning | Yes | Training framework, training compute, dataset, fine-tuned model |
| T6 | Deployment & Operations | No | Guardrails, evaluation, deployment, monitoring, cost estimate |

Tiers organise research and the user's guided flow. They are not a strict waterfall: selections in any tier can constrain others.

## Three layers

1. **Catalog**: validated datasets of components, specifications, pricing and evidence (`catalog/`, `pricing/`, `evidence/`), following the shared contract in `contracts/v1/`.
2. **Rules**: dependencies and compatibility rules over catalog entries, defined by the same contract (see [CONTRACT_MAPPING.md](CONTRACT_MAPPING.md) for how component kinds map to issues).
3. **Builder** (future): a constraint-resolution engine that applies rules to the user's selections, recomputes valid options and costs, and exports configurations.

## Dependency-aware compatibility

Selections form a graph rather than a list. When a component is added, removed or changed, every rule touching it, and every component whose requirements or costs depend on it, is revalidated. Examples of two-way constraints: model <-> GPU fit, context window <-> VRAM, inference engine <-> model format, fine-tuning -> inference requirements, guardrails <-> tool choice. These are modelled as compatibility constraints, not GitHub issue-blocking cycles.

The component-level relationships are documented in [DEPENDENCIES.md](DEPENDENCIES.md).

## Shared interfaces needing owner collaboration

- T1 model attributes <-> T2 GPU / inference engine attributes (model format, quantization, memory estimates).
- T1 context window <-> T2 GPU memory (KV cache sizing).
- T2 hosting <-> T0 deployment mode and T3 embedding / vector hosting.
- T3 RAG <-> T1 model and T4 agent framework.
- T4 tools / MCP <-> T6 guardrails and permissions.
- T5 fine-tuned model <-> T2 inference engine and T6 evaluation.
- T6 cost estimate <-> every active component's pricing records.

## Out of scope for this repository

The production web application, user accounts, payment handling, and any claim that a particular stack is recommended.
