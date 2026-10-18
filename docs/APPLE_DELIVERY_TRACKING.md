# Apple/iOS delivery tracking and triage

Mobile planning issues now live in `Pick-Your-AI/pick-your-ai-android` and `Pick-Your-AI/pick-your-ai-apple`. See the [migration record](../prompts/mobile/MIGRATION.md). Repository creation resolves location only; framework, modules and service placement remain gated. Existing acceptance-record paths are preserved. Historical snapshots below do not override the live migration.

[Project #5](https://github.com/orgs/Pick-Your-AI/projects/5) ·
[Program Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) ·
[Delivery plan](APPLE_DELIVERY_PLAN.md)

Publication snapshot: 2026-10-17 UTC. GitHub is authoritative for mutable status,
ownership, release scope and native relationships. This index records structure and
review decisions, not a second delivery tracker. Refresh the project before acting.

## Review coverage and disposition

All 129 issues were individually reviewed: 1 program, 18 epics and 110 features/tasks.
Their existing 128 parent-child relationships are retained. Small implementation
steps remain checklists; no additional issue was justified after the review, and no
duplicate or completed Apple outcome was evidenced. Every issue remains open.

The review keeps existing titles and stable `IOS-XX.YY` coordinates (epics `IOS-XX`,
program `IOS-PROGRAM`). Earlier unpadded documentation coordinates are aliases, not
new work. Product T0-T6 tiers are distinct from Program/Epic/Feature delivery levels.

Every feature now names its produced artifact, receiving review roles, decision
coordination issue, issue-specific negative/recovery case and completion boundary.
Each native prerequisite names the consumed output and whether implementation,
integration or release acceptance needs it; preliminary design/fixtures may proceed.
Epics require their specific integrated outcomes rather than generic child closure.
The [per-issue review ledger](delivery/apple/triage-2026-10-17.json) retains all 129
review dispositions, body hashes, label/field deltas and dependency changes.

## Metadata conventions

All 19 existing fields and their options are retained. Status stays Backlog until
execution evidence exists; no implementation or release is marked complete.
Readiness is independent: Needs owner when ownership alone prevents intake, Needs
input for missing named deliverables, Awaiting decision for an explicit unresolved
choice, and Blocked for an evidenced obstacle. Ready requires sufficient decisions,
inputs and an accountable assignee. All 129 Apple issues lack assignees at this
snapshot, including items displaying another readiness condition. No owner, date,
estimate or milestone was invented. **There is no fully Ready work at this snapshot.**

Priority uses release necessity, fan-out, user value and risk: P0 foundations and
security boundaries; P1 core journeys, core T6 guidance, release and operating needs;
P2 optional tier breadth; P3 separately approved expansion. Each issue explains its
rationale. Shared-service foundation/authorization integration Pick-Your-AI/pick-your-ai-apple#44/Pick-Your-AI/pick-your-ai-apple#50 is P0;
core T6 Pick-Your-AI/pick-your-ai-apple#95/Pick-Your-AI/pick-your-ai-apple#96 is P1. Contract integration completes at Integrated behavior verified,
not Decision accepted. Conditional epic Pick-Your-AI/pick-your-ai-apple#19 and implementation Pick-Your-AI/pick-your-ai-apple#124-Pick-Your-AI/pick-your-ai-apple#129 still needs verified
behavior after scope approval; scope approval alone cannot close those issues.

Reused labels: `epic`, `enhancement`, `question`, `area:ios`, `area:data`, `area:ci`,
`area:catalog`, `area:builder`, `accessibility`. Two new cross-cutting labels are
defined: `security` (security/privacy/abuse/vulnerability-response deliverables),
`optional capability` (conditional inclusion requiring a recorded scope decision,
independent of priority). No status/priority/workstream labels were added. An issue
with both mandatory and optional branches is not labeled wholly optional.

Phases are sequencing guidance: preparation starts early, while actual staging,
device or store acceptance waits for the stated output. Signing/team/policy setup is
Foundation; TestFlight is Real-data beta; account/sync/link/adversarial integration
is Real-data beta. Core local forks remain Preview alpha. No schedule is implied.

## Native dependency corrections

The baseline has 213 Apple prerequisite edges. The review removes 8 and adds 17,
leaving 222. Shared-output prerequisites remain distinct from Android UI delivery.
No epic-wide blocker was added. The complete organization graph is checked across
technical research, market, web, Android and Apple, not only the Apple subgraph.

| Removed consumer ← prerequisite | Reason / retained context |
| --- | --- |
| Pick-Your-AI/pick-your-ai-apple#38 ← Pick-Your-AI/pick-your-ai-android#22 | Android use matrix does not gate independent Apple rights applicability; reuse exact accepted research Pick-Your-AI/pick-your-ai-research#41/Pick-Your-AI/pick-your-ai-research#60 rows. |
| Pick-Your-AI/pick-your-ai-apple#40 ← Pick-Your-AI/pick-your-ai-apple#38 | Rights already arrives through Pick-Your-AI/pick-your-ai-apple#39; retain the requirement in acceptance. |
| Pick-Your-AI/pick-your-ai-apple#43 ← Pick-Your-AI/pick-your-ai-apple#41 | Published release arrives through Pick-Your-AI/pick-your-ai-apple#42; preserve the manifest requirement. |
| Pick-Your-AI/pick-your-ai-apple#75 ← Pick-Your-AI/pick-your-ai-apple#70 | Evaluator output arrives through Pick-Your-AI/pick-your-ai-apple#71. |
| Pick-Your-AI/pick-your-ai-apple#84 ← Pick-Your-AI/pick-your-ai-apple#90 | Conflict service gates selected cross-device continuity, not independent local/shared-snapshot forking. |
| Pick-Your-AI/pick-your-ai-apple#97 ← Pick-Your-AI/pick-your-ai-apple#92/Pick-Your-AI/pick-your-ai-apple#93/Pick-Your-AI/pick-your-ai-apple#94 | Optional T3-T5 branches follow Pick-Your-AI/pick-your-ai-apple#21 scope disposition; omitted tiers cannot block core verification. |

Added dependencies cover shared hosting ADR Pick-Your-AI/pick-your-ai-android#35 → Apple integration ADR Pick-Your-AI/pick-your-ai-apple#23;
account/authority decision Pick-Your-AI/pick-your-ai-apple#24 → API integration Pick-Your-AI/pick-your-ai-apple#34; authorization Pick-Your-AI/pick-your-ai-apple#50 → build
and share adapters Pick-Your-AI/pick-your-ai-apple#46/Pick-Your-AI/pick-your-ai-apple#48; pricing service Pick-Your-AI/pick-your-ai-apple#47 → rate selection Pick-Your-AI/pick-your-ai-apple#76; signing
Pick-Your-AI/pick-your-ai-apple#114 → Universal Links Pick-Your-AI/pick-your-ai-apple#85; threat model Pick-Your-AI/pick-your-ai-apple#98 → disclosures/policy Pick-Your-AI/pick-your-ai-apple#101/Pick-Your-AI/pick-your-ai-apple#113;
platform identity Pick-Your-AI/pick-your-ai-apple#22 → team setup Pick-Your-AI/pick-your-ai-apple#112; real-data, policy, resilience and device
evidence Pick-Your-AI/pick-your-ai-apple#43/Pick-Your-AI/pick-your-ai-apple#113/Pick-Your-AI/pick-your-ai-apple#106/Pick-Your-AI/pick-your-ai-apple#107 → final TestFlight acceptance Pick-Your-AI/pick-your-ai-apple#115; working support Pick-Your-AI/pick-your-ai-apple#122
→ store package Pick-Your-AI/pick-your-ai-apple#116; and ongoing data/support/compatibility readiness
Pick-Your-AI/pick-your-ai-apple#121/Pick-Your-AI/pick-your-ai-apple#122/Pick-Your-AI/pick-your-ai-apple#123 → launch Pick-Your-AI/pick-your-ai-apple#117. Bodies explain exact consumed outputs and preparation.

Accounts remain conditional: launch Pick-Your-AI/pick-your-ai-apple#117 must accept Pick-Your-AI/pick-your-ai-apple#100 deletion evidence if
accounts are included, or record the Pick-Your-AI/pick-your-ai-apple#24 exclusion. It is not an unconditional
native blocker. Conditional continuity and T3-T5 evidence are handled similarly.
Server/data rollback is distinct from installed-client containment and forward-fix;
no assumption that a released App Store binary can be remotely downgraded is allowed.

## Shared output ownership and implementation overlap

No shared issue was reparented, reassigned, closed or retagged. Canonical delivery
slices keep their existing Android parents; Apple consumes the named shared subset,
not full Android completion. None of these implementation slices has an accountable
assignee at this snapshot. Research owners remain decision owners, not assumed
service implementers. Agree the service/data owner through Pick-Your-AI/pick-your-ai-apple#23 and Pick-Your-AI/pick-your-ai-apple#25.

| Canonical obligation / delivery slice | Apple acceptance |
| --- | --- |
| Research Pick-Your-AI/pick-your-ai-research#40 / application Pick-Your-AI/pick-your-ai-android#36 versioned API | Pick-Your-AI/pick-your-ai-apple#34 |
| Research Pick-Your-AI/pick-your-ai-research#41/Pick-Your-AI/pick-your-ai-research#60 source-use policy; Pick-Your-AI/pick-your-ai-android#22 Android use matrix is context | Pick-Your-AI/pick-your-ai-apple#38 Apple display/cache/export matrix |
| Website Pick-Your-AI/pickyour.ai#15 / Pick-Your-AI/pick-your-ai-android#28 normalization, Pick-Your-AI/pick-your-ai-android#38 promotion, Pick-Your-AI/pick-your-ai-android#50 immutable publication, Pick-Your-AI/pick-your-ai-android#39 corrections, Pick-Your-AI/pick-your-ai-android#60 supported slice | Pick-Your-AI/pick-your-ai-apple#39-Pick-Your-AI/pick-your-ai-apple#43 |
| Website Pick-Your-AI/pickyour.ai#15 / Pick-Your-AI/pick-your-ai-android#51 service foundation, Pick-Your-AI/pick-your-ai-android#61 discovery | Pick-Your-AI/pick-your-ai-apple#44/Pick-Your-AI/pick-your-ai-apple#45 |
| Website Pick-Your-AI/pickyour.ai#17 and research Pick-Your-AI/pick-your-ai-research#42 / Pick-Your-AI/pick-your-ai-android#78 lifecycle, Pick-Your-AI/pick-your-ai-android#95 sharing | Pick-Your-AI/pick-your-ai-apple#46/Pick-Your-AI/pick-your-ai-apple#48 |
| Research Pick-Your-AI/pick-your-ai-research#39 and website Pick-Your-AI/pickyour.ai#17 / Pick-Your-AI/pick-your-ai-android#94 evaluation/pricing | Pick-Your-AI/pick-your-ai-apple#47 and Pick-Your-AI/pick-your-ai-apple#76-Pick-Your-AI/pick-your-ai-apple#79 |
| Website Pick-Your-AI/pickyour.ai#16; research Pick-Your-AI/pick-your-ai-research#10/Pick-Your-AI/pick-your-ai-research#36 / Pick-Your-AI/pick-your-ai-android#79 capacity/quality reads | Pick-Your-AI/pick-your-ai-apple#49/Pick-Your-AI/pick-your-ai-apple#73 |
| Website Pick-Your-AI/pickyour.ai#17 / Pick-Your-AI/pick-your-ai-android#62 authorization, Pick-Your-AI/pick-your-ai-android#63 security controls | Pick-Your-AI/pick-your-ai-apple#50/Pick-Your-AI/pick-your-ai-apple#51 |
| Website Pick-Your-AI/pickyour.ai#18 / research Pick-Your-AI/pick-your-ai-research#40 display labels | Pick-Your-AI/pick-your-ai-apple#32/Pick-Your-AI/pick-your-ai-apple#58 |

Application repository `main` contains React/TypeScript, no native Apple/Android
application or backend deployment. [PR #9](https://github.com/Pick-Your-AI/pickyour.ai/pull/9)
supplies generated web models, validators, evaluator and provider adapters;
[PR #13](https://github.com/Pick-Your-AI/pickyour.ai/pull/13) supplies builder/catalog,
local library and fragment-share preview. The HTTP resource provider explicitly
returns unavailable; remote build list/delete still use local index/removal. These
are exact reuse references and remaining gaps, not deployed backend proof.
[PR #30](https://github.com/Pick-Your-AI/pickyour.ai/pull/30) fixes the empty workload
step; [#29](https://github.com/Pick-Your-AI/pickyour.ai/pull/29) adds blocking dependency
review. Preserve those web checks when adding macOS CI.

The PR inventory includes all open, closed and merged PRs in all three organization
repositories. No open application implementation PR exists at this snapshot.
Merged research Pick-Your-AI/pick-your-ai-research#100-Pick-Your-AI/pick-your-ai-research#105 contains partial evidence/reconciliation; it does not
establish production publication or accepted executable policy. Open research
PRs Pick-Your-AI/pick-your-ai-research#69-Pick-Your-AI/pick-your-ai-research#73, Pick-Your-AI/pick-your-ai-research#81 and Pick-Your-AI/pick-your-ai-research#83 have Changes requested despite green structural validation:
T4 provenance/summary consistency, workload resident-sequence sizing, and benchmark
uncertainty claims need reviewer disposition. Updated commits require re-review;
the old review is not proof the current head remains defective. Pick-Your-AI/pick-your-ai-research#74 is open with
green validation and review comments but no recorded approval decision. These are
bounded input-review gaps, not blanket blockers on unrelated Apple preparation.

## Apple policy and release applicability

Official sources checked on 2026-10-17 UTC:

- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/): selected login, commerce, sharing/content, privacy and review-access obligations.
- [Submission guidance](https://developer.apple.com/app-store/submitting/): SDK/submission and store package requirements; recheck at implementation and submission.
- [Third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/): applicable SDK privacy/signature requirements.
- [Account deletion](https://developer.apple.com/help/app-review/guideline-reference/5-1-1-account-deletion): selected account lifecycle applicability.
- [TestFlight](https://developer.apple.com/testflight/): internal/external distribution, beta review and feedback.

Pick-Your-AI/pick-your-ai-apple#113 owns the dated applicability/evidence matrix; Pick-Your-AI/pick-your-ai-apple#21 selects release scope,
Pick-Your-AI/pick-your-ai-apple#22 framework/OS/repository placement, Pick-Your-AI/pick-your-ai-apple#23 hosting, Pick-Your-AI/pick-your-ai-apple#24 accounts/analytics/commerce,
Pick-Your-AI/pick-your-ai-apple#25 review roles/gates. All remain open/unassigned. No SDK number, monetary price,
purchase exception, source-use permission or supported stack is invented. Optional
alerts, commerce, public community, personalization, execution and other markets or
Apple platforms stay disabled until their explicit scope and behavioral gates pass.
This triage does not implement, provision, contact participants, deploy or submit.

## First intake and maintainer actions

Assign accountable decision/review roles through Pick-Your-AI/pick-your-ai-apple#25 without waiting to finish the
whole scope matrix; accept the final gates only after Pick-Your-AI/pick-your-ai-apple#21. First P0 intake is
Pick-Your-AI/pick-your-ai-apple#20 journey/evidence mapping and Pick-Your-AI/pick-your-ai-apple#98 threat/data inventory, which have no native
execution prerequisites. Pick-Your-AI/pick-your-ai-apple#38 source-use applicability can also start independently.
Then resolve Pick-Your-AI/pick-your-ai-apple#21-Pick-Your-AI/pick-your-ai-apple#24 scope/platform/hosting/identity, followed by Pick-Your-AI/pick-your-ai-apple#26 toolchain,
Pick-Your-AI/pick-your-ai-apple#32 contracts, Pick-Your-AI/pick-your-ai-apple#30 macOS CI and Pick-Your-AI/pick-your-ai-apple#86 durable storage. Access/signing evidence from
Pick-Your-AI/pick-your-ai-apple#112/Pick-Your-AI/pick-your-ai-apple#114 needs authorized Apple maintainers; no team permissions were changed here.
No work is marked Ready until ownership and its exact inputs are available.

## Validation boundaries

Complete pagination covers all 329 organization issues, 62 PRs and all five project
memberships (37/20/16/129/129); nested collections were checked for additional pages.
Readback compares every Apple body, label set, field, parent, child and prerequisite
to the planned result, preserves assignees/milestones/states, and checks unique
coordinates, link targets, graph direction/cycles and unrelated shared metadata.
Views retain an unfiltered hierarchy and visible parent/sub-issue fields; focused
filters use actual options. The release view includes workstream 16/17 even when
setup moved earlier, and the Apple-experience view includes tier workstream 13.

Python 3.12 validation: 21 contract tests, 24 repository tests and research intake
validation pass (30 catalog proposals, 2 pricebooks). Market integrity also passes
(33 entities, 1,584 cells and 20 issues). Frozen import hashes and
generator consistency pass. These checks establish structural consistency, not
source rights, real prices, physical-device behavior, deployment, App Store approval
or production release. Behavioral evidence remains a delivery requirement.

Documentation PR Pick-Your-AI/pick-your-ai-android#66 merged at `f1d9148f2fef82a57e698dd5d91b92e7b495dfdc`;
its current file list contained the plan but no tracking index. This update adds
that index and removes obsolete proposal-only and branch-specific links.

## Verified mutation readback

At 2026-10-17T02:33:55.111757+00:00, all 129 revised bodies and label sets, all 7 select fields per
item, 128 native parents and 222 prerequisite sets matched live readback. There were
113 label-set revisions and 42 select-value changes across 37 issues. Ownership,
milestones, issue states and unrelated Projects Pick-Your-AI/pickyour.ai#1-Pick-Your-AI/pickyour.ai#4 were unchanged. All 245 distinct
issue/PR hyperlink targets resolved against the complete live inventory. Referenced
contract schema files resolve in the frozen local import.

The organization graph contains 329 nodes and 435 prerequisite edges: zero cycles,
self-dependencies or missing targets; inverse blocking directions also match. The
15 distinct shared-output targets retain their original metadata and parents.
Current Readiness: 21 Needs owner, 94 Needs input, 14 Awaiting decision, zero Ready.
These are timestamped observations and must be refreshed for future execution.

Server-side queries of the actual saved view filters return, in view order,
129 / 21 / 129 / 108 / 60 / 42 / 16 / 14 / 11 issues. All 9 views expose Title,
Parent issue, Sub-issues progress and Labels. Existing Workstream grouping is
preserved in focused tables. The hierarchy view has no filter and contains all 129
items. Filter membership and configuration were checked through GitHub's API;
browser rendering, Apple Developer access and real-device behavior were not audited.

The recoverable before-state, mutation receipts and final readbacks are retained in
the task's local `apple-triage` recovery archive. The public JSON ledger contains
per-issue before/after hashes and all applied metadata/dependency deltas; it does not
include credentials, private customer data, raw research datasets or large downloads.

## Issue index

Native GitHub relationships remain authoritative. Every item below belongs to
Project #5; shared prerequisites keep their original project membership.

| Coordinate | Issue | Parent |
| --- | --- | --- |
| IOS-PROGRAM | [Pick-Your-AI/pick-your-ai-apple#1 End-to-end application delivery](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) | — |
| IOS-01 | [Pick-Your-AI/pick-your-ai-apple#2 Product scope and decisions](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-02 | [Pick-Your-AI/pick-your-ai-apple#3 Apple application foundation](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/3) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-03 | [Pick-Your-AI/pick-your-ai-apple#4 Shared contracts and mobile conformance](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/4) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-04 | [Pick-Your-AI/pick-your-ai-apple#5 Research-to-production catalog pipeline](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-05 | [Pick-Your-AI/pick-your-ai-apple#6 Shared application services](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-06 | [Pick-Your-AI/pick-your-ai-apple#7 Mobile experience and design system](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-07 | [Pick-Your-AI/pick-your-ai-apple#8 Component discovery and comparison](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/8) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-08 | [Pick-Your-AI/pick-your-ai-apple#9 AI stack builder](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/9) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-09 | [Pick-Your-AI/pick-your-ai-apple#10 Compatibility and capacity](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/10) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-10 | [Pick-Your-AI/pick-your-ai-apple#11 Cost estimation](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/11) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-11 | [Pick-Your-AI/pick-your-ai-apple#12 Saved builds, comparison and sharing](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/12) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-12 | [Pick-Your-AI/pick-your-ai-apple#13 Offline storage and synchronization](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/13) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-13 | [Pick-Your-AI/pick-your-ai-apple#14 Optional tiers and operational capabilities](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/14) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-14 | [Pick-Your-AI/pick-your-ai-apple#15 Privacy, security and trust](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-15 | [Pick-Your-AI/pick-your-ai-apple#16 Quality and performance](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-16 | [Pick-Your-AI/pick-your-ai-apple#17 TestFlight, App Store delivery and launch](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-17 | [Pick-Your-AI/pick-your-ai-apple#18 Product and data operations](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/18) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-18 | [Pick-Your-AI/pick-your-ai-apple#19 Decision-dependent expansion](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) | [Pick-Your-AI/pick-your-ai-apple#1](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/1) |
| IOS-01.01 | [Pick-Your-AI/pick-your-ai-apple#20 Target users and primary iPhone and iPad journeys](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/20) | [Pick-Your-AI/pick-your-ai-apple#2](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) |
| IOS-01.02 | [Pick-Your-AI/pick-your-ai-apple#21 MVP scope and phased capabilities](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/21) | [Pick-Your-AI/pick-your-ai-apple#2](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) |
| IOS-01.03 | [Pick-Your-AI/pick-your-ai-apple#22 Apple platform scope, technology and repository structure](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/22) | [Pick-Your-AI/pick-your-ai-apple#2](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) |
| IOS-01.04 | [Pick-Your-AI/pick-your-ai-apple#23 Backend architecture and hosting](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/23) | [Pick-Your-AI/pick-your-ai-apple#2](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) |
| IOS-01.05 | [Pick-Your-AI/pick-your-ai-apple#24 Accounts and monetization decisions](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/24) | [Pick-Your-AI/pick-your-ai-apple#2](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) |
| IOS-01.06 | [Pick-Your-AI/pick-your-ai-apple#25 Acceptance criteria, ownership and release gates](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/25) | [Pick-Your-AI/pick-your-ai-apple#2](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/2) |
| IOS-02.01 | [Pick-Your-AI/pick-your-ai-apple#26 Xcode toolchain, dependencies and modules](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/26) | [Pick-Your-AI/pick-your-ai-apple#3](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/3) |
| IOS-02.02 | [Pick-Your-AI/pick-your-ai-apple#27 Preview, staging and production environments](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/27) | [Pick-Your-AI/pick-your-ai-apple#3](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/3) |
| IOS-02.03 | [Pick-Your-AI/pick-your-ai-apple#28 Navigation, lifecycle and state restoration](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/28) | [Pick-Your-AI/pick-your-ai-apple#3](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/3) |
| IOS-02.04 | [Pick-Your-AI/pick-your-ai-apple#29 UI, domain and data boundaries](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/29) | [Pick-Your-AI/pick-your-ai-apple#3](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/3) |
| IOS-02.05 | [Pick-Your-AI/pick-your-ai-apple#30 macOS continuous integration and required checks](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/30) | [Pick-Your-AI/pick-your-ai-apple#3](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/3) |
| IOS-02.06 | [Pick-Your-AI/pick-your-ai-apple#31 Clearly identified synthetic fixtures](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/31) | [Pick-Your-AI/pick-your-ai-apple#3](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/3) |
| IOS-03.01 | [Pick-Your-AI/pick-your-ai-apple#32 Adopt versioned contracts and generate models](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/32) | [Pick-Your-AI/pick-your-ai-apple#4](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/4) |
| IOS-03.02 | [Pick-Your-AI/pick-your-ai-apple#33 Separate incomplete drafts from saved snapshots](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/33) | [Pick-Your-AI/pick-your-ai-apple#4](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/4) |
| IOS-03.03 | [Pick-Your-AI/pick-your-ai-apple#34 Define required versioned API extensions](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/34) | [Pick-Your-AI/pick-your-ai-apple#4](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/4) |
| IOS-03.04 | [Pick-Your-AI/pick-your-ai-apple#35 Model component placement and relationships](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/35) | [Pick-Your-AI/pick-your-ai-apple#4](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/4) |
| IOS-03.05 | [Pick-Your-AI/pick-your-ai-apple#36 Define evidence, unknowns and rule semantics](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/36) | [Pick-Your-AI/pick-your-ai-apple#4](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/4) |
| IOS-03.06 | [Pick-Your-AI/pick-your-ai-apple#37 Cross-client conformance and migration fixtures](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/37) | [Pick-Your-AI/pick-your-ai-apple#4](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/4) |
| IOS-04.01 | [Pick-Your-AI/pick-your-ai-apple#38 Source access, display and redistribution rights](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/38) | [Pick-Your-AI/pick-your-ai-apple#5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) |
| IOS-04.02 | [Pick-Your-AI/pick-your-ai-apple#39 Normalize and validate component facts](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/39) | [Pick-Your-AI/pick-your-ai-apple#5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) |
| IOS-04.03 | [Pick-Your-AI/pick-your-ai-apple#40 Evidence review and production approval](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/40) | [Pick-Your-AI/pick-your-ai-apple#5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) |
| IOS-04.04 | [Pick-Your-AI/pick-your-ai-apple#41 Publish immutable catalog and rule releases](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/41) | [Pick-Your-AI/pick-your-ai-apple#5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) |
| IOS-04.05 | [Pick-Your-AI/pick-your-ai-apple#42 Freshness, corrections and retractions](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/42) | [Pick-Your-AI/pick-your-ai-apple#5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) |
| IOS-04.06 | [Pick-Your-AI/pick-your-ai-apple#43 Publish the first complete supported real-data path](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/43) | [Pick-Your-AI/pick-your-ai-apple#5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/5) |
| IOS-05.01 | [Pick-Your-AI/pick-your-ai-apple#44 API foundation, database and migrations](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/44) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.02 | [Pick-Your-AI/pick-your-ai-apple#45 Catalog discovery, search and delivery](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/45) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.03 | [Pick-Your-AI/pick-your-ai-apple#46 Build creation, revisions, history and deletion](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/46) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.04 | [Pick-Your-AI/pick-your-ai-apple#47 Compatibility evaluation and pricing services](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/47) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.05 | [Pick-Your-AI/pick-your-ai-apple#48 Share creation, access and revocation](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/48) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.06 | [Pick-Your-AI/pick-your-ai-apple#49 Resource estimates and quality evidence](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/49) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.07 | [Pick-Your-AI/pick-your-ai-apple#50 Authorization and optional account authentication](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/50) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.08 | [Pick-Your-AI/pick-your-ai-apple#51 Limits, auditability, secrets and recovery](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/51) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-05.09 | [Pick-Your-AI/pick-your-ai-apple#52 Integration with the existing website](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/52) | [Pick-Your-AI/pick-your-ai-apple#6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/6) |
| IOS-06.01 | [Pick-Your-AI/pick-your-ai-apple#53 Information architecture and interaction prototypes](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/53) | [Pick-Your-AI/pick-your-ai-apple#7](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) |
| IOS-06.02 | [Pick-Your-AI/pick-your-ai-apple#54 Accessible components and design tokens](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/54) | [Pick-Your-AI/pick-your-ai-apple#7](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) |
| IOS-06.03 | [Pick-Your-AI/pick-your-ai-apple#55 Adaptive iPhone and iPad layouts](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/55) | [Pick-Your-AI/pick-your-ai-apple#7](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) |
| IOS-06.04 | [Pick-Your-AI/pick-your-ai-apple#56 Builder guidance and understandable status labels](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/56) | [Pick-Your-AI/pick-your-ai-apple#7](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) |
| IOS-06.05 | [Pick-Your-AI/pick-your-ai-apple#57 Loading, empty, offline and failure states](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/57) | [Pick-Your-AI/pick-your-ai-apple#7](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) |
| IOS-06.06 | [Pick-Your-AI/pick-your-ai-apple#58 Themes, localization, units and presentation](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/58) | [Pick-Your-AI/pick-your-ai-apple#7](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/7) |
| IOS-07.01 | [Pick-Your-AI/pick-your-ai-apple#59 Browse, search, filter and sort the catalog](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/59) | [Pick-Your-AI/pick-your-ai-apple#8](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/8) |
| IOS-07.02 | [Pick-Your-AI/pick-your-ai-apple#60 Compatibility-aware component picker](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/60) | [Pick-Your-AI/pick-your-ai-apple#8](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/8) |
| IOS-07.03 | [Pick-Your-AI/pick-your-ai-apple#61 Component details, conditions and evidence](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/61) | [Pick-Your-AI/pick-your-ai-apple#8](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/8) |
| IOS-07.04 | [Pick-Your-AI/pick-your-ai-apple#62 Side-by-side component comparison](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/62) | [Pick-Your-AI/pick-your-ai-apple#8](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/8) |
| IOS-07.05 | [Pick-Your-AI/pick-your-ai-apple#63 Select components from search and deep links](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/63) | [Pick-Your-AI/pick-your-ai-apple#8](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/8) |
| IOS-08.01 | [Pick-Your-AI/pick-your-ai-apple#64 Workload, constraints and deployment inputs](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/64) | [Pick-Your-AI/pick-your-ai-apple#9](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/9) |
| IOS-08.02 | [Pick-Your-AI/pick-your-ai-apple#65 Model and infrastructure selection](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/65) | [Pick-Your-AI/pick-your-ai-apple#9](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/9) |
| IOS-08.03 | [Pick-Your-AI/pick-your-ai-apple#66 Enable and disable optional tiers](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/66) | [Pick-Your-AI/pick-your-ai-apple#9](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/9) |
| IOS-08.04 | [Pick-Your-AI/pick-your-ai-apple#67 Edit component settings and build objectives](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/67) | [Pick-Your-AI/pick-your-ai-apple#9](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/9) |
| IOS-08.05 | [Pick-Your-AI/pick-your-ai-apple#68 Persistent summary and suggested next steps](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/68) | [Pick-Your-AI/pick-your-ai-apple#9](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/9) |
| IOS-08.06 | [Pick-Your-AI/pick-your-ai-apple#69 Undo, autosave and revision restoration](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/69) | [Pick-Your-AI/pick-your-ai-apple#9](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/9) |
| IOS-09.01 | [Pick-Your-AI/pick-your-ai-apple#70 Integrate the governed evaluator](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/70) | [Pick-Your-AI/pick-your-ai-apple#10](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/10) |
| IOS-09.02 | [Pick-Your-AI/pick-your-ai-apple#71 Recheck affected components after changes](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/71) | [Pick-Your-AI/pick-your-ai-apple#10](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/10) |
| IOS-09.03 | [Pick-Your-AI/pick-your-ai-apple#72 Explain findings and possible fixes](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/72) | [Pick-Your-AI/pick-your-ai-apple#10](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/10) |
| IOS-09.04 | [Pick-Your-AI/pick-your-ai-apple#73 Consume qualified capacity estimates](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/73) | [Pick-Your-AI/pick-your-ai-apple#10](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/10) |
| IOS-09.05 | [Pick-Your-AI/pick-your-ai-apple#74 Suggest alternatives with stated tradeoffs](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/74) | [Pick-Your-AI/pick-your-ai-apple#10](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/10) |
| IOS-09.06 | [Pick-Your-AI/pick-your-ai-apple#75 Handle stale and out-of-order results](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/75) | [Pick-Your-AI/pick-your-ai-apple#10](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/10) |
| IOS-10.01 | [Pick-Your-AI/pick-your-ai-apple#76 Select applicable dated rates](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/76) | [Pick-Your-AI/pick-your-ai-apple#11](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/11) |
| IOS-10.02 | [Pick-Your-AI/pick-your-ai-apple#77 Calculate costs from explicit usage scenarios](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/77) | [Pick-Your-AI/pick-your-ai-apple#11](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/11) |
| IOS-10.03 | [Pick-Your-AI/pick-your-ai-apple#78 Show missing costs, coverage and uncertainty](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/78) | [Pick-Your-AI/pick-your-ai-apple#11](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/11) |
| IOS-10.04 | [Pick-Your-AI/pick-your-ai-apple#79 Compare scenarios and preserve price provenance](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/79) | [Pick-Your-AI/pick-your-ai-apple#11](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/11) |
| IOS-11.01 | [Pick-Your-AI/pick-your-ai-apple#80 Local build library](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/80) | [Pick-Your-AI/pick-your-ai-apple#12](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/12) |
| IOS-11.02 | [Pick-Your-AI/pick-your-ai-apple#81 Compare complete builds and revisions](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/81) | [Pick-Your-AI/pick-your-ai-apple#12](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/12) |
| IOS-11.03 | [Pick-Your-AI/pick-your-ai-apple#82 Safe import and export](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/82) | [Pick-Your-AI/pick-your-ai-apple#12](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/12) |
| IOS-11.04 | [Pick-Your-AI/pick-your-ai-apple#83 Read-only shared builds with pinned evidence](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/83) | [Pick-Your-AI/pick-your-ai-apple#12](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/12) |
| IOS-11.05 | [Pick-Your-AI/pick-your-ai-apple#84 Fork builds and optional cross-device continuity](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/84) | [Pick-Your-AI/pick-your-ai-apple#12](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/12) |
| IOS-11.06 | [Pick-Your-AI/pick-your-ai-apple#85 Universal Links, associated domains and browser fallback](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/85) | [Pick-Your-AI/pick-your-ai-apple#12](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/12) |
| IOS-12.01 | [Pick-Your-AI/pick-your-ai-apple#86 Durable local database and migrations](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/86) | [Pick-Your-AI/pick-your-ai-apple#13](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/13) |
| IOS-12.02 | [Pick-Your-AI/pick-your-ai-apple#87 Cached catalogs and offline draft editing](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/87) | [Pick-Your-AI/pick-your-ai-apple#13](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/13) |
| IOS-12.03 | [Pick-Your-AI/pick-your-ai-apple#88 Atomic refresh and background scheduling](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/88) | [Pick-Your-AI/pick-your-ai-apple#13](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/13) |
| IOS-12.04 | [Pick-Your-AI/pick-your-ai-apple#89 Queued writes and retry reconciliation](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/89) | [Pick-Your-AI/pick-your-ai-apple#13](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/13) |
| IOS-12.05 | [Pick-Your-AI/pick-your-ai-apple#90 Conflict resolution without lost edits](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/90) | [Pick-Your-AI/pick-your-ai-apple#13](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/13) |
| IOS-12.06 | [Pick-Your-AI/pick-your-ai-apple#91 Logout, deletion and unavailable-version handling](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/91) | [Pick-Your-AI/pick-your-ai-apple#13](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/13) |
| IOS-13.01 | [Pick-Your-AI/pick-your-ai-apple#92 Knowledge and retrieval configuration — T3](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/92) | [Pick-Your-AI/pick-your-ai-apple#14](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/14) |
| IOS-13.02 | [Pick-Your-AI/pick-your-ai-apple#93 Agents, tools, MCP and memory — T4](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/93) | [Pick-Your-AI/pick-your-ai-apple#14](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/14) |
| IOS-13.03 | [Pick-Your-AI/pick-your-ai-apple#94 Training and fine-tuned models — T5](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/94) | [Pick-Your-AI/pick-your-ai-apple#14](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/14) |
| IOS-13.04 | [Pick-Your-AI/pick-your-ai-apple#95 Guardrails and evaluation guidance — T6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/95) | [Pick-Your-AI/pick-your-ai-apple#14](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/14) |
| IOS-13.05 | [Pick-Your-AI/pick-your-ai-apple#96 Deployment plans and monitoring choices — T6](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/96) | [Pick-Your-AI/pick-your-ai-apple#14](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/14) |
| IOS-13.06 | [Pick-Your-AI/pick-your-ai-apple#97 Validate supported combinations across tiers](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/97) | [Pick-Your-AI/pick-your-ai-apple#14](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/14) |
| IOS-14.01 | [Pick-Your-AI/pick-your-ai-apple#98 Data inventory and threat model](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/98) | [Pick-Your-AI/pick-your-ai-apple#15](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) |
| IOS-14.02 | [Pick-Your-AI/pick-your-ai-apple#99 Keychain, data protection and secure networking](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/99) | [Pick-Your-AI/pick-your-ai-apple#15](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) |
| IOS-14.03 | [Pick-Your-AI/pick-your-ai-apple#100 Account and associated-data lifecycle, if included](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/100) | [Pick-Your-AI/pick-your-ai-apple#15](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) |
| IOS-14.04 | [Pick-Your-AI/pick-your-ai-apple#101 Privacy disclosures and third-party SDK controls](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/101) | [Pick-Your-AI/pick-your-ai-apple#15](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) |
| IOS-14.05 | [Pick-Your-AI/pick-your-ai-apple#102 Adversarial testing of sharing, imports and APIs](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/102) | [Pick-Your-AI/pick-your-ai-apple#15](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) |
| IOS-14.06 | [Pick-Your-AI/pick-your-ai-apple#103 Dependency security and vulnerability response](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/103) | [Pick-Your-AI/pick-your-ai-apple#15](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/15) |
| IOS-15.01 | [Pick-Your-AI/pick-your-ai-apple#104 Contract and domain regression tests](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/104) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-15.02 | [Pick-Your-AI/pick-your-ai-apple#105 Apple UI and accessibility tests](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/105) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-15.03 | [Pick-Your-AI/pick-your-ai-apple#106 Network failure and recovery tests](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/106) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-15.04 | [Pick-Your-AI/pick-your-ai-apple#107 Device, OS and lifecycle test matrix](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/107) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-15.05 | [Pick-Your-AI/pick-your-ai-apple#108 Apple, Android, web and backend conformance tests](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/108) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-15.06 | [Pick-Your-AI/pick-your-ai-apple#109 Measured startup, rendering and resource budgets](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/109) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-15.07 | [Pick-Your-AI/pick-your-ai-apple#110 Security and release-build regression tests](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/110) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-15.08 | [Pick-Your-AI/pick-your-ai-apple#111 Authorized user validation and acceptance](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/111) | [Pick-Your-AI/pick-your-ai-apple#16](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/16) |
| IOS-16.01 | [Pick-Your-AI/pick-your-ai-apple#112 Apple Developer team and App Store Connect identity](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/112) | [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) |
| IOS-16.02 | [Pick-Your-AI/pick-your-ai-apple#113 Platform and store-policy requirements](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/113) | [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) |
| IOS-16.03 | [Pick-Your-AI/pick-your-ai-apple#114 Signing, provisioning, entitlements and key management](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/114) | [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) |
| IOS-16.04 | [Pick-Your-AI/pick-your-ai-apple#115 Internal and external TestFlight testing](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/115) | [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) |
| IOS-16.05 | [Pick-Your-AI/pick-your-ai-apple#116 App Store listing, screenshots and privacy declarations](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/116) | [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) |
| IOS-16.06 | [Pick-Your-AI/pick-your-ai-apple#117 Launch readiness and controlled rollout](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/117) | [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) |
| IOS-16.07 | [Pick-Your-AI/pick-your-ai-apple#118 Verify the installed production release](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/118) | [Pick-Your-AI/pick-your-ai-apple#17](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/17) |
| IOS-17.01 | [Pick-Your-AI/pick-your-ai-apple#119 Application and service monitoring](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/119) | [Pick-Your-AI/pick-your-ai-apple#18](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/18) |
| IOS-17.02 | [Pick-Your-AI/pick-your-ai-apple#120 Incident response and restore drills](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/120) | [Pick-Your-AI/pick-your-ai-apple#18](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/18) |
| IOS-17.03 | [Pick-Your-AI/pick-your-ai-apple#121 Catalog, evidence and pricing maintenance](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/121) | [Pick-Your-AI/pick-your-ai-apple#18](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/18) |
| IOS-17.04 | [Pick-Your-AI/pick-your-ai-apple#122 Support, corrections and contribution workflow](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/122) | [Pick-Your-AI/pick-your-ai-apple#18](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/18) |
| IOS-17.05 | [Pick-Your-AI/pick-your-ai-apple#123 Compatibility maintenance and release cadence](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/123) | [Pick-Your-AI/pick-your-ai-apple#18](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/18) |
| IOS-18.01 | [Pick-Your-AI/pick-your-ai-apple#124 Favorites and price/compatibility alerts](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/124) | [Pick-Your-AI/pick-your-ai-apple#19](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) |
| IOS-18.02 | [Pick-Your-AI/pick-your-ai-apple#125 Paid plans and entitlements](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/125) | [Pick-Your-AI/pick-your-ai-apple#19](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) |
| IOS-18.03 | [Pick-Your-AI/pick-your-ai-apple#126 Community build publishing and moderation](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/126) | [Pick-Your-AI/pick-your-ai-apple#19](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) |
| IOS-18.04 | [Pick-Your-AI/pick-your-ai-apple#127 Advanced recommendations and personalization](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/127) | [Pick-Your-AI/pick-your-ai-apple#19](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) |
| IOS-18.05 | [Pick-Your-AI/pick-your-ai-apple#128 Actual runtime execution or provisioning](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/128) | [Pick-Your-AI/pick-your-ai-apple#19](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) |
| IOS-18.06 | [Pick-Your-AI/pick-your-ai-apple#129 Additional markets and platforms](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/129) | [Pick-Your-AI/pick-your-ai-apple#19](https://github.com/Pick-Your-AI/pick-your-ai-apple/issues/19) |
