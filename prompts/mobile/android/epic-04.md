# Android 04: Research-to-production catalog pipeline — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-android#5](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/5) under [Pick-Your-AI/pick-your-ai-android#1](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-android-5).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Trace the approved slice from source-use permission through normalized claims, human promotion receipt and atomic immutable manifest to the client. Reject malformed, withdrawn or unapproved data while retaining the prior complete cache. Historical pins and current corrections must remain distinguishable.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-android#22](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/22) — Android 04.01: Source rights and ingestion register | Use exact per-source permitted retrieval, commercial display, offline caching, retention, redistribution and export paths; unresolved rights excluded from production promotion. | None; ownership and stated decisions still apply | catalog publication owner, research evidence/rights owners and Android consumer |
| [Pick-Your-AI/pick-your-ai-android#28](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/28) — Android 04.02: Normalization and validation | Map catalog identity, versions, references, units, provenance and conditions without placeholder facts; validate source-to-field traceability. | [Pick-Your-AI/pick-your-ai-android#21](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/21) | catalog publication owner, research evidence/rights owners and Android consumer |
| [Pick-Your-AI/pick-your-ai-android#38](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/38) — Android 04.03: Review and promotion workflow | Human evidence review plus automated structure checks; separate research merge from production approval; quarantine conflicts and incomplete records. | [Pick-Your-AI/pick-your-ai-android#27](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/27), [Pick-Your-AI/pick-your-ai-android#28](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/28), [Pick-Your-AI/pick-your-ai-android#22](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/22) | catalog publication owner, research evidence/rights owners and Android consumer |
| [Pick-Your-AI/pick-your-ai-android#50](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/50) — Android 04.04: Immutable artifact publication | Publish hash-addressed catalog/rules/graph/pricebook snapshots atomically; support retention, compatibility manifests, rollback and availability. | [Pick-Your-AI/pick-your-ai-android#38](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/38) | catalog publication owner, research evidence/rights owners and Android consumer |
| [Pick-Your-AI/pick-your-ai-android#39](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/39) — Android 04.05: Freshness and correction workflow | Differentiate pinned facts from current prices/availability; apply approved freshness rules, retractions, supersession and change notification. | [Pick-Your-AI/pick-your-ai-android#27](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/27), [Pick-Your-AI/pick-your-ai-android#22](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/22) | catalog publication owner, research evidence/rights owners and Android consumer |
| [Pick-Your-AI/pick-your-ai-android#60](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/60) — Android 04.06: First supported real-data slice | Release a reviewed end-to-end workload/model/runtime/price slice with explicit coverage and unknowns, not a catalog-count-only milestone. | [Pick-Your-AI/pick-your-ai-android#50](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/50) | catalog publication owner, research evidence/rights owners and Android consumer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/04.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: catalog publication owner, research evidence/rights owners and Android consumer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
