# Shared mobile delivery execution rules

Read this file with the platform program prompt, selected epic prompt, and that issue's entry in [the index](INDEX.md). These rules apply to every program, epic and assigned work package. Publication is proposed guidance, not invocation, assignment, implementation evidence or release authority. A narrower user mandate controls execution.

## Inspect and take ownership

1. Read applicable AGENTS.md, CONTRIBUTING.md, governance, architecture, CODEOWNERS and required checks in every destination repository. In this research repository also read [RESEARCH_WORKFLOW.md](../../docs/RESEARCH_WORKFLOW.md), [CONTRACT_MAPPING.md](../../docs/CONTRACT_MAPPING.md), [ADOPTION.md](../../contracts/v1/ADOPTION.md) and the platform plans. The archived IMPLEMENTATION documents do not authorize runtime work here.
2. Refresh the selected Project, field IDs/options, all in-scope issues, full bodies/comments, native parents/children/prerequisites, assignees, accepted records, linked/open/closed/merged PRs and existing runs. Paginate every connection. Counts in the index are a publication snapshot, never a quota. Check issue bodies as well as native edges: information inputs often have no edge.
3. Live GitHub Assignees are ownership authority. Research owners do not acquire implementation assignments. Record accountable owner and receiving reviewers from actual agreements; leave missing intake explicit. Do not invent people, dates, estimates, commitments, thresholds or decisions. Coordinate with an active owner/run and reuse its receipts and branches; do not start duplicate controllers or independent copies of shared work.
4. Reconcile the live issue against the indexed acceptance baseline. Preserve every criterion, implementation step, negative/recovery case, deliverable and scope limitation. If changed, reconcile with the responsible owner before dependent work; do not overwrite current scope with the snapshot. Work-package invocation selects only that issue, not siblings or the entire epic.

## Reconcile prerequisites and architecture

