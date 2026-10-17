# Validation record

Initial local validation on 2026-10-16, Python 3.12, against proposed contract revision `a222013c1f0106159132564d05e5d24666ad6342` from PR #44:

- `python -m pip install -r requirements-research.txt` — completed.
- `python -m unittest discover -s contracts/v1/tests -v` — 21 passed.
- `python -m unittest discover -s tests -v` — 11 passed.
- `python scripts/validate_research.py` — passed; zero catalog and pricebook proposals, intentionally.
- `python scripts/validate_market_research.py` — passed: 32 entities, 1,536 cells and 20 issues.
- `git diff --check` — passed.

Market validation checks identifiers, evidence references, matrix coverage, bounded statuses, issue paths, priority arithmetic and parent cycles. Existing validation checks frozen-contract integrity and proposal rules. Neither establishes truth, licensing permission, sufficient market demand, actual runtime capacity or reviewer acceptance. No independent benchmark was run and no customer interviews were conducted.

GitHub verification uses authenticated API readback, including filtered item queries for every view, assignments, parent relationships and metadata. The anonymous browser cannot display this private Project. Evidence limitations and failed website access are retained in the research notes.

The research is submitted for review; a passing check does not make any issue Done. PR #44 has since merged; the PR is rebased onto `main` (see below).

## Revalidation after rebase onto `main` — 2026-10-16

Rerun after rebasing onto `main` (#44 and #45 merged). Results are recorded in the PR description. These checks still do not verify market truth, rights, benchmark accuracy or owner acceptance.

## CanIRun.ai intake validation (2026-10-16)

Python 3.12: required dependencies satisfied; contract suite 21/21 and repository suite 24/24 passed. `scripts/validate_research.py` passed (30 catalog proposals, 2 pricebooks); `scripts/validate_market_research.py` passed (33 entities, 1,584 cells, 20 existing issues). `python -X utf8 prompts/market/validate_prompts.py` passed; UTF-8 mode avoids the Windows console's inability to print the existing arrow character. `git diff --check` passed.

These checks establish schema, reference, matrix and prompt integrity. CanIRun.ai scenario execution, recommendation accuracy, reuse rights and owner acceptance remain pending; see [the intake profile](../../research/market/competitors/canirun-ai.md). Historical counts above describe the initial validation, not the current inventory.
