# Publication eligibility handoff

Refs research #39, #41 and #60; consumer [website #15](https://github.com/Pick-Your-AI/pickyour.ai/issues/15). Audit snapshot: `7115e77caf2d766b98d42dd8d75ee65325f2d4e7` (2026-10-18).

The existing proposals are structurally validated research inputs. **No complete existing pricebook or catalog artifact has publication eligibility established by this handoff.** This is a conservative scope assessment of the recorded rights evidence, not a new interpretation of vendor terms or a claim that every underlying fact is prohibited. Do not turn a missing assessment into an invented permission.

## Current product decision — 2026-10-18

The [scoped #60 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6248616771), delivered by [PR #299](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/299) at [accepted main `3d395801`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/3d395801742461aa82ac31a21857ec6f8d0270fb/research/market/rights-validation.md), **excludes GPUs.io API retrieval, display and export from the current product**. Its conditional API/display terms do not establish this product's eligibility under the competing-product restriction. Reconsider only on a specific permitted-use basis covering this product and a new #39/#41/#60 review.

The source-by-use table below preserves the earlier audit snapshot. Its conditional GPUs.io row is historical evidence, not the current product decision. The immutable inventory, its hashes and source attribution remain unchanged; this amendment establishes no publication eligibility for any complete catalog or pricebook artifact.

## Immutable artifacts

[The inventory](publication-artifact-inventory.json) identifies every catalog and pricebook proposal at the snapshot: exact path, SHA-256 of file bytes, ID/version or revision, and all provenance source URLs. Resolve paths against [this immutable tree](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/7115e77caf2d766b98d42dd8d75ee65325f2d4e7), not the current branch. This inventory remains a historical snapshot when later proposals change; its statuses are not a dynamic source-use service.

| Pricebook path under `pricing/proposals/` | ID / revision | Rates | Source scopes | Publication gap |
| --- | --- | --- | --- | --- |
| `t1-api-2026-10-16.json` | `pricebook.t1_api_2026_10_16` / 1 | 8 | OpenAI model documentation; Anthropic pricing documentation | No recorded #60 grant for these exact price-source/use scopes |
| `t2-hosting-2026-10-16.json` | `t2-hosting-2026-10-16` / 1 | 5 | Hugging Face endpoint pricing; Runpod network-volume documentation; Cloudflare R2 pricing | HF Hub identifier decision does not cover endpoint prices; remaining scopes are outside the ten-source table |
| `t4b-anthropic-web-search.json` | `pricebook.t4b.anthropic-web-search` / 1 | 1 | Anthropic pricing documentation | No recorded #60 grant for this exact price-source/use scope |

All 14 rates retain their captured dates, conditions and `unverified` provenance status. Validation is not evidence that these are current quotes, complete costs, eligible rates for every workload, or cleared for commercial publication. The AWS-backed HF endpoint rate is sourced from HF; an AWS pricing permission would not automatically cover it. There is no Azure pricebook in this snapshot.

## Source-by-use scope

This table transcribes the project decisions in [the pinned #60 record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/7115e77caf2d766b98d42dd8d75ee65325f2d4e7/research/market/rights-validation.md), terms checked 2026-10-16. “Conditional” means the recorded conditions still have to be satisfied by the consumer. It does not authorize a new fetch, subscription or deployment.

| Source / scope | Automated retrieval | Internal research | Commercial display | Bulk redistribution | Conditions / relationship to existing proposals |
| --- | --- | --- | --- | --- | --- |
| models.dev compilation | Conditional yes | Yes | Conditional yes | Conditional yes | MIT notice; not a blanket grant for upstream measurements; no matching provenance URL in this snapshot |
| ModelFit dataset | Conditional yes | Yes | Conditional yes | Conditional yes | CC BY 4.0, credit/link/change indication, label estimates; no matching provenance URL |
| llmfit repository data | Conditional yes | Yes | Conditional yes | Conditional yes | MIT notice; excludes website content; no matching provenance URL |
| MCP registry metadata | Conditional yes | Yes | Conditional yes | Conditional yes | Preserve listing-versus-certification distinction and separate annotations; applies only to registry-derived metadata, not entire mixed-source records |
| Hugging Face Hub identifiers | Conditional yes | Yes | Conditional yes | No under blanket Hub decision | Identifiers/revision/declared licence/size with link; cards/files require repository-specific grants; does not cover endpoint pricebook |
| Harness Bench paper v2 | Conditional yes | Yes | Conditional yes | No under recorded decision | Attributed paper results only; repository tasks/trajectories/catalog files excluded; no matching provenance URL |
| GPUs.io paid API | Conditional yes | Yes | Conditional yes | No | Paid API, attribution/link, inside build cost estimate only; competing comparison restriction still needs #39 disposition; no matching provenance URL, no purchase authorized |
| BenchLM-owned output | Conditional yes | Yes | No | No | Plans cover internal analysis; separate agreement for display/bulk output; no matching provenance URL |
| OpenRouter | No | Manual only | No | No | Written permission needed; no matching provenance URL |
| Artificial Analysis | No | Manual only | No | No | Product-category restriction; written consent needed; no matching provenance URL |
| Direct vendor pricing/docs, package registries and other repository sources in inventory | Not established by this audit | Existing research citations only | Not established; withhold pending scope review | Not established; withhold pending scope review | #60 has no general domain-wide grant; a code licence or public documentation URL does not certify every field's source-use scope |

Six catalog records cite the MCP registry: `t4c-atlassian-remote`, `t4c-github-local`, `t4c-github-remote`, `t4c-playwright`, `t4c-sentry-remote`, and `t4c-stripe-remote` (each `.json` under `catalog/proposals/`). Each also cites other sources. A registry-only projection could be assessed for publication under the recorded metadata grant; the current complete files are not that projection. A single provenance list also does not establish field-by-field attribution. Hugging Face catalog entries similarly include provider/hosting facts beyond the narrow identifier permission. Preserve software licence metadata as a fact about the software; do not treat it as an automatic grant over the full catalog record.

## Receiving decisions and deliverables

| Owner / entry point | Concrete output or remaining decision | Effect on consumer |
| --- | --- | --- |
| #60 / #41 (@tynamite, with live issue co-assignees) | Source-and-use decisions for exact price/docs sources in the inventory, with terms evidence, scope, required notices and any exceptions | No complete pricebook may be labelled cleared using the existing ten-source table alone |
| #39 (live T6 co-owners) | Accept rate applicability, incomplete cost coverage and source-use conditions; retain the accepted GPUs.io API/display/export exclusion unless a specific permitted-use basis and new #39/#41/#60 review establish a later decision | Cannot promise full or current production quotes from schema-valid rates |
| #40 / #41 and publication consumer | Agree a field-level source/rights projection or sidecar plus consumer enforcement, immutable artifact pins, retained notices, failure handling and rights-change invalidation | Inventory is an audit receipt, not a new v1 contract or final public catalog |
| Website #15 owner | Confirm selected source scopes and whether output is commercial display, public downloadable data, or both | Browser-bundled JSON and export/API designs need explicit assessment of redistribution, not only display |
| Relevant catalog owners | Map individual fields to source scopes for any eligible subset and retain attribution | Mixed-source records cannot inherit their most permissive source's grant |

The #60 owner recorded #41 adoption in the issue discussion; its older document status line is not evidence that adoption never occurred. The T1 receiving receipt accepts the restrictive metadata intake gate, not fresh blanket clearance. This handoff does not substitute for missing receiving-owner decisions, close any issue, approve memory semantics under #40, or assert a deployed catalog/price service exists.

## Validation boundary

Run the normal research workflow at the pinned snapshot to check proposals and references. Hash comparison verifies identity, not permission. The repository validators do not fetch legal terms or certify source accuracy. No new terms review, benchmark run, source-rights grant, external acceptance, or service availability is claimed here. Consumers must obtain and preserve the missing source-by-use decisions before promoting research files to public product data.
