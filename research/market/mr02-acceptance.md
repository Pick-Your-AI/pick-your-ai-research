# MR-02 acceptance and evidence audit

## Memory-boundary correction — 2026-10-18

Prepared from accepted research main `387e3ff639fc65c125ccd1716507acc2ae43c3bc`, matrix blob `a5e6a0887516b47cd7077a2b7471622cced8f73b`. The later sections retain their literal historical revision, counts, owners and validation; they are not rewritten as current acceptance.

The existing `canirun-ai` / `vram_ram` cell had status Documented, although its own basis describes device memory capacities and explicitly separates them from model memory requirements. The unchanged dimension test requires a requirement for a pinned model/runtime configuration, with units and assumptions. Available device capacity is not partial evidence of that required quantity. The current repair sets this one cell to Unknown and updates its limitation; the previous source identity, URL, access date, reading method, documentary grade, confidence and capacity observation remain exact as historical context.

| Classification | Before this correction | After this correction |
| --- | --- | --- |
| Complete matrix | 33 entities × 48 dimensions = 1,584 cells | Unchanged |
| Documented / Unknown | 123 / 1,461 | 122 / 1,462 |
| Exercised / Unsupported | 0 / 0 | Unchanged |
| CanIRun.ai Documented / Unknown | 3 / 45 | 2 / 46 |
| Other cells and capability-test definitions | 1,583 other cells; 48 tests | Exact preservation required |

This resolves the specific memory-cell mismatch identified in the earlier [shared-file agreement](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6245977192), without adding the six separately staged discovery candidates or their 288 cells. Their catalog/source integration remains a distinct #48 decision. No current source retrieval, product test, model sizing, source-use permission, capability absence or matrix-wide evidence acceptance is asserted by this repair.

The scope supports the #10 distinction between hardware capacity and a model/runtime memory requirement. Actual independent review of this changed cell and guide remains required before delivery; it is not a substitute for the other #49 receiving decisions or review of the remaining supported claims. The completed #66 research may inform a separately reviewed matrix update; its observations are not relabelled as this author's execution and no Flocci grade changes here. All source-register, catalog, canonical handoff, frozen-contract and issue/Project metadata remain outside this patch.

Required checks, exact current-head review and normal canonical delivery are recorded in the contribution's PR. Until those checks and the remaining literal #49 criteria and receiving decisions are met, #49 remains open.

## Delivery and evidence readback — 2026-10-18

Readback basis: research main `ac5e5844dd1cd01366a1b51a0054afa71a340aca` and GitHub
responses read through 2026-10-18T05:19:30Z. PR #87's matrix audit reached canonical main through
#67; #98 added CanIRun.ai. At this revision there are 33 entities, 48 dimensions,
1,584 cells, 123 Documented and 1,461 Unknown; no Exercised or Unsupported cells.
The 48 capability tests cover exactly the 48 dimension IDs. These are coverage
counts, not a product capability score or an acceptance receipt.

The validator uses explicit `MarketValidationError` checks under normal and
optimized Python. The current correction also requires every non-Unknown cell's
existing claim metadata: basis, verification method, evidence grade, exact HTTP(S)
URL without credentials, actual YYYY-MM-DD access date, confidence, limitations
and audit scope. A resolvable source-register ID alone is insufficient. These
offline checks reject incomplete records; they do not retrieve the source or
verify that its text supports the feature's bounded test. Unknown cells can stay
incomplete without fabricated evidence. No grade taxonomy or frozen v1 field is
changed.

### Current acceptance map

