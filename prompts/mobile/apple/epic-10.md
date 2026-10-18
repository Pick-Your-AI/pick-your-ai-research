# Apple/iOS 10: Cost estimation — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#11](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/11) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-11).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Resolve dated eligible rates by exact item version, region, currency and meter. Use approved decimal arithmetic and rounding; unsupported meters remain uncovered. Partial, stale or mixed-currency evidence cannot satisfy a complete-total or budget gate. Preserve original price provenance during scenario comparison and refresh.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#76](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/76) — Apple/iOS 10.01: Select applicable dated rates | Every priced line identifies the applicable rate and source conditions. | [Pick-Your-AI/pick-your-ai-apple#47](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/47), [Pick-Your-AI/pick-your-ai-apple#32](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/32) | pricing semantics and Apple consumer reviewers |
| [Pick-Your-AI/pick-your-ai-apple#77](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/77) — Apple/iOS 10.02: Calculate costs from explicit usage scenarios | Worked scenarios reconcile line totals and assumptions with the canonical service. | [Pick-Your-AI/pick-your-ai-apple#76](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/76) | pricing semantics and Apple consumer reviewers |
| [Pick-Your-AI/pick-your-ai-apple#78](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/78) — Apple/iOS 10.03: Show missing costs, coverage and uncertainty | Missing costs cannot render as zero or an unqualified complete total. | [Pick-Your-AI/pick-your-ai-apple#54](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/54), [Pick-Your-AI/pick-your-ai-apple#77](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/77) | pricing semantics and Apple consumer reviewers |
| [Pick-Your-AI/pick-your-ai-apple#79](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/79) — Apple/iOS 10.04: Compare scenarios and preserve price provenance | Cost comparisons remain reproducible and do not silently mix currencies. | [Pick-Your-AI/pick-your-ai-apple#81](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/81), [Pick-Your-AI/pick-your-ai-apple#78](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/78) | pricing semantics and Apple consumer reviewers |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 10`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: pricing semantics and Apple consumer reviewers. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Every priced line identifies the applicable rate and source conditions.

- Worked scenarios reconcile line totals and assumptions with the canonical service.

- Missing costs cannot render as zero or an unqualified complete total.

- Cost comparisons remain reproducible and do not silently mix currencies.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
