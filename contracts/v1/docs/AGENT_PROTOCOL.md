# Inter-agent coordination, immutable data and API protocol

## Ownership and mutations

**One logical writer per authority**: catalog publishing, build revision creation, canonical ruleset publication, published pricebooks, compatibility evaluation, capacity estimation, and deployment approval must have defined owners. Parallel agents can submit proposals, but cannot mutate each other's stored records.

- `ComponentRegistry` and JSON Schemas: schema stewardship, major/minor/patch versions.
- `CatalogSnapshot`: catalog service, immutable and source-dated; vendors can supply new item revisions.
- `BuildSnapshot`: configurator service, revisioned and concurrency protected; not directly written by catalog or compatibility agents.
- `DependencyGraph`: compatibility service, graph versioned; UI consumes, does not interpret differently.
- `Ruleset`: compatibility service, versioned and approval controlled; no per-agent forks for final status.
- `ResourceEstimate`: capacity/hardware analysis agent; always pinned to build revision and selection IDs.
- `Pricebook` / `CostEstimate`: pricing service, retains effective dates, coverage and assumptions.
- `QualityEvaluationRun`: benchmark/safety/evaluation service, measured results rather than predictions.
- `DeploymentManifest`: deployment service; references unchanged reports and signed/approved decisions.

## Build write sequence (optimistic concurrency)

1. UI obtains `GET /v1/builds/{build_id}` with `revision=N` and current `ETag`.
2. User submits `PUT /v1/builds/{build_id}` with `If-Match: "N"`, `Idempotency-Key`, and a candidate build `revision=N+1`.
3. Server checks authentication/authorization, JSON Schema, semantic referential integrity, version locks and business invariants.
4. In one transaction, server compares head revision, stores revision `N+1` and an outbox event. On mismatch, return `409` and current revision; the client must rebase/retry, not force overwrite.
5. Event `build.selection.upserted` / `build.objectives.updated` includes **IDs, new revision and affected kinds**, not raw keys, dataset content or full prompts.
6. Dependency engine traverses old and new activated graphs; invalidates derived evidence for build revision `N+1`.
7. Compatibility, resource, quality and cost services recompute asynchronously or on user request. Their outputs contain build ID and exact revision.
8. UI accepts diagnostics only if `report.build_revision == current build.revision`; otherwise marks them stale and requests newer evidence.
9. Production deployments require a manifest referencing an immutable compatible evaluation, successful quality run, complete cost estimate, calibrated capacity and real approvals.

For distributed agents, dispatch work with `correlation_id`; use `causation_id` and `idempotency_key` for retries, deduplication and tracing. Use an outbox/inbox pattern or equivalent durable delivery. Events are **at-least-once**; handlers must be idempotent. Do not assume messages are globally ordered across different builds.

## Endpoint outline

See `api/openapi.yaml` for exact payload schemas:

| Operation | Resource | Behavior |
|---|---|---|
| `GET` | `/v1/component-kinds` | Lists canonical registry |
| `GET` | `/v1/catalog/snapshots/{id}` | Retrieves source-dated immutable catalog |
| `GET` | `/v1/dependencies/{id}` | Retrieves canonical dependency graph |
| `GET` | `/v1/rulesets/{id}` | Retrieves versioned ruleset |
| `POST` | `/v1/builds` | Creates revision 1 with idempotency key |
| `GET` | `/v1/builds/{id}` | Returns latest revision with ETag |
| `PUT` | `/v1/builds/{id}` | CAS revision change with `If-Match` |
| `POST` | `/v1/builds/{id}/evaluate` | Compatibility report for requested revision |
| `POST` | `/v1/builds/{id}/estimate-cost` | Cost estimate for requested revision |
| `GET` | `/v1/builds/{id}/compatible-options?kind=...` | Alternative selections with pass/fail/unknown reasons |
| `POST` | `/v1/builds/{id}/deployment-proposals` | Preflight checks and approval manifest; does not auto-deploy |

## Validation layers — mandatory, in order

1. **JSON Schema:** keys, types, enums, min/max, credential-reference format.
2. **Referential integrity:** every catalog and selection reference exists, version agrees, catalog kinds agree, no duplicate selection IDs or ambiguous `(kind,role)` in a build.
3. **Activation/cardinality:** required one-per-build `workload`, `deployment_mode`, and `context_policy`; one active primary model; other components conditional, many-valued if configured.
4. **Graph and compatibility:** use all relevant cross-tier rules; test both directions and n-ary estimator requirements.
5. **Evidence and freshness:** resource report, pricebook and quality run must apply to the same build revision, and prices to current effective dates and regions.
6. **Policy gates:** license, authorization, privacy, data classification, tool side effects, geographic compliance, measured evaluations, budget and approvals.
7. **Deployment approvals:** must be explicitly authorized and reversible; a preview or `ready` badge cannot bypass policy checks.

## Schema change contract

- JSON field meaning and unit is immutable in a major version. Example: `context_window_tokens` always integer tokens; never silently change to kilotokens.
- New optional fields and new catalog kinds require shared migration planning, regenerated schemas, validators, UI, docs, tested example, and dependency graph changes.
- New enum values can break clients that exhaustively switch; version and coordinate them even when payload validation is otherwise compatible.
- Change catalogs and rulesets by publication of **new snapshot/version**, never in-place modifications. Historical builds still reference old versions.
- API clients should accept unknown catalog fields **only in namespaced `extensions`**; unknown top-level fields are rejected to catch typos. Schema extension names use the form `x_vendorname`.
- Do not rely on lexical timestamp/price comparisons, machine float currency, or unversioned live URLs for authoritative performance and price facts.
