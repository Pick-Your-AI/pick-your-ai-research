# Android 06: Mobile experience and design system — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#40](https://github.com/Pick-Your-AI/pickyour.ai/issues/40) under [Pick-Your-AI/pickyour.ai#34](https://github.com/Pick-Your-AI/pickyour.ai/issues/34). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-40).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Review original parts-list navigation with persistent build context. Implement accessible semantic controls, adaptive comparison, localized units and recovery for empty/offline/denied/stale/conflict states. Incomplete, incompatible and unknown must remain distinct through every screen and assistive path.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#62](https://github.com/Pick-Your-AI/pickyour.ai/issues/62) — Android 06.01: Information architecture and prototypes | Original PCPartPicker-inspired component rows, selection flow, persistent summary, comparison and evidence drilldown; validate actual Android usability. | [Pick-Your-AI/pickyour.ai#53](https://github.com/Pick-Your-AI/pickyour.ai/issues/53) | Android UX/accessibility reviewer |
| [Pick-Your-AI/pickyour.ai#97](https://github.com/Pick-Your-AI/pickyour.ai/issues/97) — Android 06.02: Accessible component library | TalkBack order/labels, semantics, focus, touch targets, contrast, font scaling, reduced motion and non-color-only statuses. | [Pick-Your-AI/pickyour.ai#62](https://github.com/Pick-Your-AI/pickyour.ai/issues/62), [Pick-Your-AI/pickyour.ai#81](https://github.com/Pick-Your-AI/pickyour.ai/issues/81) | Android UX/accessibility reviewer |
| [Pick-Your-AI/pickyour.ai#113](https://github.com/Pick-Your-AI/pickyour.ai/issues/113) — Android 06.03: Adaptive layouts | Phone/tablet/foldable, portrait/landscape, split-screen/resize, keyboard and edge-to-edge system bars remain usable. | [Pick-Your-AI/pickyour.ai#80](https://github.com/Pick-Your-AI/pickyour.ai/issues/80), [Pick-Your-AI/pickyour.ai#97](https://github.com/Pick-Your-AI/pickyour.ai/issues/97) | Android UX/accessibility reviewer |
| [Pick-Your-AI/pickyour.ai#73](https://github.com/Pick-Your-AI/pickyour.ai/issues/73) — Android 06.04: Builder guidance and status language | Separate incomplete configuration, rule failure, unknown evaluation and stale data; severity remains independent. | [Pick-Your-AI/pickyour.ai#62](https://github.com/Pick-Your-AI/pickyour.ai/issues/62), [Pick-Your-AI/pickyour.ai#60](https://github.com/Pick-Your-AI/pickyour.ai/issues/60) | Android UX/accessibility reviewer |
| [Pick-Your-AI/pickyour.ai#114](https://github.com/Pick-Your-AI/pickyour.ai/issues/114) — Android 06.05: System and error states | Loading, empty, offline, permission-denied, server failure, sync conflict and unavailable version all provide recovery actions. | [Pick-Your-AI/pickyour.ai#91](https://github.com/Pick-Your-AI/pickyour.ai/issues/91), [Pick-Your-AI/pickyour.ai#62](https://github.com/Pick-Your-AI/pickyour.ai/issues/62) | Android UX/accessibility reviewer |
| [Pick-Your-AI/pickyour.ai#98](https://github.com/Pick-Your-AI/pickyour.ai/issues/98) — Android 06.06: Localization and presentation | Externalized strings, pluralization, RTL readiness, local formats and units; currency conversion never inferred; original branding assets. | [Pick-Your-AI/pickyour.ai#62](https://github.com/Pick-Your-AI/pickyour.ai/issues/62), [Pick-Your-AI/pickyour.ai#81](https://github.com/Pick-Your-AI/pickyour.ai/issues/81) | Android UX/accessibility reviewer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/06.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: Android UX/accessibility reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
