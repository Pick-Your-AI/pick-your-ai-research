---
name: ai-usage-ledger
description: >-
  Compile every locally recorded AI coding-agent model call (Claude Code, Codex CLI/Desktop, GitHub Copilot CLI, Gemini CLI, opencode, OpenClaw, Cline/Roo/Kilo, aider, Kimi Code, Mistral Vibe, Continue, pi, Codebuff and any JSON-logging tool) across the operator's own profile and, when enabled, other drives, user profiles, WSL distros and named SSH hosts into one append-only, de-duplicated ledger stored as SQLite, JSON or CSV; price it at list API rates; split it by subscription account and billing plan; validate it against the tools' own counters; and render a branded light/dark dashboard plus a research-grade study package. Onboards once (branding, theme, storage backend, scheduled refresh, anonymised publication copy; hosts and accounts auto-detected per OS), remembers the preferences, refreshes with one command or on a schedule, renders fifteen ledger documents (statements, memos, briefs, billing evidence) as Markdown, HTML, PDF and DOCX, can anonymise everything for publication, optionally archives the raw log files themselves so they outlive the tools' retention, and answers detailed questions (per day, project, account, model or session, and inside prompt text or the archived logs when those opt-ins are on) through a query layer over the accumulated store. Disclosure: this skill reads agent transcripts and tool databases on this machine and on hosts the operator names, keeps a durable local ledger under ~/.ai-usage-ledger and the chosen working directory, and captures prompt text or credential-derived account claims only when the operator opts in. Use when asked to "find all my AI logs", "how many tokens did I use", "what would this have cost on the API", "compare my subscriptions", "usage by account", "cache savings", "set up my usage ledger", "monthly usage statement", "publish my usage anonymously", or to refresh an existing ledger.
version: 1.6.0
metadata:
  openclaw:
    skillKey: ai-usage-ledger
    homepage: https://github.com/CompleteTech-LLC/ai-usage-ledger-skill
    requires:
      bins:
        - python3
    install:
      - kind: uv
        package: pyyaml==6.0.3
---

# AI Usage Ledger Skill

## Purpose

| Use | Scope |
|---|---|
| Usage ledger | Locate, de-duplicate, price and attribute every locally recorded AI coding-agent call on a person's machines. |
| Starting point | Any request to count tokens, estimate API-equivalent cost, compare subscriptions, or break usage down by account, model, project or time. |
| Operating boundary | Read-only over the tools' directories; credential files are opened only when the operator opts in, for identity claims never credentials, minimised to pseudonymous ids and plan types unless identifiable output is requested; nothing is transmitted. Prompt text (what the operator typed to each agent) is recorded only when `prompts.capture` is `y`; by default the ledger holds counts, tokens, models and costs and never the words. The ledger store is append-only: nothing already stored is edited or removed. |

## Before You Start

Relay this table to the operator, in chat or on the terminal, before the first onboarding (`ledger.py init`) and again whenever one of the opt-ins below is about to be switched on. Do not run `init` until the operator has seen it. It does not replace the separate typed consent that `schedule install` collects.

