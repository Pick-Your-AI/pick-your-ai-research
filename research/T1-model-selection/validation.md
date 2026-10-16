# T1 validation evidence

This file records actual checks of this contribution. Preparation and automation do not verify vendor truth, account access, independent performance, source reuse rights, owner acceptance or merge.

## Environment

Python **3.12.12**, local ignored `.venv`. `python -m pip install -r requirements-research.txt` completed successfully under that environment. Frozen import files are not changed. JSON LSP is unavailable because Biome is not installed and installation was previously declined; repository schema validation is the applicable structural check.

## Execution log

Executed on the prepared T1 contribution with `.venv/bin/python` (Python 3.12.12):

| Check | Actual result |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | Exit 0; **21 tests passed** |
| `python -m unittest discover -s tests -v` | Exit 0; **11 tests passed** |
| `python scripts/validate_research.py` | Exit 0; **26 catalog proposals and 2 Pricebooks**, including existing T2 records and the new 10 T1 records/one Pricebook |
| `git diff --check` | Exit 0 |
| Read-only Markdown/path and acceptance audit (Node standard-library assertions) | Exit 0; **12 Markdown files, 146 resolving local links, 41 exact criterion rows** |
| Synthetic context examples | Shared cap: 700+200 <=1000 passes; 900+200 fails; output201 >200 fails |
| Price threshold examples | 272000 selects short; 272001 selects long; eight conditioned rates and all vendor provenance unverified |

These arithmetic checks exercise the documented examples, not a new production evaluator. No market files are present on this branch, so its market validator is not claimed; the separately based #49 contribution runs that validator against its actual proposal data.

## Research surface and limitations

Primary source pages and immutable Qwen config/license were opened. No inference API call, GPU benchmark, fine-tune or deployment was run. Counter APIs are documented methods, not exercised. The rule files' examples are synthetic arithmetic, never evidence of model quality or real hardware fit.

The [41-row criterion map](acceptance-matrix.md) and [handoff ledger](handoffs.md) keep prepared content separate from unsatisfied reviews, merge and closure. #41's live owner policy is linked in [evidence.md](evidence.md); vendor-only provenance stays unverified. Final diff/source self-review and a separate skeptical artifact pass precede PR handoff; remote CI and actual review dispositions are recorded after publication. All existing frozen-contract/import checks passed; no new Python application code or test was added.
