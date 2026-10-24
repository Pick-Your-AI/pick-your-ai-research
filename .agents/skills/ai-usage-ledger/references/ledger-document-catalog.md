# Ledger Document Catalog

Each template is a drafting pattern rendered by `scripts/render_ledger_doc.py`. Every placeholder that describes the ledger is filled automatically from `compiled/summary.json` and `compiled/analysis.json` (the output of `ledger.py run` or `run_pipeline.py`); the remaining placeholders (recipient, reference, notes, corrections) come from `--var key=value`. Figures are API-equivalents at list price and are labelled as such; none of these documents is an invoice. Verify every number against the study package before sending anything outside the organisation.

## Common Placeholders

Filled from the ledger:

- `{brand_name}`, `{brand_eyebrow}`, `{brand_contact}` - from the saved branding.
- `{date}`, `{snapshot_date}`, `{period}`, `{period_start}`, `{period_end}`, `{months_count}` - snapshot and covered period.
- `{hosts}`, `{hosts_count}`, `{tools}`, `{tools_count}` - what was scanned.
- `{total_calls}`, `{total_sessions}`, `{total_tokens}`, `{input_uncached}`, `{cache_read}`, `{cache_write}`, `{output_tokens}`, `{reasoning_tokens}`, `{cache_read_share_pct}` - volume.
- `{api_equivalent_usd}`, `{cost_if_uncached_usd}`, `{cache_savings_usd}`, `{cache_savings_pct}` - list-price valuation.
- `{subscription_usd}`, `{subscription_accounts_count}`, `{subscription_months}`, `{api_to_sub_ratio}`, `{subscription_savings_usd}`, `{usage_based_usd}` - subscriptions versus metered spend.
- `{top_tool}`, `{top_tool_share_pct}`, `{top_model}`, `{top_model_share_pct}`, `{top_project}`, `{top_project_share_pct}`, `{busiest_month}`, `{busiest_month_tokens}` - concentration.
- `{latest_month}`, `{latest_month_tokens}`, `{latest_month_api_usd}`, `{prev_month}`, `{prev_month_tokens}`, `{month_over_month_pct}` - trend.
- `{run_rate_monthly_tokens}`, `{run_rate_monthly_usd}`, `{projected_12mo_api_usd}`, `{projected_12mo_subscription_usd}` - run rate over active months.
- `{assumed_models}`, `{excluded_sources}`, `{low_confidence_rules}` - caveats.
- Tables (Markdown): `{tools_table}`, `{months_table}`, `{models_table}`, `{projects_table}`, `{accounts_table}`, `{subscription_table}`, `{hosts_table}`, `{billing_table}`.
- Month scope (`--var month=YYYY-MM`, default latest month): `{month}`, `{month_tokens}`, `{month_calls}`, `{month_api_usd}`, `{month_cache_savings_usd}`, `{month_tools_table}`, `{month_accounts_table}`.
- Account scope (`--var account=<key>`, default the largest account): `{account}`, `{account_label}`, `{account_plan}`, `{account_calls}`, `{account_tokens}`, `{account_api_usd}`, `{account_subscription_usd}`, `{account_months}`, `{account_ratio}`, `{account_months_table}`.
- Project scope (`--var project=<substring of the working directory>`, default the largest project): `{project}`, `{project_calls}`, `{project_tokens}`, `{project_api_usd}`, `{project_share_pct}`, `{project_tools_table}`.

Supplied with `--var`:

- `{prepared_for}` - recipient (person, team or client).
- `{reference}` - document reference or ticket.
- `{notes}` - free text appended at the end.
- `{previous_value}`, `{corrected_value}`, `{cause}`, `{affected_documents}` - correction notices.
- `{contract_id}`, `{billing_period}` - billing evidence summaries.

Anything left unfilled stays as `{name}` so the gap is visible.

## Templates

### executive-summary
Use when: leadership wants one page on how much agent work happened, what it would have cost, and what paid for it.

# Agent usage: executive summary

**Prepared for:** {prepared_for} · **Prepared by:** {brand_name} ({brand_contact}) · **Date:** {date} · **Reference:** {reference}

## Headline

