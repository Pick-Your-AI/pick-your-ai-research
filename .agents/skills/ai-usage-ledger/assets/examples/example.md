# AI coding-agent usage: token volume, caching and cost study

**Snapshot date:** 2026-09-09 · **Timezone for time-of-day analysis:** America/New_York · **Mode:** read-only, local logs only · **Prices:** list API rates as of 2026-09-07

**Scope:** every model call recorded on disk by Codex, Claude Code across 1 hosts (fixture), 2026-01-01 to 2026-09-01. 13 calls in 11 sessions were compiled into one event stream, cross-checked against the tools' own counters, and priced at published API list rates. Dollar figures are API-equivalents; the subscription-billed work was actually paid for by 2 flat-rate subscriptions.

## Executive summary

**73.2% of tokens are aider, and 10.0% of all prompt tokens were served from cache.** The two busiest working directories, `repo` (73.2%, 1 threads) and `w` (9.8%, 1 threads), account for 83.0% of all tokens; the two busiest months, 2026-04 and 2026-06, hold 83.0% of the period. At list prices the compiled usage is worth $0.22; the same tokens without caching would be $0.23; the 2 subscriptions that actually paid for the subscription-billed tools cost $400.00 over the months they were used.

| Measure | Value |
|---|---:|
| Model calls compiled | 13 |
| Sessions / threads | 11 |
| Typed prompts recovered | 4 |
| Active days | 10 |
| Total tokens (all four classes), de-duplicated | 53,810 (53.81K) |
| Output tokens (reasoning share) | 1.00K (4.0%) |
| Cache hit rate, all tools | 10.0% |
| API-equivalent cost at list rates | $0.22 |
| Cost if nothing had been cached | $0.23 |
| Saved by prompt caching | $0.01 (6.2%) |
| Subscriptions paid (2 accounts, months with use) | $400.00 |
| API-equivalent of subscription-billed calls | $0.01 |
| Usage-based calls (real spend at list rates) | $0.21 |
| Peak month | 2026-04: 39.38K tokens, $0.20 API-equivalent |

**Confidence definitions.** *High*: read directly from per-call usage records the tool wrote at request time, de-duplicated, and cross-checked against a second counter. *Medium*: derived from those records through a documented rule with a stated assumption (pricing rows, replay filter, account rules). *Low*: an estimate that depends on an unpublished price or on a tool-maintained aggregate that could not be reconciled call by call.

## 1. Coverage and evidence rules

Three classes of evidence are used and kept apart throughout:

1. **Per-call usage records (class A).** Claude Code session transcripts (`~/.claude/projects/**/*.jsonl`, assistant messages carry `usage`), Codex rollouts (`~/.codex/sessions/**/rollout-*.jsonl`, `token_count` events), Copilot CLI session events, opencode's SQLite message table, and OpenClaw session files. Every number in the results sections comes from this class unless marked otherwise.
2. **Tool-maintained aggregates (class B).** Codex `state_5.sqlite` (`threads.tokens_used`) and Claude Code `stats-cache.json` (`modelUsage`, `dailyActivity`). Used to validate class A and to bound what class A cannot see.
3. **Derived estimates (class C).** API-equivalent cost, cache savings, subscription comparisons and account attribution. These multiply class A tokens by published list prices in `pricing.json` and apply the rules in `accounts.json`; models without a published rate are priced at a stated sibling.

### Source inventory

| Tool | Host | Files | Size | First | Last | Calls | Tokens |
|---|---|---:|---:|---|---|---:|---:|
| Codex | fixture | 2 | 0.00 GB | 2026-02-01 | 2026-02-01 | 3 | 2.43K |
| Claude Code | fixture | 1 | 0.00 GB | 2026-01-01 | 2026-01-01 | 1 | 1.26K |
| pi | fixture | 1 | 0.00 GB | 2026-08-01 | 2026-08-01 | 1 | 430 |
| gemini-cli | fixture | 1 | 0.00 GB | 2026-03-01 | 2026-03-01 | 1 | 560 |
| kimi | fixture | 1 | 0.00 GB | 2026-05-01 | 2026-05-01 | 1 | 1.09K |
| cline | fixture | 1 | 0.00 GB | 2026-03-31 | 2026-03-31 | 1 | 1.66K |
| codebuff | fixture | 1 | 0.00 GB |  |  | 1 | 425 |
| aider | fixture | 1 | 0.00 GB | 2026-04-01 |  | 2 | 39.38K |
| mistral-vibe | fixture | 1 | 0.00 GB | 2026-06-01 |  | 1 | 5.30K |
| continue | fixture | 1 | 0.00 GB |  |  | 1 | 1.28K |

