# Android 02: Android application foundation — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-android#3](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/3) under [Pick-Your-AI/pick-your-ai-android#1](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-android-3).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Deliver a reproducible clean-checkout client with isolated environments and typed UI/domain/data boundaries. Demonstrate interrupted editing and cold external entry without mixing drafts; preserve existing web CI gates and prevent release-secret access from untrusted changes.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-android#48](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/48) — Android 02.01: Toolchain and modules | Pinned compatible JDK/Gradle/Android/Kotlin dependencies, package ID decision, modular build, documented developer setup and clean-checkout build. | [Pick-Your-AI/pick-your-ai-android#34](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/34) | Android technical lead and CI maintainer |
| [Pick-Your-AI/pick-your-ai-android#57](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/57) — Android 02.02: Environments and configuration | Separate preview/staging/production endpoints and IDs; no secrets in APK; configuration and contract versions observable. | [Pick-Your-AI/pick-your-ai-android#35](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/35), [Pick-Your-AI/pick-your-ai-android#48](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/48) | Android technical lead and CI maintainer |
| [Pick-Your-AI/pick-your-ai-android#76](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/76) — Android 02.03: Navigation and lifecycle | Stable navigation/routes, deep-link entry and back handling; restore correct screen and draft across rotation, backgrounding and process death. | [Pick-Your-AI/pick-your-ai-android#67](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/67) | Android technical lead and CI maintainer |
| [Pick-Your-AI/pick-your-ai-android#58](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/58) — Android 02.04: Data and domain boundaries | UI state, repositories, domain rules and adapters separated; typed asynchronous errors and cancellation; no network work on main thread. | [Pick-Your-AI/pick-your-ai-android#21](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/21), [Pick-Your-AI/pick-your-ai-android#48](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/48) | Android technical lead and CI maintainer |
| [Pick-Your-AI/pick-your-ai-android#59](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/59) — Android 02.05: Android CI baseline | Reproducible lint/unit/contract/build checks, emulator strategy, protected required status and artifact provenance; preserve current web gates. | [Pick-Your-AI/pick-your-ai-android#48](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/48) | Android technical lead and CI maintainer |
| [Pick-Your-AI/pick-your-ai-android#77](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/77) — Android 02.06: Preview and test fixtures | Explicitly synthetic sample data, isolated test contracts, no accidental promotion of fictional prices/components into real-data mode. | [Pick-Your-AI/pick-your-ai-android#58](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/58) | Android technical lead and CI maintainer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/02.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: Android technical lead and CI maintainer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
