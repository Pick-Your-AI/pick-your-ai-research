# Harness and runtime catalog

Where AI coding agents, IDE assistants, gateways and inference runtimes keep usage on disk, what each record carries, and how this skill reads it. Compiled 2026-09-09 from vendor docs, source trees and the aggregators listed at the end; verify any row on a sample before trusting it, and treat "verify" rows as leads, not facts.

Legend for the **Scanner** column: `built-in` = `compile_ai_logs.py` has a dedicated parser; `generic` = readable with `--generic-root` (usage-object sniffing, see log-formats.md); `session-level` = only per-session totals exist; `none` = no local token data (counts of chats only); `export` = usage must be exported from the vendor.

Generic sniffer boundary: `--generic-root <tool>=<dir>` reads every `.json` / `.jsonl` below `<dir>`, so `<dir>` must be the tool's own directory (`~/.config/manicode`, `~/.factory/sessions`, `~/.lmstudio/conversations`); a home directory, a drive root or a broad container such as `~`, `AppData`, `.config`, `.local/share` or `Documents` is refused by `safety.check_generic_root` before anything is opened. Files that look like credentials (`auth.json`, `*credential*`, `*token*`, `*secret*`, `*.pem`, `*.key`, `.env*`, anything under `.ssh`, `.aws` ...) are never opened; the inventory row for a sniffed root records how many were skipped (`credential_files_skipped`) and carries the note "generic usage sniffer; N credential-like files skipped; verify on a sample".

`~` is each user profile on each host (`C:\Users\<u>`, `/home/<u>`, `/Users/<u>`, WSL homes, old-profile backups). `$APPDATA` = `%APPDATA%` on Windows, `~/.config` on Linux, `~/Library/Application Support` on macOS.

## Terminal coding agents

