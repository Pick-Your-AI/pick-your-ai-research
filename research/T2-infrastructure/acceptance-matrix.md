# T2 acceptance matrix

Issue criteria copied verbatim from the live issues on 2026-10-16. `Prepared` means an artifact is supplied for review; it does not satisfy merged-work or owner-confirmation requirements. Issue #11 is complete through [PR #291](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/291), and #10 through [PR #339](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/339) with its [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250602587); #8/#9 remain open.

Continuation audit: all **32 criteria** were compared verbatim against fresh #8–#11 issue bodies on 2026-10-16. That historical matrix counted 24 prepared content criteria and eight then-unmet gates. The 2026-10-18 [#11 criterion audit](inference-engine.md#criterion-and-integration-audit--2026-10-18) assessed its eight artifact criteria while the receiving criterion was then pending. The later [final research handoff assessment](inference-engine.md#final-research-handoff-assessment--2026-10-18), delivered by [PR #291](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/291), satisfies criterion 11.8 from actual owner confirmations for all five declared consumers. All nine #11 criteria are now satisfied within their original research scope. Passing automation alone does not certify evidence or owner acceptance. Source corrections and fixed-severity rule clauses are recorded in [validation.md](validation.md).

| ID | Acceptance criterion (unchanged) | Artifact / evidence to inspect | Reviewer / consuming owner | Status |
| --- | --- | --- | --- | --- |
| 8.1 | All sub-issues are closed with merged decision records that meet their acceptance criteria | [README.md](README.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | #9 remains open; #10/#11 are complete through #339/#291. Record merges alone are insufficient for parent acceptance |
| 8.2 | The handoffs above are confirmed by the affected workstream owners | [handoffs.md](handoffs.md); linked owner acknowledgements required | @Mattycodes69; T3 @zabyxc01; T4 @CompleteDotTech; T5 @appletechie; T6 @PUSHINGSQUARES | Pending owner confirmation |
| 8.3 | A workstream summary at `research/T2-infrastructure/README.md` lists decisions, rules contributed to #40, and open questions | [README.md](README.md) compatibility proposals; [contract-proposals.md](contract-proposals.md) | #40 @tynamite; @Mattycodes69 | Summary merged in #75; child/handoff acceptance remains separate |
| 9.1 | Taxonomy with boundary examples | [hosting.md](hosting.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Prepared; owner review pending |
| 9.2 | Candidate set per category with priced examples and provenance | [hosting.md](hosting.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Prepared; owner review pending |
| 9.3 | Availability represented with explicit `unknown` handling | [hosting.md](hosting.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Prepared; owner review pending |
| 9.4 | Decision record merged at `research/T2-infrastructure/hosting.md` following the research method | [hosting.md](hosting.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Merged in #75; full issue acceptance remains open |
| 9.5 | Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | [hosting.md](hosting.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Prepared; owner review pending |
| 9.6 | Comparison fields defined with type, unit, and evidence requirement | [hosting.md](hosting.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Prepared; owner review pending |
| 9.7 | Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | [hosting.md](hosting.md) compatibility proposals; [contract-proposals.md](contract-proposals.md) | #40 @tynamite; @Mattycodes69 | Prepared; owner review pending |
| 9.8 | Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | [hosting.md](hosting.md) evidence table and claim references | #41 @tynamite; @Mattycodes69 | Prepared; owner review pending |
| 9.9 | Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | [handoffs.md](handoffs.md); linked owner acknowledgements required | @Mattycodes69; #10 @Mattycodes69, #14/#15 @zabyxc01, #27 @CompleteDotTech, #31 @appletechie, #37/#39 @PUSHINGSQUARES | Partial: #10/#27/#31 receipts; appletechie's #15 boundary and historical #37/#39 scopes; [PUSHINGSQUARES's actual `9192d5d` response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6247689488) confirms #37 inputs from #247's delivered map and narrows #39 to scoped units, visible not-totalled L37/L38 estimates and distinct billing stages. #14, substantive #15, receiving review of the #37 map and appletechie's separate scope remain |
| 9.10 | Open questions recorded with a named follow-up owner | [hosting.md](hosting.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Prepared; owner review pending |
| 10.1 | Sizing method with assumptions and uncertainty documented | [gpu-compute.md](gpu-compute.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: byte-based sizing, explicit per-domain reserve, topology, an uncalibrated load-to-count procedure and named uncertainty are documented; no universal numeric default or measured fit is claimed |
| 10.2 | Measured values cite their source and conditions; estimates are labelled | [gpu-compute.md](gpu-compute.md) evidence table and claim references | #41 @tynamite; @Mattycodes69 | Artifact criterion satisfied: publisher-measured C16 values retain their hardware/runtime/workload conditions; calculations and synthetic sensitivities are labelled estimates |
| 10.3 | Model ↔ GPU rules in the #40 format | [gpu-compute.md](gpu-compute.md) compatibility proposals; [contract-proposals.md](contract-proposals.md) | #40 @tynamite; @Mattycodes69 | Artifact criterion satisfied: four COMPUTE groups use the shared proposal format and central queue narrowing; executable CD/version approval remains separate |
| 10.4 | Decision record merged at `research/T2-infrastructure/gpu-compute.md` following the research method | [gpu-compute.md](gpu-compute.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: the decision record merged in #75 and accepted source/intake corrections are retained; #339 delivered the completed assessment and cost-condition integration in signed `a2bba46f` |
| 10.5 | Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | [gpu-compute.md](gpu-compute.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: API omission, exposed managed capacity and self-hosted/hybrid paths are covered, with CPU/edge and incomplete-profile gaps explicit |
| 10.6 | Comparison fields defined with type, unit, and evidence requirement | [gpu-compute.md](gpu-compute.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: 19 typed field groups specify units, evidence and unknowns; the current 20-record intake preserves H100/MI300X as note-only and keeps native precision separate from joint execution |
| 10.7 | Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | [gpu-compute.md](gpu-compute.md) compatibility proposals; [contract-proposals.md](contract-proposals.md) | #40 @tynamite; @Mattycodes69 | Artifact criterion satisfied: fixed severity, outcome, evidence status and applicability remain distinct; sourced premises and synthetic examples are separated from independently verified joint compatibility |
| 10.8 | Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | [gpu-compute.md](gpu-compute.md) evidence table and claim references | #41 @tynamite; @Mattycodes69 | Artifact criterion satisfied for bounded documented findings: C01–C22 and the RTX 4090/A100/P4de supplements retain primary sources, dates, versions, units and conditions; no new source access or hardware result is inferred |
| 10.9 | Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | [handoffs.md](handoffs.md); linked owner acknowledgements required | @Mattycodes69; #9/#11 @Mattycodes69, #31 @appletechie, #39 @PUSHINGSQUARES | Receiving criterion satisfied by the [actual delegated project-engineering review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107), posted by @CompleteDotTech at `8a6b8a67`: all four #9/#11/#31/#39 scopes receive the current retained subset, explicit withdrawals and implemented headroom condition. Earlier authors, revisions and limits are preserved; the [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250602587) confirms reviewed canonical delivery and issue completion |
| 10.10 | Open questions recorded with a named follow-up owner | [gpu-compute.md](gpu-compute.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: named follow-up owners cover actual remaining model/engine, native-precision, future-estimate, rights and runtime questions |
| 11.1 | Support matrix keyed by engine version with sources | [inference-engine.md](inference-engine.md) evidence table and claim references | #41 @tynamite; @Mattycodes69 | Artifact criterion satisfied: three examined releases and three historical rows with scoped sources; no runtime certification |
| 11.2 | Rules in the #40 format, including `unknown` for unverified combinations | [inference-engine.md](inference-engine.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: shared proposal template and E27 owner decisions; unknown for missing eligible evidence, with documented outcomes/evidence status distinct; executable approval separate |
| 11.3 | Decision record merged at `research/T2-infrastructure/inference-engine.md` following the research method | [inference-engine.md](inference-engine.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: original record merged in #75 and its central corrections are retained |
| 11.4 | Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | [inference-engine.md](inference-engine.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: all three modes and undisclosed managed-version unknowns are addressed; lifecycle/expansion decisions retain their scope |
| 11.5 | Comparison fields defined with type, unit, and evidence requirement | [inference-engine.md](inference-engine.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: 15 typed field groups with units/semantics and evidence requirements; note-only extensions remain proposals |
| 11.6 | Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | [inference-engine.md](inference-engine.md) compatibility proposals; [contract-proposals.md](contract-proposals.md) | #40 @tynamite; @Mattycodes69 | Artifact criterion satisfied: fixed-severity proposal clauses, sourced premises, evidence status and synthetic examples remain distinct; no independently verified joint rule is claimed |
| 11.7 | Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | [inference-engine.md](inference-engine.md) evidence table and claim references | #41 @tynamite; @Mattycodes69 | Artifact criterion satisfied for the bounded documentation findings: dated E01–E28/H01–H09 and build-supplement primary locators preserve version/conditions; no new measurement or blanket source recheck |
| 11.8 | Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | [handoffs.md](handoffs.md); [final five-consumer assessment](inference-engine.md#final-research-handoff-assessment--2026-10-18) | @Mattycodes69; #10 @Mattycodes69, #25 @CompleteDotTech, #33 @appletechie, #37/#38 @PUSHINGSQUARES | Research handoff criterion satisfied: actual current consuming owners confirm all five declared interfaces, with their linked constraints and narrowing. PUSHINGSQUARES's [6247689868](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868) confirms the delivered #37 map and accepts #38 source/evidence inputs at `9192d5d`; appletechie's earlier `66b46d4` scope remains historical. No runtime, executable-rule or additional owner acceptance is inferred |
| 11.9 | Open questions recorded with a named follow-up owner | [inference-engine.md](inference-engine.md) | @Mattycodes69; @CompleteDotTech (repository default reviewer) | Artifact criterion satisfied: named follow-up owners are recorded; unresolved decisions are not treated as accepted |

## Baseline and tracking audit

Publication: [PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75), with issue-specific progress and handoff requests linked from [handoffs.md](handoffs.md#posted-requests-not-acknowledgements). The original publication did not establish acceptance. Current receipt assessments above follow the linked 2026-10-18 ledger; historical intake observations below retain their dates.

- Initial intake default branch `main` at `324518ff8d9629fbb7cd4f2d6a27dcc219300fd4`; PR #44 merged at `9769fcd9ea380b1211669b2753181c7782444178` on 2026-10-16. PR #45 also merged. No T2 records or proposals were present on that default-branch baseline. Continuation reuses existing PR #75 and its records rather than treating them as new findings.
- Native relationships read through GitHub GraphQL: #8 has #9/#10/#11; each child's parent is #8; none has `blockedBy` relationships. No relationships are changed.
- Live assignees: #8–#11 @Mattycodes69. All scoped and consuming issue comments were read; no handoff acknowledgements existed at intake.
- Public Project UI was read on 2026-10-16: #8/#9/#10/#11 all `Backlog`, `Tier = T2 Infrastructure`, `Readiness = Ready`; priority #8/#10/#11 `Critical`, #9 `High`. These live values differ from the brief and CONTRIBUTING's earlier field names. Preserve priority and field definitions; do not create substitute labels or fields.
- Project GraphQL read failed with `INSUFFICIENT_SCOPES`: CLI token lacks `read:project` / `project`; browser is signed out. Board edits cannot be verified or performed with current access. That access failure and the requested In Review update describe the 2026-10-16 publication snapshot, not a current instruction. PR #75 and its follow-ups are now merged. Before changing the Project, an authorized administrator must refresh current work and fields: ongoing incomplete research is In Progress, an actual external prerequisite may warrant Blocked, and In Review requires an open decision-record PR. Preserve current priority and Tier; do not replay the obsolete publication update. #40 @tynamite should reconcile the documented field vocabulary with the board. This is an access/tracking limitation, not a new native research blocker.

## Scoped #10/#61 continuation (2026-10-18)

The [decision record](gpu-compute.md#headroom-and-measurement-handoff-disposition-2026-10-18)
now proposes explicit scenario headroom with no universal numeric default,
note-only consumption of #61 observations, and a future build-bound estimate
placement. This supports prepared content for 10.1/10.2/10.10; it does not accept
those criteria or supply calibration. appletechie's later scoped acceptance of
explicit headroom/note-only observations is recorded in the continuation below;
Mattycodes69's disposition and future placement agreement remain open. For 10.9, the existing #31 scoped
receipt is present; Mattycodes69's #9/#11 interface receipts are now linked in the ledger, while appletechie's #39 response and other co-owner decisions keep their own scope. The interface receipts do not accept headroom, calibration or estimate placement. #61's full
empirical coverage, matching estimator errors and coordinator evidence acceptance
remain open in its [current acceptance map](../market/mr09-acceptance.md#current-1061-continuation-map-2026-10-18).
No acceptance criterion, assignee, native relationship or Project value changes.

## Scoped interface reconciliation (2026-10-18)

Live owners: #8/#11 @zwright8 and @Mattycodes69; #9/#10 @Mattycodes69 and @appletechie. The [ledger](handoffs.md) credits each actual receipt author without treating it as approval by every co-owner. Existing merged record gates are complete; remaining full acceptance criteria stay open. Project readback again returned `INSUFFICIENT_SCOPES` for `read:project`; no board values are claimed or changed.


## Scoped #11 lifecycle continuation (2026-10-18)

The [engine record](inference-engine.md#version-retention-and-bounded-candidate-recommendation--2026-10-18) now records zwright8's actual retention/candidate receipt and proposes the matching bounded recommendation for Mattycodes69's review. It defines reference-based retention and new-release research triggers, preserves single-version-per-ID intake, and names #42's receiving owners. That earlier lifecycle continuation prepared 11.4/11.9 without assessing their acceptance. The later criterion audit linked above assesses the literal artifact criteria as satisfied; it does not supply Mattycodes69's lifecycle concurrence or #42's receiving decision. A separately dated TGI lifecycle source check leaves the main matrix and catalog dates intact. For 11.8, appletechie's deployment/monitoring responses keep their reviewed revision, direction and integration limits; other owners' decisions are not inferred. No runtime tuple, support window, security certification or versioned executable rule is approved by this update.


## #10 explicit-reserve arithmetic continuation (2026-10-18)

The [compute record](gpu-compute.md#research-arithmetic-check-for-the-headroom-proposal)
links a research-only checker and synthetic boundary regressions for explicit
headroom, single reserve accounting, confidence eligibility and matching domains.
This supplies reproducible methodology support for 10.1/10.2 without a measured
error bound, default reserve, ResourceEstimate or GPU-count recommendation.
The note records appletechie's actual headroom/note-only, #33 and #39 responses
at their reviewed revision; Mattycodes69's methodology disposition, future
placement and PUSHINGSQUARES's cost scope remain separate. No criterion is
marked accepted by these tests or this reconciliation.

## #9 regional/billing continuation (2026-10-18)

The [hosting recommendation](hosting.md#proposed-initial-regional-scope-and-expansion-gates-2026-10-18)
proposes initial regional samples, named expansion triggers and explicit
account/stock/network/rate evidence gates. H34–H37 are separately dated source
rechecks; original rates, catalog scope and source dates are preserved. This
prepares 9.3/9.5/9.10 without asserting owner adoption. For 9.9, appletechie's
actual #15/#37/#39 responses retain their limits. PUSHINGSQUARES's later
`9192d5d` response is now linked for #37 input confirmation and #39 narrowing;
invoice rounding and Runpod sub-hour cadence remain unresolved. #14, the
substantive #15 response, receiving review of the #37 map and appletechie's
separate scope remain.
No issue checkbox or Project metadata changes.

## #10 precision intake and receipt review (2026-10-18)

The [compute correction](gpu-compute.md#incomplete-precision-intake-correction-2026-10-18)
reproduces the known frozen membership limit using two actual historical
accelerator proposals, then keeps those incomplete candidates note-only.
Independent review found the sizing arithmetic, explicit reserve accounting and
four shared-format rule proposals coherent; this is artifact review, not
calibration or approval of a versioned rule. The current T5 availability text
reflects the withdrawal, while historical inventory and receiving receipts stay
pinned to their original revisions. The actual later #39 response is narrowed
to quantity/utilization inputs and requires an unapplied-headroom disclosure.
No literal criterion, assignment, native relationship or Project field changes,
and #10 remains open for the named semantic and receiving decisions.


## Current compute artifact assessment (2026-10-18)

The [dated compute assessment](gpu-compute.md#compute-research-artifact-assessment--2026-10-18)
reviews the literal ten criteria after the accepted #301 intake correction.
Nine artifact criteria are satisfied; 10.9 is supported by the
[actual current-scope delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107)
of published `8a6b8a67`, tree `38cda613ed05c30adf9fdb34cd2d0584866de414`.
The intake count is 20 (five hosts, seven storage items, three
accelerators, two profiles and three engines); no removed ID is restored.
The earlier continuation paragraphs retain their historical review scope and
are not additional calibration or future-ResourceEstimate closure criteria.
The actual #39 narrowing is now integrated as explicit unapplied-headroom
disclosures, with L37/L38 visible but not totalled. The new review is attributed
to the coordinating engineer under the user's project delegation, with every
earlier receipt retained at its own scope. [PR #339](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/339)
received [independent review at `94ea2422`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/339#pullrequestreview-5563188565)
and delivered the assessment in signed [`a2bba46f`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/a2bba46ff850af5d6263561a94f9866b01c03c05).
The [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250602587)
records passing post-main validation, all ten criteria checked, the completed
issue and the subsequently observed Project `Done` state. This status
reconciliation changes no criterion wording, owner, runtime result or Project
field; #8/#9 retain their remaining acceptance criteria.
