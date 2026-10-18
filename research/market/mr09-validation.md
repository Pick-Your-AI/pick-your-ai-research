# MR-09 validation and evidence-review record

Research date: 2026-10-16. Branch: `codex/mr09-feasibility-validation`. Base: PR #67 commit `075653aa4c0682c976ea9486d7d549d667118530`. Validation belongs to this submission; earlier #67/#75 results are historical inputs only.

## Estimator comparison validation — 2026-10-18

Branch `codex/issue61-estimator-comparisons`, base main
`b9694364b6f0a3d1e9c6b37189cc007778fc54bc`. This dated addendum covers the new
estimator runner, six llmfit outputs, ModelFit output, author-reported browser observation,
12 component pairs and updated decision notes. The final integration at main `2ecfa005a93b3944e6832bdb6a168d535e5efca6`
retains #251 GPU evidence unchanged and outside this estimator-pair set.
The full required suite and all validators were rerun after resolving the three
note conflicts; upstream tests account for the increased integrated count.
Historical validation below remains dated.

Used bundled Python **3.12.14**, Node **v25.9.0**, and the pinned external binary,
engine and metadata identities recorded in the comparison ledger. Ran the
workflow dependency installation with `-r requirements-research.txt --target
$TASK_VALIDATION_DEPS`; set PYTHONPATH to that existing isolated dependency
directory. Existing-target warnings did not replace or change installed packages.

| Command / check | Result |
| --- | --- |
| `python -m pip install -r requirements-research.txt --target $TASK_VALIDATION_DEPS` | Passed |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed |
| `python -m unittest discover -s tests -v` initially, `-q` after integration | 226 initially; 247 passed after integration, including eight new comparison eligibility/integrity tests |
| `python scripts/validate_research.py` | 74 catalog proposals, 3 pricebooks and external evidence metadata passed |
| `python scripts/validate_market_research.py` | 33 entities, 1,584 cells and 20 issues passed |
| `python scripts/validate_handoff_audit.py` | 101 rows / 98 declared pairs passed; ledgers unchanged |
| `python prompts/mobile/validate_prompts.py` | 2 Projects, 258 issues, 36 epic prompts, 906 criteria and 880 steps passed |
| `git diff --check` | Passed |

New offline tests check GiB conversion only for the named KV field, context and
geometry/revision rejection, active2/Quanto exclusions, positive denominators,
nonzero-error arithmetic, existing-output preservation and recomputation of all
12 committed component pairs with source/result hashes. Synthetic mutations stay
in tests and produce no research observations. Tests do not execute an estimator,
download an artifact or use a GPU. Actual estimator execution is recorded
separately with its command/code/output pins.

Quality review checked local note targets, retained source attribution and
separated native storage-width agreement from a whole-runtime prediction.
No GPU counters, original runtime source/protocol/summary, contract or shared
handoff ledger changed. Task-owned external artifacts were removed with a
checked cleanup receipt. Record-shape/hash checks do not certify source rights,
physical measurements, artifact/runtime equivalence, fresh deployment identity,
fit accuracy or human acceptance. #61 co-owners/coordinator and #7/#10/#11
receivers must review those matters; whole-runtime pairs remain zero and no
decision tolerance or issue completion is claimed.

### Subsequent offline review correction

The exact executed runner is retained at
[`mr09_compare_estimators.executed.py`](measurements/estimator-comparison-2026-10-18/mr09_compare_estimators.executed.py),
matching the unchanged comparison ledger's recorded source SHA-256. The current
runner now rejects boolean, fractional, nonpositive and nonfinite payload byte
counts before calculating an error. Both observation points have synthetic
negative and integral-float normalization coverage. The historical estimator
outputs, pairs, timestamps and their source hashes are unchanged; no external
estimator or GPU run was repeated to produce this correction.

