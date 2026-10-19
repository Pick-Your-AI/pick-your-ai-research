# MR-08: Validate commercial display and redistribution rights

Issue: [#60](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60). Live assignees (2026-10-18): @tynamite and @appletechie. Research disposition: ten-source intended-use boundaries and scoped engineering receiving decisions recorded below. Initial terms audit: 2026-10-16; the two bounded 2026-10-18 source checks retain their separate scope.

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

- The publisher's own licence or terms decide. A stated limitation beats a capability listing from the same publisher; for example, a terms clause against automated copying beats the existence of a public API ([accepted #41 conflict order](../T0-configuration/catalog-data-sources.md#conflict-resolution), step 4).
- Where no applicable licence or terms grant is established, commercial display and redistribution are **no for the project's current intake**. This is a conservative project exclusion, not a finding that missing documentation proves a legal prohibition; the unestablished legal scope remains unknown.
- **Unclear** describes existing terms whose applicable scope is ambiguous. A project exclusion can still be chosen while that legal question is unresolved; it does not turn the unknown into a publisher prohibition or a permission grant.
- A licence on a compilation covers that compilation. Upstream measurements keep their own rights.

This is a reading of published terms for project decisions, not legal advice. Escalate before any commercial launch.

## Decisions

Each permission applies only to its stated source material, use and conditions. A conditional publisher licence does not itself approve Pick Your AI's product use. The accepted current-product exclusion for GPUs.io is recorded below; placing a value inside a build estimate does not resolve its broader competition restriction.

| Source | Terms checked | Automated retrieval | Internal research | Commercial display | Redistribution | Conditions |
| --- | --- | --- | --- | --- | --- | --- |
| models.dev | [MIT licence](https://github.com/anomalyco/models.dev/blob/84a113860a478edfbbf42c8cce4d7ad76fa48d9d/LICENSE) | Yes | Yes | Yes | Yes | Keep the MIT notice |
| ModelFit dataset | [Terms section 7](https://modelfit.io/terms/), [dataset page](https://modelfit.io/data/) and [mirror licence at 6fa130db](https://github.com/Wecko-ai/modelfit-hardware-dataset/blob/6fa130db0efa61a5b7ac242fb400c632ab730c52/LICENSE): CC BY 4.0 | Yes | Yes | Yes | Yes | Credit "ModelFit (modelfit.io)", link the licence, indicate changes. Figures are ModelFit estimates. |
| llmfit | [MIT licence](https://github.com/AlexsJones/llmfit/blob/e915091dd58f7fefaa9814d2d34ee61bd754fdc0/LICENSE) | Yes | Yes | Yes | Yes | Keep the MIT notice. Covers repository data, not llmfit.org website content. |
| MCP registry | [Licence](https://github.com/modelcontextprotocol/registry/blob/11b7b0e274d518b6f449c5ee3518a6151d9848b9/LICENSE); [ecosystem vision](https://github.com/modelcontextprotocol/registry/blob/11b7b0e274d518b6f449c5ee3518a6151d9848b9/docs/design/ecosystem-vision.md); [design principles](https://github.com/modelcontextprotocol/registry/blob/11b7b0e274d518b6f449c5ee3518a6151d9848b9/docs/design/design-principles.md) | Yes | Yes | Yes | Yes | The design expects subregistries to ETL, cache and serve its metadata. A listing is not a certification; keep our annotations separate. Server code keeps its own licence. |
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
- **Harness Bench**: paper material can be used within its CC BY 4.0 scope and notice conditions. The separately unlicensed repository tasks, trajectories and catalogue remain excluded from the project's current intake because no applicable reuse grant was established in the bounded audit below. That exclusion does not turn unestablished legal scope into a finding about every possible use.
- **MCP registry**: downstream republishing is the intended use, not an open question.
- **OpenRouter**: automated collection, including through its public API, needs written permission.

## Consequences

- **Conditionally available for commercial display:** models.dev, ModelFit, llmfit, MCP registry metadata, Hugging Face factual identifiers and Harness Bench paper results, within the exact material and notice conditions above. Source rights are distinct from verified technical accuracy and product integration acceptance.
- **Not usable without an agreement:** BenchLM-owned outputs, Artificial Analysis data, and automated OpenRouter collection. Source benchmark results from their original publishers instead.
- **Accepted #39/#41 project decision: exclude GPUs.io from the current product scope.** See the [actual delegated engineering receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771) and bounded receiving scope below. Do not retrieve its API data for the product or display/export its values. Use separately reviewed original provider sources instead. This resolves the current integration choice without asserting that Pick Your AI satisfies the competition restriction. Reconsider only with a specific permitted-use basis, such as written permission that covers the proposed product, and a new #39/#41/#60 review.

## Protocol

- [x] Inspect exact licence scope per source
- [x] Record BenchLM agreement requirement
- [x] Confirm upstream rights for compiled data: compilation licences cover the compilations (models.dev, ModelFit, llmfit); upstream measurements keep their own rights (BenchLM states this)
- [x] Approve or reject each intended use (table above)
- [x] Record exact source, version or date, conditions, failures and confidence (`integrations.json`)
- [x] Record the exact receiving dispositions below. Historical #41/#5/#6/#27 receipts retain their stated scope. The current #41 table, #39 exclusion and #36/#62 material boundaries have actual delegated project engineering review; this does not manufacture a publisher grant or another assignee's response.

## Bounded source recheck — 2026-10-18

| Source / exact scope | Primary evidence read | Finding and limit |
| --- | --- | --- |
| GPUs.io service and data | [Terms](https://gpus.io/en/terms), dated 2026-06-05, sections 3, 5–7 | The competing-product restriction remains distinct from conditional API access/display. The current-product exclusion is a project decision, not a legal exemption. |
| Harness-Bench paper | [arXiv v2 licence link](https://arxiv.org/abs/2605.27922v2) and [CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode.en), sections 2–3 | The licence permits sharing/adaptation of the licensed paper with the required attribution, notices and change indication. Preserve author/version identity; no endorsement is implied. Separate repository material is outside that paper licence. |
| Harness-Bench repository | [Root tree at `b8d8963`](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863); GitHub repository licence metadata | The complete root listing has no repository-wide licence file and GitHub reports no detected licence. No permission for the task/code/trajectory collection is inferred; third-party material keeps its own terms. |
| BenchLM service versus upstream measurements | [Data access](https://benchlm.ai/data/access), commercial-use section; [Terms](https://benchlm.ai/terms), dated 2026-10-02 | Access plans do not grant commercial display or feed redistribution. Independently licensed publisher measurements retain their own rights; attributed quotations/standard embeds keep their separately stated permissions. No agreement was obtained. |

These are the earlier bounded source-checked policy observations. That pass did not recheck the other seven shortlisted sources. Their historical observations remain intact; the separate ten-source check below records what was subsequently read. No account, paid data feed, task package or provider workload was used.

## Ten-source material check and ModelFit resolution — 2026-10-18

The in-session research engineer read the following public primary documents;
the independent root engineering reviewer checked the same ten material
boundaries. Evidence class is **Primary documentation** for the licence/terms
text and **project engineering decision** for the resulting intake constraints.
Confidence is high in the recorded text and exact repository identity, limited
to the material and clauses read; applicability to uninspected upstream material
and future product uses remains unknown. Region is not applicable to this
documentary check. Mutable pages are dated observations, without a claim of
permanent legal freshness. No payload equivalence, integration, estimator
calibration or provider workload was tested.

| Source / publisher | Exact primary evidence read | Material boundary and limitation |
| --- | --- | --- |
| models.dev / anomalyco | [MIT LICENSE at 84a11386](https://github.com/anomalyco/models.dev/blob/84a113860a478edfbbf42c8cce4d7ad76fa48d9d/LICENSE) | Retain the repository MIT notice. No grant for third-party model binaries, provider branding or upstream measurements follows from it. |
| ModelFit / Wecko AI | [Terms](https://modelfit.io/terms/), updated 2026-10-01, sections 2/6/7; [publisher dataset page](https://modelfit.io/data/); publisher-linked [mirror LICENSE](https://github.com/Wecko-ai/modelfit-hardware-dataset/blob/6fa130db0efa61a5b7ac242fb400c632ab730c52/LICENSE) and [README](https://github.com/Wecko-ai/modelfit-hardware-dataset/blob/6fa130db0efa61a5b7ac242fb400c632ab730c52/README.md) | The dataset is CC BY 4.0; the CLI is separately MIT, and the mirror generation script is additionally MIT. This resolves the old mirror-licence-file question. Credit, licence link, changes and estimate labels remain necessary. Separate upstream benchmark rights and actual payload equivalence remain unestablished. |
| llmfit / Alex Jones | [MIT LICENSE at e915091d](https://github.com/AlexsJones/llmfit/blob/e915091dd58f7fefaa9814d2d34ee61bd754fdc0/LICENSE) | Preserve the repository notice. The seed website's ownership/content and third-party models or measurements remain separate; no site permission or hardware calibration is inferred. |
| MCP registry / Model Context Protocol | [LICENSE](https://github.com/modelcontextprotocol/registry/blob/11b7b0e274d518b6f449c5ee3518a6151d9848b9/LICENSE), [ecosystem vision](https://github.com/modelcontextprotocol/registry/blob/11b7b0e274d518b6f449c5ee3518a6151d9848b9/docs/design/ecosystem-vision.md) and [design principles](https://github.com/modelcontextprotocol/registry/blob/11b7b0e274d518b6f449c5ee3518a6151d9848b9/docs/design/design-principles.md) | New/consented Apache-2.0 code, legacy MIT code and CC BY 4.0 documentation are distinct. Downstream metadata ETL, serving, caching and annotations are intended; server package code/binaries retain their own licences. Listing is not certification. |
| Hugging Face Hub / Hugging Face | [Terms](https://huggingface.co/terms-of-service), Your Content and Intellectual Property sections | Public-content permissions operate through the Services and preserve accompanying licences. Retain the factual-identifier intake boundary; model-card text, weights, datasets, service code and branding need their own applicable basis. |
| OpenRouter / OpenRouter | [Terms](https://openrouter.ai/terms), updated 2026-08-31, sections 7/12 | Automated copying and competitive-service restrictions remain applicable; public API documentation supplies no contrary permission. Retain excluded automated collection and commercial republication. |
| Artificial Analysis / Artificial Analysis | [Site terms](https://artificialanalysis.ai/docs/legal/Terms-of-Use.pdf), sections 2.1–2.2; [Data Platform Terms](https://artificialanalysiscdn.com/legal/ProDataPlatformTerms.pdf), sections 2.4–2.5/4.2 | The site licence is personal/noncommercial; data terms separately restrict raw redistribution and third-party benchmarking/ranking/selection products without consent. Retain the current product exclusion; no consent or paid agreement was obtained. |
| BenchLM / BenchLM | [Data access](https://benchlm.ai/data/access), Commercial display or redistribution section | Query/internal-analysis access does not cover commercial display or redistribution of BenchLM-owned outputs or compiled feeds. Original publishers' measurements and separately permitted quotations/embeds retain their own conditions. No separate agreement was obtained. |
| Harness-Bench / paper authors and Qihoo360 repository | [arXiv v2 landing/licence link](https://arxiv.org/abs/2605.27922v2), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); complete [root at b8d8963](https://github.com/Qihoo360/harness-bench/tree/b8d89634c6f445fcc68ceb6744a59bef6cdf4863) | The licensed paper and separate task/code/trajectory collection are distinct. The exact root has no repository-wide licence file; this bounded root check is not a claim that every nested file lacks a licence. Exclude unestablished repository reuse and retain paper attribution/version/notices. |
| GPUs.io / GPUs.io | [Terms](https://gpus.io/en/terms), updated 2026-06-05, sections 3/5/6/7 | Conditional paid API/display clauses coexist with competition and bulk-redistribution restrictions. The product excludes retrieval/display/export without claiming eligibility for an exception. |

The original access-date and update-cadence observations in
[integrations.json](integrations.json) are unchanged. Only ModelFit's
last-check date, explicit recheck scope and completed mirror next action advance
for the newly resolved question. Its previous API/mirror-update observations
are not refreshed by reading a licence. The new source links and current
technical dispositions are additional evidence, not backdated owner receipts.

## Receiving decisions and criterion map

The [scoped receiving receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771) records actual in-session research
and independent root engineering work under the user's delegated project
engineering mandate. It accepts the stated **technical research inputs and
conservative project exclusions**. It does not speak as an unparticipating
GitHub assignee, waive an external permission, or approve a production feed.
Live assignees and all earlier receipts are retained.

The receipt explicitly identifies accepted main
[2f307a10](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/2f307a10ef98a8c7c711ef28ba35c6246d36f9fd)
and published #294 source
[86fa60c4](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/86fa60c445dbd29197ca576af6ae633a7943ca74),
with the exact primary pins above. The latter's unchanged tree is delivered on
signed main at [3f863edb](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/3f863edbf2dd0470b26dc108f1b3f706f5ae93ad).
The research engineer inspected the linked
hosting, cost, source-policy, evaluation and benchmark consumer boundaries.
The root engineer independently reviewed the source scopes and accepted the
specific decisions below. Final review of this canonical amendment and its
validation are recorded on its PR; the earlier #294 integrity review is not
relabelled as acceptance of later edits.

| Handoff | Actual disposition | Retained boundary |
| --- | --- | --- |
| #60 → #41 | Accept the current qualified ten-source material/use table and GPUs.io product exclusion through the scoped engineering receipt. Preserve [tynamite's earlier adoption](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6235704731) at its historical scope. | Changed material, terms or use returns to #60/#41. Unknown upstream rights remain unknown and excluded; source rights are separate from correctness and publication qualification. |
| #60 → #5/#6 | Preserve [zwright8's accepted constrained intake](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6242698806) at 7acbefbf. | Source notices, estimates, dataset/website boundaries and excluded uses remain. No broader grant for weights, cards or measurements is inferred. |
| #60 → #27 | Preserve [CompleteDotTech's accepted MCP metadata scope](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6244042769), pinned to registry 11b7b0e. | Retain applicable notices, provenance and separate annotations; listing is not security or compatibility certification. |
| #60 → #39 | Accept exclusion of GPUs.io from current product API retrieval, display and export. The [cost record](../T6-deployment-operations/cost-estimate.md#review-corrections-and-governing-decisions-2026-10-17) records the same scoped decision. | Conditional publisher clauses remain evidence only. Original-provider price sources need separate rights, region, meter and applicability review. Reconsider exclusion only with a specific permitted-use basis and new #39/#41/#60 review. |
| #60 → #36/#62 | Accept the licensed-paper versus separate repository/service material boundary, as used by the [evaluation record](../T6-deployment-operations/evaluation.md#reproducibility-criteria-for-displayed-benchmark-comparisons) and [benchmark note](benchmark-validation.md). | Exclude unestablished repository tasks/trajectories and BenchLM-owned feeds. A licence supplies no missing model/grader/result pins, paired evidence or comparable score. #62's unmet experimental-identity criterion and any future experiment remain its own work. |

### Related #55 shortlist receiving decisions

These are distinct from #60's rights dispositions; the historical #60 → #27
response is not transferred onto #55. The same current receipt explicitly
reviews the newly completed #55 scopes.

| Handoff | Accepted research use | Evidence and boundary |
| --- | --- | --- |
| #55 → #9 | Source discovery and maintenance planning | [Hosting comparison/evidence fields](../T2-infrastructure/hosting.md) retain provider/offering/region, exact units and dated observations. A rank is not a current quote, available capacity, measurement or SLA. |
| #55 → #27 | MCP metadata discovery with provenance and separate annotations | The exact registry sources above distinguish metadata from implementation/package rights. No trust, compatibility or execution authorization is inferred. |
| #55 → #39 | Nominate original-provider sources for later exact-scope rate research | The [cost record](../T6-deployment-operations/cost-estimate.md) retains unit normalization and source-use gates. The shortlist supplies no billable meter, Pricebook, FX rate or missing-price zero. |
| #55 → #41 | Adopt the explicit ranked, dated code/data and intended-use research records | Every row still routes to #41 and remains Not approved for integration. Preserve the [earlier starting-deliverable receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545); the current decision covers the completed research fields at their bounded scope. |
| #55 → #5/#6 | Preserve the [actual per-source rights constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6242699859) at 7acbefbf | Identity, source notices, estimate labels and material distinctions remain with #5/#6; no new integration or capability approval is inferred. |

The five existing affected [handoff ledger](handoffs.md) rows append these
post-snapshot decisions separately. Historical assignee responses and the
2026-10-18 02:50:05 UTC snapshot counts are unchanged. The cutoff validator
checks that historical accounting; it does not certify the new evidence or
substitute for the actual scoped review.

| Live #60 criterion | Accepted research evidence and exact limit |
| --- | --- |
| Inspect exact licence scope per source | Ten-source/four-use table, source-specific clauses, immutable repository pins and the two separately scoped rechecks. Uninspected upstream material stays unknown. |
| Record BenchLM agreement requirement | Separate display/feed agreement boundary, independently re-read. Obtaining an agreement is outside this issue's scope. |
| Confirm upstream rights for compiled data | Distinguish compilation, publisher-owned outputs, original third-party material and code. Confirm the inspected grants; explicitly exclude remaining unestablished material rather than imply a blanket upstream licence. |
| Approve or reject each intended use | Retain each qualified source/use determination and adopt the current-product GPUs.io exclusion. Conditional source permission grants no production eligibility. |
| Significant conclusions linked to evidence or hypothesis | Primary clauses, exact repository/paper identities, dates, confidence/limits and explicit project decisions above. |
| Relevant technical owners review handoffs; unresolved decisions named | Historical #5/#6/#27 receipts plus the actual delegated #41/#39/#36/#62 receiving decisions above. Unknown rights, specific future use decisions and #62's real evidence gaps remain named. |
| Checks pass; reviewer accepts evidence before Done | Exact amendment review, workflow results, signed main merge and readback are recorded on the delivery PR. Issue completion follows that delivery; this table is not a test result or closure by itself. |

## Result

The current research decision is a restrictive, material-specific intake policy.
Licensed material keeps its conditions; unestablished rights remain unknown
and those uses stay excluded. This completes the choices within #60's
documentary research scope when the reviewed amendment reaches canonical main.
It does not require acquiring an agreement merely to exclude a use. All ten
integration records remain Not approved for integration.

The linked #55 shortlist has its distinct ranked evidence and scoped consumer
reviews. Its parent-completion check still requires #60's accepted delivery.
Neither issue's completion approves production collection, source publication,
a schema migration, benchmark comparability or a deployment.
