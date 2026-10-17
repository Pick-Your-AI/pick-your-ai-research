# T6 Deployment & Operations

Workstream: [#34](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34) · Contract: 1.0.0 · Owners: @PUSHINGSQUARES, @appletechie (issue assignees)
Status: ready for review · Last researched: 2026-10-17 · Sources accessed 2026-10-16 (and 2026-10-17 for re-checked rows in #39)

Product question: is the build safe, measurable, deployable, observable, and affordable?

This summary lists the decisions in the five T6 records, the rules they contribute to [#40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40), the handoffs that other owners need to confirm, and the open questions. The records are the source; this page only points into them.

## Records

| issue | record | v1 kind | decision it supports | source-checked rules | hypotheses | evidence rows |
|---|---|---|---|---|---|---|
| [#35](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35) | [Guardrails](guardrails.md) | `guardrail` | Which safety, security and policy controls should this build include, and what does the builder show when one is missing? | 34 | 2 | 30 |
| [#36](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/36) | [Evaluation](evaluation.md) | `evaluation_suite` | How will the user know whether the build meets its quality, safety, latency and cost targets? | 86 | 13 | 290 |
| [#37](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37) | [Deployment](deployment.md) | `deployment_target` | What does it take to ship this build, and is it ready? | 87 | 21 | 222 |
| [#38](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/38) | [Monitoring](monitoring.md) | `monitoring_stack` | Which signals must be watched once the build runs? | 71 | 25 | 285 |
| [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39) | [Cost Estimate](cost-estimate.md) | `cost_policy` | What will this build cost, under stated assumptions, and with what uncertainty? | 43 | 11 | 198 |
| | total | | | 321 | 72 | 1,025 |

Each record was checked by a QC pass that re-opened every cited URL and tried to refute each row. The corrections are applied in the records. Every evidence row carries an interim grade under `docs/RESEARCH_METHOD.md` (#41 owns the final policy): 1,002 Primary documentation, 19 Independent measurement, 4 Vendor claim. Where a row mixes types, or a page was not opened or was read from a mirror, the grade says so. No T6 research ran a system, so no number in these records is measured. Figures are published (copied from a dated source), estimated (derived here, with the formula shown) or builder-set.

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
- Every worked-scenario figure is re-computed by [`cost-scenarios.py`](cost-scenarios.py) from [`cost-estimate.scenarios.json`](cost-estimate.scenarios.json).

## Rules contributed to #40

**Rule interpretation (candidate revision 0.2).** Each row has one fixed v1 severity (`error`, `warning` or `info`), separate from outcome (`pass`, `fail`, `unknown`, `skipped`). The condition describes the violation: known applicable violation is `fail`; known absence of that violation is `pass`; non-applicability is `skipped` with `not_applicable`; missing eligible inputs are `unknown` with `missing_evidence` and `on_unknown: review`. Resolve conflicts using #41's scope, version/date and authority order before taking the conservative equal-rank numeric value, flagged disputed. Only missing eligible evidence or genuine unresolved ties yield `unknown`; conflict alone does not. Hypotheses remain unaccepted and cannot drive production verdicts. Suffixed rows split the old condition; the unsuffixed ID is retained for its stated scope. No frozen schema or executable ruleset changes. See merged [T0 modes and evidence policy](../T0-configuration/deployment-mode.md), [#126 rule review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126) and [#127 evidence review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/127); the latter two remain open review proposals, while the cited interim owner decisions apply.

| record | source-checked rules | hypotheses |
|---|---|---|
| #35 Guardrails | 35 candidates (original IDs plus explicit suffixed splits) | 3 candidates (including explicit splits) |
| #36 Evaluation | 92 candidates (original IDs plus explicit suffixed splits) | 13 candidates (including explicit splits) |
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
| #41 Data sources | interim evidence grades to confirm for every record; reproducibility tiers A to C; price sources, dates and terms | all |
| #42 Saved builds | accepted warnings with their reasons (#35); the price snapshot fields and re-pricing behaviour (#39) | #35, #39 |
| #32 and #33 (T5) | `D-20` accepted, narrowed, in #36: #36 freezes and hashes the evaluation set, T5 runs the leakage check (E-R44, G1); `A-20` accepted in #36 as a G5 input; `A-13` (Foundry deletes a fine-tuned deployment after 15 idle days) accepted in #37 as D-R87; a T5 cost scenario is a follow-up in #39 | #36, #37, #39 |
| T1 to T5 owners | lifecycle dates per host, engine maintenance status, embedding versions, feature availability per platform, base-model matching (#37); the signals each component must expose, by mode (#38) | #37, #38 |

## Open questions

Grouped by who can answer them. #38 and #39 name an owner for each question; #35 to #37 give a deadline instead, so their questions are placed here by subject. Each record's Open questions table has the reason and the detail.

**#2 owner**
- Add the T0 fields listed under Handoffs (#35, #37, #38, #39).

**#40 owner**
- Serving mode is decided by merged #81; apply the per-component definition above.
- Accept the placement rules, the alert-class enum and the threshold-source enum (#38).
- Review the candidate rule splits and reason codes through #40; fixed severity is already the required convention, not an open choice.

**#41 owner**
- The final evidence-grade policy. Every evidence row carries an interim grade under `docs/RESEARCH_METHOD.md`; #41 confirms them, including whether vendor accuracy claims may be displayed (#35, #37, #38).
- Sizing rule for evaluation sets and reproducibility tier boundaries (#36).
- Whether AWS and Azure price data may be redistributed (#39).

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
- Azure OpenAI and Bedrock SLA figures; OpenAI policy pages that returned HTTP 403; the NVIDIA NIM production licence conflict (#37, also asked by #39); GPU quota lead times (#37).
- Azure abuse-monitoring retention and log schema; vendor retention and regions for Arize AX and Helicone (#38).
- Bedrock Provisioned Throughput model-unit throughput, which needs an AWS account team; the Azure VM reservation row reading (#39).

**Answered by a later record**
- Guardrail pricing units (#35) are normalised in #39 (L56 to L60).
- Price inputs for in-process spend (#38) are supplied by #39 (catalog T1 and T2, FX policy, snapshot fields).
- Rollout gates (#36) are scoped in #37 ("Rollout gates: the scope decision #36 asked for"), pending the maintainers' confirmation above.
- Evidence rows "as cited in the pack" (#36) now all carry URLs (#36 Evidence).

## Workstream done when

- [ ] All sub-issues are closed with merged decision records: the five records are in review; none is merged yet.
- [ ] The handoffs above are confirmed by the affected workstream owners.
- [x] A workstream summary at `research/T6-deployment-operations/README.md` lists decisions, rules contributed to #40, and open questions (this page).
