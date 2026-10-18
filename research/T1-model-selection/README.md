# T1 Model Selection — current workstream summary

Parent: [#4](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/4) · Live assignees: @zwright8, @Mattycodes69 · Reconciled: **2026-10-18 UTC**

**All three child research decisions are accepted and closed.** This summary reconciles their delivered decisions, actual receiving records and remaining consumer work. Parent #4 stays open until this summary has independent review, required validation, canonical delivery and a separate assessment of its three original criteria. Actual Project status requires its own readback.

The workstream answers which exact model, offering and context policy can be considered for a declared workload and serving mode. The accepted decision is to keep identity, capability, access, context admission, runtime support, resource fit, quality and cost as distinct evidence-bound questions. A model name or a broad capability flag cannot establish a complete suitable deployment. The canonical decisions below supply the research interfaces; selected-service operation and released successor contracts remain separate work.

## Accepted child decisions and source identity

The native #4 child collection and all three issue states were read on **2026-10-18** after #6 closed at **20:11:45 UTC**. They contain exactly #5, #6 and #7, all closed/completed. The accepted source baseline for this summary is main [`5dd6e1c2174033a279325eb8fb445a0c4a694587`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/5dd6e1c2174033a279325eb8fb445a0c4a694587). Its three note blobs below equal the corresponding delivered child artifacts. Each delivery's actual Git object was independently read and reports a valid verified signature. That is repository delivery evidence, not a higher research-confidence grade.

| Child / accepted decision | Canonical delivered note | Actual completion evidence |
| --- | --- | --- |
| #5 Model Provider: distinguish publisher, distributor, runtime operator and selected offering; carry route-specific terms, quotas, lifecycle and price conditions | [Provider record at 5dd6e1c](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/5dd6e1c2174033a279325eb8fb445a0c4a694587/research/T1-model-selection/model-provider.md), blob `719b072daf2d213024bde7fd6816e5387389c131`; [PR #348](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/348), signed delivery `8cf075b1a887459337bfe886958b4c7d7f3c362f` | [Ten-criterion completion in #5](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/5); closed 15:33:12 UTC. [Actual subsequent Project receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/5#issuecomment-6251782710) records Done with other fields retained. |
| #6 AI Model: bind the exact release/artifact, serving route/configuration, task representation, requested capability and distribution-specific rights | [Model record at 5dd6e1c](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/5dd6e1c2174033a279325eb8fb445a0c4a694587/research/T1-model-selection/ai-model.md), blob `e723397dc36a3997163ee8119af0f883e8fb62df`; [PR #385](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/385), signed delivery `bda09ee40edca5a0f7919fe2a597f424d27119ff` | [Eleven-criterion completion](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6#issuecomment-6254590273); closed 20:11:45 UTC. Actual Project reconciliation is separate and is not inferred from issue closure. |
| #7 Context Window: use exact route/tokenizer/template semantics, complete serialized input, reserved output and the applicable shared or independent limits | [Context record at 5dd6e1c](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/5dd6e1c2174033a279325eb8fb445a0c4a694587/research/T1-model-selection/context-window.md), blob `5384081104cc2d872a4173138fc00a00c115c072`; [PR #378](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/378), signed delivery `cae31f324f827cdeb73548b72cafd392dd777dfa` | [Ten-criterion completion](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6253817788); closed 18:56:38 UTC. [Actual subsequent Project receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6253914197) records Done with other fields retained. |

The complete earlier summary, blob `90793d12b68dd16701c6dd5ceff2b97d69e4dd12`, remains unchanged under **Historical summary** below. Its pending-child and pending-handoff statements describe that earlier checkpoint. The old [acceptance matrix](acceptance-matrix.md), [validation](validation.md) and [goal progress](goal-progress.md) preserve their own earlier scopes; they do not override the later child completion receipts. No prior source access date, review, test execution or personal attribution is reassigned to this summary.

## Decisions the workstream supplies

| Decision | Accepted interpretation and limits |
| --- | --- |
| Offering and deployment mode | Follow the [provider decision](model-provider.md#current-provider-and-offering-disposition--2026-10-18): classify each serving component by runtime operator and capacity, retaining API, dedicated/reserved managed and user-operated alternatives. Billing channel, cloud branding and the presence of an API do not decide mode. Multiple providers alone do not create hybrid. |
| Canonical identity and task coverage | Follow the [current model decision](ai-model.md#current-model-selection-decision): distinguish family, exact release/artifact, alias, route, configuration and derivative lineage. Preserve tokenizer/template/processor and selected request details. The broader [taxonomy](model-taxonomy.md) and [inventory](model-research-inventory.json) remain sourced discovery, not an inventory of fully qualified deployments. Task-native nontext representations and unsupported units stay explicit. |
| Capability and runtime support | A broad tool, schema, fine-tuning or format flag is a necessary scoped input where applicable. It does not establish every request feature, architecture/loader, precision/backend/device or account combination. The [model interpretation](ai-model.md#version-field-and-capability-interpretation) and the actual #11 receipt below preserve exact tuple, original-schema, refusal/incomplete-result and adapter-lineage boundaries. |
| Context and tokenization | Follow the [current assembly contract](context-window.md#current-assembly-and-normalized-input-contract). Count the complete actual serialization or an eligible bound for that route and operation; include tool schemas, history, retrieved content and memory. Reserve output/thinking once under the applicable caps. An isolated fragment subtotal, billing sensitivity or character ratio does not establish full-request fit. Recount after permitted transformations. Unknown tokenizer, serialization, overhead or extension configuration retains the established unknown/native-limit treatment. |
| Resource and quality consequences | #10/#11 receive exact artifact, geometry, sequence/admission, cache dtype/layout, overhead and allocation inputs. Context admission and weight size alone establish no per-rank fit, calibrated error bound, throughput or quality. [Current KV input](context-window.md#current-kv-cache-handoff-to-10) and the [model compatibility boundary](ai-model.md#compatibility-and-retained-ownership) preserve those separate checks. Conditional workload quality remains W-R10 with #36's evidence requirements. |
| Access and training | The actual T5 decisions below accept field sufficiency with conditions. Retain normalized licence/custom terms, applicable eligibility and obligations, exact base/adapter/distribution and separate weight access, method support, account conditions and lifecycle. The [NOTICE observation](artifact-notices.md) concerns one inspected distribution; it grants no general permission or derivative clearance. |
| Provider price and total cost | The [provider price interface](model-provider.md#field-and-decision-boundaries-offered-for-acceptance) and [context cost interface](context-window.md#current-cost-handoff-to-39) retain exact dated item/version/route, meter, threshold, session, region and currency conditions. Reserved output is not predicted billing; a threshold-straddling input keeps both scenarios and the eligible higher-tier budget. Uncovered active costs remain unknown. #39 retains normalization, rounding, aggregation and regional/default policy. |

These interpretations summarize the already accepted child records. This amendment performs no new vendor retrieval, tokenization, model or account invocation, GPU measurement, benchmark, training job, pricing capture or source-rights assessment. The child notes retain their actual primary sources, access dates, evidence classes and numerical conditions. Successful structural validation and a valid Git signature do not certify source truth, deployment suitability or publication rights.

## Actual T2 and T5 handoffs required by parent #4

The full bodies of the following actual receipts were fetched and read for this parent assessment. Each accepts the named research interface with its own source and consumer pins; no new response from an absent assignee is inferred. The [canonical T1 ledger](handoffs.md#current-model-receiving-reconciliation-2026-10-18) preserves the earlier and current directional records separately.

| Parent boundary | Actual receiving evidence | Accepted meaning and retained consumer work |
| --- | --- | --- |
| Model access facts → T5 #30 | Historical [6245639699](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6245639699) and current [#6 → #30, 6254146777](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6254146777), producer `2c098336` / note `2d40a6f9` | Field sufficiency is accepted with normalized identifiers, action-bound conditions and obligations. The later receipt preserves the exact-distribution NOTICE finding and accepted training correction. The older comment did not name a reviewed SHA and receives no retroactive one. Individual permission, method/export and derivative decisions remain with #30/#33/#40. |
| Provider lifecycle → T5 #30 | [#5 → #30, 6251442684](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6251442684), producer `d81f4cb3` / note `ad87e5f8` | Exact selected capability, training-job eligibility and base/derived inference lifecycle are distinct. Provider-wide dates, rights grants and a working service are not inferred; the current model intake expressly retains this earlier direction. |
| Model inputs → GPU #10 | [#6 → #10, 6254086133](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6254086133), producer `2c098336` / note `2d40a6f9` | Accept exact artifact/configuration and source geometry, separate storage/compute/cache precision, complete context, live residency and per-pool/rank placement. Sum only evidenced simultaneous allocations and apply a supplied reserve once. Current selected-runtime measurements and calibration remain separate. |
| Context/KV manifest → GPU #10 | [#7 → #10, 6253262636](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6253262636), producer `bca2bc00` / note `cf1c581b` | Accept complete input and separate output, configured request-to-sequence expansion before applicable admission, exact cache geometry/dtype/block rounding and all resident allocations. A step batch is not a complete retained-cache cap; missing allocation/reserve evidence remains unknown. |
| Model/artifact/request inputs → engine #11 | [#6 → #11, 6254202835](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6254202835), producer `2c098336` / note `2d40a6f9` | Accept the exact model/engine/build/backend/device/API/parser/request tuple. Keep architecture admission, joint support, adapter composition, memory and original-schema/request behavior distinct. Known opaque API applicability differs from an explicitly selected managed engine or unknown operator. |

The current child records and their completion receipts account for all other declared outgoing directions: [five provider intakes](model-provider.md#actual-five-consumer-receiving-decisions), [nine model intakes](ai-model.md#current-receiving-decisions) and [four context intakes](context-window.md#actual-outgoing-receiving-decisions). Those accepted child-level records supply the remaining T3/T4/T6 and reciprocal scope. This summary does not relabel them as new reviews, accept an entire consumer issue or broaden their original evidence.

## Rules contributed to #40

| Existing contribution | Workstream decision retained |
| --- | --- |
| [T1-O1 / T1-O2](rules/model-offering.md) | Preserve selected model/provider identity and the necessary fine-tuning capability check. An eligible explicit negative is actionable in its scope; a capability pass cannot supply entitlement or satisfy licence conditions. |
| [CTX-01 / CTX-02](rules/context-fit.md) | Preserve complete-request input/output admission, applicable native/provider limits and conservative eligible bounds. A straddling fit estimate fails with the stated uncertainty; missing required evidence stays unknown. |
| [CTX-03 / CTX-04](rules/context-warnings.md) | Preserve supported transformations and recounting, and complete context-dependent price classification. No universal usable-context threshold or unselected quality diagnostic is added. |
| COMPUTE-02 / ENGINE-02 / D-R3 | One joint model/engine/backend/hardware support family. Retired T1-M1 does not create a second verdict. #10/#11 retain scoped support evidence. |
| COMPUTE-01 / W-R6 | One memory-fit family, with exact T1 inputs and #10/#11 geometry/admission/placement evidence. Retired T1-M2 does not duplicate it. Missing resource evidence retains `on_unknown: review`; supplied reserve is applied once. |
| D-R2a / D-R2b and W-R10 inputs | Eligibility, obligation answers and conditional comparable-quality evidence remain their shared families, with existing fixed severities and independent outcomes. No actual answer, grant or quality result is created. |

The [existing central #88 disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), applied in the child records, and their current actual receiving decisions establish this research contribution. Frozen v1, published Ruleset adoption and released wire/readers remain distinct. Later #40/#41 source-only packets keep their own review and delivery states; this parent summary does not declare them merged or necessary new native blockers for the already accepted T1 research.

## Named remaining decisions

| Follow-up scope | Existing accountable issues and owners |
| --- | --- |
| Future offering/model/context corrections and additional discovery | #5 @zwright8/@tynamite; #6 @zwright8/@PUSHINGSQUARES; #7 @zwright8/@appletechie. Preserve source dates, exact selected identities, unsupported task mappings and named unknowns. |
| Exact runtime support, per-rank capacity and guarded empirical measurements | #10 @Mattycodes69/@appletechie; #11 @zwright8/@Mattycodes69; #61 @Mattycodes69/@appletechie. Research handoff acceptance supplies no selected-deployment result. |
| Action-bound rights, method/export and derivative obligations | #30 @zwright8/@appletechie; #33 @Mattycodes69/@appletechie, with #40 representation governance. Preserve actual current training corrections and per-distribution evidence. |
| Retrieval/memory assembly and original-schema controls | #16 @zabyxc01/@appletechie; #28 @CompleteDotTech/@PUSHINGSQUARES; #25 and #35 in their existing scopes. Complete-request counting does not choose a backend, approve content loss or prove access enforcement. |
| Workload quality, source use and costs | #36/#39 @appletechie/@PUSHINGSQUARES; #41 @tynamite/@PUSHINGSQUARES; #60 retains its accepted material/use restrictions. Missing benchmark identities, permission or active charges remain explicit. |
| Versioned representations, rules and saved-build migration | #40 @zwright8/@tynamite and #42 @tynamite/@appletechie. Existing research proposals do not change the frozen import, supply a released successor, or overwrite historical saved identities. |

These are retained consumer/future-work responsibilities, not new assignments or completed actions. Their existence does not undo the accepted bounded child research; it also supplies no authority to operate a service, publish restricted data or close those issues.

## Parent acceptance and delivery boundary

| Exact original #4 criterion | Evidence and final gate |
| --- | --- |
| All sub-issues are closed with merged decision records that meet their acceptance criteria | The actual native child collection contains the three closed/completed issues above, with their original ten/eleven/ten criteria accepted and signed delivered notes preserved at the summary baseline. Refresh those states before the final parent reconciliation. |
| The handoffs above are confirmed by the affected workstream owners | The actual T5 access/lifecycle and T2 model/engine/KV receipts above accept the interfaces with explicit conditions. They preserve live co-assignees, delegated reviewer attribution and shared #40 families; no absent owner's personal approval is invented. |
| A workstream summary at `research/T1-model-selection/README.md` lists decisions, rules contributed to #40, and open questions | This current summary provides that synthesis at the canonical path and preserves the old record below. Independent source/composition review, required checks, ordinary protected delivery and actual default-branch verification remain the final publication gates. |

This amendment uses **Refs #4**. It does not automatically close the parent. After reviewed delivery, assess the three unchanged criteria and independently read the actual Project item and resulting issue state. Preserve its assignees, native children, priority, readiness, confidence and other fields. Research completion and Project Done describe the accepted research deliverable; neither claims an implemented or deployed model-selection product.

## Historical summary

Everything below is the complete earlier `90793d12b68dd16701c6dd5ceff2b97d69e4dd12` summary, retained once with its original dates, pending statements and attribution. The current section above supersedes only those status interpretations supported by the later accepted evidence.

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
