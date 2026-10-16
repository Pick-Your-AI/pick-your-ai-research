# Market research method and phase limits

This extends the existing research method for market notes; it does not change the frozen v1 component contract. JSON under `research/market/` serializes incomplete analyst observations and tracking records, not production CatalogItems, Pricebooks or runtime outputs. No second canonical component catalog is created. Complete facts and prices must later use the existing proposal workflow. PR #44 remains the pending source of that workflow.

## Bounded phases

| Phase | Initial limit | Exit evidence |
| --- | --- | --- |
| A Audit | All current issues/PRs/Projects, one current snapshot | Classifications, live ownership and canonical boundaries |
| B Project | One dedicated organization Project, nine requested fields, twelve views | Readback of owner, field options, view filters/grouping |
| C Discovery | 30–40 distinct resources, all named seeds/candidates | Dated source and capability evidence; failed access retained |
| D/E Backlog | One program, twelve workstreams, at most eight independent validations | Owner, question, scope, output, criteria, priority and next action |
| F Research | 10–15 desk profiles and one reviewable evidence PR | Matrix, customer/market analysis, risks and conditional MVP recommendation |
| G QA | One complete readback plus checks; rerun failures/changed areas | Validation record, remaining gaps, accurate status |

These limits constrain breadth rather than waive acceptance. Expand only for a material counterexample or decision-changing evidence, document the reason, and preserve completed work. No paid services, deployments, customer outreach or bulk third-party downloads in the initial pass. A lack of authenticated access is recorded and independent work continues. Owner review cannot be replaced by agent self-approval.

## Priority rubric

Weighted score = .25 strategic + .20 downstream + .20 user problem + .15 evidence availability + .10 feasibility + .10 urgency/change risk. Each is ordinal 1–5: 1 peripheral/isolated/weak or inaccessible/highly constrained/stable; 3 meaningful to one decision or workstream with obtainable inputs and material uncertainty; 5 central to product viability or multiple downstream decisions with strong starting evidence, bounded execution or immediate invalidation risk. Values 2 and 4 interpolate those anchors. These are sequencing judgements, not empirical vendor scores or effort estimates.

P0 >= 4.6; P1 >= 3.8; P2 >= 2.8; P3 below 2.8. Unknown criterion yields an unknown total, not zero. Apply documented qualitative priority where needed. Data-rights risk receives P0 override because it may invalidate all dependent ingestion. Do not force P3 or all-high distributions for appearance. Detailed vectors and overrides live in `research-backlog.json`.

## Evidence and readiness

Use claim-level URL, publisher, accessed date, version/region and evidence type. Verified Full is bounded by an exercised definition; Verified Partial is narrower documented support; Unsupported requires explicit negative evidence; Unknown records missing verification. No feature is absent merely because marketing omits it. Vendor descriptions and public tests are not independent performance measurements.

Ready requires a coherent question, owner, output path, acceptance criteria and sufficient starting inputs. Needs Input names missing information; Blocked identifies a genuine access/prerequisite constraint; Awaiting Decision names the deciding owner. Creating an issue is not starting work. In Review requires a relevant open PR; Done requires merged accepted evidence and handoffs. Parent completion additionally requires children. Assignees are authoritative.

## Organization compatibility

Project #1 currently uses Critical/High/Medium/Low priorities and Tier, not the older CONTRIBUTING labels. Market P0/P1/P2/P3 map to those four priorities conceptually; fields remain separate. Market Research Readiness maps to technical Readiness. Do not alter technical status or assignments from market inference. `type: workstream` is reserved for T0–T6 by existing guidance; new market items use `type: research`, with hierarchy and Work Type distinguishing epics.

Native blockers represent genuine execution constraints only; information inputs and validation gates are linked in bodies and handoffs. The existing #42 blocked-by #40 relation is preserved. Initial market tasks can investigate in parallel; accepted synthesis follows evidence review, so no artificial circular graph is introduced.
