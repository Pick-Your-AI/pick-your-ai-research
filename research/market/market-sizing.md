# Market boundaries, demand and sizing

Status: desk analysis, originally 2026-10-16; source and scenario clarification 2026-10-18 for #53. This is a bounded market hypothesis and research recommendation, not a revenue forecast, TAM/SAM/SOM finding or purchase-intent measurement. Original source access dates remain 2026-10-16; the separately scoped 2026-10-18 readback below identifies what was actually rechecked.

Adoption is a broad enabling condition, not a count of buyers for configuration advice. None of the sources below estimates willingness to pay for Pick Your AI or demand for a configuration-decision tool.

## Decision market and counting units

Define the target hypothesis by a recurring decision: selecting or revising a multi-component AI configuration (model, runtime, hardware or hosted provider, retrieval/agent stack). Whether those decisions recur often enough to support a paid product remains unmeasured. Exclude all general AI spend, model training capital and cloud revenue from the product's addressable-revenue denominator. Distinguish individual comparison users, team collaboration buyers and enterprise governance buyers; their purchase processes are different.

Units are not interchangeable and are never summed:

| Unit | Definition used here | Evidence status |
| --- | --- | --- |
| Respondent / business / enterprise | The unit each external survey counts (people, U.S. employer firms, EU enterprises with 10+ persons employed) | Sourced, but a population of AI users, not of buyers |
| Individual account | One person paying for their own use | Analyst assumption only |
| Team account | One organizational workspace paying one annual price, regardless of seats | Analyst assumption only |
| Decision | One configuration selection or revision event | Unmeasured; frequency per account unknown |

## Dated adoption evidence (use, not purchase intent)

Every row measures reported AI use or platform activity. None measures intent to buy a decision tool.

