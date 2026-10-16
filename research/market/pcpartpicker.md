# PCPartPicker experience transfer

Status: partial evidence; public and authenticated workflows both unobserved by this contributor. Accessed 2026-10-16. Refs #51.

## Earlier access attempt (preserved)

The [requested list URL](https://pcpartpicker.com/list/) returned HTTP 403 in web retrieval. A browser visit redirected to `/accounts/login/?next=/list/`. No account was created, credentials used, access control bypassed or saved build changed. Current filtering, compatibility warnings, price aggregation and sharing behavior could not be directly verified in that session.

## No-login walkthrough attempt, 2026-10-16

### Access check

Before fetching any product page, `https://pcpartpicker.com/robots.txt` was retrieved once (HTTP 200, accessed 2026-10-16, evidence class: observed behavior, publisher PCPartPicker / Cloudflare-managed block). It contains:

- An "AI Agents" group that disallows `/` for `Claude-User`, `ChatGPT-User`, `Perplexity-User`, `Google-Agent`, `MistralAI-User` and other user-initiated AI fetchers. `ClaudeBot`, `Claude-Web` and `anthropic-ai` are also disallowed from `/`.
- A general `User-agent: *` group that disallows `/accounts/`, `/api/`, `/list/markup/`, `/list/*/add_to_cart/`, `/mr/`, `/search/` and `/user/`, sets `Crawl-delay: 60`, and declares `Content-Signal: search=yes, ai-train=no, ai-input=no`.

This walkthrough was run by an AI agent (Claude) acting on a contributor's behalf, which is exactly the `Claude-User` case. Sending a browser User-Agent to get around that group would bypass the site's stated access policy, and `ai-input=no` reserves content against real-time input into AI models. **No PCPartPicker page other than robots.txt was fetched.** The home page, `/products/cpu/`, a product detail page, `/builds/`, a Completed Build, a shared list permalink, `/guide/` and `/trends/` all stay unobserved. Total requests to pcpartpicker.com: 1. No raw HTML was kept in Git.

### Step log

| # | URL | Access date | Access mode | Starting state | Action | Visible result | Observed pattern |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S0 | https://pcpartpicker.com/list/ | 2026-10-16 (earlier session, preserved) | Public, no login | No session | Open list builder | Web retrieval HTTP 403; browser redirect to `/accounts/login/?next=/list/` | In this one session, `/list/` redirected to login. This does not show what the list builder requires in general, or whether creating or editing a list needs an account |
| S1 | https://pcpartpicker.com/robots.txt | 2026-10-16 | Public, no login | No session | Read crawl policy | HTTP 200; AI-agent fetchers disallowed from `/`; `ai-input=no` | The site excludes AI-agent retrieval of all pages |
| S2–S9 | Home, `/products/cpu/`, product detail, `/builds/`, Completed Build, shared list, `/guide/`, `/trends/` | Not attempted | n/a | n/a | Not fetched, per S1 | None | Unobserved |

### Secondary report (not an observation by this walkthrough)

Unmerged PR #81 (`research/T0-configuration/workload-use-case.md`, D44) cites https://pcpartpicker.com/builds/ "as shown at access" and describes Completed Builds pages as showing user builds with images, a priced part list, votes and comments. tynamite's PR #67 review relies on D44 for the point that Completed Builds were publicly viewable. Evidence class: secondary description by another contributor, not observed behavior here. Neither source records compatibility notes on Completed Build pages.

## Hypothesis status

The five hypotheses below are original AI UX ideas based on the user-provided product vision, not observations of PCPartPicker's current interface.

| # | Hypothesis | Status 2026-10-16 | Evidence |
| --- | --- | --- | --- |
| H1 | Show a component-by-component decision record with optional tiers | Still hypothesis | No page observed (S1). D44 mentions a part list on Completed Builds, secondary only |
| H2 | Explain a constraint conflict using the two affected selections and the dated rule | Still hypothesis | No compatibility warning observed (S0, S1) |
| H3 | Separate a hard incompatibility from unmeasured performance or missing evidence | Still hypothesis | Not observed (S1) |
| H4 | Preserve a versioned configuration link and show source changes on revisit | Still hypothesis | Shared lists unobserved; list builder reached only a login redirect in one session (S0) |
| H5 | Compare total-cost assumptions beside component prices | Still hypothesis | No price display observed (S1). D44 mentions a priced part list, secondary only |

None was observed or partially observed. Owner mapping (tynamite, PR #67 review): H2 and H3 match #40's explanation and outcome/severity model; H4 is #42's re-validation on revisit.

## Inaccessible steps

| Step | Status | Evidence |
| --- | --- | --- |
| Public browsing (category filters, product detail and multi-retailer prices, Completed Builds, guides, trends) | Not observed by an AI agent | robots.txt disallows `Claude-User` from `/` (S1) |
| Create or edit a list | Not observed; whether it needs an account is not established | One `/list/` visit in the earlier session redirected to `/accounts/login/?next=/list/` (S0). That is a single redirect, not evidence about list creation or editing |
| Save a list | Not observed; whether it needs an account is not established | Depends on the list builder, which is itself unobserved beyond S0; `/accounts/` and `/user/` disallowed for all agents (S1) |
| Share a list | Not observed | Share flow depends on a saved list (S0). `/list/markup/` is disallowed (S1); what it does is not verified |
| Run compatibility check on own list | Not observed | Depends on the list builder (S0) |
| Add list to retailer cart | Not observed | `/list/*/add_to_cart/` disallowed (S1) |

## Proposed AI-builder requirements (not observed behavior)

These are proposed requirements in original wording. None was observed on PCPartPicker. Each one goes to its technical owner for review.

1. **Separate the check result from its consequence (#40).** For each rule, record whether it passed, failed, could not be decided (`unknown`) or was not run (`skipped`), and separately how much it matters (`info`, `warning`, `error`). Apply the #40/#41 owner's interim conflict order (PR #75 review; an owner position, not an approved contract change) before leaving a result `unknown`. `unknown` is then reserved for genuine gaps: no eligible evidence (for example, no benchmark exists for the selection) or equally ranked sources that make opposite claims. A documented hard conflict, such as a model exceeding available memory at its declared precision, is `fail`/`error`. Absence of permission is not uncertainty: when no licence or terms grant is found for an intended use, display and redistribution resolve to `no` (PR #67 review, #41 owner), not `unknown`. Keep that separate from genuine rights uncertainty, such as terms the researcher could not read or contradictory sources of equal rank, which stays `unclear` with the reason recorded. Source: H2, H3.
2. **Explain each non-pass result.** Name the two selections involved, the rule and its version, and the evidence and access date it relies on. Source: H2.
3. **Treat optional tiers as explicitly skipped.** If a user leaves out a tier (for example, no vector store), the dependent rules are recorded as `skipped` with a reason instead of being omitted. Source: H1.
4. **Re-validate saved and shared builds on revisit (#42).** A saved build pins the catalog, rule and pricebook versions it was evaluated with. On reopening it, re-run the rules against the current versions and show which outcomes, severities or prices changed and why. Source: H4.
5. **Show conditional costs, not just component prices (#39).** Show per-component prices next to the usage assumptions behind them (tokens, hours, region), and mark unsupported cost meters as gaps. Source: H5.

## Limits of the analogy

Physical PC compatibility is mostly static fit. AI combinations depend on model and runtime versions, quantization, context length, concurrency and evidence quality. Eligible versioned documentation can support a passing result labelled unverified; genuine evidence gaps remain `unknown` after applying the conflict order. A passing check must be re-evaluated when its relevant version changes. A warnings UI cannot stand in for #40's rule semantics, and no universal compatibility claim follows from this note.

## Limitations

- Single access date (2026-10-16). No login. No PCPartPicker page content was observed, so region, currency, retailer coverage and price freshness are unknown.
- The site's robots policy excludes AI-agent retrieval. Completing the public walkthrough needs either a human contributor browsing normally (a person using a browser is not the `Claude-User` agent) or a coordinator decision to drop the observation from scope. Any account-based walkthrough (if the list builder turns out to need an account, which one login redirect does not establish) still needs coordinator authorization (issue #51 "Needs input").
- `ai-input=no` also limits how any human-collected observations may be used: keep them as short factual descriptions, never PCPartPicker content fed into AI models.

## Next action

The coordinator (CompleteDotTech) chooses one of three options: (a) assign a human for the public walkthrough, using the S2–S9 step list and the step-log columns above; (b) authorize an account-based walkthrough for the list steps, if a human contributor finds they need an account; or (c) explicitly accept the narrower scope. Until then, this note is partial evidence (`Refs #51`). The findings feed #2, #3, #40, #42 and #58. This access gap does not block independent AI product research.

## Proposed source-register additions

The shared registers were not edited. Proposed for the #48 source-register owner:

| Suggested id | Publisher | URL | Access date | Evidence class |
| --- | --- | --- | --- | --- |
| `pcpartpicker-robots` | PCPartPicker (Cloudflare-managed block) | https://pcpartpicker.com/robots.txt | 2026-10-16 | Observed behavior (access policy) |
| `pcpartpicker-list-login` (if not already registered) | PCPartPicker | https://pcpartpicker.com/list/ | 2026-10-16 | Observed behavior (login redirect) |
| `pcpartpicker-completed-builds` (via PR #81 D44) | PCPartPicker | https://pcpartpicker.com/builds/ | Per PR #81 | Secondary description; not observed here |
