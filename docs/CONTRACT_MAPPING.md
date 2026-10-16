# Contract coverage and issue mapping

The existing issues cover all 29 canonical kinds. This mapping proposes artifact coverage; live GitHub assignees remain the ownership authority. No new component issues or assignment changes are needed.

| Tier | Canonical kind | Research issue |
| --- | --- | --- |
| T0 | `workload` | [#2: T0: Workload / Use Case](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2) |
| T0 | `deployment_mode` | [#3: T0: Deployment Mode](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3) |
| T1 | `model_provider` | [#5: T1: Model Provider](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/5) |
| T1 | `model` | [#6: T1: AI Model](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6) |
| T1 | `context_policy` | [#7: T1: Context Window](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7) |
| T2 | `hosting_platform` | [#9: T2: Hosting](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9) |
| T2 | `accelerator` | [#10: T2: GPU / Compute](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10) |
| T2 | `compute_profile` | [#10: T2: GPU / Compute](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10) |
| T2 | `inference_engine` | [#11: T2: Inference Engine](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11) |
| T2 | `storage` | [#9: T2: Hosting](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9) |
| T3 | `data_source` | [#13: T3: Knowledge Base](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13) |
| T3 | `knowledge_base` | [#13: T3: Knowledge Base](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13) |
| T3 | `embedding_model` | [#14: T3: Embedding Model](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/14) |
| T3 | `vector_database` | [#15: T3: Vector Database](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/15) |
| T3 | `rag_pipeline` | [#16: T3: RAG & Retrieval Backends](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16) |
| T4 | `agent_framework` | [#25: T4: Agent Framework](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25) |
| T4 | `tool` | [#26: T4: Tools & APIs](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/26) |
| T4 | `mcp_server` | [#27: T4: MCP Servers](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/27) |
| T4 | `memory_store` | [#28: T4: Agent Memory](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/28) |
| T4 | `integration` | [#26: T4: Tools & APIs](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/26) |
| T5 | `training_framework` | [#30: T5: Training Framework](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30) |
| T5 | `training_compute` | [#31: T5: Training Compute](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/31) |
| T5 | `training_dataset` | [#32: T5: Training Dataset](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/32) |
| T5 | `fine_tuned_model` | [#33: T5: Fine-Tuned Model](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/33) |
| T6 | `guardrail` | [#35: T6: Guardrails](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35) |
| T6 | `evaluation_suite` | [#36: T6: Evaluation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36) |
| T6 | `deployment_target` | [#37: T6: Deployment](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37) |
| T6 | `monitoring_stack` | [#38: T6: Monitoring](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/38) |
| T6 | `cost_policy` | [#39: T6: Cost Estimate](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39) |

## Shared contracts

- #40 owns schema and compatibility review: registry, catalog schema, Ruleset, DependencyGraph and EvaluationReport. All workstreams supply candidate fields and rule proposals.
- #41 owns catalog evidence, freshness and reuse policy. The domain kind `data_source` in #13 describes user knowledge sources, not catalog research sources.
- #42 researches saved/shared configurations using BuildSnapshot, Selection and pinned CatalogSnapshot references. Importing these schemas does not resolve all saved-build product questions.
- #10 supplies ResourceEstimate methodology; #36 owns measured QualityEvaluationRun research; #39 owns Pricebook and CostEstimate semantics; #37 owns DeploymentManifest research. These runtime artifact schemas are reference material until their real inputs exist.

## Boundaries requiring explicit handoffs

- #10 covers both physical accelerators and provisionable compute profiles. They are separate catalog kinds.
- #9 covers infrastructure `storage` offerings. #13 owns knowledge organization, ingestion, ACLs and data semantics; #28 owns memory semantics. These consumers reference infrastructure storage rather than defining another storage product catalog.
- #13 covers both `data_source` and `knowledge_base`. #26 covers both `tool` and `integration`; #27 covers MCP server packaging/transport.
- #7 researches context policy as well as model/provider context limits. #39 researches cost policy separately from dated price rates.

All catalog proposals use `catalog-item.schema.json`, particularly `spec_<kind>`. Required fields are summarized in [the component guide](../contracts/v1/docs/COMPONENTS.md). `research/component-issues.json` is checked against the canonical registry in CI.

The rule contract distinguishes outcome (`pass/fail/unknown/skipped`) from severity (`info/warning/error`). Use those enums in JSON; earlier issue comparison lists are conceptual research prompts, not alternate schema definitions.
