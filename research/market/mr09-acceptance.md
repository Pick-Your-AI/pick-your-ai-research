# MR-09 acceptance and remaining gates

Issues: [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56), [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61). Research date: 2026-10-16. Submission uses **Refs #56; Refs #61**. Neither issue is complete.

Review submission: **[PR #79](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/79)**. [Posted owner requests](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/79#issuecomment-6217452110) cover all 13 required receiving-owner rows; six external reviewer requests were verified by GitHub readback. **Accepted dispositions: 0.** The [#58 handoff](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/58#issuecomment-6217454289) is posted and remains pending coordinator review. Detailed request/response records are in [handoffs.md](handoffs.md).

## Refreshed baseline and branch dependency

[Sanitized live snapshot](mr09-baseline.json) records GitHub issue ownership, native relationships, exact criteria and PR reviews. GitHub metadata is observed repository state, not accepted research. #56/#61 remain assigned to **Mattycodes69**. #62 belongs to **PUSHINGSQUARES** and #65 to **zabyxc01**; both are open. #58 has no live assignee; **CompleteDotTech** coordinates its decision rather than being silently assigned here.

This submission is deliberately **stacked on PR #67** at `075653aa4c0682c976ea9486d7d549d667118530`, targeting `research/market-intelligence` from `codex/mr09-feasibility-validation`. Its existing deliverables, shared tracking history, methodology and `scripts/validate_market_research.py` are real editing/validation dependencies. No wholesale copy or merge of #67 was added to obtain references. Once #67 merges, rebase this focused change onto the accepted base and retarget to `main`; revalidate if conflicts or behavior change. The refreshed `origin/main` is `d4bdca4` (MIT-license addition after #67's base); this is disclosed rather than importing unrelated changes.

PR #75 at `9e66622a4b2698a9305274f05da9c15ae5d90b8c` is a **pinned reference only**, with no merge dependency. Its GPU, engine, sizing-example, handoff and contract-proposal records were read through that ref. They remain unmerged proposals. The arithmetic and synthetic examples are not runtime measurements, accepted compatibility rules or calibration evidence. Neither PR had a submitted review in the baseline readback.

The frozen v1 schemas were inspected, particularly CatalogItem, ResourceEstimate, CostEstimate and the separate evidence-manifest schema. Findings remain notes: no complete new component/price records are needed, and #10 has not agreed to a ResourceEstimate consumer or placement. Contract/rule changes still go through #40; #39 retains cost semantics.

## Criterion-by-criterion matrix

Criteria below are verbatim from the live issue bodies, also retained in the snapshot. **Prepared** means an artifact exists; **measured** requires real execution with matching instrumentation; **reviewed** requires a review of this submission; **accepted** requires the designated human disposition. Agent quality review is recorded separately in [validation](mr09-validation.md). A requested review never fills an acceptance cell.

| ID | Live criterion (verbatim) | Artifact / section and evidence | Required human reviewer | Current stage | Remaining action |
| --- | --- | --- | --- | --- | --- |
| 56-1 | Compare sizing assumptions | [Feasibility](technical-feasibility.md), dated estimator comparison and primary-source ledger | Mattycodes69; CompleteDotTech | Prepared for review; empirical calibration pending | Review source pins, estimator identities and unlike-unit/quantity limitations |
| 56-2 | Assess context cache concurrency and multi-GPU limits | [Feasibility](technical-feasibility.md), comparison/risks; [protocol and results](sizing-validation.md) | zwright8; Mattycodes69 | Prepared; dense subset measured in 15 runs; human review pending | Accept context/cache/active-sequence semantics and retained MoE/multi-device gaps |
| 56-3 | Define falsifiable measurement protocol | [Sizing validation](sizing-validation.md), dated protocol, matrix, comparison and failure semantics | Mattycodes69; zwright8; CompleteDotTech | Prepared; human protocol review pending | Review bounded coverage, instrumentation, isolation and comparison eligibility |
| 56-4 | Reuse technical component decisions rather than duplicate them | [Feasibility](technical-feasibility.md), pinned T2 reuse; baseline dependency above; [handoffs](handoffs.md) | Mattycodes69; affected consumers | Prepared; proposed T2 evidence distinguished from accepted decisions | Confirm scope and reconcile T2 owner decisions as #75 is reviewed |
| 56-5 | Deliverable links every significant conclusion to evidence or an explicit hypothesis. | [Feasibility](technical-feasibility.md), source and risk ledgers; [sizing evidence](sizing-validation.md) | CompleteDotTech | Prepared; agent audit does not establish human acceptance | Check claim support, dates, rights, observed/source-derived distinctions and unknowns |
| 56-6 | Relevant technical owners review handoffs; unresolved decisions are named. | [Handoff ledger](handoffs.md), MR-09 dated dispositions; [structured ledger](handoffs.json) | #7/#10/#11/#16/#25/#27/#33/#36/#39/#40 live owners | Pending human review; zero accepted dispositions | Each receiving owner accepts, narrows or rejects precise offered scope with a review link/date |
| 56-7 | Repository checks pass; reviewer accepts the evidence before Done. | [Validation](mr09-validation.md); this matrix; PR review/merge | CompleteDotTech; maintainers | Automated results recorded separately; human acceptance and merge pending | Accept evidence, satisfy handoffs and all children, merge through normal review |
| 61-1 | Design dense and MoE measurement matrix | [Sizing validation](sizing-validation.md), bounded dense/MoE coverage | Mattycodes69; zwright8 | Prepared; executed cells identified separately | Review design; execute missing architecture/boundary cases on authorized hardware |
| 61-2 | Vary context cache precision and concurrency | [Sizing validation](sizing-validation.md), actual-versus-planned cell ledger | zwright8; Mattycodes69 | Measured dense: 5 configurations × 3 repetitions; MoE variations unexecuted | Review dense coverage; complete missing MoE variations when spare-capacity guards permit |
| 61-3 | Measure peak allocated and reserved memory | [Sizing validation](sizing-validation.md), synchronized per-phase allocated/reserved counters and result ledger | Mattycodes69 (#10/#11) | Measured for the explicitly executed dense configurations; full coverage and human review pending | Review counter semantics and complete missing MoE/boundary/per-device evidence on authorized spare capacity |
| 61-4 | Report error bounds and failures without universal fit claims | [Sizing validation](sizing-validation.md), error/failure policy, actual counts and payload sanity check | Mattycodes69; CompleteDotTech | Observed dense counters; comparable competitor/runtime pairs = 0, error range unavailable | Obtain comparable positive pairs or owner-reviewed narrowed scope; retain mismatch, failure and unexecuted categories without invented errors |
| 61-5 | Deliverable links every significant conclusion to evidence or an explicit hypothesis. | [Sizing validation](sizing-validation.md), local inventory and pinned-source ledger | CompleteDotTech | Prepared; review pending | Audit reproducibility, source rights, measurement validity and coverage limits |
| 61-6 | Relevant technical owners review handoffs; unresolved decisions are named. | [Handoffs](handoffs.md), #61 to #7/#10/#11 | zwright8; Mattycodes69 | Pending human review; zero accepted dispositions | Record explicit consuming-owner responses, including internal T2 acknowledgement |
| 61-7 | Repository checks pass; reviewer accepts the evidence before Done. | [Validation](mr09-validation.md); PR review and merge | CompleteDotTech; maintainers | Automated results recorded separately; evidence acceptance and merge pending | Complete empirical criteria, confirm handoffs, accept evidence and merge |

## Additional parent-completion gate

| Child | Live owner / status | Evidence available to integrate | Exact remaining owner action |
| --- | --- | --- | --- |
| #61 | Mattycodes69 / open | This submission; execution and counter coverage are explicitly bounded | Complete missing qualifying dense/MoE observations, secure #7/#10/#11 acceptance and evidence review, merge |
| #62 | PUSHINGSQUARES / open | Existing protocol only; release-identity desk observation in [handoffs](handoffs.md) | Reconcile v2 landing metadata106 versus v2 body/current300 and v1/v2 task/result identities; pin model/harness/budget/task versions, check contamination and overlap, separate mean score from complete delivery, record replication limits and obtain #25/#36 acceptance |
| #65 | zabyxc01 / open | Existing protocol only; no reviewed interoperability results | Check embedding dimensions and metrics, API/auth boundaries, and successful end-to-end workloads separately from connector existence; obtain retrieval-owner and affected #25/#27 review |

Completion of #61 alone cannot complete #56. No waiver is inferred. #56/#61/#62/#65 have no native blockers in the refreshed readback. These are acceptance, access and information gates, not authorization to invent blocking relationships. #58 retains its existing native blocker #66.

## Executed coverage and remaining experiment action

[Sizing-validation results and reproduction](sizing-validation.md) and the [machine-readable summary](measurements/mr09-results-summary.json) contain **15 successful real CUDA runs**, five dense configurations with three fresh processes each. All use pinned SmolLM2 BF16 weights on one RTX 5070 Ti. There were **0 model-runtime errors and 0 observed OOMs**. Administrative wrapper errors and missing pilot preflight metadata are recorded separately; they are not inference failures.

| Cell | Prompt tokens / active sequences | KV | Successful runs | Prefill peak allocated min = median = max (MiB) | Prefill peak reserved min = median = max (MiB) |
| --- | --- | --- | --- | --- | --- |
| D1 | 256 / 1 | BF16 | 3 | 279.472 | 298 |
| D2 | 2,048 / 1 | BF16 | 3 | 681.265 | 736 |
| D3 | 2,048 / 2 | BF16 | 3 | 1,083.298 | 1,178 |
| D4 | 2,048 / 1 | INT4 + metadata/residual | 3 | 650.421 | 690 |
| D5 | 2,048 / 2 | INT4 + metadata/residual | 3 | 1,018.517 | 1,078 |

MiB = 2^20 bytes; table values are rounded, with raw byte counters and every phase in the result files. Identical peaks across three observations are not a guaranteed bound. Native BF16 KV tensor-payload arithmetic matched the observed tensor layout in nine runs (0% signed relative payload error); this is a layout check only. **Comparable competitor/runtime pairs = 0; competitor error range is unavailable.** No total-memory estimator is calibrated by these data. The estimator source audit explains the missing model/runtime/input/quantity matches.

The user explicitly selected **spare local capacity only**. Original OLMoE rows remain unexecuted. A Granite3.0 candidate failed the chosen temporary-volume disk guard; no machine-wide lack of disk is inferred. A smaller official Granite3.1 BF16 profile passed its RAM/disk screens but failed its unchanged GPU guard twice. The [final observation](measurements/mr09-granite31-preflight-final.json) at 22:06:50 Asia/Shanghai (14:06:50 UTC) reported **3,935 MiB free < 4,096 MiB required**. No MoE weights were downloaded, no unrelated workload was altered, and task-created dense-model/package downloads were removed with readback.

**Exact remaining experiment action:** Mattycodes69 may execute the separately pinned Granite3.1 short case only when the same predeclared spare-capacity guards pass (GPU ≥4,096 MiB reported free, available host RAM ≥12 GiB, temporary storage ≥6,412,308,016 bytes, own allocator cap ≤3 GiB). That short case cannot stand in for the remaining OLMoE context/KV/concurrency matrix. Review the protocol before extending to those cases; a second authorized GPU and per-rank/topology instrumentation are required for the multi-GPU row. No paid compute or provisioning was used or requested. If existing owners propose narrowing the accepted scope, that requires an explicit human disposition; no waiver is invented here.

## Project state: precise pending administrator action

The authenticated API rejected Project queries because the token lacks `read:project`. A read-only computer-use fallback returned an empty enabled-surface inventory (`apps: []`, `browsers: []`), so no already-authorized browser session was available either. No Project values or actual field options were refreshed or written. `project-configuration.json`, `research-backlog.json` and issue prose are historical snapshots, not live board readback. Preserve priorities, labels, hierarchy, assignees and unrelated fields.

Project administrator / CompleteDotTech must read actual Project #2 options and current items for #56 and #61, link the MR-09 review PR, and set **Status to the existing In Review option** for this open research submission if that option is still present. This is a pending update, not an applied value. Preserve priority, assignees, labels, hierarchy and confidence; protocol preparation or supplementary runtime observations cannot establish calibration. Reconcile readiness against the exact remaining coverage/owner actions below using the actual field options, distinguishing experiment access from independently startable desk/review work. Read back every applied value. No `Done` update is appropriate while criteria, children, acceptance or merge remain unmet.

## Completion verdicts

**#61: incomplete.** A pinned protocol and 15 successful dense CUDA allocator observations are available. MoE/multi-GPU coverage, matching competitor comparisons or explicitly reviewed scope decisions, receiving-owner acceptance and merge remain unmet. No synthetic result, process/device memory trace or CPU inference substitutes for allocated/reserved GPU peaks.

**#56: prepared research, incomplete acceptance.** The conditional desk assessment can be reviewed now. Empirical limitations, #62/#65 child completion, receiving-owner decisions, coordinator evidence acceptance and merge remain gates. No product implementation or deployment is authorized by this submission.
