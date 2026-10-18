# Handoff and research quality audit — 2026-10-18

The GitHub API snapshot ended at **2026-10-18T02:50:05Z**, against main commit 5e8051e4ffa9eea99dfe2bff25466cd1cc690f5d. The [sanitized readback](../../research/market/handoff-audit-readback.json) records all **55 open issues**, **133 PRs**, current assignees/labels, native parent/sub-issue/blocker links and exact review metadata. Separately timestamped public Project observations cover all 28 technical component rows and #59's market row. This is a dated audit, not a continuously refreshed board.

#59 owns [handoffs.md](../../research/market/handoffs.md), [handoffs.json](../../research/market/handoffs.json), [audit.json](../../research/market/audit.json) and the [risk register](../../research/market/risk-register.md). Executive synthesis remains with #47 at [synthesis.md](../../research/market/synthesis.md). No issue assignees, labels, native relationships or Project fields were changed.

## Reconciliation plan and delivery

- [x] Capture issue bodies/comments, live coassignees, PR/review/merge states and native relationships at an explicit cutoff.
- [x] Preserve all 86 previous ledger rows and all 28 historical owner_review objects.
- [x] Add 15 missing declared validation pairs: #60 → #41; #63 → #2/#3/#39; #64 → #9/#39/#41; #65 → #14/#15/#16/#25/#27; #66 → #2/#40/#42.
- [x] Record 22 newer response records with exact reviewer, receipt URL/date, scope, restrictions and explicit reviewed SHA or stated absence.
- [x] Cross-check material conclusions against repository evidence, original access dates, claim conflicts and rights boundaries.
- [x] Read public Project values and publish metadata exceptions without changing triage.
- [ ] Coordinator/co-owner accepts this refreshed #59 artifact set at its PR head.
- [ ] Affected receiving owners review their current artifact scopes; unresolved decisions stay named in the register.

The structured ledger has **101 rows**, covering **98 distinct pairs declared in live Relationships sections** plus the three supplemental #62 → #39/#40/#41 rows already merged through #83. **44** rows have a historical or scoped receiving response, **2** have author integration only, and **55** have no scoped receiving response recorded. Those counts describe response coverage, not completed acceptance. All **19 current #59 audit-artifact handoffs remain pending review of this refresh**.

## What changed since the previous audit

