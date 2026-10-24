# Running this skill from different harnesses

The scripts are plain Python 3.8+ with no dependencies, so any agent that can run a shell command can drive them. What differs between harnesses is where the skill lives, how it is invoked, and how the result is delivered.

## Install locations

| Harness | Skill directory | Notes |
|---|---|---|
| Claude Code | `~/.claude/skills/ai-usage-ledger/` (user) or `<repo>/.claude/skills/ai-usage-ledger/` (project) | Invoked with `/ai-usage-ledger` or automatically when the description matches. |
| Codex | `~/.codex/skills/ai-usage-ledger/` | Codex reads `SKILL.md` frontmatter; scripts are run through its shell tool. Use the WSL copy of `~/.codex` if Codex runs inside WSL. |
| Cursor / Cline / Continue / Windsurf | `~/.cursor/skills/`, `~/.cline/skills/`, `~/.continue/skills/` | Same layout; the agent reads `SKILL.md` as instructions. |
| Any (Skills CLI) | `npx skills add <path or repo>` | Installs into every harness it detects. |
| No agent at all | anywhere | `python scripts/run_pipeline.py --manifest manifest.json` |

Copy the whole folder (SKILL.md, scripts/, templates/, references/); the scripts locate each other relative to `scripts/`.

## Claude Code

- Long scans: run `run_pipeline.py` in the background (`run_in_background`) and poll the `scans/<host>/inventory.<host>.json` file; a scan of a 90 GB Codex tree takes 8 to 10 minutes on NVMe.
- Publishing: the dashboard (`compiled/agent-ledger.html`) and the study (`reports/<pkg>/report.html`) are self-contained single files that publish directly as Artifacts; give them stable names and republish to the same path to keep the link.
- Before the first publish, glance at the rendered page once; the JS is syntax-checked with `node --check` on the extracted script if node is available.

## Codex

- Codex's shell tool runs commands in the workspace; point `--manifest` at a file in the workspace and keep `workdir` there so outputs are visible to the user.
- When Codex itself is the tool being measured, its current rollout is still open; the scanner reads it fine but the last few calls will be missing until the session ends.
- Codex Desktop shows token totals that include replayed history (see pitfalls); do not "correct" the de-duplicated figures to match it.

## Remote and mixed hosts

- SSH hosts: `kind: ssh` copies the scanner with `scp`, runs it with the remote `python3`, and copies the results back. Only stdlib is needed remotely.
- WSL: `kind: wsl` runs inside the distro; set `share_fallback` so the pipeline can retry over `\\wsl$` if the WSL service refuses the background call.
- macOS: run the pipeline on the Mac (`kind: local`) or add it as `kind: ssh` after enabling Remote Login; without SSH it cannot be scanned from another machine.
- Old profile backups on other drives: `kind: share` with the backup's `.claude` / `.codex` paths.

## Delivering the result

Always hand over three things: the dated package zip (report, ledger.json, pricing, accounts, checksums), the dashboard HTML, and the event-level `all_events.csv`. State the snapshot date, the price date, which hosts were excluded and why, and which attribution rules are below high confidence.
