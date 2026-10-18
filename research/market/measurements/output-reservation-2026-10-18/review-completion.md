# PR #267 evidence-review integration — 2026-10-18

Refs #61. Integrates accepted main `9192d5d6994b644ebbb81344300fda48db6d29a8`
with reviewed prospective-launcher head
`8a5e4063af352e0fa320b050ba0cfba0a37b9751`, without conflicts, in merge commit
`9a317293f7169157857e0764254bf46be81f1537`.

## Review findings and disposition

| Finding | Correction / retained evidence | Review boundary |
| --- | --- | --- |
| Duplicate/aliased driver headers, invalid rehashed preflights, event ordering | Offline reader rejects all demonstrated cases before publication; original inputs remain intact | [Original requested changes](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561872151); independent corrected-source receipts are recorded in [5561943027](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561943027) and [5561943495](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561943495). Formal whole-PR disposition remains separate |
| Decreasing final peak / invalid native discovery bytes | Cross-phase peak consistency and exact unsigned discovery guards | Same independent correction receipts; no new CUDA observation |
| Wrapped free callback changes CUDA identity/copy paths | Explicit instrumentation qualifier and pinned common.cuh graph-disable source retained | Source qualification only; unchanged standard-runtime copy behavior is not asserted |
| Post-child telemetry could lose the native result | Prospective launcher persists atomically before bounded telemetry; pending/failed telemetry never qualifies; seven mocked regression methods retained | [Independent correction review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561952952), at exact 8a5e406; archived executed launcher and old cohort pin preserved |
| Stale estimator rationale and imprecise anchors | Cite the estimator's one-graph-output assumption and contrast the pinned runtime's 256-row reserve; point directly to L914/L944/L770 | Addresses [appletechie's source review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561985132); source-audit/report hashes and conclusions unchanged |
| Missing spaces | Correct matching-note prose and the version description in both runtime manifests | Manifest IDs, artifact hashes, source commit and locators unchanged |
| Current-main integration | All 28 main-side changed paths match main exactly; unrelated upstream contributions preserved | Fresh combined validation below; this is not reviewer approval |

[Zwright8's #7 acceptance with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/267#pullrequestreview-5561909720)
is recorded only for the exact matching diagnosis as an exclusion gate.
Appletechie's no-blocking-findings source review does not supply #7/#10/#11
or coordinator evidence acceptance. No broader receipt is inferred. The formal
requested-changes review needs its reviewer's new disposition on the integrated
submission; this note does not dismiss or approve that review.

## Validation and preservation

Python 3.12.14, pinned requirements installed into isolated temporary storage:
21 contract tests and **339 repository tests passed**, with one Windows
portable-g++ skip. The original native MSVC CPU selftest and subsequent portable
CPU review receipts keep their own historical scopes. Research, market,
handoff-audit and mobile workflow validators passed. Historical setup, native
capture and output-reservation helpers recompute unchanged quantities.

A preservation check compared 84 protected paths with 8a5e406: native captures,
preflights, source/build/runtime ledgers, historical setup and CPU output,
source-audit/matching report, native source/quota, current reviewed launcher,
archived executed launcher and frozen v1 retain their exact Git bytes. The
matching narrative is the explicit prose exception. Both manifests change only
spacing in version text. The archived executed launcher SHA-256 remains
`6a645f212c3b947789345dc739d88d554f3e083021db3cc0f7abfebc8ff1f8b8`.
All 28 main-side changed blobs equal the accepted main tree. Whitespace and
local-link checks pass. No historical validation note is rewritten as though
it tested this later integration.

No estimator, model, native GPU process or driver operation was executed during
this review integration. Three native initialization observations remain
bounded to their instrumented managed-buffer scope; accepted estimator pairs
and whole-process peak pairs remain zero. Output-count agreement does not
repair the host-capacity/output-placement mismatch. No versioned estimator
correction, ResourceEstimate, tolerance, compatibility decision, scope waiver or
issue closure is included. #61 remains open with its co-owners and full criteria.

Automation checks integrity, arithmetic and preservation. It does not reproduce
physical measurements, verify every source interpretation/rights/freshness,
accept a replacement estimator or grant outstanding receiving-owner decisions.
Hosted checks and the reviewer's formal disposition remain separate live gates.
