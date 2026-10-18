# Apple/iOS 18: Decision-dependent expansion — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#19](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-19).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Resolve each capability-specific scope gate independently: notifications, commerce, public community, recommendations, runtime actions and expansion. Approval is an entry gate, not completion. Preserve ranking neutrality, operational moderation and scoped runtime/spend authority; execute the issue-specific behavioral and recovery checks only for approved scope.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#124](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/124) — Apple/iOS 18.01: Favorites and price/compatibility alerts | Alerts ship only with accepted scope and user-controlled delivery. | [Pick-Your-AI/pick-your-ai-apple#24](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24) | product scope reviewer plus capability security/privacy reviewer |
| [Pick-Your-AI/pick-your-ai-apple#125](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/125) — Apple/iOS 18.02: Paid plans and entitlements | Paid access reflects verified transactions and the applicable platform policy. | [Pick-Your-AI/pick-your-ai-apple#24](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24) | product scope reviewer plus capability security/privacy reviewer |
| [Pick-Your-AI/pick-your-ai-apple#126](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/126) — Apple/iOS 18.03: Community build publishing and moderation | Public content cannot launch without an operational moderation path. | [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98), [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product scope reviewer plus capability security/privacy reviewer |
| [Pick-Your-AI/pick-your-ai-apple#127](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/127) — Apple/iOS 18.04: Advanced recommendations and personalization | Recommendations are auditable and do not imply unsupported performance. | [Pick-Your-AI/pick-your-ai-apple#36](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/36), [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product scope reviewer plus capability security/privacy reviewer |
| [Pick-Your-AI/pick-your-ai-apple#128](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/128) — Apple/iOS 18.05: Actual runtime execution or provisioning | No real execution occurs before explicit authority and deployment gates. | [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98), [Pick-Your-AI/pick-your-ai-apple#96](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/96), [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product scope reviewer plus capability security/privacy reviewer |
| [Pick-Your-AI/pick-your-ai-apple#129](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/129) — Apple/iOS 18.06: Additional markets and platforms | Expansion has its own accepted coverage and release evidence. | [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product scope reviewer plus capability security/privacy reviewer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 18`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: product scope reviewer plus capability security/privacy reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Alerts ship only with accepted scope and user-controlled delivery.

- Paid access reflects verified transactions and the applicable platform policy.

- Public content cannot launch without an operational moderation path.

- Recommendations are auditable and do not imply unsupported performance.

- No real execution occurs before explicit authority and deployment gates.

- Expansion has its own accepted coverage and release evidence.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
