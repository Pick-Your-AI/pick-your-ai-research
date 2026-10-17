# Android 13: Optional tiers and operational catalog depth — execution prompt

Scope: [Pick-Your-AI/pickyour.ai#47](https://github.com/Pick-Your-AI/pickyour.ai/issues/47) under [Pick-Your-AI/pickyour.ai#34](https://github.com/Pick-Your-AI/pickyour.ai/issues/34). Required: [shared rules](../SHARED.md), [platform requirements](../ANDROID.md), [launch instructions](../README.md), [issue/acceptance index](../INDEX.md#issue-47).

## Intake and prerequisite reconciliation

Execute SHARED.md’s complete workflow: inspect live issues/comments/PRs and owners, reconcile native prerequisites and active work, implement the authorized slice, validate meaningful behavior, obtain receiving review, deliver a scoped PR, and verify evidence-backed completion. Preserve the live acceptance criteria and native parents. For a work-package invocation select only its row below; other rows remain coordination context. No assignment or execution is created by publishing this file.

## Integrated outcome and implementation focus

Separate optional T3–T5 breadth from mandatory core T6 guidance. Test selected tier combinations and disabled-tier paths against accepted contracts, not invented capabilities. Guardrail/evaluation selection is not measured quality, proposed deployment export is not execution, and excluded optional combinations do not block core release.

Android-specific execution boundary: use the accepted client/service locations and preserve the static web boundary. Apply process-death, durable migration, permission/Keystore, verified App Links, TalkBack, device and Google Play requirements from ANDROID.md where applicable.

## Existing work packages

| Assigned slice | Outcome to implement | Native prerequisite inputs | Receiving review |
| --- | --- | --- | --- |
| [Pick-Your-AI/pickyour.ai#160](https://github.com/Pick-Your-AI/pickyour.ai/issues/160) — Android 13.01: Knowledge and retrieval configuration | T3 data-source/knowledge/embedding/vector/RAG settings, identities, access constraints and evidence-based relationships. | [Pick-Your-AI/pickyour.ai#154](https://github.com/Pick-Your-AI/pickyour.ai/issues/154) | relevant T3–T6 research owners and Android domain reviewer |
| [Pick-Your-AI/pickyour.ai#161](https://github.com/Pick-Your-AI/pickyour.ai/issues/161) — Android 13.02: Agents, tools, MCP and memory configuration | T4 transport, permissions, memory and framework relationships follow approved contracts and missing-evidence handling. | [Pick-Your-AI/pickyour.ai#154](https://github.com/Pick-Your-AI/pickyour.ai/issues/154) | relevant T3–T6 research owners and Android domain reviewer |
| [Pick-Your-AI/pickyour.ai#162](https://github.com/Pick-Your-AI/pickyour.ai/issues/162) — Android 13.03: Training and fine-tuned model configuration | T5 datasets, lineage, training methods/compute/export/runtime checks remain conditional on accepted contract extensions. | [Pick-Your-AI/pickyour.ai#154](https://github.com/Pick-Your-AI/pickyour.ai/issues/154), [Pick-Your-AI/pickyour.ai#69](https://github.com/Pick-Your-AI/pickyour.ai/issues/69) | relevant T3–T6 research owners and Android domain reviewer |
| [Pick-Your-AI/pickyour.ai#74](https://github.com/Pick-Your-AI/pickyour.ai/issues/74) — Android 13.04: Guardrails and evaluation configuration | Core T6 readiness and relevant guardrail/evaluation guidance are not silently optional; communicate scope, measured conditions and limits. Specific catalog depth follows launch-scope decisions; no guarantee of safety/quality. | [Pick-Your-AI/pickyour.ai#60](https://github.com/Pick-Your-AI/pickyour.ai/issues/60) | relevant T3–T6 research owners and Android domain reviewer |
| [Pick-Your-AI/pickyour.ai#85](https://github.com/Pick-Your-AI/pickyour.ai/issues/85) — Android 13.05: Deployment and monitoring plans | Core planning summary preserves readiness, limitations and relevant deployment/monitoring guidance. Detailed configuration exports and operational catalog breadth follow scope decisions; actual runtime provisioning remains separate. | [Pick-Your-AI/pickyour.ai#57](https://github.com/Pick-Your-AI/pickyour.ai/issues/57) | relevant T3–T6 research owners and Android domain reviewer |
| [Pick-Your-AI/pickyour.ai#101](https://github.com/Pick-Your-AI/pickyour.ai/issues/101) — Android 13.06: Expanded-mode validation | Exercise API/managed/self-hosted/hybrid component placements across optional tiers with evidence, pricing and migration acceptance. | [Pick-Your-AI/pickyour.ai#82](https://github.com/Pick-Your-AI/pickyour.ai/issues/82) | relevant T3–T6 research owners and Android domain reviewer |

## Validation and acceptance record

Epic record/output: `docs/delivery/android/epics/13.md`. This is an intended path in `Pick-Your-AI/pickyour.ai`, not an existing research artifact.

Receiving review: relevant T3–T6 research owners and Android domain reviewer. Resolve people from live assignees and agreed reviewer intake, never from these role names.

For every selected row, open its [index entry](../INDEX.md) and the matching `coverage.json` record. Preserve every exact criterion, implementation step, validation method, required negative/recovery case and delivery/review boundary. Use the live issue to reconcile changes before implementing. Create the criterion-to-evidence table required by SHARED.md at that issue’s existing record location; link artifact hashes, commands, failure/recovery observations and receiving-review disposition.

Demonstrate this epic’s combined outcome, including relevant platform interruption, unavailable-data and recovery paths. Apply the platform program’s device and store distinctions; fixtures and local build success cannot certify production integration or release. Do not infer Done from child counts. The epic’s exact acceptance baseline is:

- Each selected child work package has a concrete deliverable, an owner, validation evidence and required review.

- Child outcomes work together in the supported end-to-end journey, including relevant failure and recovery states.

- Conditional/deferred work has an explicit scope decision; omitted capabilities are not claimed complete.

- Cross-client and research handoffs are accepted where needed; no fabricated facts or undocumented contract changes.

## Handoffs, PR and completion

Use the issue-specific producer/input links in the index and coverage ledger plus the common authority table in SHARED.md. Confirm exact output/version and consumer acceptance with current owners. Native prerequisites gate named outputs; research information and compatibility links are not blanket blockers. Continue independent authorized work when a particular input is missing.

Deliver scoped signed commits and a PR with fully qualified partial issue references, actual validation and unresolved criteria. Obtain receiving and required repository review; do not bypass gates or merge beyond the execution mandate. Re-read before each authorized issue/Project write and verify after it. Complete this epic only when its own integrated criteria and selected child outcomes are accepted, with explicit dispositions for deferred work. Report proposed/submitted/merged status, evidence gaps and the precise remaining owner, input, decision or access condition.
