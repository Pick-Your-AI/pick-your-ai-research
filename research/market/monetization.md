# Monetization and neutral recommendations

Status: research proposal for [#54](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/54). Initial desk research: 2026-10-16; the separate 2026-10-18 source and proposal review is identified below, and section 8 preserves an additional bounded four-page offer readback. No accounts, quotes, agreements, outreach or willingness-to-pay data. Confidence overall: Low for commercial viability; the observed offer structures have the narrower confidence stated in sections 2 and 8.

This note compares business-model **structure**. It records no prices, rates, fees, discounts or allowances. Monetary rates belong in dated pricebooks only when complete units and conditions exist ([`docs/RESEARCH_WORKFLOW.md`](../../docs/RESEARCH_WORKFLOW.md)); price freshness and total-cost scenarios are owned by [#64](pricing-validation.md), and pricing/cost semantics by [#39](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39). Country, taxes, discounts, storage, egress, idle capacity, support and commitment terms must be evaluated for an actual quote.

Evidence grades follow [`docs/RESEARCH_METHOD.md`](../../docs/RESEARCH_METHOD.md) (Primary documentation, Vendor claim, Independent measurement, Estimate). "Hypothesis" is a claim status, not a grade. A pricing page is primary documentation of what is **offered**; it is not evidence of what customers buy, retain or would pay ([#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63)).

## 1. Model comparison

| Model | Evidence / comparable | Opportunity | Constraint / next test |
| --- | --- | --- | --- |
| Free discovery plus paid research/data | [BenchLM data access](https://benchlm.ai/data/access) | Subscription for retained history or team work | Data display is separately licensed; access fees do not buy redistribution rights |
| Usage/API facilitation | [OpenRouter pricing](https://openrouter.ai/pricing) | Execution path after comparison | Costs, routing and fees depend on provider and usage; requires explicit economics |
| Cloud or team subscription | [Dify plans](https://dify.ai/pricing), [n8n plans](https://n8n.io/pricing/) | Shared builds, evidence reviews and governance | Willingness to pay not established; avoid charging for generic directory access alone |
| Hardware/cloud referral | [ModelFit disclosure](https://modelfit.io/about/), [PCPartPicker disclosure](https://pcpartpicker.com/disclosure/) | Referral revenue where genuine purchase intent exists | Commission incentive can distort rankings; no partner agreement established |
| Vendor-paid listing/marketing | [G2 scoring methodology](https://documentation.g2.com/docs/research-scoring-methodologies), [ModelFit sponsor](https://modelfit.io/sponsor/) | Revenue from vendors rather than buyers | Highest direct ranking-bias risk; paid ranking is not a permissible design (section 3) |
| Deployment/consulting service | Product hypothesis | Paid integration and verification | Labor and liability make it a service business; not validated by this study |

## 2. Commercial offer structure (no rates)

The current review read the publisher's own pages on 2026-10-18 except where the row explicitly retains an older observation or records an access failure. Evidence grade: Primary documentation for the offered terms; statements about neutrality, quality or customer outcomes remain Vendor claims. Region: unauthenticated public pages from one research environment; regional variation not checked. Confidence: Medium for successfully retrieved offer structures on their access date, Low for durability, and unknown for terms not retrieved. No checkout, executed contract or enterprise quote was inspected. A new access failure does not disprove the retained older observation.

| Precedent | Tiers observed | Charging basis | Self-host / licence terms | Data-access or display licensing |
| --- | --- | --- | --- | --- |
| BenchLM Data ([data access](https://benchlm.ai/data/access); rechecked 2026-10-18) | Free, Data Pro, Research; the first paid tier offers a one-time trial | Per account, monthly subscription; tier allowances and request limits are shared across REST, MCP and connected apps, with different retained-history depth | Not applicable to this hosted offer | Query/internal-analysis access does not include commercial display or redistribution. Customer-facing display requires a separate agreement; redistribution needs separately agreed scope, and original measurement publishers retain their rights. Website/newsletter sponsorship is also advertised. |
| OpenRouter ([pricing](https://openrouter.ai/pricing); rechecked 2026-10-18) | Free, Standard and Business pay-as-you-go, Enterprise contract | Prepaid credits fund provider-priced inference; the platform fee applies to credit purchases. Enterprise offers volume/commitment contracts and invoicing. BYOK inference is billed by the provider, with an OpenRouter fee above its monthly BYOK allowance | Not applicable to this hosted offer | Paid tiers distinguish routing, data-policy controls, regional routing and enterprise support. These are offered features, not observed bills or proof that a routed option is cheapest. |
| Dify ([pricing](https://dify.ai/pricing), [licence at `76d0cfcd`](https://github.com/langgenius/dify/blob/76d0cfcd5cd09e93cfa513899a9f66c4c1a2463e/LICENSE); rechecked 2026-10-18) | Cloud: Sandbox, Professional, Team. Self-host: Community, Enterprise | Per workspace, monthly or annual; member/app/storage/trigger limits and model-dependent message credits, then the user's own API key | Modified Apache 2.0 with additional conditions: multi-tenant use requires written authorization; removing/changing logo or copyright in its frontend requires a commercial licence. The frontend condition does not apply to uses without that frontend. Enterprise advertises commercial authorization and negotiated features | No dataset display permission is established by these software offers. Marketplace placement was not examined. |
| n8n ([pricing](https://n8n.io/pricing/), [licence at `d2dc2f9c`](https://github.com/n8n-io/n8n/blob/d2dc2f9ce50294df5c08799af437c56e3e04ab13/LICENSE.md); rechecked 2026-10-18) | Starter/Pro cloud; Business self-host; Enterprise cloud or self-host; Community self-host | Monthly workflow executions, with monthly/annual subscription options and unlimited users/workflows; tiers differentiate concurrency, collaboration, environments and support | Sustainable Use License 1.0 restricts use/modification to internal business or noncommercial/personal use, and distribution to free noncommercial purposes. `.ee.` files or `.ee` directories need the separate Enterprise licence; third-party components retain their licences | These are software-use terms, not data-display rights. The observed billing axis is executions rather than seats. |
| ModelFit ([about](https://modelfit.io/about/), [sponsor](https://modelfit.io/sponsor/); rechecked 2026-10-18) | No paid user tier observed on these pages | Amazon/cloud-GPU referral commissions; a separately purchased fixed site slot plus newsletter placement for 30 days, without automatic renewal | Not applicable to this site offer | The publisher says third-party placements are labelled, and sponsorship/affiliate revenue does not enter recommendations, rankings or benchmarks. Those separation claims were not independently audited. The sponsor page was read through a bounded public HTML download after text extraction failed. |
| PCPartPicker ([disclosure](https://pcpartpicker.com/disclosure/), [industry affiliate code](https://pcpartpicker.com/code-of-conduct/industry-affiliate/)) | Retained 2026-10-16 observation: free to users | Retained observation: merchant affiliate income, Amazon Associates participation, no donations | Not applicable to the observed site offer | The earlier note recorded a vendor claim that affiliate income does not affect editorial opinions, plus affiliation-disclosure and unsolicited-promotion rules for industry representatives. Both URLs returned HTTP 403 on the 2026-10-18 public recheck. Current wording remains unverified; this row is historical precedent, not a current partner agreement. |
| G2 ([scoring](https://documentation.g2.com/docs/research-scoring-methodologies), [FAQ](https://research.g2.com/methodology/research-faq), [DSA page](https://legal.g2.com/digital-services-act), [ads](https://sell.g2.com/advertising); rechecked 2026-10-18) | Public research pages; vendor marketing/data products | G2 Clicks charges per click; Paid Promotions sells fixed quarterly visibility on category and competitor pages | Not applicable to the observed site offers | Software G2 Score combines Satisfaction and Market Presence. Eligible category pages default to G2 Score; smaller categories use popularity. Other sorts and personalised recommender inputs are described, and AI designations are said not to change Grid placement. Paid ad visibility is now documented separately; any effect on **organic** order remains unverified. The earlier claim about down-weighting incentivised reviews was not located in the current cited methodology and is not retained as a current finding. |
| Capterra ([legal](https://www.capterra.com/legal/)) | Unknown | Unknown | Unknown | The original 2026-10-16 attempt returned HTTP 403; the same public URL returned HTTP 404 on 2026-10-18. No paid-placement terms were retrieved. This is an access result, not evidence that such terms or paid placements are absent. |

Structural takeaways (Estimate, from the rows above; confidence Low-Medium):

- Charging axes observed: per account (BenchLM), per workspace with member caps (Dify), executions with unlimited users (n8n), inference usage/credits (OpenRouter), referral conversion (ModelFit; PCPartPicker is a retained older observation), and clicks or fixed-period placements (G2, ModelFit).
- Source-available self-host editions (Dify, n8n) restrict commercial or multi-tenant reuse; an open repository is not a grant to resell a hosted version.
- Data access and display rights are sold separately (BenchLM). This matches the interim #41 reuse position accepted by tynamite in the [PR #67 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67).

## 3. Conflicts of interest by model

Status: Hypothesis (analysis of incentives, not observed misconduct by any named precedent).

| Revenue source | How it could bias a recommendation | Observable symptom to audit |
| --- | --- | --- |
| Referral/affiliate commission | Favouring purchasable hardware or cloud sign-ups over "use existing hardware" or local-only answers; preferring partners with higher commissions; over-sizing builds | Share of recommendations that resolve to a commissioned link vs to "no purchase needed"; rank changes after a partner is added |
| Usage/routing fees | Steering toward hosted execution through the facilitated route rather than local or direct-provider options; favouring higher-volume (more fee-bearing) configurations | Recommendation mix (local vs routed) by revenue; whether the cheapest adequate option is ever the direct provider |
| Sponsored placement | Paid vendors appear more prominent, or sponsorship blends with organic results | Sponsored items rendered inside ranked lists; missing or weak labels |
| Data licensing (selling the evidence base) | Pressure to keep licensors' or buyers' preferences in the scoring; reluctance to publish unfavourable measurements about a data customer | Methodology changes coinciding with licensing deals; suppressed results |
| Team subscription | Lower direct ranking bias; risk of gating essential neutrality features (commission-free view, rationale) behind a paid tier | Whether the neutral view is free for all users |
| Consulting/deployment | Recommending complex stacks that need paid integration; favouring stacks the consultancy implements | Complexity of recommendations vs stated user constraints; disclosure when a recommended path is one the operator sells services for |

The precedents above self-report separation (ModelFit, PCPartPicker); none provides an independent audit. A disclosure statement is therefore not proof of neutral rankings (Issue-specific completion gate).

## 4. Neutrality controls grounded in primary legal text

The cited provisions were rechecked on 2026-10-18 using eCFR and the official EUR-Lex texts; the earlier read was on 2026-10-16. Evidence grade: Primary documentation of the provisions, with High confidence in the summaries below. **Applicability to a particular launched service remains undetermined.** These are inputs to a voluntary product-control proposal, not legal clearance; national transpositions and the complete set of applicable rules were not assessed. The DSA was retrieved through its official ELI page after the older HTML endpoint did not expose the text.

| Instrument | Provision reviewed | Applicability limits | Proposed control |
| --- | --- | --- | --- |
| FTC Endorsement Guides, 16 CFR Part 255 (source 88 FR 48102, 26 July 2023) — [eCFR](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | §§ 255.5(a) and 255.0(f) address disclosure of unexpected material connections and whether a disclosure is noticeable and understandable. § 255.5(b), Example 11, applies this to affiliate reviews. § 255.4(b), Example 3, says paid-for ranking is deceptive even without express independence claims; disclosure does not cure a ranking actually determined by those payments. | The Guides are administrative interpretations of FTC Act § 5, with fact-specific examples (§ 255.0(a)); a project-specific assessment was not performed | Disclose material commercial relationships at the affected recommendation. Keep sponsorship outside organic order; payments and partner relationships never determine rank. |
| Regulation (EU) 2019/1150 (P2B) — [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019R1150) | Art. 5(1) covers main ranking parameters for intermediation services; **Art. 5(2) separately covers search engines**. Art. 5(3) requires explanation of ranking influence bought through remuneration. Art. 5(6) does not require algorithm disclosure. | Art. 1(2) states the EU business/consumer scope. Intermediation under Art. 2(2) includes contractual business-user relationships; search engines have a separate definition in Art. 2(5). Lack of vendor contracts alone cannot decide the entire Regulation's applicability | Publish the main parameters and their relative importance. Adopt a stronger project policy that remuneration never changes organic ranking. |
| Directive (EU) 2019/2161 (Omnibus), amending UCPD — [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L2161) | Art. 3(7)(a) inserts Annex I point 11a on undisclosed paid ads or payment for higher search ranking. Art. 3(4)(b) inserts Art. 7(4a), treating accessible information about main ranking parameters and their relative importance as material | The provisions concern consumer commercial practices; the ranking-information provision covers product searches across traders/consumers and excludes P2B search-engine providers. National transposition and service-specific applicability were not reviewed | Clearly label paid placements and make the ranking explanation directly accessible from results. |
| Regulation (EU) 2022/2065 (DSA) — [official ELI text](https://eur-lex.europa.eu/eli/reg/2022/2065/oj/eng) | Arts. 27(1)–(3) address recommender parameters and selection between available options. Art. 26(1) covers ad identification, beneficiary/payer and accessible targeting-parameter information | Arts. 26–27 concern online platforms as defined in Art. 3(i), including its ancillary-feature exception. Art. 19 excludes qualifying micro/small providers from these provisions unless designated very large. Art. 38's non-profiling option concerns very large services. Project classification is unresolved | Voluntarily explain recommendation parameters/options and paid placements. The proposed commission-free presentation is a separate product choice; it is not equivalent to a legally required non-profiling option. |

Proposed control set (Hypothesis; none is implemented or proven):

1. Rank adequacy against disclosed user constraints before any revenue consideration; commission, sponsorship and consulting data are excluded from scoring inputs.
2. Sponsorship shown in a separate, labelled slot, never inside the ranked list; payment never buys rank (16 CFR § 255.4(b) Example 3; UCPD Annex I point 11a).
3. Per-recommendation disclosure of any referral, routing or consulting relationship (16 CFR § 255.5).
4. Published ranking parameters and weights, linked from every results page (P2B Art. 5; UCPD Art. 7(4a)).
5. A commission-free view available to every user, including free users. For fixed user constraints, evidence, source revisions and chosen sort, **organic eligibility, scores and order are identical in both views**. Only commissioned links and paid-slot presentation change: the commission-free view omits them and uses a verified non-affiliate destination where available, otherwise a provider name without a monetized link. It never hides a superior unpaid or "no purchase" option. This describes the project's presentation, not a guarantee about a third party's prior tracking state.
6. Auditable selection rationale: retain scoring inputs, source revisions and ranking changes. A proposed counterfactual audit toggles commission amounts, partner membership and sponsorship while holding all noncommercial inputs and tie-breaking fixed; any organic eligibility, score or order change fails the design. Inspect paid-slot separation and links independently. No such product audit has been run.

## 5. Viability assumptions vs evidence

| Assumption | Status | Evidence / what would test it |
| --- | --- | --- |
| Evidenced buyers will pay a subscription for shared builds/evidence | Untested hypothesis | Competitor pricing pages show offers, not demand. #63 study (section 6). |
| Referral revenue is material for this audience | Untested hypothesis | The "use existing hardware" job ([customers.md](customers.md)) may produce few purchases; needs measured purchase intent. |
| Retention beyond a one-off selection | Untested hypothesis | Frequency of comparison and switching is unknown per segment ([customers.md](customers.md)). |
| Support and data-licensing costs are manageable | Unknown | Display/redistribution rights are separate from access (BenchLM row). The accepted [#60 constrained-use decision](rights-validation.md#receiving-decisions-and-criterion-map) excludes unsupported uses; it does not supply prices, agreements or a complete operational cost model. Other #41 work remains separate. |
| Consulting is scalable | Unlikely by structure (Estimate) | Labour and liability; not validated. |

Developer adoption or competitor pricing is not evidence of paid demand.

## 6. Proposed willingness-to-pay validation (handoff to #63)

This supplies a research-design proposal for [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63), whose [approval package](customer-validation.md) still governs recruitment, consent, storage, retention and reporting. Nothing has been run. Accepting this proposal does not authorize participant contact, set those unfilled operational decisions or complete #63's fieldwork criteria.

### 6.1 Define the offer before asking a price

The proposed **paid concept** is one private team workspace with shared versioned builds, evidence/source-revision links, comparison history and review comments. The buyer/decision unit is the participant's actual paying team or organization, not an inferred buyer role. The proposed price-question unit is **USD per workspace per month**, with the existing team's size stated. It excludes inference execution, model-provider credits, commercial redistribution of third-party datasets, consulting and an SLA. These are hypothetical test benefits, not implemented features or an available plan.

Before the first price interview, #63 D-14 must freeze the exact concept card: member/build limits, history retention, included support, rights-qualified content and the worked use case, as well as that benefit bundle, buyer unit, currency and billing period. Without a complete card, omit the price module. Use the same version within an analysis cell. If a participant cannot evaluate USD, use a separately specified local-currency card and report it separately; do not invent exchange rates or pool the answers. Scope-mismatched competitor plans are not price anchors or willingness-to-pay thresholds.

The **referral-funded free concept** retains the neutral comparison core and the section 4 controls. Its paid links and separate sponsor slots are disclosed; the commission-free presentation is available without charge. Ask whether the participant understands the relationship, trusts the explanation and would choose the workflow. Do not ask a free offer for a "too expensive" price point. It is also not the same benefit bundle as the paid collaboration concept, so their answers are not a controlled price comparison.

### 6.2 Fixed sequence

1. **Past behaviour first:** use the neutral [#52 guide](customers.md#screener) to reconstruct the last real decision, alternatives, consequences and any earlier similar decision. Keep no-decision cases and existing-hardware outcomes. Do not suggest that cost or a recurring problem must matter.
2. **Spend and authority:** distinguish reported past money/time from stated future intent. Identify the payer, approver and procurement route; a user who does not control the purchase describes that process rather than supplying a proxy willingness-to-pay amount. Do not request private employer records for this public research.
3. **Concept and comprehension:** show the frozen card after the past-behaviour questions and ask the participant to explain the benefits, exclusions and commercial relationship. Counterbalance the order of the paid and free concept cards according to a sequence declared before fieldwork. A baseline/prototype task comparison is optional and needs an actual prototype, fixed tasks, success criteria and order plan; the current #52 guide explicitly has no such validated task instrument. Without it, collect concept reactions only and report no task-completion improvement.
4. **Paid price perception:** only an eligible payer who understands the paid card receives open questions about prices too low to trust, a bargain, expensive but still considered, and too expensive to consider, in the card's fixed unit. Do not show a competitor price or a researcher-supplied amount. Record skipped, inconsistent or unknown answers rather than imputing zeros; preserve their counts. Report these as exploratory stated perceptions, separately from existing spend and actual purchases.
5. **Free-concept and follow-through questions:** record disclosure comprehension, changes in trust, task/workflow preference, reachable purchase channels and reasons for choosing no purchase. An optional, separately approved non-binding pilot request can indicate interest; it is not a sale, a paid commitment or demonstrated retention. No fabricated checkout or purchase is proposed.

Method provenance: the four exploratory price prompts are drawn from the previously cited Van Westendorp/PSM description; this proposal does not claim a validated PSM instrument, an optimal-price curve or a Newton–Miller–Smith purchase/revenue estimate. The original 1976 Van Westendorp and 1993 Newton, Miller and Smith papers **remain unread**. The retained bibliographic details come from the [CRAN reference manual](https://cran.csiro.au/web/packages/pricesensitivitymeter/refman/pricesensitivitymeter.html) (secondary, accessed 2026-10-16). On 2026-10-18 the [ESOMAR publisher catalogue](https://ana.esomar.org/documents/nss-pricesensitivity-meter-psm-) identified the 1976 paper, but its full text was not retrieved; the previously linked Research World archive remained unavailable. Formal method adoption remains a separate #63 design decision.

### 6.3 Declare denominators and interpretation before fieldwork

Use #63's proposed ten-primary-segment/role sampling plan; count each participant in one primary segment, retain secondary matches, and do not present a purposive cohort as representative. #63 D-04/D-12/D-13 must record the final sample/role quotas, minimum reportable cell and these descriptive rules before recruitment. A changed concept card, currency, billing unit or task protocol creates a separate analysis cell. Record the number exposed, valid answers, skips/unknowns and withdrawals for each module; repeated respondents from the same buying decision cannot count as independent buyer decisions.

The following are **proposed pilot-triage rules (Estimate), not validated market cutoffs**. A cell with fewer than three valid independent responses yields no directional model judgment, and any public breakdown must also meet the approved #63 minimum reporting cell. The initial #63 quota of two per segment therefore does not guarantee a usable segment-level result. Report exact numerators/denominators where disclosure permits, not an undefined "most".

| Question | Denominator and proposed flag | Permitted interpretation / next step |
| --- | --- | --- |
| Is the paid bundle useful to a reachable buyer? | Distinct eligible buyer decisions with an understood, complete paid card and a valid response. Flag a cell if at least half say the described paid benefit has no use for their decision or prefer the existing workflow after explaining the tradeoff | Revise or deprioritize that paid pilot for this cohort. Lack of current spend or budget authority alone is a weaker signal, not proof that future demand is absent; user-only answers do not reject buyer demand |
| Can referrals reach the observed purchase path? | Distinct recent decisions with a known purchase/no-purchase outcome and known channel. Flag a cell if at least half involve no purchase or a channel the proposed referral cannot reach | Limited observed referral coverage. Do not infer conversion, commission revenue or profitability; an agreement and full cost/rights evidence remain necessary for an economic decision |
| Does the prototype work? | Participants who attempted the same approved tasks; record each predeclared success/error measure and its threshold separately from concept preference | A failed task or misunderstood feature requires prototype/instrument revision. It does not by itself reject the underlying value proposition. Without a task protocol, leave this row untested |
| Are paid and organic results distinguishable? | Participants who saw the same labelled scenario and answered the comprehension question. Any observed inability to identify the paid placement or describe whether payment affects organic order triggers review of that presentation | This is a disclosure/usability failure. Fix and re-pilot; it is not evidence that neutrality has no value, and a small error-free pilot does not prove legal compliance |
| Does a disclosed commission change trust? | Participants who understood the relationship; report positive, negative, unchanged and unknown responses separately, with their reasons | Reduced trust may support demand for a commission-free option or constrain referrals. It must not be relabelled as disconfirmation of neutrality |

Compare any later monetary answers only against a genuinely equivalent benefit/unit/period and a dated #64 Pricebook context. A competitor's offered team-plan price is not this project's viability threshold. Costs of content rights, support, retention, acquisition and deployment need their own complete assumptions; the current partial #64 examples cannot establish a profitable price.

Limits: this design can prioritize or revise a pilot, not estimate market size, conversion, retention or population willingness to pay. Self-selected developer responses cannot stand in for enterprise buyers. Stated perceptions, reported past behaviour, observed task performance and actual transactions remain separate evidence classes.

## 7. Conditional recommendation

First concept to test (Hypothesis, confidence Low): a free, neutral comparison core with a commission-free presentation for everyone, plus the **workspace subscription** concept in section 6 for shared builds and evidence review. This ordering is an incentive-design judgment, not demonstrated paid demand. Essential ranking explanations and neutrality controls stay free. Referral links are a separately evaluated, labelled add-on; vendor-paid organic ranking is rejected. Consulting remains a separately disclosed service hypothesis.

Each model must qualify independently. A subscription needs a useful recurring buyer job, reachable procurement, rights-qualified benefits and support/data/retention economics. Referrals need reachable purchases, a real partner agreement, disclosed incentives, unchanged organic order and support/data costs that can be covered. The accepted #60 policy excludes unsupported source uses; neither model may assume those uses become licensed by monetization. #63 observations can revise either pilot, and **both models may remain unqualified**. Rejection of a subscription does not automatically select referrals; the outcome may be a smaller free research tool, a revised concept or no commercial launch.

Handoffs: #39 receives comparison-unit boundaries, partial-cost limits and the prohibition on treating offered prices as validated willingness to pay; the exploratory workspace/month unit is not a new frozen billing unit or a runtime pricebook entry. #41 receives the rights exclusions and voluntary neutrality controls; tynamite's earlier #54 → #41 acceptance in PR #67 remains historical. #63 receives a proposal for D-14/D-15, with its operational/participant decisions still open. #58 receives the conditional research recommendation, not a launch decision. Current #39/#41 technical receiving decisions and final evidence review are to be recorded separately; Capterra terms, current PCPartPicker wording, G2 organic paid influence, service-specific legal applicability and all fieldwork/economics remain explicit unknowns.

## 8. Commercial-offer readback, 2026-10-18

This readback covers the four public pages named in #54's Sources, not every
source in this note. Publisher: the organization named in each row. Access date:
2026-10-18 for each linked page. Version: the unversioned public offer displayed
on that date, not a selected software release or executed contract. Region:
unauthenticated English-language pages; no country selector, regional checkout,
tax treatment or negotiated quote was tested. Evidence grade: Primary
documentation of advertised offer structure, not an independent measurement of
billing, demand or neutrality. Confidence: Medium for the displayed structure;
durability and actual customer outcomes remain unknown. No rates, monetary
allowances or numerical quotas are copied.

| Publisher / exact primary page | Structure read directly | Boundary retained |
| --- | --- | --- |
| BenchLM, [Data access](https://benchlm.ai/data/access) | Free, Data Pro and Research share one account allowance across REST, MCP and connected apps. Paid access increases reads and retained-history access. Coverage checks are separate from data reads. | Research removes the history-age cap on eligible retained records; it does not fill missing history. The page separates query/internal-analysis plans from separately agreed commercial display and redistribution scope. Paying for access supplies no display permission here. |
| OpenRouter, [Pricing](https://openrouter.ai/pricing) | Standard and Business use prepaid credits; the page places their platform fee on credit purchase and describes model input/output-token billing separately. Enterprise uses contract terms. BYOK inference is billed directly by the provider, with a separate platform-fee condition beyond an allowance. | These are distinct charging events, not a single universal per-request markup. The page's billing assertions were read, not reproduced. No provider price, platform rate or bill is imported into this note or a Pricebook. |
| LangGenius / Dify, [Pricing](https://dify.ai/pricing) | Cloud lists Sandbox, Professional and Team; the paid workspace offers have monthly/annual selection, member limits and model-dependent message credits. After those credits are used, the page describes switching to the user's own API key. Self-hosted Community and custom Enterprise are separate offers. | Workspace access, member limits and model consumption are separate axes. The pricing page's Community description is not a new license grant; the older license analysis is not refreshed by this page check. No inference cost or production entitlement is established. |
| n8n, [Plans and pricing](https://n8n.io/pricing/) | The headline basis remains monthly workflow executions with unlimited users/workflows. Starter/Pro are hosted; Business is self-hosted and Enterprise can be hosted or self-hosted. Assistant credits are described separately from workflow executions, including a different self-hosted BYOK path. | The page also advertises an affiliate program. Neither its commission terms nor recommendation neutrality was tested. Execution, Assistant-credit and upstream-model charges must not be collapsed into one hypothetical usage unit or treated as a per-seat subscription. |

**Decision implications (analyst hypotheses, not measured outcomes):** Keep the
section 7 team-subscription recommendation conditional. An access subscription
could fund shared review/history while leaving scoring independent, but the
BenchLM boundary means source-display costs/permissions still need #41/#60's
actual source-specific disposition. A subscription does not buy those rights.
The OpenRouter, Dify and n8n structures illustrate why a proposed usage product
must name its charging event and upstream obligations before #39 can assess it;
they do not establish our unit economics. Referral remains a separately
disclosed option under section 3's conflict analysis, rather than an inferred
neutral or profitable fallback. #63 still owns evidence of willingness to pay;
no participant was contacted and no paid-demand inference is added.

**Receiving and remaining decisions:** @appletechie retains the co-owner and
#64 freshness/scenario slice; this readback does not refresh its captured rates
or modify `pricing-validation.md`. #39's monetization handoff is still pending
an explicit owner disposition; no relevant #54/#64 response was present in its
live discussion at this check. The earlier #41 receipt keeps its original
artifact/scope and is not silently transferred to this addition. Request
@tynamite / @PUSHINGSQUARES to assess the new access-versus-display boundary in
their actual #41 scope, and @CompleteDotTech to review this bounded source
readback. #48's source register and #59's canonical handoff ledger remain with
their existing writers. The seven live #54 criteria, unresolved legal
applicability questions, untested neutrality controls and conditional
recommendation remain unchanged; #54 stays open.

## Acceptance map (#54)

| Criterion | Section | Status |
| --- | --- | --- |
| Compare subscription and referral models | 1, 2, 7 | Drafted; awaiting reviewer |
| Review commercial offers without inventing rates | 2, 8 | Original observations retained; four dated primary-page structures rechecked without rates; independent review pending |
| Assess neutrality conflicts | 3, 4 | Drafted; legal applicability needs review |
| Propose willingness-to-pay validation | 6 | Proposed to #63; not run |
| Every significant conclusion linked to evidence or explicit hypothesis | All | Section 8 links each new structure to its exact primary page and marks its decision implications as hypotheses; reviewer to confirm |
| Technical owners review handoffs; unresolved decisions named | 7 | #41 prior acceptance; #39 pending |
| Repository checks pass; reviewer accepts evidence | — | Checks run locally; reviewer acceptance pending |

## Proposed source-register additions

For the `sources.json` owner (#48); not applied here. The original suggestions retain their 2026-10-16 access date; section 2 records the current recheck and failures. The three explicitly dated additions below come from the separate 2026-10-18 review.

| Suggested id | Publisher | URL | Note |
| --- | --- | --- | --- |
| src-dify-pricing | LangGenius, Inc. (Dify) | https://dify.ai/pricing | Missing from register; `src-dify` lacks the pricing page |
| src-benchlm-data-access | BenchLM | https://benchlm.ai/data/access | Already an additional URL on `src-benchlm`; add claim-level licensing note |
| src-modelfit-about | ModelFit | https://modelfit.io/about/ | Affiliate disclosure |
| src-modelfit-sponsor | ModelFit | https://modelfit.io/sponsor/ | Sponsored placement terms |
| src-pcpartpicker-disclosure | PCPartPicker, LLC | https://pcpartpicker.com/disclosure/ | Affiliate disclosure |
| src-pcpartpicker-industry-affiliate | PCPartPicker, LLC | https://pcpartpicker.com/code-of-conduct/industry-affiliate/ | Industry representative disclosure rules |
| src-g2-scoring | G2.com, Inc. | https://documentation.g2.com/docs/research-scoring-methodologies | Ranking parameters |
| src-g2-dsa | G2.com, Inc. | https://legal.g2.com/digital-services-act | Recommender disclosure |
| src-ftc-16cfr255 | US Federal Trade Commission / eCFR | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 | Endorsement Guides, 2023 revision |
| src-eu-p2b-2019-1150 | Publications Office of the EU | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019R1150 | P2B Art. 5 |
| src-eu-omnibus-2019-2161 | Publications Office of the EU | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L2161 | UCPD Annex I 11a, Art. 7(4a) |
| src-eu-dsa-2022-2065 | Publications Office of the EU | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022R2065 | DSA Arts. 3, 19, 26, 27, 38 |
| src-cran-psm | CRAN (pricesensitivitymeter, M. Alletsee) | https://cran.csiro.au/web/packages/pricesensitivitymeter/refman/pricesensitivitymeter.html | Secondary method reference |
| src-g2-advertising | G2.com, Inc. | https://sell.g2.com/advertising | 2026-10-18: per-click and fixed-quarterly paid visibility; organic paid influence remains unverified |
| src-dify-licence-review | LangGenius, Inc. | https://github.com/langgenius/dify/blob/76d0cfcd5cd09e93cfa513899a9f66c4c1a2463e/LICENSE | 2026-10-18: immutable code-use terms, not dataset display rights |
| src-n8n-licence-review | n8n | https://github.com/n8n-io/n8n/blob/d2dc2f9ce50294df5c08799af437c56e3e04ab13/LICENSE.md | 2026-10-18: immutable master-branch source terms, including Enterprise/third-party exclusions |
