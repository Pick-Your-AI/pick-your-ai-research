# T6 Deployment & Operations

Workstream: [#34](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34) · Contract: 1.0.0 · Owners: @PUSHINGSQUARES, @appletechie (issue assignees)
Status: five decision records merged through [#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121), with rule-semantics corrections merged through [#190](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/190); component-issue acceptance and handoffs remain under review. Last researched: 2026-10-18. Original source sweeps: 2026-10-16/17; source additions and the W5 illustration were checked on 2026-10-18 as identified in each record.

Product question: is the build safe, measurable, deployable, observable, and affordable?

This summary lists the decisions in the five T6 records, the rules they contribute to [#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40), the handoffs that other owners need to confirm, and the open questions. The records are the source; this page only points into them.

The [2026-10-18 sibling reconciliation](sibling-reconciliation.md) preserves the corrected alternative proposals from #113/#115/#116/#118/#120 at immutable revisions and records the four source findings also carried by concurrent #191, with a pinned harness readback and explicit Gemini API-family telemetry. Its supplemental sources are separate from the inventory counts below; PR supersession does not accept a receiving handoff or complete an issue.

## Records

| issue | record | v1 kind | decision it supports | source-checked rules | hypotheses | evidence rows |
|---|---|---|---|---|---|---|
| [#35](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35) | [Guardrails](guardrails.md) | `guardrail` | Which safety, security and policy controls should this build include, and what does the builder show when one is missing? | 36 | 3 | 30 |
| [#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36) | [Evaluation](evaluation.md) | `evaluation_suite` | How will the user know whether the build meets its quality, safety, latency and cost targets? | 94 | 13 | 292 |
| [#37](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37) | [Deployment](deployment.md) | `deployment_target` | What does it take to ship this build, and is it ready? | 90 | 21 | 222 |
| [#38](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/38) | [Monitoring](monitoring.md) | `monitoring_stack` | Which signals must be watched once the build runs? | 71 | 25 | 286 |
| [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39) | [Cost Estimate](cost-estimate.md) | `cost_policy` | What will this build cost, under stated assumptions, and with what uncertainty? | 43 | 11 | 202 |
| | total | | | 334 | 73 | 1,032 |

The original #121 submission records a QC pass that re-opened its cited URLs and applied the corrections in the records. The 2026-10-18 follow-ups rechecked their added findings and pricing inputs; they do not claim a new reread of every older source. The counts above describe the current rule, hypothesis and evidence tables; inline primary-source links and linked evidence appendices are additional references. Every evidence row carries an interim grade under `docs/RESEARCH_METHOD.md` (#41 owns the final policy). Where a row mixes types, or a page was not opened or was read from a mirror, the grade says so. These records do not supply a T6 runtime experiment. Figures are published (copied from a dated source), estimated (derived here, with the formula shown) or builder-set; automated recomputation of the scenarios is arithmetic validation.

## Decisions

### #35 Guardrails

- A catalog of controls plus compatibility rules, not a recommended product. No single product covers the catalog; for example, harm classifiers lack injection and PII detection (G-R18).
- A baseline of controls applies to every build. Further controls apply when T3 retrieval or T4 tools and agents are active.
- A missing control is a rule result, shown in the build's risk review. A `warning` can be accepted with a reason saved in the build (#42). A failed `error` rule blocks the build until the selection changes. An `unknown` result is shown with its open question and owner, never as a pass.
- Controls that the platform supplies in API or managed mode are shown as provided by the platform, with their source (G-R19).

### #36 Evaluation

- Evaluation is a per-build plan with four parts: the workload row, the safety pair, a latency-and-cost measurement, and a regression gate on a dataset the user owns.
- No primary source gives a recommended pass threshold, so every threshold is builder-set.
- Deployment gates G1 to G12 are handed to #37. Judges come from a different model family where the stack allows, with a pinned version and a human-labelled agreement sample before a judged metric gates a release (G3).
- Public benchmarks are selection priors only, shown with their reproducibility fields and tier (G11). OpenAI Evals is excluded because it is being retired (read-only from 2026-10-31).

### #37 Deployment

- Mode follows the serving-component decision in [T0](../T0-configuration/deployment-mode.md), merged through #81: user-operated serving is `self_hosted`; provider-operated dedicated or reserved capacity is `managed`; provider-operated shared capacity is `api`. Billing units and customer-owned deployment objects do not determine mode. Hyperscaler on-demand/shared inference is `api`; dedicated endpoints and provisioned throughput are `managed`. Training runs do not set serving mode. Select the actual offering/capacity rather than inferring a mode from the provider name.
- Order of work runs from T0 through terms, identity, pins, the mode's platform steps, gates, monitoring and rollback, and only then traffic (S1 to S13).
- Default to a runtime identity in every mode, and to the pin that cannot move: a snapshot id (API), an explicit deployment version (managed), or an image digest plus a weights commit hash (self-hosted).
- Rollout mechanics belong to #37; promotion criteria belong to #36 and #38. Readiness rows show one of pass, fail, not applicable, unknown or not measured.

### #38 Monitoring

- Page on three things only: SLO burn on client-measured latency and errors, a spend stop that is rejecting requests, and a serving pool with no ready endpoints.
- Measure latency at the client, because platform latency metrics differ in start point and statistic. Compute spend in-process and reconcile it with billing later, because billing lags by minutes to over a day.
- Content capture, provider payload logging, retention and sink region are audited state (P1 to P5).
- Pin the telemetry conventions as finding 3 proposes for #36 G12, and smoke-test metric names after an engine or instrumentation upgrade.

### #39 Cost Estimate

- Keep every price as published and derive normalised per-unit prices with the factor recorded (30 unit rows, U1 to U30).
- Build low, expected and high from quantities and builder-set drivers, with prices fixed. On the reference workload the API estimate spans 4.3 times (W1: 6,700 to 29,000 USD a month).
- Show capacity next to its utilisation and break-even. Peak-sized Azure provisioned throughput runs at about a third of its capacity, so reserved PTUs cost about 3 times pay-as-you-go and hourly PTUs about 8.5 times (W2).
- Price in USD, display in the T0 currency, exclude tax and date every price. The operations lines from #35 to #38 add 9 to 22 percent to an API build (W4).
- W5 separates provider-specific fine-tuning quantities and minimums from subsequent hosting, including a stated 30-day period. Every worked-scenario figure is re-computed by [`cost-scenarios.py`](cost-scenarios.py) from [`cost-estimate.scenarios.json`](cost-estimate.scenarios.json).

## Rules contributed to #40

**Rule interpretation (candidate revision 0.2).** Each row has one fixed v1 severity (`error`, `warning` or `info`), separate from outcome (`pass`, `fail`, `unknown`, `skipped`). The condition describes the violation: known applicable violation is `fail`; known absence of that violation is `pass`; non-applicability is `skipped` with `not_applicable`; missing eligible inputs are `unknown` with `missing_evidence` and `on_unknown: review`. Resolve conflicts using #41's scope, version/date and authority order before taking the conservative equal-rank numeric value, flagged disputed. Only missing eligible evidence or genuine unresolved ties yield `unknown`; conflict alone does not. Hypotheses remain unaccepted and cannot drive production verdicts. Suffixed rows split the old condition; the unsuffixed ID is retained for its stated scope. No frozen schema or executable ruleset changes. See merged [T0 modes and evidence policy](../T0-configuration/deployment-mode.md), [#126 rule review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126) and [#127 evidence review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/127); both PRs are merged partial decision records. Their scoped owner decisions apply, while open #40/#41 acceptance and next-version adoption remain separate.

| record | source-checked rules | hypotheses |
|---|---|---|
| #35 Guardrails | 36 candidates (original IDs plus explicit suffixed splits) | 3 candidates (including explicit splits) |
| #36 Evaluation | 94 candidates (original IDs plus explicit suffixed splits) | 13 candidates (including explicit splits) |
| #37 Deployment | 90 candidates (original IDs plus explicit suffixed splits) | 21 candidates (including explicit splits) |
| #38 Monitoring | 71 candidates (original IDs plus explicit suffixed splits) | 25 candidates (including explicit splits) |
| #39 Cost Estimate | 43 candidates (original IDs plus explicit suffixed splits) | 11 candidates (including explicit splits) |

Conditional severity cells have been replaced with fixed severities and explicit applicability/outcome semantics. Suffixed candidates preserve the separate conditions; #40 still reviews adoption.

Missing ids were retired while drafting or during QC: a hypothesis became a source-checked rule, a rule restated another record's rule, or a source settled the question. Ids are not reused.

The records also hand #40 these enums and fields: the guardrail category and failure-behaviour enums (#35), the evaluation type enum and the evaluator-placement field (#36), the adopted serving-mode definition (#37), and the alert-class and threshold-source enums (#38).

## Handoffs awaiting confirmation

#34 is done only when the affected owners confirm these.

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

**#2 owner**
- Add the T0 fields listed under Handoffs (#35, #37, #38, #39).

**#40 owner**
- Serving mode is decided by merged #81; apply the per-component definition above.
- Accept the placement rules, the alert-class enum and the threshold-source enum (#38).
- Review the candidate rule splits and reason codes through #40; fixed severity is already the required convention, not an open choice.

**#41 owner**
- The final evidence-grade policy. Every evidence row carries an interim grade under `docs/RESEARCH_METHOD.md`; #41 confirms them, including whether vendor accuracy claims may be displayed (#35, #37, #38).
- Sizing rule for evaluation sets and reproducibility tier boundaries (#36).
- Apply the [#60 source-specific reuse decisions](../market/rights-validation.md) to AWS/Azure price reuse (#39); keep unaddressed rights questions with #60/#41. No broader redistribution permission is implied.

**#42 owner**
- Re-evaluation on changed pricebook, snapshot, ruleset, rights decision or build edits (#42); prices retain as-of dates, without a time-window expiry.

**Maintainers**
- The default currency and region: USD pricing, T0 budget currency for display, and a region fallback (#39).
- Confirm the rollout scope split: mechanics in #37, promotion criteria in #36 and #38 (#37).
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
- Price inputs for in-process spend (#38) are supplied by #39 (catalog T1 and T2, FX policy, snapshot fields).
- Rollout gates (#36) are scoped in #37 ("Rollout gates: the scope decision #36 asked for"), pending the maintainers' confirmation above.
- Evidence rows "as cited in the pack" (#36) now all carry URLs (#36 Evidence).

## Workstream done when

- [ ] All sub-issues are closed with merged decision records: the five canonical records are merged through #121, and #190 merged the rule-semantics corrections. The component issues remain open while their remaining acceptance criteria and handoffs are reconciled; a merged record alone does not close an issue.
- [ ] The handoffs above are confirmed by the affected workstream owners.
- [x] A workstream summary at `research/T6-deployment-operations/README.md` lists decisions, rules contributed to #40, and open questions (this page).
