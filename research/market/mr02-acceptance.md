# MR-02 acceptance and evidence audit

Issue: [#49](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49). Assignee: @zwright8. Audit date: 2026-10-16. Status: corrected draft, awaiting evidence and consuming-owner review; **not Done**.

## Revision and boundary

This contribution starts from `6511dea2a5102b13df1e47378a31f31230ecb494` on the unmerged `research/market-intelligence` branch (PR #67, base main). It changes the matrix and its guide, plus status wording in the market methodology. It does not approve or merge the parent package. Canonical-main delivery remains outstanding.

The live issue and PR review were read before edits. The [2026-10-16 review by @tynamite](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545) requests the neutral statuses and narrows the #42 handoff until saved/share/export/model_versions are examined for the 13 profiled products. This audit follows that request. Other issue files, source registrations and the canonical handoff ledger remain owned by their respective contributors.

## Criterion map

| Live criterion | Reviewable artifact and evidence | Exact check / observable | Required review and remaining gap |
| --- | --- | --- | --- |
| Define atomic capability tests | features.json capability_tests: all 48 IDs have bounded scenario, binary capture condition and required version/plan/access inputs | audit-check.log: 48 test definitions, key set equal to dimensions | @CompleteDotTech accepts taxonomy. Compound RAG/MCP/export labels retain explicit branches; a taxonomy split needs review |
| Link every supported cell to evidence | All 120 P cells have resolvable source ID, exact evidence_url, basis, method, evidence class and audit_scope | market-validation.log: 1,536 cells resolve; audit-check.log: all 120 documentary cells include claim metadata | @CompleteDotTech reviews claim truth and scope; source-register URL refinements go to #48 |
| Keep silence Unknown | 1,416 ? cells, no N; inaccessible/unperformed checks remain ? | audit-check.log status histogram and preserved pre-existing unknowns outside explicitly documented additions | No negative market-gap inference permitted |
| Review overlap and compare coverage | feature-matrix.md selected coverage, all 13 profile rows and counterexamples; every cell carries its narrower basis | audit-check.log: 13 × 4 targeted profile checks recorded | #42 owner @tynamite accepts/narrows documentary coverage and chooses required round-trip tests |
| Link significant conclusions to evidence or hypothesis | Guide links primary docs and machine cells; differentiating versioned history explicitly remains hypothesis | Source review manifest and claim-by-claim URLs in matrix | #57/#58 must decide positioning; no acceptance inferred |
| Technical owners review handoffs; name unresolved decisions | Owner/gap table below, refreshed live assignees | issue/pr snapshots; actual #42 review is narrowing only | All final-revision dispositions remain pending; #59 integrates accepted evidence |
| Checks pass and reviewer accepts evidence before Done | Python 3.12 workflow and market integrity results below | Each command exit 0 with captured output | Independent reviewer acceptance, qualifying merge to main, issue/Project readback remain open |

## Evidence collection and corrections

Read-only web text inspection covered the existing 32 entities' primary pages, with targeted documentation for the materially ambiguous cells. It did not execute product capability tests, request model output, deploy compute, pay for access, or reproduce third-party benchmark results. Thus this revision has no F cells. Claim-level classes are **Primary documentation** or **Vendor claim**, not a combined class. All numeric product performance, catalog counts and price examples were excluded from conclusions; no source-rate truth is certified.

All documentary claims inherit the dated public-page scope in features.json, including unpinned software versions, untested entitlements and no permission for downstream dataset display/redistribution. Exact URLs, publishers (existing source IDs), access date, methods, confidence and limitations are preserved in the matrix. This does not resolve #41/#60 rights review.

| Material prior claim | Audit disposition | Evidence / reason |
| --- | --- | --- |
| Flocci natural_language and explanation were F | natural_language becomes P; explanation becomes ? | Public Ask describes natural-language intake. Prior profile/substitute reports describe an observed answer, but their cited records contain no replayable capture locator; this pass did not independently verify that answer |
| Flocci constraints and rag were P from generated Windows/16 GB/no-GPU PDF advice | Both become ? | Generated advice does not establish constraint response correctness or an executed/evaluated retrieval flow |
| Flocci saved had a generic discovery basis | P narrowed to documented bookmarking | Public FAQ explicitly describes bookmarks without an account; persistence and versioned configurations remain untested |
| SkyPilot hosting was P | ? | Compute orchestration documentation does not establish SkyPilot as the actual hosted compute provider for a named offering |
| LM Evaluation Harness evaluation was P | ? | Cited repository establishes model benchmark evaluation, not the application-evaluation scenario; benchmarks remains P |
| MCP Registry mcp was P | P narrowed to registry discovery only | Server metadata registration does not establish a functioning MCP tool exchange |
| Local AI Planner context/multi_gpu were broad P | P narrowed to selector and identical-GPU heuristic | Page explicitly says current model context metadata is unavailable; multiplying VRAM/bandwidth is not topology/parallelism validation |

The original Flocci narrative remains in `competitors/flocci.md` and `substitute-validation.md` at the base revision: a private-laptop prompt reportedly returned local tools, and a Windows/16 GB/no-GPU PDF prompt reportedly returned Docling, txtai, Chroma, Ollama, Gemma and Open WebUI. This is preserved historical reporting, not a newly reproduced observation. #66/@CompleteDotTech should provide the captured interaction or rerun the bounded prompt before reinstating F. This correction neither declares the tools absent nor rejects the original observer's report.

The public ModelFit MCP link was discoverable, but a subsequent text fetch was inaccessible. Its cell remains documentary P for the advertised endpoint, never F or N. Arena's root text showed an app-building surface; the dedicated leaderboard URL was inspected to substantiate its ranking/comparison cells instead.

## #42 scope and counterexample review

All 52 requested cells across the 13 existing profiles carry a targeted check record. Documentary support was added where available, with boundaries in each cell; unanswered tests remain ?. This satisfies coverage of the audit, not a promise of affirmative capability grades.

Dify documents DSL transfer and exclusions; n8n documents JSON transfer and credential-metadata caveats; BenchLM describes filter URLs and a CSV surface; llmfit documents recommendation JSON and benchmark sharing; Models.dev documents catalog JSON; SkyPilot documents task YAML; Hugging Face documents versioned repository history. These mechanisms are heterogeneous and cannot be equated with BuildSnapshot. Account-specific saved selections, import/restore behavior, model revision pinning and recipient authorization still need bounded execution where the receiving owner considers them material. Unknowns cannot support a claim that competitors lack sharing/export.

## Required owner dispositions

Live assignees were read on 2026-10-16. No acceptance is fabricated from an assignment, agent review, PR comment or this table.

| Consumer | Live owner | Exact decision requested for final revision |
| --- | --- | --- |
| #6, #7 | @zwright8 | Accept model identity/context field comparisons as documentary inputs; do not equate displayed context with enforced limits |
| #10 | @Mattycodes69 | Accept/narrow fit-estimate coverage and explicitly reject treating estimated fit as measured sizing |
| #16 | @zabyxc01 | Accept distinction between RAG construction, advice and evaluation |
| #25, #27 | @CompleteDotTech | Accept agent/MCP boundaries; registry presence is not executed interoperability |
| #33 | @appletechie | Accept fine-tuning documentation as coverage only; no fine-tuned deployment proof supplied |
| #36, #39 | @PUSHINGSQUARES | Accept benchmark/evaluation and price-field boundaries; no measurement or complete cost model delivered |
| #42 | @tynamite | Accept/narrow the 13-product saved/share/export/version audit; select required execution cases |
| #48 | Unassigned | Program coordinator routes claim-specific URL refinements into the existing source register; do not assign an owner from stale prose |
| #57, #58 | Unassigned | Program coordinator routes overlap/counterexamples; differentiated versioned history remains a hypothesis |
| #59 | Unassigned | Program coordinator routes final accepted dispositions into the canonical handoff ledger |

The issue names @CompleteDotTech as program evidence reviewer. That review remains required. Source and handoff files were not rewritten by this issue. Project synchronization cannot be claimed from this draft; the coordinating run reported missing GitHub read:project scope, so live board readback remains an external gate.

## Validation and reproducibility

Executed with Python **3.12.12** in a local disposable venv, from this worktree. For each command, the observable is its exit code and the nonempty log below, not a historical report:

| Invocation | Observable | Captured local artifact |
| --- | --- | --- |
| python -m pip install -r requirements-research.txt | Exit 0 | .omo/evidence/mr02-feature-audit/install.log |
| python -m unittest discover -s contracts/v1/tests -v | Exit 0; 21 tests OK | .omo/evidence/mr02-feature-audit/contracts-tests.log |
| python -m unittest discover -s tests -v | Exit 0; 24 tests OK | .omo/evidence/mr02-feature-audit/research-tests.log |
| python scripts/validate_research.py | Exit 0; 0 catalog proposals, 0 pricebooks; external metadata checked | .omo/evidence/mr02-feature-audit/research-validation.log |
| python scripts/validate_market_research.py | Exit 0; 32 entities, 1,536 cells, 20 issues | .omo/evidence/mr02-feature-audit/market-validation.log |
| Recorded read-only matrix audit invocation | Exit 0; all bounded structural checks PASS | .omo/evidence/mr02-feature-audit/audit-check.log |
| git diff --check | Exit 0 | .omo/evidence/mr02-feature-audit/diff-check.log |

The python executable is `.omo/evidence/mr02-feature-audit/venv/bin/python`. Actual audit invocation and source-review manifest are retained in the same evidence directory. No repository Python code was changed, so no new test suite was introduced. Existing market checks derive allowed statuses from status_semantics; the label migration requires no validator rewrite.

Automation checks structure, references, metadata and imported-contract integrity. It does not prove source truth, rights, freshness, actual product execution or owner acceptance. The existing market validator uses Python assertions: run it normally, not with -O; replacing its assertions and changing sparse/not-applicable matrix policy are separate follow-ups from the review, outside this bounded artifact correction.

## Remaining delivery

Use **Refs #49**, not Closes. Coordinate this focused stack with PR #67; review and merge into the proposal branch alone is not delivery to main. Refresh source/owner state and final head before review. After actual evidence and owner acceptance, verify the qualifying main merge, issue closure and Project values. Until those actions occur, this remains an auditable local contribution to an open goal.
