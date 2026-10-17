# MVP alternatives

Issue: [#58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58) (MR-11). Parent: #47. Refreshed: 2026-10-16.

Status: **draft recommendation for validation only.** It is not implementation, build, deployment or outreach authorization, and it is not an accepted MVP choice. #58 is natively blocked by [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66) and cannot be accepted, nor closed, before #66 is resolved through the accepted workflow. Validation approval, evidence acceptance and product implementation authorization are three separate decisions; this note requests none of them on anyone's behalf.

## Evidence classes

Each claim below carries one class. Grades follow [RESEARCH_METHOD.md](../../docs/RESEARCH_METHOD.md); the remaining labels are claim statuses.

| Label | Meaning |
| --- | --- |
| PD | Primary documentation (publisher's own docs, terms, robots.txt, model card) |
| VC | Vendor claim, not independently reproduced |
| IM | Independent measurement: project-run, pinned and reproducible under stated conditions |
| EST | Estimate derived by this project, with method and assumptions in the cited file |
| OBS | Observed browser behavior, scoped to the recorded steps |
| AJ | Analyst judgement (all ratings in the comparison table) |
| HYP | Hypothesis, unvalidated |
| RS | Repository state (GitHub issue/PR metadata, read 2026-10-16); not accepted research |

**Pending review** means the cited input is unmerged, or merged only to the `research/market-intelligence` proposal branch without accepted handoff dispositions. Nothing marked pending is accepted evidence.

## 1. Six launch approaches

The six approaches and their ratings are unchanged from the earlier draft. Every rating is **AJ**; user value, monetization and time-to-value remain **HYP**. No implementation effort or delivery time is estimated. The final column lists the current inputs bearing on each row.

| Approach | User value hypothesis | Differentiation | Data availability | Feasibility / research | Integration / maintenance | Monetization | Time-to-value hypothesis | Current evidence (class; state) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Model-first | Quick model/provider shortlist | Low versus AA/OpenRouter/BenchLM | Relatively accessible, terms vary | Bounded but task-quality validation needed | Moderate, rapidly changing metadata | Unproven, many free substitutes | Shortest comparison flow | PR #82: Artificial Analysis Data Platform Terms s2.5 bar use of its data in third-party products whose primary purpose includes model/provider selection guidance without written consent; OpenRouter terms prohibit automated scraping (PD; approved by PUSHINGSQUARES, unmerged, #60 owner disposition pending). PR #83: no published Harness Bench harness-effect claim passes the pinning gate (PD/EST; pending review). |
| Hardware-first | Avoid failed local installs | Low–medium versus llmfit/ModelFit | Metadata exists; performance sparse | Runtime measurements needed | Hardware/runtime matrix expensive | Referral possible, conflict risk | Fast when hardware known | [mr09-acceptance.md](mr09-acceptance.md) / PR #79: 15 dense SmolLM2 BF16 CUDA runs on one RTX 5070 Ti, 0 runtime errors/OOMs; comparable competitor/runtime pairs = 0, so no estimator error range; MoE and multi-GPU unexecuted (IM; merged to proposal branch, 0 accepted dispositions). PR #67 review (tynamite): community fit-report projects (LocalScore, LocalMaxxing, Rapid-MLX, MetriLLM, OpenBenchmarking `pts/llama-cpp`) are direct counterexamples to the defensibility hypothesis (AJ by owner; follow-up open). |
| Workload-first | Reduce expertise required | Medium hypothesis, Flocci counterexample | Intent-to-quality evidence sparse | Requires demand and recommendation tests | Broad integrations create maintenance | Unproven | Fast interface, slower trusted answer | [substitute-validation.md](substitute-validation.md): one free Flocci Stack Builder run returned an ordered local PDF RAG workflow with constraints and uncertainty; run, privacy and export unverified (OBS; #66 open). PR #92: personas and the #63 approval package; no participant contact, demand unmeasured (HYP; pending review, D-01 to D-17 coordinator decisions open). |
| Cost-first | Avoid cost surprises | Low for list prices; potential in uncertainty | Prices available, workload inputs missing | Full bill models and scenario validation | High freshness burden | Potential qualified referrals | Depends on user supplying workloads | [pricing-validation.md](pricing-validation.md): protocol only (RS; #64 open, no PR). PR #82: GPUs.io values displayable with attribution but not as a competing GPU price comparison service; #39 to decide impact (PD; pending). PR #91: referral and routing-fee models carry conflicts of interest (AJ grounded in PD; pending review). |
| End-to-end stack | Coordinate every tier | Potentially higher, unproven | Fragmented and rights-constrained | Very broad research burden | Highest compatibility surface | Team/enterprise hypothesis | Slowest credible coverage | PR #82: Harness Bench repository has no licence, so tasks and trajectories cannot be reused; paper results (CC BY 4.0) only with attribution (PD; pending). PR #89: PCPartPicker robots.txt disallows AI agent fetchers from `/` with `ai-input=no`, so the reference walkthrough was not run by an agent; H1–H5 remain hypotheses (PD; pending, coordinator choice of three options open). |
| Hybrid bounded workflow | Explain one local/API decision with a shareable record | Medium hypothesis | Reuse a small rights-cleared subset | Testable scope; still needs real measurements | Constrained adapters and explicit unknowns | Test team artifact value | Faster credible learning than full stack | PR #67 review (tynamite): #58 → #2/#3/#40/#42 accepted, matching #81's hybrid model, with the narrowing in section 4 (RS; review comment, PR unmerged). Mattycodes69's #79 handoff: proceed with review, narrow advice, validate further (RS; pending coordinator disposition). PR #90: one-at-a-time sensitivity puts reachable accounts first, with conversion spanning about 80× (EST; pending review). PR #91: proposed neutral free core, team subscription, labelled referrals, no paid rank (HYP; pending, legal applicability unreviewed). |

## 2. Recommended next validation (conditional)

Validate a hybrid local-versus-API inference decision for one narrowly defined workload, carrying explicit context/concurrency, runtime, evidence date, uncertainty and a shareable versioned decision record. Reuse model and hardware evidence only where rights allow. Retrieval, agents and fine-tuning stay visible as optional future requirements; the MVP does not claim to cover them. **HYP** throughout.

The Flocci observation (OBS) already shows generated, constraint-aware workflow advice exists, so guided output alone is not a distinctive proposition. The remaining testable distinctions are narrower: reproducible, dated evidence behind each decision; explicit error correction; and a reviewed compatibility outcome. Each is **HYP** until #66 and #63 report.

Alternatives retained: **narrow** to a decision-record layer on top of existing substitutes, or partner with one; **stop** if a direct substitute satisfies the scenario (section 5). Model-first and hardware-first remain available as narrower entry points if data rights permit them.

## 3. Ranked data and maintenance risks

Order is **AJ**, by how much of the MVP the risk can invalidate and how early. Rights receives the P0 override from the [method](../../docs/market-research/research-methodology.md) because it can invalidate every dependent ingestion.

| Rank | Risk | Why ranked here | Evidence (class; state) |
| --- | --- | --- | --- |
| 1 | Data display and redistribution rights | A no on display removes the data a recommendation shows, for every approach. Access does not grant reuse. | PR #82: AA s2.5 selection-guidance bar, OpenRouter no-scraping, Harness Bench repo unlicensed, GPUs.io competing-service limit (PD; approved, unmerged). tynamite PR #67 review: where no licence or terms grant is found, display and redistribution default to `no` (owner position). |
| 2 | Direct substitute already satisfies the workflow | Native #66 gate; a pass narrows or stops #58 regardless of other gates. | substitute-validation.md: one Flocci run (OBS); contradictory constraints, deployment, export and a second substitute untested (RS; #66 open). tynamite: community fit-report projects are counterexamples (AJ by owner). |
| 3 | Uncalibrated sizing and fit | The hybrid decision depends on a fit verdict; no estimator error range exists. | mr09-acceptance.md: 15 dense runs, 0 comparable pairs, MoE/multi-GPU unexecuted; INT4 payload reduction did not remove prefill/workspace/reservation costs in the tested model (IM; proposal branch, pending). |
| 4 | Benchmark comparability | Quality claims behind model choice may not survive pinning. | PR #83: no harness-effect claim passes the pinning gate; repository applies an LLM-judge fallback on 79 of 274 general tasks, contradicting the website; tests and ground truth ship publicly (contamination risk); each configuration ran once (PD/EST; pending). |
| 5 | Price freshness and incomplete bills | Current-state facts expire; idle, storage and egress are often missing. Highest recurring maintenance load. | pricing-validation.md: protocol only (RS; #64 open). tynamite PR #75 review: current-state facts are shown "as of <date>", no TTL yet; no automated retrieval or bulk copying of vendor tables until the #41 terms inventory exists (owner interim policy). |
| 6 | Runtime/engine/hardware matrix churn | Each runtime and engine release changes fit and support; maintenance grows with every adapter. | mr09-acceptance.md: estimator quantities and runtime assumptions must be exposed (IM/AJ; pending). tynamite PR #75 review: version-pinned facts re-checked on version change (owner interim policy). |
| 7 | Monetization conflict of interest | Referral or paid placement can bias rankings and erode trust in the record. | PR #91: FTC 16 CFR 255, EU P2B Art. 5, Omnibus/UCPD, DSA Arts. 26/27 cited; applicability marked for legal review (PD; pending). |
| 8 | Unmeasured demand and sizing | Does not invalidate the data, but decides whether validation continues at all. | PR #90: sizing scenarios are assumptions; conversion is unknown (EST; pending). tynamite rejected #53 as a #2 input. PR #92: #63 contact not approved (RS). |
| 9 | Reference-study gap | Limits UX borrowing, not data. | PR #89: PCPartPicker walkthrough not run under robots.txt policy (PD; pending coordinator option). |

## 4. Owner narrowing and handoff conditions

**tynamite, [PR #67 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67), 2026-10-16, at `6511dea`:** #58 → #2, #3, #40, #42 is **accepted**: "The hybrid local-vs-API workflow is exactly what #81 models: the workload profile, mode per component (operator/capacity test), fit records under EV-1 and a versioned build." Narrowed: "I'd narrow 'missing performance or rights must surface as unknown': apply the conflict order in my #75 review first, so `unknown` is reserved for genuine gaps."

Applied here. The [PR #75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75) interim conflict order is: (1) normalise units, rounding, currency and naming; (2) drop claims whose stated scope excludes the selection, then the most specific wins; (3) for pinned facts the selected version's source wins, for current-state facts the latest effective date wins; (4) authority by fact type: publisher over third parties for facts it controls, a stated requirement over a capability listing, billing/legal pages over overviews, and for fit and performance a matching measurement over an estimate over a vendor claim; (5) equal-rank numbers show median and spread, decide on the conservative value and flag as disputed. `unknown` remains only when no eligible evidence exists or equally ranked sources make opposite yes/no claims after these steps, and those cases are flagged for a reproducible test. For rights specifically, no found licence or terms grant means `no`, not `unknown`. A rule may pass on checked publisher documentation, labelled "unverified" until reproduced. Missing performance or rights are never a compatibility pass.

**Mattycodes69, [#79 handoff to #58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58#issuecomment-6217454289), pending coordinator (@CompleteDotTech) disposition:**

- Proceed with review: assumption-explicit screening is technically plausible; 15 pinned dense runs demonstrate reproducible allocator evidence collection; estimator quantities and runtime assumptions must be exposed.
- Narrow advice: identify artifact, runtime, context, KV, active sequences and topology, and separate payload, allocated, reserved and device budgets. INT4 payload reduction did not remove prefill/workspace/reservation costs in the tested model.
- Validate further: competitor/runtime comparable pairs remain 0, with no calibrated error range; MoE/multi-GPU unexecuted under the recorded spare-capacity/access guards; #62/#65 need their owners' reviewed outputs; #39/#64 retain conditional economics and fresh-rate validation.
- Proposed stop/scope-change triggers: inability to represent the required runtime/placement, unresolved source reuse, or failure of coordinator-defined product criteria. No approved numeric threshold, economic saving or implementation/deployment approval.

It is a pending handoff, not an accepted MVP decision; #66 remains the native blocker and #61 an information/validation gate. Both are incorporated as conditions on the recommendation, not as acceptance of it.

Minimum data for the hybrid record, with receiving owners: workload constraints (#2), deployment mode per component (#3), identified model/provider (#5/#6), context policy (#7), hardware/runtime (#10/#11), dated cost units (#39), provenance and reuse (#41), versioned selection and rule semantics (#40/#42).

## 5. Minimum evidence per validation gate

State is from live GitHub readback on 2026-10-16 (RS). #60–#64 are informational gates; only #66 is a native blocker. All thresholds are **named coordinator decisions (@CompleteDotTech)**; none is set here.

| Gate | Minimum evidence needed | Current state | MVP decision it changes | Narrow / stop trigger (threshold owner) |
| --- | --- | --- | --- | --- |
| #60 rights (tynamite) | Source × intended-use decision (internal research, display, redistribution, automated retrieval) for every source the hybrid record would show, with governing clause and date | Open. PR #82 has 40 decisions, approved by PUSHINGSQUARES, unmerged; #60 and #41 owner disposition pending | Which sources the MVP may display, and whether model-first data can be used at all | Narrow to permitted sources, or pursue written consent/partnership, when a required source is `no` for display. Stop if no rights-cleared subset can support one decision: required-source set is a coordinator decision |
| #61 sizing (Mattycodes69) | Comparable estimator/runtime pairs with an error range for the target workload's architecture, or an owner-reviewed narrowed scope; MoE/multi-GPU cells if in scope | Open. 15 dense runs merged to proposal branch via PR #79; 0 comparable pairs; 0 accepted dispositions; PR #80 readback pending | Whether the record can state a fit verdict or only explicit assumptions; which architectures are in scope | Narrow to dense, single-device, assumption-explicit screening if pairs stay unavailable. Stop/scope change if the required runtime/placement cannot be represented. Acceptable error bound: coordinator decision |
| #62 benchmark comparability (PUSHINGSQUARES) | Pinned model/harness/budget/task versions, contamination and overlap checks, replicated harness effects | Open. PR #83 desk validation pending review; no benchmark run authorized | Whether quality comparisons appear in the record, or only cited publisher results with conditions | Narrow to cited, version-pinned results without cross-harness ranking if no claim survives pinning. Survival criteria and noise floor acceptance: coordinator and #36 |
| #63 demand (appletechie; coordinator approval by CompleteDotTech) | Approved recruitment/consent protocol, interviews across distinct buyer roles, current alternatives and recent decisions, unanchored willingness-to-pay | Open, Awaiting Decision. PR #92 approval package pending; D-01 to D-17 undecided; no contact made | Whether to continue validating at all; which segment the bounded workload targets | Narrow segment, or stop, if disconfirming tests T-1 to T-6 hold. Their values: coordinator decision |
| #64 cost (PUSHINGSQUARES) | Pinned provider, region, date and billing units; idle, storage, egress and utilization; ranges and invalidation triggers | Open, protocol only, no PR | Whether the local-vs-API record can include a cost comparison, or only cost units and unknown coverage | Narrow to unit-level, dated rates with explicit gaps if complete bills cannot be modelled. Acceptable uncertainty range: coordinator and #39 |
| #66 substitute (itisSomeone) — native blocker | Common non-sensitive scenario across Flocci and at least one more substitute; contradictory-constraint handling; saved/export behavior; counterexamples and pivot recommendation | Open. One Flocci run observed; no PR; analysis in review via PR #67 | Whether the hybrid recommendation stands, narrows to a record layer, or stops; #58 acceptance waits on it | Narrow or stop if a substitute satisfies the scenario, including a reproducible, versioned record. Definition of "satisfies": coordinator decision |

A failed gate calls for narrowing, partnership or stopping, not adding features.

## 6. Unresolved decisions

- Coordinator (@CompleteDotTech): every threshold in section 5; accept, narrow or reject Mattycodes69's #79 handoff; PR #89 walkthrough option; PR #92 D-01 to D-17; whether to approve this validation.
- #66 owner: complete the substitute protocol; #58 acceptance cannot precede it.
- #60/#41 (tynamite): disposition of PR #82. #39 (PUSHINGSQUARES): GPUs.io impact and #64 economics. #36: benchmark handoff from PR #83. #10/#11: sizing handoff.
- No implementation, deployment, paid compute, outreach or delivery estimate is authorized or implied by this note.
