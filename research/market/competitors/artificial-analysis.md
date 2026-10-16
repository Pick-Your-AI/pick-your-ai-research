# Artificial Analysis — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `artificial-analysis`. Classification: Partial competitor, Benchmark provider, Data source (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | Model/provider leaderboards, Model Recommender, Optima custom benchmarks, Data API (free and commercial) |
| Operator | Artificial Analysis, Inc. (named in the Terms of Use) |
| URLs | [home](https://artificialanalysis.ai/), [Model Recommender](https://artificialanalysis.ai/models/recommend), [API reference](https://artificialanalysis.ai/api-reference), [methodology](https://artificialanalysis.ai/methodology), [Terms of Use](https://artificialanalysis.ai/terms-of-use) |
| Access date | 2026-10-16 |
| Version / revision | Intelligence Index v4.3.2 (10 evaluations); Terms "Last revised: September 15 2026"; Data Platform Terms version per PR #82 |
| Access tier observed | Public pages only; no Insights account or API key |
| robots.txt | Allows all. Terms §3.3 restricts automated queries "to strip, scrape, or mine data" except search indexing, so this review fetched five pages once and extracted no data |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Recommender: "personalized model recommendations based on your priorities for intelligence, speed, and price". Exact inputs render client-side and were not seen | Documented (page metadata); inputs Unknown | [Model Recommender](https://artificialanalysis.ai/models/recommend) |
| Constraints | Priority weighting across intelligence, speed and cost; provider-specific endpoints selectable on charts | Documented / Observed (chart controls in page) | [home](https://artificialanalysis.ai/) |
| Selection logic | Recommender method Unknown; leaderboards rank by indices built from named evaluations | Unknown / Documented | [home](https://artificialanalysis.ai/), [methodology](https://artificialanalysis.ai/methodology) |
| Explanation | Index composition, Pareto charts (intelligence vs cost per task), metric definitions | Observed (page content) | [home](https://artificialanalysis.ai/), [methodology](https://artificialanalysis.ai/methodology) |
| Save/share/export | Free API returns model data (JSON) with a key; share and saved recommendations Unknown | Documented / Unknown | [API reference](https://artificialanalysis.ai/api-reference) |

## Architecture and data

- Data: first-party evaluations (Intelligence Index v4.3.2 incorporates 10 named evaluations) and API performance benchmarks per provider endpoint, e.g. output speed on a 10k-input-token workload measured on the same endpoint used for price. Documented, [methodology](https://artificialanalysis.ai/methodology).
- Identifiers: API docs recommend stable model and creator IDs over slugs. Documented.
- Freshness: home page changelog dated 16 Oct; measurement cadence not recorded here. Observed / Unknown.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free website; free Data API with an account key; commercial API "with more comprehensive data" documented to partners separately | Documented | [API reference](https://artificialanalysis.ai/api-reference) |
| (b) Code licence | Closed service; no public repository | Not applicable | — |
| (c) Data reuse | "Attribution is required for all use of our free API"; use is subject to the Terms of Use and Data Platform Terms. Pending [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82): Data Platform Terms s2.5 bar use, on all tiers, in third-party products whose primary purpose includes model or provider selection guidance, without written consent | Documented (terms); s2.5 cited as pending PR #82 | [API reference](https://artificialanalysis.ai/api-reference), [Terms of Use](https://artificialanalysis.ai/terms-of-use) |

Consequence: Pick Your AI is the product category s2.5 names. Automated retrieval, display and redistribution are no without written consent; manual reading and citation only.

## Counterexample

- **Suffices (hypothesis, documented basis):** an API buyer choosing a hosted model and provider by intelligence/speed/price trade-off. The recommender plus per-endpoint speed and price measurements answer that directly, with stronger first-party measurement than Pick Your AI could reproduce.
- **Falls short (hypothesis):** no documented hardware, self-hosting, retrieval or agent-stack composition; the recommender's inputs and saved output are unverified; its data cannot legally feed a competing selection product, so Pick Your AI cannot simply wrap it.

## Matrix consistency

Pending [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `model_compare`, `explanation`, `model_versions`, `benchmarks`, `api_pricing`, `export`, `api_access` Documented; `saved`, `share` Unknown. Agrees.

## Open questions and routing

- #41/#60: adopt the s2.5 decision; decide whether written consent is worth requesting.
- #66: exercise the recommender in a browser on the shared scenario.
- #36: whether constituent evaluations can be sourced from their original publishers instead.
