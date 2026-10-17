# Mobile prompt publication review

This review concerns execution guidance, not implementation acceptance. Live source refresh was performed during publication preparation; source `updatedAt` and SHA-256 identities are recorded per issue in [coverage.json](coverage.json). Historical dates/counts in plans and triage text are not deadlines, live status or quotas.

## Source and coverage findings

- Planning issues are in `Pick-Your-AI/pickyour.ai`; guidance and Apple planning/tracking documents are in `Pick-Your-AI/pick-your-ai-research`. The Android plan is the live program, epic/work-package bodies and Project README. No nonexistent Android plan path is required.
- Project 4: 129 issues, one program, 18 epics, 110 work packages, 128 parent edges and 210 native prerequisite edges. Project 5: 129 issues, one program, 18 epics, 110 work packages, 128 parent edges and 222 prerequisite edges. The combined covered prerequisite graph has no cycles.
- Exact coverage: 258 issue mappings, 906 acceptance criteria and 880 implementation checklist steps. There are two program prompts and 36 scoped epic prompts; no checklist-task prompt duplication.
- Both Projects' 19 fields and their option IDs were inspected independently. All 258 issues were unassigned and Backlog at intake. Readiness includes Needs owner, Needs input and Awaiting decision; none of this guidance makes them Ready or In Progress.
- All covered issue bodies, parent/child/prerequisite relations, comments and linked PR references were retrieved. No existing mobile execution-prompt sections were found. The open research PR 74 supplies the T0–T6 approach but is not a merged dependency. Existing mobile planning/triage publications, including research PRs 99 and 106, are planning evidence, not app delivery.
- Research authorities Pick-Your-AI/pick-your-ai-research#39, Pick-Your-AI/pick-your-ai-research#40, Pick-Your-AI/pick-your-ai-research#41, Pick-Your-AI/pick-your-ai-research#42 and Pick-Your-AI/pick-your-ai-research#60 were verified live and remain open. Their current owners were inspected but not copied into mobile ownership.
- Website inputs Pick-Your-AI/pickyour.ai#15, Pick-Your-AI/pickyour.ai#16, Pick-Your-AI/pickyour.ai#17 and Pick-Your-AI/pickyour.ai#18 remain open canonical coordination points with live assignees. No owner, parent, status, label or prerequisite is changed by this publication.

## Cross-set consistency review

| Dimension | Review conclusion |
| --- | --- |
| Ownership and invocation | One common intake rule; platform and epic prompts inherit it. Full program, epic and single-package launches are bounded separately. Publication starts no campaign. |
| Scope and acceptance | Every original criterion and step is retained in the ledger; epic tables scope actual native children. Live changes require reconciliation. Core T6 remains mandatory while selected T3–T5 and expansion stay conditional. |
| Shared services | Website coordination points and Android shared outputs remain canonical. Apple service titles are interpreted as requirements/adapters/receiving acceptance, not new backend commissions. |
| Architecture and paths | Android intended acceptance paths are preserved verbatim in the implementation repository. Apple named outputs and unresolved placement are explicit. Framework, module, service-hosting and extra-platform choices remain behind existing decisions. |
| Contract and evidence | Frozen v1 unchanged; central versioning, evidence, price, saved-build and rights authorities retained. Unknowns, fixtures, estimates, actual measurements and reviewed production publication remain distinct. |
| Prerequisites and triage | Native graph preserved; information/compatibility links remain nonblocking context. Missing owner, input, decision and evidenced stopped/access state are distinguished. No field/status mutations accompany publication. |
| Platform specificity | Android process death, permissions, App Links, TalkBack, signing and Play requirements differ substantively from Apple state restoration, entitlements, Universal Links, VoiceOver, provisioning, TestFlight and App Store requirements. |
| Validation and finish | Exact issue-specific failure/recovery checks accompany common requirements. Local/simulated/device/service/store/release/operations evidence is distinct. Partial PRs and prompt publication cannot close delivery issues. |

Potential source drift is handled explicitly: older issue-body PR-state descriptions and numeric store-policy baselines are historical inputs, not current approvals or permanent requirements. Future execution must refresh actual PR state and current primary platform/store policy. The original scope criteria are preserved, not silently rewritten to an assumed policy or technology.

## Validation and limitations

Run `python prompts/mobile/validate_prompts.py`; for a fresh read-only snapshot also use `--audit-dir <directory>`. The latter compares exact criteria/steps, source body identity, ownership, hierarchy, native prerequisites, membership and Project fields. The offline check validates unique coverage, relative links/anchors, intended Android paths, explicit unresolved Apple locations, field vocabulary and the covered native prerequisite DAG.

Run all commands in [RESEARCH_WORKFLOW.md](../../docs/RESEARCH_WORKFLOW.md) with Python 3.12. These checks validate research structure and frozen contract integrity; they cannot establish factual evidence, rights, prompt quality, device behavior or release acceptance. Manual comparison of ownership, shared architecture, scope, prerequisite meaning, platform requirements and receiving-review boundaries is a separate review recorded above.

Publication preparation results: requirements installation succeeded; 21 contract tests passed; 24 repository tests passed; `scripts/validate_research.py` validated 30 catalog proposals, 2 pricebooks and external evidence metadata. The mobile validator passed against the full live-source snapshot. No application code or website repository files changed, so app builds/device/store tests are not claimed. Full REST timeline pagination for the five issues exceeding the first 100 cross-reference events found no hidden implementation PRs. The initial extraction missed the Apple parent issues' `Validation` heading; it was corrected before publication and exact coverage validation rerun successfully.

Remaining implementation intake: all mobile assignees and actual receiving reviewer commitments are unfilled in this baseline; scope/framework/module/service choices retain their issue gates. No device, signing account, console, deployment or production access has been exercised by prompt publication. This is not an access-denial finding. Independent maintainer review remains required before accepting this proposed guidance; the publication author is also the default CODEOWNER, so self-review must not be represented as independent approval. The user requested commit/push and no merge.
