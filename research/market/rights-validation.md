# MR-08: Validate commercial display and redistribution rights

Issue: [#60](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60). Owner: @tynamite. Status: decisions recorded for the 10 shortlisted sources; adoption by #41 pending. Terms checked: 2026-10-16.

## Question

Can the shortlisted data be displayed or redistributed commercially?

## Intended uses

| Use | Meaning |
| --- | --- |
| Automated retrieval | The project fetches the data by API, export or clone, rather than a person reading it |
| Internal research | Read, analyse and cite in research notes (short paraphrase with a link) |
| Commercial display | Show the data's values to users of a commercial Pick Your AI product |
| Redistribution | Make the data available to others in bulk: export, API, feed or dataset |

## Decision rule

- The publisher's own licence or terms decide. A stated limitation beats a capability listing from the same publisher; for example, a terms clause against automated copying beats the existence of a public API (#41 interim conflict order, step 4).
- Where no licence or terms grant is found, commercial display and redistribution are **no**.
- **Unclear** is reserved for terms that exist but are ambiguous. None of the 10 sources needed it.
- A licence on a compilation covers that compilation. Upstream measurements keep their own rights.

This is a reading of published terms for project decisions, not legal advice. Escalate before any commercial launch.

## Decisions

| Source | Terms checked | Automated retrieval | Internal research | Commercial display | Redistribution | Conditions |
| --- | --- | --- | --- | --- | --- | --- |
| models.dev | [MIT licence](https://github.com/anomalyco/models.dev/blob/dev/LICENSE) | Yes | Yes | Yes | Yes | Keep the MIT notice |
| ModelFit dataset | [Dataset page](https://modelfit.io/data/): CC BY 4.0 | Yes | Yes | Yes | Yes | Credit "ModelFit (modelfit.io)", link the licence, indicate changes. Figures are ModelFit estimates. |
| llmfit | [MIT licence](https://github.com/AlexsJones/llmfit/blob/main/LICENSE) | Yes | Yes | Yes | Yes | Keep the MIT notice. Covers repository data, not llmfit.org website content. |
| MCP registry | [Licence](https://github.com/modelcontextprotocol/registry/blob/main/LICENSE); [ecosystem vision](https://github.com/modelcontextprotocol/registry/blob/main/docs/design/ecosystem-vision.md); [design principles](https://github.com/modelcontextprotocol/registry/blob/main/docs/design/design-principles.md) | Yes | Yes | Yes | Yes | The design expects subregistries to ETL, cache and serve its metadata. A listing is not a certification; keep our annotations separate. Server code keeps its own licence. |
| Hugging Face Hub | [Terms of service](https://huggingface.co/terms-of-service) | Yes | Yes | Yes | No | Display factual identifiers (id, revision, declared licence, size) with a link. Model-card text, files and redistribution only where the repository's licence allows; the ToS grant covers use through Hugging Face's services only. |
| Harness Bench | [Repository](https://github.com/Qihoo360/harness-bench) (no licence); [paper](https://arxiv.org/abs/2605.27922) (CC BY 4.0) | Yes | Yes | Yes | No | Display only results and text published in the paper, attributed and pinned to v2. Repository tasks, trajectories and catalogue files have no licence. |
| GPUs.io | [Terms](https://gpus.io/en/terms), last updated 2026-06-05 | Yes | Yes | Yes | No | Through the paid API only, with "Pricing data by GPUs.io" and a link. Values inside a build's cost estimate, not a standalone GPU price comparison: the terms bar competing comparison services. |
| BenchLM | [Data access, commercial use](https://benchlm.ai/data/access) | Yes | Yes | No | No | Plans cover internal analysis only. Display and redistribution need separate agreements. Individual quotations and attributed embeds keep their permissions. |
| OpenRouter | [Terms](https://openrouter.ai/terms), last updated 2026-08-31 | No | Yes | No | No | The terms prohibit automated scraping or copying of site or service information. Needs written permission. |
| Artificial Analysis | [Terms of use](https://artificialanalysis.ai/docs/legal/Terms-of-Use.pdf) v1.0; [Data Platform Terms](https://artificialanalysiscdn.com/legal/ProDataPlatformTerms.pdf) | No | Yes | No | No | Data Platform Terms s2.5, on all tiers including the free API, bar using the Data for third-party products whose primary purpose includes model or provider selection guidance, without written consent. Internal research means manual reading and citation only. |

Per-source evidence, update cadence and next actions are recorded in [integrations.json](integrations.json).

## What this changes in #67's starting notes

- **GPUs.io** has published terms and a paid API; both were recorded as unknown.
- **Artificial Analysis**: commercial display isn't just "requires review". Its terms bar this product category without written consent.
- **Harness Bench**: the paper is CC BY 4.0, so its published results can be shown with attribution. The repository has no licence, so its tasks, trajectories and catalogue cannot be reused.
- **MCP registry**: downstream republishing is the intended use, not an open question.
- **OpenRouter**: automated collection, including through its public API, needs written permission.

## Consequences

- **Usable for commercial display now:** models.dev, ModelFit, llmfit, MCP registry metadata, Hugging Face factual identifiers, Harness Bench paper results, and GPUs.io values under the conditions above.
- **Not usable without an agreement:** BenchLM-owned outputs, Artificial Analysis data, and automated OpenRouter collection. Source benchmark results from their original publishers instead.
- **#39:** decide whether the cost feature could count as a competing GPU price comparison before using GPUs.io data.

## Protocol

- [x] Inspect exact licence scope per source
- [x] Record BenchLM agreement requirement
- [x] Confirm upstream rights for compiled data: compilation licences cover the compilations (models.dev, ModelFit, llmfit); upstream measurements keep their own rights (BenchLM states this)
- [x] Approve or reject each intended use (table above)
- [x] Record exact source, version or date, conditions, failures and confidence (`integrations.json`)
- [ ] Obtain affected-owner review and accepted handoff: #41 (adopt the decisions), #39 (GPUs.io condition), #5/#6 (model-metadata sources), #27 (MCP registry), #36/#62 (Harness Bench)

## Result

Decisions are recorded for all 10 shortlisted sources from their primary licence and terms pages, accessed 2026-10-16. No source data was downloaded or redistributed in this check. Consumers: #41, #39, #5, #6, #27, #36, #62.
