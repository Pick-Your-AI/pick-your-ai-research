# Muse integration verification

This is a fixture-based integration, not a live-provider or invoice audit. See
[the installation and consent guide](../../references/muse-mesh.md).

## Exact companion

- Muse base: `e537b757c112557f5256b3397523a6772d768697`.
- Companion commit prepared locally: `56cc31db555922dc92645c09b888984a65669c1a`.
- Resulting Muse tree: `a5f1f7da1673127e5f685f81c4ea7b7d257d3c68`.
- [Apply-ready patch](mu.patch.txt) SHA-256:
  `da5b76b047ad7ccc3cbd369b6de55d6dd587f1317f597cc66a96636197ab0655`.

An actual upstream branch-creation attempt returned HTTP 403, `Resource not
accessible by integration`. No Muse upstream PR or merge is claimed. Unmodified
stock Muse does not produce these events. The ledger CI applies and tests this
exact patch against the exact upstream base on every run.

## Reproducible checks

From the ledger checkout:

```bash
python -m unittest discover -s tests -p 'test_muse_usage.py' -v
python -m unittest discover -s tests -p 'test_ledger_mcp.py' -v
python -m unittest discover -s tests -p 'test_package_*.py' -v
python scripts/validate_package.py
python scripts/validate_quality.py
```

The first two suites contain 31 accounting/ingestion tests and 6 MCP tests after
the completion-status review correction. The existing Quality gate also requires
its documented development dependencies; do not skip or weaken it.

In a patched Muse checkout with the pinned dependencies installed:

```bash
pnpm exec tsc --project tsconfig.usage-ledger.json --noEmit
pnpm build
MU_LEDGER_REPO=/absolute/path/to/ai-usage-ledger-skill \
MU_LEDGER_EVIDENCE=/absolute/path/to/new-evidence.json \
PYTHON=python pnpm test:usage-ledger
```

With `MU_LEDGER_REPO` set, all 18 native tests and the end-to-end test must pass
with zero skips. The test isolates its HOME, workspace, configuration and logs.
The provider is a deterministic local HTTP fixture; no personal logs or model API
credentials are needed. Do not execute these tests against personal source data.

## Accounting receipt

The real Muse Agent, supported SDK fetch boundary, SQLite importer and Muse's
actual MCP client participate in the end-to-end test. The receipt establishes:

| Measurement | Expected |
| --- | ---: |
| First input tokens, including cached input | 100 |
| Cache-read subset of input | 40 |
| First output tokens | 20 |
| Reasoning subset of output | 5 |
| First total tokens | 120 |
| Fixture gateway-reported charge in USD | 0.015 |
| Separately calculated synthetic API-equivalent estimate in USD | 0.0003 |
| Rows added by native-response replay | 0 |
| Total after replay | 120 |
| Final recorded attempts, including a rate-limit failure | 7 |
| Final responses with measured usage | 6 |
| Final measured token total | 720 |

The test also executes memory extraction, the separate Web UI provider path,
compaction/reset and SDK retries. Its price rates are synthetic, not assertions
about current commercial prices. A gateway `usage.cost` field is reported
charge evidence, not proof of a paid invoice.

## Review correction

The initial code review identified that completion status changed pricing
eligibility without changing the conflict fingerprint. Commit
`4e6fa0f149bf8478331c2a59153e6e26121c2f34` binds both status and eligibility to that
fingerprint. The two added regression tests cover interrupted, failed and
cancelled records versus completed records in both arrival orders, both in a
first batch and after reopening a persisted store. They verify conflict rejection,
full rollback of unrelated new rows, preservation of original evidence and exact
replay idempotency. They do not silently rewrite previously recorded charges.

Local re-verification after this correction passed all 31 ingestion/accounting
checks and all 19 native/end-to-end checks. Local full Quality initially lacked
Ruff; the unchanged GitHub Quality workflow subsequently passed on `dc71e14`
before this correction. Check the current PR head's CI and review status rather
than treating earlier evidence as approval of later commits.

CI retains numeric receipts as `muse-e2e-python-3.12` and
`muse-e2e-python-3.13` artifacts. Required reviews and CI remain normal merge
prerequisites; this document is not a substitute for their results.
