# Finding the logs and the accounts

## Boundaries

| Boundary | Rule |
|---|---|
| Whose data | Scan only profiles, drives, distros and hosts the operator owns or is explicitly authorised to audit. Another user's home (`C:\Users\<other>`, `/home/<other>`, `/Users/<other>`), a shared server's other accounts, or a container someone else runs are read only with that person's consent, recorded in the run notes; without it, leave the root out of the manifest and list it under exclusions. |
| Other profiles and drives, WSL | `detect.all_profiles` and `detect.wsl` are opt-ins the operator turns on at onboarding; the default is the operator's own profile on this machine. `--all-profiles` on `detect_hosts.py` is the same opt-in and needs the same authorisation. |
| SSH hosts | Only hosts the operator names (at the prompt or in `config.json` `extra_hosts`), with an account they already hold; the skill never discovers hosts, never widens a login and never escalates. |
| Credential files | `auth.json`, `.claude.json`, `.credentials.json` and saved auth snapshots are opened only under `accounts.from_credentials`; the default is per-host placeholders. When on, only identity claims (account id prefix, plan type, tier) are taken, tokens are never printed or copied, and e-mails and organisation names are kept only under `accounts.identifiable`. Minimised, pseudonymous ids are the default. |
| Prompt text | Transcript text is stored only under `prompts.capture` (default off) and copied only under `archive.raw_logs` (default off); the default ledger holds counts and metadata. |
| Escalation | Never `sudo`, never run as another user, never change permissions, never mount or copy a locked directory to get past an access error. A root that cannot be read as the current user is an exclusion: record the path, the reason and the date, and move on. |
| Outputs | Everything found stays on this machine. Before any output is shared, build the anonymised copy (`ledger.py run --anonymize`) and run `ledger.py publish-check <dir>` on it. |

`scripts/detect_hosts.py` does the routine part of this automatically and `ledger.py init` runs it during onboarding. Read on for what it looks for, what it cannot see, and how to check its output.

## What the detector covers

| Platform | Home directories | Extra locations |
|---|---|---|
| Windows | `%USERPROFILE%`; with `--all-profiles` every `<drive>:\Users\<name>` on every mounted drive | `%APPDATA%\{Code, Code - Insiders, VSCodium, Cursor, Windsurf, Trae, Kiro, Antigravity}\User\globalStorage` for Cline / Roo / Kilo; `%LOCALAPPDATA%` tools |
| WSL | every distro from `wsl.exe -l -q` (Docker distros skipped), every `/home/<name>` reached through `\\wsl$\<distro>` | `~/.vscode-server/data/User/globalStorage`, `~/.cursor-server/...` for remote-mode extensions; the distro path is written to the manifest with the share as `share_fallback` |
| macOS | `~`; with `--all-profiles` every `/Users/<name>` | `~/Library/Application Support/<editor>/User/globalStorage` |
| Linux | `~`; with `--all-profiles` every `/home/<name>` | `~/.config/<editor>/User/globalStorage`, `~/.vscode-server/...` |

Per home it checks, in order: `CODEX_HOME` or `~/.codex` (needs `sessions/` or `archived_sessions/`; `state_5.sqlite` noted), `~/.claude` (needs `projects/`; `stats-cache.json` noted), `COPILOT_HOME` or `~/.copilot/session-state`, `GEMINI_DATA_DIR` or `~/.gemini/tmp`, `QWEN_DATA_DIR` or `~/.qwen/history`, `KIMI_DATA_DIR` / `KIMI_SHARE_DIR` / `~/.kimi` / `~/.kimi-code`, `VIBE_HOME` or `~/.vibe/logs/session`, `~/.continue/dev_data`, `PI_AGENT_DIR` or `~/.pi/agent/sessions`, `OPENCODE_DATA_DIR` or `~/.local/share/opencode/opencode.db`, `OPENCLAW_DIR` or `~/.openclaw/agents`, the Cline family under each editor's global storage and `~/.cline`, and generic roots for Codebuff (`~/.config/manicode`), Droid (`~/.factory/sessions`), Amp, LM Studio, OpenHands, Grok, Hermes and Zcode. Environment overrides apply only to the profile the detector runs as.

Two profiles that resolve to the same directory (a mapped or `subst` drive letter, a bind mount, a symlinked home) are reported once; the note `same volume as an already detected profile` explains the skip. Without that rule every call would be stored twice under two host names.

