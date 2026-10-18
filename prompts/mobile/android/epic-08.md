# Android 08: AI stack configuration — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-android#9](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/9) under [Pick-Your-AI/pick-your-ai-android#1](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-android-9).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Preserve incomplete drafts without fictional defaults, canonical role/cardinality and settings across deployment changes. Toggle T3–T5 independently without losing intent; preserve core T6. Invalidate only with correct before/after graph semantics and prove that saved indicators correspond to durable acknowledged state, including undo/recovery.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-android#83](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/83) — Android 08.01: Workload and deployment inputs | Capture goals, budgets and workload assumptions; required T0/T1 readiness is separate from compatibility. | [Pick-Your-AI/pick-your-ai-android#67](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/67), [Pick-Your-AI/pick-your-ai-android#37](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/37) | Android domain/UX reviewer |
| [Pick-Your-AI/pick-your-ai-android#112](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/112) — Android 08.02: Core model and infrastructure selection | Canonical role-aware add/replace/remove/configure flows for T1/T2; dependent requirements adapt without deleting user work. | [Pick-Your-AI/pick-your-ai-android#98](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/98), [Pick-Your-AI/pick-your-ai-android#83](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/83) | Android domain/UX reviewer |
| [Pick-Your-AI/pick-your-ai-android#121](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/121) — Android 08.03: Optional tier activation | T3-T5 enable/disable independently with preserved settings and clear effect on validation/cost; no hidden forced dependencies. | [Pick-Your-AI/pick-your-ai-android#100](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/100), [Pick-Your-AI/pick-your-ai-android#112](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/112) | Android domain/UX reviewer |
| [Pick-Your-AI/pick-your-ai-android#99](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/99) — Android 08.04: Settings and objective editor | Typed contract-driven settings validate user input, units and ranges; preserve explicit unknowns and sensitive-input boundaries. | [Pick-Your-AI/pick-your-ai-android#27](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/27), [Pick-Your-AI/pick-your-ai-android#83](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/83) | Android domain/UX reviewer |
| [Pick-Your-AI/pick-your-ai-android#113](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/113) — Android 08.05: Summary and next actions | Persistent mobile summary includes selected components, missing pieces, findings, total coverage and direct remediation navigation. | [Pick-Your-AI/pick-your-ai-android#52](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/52), [Pick-Your-AI/pick-your-ai-android#41](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/41), [Pick-Your-AI/pick-your-ai-android#103](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/103), [Pick-Your-AI/pick-your-ai-android#101](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/101), [Pick-Your-AI/pick-your-ai-android#83](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/83) | Android domain/UX reviewer |
| [Pick-Your-AI/pick-your-ai-android#122](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/122) — Android 08.06: Undo and revisions | Predictable undo/redo or revision restore, autosave feedback, duplicate handling and process-death recovery; no lost edits. | [Pick-Your-AI/pick-your-ai-android#86](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/86), [Pick-Your-AI/pick-your-ai-android#112](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/112) | Android domain/UX reviewer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/08.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: Android domain/UX reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
