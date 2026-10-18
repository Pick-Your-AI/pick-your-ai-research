# MR-01 landscape review and selection rationale

Refs #48. Original documentary checks: 2026-10-18 (Asia/Shanghai); current-main reconciliation and correction review: 2026-10-18 (UTC). Partial contribution for review; no issue acceptance is asserted.

The original audit and receipt-only sections retain their PR #214/#231 bases, counts and validation records. The [later catalog and summary reconciliation](#2026-10-18-catalog-and-summary-reconciliation) below adds narrowly dated source evidence and reader-facing corrections. The [current seed and receipt readback](#2026-10-18-seed-and-receipt-readback) records the subsequent bounded source pass and T4 receipt; historical acceptance maps and pending requests below describe their stated revisions.

## Revision, authority and writer boundary

Live GitHub lists **Mattycodes69 and appletechie** as co-assignees; CompleteDotTech remains the issue's named evidence coordinator. This contribution claims no ownership transfer and changes no assignment, issue checklist, Project field or native relationship.

PR #67 merged to main. The original audit at `5b5afdc967e02a74fb6cb0090c2ca09ff83f330a` targeted its historical branch `research/market-intelligence` at `aed4e7d6fd63d1f8a3e765295fa0a23ab8af3ce2`. That original draft and its stated review-only context remain in Git history. The author correction at `ae1533b58df6b01ac06d223147ed0527081030f2` is preserved, including the four source corrections, ModelFit date discrepancy and per-field review dating. The original delivery responds to [co-owner review 5561429617](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214#pullrequestreview-5561429617) and reconciles the audit for delivery to `main` at `254227acc0d6f1eef8bc17a20d9c1994c12d20cd`. That delivery changed only the two landscape JSON files and this rationale relative to that main revision. The follow-up below changes this rationale only, relative to merged main `bf5fe18ddea9703565ed3184d73cbd8d829b741c`.

The reconciled main inventory has **33 registered entities**, 14 profiles, 1,584 feature cells and 58 distinct source IDs, including CanIRun.ai intake #98 and operator correction #109. The original audit adds dated `discovery_review` records for its 32 historical entities and separately rechecks the existing CanIRun.ai source. Main's CanIRun.ai entity, later source records, profiles and matrix remain intact. Source records are reconciled by stable ID, so `src-canirun-ai` and `src-canirun-ai-repo` each occur once.

Contributor and submission instructions apply at current main; the original base and prompt references remain available in the original audit commit. Unmerged review proposals are leads. Earlier proposal merges do not confer receiving-owner acceptance for this revision. Current PR head, base and checks must be refreshed before integration; this note does not certify later live state.

The original draft records separate collection passes and one serialized integration of the shared JSON files. This corrective reconciliation likewise has one writer. Assistant evidence/integrity review has its stated scope and does not supply an absent receiving-owner disposition. #49 retains the feature matrix, #50 the profiles, #66 hands-on tests, #59 the canonical handoff ledger, and #41/#60 reuse decisions. No catalog proposal, pricebook, contract or schema is changed by this audit.

## Acceptance map

| Live #48 criterion | Artifact / evidence | Check for this submission | Required reviewer | Status / remaining gap |
| --- | --- | --- | --- | --- |
| Verify all five seeds | First five `competitors.json` discovery_review records; dated `sources.json` rechecks; seed section below | Official pages and linked upstream documents read; website/product/repository boundaries compared | appletechie and evidence coordinator CompleteDotTech | Partly met: all five operational seeds source-checked; original historical seed intent remains undocumented and operator unknowns remain explicit |
| Classify at least 30 distinct resources | 33 preserved main entity IDs and existing taxonomy; 32 dated discovery records plus the CanIRun source recheck | Per-entity documentary identity/scope audit; no duplicate ID or alias promoted as a new resource | appletechie / CompleteDotTech | Numeric/documentary coverage met; no claim that the products ran or are complete substitutes |
| Record entity boundaries and unknowns | `discovery_review`; source limitations, URL statuses, version/region and rights | Site/repo/product/cloud/code/data boundaries reviewed for every base entity | appletechie; #41 owners for provenance | Met as an uncertainty record; unresolved operators and version pins are recorded, not invented |
| Select 10–15 material deep dives | Fourteen-candidate selection below; the 13 existing historical profiles plus the existing CanIRun profile | Decision overlap, evidence availability, substitution risk and source relevance stated; exclusions bounded | #50: zwright8 / appletechie; coordinator | Working list accepted with constraints by zwright8 at `f97aa1a`; appletechie's earlier conditional narrowed disposition remains recorded. Coordinator confirmation, community-profile changes and profile/hands-on acceptance remain separate; no automatic acceptance of later heads |
| Every significant conclusion links to evidence or an explicit hypothesis | Dated recheck claims contain URLs, publishers, evidence classes and inherited date/version/region/confidence/rights/limits | Explicit claim review described below; no fresh performance, price or feature grade inferred | Independent evidence reviewer; #41 for intended reuse | Partly met for the full historical artifact: fresh discovery claims are linked; untouched historical fields are not blanket reverified |
| Relevant technical owners review handoffs; unresolved decisions named | Exact receiver questions below and PR requests at submitted head | Actual receiving dispositions retain their reviewed revision and scope; remaining requests are distinguished below | All live #6/#10/#25/#41 receiving owners | Partly received: zwright8 narrowed #6 to discovery/context at `f97aa1a`; PUSHINGSQUARES and #10/#25/#41 receiving dispositions remain pending for this slice. #50's working-list receipt is separately scoped below |
| Repository checks pass; reviewer accepts evidence before Done | Validation section and PR checks at submitted head | Python 3.12 workflow plus market integrity and diff check | Independent reviewer and receiving owners | Technical correction/integration reviews and checks are recorded below; full evidence and receiving-owner acceptance remain open. Merge of partial research does not complete #48 |