Between {period_start} and {period_end}, {tools_count} coding agents on {hosts_count} host(s) made {total_calls} model calls in {total_sessions} sessions, moving {total_tokens} tokens. At published list prices the same traffic is worth {api_equivalent_usd}; prompt caching removed {cache_savings_usd} ({cache_savings_pct}) from that figure, and {subscription_accounts_count} flat-rate subscription(s) costing {subscription_usd} over {subscription_months} account-months paid for the subscription-billed share. Metered (usage-based) spend was {usage_based_usd}.

## Where the volume is

- {top_tool} carries {top_tool_share_pct} of all tokens; {top_model} is the busiest model at {top_model_share_pct}.
- The busiest working directory, {top_project}, holds {top_project_share_pct}.
- The busiest month was {busiest_month} ({busiest_month_tokens} tokens); {latest_month} closed at {latest_month_tokens}, {month_over_month_pct} against {prev_month}.

## By tool

{tools_table}

## Subscriptions against list price

{subscription_table}

## Caveats

Models priced at a stated sibling: {assumed_models}. Excluded sources: {excluded_sources}. Attribution rules below high confidence: {low_confidence_rules}. Figures are API-equivalents, not invoices.

{notes}

### monthly-usage-statement
Use when: a recurring statement for one calendar month is needed (finance close, team update, client transparency).

# Agent usage statement: {month}

**Prepared for:** {prepared_for} · **Prepared by:** {brand_name} · **Issued:** {date} · **Reference:** {reference}

## Month at a glance

| Measure | Value |
|---|---:|
| Model calls | {month_calls} |
| Tokens (all classes) | {month_tokens} |
| API-equivalent at list price | {month_api_usd} |
| Cache savings in the month | {month_cache_savings_usd} |

## By tool

{month_tools_table}

## By account

{month_accounts_table}

## Context

Twelve-month trend and the period to date:

{months_table}

Ledger snapshot {snapshot_date}; period covered {period}. Tokens are counted once after de-duplication of streamed turns and replayed history. API-equivalents value the traffic at list rates and are not amounts owed.

{notes}

### quarterly-usage-review
Use when: reviewing a quarter (or any multi-month window) for trend, concentration and spend posture.

# Quarterly agent usage review

**Period reviewed:** {period} · **Prepared for:** {prepared_for} · **Prepared by:** {brand_name} · **Date:** {date}

## Trend

{months_table}

Run rate over active months: {run_rate_monthly_tokens} tokens and {run_rate_monthly_usd} API-equivalent per month. The busiest month was {busiest_month}; the latest, {latest_month}, moved {month_over_month_pct} against {prev_month}.

## Concentration

- Tool: {top_tool} at {top_tool_share_pct}.
- Model: {top_model} at {top_model_share_pct}.
- Project: {top_project} at {top_project_share_pct}.

## Models

{models_table}

## Projects

{projects_table}

## Spend posture

Subscriptions {subscription_usd} across {subscription_accounts_count} account(s) against {api_equivalent_usd} API-equivalent (ratio {api_to_sub_ratio}). Usage-based spend {usage_based_usd}. Cache savings {cache_savings_usd} ({cache_savings_pct}).

## Actions

{notes}

### account-statement
Use when: one subscription or API account needs its own statement (per-person, per-team, or for a reimbursement claim).

# Account statement: {account_label}

**Account key:** {account} · **Plan:** {account_plan} · **Prepared for:** {prepared_for} · **Date:** {date} · **Reference:** {reference}

## Totals for the period {period}

| Measure | Value |
|---|---:|
| Model calls | {account_calls} |
| Tokens | {account_tokens} |
| API-equivalent at list price | {account_api_usd} |
| Subscription paid (active months only) | {account_subscription_usd} over {account_months} month(s) |
| API-equivalent to subscription ratio | {account_ratio} |

## By month

{account_months_table}

## How calls were attributed

Attribution follows the ordered rules in `accounts.json` (first match wins); the plan stamped on each call, the host's login and the working directory are the evidence. Rules below high confidence: {low_confidence_rules}.

{notes}

### subscription-vs-api-memo
Use when: deciding whether flat-rate subscriptions or metered API keys are the better arrangement for the observed traffic.

# Memo: subscriptions versus API list price

