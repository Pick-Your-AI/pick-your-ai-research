# Apple/iOS 07: Component discovery and comparison — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#170](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) under [Pick-Your-AI/pickyour.ai#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-170).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Keep query, filters, selected build/role and snapshot identity stable across paging, recreation and return from details. Candidate evaluation must isolate inherited build failures from candidate-caused failures. Compare only comparable versions, units and evidence conditions; external links and previews never silently mutate the build.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#221](https://github.com/Pick-Your-AI/pickyour.ai/issues/221) — Apple/iOS 07.01: Browse, search, filter and sort the catalog | Users can locate candidates without losing current build context. | [Pick-Your-AI/pickyour.ai#193](https://github.com/Pick-Your-AI/pickyour.ai/issues/193), [Pick-Your-AI/pickyour.ai#216](https://github.com/Pick-Your-AI/pickyour.ai/issues/216), [Pick-Your-AI/pickyour.ai#191](https://github.com/Pick-Your-AI/pickyour.ai/issues/191) | Apple UX and catalog consumer |
| [Pick-Your-AI/pickyour.ai#222](https://github.com/Pick-Your-AI/pickyour.ai/issues/222) — Apple/iOS 07.02: Compatibility-aware component picker | Candidate selection shows governed findings for the current build revision. | [Pick-Your-AI/pickyour.ai#232](https://github.com/Pick-Your-AI/pickyour.ai/issues/232), [Pick-Your-AI/pickyour.ai#221](https://github.com/Pick-Your-AI/pickyour.ai/issues/221) | Apple UX and catalog consumer |
| [Pick-Your-AI/pickyour.ai#223](https://github.com/Pick-Your-AI/pickyour.ai/issues/223) — Apple/iOS 07.03: Component details, conditions and evidence | Every material claim has inspectable evidence or an explicit gap. | [Pick-Your-AI/pickyour.ai#221](https://github.com/Pick-Your-AI/pickyour.ai/issues/221) | Apple UX and catalog consumer |
| [Pick-Your-AI/pickyour.ai#224](https://github.com/Pick-Your-AI/pickyour.ai/issues/224) — Apple/iOS 07.04: Side-by-side component comparison | Comparison retains comparable units and all relevant conditions. | [Pick-Your-AI/pickyour.ai#223](https://github.com/Pick-Your-AI/pickyour.ai/issues/223) | Apple UX and catalog consumer |
| [Pick-Your-AI/pickyour.ai#225](https://github.com/Pick-Your-AI/pickyour.ai/issues/225) — Apple/iOS 07.05: Select components from search and deep links | External navigation cannot silently replace a user's selected component. | [Pick-Your-AI/pickyour.ai#190](https://github.com/Pick-Your-AI/pickyour.ai/issues/190), [Pick-Your-AI/pickyour.ai#221](https://github.com/Pick-Your-AI/pickyour.ai/issues/221) | Apple UX and catalog consumer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 07`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: Apple UX and catalog consumer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Users can locate candidates without losing current build context.

- Candidate selection shows governed findings for the current build revision.

- Every material claim has inspectable evidence or an explicit gap.

- Comparison retains comparable units and all relevant conditions.

- External navigation cannot silently replace a user's selected component.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
