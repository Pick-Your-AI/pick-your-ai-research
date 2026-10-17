# Apple/iOS 16: TestFlight, App Store delivery and launch — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-17).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Use the actual publisher/team, selected regions and exact signed candidate. Verify current primary platform/store requirements, privacy declarations and signing-linked integrations. Keep local build, beta distribution, submission, approval, authorized rollout and installed production readback as separate receipts; rehearse rejection and forward-fix.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#112](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/112) — Apple/iOS 16.01: Apple Developer team and App Store Connect identity | Authorized maintainers can manage the intended app record and identity. | [Pick-Your-AI/pick-your-ai-apple#22](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22) | authorized release/App Store maintainer |
| [Pick-Your-AI/pick-your-ai-apple#113](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/113) — Apple/iOS 16.02: Platform and store-policy requirements | Current policy review identifies all selected release obligations. | [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98), [Pick-Your-AI/pick-your-ai-apple#24](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24), [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | authorized release/App Store maintainer |
| [Pick-Your-AI/pick-your-ai-apple#114](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/114) — Apple/iOS 16.03: Signing, provisioning, entitlements and key management | Signed artifact is reproducible, attributable and installable through the selected channel. | [Pick-Your-AI/pick-your-ai-apple#30](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/30), [Pick-Your-AI/pick-your-ai-apple#112](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/112) | authorized release/App Store maintainer |
| [Pick-Your-AI/pick-your-ai-apple#115](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/115) — Apple/iOS 16.04: Internal and external TestFlight testing | Beta gate has actual tester/device evidence and resolved release blockers. | [Pick-Your-AI/pick-your-ai-apple#107](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/107), [Pick-Your-AI/pick-your-ai-apple#106](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/106), [Pick-Your-AI/pick-your-ai-apple#113](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/113), [Pick-Your-AI/pick-your-ai-apple#43](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/43), [Pick-Your-AI/pick-your-ai-apple#105](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/105), [Pick-Your-AI/pick-your-ai-apple#104](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/104), [Pick-Your-AI/pick-your-ai-apple#114](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/114) | authorized release/App Store maintainer |
| [Pick-Your-AI/pick-your-ai-apple#116](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/116) — Apple/iOS 16.05: App Store listing, screenshots and privacy declarations | Store metadata accurately describes the shipping binary and available features. | [Pick-Your-AI/pick-your-ai-apple#122](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/122), [Pick-Your-AI/pick-your-ai-apple#113](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/113), [Pick-Your-AI/pick-your-ai-apple#101](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/101) | authorized release/App Store maintainer |
| [Pick-Your-AI/pick-your-ai-apple#117](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/117) — Apple/iOS 16.06: Launch readiness and controlled rollout | Store approval and release authorization are recorded separately from upload. | [Pick-Your-AI/pick-your-ai-apple#123](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/123), [Pick-Your-AI/pick-your-ai-apple#122](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/122), [Pick-Your-AI/pick-your-ai-apple#121](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/121), [Pick-Your-AI/pick-your-ai-apple#120](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/120), [Pick-Your-AI/pick-your-ai-apple#43](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/43), [Pick-Your-AI/pick-your-ai-apple#111](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/111), [Pick-Your-AI/pick-your-ai-apple#110](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/110), [Pick-Your-AI/pick-your-ai-apple#109](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/109), [Pick-Your-AI/pick-your-ai-apple#108](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/108), [Pick-Your-AI/pick-your-ai-apple#107](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/107), [Pick-Your-AI/pick-your-ai-apple#106](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/106), [Pick-Your-AI/pick-your-ai-apple#116](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/116), [Pick-Your-AI/pick-your-ai-apple#115](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/115) | authorized release/App Store maintainer |
| [Pick-Your-AI/pick-your-ai-apple#118](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/118) — Apple/iOS 16.07: Verify the installed production release | Actual installed production behavior matches the accepted release record. | [Pick-Your-AI/pick-your-ai-apple#117](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/117) | authorized release/App Store maintainer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 16`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: authorized release/App Store maintainer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Authorized maintainers can manage the intended app record and identity.

- Current policy review identifies all selected release obligations.

- Signed artifact is reproducible, attributable and installable through the selected channel.

- Beta gate has actual tester/device evidence and resolved release blockers.

- Store metadata accurately describes the shipping binary and available features.

- Store approval and release authorization are recorded separately from upload.

- Actual installed production behavior matches the accepted release record.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
