# Cross-tier dependency and compatibility contract

This AI configurator is a **constraint graph**, not a linear wizard. The UI may be ordered by tier, but validity is computed across all active selections regardless of which tier changed first. The baseline graph (`baseline/core-dependency-graph.json`) contains **59 directed semantic dependencies**, and the fixture ruleset contains **45 declarative cross-tier checks**. Publish reviewed production variants with stable IDs in `baseline/`.

## Three distinct notions of relationship

1. **Catalog references** identify source truth: a `model.spec.provider_ref` points to a model publisher; `compute_profile.spec.accelerator_ref` points to a GPU SKU; a fine-tuned model points to its base model and dataset.
2. **Build links** are actual user-selected runtime wiring: `agent_framework calls mcp_server`, `rag_pipeline reads_from knowledge_base`, `memory_store stored_in vector_database`. These are `BuildSnapshot.links` and reference `selection.id` values, not catalog IDs.
3. **Dependency graph edges** are invalidation and eligibility relations between *kinds*: `compute_profile depends_on model`; `guardrail depends_on tool`. They are **not** sufficient to declare compatibility by themselves. Explicit compatibility rules check actual capabilities and choices.

Graph edge meaning: `dependent_kind` depends on `depends_on_kind` through `requires | constrains | informs | produces`. Activation controls whether the relationship is currently relevant (`always`, `self_hosted`, `non_api`, `rag_enabled`, `agents_enabled`, `fine_tuning_enabled`, `if_selected`, `production_only`). At selection change time, **both ends** of an active edge participate in invalidation. The graph can contain cycles.

Activation conditions are deterministic: `always` applies globally; `self_hosted` applies to selected local-serving paths in `self_hosted` or `hybrid` mode; `non_api` applies where the current mode is not pure `api`; `rag_enabled` applies when a RAG pipeline is enabled; `agents_enabled` when an agent framework is enabled; `fine_tuning_enabled` when a T5 training workflow is active; `if_selected` when the relevant components are selected; `production_only` when a production deployment target is selected. When the activation status is itself unknown, conservatively invalidate and reevaluate.

## Change handling

1. Receive a requested selection/settings change with `build_id` and **expected revision**.
2. Atomically compare-and-swap the revision; reject stale writers (`409 Conflict`). Never overwrite another agent's concurrent update.
3. Persist a new immutable build revision. Keep old snapshots for comparison, rollback and auditing.
4. Determine affected kinds through graph adjacency in **both directions**, honoring the activation conditions *before and after* the change. This catches a mode switch that enables/disables whole branches.
5. Mark prior compatibility reports, capacity estimates, quality runs, price quotes and deployment manifests **stale** for the changed build. Do not physically rewrite old evidence.
6. Re-evaluate all relevant rules and materialize a fresh `EvaluationReport`. Query actual provider capability facts or estimators when necessary.
7. Re-estimate cost and resource usage for the pinned revision; return `unknown` for unresolved prices and capacity rather than zero/false.
8. Return the new build and its diagnostics; offer compatible replacements but **do not silently remove** a user selection or silently downgrade model/context/hardware.

This is invalidation traversal, not a topological sort. Re-evaluation can be made efficient by indexing `affected_kinds`, but full validation remains the reproducible fallback.

## Reference compatibility expression language

The versioned `Ruleset` uses a safe data-only expression language. **Do not use `eval`, executable strings, SQL fragments, or user-provided JS expressions.**

### Operand types

```json
{"literal": 4096}
{"ref": {"scope": "build", "pointer": "/objectives/monthly_budget_amount"}}
{"ref": {"scope": "selection", "kind": "context_policy", "role": "primary", "pointer": "/settings/requested_context_tokens"}}
{"ref": {"scope": "catalog", "kind": "model", "role": "primary", "pointer": "/spec/context_window_tokens"}}
{"metric": "inference.estimated_required_vram_gb"}
```

- JSON pointers use RFC 6901 syntax. `scope=build` addresses the root build. `scope=selection` addresses the selected component. `scope=catalog` resolves that selection to the pinned catalog item.
- A reference by `kind` and `role` **must match exactly one enabled selection**. None, duplicate roles, broken catalog refs, unsupported fields or mismatched versions return `unknown` (and duplicated primary roles must fail semantic validation).
- Derived `metric` operands come from the documented metric registry in `Ruleset` and calibrated version-pinned external evidence. The interpreter must not assume a missing metric is zero. The reference interpreter calculates safe basic metrics like `context.total_requested_tokens` and leaves model runtime VRAM to external evidence.