What it does not do: read anything that needs elevation, follow SSH (name those hosts at the prompt or in `config.json` `extra_hosts`), or find gateway logs kept outside a home directory (`/srv`, `/opt`, containers). Use the sweep below for those and add them to the manifest by hand.

Within the Boundaries above, enumerate the operator's own profiles on every drive and host they are authorised to audit; the interesting material is often in an old profile backup or a second OS on the same box that belongs to the same person.

## Where each tool keeps usage

| Tool | Per-call records (class A) | Tool's own counter (class B) | Prompts | Credentials / account |
|---|---|---|---|---|
| Claude Code | `~/.claude/projects/**/*.jsonl` | `~/.claude/stats-cache.json` | `~/.claude/history.jsonl` | `~/.claude.json` (`oauthAccount.emailAddress`, `organizationRateLimitTier`), `~/.claude/.credentials.json` (`subscriptionType`, `rateLimitTier`) |
| Codex (CLI, Desktop, VS Code) | `~/.codex/sessions/**/rollout-*.jsonl`, `~/.codex/archived_sessions/` | `~/.codex/state_5.sqlite` | `~/.codex/history.jsonl` | `~/.codex/auth.json` (id_token claims), saved copies in `~/.codex-auths/`, registries like `libreevolve_auths.json`, `~/.codex/log/codex-login.log` (login timestamps only) |
| Copilot CLI | `~/.copilot/session-state/*/events.jsonl` | `~/.copilot/session-store.db` | in events | GitHub account |
| opencode | `~/.local/share/opencode/opencode.db` | same | same | `~/.local/share/opencode/auth.json` |
| OpenClaw | `<deploy>/config/agents/*/sessions/*.jsonl` | – | in sessions | provider API keys in the gateway env |
| Antigravity / Gemini | `~/.gemini/antigravity/conversations/*.db` (protobuf blobs, no token fields) | – | – | not usable |
| Cursor / Cline / Continue | usually only skills and settings | – | – | – |

`~` means each user profile: `C:\Users\<name>`, `/home/<name>`, `/Users/<name>`, plus WSL distros (`\\wsl$\<distro>\home\<name>`) and any backed-up profile on other drives.

## Sweep commands

Windows Git Bash / any POSIX shell (adjust roots):

```
for r in /c/Users/* /d /e /g; do
  find "$r" -maxdepth 7 \( -type d \( -name .claude -o -name .codex -o -name .copilot -o -name .gemini -o -name .opencode \) \
     -o -type f \( -name history.jsonl -o -name 'rollout-*.jsonl' -o -name stats-cache.json \) \) \
     -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
done
```

Then keep only `.claude` dirs that contain `projects/` and `.codex` dirs that contain `sessions/` (repos often carry `.claude/settings.json` or `.codex/config.toml` that hold no usage).

Extend the sweep with the other names from `harness-catalog.md`: dot-dirs `.gemini .qwen .kimi .kimi-code .vibe .continue .pi .factory .amp .grok .hermes .zcode .cline .cursor .codeium .kiro .lmstudio .ollama .openhands .aider*`; VS Code storage `*/User/globalStorage/{saoudrizwan.claude-dev,rooveterinaryinc.roo-cline,kilocode.kilo-code}` and `*/User/workspaceStorage/*/chatSessions`; app data `Cursor/User/globalStorage/state.vscdb`, `Zed/threads`, `JetBrains/*/workspace`, `~/.config/manicode`, `~/.local/share/{opencode,amp,kilo,goose,crush,zed}`; and files `.aider.chat.history.md`, `tokensGenerated.jsonl`, `wire.jsonl`, `ui_messages.json`, `chat-messages.json`, `sessions.db`, `state.db`, `grok.db`.

Inside WSL: `find ~ -maxdepth 5 -type d \( -name .claude -o -name .codex \)`; also check `~/.local/share` and `~/.config`.

Remote hosts over SSH: only on a host the operator has named and holds an account on, and only after they have confirmed they are authorised to audit it. Run the same `find` under that account's own home. Do not `ls /home` or read other users' homes, and do not open gateway or container session logs in `/srv`, `/opt`, `/var/lib` or under `podman ps` / `docker ps`, unless the operator confirms those services and containers are theirs (or their owner has consented) and the paths are readable as the login user. Never use `sudo`, `su`, a shared root key or a permission change to get past an access error: note the path and the reason, record it as excluded, and leave the root out of the manifest.

Size first: `du -sh` each candidate. Codex trees of tens of GB are normal; the scanner streams them but a WSL tree scanned over the `\\wsl$` share is roughly four times slower than scanning inside the distro.

