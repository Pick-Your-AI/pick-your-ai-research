# Log formats the scanner understands

All figures come from per-call usage records the tool wrote at request time (class A evidence). Field names below are what `compile_ai_logs.py` reads; verify them on a sample before trusting a new tool version.

## Claude Code (`~/.claude/projects/<project>/<session>.jsonl`, plus `<session>/subagents/agent-*.jsonl` or `agent-*.jsonl`)

- One JSON object per line. Lines with `"type":"assistant"` carry `message.usage`:
  `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `output_tokens`, `output_tokens_details.thinking_tokens`, and `cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` (TTL split, needed for pricing).
- `input_tokens` is **uncached** input (cache classes are separate). Contrast with Codex.
- A streamed turn is written as several lines with the same `message.id` (one per content block). De-duplicate on that id across every file of the host.
- `model` is on `message.model`; `<synthetic>` rows with zero usage are placeholders.
- Line-level fields: `timestamp` (UTC ISO), `sessionId`, `cwd`, `version`, `entrypoint` (`cli`, `sdk-cli`), `effort`, `isSidechain`, `agentId`, `requestId`.
- `~/.claude/history.jsonl`: one typed prompt per line (`display`, `timestamp` ms, `project`, `sessionId`).
- `~/.claude/stats-cache.json` (class B): `modelUsage` per model cumulative since first session, `dailyActivity` (messages/sessions/tool calls per day), recent `dailyModelTokens`. Survives transcript deletion.
- **Retention:** transcripts older than `cleanupPeriodDays` (default 30) are deleted. Transcript totals are lower bounds; `stats-cache.json` is the fuller counter.

## Codex (`~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<uuid>.jsonl`, `~/.codex/archived_sessions/`)

- Line types: `session_meta` (first line: `id`, `forked_from_id`, `source` including `{"subagent":{...}}`, `cwd`, `originator`, `cli_version`, `timestamp`), `turn_context` (`model`, `collaboration_mode.settings.reasoning_effort`), `response_item` (messages, function calls), `event_msg` with `payload.type`.
- Usage is on `event_msg` / `payload.type == "token_count"`: `payload.info.last_token_usage` (`input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_output_tokens`, `total_tokens`) and `payload.info.total_token_usage` (cumulative for the thread). `info` may be null (rate-limit-only updates): skip those.
- `input_tokens` **includes** the cached tokens; uncached input = `input_tokens - cached_input_tokens`. Output includes reasoning.
- `payload.rate_limits.plan_type` on the same event records the billing plan (`pro`, `plus`, `self_serve_business_usage_based`, ...). It is per call and exact; it never carries the account id.
- Consecutive `token_count` events whose cumulative `total_tokens` did not change are repeats; drop them.
- **Replay:** a forked or spawned rollout starts with the parent's whole history copied in, re-stamped with the fork time, written as one burst (seen: 34,175 lines, 762 MB, 9 seconds). The copied lines include a second `session_meta` (the parent's) and every one of the parent's `token_count` events, byte-identical. Drop everything up to the first gap of more than 2 s between consecutive lines. A fixed time window is not enough.
- `~/.codex/state_5.sqlite` `threads` table (class B): `id`, `rollout_path`, `tokens_used`, `model`, `cwd`, `source`/`thread_source`, `cli_version`, `created_at`. `tokens_used` for spawned threads includes the replayed parent history, so it is inflated the same way; older schemas lack `model`/`thread_source`.
- `~/.codex/history.jsonl`: typed prompts (`session_id`, `ts` epoch seconds, `text`).
- `~/.codex/auth.json`: `tokens.id_token` JWT claims `https://api.openai.com/auth` → `chatgpt_account_id`, `chatgpt_plan_type`, `organizations[].title`; `https://api.openai.com/profile` → `email`. Read claims only; never print tokens.
- `logs_2.sqlite`, `thread_history_1.sqlite`: application logs and item projections, not usage counters.

## GitHub Copilot CLI (`~/.copilot/session-state/<id>/events.jsonl`)