The device is a planning client, not automatically the inference target. Resolve repository/module/framework and service-placement decisions before dependent implementation. Android placement is [Pick-Your-AI/pickyour.ai#67](https://github.com/Pick-Your-AI/pickyour.ai/issues/67), services [Pick-Your-AI/pickyour.ai#68](https://github.com/Pick-Your-AI/pickyour.ai/issues/68); Apple placement is [Pick-Your-AI/pickyour.ai#184](https://github.com/Pick-Your-AI/pickyour.ai/issues/184), service integration [Pick-Your-AI/pickyour.ai#185](https://github.com/Pick-Your-AI/pickyour.ai/issues/185). Neither platform prompt approves a framework. Keep runtime code out of research. The website remains static unless a separately accepted architecture decision changes its boundary; a static host is not a stateful write API.

For every prerequisite record the exact consumed artifact, revision, availability, required acceptance stage and receiving review. Preserve native parents and legitimate blockers. An edge gates its named output, not unrelated upstream UI/store delivery or automatic closure of an entire program. Information handoffs and compatibility relationships remain links; do not create blanket blockers or cycles. Preparation and synthetic harnesses may proceed only within the issue's authority and without claiming final integration. Continue independent authorized work while an external input is pending.

Reuse one canonical implementation for shared outputs. Apple epics 03–05 and shared portions of 09–12/17 deliver Apple requirements, adapters and receiving acceptance, not a competing backend. Android service slices extend the canonical website coordination points rather than replacing their owners or parents:

| Canonical authority | Required handoff |
| --- | --- |
| [Pick-Your-AI/pickyour.ai#15](https://github.com/Pick-Your-AI/pickyour.ai/issues/15) | Reviewed real catalog/pricebook publication, manifest identity and client promotion acceptance |
| [Pick-Your-AI/pickyour.ai#16](https://github.com/Pick-Your-AI/pickyour.ai/issues/16) | Qualified resource/capacity artifacts and read API; no guessed fit result |
| [Pick-Your-AI/pickyour.ai#17](https://github.com/Pick-Your-AI/pickyour.ai/issues/17) | Canonical saved/shared lifecycle and authorization services; client-specific acceptance remains separate |
| [Pick-Your-AI/pickyour.ai#18](https://github.com/Pick-Your-AI/pickyour.ai/issues/18) | Canonical display labels and identifiers |
| [Pick-Your-AI/pick-your-ai-research#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40) | Versioned contract and compatibility changes, migration impact and affected-owner review |
| [Pick-Your-AI/pick-your-ai-research#41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41) | Evidence grades, freshness and correction policy |
| [Pick-Your-AI/pick-your-ai-research#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39) | Pricing units, coverage, decimal arithmetic and uncertainty |
| [Pick-Your-AI/pick-your-ai-research#42](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42) | Draft/snapshot, revision, sharing and revalidation semantics |
| [Pick-Your-AI/pick-your-ai-research#60](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60) | Exact source-use rights for display, offline caching, export and redistribution |

Refresh these authorities and actual accepted outputs at intake; their existence or a merged partial research PR is not acceptance. Preserve frozen v1 in full, including generators and fixtures. Proposed successor semantics require central review, explicit versioning and coordinated client migration; never patch generated schemas alone. Catalog proposals describe component facts, not user selections. Rates belong in Pricebooks. Unknown compatibility is not pass, unknown pricing is not zero, a partial subtotal is not a complete total, and fixture parity is not measured quality or capacity. Unsupported meters or representation gaps stay explicit. Synthetic fixtures stay under tests or the existing contract examples; do not alter the frozen import or promote fixtures as real data. A research merge is not production publication.

Keep T3–T5 optional per build and release decision. Preserve core T6 evidence, cost coverage, guardrail/evaluation guidance, deployment prerequisites and readiness even when optional breadth is deferred. Accounts, purchases, alerts, community, runtime execution and additional platforms require their existing decisions. Guest remote writes still need server-enforced authority. Publication grants no paid resources, outreach, provisioning, deployment or app publication authority; check the actual execution mandate before those actions. Never expose credentials, private builds or customer content in public evidence.

## Implement and validate the selected slice

Follow the epic's actual work packages and the platform acceptance requirements. Record the approved destination first. Android acceptance paths in the index are intended files in the application repository, not existing research files. Apple issues name outputs and defer their location to the placement decision: retain that unresolved state until accepted, then link the chosen acceptance record from the issue. Do not silently invent a path or move a research decision record.

For each criterion maintain an acceptance table in the designated record:

| Criterion from live issue | Artifact/commit and pinned inputs | Check and observed result | Failure/recovery result | Receiving review | Remaining gap |
| --- | --- | --- | --- | --- | --- |
| Exact criterion text | Actual evidence only | Passed / failed / unexecuted, with command or replay | Actual result or unverified | Review URL and disposition, or pending | Named input/decision/access condition |

Implement a bounded reviewable slice using existing modules/services. Test behavior and failure recovery: persistence acknowledgment, migrations, network interruption, stale results, malformed input, cross-identity denial, source/version locks and accessibility as applicable. Do not replace issue-specific checks with generic build success. Use the chosen framework's current primary documentation; record access date, toolchain/OS/store version and applicability. Do not treat historical target SDK or store-testing numbers in issues as evergreen requirements: verify them at implementation and release, and reconcile drift without dropping the criterion.

Run the destination repository's required checks and retain commands/results. Research changes require Python 3.12 and all commands in RESEARCH_WORKFLOW.md. Automation checks structure and contract integrity; manual review must assess prompt coherence, source claims, rights, freshness, device behavior and receiving acceptance. Do not infer these from green tests. Large artifacts stay external with sanitized evidence manifests and authorized stable access.

## Receiving review and PR delivery

For each handoff record producer issue and live owner, consumer issue and live owner, exact artifact/version, interface/fields, known gaps, requested review and acceptance receipt. Role names in the index are review needs, not assigned people. Reconcile interface changes with affected web, Android, Apple, service and research owners. A client integration cannot close the canonical shared issue by itself.

Use an isolated branch/worktree, scoped staging and repository-required signing. Preserve unrelated work. Open a PR with fully qualified issue references, behavior changes, evidence, checks and outstanding criteria. Use partial references until the entire issue can close; do not use closing keywords for prompt publication. Request the required receiving/CODEOWNERS review without inventing a reviewer when intake is unfilled. Resolve review findings and respect required checks, reviews, protections and owner holds. Merge only when both the execution mandate and repository gates allow it; a commit/push-only mandate stops at the published PR. After an authorized merge verify the default-branch artifact before reconciling acceptance.

Inspect automatic side effects before qualifying a merge: the website contributor guide states that merging to main deploys production. Such a merge therefore needs the applicable deployment authority as well as merge authority. Preserve operations-owned files and request their owner’s changes through the existing handoff instead of editing them under a client assignment.

## Triage and completion

Both mobile Projects currently use the vocabulary below; [project-fields.json](project-fields.json) preserves each separate field ID/option set. Refresh before writing and use that Project's IDs, never research Project vocabulary or another Project's matching labels.

| Field | Vocabulary and meaning |
| --- | --- |
| Status | Backlog, Ready, In Progress, In Review, Blocked, Done. Active implementation evidence is required for In Progress; publishing guidance changes none of these. |
| Readiness | Needs owner: missing accountable assignee. Needs input: named output needed. Awaiting decision: explicit unresolved choice and decision authority/intake. Blocked: evidenced stopped attempt, denied access or permission, not every future prerequisite. Ready: owner, sufficient scope and available required inputs. Record all gaps even if only one value is displayed. |
| Priority | P0 foundation, P1 core delivery, P2 optional breadth, P3 conditional growth; sequencing, not estimates. Preserve live values. |
| Phase | Discovery, Foundation, Preview alpha, Real-data beta, Launch, Operations, Expansion; guidance, not a strict waterfall or schedule. |
| Level | Program, Epic, Feature. Feature includes independently reviewable feature/task packages. Small steps remain checklists. |
| Workstream | Platform-specific full labels for Program and 01–18; consult the field snapshot and refresh live. |
| Acceptance Gate | Decision accepted, Prototype verified, Production evidence accepted, Integrated behavior verified, Release verified, Operational readiness, Scope approval. Scope approval is entry permission for conditional implementation, not behavioral completion. |

Before any authorized issue/Project mutation, reread, preserve unrelated text/labels/assignees/fields/native relationships, reconcile concurrent edits and verify readback. A merged partial PR is not Done. Close a work package only after all applicable criteria, accepted scope dispositions and receiving reviews are evidenced. Epic completion additionally requires its integrated outcome; program completion additionally requires the installed release and operations criteria. Deferred work stays explicitly deferred, never implemented by assertion.

Keep separate evidence states for local build, simulator/emulator test, physical device, staging integration, signed candidate, beta distribution, store submission, store approval, authorized release, installed production verification and operational readiness. Each needs its own artifact identity and receipt. Do not infer downstream states from upstream success.

End each execution with issue-by-issue outcome, actual artifact/PR/merge state, criterion coverage, test versus manual evidence, handoff dispositions, verified Project state and precise blockers with the smallest remaining maintainer action. Complete independent authorized work before reporting external gates. Never mark an unperformed check passed or infer a publication from a rendered UI.
