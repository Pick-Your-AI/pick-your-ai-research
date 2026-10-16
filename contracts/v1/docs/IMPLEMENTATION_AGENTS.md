# Instructions for every AI Builder agent

**Project:** AI Builder (PCPartPicker-style AI stack configurator)
**Contract version:** `1.0.0`
**Contract scope:** Catalog, configuration, dependencies, validation, cost, observability, deployment.

## Mandatory rules

1. Read `README.md` and the schema matching your artifact before writing code. Follow the exact `kind`, `id`, `role`, `tier`, `schema_version`, timestamps, enum values, JSON pointer syntax and currency units.
2. `schemas/component-registry.json` lists the **only valid component kinds**. Never create `gpu` when the canonical kind is `accelerator`, `vector_db` instead of `vector_database`, or `llm` instead of `model`. Keep identifiers identical across backend, frontend, catalogs, rules, events, and tests.
3. **Catalog agents** write validated `CatalogItem` proposals, not selections. **Configurator agents** write version-pinned `Selection` entries in a `BuildSnapshot`, not vendor facts. **Compatibility agents** own canonical `Ruleset` evaluation, not individual catalog agent compatibility booleans. **Pricing agents** own versioned `Pricebook` and `CostEstimate`, not capability metadata. **Deployment agents** use the pinned artifacts and approvals, not current unpinned catalog state.
4. Every component change must update the build revision under optimistic concurrency, then invalidate re-evaluation and repricing for every impacted kind from `dependency-graph.json`, in both directions. Rules must check all active selections for the applicable roles, not just the branch that triggered the change.
5. Treat `unknown` as distinct from `false` and `true`. Missing or unsupported data must never become successful compatibility automatically. Conditions also use three-valued logic.
6. Component compatibility is **not** proof of operational capacity. For self-hosting, derive VRAM, throughput and concurrency from a version-pinned calibrated `ResourceEstimate`; missing evidence is `unknown`. Vendor marketing specifications alone do not guarantee production performance.
7. Records must be immutable and reproducible. Each `Selection` stores `catalog_item_id` and `catalog_item_version`; builds lock `catalog_snapshot_id`, `ruleset_id`, `ruleset_version`, `dependency_graph_id` and `dependency_graph_revision`. Derived outputs store the exact `build_revision`.
8. Never store plaintext keys, passwords, tokens, credentials, unredacted prompts, or personal data in catalogs, configs, rules, events, reports or logs. Use `secret://...` opaque references only in approved fields.
9. Every catalog capability and price must declare a real evidence source with `checked_at`, `verification_status`, source URI (when available), effective date (pricing), and limitations. Missing facts are missing, not false or zero. **Examples are synthetic**, not authoritative vendor truth.
10. `quality-evaluation-run.schema.json` records measured evaluation results; `evaluation-report.schema.json` records config compatibility. Do not conflate them. A production deployment needs both plus a complete cost estimate and explicit sign-offs in the deployment manifest.
11. Do not rename, remove or repurpose fields in `1.0.0`. Add compatible optional fields using the approved contract generation flow. Breaking changes require a major version and coordinated migration.
12. Before reporting completion, run `python -m unittest discover -s tests -v` and report failures, remaining `unknown` checks, and relevant changes to the external API.

## Agent ownership (one component can be supported by multiple specialists)

| Agent | Responsibility | Canonical artifacts |
|---|---|---|
| Requirements | Use cases and deployment options | `workload`, `deployment_mode`, objectives |
| Model & Provider | Model metadata, context, publisher support, licensing | `model_provider`, `model`, `context_policy` |
| Compute | Hosting, GPU/CPU, sizing, inference engines and storage | T2 items and `ResourceEstimate` |
| Knowledge & RAG | Ingestion, corpora, embeddings, retrieval | T3 items |
| Agent & Integrations | Agent tools, frameworks, MCP and memory | T4 items |
| Training | Methods, datasets, training hardware and derived models | T5 items and lineage |
| Trust & Quality | Guardrails, benchmark suites, measured gates | `guardrail`, `evaluation_suite`, `QualityEvaluationRun` |
| Operations | Deployment, monitoring, approvals and rollback | `deployment_target`, `monitoring_stack`, `DeploymentManifest` |
| Pricing | Versioned rates, usage assumptions, complete quote coverage | `Pricebook`, `CostEstimate`, `cost_policy` |
| Compatibility core | Central rules, tri-state interpreter and graph invalidation | `Ruleset`, `DependencyGraph`, `EvaluationReport` |
| Configurator/API/UI | Single revisioned build store, user workflows | `BuildSnapshot`, `Selection`, events/API |

**Escalation:** If a needed concept is missing, submit the missing field, its type/unit, owner, versioning impact and cross-tier dependency for contract review. Do not add incompatible ad hoc fields in your service.

## Definition of done for an agent change

- Typed payload conforms to the matching JSON Schema.
- Cross-reference IDs and versions resolve.
- New or changed interactions are represented by dependency edges **and** compatibility tests (the graph alone does not enforce compatibility).
- Compatibility returns a reproducible pass/fail/unknown decision with cause and remediation.
- Pricing and resource implications are either explicitly calculated or marked unknown.
- Downstream agent contracts and API/events are updated with coordinated versioning.
- Tests cover both passing and failing configurations; no secrets are emitted.
