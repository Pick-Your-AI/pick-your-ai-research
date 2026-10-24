# ClawHub Publishing

This repository is prepared for ClawHub publishing as a text-based OpenClaw skill bundle.

## Included In ClawHub

The ClawHub bundle is intended to include text-based skill material only:

- `SKILL.md`, `README.md`, `QUALITY.md`, and this file
- `agents/openai.yaml`
- `pyproject.toml`
- `.github/workflows/quality.yml`
- `scripts/*.py` and `tests/*.py`
- `references/` catalogs and format notes
- `templates/` JSON manifests, pricing sheet, account and report-config examples
- `examples/` text inputs and README placeholders
- `assets/diagrams/*.mmd`

The rendered demonstration artefacts under `assets/examples/` (branded with the CompleteTech preset) stay on GitHub and are excluded from the registry bundle, so the published skill carries no publisher identity in its outputs.

## Excluded From ClawHub

`.clawhubignore` excludes binary and generated assets from the publish candidate, including PDFs, PNG previews, DOCX files, fonts, logos, `preview/`, `output/`, caches, virtual environments, local env files, temporary files, and generated `scans/`, `compiled/` and `reports/` working directories.

Those files remain part of the GitHub repository for brand presentation, examples, local demos, and generated artifact previews. They are not part of the ClawHub text bundle.

## License And Brand Boundary

ClawHub publishes skills under MIT-0. The text/code bundle can be used under ClawHub's publishing terms, but CompleteTech LLC names, logos, seals, and other brand assets remain reserved. Publishing this text bundle does not grant a trademark or brand-asset license and does not relicense excluded binary brand assets.

## Runtime Dependencies

Runtime requirements are declared in `SKILL.md` under `metadata.openclaw`.

- The pipeline itself needs only `python3` (standard library).
- `pyyaml` is declared so the included quality validator can parse YAML metadata.
- `ruff` is a development-time dependency for the validator, not a runtime requirement.

## Data Boundary

The skill reads agent transcripts and credential files on the user's own machines to identify accounts. It decodes identity claims only and never copies, prints, or transmits tokens. Publishing the skill bundle never includes any scanned data; `scans/`, `compiled/` and `reports/` are excluded.

## Security Audit Response

ClawHub's audit of 1.5.0 reported shell command injection through the report output directory (`os.system` sort), through unquoted SSH manifest fields, and through the scheduler's free-form extra arguments, plus unescaped branding in generated HTML and external Google Fonts requests. 1.5.1 replaces the shell sort with a Python merge sort, validates and quotes every remote command word, removes free-form scheduler arguments, escapes and validates branding, inlines all resources with a Content-Security-Policy, warns on group- or world-writable configuration, and adds `tests/test_security.py` to the quality gate.

The audit of 1.5.1 asked for neutral default branding, containment and remote-command hardening in the raw-log archive, and owner-only permissions for the ledger's private files. 1.5.2 makes the default brand neutral with presets applied only on explicit request (and `run` refusing to start unconfigured), validates archive host names, source paths and destinations with realpath containment, replaces the remote heredoc scripts with fixed commands reading NUL-delimited lists, creates the ledger home and its files 0700 / 0600, refuses group- or world-writable configs, keeps `accounts.json` out of study packages unless requested, and excludes the branded example artefacts from the registry bundle.

The audit of 1.5.4 flagged credential-file access and retention of e-mails and organisation names. 1.5.5 makes credential reads an explicit onboarding opt-in preceded by a warning that names the files and fields, keeps only the claims needed for attribution and pricing (pseudonymous account ids and plan types unless identifiable output is requested), drops the credential object immediately after extraction, labels packages that carry account metadata with `SENSITIVITY.md`, and adds `ledger.py publish-check` as a pre-publication identity scan.

The audit of 1.5.5 classified the optional scheduled task as cross-session persistence (T06). 1.5.6 separates it from onboarding entirely (no configuration key can register it), requires a typed confirmation or an operator-written consent record tied to a hash of the exact configuration (wrapper, schedule, hosts, roots, flags), demands a second acknowledgement for high-impact schedules (raw-log archive, SSH, WSL, other profiles), discloses everything including storage impact and the removal command before asking, warns about entries it will replace, and adds an optional expiry after which the scheduled run removes itself.

Codex's review of the 1.5.6 branch added: scheduled runs pinned to the consented manifest and flags (`run --scheduled`), DOCX and PDF inspected by `publish-check` (or reported unscannable), legacy credential-derived `accounts.json` redrafted under the recorded preference, placeholder accounts billed as unknown rather than subscription, report and dashboard narrative reflecting how accounts were drafted, `SHA256SUMS` covering optional package files, short host and organisation names still checked, and the scheduler lookup deferred until after consent.

The audit of 1.5.7 (one A.I.G warning, 26 SkillSpector findings) was split into issues #11 to #20 and resolved in 1.5.8: `study_url` validated to HTTPS and rendered through DOM APIs; prompt text capture an explicit opt-in (default off); the generic JSON sniffer refuses broad roots and skips credential-like files; narrowed trigger phrases and a Before You Start disclosure; authorization and minimisation boundaries in the discovery guide and templates; a sensitivity notice in every study package with paths redacted from `ledger.json` unless requested; private permissions for every generated run file; no catch-all attribution rules (unmatched calls are reported as unattributed); subprocess and data text cleaned before printing; one credential-file predicate applied to every archive path including legacy rows; WSL discovery default off; SSH transfers disclosed explicitly.

The audit of 1.5.11 (one A.I.G. warning, 156 SkillSpector findings) reported that sensitive scan and report artifacts inherited potentially permissive filesystem permissions. 1.5.12 creates every scan, compiled, report, package, dashboard and document output owner-only: directories 0700 and files 0600 from the moment they are created (via `safety.private_open` / `safety.private_copy`), repairs the mode of pre-existing files opened with truncation, tightens the pipeline working directory, stages SSH scans in a 0700 remote directory that is removed in a `finally` block after retrieval, ships `safety.py` beside the scanner on the remote host, and adds a permissive-umask regression check to `tests/test_security.py` covering the scan, compiled, package, dashboard and archive outputs.

## Local Readiness Check

Run before publishing:

```bash
python3 scripts/validate_quality.py
```

The validator checks lint, Python compilation, structured-file parsing, Mermaid rendering, smoke tests, the parser fixture suite, and ClawHub bundle readiness. It does not publish to ClawHub.

## Publishing

Do not publish automatically. Use the ClawHub CLI only after explicit approval and an authenticated owner context, for example:

```bash
clawhub skill publish . --owner <owner> --version <semver>
```
