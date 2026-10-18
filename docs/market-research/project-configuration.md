# Project configuration

[Market Research Project #2](https://github.com/orgs/Pick-Your-AI/projects/2), ID `PVT_kwDOFHg4Xc4BnViW`, organization Pick-Your-AI. Private visibility. Existing specialist collaborators were granted Project writer access; repository permissions were not changed. The Project is linked to the research repository. The Project README defines a manual workflow, evidence gates and ownership; no automatic workflow was added.

Nine requested fields are configured: Status, Priority, Research Area, Workstream, Work Type, Evidence Confidence, Research Readiness, Opportunity Impact and Effort. Built-in assignees, labels, parent and subissue progress are reused. Effort and opportunity impact remain Unknown pending evidence.

| View | Layout | Filter | Grouping |
| --- | --- | --- | --- |
| [01 — Executive Overview](https://github.com/orgs/Pick-Your-AI/projects/2/views/13) | BOARD_LAYOUT | `All items` | Workstream |
| [02 — Triage Inbox](https://github.com/orgs/Pick-Your-AI/projects/2/views/14) | TABLE_LAYOUT | `-status:Ready,"In Progress","In Review",Blocked,Done` | Research Readiness |
| [03 — Research Roadmap](https://github.com/orgs/Pick-Your-AI/projects/2/views/15) | TABLE_LAYOUT | `-status:Done` | Workstream |
| [04 — Kanban Board](https://github.com/orgs/Pick-Your-AI/projects/2/views/16) | BOARD_LAYOUT | `-status:Done` | Workstream |
| [05 — Competitive Intelligence](https://github.com/orgs/Pick-Your-AI/projects/2/views/17) | TABLE_LAYOUT | `research-area:Competition` | Workstream |
| [06 — Market & Customers](https://github.com/orgs/Pick-Your-AI/projects/2/views/18) | TABLE_LAYOUT | `research-area:Market,Customers` | Research Area |
| [07 — Product Opportunities](https://github.com/orgs/Pick-Your-AI/projects/2/views/19) | TABLE_LAYOUT | `research-area:Product,Strategy` | Opportunity Impact |
| [08 — Data & Integrations](https://github.com/orgs/Pick-Your-AI/projects/2/views/20) | TABLE_LAYOUT | `research-area:Data,Technology` | Workstream |
| [09 — Blockers & Dependencies](https://github.com/orgs/Pick-Your-AI/projects/2/views/21) | TABLE_LAYOUT | `research-readiness:Blocked,"Needs Input","Awaiting Decision"` | Research Readiness |
| [10 — Owner Workload](https://github.com/orgs/Pick-Your-AI/projects/2/views/22) | TABLE_LAYOUT | `-status:Done` | Assignees |
| [11 — Evidence Review](https://github.com/orgs/Pick-Your-AI/projects/2/views/23) | TABLE_LAYOUT | `status:"In Review"` | Evidence Confidence |
| [12 — Completed Research](https://github.com/orgs/Pick-Your-AI/projects/2/views/24) | TABLE_LAYOUT | `status:Done` | Workstream |

Both boards use Status columns and Workstream swimlanes. All views sort by priority. Roadmap uses a workstream table rather than invented dates. Grouping and sort configuration required the supported REST view-creation endpoint; GraphQL supplied readback and filter updates. The initial ungrouped views created in this session were replaced; actual view numbers are 13–24. Project #1 views were untouched.

GitHub Projects cannot OR across different fields. Triage therefore includes Inbox, Triage and unset statuses through a negative status filter. The coordinator must move incomplete/unassigned work to Triage during intake; the separate metadata audit detects omissions even when a status is incorrect. No unassigned or incomplete Ready items were found in final readback. This limitation is not hidden behind a nonfunctional OR query.

[View verification](../../research/market/view-verification.json) records actual matching issue IDs, including deliberately empty completed-research results. An anonymous browser cannot render a private project; verification used the authenticated API.


## Current public visibility readback — 2026-10-18

The configuration narrative and [JSON export](../../research/market/project-configuration.json) above describe the original private Project setup and its historical view verification. They are retained verbatim. A later independent, unauthenticated public REST read completed at **2026-10-18T21:59:38.704287Z** and returned Project 2 ID `27089046`, node `PVT_kwDOFHg4Xc4BnViW`, with **`public:true`**. Project 1 also returned `public:true` at 21:59:38.579887Z. The [dated QA capture](../../research/market/project-qa-2026-10-18-2152.json) records exact URLs, HTTP 200 results, byte counts and raw-response hashes.

This establishes current visibility at those read times, not when, why or by whom visibility changed. No collaborator permission, repository permission or Project value was changed in this read. The earlier statement that an anonymous browser could not render the then-private Project remains historical; it is not a present restriction on these public endpoints.

All nine custom-field node IDs and all 53 option IDs/names/order match the original configuration. The old GraphQL export's Created/Updated/Closed built-ins and the current REST response's Type field differ as explicitly recorded in the audit; no deletion is inferred. The twelve original views retain their earlier verification and exact export. This metadata pass does not claim a new view-layout/filter/permission test.