- `session.start` (`data.context.cwd`), `session.model_change` / `session.auto_mode_resolved` (`chosenModel`), `assistant.message` (`model`, `outputTokens` only), `session.shutdown` with `data.tokenDetails.{input,cache_read,cache_write,output}.tokenCount` (authoritative per-session totals).
- Use the shutdown record when present; fall back to summing `assistant.message.outputTokens`.

## opencode (`~/.local/share/opencode/opencode.db`, SQLite)

- `message` table: `data` JSON with `role`, `modelID`, `providerID`, `tokens.{input,output,reasoning,cache.read,cache.write}`, `cost` (USD), `time.created`; `session` table has `directory`, `title`, per-session totals. Older versions used JSON files under `storage/`.
- Copy the db (and `-wal`) locally before opening it from another OS or over a share; `sqlite3` URIs reject UNC authorities.

## OpenClaw gateways (`<config>/agents/<agent>/sessions/<id>.jsonl`)

- `session` line (`cwd`), `model_change` (`provider`, `modelId`), `message` lines with `message.role`, `message.provider`, `message.model`, `message.usage.{input,output,cacheRead,cacheWrite,cost.total}`.
- `<id>.checkpoint.<x>.jsonl` files replay the parent session; de-duplicate on (line id, timestamp) across files.

## Gemini CLI and Qwen Code (`~/.gemini/tmp/<project_hash>/chats/session-*.json[l]`, `~/.qwen/history/<hash>/`)

- Older files are one JSON document (`sessionId`, `projectHash`, `startTime`, `lastUpdated`, `messages[]`); newer ones are JSONL with a header record then message records. Sub-agent sessions carry `kind: "subagent"` and `directories`.
- `gemini` messages carry `model` and `tokens: {input, output, cached, thoughts, tool, total}`; `input` includes `cached`, so uncached = `input - cached`; `thoughts` is added to output and reported as reasoning.

## Cline, Roo Code, Kilo Code (`<globalStorage>/<extension id>/tasks/<task>/`)

- `ui_messages.json` (Kilo: also `cline_messages.json`) is an array of `{ts, type, say|ask, text}`. Entries with `say: "api_req_started"` carry a JSON string in `text`: `{tokensIn, tokensOut, cacheWrites, cacheReads, cost, ...}`; `tokensIn` is uncached input. `task_metadata.json` lists `model_usage[]` with `model_id`.
- Extension ids: `saoudrizwan.claude-dev` (Cline), `rooveterinaryinc.roo-cline` (Roo), `kilocode.kilo-code` (Kilo). Storage root per OS: `%APPDATA%\Code\User\globalStorage`, `~/.config/Code/User/globalStorage`, `~/Library/Application Support/Code/User/globalStorage` (also Cursor, VSCodium, Insiders variants).

## aider (`<repo>/.aider.chat.history.md`)

- Markdown; `# aider chat started at <local time>` opens a session, `#### <prompt>` lines are user turns, `> Model: <name> ...` names the model, and `> Tokens: 2.8k sent, 27 received. Cost: $0.0029 message, $0.0029 session.` follows each response. `sent` includes any cached prefix (aider reports cache hits separately only in the terminal), so `cache_read` is 0 here.

## Kimi Code CLI (`~/.kimi/sessions/<wd-hash>/<session>/wire.jsonl`, older `~/.kimi-code/...`)

- Wire events; `StatusUpdate` records carry `token_usage` (`input_other`, `input_cache_read`, `input_cache_creation`, `output`) or camel-case `usage`. Only turn-scoped records are counted; session-scoped ones are cumulative.

## Mistral Vibe (`~/.vibe/logs/session/<id>/meta.json`, `messages.jsonl`)

- `meta.json.stats` holds `session_prompt_tokens`, `session_completion_tokens`, `session_cost`; there is no per-message usage, so each session becomes one event with `granularity: session`.

## Continue (`~/.continue/dev_data/<schema>/tokensGenerated.jsonl`)

- One event per line: `timestamp`, `sessionId`, `model`, `provider`, `promptTokens`, `generatedTokens`.

## pi and OpenClaw (`~/.pi/agent/sessions/--<cwd>--/*.jsonl`, `<config>/agents/*/sessions/*.jsonl`)