- #83 is now merged to main at 51a5c552bd8dbf6fa6a11d07d6772a3ce9d305b6, on 2026-10-18T02:09:10Z. [CompleteDotTech's approval](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83#pullrequestreview-5560802999) reviewed head 5e1b57696399a71326a92671d3f62a3326f9a5c3 and resolves that reviewer's requests. [appletechie's changes-requested review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83#pullrequestreview-5556580902) at 0be51abbffdad4992d68ea30f6d9c2fcb3014cb2 and explicitly withheld #36/#39 acceptance remain attributed to their own scope. Merge supplies no benchmark replication or receiving acceptance.
- [zwright8's receiving dispositions](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6242699859), reviewed at 7acbefbf4e4e700231e88be272bc89e3a73dde15, narrow #48/#50 discovery context, qualify #55 intake rights, narrow #56/#61 accounting interfaces and #58 proposed validation, and accept #59 risk/ownership separation as context. #49 → #6/#7 is author integration only.
- [The T5 owner reaffirmed](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6230504818) that #49 → #33 covers #30/#31/#32 while those findings remain Unknown. #59 → #33 stays accepted as synthesis context. Neither statement accepts changed audit artifacts or approves a fine-tuning MVP.
- [#60 → #41 rights adoption](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6235704731) is now explicit. The older rights note's “adoption pending” wording is superseded for this scope by that receipt. [#60 → #27](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6244042769) is contextual MCP metadata guidance; it is not transferred to #55 → #27.
- #81, #89, #98, #104/#105/#110, #112, #125, #127, #143, #156, #163 and #171 are merged to main. #91/#92/#94 merged to the proposal branch research/market-intelligence. The readback separately checks whether each merge commit is included in captured main; target-branch merge and publication to main are distinct observations.
- #156 supplies prospective follow-up design after prior observations were seen. It is not retrospective preregistration, permission to rescore old observations, or approval of #63 recruitment/consent.

## Evidence freshness and conflicts

This is a desk cross-check of committed artifacts and linked review receipts. Vendor pages were not re-accessed for this audit; original access dates below were preserved. Reviewers still assess primary-source quality, methods and rights.

| Material conclusion | Traceable artifacts / sources | Original evidence dates and kind | Reconciliation / retained uncertainty |
| --- | --- | --- | --- |
| Direct substitutes overlap entry workflows | [competitors.json](../../research/market/competitors.json), [sources.json](../../research/market/sources.json), [substitute-validation.md](../../research/market/substitute-validation.md), [browser observations](../../research/market/evidence/browser-observations.md); src-flocci, src-modelfit, src-canirun-ai, src-canirun-ai-repo | Baseline 2026-10-16; bounded public ModelFit/CanIRun scenarios 2026-10-17; mutable UI | Flocci sign-in limits the contradiction/export test. #125 author observed CanIRun heading “Apple M1”; reviewer observed “Google.” Preserve both sessions and changing ModelFit device inventory. These are bounded CPU-only observations, not runtime accuracy or exhaustive differentiation evidence. |
| Dense memory evidence is bounded | [sizing-validation.md](../../research/market/sizing-validation.md), [results summary](../../research/market/measurements/mr09-results-summary.json); M61-I/D/A/K/M/G/R | 2026-10-16; 15 successful dense runs, five configurations × three repeats; SmolLM2 revision 12fd25f77366fa6b3b4b768ec3050bf629380bac | Zero matched estimator/runtime pairs. KV-layout agreement is not total-memory calibration. MoE/multi-GPU remain unexecuted and unwaived. Historical capacity screens are not current capacity. [#61 interface receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6242699281) leaves co-owner/coordinator evidence review and #10 placement separate. |
| Harness comparability remains Unknown | [benchmark-validation.md](../../research/market/benchmark-validation.md); B1–B6, src-harness-bench, src-harness-bench-repo-b8d8963, src-miller-2024, src-bjarnason-2026, src-madaan-2024 | B2–B5 accessed 2026-10-16; B1/B6 body access 2026-10-17; bounded B1 table recheck 2026-10-18; repository b8d89634c6f445fcc68ceb6744a59bef6cdf4863 | Historical landing 106/5,194 differs from versioned body 300/20,454. Judge-free prose conflicts with 79 semantic-judge declarations; result-to-grader provenance is missing, G1 fails, all published G3 conclusions stay Unknown. Other-benchmark IRT/variance results supply no Harness correction factor. Paper rights do not license tasks/trajectories. |
| Rights depend on source and intended use | [rights-validation.md](../../research/market/rights-validation.md), [integrations.json](../../research/market/integrations.json), source IDs in each of ten product rows | Original terms checks 2026-10-16; adoption/intake receipts 2026-10-17; MCP metadata recheck 2026-10-18 at upstream 11b7b0e274d518b6f449c5ee3518a6151d9848b9 | Dataset/site, paper/task and registry/package rights remain separate. Preserve notices, ModelFit attribution/change/estimate labels, factual-only HF intake and per-repository checks; prohibit restricted Artificial Analysis reuse and unpermitted OpenRouter automation. Receipts do not grant new collection rights. #127 resolves source-checked versus independently supported terminology without rewriting historical v1 provenance. |
| Pricing scenarios are partial bills | [pricing-validation.md](../../research/market/pricing-validation.md), [T1 pricebook](../../pricing/proposals/t1-api-2026-10-16.json), [T2 pricebook](../../pricing/proposals/t2-hosting-2026-10-16.json); 13 rate IDs and A1–A8 | Pricebooks 2026-10-16; desk source recheck 2026-10-17 reports 13 matches, zero drift; mutable list prices | HF region and RunPod data-center applicability remain unbound. Missing meters, operations/capital and assumed service equivalence prevent a complete cost ranking. The note's 30-day freshness bound is proposed, not adopted #41 policy. Recheck relevant rates and eligibility at recommendation time. |
| Paid demand is unmeasured | [customers.md](../../research/market/customers.md), [market-sizing.md](../../research/market/market-sizing.md), [customer-validation.md](../../research/market/customer-validation.md); A1–A11 and their primary source links | Source access 2026-10-16; survey/report vintages and populations remain separate | 88% respondent organizations, 23.8% US businesses and 20% EU enterprises describe different populations/methods, not a comparable trend. Self-selected developer surveys do not establish buyer prevalence. Scenario arithmetic is assumption-based. No recruitment or willingness-to-pay result exists; D-01–D-17 / #63 T-1–T-5 remain coordinator decisions. |
| Differentiation follow-ups are prospective | [differentiation.md](../../research/market/differentiation.md); H1/H3/H5b, historical H5 disposition, D-57-1–D-57-7 and linked #66 observations | Source observations 2026-10-16/17; follow-up design 2026-10-18 after prior exposure | Do not reclassify old observations against new thresholds or revive rejected historical H5. New follow-ups need protocol commit, fixed inputs/fields/evaluator and labelled amendments. D-57 participant choices do not approve #63 recruitment or its unset thresholds. |
| Mobile/T5 notes provide bounded context | [mobile migration](../../prompts/mobile/MIGRATION.md), [T5 summary](../../research/T5-training-fine-tuning/README.md), [ONNX boundary](../../research/T5-training-fine-tuning/onnx-export-boundary.md) | Mobile migration is repository metadata; T5 original research date 2026-10-16; later receipts and mutable ONNX docs 2026-10-18 | Repository migration establishes location, not implementation completion or service placement. T3–T5 stay optional. No ONNX export/inference was executed; proposed composition does not establish native support or arbitrary tuple success. |

## Metadata and hierarchy QA

All captured native links were read without changing them. Parent/sub-issue reciprocity is checked automatically; information and compatibility relationships remain distinct from native blockers. #42 retains native blocked-by #40. #57/#58 retain their captured native blocker relationships; this audit creates no replacement links.

The API token lacks read:project. A read-only public browser fallback verified:

- Project #1: all 28 component rows' displayed Status, Tier, Priority, Readiness and parent values. **#15 shows Done while issue #15 is OPEN.** Its owners/coordinator must link completed acceptance/evidence review or correct Status. This audit establishes neither choice.
- Project #2 #59: P1, MR-12, Ready, In Progress, Research, Low evidence confidence; parent #47; assignees appletechie and Mattycodes69.
- Full selectable option definitions/IDs, hidden Project #1 fields and other market rows were not audited. These limits are recorded instead of treating historical project configuration JSON as live evidence. No authentication or Project writes were needed.

## Technical publication inventory

This table describes observed publication, not Project Status or full issue acceptance. All listed GitHub issues are OPEN. Exact merge SHAs, target branches and reviews are in the readback; [audit.json](../../research/market/audit.json) records the per-issue rationale.

| Issue | Current assignees | Observed publications |
| --- | --- | --- |
| #1 T0: Configuration | appletechie, tynamite | [#81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81) (merged), [#132](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/132) (merged) |
| #2 T0: Workload / Use Case | appletechie, tynamite | [#81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81) (merged), [#129](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/129) (merged) |
| #3 T0: Deployment Mode | appletechie, tynamite | [#81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81) (merged), [#129](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/129) (merged) |
| #4 T1: Model Selection | Mattycodes69, zwright8 | [#88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88) (merged), [#102](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/102) (merged) |
| #5 T1: Model Provider | tynamite, zwright8 | [#88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88) (merged) |
| #6 T1: AI Model | PUSHINGSQUARES, zwright8 | [#88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88) (merged) |
| #7 T1: Context Window | appletechie, zwright8 | [#88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88) (merged) |
| #8 T2: Infrastructure | Mattycodes69, zwright8 | [#75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75) (merged) |
| #9 T2: Hosting | Mattycodes69, appletechie | [#75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75) (merged), [#103](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/103) (merged) |
| #10 T2: GPU / Compute | Mattycodes69, appletechie | [#75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75) (merged), [#100](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/100) (merged) |
| #11 T2: Inference Engine | Mattycodes69, zwright8 | [#75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75) (merged), [#101](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/101) (merged) |
| #12 T3: Knowledge & Retrieval | Mattycodes69, zabyxc01 | [#119](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/119) (merged), [#130](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/130) (merged) |
| #13 T3: Knowledge Base | tynamite, zabyxc01 | [#130](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/130) (merged) |
| #14 T3: Embedding Model | PUSHINGSQUARES, zabyxc01 | [#130](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/130) (merged), [#139](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/139) (merged) |
| #15 T3: Vector Database | appletechie, zabyxc01 | [#130](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/130) (merged), [#138](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/138) (merged), [#151](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/151) (merged) |
| #16 T3: RAG & Retrieval Backends | appletechie, zabyxc01 | [#119](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/119) (merged) |
| #24 T4: Agents & Integrations | CompleteDotTech, appletechie | [#73](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/73) (merged) |
| #25 T4: Agent Framework | CompleteDotTech, Mattycodes69 | [#69](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/69) (merged) |
| #26 T4: Tools & APIs | CompleteDotTech, zwright8 | [#70](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/70) (merged) |
| #27 T4: MCP Servers | CompleteDotTech, tynamite | [#71](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/71) (merged) |
| #28 T4: Agent Memory | CompleteDotTech, PUSHINGSQUARES | [#72](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/72) (merged) |
| #29 T5: Training & Fine-Tuning | Mattycodes69, appletechie | [#85](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/85) (merged) |
| #30 T5: Training Framework | appletechie, zwright8 | [#68](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/68) (merged), [#110](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/110) (merged) |
| #31 T5: Training Compute | appletechie, tynamite | [#77](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/77) (merged) |
| #32 T5: Training Dataset | PUSHINGSQUARES, appletechie | [#76](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/76) (merged) |
| #33 T5: Fine-Tuned Model | Mattycodes69, appletechie | [#84](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/84) (merged) |
| #34 T6: Deployment & Operations | PUSHINGSQUARES, appletechie | [#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) (merged) |
| #35 T6: Guardrails | PUSHINGSQUARES, appletechie | [#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) (merged) |
| #36 T6: Evaluation | PUSHINGSQUARES, appletechie | [#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) (merged), [#83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83) (merged) |
| #37 T6: Deployment | PUSHINGSQUARES, appletechie | [#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) (merged) |
| #38 T6: Monitoring | PUSHINGSQUARES, appletechie | [#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) (merged) |
| #39 T6: Cost Estimate | PUSHINGSQUARES, appletechie | [#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) (merged) |
| #40 T0: Component Schema & Compatibility Rules | tynamite, zwright8 | [#44](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/44) (merged), [#134](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/134) (merged) |
| #41 T0: Catalog Data Sources & Freshness | PUSHINGSQUARES, tynamite | [#127](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/127) (merged), [#137](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/137) (merged) |
| #42 T0: Saved, Shared & Compared Builds | appletechie, tynamite | [#114](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114) (open) |

## Validation and closure boundary

Validation used Python 3.12.14 and the pinned dependencies from [RESEARCH_WORKFLOW.md](../RESEARCH_WORKFLOW.md). The contract suite passed (21 tests); the research suite passed with Windows UTF-8 mode (92 tests, including 9 handoff checks). The initial default-Windows-encoding run hit an existing cp1252 read error in the mobile tracking test; UTF-8 mode matches Linux CI. Research intake validated 74 catalog proposals and 3 pricebooks; market integrity validated 33 entities, 1,584 cells and 20 issues; handoff integrity validated 101 rows / 98 declared pairs. The mobile validator and whitespace check passed. The added handoff validator checks coverage, coassignee preservation, receipt attribution and summary arithmetic. Regression cases reject author-only promotion, cross-producer receipt transfer, dropped history/co-owners and optimistic counts. CI includes the handoff validator.

Automated integrity checks do not reverify mutable vendor facts, reproduce benchmarks, license data, approve recruitment/compute, or accept research on an owner's behalf. #59 can be considered for completion after the coordinator/co-owner and affected receiving owners review this artifact set and its named unresolved decisions. Until then use Refs #59 and keep it open.
