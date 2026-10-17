# Mobile maintainer execution prompts

Proposed execution guidance for the existing [Android Project 4](https://github.com/orgs/Pick-Your-AI/projects/4) and [Apple/iOS Project 5](https://github.com/orgs/Pick-Your-AI/projects/5). Publishing or reviewing these files does not launch either campaign, assign work, change readiness, or satisfy delivery acceptance. This revision must be reviewed before being represented as accepted guidance.

[Publication PR and revision status](PUBLICATION.md). The PR remains unmerged; issue and Project sections pin the exact pushed revision.

This set adapts the inspection → ownership → prerequisites → implementation → validation → receiving review → PR → evidence-backed completion approach of the T0–T6 maintainer prompts. The technical prompt work in [Pick-Your-AI/pick-your-ai-research PR 74](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/74) is still proposed at this publication baseline; mobile prompts are independently usable and do not require that PR to merge. Existing [market prompts](../market/README.md) remain separate.

| Entry point | Coverage |
| --- | --- |
| [SHARED.md](SHARED.md) | Common ownership, governance, evidence, delivery and completion rules |
| [ANDROID.md](ANDROID.md) / [Android epics](android/README.md) | Pick-Your-AI/pickyour.ai#34 and its native hierarchy |
| [APPLE.md](APPLE.md) / [Apple epics](apple/README.md) | Pick-Your-AI/pickyour.ai#163 and its native hierarchy |
| [INDEX.md](INDEX.md) | Every covered issue, prompt, acceptance record/output and receiving handoff |
| [coverage.json](coverage.json) | Exact issue acceptance/steps, validation, native prerequisites, input references and source identity |
| [project-fields.json](project-fields.json) | Separate field IDs/options and membership baseline for both Projects |
| [REVIEW.md](REVIEW.md) | Consistency review, validation boundaries and outstanding intake |

The live refresh found 258 issues: two programs, 36 epics and 220 work packages. There are 38 execution prompts, not a prompt per checklist item. All 906 acceptance criteria and 880 implementation steps are retained in the coverage ledger. Counts describe this revision, not quotas. The issue bodies and accepted decisions remain authoritative on later changes. No mobile issue had an existing execution-prompt section in this baseline.

## Checkout the published revision

Use the full commit SHA in the issue or Project's delimited execution-prompt section. Fetch the publication branch in the research repository, then create a separate worktree at that SHA. Replace both placeholders; preserve active work and do not reset another branch.

```sh
git fetch origin docs/mobile-maintainer-prompts
git worktree add ../mobile-guidance-REVIEW <FULL_SHA_FROM_HANDOFF>
```

The prompt checkout contains guidance only. Actual application/service work belongs in the repository/module accepted by the platform placement decisions. Read those repositories' instructions before edits. A proposed prompt can be reviewed now; execution additionally requires the actual assigned scope and mandate. Review the publication PR's live state rather than assuming the pinned revision is merged.

## Launch a full program

Paste exactly one platform instruction only when a full-program execution mandate exists. Missing ownership is reconciled first; this text does not assign all work to the invoking agent or research owners.

```text
Read applicable AGENTS.md, contribution, governance and architecture instructions.
Read prompts/mobile/SHARED.md, prompts/mobile/ANDROID.md and prompts/mobile/INDEX.md.
Coordinate the existing Pick-Your-AI/pickyour.ai#34 program in Project 4 only within
my granted execution authority. Refresh live issues, native hierarchy, assignees,
Project fields, prerequisites, decisions, linked PRs and active runs. Reuse existing
owners and canonical shared work. Use the scoped epic prompts for assigned slices.
Reconcile ownership and architecture before dependent implementation. Follow the
shared workflow through validation, receiving review and scoped PR delivery.
Do not merge, deploy, buy resources, contact customers or publish an app unless
my actual mandate authorizes that action and all required gates are satisfied.
Complete independent authorized work and report precise remaining blockers and
evidence states; do not claim completion from prompt publication or partial PRs.
```

```text
Read applicable AGENTS.md, contribution, governance and architecture instructions.
Read prompts/mobile/SHARED.md, prompts/mobile/APPLE.md and prompts/mobile/INDEX.md.
Coordinate the existing Pick-Your-AI/pickyour.ai#163 program in Project 5 only within
my granted execution authority. Refresh live issues, native hierarchy, assignees,
Project fields, prerequisites, decisions, linked PRs and active runs. Reuse existing
owners and canonical website/Android services; Apple owns its client integration.
Use scoped epic prompts for assigned slices and resolve platform/module decisions
before dependent work. Follow validation, receiving review and scoped PR delivery.
Do not merge, deploy, buy resources, contact customers or publish an app unless
my actual mandate authorizes that action and all required gates are satisfied.
Complete independent authorized work and report precise blockers, unverified
runtime/device coverage and each distinct TestFlight/store/release evidence state.
```

## Launch one epic

Choose the epic in INDEX.md and replace the platform/prompt/issue placeholders. The matching platform program is required context, not a request to execute its siblings.

```text
Read applicable repository instructions, prompts/mobile/SHARED.md,
prompts/mobile/<ANDROID-or-APPLE>.md and
prompts/mobile/<android-or-apple>/epic-<NN>.md.
Execute only Pick-Your-AI/pickyour.ai#<EPIC_NUMBER> and its actually assigned native
work packages within my existing authority. Refresh live scope, assignees,
prerequisites, decisions, Project fields and active work; coordinate with its owner.
Apply every indexed acceptance criterion and required receiving handoff. Preserve
canonical shared services and unrelated work. Deliver meaningful validation and
a scoped PR with required review. Respect my merge/release boundary. Do not start
another epic or duplicate controller. Report unmet ownership, input, decision and
access gates accurately after completing independent authorized work.
```

Concrete epic choices: Android `android/epic-12.md`, `ANDROID.md`, Pick-Your-AI/pickyour.ai#46; Apple `apple/epic-12.md`, `APPLE.md`, Pick-Your-AI/pickyour.ai#175. Choose only one.

## Launch one assigned work package

Select its row in INDEX.md and replace the placeholders. A missing assignee remains an intake gap; do not infer delegation from this example.

```text
Read applicable repository instructions, prompts/mobile/SHARED.md,
prompts/mobile/<ANDROID-or-APPLE>.md and the applicable epic prompt from INDEX.md.
Execute only assigned Pick-Your-AI/pickyour.ai#<WORK_PACKAGE_NUMBER> and its agreed
handoffs within my granted authority. The epic's other rows are context only.
Refresh the issue's full body/comments, actual assignees, native prerequisites,
accepted placement/scope decisions, linked PRs and active work before editing.
Preserve every acceptance criterion, implementation step and negative/recovery case.
Use its existing record/output boundary and canonical producer artifacts. Implement,
validate, obtain receiving review and publish a scoped PR; follow my actual merge
and release limits. Complete independent authorized work, then report exact gaps.
```

Examples of index lookup, not assignments: Android Pick-Your-AI/pickyour.ai#100 uses `ANDROID.md` and `android/epic-12.md`; Apple Pick-Your-AI/pickyour.ai#248 uses `APPLE.md` and `apple/epic-12.md`.

## Maintain and republish

Keep common rules in SHARED.md and platform acceptance in ANDROID.md/APPLE.md. Update affected epic guidance and coverage records in the same PR after rereading live issue changes. Do not regenerate from issue-number ranges; enumerate Project membership and native relationships. Preserve exact acceptance texts in the ledger and review any scope drift explicitly. The validator checks local links, graph/mapping, field vocabulary and evidence coverage; use its optional live snapshot comparison when preparing a revision.

Run `python prompts/mobile/validate_prompts.py` and all [research workflow checks](../../docs/RESEARCH_WORKFLOW.md). Separately review all prompts together for ownership, scope, architecture, contract authority, evidence, triage, prerequisites and completion. Publish signed scoped changes through a PR. Only after pushing, update the existing delimited issue/Project prompt sections with full commit-pinned prompt, shared-rule, index/launch and publication-PR links. Re-read before each write, preserve concurrent/unrelated content and verify every mutation. Mark the revision proposed until its PR actually merges. Never alter delivery statuses or acceptance checkboxes merely to publish guidance.