These statuses are submission assessments, not edits to GitHub's seven unchecked boxes.

## Seeds and identity boundaries

The base landscape calls the first-five list inferred. Current main's [landscape at the inspected revision](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/1393d00b2f710d405384360dbbdc220f0356eaf2/docs/market-research/competitive-landscape.md#seeds) explicitly selects the same five as the operational scope on 2026-10-18. This supplies a documented working list without claiming to recover undocumented original intent from array order.

- **BenchLM:** official home, selector and terms read (`src-benchlm`, dated recheck). Hosted model/provider decision tool; legal operator remains unnamed. The selector's workload/constraint/explanation/share claims are documented, not freshly exercised.
- **Harness Bench:** official site and linked Qihoo360 repository read (`src-harness-bench`). Site attribution establishes Harness Bench Team / repository linkage; it does not identify a legal company or establish dataset rights. No benchmark run or new numeric suite-size claim.
- **llmfit:** seed `llmfit.org`, upstream AlexsJones repository, CNAME, licence and `llmfit.axjns.dev` read (`src-llmfit`, `src-llmfit-upstream-pages`). Upstream Alex Jones identity is established separately; seed-domain operator/affiliation remains unverified. Mutable/cached CNAME is not a fresh repository-wide absence search.
- **Local AI Planner:** official planner and Logarithmic Spirals about page read (`src-local-ai-planner`, `src-local-ai-planner-about`). Individual pseudonymous blog author; weights/KV/runtime/speed outputs are estimates. No numerical accuracy or runtime-topology verification.
- **Flocci:** official Ask, Stack and home pages read (`src-flocci`). Flocci Technologies is the site's attribution. Fresh evidence is documentation only; the historical generated PDF-RAG advice retains its 2026-10-16 observation date. Contradiction handling and reusable export remain with #66.

Also retain BenchLM, CanRun, CanItRun and LLM Stats legal-operator unknowns. GPUs.io has a publisher-named operator in the separately rechecked terms; independent corporate/ownership verification remains incomplete. CanRun, CanItRun and CanIRun.ai are different products; similarity of names establishes no affiliation. The carried CanIRun source plus fresh site/repository check identifies the individual account **midudev**, retaining #109's correction while leaving legal entity and other affiliations unknown. ModelFit's official about page self-identifies Peter Dekker; code package branding does not replace that qualified attribution.

## Direct-substitute pressure and falsification route

The following are documentary findings or explicit test hypotheses. Per-claim publisher/date/version/region/confidence/rights/limitations live in the corresponding source's `rechecks` entry dated 2026-10-18. Reading a page is an access observation; reading instructions for an API, export or recommendation is not executing it.

