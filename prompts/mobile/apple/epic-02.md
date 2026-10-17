# Apple/iOS 02: Apple application foundation — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#165](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) under [Pick-Your-AI/pickyour.ai#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163). Required: [shared rules](../SHARED.md), [platform requirements](../APPLE.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-165).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Deliver a reproducible clean-checkout client with isolated environments and typed UI/domain/data boundaries. Demonstrate interrupted editing and cold external entry without mixing drafts; preserve existing web CI gates and prevent release-secret access from untrusted changes.

Apple-specific receiving boundary: consume the canonical shared output and implement only Apple requirements/adapters/acceptance. Use the lifecycle, Keychain/entitlement, Universal Link, VoiceOver and TestFlight/App Store requirements in APPLE.md where applicable. No second backend, imposed framework or extra Apple platform.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#188](https://github.com/Pick-Your-AI/pickyour.ai/issues/188) — Apple/iOS 02.01: Xcode toolchain, dependencies and modules | Fresh macOS checkout builds supported targets reproducibly. | [Pick-Your-AI/pickyour.ai#184](https://github.com/Pick-Your-AI/pickyour.ai/issues/184) | Apple engineering and CI reviewer |
| [Pick-Your-AI/pickyour.ai#189](https://github.com/Pick-Your-AI/pickyour.ai/issues/189) — Apple/iOS 02.02: Preview, staging and production environments | Production configuration cannot silently consume synthetic or staging data. | [Pick-Your-AI/pickyour.ai#188](https://github.com/Pick-Your-AI/pickyour.ai/issues/188) | Apple engineering and CI reviewer |
| [Pick-Your-AI/pickyour.ai#190](https://github.com/Pick-Your-AI/pickyour.ai/issues/190) — Apple/iOS 02.03: Navigation, lifecycle and state restoration | Interrupted and deep-linked journeys restore the correct draft. | [Pick-Your-AI/pickyour.ai#188](https://github.com/Pick-Your-AI/pickyour.ai/issues/188) | Apple engineering and CI reviewer |
| [Pick-Your-AI/pickyour.ai#191](https://github.com/Pick-Your-AI/pickyour.ai/issues/191) — Apple/iOS 02.04: UI, domain and data boundaries | UI remains responsive and stale tasks cannot overwrite current state. | [Pick-Your-AI/pickyour.ai#188](https://github.com/Pick-Your-AI/pickyour.ai/issues/188) | Apple engineering and CI reviewer |
| [Pick-Your-AI/pickyour.ai#192](https://github.com/Pick-Your-AI/pickyour.ai/issues/192) — Apple/iOS 02.05: macOS continuous integration and required checks | A clean PR run executes required native checks without weakening web gates. | [Pick-Your-AI/pickyour.ai#188](https://github.com/Pick-Your-AI/pickyour.ai/issues/188) | Apple engineering and CI reviewer |
| [Pick-Your-AI/pickyour.ai#193](https://github.com/Pick-Your-AI/pickyour.ai/issues/193) — Apple/iOS 02.06: Clearly identified synthetic fixtures | Every fixture is recognizable and production data mode rejects accidental demo records. | [Pick-Your-AI/pickyour.ai#194](https://github.com/Pick-Your-AI/pickyour.ai/issues/194) | Apple engineering and CI reviewer |

## Validation and acceptance record

Epic record/output: `integrated epic evidence record for 02`. Link the record from the live issue after the repository/module decision; the snapshot does not establish a file path.

Receiving review: Apple engineering and CI reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Fresh macOS checkout builds supported targets reproducibly.

- Production configuration cannot silently consume synthetic or staging data.

- Interrupted and deep-linked journeys restore the correct draft.

- UI remains responsive and stale tasks cannot overwrite current state.

- A clean PR run executes required native checks without weakening web gates.

- Every fixture is recognizable and production data mode rejects accidental demo records.

- Receiving reviews accept the combined epic demonstration and explicitly dispose of excluded scope; native child completion alone is insufficient.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