## Reading accounts without exposing secrets

This is opt-in and minimised by default. `ledger.py init` drafts `accounts.json` with per-host placeholders unless the operator turns on `accounts.from_credentials`, in which case the tool warns which files and fields it will read and keeps only the identity claims below (account id prefix, plan type, tier), never the tokens; e-mails and organisation names are kept only under `accounts.identifiable`, otherwise accounts are pseudonymous (`codex:<8-char prefix>`, `claude:<8-char hash>`). `templates/accounts.example.json` shows the same opt-ins in the draft. The snippets here are for checking the draft by hand under those same opt-ins, on the operator's own credential files only.

Codex `auth.json` (do not print the tokens; decode claims only):

```python
import json, base64
d = json.load(open(path)); t = d.get("tokens", {}); tok = t.get("id_token") or t.get("access_token")
p = tok.split(".")[1]; p += "=" * (-len(p) % 4); c = json.loads(base64.urlsafe_b64decode(p))
auth = c.get("https://api.openai.com/auth", {}); prof = c.get("https://api.openai.com/profile", {})
identifiable = False  # set True only when accounts.identifiable is on; otherwise keep the check pseudonymous
print(auth.get("chatgpt_plan_type"), (auth.get("chatgpt_account_id") or "")[:8], d.get("last_refresh"))
if identifiable:
    print(prof.get("email"), [o.get("title") for o in auth.get("organizations", [])])
```

Claude: `~/.claude.json` → `oauthAccount.emailAddress`, `organizationType`, `organizationRateLimitTier`, `subscriptionCreatedAt`; `~/.claude/.credentials.json` → `claudeAiOauth.subscriptionType`, `rateLimitTier`.

Each distinct `chatgpt_account_id` (or Claude e-mail) is one account. The same account id under two e-mails is one account whose e-mail changed. Saved auth snapshots (e.g. `~/.codex-auths/*/auth.json` with `created_at` notes) tell you when a switch happened and for which project; login logs tell you when re-logins happened but not to which account.

## Attribution rules you can defend

1. A per-call plan stamp (`rate_limits.plan_type`) beats everything: usage-based calls are usage-based regardless of host.
2. A host whose profile has only ever held one login: that login, medium confidence (high if the auth file predates the first rollout).
3. A project directory tied to a saved auth switch from a known date: that account from that date.
4. Everything else on a host: the host's current login, medium confidence; note unexplained re-logins as a limitation.

Write each rule with its `why`; the report prints them.

## mini-SWE-agent: discovery is not source consent

The detector reports a disabled candidate for `last_mini_run.traj.json` under
`MSWEA_GLOBAL_CONFIG_DIR` or the platform's mini-SWE config directory. It does not
read `.env` or credentials and never automatically enables this source. Other
`agent.output_path` directories and usage exports must be explicitly selected.

Add approved paths as a host's `mini_swe_roots` in the existing `extra_hosts`
configuration (or use a reviewed manifest without rediscovery). The dedicated
`--mini-swe-root` flag accepts a trajectory file or a narrow directory of
`*.traj.json`, `*.usage.json`, and `*.usage.jsonl`. Source directories are not
recursively added to generic sniffing. Remove these roots or use the normal
skip-tool filter to disable collection; no scheduler is installed.

See [mini-SWE-agent integration](mini-swe-agent.md) for exact platform paths,
configuration, exporter opt-in, default-file overwrite limitations, and
verification commands.

## Goose native roots

The dedicated `goose_roots` manifest field and `--goose-root` scanner argument
accept an absolute session directory or database file, optionally
`namespace=/absolute/path`. Detection follows audited Goose 1.54.0 paths:
Linux and macOS use `$XDG_DATA_HOME/goose/sessions` or
`~/.local/share/goose/sessions`; Windows uses the roaming Known Folder at
`%APPDATA%\Block\goose\data\sessions`. An absolute `GOOSE_PATH_ROOT` wins
and yields `<root>/data/sessions`. The macOS strategy is XDG, not Apple app-data.

These named locations are checked only within the already approved profile scope.
Current-process overrides are not applied to other profiles. No binary is run,
credentials loaded, unrelated tree searched or schedule enabled. Existing
`--tools goose`/`--skip-tools goose` filtering works. Read the [Goose guide](goose.md)
before collection: the WAL-safe reader creates a private, transient raw database
snapshot while retaining only usage metadata, and older schemas/exports are
coverage-only. Namespace/host stability is required for deduplication.
