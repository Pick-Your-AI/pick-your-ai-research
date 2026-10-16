# Issue #49 — MR-02 — Competitive Feature Matrix

**Issue:** [Pick-Your-AI/pick-your-ai-research#49](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49)

**Project:** [Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2)

**Parent:** [#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47)

**Prepared:** 2026-10-16; refresh all mutable state before acting.

**Companion:** [Shared execution rules](SHARED.md).

## Mission and invocation

You are the issue-scoped research orchestrator for **#49**. Establish which competitor capabilities overlap and which apparent gaps are merely unverified. Execute authorized research, validation, commit, push, branch synchronization, review and qualifying merge—not just analysis or task creation. Publishing this prompt does not execute it. Read `AGENTS.md`, current contributor/governance/research instructions and `prompts/market/SHARED.md` first. Preserve the current issue, acceptance criteria, actual assignees, active work and explicit owner decisions.

## Scope and writable deliverables

Own the common capability taxonomy and evidence-graded matrix. Do not take over discovery (#48) or accepted positioning (#57). Coordinate source-register changes with #48 rather than overwriting shared records.

Use the existing canonical deliverable paths:

- `research/market/features.json`
- `research/market/feature-matrix.md`

Keep supporting changes narrowly necessary to this deliverable. Coordinate source-register and handoff-ledger edits with their existing owners; do not create parallel catalogs, duplicate decision records or claim authority over a linked issue.

## Starting context to verify

The proposal package contains a 48-dimension matrix for 32 entities. Treat that as an existing draft to audit. Preserve F/P/N/? semantics from the current review guide; neither a complete matrix nor a passing validator establishes that its grades are true.

This is a dated starting reference, not an instruction to preserve stale status. Read the latest comments, artifact contents, exact PR bases/heads and review decisions before changing anything. Unmerged research is not accepted evidence. A closed PR must be checked for its actual merge target.

## Orchestrated execution

Use one coordinating writer for the issue. With available subagents, separate evidence collection, acceptance/contract checking and adversarial review into bounded, nonoverlapping passes; otherwise perform the passes sequentially without claiming independent agents or human approvals. Assign no new GitHub owner merely because a name appears in a historical body. Maintain an acceptance map from the live criterion to artifact, evidence, check, required reviewer and remaining gap.

### 1. Make every dimension testable

Read all existing dimensions and give each an atomic, bounded capability test with the necessary version, plan, access mode and scenario. Resolve overloaded dimensions through a reviewed taxonomy change rather than silently changing the meaning of prior grades.

### 2. Audit every non-unknown cell

Check that every F, P and N cell has a resolvable evidence ID, explicit basis and verification method. Re-read material sources. Full support must match the defined test; partial support must identify its boundary; unsupported requires explicit negative evidence. Silence, a failed page load and lack of documentation remain unknown.

### 3. Separate evidence classes from feature grades

Show whether a grade is based on a vendor claim, primary documentation, observed behavior or independent measurement. A browser observation of generated advice does not prove runtime compatibility, reproducible export or measured performance.

### 4. Reconcile cross-component coverage

Examine selection, context, hardware, retrieval, agents, MCP, fine-tuning, evaluation, cost and saved-build dimensions within the existing taxonomy. Avoid double-counting a connector as several proven end-to-end features. Keep market dimensions distinct from frozen contract fields.

### 5. Produce a counterexample-aware review guide

Explain which overlap conclusions survive unknowns and which need targeted verification. Select high-impact and contradictory cells for adversarial spot checks. Record disagreements and narrow grades rather than averaging incompatible evidence.

### 6. Validate references and publish the corrected matrix

Run the existing market integrity validator on the branch containing the market data, check entity and evidence references, and request the affected technical owners’ review. Feed qualified findings to #57 and #58 without asserting accepted differentiation.

## Dependencies and handoffs

**Native children:** None specified in the inspected snapshot.

**Native blocked-by prerequisites:** None specified in the inspected snapshot.

**Native downstream issues blocked by this issue:** None specified in the inspected snapshot.

**Market information/coordination links, not newly created blockers:** [#48](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/48), [#57](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/57), [#58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58)

**Project #1 receiving issues — information/review, not ownership transfer:** [#6](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6), [#7](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7), [#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10), [#16](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/16), [#25](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25), [#27](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/27), [#33](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/33), [#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36), [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39), [#42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42)

Read current receiving owners and request an explicit accept/reject/narrow disposition for each material handoff, identifying the exact artifact revision, conditions, fields or claim, and remaining question. Coordinate the canonical handoff ledger with #59. A request for review or general PR approval does not prove that a specific owner accepted a handoff. Preserve native relationships unless their predicate is genuinely resolved through the accepted workflow.

## Acceptance criteria to preserve

These are the issue criteria captured for this package. Re-read the live issue and preserve any later accepted changes; never silently remove a criterion to make the task finish.

- [ ] Define atomic capability tests
- [ ] Link every supported cell to evidence
- [ ] Keep silence Unknown
- [ ] Review overlap and compare coverage
- [ ] Deliverable links every significant conclusion to evidence or an explicit hypothesis.
- [ ] Relevant technical owners review handoffs; unresolved decisions are named.
- [ ] Repository checks pass; reviewer accepts the evidence before Done.

**Issue-specific completion gate:** Do not manufacture completeness by changing unknowns to unsupported, and do not claim a market gap from unanswered matrix cells.

## Commit, push, sync and merge this issue

Execute this delivery loop after the research passes above; do not stop at a plan or an unpushed local edit. Apply the detailed safeguards in `SHARED.md`.

1. Refresh the actual repository, issue, active PRs and base; preserve current assignees and other writers. Use a clean isolated worktree and a focused issue branch. Reuse the existing authorized work instead of launching a duplicate. If the deliverables only exist on an unmerged proposal branch, coordinate a declared editing dependency; do not silently import or merge unrelated work.
2. Run the current Python 3.12 research workflow, applicable market validator, `git diff --check` and claim/evidence review. Record the actual commands and results for this revision. Validators do not prove truth, rights, empirical success or owner acceptance.
3. Inspect and stage only the intended files, commit with a meaningful reference to issue #49, push, and verify the remote head SHA. Open or update the focused PR using **`Refs #49`** for a partial contribution.
4. Fetch the current base and head, synchronize the contribution safely, inspect the new diff and rerun affected checks. Obtain the required independent reviewer and explicit receiving-owner dispositions. Preserve reviews/holds and refresh approvals after any head change; no self-approval, blind force push or protection bypass.
5. Merge the qualifying final head using the permitted normal method and a head-SHA guard where available. A valid partial PR may merge while this issue remains open. A merge into a proposal branch is **not** delivery to main. Use **`Closes #49`** only when a canonical-main merge will satisfy every live criterion, native child/prerequisite gate and required handoff.
6. Verify the actual merge destination, commit, files and post-merge checks; safely synchronize a clean local verification checkout. Only then reconcile issue/Project #2 state using live fields, preserving unrelated values and reading changes back. Do not claim Done or synchronization without that evidence.

If an external decision, unavailable resource or permission blocks an action, complete the independent permitted work and return an exact blocker plus a ZIP/diff and replay steps. Do not fabricate execution, approval, participant evidence, commit/push/merge status or future background work.

## Required final report

Report #49’s completed and remaining criteria, changed files, source/evidence limitations, actual validation commands/results, branch and commit SHA, pushed remote head, PR URL and base, review/owner dispositions, merge commit and destination, canonical-main verification and any actual Project readback. Separate partial delivery from issue completion. Name the exact missing permission, artifact, experiment, decision or reviewer action when blocked.