| Topic | What the operator must hear |
|---|---|
| What will be read | Agent transcripts, session logs and tool databases in the operator's own profile for every supported harness (`~/.claude`, `~/.codex`, `~/.copilot`, IDE `globalStorage`, and the roots in `references/harness-catalog.md`), plus the tools' own counters (`state_5.sqlite`, `stats-cache.json`). Nothing is modified or deleted; nothing needs elevation; `detect_hosts.py` lists every root before the first run and prints what it could not read. |
| What is retained and where | A durable, append-only ledger of per-call records (timestamps, models, token counts, prices, host, project path, session id, pseudonymous account) in `~/.ai-usage-ledger/` (or `$AI_USAGE_LEDGER_HOME`, owner-only): `config.json`, the store, `manifest.json`, `accounts.json`, `pricing.json`, `report_config.json`, `anonymize-map.json`, `logs/`; and the generated `scans/`, `compiled/`, `reports/`, `documents/` and `anonymized/` trees under the chosen working directory. Nothing is transmitted; no network access is used. |
| Opt-in: prompt text | `prompts.capture` (default off). Off, the ledger stores counts and metadata only; on, the prompt and history text is kept in the store so `query prompts` can search it. |
| Opt-in: credential files | `accounts.from_credentials` (default off). On, `auth.json`, `.claude.json` and `.credentials.json` are opened for account id prefixes and plan types only, after a warning that names each file and field; tokens and keys are never kept or printed. |
| Opt-in: identifiable accounts | `accounts.identifiable` (default off). On, e-mails and organisation names are kept; otherwise accounts are pseudonymous (`codex:<8-char prefix>`, `claude:<8-char hash>`). |
| Opt-in: raw-log archive | `archive.raw_logs` (default off). On, every source file the scanners read is copied to `~/.ai-usage-ledger/archive/` (about the size of the tools' log trees, one tenth compressed) so it outlives the tools' retention and `query logs` can search it. |
| Opt-in: other profiles and drives | `detect.all_profiles` (default off). On, every `Users\<name>` / `/home/<name>` / `/Users/<name>` on every mounted drive is scanned; only profiles the operator owns or is authorised to audit, see `references/discovery.md` Boundaries. |
| Opt-in: WSL distros | `detect.wsl` (default off). On, `wsl.exe -l -q` lists the distros and each `/home/<name>` inside them is scanned. |
| Opt-in: SSH hosts | Only hosts the operator names at the prompt or in `config.json` `extra_hosts`. For each such host the skill uploads `compile_ai_logs.py` with `scp`, runs it there over `ssh`, and downloads the scan output (events, sessions, prompts if captured, inventory) and, when configured, copies of `state_5.sqlite` / `stats-cache.json` and, with the raw-log archive on, the transcript files themselves. Nothing else crosses the network. |
| Opt-in: scheduled refresh | Never registered by onboarding or by a configuration key; only `schedule install`, which prints the full disclosure and needs a typed `yes` (and `yes, I understand` for high-impact schedules) from the operator, not from the agent. |
| Leaving the machine | Apart from the SSH transfers above, nothing leaves through this skill and no service is contacted. For anything to be shared, build the anonymised copy (`run --anonymize`, `doc --anonymize`) and run `ledger.py publish-check <dir>` on it first. |
| Coverage limits | Detection reports the roots it found and the same-volume duplicates it skipped; a directory it could not read or a tool it does not know is not listed. Compare each host's inventory (`files`, `bytes` per root) with a native count when completeness matters (see `references/pitfalls.md` 17). |
| How to remove everything | `python3 scripts/ledger.py schedule remove` (if a schedule exists), then delete `~/.ai-usage-ledger/` (or `$AI_USAGE_LEDGER_HOME`) and the generated directories under the working directory. `python3 scripts/ledger.py reinit` starts over with a fresh configuration and keeps the previous store beside the new one with a timestamp. If `archive.path` was set outside the ledger home, delete that directory too: the skill only ever uses a dedicated archive directory (it refuses one that already holds other files and marks its own with `.ai-usage-ledger-archive`), so nothing else lives there. |

## System Boundary

| Boundary | Use |
|---|---|
| This skill | Discovery, scanning, de-duplication, pricing, account attribution, validation, dashboard and study rendering. |
| Provider consoles and exports | Invoices and billed amounts. This skill produces API-equivalents at list price, not invoices. |
| `agentic-invoice-skill` | Billing a client for agentic work; feed it verified figures from the ledger. |
| `agentic-security-review-skill` | Questions about what the transcripts contain or who may read them. |
| Vendor usage dashboards (Codex app, Cursor, Windsurf, Copilot) | Their own counters; several include replayed history or omit tokens, see `references/harness-catalog.md`. |

## Core Workflow

| Step | Action |
|---|---|
| 1 | First use only: onboard. Reports are unbranded until the operator chooses branding: answer the first prompt (`none`, or a named preset such as `completetech`), pass `--brand-preset <name>`, or set `brand.*` values; unattended `init --yes` stays neutral and `run` refuses to start without a config. On a terminal run `python3 scripts/ledger.py init` and answer the prompts. From an agent harness, ask the operator the same questions in chat (brand name, eyebrow, tagline, contact, logo, accent colour, theme, storage backend, working directory, timezone, whether to include other profiles / drives / WSL, whether to build an anonymised copy on every run, whether to archive the raw log files themselves (and compress them), and the preferred refresh schedule: none / daily / weekly / monthly, time, weekday), then run `python3 scripts/ledger.py init --yes --set key=value ...`. Preferences persist in `~/.ai-usage-ledger/config.json` and in the store; later runs never ask again. Onboarding never registers a scheduled task: that takes `schedule install`, which the operator confirms themselves after reading its disclosure. |
| 2 | Onboarding auto-detects hosts and roots for this OS (`scripts/detect_hosts.py`: Windows, macOS, Linux, every WSL distro, other user profiles and drives, VS Code-family global storage, `CODEX_HOME`-style overrides) and drafts `accounts.json`: placeholders per host by default, or from credential claims when the operator answers yes to reading credential files (ask them explicitly; the tool warns which files it opens), pseudonymous unless they also ask for identifiable output. Review the draft: labels, prices, and the `why` on each rule. Add SSH hosts when prompted or in `config.json` `extra_hosts`. Record what could not be read and why. |
| 3 | Run `python3 scripts/ledger.py run`. It rescans, archives the raw files when `archive.raw_logs` is on, appends only new calls to the store (stable ids; duplicates are skipped), rebuilds the tables, dashboard and study package, and records the run. Repeat as often as wanted. |
| 4 | Validate per the checks below; fix a rule and run `python3 scripts/ledger.py run --no-scan` to rebuild from the store without rescanning. |
| 5 | Deliver the dashboard, the study package and `all_events.csv` (or `ledger.py export`), with exclusions and low-confidence rules stated. For a statement, memo or brief, pick a template from `references/ledger-document-catalog.md` and render it with `python3 scripts/ledger.py doc --template <id> --var prepared_for=... [--pdf --docx]`. For anything leaving the organisation, use the anonymised copy (`ledger.py run --anonymize`, then `doc --anonymize`) and check the outputs for names before publishing. |
| 6 | To start over (new brand, different backend, changed hosts) run `python3 scripts/ledger.py reinit`; the previous store is kept beside the new one with a timestamp. The manual route (`run_pipeline.py` with a hand-written manifest) still works for one-off or unattended use. |
| 7 | When the operator asks a specific question ("how many tokens on Tuesday", "which project cost the most in August", "when did I first use gpt-6", "what did I ask about rate limits"), answer it from the store with `python3 scripts/ledger.py query <preset> [filters]` per the Answering Detailed Questions table, not from the summary tables; go into the archived raw logs (`query logs`) when the answer is in the transcript rather than the counts. |
| 8 | For a report output covering "since midnight" or another exact interval, use `python3 scripts/ledger.py report --since today --tz <operator-zone>`. It filters stored events before pricing and rendering, shows the cutoff and latest recorded activity, and writes a separate HTML/data package. Use `--pricing <reviewed-snapshot>` for a report-only price override. See [scoped reports](references/scoped-reports.md) for timestamp boundaries, pricing provenance and freshness. |

| Required Fact | Examples |
|---|---|
| Hosts and roots | Every `~/.claude`, `~/.codex`, IDE `globalStorage`, gateway `sessions/` directory, with size and date range. |
| Accounts | Placeholders per host unless `accounts.from_credentials` is on; then the `chatgpt_account_id` prefix and plan type from each `auth.json` and the tier from each `.claude.json`, with e-mails and organisation names only under `accounts.identifiable`. |
| Prices | List rates per model on the snapshot date, with `assumed` rows named. |
| Exclusions | Locked directories, closed SSH ports, tools without token fields. |

## Validation Checks

| Check | Requirement |
|---|---|
| Replay proof | One spawned Codex thread's burst equals the parent's first N events value for value and was skipped; a small `codex_replay_skipped` on a host with sub-agents means the rule is not firing. |
| Counter cross-check | Non-forked Codex threads within 2% of `state_5.sqlite`; spawned children explained; Claude `stats-cache.json` ≥ transcript figure. |
| Plan field | Codex calls mostly `pro`/`plus`, some `self_serve_business_usage_based` where a prepaid org exists, `?` only for old clients. |
| Generic rows | Anything with `granularity: generic` verified against two source files as per-call, not cumulative. |
| Magnitude | Median Codex context per call 100 to 200K tokens; hundreds of billions per month on one subscription is a replay bug. |
| Fixtures | `python3 tests/make_fixtures.py` prints `ALL OK` and `python3 tests/test_store.py` prints `STORE OK` before the first real run. |
| Append-only | A second `ledger.py run` straight after the first reports `added {"events": 0, ...}`; a host that adds events on every run without new activity is being counted twice (check `detect_hosts.py` notes for same-volume profiles). |
| Anonymised outputs | Before publishing, grep the anonymised `compiled/` tree and any rendered document for host names, user names, e-mails and directory names from the private map (`~/.ai-usage-ledger/anonymize-map.json`); the test suite does this on fixtures, the operator does it on real data. |
| Documents | Every ledger placeholder in a rendered document is filled; a leftover `{name}` is either a `--var` the template needs (recipient, contract, correction values) or a bug. |

## Quality Rules

| Rule | Requirement |
|---|---|
| Read-only | Never modify, delete or "clean up" agent directories; do not `wsl --shutdown` while agents run. |
| Secrets | Credential files are read only with `accounts.from_credentials`; a warning names each file and the fields taken before it is opened; only the claims needed for attribution and pricing are kept and the credential object is dropped immediately; tokens and API keys are never printed or copied. E-mails and organisation names are retained only with `accounts.identifiable`, otherwise accounts are pseudonymous (`codex:<8-char id prefix>`, `claude:<8-char hash>`). |
| Publication | `accounts.json` is owner-only and separate from the store; it enters a study package only with `package_accounts: true`, which also writes `SENSITIVITY.md`. Run `python3 scripts/ledger.py publish-check <dir>` on anything leaving the machine: it reports e-mail addresses, account identifiers, organisation names, host names and credential-file references. |
| Evidence classes | Keep class A (per-call records), class B (tool counters) and class C (priced estimates) apart in every table. |
| Confidence | Every finding and every attribution rule carries a confidence level and its evidence. |
| Unknowns | Price unpublished models at a stated sibling marked `assumed`; report the share of cost that rests on them. |
| Corrections | When a rerun changes a previously reported figure, state the cause alongside the new number. |
| Trusted input | `manifest.json`, `config.json`, `accounts.json`, `pricing.json` and `report_config.json` are executable configuration: they name hosts to reach over SSH or WSL and text to render. Keep them owner-writable only (the scripts warn otherwise) and never populate them from untrusted content. |
| No shells | Local commands are argument lists (no `os.system`, no `shell=True`); remote SSH and WSL command words are validated against a strict grammar (`safety.py`) and quoted; the CSV merge sort is Python, not `sort`. |
| Rendering | Branding text is HTML-escaped; colours, theme tokens and fonts are validated; the logo must be a local file (inlined as a data URI); `extra_css` needs `unsafe_extra_css: true` and may not contain `</`, `@import` or `url(`. |
| Private files | The ledger home, store, archive, logs and their files are created owner-only (0700 / 0600 on POSIX; the profile ACL on Windows) and repaired when found otherwise; a config that others can edit is refused unless `AI_USAGE_LEDGER_ALLOW_SHARED=1`. `accounts.json` is copied into a study package only with `package_accounts: true`. |

## Resource Guide

| Resource | Role |
|---|---|
| `references/harness-catalog.md` | Forty-plus agents, IDE assistants, gateways and runtimes: paths per OS, record shapes, token fields, scanner support. |
| `references/log-formats.md` | Exact fields per built-in parser, de-duplication and replay rules, normalised schema. |
| `references/discovery.md` | Where logs and credentials live, sweep commands, reading accounts safely, defensible attribution rules. |
| `references/pitfalls.md` | Seventeen ways the numbers go wrong. |
| `references/harnesses.md` | Install locations and notes for Claude Code, Codex, Cursor, SSH, WSL and macOS. |
| `references/ledger-document-catalog.md` | Fifteen ledger documents (executive summary, monthly statement, quarterly review, account statement, subscription memo and renewal recommendation, cache brief, budget forecast, project allocation, billing evidence, model mix, tool adoption, host inventory, data-quality note, correction notice) with their placeholders. |
| `references/template-index.json` | Machine-readable index of the catalog used by the renderer. |
| `templates/` | Manifest, pricing sheet, account and report-config examples. |
| `examples/` | A workstation manifest and the CompleteTech brand preset. |
| `scripts/ledger.py` | Daily entry point: `init` (onboarding), `run` (scan, append, rebuild), `status`, `export`, `reinit`. |
| `scripts/scoped_report.py` | Exact-interval HTML report, token and dollar breakdowns, pricing evidence and event export; reached through `ledger.py report`, with no source scan or configuration changes. |
| `scripts/detect_hosts.py` | OS-aware discovery of harness roots, profiles, drives, WSL distros and credential claims; prints or emits manifest hosts and an accounts draft. |
| `scripts/ledger_store.py` | Append-only store with SQLite, JSON (JSONL) and CSV backends, stable event ids, prefs and run history, exports. |
| `scripts/run_pipeline.py` | One command: scan every host, merge, analyse, render, zip (used by `ledger.py`, also usable alone). |
| `scripts/render_ledger_doc.py` | `--list` the catalog or `--template <id>` to fill it from the ledger: Markdown and themed HTML always, `--pdf`, `--docx`, `--png` when the optional libraries are installed; `--anonymize` reads the anonymised copy. |
| `scripts/render_pdf.py` | Branded Markdown to PDF / DOCX (letterhead band, logo, accent tables, footer). |
| `scripts/anonymize.py` | Salted pseudonyms for hosts, sessions, projects and accounts; paths, prompts and identities removed; private map kept beside the store. |
| `scripts/schedule.py` | Task Scheduler (Windows) or crontab (Linux, WSL, macOS) entry that runs `ledger.py run` daily, weekly or monthly through a wrapper that logs to `~/.ai-usage-ledger/logs/run.log`. |
| `scripts/ledger_archive.py` | Raw-log archive: copies every source file the scanners read (any tool, any host kind) into `~/.ai-usage-ledger/archive/<host>/...`, gzip by default, with an index; `status`, `list`, `grep`, `restore`. |
| `scripts/ledger_query.py` | Question layer: thirty presets (totals, by day / week / month / tool / host / model / project / account / plan / kind / entrypoint / hour / weekday / effort / version, sessions, one session, raw calls, biggest calls, cache, first-last, prompts, prompt counts), free SQL, and regex search inside the archived logs; filters by date range, tool, host, account, model, project, session, kind, plan, billing; table / csv / json / jsonl output. |
| `scripts/compile_ai_logs.py` | `scan` (14 parsers plus a generic sniffer) and `report` (merge, price, attribute). |
| `scripts/analyze_events.py` | Distributions, time of day, concentration, validation, sensitivity. |
| `scripts/build_dashboard.py`, `scripts/build_report.py` | Branded dashboard and study package. |
| `tests/make_fixtures.py` | Synthetic logs and totals check for every parser. |
| `tests/make_onboarding_example.py`, `assets/examples/example-onboarding.md` | The onboarding, question by question, on a synthetic machine; show it to an operator before asking the questions in chat. |
| `tests/test_store.py` | Every backend ingests once and skips the repeat; non-interactive onboarding; two `ledger.py run`s end with zero new rows and archive every source file exactly once; the anonymised copy holds no fixture host, path or e-mail; schedule dry-runs; presets, SQL, prompt search and archived-log search return the expected rows; all fifteen documents render with no ledger placeholder left. |
| `tests/test_security.py` | Shell syntax in the output directory, SSH and WSL manifest fields, the scheduler wrapper and branding stays literal or is refused; generated pages carry a CSP and no external references. |
| `scripts/safety.py` | The validation and escaping helpers the pipeline, renderers and scheduler share. |

## Runtime Permissions

| Capability | Boundary |
|---|---|
| Files read | Agent transcripts, tool databases and credential files under the user's own profiles and hosts named in the manifest; prompt-only history files (Claude Code and Codex `history.jsonl`) only when `prompts.capture` is on; bundled templates, references and `assets/logo.png`. A `generic_roots` entry is read only when it names one tool's own directory (a home, drive root, `AppData`, `.config`, `Documents` or similar is refused) and credential-looking files below it (`auth.json`, `*token*`, `*.pem`, `.env*` ...) are skipped and counted in the inventory. |
| Files written | `~/.ai-usage-ledger/` (or `$AI_USAGE_LEDGER_HOME`): `config.json`, the store, generated `manifest.json`, `accounts.json`, `pricing.json`, `report_config.json`, `anonymize-map.json`, `run-ledger.cmd|sh`, `logs/`, and `archive/` when raw-log archiving is on (size of the tools' log trees, roughly one tenth when compressed); `scans/`, `compiled/`, `store-export/`, `reports/`, `anonymized/` and `documents/` under the chosen `workdir`; `tests/fixtures`, `tests/out` during the test suites. |
| Local commands | `python3` for the scripts; `wsl.exe -l -q` to list distros during detection; `wsl.exe`, `ssh` and `scp` only for hosts in the manifest; `schtasks` or `crontab` only when the operator asks for a scheduled refresh (`schedule install|remove`), never silently. |
| Not required | Outbound network access (pricing pages are fetched by the operator, not the scripts), credential use, persistence, privilege escalation, destructive file operations, background services. |

## Renderer

| Task | Command |
|---|---|
| Onboard (interactive) | `python3 scripts/ledger.py init` |
| Onboard (agent or CI, no prompts) | `python3 scripts/ledger.py init --yes --set brand.name=Acme --set store.kind=sqlite --set detect.all_profiles=y` |
| Refresh everything | `python3 scripts/ledger.py run` |
| Rebuild without rescanning | `python3 scripts/ledger.py run --no-scan` |
| Scan a subset of hosts | `python3 scripts/ledger.py run --hosts lighthouse,wsl-ubuntu` |
| What is configured and stored | `python3 scripts/ledger.py status` |
| Export the store | `python3 scripts/ledger.py export --table events --format csv --out events.csv` (`json`, `jsonl`; tables `events`, `sessions`, `prompts`) |
| Start over | `python3 scripts/ledger.py reinit` |
| Identity scan before sharing | `python3 scripts/ledger.py publish-check <package, directory, zip, DOCX or PDF> [--term extra]` (exit 1 on findings; a PDF needs `pypdf`, otherwise it is reported as unscannable rather than approved) |
| Anonymised copy for publication | `python3 scripts/ledger.py run --anonymize` (or `--set anonymize.on_every_run=y` at onboarding); outputs under `<workdir>/anonymized/`; `ledger.py export --anonymize` for tables |
| List ledger documents | `python3 scripts/ledger.py doc --list [--stage finance] [--type memo]` |
| Render a document | `python3 scripts/ledger.py doc --template monthly-usage-statement --var prepared_for="Finance" --var month=2026-08 --pdf --docx` |
| Render from the anonymised copy | `python3 scripts/ledger.py doc --template executive-summary --anonymize --pdf` |
| Scheduled refresh | `python3 scripts/ledger.py schedule install --frequency daily --time 03:00 [--expires YYYY-MM-DD]` (disclosure, then typed confirmation or a matching `schedule-consent.json`) · `schedule consent` (prints the consent record for a terminal-less operator) · `schedule status` · `schedule remove` (`--dry-run` shows everything without registering; the wrapper carries `--anonymize` / `--archive` / `--until` at most, nothing free-form) |
| Raw-log archive | `python3 scripts/ledger.py archive status` · `archive list --host wsl-ubuntu --grep-path 2026/08` · `archive grep "ECONNRESET" --since 2026-08-01` · `archive restore --host lighthouse --to /tmp/restored --match sessions/2026/08` · one-off: `ledger.py run --archive` |
| Detailed questions | `python3 scripts/ledger.py query --presets` · `query totals --since 2026-08-01` · `query by-project --tool codex --since 2026-08-01 --until 2026-08-31 --limit 10` · `query sessions --project libreevolve` · `query session --session <id>` · `query prompts --grep "rate limit"` · `query sql "SELECT ..."` · `query logs "pattern" --since 2026-08-01` |
| Just look at what is on this machine | `python3 scripts/detect_hosts.py --all-profiles` (`--json` for the manifest shape) |
| Manual pipeline (no store) | `python3 scripts/run_pipeline.py --manifest manifest.json [--only report,analyze,build] [--hosts a,b]` |
| Parser, store and security self-tests | `python3 tests/make_fixtures.py` · `python3 tests/test_store.py` · `python3 tests/test_security.py` |
| Quality gate | `python3 scripts/validate_quality.py` |

| Preference key (`--set`) | Values |
|---|---|
| `brand.name`, `brand.eyebrow`, `brand.tagline`, `brand.contact`, `brand.logo`, `brand.accent`, `brand.footer` | Free text; the logo is a local PNG/SVG path, inlined as a data URI (a URL is used only with `allow_external_resources: true`); accent is hex. |
| `theme` | `light`, `dark`, `system` (initial theme of both pages; the viewer's toggle still wins). |
| `store.kind` | `sqlite` (one file, indexed), `json` (JSONL files plus id index), `csv` (CSV files plus id index). |
| `workdir`, `timezone` | Paths and IANA zone. |
| `detect.all_profiles`, `detect.wsl` | `y` / `n`. |
| `anonymize.on_every_run` | `y` / `n`: also build `<workdir>/anonymized/` on every run. |
| `prompts.capture` | `y` / `n` (default `n`): store the text of typed prompts so `query prompts` / `prompt-count` can search it. Off, the scanners run with `--no-prompts`: no `prompts.<host>.jsonl` is written, prompt-only history files are not opened, the store's `prompts` table stays empty and those queries say so. |
| `accounts.from_credentials`, `accounts.identifiable` | `y` / `n`: read credential files for account ids and plans (default `n`: per-host placeholders to fill in); keep e-mails and organisation names (default `n`: pseudonymous ids). |
| `archive.raw_logs`, `archive.compress`, `archive.path` | `y` / `n` keep the raw log files; `y` / `n` gzip them (`n` keeps them re-scannable in place); directory (default `~/.ai-usage-ledger/archive`). |
| `schedule.frequency`, `schedule.time`, `schedule.weekday`, `schedule.expires` | `none` / `daily` / `weekly` / `monthly`; `HH:MM`; `mon`..`sun`; optional `YYYY-MM-DD` after which the scheduled run removes itself. Preferences only: nothing is registered until `schedule install` is confirmed. |

| Output | Path |
|---|---|
| Ledger store (source of truth after the first run) | `~/.ai-usage-ledger/ledger.sqlite`, or `ledger-json/`, `ledger-csv/` (tables `events`, `sessions`, `prompts`, `prefs`, `runs`) |
| Event log (primary artefact) | `compiled/all_events.csv` |
| Aggregates | `compiled/by_*.csv`, `subscription_vs_api*.csv`, `SUMMARY.md`, `summary.json`, `analysis.json` |
| Dashboard | `compiled/agent-ledger.html` |
| Study package | `reports/<prefix>_<date>/` (`USAGE_REPORT.md`, `report.html`, `ledger.json`, `pricing.json`, `accounts.json`, `README.md`, `SENSITIVITY.md`, `SHA256SUMS`) and `.zip` |

## Branding and Themes

| Element | Source |
|---|---|
| Default | Neutral: the name "Usage Ledger", an accent colour and a footer saying branding has not been configured. No publisher name, contact, logo or slogan appears unless chosen. |
| Brand preset | `examples/report_config.completetech.json`, applied only on explicit request (`init --brand-preset completetech`, the first onboarding prompt, or `--set brand.preset=completetech`): CompleteTech LLC logo, eyebrow, tagline, contact, footer and palette (`#1E3A8A` accent, `#0F172A` ink, `#EEF2FF` soft accent, `#64748B` muted, `#E2E8F0` border, `#F8FAFC` zebra). |
| Logo | `assets/logo.png`, inlined as a data URI so both pages stay self-contained. |
| Themes | Light, dark and system in both pages via `prefers-color-scheme`, a fixed Light / System / Dark toggle persisted in the browser, and an explicit `data-theme` stamp from a host. |
| Overrides | `branding.light` / `branding.dark` may set any token (`bg`, `surface`, `surface-2`, `ink`, `ink-2`, `ink-3`, `line`, `line-2`, tool colours, `seq1..seq7`) to a plain CSS colour or length; `font_display` / `font_body` / `font_mono` name locally installed fonts; `google_fonts_url` is honoured only with `allow_external_resources: true`; `extra_css` only with `unsafe_extra_css: true`. Keep tool colours CVD-safe. |

## Store and De-duplication

| Element | Rule |
|---|---|
| Event id | Tool request id when the tool records one (Claude message id); otherwise SHA-1 of tool, host, session, source file name, timestamp, model, the four token counts and an ordinal among identical keys in that file. Re-scanning an append-only log yields the same ids. |
| Ingest | `INSERT OR IGNORE` (SQLite) or an id index (JSON, CSV). Rows are never updated or deleted; a changed rule is applied at report time, not in the store. |
| Sessions and prompts | Same scheme keyed on tool, host, session and file (sessions) or timestamp, session and text (prompts). |
| Prefs and runs | Every preference is mirrored into the store; each `run` records what it added, skipped and produced. |
| Reinit | Moves the store aside as `<store>.before-reinit-<stamp>` and onboards again; nothing is deleted. |

## Anonymisation

| Element | Rule |
|---|---|
| Replaced | Host names to `host-<6 hex>`, session and request ids to 12-hex digests, working directories to `project-<8 hex>`, account keys to `<tool>:acct-<6 hex>`, any path, URL or e-mail in a free-text field to `path-`/`user-` tokens. |
| Removed | Source file paths, prompts, account labels, e-mails, organisations, evidence strings, host descriptions and the primary-host note in the report config. |
| Kept | Tool, model, plan type, timestamps, token counts, costs, kind, entrypoint kind, version, effort: the study itself. |
| Stability | Pseudonyms are SHA-256 of a private salt generated at onboarding, so reruns agree and outsiders cannot reverse them; the real-to-pseudonym map stays in `~/.ai-usage-ledger/anonymize-map.json`. |
| Branding | The publisher's own branding stays on anonymised outputs; change it at onboarding if the publisher differs from the operator. |

## Raw-Log Archive

| Element | Rule |
|---|---|
| What is kept | Every file a scanner read on the last run (the `src` of each event, the `file` of each session), plus the counters beside the roots (`stats-cache.json`, `state_5.sqlite`, `history.jsonl`, `session-store.db`). Credential files are never archived. |
| Harness-agnostic | The archive follows the scanners' source paths, so a new parser or a generic-root tool is archived without any archive-side change; nothing in the archive knows tool formats. |
| Hosts | Local and share hosts by copy; WSL through the `\\wsl$` share; SSH hosts through fixed remote commands (`xargs -0 stat`, `tar --null -T -`) that read a NUL-delimited file list on stdin after the target passed `safety.validate_ssh_host`; no remote shell script is ever composed from paths. |
| Boundaries | Host names are plain identifiers; every source path (from the scan output, which is data) must be absolute with no control characters and no `..`; every destination is verified to stay inside the archive root after symlink resolution, on archive and on restore. |
| Append-only | A file is copied when new or grown; the tools only append, so the latest copy is a superset. The index keeps a version count and nothing is deleted. |
| Reading back | `archive grep` streams through gzip and reports file, line and the timestamp found on the line; `archive restore` decompresses a host (or a path match) into a directory that the scanners can read again. |
| Size | Expect the size of the tools' log trees (tens of GB for heavy Codex use) at roughly one tenth when compressed. Say so before enabling it on a small disk. |

## Answering Detailed Questions

| Question shape | Command |
|---|---|
| How much on a day / week / month, optionally one tool or host | `query by-day --since D --until D [--tool t] [--host h]`, `by-week`, `by-month`, `totals` |
| Report output since local midnight or between exact timestamps | `report --since today --tz America/New_York`, or `report --since <date-or-timestamp> --until <date-or-timestamp> --tz <zone> [--pricing <snapshot>]`; [scope and pricing details](references/scoped-reports.md) |
| Which projects, models, accounts, plans, entry points, effort levels, client versions | `query by-project`, `by-model`, `by-model-month`, `by-account`, `by-account-month`, `by-plan`, `by-entrypoint`, `by-effort`, `by-version` |
| Working pattern | `query by-hour`, `by-weekday`, `by-kind` (main vs sub-agents) |
| Biggest or specific sessions and calls | `query sessions [--project p]`, `session --session <id>`, `biggest-calls`, `calls --since D --until D --limit N` |
| Cache behaviour, first and last use | `query cache`, `first-last` |
| What was asked | `query prompts --grep "text" [--since D]`, `prompt-count` |
| Anything else about the counts | `query sql "SELECT ... FROM events|sessions|prompts"` (read-only; columns are the normalised event schema) |
| What the transcript actually said, errors, tool output | `query logs "regex" [--since D] [--host h] [--project path-fragment]` over the archived raw files (needs `archive.raw_logs`) |
| Output for a document or a spreadsheet | add `--format csv|json|jsonl` |

Accounts in `query` come from the same `accounts.json` rules the report uses (`acct()` / `bill()` SQL functions), so per-account answers agree with the dashboard. JSON and CSV stores are loaded into an in-memory SQLite database, so every preset works on every backend.

The `query --since/--until` flags filter stored calendar-date fields; they do not convert an intraday cutoff into the operator's timezone. Use `report` for timezone-aware report output. Reuse an existing fresh store when sufficient; if a refresh is needed, finish it within the approved source scope, then build the bounded report. A historical scan does not expand the report's time range.

Saved price files are persistent operator configuration and can lag the bundled template. Check each used model's exact row and verification date; missing models must remain marked as assumed or unpriced. A report-only `--pricing templates/pricing.json` uses the bundled snapshot without replacing saved prices. Keep API-equivalent estimates separate from actual charges, including any service-tier premiums or unrecorded usage categories.

## Ledger Documents

| Element | Rule |
|---|---|
| Source of figures | `compiled/summary.json` and `analysis.json` of the configured ledger (or `--compiled <dir>`); nothing is typed in by hand. |
| Recipient facts | `--var prepared_for=`, `reference=`, `notes=`, `contract_id=`, `billing_period=`, correction values. |
| Scopes | `--var month=YYYY-MM`, `--var account=<key>`, `--var project=<directory substring>`; defaults are the latest month, the largest account, the largest project. |
| Formats | Markdown and themed HTML always; PDF (reportlab) and DOCX (python-docx) with `--pdf` / `--docx`; PNG preview with `--png`. |
| Wording | Every document states that figures are API-equivalents at list price and not invoices; the billing evidence template feeds `agentic-invoice-skill`, it does not replace it. |

## Scheduling

| Element | Rule |
|---|---|
| Windows | `schtasks` task "AI Usage Ledger" running `~/.ai-usage-ledger/run-ledger.cmd` daily, weekly (`--weekday`) or monthly (day 1) at `--time`. |
| Linux, WSL, macOS | One crontab line tagged `# ai-usage-ledger` running `run-ledger.sh`; macOS may need Full Disk Access for cron. |
| Logging | Each run appends to `~/.ai-usage-ledger/logs/run.log`; `ledger.py status` shows the entry and the last log lines. |
| Consent | Onboarding never registers persistence, and no configuration key can. `schedule install` prints the disclosure (wrapper, schedule, every host and root it will read, archive and anonymise flags, output directories, storage used so far, the removal command) and then needs a typed `yes` on a terminal, plus `yes, I understand` when the schedule is high-impact (raw-log archive, SSH, WSL or other profiles). Without a terminal the operator writes `~/.ai-usage-ledger/schedule-consent.json` from `schedule consent` (approver, timestamp, hash of the exact configuration, high-impact acknowledgement); install refuses when the hash no longer matches. An agent must not write that file on the operator's behalf. |
| Expiry | `schedule install --expires YYYY-MM-DD` makes the scheduled run stop and remove the entry after that date; the saved schedule state is cleared when it does. |
| Pinned to the consent | The wrapper runs `ledger.py run --scheduled`: no host re-detection, and the run refuses if the manifest (hosts, roots), flags or schedule no longer hash to the consented configuration, so a scheduled run can never read something the operator did not review. |
| Existing entries | An existing task or cron line is reported before it is replaced. |

## Definitions

`input_uncached` fresh prompt tokens · `cache_read` served from cache · `cache_write` written to cache (Anthropic, split 5m/1h) · `output` incl. reasoning · `total` = sum. API-equivalent = tokens × list price. Cache saving = same call priced with all prompt tokens uncached, minus actual. Subscription months are counted only when that account made a call. Usage-based calls are real spend and stay out of the subscription comparison. Typed prompts = the operator's own messages; their text enters the store only under `prompts.capture=y`, otherwise the prompt count is 0 and `all_prompts.*` are empty.

## Network Boundary

| Boundary | Requirement |
|---|---|
| Local-only runtime | The scripts contact no service. The only network traffic is `ssh` / `scp` to hosts the operator names in the manifest: the scanner is uploaded, scan outputs (and, when configured, tool counters or archived transcripts) are downloaded. WSL distros are reached through `wsl.exe` or the `\\wsl$` share only when `detect.wsl` is on. |
| Generated pages | The dashboard, study and documents are self-contained: no external fonts, images or stylesheets, and a `Content-Security-Policy` meta tag that forbids network loads. A remote logo or Google Fonts stylesheet is used only when `branding.allow_external_resources` is true. |
| Publishing | Dashboards and study packages are published only when the operator asks (Artifacts, files, or a repository). |
| Data | Scanned transcripts and the compiled ledger never leave the operator's machines through this skill. |

## Goose native integration

For Goose, use `goose_roots` and the dedicated native collector described in
[the Goose guide](references/goose.md), not generic export totals. Observe normal
onboarding/profile consent. The audited source is 1.54.0 with session schema 17;
unknown schemas, carried-forward totals and legacy exports are coverage gaps,
not guessed per-call usage. Keep provider inference/unknowns and native cost
provenance separate from snapshot-priced API equivalents. Report inventory gaps
alongside the dashboard. The read-only reader stages a private temporary DB/WAL
copy (including raw transcript bytes) but retains only allowlisted usage metadata;
disclose that transient-copy caveat where relevant. Do not enable prompts,
credentials, other profiles, archives or schedules merely to validate it.
