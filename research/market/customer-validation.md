# MR-05: Validate customer demand and willingness to pay

Issue: [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63). Parent: [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52). Live issue assignees checked on 2026-10-18: @zwright8 and @appletechie; @CompleteDotTech is the program coordinator. Status: **protocol preparation only; validation has not started.** The original package recorded readiness as Awaiting Decision; this amendment does not certify current Project fields. Evidence availability score: unknown (not zero).

No one has been contacted, no community has been posted to, no account was created and no personal data was collected. Nothing in this note may be used for outreach until the coordinator records each decision in [Decisions required](#8-decisions-required-from-coordinator-before-any-contact). Numbers marked **proposal** retain that status unless the dated [instrument decisions](#instrument-decisions--2026-10-19) explicitly select them. Selected instrument values are design choices, not validated market thresholds, implemented product limits or permission to start fieldwork.

## Question
Do target users repeatedly face multi-component AI configuration decisions, and does an actual buyer value paying to improve them?

## Inputs from #52
[customers.md](customers.md): ten segments with user/buyer/approver hypotheses, jobs to be done, desk evidence, the screener and the interview guide. This note does not repeat the guide; it adds recruitment, consent, data handling, reporting, analysis and willingness to pay.

The 2026-10-18 instrument clarification also consumes the accepted [#54 willingness-to-pay design](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/745e58704262aa7b0c755794f820ec1372b24395/research/market/monetization.md#6-proposed-willingness-to-pay-validation-handoff-to-63), input blob `3baf64e0aca6c9190bc6012fde5cc62e3fe9baf8`. It aligns the questions and interpretation below with that proposal. It is not a new review of the dated channel/privacy sources, an adopted price or a fieldwork result. The actual #54 receiving receipts retain their separate design-only scope.

## 1. Recruitment channels (for approval)

Rules were read on 2026-10-16. Where a page could not be retrieved, the gap is recorded rather than assumed.

| Channel | Relevant rules | Fit and bias | Proposal |
| --- | --- | --- | --- |
| Project-owned opt-in: a sign-up link in this repository or on a Pick-Your-AI page | [GitHub Acceptable Use Policies](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies): bars bulk unsolicited promotion and "sending unsolicited emails to users"; researchers may use only public, non-personal information. So: never email or message people found through GitHub; only people who opt in | Reaches people already interested in the project (positive bias) | Allowed as passive opt-in only |
| Hacker News | [Guidelines](https://news.ycombinator.com/newsguidelines.html): "Please don't use HN primarily for promotion"; posting one's own work is acceptable "part of the time"; no automated posting. Surveys and recruiting are not mentioned | Developer-heavy; self-selected | Coordinator decision; at most one disclosed post |
| Reddit communities (e.g. r/LocalLLaMA) | **Not retrieved**: reddit.com and redditinc.com were unreachable from this environment. Subreddit rules and Reddit's site rules must be read and recorded before use, and moderator permission obtained where rules require it | Strong for segment 1; weak for buyers and approvers | Blocked until rules are read |
| Discord servers (model, runtime or tool communities) | [Discord Community Guidelines](https://discord.com/guidelines): "Do not send unsolicited bulk messages (or spam) to others"; do not share someone's PII without consent. Each server's own rules are separate and not reviewed | Strong for segments 1–4 | Post only in channels whose rules allow it, with moderator approval; no cold DMs |
| LinkedIn | [Professional Community Policies](https://www.linkedin.com/legal/professional-community-policies): no "untargeted, irrelevant, obviously unwanted ... commercial or promotional" messages; no misleading information about yourself or your business. Research recruitment not addressed | Best route to buyers and approvers (segments 5–8, 10) | Coordinator's own disclosed post; no bulk connection or invitation messages |
| Paid research panel (example: User Interviews) | [Researcher Terms](https://www.userinterviews.com/legal/terms-and-conditions) (effective 2025-07-01): customer must provide an incentive to recruited participants and pay it within 10 business days if paying directly; may not contact participants outside the project; must obtain any required informed consent. Requires a paid account (not created) | Reaches enterprise roles; professional-respondent bias | Coordinator decision; requires budget and an account |
| Referrals from the coordinator's or contributors' professional networks | No platform rules; ethical issue is relationship pressure and positive bias | Reaches buyers; high acquaintance bias | Allowed only by introduction, with explicit "no obligation" wording; cap per referrer (proposal: 2) |

### Outreach wording draft (not to be sent before approval)

> **Research participants wanted: how people choose AI tools and infrastructure**
>
> I'm [name], part of the open-source Pick-Your-AI research project ([link]). We are studying how people and teams decide which AI models, tools, hardware or hosting to use, including people who rarely make these decisions. This is research, not a sales call; we will not try to sell you anything during the conversation. Pick-Your-AI is working on a tool in this area, and what we learn may shape it.
>
> The conversation takes about 45 minutes by video or voice. [Incentive sentence, coordinator decision D-05.] Taking part is voluntary, and you can stop at any time. We publish only anonymized summaries.
>
> If you are interested, fill in a short screener: [link]. Questions: [contact, D-06].

The wording avoids describing a problem participants are expected to have, avoids naming the product's benefits and discloses the project's commercial interest.

### Incentive options
Amount and currency are **coordinator decisions (D-05)**; none is proposed here.
- No incentive (lowest cost; skews to enthusiasts).
- Fixed gift card or bank payment, the same for everyone regardless of answers (required on a paid panel).
- Charity donation in the participant's name.
- Not recommended: early or free access to the product, because it rewards positive concept reactions and creates a relationship that biases Part D.

## 2. Screener and quotas (proposal)

The screener is in [customers.md](customers.md#screener). Each participant gets one primary segment, any secondary segments, and a role code from screener question 3 (user, recommender, approver, payer or none).

Proposed quotas (Q-1 to Q-5), all subject to D-04:

| ID | Proposal | Rationale |
| --- | --- | --- |
| Q-1 | At least 2 participants per primary segment (20 minimum) | Covers all ten segments; the draft covered three |
| Q-2 | At least 6 participants who paid for or controlled the budget for an AI tool or service | Buyer evidence cannot come from users only |
| Q-3 | At least 4 participants who approved or rejected a choice without paying | Approver role is distinct (segments 7, 8) |
| Q-4 | At least 4 participants who answer "No" to screener question 2 | Disconfirming cases: no recent decision |
| Q-5 | No more than 30% of participants from any single recruitment channel | Limits channel bias |

These counts are for qualitative coverage. They support no statistical inference, conversion rate or market-size estimate.

## 3. Consent text (draft)

> **Pick-Your-AI customer research: participant information and consent**
>
> **Who is running this.** [Controller identity, D-06]: the Pick-Your-AI research project, contact [address].
>
> **Purpose.** To understand how people and teams choose AI models, tools, hardware and hosting, what they use today, and what that costs. Findings will inform the Pick-Your-AI project, which may build a commercial or free product.
>
> **What we collect.** Your answers to the screener and the interview, your role and organization-size band, and your region. Your name and contact details are used only to schedule and, if applicable, pay the incentive. Please do not share confidential information about your employer or clients.
>
> **Voluntary.** Taking part is your choice. You can skip any question or stop at any time without giving a reason. [If an incentive applies: you receive it even if you stop early, D-05.]
>
> **Recording (optional).** We would like to record audio [and video, D-11] to make accurate notes. You can take part without being recorded. ☐ I agree to audio recording ☐ I do not agree to recording.
>
> **How we use it.** Notes are stored outside the public repository and seen only by [access list, D-09]. Published results use a code (for example P-07), a broad role and segment label, and no names, employer names or details that could identify you. Short quotes may be published without attribution. ☐ You may quote me anonymously ☐ Do not quote me.
>
> **How long we keep it.** Recordings are deleted by [date, D-10]; contact details by [date, D-10]; anonymized notes are kept until [D-10].
>
> **Withdrawal.** You can withdraw by contacting [address] using the same channel you used to join. We will then delete your recording, notes and contact details, except anonymized results already published in aggregate.
>
> **Your rights.** [Jurisdiction-specific text, D-07/D-08.]
>
> ☐ I have read this information and agree to take part. ☐ I am 18 or older.

### Data protection considerations (if EU or UK participants are included)

Which jurisdictions to recruit in, who the controller is, and which lawful basis applies are **coordinator decisions (D-06 to D-08)**. This is not legal advice; these sources should be read by the coordinator, and a privacy professional consulted if needed.

- **Consent as the lawful basis.** [EDPB Guidelines 05/2020 on consent](https://www.edpb.europa.eu/system/files/documents/files/file1/edpb_guidelines_202005_consent_en.pdf) (version 1.1, adopted 2020-05-04): paragraph 64 lists the minimum information for informed consent: controller identity, purpose of each processing operation, type of data, the right to withdraw, automated decision-making where relevant, and risks of transfers without adequacy or safeguards. Paragraphs 113–114: withdrawal must be as easy as giving consent and through the same interface where practicable. Paragraph 46: refusing or withdrawing must not cause detriment, which supports paying the incentive regardless of withdrawal. The draft above covers these elements; international-transfer wording depends on where data are stored (D-09).
- **Other lawful bases for research.** EDPB paragraph 154: for research, GDPR does not limit Article 6 to consent; Article 6(1)(e) or (f) may be available with Article 89(1) safeguards. Research-ethics consent can then be an additional safeguard.
- **Legitimate interests (UK).** [ICO legitimate interests guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/a-guide-to-lawful-basis/legitimate-interests/): purpose, necessity and balancing tests, and the ICO says organizations "should keep a record of" the legitimate interests assessment.
- **Research provisions (UK).** [ICO, "What is research-related processing?"](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/the-research-provisions/what-is-research-related-processing/): scientific research can be carried out in commercial settings, judged by purpose (for example advancing the state of the art, publishing findings). The page does not classify market research as scientific research. Product-oriented demand research should not assume the research exemptions apply. The ICO notes this guidance is under review following the Data (Use and Access) Act.
- **Not reviewed:** rules on unsolicited electronic messages (UK PECR, EU ePrivacy), US state privacy laws and any panel provider's data processing agreement.

Evidence class for all of the above: Primary documentation (regulator guidance). Confidence: High that the cited text says this; whether it applies to this project is a coordinator decision.

## 4. Retention and access

Follows [docs/RESEARCH_WORKFLOW.md "What belongs in Git"](../../docs/RESEARCH_WORKFLOW.md#what-belongs-in-git): recordings, private documents and personal data stay outside this public repository.

| Item | Where | Access | Retention (proposal, D-10) |
| --- | --- | --- | --- |
| Contact details, consent records, incentive records | Private store chosen by coordinator (D-09); never Git | [Access list placeholder: coordinator plus named interviewers, D-09] | Contact details deleted within 30 days after the last interview or incentive payment; consent records kept as long as the notes they cover |
| Recordings | Same private store, encrypted at rest | Interviewers only | Deleted within 30 days of the interview, after notes are checked |
| Pseudonymized notes and key mapping P-ID to person | Private store; mapping file kept separately from notes | Mapping: coordinator only | Mapping deleted when #63 closes; notes kept until #63 closes plus 12 months |
| Anonymized summary | `research/market/customer-validation.md` (Git) | Public | Permanent |

If supporting artifacts need to be referenced from Git, add one sanitized manifest per artifact under `evidence/` using the existing [evidence manifest schema](../../schemas/evidence-manifest.schema.json): a stable `https`, `s3` or `gs` locator without credentials or query strings, an access-requirements statement and no personal content in any field. The manifest describes the artifact; it does not make it public or grant reuse rights.

## 5. Anonymized reporting rules

P-IDs and coarse labels are a pseudonymization scheme, not proof that a record or quote is anonymous. Before public release, assess the combination of role, segment, channel, region and distinctive account or quotation; withhold identifying combinations. The proposed minimum cell size below is one disclosure control, not an anonymity guarantee. The two-per-segment recruitment proposal cannot by itself support a three-person public segment breakdown.

- Participants are referred to only by pseudonymous IDs (P-01, P-02, ...), assigned in interview order.
- Labels are coarse: primary segment from the ten in #52, role code, organization-size band and broad region (for example "EU", "North America"). No job title, employer, client, product name of the participant's employer, city or exact dates.
- No employer or client names, even if the participant says them; replace with "[employer]" or a category.
- Quotes only from participants who ticked the quote box; at most two sentences; remove identifying details; never attribute a quote with more than its P-ID and segment label.
- **Minimum cell size (proposal, D-12): no reported split smaller than 3 participants.** Smaller groups are merged or reported as "fewer than 3".
- Always report the total sample, role mix, channel mix, and how many participants were excluded or withdrew.

## 6. Analysis plan

Coding follows the #52 analysis questions. Each participant is coded for: decision in the declared window (yes/no/unknown), previous similar decision (yes/no/unknown), known component types in that decision, role, current alternatives, reported past spend (money; time; none; unknown), actual payer/approver and whether they say existing alternatives were enough. Attach a catalog ID only when a recorded alternative actually matches the item/version in an identified catalog snapshot; retain an unmatched description or unknown instead of inventing an identity. A marketing name alone does not establish an immutable model or serving revision.

Keep the participant, the described decision and the purchasing unit separate. Several people may describe the same buying decision; their role accounts remain useful but cannot be counted as independent buyer decisions. Preserve no-decision cases. Record each module's eligible/exposed count, valid responses, skips, unknowns, exclusions and withdrawals, with the applicable window and concept version. Missing or untracked time is not zero effort, and missing spend is not a zero budget. Use the approved disclosure rules when publishing these counts.

### Descriptive signals for revising this pilot

Thresholds are named but **not set**. D-13 must fix each descriptive threshold, minimum valid response count and denominator before the first interview, including how the no-decision and incomplete-response cases are handled. These are pilot-triage choices, not validated market cutoffs. The purposive quota sample cannot establish population demand, reach, recurring-use prevalence, paid conversion or market rejection. Paid-concept flags must also keep #54's separate eligible-buyer/comprehension denominators and proposed minimum-response rule.

| ID | Possible pilot signal | Denominator and interpretation boundary | Threshold |
| --- | --- | --- | --- |
| T-1 | Few participants report a decision in the window | Participants with a valid window/decision response, including valid no-decision answers; unknown recall remains separate | Share below `T-1` |
| T-2 | Few report an earlier similar decision | Respondents with a recent decision and a valid answer about an earlier similar decision; this does not measure future recurrence | Share below `T-2` |
| T-3 | Decisions involve only one known component type | Distinct described decisions with enough component detail to classify them; unknown components are not silently counted as absent | Share above `T-3` |
| T-4 | Participants report neither monetary spend nor time spent on the decision | Distinct decisions with valid money and time answers; untracked or unknown time/spend is excluded from this numerator and reported separately | Share above `T-4` |
| T-5 | Existing alternatives suffice by the participant's account | Distinct decisions with known alternatives and a valid sufficiency response; retain reuse of existing hardware and a decision to buy nothing | Share above `T-5` |
| T-6 | A buyer and user describe different needs | Role accounts linked to the same actual decision where available; unrelated user and buyer answers do not establish within-team disagreement | Qualitative review |

Results are reported by segment and role only where cells meet D-12 and the disclosure review. Report channel bias, missing segments and incomplete modules. A failed or misunderstood prototype task calls for instrument/prototype revision; it does not by itself reject the underlying value proposition. Without an actual fixed baseline/prototype task, success criteria and order plan, collect concept reactions only and report no task-performance improvement. Stated intent, reported past behaviour, directly observed tasks and actual transactions remain separate evidence classes.

## 7. Willingness-to-pay module (proposal)

Status: proposal. Monetization models are owned by [#54](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/54); this module only collects inputs for it.

**Offer prerequisite.** Reuse #54's proposed paid concept: one private team workspace with shared versioned builds, evidence/source-revision links, comparison history and review comments, evaluated by the actual buying team or organization. Its proposed question unit is **USD per workspace per month**, with the existing team's size stated. These are hypothetical benefits, not an available product or a new frozen billing unit. The card excludes inference execution, model-provider credits, third-party dataset redistribution rights, consulting and an SLA. Before any price question, D-14 must freeze the exact member/build limits, history retention, included support, rights-qualified content and worked use case, together with that benefit bundle, buyer unit, currency and period. If the card is incomplete or not understood, omit the price module. A separately specified local-currency card is a separate analysis cell, with no invented FX conversion or pooling.

Sequence (fixed, after Part C of the #52 guide):

1. **Reported past behaviour first.** Reconstruct current and past spending on tools, services, consultants and decision time, who paid and how the participant knows. An interview answer is a self-report, not an independently observed purchase. Any separately supported observation keeps its own consent, provenance and scope; do not request private employer records for this public research. Keep no-spend and unknown responses distinct.
2. **Concept and comprehension.** Use the fixed, versioned D-14 card after the past-behaviour questions. Ask the participant to explain the benefits, exclusions, buyer unit and commercial relationship. If both paid and referral-funded free concepts are shown, predeclare their counterbalanced order. They offer different benefit bundles, so their answers are not a controlled comparison of price alone.
3. **Paid price perception.** Only an eligible payer who understands the complete paid card receives the four exploratory free-response prompts: too cheap to trust, a bargain, expensive but still considered, and too expensive to consider, in the card's fixed unit. Do not show competitor prices or researcher-supplied amounts. A participant who does not control the purchase describes who decides and how, without supplying a proxy payer amount. Record unknown, skipped and inconsistent answers rather than imputing zero.
4. **Free-concept and purchasing process.** For the separately disclosed referral-funded free concept, ask about disclosure comprehension, trust and workflow choice; do not ask a free offer for a "too expensive" price point. For a paid offer, ask about approval steps, budget, procurement, reachable purchase channels and reasons for choosing no purchase. A non-binding request for a pilot, if separately included in the operational protocol, is interest rather than a sale or demonstrated retention.

Reporting: keep stated price perceptions, reported past spend, directly observed task outcomes and actual paid transactions separate. Report exposed/eligible/valid counts, skips, unknowns and withdrawals for each module, deduplicating the actual buying decision. Compare ranges only within the same complete benefit/card version, buyer unit, currency and billing period; do not pool role or unit mismatches into a price curve or an optimal price. These amounts are not supplier rates or Pricebook inputs.

The four prompts retain #54's explicit method limit: the original Van Westendorp and Newton–Miller–Smith papers remain unread, so this is not a validated PSM instrument or a purchase/revenue estimate. The present exploratory design chooses open questions; it does not establish that every method showing a price is invalid. Adopting a different pricing experiment requires its own declared offer, sequence, sampling and interpretation. The proposed free and paid models can each remain unqualified; failed task comprehension is separate from demand, and reduced trust after commission disclosure can support neutrality concerns rather than refute their value.

## Instrument decisions — 2026-10-19

The coordinating ChatGPT engineer selects the six decisions below under the user's delegated project authority, for independent review and ordinary research delivery. These are present **instrument-design decisions**; no answer is attributed to an absent assignee. They consume the accepted [#54 design, sections 6–7](monetization.md#6-proposed-willingness-to-pay-validation-handoff-to-63) and preserve the actual [#63 technical intake](#actual-prospective-technical-intake--2026-10-18). The original source-check dates and historical receipt remain unchanged.

**Fieldwork is still not approved.** D-01, D-02, D-04–D-10, D-13 and D-16 remain unresolved. In particular, these choices supply no real controller/contact, lawful basis, eligible jurisdiction, private store/access list, channel permission, retention execution, incentive or interviewer. All four operational/empirical issue criteria remain unchecked. Complete the remaining decisions and their actual review before applying this instrument to a participant; no public recruitment form, mailing or contact is created here.

| Decision | Selected design value | Reason and limit |
| --- | --- | --- |
| D-03: recall window | Use **six calendar months before the interview** for the existing screener's N-month placeholder. Keep Yes, No and Not sure. Preserve uncertainty when a person cannot place a decision in that window; do not replace missing recall with no decision. | Fixes a common elicitation window while retaining recent and no-decision accounts. Six months is this design choice, not an empirically validated recall interval or a recurrence estimate. Record the actual private interview/window dates only after the operational package is approved. |
| D-11: recordings | **Written notes only.** Researchers create no audio/video recording, automated transcript, screenshot or screen recording. Before any session, verify that the selected platform's recording/transcription features are disabled; if that cannot be established, do not start that session. | Reduces the material collected; it does not certify that an unselected platform has no processing, metadata or retention. The real platform, private note store, access and deletion controls still require D-09/D-10 review. Live voice/video transport is not classified as absent personal-data processing. |
| D-12: disclosure | **No public participant-level rows, P-ID-linked accounts or quotations in this pilot.** Public output is aggregate-only after disclosure review, with a minimum of **three distinct participants per reported cell**. Suppress or combine smaller cells and related totals where they would reveal the suppressed cell. | Adopts the existing three-person proposal as one disclosure floor, not an anonymity guarantee. Review combinations across tables and prior releases. The separate #54 minimum of three valid independent buyer decisions for a directional pilot judgment also remains; three people describing one purchase do not supply three decisions. |
| D-14: concept cards | Freeze the two hypothetical cards below as **MR63-P1-2026-10-19** and **MR63-F1-2026-10-19**. Change the card identifier and analysis cell if its benefit, limits, buyer, currency, period or worked scenario changes. | Resolves the incomplete-card gate for this defined instrument. No feature, plan, commercial licence, service availability, supplier price or production billing unit is adopted. These are fictional offers for future concept questions, not saleable products. |
| D-15: modules | Use both cards for concept/comprehension questions. Use the four open paid-price prompts **only** for an actual eligible payer who understands the complete P1 card and can answer in its stated USD/workspace/month unit. Ask F1 only disclosure/trust/workflow questions. | Retains the accepted #54 sequence and design limits. Record ineligible, misunderstood, skipped and unknown cases separately; provide no proxy payer amount, currency conversion, competitor price anchor or free-offer price point. No validated PSM, purchase or revenue estimate follows. |
| D-17: age | Include **adults who self-attest that they are at least 18**; do not collect identity documents for this check. A missing or negative attestation is ineligible for this instrument. | Selects a research inclusion rule. This is not a jurisdiction-specific legal capacity determination; D-07/D-08 must still resolve the actual participant/legal scope. |

### Frozen hypothetical concept cards

Read the hypothetical status and the entire applicable card before its comprehension questions. Do not substitute the current app, a live plan or an incomplete feature list. Every count or duration in these cards is a **design choice**, not a measured need, implementation capability, cost estimate or validated demand threshold.

| Card field | P1: hypothetical private team workspace | F1: hypothetical referral-funded free core |
| --- | --- | --- |
| Status and purpose | An imagined future paid collaboration offer; nothing is being sold or provisioned. | An imagined future free comparison offer; nothing is being provisioned or referred for payment in this research. |
| Benefits | One private workspace for shared versioned builds, evidence/source-revision links, side-by-side comparison history and review comments. | The neutral comparison core, evidence/source-revision links and ranking explanations. Paid collaboration features in P1 are excluded. |
| Member and build scope | Up to **five named members** in the one workspace and **100 current saved build records**. Compare **two saved builds at a time**. | A single person's comparison of **two hypothetical build options** in the worked scenario. No team membership, private team workspace, shared review comments or retained collaboration history is included. |
| History and support | **90 calendar days of comparison/change history** for the current saved records. Included support is public self-service documentation only; no dedicated human support, response-time promise, consulting or SLA. | No retained team history. Included support is public self-service documentation only; no dedicated human support, response-time promise, consulting or SLA. |
| Content and rights boundary | The team's own entered selections/comments plus eligible public catalog metadata and source/evidence links, subject to actual material/use rights review. No copied third-party datasets, weights, restricted evidence, private source attachments or implied training/redistribution permission. | Eligible public catalog metadata and source/evidence links, subject to the same actual material/use review. No third-party dataset/weight redistribution or private source attachments. Public reachability is not permission. |
| Buyer and question unit | The participant's actual buying team/organization. Price questions use **USD per workspace per month** for the stated existing team size. No amount is shown or charged, and answers from another currency/unit are not converted or pooled. | No user charge. Disclosed paid referral links and separately labelled sponsor slots are optional; a commission-free presentation remains available without charge. Payment never changes organic ordering or eligibility. No price-perception questions apply. |
| Exclusions | No inference execution, model-provider credits, third-party data redistribution rights, custom services, availability/security certification or operational-readiness guarantee. | The same inference, credit, rights, custom-service and readiness exclusions; no P1 collaboration bundle. No actual partner agreement or commission revenue is assumed. |
| Worked use case | An invented four-person team records three options for one configuration decision, compares two at a time, follows the source-revision links, and comments on why it would retain or reject an option. It can revisit that comparison within the card's stated history. No actual team, catalog eligibility, recommendation quality or saving is observed. | An invented individual compares two options for one configuration decision and explains the evidence/ordering and any paid relationship. They can choose the commission-free presentation or an existing alternative. No actual purchaser, recommendation quality or referral conversion is observed. |

The finite member/build/history choices make P1's offer evaluable at one declared scope; they are not a conclusion about the right commercial limits or the cost of operating it. F1 retains #54's free neutrality controls and separate paid-placement disclosure. Different benefits mean P1/F1 answers cannot isolate a price effect, and neither card creates an authorized source-use entitlement.

### Application to the existing draft instrument

Use the six-month placeholder in the unchanged #52 screener. Retain its no-recent-decision branch, roles and unknown answers. After actual consent, a note-taker may read back a paraphrase to check understanding, but must not request employer records or make a recording. Internal P-IDs may still link approved private notes; the public aggregate-only rule prevents releasing those rows or linking their quotations. No quote-consent box is used for this pilot.

The selected written-notes-only and aggregate-only rules take precedence over the older recording, public P-ID and quotation proposals in sections 4–5. Where section 5 asks to always report sample, role, channel, exclusion or withdrawal counts, preserve exact counts in the approved private analysis but withhold unsafe public counts and any related totals, percentages or summaries that would reveal them. Mark a withheld count as withheld, not zero or an exact small-cell range. Apply the same review across tables and prior releases; the three-person floor alone does not establish anonymity.

The consent and outreach blocks above remain **unapproved historical drafts**. For an eventual reviewed participant-facing version, replace their optional-recording and anonymous-quotation passages with the written-notes-only and aggregate-only scope, and remove the audio/video and quotation boxes. Do not send either draft with placeholders or conflicting recording/reporting language. This decision does not certify the remaining consent, controller, jurisdiction, withdrawal or platform terms.

Preserve past behaviour/spend and actual purchasing authority questions **before** either card. Before fieldwork, freeze a P1-then-F1 / F1-then-P1 alternating sequence by planned interview slot; retain each planned and actually exposed order, including missed or withdrawn slots, without silently resequencing completed interviews. This is counterbalancing for the instrument, not random sampling or proof that order effects are absent. Keep the same card version in each analysis cell.

Ask the participant to explain each card's benefits, exclusions, unit and commercial relationship before proceeding. The price module is omitted for a nonpayer, incomplete comprehension or inability to evaluate the specified unit; record the reason without assigning a price of zero. Do not invent a local-currency card, inference, payment, purchase, return, task-performance improvement or willingness-to-pay finding. Until there is a separately approved fixed task/prototype instrument, this phase collects concept reactions only; the baseline/prototype task row remains untested.

D-04's recruitment quotas and D-13's pilot flags/minimum valid denominators still need explicit decisions before the first interview. The selected reporting floor does not make the two-per-segment proposal reportable, validate any market threshold or resolve the required independent-decision count. Recruitment/consent approval, actual participants, current-alternative accounts and paid-price execution remain absent.

## 8. Decisions required from coordinator before any contact

Project engineering decisions can be recorded under the user's delegated authority; no reply from an absent assignee is created or required merely to review this instrument. The operational package still needs actual controller/contact details, storage/access arrangements, applicable channel/participant permissions and a recorded recruitment/consent decision. A technical receiving review cannot invent those facts or a participant's consent. The checked rows below are selected only at the scope of the dated instrument decisions above. Every unchecked row still needs its real value and scope; partial design selection does not approve the package.

- [ ] D-01 Approve, change or reject this package as a whole.
- [ ] D-02 Which recruitment channels are allowed (section 1); Reddit stays blocked until its rules are read and recorded.
- [x] D-03 Recall window N months for screener question 2.
- [ ] D-04 Quotas Q-1 to Q-5 and the participant/decision/buyer denominators (approve or replace).
- [ ] D-05 Incentive type, amount, currency and whether it is paid on withdrawal.
- [ ] D-06 Controller identity and the contact address in consent and outreach.
- [ ] D-07 Lawful basis (consent, legitimate interests with a documented assessment, or other) and the rights text.
- [ ] D-08 Which participant jurisdictions are in scope (EU, UK, US, other).
- [ ] D-09 Private storage location, encryption, and the named access list.
- [ ] D-10 Retention and deletion deadlines (approve or replace the section 4 proposals).
- [x] D-11 Whether audio and/or video recording is offered at all.
- [x] D-12 Minimum reported cell size (proposal: 3) and review of identifying combinations/quotes.
- [ ] D-13 Values, denominators and minimum valid response counts for pilot flags T-1 to T-5, set before the first interview.
- [x] D-14 The complete versioned benefit/buyer/currency/period card for Part D, or a decision to omit Part D; incomplete cards receive no price questions.
- [x] D-15 Whether the paid-payer price module and distinct free-concept questions are used, under the accepted #54 design limits.
- [ ] D-16 Who interviews, and how interviewer conflicts of interest are disclosed.
- [x] D-17 Minimum participant age (consent draft assumes 18+).

## Acceptance status

| Live criterion | Status |
| --- | --- |
| Approve recruitment and consent protocol | Package prepared; approval not given |
| Recruit across distinct buyer roles | Not started; quota proposal only |
| Capture current alternatives and recent decisions | Not started; instrument in #52 guide |
| Test willingness to pay without leading questions | Not started; module proposed |
| Deliverable links every significant conclusion to evidence or an explicit hypothesis | Met for this package: no demand conclusion is drawn |
| Relevant technical owners review handoffs; unresolved decisions are named | Actual prospective #2/#3/#39 intakes accepted with narrowing in the dated receipt below; six bounded instrument decisions are selected above, and every remaining operational value/permission is unresolved |
| Repository checks pass; reviewer accepts the evidence before Done | Technical instrument review accepted at prepared `1a1324d`; final amendment checks and canonical delivery remain required, with no fieldwork acceptance |

## Result
No customer fieldwork validation has been completed. The prospective technical design has the scoped receiving review below; no participant data, raw customer data, benchmark artifact or paid API output exists. Actual future results retain separate intake requirements for #52, #58, #2, #3 and #39.

## Actual prospective technical intake — 2026-10-18

The coordinating in-session engineer's [actual receipt 6253426889](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63#issuecomment-6253426889), created **18:17:50Z**, reviewed prepared local `1a1324d064139efecb4830fe5e2b793efec81d3b`, tree `139a0db010896b67f121208a2a68a41cc5489d59`, customer-protocol blob `4ca91862a532c0d662ab12ecf4203deef267343f`, on accepted parent `745e58704262aa7b0c755794f820ec1372b24395`. It also read accepted #54 sections 6–7 and their receiving limits at monetization blob `3baf64e0aca6c9190bc6012fde5cc62e3fe9baf8`, the complete revised T-1–T-6/price instrument and relevant workload, deployment and cost dictionaries. This is actual delegated engineering review, posted through CompleteDotTech, with no response attributed to an absent assignee. It is not a new privacy-law, vendor-price or primary-source audit.

| Consumer | Actual disposition | Retained boundary |
| --- | --- | --- |
| #2 Workload / Use Case | Accept with narrowing the prospective task/constraint/alternative/component/effort interview and coding design | Keep no-decision/unknown and unmatched alternatives; attach item/version/snapshot identity only after a real match. No segment or preference produces a typed workload, default, serving pin, measured performance or numerical quantity. |
| #3 Deployment Mode | Accept with narrowing prospective local/API/hosting decision context | Actual per-component runtime operator/capacity and applicable dataflows/isolation are still needed. Brand, protocol, payment, hardware ownership, training channel or preference alone establishes neither serving mode nor privacy/air gap. |
| #39 Cost Estimate | Accept with narrowing the separation of self-reported spending/time, stated price perception, observed tasks and actual purchases | Deduplicate buying decisions, apply #54's complete paid card and comprehension/eligible-payer conditions, and keep the free offer's questions distinct. No supplier rate, Pricebook, realized revenue, full cost/TCO, population willingness to pay or FX policy follows. |

The accepted scope is this **prospective technical design**. Pilot flags retain valid denominators, unknown/skipped/excluded/withdrawn counts and purposive-sample limits. Misunderstood tasks require instrument revision; without a fixed task/baseline/order there is no task-performance result. Original pricing-method papers remain unread. Pseudonyms and coarse cells do not prove anonymity.

The receipt supplies no real controller/contact details, private storage/access arrangement, channel permission or participant consent, and selects none of D-01–D-17's operational values. Engineering choices can be made under the existing delegation; actual permissions, identities and consent cannot be invented. Recruitment, current-alternative capture, task trials, transactions and willingness-to-pay execution remain absent, so the four operational/empirical criteria and #63 stay open. Publication checks and Project-field QA retain separate evidence. The three actual receipts are appended to the existing handoff rows without rewriting earlier records.

## Proposed source-register additions

Not applied to `sources.json` (owned by #48). Proposed entries, all accessed 2026-10-16:

| Proposed ID | URL | Publisher | Evidence class | Limitation |
| --- | --- | --- | --- | --- |
| `src-github-aup` | https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies | GitHub | Primary documentation (platform policy) | Policy may change; no research-recruitment clause |
| `src-hn-guidelines` | https://news.ycombinator.com/newsguidelines.html | Y Combinator | Primary documentation (community rules) | Silent on surveys and recruiting |
| `src-discord-guidelines` | https://discord.com/guidelines | Discord | Primary documentation (platform policy) | Per-server rules not covered |
| `src-linkedin-community-policies` | https://www.linkedin.com/legal/professional-community-policies | LinkedIn | Primary documentation (platform policy) | Research recruitment not addressed |
| `src-userinterviews-terms` | https://www.userinterviews.com/legal/terms-and-conditions | User Interviews (UserTesting) | Primary documentation (terms) | Effective 2025-07-01; DPA not reviewed |
| `src-edpb-consent-05-2020` | https://www.edpb.europa.eu/system/files/documents/files/file1/edpb_guidelines_202005_consent_en.pdf | European Data Protection Board | Primary documentation (regulator guidance) | EU GDPR; not legal advice |
| `src-ico-legitimate-interests` | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/a-guide-to-lawful-basis/legitimate-interests/ | Information Commissioner's Office | Primary documentation (regulator guidance) | UK GDPR |
| `src-ico-research-processing` | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/the-research-provisions/what-is-research-related-processing/ | Information Commissioner's Office | Primary documentation (regulator guidance) | Under review after the Data (Use and Access) Act |
| (access failure) | https://www.reddit.com/r/LocalLLaMA/about/rules ; https://redditinc.com/policies/reddit-rules | Reddit | Not retrieved | Unreachable from the research environment on 2026-10-16 |