- Same shape: `session` header (`cwd`), `model_change` (`provider`, `modelId`), `message` entries whose assistant `message.usage` is `{input, output, cacheRead, cacheWrite, totalTokens, cost:{total}}`. OpenClaw checkpoint files replay the parent and are de-duplicated on (id, timestamp).

## Generic sniffer (`--generic-root <tool>=<dir>`)

- Walks every `.json` / `.jsonl` under the root and emits one event per object that has an input-like and an output-like key under `usage`, `token_usage`, `tokens`, `tokenUsage`, `usageMetadata` or `llm_metrics`, taking the nearest `model`, timestamp and `cost` seen above it. Recognised keys: input `input_tokens|inputTokens|prompt_tokens|promptTokens|input|input_other|promptTokenCount`; output `output_tokens|outputTokens|completion_tokens|completionTokens|generatedTokens|output|candidatesTokenCount`; cache read `cache_read_input_tokens|cached_input_tokens|cacheRead|cache_read|input_cache_read|cachedContentTokenCount|cached`; cache write `cache_creation_input_tokens|cacheWrite|cache_write|input_cache_creation|cacheWrites`. When both `input_tokens` and `cached_input_tokens` are present the input is treated as inclusive (OpenAI style). Events are marked `granularity: generic`; verify on two files before quoting them.

## Normalised event schema (output of `scan`)

`tool, host, ts, date, session, model, input_uncached, cache_read, cache_write, cache_write_5m, cache_write_1h, output, reasoning, total, cwd, project, kind (main|subagent), parent, entrypoint, version, effort, plan, credits, limit_id, archived, request_id, src` — then `report` adds `api_cost_usd, cost_if_uncached_usd, cache_savings_usd, priced_as, account, billing, account_confidence`.

## mini-SWE-agent (explicit `--mini-swe-root`)

`mini-swe-agent-1.1` trajectories keep successful Chat usage in
`messages[].extra.response.usage`, Responses API usage in the response message's
own `usage`, and rejected-action usage in the `FormatError` message's
`extra.response.usage`. Do not sum `info.model_stats` with per-response records.
The optional `mini-swe-agent-usage-1` exporter stores only allowlisted usage and
provenance before pricing can fail. Its embedded `extra.mini_swe_usage` snapshot
takes precedence over raw response usage, which the pinned Portkey adapter can
mutate during cost calculation.

Missing prices never discard tokens. Missing totals are labeled component sums;
malformed totals never reconstruct prompt tokens by subtraction. Reasoning is
already in output. Provider/model-scoped response IDs (or export UUIDs) deduplicate
trajectory/export overlap and repeated ingestion; no-ID legacy records have
explicitly weaker path-scoped guarantees. Generic sniffing excludes both mini
formats so it cannot bypass consent or duplicate the dedicated parser.

See [mini-SWE-agent integration](mini-swe-agent.md) for the backend/version matrix,
complete category mappings, partial-data flags, concurrency, failure paths,
privacy, and reconciliation commands.

## Goose native SQLite (schema 17)

`goose_roots` selects the dedicated reader, not generic JSON sniffing. The audited
Goose 1.54.0 source persists immutable `usage_ledger` rows with `id`, `session_id`,
`created_timestamp` (UTC seconds), `model`, nullable `input_tokens`, `output_tokens`,
`total_tokens`, `cache_read_tokens`, `cache_write_tokens`, `cost`, `cost_source`
and `is_compaction`. Input includes both cache categories. Output is not increased
by an invented reasoning count. Native currency, cache TTL, provider request ID
and reasoning breakdown are unavailable. Historical provider is only a labelled
unique-message-usage inference; the current session provider is never substituted.

Class A native records, Class B `accumulated_*`/legacy/carried-forward counters and
Class C snapshot-priced API estimates remain separate. Exports do not contain
the immutable native ledger and are not billable input. Repeated scans reuse
identities; growing sessions contribute only new usage rows. The bounded legacy
JSONL first header is coverage-only, not a guessed final-session total or delta.
See [Goose field mappings, versions, exclusions and privacy](goose.md).
