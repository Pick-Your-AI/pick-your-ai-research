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

The [41-row criterion map](acceptance-matrix.md) and [handoff ledger](handoffs.md) keep prepared content separate from unsatisfied reviews, merge and closure. #41's live owner policy is linked in [evidence.md](evidence.md); vendor-only provenance stays unverified. A separate skeptical artifact pass approved partial PR publication at T1 `d31283a88d62027d2453827c05730efbe0e5e907` and matrix `870d6d87c555112fb782147589487e2c8421e4cf`; it independently reran both branches' suites/validators and spot-checked primary claims. Local audit report: `.omo/evidence/assigned-research-audit.md` (not part of the public PR). Two low wording findings were corrected in the following revision. Agreement citations/license_ref and browser-state updates are a separately reviewed follow-up delta. All frozen-contract/import checks passed; no new Python application code or test was added. These checks are not owner acceptance.

Follow-up skeptical audit at `9c04077547ed252fea584fdc333231e7cf55ddd5` approved partial publication, independently reran 21+11 tests and the 26-record/2-Pricebook validator, and checked the agreement/HF sources. Report: `.omo/evidence/assigned-research-delta-audit.md` (local). Its low Anthropic clause(a)/(b) wording ambiguity is corrected in the next progress commit. Main-session review of that small prose/tracking delta checks the exact cited clauses and actual PR/Project readbacks; it does not claim the earlier reviewer covered a newer SHA. No new model/schema/price fields changed in that delta.

Actual remote CI: [PR #88 initial head](https://github.com/Pick-Your-AI/pick-your-ai-research/actions/runs/38955418647) and [PR #87 matrix head](https://github.com/Pick-Your-AI/pick-your-ai-research/actions/runs/38955286861) completed SUCCESS. Final-head CI must be read from the current PR check after any push. Both PR reviewer lists contain the six affected owners; no submitted owner reviews or main merge is inferred.
