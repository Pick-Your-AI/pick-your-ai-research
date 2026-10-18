# Models.dev — competitor profile

## 2026-10-18 review reconciliation

The [current fourteen-profile review](README.md#2026-10-18-current-profile-review)
records a 2026-10-18 [publisher documentation](https://models.dev/) read:
canonical model metadata, provider-specific records, documented exports and
SDK snapshots are distinct. No endpoint payload or model/provider claim was
independently verified. The repository MIT condition and [#60](../rights-validation.md)
integration boundary remain separate from measured capability or artifact
rights; the historical table's unobserved fields do not prove permanent absence.

## Historical profile retained

The following dated record is unchanged; current interpretation is above.


Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `models-dev`. Classification: Data source, Open-source integration candidate, Partial competitor (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | Models.dev open model/provider database (site, JSON endpoints, `@opencode-ai/models` SDK) |
| Operator | OpenCode ("Created by OpenCode"); repository under the anomalyco GitHub organization |
| URLs | [site](https://models.dev/), [repository](https://github.com/anomalyco/models.dev), [licence](https://github.com/anomalyco/models.dev/blob/dev/LICENSE) |
| Access date | 2026-10-16 |
| Version / revision | Default branch `dev`, head `3587a41` (2026-10-16 22:25 UTC) |
| Access tier observed | Public site (first 400 KB of the HTML fetched to stay small) and repository metadata; no JSON endpoint downloaded |
| robots.txt | None served (HTML fallback); no restriction recorded |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Search plus a sortable table of models, labs and providers | Observed | [site](https://models.dev/) |
| Constraints | Columns for context, output, input modalities, reasoning, tool call, structured output, temperature, weights (open/closed), price, release and updated dates | Observed (table headers and rows) | [site](https://models.dev/) |
| Selection logic | None; user sorts and filters | Observed | [site](https://models.dev/) |
| Explanation | None beyond field values | Observed | [site](https://models.dev/) |
| Save/share/export | `api.json`, `models.json`, `catalog.json` (`?type=all` for specialised types); SDK "exports the latest snapshot for offline use"; saved/share Unknown | Documented | [site](https://models.dev/) |

## Architecture and data

- Data stored as TOML files in GitHub "organized by provider and canonical model", edited by pull request. Documented, [site](https://models.dev/).
- Provider records are separated from provider-agnostic canonical model records. Documented. Useful for mapping canonical identity apart from endpoints.
- Freshness: repository commits on the access date; table shows per-row release and updated dates. Observed.
- Specialised model types are omitted from JSON by default. Documented. An importer must set scope explicitly.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free; no paid tier found | Observed (absence of pricing is not proof) | [site](https://models.dev/) |
| (b) Code licence | SPDX `MIT` (`gh api repos/anomalyco/models.dev/license`) | Observed | [licence](https://github.com/anomalyco/models.dev/blob/dev/LICENSE) |
| (c) Data reuse | Data lives in the MIT repository; provider logos and upstream provider facts may carry trademark or provider terms | Observed / hypothesis for upstream | [repository](https://github.com/anomalyco/models.dev) |

Historical comparison with merged [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82): all four uses Yes with the MIT notice. This profile agrees; logos and trademarks remain a #41 question.

## Counterexample

- **Suffices (hypothesis, observed table):** a developer comparing hosted models on context, tool-call support and price can sort one table and pull JSON. For catalogue lookup Pick Your AI is redundant, and models.dev is a likely input rather than a rival.
- **Falls short (observed):** no workload intake, recommendation, explanation, hardware or self-hosting dimension.

## Matrix consistency

Historical comparison with merged [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `model_search`, `model_compare`, `model_versions`, `context`, `api_pricing`, `export`, `api_access` Documented; `saved`, `share` Unknown. Agrees.

## Open questions and routing

- #5/#6: identifier mapping and mismatches against primary provider docs; keep market IDs separate from CatalogItem IDs.
- #41: trademark/logo use and per-provider data restrictions.
