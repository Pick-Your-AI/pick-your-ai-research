# T6 Deployment & Operations

Workstream: [#34](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34) · Contract: 1.0.0 · Owners: @PUSHINGSQUARES, @appletechie (issue assignees)
Status: all five child decision records are research-complete: Guardrails (#35) through [#413](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/413), Evaluation (#36) through [#402](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/402), Deployment (#37) through [#447](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/447), Monitoring (#38) through [#442](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/442) and Cost Estimate (#39) through [#436](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/436). The parent workstream (#34) remains open pending reviewed summary delivery, actual-main validation and final issue/Project reconciliation. Summary reconciled: 2026-10-19. Original source sweeps: 2026-10-16/17; source additions and the W5 illustration were checked on 2026-10-18 as identified in each record. This summary reconciliation does not refresh those source dates.

Product question: is the build safe, measurable, deployable, observable, and affordable?

This summary lists the decisions in the five T6 records, the rules they contribute to [#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40), the handoffs that other owners need to confirm, and the open questions. The records are the source; this page only points into them.

The [2026-10-18 sibling reconciliation](sibling-reconciliation.md) preserves the corrected alternative proposals from #113/#115/#116/#118/#120 at immutable revisions and records the four source findings also carried by concurrent #191, with a pinned harness readback and explicit Gemini API-family telemetry. Its supplemental sources are separate from the inventory counts below; PR supersession does not accept a receiving handoff or complete an issue.

## Records

| issue | record | v1 kind | decision it supports | source-checked rules | hypotheses | evidence rows |
|---|---|---|---|---|---|---|
| [#35](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35) | [Guardrails](guardrails.md) | `guardrail` | Which safety, security and policy controls should this build include, and what does the builder show when one is missing? | 36 | 3 | 55 |
| [#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36) | [Evaluation](evaluation.md) | `evaluation_suite` | How will the user know whether the build meets its quality, safety, latency and cost targets? | 94 | 13 | 296 |
| [#37](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37) | [Deployment](deployment.md) | `deployment_target` | What does it take to ship this build, and is it ready? | 90 | 21 | 222 |
| [#38](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/38) | [Monitoring](monitoring.md) | `monitoring_stack` | Which signals must be watched once the build runs? | 71 | 25 | 286 |
| [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39) | [Cost Estimate](cost-estimate.md) | `cost_policy` | What will this build cost, under stated assumptions, and with what uncertainty? | 45 | 11 | 202 |
| | total | | | 336 | 73 | 1,061 |

The original #121 submission records a QC pass that re-opened its cited URLs and applied the corrections in the records. The 2026-10-18 follow-ups rechecked their added findings and pricing inputs; they do not claim a new reread of every older source. The counts above reconcile Guardrails' E1–E55 inventory to #413 and Evaluation's evidence rows to #402; other component counts retain their recorded summary scope. Inline primary-source links and linked evidence appendices are additional references. The [accepted #41 evidence policy](../T0-configuration/catalog-data-sources.md#evidence-grades-and-labels), completed in [receipt 6256107246](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6256107246), grades each claim and distinguishes a checked citation from independently reproduced evidence. Existing row labels, access dates and unresolved source/use conditions retain their original scope; this summary does not regrade or re-certify them. These records do not supply a T6 runtime experiment. Figures are published (copied from a dated source), estimated (derived here, with the formula shown) or builder-set; automated recomputation of the scenarios is arithmetic validation.

## Decisions

### #35 Guardrails

**Research complete:** [#413](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/413) delivered the reviewed record at signed [`0d2e34d7`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/0d2e34d76cc6ac3e56165b7e72f4bbe0b8b87cb2). The [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6256149374) maps all nine original criteria and the actual R1–R6 receiving decisions. Selected-control execution, effectiveness, source-use permission and versioned builder adoption retain their separate evidence requirements.

- The control catalog maps 33 duties to the actual selected implementation, surface, operator and configuration. A catalog label or a documented capability does not establish enabled coverage.
- The editable project baseline assesses each build's applicable hazards and responsibilities, with additional retrieval, tool/agent and memory requirements when those paths are active. It does not require every build to buy a classifier or select a `guardrail` item.
- Show each scoped result with its fixed severity, outcome, evidence reason and follow-up owner. A saved warning acknowledgement preserves the warning/failure and does not waive a separate error or unknown-policy block; a passing error-severity assertion is not a block. Missing or unqualified evidence remains distinct from a known failure. These are the [reviewed display and policy semantics](guardrails.md#recommendation-policy-and-missing-control-display).
- Bind each control's configuration and observation responsibility to its actual operator and selected offering across API, managed and self-hosted paths. Documented availability, effective configuration and observed enforcement remain separate; a provider or mode label supplies none of the latter evidence.

### #36 Evaluation

**Research complete:** [#402](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/402) delivered the reviewed record and closed [#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36) at signed [`bf453fcf`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/bf453fcfd8bf501fca6ef10e6eb5414b3d5f2101). The [catalog qualification companion](evaluation-catalog-qualification.md) accounts for all 101 comparison rows and links 33 source-qualified `evaluation_suite` proposals. All new provenance remains `unverified`; no evaluator or model was run. Additional tier/sizing proposals and the named note-only questions retain their scope. Other T6 component issues and the parent workstream retain their own completion criteria.

- Evaluation is a per-build plan with four parts: the workload row, the safety pair, a latency-and-cost measurement, and a regression gate on a dataset the user owns.
- No primary source gives a recommended pass threshold, so every threshold is builder-set.
- Deployment gates G1 to G12 are handed to #37. Judges come from a different model family where the stack allows, with a pinned version and a human-labelled agreement sample before a judged metric gates a release (G3).
- Public benchmarks are selection priors only, shown with their reproducibility fields and tier (G11). OpenAI Evals is excluded because it is being retired (read-only from 2026-10-31).

### #37 Deployment

**Research complete:** [#447](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/447) delivered the reviewed record at signed [`ffe64042`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/ffe6404271c50c6ee4f44043e0d52a842df6afba), exact Deployment blob `08c3dacf4ce574071a4ce88a13509be42ace5f38`. The [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6258475240) maps all nine original criteria, the corrected D-R59/D-R66 and retention predicates, and the actual #37 → #38 interface whose source conditions are delivered in #442. #37 closed on 2026-10-19. Selected-target launch configuration, runtime observations, rights/account applicability, additional source coverage and versioned rule adoption retain the named follow-up owners; research completion is not deployment readiness.

- Mode follows the serving-component decision in [T0](../T0-configuration/deployment-mode.md), merged through #81: user-operated serving is `self_hosted`; provider-operated dedicated or reserved capacity is `managed`; provider-operated shared capacity is `api`. Billing units and customer-owned deployment objects do not determine mode. Hyperscaler on-demand/shared inference is `api`; dedicated endpoints and provisioned throughput are `managed`. Training runs do not set serving mode. Select the actual offering/capacity rather than inferring a mode from the provider name.
- Order of work runs from T0 through terms, identity, pins, the mode's platform steps, gates, monitoring and rollback, and only then traffic (S1 to S13).
- Default to a runtime identity in every mode, and to the pin that cannot move: a snapshot id (API), an explicit deployment version (managed), or an image digest plus a weights commit hash (self-hosted).
- Rollout mechanics belong to #37; promotion criteria belong to #36 and #38. Readiness rows show one of pass, fail, not applicable, unknown or not measured.

### #38 Monitoring

**Research complete:** [#442](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/442) delivered the reviewed record at signed [`e009fc0e`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/e009fc0edbb1821c045db036c5ae263921291c4d). The [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/38#issuecomment-6258005170) maps all nine original criteria and the actual R1–R7 receiving decisions; #38 closed on 2026-10-19. Signal availability, effective collection configuration, observed alert delivery, retention and source-use eligibility remain separately qualified. No installation, scrape, operational SLO result or new wire field follows from research completion.

- Page on three things only: SLO burn on client-measured latency and errors, a spend stop that is rejecting requests, and a serving pool with no ready endpoints.
- Measure latency at the client, because platform latency metrics differ in start point and statistic. Compute spend in-process and reconcile it with billing later, because billing lags by minutes to over a day.
- Content capture, provider payload logging, retention and sink region are audited state (P1 to P5).
- Pin the telemetry conventions as finding 3 proposes for #36 G12, and smoke-test metric names after an engine or instrumentation upgrade.

### #39 Cost Estimate

**Research complete:** [#436](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/436) delivered the reviewed record at signed [`9a4fa8af`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/9a4fa8afe71136611bdab50b824700777d39397d). The [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6257325094) maps all ten original criteria and the actual [#39 → #42 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/42#issuecomment-6257029583), whose corrected-source delivery condition is now satisfied. Current price eligibility, complete priced coverage, calibrated sizing and source-use permission remain separately qualified; #40/SB-3 representation and #42 implementation/adoption retain their own gates.

- Keep every price as published and derive normalised per-unit prices with the factor recorded (30 unit rows, U1 to U30).
- Build low, expected and high from quantities and builder-set drivers, with prices fixed. On the reference workload the API estimate spans 4.3 times (W1: 6,700 to 29,000 USD a month).
- Show capacity next to its utilisation and break-even. Peak-sized Azure provisioned throughput runs at about a third of its capacity, so reserved PTUs cost about 3 times pay-as-you-go and hourly PTUs about 8.5 times (W2).
- Match each price to its actual offering, meter, source currency, region, effective period and account/plan conditions, under the [accepted #41 → #39 receiving boundary](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6254388872). An unanswered budget currency stays unknown; the USD preview supplies no source-currency, FX-rate or region default. Historical conversion and reference-region proposals require their own qualified policy before use. Retain the stated tax treatment and date each price. The operations lines from #35 to #38 add 9 to 22 percent in the recorded API scenario (W4), rather than defining a general overhead rate.
- W5 separates provider-specific fine-tuning quantities and minimums from subsequent hosting, including a stated 30-day period. Every worked-scenario figure is re-computed by [`cost-scenarios.py`](cost-scenarios.py) from [`cost-estimate.scenarios.json`](cost-estimate.scenarios.json).

## Rules contributed to #40

**Rule interpretation (candidate revision 0.2).** Each row has one fixed v1 severity (`error`, `warning` or `info`), separate from outcome (`pass`, `fail`, `unknown`, `skipped`). For retained violation-form rows, a known applicable violation is `fail`; known absence of that violation is `pass`; non-applicability is `skipped` with `not_applicable`; missing eligible inputs are `unknown` with `missing_evidence` and `on_unknown: review`. Current positive-assertion profiles retain their recorded applicability and reason semantics; [Guardrails](guardrails.md#evaluation-and-representation-rules) converts violation predicates through typed negation before terminal evaluation. Resolve conflicts using #41's scope, version/date and authority order before taking the conservative equal-rank numeric value, flagged disputed. In source-conflict resolution, only missing eligible evidence or genuine unresolved ties yield `unknown`; conflict alone does not. Hypotheses remain unaccepted and cannot drive production verdicts. Suffixed rows split the old condition; the unsuffixed ID is retained for its stated scope. No frozen schema or executable ruleset changes. See merged [T0 modes and evidence policy](../T0-configuration/deployment-mode.md), [#126 rule review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126) and [#127 evidence review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/127); those original partial records retain their scoped decisions. #41's research policy is complete through [#403](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/403); #40's research record is complete in [receipt 6257213742](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6257213742); remaining component-specific proposal disposition and versioned representation/rule integration retain their own acceptance requirements.

| record | source-checked rules | hypotheses |
|---|---|---|
| #35 Guardrails | 36 candidates (original IDs plus explicit suffixed splits) | 3 candidates (including explicit splits) |
| #36 Evaluation | 94 candidates (original IDs plus explicit suffixed splits) | 13 candidates (including explicit splits) |
| #37 Deployment | 90 candidates (original IDs plus explicit suffixed splits) | 21 candidates (including explicit splits) |
| #38 Monitoring | 71 candidates (original IDs plus explicit suffixed splits) | 25 candidates (including explicit splits) |
| #39 Cost Estimate | 45 candidates (original IDs plus explicit suffixed splits) | 11 candidates (including explicit splits) |

Conditional severity cells have been replaced with fixed severities and explicit applicability/outcome semantics. Suffixed candidates preserve the separate conditions; #40 still reviews adoption.

Missing ids were retired while drafting or during QC: a hypothesis became a source-checked rule, a rule restated another record's rule, or a source settled the question. Ids are not reused.

The records also hand #40 these enums and fields: the guardrail category and failure-behaviour enums (#35), the evaluation type enum and the evaluator-placement field (#36), the adopted serving-mode definition (#37), and the alert-class and threshold-source enums (#38).

## Handoffs and receiving status

#34 is done only when the affected owners confirm its workstream handoffs and the remaining child criteria are complete. Guardrails' [R1–R6 receiving record](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6256149374) covers its three literal #36/#37/#38 directions and additional #40/#2/#39/#41 interfaces. Evaluation's four declared downstream interfaces have scoped receiving decisions: [#37 gates and rollout allocation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6254282660), [#38 online scoring and G12](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/38#issuecomment-6254283671), [#32 frozen evaluation inputs and leakage evidence](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/32#issuecomment-6254284924), and [#41's adopted reproducibility minimum](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/127#issuecomment-6242306958). These receipts preserve their actual revisions and conditions; the remaining cross-component requests and additional proposals below are separate.

### Three parent workstream boundaries — 2026-10-19

The live [#34 issue](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34) declares the three boundaries below. This dated reconciliation addresses those responsibility and receiving interfaces. It does not treat the broader component requests in the retained table below as one completed handoff, or replace any component's actual source/receiving history and selected-target follow-ups.

Inputs are the accepted records at [`ffe64042`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/ffe6404271c50c6ee4f44043e0d52a842df6afba): [cost](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/ffe6404271c50c6ee4f44043e0d52a842df6afba/research/T6-deployment-operations/cost-estimate.md), [evaluation](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/ffe6404271c50c6ee4f44043e0d52a842df6afba/research/T6-deployment-operations/evaluation.md), [workload](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/ffe6404271c50c6ee4f44043e0d52a842df6afba/research/T0-configuration/workload-use-case.md) and [evidence policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/ffe6404271c50c6ee4f44043e0d52a842df6afba/research/T0-configuration/catalog-data-sources.md). Their exact Git blobs are respectively `dc97759ed922326ddf8d270e1861f627725a5a31`, `b50e59f03ead7799944ee82b94fc31a2fd93a7dc`, `d8e86c8794ce175020e3457e62cba86c124f82ca` and `c862112312d45bbe13b9e9261b8f83ee581cafa6`. Earlier receipts below retain their own input revisions and reviewer attributions; this is a current method/receipt review, not a repeated vendor-source audit.

| Parent boundary | Accepted method and actual receiving evidence | Limits retained |
| --- | --- | --- |
| H34-1: #39 owns pricing units, aggregation and uncertainty; component issues supply prices; #41 governs provenance and freshness | The completed #39 record retains each component's dated price and conditions, records its unit conversion and workload quantity, and separates one-off from recurring periods and scenario uncertainty. Its [current receiving reconciliation](cost-estimate.md#actual-incoming-decisions-and-their-retained-scope) indexes the actual component interfaces. [#41 → #39 receipt 6254388872](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6254388872) explicitly accepts eligible selected-offering rates under the evidence policy. This confirms responsibility for the method; supplying a price remains with its actual component/source. | Keep exact item/version, meter, currency, region, date, account conditions and source-use eligibility. Unknown required quantities are not sized; missing eligible rates are not priced. Neither becomes zero or a complete budget result. No preview currency, FX, region, throughput calibration or complete catalog coverage is adopted. |
| H34-2: #36 owns evaluation methodology, including reproducibility of benchmark comparisons cited in catalogs | The completed #36 record separates workload evaluations, safety checks, latency/cost observations and regression decisions, with exact R1–R15 comparison inputs. [#36 → #41 receipt 6242306958](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/127#issuecomment-6242306958) adopts the reproducibility minimum and one independent control; the [current #41 → #36 decision 6254392681](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36#issuecomment-6254392681) confirms its use with claim-level eligibility. | Published scores remain selection priors unless an eligible actual run supports the intended comparison. Keep dataset/task, model/runtime, prompt/precision/context, attempts/load, metric/reducer, uncertainty, date and claim grade. Missing eligible evidence remains unknown; known incomparable tuples cannot support a ranking. The additional tier/sizing proposals, numerical thresholds and any executable quality gate require their own decisions. |
| H34-3: #2 supplies workload targets; #36 evaluates against those targets | The current workload record preserves primary workload and independent axes, declared target/answer states and the W-R10 evaluation interface. Actual [#2 co-owner receipt 6245701804](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6245701804) and [#36/#39 co-owner receipt 6247690142](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6247690142) accept the narrowed evaluation and quantity interfaces; the [#2 completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6256591575) retains their scopes. | Builder-set targets, presets, tool defaults and measured outcomes remain distinct. Use the actual metric direction, workload/dataset and serving tuple; keep judge identity and human agreement where required. Requests in flight are not arrival rate or resident sequences; input assembly and disjoint billable output classes must not double count. Unknown quality evidence does not satisfy a target, and the target itself supplies no measurement. |

**Actual parent-level confirmation:** [receipt 6258627271](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34#issuecomment-6258627271), posted on 2026-10-19 at 02:53:21 UTC, records the coordinating in-session engineer's independent review of the four exact method inputs, all five earlier cited receiving bodies, the initial summary and its Deployment-completion successor. H34-1, H34-2 and H34-3 are accepted within their stated research scope. This is that engineer's actual delegated disposition, not a new reply attributed to the named historical assignees. Source rights, selected-build implementation, additional #40 fields/rules and deployment execution retain their own requirements. Reviewed summary delivery, configured validation and current issue/Project reconciliation remain separate from this source/receiving decision.

### Retained component-level requests

| to | what T6 hands over | from |
|---|---|---|
| #2 T0 | fields the rules and quantities need: data sensitivity, residency, tenancy, language, regulated-workload flag (#35); evaluator placement and region at provisioning (#36); peak volume, build life and migration window, licensee domicile, MAU or revenue, end-user countries (#37); availability objective, SLO window, freshness tolerance, retention, budget hard stop, high-risk status (#38); quantity roles and case drivers (#39) | all |
| #40 Schema | the rules and enums above; the adopted serving-mode definition | all |
| #41 Data sources | claim-level evidence grades and price-source eligibility to review; R1–R15 and one-factor semantics are already adopted in merged #41 and retained in #36; additional reproducibility tiers A to C and sizing remain proposals | all |
| #42 Saved builds | accepted warnings with their reasons (#35); the price snapshot fields and re-pricing behaviour (#39) | #35, #39 |
| #32 and #33 (T5) | `D-20` accepted, narrowed, in #36: #36 freezes and hashes the evaluation set, T5 runs the leakage check (E-R44, G1); `A-20` accepted in #36 as a G5 input; `A-13` (the Foundry classic FAQ says a fine-tuned deployment can be deleted after more than 15 inactive days while the customized model is retained) accepted in #37 as D-R87; #39 W5 now supplies separate Together and Azure training/hosting illustrations, with receiving acceptance and unpriced deployment-specific items recorded separately | #36, #37, #39 |
| T1 to T5 owners | lifecycle dates per host, engine maintenance status, embedding versions, feature availability per platform, base-model matching (#37); the signals each component must expose, by mode (#38) | #37, #38 |

## Open questions

Grouped by who can answer them. Every record has an owner column in its Open questions table; #35 to #37 also record when an answer is needed. Issue-owner references resolve to the live GitHub assignees and do not reassign work. Each record's table retains the question and its details.

**#40 owner**
- Use the [completed #2 workload record](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/2#issuecomment-6256591575) and its accepted receiving interfaces as the input basis. Additional T6 fields remain proposals for explicit versioned #40 adoption and selected-build implementation; #2's research completion does not install them.
- Serving mode is decided by merged #81; apply the per-component definition above.
- Accept the placement rules, the alert-class enum and the threshold-source enum (#38).
- Review the candidate rule splits and reason codes through #40; fixed severity is already the required convention, not an open choice.

**#41 owner**
- Apply the completed #41 claim-level grading, source eligibility, freshness and permitted-use policy to each selected fact or price. Vendor accuracy claims, independent reproduction and permission to display remain separately qualified; policy completion does not grant rights or refresh a component's evidence.
- Sizing rule for evaluation sets and reproducibility tier boundaries (#36).
- Apply the [#60 source-specific reuse decisions](../market/rights-validation.md) to AWS/Azure price reuse (#39); keep unaddressed rights questions with #60/#41. No broader redistribution permission is implied.

**#42 owner**
- Re-evaluation on changed pricebook, snapshot, ruleset, rights decision or build edits (#42); prices retain as-of dates, without a time-window expiry.

**Maintainers**
- Any currency conversion or region-selection policy beyond the accepted #41/#39 interface needs explicit #39/#40 review, including eligible source, date, direction, rounding and fee/tax treatment. Missing currency or region evidence cannot be supplied by a preview preference or historical reference-region example.
- Which prompt storage pattern the builder defaults to (#37).

**Legal reviewer named by the #34 owner**
- Log duties beyond GDPR Art. 5, 25 and 30, high-risk status under the AI Act, and national log rules (#38).
- The AI Act Article 50 text and the provider-versus-deployer role, and the Llama EU multimodal clauses (#37).

**Provider-side questions (#34 owner)**
- Guardrail failure modes when a service is unreachable; Anthropic retention wording; the Cloudflare AI Gateway Guardrails categories; a Lakera flag-only mode (#35).
- Red-team authorisation routes; eval-dataset retention under zero-retention settings; Bedrock evaluation regions and judge prices (#36).
- Selected-offering SLA applicability and model-specific latency targets: [the Bedrock page and October 2026 Foundry Models section are now source checked](deployment-sla-source-check.md), without assuming separate Azure OpenAI coverage. OpenAI policy pages that returned HTTP 403; the NVIDIA NIM production licence conflict (#37, also asked by #39); GPU quota lead times (#37).
- Azure abuse-monitoring retention and log schema; vendor retention and regions for Arize AX and Helicone (#38).
- Bedrock Provisioned Throughput model-unit throughput, which needs an AWS account team; the Azure VM reservation row reading (#39).

**Answered by a later record**
- Guardrail pricing units (#35) are normalised in #39 (L56 to L60).
- Pricing and measurement interfaces for in-process spend (#38) are accepted in the [#39 → #38 priced-input decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/38#issuecomment-6256810734) and the separate [#38 → #39 accounting-input decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6256811740). Their scoped meter, currency, billing-window and coverage requirements preserve missing quantities and rates. No conversion policy, default currency or region, or complete catalog coverage is adopted.
- Rollout-gate allocation is accepted for Evaluation's research interface in [#37 receipt 6254282660](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6254282660): #37 owns rollout mechanics, #36 owns quality decisions and #38 owns monitoring thresholds. Actual deployment/release acceptance remains separate.
- Evidence rows "as cited in the pack" (#36) now all carry URLs (#36 Evidence).

## Workstream done when

- [x] All sub-issues are closed with merged decision records: #35 is research-complete through #413, #36 through #402, #37 through #447, #38 through #442 and #39 through #436. The actual #37 completion receipt above and the 2026-10-19 native child readback confirm all five are closed; their selected-build and source-use limits remain separate.
- [x] The handoffs above are confirmed by the affected workstream owners: the three literal parent boundaries H34-1–H34-3 have the actual scoped confirmation in receipt 6258627271. Broader component requests retain their separately recorded dispositions and follow-ups.
- [x] A workstream summary at `research/T6-deployment-operations/README.md` lists decisions, rules contributed to #40, and open questions (this page).
