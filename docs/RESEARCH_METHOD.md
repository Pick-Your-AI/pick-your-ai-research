# Research method

Use the [submission workflow](RESEARCH_WORKFLOW.md), [canonical-kind mapping](CONTRACT_MAPPING.md), and [research note template](../templates/research-note.md). The frozen v1 contract supplies shared names and types; schema changes go through #40. Raw or incomplete findings do not need a complete CatalogItem yet. Never fill unknown required fields with invented values.

Each component issue produces a decision record at `research/<workstream>/<component>.md` (the path is listed in the issue) with:

1. **Decision to support:** the user choice or compatibility check being researched.
2. **Candidate set:** options considered, including API, managed, and self-hosted paths where applicable.
3. **Attributes:** the minimum normalized fields needed for comparison, filtering, and compatibility.
4. **Evidence:** direct links to primary documentation, pricing, model cards, licenses, or benchmarks; record access date and region/currency for prices.
5. **Rules:** explicit hard constraints, warnings, unknowns, and dependencies on other components. Distinguish verified rules from hypotheses.
6. **Tradeoffs:** capability, latency, cost, privacy, operational effort, and vendor limitations as relevant.
7. **Open questions:** missing evidence, unresolved choices, and the owner of any follow-up.

Avoid presenting model performance, context limits, GPU fit, or price as universal facts. These can vary by model version, provider, quantization, runtime, batch size, region, and date. Preserve the source and conditions for every numeric claim.

## Evidence grades

Until [#41](https://github.com/Pick-Your-AI/research/issues/41) finalises the policy, label each claim with one of:

- **Primary documentation:** publisher's own docs, pricing page, model card, license, or specification.
- **Vendor claim:** a performance or capability statement by the vendor that has not been independently reproduced.
- **Independent measurement:** a published, reproducible measurement with stated conditions.
- **Estimate:** derived by this project; show the method and assumptions.

## Completion criteria

A research issue is **complete** when its decision record is merged and the acceptance criteria in the issue are met: candidate fields, compatibility rules in the shared format ([#40](https://github.com/Pick-Your-AI/research/issues/40)), source links, and unresolved questions are documented, and handoffs are confirmed by the consuming owners. A parent workstream is complete when its sub-issues are complete and its cross-workstream assumptions have been reviewed with the affected owners.

Research completion is not implementation completion. Describing a task, or opening a draft, does not complete research.

## Suggested decision record

```markdown
## User decision
## Candidate options
## Comparison fields
## Compatibility rules (hard / warning / unknown)
## Evidence (URL, publisher, access date, version, region)
## Recommendation and rationale
## Open questions
```
