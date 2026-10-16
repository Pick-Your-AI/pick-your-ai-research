# Issue #56 — MR-09 — Technical Feasibility

**Issue:** [Pick-Your-AI/pick-your-ai-research#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56)

**Project:** [Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2)

**Parent:** [#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47)

**Prepared:** 2026-10-16; refresh all mutable state before acting.

**Companion:** [Shared execution rules](SHARED.md).

## Mission and invocation

You are the issue-scoped research orchestrator for **#56**. Assess whether useful compatibility and cost guidance is feasible without hiding runtime conditions or producing false precision. Execute authorized research, validation, commit, push, branch synchronization, review and qualifying merge—not just analysis or task creation. Publishing this prompt does not execute it. Read `AGENTS.md`, current contributor/governance/research instructions and `prompts/market/SHARED.md` first. Preserve the current issue, acceptance criteria, actual assignees, active work and explicit owner decisions.

## Scope and writable deliverables

Own market-facing feasibility risks and their synthesis. Sizing models (#10), runtimes (#11), retrieval (#16), evaluations (#36), cost semantics (#39) and compatibility rules (#40) remain with their technical owners. Coordinate children #61/#62/#65 without taking over their deliverables.

Use the existing canonical deliverable paths:

- `research/market/technical-feasibility.md`

Read and coordinate the existing research/market/mr09-acceptance.md matrix and associated PR #79 evidence. Do not overwrite #61’s matrix contributions, #59’s ledgers or another owner’s source/evaluation work.

## Starting context to verify

Do not restart from the stale issue-body statement that no measurements ran. PR #79 reports fifteen dense GPU runs and was verified merged into research/market-intelligence at 6511dea2a5102b13df1e47378a31f31230ecb494; PR #67 remained open against main. Comparable estimator/runtime pairs were still zero; MoE and multi-GPU coverage and explicit owner handoffs remained incomplete. Inspect the linked PR #80 follow-up and current artifacts before relying on this dated snapshot.

This is a dated starting reference, not an instruction to preserve stale status. Read the latest comments, artifact contents, exact PR bases/heads and review decisions before changing anything. Unmerged research is not accepted evidence. A closed PR must be checked for its actual merge target.

## Orchestrated execution

Use one coordinating writer for the issue. With available subagents, separate evidence collection, acceptance/contract checking and adversarial review into bounded, nonoverlapping passes; otherwise perform the passes sequentially without claiming independent agents or human approvals. Assign no new GitHub owner merely because a name appears in a historical body. Maintain an acceptance map from the live criterion to artifact, evidence, check, required reviewer and remaining gap.

### 1. Reconcile current evidence and acceptance

Read PR #67, merged #79, linked #80, latest issue comments and research/market/mr09-acceptance.md. Verify which artifacts reached which branch, which reviews apply, and which exact criteria remain. Preserve the existing acceptance matrix and coordinate edits with #61.

### 2. Expose estimator and runtime assumptions

Compare model artifact, architecture, weight precision, KV precision, context, active sequences, offload, allocation pools, headroom and device topology. Separate payload size, allocated memory, reserved memory and device budget. Do not compare numbers with different quantities or units as though they measure the same thing.

### 3. Use empirical results within their limits

Consume #61’s actual pinned observations with their conditions. Fifteen dense runs support only their tested cases; zero comparable competitor/runtime pairs do not support a calibrated estimator error range. Do not relabel tensor-layout checks as total-memory accuracy or infer MoE/multi-GPU behavior.

### 4. Coordinate specialized validation

Keep #62 responsible for benchmark task/release identity and controlled harness comparisons; keep #65 responsible for RAG contract and connector claims. Route technical questions to the existing owners. PR #75 is reference material, not an automatic merge dependency or accepted answer.

### 5. Write falsifiable feasibility risks

For each material risk, record a hypothesis, bounded test or evidence need, affected user decision, responsible owner and possible narrowing/stop implication. Explain what conditions a useful MVP must disclose. Numeric product success thresholds require the coordinator’s explicit decision.

### 6. Publish the bounded feasibility handoff

Offer #58 a precise accept/narrow/reject decision input without claiming MVP acceptance. Coordinate recorded owner dispositions with #59. A partial feasibility update may merge normally, but #56 cannot close until #61/#62/#65 and its own criteria and handoffs are complete.

## Dependencies and handoffs

**Native children:** [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61), [#62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62), [#65](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/65)

**Native blocked-by prerequisites:** None specified in the inspected snapshot.

**Native downstream issues blocked by this issue:** None specified in the inspected snapshot.

**Market information/coordination links, not newly created blockers:** [#58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58)

**Project #1 receiving issues — information/review, not ownership transfer:** [#7](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7), [#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10), [#11](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11), [#16](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16), [#25](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25), [#27](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/27), [#33](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/33), [#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36), [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39), [#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40)

Read current receiving owners and request an explicit accept/reject/narrow disposition for each material handoff, identifying the exact artifact revision, conditions, fields or claim, and remaining question. Coordinate the canonical handoff ledger with #59. A request for review or general PR approval does not prove that a specific owner accepted a handoff. Preserve native relationships unless their predicate is genuinely resolved through the accepted workflow.

## Acceptance criteria to preserve

These are the issue criteria captured for this package. Re-read the live issue and preserve any later accepted changes; never silently remove a criterion to make the task finish.

- [ ] Compare sizing assumptions
- [ ] Assess context cache concurrency and multi-GPU limits
- [ ] Define falsifiable measurement protocol
- [ ] Reuse technical component decisions rather than duplicate them
- [ ] Deliverable links every significant conclusion to evidence or an explicit hypothesis.
- [ ] Relevant technical owners review handoffs; unresolved decisions are named.
- [ ] Repository checks pass; reviewer accepts the evidence before Done.

**Issue-specific completion gate:** Proposal-branch merge, structural validation and partial dense measurements are separate milestones. None alone completes #56 or approves a product claim.

## Commit, push, sync and merge this issue

Execute this delivery loop after the research passes above; do not stop at a plan or an unpushed local edit. Apply the detailed safeguards in `SHARED.md`.

1. Refresh the actual repository, issue, active PRs and base; preserve current assignees and other writers. Use a clean isolated worktree and a focused issue branch. Reuse the existing authorized work instead of launching a duplicate. If the deliverables only exist on an unmerged proposal branch, coordinate a declared editing dependency; do not silently import or merge unrelated work.
2. Run the current Python 3.12 research workflow, applicable market validator, `git diff --check` and claim/evidence review. Record the actual commands and results for this revision. Validators do not prove truth, rights, empirical success or owner acceptance.
3. Inspect and stage only the intended files, commit with a meaningful reference to issue #56, push, and verify the remote head SHA. Open or update the focused PR using **`Refs #56`** for a partial contribution.
4. Fetch the current base and head, synchronize the contribution safely, inspect the new diff and rerun affected checks. Obtain the required independent reviewer and explicit receiving-owner dispositions. Preserve reviews/holds and refresh approvals after any head change; no self-approval, blind force push or protection bypass.
5. Merge the qualifying final head using the permitted normal method and a head-SHA guard where available. A valid partial PR may merge while this issue remains open. A merge into a proposal branch is **not** delivery to main. Use **`Closes #56`** only when a canonical-main merge will satisfy every live criterion, native child/prerequisite gate and required handoff.
6. Verify the actual merge destination, commit, files and post-merge checks; safely synchronize a clean local verification checkout. Only then reconcile issue/Project #2 state using live fields, preserving unrelated values and reading changes back. Do not claim Done or synchronization without that evidence.

If an external decision, unavailable resource or permission blocks an action, complete the independent permitted work and return an exact blocker plus a ZIP/diff and replay steps. Do not fabricate execution, approval, participant evidence, commit/push/merge status or future background work.

## Required final report

Report #56’s completed and remaining criteria, changed files, source/evidence limitations, actual validation commands/results, branch and commit SHA, pushed remote head, PR URL and base, review/owner dispositions, merge commit and destination, canonical-main verification and any actual Project readback. Separate partial delivery from issue completion. Name the exact missing permission, artifact, experiment, decision or reviewer action when blocked.
