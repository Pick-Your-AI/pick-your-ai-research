# Apple/iOS 05: Shared application services — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-6).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Reconcile one shared service contract and producer before adapter work. Exercise server authority for guest/private operations, durable revision/head/event intent, CAS and idempotency, version-bound evaluation/pricing, share redaction/revocation and bounded recovery. Test unavailable service and stale-write cases against an authorized real integration environment before claiming integration.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#44](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44) — Apple/iOS 05.01: API foundation, database and migrations | Staging integration proves service contract availability without a duplicate backend. | [Pick-Your-AI/pick-your-ai-android#51](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/51), [Pick-Your-AI/pick-your-ai-apple#34](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/34), [Pick-Your-AI/pick-your-ai-apple#23](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/23) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#45](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/45) — Apple/iOS 05.02: Catalog discovery, search and delivery | Search and catalog loading remain consistent across page and cache boundaries. | [Pick-Your-AI/pick-your-ai-android#61](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/61), [Pick-Your-AI/pick-your-ai-apple#41](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/41), [Pick-Your-AI/pick-your-ai-apple#44](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#46](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/46) — Apple/iOS 05.03: Build creation, revisions, history and deletion | Remote lifecycle operations preserve history and reject stale overwrites. | [Pick-Your-AI/pick-your-ai-apple#50](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/50), [Pick-Your-AI/pick-your-ai-android#78](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/78), [Pick-Your-AI/pick-your-ai-apple#33](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/33), [Pick-Your-AI/pick-your-ai-apple#44](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#47](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/47) — Apple/iOS 05.04: Compatibility evaluation and pricing services | Only matching current analysis is presented as current. | [Pick-Your-AI/pick-your-ai-android#94](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/94), [Pick-Your-AI/pick-your-ai-apple#36](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/36), [Pick-Your-AI/pick-your-ai-apple#44](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#48](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/48) — Apple/iOS 05.05: Share creation, access and revocation | Share lifecycle works through the canonical service with explicit privacy handling. | [Pick-Your-AI/pick-your-ai-apple#50](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/50), [Pick-Your-AI/pick-your-ai-android#95](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/95), [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98), [Pick-Your-AI/pick-your-ai-apple#46](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/46) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#49](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/49) — Apple/iOS 05.06: Resource estimates and quality evidence | Capacity and measured quality remain separate and correctly bound. | [Pick-Your-AI/pick-your-ai-android#79](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/79), [Pick-Your-AI/pick-your-ai-apple#34](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/34), [Pick-Your-AI/pick-your-ai-apple#44](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#50](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/50) — Apple/iOS 05.07: Authorization and optional account authentication | No remote mutation relies solely on client-side ownership checks. | [Pick-Your-AI/pick-your-ai-android#62](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/62), [Pick-Your-AI/pick-your-ai-apple#98](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98), [Pick-Your-AI/pick-your-ai-apple#44](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44), [Pick-Your-AI/pick-your-ai-apple#24](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#51](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/51) — Apple/iOS 05.08: Limits, auditability, secrets and recovery | Apple retries are bounded and observable without exposing sensitive content. | [Pick-Your-AI/pick-your-ai-android#63](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/63), [Pick-Your-AI/pick-your-ai-apple#44](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pick-your-ai-apple#52](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/52) — Apple/iOS 05.09: Integration with the existing website | Both clients interpret the same supported configuration consistently. | [Pick-Your-AI/pick-your-ai-apple#48](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/48), [Pick-Your-AI/pick-your-ai-apple#47](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/47), [Pick-Your-AI/pick-your-ai-apple#46](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/46), [Pick-Your-AI/pick-your-ai-apple#45](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/45) | canonical shared-service reviewer, security reviewer and Apple consumer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 05`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: canonical shared-service reviewer, security reviewer and Apple consumer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Staging integration proves service contract availability without a duplicate backend.

- Search and catalog loading remain consistent across page and cache boundaries.

- Remote lifecycle operations preserve history and reject stale overwrites.

- Only matching current analysis is presented as current.

- Share lifecycle works through the canonical service with explicit privacy handling.

- Capacity and measured quality remain separate and correctly bound.

- No remote mutation relies solely on client-side ownership checks.

- Apple retries are bounded and observable without exposing sensitive content.

- Both clients interpret the same supported configuration consistently.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
