# Cost, capacity, evaluation and deployment gates

## Pricebook and cost semantics

- Catalog items declare `billing_class`: `free`, `included`, `metered`, or `unknown`. Only a **verified** free/included classification may safely bypass rate lookup. `unknown` is **not zero cost**.
- A `Pricebook` rate is uniquely tied to a catalog item ID + item version + meter + optional region, with a start and optional expiry. Its `price_type` is `list`, `contract`, or `estimate`; provenance includes verification status and check date.
- Money values are `{ "amount": "123.45", "currency": "USD" }`; decimals are strings, not binary floats. Currencies may not be summed without an explicit pinned exchange-rate policy; the schema intentionally does not invent conversion.
- A cost line contains a priced `meter`, `quantity`, `unit_price`, `amount`, `price_rate_id`, `selection_id`, method, confidence, assumptions. Check `line.amount = quantity × unit_price` with decimal arithmetic and a documented rounding rule. Add tax separately from subtotal; preserve the original tax assumptions and rate basis.
- `coverage=complete` only if all active **metered** selections and billable related operations are accounted for, all rates are applicable/current, discounts are treated explicitly, no catalog billing class is `unknown`, and no unpriced IDs remain. A complete quote can still be an **estimate** with low confidence; expose that distinction.
- Usage projections must account for input vs output tokens, caching, retries, peak rate limits, hosted GPU hours, training GPU hours, storage GB-month, vector indexing, tool/API calls, network egress, observability charges, taxes, and minimum commitments where applicable. For baseline v1, some meters such as egress are not in the enumerated rate registry: report such unmodeled costs as uncovered, or extend the schema through a reviewed revision; do **not** hide them.
- The `cost.monthly_total_amount` derived metric requires a **complete 30-day quote** matching the current build revision and currency. Stale or partial quotes yield `unknown`, never budget-pass.

## Model hardware capacity is a separate concern

A published model parameter count, advertised GPU VRAM, or weights-only lower bound is **not sufficient** to mark a combination as runnable. A production capacity estimator must consider:

- Weights and quantization format, runtime overhead, fragmented memory, graph captures and offload.
- Model architecture, token context, output reservation, KV-cache precision and concurrent sessions.
- Batch strategy, expected request mix, SLA/latency, parallelism topology and per-device VRAM (not merely cluster sum).
- GPU architecture/backend, driver, supported engine/model format, interconnect bandwidth, host RAM and disks.
- Fine-tuned adapter merges, longer contexts, embeddings, multimodal payloads and training reservation.

The `ResourceEstimate` schema stores version-pinned estimates with `estimator_id`, version, assumptions, selected component IDs, units and confidence (`verified`, `calibrated`, `estimated`, `unverified`). Missing or insufficiently confident evidence is `unknown` under the build's resource confidence policy.

## Compatibility versus measured quality

`EvaluationReport` is deterministic compatibility logic: field validity, rules and capacity evidence. `QualityEvaluationRun` is an independently measured run of actual test data, tools, agent workflow and security scenarios with metric scores, thresholds, evaluator version, dataset revision and artifacts. A passed compatibility report does **not** substitute for a successful quality run.

When any part of the build changes, evaluations and resource assumptions tied to earlier build revisions are stale. Measurements must not be transferred blindly to a model/GPU/framework/quantization/dataset revision that has changed.

## Deployment approval contract

A proposed `DeploymentManifest` references the **same** `build_id` + `build_revision` as compatibility, quality, cost, resource and target selection. Before publishing status `approved` or `deployed`, production deployment service must establish:

1. Valid current catalog selections, verified product capability/terms, active permissions and licenses.
2. No failed blocking compatibility rules; no blocking unknown conditions; no missing n-ary resource estimates.
3. Production-quality run actually passed against current revision and dataset, with safety/tooling checks.
4. All required security, privacy, data residency and authorization controls apply, especially to mutating tools, MCP and data sources.
5. Quote is complete, currency/rates applicable and approved budget policy satisfied.
6. All required human approvals exist and were granted for this revision (owner, security, compliance, finance as applicable).
7. Monitoring, incident handling, a rollback artifact/plan, and validated deployment target are present.

The included **fictional** manifest is `proposed` with `pending` approval and is *not* a production deployment. The sample quality run contains synthetic numbers for contract testing only.

## Failure and unknown semantics

| Situation | Compatibility outcome | Deployment behavior |
|---|---|---|
| Unsupported GPU backend | `fail` | Block |
| GPU memory not calibrated or context changed | `unknown` | Block until estimator evidence |
| RAG vector dimension mismatch | `fail` | Block and warn index must be recreated |
| Provider capability unverified | `unknown` | Review/block according to policy |
| Missing valid price for billable item | Cost coverage `partial`/`unknown` | Budget gate cannot pass |
| Absent completed quality run | Compatibility may be `valid` | Must remain pending, not auto-deploy |
| Previous build revision report | Stale | Ignore, recompute and reapprove |

**Do not claim exact costs or production readiness from synthetic fixtures.**
