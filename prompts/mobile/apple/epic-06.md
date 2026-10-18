# Apple/iOS 06: Mobile experience and design system — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#7](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-7).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Review original parts-list navigation with persistent build context. Implement accessible semantic controls, adaptive comparison, localized units and recovery for empty/offline/denied/stale/conflict states. Incomplete, incompatible and unknown must remain distinct through every screen and assistive path.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#53](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/53) — Apple/iOS 06.01: Information architecture and interaction prototypes | Reviewed prototype covers the complete mobile decision journey. | [Pick-Your-AI/pick-your-ai-apple#20](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/20) | Apple UX and accessibility reviewers |
| [Pick-Your-AI/pick-your-ai-apple#54](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/54) — Apple/iOS 06.02: Accessible components and design tokens | Core controls remain usable at accessibility sizes and with assistive technology. | [Pick-Your-AI/pick-your-ai-apple#53](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/53) | Apple UX and accessibility reviewers |
| [Pick-Your-AI/pick-your-ai-apple#55](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/55) — Apple/iOS 06.03: Adaptive iPhone and iPad layouts | Supported device layouts expose all primary actions without clipping. | [Pick-Your-AI/pick-your-ai-apple#28](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/28), [Pick-Your-AI/pick-your-ai-apple#54](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/54) | Apple UX and accessibility reviewers |
| [Pick-Your-AI/pick-your-ai-apple#56](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/56) — Apple/iOS 06.04: Builder guidance and understandable status labels | Users can identify missing input and conflicts without misleading success/failure labels. | [Pick-Your-AI/pick-your-ai-apple#53](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/53), [Pick-Your-AI/pick-your-ai-apple#36](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/36) | Apple UX and accessibility reviewers |
| [Pick-Your-AI/pick-your-ai-apple#57](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/57) — Apple/iOS 06.05: Loading, empty, offline and failure states | Every data-driven screen has tested non-success states. | [Pick-Your-AI/pick-your-ai-apple#54](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/54) | Apple UX and accessibility reviewers |
| [Pick-Your-AI/pick-your-ai-apple#58](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/58) — Apple/iOS 06.06: Themes, localization, units and presentation | Locale and theme changes preserve semantics and accessible layout. | [Pick-Your-AI/pick-your-ai-apple#54](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/54) | Apple UX and accessibility reviewers |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 06`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: Apple UX and accessibility reviewers. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Reviewed prototype covers the complete mobile decision journey.

- Core controls remain usable at accessibility sizes and with assistive technology.

- Supported device layouts expose all primary actions without clipping.

- Users can identify missing input and conflicts without misleading success/failure labels.

- Every data-driven screen has tested non-success states.

- Locale and theme changes preserve semantics and accessible layout.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
