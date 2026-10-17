# Architecture and scope

Shared research architecture and implementation boundaries. The website demonstrates
builder behavior with synthetic data; this description does not certify production
catalog coverage or native-client delivery.

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
3. **Builder clients and services**: apply the governed rules to user selections,
   recompute valid options and costs, and export configurations. The website has a
   synthetic preview; native clients and production services have separate delivery gates.

## Mobile delivery and shared services

The [Apple/iOS delivery plan](APPLE_DELIVERY_PLAN.md) aligns with the Android plan:
1 program, 18 epics and 110 feature/task work packages. These are delivery levels,
not new component tiers or contract kinds. Epics 03–05 cover shared contracts,
production data and services; each client owns its native UI, persistence, lifecycle,
network adapters and conformance checks.

Keep one canonical implementation issue for each shared capability. Apple, Android
and web integration tasks link to that work without changing its assignees or parent.
Repository/framework decisions remain in 01.3, service hosting in 01.4, and contract
changes under research #40. API declarations and a static website do not establish
that a production backend exists. Approved research, published data and deployed
services must be verified separately.

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

Production web/mobile runtime code, operating backend services, user-account and
payment implementation, and unsupported claims that a particular stack is recommended.
Delivery planning may live here; it does not override research ownership or frozen v1.

Apple delivery structure and canonical shared handoffs are indexed in
[APPLE_DELIVERY_TRACKING.md](APPLE_DELIVERY_TRACKING.md). Its dated snapshot does not
replace live GitHub status, ownership or dependency relationships.
