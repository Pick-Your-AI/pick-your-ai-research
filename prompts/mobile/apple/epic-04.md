# Apple/iOS 04: Research-to-production catalog pipeline — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-5).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Trace the approved slice from source-use permission through normalized claims, human promotion receipt and atomic immutable manifest to the client. Reject malformed, withdrawn or unapproved data while retaining the prior complete cache. Historical pins and current corrections must remain distinguishable.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#38](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/38) — Apple/iOS 04.01: Source access, display and redistribution rights | Every displayed production field has an applicable source-use decision. | None; ownership and stated decisions still apply | source-rights/evidence/publication reviewers and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#39](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/39) — Apple/iOS 04.02: Normalize and validate component facts | Apple ingestion matches canonical validation and retains valid cached state on failure. | [Pick-Your-AI/pick-your-ai-android#28](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/28), [Pick-Your-AI/pick-your-ai-apple#38](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/38), [Pick-Your-AI/pick-your-ai-apple#32](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/32) | source-rights/evidence/publication reviewers and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#40](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/40) — Apple/iOS 04.03: Evidence review and production approval | Research merge alone cannot activate production data in the client. | [Pick-Your-AI/pick-your-ai-android#38](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/38), [Pick-Your-AI/pick-your-ai-apple#39](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/39) | source-rights/evidence/publication reviewers and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#41](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/41) — Apple/iOS 04.04: Publish immutable catalog and rule releases | Apple installs or rolls back an internally consistent data release. | [Pick-Your-AI/pick-your-ai-android#50](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/50), [Pick-Your-AI/pick-your-ai-apple#40](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/40) | source-rights/evidence/publication reviewers and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#42](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/42) — Apple/iOS 04.05: Freshness, corrections and retractions | Corrections update current guidance without rewriting historical evidence. | [Pick-Your-AI/pick-your-ai-android#39](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/39), [Pick-Your-AI/pick-your-ai-apple#41](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/41) | source-rights/evidence/publication reviewers and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#43](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/43) — Apple/iOS 04.06: Publish the first complete supported real-data path | A real-data build-to-share demonstration has reviewed coverage and evidence. | [Pick-Your-AI/pick-your-ai-android#60](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/60), [Pick-Your-AI/pick-your-ai-apple#42](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/42) | source-rights/evidence/publication reviewers and Apple consumer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 04`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: source-rights/evidence/publication reviewers and Apple consumer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Every displayed production field has an applicable source-use decision.

- Apple ingestion matches canonical validation and retains valid cached state on failure.

- Research merge alone cannot activate production data in the client.

- Apple installs or rolls back an internally consistent data release.

- Corrections update current guidance without rewriting historical evidence.

- A real-data build-to-share demonstration has reviewed coverage and evidence.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
