# Dify — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `dify`. Classification: Adjacent competitor, Substitute workflow (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | Dify agentic workflow and RAG application platform (Cloud, Enterprise, Community Edition) |
| Operator | LangGenius, Inc. ("© 2025 LangGenius, Inc." in LICENSE) |
| URLs | [site](https://dify.ai/), [docs](https://docs.dify.ai/en/home), [app management docs](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management), [repository](https://github.com/langgenius/dify), [LICENSE](https://github.com/langgenius/dify/blob/main/LICENSE), [terms](https://dify.ai/legal/terms-of-service) |
| Access date | 2026-10-16 |
| Version / revision | Latest release 1.17.1 (2026-09-10); repository pushed 2026-10-16; terms "Latest update: Jun 30, 2026" |
| Access tier observed | Public site, docs and repository; no Cloud account; nothing deployed |
| robots.txt | dify.ai allows all; docs.dify.ai allows content (blocks `/_next/`, `/cdn-cgi/`) |

## Workflow

Dify does not recommend a stack; the user builds one.

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | User assembles workflows, chatflows or agents in a visual builder; Knowledge Pipeline for documents | Documented | [site](https://dify.ai/), [docs](https://docs.dify.ai/en/home) |
| Constraints | Model providers, tools and plugins from a Marketplace; request-rate and storage limits per plan | Documented | [site](https://dify.ai/), [app management docs](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management) |
| Selection logic | None; component choice is the user's | Documented | [docs](https://docs.dify.ai/en/home) |
| Explanation | None for component choice; logs and monitoring for runs | Documented | [docs](https://docs.dify.ai/en/home) |
| Save/share/export | "Export DSL" includes app configuration, workflow nodes, model parameters, prompts and knowledge-base connections; excludes third-party API keys, knowledge content and logs; import shares apps between workspaces | Documented | [app management docs](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management) |

## Architecture and data

- Self-hostable application server plus `web/` frontend; Docker images; hosted Cloud SaaS. Documented, [LICENSE](https://github.com/langgenius/dify/blob/main/LICENSE), [site](https://dify.ai/).
- Data used: the user's own documents, prompts and chosen model providers. No market or benchmark dataset.
- Freshness: not applicable (no reference data).

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Hosted Cloud plans, private Enterprise deployment, free Community Edition (rates not recorded) | Documented | [site](https://dify.ai/) |
| (b) Code licence | GitHub API: `NOASSERTION` ("Other"). LICENSE: "a modified version of the Apache License 2.0"; a commercial licence is needed to "operate a multi-tenant environment" or to remove "the LOGO or copyright information" in the frontend; contributors accept that terms may change | Observed (LICENSE) | [LICENSE](https://github.com/langgenius/dify/blob/main/LICENSE) |
| (c) Data reuse | Not a data source. Exported DSL is user content; Cloud terms govern hosted use | Documented | [terms](https://dify.ai/legal/terms-of-service) |

Not in the PR #82 shortlist. Relevance for Pick Your AI is export targeting, not ingestion.

## Counterexample

- **Suffices (hypothesis, documented basis):** a team that already knows its model and vector store and wants a working RAG or agent app. Building directly in Dify with marketplace components skips a separate planning step, and the DSL gives a shareable, re-importable configuration that Pick Your AI's plan would not execute.
- **Falls short (hypothesis):** it does not advise which model, hardware or hosting fits the workload, does not estimate cost, and a drawn graph does not prove component compatibility. A complementary path is exporting a reviewed plan into Dify DSL (#16/#25).

## Matrix consistency

Pending [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `rag`, `agents`, `deployment`, `saved`, `share`, `export` Documented; `model_versions` Unknown. Agrees.

## Open questions and routing

- #16/#25: whether a DSL export target is worth a contract proposal via #40.
- #41: commercial-licence trigger if Pick Your AI ever hosts Dify for users (multi-tenant clause).
