# Issue #48 — MR-01 — Competitive Landscape Discovery

**Issue:** [Pick-Your-AI/pick-your-ai-research#48](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/48)

**Project:** [Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2)

**Parent:** [#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47)

**Prepared:** 2026-10-16; refresh all mutable state before acting.

**Companion:** [Shared execution rules](SHARED.md).

## Mission and invocation

You are the issue-scoped research orchestrator for **#48**. Identify existing products, tools, datasets and services that already solve the AI selection decision, including direct substitutes. Execute authorized research, validation, commit, push, branch synchronization, review and qualifying merge—not just analysis or task creation. Publishing this prompt does not execute it. Read `AGENTS.md`, current contributor/governance/research instructions and `prompts/market/SHARED.md` first. Preserve the current issue, acceptance criteria, actual assignees, active work and explicit owner decisions.

## Scope and writable deliverables

Own landscape discovery and the source register. Feature-level grading belongs to #49, deep profiles to #50 and monetization analysis to #54. Keep these market observations separate from production component catalogs.

Use the existing canonical deliverable paths:

- `research/market/competitors.json`
- `research/market/sources.json`

Keep supporting changes narrowly necessary to this deliverable. Coordinate source-register and handoff-ledger edits with their existing owners; do not create parallel catalogs, duplicate decision records or claim authority over a linked issue.

## Starting context to verify

PR #67 contains a draft landscape of 32 resources. Review and extend it rather than recreating IDs or replacing its source register. The issue requires at least 30 distinct resources and selection of 10–15 material deep dives; the market method’s normal discovery bound is 30–40.

This is a dated starting reference, not an instruction to preserve stale status. Read the latest comments, artifact contents, exact PR bases/heads and review decisions before changing anything. Unmerged research is not accepted evidence. A closed PR must be checked for its actual merge target.

## Orchestrated execution

Use one coordinating writer for the issue. With available subagents, separate evidence collection, acceptance/contract checking and adversarial review into bounded, nonoverlapping passes; otherwise perform the passes sequentially without claiming independent agents or human approvals. Assign no new GitHub owner merely because a name appears in a historical body. Maintain an acceptance map from the live criterion to artifact, evidence, check, required reviewer and remaining gap.

### 1. Recover the actual seed list

Read the named seeds and candidates from the current issue, landscape documents and catalog. Verify all five original seeds using their official sites, documentation or repositories. Do not substitute a guessed seed list, infer the operator from a similar name, or conflate a website, repository, company and product.

### 2. Audit entity boundaries and evidence IDs

For each existing entity, verify canonical identity, operator where established, product scope, official URL, access date and relevant version. Preserve stable IDs and references. Record ambiguous affiliations and failed access as unverified instead of inventing ownership or declaring the product absent.

### 3. Complete bounded discovery

Classify at least thirty distinct resources across model choice, hardware fit, runtimes, benchmarks, data feeds and guided stacks as the existing taxonomy permits. Snowball from primary sources and include material counterexamples. Expand beyond the normal bound only when decision-changing evidence justifies it and the owner records the reason.

### 4. Test the direct-substitute assumption

Locate resources that claim or demonstrate workload-first, multi-tier selection, compatibility explanations and reusable configurations. Distinguish an advertised capability from an observed workflow. Route hands-on falsification candidates to #66 through #50 rather than claiming that broad landscape coverage proves no substitute exists.

### 5. Select deep dives with an explicit rationale

Choose ten to fifteen material entities for #50 using overlap with the target decision, evidence availability, substitution risk and source relevance. Explain exclusions without turning analyst selection into an empirical vendor ranking.

### 6. Integrate source contributions without collisions

Reconcile contributions from other issue agents into sources.json in a controlled, serialized change. Check entity/source references and validator output. Submit the verified landscape and selection rationale, request consumer review and preserve all unverified fields.

## Dependencies and handoffs

**Native children:** None specified in the inspected snapshot.

**Native blocked-by prerequisites:** None specified in the inspected snapshot.

**Native downstream issues blocked by this issue:** None specified in the inspected snapshot.

**Market information/coordination links, not newly created blockers:** [#49](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49), [#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50), [#57](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/57)

**Project #1 receiving issues — information/review, not ownership transfer:** [#6](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6), [#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10), [#25](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25), [#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41)

Read current receiving owners and request an explicit accept/reject/narrow disposition for each material handoff, identifying the exact artifact revision, conditions, fields or claim, and remaining question. Coordinate the canonical handoff ledger with #59. A request for review or general PR approval does not prove that a specific owner accepted a handoff. Preserve native relationships unless their predicate is genuinely resolved through the accepted workflow.

## Acceptance criteria to preserve

These are the issue criteria captured for this package. Re-read the live issue and preserve any later accepted changes; never silently remove a criterion to make the task finish.

- [ ] Verify all five seeds
- [ ] Classify at least 30 distinct resources
- [ ] Record entity boundaries and unknowns
- [ ] Select 10–15 material deep dives
- [ ] Deliverable links every significant conclusion to evidence or an explicit hypothesis.
- [ ] Relevant technical owners review handoffs; unresolved decisions are named.
- [ ] Repository checks pass; reviewer accepts the evidence before Done.

**Issue-specific completion gate:** Thirty entries are not sufficient by themselves: seed verification, distinct identities, evidence traceability, deep-dive selection and required handoff review must also be satisfied.

## Commit, push, sync and merge this issue

Execute this delivery loop after the research passes above; do not stop at a plan or an unpushed local edit. Apply the detailed safeguards in `SHARED.md`.

1. Refresh the actual repository, issue, active PRs and base; preserve current assignees and other writers. Use a clean isolated worktree and a focused issue branch. Reuse the existing authorized work instead of launching a duplicate. If the deliverables only exist on an unmerged proposal branch, coordinate a declared editing dependency; do not silently import or merge unrelated work.
2. Run the current Python 3.12 research workflow, applicable market validator, `git diff --check` and claim/evidence review. Record the actual commands and results for this revision. Validators do not prove truth, rights, empirical success or owner acceptance.
3. Inspect and stage only the intended files, commit with a meaningful reference to issue #48, push, and verify the remote head SHA. Open or update the focused PR using **`Refs #48`** for a partial contribution.
4. Fetch the current base and head, synchronize the contribution safely, inspect the new diff and rerun affected checks. Obtain the required independent reviewer and explicit receiving-owner dispositions. Preserve reviews/holds and refresh approvals after any head change; no self-approval, blind force push or protection bypass.
5. Merge the qualifying final head using the permitted normal method and a head-SHA guard where available. A valid partial PR may merge while this issue remains open. A merge into a proposal branch is **not** delivery to main. Use **`Closes #48`** only when a canonical-main merge will satisfy every live criterion, native child/prerequisite gate and required handoff.
6. Verify the actual merge destination, commit, files and post-merge checks; safely synchronize a clean local verification checkout. Only then reconcile issue/Project #2 state using live fields, preserving unrelated values and reading changes back. Do not claim Done or synchronization without that evidence.

If an external decision, unavailable resource or permission blocks an action, complete the independent permitted work and return an exact blocker plus a ZIP/diff and replay steps. Do not fabricate execution, approval, participant evidence, commit/push/merge status or future background work.

## Required final report

Report #48’s completed and remaining criteria, changed files, source/evidence limitations, actual validation commands/results, branch and commit SHA, pushed remote head, PR URL and base, review/owner dispositions, merge commit and destination, canonical-main verification and any actual Project readback. Separate partial delivery from issue completion. Name the exact missing permission, artifact, experiment, decision or reviewer action when blocked.
