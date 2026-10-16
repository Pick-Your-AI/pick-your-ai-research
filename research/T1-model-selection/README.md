# T1 Model Selection research

Parent: [#4](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/4) · Owner at intake: @zwright8 · Last researched: 2026-10-16
Status: **draft research for independent and consuming-owner review**. This summary reports proposals and sourced findings, not accepted product requirements or completed issues.

## Decision records

| Issue | Record | Canonical kind |
| --- | --- | --- |
| #5 Model Provider | [model-provider.md](model-provider.md) | `model_provider` |
| #6 AI Model | [ai-model.md](ai-model.md) | `model` |
| #7 Context Window | [context-window.md](context-window.md) | `context_policy` |

Supporting records: [source register](evidence.md), [handoffs](handoffs.md), [exact acceptance matrix](acceptance-matrix.md), [validation](validation.md), [goal progress](goal-progress.md).

## Proposed decisions and findings

- Model publisher, serving provider, distributor and offering are distinct. Pin a release and its serving route; an alias/marketing family alone is insufficient. The [source register](evidence.md) supplies claim-level dates and versions.
- Apply #3's [current operator/capacity taxonomy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) per serving component: self-operated -> self-hosted; provider-operated shared -> API; dedicated/reserved -> managed; mixed serving modes -> hybrid. Bedrock on-demand is API; dedicated HF endpoints are the managed candidate. Billing/hosting brand does not set mode.
- Published API candidates include exact GPT-5.4 and Claude Sonnet5.5 snapshots. Gemini2.5Flash is a restricted legacy-access comparison. Pinned Qwen3-8B is the self-hosted source-artifact comparison. Candidate quality was not benchmarked; recommendations must not imply a universal best model.
- Dateless does not necessarily mean rolling: current Claude release IDs are fixed snapshots. For weights, preserve model/tokenizer/config/license revision and derivative lineage.
- Model/provider context limits, output limits and usable task quality are different. Gemini's independent budgets cannot be safely forced into a fabricated combined v1 scalar. Qwen's generation recommendation is not a universal output cap. Direct and Bedrock limits remain route-specific.
- Token estimates include complete serialized inputs and generation reserves, with explicit bounded/unbounded uncertainty. Context fit is not a guarantee of usable quality, latency, GPU capacity or training permission.
- License/access fields retain the actual source and conditions; #30 must confirm sufficiency. T2 owns exact engine/backend support and resource methodology; #36 owns measured quality.
- API prices are dated USD first-party list rates with exact model versions. Prompt thresholds, caching, service tier and residency affect applicability. Unknown self-hosting and uncovered operations remain unpriced; the Pricebook is not a complete build quote.
- #41's adopted distinction between checked and independently verified evidence is applied. Current-state facts are dated; pinned facts are rechecked on version/source correction. Resolve conflicts by documented scope and authority before assigning unknown.

## Contributions for #40 review

Eight proposed rule groups follow the shared template: [T1-O1/O2 and T1-M1/M2](rules/model-offering.md), [CTX-01/02](rules/context-fit.md), [CTX-03/04](rules/context-warnings.md). They cover route identity, license/permission, format/engine support, scoped capacity evidence, context fit/configuration, quality/content loss and price classification. Each has applicability, fixed severity, missing-data behavior, examples, consumers and version consequences. Outcomes remain separate from severity. No final executable Ruleset is published.

Contract gaps: offering/model binding, independent context budget semantics and overrides, tokenizer/estimate bounds, architecture/derivative lineage, scoped terms/quotas/regions and conditional price applicability. Existing v1 fields and one-version intake are preserved; extend through #40 with affected-owner review and migration examples rather than patching imported files.

## Structured proposals

Ten catalog records: six provider/source identity captures, two exact API model records and two model-specific published-ceiling context records. One Pricebook supplies eight conditioned rates. Provider capture dates are not vendor release versions; provider/context billing classification remains unknown rather than implying a free service. Model optional unknowns stay absent.

Qwen/Gemini remain note-only model candidates where required max-output/combined-context semantics lack a sufficiently supported mapping. This preserves evidence, not a synthetic placeholder record. No weights, raw datasets, credentials, private data, new API service or model deployment are included.

## Completion and open work

All [41 criteria](acceptance-matrix.md) for assigned #4–7/#49 are tracked without equating prepared content with acceptance. Required T1 handoffs are [pending](handoffs.md). #49's matrix contribution remains separate from T1 and builds on unmerged PR #67. Parent #4 needs the three accepted/merged child records, this merged summary and its own confirmed cross-workstream assumptions before closure.

Submitted as [PR #88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88); the separate matrix contribution is [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87). See [goal progress](goal-progress.md) for exact branch/check/review state. The signed-in browser wrote and read back T1 Status=In Review without account permission expansion; #49 was already In Review. Normal independent reviews and owner decisions remain required before completion.
