# Android 14: Privacy, security and trust — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-android#15](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/15) under [Pick-Your-AI/pick-your-ai-android#1](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-android-15).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Trace sensitive fields through imports, caches, shares, services, diagnostics and deletion. Implement the approved threat mitigations early, test negative authority and device-protection states, reconcile SDK traffic with disclosures, and retest fixes. Conditional accounts do not waive authorization of guest remote writes.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23) — Android 14.01: Data inventory and threat model | Map workload metadata, accounts, shares, telemetry, links and artifacts; minimize collection and identify concrete attack surfaces. | None; ownership and stated decisions still apply | security/privacy reviewer and affected service owner |
| [Pick-Your-AI/pick-your-ai-android#89](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/89) — Android 14.02: Android secure storage and networking | Least-permission manifest, TLS/network policy, safe token handling/Keystore where applicable, redacted logs and backup exclusions. | [Pick-Your-AI/pick-your-ai-android#57](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/57), [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23) | security/privacy reviewer and affected service owner |
| [Pick-Your-AI/pick-your-ai-android#42](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/42) — Android 14.03: Account and data lifecycle | If account creation exists, including optional signup or links to external signup, implement registration/recovery/revocation, in-app and public web deletion initiation, associated-data fulfillment and retention disclosures; test actual completion. | [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23), [Pick-Your-AI/pick-your-ai-android#25](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/25) | security/privacy reviewer and affected service owner |
| [Pick-Your-AI/pick-your-ai-android#43](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/43) — Android 14.04: Privacy disclosures and SDK controls | Actual collection/sharing map matches privacy policy, consent and Play Data safety; third-party SDK behavior inventoried. | [Pick-Your-AI/pick-your-ai-android#25](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/25), [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23) | security/privacy reviewer and affected service owner |
| [Pick-Your-AI/pick-your-ai-android#31](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/31) — Android 14.05: Share/import and API adversarial review | Test unauthorized object access, enumeration, malicious payloads, oversized inputs, injection and untrusted external navigation. | [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23) | security/privacy reviewer and affected service owner |
| [Pick-Your-AI/pick-your-ai-android#69](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/69) — Android 14.06: Dependency and vulnerability response | Pinned dependencies, SBOM/license review, secret scanning, vulnerability handling, reporting channel and urgent update runbook. | [Pick-Your-AI/pick-your-ai-android#48](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/48) | security/privacy reviewer and affected service owner |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/14.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: security/privacy reviewer and affected service owner. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
