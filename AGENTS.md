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

## Review policy for Codex and Claude

Apply this policy to Pick Your AI reviews, including related repositories reviewed from this workspace.

- For greenfield work, favor approving a useful, bounded contribution with constructive, non-blocking suggestions. Do not turn optional refinements, future hardening, incomplete neighboring work, or editorial preferences into approval gates.
- Encourage sound planning and architecture: clear component responsibilities, consistent data and state definitions, explicit interfaces and dependencies, usable handoffs, and testable acceptance criteria. Suggest concrete improvements without requiring an entire future system in the current PR.
- Request changes when a demonstrated, serious correctness, security, data-integrity, or architectural defect makes accepting the contribution unsafe or defeats its central purpose. Malice is not required for a real blocker. Explain the consequence and why it cannot reasonably be deferred; do not rubber-stamp known blockers or bypass required checks and independent review.
- When GitHub publication is authorized, provide a formal Approve or Request changes decision, not only a conversation comment. Put actionable suggestions inline on the exact reviewed revision, tag the contributor, and use GitHub suggestion blocks where a replacement is concrete. Clearly label non-blocking advice.
- Reviewers do not edit files, commit, push, merge, or implement their suggestions unless the user separately requests those actions. Use the requested reviewer model; do not substitute another model silently.
- Distinguish approval of the bounded PR from completion of its parent issues, receiving handoffs, deployment, or broader research acceptance. State what was inspected and what tests or runtime/VM checks were not performed.
- Search existing discussions before drafting. Verify the live head, submitted review state, contributor mentions, and inline suggestion ranges after posting. If a broader earlier critique is reassessed as non-blocking, say so explicitly in the formal review.
