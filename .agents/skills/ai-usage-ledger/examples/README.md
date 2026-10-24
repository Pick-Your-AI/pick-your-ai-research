# Examples

Runnable example inputs for this skill.

- `manifest.workstation.json` — a Windows workstation with a WSL distro, a lab server over SSH, and an old-profile backup on another drive.
- `report_config.completetech.json` — the CompleteTech LLC brand preset (logo, palette, tagline, footer) for the dashboard and study; applied only when selected (`ledger.py init --brand-preset completetech`). Without a choice the pages are neutral.

Rendered demonstration artifacts live under `assets/examples/` (`example.md`, `example.html`, `example.png`) so README previews and packaged outputs stay close to the visual assets they reference. They were produced from synthetic fixtures (`tests/make_fixtures.py`), not from any real account.

Most people do not need these files: `python3 scripts/ledger.py init` detects the hosts and writes the manifest, accounts draft, pricing sheet and report config into `~/.ai-usage-ledger/`, and `python3 scripts/ledger.py run` refreshes the ledger from then on. `examples/config.example.json` shows what the saved preferences look like. `assets/examples/example-onboarding.md` is a full transcript of the questions and answers.

For a manual, store-less run copy the two files to a working directory, replace the `<you>` placeholders, add `pricing.json` and `accounts.json` from `templates/`, then:

```bash
python3 scripts/run_pipeline.py --manifest manifest.workstation.json
```

`manifest.fixtures.json` and `accounts.fixtures.json` drive the synthetic example in `assets/examples/`, including the executive-summary PDF and DOCX rendered from `references/ledger-document-catalog.md` with `scripts/render_ledger_doc.py`.
