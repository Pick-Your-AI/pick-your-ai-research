# Customers and jobs to be done

Issue: [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52). Child validation: [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63) ([customer-validation.md](customer-validation.md)). Original source observations retain their 2026-10-16 access date; the final review section records a separate 2026-10-18 source and protocol check.

Status: **desk personas and hypotheses, not validated customers.** No interviews were run, no one was contacted and no personal data was collected. Nothing here establishes demand, frequency of decisions or willingness to pay; those belong to #63 after the coordinator approves recruitment, consent, retention and anonymized reporting.

## How to read this note

- **Evidenced** means a cited primary source supports the specific statement, within that source's population and method. Survey percentages describe the survey's respondents, not the segment.
- **Hypothesis** means an analyst assumption to test in #63. Every job, role split and segment-to-alternative usage claim below is a hypothesis unless a source is cited next to it.
- Alternative IDs refer to entries in [competitors.json](competitors.json). The catalog evidences that an alternative exists and what it documents; it does not evidence that a given segment uses it.
- Evidence classes follow [docs/RESEARCH_METHOD.md](../../docs/RESEARCH_METHOD.md) (Primary documentation, Vendor claim, Independent measurement, Estimate). "Hypothesis" is a claim status, not a grade, following tynamite's PR #67 review.

## Desk evidence

### Stack Overflow Developer Survey 2026 (developer population only)

Publisher: Stack Overflow / Stack Exchange Inc. Evidence class: Primary documentation of the publisher's own survey results (self-reported answers). Licence noted on data pages: ODbL 1.0.

