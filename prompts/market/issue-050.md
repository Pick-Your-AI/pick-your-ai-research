# Issue #50 — MR-03 — Competitor Deep Dives

**Issue:** [Pick-Your-AI/pick-your-ai-research#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50)

**Project:** [Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2)

**Parent:** [#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47)

**Prepared:** 2026-10-16; refresh all mutable state before acting.

**Companion:** [Shared execution rules](SHARED.md).

## Mission and invocation

You are the issue-scoped research orchestrator for **#50**. Explain how the strongest substitutes solve the target user decision and whether any makes the proposed product redundant for a segment. Execute authorized research, validation, commit, push, branch synchronization, review and qualifying merge—not just analysis or task creation. Publishing this prompt does not execute it. Read `AGENTS.md`, current contributor/governance/research instructions and `prompts/market/SHARED.md` first. Preserve the current issue, acceptance criteria, actual assignees, active work and explicit owner decisions.

## Scope and writable deliverables

Own the profile index and the existing competitor profile files selected with #48. Hands-on direct-substitute testing is separately owned by child #66. Avoid an exhaustive profile for every landscape entry.

Use the existing canonical deliverable paths:

- `research/market/competitors/README.md`

Additional writable scope is limited to the existing selected files beneath research/market/competitors/, coordinated with their active writers. The index is not permission to overwrite every profile.

## Starting context to verify

PR #67 contains thirteen draft desk profiles, including Flocci, ModelFit and llmfit. Review those exact paths and their evidence before expanding coverage. Profile claims are not hands-on test results.

This is a dated starting reference, not an instruction to preserve stale status. Read the latest comments, artifact contents, exact PR bases/heads and review decisions before changing anything. Unmerged research is not accepted evidence. A closed PR must be checked for its actual merge target.

## Orchestrated execution

Use one coordinating writer for the issue. With available subagents, separate evidence collection, acceptance/contract checking and adversarial review into bounded, nonoverlapping passes; otherwise perform the passes sequentially without claiming independent agents or human approvals. Assign no new GitHub owner merely because a name appears in a historical body. Maintain an acceptance map from the live criterion to artifact, evidence, check, required reviewer and remaining gap.

### 1. Confirm the review set

Use #48’s documented selection to confirm ten to fifteen material profiles. Preserve entity IDs and existing profile paths. Prioritize direct substitution risk and decision-changing evidence instead of choosing only products that make Pick Your AI look differentiated.

### 2. Reconstruct each product workflow

Document entry inputs, constraint handling, component selection, explanation, saved output, export and the observable architecture where supported by primary sources. State access tier and version. Separate what was exercised from what was described by the vendor.

### 3. Analyze commercial and technical boundaries

Distinguish access to a hosted product, source-code licensing, data reuse, commercial display and export rights. Record API or authentication limitations without bypassing them. Route unresolved rights questions to #55/#60 and #41.

### 4. Coordinate, do not duplicate, the substitute experiment

Read #66’s current test plan, observations and active branch. Ensure the selected profiles accurately describe those bounded observations. Do not run a second uncoordinated test controller or edit substitute-validation.md from the profile task.

### 5. Write material counterexamples

For each differentiation claim, identify the strongest competing workflow and the scenario in which it could suffice. Record constraints or verification gaps explicitly; avoid interpreting missing documentation as a missing feature.

### 6. Publish the index and scoped profiles

Keep the index, linked profiles and landscape references consistent. Request evidence review and the relevant technical handoffs. A profile-only slice can merge with Refs #50 while #66 remains open, but the parent cannot close before its child and its own criteria are complete.

## Dependencies and handoffs

**Native children:** [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66)

**Native blocked-by prerequisites:** None specified in the inspected snapshot.

**Native downstream issues blocked by this issue:** None specified in the inspected snapshot.

**Market information/coordination links, not newly created blockers:** [#48](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/48), [#57](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/57)

**Project #1 receiving issues — information/review, not ownership transfer:** [#6](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6), [#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10), [#25](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25), [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39), [#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41)

Read current receiving owners and request an explicit accept/reject/narrow disposition for each material handoff, identifying the exact artifact revision, conditions, fields or claim, and remaining question. Coordinate the canonical handoff ledger with #59. A request for review or general PR approval does not prove that a specific owner accepted a handoff. Preserve native relationships unless their predicate is genuinely resolved through the accepted workflow.

## Acceptance criteria to preserve

These are the issue criteria captured for this package. Re-read the live issue and preserve any later accepted changes; never silently remove a criterion to make the task finish.

- [ ] Review 10–15 profiles
- [ ] Analyze workflow and architecture
- [ ] Separate commercial access from reuse rights
- [ ] Test material differentiation counterexamples
- [ ] Deliverable links every significant conclusion to evidence or an explicit hypothesis.
- [ ] Relevant technical owners review handoffs; unresolved decisions are named.
- [ ] Repository checks pass; reviewer accepts the evidence before Done.

**Issue-specific completion gate:** Do not close #50 on desk profiles alone while the required direct-substitute child remains unresolved.

## Commit, push, sync and merge this issue

Execute this delivery loop after the research passes above; do not stop at a plan or an unpushed local edit. Apply the detailed safeguards in `SHARED.md`.

1. Refresh the actual repository, issue, active PRs and base; preserve current assignees and other writers. Use a clean isolated worktree and a focused issue branch. Reuse the existing authorized work instead of launching a duplicate. If the deliverables only exist on an unmerged proposal branch, coordinate a declared editing dependency; do not silently import or merge unrelated work.
2. Run the current Python 3.12 research workflow, applicable market validator, `git diff --check` and claim/evidence review. Record the actual commands and results for this revision. Validators do not prove truth, rights, empirical success or owner acceptance.
3. Inspect and stage only the intended files, commit with a meaningful reference to issue #50, push, and verify the remote head SHA. Open or update the focused PR using **`Refs #50`** for a partial contribution.
4. Fetch the current base and head, synchronize the contribution safely, inspect the new diff and rerun affected checks. Obtain the required independent reviewer and explicit receiving-owner dispositions. Preserve reviews/holds and refresh approvals after any head change; no self-approval, blind force push or protection bypass.
5. Merge the qualifying final head using the permitted normal method and a head-SHA guard where available. A valid partial PR may merge while this issue remains open. A merge into a proposal branch is **not** delivery to main. Use **`Closes #50`** only when a canonical-main merge will satisfy every live criterion, native child/prerequisite gate and required handoff.
6. Verify the actual merge destination, commit, files and post-merge checks; safely synchronize a clean local verification checkout. Only then reconcile issue/Project #2 state using live fields, preserving unrelated values and reading changes back. Do not claim Done or synchronization without that evidence.

If an external decision, unavailable resource or permission blocks an action, complete the independent permitted work and return an exact blocker plus a ZIP/diff and replay steps. Do not fabricate execution, approval, participant evidence, commit/push/merge status or future background work.

## Required final report

Report #50’s completed and remaining criteria, changed files, source/evidence limitations, actual validation commands/results, branch and commit SHA, pushed remote head, PR URL and base, review/owner dispositions, merge commit and destination, canonical-main verification and any actual Project readback. Separate partial delivery from issue completion. Name the exact missing permission, artifact, experiment, decision or reviewer action when blocked.

## Additional intake: CanIRun.ai (2026-10-16)

Include `canirun-ai` / https://www.canirun.ai/devices in this issue's existing scope. Read [the profile](../../research/market/competitors/canirun-ai.md), `src-canirun-ai` and its matrix cells. Do not conflate it with `canrun` or `canitrun`. Directory inspection is documentary evidence, not a completed scenario. Preserve live owners, prior test order and acceptance gates; this addition does not authorize unrelated work.
