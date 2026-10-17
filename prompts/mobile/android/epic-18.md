# Android 18: Decision-dependent growth capabilities — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#52](https://github.com/Pick-Your-AI/pickyour.ai/issues/52) under [Pick-Your-AI/pickyour.ai#34](https://github.com/Pick-Your-AI/pickyour.ai/issues/34). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-52).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Resolve each capability-specific scope gate independently: notifications, commerce, public community, recommendations, runtime actions and expansion. Approval is an entry gate, not completion. Preserve ranking neutrality, operational moderation and scoped runtime/spend authority; execute the issue-specific behavioral and recovery checks only for approved scope.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#89](https://github.com/Pick-Your-AI/pickyour.ai/issues/89) — Android 18.01: Favorites and price/compatibility alerts | Only after explicit scope acceptance: meaningful events, subscriptions, permission timing, background scheduling and opt-out. | [Pick-Your-AI/pickyour.ai#58](https://github.com/Pick-Your-AI/pickyour.ai/issues/58) | product decision authority and relevant security/policy reviewer |
| [Pick-Your-AI/pickyour.ai#78](https://github.com/Pick-Your-AI/pickyour.ai/issues/78) — Android 18.02: Paid plans and entitlements | Only if monetization chosen: applicable Play Billing rules, verified entitlements, restore/cancel/refunds and non-biased recommendations. | [Pick-Your-AI/pickyour.ai#56](https://github.com/Pick-Your-AI/pickyour.ai/issues/56), [Pick-Your-AI/pickyour.ai#58](https://github.com/Pick-Your-AI/pickyour.ai/issues/58) | product decision authority and relevant security/policy reviewer |
| [Pick-Your-AI/pickyour.ai#153](https://github.com/Pick-Your-AI/pickyour.ai/issues/153) — Android 18.03: Community build publishing | Only if selected: moderation/report/block, trust/provenance, privacy, spam controls and terms. | [Pick-Your-AI/pickyour.ai#128](https://github.com/Pick-Your-AI/pickyour.ai/issues/128) | product decision authority and relevant security/policy reviewer |
| [Pick-Your-AI/pickyour.ai#142](https://github.com/Pick-Your-AI/pickyour.ai/issues/142) — Android 18.04: Advanced recommendations and personalization | Only with accepted evidence and user value: transparent ranking, conflicts disclosure, opt-outs and reproducible evaluation. | [Pick-Your-AI/pickyour.ai#56](https://github.com/Pick-Your-AI/pickyour.ai/issues/56), [Pick-Your-AI/pickyour.ai#117](https://github.com/Pick-Your-AI/pickyour.ai/issues/117) | product decision authority and relevant security/policy reviewer |
| [Pick-Your-AI/pickyour.ai#79](https://github.com/Pick-Your-AI/pickyour.ai/issues/79) — Android 18.05: Runtime execution or provisioning | Separate approved scope from planning/export; provider credentials, spend consent, isolation, rollback and authorization required before execution. | [Pick-Your-AI/pickyour.ai#56](https://github.com/Pick-Your-AI/pickyour.ai/issues/56), [Pick-Your-AI/pickyour.ai#57](https://github.com/Pick-Your-AI/pickyour.ai/issues/57) | product decision authority and relevant security/policy reviewer |
| [Pick-Your-AI/pickyour.ai#108](https://github.com/Pick-Your-AI/pickyour.ai/issues/108) — Android 18.06: Expanded markets and platforms | Localization, regions/currencies and non-Android clients only after approved product priorities and maintained data rights. | [Pick-Your-AI/pickyour.ai#82](https://github.com/Pick-Your-AI/pickyour.ai/issues/82) | product decision authority and relevant security/policy reviewer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/18.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: product decision authority and relevant security/policy reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
