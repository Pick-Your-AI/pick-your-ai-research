# AI Builder — Shared Contract v1.0.0

**Goal:** A PCPartPicker-style AI configurator in which component catalogs, user selections, cross-tier compatibility, compute estimates, pricing, and deployment evidence are understood identically by all agents.

This package is an **implementation contract**, not a claim that any particular AI model, accelerator, API, price, or deployment has been verified. Every item in `examples/` is **fictional test data**.

## Hand this to every agent

1. Provide the **complete ZIP** and tell each agent to read `AGENTS.md` and this file.
2. Treat `schemas/component-registry.json` and the versioned JSON Schemas in `schemas/` as the **only canonical field names, types, identifiers, and enum sets**. `reference/generate_schemas.py` is their generation source; do not patch a generated schema independently.
3. Validate every catalog proposal, selection, build, rule, evaluation, estimate, and event against the corresponding schema. Run semantic/reference checks and compatibility rules in addition to JSON Schema validation.
4. Any agent may **propose** compatibility rules; only the compatibility-engine owner publishes approved rules into a versioned ruleset. No agent may independently invent its own final "compatible" boolean.
5. A build update must increment its revision and invalidate related evaluations and quotes. Validation is scoped to the exact build revision and catalog/ruleset/pricebook locks.

## Package map

| Artifact | Contract |
|---|---|
| `schemas/component-registry.json` | **29 component kinds**, T0–T6, activation/cardinality |
| `schemas/catalog-item.schema.json` | Immutable catalog identity, version, verified provenance, billing classification, typed vendor specification |
| `schemas/catalog-snapshot.schema.json` | Reproducible catalog snapshot |
| `schemas/selection.schema.json` | Typed selection and user settings per component kind |
| `schemas/build.schema.json` | User's immutable revisioned build and explicit links |
| `schemas/dependency-graph.schema.json` | Typed dependency graph for bidirectional change invalidation |
| `baseline/core-dependency-graph.json` | **59 starter cross-tier edges**, versioned and ready for rules-service review |
| `baseline/core-ruleset.json` | **45 starter compatibility rules** (must be validated for target workload) |
| `schemas/ruleset.schema.json` | Safe declarative cross-tier compatibility expressions |
| `schemas/evaluation-report.schema.json` | Per-rule `pass/fail/unknown/skipped` compatibility findings |
| `schemas/resource-estimate.schema.json` | Sourced/calibrated capacity estimate (e.g., VRAM, tokens/sec) |
| `schemas/quality-evaluation-run.schema.json` | Actual benchmark/quality/safety results separate from compatibility |
| `schemas/pricebook.schema.json` | Metered vendor prices, validity, region and provenance |
| `schemas/cost-estimate.schema.json` | Cost lines, quantity, tax, currency, and coverage |
| `schemas/deployment-manifest.schema.json` | Revision-pinned predeployment evidence and approvals |
| `schemas/event.schema.json` | Idempotent secret-free cross-agent events |
| `api/openapi.yaml` | Reference HTTP resource contracts; adapt transport without changing payloads |
| `sql/postgres_reference.sql` | Optional PostgreSQL immutable-snapshot storage pattern |
| `examples/*` | **Synthetic fictional** end-to-end fixtures (29 catalog items and selections, 59 dependencies, 45 rules) |
| `reference/evaluate.py` | Small sample interpreter for the rule DSL; **not** a production hardware estimator |
| `reference/generate_schemas.py` | Shared schema generator / versioned type definitions |
| `reference/create_examples.py` | Fixture generator |
| `tests/test_contract.py` | Structural, referential, price consistency, and negative compatibility tests |
| `reference/validate_payload.py` | CLI to validate any JSON payload with the bundled schema files |

## Layered model

```text
CatalogSnapshot                      Reference Data (revision-pinned)
   └─ CatalogItem x N  <---------- Selection x N -----------┐
                                    |                       |
ComponentRegistry -----> BuildSnapshot (revision) ----------┤
                         |          └─ Links x N            |
                         |                                  |
DependencyGraph ---------┤   bidirectional invalidation     |
Ruleset -----------------┤   tri-state compatibility        |
ResourceEstimate --------┤   calibrated derived evidence   |
Pricebook ---------------┤   sourced metered prices         |
                         v                                  |
                 EvaluationReport / CostEstimate -----------┤
                         |                                  |
                 QualityEvaluationRun                       |
                         |                                  |
                         v                                  |
                 DeploymentManifest ------------------------┘

Events refer to IDs, versions and changed component kinds, not secret values.
```

