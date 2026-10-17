# Android 07: Discover and compare AI components — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#41](https://github.com/Pick-Your-AI/pickyour.ai/issues/41) under [Pick-Your-AI/pickyour.ai#34](https://github.com/Pick-Your-AI/pickyour.ai/issues/34). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-41).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Keep query, filters, selected build/role and snapshot identity stable across paging, recreation and return from details. Candidate evaluation must isolate inherited build failures from candidate-caused failures. Compare only comparable versions, units and evidence conditions; external links and previews never silently mutate the build.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#115](https://github.com/Pick-Your-AI/pickyour.ai/issues/115) — Android 07.01: Catalog navigation and search | Browse seven tiers and canonical kinds; search, sort, facets and paging persist context during selection. | [Pick-Your-AI/pickyour.ai#100](https://github.com/Pick-Your-AI/pickyour.ai/issues/100), [Pick-Your-AI/pickyour.ai#91](https://github.com/Pick-Your-AI/pickyour.ai/issues/91) | Android catalog/UX reviewer and data consumer |
| [Pick-Your-AI/pickyour.ai#129](https://github.com/Pick-Your-AI/pickyour.ai/issues/129) — Android 07.02: Constraint-aware picker | Candidate verdicts compatible/incompatible/unknown remain separate from per-rule pass/fail/unknown/skipped outcomes; filter conservatively and explain excluded/unknown options with reasons. Preserve existing slot-empty-baseline logic so inherited build failures are not attributed to the candidate. | [Pick-Your-AI/pickyour.ai#117](https://github.com/Pick-Your-AI/pickyour.ai/issues/117), [Pick-Your-AI/pickyour.ai#115](https://github.com/Pick-Your-AI/pickyour.ai/issues/115) | Android catalog/UX reviewer and data consumer |
| [Pick-Your-AI/pickyour.ai#130](https://github.com/Pick-Your-AI/pickyour.ai/issues/130) — Android 07.03: Component detail and evidence | Versioned specs, provider/offering identity, license conditions, source links, dates, price conditions and limitations visible. | [Pick-Your-AI/pickyour.ai#60](https://github.com/Pick-Your-AI/pickyour.ai/issues/60), [Pick-Your-AI/pickyour.ai#115](https://github.com/Pick-Your-AI/pickyour.ai/issues/115) | Android catalog/UX reviewer and data consumer |
| [Pick-Your-AI/pickyour.ai#144](https://github.com/Pick-Your-AI/pickyour.ai/issues/144) — Android 07.04: Component comparison | Normalize comparable fields and conditions; unknown remains explicit; accessible horizontal or stacked comparison on phones. | [Pick-Your-AI/pickyour.ai#113](https://github.com/Pick-Your-AI/pickyour.ai/issues/113), [Pick-Your-AI/pickyour.ai#130](https://github.com/Pick-Your-AI/pickyour.ai/issues/130) | Android catalog/UX reviewer and data consumer |
| [Pick-Your-AI/pickyour.ai#131](https://github.com/Pick-Your-AI/pickyour.ai/issues/131) — Android 07.05: Selection from search and deep links | Add/replace selection deterministically, preserve builder state, handle removed or incompatible-version entries and untrusted links. | [Pick-Your-AI/pickyour.ai#109](https://github.com/Pick-Your-AI/pickyour.ai/issues/109), [Pick-Your-AI/pickyour.ai#115](https://github.com/Pick-Your-AI/pickyour.ai/issues/115) | Android catalog/UX reviewer and data consumer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/07.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: Android catalog/UX reviewer and data consumer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
