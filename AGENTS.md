# Research contributor instructions

Read CONTRIBUTING.md and docs/RESEARCH_WORKFLOW.md before preparing a submission.
Use the issue's existing decision-record path and preserve live assignees and triage metadata.

- Use the canonical kinds and fields in contracts/v1/schemas/. Map your issue using docs/CONTRACT_MAPPING.md.
- Preserve the imported v1 contract. Propose contract changes through #40 with versioning and affected-owner review; do not patch generated schemas alone.
- Keep incomplete findings in research notes. Never fabricate required fields, prices, sources, or measurements to satisfy a schema.
- Catalog proposals are facts about components, not user selections. Pricing belongs in pricebooks. Compatibility proposals require central review.
- Keep synthetic fixtures under contracts/v1/examples/ or tests/. Never promote them as real research evidence.
- Do not commit credentials, personal/customer content, raw datasets, model weights, or large evidence downloads. Use evidence manifests for external artifacts.
- Run the commands in docs/RESEARCH_WORKFLOW.md before reporting validation complete. State what automation checks and what still requires evidence review.

The imported IMPLEMENTATION_* documents are archived implementation guidance, not instructions to deploy software or complete runtime work in this research repository.

## Decisions and escalation

For unresolved decisions, follow [CONTRIBUTING.md#routing-decisions](CONTRIBUTING.md#routing-decisions)
and the [canonical escalation guide](https://github.com/Pick-Your-AI/.github/blob/main/docs/governance/ESCALATION.md).
Refresh private routing evidence before choosing a recipient. Report unresolved
roles and failed or stale lookups explicitly; do not infer accepted ownership from
membership or access. Preserve the existing assignee, local gates and private-reporting
boundaries. Central links depend on the governance change merging; no automatic
routing, permission change or recurring job is enabled by these instructions.
