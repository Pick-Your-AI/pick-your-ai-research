# Apple/iOS 14: Privacy, security and trust — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#15](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-15).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Trace sensitive fields through imports, caches, shares, services, diagnostics and deletion. Implement the approved threat mitigations early, test negative authority and device-protection states, reconcile SDK traffic with disclosures, and retest fixes. Conditional accounts do not waive authorization of guest remote writes.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98) — Apple/iOS 14.01: Data inventory and threat model | Reviewed threat model maps risks to concrete verification tasks. | None; ownership and stated decisions still apply | security/privacy reviewer and affected service reviewer |
| [Pick-Your-AI/pick-your-ai-apple#99](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/99) — Apple/iOS 14.02: Keychain, data protection and secure networking | Secrets and private build content are protected across device lifecycle states. | [Pick-Your-AI/pick-your-ai-apple#26](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/26), [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98) | security/privacy reviewer and affected service reviewer |
| [Pick-Your-AI/pick-your-ai-apple#100](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/100) — Apple/iOS 14.03: Account and associated-data lifecycle, if included | Deletion is an actual service outcome rather than hiding an account locally. | [Pick-Your-AI/pick-your-ai-apple#91](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/91), [Pick-Your-AI/pick-your-ai-apple#50](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/50), [Pick-Your-AI/pick-your-ai-apple#24](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24) | security/privacy reviewer and affected service reviewer |
| [Pick-Your-AI/pick-your-ai-apple#101](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/101) — Apple/iOS 14.04: Privacy disclosures and third-party SDK controls | Disclosures match measured application and SDK behavior. | [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98), [Pick-Your-AI/pick-your-ai-apple#24](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24) | security/privacy reviewer and affected service reviewer |
| [Pick-Your-AI/pick-your-ai-apple#102](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/102) — Apple/iOS 14.05: Adversarial testing of sharing, imports and APIs | Adversarial cases fail safely without data disclosure or draft corruption. | [Pick-Your-AI/pick-your-ai-apple#50](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/50), [Pick-Your-AI/pick-your-ai-apple#85](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/85), [Pick-Your-AI/pick-your-ai-apple#82](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/82) | security/privacy reviewer and affected service reviewer |
| [Pick-Your-AI/pick-your-ai-apple#103](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/103) — Apple/iOS 14.06: Dependency security and vulnerability response | Release dependencies and response path have reviewed evidence. | [Pick-Your-AI/pick-your-ai-apple#26](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/26) | security/privacy reviewer and affected service reviewer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 14`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: security/privacy reviewer and affected service reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Reviewed threat model maps risks to concrete verification tasks.

- Secrets and private build content are protected across device lifecycle states.

- Deletion is an actual service outcome rather than hiding an account locally.

- Disclosures match measured application and SDK behavior.

- Adversarial cases fail safely without data disclosure or draft corruption.

- Release dependencies and response path have reviewed evidence.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
