# Apple/iOS 16: TestFlight, App Store delivery and launch — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) under [Pick-Your-AI/pickyour.ai#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-179).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Use the actual publisher/team, selected regions and exact signed candidate. Verify current primary platform/store requirements, privacy declarations and signing-linked integrations. Keep local build, beta distribution, submission, approval, authorized rollout and installed production readback as separate receipts; rehearse rejection and forward-fix.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#274](https://github.com/Pick-Your-AI/pickyour.ai/issues/274) — Apple/iOS 16.01: Apple Developer team and App Store Connect identity | Authorized maintainers can manage the intended app record and identity. | [Pick-Your-AI/pickyour.ai#184](https://github.com/Pick-Your-AI/pickyour.ai/issues/184) | authorized release/App Store maintainer |
| [Pick-Your-AI/pickyour.ai#275](https://github.com/Pick-Your-AI/pickyour.ai/issues/275) — Apple/iOS 16.02: Platform and store-policy requirements | Current policy review identifies all selected release obligations. | [Pick-Your-AI/pickyour.ai#260](https://github.com/Pick-Your-AI/pickyour.ai/issues/260), [Pick-Your-AI/pickyour.ai#186](https://github.com/Pick-Your-AI/pickyour.ai/issues/186), [Pick-Your-AI/pickyour.ai#183](https://github.com/Pick-Your-AI/pickyour.ai/issues/183) | authorized release/App Store maintainer |
| [Pick-Your-AI/pickyour.ai#276](https://github.com/Pick-Your-AI/pickyour.ai/issues/276) — Apple/iOS 16.03: Signing, provisioning, entitlements and key management | Signed artifact is reproducible, attributable and installable through the selected channel. | [Pick-Your-AI/pickyour.ai#192](https://github.com/Pick-Your-AI/pickyour.ai/issues/192), [Pick-Your-AI/pickyour.ai#274](https://github.com/Pick-Your-AI/pickyour.ai/issues/274) | authorized release/App Store maintainer |
| [Pick-Your-AI/pickyour.ai#277](https://github.com/Pick-Your-AI/pickyour.ai/issues/277) — Apple/iOS 16.04: Internal and external TestFlight testing | Beta gate has actual tester/device evidence and resolved release blockers. | [Pick-Your-AI/pickyour.ai#269](https://github.com/Pick-Your-AI/pickyour.ai/issues/269), [Pick-Your-AI/pickyour.ai#268](https://github.com/Pick-Your-AI/pickyour.ai/issues/268), [Pick-Your-AI/pickyour.ai#275](https://github.com/Pick-Your-AI/pickyour.ai/issues/275), [Pick-Your-AI/pickyour.ai#205](https://github.com/Pick-Your-AI/pickyour.ai/issues/205), [Pick-Your-AI/pickyour.ai#267](https://github.com/Pick-Your-AI/pickyour.ai/issues/267), [Pick-Your-AI/pickyour.ai#266](https://github.com/Pick-Your-AI/pickyour.ai/issues/266), [Pick-Your-AI/pickyour.ai#276](https://github.com/Pick-Your-AI/pickyour.ai/issues/276) | authorized release/App Store maintainer |
| [Pick-Your-AI/pickyour.ai#278](https://github.com/Pick-Your-AI/pickyour.ai/issues/278) — Apple/iOS 16.05: App Store listing, screenshots and privacy declarations | Store metadata accurately describes the shipping binary and available features. | [Pick-Your-AI/pickyour.ai#284](https://github.com/Pick-Your-AI/pickyour.ai/issues/284), [Pick-Your-AI/pickyour.ai#275](https://github.com/Pick-Your-AI/pickyour.ai/issues/275), [Pick-Your-AI/pickyour.ai#263](https://github.com/Pick-Your-AI/pickyour.ai/issues/263) | authorized release/App Store maintainer |
| [Pick-Your-AI/pickyour.ai#279](https://github.com/Pick-Your-AI/pickyour.ai/issues/279) — Apple/iOS 16.06: Launch readiness and controlled rollout | Store approval and release authorization are recorded separately from upload. | [Pick-Your-AI/pickyour.ai#285](https://github.com/Pick-Your-AI/pickyour.ai/issues/285), [Pick-Your-AI/pickyour.ai#284](https://github.com/Pick-Your-AI/pickyour.ai/issues/284), [Pick-Your-AI/pickyour.ai#283](https://github.com/Pick-Your-AI/pickyour.ai/issues/283), [Pick-Your-AI/pickyour.ai#282](https://github.com/Pick-Your-AI/pickyour.ai/issues/282), [Pick-Your-AI/pickyour.ai#205](https://github.com/Pick-Your-AI/pickyour.ai/issues/205), [Pick-Your-AI/pickyour.ai#273](https://github.com/Pick-Your-AI/pickyour.ai/issues/273), [Pick-Your-AI/pickyour.ai#272](https://github.com/Pick-Your-AI/pickyour.ai/issues/272), [Pick-Your-AI/pickyour.ai#271](https://github.com/Pick-Your-AI/pickyour.ai/issues/271), [Pick-Your-AI/pickyour.ai#270](https://github.com/Pick-Your-AI/pickyour.ai/issues/270), [Pick-Your-AI/pickyour.ai#269](https://github.com/Pick-Your-AI/pickyour.ai/issues/269), [Pick-Your-AI/pickyour.ai#268](https://github.com/Pick-Your-AI/pickyour.ai/issues/268), [Pick-Your-AI/pickyour.ai#278](https://github.com/Pick-Your-AI/pickyour.ai/issues/278), [Pick-Your-AI/pickyour.ai#277](https://github.com/Pick-Your-AI/pickyour.ai/issues/277) | authorized release/App Store maintainer |
| [Pick-Your-AI/pickyour.ai#280](https://github.com/Pick-Your-AI/pickyour.ai/issues/280) — Apple/iOS 16.07: Verify the installed production release | Actual installed production behavior matches the accepted release record. | [Pick-Your-AI/pickyour.ai#279](https://github.com/Pick-Your-AI/pickyour.ai/issues/279) | authorized release/App Store maintainer |

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
