# Issue #62 — MR-09: Validate benchmark comparability and harness effects

**Issue:** [Pick-Your-AI/pick-your-ai-research#62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62)

**Project:** [Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2)

**Parent:** [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56)

**Prepared:** 2026-10-16; refresh all mutable state before acting.

**Companion:** [Shared execution rules](SHARED.md).

## Mission and invocation

You are the issue-scoped research orchestrator for **#62**. Determine which benchmark differences remain meaningful when model, harness, budget and task-set conditions are controlled. Execute authorized research, validation, commit, push, branch synchronization, review and qualifying merge—not just analysis or task creation. Publishing this prompt does not execute it. Read `AGENTS.md`, current contributor/governance/research instructions and `prompts/market/SHARED.md` first. Preserve the current issue, acceptance criteria, actual assignees, active work and explicit owner decisions.

## Scope and writable deliverables

Own comparability research and bounded replication findings. Do not take over #36’s product evaluation program, run paid APIs without approval, or infer reuse permission from a public repository with unclear licensing.

Use the existing canonical deliverable paths:

- `research/market/benchmark-validation.md`

Keep supporting changes narrowly necessary to this deliverable. Coordinate source-register and handoff-ledger edits with their existing owners; do not create parallel catalogs, duplicate decision records or claim authority over a linked issue.

## Starting context to verify

The issue flags Harness Bench task-count inconsistencies. Newer #56 discussion distinguishes a v2 landing abstract with 106 tasks from v2 body/current-release references to 300. Verify the actual paper, release, task locks and result identities; do not collapse the discrepancy into an unsupported paper-versus-repository story.

This is a dated starting reference, not an instruction to preserve stale status. Read the latest comments, artifact contents, exact PR bases/heads and review decisions before changing anything. Unmerged research is not accepted evidence. A closed PR must be checked for its actual merge target.

## Orchestrated execution

Use one coordinating writer for the issue. With available subagents, separate evidence collection, acceptance/contract checking and adversarial review into bounded, nonoverlapping passes; otherwise perform the passes sequentially without claiming independent agents or human approvals. Assign no new GitHub owner merely because a name appears in a historical body. Maintain an acceptance map from the live criterion to artifact, evidence, check, required reviewer and remaining gap.

### 1. Reconcile benchmark identities first

Read official paper versions, release notes, repository revisions, task lists and available result manifests. Record exactly which version and task-set count each claim concerns. Distinguish a stale abstract, changed release and different evaluation subset instead of combining their results.

### 2. Define controlled comparisons

Pin model and provider revision, harness/scaffold commit, tool environment, prompt/configuration, token or compute budget, task-set version and evaluator. Compare the same model across harnesses only where those other conditions are controlled or explicitly analyzed.

### 3. Audit task overlap and contamination limits

Describe overlap, selection, exposure and available contamination evidence. State what cannot be checked. Do not claim a clean benchmark merely because contamination was not reported, or treat disjoint task sets as a controlled comparison.

### 4. Separate score from complete delivery

Report mean score, task completion and end-to-end delivery as different outcomes under the actual evaluation definitions. Include failures, retries, budget constraints and uncertainty. Avoid universal rankings or causal harness claims from uncontrolled aggregate scores.

### 5. Replicate only within scope and rights

Reuse permitted public artifacts or run authorized bounded tests when tools, resources and licenses allow. Obtain approval before paid runs. A protocol, source re-analysis and an actual replication are separate evidence classes; label each honestly and document exact replication limits.

### 6. Publish comparable findings and exclusions

Explain which published comparisons can be used, narrowed or excluded and why. Hand the version-pinned findings to #25 and #36, retain #36’s ownership of evaluation methodology and request the required evidence review.

## Dependencies and handoffs

**Native children:** None specified in the inspected snapshot.

**Native blocked-by prerequisites:** None specified in the inspected snapshot.

**Native downstream issues blocked by this issue:** None specified in the inspected snapshot.

**Market information/coordination links, not newly created blockers:** [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56)

**Project #1 receiving issues — information/review, not ownership transfer:** [#25](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25), [#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36)

Read current receiving owners and request an explicit accept/reject/narrow disposition for each material handoff, identifying the exact artifact revision, conditions, fields or claim, and remaining question. Coordinate the canonical handoff ledger with #59. A request for review or general PR approval does not prove that a specific owner accepted a handoff. Preserve native relationships unless their predicate is genuinely resolved through the accepted workflow.

## Acceptance criteria to preserve

These are the issue criteria captured for this package. Re-read the live issue and preserve any later accepted changes; never silently remove a criterion to make the task finish.

- [ ] Pin models harnesses budgets and task versions
- [ ] Check contamination and task overlap
- [ ] Separate mean score from complete delivery
- [ ] Record replication limits and confidence
- [ ] Deliverable links every significant conclusion to evidence or an explicit hypothesis.
- [ ] Relevant technical owners review handoffs; unresolved decisions are named.
- [ ] Repository checks pass; reviewer accepts the evidence before Done.

**Issue-specific completion gate:** Do not present mixed releases, unmatched budgets or task-set changes as measured harness effects. Missing licensing, access or comparable result locks must remain explicit.

## Commit, push, sync and merge this issue

Execute this delivery loop after the research passes above; do not stop at a plan or an unpushed local edit. Apply the detailed safeguards in `SHARED.md`.

1. Refresh the actual repository, issue, active PRs and base; preserve current assignees and other writers. Use a clean isolated worktree and a focused issue branch. Reuse the existing authorized work instead of launching a duplicate. If the deliverables only exist on an unmerged proposal branch, coordinate a declared editing dependency; do not silently import or merge unrelated work.
2. Run the current Python 3.12 research workflow, applicable market validator, `git diff --check` and claim/evidence review. Record the actual commands and results for this revision. Validators do not prove truth, rights, empirical success or owner acceptance.
3. Inspect and stage only the intended files, commit with a meaningful reference to issue #62, push, and verify the remote head SHA. Open or update the focused PR using **`Refs #62`** for a partial contribution.
4. Fetch the current base and head, synchronize the contribution safely, inspect the new diff and rerun affected checks. Obtain the required independent reviewer and explicit receiving-owner dispositions. Preserve reviews/holds and refresh approvals after any head change; no self-approval, blind force push or protection bypass.
5. Merge the qualifying final head using the permitted normal method and a head-SHA guard where available. A valid partial PR may merge while this issue remains open. A merge into a proposal branch is **not** delivery to main. Use **`Closes #62`** only when a canonical-main merge will satisfy every live criterion, native child/prerequisite gate and required handoff.
6. Verify the actual merge destination, commit, files and post-merge checks; safely synchronize a clean local verification checkout. Only then reconcile issue/Project #2 state using live fields, preserving unrelated values and reading changes back. Do not claim Done or synchronization without that evidence.

If an external decision, unavailable resource or permission blocks an action, complete the independent permitted work and return an exact blocker plus a ZIP/diff and replay steps. Do not fabricate execution, approval, participant evidence, commit/push/merge status or future background work.

## Required final report

Report #62’s completed and remaining criteria, changed files, source/evidence limitations, actual validation commands/results, branch and commit SHA, pushed remote head, PR URL and base, review/owner dispositions, merge commit and destination, canonical-main verification and any actual Project readback. Separate partial delivery from issue completion. Name the exact missing permission, artifact, experiment, decision or reviewer action when blocked.
