# H1 preparation validation — 2026-10-19

Refs #61. Source/build preparation at `86c19ef828f4fa6a48ea5138b834d8317f87d304`.
Python3.12.14; exact `requirements-research.txt` installed in a fresh task-only
temporary validation environment. Existing inference environments, packages,
drivers and system settings were unchanged. A preliminary sandbox dependency
check could not resolve the newly required idna package; no package was changed
there. The isolated host environment subsequently installed every required pin.

| Actual command / check | Result and boundary |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed |
| `python -m unittest discover -s tests -v` | 1,216 methods: 1,206 passed, 2 errors, 8 skipped;532.178seconds. All10 new mocked launcher methods passed. This original local run is not green. |
| `python scripts/validate_research.py` | Passed;124 catalog proposals/3 pricebooks and evidence metadata |
| `python scripts/validate_market_research.py` | Passed;39 entities/1,872 cells/20 issues |
| `python scripts/validate_handoff_audit.py` | Passed;101 rows/98 pairs; no human acceptance certified |
| `python prompts/mobile/validate_prompts.py` | Passed;2 Projects/258 issues/36 epic prompts/906 criteria/880 steps |
| Existing native CPU quota fixture, freshly compiled | Passed:8threads/16,000 admissions, boundary denials and zero final live bytes |
| `git diff --check` | Passed |

Independent in-session evidence review checked all six original local log
lengths/hashes and attendance, including all10 new launcher results. Original
logs remain separately attributed to this execution. The [hosted Ubuntu check](https://github.com/Pick-Your-AI/pick-your-ai-research/actions/runs/39212658801)
for the initial PR #472 source also completed successfully; it does not replace the non-green
Windows observation or establish native execution.

The unchanged mobile reference test read a UTF-8 document using Windows CP1252.
A separate process-local `python -X utf8 -m unittest discover -s prompts/mobile
-p test_migrate_references.py -v` run passed all14 methods, including the failed
case. No mobile file or machine encoding setting was changed.

The other error is the unchanged native alias test's missing Windows symlink
privilege (`WinError1314`). Its existing contributor owns [PR #473](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/473).
This contribution does not edit that test or grant host privileges. No full-suite
pass is claimed by combining these separate observations.

Independent native/launcher review confirmed the fixed H1 tuple, unchanged cap,
graph refusal, fresh guards, exact source/build/runtime bindings, preservation
before telemetry and no continuation after failed/pending trials. The actual
compiler is MSVC19.29.30153, linker14.29.30153.0;14.29.30133 identifies the existing
toolchain directory only. Source hashes also match the literal committed blobs
at `52c783e7d5ea32d43f240d1e72dab1b510b832a9`.

These checks qualify preparation/integrity only. No prediction freeze or native
model capture exists at this checkpoint. Estimator source/build/semantic review,
frozen prediction, fresh resource screens, actual capture and receiving evidence
review remain separate. No estimator pair, peak calibration, fit verdict,
ResourceEstimate, named-owner response or issue completion is supplied.

## Final integrated validation — 2026-10-19

The original preparation checkpoint above is preserved. The later three real
H1 observations and [descriptive comparison](results.md) have their own evidence;
they are not attributed to that earlier validation run.

At integrated source `a7e58171c2627f4bb0ba615fb25dd0e9ffe9b9c7`, after carrying
accepted #473, the actual final run used the same pinned isolated environment
with **process-local `PYTHONUTF8=1`**, from07:19:18 through07:27:41UTC:

| Check | Actual final result |
| --- | --- |
| Frozen-contract suite | 21 passed |
| Repository suite | 1,216 methods: **1,207 passed,9 skipped,0 failures/errors**;499.109seconds |
| Research, market, handoff and mobile validators | All four passed |
| Offline H1 comparison reproduction | Passed, same three records and exact arithmetic |
| Complete-contribution whitespace and Git-byte checks | Passed; each captured preflight retains its original bytes |

The [final receipt](final-validation-receipt.json) retains exact commands,
source identity, original log lengths/hashes and results. Later publication
wording and readable-path redaction do not change the executable source,
frozen prediction or measured artifact bytes. Earlier errors are not relabeled
as successful tests. No system encoding setting or symlink privilege changed.
The [hosted check39215499249](https://github.com/Pick-Your-AI/pick-your-ai-research/actions/runs/39215499249)
also succeeded at the separately published `ba0faa4` source.

The nine skips are four Windows directory-symlink capability cases, three
Linux parent-death cleanup cases, one unavailable FIFO case and one absent
portable C++ compiler case. The native quota fixture was separately compiled
with the existing MSVC toolchain and passed. Independent readback checked all
seven final log hashes/lengths, complete method attendance, every new launcher
pass, the skip reasons and exact offline-summary equality before cleanup.

The initial draft #472 was replaced by [PR #476](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/476)
under the repository's permitted `contrib/**` branch namespace. Existing commits
and all frozen/measured bytes are preserved; no main merge, approval or issue
completion is implied. Reviewer and named receiving-owner acceptance remain
outstanding. Original non-sensitive CPU test log bytes are retained in the four
published base64 fields; readable traceback paths are explicitly redacted.
