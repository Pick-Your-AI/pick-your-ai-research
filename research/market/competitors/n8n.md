# n8n — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `n8n`. Classification: Adjacent competitor, Substitute workflow (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | n8n workflow automation with AI agent, RAG and MCP nodes (Cloud and self-hosted) |
| Operator | n8n (licensor named in LICENSE.md) |
| URLs | [site](https://n8n.io/), [pricing](https://n8n.io/pricing/), [export/import docs](https://docs.n8n.io/build/manage-workflows/export-and-import.md), [repository](https://github.com/n8n-io/n8n), [LICENSE.md](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) |
| Access date | 2026-10-16 |
| Version / revision | Latest release `n8n@2.43.7` (2026-10-16); Sustainable Use License Version 1.0 |
| Access tier observed | Public site, pricing, docs and repository; no account; nothing deployed |
| robots.txt | n8n.io and docs.n8n.io allow content |

## Workflow

n8n executes user-built workflows; it does not recommend components.

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Visual editor; 10k+ templates; MCP to build workflows from an AI app | Documented / Vendor claim (template count) | [site](https://n8n.io/) |
| Constraints | Plan limits on executions and concurrency; credentials per integration | Documented | [pricing](https://n8n.io/pricing/) |
| Selection logic | None; the user or a template picks nodes and models. Hosted plans list "AI models without API keys" | Documented | [pricing](https://n8n.io/pricing/) |
| Explanation | None for component choice; "metric-based evaluations" on paid plans | Documented | [pricing](https://n8n.io/pricing/) |
| Save/share/export | "n8n saves workflows in JSON format"; copy-paste, file or URL import/export; exported JSON includes credential names and IDs; Git version control on higher tiers | Documented | [export/import docs](https://docs.n8n.io/build/manage-workflows/export-and-import.md), [pricing](https://n8n.io/pricing/) |

## Architecture and data

- Node-based workflow engine, self-hostable (queue mode for scaling) or hosted. Documented, [pricing](https://n8n.io/pricing/).
- Data: user's own credentials, workflows and connected services; no reference catalog of model performance. Freshness not applicable.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Hosted tiers priced by monthly workflow executions; a self-hosted Business tier; Enterprise by contract; free self-hosted Community use under the licence (rates not recorded) | Documented | [pricing](https://n8n.io/pricing/) |
| (b) Code licence | GitHub API `NOASSERTION` ("Other"). LICENSE.md: Sustainable Use License — use "only for your own internal business purposes or for non-commercial or personal use"; distribution only "free of charge for non-commercial purposes"; `.ee.` files need an Enterprise licence. Source-available, not OSI open source | Observed (LICENSE.md) | [LICENSE.md](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) |
| (c) Data reuse | Not a data source. Templates and exported JSON are user/community content with their own terms (not reviewed) | Unknown | — |

Not in the PR #82 shortlist. Embedding n8n inside a commercial Pick Your AI offering would fall under the licence limitations; route to #41.

## Counterexample

- **Suffices (hypothesis, documented basis):** an operations team automating a known business process with an AI step picks a template, swaps credentials and runs it, with JSON export and Git history. For that segment a planning-only product is redundant.
- **Falls short (hypothesis):** no workload-to-model, hardware, retrieval-quality or cost recommendation; a connector catalog does not prove a model/tool/runtime combination works. Exporting a reviewed plan into n8n JSON is a possible complement, with credentials and lifecycle left to the user.

## Matrix consistency

Pending [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `agents`, `deployment`, `saved`, `share`, `export` Documented; `model_versions` Unknown. Agrees. Pricing lists "Workflow history" and "Version control using Git", which bear on `saved`; already Documented.

## Open questions and routing

- #25: n8n as an agent/automation export target.
- #39: compare execution-based pricing with token/compute cost in total economics.
- #41: licence implications of embedding or redistributing n8n.
