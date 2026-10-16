# Component catalog and selection schema

The **29** canonical component `kind` values. All component IDs are stable; an item of a given kind can be used in more than one build or role. Types, requiredness, and allowed enum values are defined in JSON Schema, not this descriptive table.

| Tier | Kind (`kind`) | Required catalog spec keys | Required selection settings | Cross-tier dependencies (examples) |
|---|---|---|---|---|
| T0 | `workload` | `workload_type`, `modalities` | — | — |
| T0 | `deployment_mode` | `mode` | — | — |
| T1 | `model_provider` | — | — | — |
| T1 | `model` | `provider_ref`, `model_type`, `modalities_in`, `modalities_out`, `context_window_tokens`, `max_output_tokens`, `access_modes`, `model_formats` | — | deployment_mode [T0] |
| T1 | `context_policy` | — | `requested_context_tokens`, `reserved_output_tokens` | — |
| T2 | `hosting_platform` | `hosting_type` | — | deployment_mode [T0] |
| T2 | `accelerator` | `accelerator_type`, `vendor`, `model_name`, `vram_gb`, `backends`, `precisions` | `device_count` | model [T1], context_policy [T1] |
| T2 | `compute_profile` | `hosting_ref`, `cpu_cores`, `ram_gb`, `region` | `instances` | model [T1] |
| T2 | `inference_engine` | `backends`, `model_formats`, `supported_precisions` | — | model [T1], fine_tuned_model [T5] |
| T2 | `storage` | `storage_type` | — | — |
| T3 | `data_source` | `source_type`, `modalities`, `classification` | — | — |
| T3 | `knowledge_base` | `data_source_refs` | — | — |
| T3 | `embedding_model` | `provider_ref`, `embedding_dimensions`, `max_input_tokens`, `similarity_metrics`, `supported_modalities`, `access_modes` | — | model_provider [T1] |
| T3 | `vector_database` | `supported_metrics` | `index_dimension`, `similarity_metric` | storage [T2], hosting_platform [T2] |
| T3 | `rag_pipeline` | `retrieval_mode` | — | model [T1] |
| T4 | `agent_framework` | `programming_languages` | — | model [T1], rag_pipeline [T3] |
| T4 | `tool` | `protocol`, `side_effect` | — | — |
| T4 | `mcp_server` | `transport` | — | hosting_platform [T2] |
| T4 | `memory_store` | `memory_type`, `backing_type` | — | vector_database [T3], storage [T2] |
| T4 | `integration` | `integration_type` | — | — |
| T5 | `training_framework` | `methods`, `backends` | — | model [T1] |
| T5 | `training_compute` | `compute_profile_ref` | — | compute_profile [T2] |
| T5 | `training_dataset` | `data_source_refs`, `data_classification` | — | data_source [T3] |
| T5 | `fine_tuned_model` | `base_model_ref`, `training_framework_ref`, `training_dataset_ref`, `artifact_format` | — | model [T1] |
| T6 | `guardrail` | `targets`, `policies`, `enforcement` | — | tool [T4], rag_pipeline [T3], model [T1] |
| T6 | `evaluation_suite` | `metric_names`, `mode` | — | model [T1], rag_pipeline [T3], agent_framework [T4], fine_tuned_model [T5] |
| T6 | `deployment_target` | `target_type` | — | hosting_platform [T2], model [T1], agent_framework [T4] |
| T6 | `monitoring_stack` | `signals` | — | model [T1], compute_profile [T2] |
| T6 | `cost_policy` | `default_currency` | — | model [T1], compute_profile [T2], storage [T2], integration [T4], training_compute [T5] |

## Universal catalog item envelope

All catalog items must contain: `schema_version`, `id`, `kind`, `tier`, `name`, `version`, `status`, `billing_class`, `spec`, `provenance`, and `updated_at`. Optional fields include `description`, `tags`, verified `license`, and namespaced `extensions`. Catalog `spec` has 29 strict discriminated variants (one per kind); vendor-specific experimental data belongs in `extensions`.

## Universal selection envelope

All selections must contain: `id`, `kind`, `catalog_item_id`, `catalog_item_version`, `role`, `enabled`, and typed `settings`. A component selected twice for different purposes must have distinct `id` and `role` values. The `role` is only meaningful **within a component kind** (e.g., generative model `primary`, `fallback`; multiple embedding indexes might use `documents` and `memory`).

## Essential units and scoping

- Tokens are **tokens**, never kilotokens unless a property explicitly includes `_1m`. Context request is prompt budget and reserved output; compare their sum to model maximum.
- `vram_gb` is device VRAM in GB; `device_count` is physical/logical selected devices. Do not assume multi-GPU VRAM can be pooled without engine/model parallelism support.
- `region` uses a canonical deployment-provider region identifier or a validated user-residency mapping; do not compare incompatible provider geographies by free text.
- `embedding_dimensions` describes supported model dimensions, while `vector_database.settings.index_dimension` describes a **particular index**. Changing dimensions typically requires an index rebuild.
- Model inference `precision`, quantization and context choices are specific to each selected model and engine; model/accelerator/backend constraints are joint and not just pairwise.
- API-only builds can omit a local GPU/inference runtime. Keyword-only RAG need not select embeddings or a vector database.
- `credential_ref` values start `secret://` and are opaque references, not credentials.
- Price amounts and quantities are decimal strings; units are explicit; timestamps are RFC 3339 and catalog evidence is dated.

## Enforced structural relationship examples

- `model.spec.provider_ref` resolves to a `model_provider` catalog item; an active model selection is linked to its provider.
- `compute_profile.spec.accelerator_ref` resolves to a selected `accelerator`, and `hosting_ref` to the selected platform.
- `training_compute.spec.compute_profile_ref` must reference a compute SKU already known in the catalog.
- `knowledge_base.spec.data_source_refs` and `training_dataset.spec.data_source_refs` refer to `data_source` catalog items; they are not inline contents.
- `fine_tuned_model.spec.base_model_ref`, `.training_framework_ref`, and `.training_dataset_ref` form immutable lineage.
- `memory_store` may reuse `vector_database` or `storage`, and does not create another independent vector DB.

See `docs/DEPENDENCIES.md` for conditional rule semantics, non-tree relationships and invalidation.