**To:** {prepared_for} · **From:** {brand_name} · **Date:** {date} · **Reference:** {reference}

## Finding

Over {period}, subscription-billed agents produced traffic worth {api_equivalent_usd} at list price (or {cost_if_uncached_usd} with no caching). The subscriptions that paid for it cost {subscription_usd} across {subscription_months} account-months, a ratio of {api_to_sub_ratio} API-equivalent dollars per subscription dollar and a difference of {subscription_savings_usd}.

## Per account

{subscription_table}

## Assumptions

- Identical traffic on a metered key, at the list prices in `pricing.json` as of {snapshot_date}.
- Cache behaviour on a metered key would match what the agents achieved on the subscription ({cache_read_share_pct} of prompt tokens served from cache).
- Subscription months count only months with at least one call on that account.
- Models priced at a stated sibling: {assumed_models}.

## Recommendation

{notes}

### subscription-renewal-recommendation
Use when: a subscription renews and someone must decide keep, downgrade or cancel.

# Subscription renewal recommendation

**Account:** {account_label} ({account_plan}) · **Prepared for:** {prepared_for} · **Date:** {date}

## Evidence

- {account_calls} calls and {account_tokens} tokens over {account_months} active month(s) in {period}.
- API-equivalent {account_api_usd} against {account_subscription_usd} paid; ratio {account_ratio}.
- Latest month across all accounts: {latest_month_tokens} tokens, {month_over_month_pct} against {prev_month}.

## Monthly detail

{account_months_table}

## Recommendation

A ratio above 1.0 means the subscription delivered more list-price value than it cost; a ratio well below 1.0 for several months suggests a lower tier or a metered key. Decide on the trend, not on one month.

{notes}

### cache-savings-brief
Use when: explaining what prompt caching contributed and where it is missing.

# Cache savings brief

**Prepared for:** {prepared_for} · **Prepared by:** {brand_name} · **Date:** {date}

## Summary

{cache_read_share_pct} of all prompt tokens in {period} were served from cache. Priced at list rates the traffic is worth {api_equivalent_usd}; without caching it would be {cost_if_uncached_usd}. Caching therefore removed {cache_savings_usd} ({cache_savings_pct}).

## Token classes

| Class | Tokens |
|---|---:|
| Fresh prompt (uncached) | {input_uncached} |
| Cache read | {cache_read} |
| Cache write | {cache_write} |
| Output (incl. reasoning) | {output_tokens} |
| Reasoning | {reasoning_tokens} |

## By tool

{tools_table}

## Notes

Anthropic cache reads are billed at a fraction of the input price and writes at a premium; OpenAI cached input is discounted with no write charge. A tool with a low cache-read share re-sends its context at full price on every call.

{notes}

### budget-forecast-memo
Use when: projecting agent spend for a budget cycle from the observed run rate.

# Budget forecast: agent usage

**Prepared for:** {prepared_for} · **Prepared by:** {brand_name} · **Date:** {date} · **Reference:** {reference}

## Run rate

Averaged over active months in {period}: {run_rate_monthly_tokens} tokens and {run_rate_monthly_usd} API-equivalent per month. Latest month {latest_month}: {latest_month_tokens} tokens, {latest_month_api_usd}.

## Twelve-month projection

| Scenario | Annual figure |
|---|---:|
| Same traffic on metered API keys at list price | {projected_12mo_api_usd} |
| Current subscriptions continued | {projected_12mo_subscription_usd} |
| Usage-based spend at the current rate | {usage_based_usd} over the period to date |

## Trend basis

{months_table}

## Risks

Projections extrapolate a run rate; agent loops and new projects change volume by an order of magnitude within a month. Re-run the ledger before committing a number.

{notes}

### project-cost-allocation
Use when: allocating agent cost to projects, clients or cost centres by working directory.

# Project cost allocation

**Period:** {period} · **Prepared for:** {prepared_for} · **Prepared by:** {brand_name} · **Date:** {date}

## Allocation by working directory

{projects_table}

## Basis

Allocation follows the working directory recorded on each call. The figures are API-equivalents at list price; the subscription cost ({subscription_usd}) can be spread in the same proportions, and usage-based calls ({usage_based_usd}) are real spend already attributed by plan.

