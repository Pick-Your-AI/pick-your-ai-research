# Research method

Each component issue should produce a short research note or linked artifact with:

1. **Decision to support:** the user choice or compatibility check being researched.
2. **Candidate set:** options considered, including API, managed, and self-hosted paths where applicable.
3. **Attributes:** the minimum normalized fields needed for comparison, filtering, and compatibility.
4. **Evidence:** direct links to primary documentation, pricing, model cards, licenses, or benchmarks; record access date and region/currency for prices.
5. **Rules:** explicit hard constraints, warnings, unknowns, and dependencies on other components. Distinguish verified rules from hypotheses.
6. **Tradeoffs:** capability, latency, cost, privacy, operational effort, and vendor limitations as relevant.
7. **Open questions:** missing evidence, unresolved choices, and the owner of any follow-up.

Avoid presenting model performance, context limits, GPU fit, or price as universal facts. These can vary by model version, provider, quantization, runtime, batch size, region, and date. Preserve the source and conditions for every numeric claim.

## Completion criteria

A research issue is ready for design when its candidate fields, compatibility rules, source links, and unresolved questions are documented. A parent workstream is ready when its sub-issues are complete and its cross-workstream assumptions have been reviewed with the affected owners.

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