| ID | Source and locator | Exact figure | Population and method | Data date | Evidence class / confidence | Limitation |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | [Stanford HAI, AI Index Report 2026](https://hai.stanford.edu/assets/files/ai_index_report_2026.pdf), ch. 4, sec. 4.3 Corporate AI Adoption, Figure 4.3.1 and detailed text p. 193; conflicting chapter highlight 5, p. 173 | Detailed text/chart: 88% report organization AI use in at least one business function (78% in 2024); 79% regularly use generative AI in at least one function (71% in 2024). Chapter highlight 5 instead states 70% for generative AI use in at least one function | McKinsey 2025 online survey, 1,993 participants in 105 nations, fielded 2025-06-25 to 2025-07-29, weighted by national GDP share; 38% from organizations with >$1B revenue (Appendix, pp. 396-397) | 2025 | Self-reported survey, secondary compilation by AI Index / Medium for the identified detailed result; Low for cross-summary consistency | The in-source 79%/70% difference is unresolved here; neither averaging nor a silently selected single report-wide figure is justified. The report treats these as directional results, not comprehensive coverage; respondents skew to large firms; one respondent per organization is not guaranteed; measures any AI use |
| A2 | Same report, sec. 4.3, text p. 197 and the lower agent-adoption-stage chart captioned Figure 4.3.8, p. 198 | Scaled AI-agent use is in single-digit percentages for nearly all functions; IT and knowledge management report 69% and 66% no use respectively | Same McKinsey survey | 2025 | Self-reported survey, secondary / Medium | Agent stage is self-classified; not specific to configuration decisions. The prose on p. 197 reverses the Figure 4.3.7/4.3.8 references; this locator follows the actual p. 198 chart caption |
| A3 | Same report, ch. 1, sec. 1.5 Open-Source AI Software, printed p. 44 (PDF p. 45), Figures 1.5.6-1.5.8 | Hugging Face model uploads grew by more than three times from 2023 to 2025; dataset uploads grew fourfold | Upload charts use Hugging Face metadata for 2022-2025. The separate download chart uses Longpre et al. (2025)'s weekly top-200-model panel, covering 49.6% of normalized downloads, Mar 2020-Aug 2025 | 2022-2025 | Platform activity, secondary analysis / Medium | Uploads and downloads are activity proxies, not users or buyers; the top-200 restriction applies to the separate download panel, not the upload counts |
| A4 | [Stack Overflow Developer Survey 2026, AI](https://survey.stackoverflow.co/2026/ai) and [AI full data](https://survey.stackoverflow.co/2026/ai/data), question "Do you currently use AI tools or AI agents in your role at work?" | 65.9% use AI coding assistants or agents; 62.5% general-purpose chat tools; 26.2% agents or automated workflows; 17.2% use no AI tools (n = 17,464) | Online survey of developers and technologists | Fielded 2026-06-23 to 2026-08-05 | Self-reported, self-selected survey / Medium for respondents, Low for generalization | See S-method below |
| A5 | Same data page, "How often do you use each of these AI tools...?" | 77% overall daily users; 73.0% daily for coding assistants (n = 14,478) | As A4 | 2026 | As A4 | Frequency of use, not willingness to pay |
| A6 | Same data page, "In the past year, have you switched from one AI tool to another for work?" | 33.7% did not switch; 25.1% switched for better output quality; 10.6% because the organization required or recommended a different tool; 6.4% for lower cost; 2.1% for access to a preferred model/provider (n = 13,144) | As A4 | 2026 | As A4 | Reports switching during one year; does not establish recurring multi-component configuration frequency, evaluation effort or demand for advice |
| A7 | Same data page, "Which of the following best describes how AI tools or agents are used at your organization today?" | 29.7% mostly optional and individual-led; 24.0% approved tools and guidance; 6.1% organization does not use AI (n = 13,167) | As A4 | 2026 | As A4 | Suggests both individual and organizational decision contexts exist; says nothing about who would pay |
| A8 | [U.S. Census Bureau, BTOS National estimates](https://www.census.gov/hfp/btos/downloads/National.xlsx), sheet "Response Estimates", question 7 ("In the last two weeks, did this business use AI in any of its business functions?") and question 24 (next six months) | Cycle 202620: 23.8% used AI (SE 0.41 pp); 27.7% expect to use AI in the next six months (SE 0.36 pp). Cycle 202609: 19.8%. Cycle 202601: 17.7% | Biweekly, nationally representative survey of U.S. employer businesses. Cycle 202620 collected 2026-09-21 to 2026-10-04, reference period 2026-09-07 to 2026-09-20, published 2026-10-08 (sheet "Collection and Reference Dates") | 2026-09 | Official statistical survey, firm self-report / High for the stated measure | Question wording changed in November 2025 from "producing goods or services" to "any business function", so pre-change cycles are not comparable; counts firms, not users or decision events; no estimates for cycles 202521-202523 (federal shutdown) |
| A9 | [U.S. Census Bureau, "Large Firms With at Least 20 Employees Biggest AI Users"](https://www.census.gov/library/stories/2026/05/ai-use-businesses.html), published 2026-05-26 | Use 17%-20% Dec 2025-May 2026; 37% of firms with 250+ employees; 32% of firms with 100-249; under 20% of firms with 4 or fewer; Information sector 39.7% vs national 19.8% (period ending 2026-05-03) | BTOS, Dec 14 2025 to May 3 2026 | 2025-12 to 2026-05 | Official statistical publication / High | Same unit and wording limitations as A8; superseded in level by A8 |
| A10 | [Eurostat news, "20% of EU enterprises use AI technologies"](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2), 2025-12-11; [Statistics Explained, Use of AI in enterprises](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises), Figures 1-3, dataset `isoc_eb_ai` | 20.0% (19.95%) of EU enterprises used AI in 2025, up from 13.5% in 2024; small 17%, medium 30.36%, large 55.03%; information and communication sector 62.52% | 2025 EU survey on ICT usage and e-commerce in enterprises; enterprises with 10+ employees or self-employed persons, NACE Rev. 2 sections C-J, L-N and group 95.1 | 2025 (data extracted Dec 2025; next update planned Dec 2026) | Official statistical survey / High for the stated measure | Excludes micro-enterprises and some sectors. The article flags a Netherlands series break for 2025; the news says the picture/video/sound-generation category is new in 2025. The technology list is therefore not an unchanged instrument. The historical 2026-10-16 API read recorded 19.95% for 2025, 13.48% for 2024 and update date 2026-06-15; that API read is not newly repeated here |
| A11 | Same Statistics Explained article, "Reasons for not using AI technologies" | Among enterprises that had considered AI but did not use it: lack of relevant expertise 70.89%; unclear legal consequences 52.52% | As A10 | 2025 | Official statistical survey / High | Expertise gaps are a plausible need, but this does not show demand for a configuration tool |

**S-method (Stack Overflow).** [Methodology page](https://survey.stackoverflow.co/2026/methodology): 30,903 valid responses from 169 countries out of 39,266 rows recorded 2026-06-23 to 2026-08-05; promoted through stackoverflow.com, stackoverflow.blog and an opt-in email list. Participation is voluntary and self-selected; the page makes no representativeness claim. Its counts describe the current extract and can change. Per-question bases differ (10,926-17,464 for the AI questions); without eligibility and routing counts, their difference from 30,903 cannot be assigned entirely to item non-response. The documented validity rules include a primary consent/employment/bot screen and a separate substantive-response recovery rule; the latter can retain a row flagged by the bot heuristic if all ten named core questions are answered. This describes a quality rule, not observed bot prevalence. Do not extrapolate to all developers or enterprise buyers. The [AI data page](https://survey.stackoverflow.co/2026/ai/data) reports 48.0% choosing easy output verification as a trust condition (n = 14,304); this supports testing source attribution, not product demand.

### Local and self-hosted model activity (discoverability/usage proxy only)

These counters report requests or pulls for model artifacts. They do not identify people, a local versus hosted execution destination, buyers or purchase intent.

| ID | Source | Figure as retrieved 2026-10-16 | Counting rule | Evidence class / confidence | Limitation |
| --- | --- | --- | --- | --- | --- |
| L1 | [Hugging Face Hub API, text-generation models sorted by downloads](https://huggingface.co/api/models?sort=downloads&direction=-1&limit=10&filter=text-generation) | Top model Qwen/Qwen3-0.6B: 29,878,421 downloads; Qwen/Qwen3-8B: 9,422,391 (all-time 132,402,789 via `expand[]=downloadsAllTime`) | `downloads` = last 30 days ([huggingface_hub HfApi reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api)); GET or HEAD requests on a query file such as `config.json` count, not unique downloaders ([Models Download Stats](https://huggingface.co/docs/hub/models-download-stats)) | Platform-published counter / Medium for activity, Low for people | Repeated or automated requests can count; GGUF multi-file downloads have a documented double-counting case. Neither human-use share nor local-only execution is measured |
| L2 | [Ollama library, sorted by popular](https://ollama.com/library?sort=popular) | llama3.1 120.3M pulls; deepseek-r1 93.8M; nomic-embed-text 90.6M; llama3.2 85.6M; qwen2.5 42.6M | Counting rule and time window not documented on the page | Vendor-published counter / Low | Deduplication and automated-request treatment are unknown; cannot be converted to users |

Sources reviewed but not used as sizing inputs: AI Index Figure 4.2.22 (p. 192, Brynjolfsson et al. 2026: 115M U.S. adults using generative AI), which counts consumers in general rather than configuration decision-makers.

### Contradictions and weak points

- Organizational adoption differs by source and unit: 88% of McKinsey respondents' organizations (A1) versus 23.8% of U.S. employer businesses (A8) and 20.0% of EU enterprises with 10+ employees (A10). The difference reflects population (large-firm respondents vs representative firm samples) and question wording, not a trend contradiction. Use the official series for business prevalence and treat A1 as directional.
- Census and Eurostat report the stated size and sector differences (A9, A10). A technical-team focus remains an analyst hypothesis; these figures identify neither configuration decision-makers nor a paying segment.
- Developer use is high among Stack Overflow respondents (A4, A5) but the sample is self-selected and cannot be weighted to a population.

## Use versus purchase intent

Every figure above measures current or expected use of AI, or platform activity. Purchase intent for a configuration-decision tool is not measured by any reviewed source. The closest signals are switching behavior (A6: 2.1% switched for a preferred model/provider, 6.4% for cost) and expertise barriers among nonusers that considered AI (A11); both motivate hypotheses about need, not evidence of willingness to pay. #63's future approved qualitative work can inform buyer definitions, prior behavior and stated reactions. It cannot supply measured paid conversion, population reach or a validated price by itself. Those require separately defined observations of the relevant behavior. #52's personas remain hypotheses.

## Explicit scenarios, not market measurements

Modeled gross annual subscription amount = qualified accounts in one deduplicated acquisition cohort × activation share within that cohort × paying share among those active accounts × one complete annual price per paying account. Modeled paying accounts = cohort accounts × activation × paying share. All inputs are analyst assumptions in USD, not verified demand or proposed final prices. Individual and team accounts are separate units and are never added together.

The arithmetic assumes every converted account buys exactly one full annual subscription, with no partial-year billing, refund or renewal. It is a full-year-price equivalent for one cohort, not measured calendar-year revenue, revenue recognition or a recurring acquisition forecast. No observation window or accessible cohort was measured for these historical rows; the prospective protocol below supplies explicit definitions for a later test. A monthly offer would require its own payment/retention model; multiplying an unmeasured monthly price by twelve would not demonstrate twelve payments.

| Scenario | Account unit | Cohort accounts (assumed reachable) | Activation (assumption) | Paid among active (assumption) | Annual price, USD (assumption) | Modeled paying accounts | Modeled gross annual subscription amount, USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Small validation channel | Individual | 1,000 | 10% | 5% | $120 | 5 | $600 |
| Focused developer channel | Individual | 10,000 | 20% | 5% | $120 | 100 | $12,000 |
| Team-oriented channel | Team | 10,000 | 20% | 10% | $600 | 200 | $120,000 |

Historical arithmetic check and revision note (2026-10-16): 1,000 × 0.10 × 0.05 × 120 = 600; 10,000 × 0.20 × 0.05 × 120 = 12,000; 10,000 × 0.20 × 0.10 × 600 = 120,000. That revision kept the earlier scenario values and added the account unit. The 2026-10-18 amendment also clarifies their interpretation while keeping all values unchanged. Reaching 10,000 qualified team accounts is a much stronger assumption than reaching 10,000 individuals; no sourced count of teams making configuration decisions exists.

The large spread demonstrates the consequences of the chosen assumptions, not their likelihood or the empirical importance of one market factor. These are neither TAM/SAM/SOM estimates nor evidence of attainable revenue. Acquisition, churn, taxes, payment fees, support and data-license costs are omitted; profitability cannot be inferred.

## One-at-a-time sensitivity

Each row changes one input to its low or high bound and holds the others at the base scenario. Bounds are analyst-selected illustrations, not measured uncertainty ranges or likelihood bounds. The tables retain the historical shorthand "revenue" for the modeled full-year-price amount just defined. Paid conversion is conditional on the offer, price and buyer; holding it fixed while varying price is an arithmetic sensitivity exercise, not a claim of independent demand.

Individual base: Focused developer channel (10,000 × 20% × 5% × $120 = $12,000).

| Input varied | Low bound | High bound | Revenue at low, USD | Revenue at high, USD | High/low ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| Reachable individual accounts | 1,000 | 50,000 | $1,200 | $60,000 | 50× |
| Activation | 5% | 40% | $3,000 | $24,000 | 8× |
| Paid among active | 1% | 10% | $2,400 | $24,000 | 10× |
| Annual price | $60 | $240 | $6,000 | $24,000 | 4× |

Team base: Team-oriented channel (10,000 × 20% × 10% × $600 = $120,000).

| Input varied | Low bound | High bound | Revenue at low, USD | Revenue at high, USD | High/low ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| Reachable team accounts | 1,000 | 20,000 | $12,000 | $240,000 | 20× |
| Activation | 5% | 40% | $30,000 | $240,000 | 8× |
| Paid among active | 2% | 20% | $24,000 | $240,000 | 10× |
| Annual price | $240 | $1,200 | $48,000 | $240,000 | 5× |

All-low/all-high combinations span $30 to $480,000 (individual) and $240 to $1,920,000 (team). These are endpoints of the assumed arithmetic ranges, not a confidence interval. The individual all-low combination has 1,000 × 5% × 1% = 0.5 modeled payers; that fractional intermediate is algebra, not half of an observed customer. Actual cohort counts would be nonnegative integers.

**Largest one-input swing under these chosen bounds: qualified cohort accounts.** The model is a pure product, so a given percentage change in any input moves its output by the same percentage. The ranking follows only from the widths assigned by the analyst: reach 50× for individuals and 20× for teams, versus 4×/5× for annual price. Activation and paid share varied jointly span 80× in each model. This does not establish that reach is empirically more uncertain, or price less important. The proposed learning priority is to identify one observable cohort and its buyer/offer first, then measure the associated stages; pricing and conversion must be interpreted together. No search-volume, accessible-channel or paid-conversion evidence currently constrains those choices.

## Missing evidence (recorded as unknown, not zero)

| Input | Status on 2026-10-16 | Why not obtained / next step |
| --- | --- | --- |
| Absolute search volume | Not obtained | No keyword-volume tool or Search Console property; paid keyword tools are out of scope |
| Google Trends relative interest | Not obtained | Unauthenticated request to the Trends explore endpoint returned HTTP 429; no index values recorded |
| Customer acquisition cost | Unknown | No ad, landing-page or outreach experiment run |
| Activation and paid conversion | Unknown | Requires a defined cohort, offer, observation window and actual behavioral measurement; qualitative #63 interviews do not substitute for transactions or traffic |
| Purchase frequency / decisions per account | Unknown | Not measured by any reviewed source |
| Willingness to pay | Unknown | No participant or price-test result is supplied; later stated reactions remain distinct from actual payment |
| Competitor revenue, active users, concentration | Not established | No primary disclosures found in reviewed sources |
| Count of teams making configuration decisions | Unknown | Business surveys count firms using AI (A8-A10), not teams choosing configurations |

Search results and competitor page counts demonstrate discoverability, not query volume or acquisition efficiency. Candidate channels are local-model communities, model/runtime integrations, developer search and consultancy referrals.

## Bounded next learning proposal for #58 and #63

**Research recommendation, 2026-10-18; not an executed campaign.** Start with one project-owned passive opt-in entry point and one prospective **team workspace buyer** cohort. This reuses a channel already listed in [#63's approval package](customer-validation.md#1-recruitment-channels-for-approval). It asserts neither existing traffic nor permission to contact a community, collect participant information, deploy a funnel or take payment. Source access and the arithmetic above cannot establish any of those conditions.

The target is a technical team considering the [accepted #58 bounded local/API decision-record comparison](mvp-analysis.md#current-narrowed-recommendation-2026-10-18), with a person who can identify the workspace's purchase decision and payer. The workload can remain single-user text inference even when a team buys the decision record. Team, person, workload and purchasing unit are different counts. The team's recurring decision need, usefulness of the record and willingness to pay are hypotheses; this recommendation does not select a product launch or expand optional-stack scope.

The following are **proposed measurement definitions**, with every duration an analyst design choice rather than a measured sales-cycle or an adopted #63 operational value. Before a later test, the owner must pin the actual entry point, eligibility text, instrument, complete benefit/price card, identity/deduplication method and lawful participant handling through #63's existing decisions. Preserve the test version and its original denominator definitions; changes create a separately reported cohort.

| Item | Proposed definition | What a later observation can establish |
| --- | --- | --- |
| Channel and enrollment window | One versioned project-owned passive entry point; enroll for 28 consecutive days after its actual start is recorded. Keep other channels separate | Observed entrants through this entry point; not the size of a community, search audience or addressable market |
| Buyer/account unit | One prospective workspace with one identified purchase decision. Count multiple contacts from that workspace once; separate workspaces in one firm only with evidence of independent purchase decisions. Unresolved identity stays unclassified | Deduplicated purchasing units, without treating respondents, seats or firms as interchangeable |
| Qualified cohort, R | Count all eligible, consented workspaces initially enrolled in the window; eligibility requires a described local/API configuration decision and identifiable buyer. Report screened-out, unknown-eligibility and withdrawn counts separately under the approved retention rules; do not silently drop withdrawals from the original denominator | Observed qualified entrants. It does not replace the assumed potentially reachable population outside the observed channel |
| Activation, A | Among R, complete the fixed narrow decision-record/reconstruction task within seven days of first entry, using the predeclared fields and baseline from #58/D-57-1–3. Record partial attempts and instrument failures separately | A/R for that task and cohort. Completion is not repeat use, compatibility, fit, quality, cost accuracy or willingness to pay |
| Paid outcome, P | Among A, a completed non-test purchase of the exact paid offer within 28 days of first entry, with amount, period, cancellation/refund status and observation cutoff recorded. If no authorized functioning purchase module exists, P and paid conversion are unmeasured | P/A conditional on that offer, price and window; a sign-up, interview answer, waitlist entry or checkout click is not a purchase |
| Observation completion | Follow every enrolled workspace for the full 28 days, so the last entrant finishes after enrollment closes. Report missing/withdrawn/censored outcomes and their denominators rather than silently calling them non-buyers | An interpretable cohort result; incomplete observation cannot produce a complete conversion rate |
| Annual scenario replacement | To replace the historical annual-price rows directly, observe the defined annual offer and its full-year payment condition. A monthly offer, including #54's proposed workspace/month card, needs a separately versioned payment/retention model | Correct period and buyer mapping; neither a monthly response nor a single payment proves twelve payments or annual retention |

Traffic-event counts, if authorized and available, require their own bot/repeat/attribution definition; they are not automatically R. Do not inflate the observed cohort into a market estimate or carry rates to another channel, segment, offer or period. Actual counts remain integers; report the full stage counts and uncertainty arising from the actual design before judging repeatability. No conversion-success threshold, sample-size sufficiency or population-confidence claim is adopted here.

This cohort proposal is separate from #63's purposive qualitative interviews and its proposed maximum channel share. Interviews can refine eligibility, buyer roles, benefit comprehension, prior frequency and stated price reactions. A purposive interview quota cannot supply the traffic or paid-conversion denominator above. Qualitative findings that challenge the recurring need or the offer should narrow or stop this hypothesis; absent demand evidence remains absent. Completing #53's desk analysis does not require conducting that later fieldwork, and accepting this definition does not approve #63's D-01–D-17 operational choices.

## Decision record and handoffs

Conclusion (hypothesis, Low confidence): the dated sources describe substantial AI use in their different populations (A1, A4, A8, A10), while switching and organizational decision contexts motivate a recurring configuration-need hypothesis (A6, A7). They do not establish its frequency, effort, reachable buyers or paying demand. Series/method changes limit trend comparison. The scenario spread follows from selected unmeasured assumptions; it is not evidence that the high outcome is attainable or that one unknown empirically dominates.

Conditional recommendation for #58: use the defined passive-channel/team-buyer cohort as the next demand-learning proposal for the already narrowed decision-record comparison. Establish the actual offer and measurement capability before replacing any assumption. The first questions are whether eligible buyers enter, can use/reconstruct the bounded record and report a recurring decision need; an actual paid module would answer a separate offer-conditioned purchase question. Neither subscriptions nor referrals become qualified by this note, and a failed or unavailable instrument is not evidence that the underlying value is absent.

| Receiving issue | Claim offered | Disposition |
| --- | --- | --- |
| #2 (T0 workload) | Sizing scenarios | Rejected as a #2 input by the #2 owner in the PR #67 review at `6511dea` ("Sizing scenarios change no workload field"); kept as #47 context |
| #39 (T6 cost) | Assumed USD annual cohort amounts and charging-period boundaries; no pricebook rate, cost estimate, margin or billing-unit change | Current scoped engineering receiving review pending; retain explicit annual-payment assumptions and all #64 incomplete-cost limits |
| #58 (MVP) | The bounded passive-channel/team-workspace learning proposal, linked to the accepted narrow decision-record comparison | Current scoped engineering receiving review pending; no demand, reachable-market, fieldwork, implementation or launch result is supplied |

The original #2 rejection remains unchanged; neither a funnel definition nor an assumed price changes a workload field. The actual current #39/#58 receiving receipt, final source review, required checks and canonical delivery must be recorded before #53 completion. Those are documentary/engineering acceptance gates; future traffic, participants, transactions and commercial viability remain separate evidence stages.

## Source and arithmetic readback, 2026-10-18

This research-session pass read the primary publications below. It adds no raw report, dataset, contact information or payment data to the repository. Source-specific permission to redistribute those materials or use them in a product remains unassessed here; the note uses attributed factual paraphrases and links, and [#60's use-specific boundaries](rights-validation.md) remain effective. A public source or checksum grants no new retrieval/display/redistribution permission.

| Source | Actual readback and exact scope | Retained limitation |
| --- | --- | --- |
| Stanford AI Index PDF linked in A1 | Downloaded 2026-10-18 at 12:13:05Z, 37,885,501 bytes, SHA-256 `fff5ac1df971cee7daf847fa5ed00dd7444db693092821c3e691debc1eaada09`. Read PDF pages 45, 173, 193, 197, 198, 396 and 397; visually inspected the chapter highlight, adoption/agent charts and methods page. The later page-173 check independently confirms A1's 70% highlight versus 79% detailed result. Corrected A2's chart-caption locator and separated A3's upload/download populations | Publisher compilation and its survey/platform methods, not independent user, buyer or demand measurement; the unresolved 79%/70% difference and swapped prose figure references are retained as source limitations |
| Stack Overflow AI data and methodology linked in A4/S-method | Read the current question figures, bases, field dates and validity rules. Corrected the organization-required-or-recommended option and the unsupported inference that all denominator differences are item non-response | Self-selected survey, changing local extract and conditional question bases; no representative market or bot-prevalence estimate |
| Census National workbook linked in A8 | Downloaded 2026-10-18 at 12:13:05Z, 88,868 bytes, SHA-256 `d905e1b7ad042971e67e8b4b36a50a3050522cb675c609056c7ba374b88c8668`. Read `Response Estimates` E1/E16/E82 and matching standard errors E16/E82; matched 202620 to `Collection and Reference Dates` D81:I81. Confirmed 23.8%, 27.7%, 0.41/0.36 percentage-point SEs and the stated collection/reference/publication dates; 202601/202609 remain 17.7%/19.8% | The workbook retains the shutdown's structural gaps, not zero observations. Current official story read confirms the November 2025 wording change; business use is not a paid decision-tool market |
| Eurostat news and Statistics Explained linked in A10 | Read figures, 10+ enterprise/sector scope, conditional A11 denominator and 2025 methodology caveats. Added the Netherlands series break and newly included generation category | No new Eurostat API extraction; its prior access/update metadata stays historical. Changes limit simple like-for-like trend claims |
| Hugging Face API/download documentation linked in L1 | Read the 30-day versus all-time definitions, query-file GET/HEAD counting and documented GGUF double counting. The current model-list API retrieval failed; no fresh model count was obtained | L1's counts remain the dated 2026-10-16 observation, not refreshed values or unique people |
| Ollama library linked in L2 | The current page showed llama3.1 120.4M, deepseek-r1 93.8M, nomic-embed-text 91.1M, llama3.2 85.7M and qwen2.5 42.8M pulls. L2 preserves its original 2026-10-16 counts separately | The mutable rounded counter and undocumented counting window cannot establish buyer growth or a local-only audience |

An independent in-session Apple engineer recomputed the unchanged three scenario revenues/payer counts, all sixteen low/high sensitivity amounts, eight ratios, the four joint endpoints (two ranges) and both 80× conversion products using Decimal arithmetic against accepted main `a8e73247b54fee46555c757b19f0be9aed776258`, original note blob `ee9b9134e889f17c37ab0604c96e6db6f03c7d43`. All arithmetic matched. That review identified cohort/annual-period, fractional-payer, offer-dependence and recurring-need interpretation gaps. The same engineer independently read the amended scenario and prospective-cohort logic at `4ca60d05732a204c3b9568e1fd8acc58585daadb`, note blob `af598e4f942a4ff62184d2402b2481affe352ed1`, and found those gaps resolved, with all eleven original numeric table rows byte-identical. This records actual bounded arithmetic/logic review; it supplies no primary-source, participant or transaction execution by that reviewer, or a #39/#58 receiving decision. The current final evidence/receiving review and delivery gates remain separate.

| Literal #53 criterion | Delivered section / evidence | Remaining acceptance for this candidate |
| --- | --- | --- |
| Review dated adoption evidence | A1-A11/L1-L2, S-method and exact 2026-10-18 readback | Independent final evidence review |
| Distinguish use from purchase intent | Use-versus-intent section; source/participant/transaction limits throughout | Preserve the distinctions in receiving use |
| Build explicit sizing scenarios | Unchanged formulas, three scenarios, both sensitivity tables and cohort/period clarifications | Final logic review; no fieldwork required to validate arithmetic |
| Record missing search and conversion evidence | Unknowns table and prospective measurement definitions | Remain unknown until a separately authorized eligible observation |
| Link every significant conclusion to evidence or hypothesis | Source IDs/URLs/dates/methods and explicit analyst scenario/protocol choices | Independent final evidence review |
| Relevant technical review; name unresolved decisions | Preserved #2 rejection and exact #39/#58 receiving scopes | Actual current #39/#58 receipt and canonical ledger reconciliation |
| Repository checks and evidence acceptance before Done | Exact submitted-tree checks and source/logic reviews belong in the delivery receipt | Required commands, current-head review and signed canonical delivery pending |

## Proposed source-register additions

Not applied to `sources.json`; for the register owner (#48) to review. Existing IDs `src-ai-index`, `src-survey-method`, `src-survey-knowledge` and `src-survey-trust` already cover A1-A3 and the Stack Overflow methodology/knowledge/trust pages.

| Suggested ID | Publisher | URL | Access date |
| --- | --- | --- | --- |
| src-survey-ai | Stack Overflow (Stack Exchange Inc.) | https://survey.stackoverflow.co/2026/ai | 2026-10-16 |
| src-survey-ai-data | Stack Overflow (Stack Exchange Inc.) | https://survey.stackoverflow.co/2026/ai/data | 2026-10-16 |
| src-census-btos-national | U.S. Census Bureau | https://www.census.gov/hfp/btos/downloads/National.xlsx | 2026-10-16 |
| src-census-ai-story-2026-05 | U.S. Census Bureau | https://www.census.gov/library/stories/2026/05/ai-use-businesses.html | 2026-10-16 |
| src-eurostat-ai-news-2025 | Eurostat | https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2 | 2026-10-16 |
| src-eurostat-ai-explained | Eurostat | https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises | 2026-10-16 |
| src-hf-api-downloads | Hugging Face | https://huggingface.co/api/models?sort=downloads&direction=-1&limit=10&filter=text-generation | 2026-10-16 |
| src-hf-download-stats-doc | Hugging Face | https://huggingface.co/docs/hub/models-download-stats | 2026-10-16 |
| src-ollama-library | Ollama | https://ollama.com/library?sort=popular | 2026-10-16 |
