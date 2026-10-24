# Start here: ai-usage-ledger

<p align="center"><img src="assets/logo.png" alt="CompleteTech LLC logo" width="260"></p>

**CompleteTech LLC Skills** — Usage evidence and cost attribution.

[Overview](README.md) · [Agent instructions](SKILL.md) · [Branding and handoffs](BRANDING.md) · [Contributing](CONTRIBUTING.md)

## 1. Choose the right skill

Use the ledger for recorded AI usage, attribution, list-price estimates and evidence packages. Its activation/install-directory key is **`ai-usage-ledger`**; the repository is `ai-usage-ledger-skill`. Install the whole skill directory, not only SKILL.md. Each agent product has its own discovery directory; use that product's documented installation mechanism.

## 2. Prepare a full checkout

Python 3.12 is the shared CI baseline. The core ledger, fixture workflow and package checks use the standard library; installing optional PDF/DOCX libraries is not necessary for the first demonstration.

```bash
git clone https://github.com/CompleteTech-LLC/ai-usage-ledger-skill.git ai-usage-ledger
cd ai-usage-ledger
python3 -m venv .venv
. .venv/bin/activate
python scripts/validate_package.py
```

On Windows PowerShell, create the environment with `py -3 -m venv .venv` and use `.\.venv\Scripts\python.exe` instead of `python`; activation is optional. Do not change machine execution policy. A text-only registry package can omit binary logos/previews; these checkout checks require the full GitHub sources.

## 3. Run the fixture demonstration

```bash
python tests/make_fixtures.py
python scripts/run_pipeline.py --manifest examples/manifest.fixtures.json
```

The first command should print `ALL OK`. The manifest uses synthetic local roots and writes under `tests/out/pipeline`; open the artifacts printed by the pipeline and inspect totals, coverage, identity and layout. Re-running can replace prior fixture outputs. This does not initialize the personal ledger, discover personal credentials, contact SSH hosts or register schedules. Do not replace the fixture manifest with real sources during this demonstration.

## 4. Start real onboarding separately

Before `ledger.py init`, relay the complete **Before You Start** table in [SKILL.md](SKILL.md). Confirm what will be read, retained, where it will be stored and which optional capabilities are approved. Then follow its existing `init` / `run` / `status` workflow. Review detected roots and account-attribution rules before trusting the first report. The initial scope is the operator's own profile; other profiles/drives, WSL and named SSH hosts require their corresponding opt-ins and authorization.

Prompt text, credential-file identity claims, identifiable accounts and raw-log archiving default off. Do not enable them merely because the library is installed. Scheduling is a separate `schedule install` operation requiring operator confirmation; choosing preferences or running package validation does not install a task.

## Branding and downstream use

Keep neutral branding unless an approved identity is selected. Use the existing `--brand-preset completetech` onboarding option or [CompleteTech report configuration](examples/report_config.completetech.json) for authorized company output. Optional PDF/DOCX generation uses [requirements.txt](requirements.txt). Do not synthesize logos, fetch fonts or redistribute private assets.

Follow [BRANDING.md](BRANDING.md) when handing artifacts to another skill. Preserve observed evidence, estimates, exclusions, price snapshot, confidence, artifact version, brand choices and approval status. A ledger estimate is not an invoice or authority to bill.

## Safety, network and troubleshooting

Treat manifests and configurations as trusted operator-controlled input. Named SSH hosts use SSH/SCP transfers; they are not authorized by installing the package. Browser resource fetching can occur only when the operator explicitly enables external resources in the existing renderer settings. The fixture workflow does neither.

For missing modules, use the same interpreter for `python -m pip` and execution, and install only the dependencies needed for the intended operation. Missing assets usually indicate a partial checkout or wrong working directory. Run from the skill root. Keep real logs, keys, account maps, archives and generated personal reports out of Git.

## Verify changes

```bash
python -m unittest discover -s tests -p 'test_package_*.py' -v
python scripts/validate_package.py
python scripts/validate_quality.py
```

Package tests are structural and use synthetic fixtures; the original Quality gate has additional development dependencies and specialist tests. Follow [CONTRIBUTING.md](CONTRIBUTING.md). Neither structural checks nor successful rendering certify visual quality, complete source coverage, billing facts or permission to share data.
