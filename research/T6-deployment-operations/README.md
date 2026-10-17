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
- A missing control is a rule result, shown in the build's risk review. A `warning` can be accepted with a reason saved in the build (#42). An `incompatible` result blocks the build until the selection changes. An `unknown` result is shown with its open question and owner, never as a pass.
- Controls that the platform supplies in API or managed mode are shown as provided by the platform, with their source (G-R19).

### #36 Evaluation

- Evaluation is a per-build plan with four parts: the workload row, the safety pair, a latency-and-cost measurement, and a regression gate on a dataset the user owns.
- No primary source gives a recommended pass threshold, so every threshold is builder-set.
- Deployment gates G1 to G12 are handed to #37. Judges come from a different model family where the stack allows, with a pinned version and a human-labelled agreement sample before a judged metric gates a release (G3).
- Public benchmarks are selection priors only, shown with their reproducibility fields and tier (G11). OpenAI Evals is excluded because it is being retired (read-only from 2026-10-31).

### #37 Deployment

- Mode working rule: a build with a customer-owned deployment object is managed, one without is API, and self-hosted means the build runs the engine. This places hyperscaler-hosted inference, pending #40.
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

All five records use the same rule format at rule version 0.1: rule id, participants, condition, severity, explanation, suggested correction, source. Severity is one of compatible, warning, incompatible or unknown. Each record separates source-checked rules (the cited page was opened on its access date and states the rule) from hypotheses (no opened source states it yet). Source checked does not mean independently reproduced; it follows the interim #41 definition adopted in the [#75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). A rule owned by one record is cited by id in the others, not restated.

| record | source-checked rules | hypotheses |
|---|---|---|
| #35 Guardrails | G-R1 to G-R34 (34) | G-H7, G-H9 (2) |
| #36 Evaluation | E-R1 to E-R86 (86) | E-H1 to E-H14 except E-H9 (13) |
| #37 Deployment | D-R1 to D-R87 (87) | D-H1 to D-H24 except D-H5, D-H18, D-H19 (21) |
| #38 Monitoring | M-R1 to M-R72 except M-R34 (71) | M-H1 to M-H25 (25) |
| #39 Cost Estimate | C-R1 to C-R43 (43) | C-H1, C-H5 to C-H10, C-H12, C-H13, C-H15, C-H17 (11) |

Contract v1 arrived after these records were drafted. Its Ruleset has severities `error`, `warning` and `info`, and a separate `on_unknown` behaviour. Each record's Compatibility proposals section proposes the same reading for #40: `incompatible` is `error`, `warning` is `warning`, `unknown` is `warning` with `on_unknown: review` until the evidence settles it, and a conditional severity becomes two rules. No v1 Ruleset JSON is included; #40 reviews the rules first.

Missing ids were retired while drafting or during QC: a hypothesis became a source-checked rule, a rule restated another record's rule, or a source settled the question. Ids are not reused.

The records also hand #40 these enums and fields: the guardrail category and failure-behaviour enums (#35), the evaluation type enum and the evaluator-placement field (#36), the mode working rule (#37), and the alert-class and threshold-source enums (#38).

## Handoffs awaiting confirmation

#34 is done only when the affected owners confirm these.

| to | what T6 hands over | from |
|---|---|---|
| #2 T0 | fields the rules and quantities need: data sensitivity, residency, tenancy, language, regulated-workload flag (#35); evaluator placement and region at provisioning (#36); peak volume, build life and migration window, licensee domicile, MAU or revenue, end-user countries (#37); availability objective, SLO window, freshness tolerance, retention, budget hard stop, high-risk status (#38); quantity roles and case drivers (#39) | all |
| #40 Schema | the rules and enums above; the mode working rule | all |
| #41 Data sources | interim evidence grades to confirm for every record; reproducibility tiers A to C; price sources, dates and terms | all |
| #42 Saved builds | accepted warnings with their reasons (#35); the price snapshot fields and re-pricing behaviour (#39) | #35, #39 |
| #32 and #33 (T5) | `D-20` accepted, narrowed, in #36: #36 freezes and hashes the evaluation set, T5 runs the leakage check (E-R44, G1); `A-20` accepted in #36 as a G5 input; `A-13` (Foundry deletes a fine-tuned deployment after 15 idle days) accepted in #37 as D-R87; a T5 cost scenario is a follow-up in #39 | #36, #37, #39 |
| T1 to T5 owners | lifecycle dates per host, engine maintenance status, embedding versions, feature availability per platform, base-model matching (#37); the signals each component must expose, by mode (#38) | #37, #38 |

## Open questions

Grouped by who can answer them. #38 and #39 name an owner for each question; #35 to #37 give a deadline instead, so their questions are placed here by subject. Each record's Open questions table has the reason and the detail.

**#2 owner**
- Add the T0 fields listed under Handoffs (#35, #37, #38, #39).

**#40 owner**
- Is hyperscaler-hosted inference API or managed? #37 uses a working rule (#37).
- Accept the placement rules, the alert-class enum and the threshold-source enum (#38).
- 28 rules and 3 hypotheses in #35 to #37 carry a conditional severity, for example "warning; incompatible when …". #38 and #39 use exactly one severity per rule. Decide whether #40 allows the conditional form or the rules are split. Rules: G-R13, G-R21, G-R23, G-R26 and G-H9 (#35); E-R3, E-R6, E-R8, E-R10, E-R11, E-R12, E-R21, E-R30, E-R48, E-R60, E-R70, E-R72, E-R74, E-R82, E-R83 and E-H2 (#36); D-R10, D-R13, D-R25, D-R34, D-R43, D-R69, D-R72, D-R77, D-R79 and D-H22 (#37).

**#41 owner**
- The final evidence-grade policy. Every evidence row carries an interim grade under `docs/RESEARCH_METHOD.md`; #41 confirms them, including whether vendor accuracy claims may be displayed (#35, #37, #38).
- Sizing rule for evaluation sets and reproducibility tier boundaries (#36).
- Whether AWS and Azure price data may be redistributed (#39).

**#42 owner**
- The stale-after window for saved builds (#39).

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