Hosts: **fixture** = fixture.

### Scan provenance

| Host | Tool | Root scanned | Calls found | Prompts | Tool's thread count | Tool's token total |
|---|---|---|---:|---:|---:|---:|
| fixture | Claude Code | `/tmp/ai-usage-ledger-skill/tests/fixtures/claude` | 1 | 0 | – | – |
| fixture | Codex | `/tmp/ai-usage-ledger-skill/tests/fixtures/codex` | 3 | 0 | – | – |
| fixture | pi | `/tmp/ai-usage-ledger-skill/tests/fixtures/pi` | 1 | 0 | – | – |
| fixture | gemini-cli | `/tmp/ai-usage-ledger-skill/tests/fixtures/gemini` | 1 | 0 | – | – |
| fixture | cline | `/tmp/ai-usage-ledger-skill/tests/fixtures/cline` | 1 | 0 | – | – |
| fixture | aider | `/tmp/ai-usage-ledger-skill/tests/fixtures/aider` | 2 | 0 | – | – |
| fixture | kimi | `/tmp/ai-usage-ledger-skill/tests/fixtures/kimi` | 1 | 0 | – | – |
| fixture | mistral-vibe | `/tmp/ai-usage-ledger-skill/tests/fixtures/vibe` | 1 | 0 | – | – |
| fixture | continue | `/tmp/ai-usage-ledger-skill/tests/fixtures/continue` | 1 | 0 | – | – |
| fixture | codebuff | `/tmp/ai-usage-ledger-skill/tests/fixtures/generic` | 1 | 0 | – | – |

Scan statistics: **fixture** 11 files, 0.0 GB, 39 lines, 0 JSON errors, 2 replayed Codex token events skipped, 1 duplicates skipped, 0.0s.

### Sources examined and excluded

- **Claude desktop app and claude.ai** leave no local transcript.
- **Antigravity / Gemini** stores conversations as protobuf blobs without token fields.

## 2. Method

### 2.1 Parsing rules

