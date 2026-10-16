# BenchLM — competitor profile

Status: draft for owner review ([#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)). Entity ID: `benchlm`. Classification: Partial competitor, Benchmark provider, Data source (analyst judgement). Evidence classes are defined in the [index](README.md#evidence-classes).

| Field | Value |
| --- | --- |
| Product | BenchLM leaderboard, LLM Selector, AI App Stack reference, Data (REST/MCP) |
| Operator | BenchLM (legal entity not stated on the pages fetched) |
| URLs | [home](https://benchlm.ai/), [LLM Selector](https://benchlm.ai/tools/llm-selector), [AI App Stack](https://benchlm.ai/stack), [data access](https://benchlm.ai/data/access), [methodology](https://benchlm.ai/methodology), [terms](https://benchlm.ai/terms) |
| Access date | 2026-10-16 |
| Version / revision | Selector method `bench-align-v5.8-2026-09-30`; methodology: BenchAlign v5.8, source refresh 2026-10-15; terms "Last updated: October 2, 2026" |
| Access tier observed | Public pages only; no account, API key or MCP connection |
| robots.txt | Allows `/`; disallows `/api/` and `/admin/`. The `/api/tools/recommend` endpoint was not called |

## Workflow

| Stage | Finding | Class | Source |
| --- | --- | --- | --- |
| Inputs | Selector accepts a free-text job description (2,000 characters) plus chips for kind of work, processing location (hosted vs own hardware), budget, input size and what would make a model wrong | Observed (form present in page) | [LLM Selector](https://benchlm.ai/tools/llm-selector) |
| Constraints | Budget, context and local-deployment requirements narrow candidates; unstated answers become marked defaults | Documented | [LLM Selector](https://benchlm.ai/tools/llm-selector) |
| Selection logic | A "decision model" only fills the form; the shortlist is computed in the page from the dataset across 31 tasks; unsupported tasks get an evidence gap instead of a recommendation | Documented; independence of the decision model is a vendor claim | [LLM Selector](https://benchlm.ai/tools/llm-selector) |
| Explanation | Each model is placed as shortlisted, filtered by a stated constraint, below the cut, or without evidence; rows carry Supported/Estimated labels | Documented | [LLM Selector](https://benchlm.ai/tools/llm-selector), [methodology](https://benchlm.ai/methodology) |
| Save/share | Answers are written into the URL; the free-text description is excluded; the link "reopens the same shortlist against the current dataset" (not pinned to a data version) | Documented | [LLM Selector](https://benchlm.ai/tools/llm-selector) |
| Export | Website downloads and CSV; REST/MCP data with an account | Documented (not downloaded) | [terms](https://benchlm.ai/terms), [data access](https://benchlm.ai/data/access) |
| Multi-layer guidance | AI App Stack lists six layers (model, data, orchestration, hosting, interface, observability) with editorial roundups and partner-link disclosure | Observed (page content) | [AI App Stack](https://benchlm.ai/stack) |

The shortlist itself was not generated: it runs client-side and hands-on testing belongs to [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66).

## Architecture and data

- Data: benchmark results, external composite indices and preference signals calibrated by BenchAlign; runtime metrics kept separate from scores; list prices. Origin: third-party publishers plus BenchLM-compiled outputs. Documented, [methodology](https://benchlm.ai/methodology).
- Freshness: per-benchmark version, refresh cadence and staleness state are documented; the home page showed a snapshot dated 2026-10-16. Documented / Observed.
- Exact model-to-provider revision pinning: Unknown.

## Commercial access, code licence and data rights

| Layer | Finding | Class | Source |
| --- | --- | --- | --- |
| (a) Commercial access | Free web use; Data service with a free read allowance and paid tiers adding reads and history; site and newsletter sponsorship; partner (affiliate) links on tool roundups. Rates not recorded | Documented | [data access](https://benchlm.ai/data/access), [AI App Stack](https://benchlm.ai/stack) |
| (b) Code licence | No public source repository identified; not applicable / Unknown | Unknown | — |
| (c) Data reuse | Terms: the public website dataset is "licensed under CC BY-NC 4.0"; commercial use "requires a separate license". Data plans cover "queries and internal analysis"; commercial display needs "a separate display agreement". Publisher measurements keep their own licences | Documented (terms) | [terms](https://benchlm.ai/terms), [data access](https://benchlm.ai/data/access) |

Consistent with pending [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82) (commercial display: no; redistribution: no). The CC BY-NC licence on website downloads is an additional finding for #41/#60 to confirm.

## Counterexample

- **Suffices (hypothesis, documented basis):** a user choosing one hosted API model for a single stated task under a budget. The selector takes a plain-language job, applies budget/context/local constraints, explains exclusions and gives a shareable link. Pick Your AI adds little for that segment.
- **Falls short (hypothesis):** a joint multi-component configuration. The stack page is per-layer editorial guidance, not a computed, compatibility-checked combination of hardware, runtime, retrieval and hosting. Shared links re-evaluate against the current dataset, so a historical recommendation is not reproducible as a versioned record. Both gaps are documented-surface readings, not tested absences.

## Matrix consistency

Pending [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87): `share` Documented, `export` Documented, `model_versions` Documented, `saved` Unknown. This profile agrees; the selector's URL state is sharing, not a saved versioned build, so `saved` stays Unknown. `natural_language`, `constraints` and `guided_selection` appear Documented on the selector page but are Unknown in #87; proposed to #49, not edited here.

## Open questions and routing

- #41/#60: confirm CC BY-NC scope of website downloads versus Data service outputs.
- #66: run the selector on the shared scenario and record the shortlist and URL round-trip.
- #6: compare BenchAlign task mapping with T1 model-selection inputs.
