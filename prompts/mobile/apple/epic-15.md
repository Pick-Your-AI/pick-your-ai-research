# Apple/iOS 15: Quality and performance — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) under [Pick-Your-AI/pickyour.ai#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-178).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Build a criterion-to-test matrix across domain, UI/accessibility, faults, device/lifecycle, cross-client, performance and release security. Intentionally break boundaries to prove gates detect failures. Separate physical-device and real-service evidence from mocks/simulators; authorized user validation requires its own protocol and authority.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#266](https://github.com/Pick-Your-AI/pickyour.ai/issues/266) — Apple/iOS 15.01: Contract and domain regression tests | Domain suite detects policy drift and malformed boundary data. | [Pick-Your-AI/pickyour.ai#239](https://github.com/Pick-Your-AI/pickyour.ai/issues/239), [Pick-Your-AI/pickyour.ai#232](https://github.com/Pick-Your-AI/pickyour.ai/issues/232), [Pick-Your-AI/pickyour.ai#199](https://github.com/Pick-Your-AI/pickyour.ai/issues/199) | quality reviewer and affected feature consumer |
| [Pick-Your-AI/pickyour.ai#267](https://github.com/Pick-Your-AI/pickyour.ai/issues/267) — Apple/iOS 15.02: Apple UI and accessibility tests | Accessibility evidence covers actual devices and complete user journeys. | [Pick-Your-AI/pickyour.ai#242](https://github.com/Pick-Your-AI/pickyour.ai/issues/242), [Pick-Your-AI/pickyour.ai#217](https://github.com/Pick-Your-AI/pickyour.ai/issues/217), [Pick-Your-AI/pickyour.ai#230](https://github.com/Pick-Your-AI/pickyour.ai/issues/230) | quality reviewer and affected feature consumer |
| [Pick-Your-AI/pickyour.ai#268](https://github.com/Pick-Your-AI/pickyour.ai/issues/268) — Apple/iOS 15.03: Network failure and recovery tests | Recoverable faults do not lose edits or display misleading success. | [Pick-Your-AI/pickyour.ai#252](https://github.com/Pick-Your-AI/pickyour.ai/issues/252), [Pick-Your-AI/pickyour.ai#237](https://github.com/Pick-Your-AI/pickyour.ai/issues/237) | quality reviewer and affected feature consumer |
| [Pick-Your-AI/pickyour.ai#269](https://github.com/Pick-Your-AI/pickyour.ai/issues/269) — Apple/iOS 15.04: Device, OS and lifecycle test matrix | Release qualification covers all declared supported device classes. | [Pick-Your-AI/pickyour.ai#248](https://github.com/Pick-Your-AI/pickyour.ai/issues/248), [Pick-Your-AI/pickyour.ai#190](https://github.com/Pick-Your-AI/pickyour.ai/issues/190) | quality reviewer and affected feature consumer |
| [Pick-Your-AI/pickyour.ai#270](https://github.com/Pick-Your-AI/pickyour.ai/issues/270) — Apple/iOS 15.05: Apple, Android, web and backend conformance tests | Cross-client supported workflows agree on identity, policy and version locks. | [Pick-Your-AI/pickyour.ai#247](https://github.com/Pick-Your-AI/pickyour.ai/issues/247), [Pick-Your-AI/pickyour.ai#214](https://github.com/Pick-Your-AI/pickyour.ai/issues/214) | quality reviewer and affected feature consumer |
| [Pick-Your-AI/pickyour.ai#271](https://github.com/Pick-Your-AI/pickyour.ai/issues/271) — Apple/iOS 15.06: Measured startup, rendering and resource budgets | Performance claims have reproducible measurements and enforced agreed budgets. | [Pick-Your-AI/pickyour.ai#187](https://github.com/Pick-Your-AI/pickyour.ai/issues/187), [Pick-Your-AI/pickyour.ai#230](https://github.com/Pick-Your-AI/pickyour.ai/issues/230), [Pick-Your-AI/pickyour.ai#221](https://github.com/Pick-Your-AI/pickyour.ai/issues/221) | quality reviewer and affected feature consumer |
| [Pick-Your-AI/pickyour.ai#272](https://github.com/Pick-Your-AI/pickyour.ai/issues/272) — Apple/iOS 15.07: Security and release-build regression tests | Release binary passes the selected security and configuration checks. | [Pick-Your-AI/pickyour.ai#276](https://github.com/Pick-Your-AI/pickyour.ai/issues/276), [Pick-Your-AI/pickyour.ai#265](https://github.com/Pick-Your-AI/pickyour.ai/issues/265), [Pick-Your-AI/pickyour.ai#264](https://github.com/Pick-Your-AI/pickyour.ai/issues/264) | quality reviewer and affected feature consumer |
| [Pick-Your-AI/pickyour.ai#273](https://github.com/Pick-Your-AI/pickyour.ai/issues/273) — Apple/iOS 15.08: Authorized user validation and acceptance | User validation evidence supports release decisions without invented results. | [Pick-Your-AI/pickyour.ai#215](https://github.com/Pick-Your-AI/pickyour.ai/issues/215), [Pick-Your-AI/pickyour.ai#187](https://github.com/Pick-Your-AI/pickyour.ai/issues/187) | quality reviewer and affected feature consumer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 15`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: quality reviewer and affected feature consumer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Domain suite detects policy drift and malformed boundary data.

- Accessibility evidence covers actual devices and complete user journeys.

- Recoverable faults do not lose edits or display misleading success.

- Release qualification covers all declared supported device classes.

- Cross-client supported workflows agree on identity, policy and version locks.

- Performance claims have reproducible measurements and enforced agreed budgets.

- Release binary passes the selected security and configuration checks.

- User validation evidence supports release decisions without invented results.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
