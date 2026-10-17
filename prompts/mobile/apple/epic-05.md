# Apple/iOS 05: Shared application services — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) under [Pick-Your-AI/pickyour.ai#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-168).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Reconcile one shared service contract and producer before adapter work. Exercise server authority for guest/private operations, durable revision/head/event intent, CAS and idempotency, version-bound evaluation/pricing, share redaction/revocation and bounded recovery. Test unavailable service and stale-write cases against an authorized real integration environment before claiming integration.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#206](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) — Apple/iOS 05.01: API foundation, database and migrations | Staging integration proves service contract availability without a duplicate backend. | [Pick-Your-AI/pickyour.ai#84](https://github.com/Pick-Your-AI/pickyour.ai/issues/84), [Pick-Your-AI/pickyour.ai#196](https://github.com/Pick-Your-AI/pickyour.ai/issues/196), [Pick-Your-AI/pickyour.ai#185](https://github.com/Pick-Your-AI/pickyour.ai/issues/185) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#207](https://github.com/Pick-Your-AI/pickyour.ai/issues/207) — Apple/iOS 05.02: Catalog discovery, search and delivery | Search and catalog loading remain consistent across page and cache boundaries. | [Pick-Your-AI/pickyour.ai#94](https://github.com/Pick-Your-AI/pickyour.ai/issues/94), [Pick-Your-AI/pickyour.ai#203](https://github.com/Pick-Your-AI/pickyour.ai/issues/203), [Pick-Your-AI/pickyour.ai#206](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#208](https://github.com/Pick-Your-AI/pickyour.ai/issues/208) — Apple/iOS 05.03: Build creation, revisions, history and deletion | Remote lifecycle operations preserve history and reject stale overwrites. | [Pick-Your-AI/pickyour.ai#212](https://github.com/Pick-Your-AI/pickyour.ai/issues/212), [Pick-Your-AI/pickyour.ai#111](https://github.com/Pick-Your-AI/pickyour.ai/issues/111), [Pick-Your-AI/pickyour.ai#195](https://github.com/Pick-Your-AI/pickyour.ai/issues/195), [Pick-Your-AI/pickyour.ai#206](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#209](https://github.com/Pick-Your-AI/pickyour.ai/issues/209) — Apple/iOS 05.04: Compatibility evaluation and pricing services | Only matching current analysis is presented as current. | [Pick-Your-AI/pickyour.ai#127](https://github.com/Pick-Your-AI/pickyour.ai/issues/127), [Pick-Your-AI/pickyour.ai#198](https://github.com/Pick-Your-AI/pickyour.ai/issues/198), [Pick-Your-AI/pickyour.ai#206](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#210](https://github.com/Pick-Your-AI/pickyour.ai/issues/210) — Apple/iOS 05.05: Share creation, access and revocation | Share lifecycle works through the canonical service with explicit privacy handling. | [Pick-Your-AI/pickyour.ai#212](https://github.com/Pick-Your-AI/pickyour.ai/issues/212), [Pick-Your-AI/pickyour.ai#128](https://github.com/Pick-Your-AI/pickyour.ai/issues/128), [Pick-Your-AI/pickyour.ai#260](https://github.com/Pick-Your-AI/pickyour.ai/issues/260), [Pick-Your-AI/pickyour.ai#208](https://github.com/Pick-Your-AI/pickyour.ai/issues/208) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#211](https://github.com/Pick-Your-AI/pickyour.ai/issues/211) — Apple/iOS 05.06: Resource estimates and quality evidence | Capacity and measured quality remain separate and correctly bound. | [Pick-Your-AI/pickyour.ai#112](https://github.com/Pick-Your-AI/pickyour.ai/issues/112), [Pick-Your-AI/pickyour.ai#196](https://github.com/Pick-Your-AI/pickyour.ai/issues/196), [Pick-Your-AI/pickyour.ai#206](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#212](https://github.com/Pick-Your-AI/pickyour.ai/issues/212) — Apple/iOS 05.07: Authorization and optional account authentication | No remote mutation relies solely on client-side ownership checks. | [Pick-Your-AI/pickyour.ai#95](https://github.com/Pick-Your-AI/pickyour.ai/issues/95), [Pick-Your-AI/pickyour.ai#260](https://github.com/Pick-Your-AI/pickyour.ai/issues/260), [Pick-Your-AI/pickyour.ai#206](https://github.com/Pick-Your-AI/pickyour.ai/issues/206), [Pick-Your-AI/pickyour.ai#186](https://github.com/Pick-Your-AI/pickyour.ai/issues/186) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#213](https://github.com/Pick-Your-AI/pickyour.ai/issues/213) — Apple/iOS 05.08: Limits, auditability, secrets and recovery | Apple retries are bounded and observable without exposing sensitive content. | [Pick-Your-AI/pickyour.ai#96](https://github.com/Pick-Your-AI/pickyour.ai/issues/96), [Pick-Your-AI/pickyour.ai#206](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) | canonical shared-service reviewer, security reviewer and Apple consumer |
| [Pick-Your-AI/pickyour.ai#214](https://github.com/Pick-Your-AI/pickyour.ai/issues/214) — Apple/iOS 05.09: Integration with the existing website | Both clients interpret the same supported configuration consistently. | [Pick-Your-AI/pickyour.ai#210](https://github.com/Pick-Your-AI/pickyour.ai/issues/210), [Pick-Your-AI/pickyour.ai#209](https://github.com/Pick-Your-AI/pickyour.ai/issues/209), [Pick-Your-AI/pickyour.ai#208](https://github.com/Pick-Your-AI/pickyour.ai/issues/208), [Pick-Your-AI/pickyour.ai#207](https://github.com/Pick-Your-AI/pickyour.ai/issues/207) | canonical shared-service reviewer, security reviewer and Apple consumer |

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
