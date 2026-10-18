# Native qualification submission validation — 2026-10-18

Refs #61. Integrated against main `bc35bbe`; Python 3.12.14 with pinned
`requirements-research.txt` installed in isolated temporary dependency storage.

- 21 contract tests passed.
- 312 repository tests passed with one skip: portable g++ compiler absent on
  Windows. The existing MSVC x64 toolchain separately compiled and passed the
  [native synthetic quota selftest](quota-selftest.json), including 16,000
  concurrent admissions. These fixtures are not physical GPU evidence.
- Research validator: 76 catalog proposals, 3 pricebooks and evidence metadata.
- Market validator: 33 entities, 1,584 cells and 20 issues.
- Handoff audit validator: 101 rows and 98 declared pairs; no acceptance inferred.
- Mobile prompt validator: 2 Projects, 258 issues, 36 epic prompts, 906 criteria,
  880 steps, including local links and prerequisite graph.
- Original offline setup checker still reports prepared/disabled and zero runtime
  observations in its historical record. Native capture checker separately
  reproduces three initialization captures, each 334,511,360 live buffer bytes,
  zero accepted estimator pairs and zero whole-process peak pairs.
- Whitespace/local-link/private-path checks passed. Current and retained Git
  source hashes match the successful build receipt. Frozen v1, historical CPU
  preparation/output and merged #259 checker/tests have no diff from main.

Automation checks structural consistency, arithmetic, pinned records and failure
handling. It does not reproduce GPU hardware observations in CI, establish
source accuracy or rights/freshness, prove a physical process-wide cap, accept
estimator matching/tolerance, or provide receiving-owner acceptance. Actual
initialization-only evidence and remaining gates are in [qualification.md](qualification.md).