| Tool | Where | Records | Token fields | Scanner |
|---|---|---|---|---|
| Claude Code / Claude Agent SDK | `~/.claude/projects/<cwd-slug>/<session>.jsonl`, `agent-*.jsonl`; counter `~/.claude/stats-cache.json`; prompts `~/.claude/history.jsonl` | one JSON per line; assistant lines carry `message.usage` | `input_tokens` (uncached), `cache_read_input_tokens`, `cache_creation_input_tokens` (+ `cache_creation.ephemeral_5m/1h_input_tokens`), `output_tokens`, `output_tokens_details.thinking_tokens` | built-in |
| Codex CLI / Codex Desktop / Codex VS Code | `${CODEX_HOME:-~/.codex}/sessions/YYYY/MM/DD/rollout-*.jsonl`, `archived_sessions/`; counter `state_5.sqlite`; prompts `history.jsonl` | `event_msg` / `token_count` events | `last_token_usage.{input_tokens (incl. cached), cached_input_tokens, output_tokens, reasoning_output_tokens}`; `rate_limits.plan_type` per call; replay on fork (see pitfalls) | built-in |
| GitHub Copilot CLI | `${COPILOT_HOME:-~/.copilot}/session-state/<id>/events.jsonl` | typed events | `session.shutdown.data.tokenDetails.{input,cache_read,cache_write,output}.tokenCount`; `assistant.message.outputTokens` | built-in |
| opencode | `${OPENCODE_DATA_DIR:-~/.local/share/opencode}/opencode.db` (older: `storage/message/*/*.json`) | SQLite `message.data` JSON | `tokens.{input,output,reasoning,cache.read,cache.write}`, `cost`, `modelID`, `providerID` | built-in |
| Gemini CLI | `${GEMINI_DATA_DIR:-~/.gemini/tmp}/<project_hash>/chats/session-*.json[l]`; sub-agents nested | JSON (older) or JSONL; header + `messages[]` | per `gemini` message: `tokens.{input,output,cached,thoughts,tool,total}`, `model`, `timestamp` | built-in |
| Kimi Code CLI | `~/.kimi/sessions/<wd-hash>/<session>/wire.jsonl` (+ `subagents/<id>/`), older `~/.kimi-code/sessions/<ws>/<session>/agents/<agent>/wire.jsonl`; `context.jsonl`, `state.json` | JSONL wire events | `StatusUpdate` records: `token_usage.{input_other, input_cache_read, input_cache_creation, output}` (or `usage.inputOther/...`); count turn-scoped records only, session-scoped ones are cumulative | built-in |
| Mistral Vibe | `${VIBE_HOME:-~/.vibe}/logs/session/<id>/meta.json` + `messages.jsonl`; sub-agents under `agents/` | JSON meta, JSONL messages | `meta.json.stats.{session_prompt_tokens, session_completion_tokens, session_cost}`, model config and prices; no per-message usage | built-in (session-level) |
| Continue (CLI + IDE) | `~/.continue/dev_data/<schema>/tokensGenerated.jsonl` (+ `chatInteraction`, `autocomplete`); sessions `~/.continue/sessions/*.json` | JSONL events | `model`, `provider`, `promptTokens`, `generatedTokens`, `timestamp`, `sessionId` | built-in |
| aider | `<repo>/.aider.chat.history.md`, `.aider.input.history` (repo root by default; `--chat-history-file`) | Markdown transcript | lines `> Tokens: 36,428 sent, 0 received. Cost: $0.11 message, $1.39 session.`; session headers `# aider chat started at ...`; model on `> Model: ...` lines | built-in |
| pi (pi-coding-agent) | `${PI_AGENT_DIR:-~/.pi/agent/sessions}/--<cwd>--/<ts>_<uuid>.jsonl` | JSONL tree (`id`, `parentId`) | assistant `message.usage` (input/output/cache/cost); `model_change` entries; compaction summaries carry usage | generic |
| Codebuff | `${CODEBUFF_DATA_DIR:-~/.config/manicode}/projects/<project>/chats/<chat>/chat-messages.json` | JSON | assistant `metadata.usage` / `metadata.codebuff.usage` (input, output, cache read/create), credits | generic |
| Factory Droid | `${DROID_SESSIONS_DIR:-~/.factory/sessions}` and `<project>/.factory/sessions/` | JSON/JSONL sessions | usage per message (verify) | generic |
| Amp (Sourcegraph) | `${AMP_DATA_DIR:-~/.local/share/amp}`; threads also sync to ampcode.com | JSON threads | usage per message (verify) | generic |
| mini-SWE-agent | Explicit `agent.output_path` (`*.traj.json`); default `last_mini_run.traj.json` in platformdirs config; optional private `*.usage.json` export | Per-response usage, including persisted FormatError evidence; pre-cost exporter for otherwise lost usage | Chat/Responses input/output, cache read/write, reasoning; separate source costs | built-in, explicit `mini_swe_roots` consent; [configuration and limits](mini-swe-agent.md) |
| Goose | Native `sessions/sessions.db`; Linux/macOS XDG, Windows roaming `Block/goose/data`, `GOOSE_PATH_ROOT` override | SQLite schema 17 (audited 1.54.0 source); legacy JSONL headers | Native usage rows: per-record model, inclusive input/output and cache subsets; qualified cost evidence; provider inference or unknown | dedicated `goose_roots`; stable IDs; counters/exports never additional billable events; [support and gaps](goose.md) |
| Crush (Charm) | `~/.local/share/crush` (`%LOCALAPPDATA%\crush`) SQLite; `crush stats` builds its own HTML | SQLite `sessions`, `messages` | prompt/completion tokens and cost per message (columns verify) | session-level (query) |
| Qwen Code | `${QWEN_DATA_DIR:-~/.qwen}/history/<project_hash>/` | Gemini-CLI-derived JSON | as Gemini CLI (verify) | generic |
| Grok Build CLI | `${GROK_HOME:-~/.grok}/grok.db` | SQLite sessions/transcripts | usage columns (verify) | session-level (query) |
| Hermes Agent | `${HERMES_HOME:-~/.hermes}/state.db` | SQLite | verify | session-level (query) |
| Kilo CLI | `${KILO_DATA_DIR:-~/.local/share/kilo}` | opencode-derived | as opencode (verify) | generic |
| ZCode | `${ZCODE_HOME:-~/.zcode}` | verify | verify | generic |
| OpenClaw gateways | `<config>/agents/<agent>/sessions/*.jsonl`; `${OPENCLAW_DIR:-~/.openclaw}` | JSONL | `message.usage.{input,output,cacheRead,cacheWrite,cost.total}`; checkpoint files replay | built-in |
| Plandex | server-side (self-host DB); `~/.plandex-home*` holds client state only | – | usage in the server's Postgres | export |
| Jules CLI / Devin CLI | cloud agents; Devin desktop keeps `~/.config/Devin/User/acp-events/` (`~/Library/Application Support/Devin/...`) | ACP event JSON | verify | generic |
| Warp agent mode | local conversation store (path undocumented; cloud sync optional) | – | none published | none |

## IDE extensions and editors

