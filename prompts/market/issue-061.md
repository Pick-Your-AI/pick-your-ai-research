# Issue #61 — MR-09: Validate GPU sizing against pinned runtime measurements

**Issue:** [Pick-Your-AI/pick-your-ai-research#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61)

**Project:** [Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2)

**Parent:** [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56)

**Prepared:** 2026-10-16; refresh all mutable state before acting.

**Companion:** [Shared execution rules](SHARED.md).

## Mission and invocation

You are the issue-scoped research orchestrator for **#61**. Determine where third-party memory/fit estimates agree with or fail against comparable, pinned runtime measurements. Execute authorized research, validation, commit, push, branch synchronization, review and qualifying merge—not just analysis or task creation. Publishing this prompt does not execute it. Read `AGENTS.md`, current contributor/governance/research instructions and `prompts/market/SHARED.md` first. Preserve the current issue, acceptance criteria, actual assignees, active work and explicit owner decisions.

## Scope and writable deliverables

Own estimator-versus-runtime validation, not the product sizing model or new ResourceEstimate records owned by #10. Preserve the user’s spare-local-capacity-only constraint, existing resource guards and other workloads. No paid compute or second device without explicit authorization.

Use the existing canonical deliverable paths:

- `research/market/sizing-validation.md`

Existing PR #79 instruments, sanitized result files and research/market/mr09-acceptance.md may be changed only within an agreed #56/#61 boundary. Do not fabricate a new canonical runtime artifact to satisfy a schema or take over #10’s sizing research.

## Starting context to verify

PR #79 reports fifteen successful dense runs: five configurations with three isolated repetitions, using pinned SmolLM2-135M BF16 weights, context/KV/active-sequence variations and synchronized allocated/reserved phases. It merged into the market proposal branch, not main. Comparable competitor/runtime pairs were zero; nine native KV payload checks were layout checks, not total-memory calibration. MoE and multi-GPU execution remained absent.

This is a dated starting reference, not an instruction to preserve stale status. Read the latest comments, artifact contents, exact PR bases/heads and review decisions before changing anything. Unmerged research is not accepted evidence. A closed PR must be checked for its actual merge target.

## Orchestrated execution

Use one coordinating writer for the issue. With available subagents, separate evidence collection, acceptance/contract checking and adversarial review into bounded, nonoverlapping passes; otherwise perform the passes sequentially without claiming independent agents or human approvals. Assign no new GitHub owner merely because a name appears in a historical body. Maintain an acceptance map from the live criterion to artifact, evidence, check, required reviewer and remaining gap.

### 1. Resume the existing experiment, not a substitute campaign

Read PR #79, linked #80, latest #61 comments, the committed instrument/protocol, sizing-validation.md and mr09-acceptance.md. Verify artifact revisions, result hashes, actual review state and current hardware permissions. Preserve valid results and identify precisely which acceptance cells remain incomplete.

### 2. Keep predeclared resource guards intact

Confirm authorized spare GPU, RAM and disk capacity before downloads or execution. Do not lower the existing guards, evict unrelated workloads or treat a failed preflight as permission to proceed. The historical smaller MoE preflight had 3,935 MiB free against a 4,096 MiB guard; refresh current measurements rather than assuming that state still holds.

### 3. Construct genuinely comparable test pairs

Pin model revision, architecture, weight quantization, runtime/dependencies, KV precision, context, active sequences, offload and topology. Align estimator inputs and the measured quantity. Distinguish payload, allocated, reserved and whole-device memory; without matching quantities and conditions, report no comparable error pair.

### 4. Address remaining dense, MoE and topology coverage

Reuse the accepted experimental design and run only cases allowed by actual capacity and authority. Preserve the dense/MoE matrix, context/cache/concurrency variations and per-rank needs. Missing MoE capacity or a second authorized device is a concrete coverage gap, not a reason to infer the result from dense runs.

### 5. Report results and failures without false calibration

Retain fresh-process repetitions, synchronized phase measurements, environment pins, failures and actual allocated/reserved peaks. Compute estimator errors only for valid pairs with explicit denominators and units. Do not call tensor-layout agreement a total-memory error bound or claim universal fit from a small tested model.

### 6. Complete the technical handoff and partial delivery

Use sanitized small evidence records or authorized external manifests, not model weights or large downloads in Git. Coordinate the existing acceptance matrix with #56 and handoffs with #59. #10 must explicitly agree to consume and locate any ResourceEstimate before such records are added. Seek #7/#10/#11 review and retain empirical gaps on the issue.

## Dependencies and handoffs

**Native children:** None specified in the inspected snapshot.

**Native blocked-by prerequisites:** None specified in the inspected snapshot.

**Native downstream issues blocked by this issue:** None specified in the inspected snapshot.

**Market information/coordination links, not newly created blockers:** [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56), [#58](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58)

**Project #1 receiving issues — information/review, not ownership transfer:** [#7](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7), [#10](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10), [#11](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11)

Read current receiving owners and request an explicit accept/reject/narrow disposition for each material handoff, identifying the exact artifact revision, conditions, fields or claim, and remaining question. Coordinate the canonical handoff ledger with #59. A request for review or general PR approval does not prove that a specific owner accepted a handoff. Preserve native relationships unless their predicate is genuinely resolved through the accepted workflow.

## Acceptance criteria to preserve

These are the issue criteria captured for this package. Re-read the live issue and preserve any later accepted changes; never silently remove a criterion to make the task finish.

- [ ] Design dense and MoE measurement matrix
- [ ] Vary context cache precision and concurrency
- [ ] Measure peak allocated and reserved memory
- [ ] Report error bounds and failures without universal fit claims
- [ ] Deliverable links every significant conclusion to evidence or an explicit hypothesis.
- [ ] Relevant technical owners review handoffs; unresolved decisions are named.
- [ ] Repository checks pass; reviewer accepts the evidence before Done.

**Issue-specific completion gate:** Do not close #61 by dropping MoE/topology or comparable-error requirements without an explicit owner-approved scope decision. Missing capacity, noncomparable estimators and pending handoffs remain visible.

## Commit, push, sync and merge this issue

Execute this delivery loop after the research passes above; do not stop at a plan or an unpushed local edit. Apply the detailed safeguards in `SHARED.md`.

1. Refresh the actual repository, issue, active PRs and base; preserve current assignees and other writers. Use a clean isolated worktree and a focused issue branch. Reuse the existing authorized work instead of launching a duplicate. If the deliverables only exist on an unmerged proposal branch, coordinate a declared editing dependency; do not silently import or merge unrelated work.
2. Run the current Python 3.12 research workflow, applicable market validator, `git diff --check` and claim/evidence review. Record the actual commands and results for this revision. Validators do not prove truth, rights, empirical success or owner acceptance.
3. Inspect and stage only the intended files, commit with a meaningful reference to issue #61, push, and verify the remote head SHA. Open or update the focused PR using **`Refs #61`** for a partial contribution.
4. Fetch the current base and head, synchronize the contribution safely, inspect the new diff and rerun affected checks. Obtain the required independent reviewer and explicit receiving-owner dispositions. Preserve reviews/holds and refresh approvals after any head change; no self-approval, blind force push or protection bypass.
5. Merge the qualifying final head using the permitted normal method and a head-SHA guard where available. A valid partial PR may merge while this issue remains open. A merge into a proposal branch is **not** delivery to main. Use **`Closes #61`** only when a canonical-main merge will satisfy every live criterion, native child/prerequisite gate and required handoff.
6. Verify the actual merge destination, commit, files and post-merge checks; safely synchronize a clean local verification checkout. Only then reconcile issue/Project #2 state using live fields, preserving unrelated values and reading changes back. Do not claim Done or synchronization without that evidence.

If an external decision, unavailable resource or permission blocks an action, complete the independent permitted work and return an exact blocker plus a ZIP/diff and replay steps. Do not fabricate execution, approval, participant evidence, commit/push/merge status or future background work.

## Required final report

Report #61’s completed and remaining criteria, changed files, source/evidence limitations, actual validation commands/results, branch and commit SHA, pushed remote head, PR URL and base, review/owner dispositions, merge commit and destination, canonical-main verification and any actual Project readback. Separate partial delivery from issue completion. Name the exact missing permission, artifact, experiment, decision or reviewer action when blocked.
