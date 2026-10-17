# Apple/iOS delivery tracking and triage

[Project #5](https://github.com/orgs/Pick-Your-AI/projects/5) ·
[Program #163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) ·
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
rationale. Shared-service foundation/authorization integration #206/#212 is P0;
core T6 #257/#258 is P1. Contract integration completes at Integrated behavior verified,
not Decision accepted. Conditional epic #181 and implementation #286-#291 still needs verified
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
| #200 ← #55 | Android use matrix does not gate independent Apple rights applicability; reuse exact accepted research #41/#60 rows. |
| #202 ← #200 | Rights already arrives through #201; retain the requirement in acceptance. |
| #205 ← #203 | Published release arrives through #204; preserve the manifest requirement. |
| #237 ← #232 | Evaluator output arrives through #233. |
| #246 ← #252 | Conflict service gates selected cross-device continuity, not independent local/shared-snapshot forking. |
| #259 ← #254/#255/#256 | Optional T3-T5 branches follow #183 scope disposition; omitted tiers cannot block core verification. |

Added dependencies cover shared hosting ADR #68 → Apple integration ADR #185;
account/authority decision #186 → API integration #196; authorization #212 → build
and share adapters #208/#210; pricing service #209 → rate selection #238; signing
#276 → Universal Links #247; threat model #260 → disclosures/policy #263/#275;
platform identity #184 → team setup #274; real-data, policy, resilience and device
evidence #205/#275/#268/#269 → final TestFlight acceptance #277; working support #284
→ store package #278; and ongoing data/support/compatibility readiness
#283/#284/#285 → launch #279. Bodies explain exact consumed outputs and preparation.

Accounts remain conditional: launch #279 must accept #262 deletion evidence if
accounts are included, or record the #186 exclusion. It is not an unconditional
native blocker. Conditional continuity and T3-T5 evidence are handled similarly.
Server/data rollback is distinct from installed-client containment and forward-fix;
no assumption that a released App Store binary can be remotely downgraded is allowed.

## Shared output ownership and implementation overlap

No shared issue was reparented, reassigned, closed or retagged. Canonical delivery
slices keep their existing Android parents; Apple consumes the named shared subset,
not full Android completion. None of these implementation slices has an accountable
assignee at this snapshot. Research owners remain decision owners, not assumed
service implementers. Agree the service/data owner through #185 and #187.

| Canonical obligation / delivery slice | Apple acceptance |
| --- | --- |
| Research #40 / application #69 versioned API | #196 |
| Research #41/#60 source-use policy; #55 Android use matrix is context | #200 Apple display/cache/export matrix |
| Website #15 / #61 normalization, #71 promotion, #83 immutable publication, #72 corrections, #93 supported slice | #201-#205 |
| Website #15 / #84 service foundation, #94 discovery | #206/#207 |
| Website #17 and research #42 / #111 lifecycle, #128 sharing | #208/#210 |
| Research #39 and website #17 / #127 evaluation/pricing | #209 and #238-#241 |
| Website #16; research #10/#36 / #112 capacity/quality reads | #211/#235 |
| Website #17 / #95 authorization, #96 security controls | #212/#213 |
| Website #18 / research #40 display labels | #194/#220 |

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
Merged research #100-#105 contains partial evidence/reconciliation; it does not
establish production publication or accepted executable policy. Open research
PRs #69-#73, #81 and #83 have Changes requested despite green structural validation:
T4 provenance/summary consistency, workload resident-sequence sizing, and benchmark
uncertainty claims need reviewer disposition. Updated commits require re-review;
the old review is not proof the current head remains defective. #74 is open with
green validation and review comments but no recorded approval decision. These are
bounded input-review gaps, not blanket blockers on unrelated Apple preparation.

## Apple policy and release applicability

Official sources checked on 2026-10-17 UTC:

- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/): selected login, commerce, sharing/content, privacy and review-access obligations.
- [Submission guidance](https://developer.apple.com/app-store/submitting/): SDK/submission and store package requirements; recheck at implementation and submission.
- [Third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/): applicable SDK privacy/signature requirements.
- [Account deletion](https://developer.apple.com/help/app-review/guideline-reference/5-1-1-account-deletion): selected account lifecycle applicability.
- [TestFlight](https://developer.apple.com/testflight/): internal/external distribution, beta review and feedback.

#275 owns the dated applicability/evidence matrix; #183 selects release scope,
#184 framework/OS/repository placement, #185 hosting, #186 accounts/analytics/commerce,
#187 review roles/gates. All remain open/unassigned. No SDK number, monetary price,
purchase exception, source-use permission or supported stack is invented. Optional
alerts, commerce, public community, personalization, execution and other markets or
Apple platforms stay disabled until their explicit scope and behavioral gates pass.
This triage does not implement, provision, contact participants, deploy or submit.

## First intake and maintainer actions

Assign accountable decision/review roles through #187 without waiting to finish the
whole scope matrix; accept the final gates only after #183. First P0 intake is
#182 journey/evidence mapping and #260 threat/data inventory, which have no native
execution prerequisites. #200 source-use applicability can also start independently.
Then resolve #183-#186 scope/platform/hosting/identity, followed by #188 toolchain,
#194 contracts, #192 macOS CI and #248 durable storage. Access/signing evidence from
#274/#276 needs authorized Apple maintainers; no team permissions were changed here.
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

Documentation PR #99 merged at `f1d9148f2fef82a57e698dd5d91b92e7b495dfdc`;
its current file list contained the plan but no tracking index. This update adds
that index and removes obsolete proposal-only and branch-specific links.

## Verified mutation readback

At 2026-10-17T02:33:55.111757+00:00, all 129 revised bodies and label sets, all 7 select fields per
item, 128 native parents and 222 prerequisite sets matched live readback. There were
113 label-set revisions and 42 select-value changes across 37 issues. Ownership,
milestones, issue states and unrelated Projects #1-#4 were unchanged. All 245 distinct
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
| IOS-PROGRAM | [#163 End-to-end application delivery](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) | — |
| IOS-01 | [#164 Product scope and decisions](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-02 | [#165 Apple application foundation](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-03 | [#166 Shared contracts and mobile conformance](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-04 | [#167 Research-to-production catalog pipeline](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-05 | [#168 Shared application services](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-06 | [#169 Mobile experience and design system](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-07 | [#170 Component discovery and comparison](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-08 | [#171 AI stack builder](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-09 | [#172 Compatibility and capacity](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-10 | [#173 Cost estimation](https://github.com/Pick-Your-AI/pickyour.ai/issues/173) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-11 | [#174 Saved builds, comparison and sharing](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-12 | [#175 Offline storage and synchronization](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-13 | [#176 Optional tiers and operational capabilities](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-14 | [#177 Privacy, security and trust](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-15 | [#178 Quality and performance](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-16 | [#179 TestFlight, App Store delivery and launch](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-17 | [#180 Product and data operations](https://github.com/Pick-Your-AI/pickyour.ai/issues/180) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-18 | [#181 Decision-dependent expansion](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) | [#163](https://github.com/Pick-Your-AI/pickyour.ai/issues/163) |
| IOS-01.01 | [#182 Target users and primary iPhone and iPad journeys](https://github.com/Pick-Your-AI/pickyour.ai/issues/182) | [#164](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) |
| IOS-01.02 | [#183 MVP scope and phased capabilities](https://github.com/Pick-Your-AI/pickyour.ai/issues/183) | [#164](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) |
| IOS-01.03 | [#184 Apple platform scope, technology and repository structure](https://github.com/Pick-Your-AI/pickyour.ai/issues/184) | [#164](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) |
| IOS-01.04 | [#185 Backend architecture and hosting](https://github.com/Pick-Your-AI/pickyour.ai/issues/185) | [#164](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) |
| IOS-01.05 | [#186 Accounts and monetization decisions](https://github.com/Pick-Your-AI/pickyour.ai/issues/186) | [#164](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) |
| IOS-01.06 | [#187 Acceptance criteria, ownership and release gates](https://github.com/Pick-Your-AI/pickyour.ai/issues/187) | [#164](https://github.com/Pick-Your-AI/pickyour.ai/issues/164) |
| IOS-02.01 | [#188 Xcode toolchain, dependencies and modules](https://github.com/Pick-Your-AI/pickyour.ai/issues/188) | [#165](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) |
| IOS-02.02 | [#189 Preview, staging and production environments](https://github.com/Pick-Your-AI/pickyour.ai/issues/189) | [#165](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) |
| IOS-02.03 | [#190 Navigation, lifecycle and state restoration](https://github.com/Pick-Your-AI/pickyour.ai/issues/190) | [#165](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) |
| IOS-02.04 | [#191 UI, domain and data boundaries](https://github.com/Pick-Your-AI/pickyour.ai/issues/191) | [#165](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) |
| IOS-02.05 | [#192 macOS continuous integration and required checks](https://github.com/Pick-Your-AI/pickyour.ai/issues/192) | [#165](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) |
| IOS-02.06 | [#193 Clearly identified synthetic fixtures](https://github.com/Pick-Your-AI/pickyour.ai/issues/193) | [#165](https://github.com/Pick-Your-AI/pickyour.ai/issues/165) |
| IOS-03.01 | [#194 Adopt versioned contracts and generate models](https://github.com/Pick-Your-AI/pickyour.ai/issues/194) | [#166](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) |
| IOS-03.02 | [#195 Separate incomplete drafts from saved snapshots](https://github.com/Pick-Your-AI/pickyour.ai/issues/195) | [#166](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) |
| IOS-03.03 | [#196 Define required versioned API extensions](https://github.com/Pick-Your-AI/pickyour.ai/issues/196) | [#166](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) |
| IOS-03.04 | [#197 Model component placement and relationships](https://github.com/Pick-Your-AI/pickyour.ai/issues/197) | [#166](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) |
| IOS-03.05 | [#198 Define evidence, unknowns and rule semantics](https://github.com/Pick-Your-AI/pickyour.ai/issues/198) | [#166](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) |
| IOS-03.06 | [#199 Cross-client conformance and migration fixtures](https://github.com/Pick-Your-AI/pickyour.ai/issues/199) | [#166](https://github.com/Pick-Your-AI/pickyour.ai/issues/166) |
| IOS-04.01 | [#200 Source access, display and redistribution rights](https://github.com/Pick-Your-AI/pickyour.ai/issues/200) | [#167](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) |
| IOS-04.02 | [#201 Normalize and validate component facts](https://github.com/Pick-Your-AI/pickyour.ai/issues/201) | [#167](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) |
| IOS-04.03 | [#202 Evidence review and production approval](https://github.com/Pick-Your-AI/pickyour.ai/issues/202) | [#167](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) |
| IOS-04.04 | [#203 Publish immutable catalog and rule releases](https://github.com/Pick-Your-AI/pickyour.ai/issues/203) | [#167](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) |
| IOS-04.05 | [#204 Freshness, corrections and retractions](https://github.com/Pick-Your-AI/pickyour.ai/issues/204) | [#167](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) |
| IOS-04.06 | [#205 Publish the first complete supported real-data path](https://github.com/Pick-Your-AI/pickyour.ai/issues/205) | [#167](https://github.com/Pick-Your-AI/pickyour.ai/issues/167) |
| IOS-05.01 | [#206 API foundation, database and migrations](https://github.com/Pick-Your-AI/pickyour.ai/issues/206) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.02 | [#207 Catalog discovery, search and delivery](https://github.com/Pick-Your-AI/pickyour.ai/issues/207) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.03 | [#208 Build creation, revisions, history and deletion](https://github.com/Pick-Your-AI/pickyour.ai/issues/208) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.04 | [#209 Compatibility evaluation and pricing services](https://github.com/Pick-Your-AI/pickyour.ai/issues/209) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.05 | [#210 Share creation, access and revocation](https://github.com/Pick-Your-AI/pickyour.ai/issues/210) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.06 | [#211 Resource estimates and quality evidence](https://github.com/Pick-Your-AI/pickyour.ai/issues/211) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.07 | [#212 Authorization and optional account authentication](https://github.com/Pick-Your-AI/pickyour.ai/issues/212) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.08 | [#213 Limits, auditability, secrets and recovery](https://github.com/Pick-Your-AI/pickyour.ai/issues/213) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-05.09 | [#214 Integration with the existing website](https://github.com/Pick-Your-AI/pickyour.ai/issues/214) | [#168](https://github.com/Pick-Your-AI/pickyour.ai/issues/168) |
| IOS-06.01 | [#215 Information architecture and interaction prototypes](https://github.com/Pick-Your-AI/pickyour.ai/issues/215) | [#169](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) |
| IOS-06.02 | [#216 Accessible components and design tokens](https://github.com/Pick-Your-AI/pickyour.ai/issues/216) | [#169](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) |
| IOS-06.03 | [#217 Adaptive iPhone and iPad layouts](https://github.com/Pick-Your-AI/pickyour.ai/issues/217) | [#169](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) |
| IOS-06.04 | [#218 Builder guidance and understandable status labels](https://github.com/Pick-Your-AI/pickyour.ai/issues/218) | [#169](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) |
| IOS-06.05 | [#219 Loading, empty, offline and failure states](https://github.com/Pick-Your-AI/pickyour.ai/issues/219) | [#169](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) |
| IOS-06.06 | [#220 Themes, localization, units and presentation](https://github.com/Pick-Your-AI/pickyour.ai/issues/220) | [#169](https://github.com/Pick-Your-AI/pickyour.ai/issues/169) |
| IOS-07.01 | [#221 Browse, search, filter and sort the catalog](https://github.com/Pick-Your-AI/pickyour.ai/issues/221) | [#170](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) |
| IOS-07.02 | [#222 Compatibility-aware component picker](https://github.com/Pick-Your-AI/pickyour.ai/issues/222) | [#170](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) |
| IOS-07.03 | [#223 Component details, conditions and evidence](https://github.com/Pick-Your-AI/pickyour.ai/issues/223) | [#170](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) |
| IOS-07.04 | [#224 Side-by-side component comparison](https://github.com/Pick-Your-AI/pickyour.ai/issues/224) | [#170](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) |
| IOS-07.05 | [#225 Select components from search and deep links](https://github.com/Pick-Your-AI/pickyour.ai/issues/225) | [#170](https://github.com/Pick-Your-AI/pickyour.ai/issues/170) |
| IOS-08.01 | [#226 Workload, constraints and deployment inputs](https://github.com/Pick-Your-AI/pickyour.ai/issues/226) | [#171](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) |
| IOS-08.02 | [#227 Model and infrastructure selection](https://github.com/Pick-Your-AI/pickyour.ai/issues/227) | [#171](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) |
| IOS-08.03 | [#228 Enable and disable optional tiers](https://github.com/Pick-Your-AI/pickyour.ai/issues/228) | [#171](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) |
| IOS-08.04 | [#229 Edit component settings and build objectives](https://github.com/Pick-Your-AI/pickyour.ai/issues/229) | [#171](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) |
| IOS-08.05 | [#230 Persistent summary and suggested next steps](https://github.com/Pick-Your-AI/pickyour.ai/issues/230) | [#171](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) |
| IOS-08.06 | [#231 Undo, autosave and revision restoration](https://github.com/Pick-Your-AI/pickyour.ai/issues/231) | [#171](https://github.com/Pick-Your-AI/pickyour.ai/issues/171) |
| IOS-09.01 | [#232 Integrate the governed evaluator](https://github.com/Pick-Your-AI/pickyour.ai/issues/232) | [#172](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) |
| IOS-09.02 | [#233 Recheck affected components after changes](https://github.com/Pick-Your-AI/pickyour.ai/issues/233) | [#172](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) |
| IOS-09.03 | [#234 Explain findings and possible fixes](https://github.com/Pick-Your-AI/pickyour.ai/issues/234) | [#172](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) |
| IOS-09.04 | [#235 Consume qualified capacity estimates](https://github.com/Pick-Your-AI/pickyour.ai/issues/235) | [#172](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) |
| IOS-09.05 | [#236 Suggest alternatives with stated tradeoffs](https://github.com/Pick-Your-AI/pickyour.ai/issues/236) | [#172](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) |
| IOS-09.06 | [#237 Handle stale and out-of-order results](https://github.com/Pick-Your-AI/pickyour.ai/issues/237) | [#172](https://github.com/Pick-Your-AI/pickyour.ai/issues/172) |
| IOS-10.01 | [#238 Select applicable dated rates](https://github.com/Pick-Your-AI/pickyour.ai/issues/238) | [#173](https://github.com/Pick-Your-AI/pickyour.ai/issues/173) |
| IOS-10.02 | [#239 Calculate costs from explicit usage scenarios](https://github.com/Pick-Your-AI/pickyour.ai/issues/239) | [#173](https://github.com/Pick-Your-AI/pickyour.ai/issues/173) |
| IOS-10.03 | [#240 Show missing costs, coverage and uncertainty](https://github.com/Pick-Your-AI/pickyour.ai/issues/240) | [#173](https://github.com/Pick-Your-AI/pickyour.ai/issues/173) |
| IOS-10.04 | [#241 Compare scenarios and preserve price provenance](https://github.com/Pick-Your-AI/pickyour.ai/issues/241) | [#173](https://github.com/Pick-Your-AI/pickyour.ai/issues/173) |
| IOS-11.01 | [#242 Local build library](https://github.com/Pick-Your-AI/pickyour.ai/issues/242) | [#174](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) |
| IOS-11.02 | [#243 Compare complete builds and revisions](https://github.com/Pick-Your-AI/pickyour.ai/issues/243) | [#174](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) |
| IOS-11.03 | [#244 Safe import and export](https://github.com/Pick-Your-AI/pickyour.ai/issues/244) | [#174](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) |
| IOS-11.04 | [#245 Read-only shared builds with pinned evidence](https://github.com/Pick-Your-AI/pickyour.ai/issues/245) | [#174](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) |
| IOS-11.05 | [#246 Fork builds and optional cross-device continuity](https://github.com/Pick-Your-AI/pickyour.ai/issues/246) | [#174](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) |
| IOS-11.06 | [#247 Universal Links, associated domains and browser fallback](https://github.com/Pick-Your-AI/pickyour.ai/issues/247) | [#174](https://github.com/Pick-Your-AI/pickyour.ai/issues/174) |
| IOS-12.01 | [#248 Durable local database and migrations](https://github.com/Pick-Your-AI/pickyour.ai/issues/248) | [#175](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) |
| IOS-12.02 | [#249 Cached catalogs and offline draft editing](https://github.com/Pick-Your-AI/pickyour.ai/issues/249) | [#175](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) |
| IOS-12.03 | [#250 Atomic refresh and background scheduling](https://github.com/Pick-Your-AI/pickyour.ai/issues/250) | [#175](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) |
| IOS-12.04 | [#251 Queued writes and retry reconciliation](https://github.com/Pick-Your-AI/pickyour.ai/issues/251) | [#175](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) |
| IOS-12.05 | [#252 Conflict resolution without lost edits](https://github.com/Pick-Your-AI/pickyour.ai/issues/252) | [#175](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) |
| IOS-12.06 | [#253 Logout, deletion and unavailable-version handling](https://github.com/Pick-Your-AI/pickyour.ai/issues/253) | [#175](https://github.com/Pick-Your-AI/pickyour.ai/issues/175) |
| IOS-13.01 | [#254 Knowledge and retrieval configuration — T3](https://github.com/Pick-Your-AI/pickyour.ai/issues/254) | [#176](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) |
| IOS-13.02 | [#255 Agents, tools, MCP and memory — T4](https://github.com/Pick-Your-AI/pickyour.ai/issues/255) | [#176](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) |
| IOS-13.03 | [#256 Training and fine-tuned models — T5](https://github.com/Pick-Your-AI/pickyour.ai/issues/256) | [#176](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) |
| IOS-13.04 | [#257 Guardrails and evaluation guidance — T6](https://github.com/Pick-Your-AI/pickyour.ai/issues/257) | [#176](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) |
| IOS-13.05 | [#258 Deployment plans and monitoring choices — T6](https://github.com/Pick-Your-AI/pickyour.ai/issues/258) | [#176](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) |
| IOS-13.06 | [#259 Validate supported combinations across tiers](https://github.com/Pick-Your-AI/pickyour.ai/issues/259) | [#176](https://github.com/Pick-Your-AI/pickyour.ai/issues/176) |
| IOS-14.01 | [#260 Data inventory and threat model](https://github.com/Pick-Your-AI/pickyour.ai/issues/260) | [#177](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) |
| IOS-14.02 | [#261 Keychain, data protection and secure networking](https://github.com/Pick-Your-AI/pickyour.ai/issues/261) | [#177](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) |
| IOS-14.03 | [#262 Account and associated-data lifecycle, if included](https://github.com/Pick-Your-AI/pickyour.ai/issues/262) | [#177](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) |
| IOS-14.04 | [#263 Privacy disclosures and third-party SDK controls](https://github.com/Pick-Your-AI/pickyour.ai/issues/263) | [#177](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) |
| IOS-14.05 | [#264 Adversarial testing of sharing, imports and APIs](https://github.com/Pick-Your-AI/pickyour.ai/issues/264) | [#177](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) |
| IOS-14.06 | [#265 Dependency security and vulnerability response](https://github.com/Pick-Your-AI/pickyour.ai/issues/265) | [#177](https://github.com/Pick-Your-AI/pickyour.ai/issues/177) |
| IOS-15.01 | [#266 Contract and domain regression tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/266) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-15.02 | [#267 Apple UI and accessibility tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/267) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-15.03 | [#268 Network failure and recovery tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/268) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-15.04 | [#269 Device, OS and lifecycle test matrix](https://github.com/Pick-Your-AI/pickyour.ai/issues/269) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-15.05 | [#270 Apple, Android, web and backend conformance tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/270) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-15.06 | [#271 Measured startup, rendering and resource budgets](https://github.com/Pick-Your-AI/pickyour.ai/issues/271) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-15.07 | [#272 Security and release-build regression tests](https://github.com/Pick-Your-AI/pickyour.ai/issues/272) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-15.08 | [#273 Authorized user validation and acceptance](https://github.com/Pick-Your-AI/pickyour.ai/issues/273) | [#178](https://github.com/Pick-Your-AI/pickyour.ai/issues/178) |
| IOS-16.01 | [#274 Apple Developer team and App Store Connect identity](https://github.com/Pick-Your-AI/pickyour.ai/issues/274) | [#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| IOS-16.02 | [#275 Platform and store-policy requirements](https://github.com/Pick-Your-AI/pickyour.ai/issues/275) | [#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| IOS-16.03 | [#276 Signing, provisioning, entitlements and key management](https://github.com/Pick-Your-AI/pickyour.ai/issues/276) | [#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| IOS-16.04 | [#277 Internal and external TestFlight testing](https://github.com/Pick-Your-AI/pickyour.ai/issues/277) | [#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| IOS-16.05 | [#278 App Store listing, screenshots and privacy declarations](https://github.com/Pick-Your-AI/pickyour.ai/issues/278) | [#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| IOS-16.06 | [#279 Launch readiness and controlled rollout](https://github.com/Pick-Your-AI/pickyour.ai/issues/279) | [#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| IOS-16.07 | [#280 Verify the installed production release](https://github.com/Pick-Your-AI/pickyour.ai/issues/280) | [#179](https://github.com/Pick-Your-AI/pickyour.ai/issues/179) |
| IOS-17.01 | [#281 Application and service monitoring](https://github.com/Pick-Your-AI/pickyour.ai/issues/281) | [#180](https://github.com/Pick-Your-AI/pickyour.ai/issues/180) |
| IOS-17.02 | [#282 Incident response and restore drills](https://github.com/Pick-Your-AI/pickyour.ai/issues/282) | [#180](https://github.com/Pick-Your-AI/pickyour.ai/issues/180) |
| IOS-17.03 | [#283 Catalog, evidence and pricing maintenance](https://github.com/Pick-Your-AI/pickyour.ai/issues/283) | [#180](https://github.com/Pick-Your-AI/pickyour.ai/issues/180) |
| IOS-17.04 | [#284 Support, corrections and contribution workflow](https://github.com/Pick-Your-AI/pickyour.ai/issues/284) | [#180](https://github.com/Pick-Your-AI/pickyour.ai/issues/180) |
| IOS-17.05 | [#285 Compatibility maintenance and release cadence](https://github.com/Pick-Your-AI/pickyour.ai/issues/285) | [#180](https://github.com/Pick-Your-AI/pickyour.ai/issues/180) |
| IOS-18.01 | [#286 Favorites and price/compatibility alerts](https://github.com/Pick-Your-AI/pickyour.ai/issues/286) | [#181](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) |
| IOS-18.02 | [#287 Paid plans and entitlements](https://github.com/Pick-Your-AI/pickyour.ai/issues/287) | [#181](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) |
| IOS-18.03 | [#288 Community build publishing and moderation](https://github.com/Pick-Your-AI/pickyour.ai/issues/288) | [#181](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) |
| IOS-18.04 | [#289 Advanced recommendations and personalization](https://github.com/Pick-Your-AI/pickyour.ai/issues/289) | [#181](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) |
| IOS-18.05 | [#290 Actual runtime execution or provisioning](https://github.com/Pick-Your-AI/pickyour.ai/issues/290) | [#181](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) |
| IOS-18.06 | [#291 Additional markets and platforms](https://github.com/Pick-Your-AI/pickyour.ai/issues/291) | [#181](https://github.com/Pick-Your-AI/pickyour.ai/issues/181) |
