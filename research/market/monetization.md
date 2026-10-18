# Monetization and neutral recommendations

Status: research proposal for [#54](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/54). The original observations below retain their 2026-10-16 access date; section 8 records a separate, bounded 2026-10-18 offer readback. Desk research only: no accounts, quotes, agreements, outreach or willingness-to-pay data. Confidence overall: Low.

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

Every row: publisher's own page, accessed 2026-10-16, evidence grade Primary documentation for the offer terms (claims about neutrality or quality on the same pages are Vendor claims). Region: pages were fetched without login from a single location; regional variation not checked. Confidence Medium for structure as displayed on the access date; Low for durability, since pricing pages change without notice. Limitation for all rows: no checkout, contract or enterprise quote was inspected, so contract terms may differ from the page.

| Precedent | Tiers observed | Charging basis | Self-host / licence terms | Data-access or display licensing |
| --- | --- | --- | --- | --- |
| BenchLM Data ([data access](https://benchlm.ai/data/access)) | Free, Data Pro, Research; first paid tier offers a one-time trial | Per account, monthly subscription; each tier carries a monthly read allowance and request-rate limit shared across REST, MCP and connected apps; tiers differ mainly by depth of retained history | Not applicable (hosted data service) | "Free, Pro, and Research are access plans for queries and internal analysis. Paid plans … do not include commercial display or redistribution permission." Customer-facing display needs "a separate display agreement"; redistribution "needs separately agreed scope"; publisher measurements "keep their own commercial-use and redistribution rights". The site also sells "Website and newsletter sponsorships" ("Advertise on BenchLM"). |
| OpenRouter ([pricing](https://openrouter.ai/pricing)) | Free, Standard (pay-as-you-go), Business (pay-as-you-go), Enterprise (contract) | Usage: prepaid credits deducted per request at provider list price per input/output token; OpenRouter's platform fee is charged on credit purchase, "never on individual requests", and the FAQ states it does not mark up provider pricing. Enterprise is set by contract on volume, prepaid credits and annual commitments with invoicing. BYOK: provider bills inference directly; a platform fee applies above a monthly BYOK threshold. | Not applicable (hosted routing) | Tiers gate auto-routing/preferred-vendor selection, data-policy-based routing, EU/US in-region routing, SSO/SAML, SLAs and DPA form. Paid tiers gate the router, so routing behaviour is part of the product being paid for. |
| Dify ([pricing](https://dify.ai/pricing), [licence](https://raw.githubusercontent.com/langgenius/dify/main/LICENSE)) | Cloud: Sandbox (free), Professional, Team; Self-hosted: Community (free), Enterprise (contact sales) | Cloud: per workspace, monthly or annual; tiers cap team members, apps, knowledge documents/storage, trigger events and annotation quota; bundled model "message credits" are consumed by model type, after which the user switches to their own API key (hybrid subscription + bring-your-own-model) | Community Edition under a modified Apache 2.0: commercial use allowed, but multi-tenant operation and removing console logo/copyright require a commercial licence. Enterprise adds "Commercial License Authorization", SSO, multiple workspaces and negotiated SLAs. | Not a data licensor. Dify also operates a Marketplace (tools, models, plugins), a potential placement surface not examined here. |
| n8n ([pricing](https://n8n.io/pricing/), [licence](https://raw.githubusercontent.com/n8n-io/n8n/master/LICENSE.md)) | Starter, Pro (hosted by n8n); Business (self-hosted only); Enterprise (hosted or self-hosted, contact sales); Community Edition (self-host, free); a start-up programme discount exists | Usage-based subscription: "unlimited users & workflows"; "Pricing based on monthly workflow executions, regardless of complexity"; tiers add concurrency, shared projects, SSO/LDAP, environments, log retention and support; invoicing on higher tiers | Sustainable Use License 1.0: use or modify "only for your own internal business purposes or for non-commercial or personal use"; distribution only "free of charge for non-commercial purposes"; files marked `.ee.` need an Enterprise licence | Not a data licensor. Notable: explicitly **not** seat-based, in contrast to Dify's member caps. |
| ModelFit ([about & disclosure](https://modelfit.io/about/), [sponsor](https://modelfit.io/sponsor/), [home](https://modelfit.io/)) | No user tiers observed (free site) | Referral: Amazon Associates and possible commission "on cloud-GPU sign-ups"; vendor-paid fixed sponsor slot plus newsletter block, sold as a one-off 30-day placement, "not a subscription" | Not applicable | Disclosure states affiliate links are "always marked" and "never influence which models or devices we recommend"; rankings come from a scoring engine "which has no knowledge of affiliate revenue"; sponsorship is "a separate, clearly-labeled placement". These are Vendor claims; not independently verified. |
| PCPartPicker ([disclosure](https://pcpartpicker.com/disclosure/), [industry affiliate code](https://pcpartpicker.com/code-of-conduct/industry-affiliate/)) | Free to users | Referral: "receives compensation through affiliate relationships with merchants listed on this site"; Amazon Associates participant; does not accept donations | Not applicable | States the affiliate income "in no way affects reviews, benchmarks, content, or this site's opinions" (Vendor claim). Separately requires industry representatives to disclose affiliation and bars them from posting advertisements or pitching their own products unprompted. |
| G2 ([scoring methodology](https://documentation.g2.com/docs/research-scoring-methodologies), [research FAQ](https://research.g2.com/methodology/research-faq), [DSA page](https://legal.g2.com/digital-services-act)) | Buyer access free; vendor-paid products listed in site navigation (Profiles, Reviews, Buyer Intent, G2 Ads, Content Marketing) | Vendor-paid (marketing/data products), not buyer-paid | Not applicable | Publishes ranking inputs: category pages sort by default on G2 Score (Satisfaction + Market Presence), with Popularity and Satisfaction sorts; incentivised reviews are down-weighted; AI designations "have no effect on Grid® placement". Its DSA page describes recommender inputs (search history, prior interactions, similarity). **Unverified:** no G2 page reviewed states whether or how paid products affect listing position; absence of a statement is not evidence either way. |
| Capterra ([legal](https://www.capterra.com/legal/)) | — | — | — | **Not accessed:** HTTP 403 to unauthenticated fetch. Its paid-placement disclosure remains unverified. |

Structural takeaways (Estimate, from the rows above; confidence Low-Medium):

- Charging axes observed: per account (BenchLM), per workspace with member caps (Dify), per usage unit with unlimited users (n8n executions, OpenRouter tokens/credits), per referral conversion (ModelFit, PCPartPicker) and per vendor placement (ModelFit sponsor, G2 vendor products).
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

All texts fetched 2026-10-16 from official sources and read in full at the cited provisions. Evidence grade: Primary documentation. Confidence High that the quoted text is as cited; **applicability to this project is a Hypothesis requiring legal review** (no legal advice was obtained). EUR-Lex HTML fetches succeeded; no fallback was needed.

| Instrument | Provision (quoted briefly) | Applicability limits | Proposed control |
| --- | --- | --- | --- |
| FTC, Guides Concerning Use of Endorsements and Testimonials in Advertising, 16 CFR Part 255 (source 88 FR 48102, 26 July 2023) — [eCFR](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | § 255.5(a): a connection that "might materially affect the weight or credibility of the endorsement" and is "not reasonably expected by the audience … must be disclosed clearly and conspicuously". § 255.0(f): "clear and conspicuous" means "difficult to miss (i.e., easily noticeable) and easily understandable by ordinary consumers". § 255.5(b) Example 11: a reviewer with affiliate links "should clearly and conspicuously disclose the compensation". § 255.4(b) Example 3: a review site accepting money "in exchange for higher rankings" is deceptive, and a disclosure of payments "would be inadequate because the payments actually determine the … relative rankings"; a ranking methodology that ranks related sellers higher "because of those relationships" is also misleading. | Guides are administrative interpretations of FTC Act § 5 (§ 255.0(a)), not regulations with independent force; US audience | Disclose referral, sponsorship and consulting relationships next to each affected recommendation, not only in a footer. Never sell rank: payment may buy a labelled slot, never position in the ranked list. Ranking inputs exclude commission data. |
| Regulation (EU) 2019/1150 (P2B) — [EUR-Lex CELEX 32019R1150](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019R1150) | Art. 5(1): providers "shall set out in their terms and conditions the main parameters determining ranking and the reasons for the relative importance of those main parameters". Art. 5(3): where ranking can be influenced by "direct or indirect remuneration paid by business users", the provider must describe "those possibilities and … the effects of such remuneration on ranking". Art. 5(6): algorithms need not be disclosed. | Applies to "online intermediation services" (Art. 2(2)), which require **contractual relationships with business users** that offer goods/services to EU consumers. A pure comparison site with no vendor contracts may fall outside; referral or listing agreements could bring it in. | Publish main ranking parameters and their relative weight; state explicitly that remuneration has no effect on ranking (or, if any exists, its effect). |
| Directive (EU) 2019/2161 (Omnibus), amending Directive 2005/29/EC (UCPD) — [EUR-Lex CELEX 32019L2161](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L2161) | Art. 3(7)(a) inserts UCPD Annex I point 11a (always unfair): "Providing search results in response to a consumer's online search query without clearly disclosing any paid advertisement or payment specifically for achieving higher ranking of products within the search results." Art. 3(4)(b) inserts UCPD Art. 7(4a): information on "the main parameters determining the ranking of products … and the relative importance of those parameters" is material, in a section "directly and easily accessible from the page where the query results are presented". Art. 3(1)(b) defines "ranking" as "the relative prominence given to products". | Business-to-consumer commercial practices of a trader; Art. 7(4a) concerns search across products "offered by different traders" and excludes online search engines as defined in P2B. Directive: national transposition governs; transposing laws not checked. | Label every paid placement at the point of display; link the ranking-parameter explanation from every results page. |
| Regulation (EU) 2022/2065 (DSA) — [EUR-Lex CELEX 32022R2065](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022R2065) | Art. 27(1): providers of online platforms using recommender systems "shall set out in their terms and conditions, in plain and intelligible language, the main parameters used in their recommender systems, as well as any options for the recipients … to modify or influence those main parameters"; Art. 27(3): where several options exist, a functionality to select and modify the preferred option "at any time". Art. 26(1): each advertisement must be identifiable as such and show on whose behalf it is presented and who paid. | Applies only to "online platforms" (Art. 3(i): hosting services that store and disseminate user information to the public). A comparison tool without user-generated public content is likely **not** an online platform; adding public shared builds or reviews could change that. Art. 19: Section 3 (including Arts. 26–27) does not apply to micro or small enterprises unless designated very large. Art. 38 (non-profiling option) applies only to very large platforms/search engines. | Adopt Art. 27-style transparency voluntarily: plain-language parameters, user-selectable sort including a commission-free view; label ads per Art. 26 even if not legally required. |

Proposed control set (Hypothesis; none is implemented or proven):

1. Rank adequacy against disclosed user constraints before any revenue consideration; commission, sponsorship and consulting data are excluded from scoring inputs.
2. Sponsorship shown in a separate, labelled slot, never inside the ranked list; payment never buys rank (16 CFR § 255.4(b) Example 3; UCPD Annex I point 11a).
3. Per-recommendation disclosure of any referral, routing or consulting relationship (16 CFR § 255.5).
4. Published ranking parameters and weights, linked from every results page (P2B Art. 5; UCPD Art. 7(4a)).
5. A commission-free view available to every user, including free users; never hide a technically superior unpaid or "no purchase" option.
6. Auditable selection rationale: log scoring inputs, source revisions and ranking changes; record partner onboarding dates so rank changes can be compared against commercial events.

## 5. Viability assumptions vs evidence

| Assumption | Status | Evidence / what would test it |
| --- | --- | --- |
| Evidenced buyers will pay a subscription for shared builds/evidence | Untested hypothesis | Competitor pricing pages show offers, not demand. #63 study (section 6). |
| Referral revenue is material for this audience | Untested hypothesis | The "use existing hardware" job ([customers.md](customers.md)) may produce few purchases; needs measured purchase intent. |
| Retention beyond a one-off selection | Untested hypothesis | Frequency of comparison and switching is unknown per segment ([customers.md](customers.md)). |
| Support and data-licensing costs are manageable | Unknown | Display/redistribution rights for third-party data are separately priced (BenchLM row); #41/#60 rights decisions pending. |
| Consulting is scalable | Unlikely by structure (Estimate) | Labour and liability; not validated. |

Developer adoption or competitor pricing is not evidence of paid demand.

## 6. Proposed willingness-to-pay validation (handoff to #63)

This is a proposal for [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63), not results. Nothing has been run. #63 must approve recruitment channels, informed consent, retention and anonymised reporting before any participant contact.

Sequence (non-leading; no price shown until step 4):

1. **Past behaviour:** reconstruct the last real AI stack/model/hardware selection: trigger, tools used, time spent, who decided, consequences of a wrong choice.
2. **Current spend and authority:** what is already paid for in this job (tools, data, consulting, cloud trials, staff time); who approves spend; procurement route. Ask for actual records where the participant is willing, not estimates of future behaviour.
3. **Concept exposure:** baseline workflow vs a prototype decision record, as in the [customers.md interview protocol](customers.md); record task completion, unsupported assumptions and rejection reasons. No price, plan or tier names shown.
4. **Non-anchored price perception:** Van Westendorp Price Sensitivity Meter: four open questions (at what price would it be too cheap to trust, a bargain, getting expensive, too expensive), answered without any reference price, followed by optional purchase-intent questions at the respondent's own "cheap" and "expensive" points (Newton–Miller–Smith extension). Separate questions per model (subscription vs referral-funded free) so each is judged independently.
5. **Commitment test (optional, approval required):** a non-binding but costly signal such as a waitlist with role/budget-owner details or a request for a pilot, never a fabricated or deceptive checkout.

Method references: Van Westendorp, P. (1976), "NSS-Price Sensitivity Meter (PSM) – A new approach to study consumer perception of price", Proceedings of the 29th ESOMAR Congress, 139–167; Newton, D., Miller, J., Smith, P. (1993), "A market acceptance extension to traditional price sensitivity measurement", AMA Advanced Research Techniques Forum. **Method reference unverified:** the original papers were not read. The bibliographic details come from the [CRAN `pricesensitivitymeter` reference manual](https://cran.csiro.au/web/packages/pricesensitivitymeter/refman/pricesensitivitymeter.html) (secondary; accessed 2026-10-16). The archive copy it links (archive.researchworld.com) returned HTTP 500.

Disconfirming evidence (decide before fieldwork):

- Subscription model disconfirmed for a segment if most participants in it report no current spend on the job **and** no budget owner, or if the "too expensive" point clusters below the team-plan level of the comparables (to be compared only in #64's dated pricebook context, not here).
- Referral model disconfirmed if most recent decisions in a segment ended with no purchase (existing hardware, existing provider) or with purchases made through channels a referral could not reach.
- Concept disconfirmed regardless of price if the decision record does not improve task completion or is rejected as untrustworthy.
- Neutrality disconfirmed as a value if participants cannot tell sponsored from organic items in the prototype, or report that a disclosed commission removes trust.

Limitations: PSM measures stated price perception, not purchase behaviour; small qualitative samples give direction, not market size; self-selected developer samples do not represent enterprise buyers.

## 7. Conditional recommendation

Best-supported option (Hypothesis, confidence Low): a free, neutral comparison core with a commission-free view for everyone, funded first by a **team subscription** for shared, versioned builds and evidence review (usage-based or workspace-based, not seat-gated access to rankings). Referral links are acceptable only as labelled, rank-independent add-ons. Vendor-paid ranking is rejected. Consulting stays a separate, disclosed service.

Rejection conditions: #63 meets the subscription disconfirmation criteria above, in which case referral-funded free becomes the fallback with the full control set; or #41/#60 rights decisions prevent displaying the evidence base needed for a paid team product.

Handoffs: #39 (no price units or semantics are proposed here; confirm no conflict with #64), #41 (display/redistribution licensing and disclosure controls; tynamite accepted the earlier #54 → #41 row in the PR #67 review), #63 (section 6 proposal), #58 (consumes the recommendation). Unresolved: #39 disposition; #63 acceptance of the protocol; legal review of section 4 applicability; Capterra and G2 paid-placement terms.

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

For the `sources.json` owner (#48); not applied here. All accessed 2026-10-16.

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
