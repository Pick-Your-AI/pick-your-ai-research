# Collaboration and governance

Lightweight by design: normal research contributions need one reviewer and no ceremony. Heavier steps apply only to shared contracts.

## Ownership

Each workstream (T0 to T6) has an owner assigned on its parent issue. Owners coordinate research and review pull requests in their tier. Ownership does not grant repository administration rights; access stays least-privilege.

## Roles in review

- **Tier owner**: reviews changes within their tier.
- **Contract reviewers**: all tier owners review changes to `contracts/v1/` and `schemas/`, following `contracts/v1/ADOPTION.md`.
- **Cross-tier reviewer**: the owner of any tier whose components are referenced by a dependency or compatibility rule must be requested for review.

## How things happen

| Activity | Process |
|---|---|
| Submit a research proposal | Open an issue with the research template: objective, scope, expected deliverables, sources. Link it to its parent component issue. |
| Add a technology to the catalog | Follow [RESEARCH_WORKFLOW.md](RESEARCH_WORKFLOW.md): a research note plus a CatalogItem proposal under `catalog/proposals/` that passes the repository validation. One tier-owner review. |
| Verify a compatibility claim | Record claim-level evidence per the shared contract. A vendor statement and an independently reproduced result are different evidence grades; unverified claims stay marked unverified until a second source or reproducible test confirms them. |
| Resolve conflicting evidence | Record both sources on the rule, prefer primary sources and newer versions, state the conditions each applies to, and note the decision in an ADR (`docs/decisions/`). If it stays unresolved, record the compatibility as unknown, never as compatible. |
| Flag stale information | Anyone can open an issue flagging a record whose source changed or whose verification date is old. Pricing and availability go stale faster than specifications. Freshness thresholds are to be agreed by tier owners and recorded as an ADR. |
| Change the schema | The shared contract lives in `contracts/v1/` (generated from its documented source; do not patch generated schemas by hand). Propose changes through an issue and PR as described in `contracts/v1/ADOPTION.md`, reviewed by all affected tier owners. |
| Communicate cross-tier changes | Mention affected owners on the PR and the related issues; update [DEPENDENCIES.md](DEPENDENCIES.md) when a relationship changes. |
| Review pull requests | Check sources and claim types first, then contract validation, then wording. Request changes only for correctness, missing evidence, or contract violations. |
| Record decisions and open questions | Decisions: short ADR in `docs/decisions/` (context, decision, consequences). Open questions: an issue with a `question` label, linked from the affected record. |

## From finding to product requirement

1. **Finding**: a research issue produces a decision record and catalog proposals.
2. **Reviewed**: merged by pull request with sources and validation.
3. **Validated rule**: a compatibility or dependency rule has primary-source evidence and passes validation.
4. **Requirement**: owners summarise what the builder must do in the product requirements, referencing the catalog item IDs. Only rules at this stage drive the product.

## Definition of done for a research issue

An issue is Done only with usable findings, source references with access dates, documented limitations, reviewed data, and contract validation where it applies. A bare list of technologies is not done.

## Application planning and cross-client handoffs

The [Apple/iOS delivery plan](APPLE_DELIVERY_PLAN.md) follows the Android plan's
18-epic, 110-work-package structure. Delivery levels do not replace research tiers.
Research, shared service delivery, native-client integration and release approval
have separate definitions of done; no status transfers automatically between them.

Before creating implementation tracking, refresh existing issues and PRs. Keep shared
contracts, data publication and service work under their canonical issues, with
client-specific integration tasks only where there is a distinct deliverable. Use
native sub-issues for independently owned/reviewed tasks and checklists for small steps.
Preserve assignees and triage metadata; a plan does not grant new ownership, approve
research, select conditional features or authorize production deployment.

## Security and conduct

Report vulnerabilities as described in [SECURITY.md](../SECURITY.md). Be respectful and assume good faith; the organization-wide code of conduct, once adopted, applies here.
