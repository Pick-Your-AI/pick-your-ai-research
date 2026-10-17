# Android 17: Sustainable product and data operations — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-android#18](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/18) under [Pick-Your-AI/pick-your-ai-android#1](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-android-18).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Exercise privacy-safe signals and alert routing, service restore, data rollback/correction and supported-old-client maintenance. Verify support/correction delivery, redaction preview and no automatic upload. Name actual operating responsibility only when accepted; a runbook without a drill is not operational acceptance.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-android#44](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/44) — Android 17.01: Service and Android observability | Privacy-preserving crash/ANR/error/reliability signals tied to app/API/catalog versions; alerts have owners and actions. | [Pick-Your-AI/pick-your-ai-android#25](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/25), [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23) | accepted support/operations owner and affected data/service owner |
| [Pick-Your-AI/pick-your-ai-android#92](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/92) — Android 17.02: Incident and restore drills | Practice backend backup recovery, catalog rollback, bad-release halt and security/data incident response. | [Pick-Your-AI/pick-your-ai-android#50](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/50), [Pick-Your-AI/pick-your-ai-android#63](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/63) | accepted support/operations owner and affected data/service owner |
| [Pick-Your-AI/pick-your-ai-android#55](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/55) — Android 17.03: Ongoing catalog maintenance | Schedule permitted rechecks, source conflict correction, rights changes, stale prices and known-issue communication with audit trail. | [Pick-Your-AI/pick-your-ai-android#39](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/39) | accepted support/operations owner and affected data/service owner |
| [Pick-Your-AI/pick-your-ai-android#33](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/33) — Android 17.04: Support and contribution workflow | User help, evidence correction requests, reproducible bug reports and safe diagnostics with ownership and response triage. | [Pick-Your-AI/pick-your-ai-android#23](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/23) | accepted support/operations owner and affected data/service owner |
| [Pick-Your-AI/pick-your-ai-android#93](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/93) — Android 17.05: Sustained compatibility and release cadence | Monitor SDK/Play policy/dependency changes, supported API versions and migration deprecation; retain reproducibility across published builds. | [Pick-Your-AI/pick-your-ai-android#69](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/69), [Pick-Your-AI/pick-your-ai-android#49](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/49) | accepted support/operations owner and affected data/service owner |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/17.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: accepted support/operations owner and affected data/service owner. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
