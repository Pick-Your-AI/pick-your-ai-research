# AI Builder dependency map

The arrows below mean **uses information from**, not necessarily a strict delivery order. Cycles are intentional: the builder may need to revisit a choice after another component is selected. Optional workstreams should disappear cleanly when unused.

| Workstream | Component | Inputs and constraints |
| --- | --- | --- |
| T0 Configuration | Workload / Use Case | User goals, modality, quality and latency targets, traffic, budget, privacy |
| T0 Configuration | Deployment Mode | API, managed, or self-hosted; user constraints |
| T1 Model Selection | Model Provider | Deployment mode (T0) |
| T1 Model Selection | AI Model | Provider (T1), GPU (T2), inference engine (T2) |
| T1 Model Selection | Context Window | Model and provider (T1), GPU (T2) |
| T2 Infrastructure | Hosting | Deployment mode (T0), GPU availability |
| T2 Infrastructure | GPU / Compute | AI model and context (T1), fine-tuning (T5), concurrency |
| T2 Infrastructure | Inference Engine | AI model (T1), GPU, model format, fine-tuned model (T5) |
| T3 Knowledge & Retrieval | Knowledge Base | Data sources (T4), storage |
| T3 Knowledge & Retrieval | Embedding Model | Data type, hosting (T2) |
| T3 Knowledge & Retrieval | Vector Database | Embedding model, hosting (T2) |
| T3 Knowledge & Retrieval | RAG | Knowledge base, embeddings, AI model (T1), retrieval backend; vector database optional |
| T4 Agents & Integrations | Agent Framework | AI model (T1), RAG (T3), tools, memory |
| T4 Agents & Integrations | Tools & APIs | Agent framework, guardrails (T6) |
| T4 Agents & Integrations | MCP Servers | Tool compatibility, hosting (T2), agent framework |
| T4 Agents & Integrations | Memory | Agent framework, storage (T3), optional vector database (T3) |
| T5 Training & Fine-Tuning | Training Framework | AI model (T1), model access |
| T5 Training & Fine-Tuning | Training Compute | Framework, GPU (T2) |
| T5 Training & Fine-Tuning | Training Dataset | Knowledge sources (T3) |
| T5 Training & Fine-Tuning | Fine-Tuned Model | Framework, compute, dataset; impacts inference (T2) and evaluation (T6) |
| T6 Deployment & Operations | Guardrails | Model (T1), RAG (T3), tools (T4) |
| T6 Deployment & Operations | Evaluation | Model (T1), RAG (T3), agents (T4), fine-tuning (T5) |
| T6 Deployment & Operations | Deployment | Provider (T1), infrastructure (T2), knowledge (T3), agents (T4), guardrails and evaluation |
| T6 Deployment & Operations | Monitoring | All active components (T1–T5) |
| T6 Deployment & Operations | Cost Estimate | Tokens (T1), compute (T2), storage (T3), APIs (T4), training (T5) |

## Shared compatibility model to research

Represent each configuration as typed selections with explicit versions and deployment mode. A rule should identify the participating fields, source, severity (`compatible`, `warning`, `incompatible`, or `unknown`), explanation, and suggested correction. Re-evaluate affected rules when a selection changes. Use ranges and assumptions for estimates such as throughput, memory, and cost.
