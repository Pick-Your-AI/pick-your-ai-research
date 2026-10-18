# Android 10: Transparent cost estimation — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-android#11](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/11) under [Pick-Your-AI/pick-your-ai-android#1](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-android-11).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Resolve dated eligible rates by exact item version, region, currency and meter. Use approved decimal arithmetic and rounding; unsupported meters remain uncovered. Partial, stale or mixed-currency evidence cannot satisfy a complete-total or budget gate. Preserve original price provenance during scenario comparison and refresh.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-android#66](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/66) — Android 10.01: Conditional rate selection | Exact component versions, meter, region, currency, effective dates and plan eligibility determine applicable rates. | [Pick-Your-AI/pick-your-ai-android#50](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/50) | pricing-semantics owner and Android domain reviewer |
| [Pick-Your-AI/pick-your-ai-android#85](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/85) — Android 10.02: Usage scenarios and arithmetic | Approved usage inputs and decimal-safe arithmetic cover inference, idle compute, storage, egress and training only where representable. | [Pick-Your-AI/pick-your-ai-android#66](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/66) | pricing-semantics owner and Android domain reviewer |
| [Pick-Your-AI/pick-your-ai-android#103](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/103) — Android 10.03: Coverage and uncertainty presentation | Known subtotal, missing items, ranges and assumptions visible; unknown never becomes zero or a complete total. Partial, stale or mixed-currency evidence cannot falsely pass a budget gate; free, included and unknown are distinct. | [Pick-Your-AI/pick-your-ai-android#40](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/40), [Pick-Your-AI/pick-your-ai-android#85](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/85) | pricing-semantics owner and Android domain reviewer |
| [Pick-Your-AI/pick-your-ai-android#116](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/116) — Android 10.04: Scenario comparison and provenance | Compare like-for-like workloads/currencies, preserve dated price snapshots, show freshness and refresh changes. | [Pick-Your-AI/pick-your-ai-android#67](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/67), [Pick-Your-AI/pick-your-ai-android#39](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/39), [Pick-Your-AI/pick-your-ai-android#103](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/103) | pricing-semantics owner and Android domain reviewer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/10.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: pricing-semantics owner and Android domain reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
