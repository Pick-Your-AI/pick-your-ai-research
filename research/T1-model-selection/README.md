# T1 Model Selection research

Parent: [#4](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/4) · Owner at intake: @zwright8 · Last researched: 2026-10-16
Status: **merged research with scoped central-owner positions; follow-up and consuming-owner review pending**. Vendor research remains dated 2026-10-16; the central [PR #88 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868) was reconciled on 2026-10-17. This summary reports sourced findings and proposed contract changes, not completed issues or an approved executable ruleset.

## Decision records

| Issue | Record | Canonical kind |
| --- | --- | --- |
| #5 Model Provider | [model-provider.md](model-provider.md) | `model_provider` |
| #6 AI Model | [ai-model.md](ai-model.md) | `model` |
| #7 Context Window | [context-window.md](context-window.md) | `context_policy` |

Supporting records: [source register](evidence.md), [handoffs](handoffs.md), [exact acceptance matrix](acceptance-matrix.md), [validation](validation.md), [goal progress](goal-progress.md).

## Expanded scope and source audit (2026-10-17)

The user clarified that model selection must include types beyond LLMs and that **all model research, including the earlier work, must cite sources**. Start with [model taxonomy and coverage](model-taxonomy.md), its six detailed comparisons and [complete primary-source register](model-research-sources.md). The [JSON notes](model-research-inventory.json) contain248 candidate records spanning55 overlapping research task tags; models, pipelines/bundles, unpinned families and recipes are explicitly distinguished. These are corpus counts, not a global census or validated production inventory.

[Retrospective T1 citation audit](citation-audit-2026-10-17.md) corrects indirect/wrong evidence references while preserving original dates. [Market citation map](../market/citation-index-2026-10-17.md) indexes every current nonunknown matrix claim; supplemental source URLs and fresh rechecks do not rewrite historical access. No independently measured performance, universal licence permission or owner acceptance is inferred. [Task-family contract proposal](model-family-contract-proposal.md) routes unsupported types/units through #40 while preserving v1 and earlier central-owner corrections.

## Proposed decisions and findings

- Model publisher, serving provider, distributor and offering are distinct. Pin a release and its serving route; an alias/marketing family alone is insufficient. The [source register](evidence.md) supplies claim-level dates and versions.
- Apply #3's [current operator/capacity taxonomy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) per serving component: self-operated -> self-hosted; provider-operated shared -> API; dedicated/reserved -> managed; mixed serving modes -> hybrid. Bedrock on-demand is API; dedicated HF endpoints are the managed candidate. Billing/hosting brand does not set mode.
- Published API candidates include exact GPT-5.4 and Claude Sonnet5.5 snapshots. Gemini2.5Flash is a restricted legacy-access comparison. Pinned Qwen3-8B is the self-hosted source-artifact comparison. Candidate quality was not benchmarked; recommendations must not imply a universal best model.
- Dateless does not necessarily mean rolling: current Claude release IDs are fixed snapshots. For weights, preserve model/tokenizer/config/license revision and derivative lineage.
- Model/provider context limits, output limits and usable task quality are different. Gemini's independent budgets cannot be safely forced into a fabricated combined v1 scalar. Qwen's generation recommendation is not a universal output cap. Direct and Bedrock limits remain route-specific.
- Token estimates include complete serialized inputs and generation reserves, with explicit bounded/unbounded uncertainty. Context fit is not a guarantee of usable quality, latency, GPU capacity or training permission.
- For bounded context estimates, decide on the upper bound; straddling intervals fail flagged **may not fit**, with the range shown. Unknown extension configuration uses the evidenced native limit. Quality checks run only for a selected workload `quality_target` under W-R10; transformation support and recounting remain independent.
- License/access fields retain the actual source and conditions; #30 must confirm sufficiency. T2 owns exact engine/backend support and resource methodology; #36 owns measured quality.
- API prices are dated USD first-party list rates with exact model versions. Prompt thresholds, caching, service tier and residency affect applicability. Unknown self-hosting and uncovered operations remain unpriced; the Pricebook is not a complete build quote.
- #41's adopted distinction between checked and independently verified evidence is applied. Current-state facts are dated; pinned facts are rechecked on version/source correction. Resolve conflicts by documented scope and authority before assigning unknown.

## Contributions for #40 review

The [PR #88 owner review at `dbfa7dd`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868) accepts T1-O1 and CTX-04, accepts CTX-01/02 with corrections, and narrows CTX-03/T1-O2. This follow-up applies all five requested edits in [model/offering rules and shared inputs](rules/model-offering.md), [CTX-01/02](rules/context-fit.md) and [CTX-03/04](rules/context-warnings.md). T1-O2 now separates v1 model/provider fine-tuning capability from proposed answerable license conditions (D-R2a/b). CTX-03 retains v1 transformation support and recounting; conditional quality belongs to W-R10. Former T1-M1/M2 IDs are retired into the #75 joint-support family (COMPUTE-02/ENGINE-02/D-R3) and memory-fit family (COMPUTE-01/W-R6), with `on_unknown: review` for missing resource evidence. T1 supplies pinned inputs; #10/#11 own formulas/runtime evidence. Outcomes remain separate from severity. The changed revision still needs review; no final executable Ruleset is published.

Contract routing is recorded in [handoffs](handoffs.md): existing `provided_by` binds model/provider; richer endpoint identity, answerable terms/lineage/context-policy roles use #81 CD-6; independent context semantics and route overrides use CD-11; per-stage budgets use CD-5. #39 first owns price applicability, followed by CD-7 migration; region mapping uses CD-9. Existing v1 fields and one-version intake are preserved. These owner positions need versioned #40 changes and affected-owner review before executable use.

## Structured proposals

Ten catalog records: six provider/source identity captures, two exact API model records and two model-specific published-ceiling context records. One Pricebook supplies eight conditioned rates. Provider capture dates are not vendor release versions; provider/context billing classification remains unknown rather than implying a free service. Model optional unknowns stay absent.

Qwen/Gemini remain note-only model candidates where required max-output/combined-context semantics lack a sufficiently supported mapping. This preserves evidence, not a synthetic placeholder record. No weights, raw datasets, credentials, private data, new API service or model deployment are included.

## Completion and open work

All [41 criteria](acceptance-matrix.md) for assigned #4–7/#49 are tracked without equating a merge with full acceptance. The #3/#41 applications and scoped #40 positions are recorded in [handoffs](handoffs.md); required independent consumer confirmations remain pending, including #30 license-field sufficiency and #10 KV inputs. #49's matrix contribution remains separate from T1; its earlier PR #67/#87 stack state is historical and must be refreshed in that track. Parent #4 still needs complete child acceptance and confirmed cross-workstream handoffs before closure.

Decision records merged in [PR #88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88); the central reviewer explicitly reviewed merged head `dbfa7dd`. The separate matrix contribution is [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87). [Goal progress](goal-progress.md) preserves the prior publication checkpoint with this follow-up noted. No new board/assignment mutation is part of this correction; owner decisions remain required before completion.
