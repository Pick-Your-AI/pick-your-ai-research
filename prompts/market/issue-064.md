# Issue #64 — MR-07: Validate price freshness and total-cost scenarios

**Issue:** [Pick-Your-AI/pick-your-ai-research#64](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/64)

**Project:** [Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2)

**Parent:** [#54](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/54)

**Prepared:** 2026-10-16; refresh all mutable state before acting.

**Companion:** [Shared execution rules](SHARED.md).

## Mission and invocation

You are the issue-scoped research orchestrator for **#64**. Determine whether dated local and hosted cost scenarios are comparable, current and explicit about missing cost coverage. Execute authorized research, validation, commit, push, branch synchronization, review and qualifying merge—not just analysis or task creation. Publishing this prompt does not execute it. Read `AGENTS.md`, current contributor/governance/research instructions and `prompts/market/SHARED.md` first. Preserve the current issue, acceptance criteria, actual assignees, active work and explicit owner decisions.

## Scope and writable deliverables

Own freshness checks and scenario completeness. Do not define new billing units or cost semantics owned by #39, duplicate rates outside Pricebook proposals, or claim that an unmerged conditional Pricebook is already accepted.

Use the existing canonical deliverable paths:

- `research/market/pricing-validation.md`

Keep supporting changes narrowly necessary to this deliverable. Coordinate source-register and handoff-ledger edits with their existing owners; do not create parallel catalogs, duplicate decision records or claim authority over a linked issue.

## Starting context to verify

The issue points to prices and conditional infrastructure research in PR #67 and PR #75. Inspect their current state and exact records. Reuse the existing Pricebook and catalog identities where suitable instead of creating a parallel price catalog.

This is a dated starting reference, not an instruction to preserve stale status. Read the latest comments, artifact contents, exact PR bases/heads and review decisions before changing anything. Unmerged research is not accepted evidence. A closed PR must be checked for its actual merge target.

## Orchestrated execution

Use one coordinating writer for the issue. With available subagents, separate evidence collection, acceptance/contract checking and adversarial review into bounded, nonoverlapping passes; otherwise perform the passes sequentially without claiming independent agents or human approvals. Assign no new GitHub owner merely because a name appears in a historical body. Maintain an acceptance map from the live criterion to artifact, evidence, check, required reviewer and remaining gap.

### 1. Inventory exact price references

Identify the provider, service/catalog item and version, currency, region, observation date, billing unit, commitment, tier, discounts, taxes and access conditions relevant to each scenario. Distinguish a stated rate from a negotiated or estimated rate.

### 2. Recheck first-party sources

Read current provider pricing and applicable terms. Record the recheck date, changed conditions and unavailable or ambiguous rates. Do not carry a historical price forward as current simply because its URL still loads.

### 3. Normalize comparable decision scenarios

Compare the same workload, time horizon, utilization and performance requirement. Expose model/context/concurrency assumptions where they drive usage. Keep capital, recurring and usage-dependent costs distinguishable and show ranges when a single total would imply false precision.

### 4. Audit missing cost coverage

Account for idle capacity, storage, egress and utilization or explicitly show the unknowns and exclusions. Unsupported canonical meters, including egress when not represented, stay in research notes with #39/#40 proposals; never disguise them as supported units or zero cost.

### 5. Use the existing canonical pricing workflow

Put complete dated rates only in pricing/proposals with exact catalog-version references and required provenance, coordinating the relevant owner. Keep incomplete rates in notes. Do not mutate frozen v1 or create duplicate catalog IDs to make a Pricebook pass validation.

### 6. Publish sensitivity and invalidation triggers

Explain which changes in rate, region, utilization or workload invalidate the comparison. Recheck the material sources before a recommendation is accepted. Hand the findings to #9/#39/#41 and the informational #58 gate; distinguish arithmetic checks from source and cost-coverage review.

## Dependencies and handoffs

**Native children:** None specified in the inspected snapshot.

**Native blocked-by prerequisites:** None specified in the inspected snapshot.

**Native downstream issues blocked by this issue:** None specified in the inspected snapshot.

**Market information/coordination links, not newly created blockers:** [#54](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/54), [#58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58)

**Project #1 receiving issues — information/review, not ownership transfer:** [#9](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9), [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39), [#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41)

Read current receiving owners and request an explicit accept/reject/narrow disposition for each material handoff, identifying the exact artifact revision, conditions, fields or claim, and remaining question. Coordinate the canonical handoff ledger with #59. A request for review or general PR approval does not prove that a specific owner accepted a handoff. Preserve native relationships unless their predicate is genuinely resolved through the accepted workflow.

## Acceptance criteria to preserve

These are the issue criteria captured for this package. Re-read the live issue and preserve any later accepted changes; never silently remove a criterion to make the task finish.

- [ ] Pin provider region date and billing units
- [ ] Include idle capacity storage egress and utilization
- [ ] Recheck live rates before recommendations
- [ ] Report ranges and invalidation triggers
- [ ] Deliverable links every significant conclusion to evidence or an explicit hypothesis.
- [ ] Relevant technical owners review handoffs; unresolved decisions are named.
- [ ] Repository checks pass; reviewer accepts the evidence before Done.

**Issue-specific completion gate:** Unknown egress, idle cost or utilization may not be silently treated as zero. A scenario is not complete merely because its supported Pricebook meters validate.

## Commit, push, sync and merge this issue

Execute this delivery loop after the research passes above; do not stop at a plan or an unpushed local edit. Apply the detailed safeguards in `SHARED.md`.

1. Refresh the actual repository, issue, active PRs and base; preserve current assignees and other writers. Use a clean isolated worktree and a focused issue branch. Reuse the existing authorized work instead of launching a duplicate. If the deliverables only exist on an unmerged proposal branch, coordinate a declared editing dependency; do not silently import or merge unrelated work.
2. Run the current Python 3.12 research workflow, applicable market validator, `git diff --check` and claim/evidence review. Record the actual commands and results for this revision. Validators do not prove truth, rights, empirical success or owner acceptance.
3. Inspect and stage only the intended files, commit with a meaningful reference to issue #64, push, and verify the remote head SHA. Open or update the focused PR using **`Refs #64`** for a partial contribution.
4. Fetch the current base and head, synchronize the contribution safely, inspect the new diff and rerun affected checks. Obtain the required independent reviewer and explicit receiving-owner dispositions. Preserve reviews/holds and refresh approvals after any head change; no self-approval, blind force push or protection bypass.
5. Merge the qualifying final head using the permitted normal method and a head-SHA guard where available. A valid partial PR may merge while this issue remains open. A merge into a proposal branch is **not** delivery to main. Use **`Closes #64`** only when a canonical-main merge will satisfy every live criterion, native child/prerequisite gate and required handoff.
6. Verify the actual merge destination, commit, files and post-merge checks; safely synchronize a clean local verification checkout. Only then reconcile issue/Project #2 state using live fields, preserving unrelated values and reading changes back. Do not claim Done or synchronization without that evidence.

If an external decision, unavailable resource or permission blocks an action, complete the independent permitted work and return an exact blocker plus a ZIP/diff and replay steps. Do not fabricate execution, approval, participant evidence, commit/push/merge status or future background work.

## Required final report

Report #64’s completed and remaining criteria, changed files, source/evidence limitations, actual validation commands/results, branch and commit SHA, pushed remote head, PR URL and base, review/owner dispositions, merge commit and destination, canonical-main verification and any actual Project readback. Separate partial delivery from issue completion. Name the exact missing permission, artifact, experiment, decision or reviewer action when blocked.
