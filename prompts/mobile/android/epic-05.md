# Android 05: Shared application services — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-android#6](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/6) under [Pick-Your-AI/pick-your-ai-android#1](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-android-6).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Reconcile one shared service contract and producer before adapter work. Exercise server authority for guest/private operations, durable revision/head/event intent, CAS and idempotency, version-bound evaluation/pricing, share redaction/revocation and bounded recovery. Test unavailable service and stale-write cases against an authorized real integration environment before claiming integration.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-android#51](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/51) — Android 05.01: Service skeleton and persistence | Deploy testable API/storage migrations with health/readiness, schema validation, structured errors and environment separation. | [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23), [Pick-Your-AI/pick-your-ai-android#21](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/21), [Pick-Your-AI/pick-your-ai-android#35](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/35) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#61](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/61) — Android 05.02: Catalog discovery and delivery | Current manifest, immutable version reads, search/filter/pagination and caching work consistently for Android and web consumers. | [Pick-Your-AI/pick-your-ai-android#36](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/36), [Pick-Your-AI/pick-your-ai-android#50](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/50), [Pick-Your-AI/pick-your-ai-android#51](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/51) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#78](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/78) — Android 05.03: Build lifecycle service | Create/read/list/update/history/fork/delete endpoints with immutable revisions, CAS/ETag, idempotency and explicit draft handling. Atomically persist immutable revision, head and durable event/outbox intent; recover safely after partial failure. | [Pick-Your-AI/pick-your-ai-android#26](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/26), [Pick-Your-AI/pick-your-ai-android#62](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/62) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#94](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/94) — Android 05.04: Evaluation and pricing service | Execute version-bound requests only after applicable build persistence; prevent stale responses or racing saves from contaminating latest state. Durable recomputation consumers must be idempotent and recover after retries/crashes, independent of client connectivity. | [Pick-Your-AI/pick-your-ai-android#49](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/49), [Pick-Your-AI/pick-your-ai-android#78](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/78) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#95](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/95) — Android 05.05: Share capability service | Read-only immutable shares with redaction, unpredictable identifiers, revocation/expiry decision, web fallback and permissions. | [Pick-Your-AI/pick-your-ai-android#78](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/78) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#79](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/79) — Android 05.06: Resource and quality evidence reads | Serve pinned measured/estimated artifacts with conditions and uncertainty; absence remains unknown, never fabricated capacity. | [Pick-Your-AI/pick-your-ai-android#62](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/62) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#62](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/62) — Android 05.07: Authentication and authorization | Every remote write/private read/share mutation must enforce object ownership and authorization, including guest capability/session models. Full identity/account lifecycle is conditional; verify cross-user access denial, least privilege and revocation in all chosen modes. | [Pick-Your-AI/pick-your-ai-android#36](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/36), [Pick-Your-AI/pick-your-ai-android#51](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/51) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#63](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/63) — Android 05.08: Operational security controls | Rate and payload limits, safe URL handling, abuse controls, audit trail, secret management, backup restore and service observability. | [Pick-Your-AI/pick-your-ai-android#51](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/51) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |
| [Pick-Your-AI/pick-your-ai-android#110](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/110) — Android 05.09: Web coexistence integration | Resolve demo defaults, HTTP/local-store mismatch and auth seam for shared services without duplicating Pick-Your-AI/pickyour.ai#15/Pick-Your-AI/pickyour.ai#17 or breaking fixture preview. | [Pick-Your-AI/pick-your-ai-android#94](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/94), [Pick-Your-AI/pick-your-ai-android#61](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/61) | canonical shared-service owner, security reviewer and Android/web/iOS consumers |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/05.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: canonical shared-service owner, security reviewer and Android/web/iOS consumers. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
