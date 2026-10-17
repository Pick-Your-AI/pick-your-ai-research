# Android 01: Product scope and decision records — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#35](https://github.com/Pick-Your-AI/pickyour.ai/issues/35) under [Pick-Your-AI/pickyour.ai#34](https://github.com/Pick-Your-AI/pickyour.ai/issues/34). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-35).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Reconcile each technology, scope and operating-responsibility decision with evidence and rejected alternatives before scaffolding. Keep unsupported modes explicit; collect actual ownership and reviewer intake instead of assigning by role.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#53](https://github.com/Pick-Your-AI/pickyour.ai/issues/53) — Android 01.01: Android users and primary journeys | Document target users, mobile context, first-release jobs and success measures; distinguish validated evidence from assumptions. The Android device is the configuration client, not automatically the selected inference target. | None; ownership and stated decisions still apply | product decision authority and Android technical lead |
| [Pick-Your-AI/pickyour.ai#57](https://github.com/Pick-Your-AI/pickyour.ai/issues/57) — Android 01.02: MVP and phased capability boundary | Record core, later and conditional scope across API, managed, self-hosted and hybrid modes; consume Pick-Your-AI/pick-your-ai-research#58/Pick-Your-AI/pick-your-ai-research#66 without claiming their acceptance. | [Pick-Your-AI/pickyour.ai#53](https://github.com/Pick-Your-AI/pickyour.ai/issues/53) | product decision authority and Android technical lead |
| [Pick-Your-AI/pickyour.ai#67](https://github.com/Pick-Your-AI/pickyour.ai/issues/67) — Android 01.03: Native implementation and repository decision | Compare Kotlin/Compose with a shared-client approach against offline, accessibility, reuse and maintenance; select package/repository/module boundaries with rationale. | [Pick-Your-AI/pickyour.ai#57](https://github.com/Pick-Your-AI/pickyour.ai/issues/57) | product decision authority and Android technical lead |
| [Pick-Your-AI/pickyour.ai#68](https://github.com/Pick-Your-AI/pickyour.ai/issues/68) — Android 01.04: Service and hosting decision | Choose the minimum production API/data-store deployment and operations owner; distinguish the existing static GoDaddy site from a stateful backend. | [Pick-Your-AI/pickyour.ai#57](https://github.com/Pick-Your-AI/pickyour.ai/issues/57) | product decision authority and Android technical lead |
| [Pick-Your-AI/pickyour.ai#58](https://github.com/Pick-Your-AI/pickyour.ai/issues/58) — Android 01.05: Account and revenue decisions | Decide guest-first behavior, optional accounts, monetization, analytics and notifications; enable only the dependent policy/implementation tasks that apply. | [Pick-Your-AI/pickyour.ai#53](https://github.com/Pick-Your-AI/pickyour.ai/issues/53) | product decision authority and Android technical lead |
| [Pick-Your-AI/pickyour.ai#80](https://github.com/Pick-Your-AI/pickyour.ai/issues/80) — Android 01.06: Acceptance and ownership baseline | Set measurable product/performance/reliability criteria, supported devices, review roles and release gates without inventing dates, budgets or assignees. | [Pick-Your-AI/pickyour.ai#67](https://github.com/Pick-Your-AI/pickyour.ai/issues/67) | product decision authority and Android technical lead |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/01.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: product decision authority and Android technical lead. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
