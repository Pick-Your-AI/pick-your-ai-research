# Apple/iOS 01: Product scope and decisions — execution prompt

Scope: [Pick-Your-AI/pick-your-ai-apple#2](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) under [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-apple-2).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Reconcile each technology, scope and operating-responsibility decision with evidence and rejected alternatives before scaffolding. Keep unsupported modes explicit; collect actual ownership and reviewer intake instead of assigning by role.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pick-your-ai-apple#20](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/20) — Apple/iOS 01.01: Target users and primary iPhone and iPad journeys | Reviewed journey map distinguishes evidence from assumptions. | None; ownership and stated decisions still apply | product/release decision reviewer |
| [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) — Apple/iOS 01.02: MVP scope and phased capabilities | Scope matrix identifies every release inclusion and exclusion. | [Pick-Your-AI/pick-your-ai-apple#20](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/20) | product/release decision reviewer |
| [Pick-Your-AI/pick-your-ai-apple#22](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22) — Apple/iOS 01.03: Apple platform scope, technology and repository structure | Architecture decision names supported targets and implementation boundaries. | [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product/release decision reviewer |
| [Pick-Your-AI/pick-your-ai-apple#23](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/23) — Apple/iOS 01.04: Backend architecture and hosting | Accepted service integration ADR identifies endpoints and operating responsibility. | [Pick-Your-AI/pick-your-ai-android#35](https://github.com/Pick-Your-AI/pick-your-ai-android/issues/35), [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product/release decision reviewer |
| [Pick-Your-AI/pick-your-ai-apple#24](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24) — Apple/iOS 01.05: Accounts and monetization decisions | Account and revenue decision explicitly selects applicable platform obligations. | [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product/release decision reviewer |
| [Pick-Your-AI/pick-your-ai-apple#25](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/25) — Apple/iOS 01.06: Acceptance criteria, ownership and release gates | Accepted criteria and ownership intake exist without invented commitments. | [Pick-Your-AI/pick-your-ai-apple#21](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | product/release decision reviewer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 01`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: product/release decision reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Reviewed journey map distinguishes evidence from assumptions.

- Scope matrix identifies every release inclusion and exclusion.

- Architecture decision names supported targets and implementation boundaries.

- Accepted service integration ADR identifies endpoints and operating responsibility.

- Account and revenue decision explicitly selects applicable platform obligations.

- Accepted criteria and ownership intake exist without invented commitments.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