### Operators

| Operator | Contract |
|---|---|
| `eq`, `ne` | Compare comparable scalar values, with numeric decimal normalization |
| `lt`, `lte`, `gt`, `gte` | Numeric comparisons only; incompatible values -> `unknown` |
| `in`, `contains` | Membership within a list or substring, with explicit operand order |
| `intersects` | Both operands arrays; any common item |
| `subset_of` | Both operands arrays; all left-side entries allowed on the right |
| `exists` | True only if an operand resolves and is non-null |
| `all`, `any` | Three-valued Boolean conjunction/disjunction |
| `not` | Three-valued logical negation |
| `implies` | Three-valued logical implication |

Three-valued semantics (`T`, `F`, `U`): `all(F, U) = F`, `all(T, U) = U`, `any(T, U) = T`, `any(F, U) = U`, `not(U) = U`. If `applies_when` resolves false, the rule is `skipped`. If `applies_when` is unknown, the result is **unknown**, never skipped or passed.

### Example: Context requirement across T1 and T2

```json
{
  "id": "rule.model.context.fit",
  "severity": "error",
  "applies_when": {
    "op": "exists",
    "value": {"ref": {"scope": "selection", "kind": "model", "role": "primary", "pointer": "/id"}}
  },
  "assert": {
    "op": "gte",
    "left": {"ref": {"scope": "catalog", "kind": "model", "role": "primary", "pointer": "/spec/context_window_tokens"}},
    "right": {"metric": "context.total_requested_tokens"}
  },
  "on_unknown": "block",
  "message": "Requested total tokens exceed model context capacity.",
  "remediation": "Reduce prompt/reserved output or select a model with a larger context window.",
  "affected_kinds": ["model", "context_policy", "compute_profile"]
}
```

Context size also affects KV-cache VRAM: `model` + `context_policy` + `inference_engine` + `accelerator` + concurrency -> **capacity estimator**. Exceeding model maximum is a hard incompatibility; exceeding measured memory is a capacity incompatibility. Those are different rules and must report different causes.

## High-value cross-tier rule families

| Upstream change | Required downstream rechecks |
|---|---|
| T0 mode `api` ↔ `self_hosted` | Weight access, host, compute, inference, API capability, licensing, network/cost |
| T1 model or provider | Context, modalities, tool use, provider, model format, inference, GPU, training, RAG, prices |
| T1 context and precision | Max context/output, KV cache, GPU memory, engine support, throughput, cost |
| T2 GPU/hosting | Engine backend, per-device memory, tensor parallelism, region, training, deployment, cost |
| T3 embedding model | Vector dimensions, metric, RAG index rebuild, memory store, cost |
| T3 vector DB / corpus | Embeddings, RAG, memory, ACL/residency, hosting, cost |
| T4 agent/MCP/tool | Framework and transport, permissions/guardrails, monitoring, quality, cost |
| T5 fine tuning | Base-model lineage, training dataset license/privacy, trainer/backend, output format, inference/GPU |
| T6 guardrail / deployment | Data classification, tool side effects, evaluation results, approval, rollback |
| Any usage or price assumption | Budget quote, monthly spend, cost policy, possible deployment block |

Some cross-tier checks are **N-ary**. Example: model, quantization, batch size, target context, tensor parallel size, KV-cache dtype, compute SKUs and GPU interconnect must be assessed **together**. Pairwise GPU-vs-model matching is not sufficient.

## Required unknown-state handling

- `error + fail` -> blocks compatibility and deployment.
- `error + unknown + on_unknown=block` -> blocks deployment; report remains `indeterminate` if no known failures.
- `warning + unknown` -> visible review, never a pass.
- `skipped` -> condition proven false; not an assertion of compatibility.
- Unverified vendor facts must be labeled and handled under `build.policy.allow_unverified_catalog_items`; a production publish gate should reject material unverified claims.

`EvaluationReport.result=valid` means the configured compatibility rules passed **for the locked selection revision and evidence**, not that the deployment is production-ready. `DeploymentManifest` is an independent approval process.