## Largest project

{project} received {project_calls} calls and {project_tokens} tokens ({project_share_pct} of the period), worth {project_api_usd}.

{project_tools_table}

{notes}

### client-billing-evidence-summary
Use when: an invoice for agentic work needs a usage exhibit; feed the verified figures to the invoice skill.

# Usage evidence for billing

**Client:** {prepared_for} · **Contract:** {contract_id} · **Billing period:** {billing_period} · **Prepared by:** {brand_name} · **Date:** {date}

## Scope of work evidenced

Working directory or project: {project}. {project_calls} model calls and {project_tokens} tokens ({project_share_pct} of all recorded traffic) in {period}.

## Detail

{project_tools_table}

## Valuation

API-equivalent at list price: {project_api_usd}. This is a reference value for the effort involved, not an amount owed; the billable amount is set by the agreement.

## Provenance

Compiled from local agent logs on {hosts}, de-duplicated, priced with `pricing.json` as of {snapshot_date}. The event log (`all_events.csv`) and the study package are available on request. Both name the hosts, working directories and accounts behind every call, not only the client's project: review them or supply the anonymised copy (see the package's `SENSITIVITY.md` and `ledger.py publish-check`) before releasing either to a client.

{notes}

### model-mix-report
Use when: engineering wants to know which models carry the work and how the mix moved.

# Model mix report

**Period:** {period} · **Prepared for:** {prepared_for} · **Prepared by:** {brand_name} · **Date:** {date}

## Models by volume

{models_table}

## Observations

- {top_model} carries {top_model_share_pct} of all tokens.
- Reasoning tokens: {reasoning_tokens} of {output_tokens} output tokens.
- Models priced at a stated sibling (unpublished prices): {assumed_models}.

## By tool

{tools_table}

{notes}

### tool-adoption-summary
Use when: comparing which agents and harnesses are actually used across the machines.

# Tool adoption summary

**Period:** {period} · **Hosts:** {hosts} · **Prepared for:** {prepared_for} · **Date:** {date}

## Tools

{tools_table}

## Hosts

{hosts_table}

## Reading

{top_tool} carries {top_tool_share_pct} of tokens across {tools_count} tools. A tool with many sessions and few tokens is used for short tasks; a tool with few sessions and many tokens is running long agent loops.

{notes}

### host-inventory-report
Use when: documenting which machines, profiles and directories were scanned, and what was not.

# Host and log inventory

**Snapshot:** {snapshot_date} · **Prepared by:** {brand_name} · **Date:** {date}

## Hosts scanned

{hosts_table}

## Not scanned or excluded

{excluded_sources}

## Retention caveats

Some tools delete transcripts after a retention window; figures for those tools are lower bounds unless the ledger store already held the calls. The store is append-only, so history remains available after the tool has purged it.

{notes}

### data-quality-and-exclusions-note
Use when: the reader must know how much to trust the numbers.

# Data quality and exclusions

**Ledger snapshot:** {snapshot_date} · **Period:** {period} · **Prepared by:** {brand_name}

## Evidence classes

- Class A: per-call records from agent logs ({total_calls} calls after de-duplication).
- Class B: tool counters used for cross-checks (where available).
- Class C: priced estimates at list rates ({api_equivalent_usd}).

## Known limitations

- Excluded sources: {excluded_sources}.
- Models priced at a stated sibling: {assumed_models}.
- Attribution rules below high confidence: {low_confidence_rules}.
- Replayed history in forked threads is dropped; vendor dashboards that include it will read higher.

## Coverage

{hosts_table}

{notes}

### correction-notice
Use when: a previously issued figure changed after a rerun and recipients must be told.

# Correction notice

**Reference:** {reference} · **Issued:** {date} · **Prepared by:** {brand_name} · **To:** {prepared_for}

## What changed

| | Value |
|---|---:|
| Previously reported | {previous_value} |
| Corrected | {corrected_value} |

## Cause

{cause}

## Documents affected

{affected_documents}

## Current figures

Period {period}: {total_calls} calls, {total_tokens} tokens, {api_equivalent_usd} API-equivalent, {subscription_usd} in subscriptions. Ledger snapshot {snapshot_date}.

{notes}