- **Claude Code.** Every `assistant` line with `message.usage` is one call. Streamed turns are written as several lines sharing one `message.id`; they are de-duplicated on that id across all files of a host. `agent-*.jsonl` files and `isSidechain` lines are labelled sub-agent. `cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` split cache writes by TTL for pricing; transcripts without that breakdown are treated as 5-minute writes. Lines with model `<synthetic>` and zero usage are dropped.
- **Codex.** Each `event_msg` of type `token_count` with a non-null `info` is one call, using `last_token_usage`. Consecutive events whose cumulative `total_token_usage.total_tokens` did not change are duplicates and dropped. Model and reasoning effort come from the most recent `turn_context`; the thread's `session_meta` supplies cwd, originator (CLI, Desktop, VS Code, exec) and version; `rate_limits.plan_type` on the same event records the billing plan. `input_tokens` includes cached tokens in Codex's schema, so uncached input = `input_tokens - cached_input_tokens`.
- **Replayed history.** Forked and sub-agent Codex rollouts (`forked_from_id` / `source.subagent`, and any file carrying a second `session_meta`, which is the parent's) begin with the parent's entire history copied in as one write burst, re-stamped at fork time. Everything up to the first gap of more than 2 seconds between consecutive lines is treated as replay and dropped. 2 `token_count` events were removed across hosts. Without this rule the parent's usage is counted once per child, and the parent's billing plan is copied onto the child; the Codex app's own counter has exactly that inflation.
- **Copilot CLI.** One record per session from `session.shutdown.tokenDetails` (input, cache read, cache write, output); `assistant.message` events only carry output tokens and are used as a fallback when a session has no shutdown record.
- **opencode.** `message.data.tokens` and `cost` from `opencode.db`; the tool's own USD cost is used as-is.
- **OpenClaw.** `message.usage` on assistant messages; `<id>.checkpoint.<x>.jsonl` files replay the parent session and are de-duplicated on (message id, timestamp) across files.

### 2.2 Token taxonomy

| Column | Meaning | Priced at |
|---|---|---|
| `input_uncached` | prompt tokens processed fresh | input rate |
| `cache_read` | prompt tokens served from the provider's prompt cache | cache-read rate |
| `cache_write` | prompt tokens written to cache (Anthropic only; OpenAI does not charge writes) | cache-write rate for the TTL used |
| `output` | completion tokens, reasoning included | output rate |
| `reasoning` | the reasoning / thinking share of `output` | informational |
| `total` | sum of the first four | – |

### 2.3 Pricing model

API-equivalent cost of a call = Σ tokens × list rate for that model, from `pricing.json`. `cost_if_uncached` re-prices the same call with every prompt token at the input rate; the difference is the cache saving. No batch discount, data-residency multiplier, fast-mode premium or long-context surcharge is applied.

| Model | Input /M | Cache read /M | Cache write 5m /M | Cache write 1h /M | Output /M | Basis |
|---|---:|---:|---:|---:|---:|---|
| `claude-opus-5` | $5.00 | $0.500 | $6.25 | $10.00 | $25.00 | published |
| `claude-sonnet-5` | $2.00 | $0.200 | $2.50 | $4.00 | $10.00 | published |
| `gpt-5.5` | $5.00 | $0.500 | – | – | $30.00 | published |
| `gpt-5-mini` | $0.25 | $0.025 | – | – | $2.00 | published |

### 2.4 Accounts and subscription attribution

Accounts were identified from the credential files on each host. Codex rollouts record the billing plan on every call (`rate_limits.plan_type`) but not the account, so calls are attributed to accounts by ordered rules in `accounts.json`; each rule carries its evidence and a confidence level. A subscription month is counted only when the account recorded at least one call in that month.

| Account | Identity | Plan | Price | Evidence |
|---|---|---|---|---|
| `codex:example` | example@example.com | ChatGPT Pro | $200/mo | fixture |
| `claude:example` | example@example.com | Claude Max 20x | $200/mo | fixture |
| `gemini:example` | Gemini CLI (Code Assist) | Gemini Code Assist | usage-based / n.a. | fixture |
| `other:usage-based` | Other tools (API keys) | usage-based | usage-based / n.a. | fixture |

| Rule (first match wins) | Account | Billing | Confidence | Why |
|---|---|---|---|---|
| `tool=codex, plan=self_serve_business_usage_based` | `other:usage-based` | usage-based | high | plan stamped on the call |
| `tool=codex` | `codex:example` | subscription | high | single login on the fixture host |
| `tool=claude-code` | `claude:example` | subscription | high | single login on the fixture host |
| `tool=gemini-cli` | `gemini:example` | subscription | high | fixture |
| `` | `other:usage-based` | usage-based | medium | every other tool in the fixture set uses an API key |

### 2.5 Validation against tool-maintained counters

## 3. Findings

### F01 · Volume is concentrated in a few hundred threads and two projects.

**Confidence:** High. Two working directories hold 83.0% of all tokens: `repo` (73.2% across 1 threads) and `w` (9.8% across 1 threads). Within aider, the top 1% of threads (0) hold 100.0% of tokens and the top 10% hold 100.0%; the largest single thread holds 100.0%. The two largest threads are `repo@202…` in `repo` (gpt-5.5, 2026-04-01 to 2026-04-01, 0 h, 39.38K) and `v1…` in `w` (devstral-2, 2026-06-01 to 2026-06-01, 0 h, 5.30K).

**Implication.** Cost and capacity planning should be done per project and per thread, not per month; a few unattended multi-thread loops set the figures.

### F02 · The cache, not the model, is doing the work.

**Confidence:** High. aider re-sent a median of 19.61K prompt tokens per call (p90 33.07K, max 36.43K) while producing a median of 73 output tokens. 10.0% of prompt tokens were cache hits (Codex 86.4%; Claude Code 82.6%). Prompt tokens per output token: Codex 10; Claude Code 24.

**Implication.** At list rates the cache removed $0.01 (6.2%) from the bill. Context length, not output, is the cost driver.

### F03 · 2 flat-rate subscriptions covered work worth far more at list price.

**Confidence:** Medium (class C). example@example.com (ChatGPT Pro): $200.00 over 1 months against $0.01 (0.0×); example@example.com (Claude Max 20x): $200.00 over 1 months against $0.00 (0.0×). Calls stamped usage-based total $0.21 at list rates and are real spend, not subscription-covered. The peak month, 2026-04, was $0.20 API-equivalent.

**Implication.** The comparison assumes the provider would have served the same traffic on a pay-as-you-go key at list rates; rate limits on each subscription, not price, are the binding constraint in practice.

### F04 · Reasoning effort and sub-agent fan-out are material.

**Confidence:** High. Reasoning tokens are 4.0% of output (Codex 8.7%; Claude Code 0.0%). aider calls by configured effort: unset 100.0%. Sub-agent share of tokens: Codex 9.5%; Claude Code 0.0%.

**Implication.** Effort settings and fan-out multiply context re-reads; they are the two levers that change the bill without changing the task.

### F05 · The model mix moved over time.

**Confidence:** High. gpt-5.5 carries 73.2% of all tokens (91.5% of API-equivalent cost). In 2026-09 the leading models by volume were claude-opus-5 (425).

**Implication.** Blended cost per million output tokens: Codex $40.65; Claude Code $76.00; these are dominated by the context re-read, not the output rate.

### F07 · Cost sensitivity to unpublished prices is small.

**Confidence:** Medium. 0.3% of the API-equivalent total ($0.00) rests on models priced by assumption. Halving or doubling every assumed rate moves the total to between $0.22 and $0.22.

**Implication.** The headline cost is robust to the pricing assumptions; it is not robust to the cache-read rate, which is where most of the discount comes from.

## 4. Results

### 4.1 By tool

| Tool | Calls | Sessions | Uncached in | Cache read | Cache write | Output | Total | Hit rate | API-eq. | Cache saved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Codex | 3 | 2 | 300 | 1.90K | 0 | 230 | 2.43K | 86.4% | $0.01 | $0.01 |
| Claude Code | 1 | 1 | 10 | 1.00K | 200 | 50 | 1.26K | 82.6% | $0.00 | $0.00 |

### 4.1b By account

| Account | Identity | Plan | Months | Paid | API-eq. | If uncached | API / sub | Calls | Tokens |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `other:usage-based` | Other tools (API keys) | usage-based | 7 | $0.00 | $0.21 | $0.21 | usage-based | 8 | 49.56K |
| `codex:example` | example@example.com | ChatGPT Pro | 1 | $200.00 | $0.01 | $0.02 | 0.0× | 3 | 2.43K |
| `claude:example` | example@example.com | Claude Max 20x | 1 | $200.00 | $0.00 | $0.01 | 0.0× | 1 | 1.26K |
| `gemini:example` | Gemini CLI (Code Assist) | Gemini Code Assist | 1 | $0.00 | $0.00 | $0.00 | usage-based | 1 | 560 |

| Month | example@example.com | example@example.com | Subscriptions paid | Usage-based spend |
|---|---:|---:|---:|---:|
| 2026-01 | – | $0.00 | $200.00 | – |
| 2026-02 | $0.01 | – | $200.00 | – |
| 2026-03 | – | – | $0.00 | $0.00 |
| 2026-04 | – | – | $0.00 | $0.20 |
| 2026-05 | – | – | $0.00 | $0.00 |
| 2026-06 | – | – | $0.00 | $0.00 |
| 2026-07 | – | – | $0.00 | $0.00 |
| 2026-08 | – | – | $0.00 | $0.00 |
| 2026-09 | – | – | $0.00 | $0.00 |

| Plan recorded on the Codex call | Calls | Tokens | API-eq. |
|---|---:|---:|---:|
| `pro` | 3 | 2.43K | $0.01 |

### 4.2 By month

*Figure 1 (tokens per month by tool) is rendered in the HTML version.*

*Figure 2 (API-equivalent cost per month) is rendered in the HTML version.*

| Month | Calls | Tokens | Output | Codex hit | Claude Code hit | API-eq. | Subscriptions | API/sub |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-01 | 1 | 1.26K | 50 | – | 82.6% | $0.00 | $200.00 | 0.0× |
| 2026-02 | 3 | 2.43K | 230 | 86.4% | – | $0.01 | $200.00 | 0.0× |
| 2026-03 | 2 | 2.22K | 120 | – | – | $0.00 | $0.00 | – |
| 2026-04 | 2 | 39.38K | 147 | – | – | $0.20 | $0.00 | – |
| 2026-05 | 1 | 1.09K | 40 | – | – | $0.00 | $0.00 | – |
| 2026-06 | 1 | 5.30K | 300 | – | – | $0.00 | $0.00 | – |
| 2026-07 | 1 | 1.28K | 80 | – | – | $0.00 | $0.00 | – |
| 2026-08 | 1 | 430 | 10 | – | – | $0.00 | $0.00 | – |
| 2026-09 | 1 | 425 | 25 | – | – | $0.00 | $0.00 | – |

*Figure 3 (cache hit rate by month) is rendered in the HTML version.*

### 4.3 By model

| Model | Tool | Calls | Tokens | Share | Output | Hit rate | API-eq. |
|---|---|---:|---:|---:|---:|---:|---:|
| `gpt-5.5` | aider | 2 | 39.38K | 73.2% | 147 | 0.0% | $0.20 |
| `devstral-2` | mistral-vibe | 1 | 5.30K | 9.8% | 300 | 0.0% | $0.00 |
| `gpt-5.5` | Codex | 3 | 2.43K | 4.5% | 230 | 86.4% | $0.01 |
| `claude-sonnet-5` | cline | 1 | 1.66K | 3.1% | 60 | 43.8% | $0.00 |
| `openai/gpt-5-mini` | continue | 1 | 1.28K | 2.4% | 80 | 0.0% | $0.00 |
| `claude-opus-5` | Claude Code | 1 | 1.26K | 2.3% | 50 | 82.6% | $0.00 |
| `kimi-k2.6` | kimi | 1 | 1.09K | 2.0% | 40 | 85.7% | $0.00 |
| `gemini-2.5-pro` | gemini-cli | 1 | 560 | 1.0% | 60 | 60.0% | $0.00 |
| `anthropic/claude-sonnet-5` | pi | 1 | 430 | 0.8% | 10 | 95.2% | $0.00 |
| `claude-opus-5` | codebuff | 1 | 425 | 0.8% | 25 | 25.0% | $0.00 |

### 4.4 Distributions

| Tool | Calls | Prompt p50 | p90 | p99 | max | Output p50 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Codex | 3 | 1.00K | 1.00K | 1.00K | 1.00K | 100 | 100 | 100 | 100 |
| Claude Code | 1 | 1.21K | 1.21K | 1.21K | 1.21K | 50 | 50 | 50 | 50 |

| Tool | Sessions | Calls p50 | p90 | max | Tokens p50 | p90 | max | Span p50 | p90 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Codex | 2 | 2 | 2 | 2 | 1.22K | 2.00K | 2.20K | 0.0 h | 0.0 h | 0 h |
| Claude Code | 1 | 1 | 1 | 1 | 1.26K | 1.26K | 1.26K | 0.0 h | 0.0 h | 0 h |

### 4.5 Time of day

Calls by weekday and hour (America/New_York), Codex and Claude Code combined. Darker cells are more calls; the scale is square-root so unattended loops do not flatten everything else.

*Figure 4 (weekday × hour heatmap) is rendered in the HTML version.*

Busiest hours: 05:00 (3), 06:00 (1), 00:00 (0), 01:00 (0), 02:00 (0). Quietest: 00:00 (0), 01:00 (0), 02:00 (0).

### 4.6 Heaviest sessions

| Tool | Host | Thread | Working directory (tail) | Model | Calls | Hours | Tokens | Output | API-eq. |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| aider | fixture | `repo@2026-04-` | /ai-usage-ledger-skill/tests/fixtures/aider/repo | gpt-5.5 | 2 | 0 | 39.38K | 147 | $0.20 |
| mistral-vibe | fixture | `v1` | /w | devstral-2 | 1 | 0 | 5.30K | 300 | $0.00 |
| Codex | fixture | `rollout-2026-` | /w | gpt-5.5 | 2 | 0 | 2.20K | 200 | $0.01 |
| cline | fixture | `t1` |  | claude-sonnet-5 | 1 | 0 | 1.66K | 60 | $0.00 |
| continue | fixture | `c1` |  | openai/gpt-5-mini | 1 | 0 | 1.28K | 80 | $0.00 |
| Claude Code | fixture | `s1` | /w | claude-opus-5 | 1 | 0 | 1.26K | 50 | $0.00 |
| kimi | fixture | `k1` |  | kimi-k2.6 | 1 | 0 | 1.09K | 40 | $0.00 |
| gemini-cli | fixture | `g1` |  | gemini-2.5-pro | 1 | 0 | 560 | 60 | $0.00 |
| pi | fixture | `2026-08-01_p` |  | anthropic/claude-sonnet-5 | 1 | 0 | 430 | 10 | $0.00 |
| codebuff | fixture | `chat-messages` |  | claude-opus-5 | 1 | 0 | 425 | 25 | $0.00 |
| Codex | fixture | `c1000000-0000` | /w | gpt-5.5 | 1 | 0 | 230 | 30 | $0.00 |

*Figure 5 (largest sessions) is rendered in the HTML version.*

### 4.7 Working directories

| Tool | Directory | Sessions | Calls | Tokens | API-eq. |
|---|---|---:|---:|---:|---:|
| aider | `/tmp/ai-usage-ledger-skill/tests/fixtures/aider/repo` | 1 | 2 | 39.38K | $0.20 |
| mistral-vibe | `/w` | 1 | 1 | 5.30K | $0.00 |
| Codex | `/w` | 2 | 3 | 2.43K | $0.01 |
| cline | `?` | 1 | 1 | 1.66K | $0.00 |
| continue | `?` | 1 | 1 | 1.28K | $0.00 |
| Claude Code | `/w` | 1 | 1 | 1.26K | $0.00 |
| kimi | `?` | 1 | 1 | 1.09K | $0.00 |
| gemini-cli | `?` | 1 | 1 | 560 | $0.00 |
| pi | `?` | 1 | 1 | 430 | $0.00 |
| codebuff | `?` | 1 | 1 | 425 | $0.00 |

### 4.8 Entry points, effort and versions

| Tool | Entry point / originator | Calls | Tokens | API-eq. |
|---|---|---:|---:|---:|
| aider | aider | 2 | 39.38K | $0.20 |
| mistral-vibe | vibe | 1 | 5.30K | $0.00 |
| Codex | codex-tui | 3 | 2.43K | $0.01 |
| cline | cline | 1 | 1.66K | $0.00 |
| continue | continue | 1 | 1.28K | $0.00 |
| Claude Code | cli | 1 | 1.26K | $0.00 |
| kimi | kimi | 1 | 1.09K | $0.00 |
| gemini-cli | gemini-cli | 1 | 560 | $0.00 |
| pi | openclaw:pi | 1 | 430 | $0.00 |
| codebuff | codebuff | 1 | 425 | $0.00 |

| Tool | Effort setting | Calls | Output | Reasoning share | API-eq. |
|---|---|---:|---:|---:|---:|
| Codex | unset | 3 | 230 | 8.7% | $0.01 |
| Claude Code | unset | 1 | 50 | 0.0% | $0.00 |

Client versions seen: **Claude Code** 2.1 (1); **Codex** 0.1 (3).

### 4.9 Cache write TTL (Claude Code)

Of 200 cache-write tokens in Claude Code transcripts, 100.0% were 1-hour writes (2× input rate) and 0.0% were 5-minute writes (1.25×).

## 5. Uncertainty and limitations

- **Retention.** Claude Code transcripts older than the retention window are gone (F06). Codex keeps rollouts indefinitely; Codex coverage is complete for the scanned profiles. Copilot CLI keeps only recent sessions.
- **Replay filter.** The gap rule that strips replayed history from forked Codex rollouts is a heuristic. A genuine first response arriving within 2 s of the end of the replay burst would be dropped; a pause of more than 2 s inside the burst would leave the rest of the parent's history counted. The per-thread comparison in 2.5 bounds the effect.
- **Prices are list prices at one date.** Provider rates change; everything is priced at the sheet in `pricing.json`. Historical months are approximations, not invoices.
- **Tokenizer.** Token counts across model generations are not directly comparable as measures of text volume.
- **Subscription counterfactual.** The API-equivalent figure assumes identical traffic on a pay-as-you-go key. In practice each subscription's rate limits shaped the traffic.
- **Account attribution.** Codex records the billing plan per call but not the account, so accounts are assigned by rules whose evidence and confidence are listed in 2.4; medium- and low-confidence rules are the ones to challenge first.
- **Timestamps.** Tool timestamps are UTC at write time; time-of-day analysis converts to America/New_York. Sessions spanning DST changes are not adjusted.

## 6. Reproducibility

All scripts are standard-library Python 3.8+. Scans run on each host (natively where possible), then one report step merges them.

```
python scripts/run_pipeline.py --manifest manifest.json          # scan every host in the manifest, then report, analyse, build
python scripts/run_pipeline.py --manifest manifest.json --only report,analyze,build   # re-price / re-render without rescanning
```

| File | SHA-256 |
|---|---|
| compile_ai_logs.py | `8aad51938c3200fbf4c03608c65919378357614473d5b9ab15e1fc6a4fd1a990` |
| analyze_events.py | `8afe1edae8d10bbe4a64e07ba78168ad8b90464bfed638041581b1f565a18853` |
| build_report.py | `92c0494857c8409bf94ddca4fed9e94a9c2a3b2d7c2b33b31f23025f7754cdea` |
| pricing.json | `d7690e151fffd3cd506def4d2346cccbbf80ddf19fcdf6d9dfddcf0afcead1fc` |
| summary.json | `2e15732337b3aa97a5ff9fe49d69c1299bb91394ee96f31d987edddd2d107b42` |
| analysis.json | `74700ba95889fa95f22e010e1105eb9f63cab0a80a7d89646fd077d643429c78` |

The event-level dataset (`compiled/all_events.csv`, 13 rows, one per model call with every token class, the pricing row applied, the account assigned and the source file path) is the primary artefact; every table above is an aggregation of it.

## Appendix A. Glossary

| Term | Definition |
|---|---|
| Call | One model request whose usage the tool recorded: an assistant message (Claude Code, OpenClaw, opencode), a `token_count` event (Codex), or a session (Copilot CLI). |
| Session / thread | One transcript file (Claude Code), one rollout file (Codex), one OpenClaw session file, one opencode session, one Copilot session. |
| Sub-agent | A Codex thread spawned by another thread (`source.subagent`) or a Claude Code `agent-*.jsonl` transcript. |
| Cache hit rate | `cache_read ÷ (input_uncached + cache_read + cache_write)`. |
| API-equivalent cost | Tokens × list price per token class, from `pricing.json`. |
| Cache saving | `cost_if_uncached − api_cost`, where `cost_if_uncached` prices every prompt token at the input rate. |
| Account | A login identified from a credential file; assigned to calls by the rules in accounts.json. |
| Usage-based | A call billed per token to a prepaid or metered org rather than covered by a subscription. |

## Appendix B. Package contents

- `USAGE_REPORT.md` — this document.
- `report.html` — the same document with the figures rendered.
- `ledger.json` — machine-readable totals, monthly and model tables, top sessions, validation results, sensitivity, accounts, source inventory and the pricing sheet used.
- `pricing.json` — the rate sheet applied.
- `SHA256SUMS` — binds the files above.