## Tier mapping

- **T0 Requirements:** `workload`, `deployment_mode`
- **T1 Models:** `model_provider`, `model`, `context_policy`
- **T2 Infrastructure:** `hosting_platform`, `accelerator`, `compute_profile`, `inference_engine`, `storage`
- **T3 Knowledge:** `data_source`, `knowledge_base`, `embedding_model`, `vector_database`, `rag_pipeline`
- **T4 Agents:** `agent_framework`, `tool`, `mcp_server`, `memory_store`, `integration`
- **T5 Training:** `training_framework`, `training_compute`, `training_dataset`, `fine_tuned_model`
- **T6 Operations:** `guardrail`, `evaluation_suite`, `deployment_target`, `monitoring_stack`, `cost_policy`

An accelerator is not always required: pure API mode can omit self-hosted infrastructure. RAG can be keyword-only and does not always require a vector DB. A model may have many roles; do not infer any one-to-one relation unless declared.

## Core schema example

The schema below is an **illustrative fragment** only; the real `build.schema.json` contains the authoritative fields and types:

```json
{
  "schema_version": "1.0.0",
  "id": "build.fixture.1",
  "revision": 1,
  "locks": {
    "catalog_snapshot_id": "catalog.fixture.1",
    "ruleset_id": "rules.fixture.1",
    "ruleset_version": "1.0.0",
    "dependency_graph_id": "dependencies.core.1",
    "dependency_graph_revision": 1,
    "pricebook_id": "prices.fixture.1"
  },
  "selections": [
    {
      "id": "sel_model",
      "kind": "model",
      "catalog_item_id": "cat.model.fixture",
      "catalog_item_version": "2026.10-demo",
      "role": "primary",
      "enabled": true,
      "settings": {"serving_mode": "weights", "precision": "fp16"}
    }
  ],
  "links": []
}
```

## Validation

Requires Python 3.10+ and `jsonschema>=4.20` (test-only dependency):

```bash
python -m pip install 'jsonschema>=4.20'
python -m unittest discover -s tests -v
python reference/validate_payload.py schemas/build.schema.json examples/build.json
```

Run the **reference** compatibility check:

```bash
python reference/evaluate.py \
  --build examples/build.json \
  --catalog examples/catalog.json \
  --rules examples/ruleset.json \
  --resource examples/resource-estimate.json \
  --cost examples/cost-estimate.json
```

Expected synthetic fixture: **41 passed, 4 skipped, 0 failed, 0 unknown**. Deployment readiness remains `needs_review` because compatibility alone never proves quality evaluations, real approvals, or actual production readiness.

## Critical rules

- **Unknown is never "compatible."** Undocumented features, uncalibrated model memory, absent prices, missing credentials, or unresolved versions are `unknown` and require policy handling.
- **A graph is not a strict tree.** Changing an AI model can invalidate its GPU, inference engine, context, training, RAG, and cost policy at once. Re-evaluate graph neighbors in **both directions**. Do not try to topologically sort the entire graph.
- **Source of truth is versioned.** Build snapshots, catalogs, rulesets, rates and evaluation evidence are immutable revisions. Publish new revisions; do not silently mutate an old one.
- **Never store secrets.** Selection credentials are only `secret://...` references. Event payloads must not include secrets, user prompts or raw customer data.
- **Do not let `CatalogItem` prices drift into `BuildSnapshot`.** Pricebook revisions and price effective dates must be explicit.
- **No model/hardware performance claims** without calibration and evidence matching model, quantization, context, concurrency, tensor parallelism, hardware, and inference engine.
- **Production deployment** needs compatibility, measured quality/safety, complete cost scope, human and policy approvals, and rollback evidence; a selected `evaluation_suite` alone is insufficient.

Additional implementation detail: `docs/COMPONENTS.md`, `docs/DEPENDENCIES.md`, `docs/AGENT_PROTOCOL.md`, `docs/PRICING_AND_GATES.md`.