| Issue #49 criterion | Evidence at the readback revision | Remaining acceptance or action |
| --- | --- | --- |
| Define atomic capability tests | `features.json` contains 48 scenarios, observables, required conditions and failure policies; the validator checks exact dimension coverage | Independent taxonomy review remains required; compound RAG/MCP/export branches are not interchangeable |
| Link every supported cell to evidence | All 123 Documented cells contain the existing claim metadata; the validator now rejects missing, blank or nontext metadata, invalid URLs and impossible access dates | A valid URL/date is not source accuracy, freshness or intended-use permission; claim review remains separate |
| Keep silence Unknown | 1,461 cells remain Unknown; no new positive or negative cell is introduced by this correction | Do not infer absent capabilities or market gaps from Unknown |
| Review overlap and compare coverage | Existing guide records the 13-profile × four-column saved/share/export/version review and documentary counterexamples | #42's original narrowing is not acceptance of the later cells; current receiver review and selected round-trip tests remain |
| Link conclusions to evidence or hypothesis | Existing matrix records and guide distinguish documentary claims from runtime behavior; the new Flocci evidence is reconciled below without changing grades | Reproducible configurations, measured fit, rights and market demand are still distinct unknowns |
| Obtain technical-owner handoffs and name unresolved decisions | Actual scoped receipts and live co-owners are recorded below, with links to their reviewed revisions | Preserve the canonical #59 writer; author integration cannot supply independent acceptance |
| Pass checks and obtain reviewer acceptance before Done | Current correction runs the complete Python 3.12 workflow and rejection regressions in both Python modes | Exact-head hosted CI, independent review of this correction and remaining research handoffs are required; #49 remains open |

### Actual receiving dispositions and next decisions

These are issue #49's acceptance-map references, not a replacement for the
[canonical handoff ledger](handoffs.json). Its ten #49 pairs at the pinned base
contain two author-integration-only rows, two scoped-response rows and six without
receiving responses. That is recorded receipt coverage, not ten accepted handoffs.
Live GitHub assignees were read for every consumer below; preserve all co-owners.

| Consumers / live co-owners | Actual receipt and retained scope | Next decision |
| --- | --- | --- |
| #6: @zwright8, @PUSHINGSQUARES; #7: @zwright8, @appletechie | [zwright8's 6242699859](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6242699859), reviewing main `7acbefbf4e4e700231e88be272bc89e3a73dde15`: author integration only | Obtain independent taxonomy/claim acceptance; this author cannot approve their own matrix as a receiving reviewer |
| #10: @Mattycodes69, @appletechie | No receiving receipt recorded for the #49 pair at this base | Accept/narrow hardware-estimate coverage; a device capacity or recommendation is not measured model sizing |
| #16: @zabyxc01, @appletechie | No receiving receipt recorded for the #49 pair at this base | Accept/narrow RAG construction versus advice versus evaluation |
| #25: @CompleteDotTech, @Mattycodes69; #27: @CompleteDotTech, @tynamite | No receiving receipts recorded for these #49 pairs at this base | Accept/narrow agent and MCP coverage; a registry listing is not a successful tool exchange |
| #33: @Mattycodes69, @appletechie; relevant #30–#32 context | [appletechie's review 5554129449](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5554129449) at `6511dea2a5102b13df1e47378a31f31230ecb494` narrows T5 to information only; [6230504818](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6230504818) reaffirms the #30–#32 mapping | See the exact reaffirmation and conditions immediately below |
| #36 / #39: @PUSHINGSQUARES, @appletechie | No receiving receipts recorded for these #49 pairs at this base | Accept/narrow benchmark/application-evaluation and price-field boundaries; no new measurements or complete cost model are delivered |
| #42: @tynamite, @appletechie | [tynamite's review 5550697545](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545) at `6511dea2a5102b13df1e47378a31f31230ecb494` requests the four columns across 13 profiles | The later 52-cell audit answers coverage, not independent acceptance of every cell or execution of a round trip |

The exact T5 reaffirmation is [comment 6230504818](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6230504818).
It explicitly extends the #33 information-only disposition to `fine_tuning`,
`training_compute` and `training_data` context for #30/#31/#32, without new rows
while that limited scope remains. It names no new reviewed SHA, so none is
inferred. A newly promoted finding needs the specific affected-consumer handoff;
`fine_tuned_deploy` must distinguish adapter, merged weights, GGUF or provider-hosted
artifacts. This does not accept a later matrix revision or include training in MVP.

