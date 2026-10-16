# MR-05: Validate customer demand and willingness to pay

Issue: [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63). Parent: [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52). Owner and approver: @CompleteDotTech (coordinator). Status: **approval package only; validation has not started.** Readiness: Awaiting Decision. Evidence availability score: unknown (not zero).

No one has been contacted, no community has been posted to, no account was created and no personal data was collected. Nothing in this note may be used for outreach until the coordinator records each decision in [Decisions required](#8-decisions-required-from-coordinator-before-any-contact). Every number below marked **proposal** is for the coordinator to approve, change or reject; none is an accepted threshold.

## Question
Do target users repeatedly face multi-component AI configuration decisions, and does an actual buyer value paying to improve them?

## Inputs from #52
[customers.md](customers.md): ten segments with user/buyer/approver hypotheses, jobs to be done, desk evidence, the screener and the interview guide. This note does not repeat the guide; it adds recruitment, consent, data handling, reporting, analysis and willingness to pay.

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

- Participants are referred to only by pseudonymous IDs (P-01, P-02, ...), assigned in interview order.
- Labels are coarse: primary segment from the ten in #52, role code, organization-size band and broad region (for example "EU", "North America"). No job title, employer, client, product name of the participant's employer, city or exact dates.
- No employer or client names, even if the participant says them; replace with "[employer]" or a category.
- Quotes only from participants who ticked the quote box; at most two sentences; remove identifying details; never attribute a quote with more than its P-ID and segment label.
- **Minimum cell size (proposal, D-12): no reported split smaller than 3 participants.** Smaller groups are merged or reported as "fewer than 3".
- Always report the total sample, role mix, channel mix, and how many participants were excluded or withdrew.

## 6. Analysis plan

Coding follows the #52 analysis questions. Each participant is coded for: decision in window (yes/no), previous similar decision (yes/no/unknown), number of component types in the decision, role, current alternatives (with catalog IDs), current spend (money; time; none; unknown), payer, and whether they say existing alternatives were enough.

### What disconfirms demand

Thresholds are named but **not set**; the coordinator sets them before the first interview (D-13), so they cannot be tuned to the results.

| ID | Disconfirming finding | Threshold |
| --- | --- | --- |
| T-1 | Few participants report a decision in the window | Share below `T-1` |
| T-2 | Decisions are one-off: few report a previous similar decision | Share below `T-2` |
| T-3 | Decisions are single-component (one model or one tool), not multi-component | Share above `T-3` |
| T-4 | No current spend of money or tracked time on making these decisions | Share above `T-4` |
| T-5 | Existing alternatives suffice by the participant's own account | Share above `T-5` |
| T-6 | Buyers (Q-2) do not see a problem their users report | Qualitative; coordinator review |

Results are reported by segment and role only where cells meet D-12. Report what the sample cannot show: recruitment bias by channel, missing segments, and the difference between stated intent and behaviour.

## 7. Willingness-to-pay module (proposal)

Status: proposal. Monetization models are owned by [#54](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/54); this module only collects inputs for it.

Sequence (fixed, after Part C of the #52 guide):
1. **Observed behaviour first.** Already asked in Part C: current spend on tools, services, consultants or time; who paid; any past purchase made to support this kind of decision. These are the strongest evidence and are reported separately.
2. **Concept description** (Part D), fixed text approved by the coordinator (D-14).
3. **Open-ended price sensitivity**, no researcher-supplied prices. Proposed: the four Van Westendorp questions with free-text answers (too cheap to trust, a bargain, getting expensive, too expensive to consider), asked for the payer the participant named. If the participant is not the payer, ask who would decide and how, instead of a price.
4. **Purchasing process**: what would need to happen for this to be bought (approval steps, budget line, procurement).

Reporting: stated willingness to pay, observed spend and actual paid transactions are separate categories. With qualitative sample sizes, open-ended price answers are reported as ranges per role, not as a price curve or an optimal price. Not proposed: Gabor-Granger or any method that shows prices, because researcher-supplied prices anchor answers (the issue flagged in #52).

## 8. Decisions required from coordinator before any contact

- [ ] D-01 Approve, change or reject this package as a whole.
- [ ] D-02 Which recruitment channels are allowed (section 1); Reddit stays blocked until its rules are read and recorded.
- [ ] D-03 Recall window N months for screener question 2.
- [ ] D-04 Quotas Q-1 to Q-5 (approve or replace).
- [ ] D-05 Incentive type, amount, currency and whether it is paid on withdrawal.
- [ ] D-06 Controller identity and the contact address in consent and outreach.
- [ ] D-07 Lawful basis (consent, legitimate interests with a documented assessment, or other) and the rights text.
- [ ] D-08 Which participant jurisdictions are in scope (EU, UK, US, other).
- [ ] D-09 Private storage location, encryption, and the named access list.
- [ ] D-10 Retention and deletion deadlines (approve or replace the section 4 proposals).
- [ ] D-11 Whether audio and/or video recording is offered at all.
- [ ] D-12 Minimum reported cell size (proposal: 3).
- [ ] D-13 Values for thresholds T-1 to T-5, set before the first interview.
- [ ] D-14 The neutral concept description text for Part D, or a decision to omit Part D.
- [ ] D-15 Whether the willingness-to-pay module is used, after #54 review.
- [ ] D-16 Who interviews, and how interviewer conflicts of interest are disclosed.
- [ ] D-17 Minimum participant age (consent draft assumes 18+).

## Acceptance status

| Live criterion | Status |
| --- | --- |
| Approve recruitment and consent protocol | Package prepared; approval not given |
| Recruit across distinct buyer roles | Not started; quota proposal only |
| Capture current alternatives and recent decisions | Not started; instrument in #52 guide |
| Test willingness to pay without leading questions | Not started; module proposed |
| Deliverable links every significant conclusion to evidence or an explicit hypothesis | Met for this package: no demand conclusion is drawn |
| Relevant technical owners review handoffs; unresolved decisions are named | Decisions named above; no handoff reviewed |
| Repository checks pass; reviewer accepts the evidence before Done | Checks run on the local working tree; no reviewer acceptance |

## Result
No validation has been completed. No participant data, raw customer data, benchmark artifact or paid API output exists. Consumers once results exist: #52, #58, #2, #3, #39.

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
