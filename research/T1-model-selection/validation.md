# T1 validation evidence

This file records actual checks of this contribution. Preparation and automation do not verify vendor truth, account access, independent performance, source reuse rights, owner acceptance or merge.

## Broad-family and retrospective citations: 2026-10-17

The earlier contribution is now traced in [the citation audit](citation-audit-2026-10-17.md) and [123-cell market citation index](../market/citation-index-2026-10-17.md). Historical access dates are retained. The broader research adds 248 candidate records across six comparison tables, with 189 primary source groups, 237 distinct URLs across 38 domains and 55 overlapping task tags. These are corpus counts, not a global census or 248 independently pinned deployable models.

Current-main integration was recorded at `d1c8b7f877a4a814c2456d2c9a89c439fe6643ab`. The additive source-register conflict preserved both the new GPUs.io observation and main's CanIRun repository correction. Frozen `contracts/v1` files are unchanged.

Executed with `.venv/bin/python` (Python 3.12) from the repository root:

| Check | Actual result |
| --- | --- |
| `python -m pip install -r requirements-research.txt` | Exit 0; pinned requirements already installed |
| `python -m unittest discover -s contracts/v1/tests -v` | Exit 0; 21 tests passed at the integrated head |
| `python -m unittest discover -s tests -v` | Exit 0; 24 tests passed at the integrated head |
| `python scripts/validate_research.py` | Exit 0; 30 catalog proposals / 2 pricebooks plus external evidence metadata |
| `python scripts/validate_market_research.py` | Exit 0; 33 entities / 1,584 cells / 20 issues |
| Additional JSON/table/reference checks after factual corrections | 248 unique records; all source IDs resolve; all 248 table rows match the inventory; zero broken local T1 document links; source and task counts above |
| `git diff --check` | Exit 0 |

An independent read-only artifact review at `d1c8b7f` reran the suites/validators, reconciled all table and market citation mappings and checked primary-source samples. It requested two factual corrections: Grok 1.5 variants had inherited older-route editing/clip input, and six Qwen rows blurred text/multimodal vectors with rerank relevance. Both are corrected in JSON and Markdown against B37/P49–P54. Main-session source review also removed the unsupported Whisper turbo translation tag against W01, and removed unrelated legacy-retirement boilerplate from newer audio rows. The earlier review is not an approval of a later revision.

A correction gate at `af2ed75` found that the JSON task-tag edit had matched Whisper large-v3 instead of turbo. The named records were corrected explicitly: large-v3 retains translation, turbo has speech recognition only. A stronger final comparison checks every table column, complete task-tag lists and exact source links for all 248 rows, plus explicit Grok/Whisper variant assertions; it passes. Earlier partial-field assertions were insufficient for this mismatch and are superseded by that full comparison. The 21+24 tests and both validators also passed at `af2ed75`; they do not check these documentary task semantics.

The normal submission validator does not ingest the new research-only inventory; its separate assertions check structure and mapping. Neither check establishes source truth for every claim, legal sufficiency, freshness, account access, runtime performance or consumer acceptance. No paid API, inference/GPU, scientific or robot experiment was performed. Missing Biome LSP was not installed after the user's prior decline. Contract and receiving-owner reviews remain in [the handoff ledger](handoffs.md); this checkpoint uses `Refs`, not issue closure.

## Central-review follow-up: 2026-10-17

Applied the five corrections requested in the [central owner's PR #88 review at `dbfa7dd`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868). The read-only GitHub API response confirms review ID `5554964868`, reviewer `tynamite`, reviewed commit `dbfa7dd13a7f732bff0653ae6ab45f55b2782f20` and submitted time 2026-10-17T00:07:36Z. #75's shared-family disposition and #81's proposed W-R10/D-R2a/b were read separately; the latter was pinned at `9786ef6f9a7942b21a3cc51a05df741360e3594f`. This is documentation reconciliation, with no generated contract, catalog fact or price change and no production evaluator added.

Executed from the follow-up worktree with bundled Python **3.12.14** at `C:/Users/Stew1/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. The parent session completed `python -m pip install -r requirements-research.txt` against the same requirements before these checks; no additional bundled-package changes were made for this follow-up.

| Check | Actual result |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | Exit 0; **21 tests passed** |
| `python -m unittest discover -s tests -v` | Exit 0; **24 tests passed**; normal temp-file access used because the session sandbox blocks temporary-file creation |
| `python scripts/validate_research.py` | Exit 0; **30 catalog proposals and 2 pricebooks**, plus external evidence metadata |
| `python scripts/validate_market_research.py` | Exit 0; **32 entities, 1,536 cells, 20 issues** |
| `git diff --check` | Exit 0 |

The contract tests include the unchanged v1 behavior; passing them does not implement or approve these proposed rule changes. Structural validation checks import/generator integrity, schemas, canonical coverage, references, provenance shape/date ordering and market integrity. It does not verify remote source truth, reuse rights, measurements, contract migration or receiving-owner acceptance. No fresh vendor research or inference/GPU/training experiment was performed. The [handoff ledger](handoffs.md) keeps the changed-revision review, #30 license sufficiency, #10 KV agreement, other consumer dispositions, #36 quality protocol and #39/#40 versioned semantics pending. The prior execution record below is historical.

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