**Method** ([methodology](https://survey.stackoverflow.co/2026/methodology)): fielded 2026-06-23 to 2026-08-05; 39,266 rows recorded, 30,903 marked valid, from 169 countries. Promoted through stackoverflow.com, stackoverflow.blog and Stack Overflow's email list. The page defines a recruitment frame (community members and opted-in email recipients), not a target population, and has no limitations section. Validity rules use Qualtrics response-quality flags plus a substantive-response recovery rule. Publication date is not stated.

**Limitation applying to every figure below:** self-selected, Stack Overflow-engaged developers; items are optional, so each question has its own n that is much smaller than 30,903. These figures cannot be generalized to non-developers, enterprise buyers or approvers, and AI adoption or trust is not willingness to pay for this product.

| Claim (respondents to that question) | Figure | Page | Confidence |
| --- | --- | --- | --- |
| Source attribution matters when judging AI answers | 52.1% very important, 26.5% important, 14.0% somewhat important (n = 13,945) | [knowledge](https://survey.stackoverflow.co/2026/knowledge) (`#knowledge-sources-and-trust`) | Medium |
| Trust in AI output is conditional on verification | 48.0% "I trust it when I can easily verify the output"; 6.6% trust it for important work decisions; 12.3% do not trust it for most work tasks (n = 14,304, single-select) | [ai-trust](https://survey.stackoverflow.co/2026/ai/data/ai-trust) | Medium |
| Tool switching in the past year and the primary reason | 33.7% did not switch; 25.1% switched for better output quality; 10.6% because their organization required or recommended it; 7.4% integration; 6.4% lower cost; 3.3% previous tool too expensive, limited or unavailable; 2.1% access to a preferred model or provider (n = 13,144, single-select) | [ai-tool-switch](https://survey.stackoverflow.co/2026/ai/data/ai-tool-switch) | Medium |
| Cost or usage limits changed how respondents personally use AI at work | 32.6% monitor their own use; 25.3% choose cheaper models when possible; 23.8% usage is metered; 22.4% not affected; 6.9% team switched to more affordable models or vendors; 12.8% team increased AI budget (n = 1,033, multi-select) | [ai-cost](https://survey.stackoverflow.co/2026/knowledge/data/ai-cost) | Low: small n relative to the survey; route and filter not explained |
| Reasons to avoid AI at work or school | 41.3% do not avoid AI; 13.0% cite privacy or security; 15.2% moral or ethical concerns (n = 13,857) | [ai-avoid](https://survey.stackoverflow.co/2026/ai/data/ai-avoid) | Medium |

What this supports: in this developer sample, tool choices change (about two thirds of respondents to the switching question switched), quality is the leading stated reason, and 10.6% of all 13,144 respondents to that question cited a switch required or recommended by their organization. Cost is a minority primary reason. That makes it plausible that recurring tool/model decisions exist and that the user is not always the decider. It does not show that the decisions are multi-component, that they are painful, or that anyone would pay for help with them. It also argues against assuming cost is the main priority.

### Enterprise and business populations (non-developer)

| Source | Population and method | Figures | Evidence class / confidence | Limitation |
| --- | --- | --- | --- | --- |
| [Eurostat, "Use of artificial intelligence in enterprises"](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises) (Statistics Explained; data extracted December 2025; datasets `isoc_eb_ai`, `isoc_eb_ain2`) | EU enterprises with 10+ employees and self-employed persons in listed NACE sectors (manufacturing, energy, construction, trade, transport, accommodation, ICT, real estate, professional, administrative services, repair of computers). National statistical surveys; about 157,000 of 1.53 million enterprises surveyed | 2025: 19.95% of enterprises used at least one AI technology; 17% small (10–49), 30.36% medium (50–249), 55.03% large (250+). Among enterprises that did not use AI but had ever **considered** it, lack of relevant expertise was the most cited reason for not using it (70.89%), then unclear legal consequences (52.52%) and data protection/privacy (48.83%); "not useful" was least cited (20.68%) | Primary documentation (official statistics); High for the stated population | Measures enterprise adoption, not decision frequency, tooling or spend. The page attributes data to the "2024 EU survey" while reporting 2025 figures; check the dataset metadata before reuse. Unreliable national data are included in EU aggregates; NL has a 2025 series break |
| [US Census Bureau, "Large Firms With at Least 20 Employees Biggest AI Users"](https://census.gov/library/stories/2026/05/ai-use-businesses.html) (2026-05-26; Grundy, Breaux, Khatiwoda) | Business Trends and Outlook Survey (BTOS), biweekly, described as nationally representative US businesses; AI supplement since 2025-11-17. Current use = used AI in any business function in the past two weeks | 2025-12-14 to 2026-05-03: current use 17–20% (19.8% as of 2026-05-03); expected use in the next six months 20–23%. 37% of firms with 250+ employees and 32% with 100–249 reported use; under 20% of firms with four or fewer employees. Information sector 39.7%, finance and insurance 33.9% | Primary documentation (official statistics); Medium: supplement is labelled an experimental product | Question wording changed in November 2025 ("in producing goods or services" to "in any business function"), so earlier figures are not comparable. Sample size and response rate are not on the page. Latest biweekly estimate: cycle 202620 (collected 2026-09-21 to 10-04) reports 23.8% used AI in the last two weeks and 27.7% expect to within six months ([National.xlsx](https://www.census.gov/hfp/btos/downloads/National.xlsx), "Response Estimates", questions 7 and 24, checked 2026-10-16). |

What this supports: AI adoption is concentrated in larger organizations and specific sectors; in the EU, expertise (not perceived usefulness) is the leading stated barrier among firms that did not use AI but had considered it. This is consistent with, but does not demonstrate, a need for decision support among enterprise architects, IT administrators and consultancies. Neither source measures who chooses components, how often, or what they spend.

## Segment map

The ten segments are unchanged from the PR #67 draft. Role columns use: **user** (does the configuration work), **buyer** (controls the budget or pays), **approver** (can veto on policy, security or procurement). All role assignments are hypotheses unless marked.

| # | Segment (as defined) | User / buyer / approver (hypothesis) | Overlaps |
| --- | --- | --- | --- |
| 1 | Local AI enthusiasts | Same person for all three when self-funded; no organizational approver | Individual developers (2), AI researchers (9) when hobby and work mix |
| 2 | Individual developers | User always; buyer when self-funded or using a personal card; employer becomes buyer/approver for work use. Stack Overflow shows 10.6% of respondents to the switching question reported switching because their organization required or recommended a tool (evidenced for that sample only) | 1, 3; may be the user inside 5, 6 or 7 |
| 3 | AI application developers | User; buyer is usually a team lead, founder or client; approver may be security or platform team | 2, 4, 6, 10 |
| 4 | ML engineers | User; buyer is team or infrastructure budget owner | 3, 5, 9 |
| 5 | Infrastructure engineers | User and often technical recommender; buyer is engineering or finance budget owner; approver may be procurement | 4, 8 |
| 6 | Startup founders | Often buyer and approver; may also be user in small teams | 2, 3; may hire 10 |
| 7 | Enterprise architects | Recommender and policy approver; rarely the payer; may not do hands-on configuration | 5, 8; client of 10 |
| 8 | IT administrators | User for deployment/management and approver for installation rights; buyer is IT budget owner | 5, 7 |
| 9 | AI researchers | User; buyer is grant, lab or employer; approver may be PI or compute allocation committee | 1, 4 |
| 10 | AI consultancies | User on client work; client is buyer; consultancy may buy its own tooling | 3, 6, 7 |

Unsupported subdivisions: none added. The overlaps mean one participant can match several segments; #63 must record a primary segment plus secondary matches rather than counting one person twice.

## Jobs to be done

Format: **trigger → constraint → consequence of a bad choice.** All jobs are hypotheses until #63 reports reconstructed decisions.

### 1. Local AI enthusiasts
- **Job:** Decide what runs on hardware I already own. Trigger: a new model release or a hardware purchase. Constraint: fixed VRAM/RAM and no cloud budget. Consequence: wasted download time, out-of-memory failures, or an unnecessary hardware upgrade.
- **Alternatives (catalog):** `llmfit`, `modelfit`, `canrun`, `canitrun`, `local-ai-planner`, `ollama`, `hugging-face`.
- **Catalog-backed scope:** the listed alternatives have different documented roles. The catalog records hardware-fit scope for `llmfit`, `modelfit`, `canrun`, `canitrun` and `local-ai-planner`; it records `ollama` as a model library/runtime substitute and `hugging-face` as a model hub. This does not establish segment usage or independently tested fit accuracy. tynamite's PR #67 review accepted this persona for #2/#3 and identified it as #81's local-first case (`hardware.mode: use_existing`); that is a technical-fit acceptance, not demand evidence.
- **Hypothesis:** that uncertainty about fit, not installation effort, is the bottleneck; that existing fit tools are insufficient.

### 2. Individual developers
- **Job:** Choose a model or provider for a workload. Trigger: a new project, a quality problem, a price or limit change. Constraint: personal budget or employer-approved tools. Consequence: poor output quality, unexpected cost, or rework when switching.
- **Alternatives:** `openrouter`, `artificial-analysis`, `arena`, `llm-stats`, `models-dev`, `benchlm`.
- **Evidenced (developer sample only):** 25.1% of Stack Overflow respondents switched tools for output quality and 6.4% for lower cost in the past year; 25.3% of a much smaller subset choose cheaper models when possible.
- **Hypothesis:** that the choice spans multiple components rather than one model; how often it recurs; switching cost.

### 3. AI application developers
- **Job:** Assemble a workable RAG or agent stack. Trigger: a new application or a failed prototype. Constraint: integration with existing data and frameworks, team skills, deadline. Consequence: rebuilding on a different framework or vector store after early commitment.
- **Alternatives:** `dify`, `langflow`, `flowise`, `n8n`, `langchain`, `llamaindex`, `langfuse`, `ragas`, `flocci`.
- **Evidenced:** these builders and frameworks exist (catalog). 7.4% of Stack Overflow respondents to the switching question cited workflow integration as their primary reason for switching; the denominator includes respondents who did not switch.
- **Hypothesis:** that planning before building saves measurable effort compared with prototyping in these tools.

### 4. ML engineers
- **Job:** Match model, quantization and serving runtime. Trigger: moving a model to production or new hardware. Constraint: latency, memory and accuracy targets. Consequence: degraded accuracy from quantization or unexpected serving cost.
- **Alternatives:** `hugging-face`, `llmfit`, `bentoml`, `lm-eval`, `unsloth`.
- **Evidenced:** tools exist (catalog).
- **Hypothesis:** the fidelity required compared with their own scripts and benchmarks.

### 5. Infrastructure engineers
- **Job:** Plan capacity, reliability and cost at concurrency. Trigger: load growth, a provider outage or a budget review. Constraint: available GPU supply, reliability targets, procurement lead times. Consequence: under-provisioning, outages or overspend.
- **Alternatives:** `skypilot`, `runpod`, `vast`, `gpus-io`, `bentoml`.
- **Evidenced:** tools exist (catalog).
- **Hypothesis:** procurement and operational constraints dominate; who signs off on capacity.

### 6. Startup founders
- **Job (revised wording):** Choose a stack that fits the product and the company's constraints. The PR #67 draft said "cheapest adequate stack", which assumed cost is the priority. The Stack Overflow switching data show cost as a minority primary reason among developers, so priority order (cost, speed to ship, quality, lock-in) is now an open question.
- Trigger: initial build, fundraising, investor or customer requirements. Constraint: runway and team size. Consequence: lock-in, migration cost, or spend that outgrows revenue.
- **Alternatives:** aggregators (`openrouter`, `artificial-analysis`) and managed builders (`dify`, `flowise`, `n8n`).
- **Hypothesis:** who owns budget and purchasing authority; which priority drives the choice.

### 7. Enterprise architects
- **Job:** Make explainable, compatible choices with provenance. Trigger: a new AI initiative, policy review or vendor renewal. Constraint: data residency, security policy, approved-vendor lists. Consequence: failed security review, compliance exposure, or a choice that cannot be justified later.
- **Alternatives (hypothesis):** existing vendor and platform evaluation processes. This note assigns no catalog ID to those processes; which alternatives this segment actually uses remains unverified.
- **Evidenced:** among EU enterprises that did not use AI but had considered it, unclear legal consequences (52.52%) and data protection (48.83%) are leading barriers (Eurostat, enterprise population). Larger firms adopt more (Eurostat, Census).
- **Hypothesis:** that architects, not procurement or security, own the configuration decision; procurement and residency requirements.

### 8. IT administrators
- **Job:** Deploy and manage permitted local or hosted tools. Trigger: user requests or a policy change. Constraint: installation rights, supportability, fleet management. Consequence: unsupported shadow tools or blocked users.
- **Alternatives:** `ollama` and managed services (provider-specific; not separately catalogued).
- **Evidenced:** 13.0% of Stack Overflow respondents cite privacy or security as a reason to avoid AI at work (developer sample).
- **Hypothesis:** installation rights, support and fleet needs; whether admins make or only enforce choices.

### 9. AI researchers
- **Job:** Compare systems reproducibly. Trigger: a paper, benchmark or review request. Constraint: pinned versions, compute allocation. Consequence: results that cannot be reproduced or compared.
- **Alternatives:** `harness-bench`, `lm-eval`, `hugging-face`, `qdrant-bench`.
- **Evidenced:** tools exist (catalog).
- **Hypothesis:** which versions and traces make a result reusable.

### 10. AI consultancies
- **Job:** Compare and share configurations with clients. Trigger: a new engagement or proposal. Constraint: client policies, billable time. Consequence: rework, lost bids or a recommendation the client cannot run.
- **Alternatives:** documents, spreadsheets and calculators (not catalogued), workflow platforms (`dify`, `n8n`), planners (`local-ai-planner`).
- **Hypothesis:** recurring project volume, collaboration and export needs; whether the consultancy or the client pays.

## Interview guide (neutral)

This guide is the instrument #63 will use if the coordinator approves the package in [customer-validation.md](customer-validation.md). It is not authorization to recruit or interview.

### Fixes to the PR #67 draft

| Issue in draft | Problem | Fix |
| --- | --- | --- |
| "Measure ... desire to reuse" | Leading: presumes the participant wants the concept | Removed. Concept reaction is collected with open questions at the end; intent is recorded only as stated intent, separate from behaviour |
| "Ask about existing spend before presenting hypothetical price points" | Presenting price points anchors answers | No researcher-supplied prices. Current spend is asked in Part C; any price-sensitivity question uses open-ended responses (see #63 WTP module) |
| "Cheapest adequate stack" | Assumes cost is the priority | Job reworded (segment 6); priorities are elicited, never suggested |
| No screener | Sample could contain only people who already have the problem | Screener below, including non-buyers and people with no recent decision |
| Sampling covered three of ten segments | Seven segments untested | #63 quota proposal covers all ten segments and three roles |
| Baseline vs prototype comparison | Requires a prototype and task protocol that do not exist | Deferred: the optional concept section is only a short description, and no task-completion metrics are claimed |

### Screener

Asked before scheduling. No employer name, email or other identifier is recorded in the screener answers (contact details live only in the separate consent/scheduling store described in #63).

1. Which best describes your main role? (open text, coded afterwards into the ten segments; "none of these" allowed)
2. In the last [N months, coordinator decision D-03], have you been involved in choosing any AI model, tool, service, hardware or hosting for yourself or others? (Yes / No / Not sure). **"No" is not screened out**; it fills the no-recent-decision quota.
3. If yes: in that decision, which of these did you do? (multi-select) did the hands-on setup or evaluation / recommended an option / approved or rejected it / paid for it or controlled the budget / none of these.
4. Who, if anyone, pays for the AI tools you use? (myself / my employer or client / free tools only / I do not use AI tools / not applicable / not sure)
5. Roughly how many people are in your organization? (bands: just me, 2–9, 10–49, 50–249, 250+, not sure; bands chosen to align with Eurostat size classes)
6. Country or region of residence (needed only for the coordinator's jurisdiction decision D-08; reported only at coarse region level).
7. Are you, or is your employer, building or selling a tool that recommends AI models, hardware or stacks? (conflict-of-interest check; recorded, not automatically excluded)

### Interview (about 45 minutes; order is fixed)

**Part A — Context (5 min).** Tell me about your work and where AI tools fit into it, if at all.

**Part B — Most recent decision (20 min).** Reconstruct one real past decision. If the participant reports none, go to Part B′.
1. Think about the most recent time you chose, changed or ruled out an AI model, tool, service, hardware or hosting option. What was it?
2. What started it?
3. Who else was involved? What did each person do?
4. Walk me through what you did, step by step. What did you look at or use?
5. How long did it take, from start to decision?
6. What information were you missing, if anything?
7. What happened afterwards? Did the choice hold, or did you change it?
8. What consequences, if any, did that decision have for you or your team?
9. Was there an earlier similar decision? If yes, when?

**Part B′ — No recent decision.** Do you use any AI tools today? If yes, how were they chosen and by whom? What, if anything, followed from those choices? If no, record that answer without assuming a missing need or asking the participant to invent a decision.

**Part C — Current alternatives and spend (10 min). No concept, product or price has been mentioned yet.**

If no relevant decision process, alternative or spend applies, record `not applicable` and skip the corresponding follow-ups. Retain non-use and no-purchase answers; do not convert them to a zero willingness-to-pay amount.

1. What do you currently use to make or check these decisions? (Probe each tool or source named; record catalog ID if it matches.)
2. What does that cost today, in money or time? Who pays for it?
3. Have you ever paid for anything specifically to help make this kind of decision (a tool, a consultant, a benchmark, a trial)? What was it, and who approved it?
4. What works well about how you do this now? What, if anything, would you change?

**Part D — Concept reaction (optional, last 10 min).** Read a neutral one-paragraph description (fixed text approved by the coordinator; it must not claim benefits). Then:
1. What, if anything, is this similar to?
2. If an actual decision was reported: where, if anywhere, would this have fitted into that decision? If none was reported, skip this question without inventing one.
3. What would stop you from using something like this?
4. Willingness-to-pay questions only as specified in the #63 module, and only after this point.

**Close.** Is there anything about how you make these decisions that I did not ask about?

### Wording rules
- Ask about past behaviour, not hypothetical future behaviour, until Part D.
- Do not name Pick Your AI's features, competitors or prices before the participant does.
- Do not use evaluative words ("hard", "painful", "frustrating", "cheapest") in questions; use the participant's own words in follow-ups.
- Record "don't know" and "not applicable" as answers, not missing data.

## Analysis questions for #63

1. How many participants report a decision in the window, and how many report a previous one (recurrence)?
2. Which segment and role made, recommended, approved or paid?
3. What alternatives were used, and did they suffice by the participant's own account?
4. What money or time is currently spent, and who controls it?
5. What consequences, if any, did participants report? Code actual events, anticipated risks and no reported consequence separately, without assuming a bad choice.

## Handoffs

| To | What | Status |
| --- | --- | --- |
| #63 | Interview guide, screener, segment/role map, analysis questions | Supplied in this note; #63 owns approval and execution |
| #2, #3 (tynamite) | Segment 1 local-first job | Historical tynamite acceptance at `6511dea` retained; the separately dated [delegated engineering receipt](#actual-technical-receiving-decisions-2026-10-18) receives the current note with constraints |
| #16 (zabyxc01), #25 (CompleteDotTech) | Segment 3 RAG/agent stack job | Current bounded input accepted with constraints in the [actual delegated engineering receipt](#actual-technical-receiving-decisions-2026-10-18); no absent-assignee response or backend/framework decision is inferred |
| #39 (PUSHINGSQUARES) | Revised segment 6 job and cost-priority caveat | Current priority/role input accepted with constraints in the [actual delegated engineering receipt](#actual-technical-receiving-decisions-2026-10-18); no rate, quantity, willingness-to-pay result or budget pass |
| #53, #54, #58 | Segment map, enterprise adoption figures, cost-priority caveat | Information only; no owner disposition recorded |

## Proposed source-register additions

Not applied to `sources.json` (owned by #48). Proposed entries:

| Proposed ID | URL | Publisher | Access date | Evidence class | Limitation |
| --- | --- | --- | --- | --- | --- |
| `src-survey-ai` | https://survey.stackoverflow.co/2026/ai | Stack Overflow | 2026-10-16 | Primary documentation (survey results) | Self-selected developers; optional items |
| `src-survey-tool-switch` | https://survey.stackoverflow.co/2026/ai/data/ai-tool-switch | Stack Overflow | 2026-10-16 | Primary documentation (survey results) | Single-select primary reason; n = 13,144 |
| `src-survey-ai-cost` | https://survey.stackoverflow.co/2026/knowledge/data/ai-cost | Stack Overflow | 2026-10-16 | Primary documentation (survey results) | n = 1,033; multi-select |
| `src-survey-ai-avoid` | https://survey.stackoverflow.co/2026/ai/data/ai-avoid | Stack Overflow | 2026-10-16 | Primary documentation (survey results) | Developer sample |
| `src-eurostat-ai-enterprises` | https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises | Eurostat | 2026-10-16 | Primary documentation (official statistics) | EU enterprises 10+ employees, listed sectors; survey-year label inconsistency |
| `src-census-btos-ai` | https://census.gov/library/stories/2026/05/ai-use-businesses.html | US Census Bureau | 2026-10-16 | Primary documentation (official statistics) | Experimental supplement; November 2025 wording change |

Existing entries `src-survey-knowledge`, `src-survey-method` and `src-survey-trust` are already registered.

## Source and protocol review, 2026-10-18

This is a separately dated documentary check of the existing desk evidence. The
original survey figures, ten segment definitions, jobs, role hypotheses and
historical receiving receipt remain unchanged. Reading a publisher's results
does not independently reproduce its survey or validate these personas.

| Input checked | Actual readback | Boundary retained |
| --- | --- | --- |
| Stack Overflow methodology and five question tables | The [methodology](https://survey.stackoverflow.co/2026/methodology) matches the original fielding dates, row counts, validity rules and recruitment frame. The [source-attribution](https://survey.stackoverflow.co/2026/knowledge/data/knowledge-source-ai), [trust](https://survey.stackoverflow.co/2026/ai/data/ai-trust), [switching](https://survey.stackoverflow.co/2026/ai/data/ai-tool-switch), [cost](https://survey.stackoverflow.co/2026/knowledge/data/ai-cost) and [avoidance](https://survey.stackoverflow.co/2026/ai/data/ai-avoid) tables match the quoted figures and their separate denominators: 13,945; 14,304; 13,144; 1,033; 13,857. | Optional questions and the self-selected developer frame remain explicit. Cost is multi-select; the other four questions are single-select. These are published respondent reports, not evidence that any segment buys or repeatedly needs this product. |
| Eurostat enterprise article | The [primary article](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises) matches the recorded adoption, size and barrier figures, sample and population. Its December 2025 extraction and inconsistent 2024-survey/2025-results wording remain visible. | The barrier discussion concerns non-users that considered AI, not all enterprises. No dataset-metadata reconciliation or buyer-role observation is claimed. |
| Census article and national workbook | The [May article](https://www.census.gov/library/stories/2026/05/ai-use-businesses.html) matches the recorded figures and November 2025 question change. A fresh public download of [National.xlsx](https://www.census.gov/hfp/btos/downloads/National.xlsx) was 88,868 bytes, SHA-256 `d905e1b7ad042971e67e8b4b36a50a3050522cb675c609056c7ba374b88c8668`. In `Response Estimates`, cycle `202620`, Q7/Yes is 23.8% (E16) and Q24/Yes is 27.7% (E82). The date sheet records collection 2026-09-21–2026-10-04, prior reference period 2026-09-07–2026-09-20, publication 2026-10-08. | This confirms the existing aggregate readback at the stated cycle. The mutable download and checksum confer no continuing freshness, project purchase intent or permission to redistribute a dataset. No raw workbook is committed. |

The protocol correction keeps Part B on reported past consequences, asks about
recurrence without presuming it, and permits non-use from screening through Parts
B′ and C. Part D's decision-specific prompt is conditional on a real report, and
analysis separates actual consequences, anticipated risks and no reported
consequence. The old counterfactual about a decision going wrong conflicted with
the guide's past-behaviour-first rule; its removal does not count as a participant
finding. The switching interpretation now uses all 13,144 question respondents;
10.6% does not describe only those who switched. Eurostat barrier statements retain
the non-user group that had considered AI. Catalog roles are distinguished without
attributing hardware-fit capability to every listed alternative or claiming
comprehensive coverage of enterprise decision processes.

The source/protocol correction delivered through [#337](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/337)
recorded no new receiving-owner disposition and made no fieldwork, recruitment,
consent, quota, concept-card or monetary decision for #63. Its complete independent
evidence/protocol review is [5563135481](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/337#pullrequestreview-5563135481).
The later receiving assessment below has its own date, role and source identity.

## Actual technical receiving decisions, 2026-10-18

The [actual receiving receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6250471522),
posted at **2026-10-18T13:27:17Z**, records decisions by ChatGPT acting as the
in-session research engineering reviewer under the user's express project
delegation, through the connected CompleteDotTech account. The reviewer authored
the #337 correction; its independent source review is linked above. These are
actual technical input decisions, not responses attributed to the other listed
assignees or a claim to have completed their issues.

The receipt reviews this note at signed main
`aee9b46df93c9e74b9c9d4ae588b203e8421df59`, exact blob
`25112cbe50585cf38892fd2b1bcf8aea58c901e1`, against the five live receiving scopes
and their applicable definitions, proposed interfaces and unresolved decisions.
Its precise receiving-note blob identities remain in that receipt. The two
original tynamite records retain their own `6511dea` scope and authorship.

| Existing technical handoff | Disposition | Accepted use and retained limits |
| --- | --- | --- |
| #52 → #2 Workload | Accepted with constraints | Use segment 1 to ask about existing hardware and actual targets. It supplies no preset workload, measured demand, memory/quality result or automatic T3/T4/T5 activation. Explicit answers, unknowns and selected capabilities remain authoritative. |
| #52 → #3 Deployment | Accepted with constraints | Receive the local-first comparison hypothesis. Determine each serving component's actual operator and capacity separately; infer no mode, billing basis, residency, isolation or fit from a persona. |
| #52 → #16 Retrieval | Accepted with constraints | Receive segment 3 as an integration/rework hypothesis. It selects no backend or vector store and supplies no ACL, context, quality or interoperability result. Preserve optional retrieval, caller/resource authorization, complete assembled-input counting and separate #36/#65 evidence. |
| #52 → #25 Agent framework | Accepted with constraints | Receive segment 3 as an orchestration/integration question. Retain no-framework/direct orchestration and explicit selected paths; catalog presence supplies no tuple compatibility, adoption or measured planning benefit. Security, iteration, evaluation and #40 decisions remain separate. |
| #52 → #39 Cost | Accepted with constraints | Receive segment 6's neutral priorities and user/buyer/approver distinction. Survey responses supply no quantity, rate, currency/region default or willingness-to-pay amount. Actual spend and hypothetical intent stay distinct; unpriced/unsized inputs remain unknown and partial coverage cannot establish a complete budget result. |

The incoming #3 → #52 incentive question remains an untested hypothesis, as in
the [historical co-owner reply](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/3#issuecomment-6245701946).
Contributor incentives and #63's interview incentive are separate decisions.
No incentive or participant contact is authorized by this assessment.

Unresolved decisions remain named: #16's zabyxc01/appletechie own backend,
enforcement and context/evaluation follow-ups; #25's CompleteDotTech/Mattycodes69
retain selected-path/security research and central #40 adoption; #39's
appletechie/PUSHINGSQUARES retain qualified quantities, rate coverage,
currency/region and saved-estimate policy. For #63, zwright8/appletechie retain
the validation work and coordinator CompleteDotTech retains recruitment,
consent, retention, quotas, concept text and incentive decisions. These
information handoffs neither change assignments nor require the complete
receiving work packages to close before the bounded #52 desk deliverable.

## Literal #52 criterion map

The [live issue](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52)
explicitly includes desk personas, current alternatives and an interview protocol,
and excludes running interviews or contacting participants. #63 remains the
separate primary-validation work package; its unperformed fieldwork does not
convert into an additional #52 criterion.

| Literal criterion | Evidence and review | Acceptance boundary |
| --- | --- | --- |
| Map ten requested segments | The ten-row segment map and ten numbered jobs remain intact; complete source review 5563135481 checked them. | Roles and overlaps are desk hypotheses, with no inferred segment population or participant count. |
| Write evidence-qualified jobs to be done | Each job records a trigger, constraint and hypothesized consequence; nearby sources and the opening claim rules distinguish reported survey evidence from analyst assumptions. | No job is represented as an observed customer finding. |
| Define neutral interview questions | Screening permits non-use; the fixed sequence reconstructs events before alternatives/spend and optional concept questions. #337's reviewed correction removes recurrence, bad-outcome and fictional-decision assumptions. | #63's operational decisions remain unfilled; the guide does not authorize recruitment or manufacture task-completion evidence. |
| Distinguish desk personas from validated customers | The status, claim rules, role map and per-segment hypotheses explicitly retain that distinction. | Demand, recurrence and willingness to pay are unestablished. |
| Deliverable links every significant conclusion to evidence or an explicit hypothesis. | The source tables, catalog IDs, original source-register proposals and dated source review supply claim-level qualifications; the independent review read the primary tables and actual Census workbook. | Publisher observations retain dates, populations, question denominators and limitations; this is not independent survey reproduction, continued freshness or a source-use grant. |
| Relevant technical owners review handoffs; unresolved decisions are named. | The five actual delegated technical receiving decisions above supplement the two preserved historical tynamite records; the receipt and ledger identify the role, exact artifact, scope and retained decisions. | No response is attributed to an absent assignee; no consumer's complete technical outcome is accepted by this desk-input receipt. |
| Repository checks pass; reviewer accepts the evidence before Done. | #337's independent source review and exact receiving/signed-main logs passed 21 contract and 659 repository tests plus all four validators. This receipt/ledger reconciliation receives its own independent review, current checks and signed-main identity verification through its publishing PR. | Close #52 only after those amendment delivery gates complete and the live issue/Project readback is reconciled. #63 remains separately gated. |

## Aggregate-parent completion boundary — 2026-10-18

The seven criteria and five technical receiving decisions above establish acceptance of this bounded desk-persona and interview-protocol deliverable. They do not waive the native parent-completion rule. The [issue-specific #52 prompt](../../prompts/market/issue-052.md), [market runbook](../../prompts/market/README.md#recommended-coordination-order), [shared delivery rules](../../prompts/market/SHARED.md#7-mandatory-delivery-loop-implement-validate-commit-push-sync-review-merge) and [market methodology](../../docs/market-research/research-methodology.md#evidence-and-readiness) require child #63's own accepted completion before overall #52 issue/Project completion.

The final criterion-map row's amendment-delivery requirements remain necessary; they are not an exception to that parent gate. Interviews, recruitment and primary demand validation remain solely within #63's scope and original criteria. This clarification adds no interview criterion to the desk deliverable and changes none of its observations, hypotheses, reviewer attribution or accepted technical inputs.

The [dated nine-row Project operation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6255435332) preserves the actual #52 Done write and subsequent policy finding. The [canonical parent-correction decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6255561527) was followed by the [completed correction and independent readback](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6255646287): #52 reopened at 2026-10-18T21:50:45Z, its bounded body correction was read back at 21:51:38Z, and Project2 Status In Progress was confirmed by a fresh read at 21:55 UTC. All seven desk criteria remained checked, while #63 remained open with its own unfinished operational and empirical criteria. The [final #59 audit handoff](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6255646921) preserves the initial operation, omitted parent-policy check and actual correction as separate dated evidence for canonical intake. This source clarification performs no metadata write and supplies no #63 fieldwork or parent-completion waiver.
