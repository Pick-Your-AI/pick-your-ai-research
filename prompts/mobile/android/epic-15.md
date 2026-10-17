# Android 15: Integrated quality and performance — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#49](https://github.com/Pick-Your-AI/pickyour.ai/issues/49) under [Pick-Your-AI/pickyour.ai#34](https://github.com/Pick-Your-AI/pickyour.ai/issues/34). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-49).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Build a criterion-to-test matrix across domain, UI/accessibility, faults, device/lifecycle, cross-client, performance and release security. Intentionally break boundaries to prove gates detect failures. Separate physical-device and real-service evidence from mocks/simulators; authorized user validation requires its own protocol and authority.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#65](https://github.com/Pick-Your-AI/pickyour.ai/issues/65) — Android 15.01: Contract and domain regression suite | Golden/malformed/version migration tests cover all supported kinds, optional states, cycles, unknowns, decimals and CAS. | [Pick-Your-AI/pickyour.ai#82](https://github.com/Pick-Your-AI/pickyour.ai/issues/82) | Android quality reviewer and feature owners |
| [Pick-Your-AI/pickyour.ai#139](https://github.com/Pick-Your-AI/pickyour.ai/issues/139) — Android 15.02: Android UI and accessibility suite | Primary flows with TalkBack/font scale/RTL/keyboard/reduced motion and automated semantics checks. | [Pick-Your-AI/pickyour.ai#109](https://github.com/Pick-Your-AI/pickyour.ai/issues/109) | Android quality reviewer and feature owners |
| [Pick-Your-AI/pickyour.ai#123](https://github.com/Pick-Your-AI/pickyour.ai/issues/123) — Android 15.03: Network and resilience suite | Offline, slow/lossy network, errors, auth expiry, cancellation, race responses, duplicate writes and restore tested. | [Pick-Your-AI/pickyour.ai#91](https://github.com/Pick-Your-AI/pickyour.ai/issues/91) | Android quality reviewer and feature owners |
| [Pick-Your-AI/pickyour.ai#140](https://github.com/Pick-Your-AI/pickyour.ai/issues/140) — Android 15.04: Device and lifecycle matrix | Real/emulated supported API levels, phone/tablet/foldable/low-memory, rotation, resize, process death and app upgrades. | [Pick-Your-AI/pickyour.ai#109](https://github.com/Pick-Your-AI/pickyour.ai/issues/109), [Pick-Your-AI/pickyour.ai#80](https://github.com/Pick-Your-AI/pickyour.ai/issues/80) | Android quality reviewer and feature owners |
| [Pick-Your-AI/pickyour.ai#103](https://github.com/Pick-Your-AI/pickyour.ai/issues/103) — Android 15.05: Cross-client integration tests | Android/web/server round trip of drafts, immutable shares, snapshots, revisions and idempotency with identical semantics. | [Pick-Your-AI/pickyour.ai#82](https://github.com/Pick-Your-AI/pickyour.ai/issues/82) | Android quality reviewer and feature owners |
| [Pick-Your-AI/pickyour.ai#104](https://github.com/Pick-Your-AI/pickyour.ai/issues/104) — Android 15.06: Measured performance budgets | Set evidence-based startup, frame time, memory, battery, download/API latency and large-catalog targets; profile optimized release build. | [Pick-Your-AI/pickyour.ai#81](https://github.com/Pick-Your-AI/pickyour.ai/issues/81), [Pick-Your-AI/pickyour.ai#80](https://github.com/Pick-Your-AI/pickyour.ai/issues/80) | Android quality reviewer and feature owners |
| [Pick-Your-AI/pickyour.ai#105](https://github.com/Pick-Your-AI/pickyour.ai/issues/105) — Android 15.07: Security and release regression | R8/minification behavior, backup restore/deletion, permissions, signing and installed-release smoke checks. | [Pick-Your-AI/pickyour.ai#124](https://github.com/Pick-Your-AI/pickyour.ai/issues/124), [Pick-Your-AI/pickyour.ai#122](https://github.com/Pick-Your-AI/pickyour.ai/issues/122), [Pick-Your-AI/pickyour.ai#102](https://github.com/Pick-Your-AI/pickyour.ai/issues/102), [Pick-Your-AI/pickyour.ai#64](https://github.com/Pick-Your-AI/pickyour.ai/issues/64) | Android quality reviewer and feature owners |
| [Pick-Your-AI/pickyour.ai#106](https://github.com/Pick-Your-AI/pickyour.ai/issues/106) — Android 15.08: User validation and acceptance | Execute approved consent protocol only when authorized; record usability evidence and acceptance decisions, no fabricated success metrics. | [Pick-Your-AI/pickyour.ai#80](https://github.com/Pick-Your-AI/pickyour.ai/issues/80) | Android quality reviewer and feature owners |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/15.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: Android quality reviewer and feature owners. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