The original 05:57 Planner report remains explicitly author-reported, without an
original-session capture. A subsequently supplied, separately dated 06:16
[reviewer receipt](measurements/mr09-estimator-comparison-2026-10-18.md#separate-reviewer-observation--2026-10-18-0616-utc)
corroborates visible controls at that later time; it does not reproduce the
earlier session, verify its HTTP 403s, pin deployed code or produce an estimate.
The original observation JSON and all estimator outputs remain unchanged by
this receipt; neither report supplies receiving-owner acceptance.

After this correction, Python 3.12.14 passed 21 contract tests and 249 repository
tests, including all 10 comparison tests; the same 10 comparison tests also passed
under optimized Python. Research intake, market, handoff-audit and mobile prompt
validators and whitespace checks passed. These are offline checks, separate from
the historical external execution recorded above.

## Supplemental GM1 validation — 2026-10-18

Branch: `codex/issue61-sizing-validation`, based on main
`61d549d76b894c1e5d8ac4229abf892d162da935`. This addendum applies to the
separate GM1 instrument, three real result records, summary and updated notes.
Historical 2026-10-16 validation below remains a dated record.

Validation used bundled Python **3.12.14** on Windows/PowerShell. Ran the
workflow's dependency installation with `-r requirements-research.txt --target
$TASK_VALIDATION_DEPS`; set PYTHONPATH to that isolated temporary dependency
directory. This does not modify the existing CUDA environment. The experiment
itself used Python **3.12.11** and the package versions in each observation.

All workflow commands were executed from the repository root:

| Check | Result |
| --- | --- |
| `python -m pip install -r requirements-research.txt --target $TASK_VALIDATION_DEPS` | Passed; pinned requirements installed |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed |
| `python -m unittest discover -s tests -v` | 213 passed, including five new guard/record-integrity tests |
| `python scripts/validate_research.py` | 74 catalog proposals, 3 pricebooks and external evidence metadata passed |
| `python scripts/validate_market_research.py` | 33 entities, 1,584 cells and 20 issues passed |
| `python scripts/validate_handoff_audit.py` | 101 rows / 98 declared pairs passed; no handoff ledger edited |
| `python prompts/mobile/validate_prompts.py` | 2 Projects, 258 issues, 36 epic prompts, 906 criteria and 880 steps passed |
| `git diff --check` | Passed |

The summary validates all six phases, recorded workload/cohort pins, finite
allocator counters and unique repetitions; record-integrity tests recompute the
summary and source/protocol/artifact pins. Guard tests use synthetic temporary
files and execute no GPU work or downloads. Real measurements are separately
identified in `measurements/granite31-2026-10-18/`. The unchanged dense cohort
continues to pass its existing integrity tests. Automated shape/hash checks do
not reproduce physical execution or establish estimator accuracy, source rights,
independence, whole-device capacity or receiving-owner acceptance.

Quality review retained the system/CUDA free-memory disagreement, driver change,
shared-device limits, administrative wrapper failure and sample-size limits.
Temporary model artifact cleanup is recorded without personal paths. Required
human review: #61 co-owners plus coordinator for evidence validity/coverage;
#7/#10/#11 consumers for their precise handoff scopes. No numerical competitor
error range, ResourceEstimate, issue completion or human approval is claimed.

## Historical environment and commands — 2026-10-16

Windows / PowerShell, from the `Pick-Your-AI/pick-your-ai-research` repository root (`$REPO` in sanitized execution records). Repository `.venv\Scripts\python.exe` is **Python 3.12.14**, isolated from the default Python 3.14.3. Prepend `.venv\Scripts` to PATH in the current shell so the exact required `python` commands select 3.12.14. Dependencies were already installed at the pinned versions; the installation command was nevertheless run for this submission.

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + ';' + $env:PATH
python --version
python -m pip install -r requirements-research.txt
python -m unittest discover -s contracts/v1/tests -v
python -m unittest discover -s tests -v
python scripts/validate_research.py
python scripts/validate_market_research.py
git diff --check
```

Initial baseline run on this branch: dependency installation succeeded; 21 contract tests and 11 research tests passed; research validator passed (0 catalog proposals / 0 pricebooks); market validator passed (32 entities, 1,536 cells, 20 issues); `git diff --check` passed. **A final run against integrated changes is recorded below before submission.**

The market validator exists because this submission is stacked on #67. It was executed here, not silently omitted or copied without its dependent market records.

## What automation establishes

Contract tests/intake cover frozen import integrity, generator consistency, canonical mapping, schema shape, reference/unit/date consistency and external artifact metadata. Market validation covers identifiers, evidence references in the existing feature matrix, paths, priority arithmetic, hierarchy and the presence of fields needed for a recorded Done state. It does **not** inspect every new prose claim, validate the handoff ledger, establish actual owner acceptance or certify that empirical criteria are met. Focused checks and independent evidence review below address the new material separately.

Reviewers still assess source accuracy, freshness, reuse rights, experimental validity, hardware interference, quantity comparability, counter availability, completeness and acceptance. Synthetic contract fixtures remain in the contract test/example paths. No new ResourceEstimate, model weights, credentials, customer content, raw dataset or large download is submitted.

## Independent contributor review

A separate evidence-review contributor checked the baseline, validator limitations, handoff/parent gates and primary sources. It independently reproduced the bounded ModelFit engine observation and verified source hashes, llmfit/planner assumptions and the within-v2 Harness Bench discrepancy. It independently recomputed all 15 published input hashes and every per-cell/per-phase min/median/max/count without using its own summary code. All six phase counters, token counts, BF16/INT4 payload sums and serial non-overlapping execution intervals were consistent.

The contributor also authored stricter summary guards and related synthetic tests; root independently inspected those two files, so that authorship is not represented as an independent review of its own code. Thirteen focused tests passed on Python 3.12.14. Fixes covered artifact identity before reuse, ledger preservation/singleton handling, incompatible summary signatures, duplicate repetitions, missing/invalid phases, failure exclusion, privacy and fresh-directory reproduction. Known pilot/ledger limitations are retained in the measurement note, with no fabricated timestamps. The measured runner and original protocol stayed unchanged; their LF file bytes and hashes match the Git newline policy and every observation.

A separate integrity contributor checked 43 prospective files: 29 JSON files parsed, all 14 criteria appeared verbatim exactly once, every original field of 78 handoff and 20 backlog records was preserved, and 135 relative Markdown links resolved with exact case in that snapshot. Targeted text/name/size scans found no unexpected binaries, model/archive files, credential-shaped strings, private paths or hardware UUIDs. Remote URL/anchor contents were excluded, and these scans cannot guarantee secret absence. Later root additions use the same verified local targets; final consistency checks accompany publication.

This is quality control, **not human evidence acceptance**. Human handoff dispositions remain in [handoffs.md](handoffs.md). The one-off preservation checker initially decoded Git output with the Windows default encoding, causing a false comparison failure; explicit UTF-8 decoding resolved it without changing historical data. An initial sandbox TEMP-permission failure in focused tests was rerun with normal temporary-directory access. Required final validation is recorded below.

The publication audit caught a distinct Windows newline issue after the first full test pass: result-file checksums matched CRLF working-tree bytes, while Git's existing `eol=lf` policy normalized the committed blobs. The summary publisher now writes explicit LF before hashing, with a regression assertion for portable published hashes. All 15 result hashes were regenerated; counters, timestamps, conditions and measured source/protocol pins are unchanged. Final verification compares hashes with actual Git blobs, not only local files. The first private commit was corrected before publication, and the required suite was rerun against the corrected content.

## Final integrated validation

Tested code/data commit: **`36e774d5fdafcaf51af8139703bb52a57e629bb2`**, on 2026-10-16 with Python **3.12.14**. This is the corrected integrated submission, including explicit LF publication and its regression assertion. All commands ran from the repository root, using the PATH selection above.

| Actual command | Result |
| --- | --- |
| `python -m pip install -r requirements-research.txt` | Success; all six pinned dependencies already satisfied |
| `python -m unittest discover -s contracts/v1/tests -v` | **21 passed** |
| `python -m unittest discover -s tests -v` | **24 passed**, including 13 focused measurement/summary tests |
| `python scripts/validate_research.py` | Passed; 0 CatalogItems / 0 Pricebooks; external weight manifest validated |
| `python scripts/validate_market_research.py` | Passed; 32 entities, 1,536 cells, 20 issues |
| `git diff --check` | Passed |

Additional actual checks compared all 15 **committed Git blobs** to the summary's SHA-256 entries and compared the committed instrument/protocol bytes to every run's retained hashes: passed. The historical-field and verbatim-criterion comparison against PR #67's pinned base also passed: all prior fields unchanged, exactly three new #61 handoff rows, all 14 criteria retained. Independent recomputation confirmed every phase's sample count and min/median/max; all five cells have n=3, total 15 successes and 0 comparable competitor error pairs.

Subsequent commits record this validation report and publication/review-request metadata only. They do not change measured counters, original protocol, measurement/analysis utilities or tests. Validate affected tracking consistency and whitespace after those edits; the PR's current-head CI remains visible in GitHub. No human acceptance, source-rights certification, empirical completion or merge is implied by these checks.
