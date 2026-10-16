# AI Builder dependency map

This map records how research components relate. Most relationships mean **uses information from**, not a strict delivery order. Cycles are intentional: the builder may need to revisit a choice after another component is selected. Optional workstreams (T3–T5) must disappear cleanly when unused. See [CONTRIBUTING](../CONTRIBUTING.md#dependency-semantics) for how each relationship type is recorded in GitHub.

## Components

| Workstream | Component | Issue | Information inputs | Compatibility (bidirectional) |
| --- | --- | --- | --- | --- |
| T0 Configuration | Workload / Use Case | [#2](https://github.com/Pick-Your-AI/research/issues/2) | User goals and constraints | — |
| T0 Configuration | Deployment Mode | [#3](https://github.com/Pick-Your-AI/research/issues/3) | #2 | — |
| T0 Configuration | Component Schema & Compatibility Rules | [#40](https://github.com/Pick-Your-AI/research/issues/40) | #2, #3; attributes from every component issue | #6, #10, #11 |
| T0 Configuration | Catalog Data Sources & Freshness | [#41](https://github.com/Pick-Your-AI/research/issues/41) | — | — |
| T0 Configuration | Saved, Shared & Compared Builds | [#42](https://github.com/Pick-Your-AI/research/issues/42) | #41, #39 · **blocked by #40** | — |
| T1 Model Selection | Model Provider | [#5](https://github.com/Pick-Your-AI/research/issues/5) | #3, #40, #41 | #6 |
| T1 Model Selection | AI Model | [#6](https://github.com/Pick-Your-AI/research/issues/6) | #2, #3, #5, #40, #41 | #7, #10, #11 |
| T1 Model Selection | Context Window | [#7](https://github.com/Pick-Your-AI/research/issues/7) | #5, #6 | #10, #16 |
| T2 Infrastructure | Hosting | [#9](https://github.com/Pick-Your-AI/research/issues/9) | #3, #10, #41 | — |
| T2 Infrastructure | GPU / Compute | [#10](https://github.com/Pick-Your-AI/research/issues/10) | #2, #6, #7, #33 | #6, #11 |
| T2 Infrastructure | Inference Engine | [#11](https://github.com/Pick-Your-AI/research/issues/11) | #6, #10, #33 | #6, #10, #33 |
| T3 Knowledge & Retrieval | Knowledge Base | [#13](https://github.com/Pick-Your-AI/research/issues/13) | #2, #9 | — |
| T3 Knowledge & Retrieval | Embedding Model | [#14](https://github.com/Pick-Your-AI/research/issues/14) | #5, #9, #13 | #15 |
| T3 Knowledge & Retrieval | Vector Database (optional backend) | [#15](https://github.com/Pick-Your-AI/research/issues/15) | #9, #14, #16 | #14 |
| T3 Knowledge & Retrieval | RAG & Retrieval Backends | [#16](https://github.com/Pick-Your-AI/research/issues/16) | #6, #7, #13, #14, #15 | #7 |
| T4 Agents & Integrations | Agent Framework | [#25](https://github.com/Pick-Your-AI/research/issues/25) | #6, #11, #16 | #6, #27 |
| T4 Agents & Integrations | Tools & APIs | [#26](https://github.com/Pick-Your-AI/research/issues/26) | #25, #35 | — |
| T4 Agents & Integrations | MCP Servers | [#27](https://github.com/Pick-Your-AI/research/issues/27) | #9, #25, #26 | #25 |
| T4 Agents & Integrations | Agent Memory | [#28](https://github.com/Pick-Your-AI/research/issues/28) | #7, #13, #15, #25 | — |
| T5 Training & Fine-Tuning | Training Framework | [#30](https://github.com/Pick-Your-AI/research/issues/30) | #5, #6 | — |
| T5 Training & Fine-Tuning | Training Compute | [#31](https://github.com/Pick-Your-AI/research/issues/31) | #9, #10, #30 | — |
| T5 Training & Fine-Tuning | Training Dataset | [#32](https://github.com/Pick-Your-AI/research/issues/32) | #13, #30, #36 | — |
| T5 Training & Fine-Tuning | Fine-Tuned Model | [#33](https://github.com/Pick-Your-AI/research/issues/33) | #30, #31, #32 | #5, #10, #11 |
| T6 Deployment & Operations | Guardrails | [#35](https://github.com/Pick-Your-AI/research/issues/35) | #2, #6, #16, #26, #27, #28 | — |
| T6 Deployment & Operations | Evaluation | [#36](https://github.com/Pick-Your-AI/research/issues/36) | #2, #6, #16, #25, #33, #35 | — |
| T6 Deployment & Operations | Deployment | [#37](https://github.com/Pick-Your-AI/research/issues/37) | #3, #5, #9, #11, #13, #25, #27, #35, #36 | — |
| T6 Deployment & Operations | Monitoring | [#38](https://github.com/Pick-Your-AI/research/issues/38) | All active components | — |
| T6 Deployment & Operations | Cost Estimate | [#39](https://github.com/Pick-Your-AI/research/issues/39) | #2, #5, #7, #9, #10, #14, #15, #26, #31, #40, #41 | — |

The only native delivery blocker is **#42 blocked by #40**: a saved build serialises the schema, so its format cannot be defined first. Every other relationship is informational or a compatibility relationship and must not be modelled as blocking.

## Boundaries and handoffs

| Concern | Owner | Consumers / notes |
| --- | --- | --- |
| Builder catalog data (facts, prices, sources, reuse terms, freshness, evidence grades) | T0 #41 | Every component issue; #40 provenance fields; #39; #42 invalidation |
| User knowledge data sources (connectors, rights, sync, deletion) | T3 #13 | Earlier versions listed "Data Sources (T4)" as a Knowledge Base input; this is now owned by T3. T4 tools (#26, #27) cover runtime actions and live API calls. |
| Infrastructure storage products (`storage`) | T2 #9 | Shared by #13, #15, #28, #31; storage pricing feeds #39 |
| Knowledge storage semantics (documents, metadata, ACLs) | T3 #13 | Reused by #28; product catalog supplied by #9 |
| Retrieval backend choice (keyword, vector, hybrid, graph, direct lookup) | T3 #16 | A vector database (#15) is one optional backend |
| Vector database product evaluation | T3 #15 | Reused by #28; not re-evaluated in T4 |
| Agent memory semantics (session vs durable, retention, consent) | T4 #28 | Storage products from #9; knowledge/retrieval semantics from #13 / #15 |
| Model access (license, weight availability, provider terms) | T1 #5, #6 | #30 decides whether training is permitted |
| Fine-tuned artifact definition and provenance | T5 #33 | Serving compatibility owned by #11; sizing by #10; evaluation by #36 |
| Inference GPU sizing | T2 #10 | #31 reuses the accelerator catalog for training estimates |
| Workload targets | T0 #2 | #36 turns them into evaluation criteria; #38 into thresholds |
| Pricing units, aggregation, uncertainty | T6 #39 | Components supply prices; #41 governs provenance |
| Compatibility rule format | T0 #40 | All rules contributed by component issues |

## Shared compatibility model

Represent each configuration as typed selections with explicit versions and deployment mode. In the imported v1 contract, a rule identifies the participating fields, condition, severity (`info`, `warning`, or `error`), explanation, and suggested correction. Evaluation outcomes are separately `pass`, `fail`, `unknown`, or `skipped`. Re-evaluate affected rules when a selection changes. Use ranges and assumptions for estimates such as throughput, memory, and cost. Research into this model is tracked in #40; see [contract coverage](CONTRACT_MAPPING.md) for all 29 kinds and ownership boundaries.