The independent program/evidence review remains with @CompleteDotTech. #48 and
#59 are currently co-owned by @Mattycodes69/@appletechie; #57 by
@tynamite/@appletechie; #58 by @appletechie/@PUSHINGSQUARES. Their historical
"Unassigned" entries below describe the 2026-10-16 snapshot only. No issue owner,
Project status, native relationship or canonical ledger receipt is changed here.

### Reserved matrix correction and later Flocci evidence

The [shared-file agreement 6245977192](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/49#issuecomment-6245977192)
leaves @appletechie the six staged community resources, their 288 cells, the
specific CanIRun `vram_ram` correction and derived guide/count reconciliation.
Device memory capacity alone does not satisfy the model-memory-requirements
dimension. That known cell remains a pending correction until their reviewed
change lands. This submission preserves all matrix cells, taxonomy IDs, source
records and the guide to avoid a competing implementation of that reserved slice.
No additional deep-dive profile or evidence grade is pre-accepted.

[PR #227](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/227), submitted
head `ef685e30af7c1c3a447f4732e1647075b23a3b2b`, merged as
`49896b41b6e0add6f333406112e8d009e7ad9ee6`, adds a dated Flocci guest contradiction,
bookmark and return-navigation observation in [substitute-validation.md](substitute-validation.md).
The older request below to rerun a sign-in-blocked test is historical. The new
note reports recognition of the offline/hosted-model conflict and one saved tool
bookmark without a recovered stack; generated fit/privacy/runtime claims remain
unverified. The distinction between detecting an impossible conjunction and
satisfying a coherent workload is preserved.

[Receiving review 5561540382](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/227#pullrequestreview-5561540382)
accepts only the #40 explanation-versus-compatibility evidence boundary. Its #50
exercised-result acceptance needs review locations for three retained captures;
this author has not independently inspected those screenshots or verified their
hashes. The note's report and other reviewers' evidence scopes are not converted
into this author's observation. No Flocci cell is promoted to Exercised, and no
general absence of export, measured fit or market gap follows. #66's owners and
the actual #42/#50/#57/#58 receivers retain their own acceptance decisions.

### Validation of this correction

Python 3.12.12 with the pinned requirements, run on 2026-10-18:

| Command or observation | Result |
| --- | --- |
| `python -m pip install -r requirements-research.txt` | Pinned dependencies installed in the external audit environment |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 pass |
| `python -m unittest discover -s tests -v` | 184 pass, including four added market-test methods |
| `python scripts/validate_research.py` | 74 catalog proposals and three pricebooks validate |
| `python scripts/validate_market_research.py` and `python -O scripts/validate_market_research.py` | Both pass: 33 entities, 1,584 cells and 20 issues |
| `python scripts/validate_handoff_audit.py` | Pass: 101 rows and 98 declared pairs; human acceptance not certified |
| `python prompts/mobile/validate_prompts.py` | Pass: 258 issues, 36 epics, 906 criteria and 880 steps |
| Controlled baseline/corrected CLI comparison on synthetic records | Missing claim URL, blank grade, URL with credentials and impossible February date each pass the unchanged validator and fail the correction, in both Python modes |

Valid complete synthetic Documented/Exercised/Unsupported cells pass, and an
Unknown cell still passes without invented provenance. Additional regressions
cover every required field missing/blank/nontext, malformed URLs and invalid or
noncanonical dates. This is record-integrity validation; no vendor capability,
freshness, source rights or receiving-owner decision is newly verified. All real
matrix/source records, the guide, canonical handoffs and frozen contracts are
unchanged by this correction. Independent exact-head review remains required.

## Historical submission record — 2026-10-16

The remainder preserves the original proposal-branch audit, counts, owner snapshot
and executed validation. Its present-tense branch/review statements describe that
submission date, not current repository state. No historical test was rerun or
receiving acceptance inferred by this status correction.

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