1. **Workload-first selection already has material overlap.** [BenchLM selector](https://benchlm.ai/tools/llm-selector) documents job descriptions, constraints, explanations and shareable answers (`src-benchlm`; method label `bench-align-v5.8-2026-09-30`). Flocci advertises ordered toolchains; Local AI Planner documents goals plus hardware controls. Hypothesis for #50 -> #66: these may suffice for bounded hosted-model or local-stack decisions. Test the unchanged local-PDF/Windows/16-GB/no-GPU scenario and explicit contradictory constraints, not merely whether an input form exists.
2. **Reusable configuration is not an unoccupied feature.** Dify [DSL export](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management), Langflow [flow JSON](https://docs.langflow.org/concepts-flows-import), SkyPilot YAML (reviewed URLs in `src-skypilot`) and n8n's [AI Starter Kit](https://docs.n8n.io/deploy/host-n8n/deploy-with-the-ai-starter-kit.md) document reusable workflows/manifests. The n8n kit names Ollama, Qdrant, PostgreSQL and n8n, explicitly for testing/proof of concept. Hypothesis: a prepared composition may substitute for planning in some segments. None was exported, imported or deployed here; a manifest does not establish compatibility explanation, secrets-safe sharing or a successful workload.
3. **Fit explanations remain scoped estimates.** CanRun, CanItRun, ModelFit, Local AI Planner and CanIRun.ai document fit assumptions/reasons; upstream llmfit documents hardware/model matching. That supports investigation, not universal compatibility or an error bound. #10 must decide which conditions are useful; no ResourceEstimate or cross-component rule follows.
4. **Published configuration histories already exist.** Upstream [llmfit README](https://github.com/AlexsJones/llmfit) documents saved benchmark results and contribution/sharing. Community resources below document shared run histories/protocols. This is evidence against assuming exclusive possession of configuration history; it is not a verdict on reproducibility, coverage or a complete multi-tier substitute.

Route these candidates through **#50 (zwright8/appletechie) to #66 (tynamite/itisSomeone)**. Preserve #66's existing test order and [dated main observations](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/1393d00b2f710d405384360dbbdc220f0356eaf2/research/market/substitute-validation.md). #125's ModelFit/CanIRun observations are historical bounded browser evidence, not new tests here. Flocci's remaining offline-plus-hosted-API-plus-zero-budget contradiction and save/export check require an authorized signed-in session and an actual run; no account, credit purchase or prompt was used here. #57/#58's native #66 gate remains unresolved. Broad discovery proves neither absence nor presence of an end-to-end substitute.

## Fourteen selected deep dives for #50

This proposed working list is the **13 existing historical profiles plus the already-merged CanIRun.ai profile**, with reasons for retaining each. It is not a newly completed set of profiles or an empirical vendor ranking. Existing IDs and profile paths are preserved. [appletechie's #50 disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214#pullrequestreview-5561429617) narrows acceptance to this working list after the CanIRun, CanRun, n8n and Dify corrections; that receipt explicitly leaves profile acceptance and hands-on tests with #50 and #66. zwright8's [receiving review 5561492174](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214#pullrequestreview-5561492174) at `f97aa1a2e121126d4d0cec59bd6792c04c8fb639` accepts the fourteen-entry working selection with constraints: existing IDs/paths, the 10–15 bound, staged community leads and #66's scenario/test order remain. The coordinator, other receiving decisions and full profile/evidence acceptance remain separate. This receipt does not automatically cover later heads.

| Entity / profile | Decision overlap and substitution risk | Evidence availability / source relevance |
| --- | --- | --- |
| `flocci` / `competitors/flocci.md` | Workload-first ordered stack is the strongest existing whole-workflow lead | Public docs plus dated #66 advice observation; contradiction/export gate remains |
| `modelfit` / `competitors/modelfit.md` | Device-first model choice can replace the initial fit decision | Official methodology, operator and dataset/code terms; #125 observation remains scoped |
| `llmfit` / `competitors/llmfit.md` | Hardware/runtime/quantization selection plus benchmark history | Official upstream README/API/licence; seed-domain affiliation unresolved |
| `local-ai-planner` / `competitors/local-ai-planner.md` | Goal/context/runtime/hardware planning | Public tool assumptions support #10 comparison; accuracy is untested |
| `benchlm` / `competitors/benchlm.md` | Workload/constraint explanations and reusable answer link | Official selector/method/terms; data reuse can change feasibility |
| `artificial-analysis` / `competitors/artificial-analysis.md` | Hosted model/provider comparison and recommendations | Official API/method/terms; vendor results and restricted reuse need separation |
| `openrouter` / `competitors/openrouter.md` | Model/provider choice can flow directly into execution | Official model/routing docs and terms; API access is not unrestricted reuse |
| `hugging-face` / `competitors/hugging-face.md` | Model discovery, model-card relations and versions | Primary Hub/card docs; per-content licences and metadata quality matter |
| `models-dev` / `competitors/models-dev.md` | Ready metadata may replace part of catalog research | Public repository and identifier model; provider versus canonical-model distinction |
| `harness-bench` / `competitors/harness-bench.md` | Model-harness evidence can change a recommendation | Official protocol/repository; no independent reproduction or reuse clearance |
| `dify` / `competitors/dify.md` | Build an application instead of selecting a stack | Official DSL/cloud/community docs; export/compatibility not exercised |
| `n8n` / `competitors/n8n.md` | Reusable multi-component starter composition | Official kit/API/source terms; proof-of-concept scope and component rights |
| `skypilot` / `competitors/skypilot.md` | Workload-driven infrastructure constraints and reusable YAML | Official latest reference/SDK docs; no optimizer or cloud capacity tested |
| `canirun-ai` / existing [main profile](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/1393d00b2f710d405384360dbbdc220f0356eaf2/research/market/competitors/canirun-ai.md) | Hardware plus use-case recommendations are a material fit substitute | Existing #98/#109 intake; fresh official site/README; estimates/API/licence claims unexercised |

**Exclusions:** Arena/LLM Stats overlap hosted comparison; CanRun/CanItRun overlap local fit but retain unnamed operators. They remain discovery resources, not negative capability findings. Langflow/Flowise/LlamaIndex/LangChain overlap composition and remain counterexamples without duplicating Dify/n8n profiles. GPUs.io/Vast/Runpod are infrastructure/pricing leads for #54/#39. Ollama/BentoML/Langfuse/Ragas/LM Evaluation Harness/Qdrant benchmarks/MCP Registry/Unsloth are runtime, evaluation, metadata or operations components rather than the clearest selection-flow tests. This bounds work; it does not say those products cannot substitute.

## Snowballed community resources

The six existing source IDs below were retained and rechecked from the primary-source leads raised in tynamite's [PR #67 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545) and #81. They remain staged candidates, **not extra counted registry entities**. Promoting them requires coordinated #49 matrix rows; this PR does not edit another writer's matrix or invent 288 evidence cells. The 33 registered main resources already meet the numeric bound; main plus these leads would be 39.

| Source ID / resource | Proposed existing-taxonomy classification | Fresh scope and limitation |
| --- | --- | --- |
| `src-localscore` / LocalScore | Benchmark provider; Data source; Open-source integration candidate | Official about page describes optional public submissions and single-GPU scope; no result verification performed |
| `src-localmaxxing` / LocalMaxxing | Partial competitor; Benchmark provider; Data source | Community model/hardware/engine/quantization runs and setup guide; sign-in/key needed for submission; operator/data rights unresolved |
| `src-rapid-mlx` / Rapid-MLX community board | Benchmark provider; Data source | Locked protocol and separate consent-previewed sharing documented; fresh footer says submissions CC0, unlike what the older static check saw; rights scope still needs #41 |
| `src-metrillm` / MetriLLM | Benchmark provider; Data source; Open-source integration candidate | Website timed out; repository README documents local scores, exports and public share links; no run or score validation |
| `src-openbenchmarking-llama-cpp` / OpenBenchmarking profile | Benchmark provider; Data source | Fresh retrieval error; historical bot challenge preserved. Current profile/version remains unverified; not treated as absent |
| `src-llama-cpp-perf-threads` / llama.cpp CUDA discussion | Data source | Primary thread specifies conditions and commit/driver reporting; posted results remain unverified community reports; part of llama.cpp, not another company |

Keep the fourteen-profile selection. LocalScore/LocalMaxxing may justify a fifteenth profile or a replacement if #50/coordinator decides the counterexample changes the decision; adding both would exceed 15. No scope expansion or acceptance is implied.

## Claim/evidence review and source limitations

All 32 `discovery_review` records point to dated source rechecks. Each `discovery_review.updated_fields` list identifies the top-level entity fields changed by the review dated in `discovery_review.access_date` (2026-10-18), including SkyPilot's website change. The matching source recheck supplies their evidence; the main revision above pins the previous values. This dates organization, capability, interface, licence and URL changes without implying that every field was freshly verified. Claim evidence classes attach to statements; the older source-level `evidence_grade` remains historical metadata, not a grade for every later claim. Date/version/region/confidence/rights/limitations on each recheck apply to its child claims. `last_verification` and original source access dates remain historical. No rate, feature cell or matrix evidence grade was promoted.

The original draft reports comparison of its changed operator/scope/interface/licensing statements against collected primary documents; independent review scopes are recorded in the PR. Documentary licences are qualified by component: Dify's modified Apache terms, Flowise enterprise exceptions, Unsloth library versus optional Studio/CLI, Langfuse code versus Cloud contracting terms, and MCP Registry's transition/docs terms. Source visibility or a code licence is not blanket permission for model, dataset, community-result or competing-product reuse. #41/#60 must accept intended material/use scopes. Legal ownership was not independently checked.

The correction review directly re-read [Dify's export instructions](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management), [n8n's AI Starter Kit guide](https://docs.n8n.io/deploy/host-n8n/deploy-with-the-ai-starter-kit.md), and CanRun's [About](https://canrunllm.com/about) and [privacy](https://canrunllm.com/privacy) pages. Dify may include Secret-type environment variables after confirmation; its exclusions are not a general secret-safe-sharing guarantee. The n8n component claim now cites the guide that names the four components. CanRun's data stamp is 2026-10-16; 2026-10-06 dates its privacy policy.

CanIRun's [README at `73ddc80`](https://github.com/midudev/canirun.ai/blob/73ddc80a44e1e2ffcbd5f92d6b2df04b23dfd983/README.md) states MIT, but the [root listing at that commit](https://api.github.com/repos/midudev/canirun.ai/contents/?ref=73ddc80a44e1e2ffcbd5f92d6b2df04b23dfd983) contains no LICENSE file and the [repository metadata](https://api.github.com/repos/midudev/canirun.ai) reports `license: null`, consistent with #109. No reuse grant is established. Unsloth's [root licence at `b4a4855`](https://github.com/unslothai/unsloth/blob/b4a4855e49c674f1dd375a5f716d901502b97b73/LICENSE), read through GitHub, explicitly scopes Apache-2.0 and optional Studio/CLI AGPLv3 files. The mutable web extraction omitted those lines during this review, so the claim now cites the immutable text rather than treating differing retrievals as interchangeable. These pins qualify documentary evidence, not installed versions or intended-use acceptance.

Public web extraction can serve cached text and supplies no immutable content hash; mutable default-branch documents remain unpinned. Access date means the source was read through that tool on 2026-10-18, not proof of its contemporaneous origin contents. No empirical product workflow, recommendation endpoint, compute job, score, saved configuration, licensing compliance or data provenance chain was independently reproduced. Read-only GitHub source and metadata queries are documentary checks, not product API execution. No raw result dataset, weights, personal data or large evidence download was committed.

PCPartPicker list returned 403 again (`src-pcpartpicker` recheck); no bypass or login. The original GPUs.io recheck yielded partial static home/privacy text, a loading table and failed about/terms requests. Those observations remain intact. A separate current-main correction read [the available /en/terms page](https://gpus.io/en/terms) on 2026-10-18 and reconciled its publisher-named operator/API evidence with [the merged source/use assessment](rights-validation.md). The proposed current-product exclusion and actual receiving requirements in #60/#41/#39 remain; no API was used, rate refreshed or legal ownership independently verified. OpenBenchmarking's current profile retrieval failed; MetriLLM's site timed out while its official repository was readable. These failures prove no missing capability or product absence.

## Delivery and scoped review readback — 2026-10-18

GitHub readback through **2026-10-18T05:07:00Z** records [PR #214](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214) merged to `main` at **`bf5fe18ddea9703565ed3184d73cbd8d829b741c`** on **2026-10-18T05:06:16Z**. Its submitted head was `c3ca81f33f62106ad41e982b7926c02f05b98c5b`. This is canonical delivery of partial research; #48 remains open. The earlier base, source-access dates and validation below describe that original delivery rather than a new source check in this follow-up.

| Receipt | Reviewed revision | Actual scope and remaining limit |
| --- | --- | --- |
| zwright8, [5561492174](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214#pullrequestreview-5561492174), 2026-10-18T04:54:24Z | `f97aa1a2e121126d4d0cec59bd6792c04c8fb639` | #48 → #50: accept with constraints the fourteen-entry working list. #48 → #6: narrow to discovery/context leads. No coordinator decision, full profile acceptance, product test, intended-use permission or other co-owner disposition; later heads are not automatically covered. |
| CompleteDotTech, [5561516782](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214#pullrequestreview-5561516782), 2026-10-18T05:03:35Z | `c3ca81f33f62106ad41e982b7926c02f05b98c5b` | Technical delta review finds the GPUs.io correction addressed, preserving failed retrieval history and prior observations. Does not dismiss formal requested-changes reviews or replace appletechie's review update. |
| CompleteDotTech, [5561522459](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214#pullrequestreview-5561522459), 2026-10-18T05:05:50Z | `c3ca81f33f62106ad41e982b7926c02f05b98c5b`; reported integration with main `8964a9a3e44d7131d7f4da12dbb902a8fb8b127d` | No blocker in correction/integration scope; reviewer reports preservation and validation checks. Does not verify every historical publisher claim, supply named receiving-owner acceptance or dismiss appletechie's review. |

The PR API still reported `CHANGES_REQUESTED` on the merged PR at this readback. The merge is recorded without reclassifying those formal review states. Technical resolution of a finding, an owner handoff disposition and formal review-state resolution are separate evidence. This follow-up records existing receipts and changes no issue checkbox, assignment, Project field or canonical #59 ledger entry. Its own review remains required.

## Exact receiving-owner disposition requests

PR #214's body pinned these requests to its submitted commit SHA; the receipts above retain their actual reviewed revisions. Please **accept, narrow or reject** the named slice and state conditions; a general approval is insufficient. The existing #59 writer should reconcile any resulting receipts in the canonical ledger in a separately authorized contribution.

- **#6 — zwright8, PUSHINGSQUARES:** Do the 32 identity/scope records and fourteen-profile selection support discovery/context only, with no model recommendation, capability or benchmark-quality endorsement? zwright8's [historical narrowed receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6242699859) at `7acbefbf4e4e700231e88be272bc89e3a73dde15` keeps its original scope. At `f97aa1a2e121126d4d0cec59bd6792c04c8fb639`, zwright8 additionally [narrowed this discovery slice](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/214#pullrequestreview-5561492174) to context leads only, excluding recommendations, runtime capability, measured fit, quality evidence and reuse permission. PUSHINGSQUARES remains pending; that receipt does not independently accept later correction heads.
- **#10 — Mattycodes69, appletechie:** Are the hardware-fit candidates and explicitly estimated conditions useful as methodology leads only, with no validated memory fit, error bound, runtime topology or ResourceEstimate? The author cannot supply independent acceptance; appletechie and an appropriate independent receiver must review the new slice.
- **#25 — CompleteDotTech, Mattycodes69:** Are Flocci/Dify/n8n/SkyPilot workflow/export claims and the #50 -> #66 tests the right composition counterexamples, without asserting deployment, privacy, runtime compatibility or an end-to-end substitute? Author integration is not a receiving-owner review.
- **#41 — tynamite, PUSHINGSQUARES:** Accept/narrow/reject the appended claim-level checks, qualified operator records, unchanged historical dates, and source-specific code/data/service rights boundaries. Which exact materials/intended uses remain excluded pending #60? The conditional [PR #67 provenance receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545) does not accept all new evidence or clear reuse.
- **#50 — zwright8/appletechie and coordinator CompleteDotTech:** zwright8's fourteen-selection working-list acceptance at `f97aa1a` is recorded above; appletechie's earlier conditional narrowing retains its scope. Coordinator confirmation and the original-seed uncertainty remain; any community-profile replacement/addition requires its own #50/coordinator decision. Route hands-on falsification to #66's existing owners. #49 owns any later new-entity matrix coverage. #59 co-owners retain the ledger.

## Validation of the original PR #214 contribution

Executed in an isolated current-main integration worktree with **Python 3.12.14** and the repository's pinned dependencies already installed. The original historical-base results (21 contract tests, 24 repository tests, 26 proposals and two pricebooks) remain in the original audit commit. The current integration results below apply to this corrected slice; the PR body pins its published head and tree.

| Exact command | Actual outcome |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | Exit 0; 21 tests passed |
| `python -m unittest discover -s tests -v` | Exit 0; 176 tests passed |
| `python scripts/validate_research.py` | Exit 0; 74 catalog proposals, 3 pricebooks and external evidence metadata validated |
| `python scripts/validate_market_research.py` and `python -O scripts/validate_market_research.py` | Exit 0; 33 entities, 1,584 cells, 20 issues in both modes |
| `python scripts/validate_handoff_audit.py` | Exit 0; 101 rows and 98 declared pairs; receiving acceptance is not certified |
| `python prompts/mobile/validate_prompts.py` | Exit 0; 258 issues, 36 epics, 906 criteria and 880 steps |
| `git diff --check` against the integrated main revision | Exit 0; no whitespace errors in this contribution |

An additional local audit checked all 33 main entity IDs/order/classifications/features, unchanged prices and historical dates, the byte-value-equivalent CanIRun entity, all original fields in all 58 main source records, the 40 original dated rechecks/92 claim records plus one separately appended GPUs.io terms correction with two claims (41 rechecks/94 claims total). All original observation fields remain intact; the later correction does not rewrite failed retrieval history. It also checked the 32 dated-field lists, evidence locators, source resolution and that exactly these three files differ from the integrated main. The current strict market reader rejects duplicate object keys and duplicate record IDs. These are integrity checks, not evidence acceptance.

Earlier review scopes and corrections remain in the original commits and PR receipts. The author correction and this integration preserve their source distinctions, including the dated ModelFit terms discrepancy, pending Flocci workflow test and exact named-owner disposition limits. Automation checks structure/imports/references, not factual truth, rights, freshness, independent performance, secrets absence or owner acceptance. The documentary review above is separate and remains subject to independent reviewer acceptance.


## Validation of this receipt-only follow-up

On 2026-10-18, Python **3.12.14** ran against this follow-up from merged main `bf5fe18ddea9703565ed3184d73cbd8d829b741c`. `python -m pip install -r requirements-research.txt --target <temporary-directory>` installed the pinned dependencies outside the repository; `PYTHONPATH` selected that directory and `PYTHONUTF8=1` made Windows text handling explicit.

- `python -m unittest discover -s contracts/v1/tests -v`: 21 passed.
- `python -m unittest discover -s tests -v`: 176 passed.
- `python scripts/validate_research.py`: 74 catalog proposals and 3 pricebooks validated.
- `python scripts/validate_market_research.py` and `python -O scripts/validate_market_research.py`: both passed, 33 entities / 1,584 cells / 20 issues.
- `python scripts/validate_handoff_audit.py`: passed, 101 rows / 98 declared pairs.
- `python prompts/mobile/validate_prompts.py`: passed, 258 issues / 36 epics / 906 criteria / 880 steps.
- `git diff --check`: passed. Only this rationale changes; all source, catalog, pricebook, matrix, contract and canonical handoff-ledger files are unchanged.

This follow-up compares existing authenticated GitHub review receipts and merge metadata; it adds no vendor source check or empirical result. Checks establish repository integrity, while source truth, rights, freshness, human acceptance and the remaining named owner decisions still require evidence review. No new test was added for this documentation-only reconciliation.


## 2026-10-18 catalog and summary reconciliation

**Scope and base:** one #48 writer, starting at main `637957347c54d215f9ef27f2af122a5b9129d0fd` and fast-forwarded before publication to main `4fadc44f64842f1a9a57dae5fe67674d1389def2`. The incoming changes did not overlap this contribution's five files. The live refresh found #214 and #231 already merged; the five operational seed checks and fourteen-profile rationale above are existing work. This follow-up corrects stale summaries and reconciles specific CanIRun.ai fields. It leaves all seven issue criteria, co-assignees, Project fields and native relationships unchanged.

### Documentary evidence added

Source/metadata inspection completed at `2026-10-18T08:43:59Z`. The two appended source rechecks have stable `review_id` locators; their original source entries and all earlier rechecks remain intact.

| Source record / pin | Finding used in this change | Limit |
| --- | --- | --- |
| `src-canirun-ai`, `mr01-canirun-documentary-reconciliation-20261018`; repository `73ddc80a44e1e2ffcbd5f92d6b2df04b23dfd983` | [README](https://github.com/midudev/canirun.ai/blob/73ddc80a44e1e2ffcbd5f92d6b2df04b23dfd983/README.md), [footer source](https://github.com/midudev/canirun.ai/blob/73ddc80a44e1e2ffcbd5f92d6b2df04b23dfd983/src/components/Footer.astro) and repository metadata agree on midudev attribution. README plus four route files document model-list/detail GET handlers and compatibility/recommendation POST handlers. | Source and documentary scope only; deployed revision, API availability, response correctness, browser privacy and empirical fit are unverified. No product endpoint was called. |
| Same CanIRun recheck; [complete tree](https://api.github.com/repos/midudev/canirun.ai/git/trees/73ddc80a44e1e2ffcbd5f92d6b2df04b23dfd983?recursive=1) | README states MIT; no root LICENSE file is listed, GitHub metadata reports `license: null`, and a scoped third-party licence exists under `.agents/skills/frontend-design/`. | Records a documentation discrepancy, not a legal grant or prohibition. Product and third-party data uses remain with #41/#60. |
| `src-llmfit-upstream-pages`, `mr01-llmfit-pinned-identity-20261018`; repository `e915091dd58f7fefaa9814d2d34ee61bd754fdc0` | Pinned [CNAME](https://github.com/AlexsJones/llmfit/blob/e915091dd58f7fefaa9814d2d34ee61bd754fdc0/CNAME) specifies `llmfit.axjns.dev`; [README](https://github.com/AlexsJones/llmfit/blob/e915091dd58f7fefaa9814d2d34ee61bd754fdc0/README.md) links that installer and has no `llmfit.org` reference. [MIT text](https://github.com/AlexsJones/llmfit/blob/e915091dd58f7fefaa9814d2d34ee61bd754fdc0/LICENSE) names Alex Jones; repository metadata identifies AlexsJones and an empty homepage. | A file-scoped identity check, not a repository-wide absence search, released-binary check or seed-domain ownership finding. The earlier cached CNAME observation is retained as history. |

The `canirun-ai` entity now exposes the already documented API scope, qualified creator attribution and licence discrepancy through a dated `discovery_review` naming its five changed fields. Its original `last_verification` remains **2026-10-16**; classification, feature flags, prices, entity/source IDs and the #125 observation remain unchanged. The previous audit deliberately carried this entity unchanged with a source recheck, so this is a subsequent reconciliation, not a claim that the original audit missed it.

The entry-point landscape now links the existing acceptance record, distinguishes its historical thirteen-profile reconstruction from the current fourteen-profile working list, includes CanIRun.ai in the summary inventory and uses the already-recorded SkyPilot canonical URL. Its GPUs.io text retains the original failed-access observation while pointing to the separately dated publisher correction. The profile index receives only the matching #48 rationale/supplement links; no profile or #50 decision is rewritten.

### Coverage and remaining acceptance

The inventory remains **33 entities, 58 source IDs, 14 profiles and 1,584 feature cells**. The original 32 entity discovery records are preserved and CanIRun.ai gains the thirty-third. The original 41 source rechecks/94 claims are preserved; this contribution adds two rechecks and six source claims, for **43 rechecks/100 claims**. The five operational seeds and fourteen selections are unchanged. No community lead is promoted to a new entity.

The acceptance map above remains qualified: the five working seeds have documentary evidence, but original historical intent and coordinator ratification remain separate; full historical claim review and named receiving-owner decisions are incomplete. The new source pins do not accept the #48→#6/#10/#25/#41 handoffs or #50/#66 outcomes. Exact pending scopes remain in the existing receiver questions. #59 retains the canonical ledger and its dated snapshot; no receipt is created, broadened or moved by this follow-up. #48 remains open.

### Validation of this contribution

On 2026-10-18, the integrated contribution was checked with **Python 3.12.14** in an isolated temporary virtual environment after `python -m pip install -r requirements-research.txt` installed the repository's pinned dependencies. The commands below used that environment's Python. The original contribution base also passed 21 contract tests, 348 repository tests and all four validators; those earlier results are not substituted for the integration results below.

| Exact command | Outcome on integrated main base `4fadc44f64842f1a9a57dae5fe67674d1389def2` |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | Exit 0; 21 tests passed |
| `python -m unittest discover -s tests -v` | Exit 0; 373 tests passed |
| `python scripts/validate_research.py` | Exit 0; 76 catalog proposals, 3 pricebooks and external evidence metadata validated |
| `python scripts/validate_market_research.py` | Exit 0; 33 entities, 1,584 cells and 20 issues |
| `python scripts/validate_handoff_audit.py` | Exit 0; 101 rows and 98 declared pairs |
| `python prompts/mobile/validate_prompts.py` | Exit 0; 2 Projects, 258 issues, 36 epics, 906 criteria and 880 steps |
| `git diff --check` | Exit 0; no whitespace errors |

A focused preservation check found exactly five changed files: the other 32 entity records, all entity/source IDs and ordering, original dates, classifications, feature flags, prices and prior source observations/rechecks remain unchanged. Only CanIRun.ai's five named fields plus its dated discovery record and the two appended source rechecks change the structured records. The resulting counts are 33 entity discovery records, 43 source rechecks and 100 claims. New local Markdown file and heading links resolve. No new test was added for this bounded research/documentation change.

An independent agent re-read the pinned CanIRun.ai and llmfit primary files and metadata and inspected this five-file diff. Its review found an incorrect GPUs.io source-record locator in the summary; the locator was corrected, and the follow-up review reported no remaining blocker in its changed-claim and history-preservation scope. The synchronized base leaves those reviewed changes intact. This is an independent agent review, not a maintainer approval or receiving-owner disposition. Automation checks repository integrity, not source truth, reuse rights, runtime behavior, freshness or owner acceptance. The four validators and whitespace check were also rerun after recording these results.

## 2026-10-18 seed and receipt readback

This continuation starts from accepted main `301b7c9` and preserves the prior audit and all original observations. GitHub still lists Mattycodes69 and appletechie as #48 co-assignees. A live API read found no native child or blocked-by issue for #48. The current work remains discovery research; #49's matrix, #50's profile experiments, #66's product tests and #59's canonical receipt ledger retain their existing boundaries.

### Five-seed source pass

All five operational seed sites were read again on 2026-10-18. The five appended `sources.json` rechecks have stable IDs, claim-specific primary URLs, publishers, access dates, evidence classes, versions, regions, confidence, method and rights/behavior limitations. They preserve the earlier 43 rechecks and 100 claims in place. The resulting source register has 58 source IDs, 48 rechecks and 107 claims; entity, profile and feature-cell counts remain 33, 14 and 1,584.

| Seed / recheck ID suffix | Source read and bounded result | What remains unknown |
| --- | --- | --- |
| BenchLM / `benchlm` | [Selector](https://benchlm.ai/tools/llm-selector): job description, editable constraints, dataset-based shortlist and reusable links are documented vendor claims. | Recommendation correctness, product execution and complete stack coverage. |
| Harness Bench / `harness-bench` | [Homepage](https://www.harness-bench.ai/): Harness Bench Team attribution, linked Qihoo360 repository and final-artifact scoring are documented. | Benchmark reproduction, dataset rights and legal operating entity. |
| llmfit.org / `llmfit` | [Seed site](https://www.llmfit.org/): local hardware-fit CLI/TUI and a link to AlexsJones/llmfit are documented. | Seed-domain operator and reciprocal upstream affiliation; no software was installed. |
| Local AI Planner / `local-ai-planner` | [Planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/): goal/hardware/runtime controls and explicitly heuristic estimates are documented. | Calibrated fit/speed accuracy, runtime topology and a successful workload. |
| Flocci / `flocci` | [Ask](https://aitools.flocci.in/ask), [Stack](https://aitools.flocci.in/stack) and [home](https://aitools.flocci.in/): job-to-tools/ordered-workflow claims and Flocci Technologies attribution are documented. | Actual generated workflow, constraint handling, saved/exported result and reuse permission. Ask/Stack extraction exposes only brief introductory text. |

Each recheck ID is `mr01-seed-readback-20261018-` plus the suffix above. This verifies documentary coverage of the already selected working list. It does not recover the undocumented original seed intent, create a new seed selection, promote any feature grade or establish that a complete substitute exists. The current direct-substitute answer remains **unverified**: BenchLM and Flocci document material selection/workflow overlap, while end-to-end scenario evidence belongs to #50/#66. Absence of a demonstrated substitute is not evidence that none exists.

### Actual reviews and their scope

[PR #284](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/284) delivered the later five-file catalog/summary correction to main on 2026-10-18. CompleteDotTech's [review 5562309563](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/284#pullrequestreview-5562309563) on `9854f56d41927c7a13867fb652e235487dbc871a` accepts that bounded source/history correction for normal checked delivery. It explicitly leaves original seed intent, reuse permission and other receiving decisions unresolved. It does not accept this new seed-readback contribution.

The separate [T4 receiving receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6248122696), authored by CompleteDotTech at 2026-10-18T09:15:34Z, **accepts #48 -> #25 narrowed to discovery and comparison context**. Its reviewed input was main `9192d5d6994b644ebbb81344300fda48db6d29a8`, with a byte-identical artifact check at `f0387630f00a95d3a78dfedba54abc96c8b833d0`; the reviewed competitor blob was `cdff0760ac405cc66034d3ef12cdfd29d7069e01`. It supplies no exact framework/model/endpoint/parser/tool tuple, new catalog requirement, runtime integration, source-use permission or other co-owner response.

The current-main competitor blob is `83464bb659b0c33c0fef4af439c812b38f1cff14`. A record-by-record comparison found only `canirun-ai` changed since that receipt; all ten T4-related entries are identical. This establishes preservation of the reviewed T4 slice while retaining the actual receipt's revision. It does not retroactively accept the changed CanIRun record or these new source rechecks. The receipt is linked here rather than appended to #59's separately owned canonical ledger.

### Current criterion and decision map

| Live #48 criterion | Delivered coverage / check | Remaining decision for issue completion |
| --- | --- | --- |
| Verify all five seeds | Five operational sites have fresh documentary rechecks above; earlier identity boundaries remain. | Confirm whether the documented working list satisfies the original-seed requirement. Original intent is still undocumented. |
| Classify at least 30 distinct resources | 33 distinct stable IDs and existing classifications; complete source references and matrix dimensions retained. | Independent evidence acceptance of the delivered research, without treating every entry as a complete competitor. |
| Record entity boundaries and unknowns | All 33 have dated discovery records; seed/upstream/operator, code/data/service and historical-observation boundaries remain explicit. | No missing operator or permission is filled by inference. Review the changed evidence at the final submitted revision. |
| Select 10-15 material deep dives | Fourteen-entry rationale and existing #50 co-owner working-list receipts are preserved. | Coordinator confirmation of the working selection; any community-resource replacement/addition remains a separate #50 decision. Full profile execution is not claimed here. |
| Link every significant conclusion to evidence or an explicit hypothesis | Seven fresh claims link their exact primary pages; substitution conclusions are explicitly documentary or unverified and routed to #50/#66. | Independent review of this contribution and acceptance of the landscape evidence in its stated historical scopes. No blanket re-verification of older claims. |
| Relevant owners review handoffs; unresolved decisions named | #6/#50 scoped receipts retained; actual #25 T4 receipt added above. #41 retains its earlier conditional provenance receipt. | #6: PUSHINGSQUARES; #10: Mattycodes69/appletechie; #25: Mattycodes69's separate scope; #41: tynamite/PUSHINGSQUARES on the appended provenance and intended-use boundaries. Existing #59 writer reconciles the T4 receipt separately. |
| Checks pass; reviewer accepts evidence before Done | Current Python 3.12 workflow and preservation checks are required on the submitted revision. | Required independent evidence/coordinator review and the named receiving decisions. Green checks and a partial merge do not close #48. |

The original five-seed question and the named independent reviews are external acceptance decisions. No issue checklist, assignee, priority, Project field, canonical ledger or acceptance requirement is changed by this contribution.

### Validation of the seed and receipt continuation

The worktree was fast-forwarded from `301b7c9cccaa6c5ab8a3c72be5a8dfc23893f554` to main `a46a06b7315ba10b3d469bea82795f0c200a1da3`. The incoming workflow/handoff-validator/test changes were disjoint from this two-file contribution and were read before the integrated checks. An isolated Python **3.12.12** virtual environment installed the pinned dependencies with `python -m pip install -r requirements-research.txt`.

| Exact command | Actual integrated result |
| --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | 21 passed |
| `python -m unittest discover -s tests -v` | 515 run, 512 passed, three Linux parent-death-cleanup cases skipped on macOS |
| `python scripts/validate_research.py` | 78 proposals, three pricebooks and external evidence metadata passed |
| `python scripts/validate_market_research.py` and `python -O scripts/validate_market_research.py` | Both passed: 33 entities, 1,584 cells, 20 issues |
| `python scripts/validate_handoff_audit.py` | Passed: 101 rows, 98 declared pairs |
| `python prompts/mobile/validate_prompts.py` | Passed: two Projects, 258 issues, 36 epics, 906 criteria, 880 steps |
| `git diff --check` | Passed |

A separate preservation check verified all 58 ordered source identities and original fields, all 43 prior rechecks/100 claims, exactly five appended rechecks/seven claims with unique IDs and matching claim/reviewed URLs, the unchanged ten-entry T4 slice and the local section links. The complete two-file diff was self-reviewed against the actual seven source-page claims and authenticated GitHub receipt; the review link and its numeric ID were checked against the API. No test was added for this evidence-only change. Automation checks structural integrity and references; source truth, rights, runtime behavior and independent acceptance remain separate. The final PR pins its submitted head and review state.
