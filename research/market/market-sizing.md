# Market boundaries, demand and sizing

Status: desk analysis, 2026-10-16 (revised for #53). Not a revenue forecast, not a TAM/SAM/SOM finding and not a purchase-intent measurement. All source access dates are 2026-10-16 unless stated.

Adoption is a broad enabling condition, not a count of buyers for configuration advice. None of the sources below estimates willingness to pay for Pick Your AI or demand for a configuration-decision tool.

## Decision market and counting units

Define the market by a recurring decision: selecting or revising a multi-component AI configuration (model, runtime, hardware or hosted provider, retrieval/agent stack). Exclude all general AI spend, model training capital and cloud revenue from the product's addressable-revenue denominator. Distinguish individual comparison users, team collaboration buyers and enterprise governance buyers; their purchase processes are different.

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
| A1 | [Stanford HAI, AI Index Report 2026](https://hai.stanford.edu/assets/files/ai_index_report_2026.pdf), ch. 4 "Economy", sec. 4.3 Corporate AI Adoption, Figure 4.3.1, p. 193 | 88% of respondents say their organization uses AI in at least one business function (78% in 2024); 79% regularly use generative AI in at least one function (71% in 2024) | McKinsey "State of AI in 2025" online survey, 1,993 participants in 105 nations, fielded 2025-06-25 to 2025-07-29, weighted by national GDP share; 38% from organizations with >$1B revenue (Appendix, p. 396) | 2025 | Self-reported survey, secondary compilation by AI Index / Medium | The report itself calls these results "directional rather than comprehensive"; respondents skew to large firms; one respondent per organization is not guaranteed; measures any AI use |
| A2 | Same report, sec. 4.3, text p. 197 and Figure 4.3.7, p. 198 | Scaled AI-agent use "in the single digits for nearly all functions"; even in IT and knowledge management, "about two-thirds or more of respondents reported no use" | Same McKinsey survey | 2025 | Self-reported survey, secondary / Medium | Agent stage is self-classified; not specific to configuration decisions |
| A3 | Same report, ch. 1, sec. 1.5 Open-Source AI Software, printed p. 44 (PDF p. 45), Figures 1.5.6-1.5.8 | Hugging Face model uploads "more than tripled" 2023-2025; dataset uploads grew fourfold | Hugging Face metadata; downloads from Longpre et al. (2025) weekly panel of top 200 models per week, covering 49.6% of normalized downloads, Mar 2020-Aug 2025 | 2022-2025 | Platform activity, secondary analysis / Medium | Uploads and downloads are developer-activity proxies, not users or buyers; top-200 restriction drops the long tail |
| A4 | [Stack Overflow Developer Survey 2026, AI](https://survey.stackoverflow.co/2026/ai) and [AI full data](https://survey.stackoverflow.co/2026/ai/data), question "Do you currently use AI tools or AI agents in your role at work?" | 65.9% use AI coding assistants or agents; 62.5% general-purpose chat tools; 26.2% agents or automated workflows; 17.2% use no AI tools (n = 17,464) | Online survey of developers and technologists | Fielded 2026-06-23 to 2026-08-05 | Self-reported, self-selected survey / Medium for respondents, Low for generalization | See S-method below |
| A5 | Same data page, "How often do you use each of these AI tools...?" | 77% overall daily users; 73.0% daily for coding assistants (n = 14,478) | As A4 | 2026 | As A4 | Frequency of use, not willingness to pay |
| A6 | Same data page, "In the past year, have you switched from one AI tool to another for work?" | 33.7% did not switch; 25.1% switched for better output quality; 10.6% because the organization required it; 6.4% for lower cost; 2.1% for access to a preferred model/provider (n = 13,144) | As A4 | 2026 | As A4 | Closest public signal to a recurring tool/model decision, but measures switching, not evaluation effort or demand for advice |
| A7 | Same data page, "Which of the following best describes how AI tools or agents are used at your organization today?" | 29.7% mostly optional and individual-led; 24.0% approved tools and guidance; 6.1% organization does not use AI (n = 13,167) | As A4 | 2026 | As A4 | Suggests both individual and organizational decision contexts exist; says nothing about who would pay |
| A8 | [U.S. Census Bureau, BTOS National estimates](https://www.census.gov/hfp/btos/downloads/National.xlsx), sheet "Response Estimates", question 7 ("In the last two weeks, did this business use AI in any of its business functions?") and question 24 (next six months) | Cycle 202620: 23.8% used AI (SE 0.41 pp); 27.7% expect to use AI in the next six months (SE 0.36 pp). Cycle 202609: 19.8%. Cycle 202601: 17.7% | Biweekly, nationally representative survey of U.S. employer businesses. Cycle 202620 collected 2026-09-21 to 2026-10-04, reference period 2026-09-07 to 2026-09-20, published 2026-10-08 (sheet "Collection and Reference Dates") | 2026-09 | Official statistical survey, firm self-report / High for the stated measure | Question wording changed in November 2025 from "producing goods or services" to "any business function", so pre-change cycles are not comparable; counts firms, not users or decision events; no estimates for cycles 202521-202523 (federal shutdown) |
| A9 | [U.S. Census Bureau, "Large Firms With at Least 20 Employees Biggest AI Users"](https://www.census.gov/library/stories/2026/05/ai-use-businesses.html), published 2026-05-26 | Use 17%-20% Dec 2025-May 2026; 37% of firms with 250+ employees; 32% of firms with 100-249; under 20% of firms with 4 or fewer; Information sector 39.7% vs national 19.8% (period ending 2026-05-03) | BTOS, Dec 14 2025 to May 3 2026 | 2025-12 to 2026-05 | Official statistical publication / High | Same unit and wording limitations as A8; superseded in level by A8 |
| A10 | [Eurostat news, "20% of EU enterprises use AI technologies"](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20251211-2), 2025-12-11; [Statistics Explained, Use of AI in enterprises](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises), Figures 1-3, dataset `isoc_eb_ai` | 20.0% (19.95%) of EU enterprises used AI in 2025, up from 13.5% in 2024; small 17%, medium 30.36%, large 55.03%; information and communication sector 62.52% | 2025 EU survey on ICT usage and e-commerce in enterprises; enterprises with 10+ employees or self-employed persons, NACE Rev. 2 sections C-J, L-N and group 95.1 | 2025 (data extracted Dec 2025; next update planned Dec 2026) | Official statistical survey / High | Excludes micro-enterprises and some sectors; AI defined by a technology list; annual Dataset `isoc_eb_ai` (Eurostat API, last updated 2026-06-15) gives 19.95% for 2025 and 13.48% for 2024 (EU27, enterprises with 10+ employees). |
| A11 | Same Statistics Explained article, "Reasons for not using AI technologies" | Among enterprises that had considered AI but did not use it: lack of relevant expertise 70.89%; unclear legal consequences 52.52% | As A10 | 2025 | Official statistical survey / High | Expertise gaps are a plausible need, but this does not show demand for a configuration tool |

**S-method (Stack Overflow).** [Methodology page](https://survey.stackoverflow.co/2026/methodology): 30,903 valid responses from 169 countries out of 39,266 rows recorded 2026-06-23 to 2026-08-05; promoted through stackoverflow.com, stackoverflow.blog and an opt-in email list. Participation is voluntary and self-selected; the page makes no representativeness claim. The page describes its counts as the "current local response extract", so figures may change. Per-question n is far below 30,903 (10,926-17,464 for the AI questions), so item non-response is large. Do not extrapolate to all developers or enterprise buyers. The earlier [knowledge](https://survey.stackoverflow.co/2026/knowledge) and [trust](https://survey.stackoverflow.co/2026/ai/data/ai-trust) pages support testing source attribution (48.0% trust AI output "when I can easily verify the output", n = 14,304), not product demand.

### Local and self-hosted model activity (discoverability/usage proxy only)

These counters show that people fetch open-weight models for local or self-hosted use. They are not users, not buyers and not purchase intent.

| ID | Source | Figure as retrieved 2026-10-16 | Counting rule | Evidence class / confidence | Limitation |
| --- | --- | --- | --- | --- | --- |
| L1 | [Hugging Face Hub API, text-generation models sorted by downloads](https://huggingface.co/api/models?sort=downloads&direction=-1&limit=10&filter=text-generation) | Top model Qwen/Qwen3-0.6B: 29,878,421 downloads; Qwen/Qwen3-8B: 9,422,391 (all-time 132,402,789 via `expand[]=downloadsAllTime`) | `downloads` = last 30 days ([huggingface_hub HfApi reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api)); every GET or HEAD on a query file such as `config.json` counts, not unique downloaders ([Models Download Stats](https://huggingface.co/docs/hub/models-download-stats)) | Platform-published counter / Medium for activity, Low for people | Includes CI/CD and repeated fetches; small models are pulled by pipelines; not local-only |
| L2 | [Ollama library, sorted by popular](https://ollama.com/library?sort=popular) | llama3.1 120.3M pulls; deepseek-r1 93.8M; nomic-embed-text 90.6M; llama3.2 85.6M; qwen2.5 42.6M | Not documented on the page; appears cumulative | Vendor-published counter / Low | Undefined counting rule and window; includes automated pulls; cannot be converted to users |

Sources reviewed but not used as sizing inputs: AI Index Figure 4.2.22 (p. 192, Brynjolfsson et al. 2026: 115M U.S. adults using generative AI), which counts consumers in general rather than configuration decision-makers.

### Contradictions and weak points

- Organizational adoption differs by source and unit: 88% of McKinsey respondents' organizations (A1) versus 23.8% of U.S. employer businesses (A8) and 20.0% of EU enterprises with 10+ employees (A10). The difference reflects population (large-firm respondents vs representative firm samples) and question wording, not a trend contradiction. Use the official series for business prevalence and treat A1 as directional.
- All three business series show higher use in large firms and the information sector (A9, A10), which supports focusing on technical teams, but none counts the people inside those firms who make configuration decisions.
- Developer use is high among Stack Overflow respondents (A4, A5) but the sample is self-selected and cannot be weighted to a population.

## Use versus purchase intent

Every figure above measures current or expected use of AI, or platform activity. Purchase intent for a configuration-decision tool is not measured by any reviewed source. The closest signals are switching behavior (A6: 2.1% switched for a preferred model/provider, 6.4% for cost) and expertise barriers (A11); both are hypotheses about need, not evidence of willingness to pay. Purchase intent and price acceptance remain unknown until #63 produces approved interview or test results. #52's personas remain hypotheses.

## Explicit scenarios, not market measurements

Annual subscription revenue = reachable qualified accounts × activation share × paying share among active accounts × annual price per account. Paying accounts = reachable × activation × paying share. All inputs are analyst assumptions in USD, not verified demand or proposed final prices. Individual and team accounts are separate units and are never added together.

| Scenario | Account unit | Reachable accounts (assumption) | Activation (assumption) | Paid among active (assumption) | Annual price, USD (assumption) | Paying accounts | Annual gross subscription revenue, USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Small validation channel | Individual | 1,000 | 10% | 5% | $120 | 5 | $600 |
| Focused developer channel | Individual | 10,000 | 20% | 5% | $120 | 100 | $12,000 |
| Team-oriented channel | Team | 10,000 | 20% | 10% | $600 | 200 | $120,000 |

Arithmetic check (2026-10-16): 1,000 × 0.10 × 0.05 × 120 = 600; 10,000 × 0.20 × 0.05 × 120 = 12,000; 10,000 × 0.20 × 0.10 × 600 = 120,000. The scenario values are unchanged from the earlier draft; only the account unit is now stated. Reaching 10,000 qualified team accounts is a much stronger assumption than reaching 10,000 individuals; no sourced count of teams making configuration decisions exists.

The large spread is the conclusion: distribution, activation, buyer identity and price dominate the estimate. These are neither TAM/SAM/SOM estimates nor evidence of attainable revenue. Exclude acquisition, churn, taxes, payment fees, support and data-license costs here; measure them before interpreting profitability.

## One-at-a-time sensitivity

Each row changes one input to its low or high bound and holds the others at the base scenario. Bounds are analyst assumptions chosen to bracket plausible uncertainty, not sourced ranges.

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

All-low/all-high combinations span $30 to $480,000 (individual) and $240 to $1,920,000 (team). These extremes show uncertainty width, not a confidence interval.

**Most influential input: reachable qualified accounts.** The model is a pure product, so a given percentage change in any input moves revenue by the same percentage; ranking depends only on how wide each input's plausible range is. Reach has the widest range (50× individual, 20× team) because no search-volume, channel or community-size evidence constrains it. Activation and paid share together form the conversion funnel; varied jointly they span 80× (individual) and 80× (team), so unmeasured conversion matters as much as reach. Price matters least within these bounds. Therefore the first validation should measure qualified reach and conversion in one channel, not refine price.

## Missing evidence (recorded as unknown, not zero)

| Input | Status on 2026-10-16 | Why not obtained / next step |
| --- | --- | --- |
| Absolute search volume | Not obtained | No keyword-volume tool or Search Console property; paid keyword tools are out of scope |
| Google Trends relative interest | Not obtained | Unauthenticated request to the Trends explore endpoint returned HTTP 429; no index values recorded |
| Customer acquisition cost | Unknown | No ad, landing-page or outreach experiment run |
| Activation and paid conversion | Unknown | Requires an approved #63 test; no industry average is substituted |
| Purchase frequency / decisions per account | Unknown | Not measured by any reviewed source |
| Willingness to pay | Unknown | No approved interviews or price tests |
| Competitor revenue, active users, concentration | Not established | No primary disclosures found in reviewed sources |
| Count of teams making configuration decisions | Unknown | Business surveys count firms using AI (A8-A10), not teams choosing configurations |

Search results and competitor page counts demonstrate discoverability, not query volume or acquisition efficiency. Candidate channels are local-model communities, model/runtime integrations, developer search and consultancy referrals.

## Decision record and handoffs

Conclusion (hypothesis, Low confidence): enabling conditions are present and growing (A1, A4, A8, A10), and a recurring model/tool choice exists (A6, A7), but there is no evidence yet of reachable, paying demand for a configuration-decision tool. Scenario outcomes are dominated by unmeasured reach and conversion.

Conditional recommendation for #58: validate one narrow channel (for example, a local-model community) with a landing proposition and measure qualified visits, activation and return use before expanding the catalog. Treat the team scenario as untested until a team buyer is identified in #63.

| Receiving issue | Claim offered | Disposition |
| --- | --- | --- |
| #2 (T0 workload) | Sizing scenarios | Rejected as a #2 input by the #2 owner in the PR #67 review at `6511dea` ("Sizing scenarios change no workload field"); kept as #47 context |
| #39 (T6 cost) | Price assumptions are analyst placeholders, not pricebook rates | Unresolved; owner disposition not yet recorded |
| #58 (MVP) | Conditional recommendation above | Unresolved; awaits #58 owner review |

Evidence review by the program coordinator is required before this note is treated as complete.

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
