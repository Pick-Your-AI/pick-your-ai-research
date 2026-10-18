# OpenRouter — competitor profile

## 2026-10-18 review reconciliation

The [current fourteen-profile review](README.md#2026-10-18-current-profile-review)
adds a 2026-10-18 [routing-documentation](https://openrouter.ai/docs/guides/routing/provider-selection)
read: support requirements, fallback order, hard price filters and soft
performance preferences are distinct. They are not an executed route, complete
bill or performance guarantee. The accepted [#60 source-use restriction](../rights-validation.md)
still applies; public API documentation does not authorize this project's
automated collection. No provider request or data endpoint was called.

## Historical profile retained

The following dated record is unchanged; current interpretation is above.


Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `openrouter`. Classification: Partial competitor, Infrastructure provider, Data source (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | Model directory, unified inference API with provider routing, Models API |
| Operator | OpenRouter, Inc. (named in the Terms of Service) |
| URLs | [models](https://openrouter.ai/models), [Models API guide](https://openrouter.ai/docs/guides/overview/models), [provider selection](https://openrouter.ai/docs/guides/routing/provider-selection), [pricing](https://openrouter.ai/pricing), [terms](https://openrouter.ai/terms) |
| Access date | 2026-10-16 |
| Version / revision | Terms "Last Updated: August 31, 2026"; API docs unversioned |
| Access tier observed | Public documentation and terms only; no account, key or API call |
| robots.txt | Allows all except `/seo/`. The Terms forbid automated scraping (below), so this review read three documentation pages once and did not call `/api/v1/models` |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Directory browsing; Models API query parameters `output_modalities`, `supported_parameters`, `sort` | Documented | [Models API guide](https://openrouter.ai/docs/guides/overview/models) |
| Constraints | Provider routing preferences: price, throughput or latency sorting, percentile performance thresholds, explicit provider order, fallbacks on/off, data-collection/ZDR and in-region routing options | Documented | [provider selection](https://openrouter.ai/docs/guides/routing/provider-selection) |
| Selection logic | Default price-based load balancing across providers for a chosen model; model choice itself is the user's (routers exist; not reviewed) | Documented | [provider selection](https://openrouter.ai/docs/guides/routing/provider-selection) |
| Explanation | Model object exposes architecture, pricing, top-provider and benchmarks fields; no per-user rationale | Documented | [Models API guide](https://openrouter.ai/docs/guides/overview/models) |
| Save/share/export | Models API returns structured JSON (catalog export, not a build); saved/share Unknown | Documented / Unknown | [Models API guide](https://openrouter.ai/docs/guides/overview/models) |

## Architecture and data

- Discovery is coupled to execution: the same account that browses can call any listed model through one API. Documented.
- The default Models response is text-output models only; image, embedding and decision models need an explicit modality or `all`. Documented. Import scope must be explicit.
- Origin: provider-supplied model metadata and OpenRouter-observed endpoint data; freshness is continuous (RSS feed for new models). Documented.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Prepaid credits for usage, optional auto-recharge, credit expiry terms; platform fee structure on the pricing page (rates not recorded) | Documented | [terms](https://openrouter.ai/terms), [pricing](https://openrouter.ai/pricing) |
| (b) Code licence | Closed service | Not applicable | — |
| (c) Data reuse | Terms prohibit using "scripts, robots or ... automated technology) to scrape or copy any information on the Site or the Services", and accessing the service "for purposes of reselling API access to Models or otherwise developing a competing service" | Documented (terms) | [terms](https://openrouter.ai/terms) |

Historical comparison with merged [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82): automated retrieval no (including the public Models API) without written permission; display and redistribution no; manual reading with link only. This profile agrees and adds the "competing service" clause for #41 to interpret.

## Counterexample

- **Suffices (hypothesis, documented basis):** a developer already committed to hosted APIs who needs the cheapest or fastest provider for a known model, with privacy (ZDR, region) constraints and fallbacks. OpenRouter selects and executes in one step; a separate planner is redundant.
- **Falls short (hypothesis):** it does not choose the model for a workload, size self-hosted hardware, or compose retrieval/agent components. Listed prices are not a complete bill (#39).

## Matrix consistency

Historical comparison with merged [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `model_versions`, `export`, `context`, `hosting`, `tool_calling`, `api_pricing`, `api_access` Documented; `saved`, `share` Unknown. Agrees. Routing constraints suggest `constraints` is Documented; proposed to #49, not edited here.

## Open questions and routing

- #41/#60: interpret the "competing service" clause; request written permission if metadata ingestion is wanted.
- #5/#6: map canonical model identity separately from provider endpoint and region.
- #39: price semantics, platform fees and fallback cost.
