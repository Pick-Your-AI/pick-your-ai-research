# MR-08: Validate commercial display and redistribution rights

Issue: [#60](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60). Live assignees (2026-10-18): @tynamite and @appletechie. Status: ten-source decisions recorded; #41/#5/#6/#27 scoped receipts linked below; remaining source-use decisions prepared for independent integration review. Initial terms audit: 2026-10-16; the bounded 2026-10-18 recheck is identified separately.

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
- Where no applicable licence or terms grant is established, commercial display and redistribution are **no for the project's current intake**. This is a conservative project exclusion, not a finding that missing documentation proves a legal prohibition; the unestablished legal scope remains unknown.
- **Unclear** describes existing terms whose applicable scope is ambiguous. A project exclusion can still be chosen while that legal question is unresolved; it does not turn the unknown into a publisher prohibition or a permission grant.
- A licence on a compilation covers that compilation. Upstream measurements keep their own rights.

This is a reading of published terms for project decisions, not legal advice. Escalate before any commercial launch.

## Decisions

Each permission applies only to its stated source material, use and conditions. A conditional publisher licence does not itself approve Pick Your AI's product use. The proposed current-product exclusion for GPUs.io is recorded below; placing a value inside a build estimate does not resolve its broader competition restriction.

| Source | Terms checked | Automated retrieval | Internal research | Commercial display | Redistribution | Conditions |
| --- | --- | --- | --- | --- | --- | --- |
| models.dev | [MIT licence](https://github.com/anomalyco/models.dev/blob/dev/LICENSE) | Yes | Yes | Yes | Yes | Keep the MIT notice |
| ModelFit dataset | [Dataset page](https://modelfit.io/data/): CC BY 4.0 | Yes | Yes | Yes | Yes | Credit "ModelFit (modelfit.io)", link the licence, indicate changes. Figures are ModelFit estimates. |
| llmfit | [MIT licence](https://github.com/AlexsJones/llmfit/blob/main/LICENSE) | Yes | Yes | Yes | Yes | Keep the MIT notice. Covers repository data, not llmfit.org website content. |
| MCP registry | [Licence](https://github.com/modelcontextprotocol/registry/blob/main/LICENSE); [ecosystem vision](https://github.com/modelcontextprotocol/registry/blob/main/docs/design/ecosystem-vision.md); [design principles](https://github.com/modelcontextprotocol/registry/blob/main/docs/design/design-principles.md) | Yes | Yes | Yes | Yes | The design expects subregistries to ETL, cache and serve its metadata. A listing is not a certification; keep our annotations separate. Server code keeps its own licence. |
| Hugging Face Hub | [Terms of service](https://huggingface.co/terms-of-service) | Yes | Yes | Yes | No | Display factual identifiers (id, revision, declared licence, size) with a link. Model-card text, files and redistribution only where the repository's licence allows; the ToS grant covers use through Hugging Face's services only. |
| Harness Bench | [Pinned repository](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863) (no repository-wide licence found); [paper v2](https://arxiv.org/abs/2605.27922v2) (CC BY 4.0) | Internal research only | Yes | Paper only | Paper under CC BY 4.0; repository no | Retain the paper authors, title/version, source and licence links, notices and change indications. Its licence does not grant rights to separate repository tasks, code, trajectories or catalogue files. |
| GPUs.io | [Terms](https://gpus.io/en/terms), last updated 2026-06-05 | Yes | Yes | Yes | No | Paid API and linked attribution are conditional on all terms. Section 5 prohibits competing-product/service use; section 6 restricts repackaging and bulk extraction. Placing values in a build estimate is not an exemption. |
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

- **Conditionally available for commercial display:** models.dev, ModelFit, llmfit, MCP registry metadata, Hugging Face factual identifiers and Harness Bench paper results, within the exact material and notice conditions above. Source rights are distinct from verified technical accuracy and product integration acceptance.
- **Not usable without an agreement:** BenchLM-owned outputs, Artificial Analysis data, and automated OpenRouter collection. Source benchmark results from their original publishers instead.
- **Proposed #39 decision: exclude GPUs.io from the current product scope.** Do not retrieve its API data for the product or display/export its values. Use separately reviewed original provider sources instead. This resolves the current integration choice without asserting that Pick Your AI satisfies the competition restriction. Reconsider only with a specific permitted-use basis, such as written permission that covers the proposed product, and a new #39/#41/#60 review.

## Protocol

- [x] Inspect exact licence scope per source
- [x] Record BenchLM agreement requirement
- [x] Confirm upstream rights for compiled data: compilation licences cover the compilations (models.dev, ModelFit, llmfit); upstream measurements keep their own rights (BenchLM states this)
- [x] Approve or reject each intended use (table above)
- [x] Record exact source, version or date, conditions, failures and confidence (`integrations.json`)
- [ ] Finish the exact receiving dispositions below. Existing #41/#5/#6/#27 receipts retain their stated scope; the current #41 table, #39 exclusion and #36/#62 paper-only boundaries require actual receiving-owner review.

## Bounded source recheck — 2026-10-18

| Source / exact scope | Primary evidence read | Finding and limit |
| --- | --- | --- |
| GPUs.io service and data | [Terms](https://gpus.io/en/terms), dated 2026-06-05, sections 3, 5–7 | The competing-product restriction remains distinct from conditional API access/display. The current-product exclusion is a project decision, not a legal exemption. |
| Harness-Bench paper | [arXiv v2 licence link](https://arxiv.org/abs/2605.27922v2) and [CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode.en), sections 2–3 | The licence permits sharing/adaptation of the licensed paper with the required attribution, notices and change indication. Preserve author/version identity; no endorsement is implied. Separate repository material is outside that paper licence. |
| Harness-Bench repository | [Root tree at `b8d8963`](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863); GitHub repository licence metadata | The complete root listing has no repository-wide licence file and GitHub reports no detected licence. No permission for the task/code/trajectory collection is inferred; third-party material keeps its own terms. |
| BenchLM service versus upstream measurements | [Data access](https://benchlm.ai/data/access), commercial-use section; [Terms](https://benchlm.ai/terms), dated 2026-10-02 | Access plans do not grant commercial display or feed redistribution. Independently licensed publisher measurements retain their own rights; attributed quotations/standard embeds keep their separately stated permissions. No agreement was obtained. |

These are source-checked policy observations. The other seven shortlisted sources retain their earlier audit date; this pass does not claim to have rechecked their terms. No account, paid data feed, task package or provider workload was used.

## Receiving decisions and criterion map

Independent integration review may evaluate this partial research for publication. It does not satisfy the separate receiving-owner acceptance required by live #60. The offered decisions below remain proposals until the relevant consuming owners record their scoped accept, narrow or reject dispositions. Any new receipt must state the actual reviewer, immutable research revision, exact scope and remaining conditions. Prior owner receipts retain their historical scope and do not transfer to another source or consumer.

| Handoff | Actual recorded receipt or offered decision | Remaining boundary |
| --- | --- | --- |
| #60 → #41 | [tynamite accepted adoption](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6235704731), incorporated in the merged #41 record. **Offered now:** accept the qualified current source/material table and proposed GPUs.io exclusion | Changed material/terms/use returns to #60/#41; the older receipt does not pre-approve this follow-up. |
| #60 → #5/#6 | [zwright8 accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6242698806) at `7acbefbf` | Preserve source notices, estimates, dataset/website boundaries and the excluded sources; no general upstream-content grant. |
| #60 → #27 | [CompleteDotTech accepted the MCP metadata scope](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6244042769) against registry `11b7b0e` | Retain applicable notices, provenance and separate annotations; listing is not security or compatibility certification. |
| #60 → #39 | **Offered:** accept the exclusion of GPUs.io from current product use; retain the publisher's conditional permission as source evidence only | Original-provider price sources still need their own rights and applicability review. No paid API use or commercial clearance is implied. |
| #60 → #36/#62 | **Offered:** accept the paper-versus-repository boundary and exclude unlicensed repository tasks/trajectories and unlicensed BenchLM-owned outputs/feeds | Paper permission does not validate its model/grader pins, result dependence, claims or comparability. The #62 negative desk finding remains separate from any future experiment. |

| Live #60 criterion | Reviewable evidence |
| --- | --- |
| Inspect exact licence scope per source | Ten-source table, source/use conditions in integrations.json, and the dated recheck above |
| Record BenchLM agreement requirement | Separate display/feed agreement boundary; upstream publisher rights remain distinct |
| Confirm upstream rights for compiled data | Compilation rights do not grant every upstream measurement or artifact; retain per-source material boundaries and exclude unestablished uses |
| Approve or reject each intended use | Four-use table plus the concrete proposed GPUs.io product exclusion; no missing permission is treated as a grant |
| Significant conclusions linked to evidence or hypothesis | Primary terms, exact repository/paper identities and explicit project decisions |
| Relevant technical owners review handoffs; unresolved decisions named | Exact prior receipts plus the offered consumer scopes above; actual receiving-owner acceptance of the new scopes remains pending |
| Checks pass; reviewer accepts evidence before Done | Final PR checks and exact scoped review are required; no new local validation result is claimed in this prepared package |

## Result

The ten-source research audit supports a restrictive intake policy. Excluding a source or material when its required permission is unestablished makes the proposed intake boundary concrete without obtaining an agreement or collecting its data. The new exclusion and remaining receiving scopes remain proposals for the consuming owners. A reviewed merge publishes this partial research; #60 remains open until its criterion-specific decisions and required receiving-owner receipts are recorded and its complete deliverable is reviewed and merged. Consumers: #41, #39, #5, #6, #27, #36, #62.