| Tool | Where | Records | Token fields | Scanner |
|---|---|---|---|---|
| Cline | `$APPDATA/Code/User/globalStorage/saoudrizwan.claude-dev/tasks/<task>/ui_messages.json`, `api_conversation_history.json`, `task_metadata.json`; `state/taskHistory.json` | JSON arrays | `ui_messages` entries with `say: "api_req_started"` whose `text` is JSON `{tokensIn, tokensOut, cacheWrites, cacheReads, cost}`; `ts` ms; `task_metadata.model_usage[]` | built-in |
| Roo Code | `.../globalStorage/rooveterinaryinc.roo-cline/tasks/<task>/` | same layout as Cline | same | built-in (same parser) |
| Kilo Code (extension) | `.../globalStorage/kilocode.kilo-code/tasks/<task>/` (`cline_messages.json` in some versions) | same layout | same | built-in (same parser) |
| Cline CLI | `~/.cline/` (verify) | Cline-format | same | built-in (point `--cline-root` at it) |
| Cursor | `$APPDATA/Cursor/User/globalStorage/state.vscdb` (`cursorDiskKV`: `composerData:*`, `bubbleId:*`), per-workspace `workspaceStorage/<hash>/state.vscdb`; `agent-transcripts/` | SQLite key-value JSON | conversation only; no reliable per-request token fields; usage is on cursor.com/settings | none (count only) |
| Cursor Agent CLI | `~/.cursor/` (verify) | verify | verify | generic |
| Windsurf / Cascade | `~/.codeium/windsurf/` (memories, settings); trajectories not exposed | – | none locally; usage on the Windsurf account page | none |
| VS Code Copilot Chat | `$APPDATA/Code/User/workspaceStorage/<hash>/chatSessions/*.json[l]` (kind 0/1/2 records) | JSON/JSONL | requests/responses, no token fields; Copilot premium-request usage is on github.com | none (count only) |
| Zed agent | macOS `~/Library/Application Support/Zed/threads/threads.db`; Linux `~/.local/share/zed/threads/`, Flatpak `~/.var/app/dev.zed.Zed/data/zed/threads/`; older `~/.config/zed/conversations/*.json` | SQLite / LMDB | token counts shown in UI; schema undocumented | none (verify) |
| JetBrains AI Assistant / Junie | `$APPDATA/JetBrains/<IDE>/workspace/*.xml`, `aia-task-history` event logs | XML | chats only; quota on the JetBrains account | none (count only) |
| Antigravity (Google) | `~/.gemini/antigravity*/conversations/*.db` (`ANTIGRAVITY_DATA_DIR`, `~/.config/antigravity`) | SQLite of protobuf blobs | none decodable without the proto | none (count only) |
| Trae | app data dir (undocumented; exporters exist) | – | none | none |
| Augment | cloud sessions | – | none locally | export |
| Sourcegraph Cody | VS Code local storage; export to JSON from the chat UI | JSON export | none | none |
| Kiro (IDE + CLI) | `~/.kiro/` local database; enterprise prompt logging to S3 | SQLite | context breakdown in UI; verify columns | session-level (query) |
| Claude desktop app, ChatGPT desktop, claude.ai, chatgpt.com | no local transcripts | – | – | export (account data export) |

## Gateways, proxies and inference runtimes

| Tool | Where | Records | Token fields | Scanner |
|---|---|---|---|---|
| LiteLLM proxy | its Postgres/SQLite: `LiteLLM_SpendLogs` | rows | `request_id`, `model`, `prompt_tokens`, `completion_tokens`, `spend`, `startTime`, `user`/`team`, `session_id` | query (documented in discovery.md) |
| OpenRouter | account Activity page / `GET /api/v1/generation` | CSV / API | tokens and cost per request | export |
| Vercel AI Gateway | dashboard | – | tokens/cost | export |
| Ollama | `server.log` (Linux `journalctl -u ollama`, macOS `~/.ollama/logs/server.log`, Windows `%LOCALAPPDATA%\Ollama\server.log`) | text log | GIN access lines only by default; `prompt_eval_count`/`eval_count` appear only with `OLLAMA_DEBUG_LOG_REQUESTS` or in API responses | none (client logs carry the counts) |
| LM Studio | `~/.lmstudio/conversations/*.json`; server logs in the app | JSON | per-message stats include token counts (structure unsupported by vendor) | generic |
| vLLM | Prometheus `/metrics` (`vllm:prompt_tokens_total`, `vllm:generation_tokens_total`, per-request histograms); INFO logs have request ids only | metrics | aggregate counters, not per request | export (scrape) |
| llama.cpp `llama-server` | `/metrics` with `--metrics` (`llamacpp:prompt_tokens_total`, `tokens_predicted_total`) | metrics | aggregate | export (scrape) |
| Amazon Bedrock | model invocation logging → CloudWatch Logs / S3 (`inputTokenCount`, `outputTokenCount` per call); CloudWatch metrics | JSON | per call | export |
| Google Vertex AI | request-response logging → BigQuery; audit logs | rows | per call (`usageMetadata`) | export |
| Azure OpenAI / Foundry | diagnostic settings → Log Analytics (`RequestResponse` logs) | rows | per call | export |
| Anthropic / OpenAI consoles | usage pages, Admin usage APIs | – | per key/day | export |

## Prior art worth knowing

- **ccusage** (Claude, Codex, OpenCode, Amp, Droid, Codebuff, Hermes, pi, Goose, OpenClaw, Kilo, Kimi, Qwen, Copilot CLI, Gemini CLI, Antigravity, Grok, ZCode) — the widest list of default directories and env overrides; per-day cost tables.
- **codeburn** (50+ providers incl. cline, roo-code, kilo-code, kiro, cursor, zed, crush, warp, devin, droid, mistral-vibe) — provider docs describe each local format; useful when a row above says "verify".
- **agent-history** (Claude Code, Codex, Gemini CLI, pi) — collects sessions across local, WSL, Windows and SSH homes; format notes per agent.
- **tokscale**, **ai-usage-monitor** — cross-agent token trackers with provider docs.

None of these de-duplicate Codex fork replay or attribute calls to accounts; that is what this skill adds.
