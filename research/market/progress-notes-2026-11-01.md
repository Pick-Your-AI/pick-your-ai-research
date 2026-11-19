# Progress notes: #52, #56, #62 (and #63 status)

Refs [#52](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52), [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56), [#62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62), [#63](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63). Status: **proposed status notes for owner review; not accepted evidence.** Originally compiled 2026-11-01 from historical `fef30de` and issue readbacks; reconciled 2026-11-19 against accepted source `d58106750bb76f72c270653993edf808f29c49bb` and the public decisions linked below. Original observations retain their dates. Live issue text, assignees and Project fields are authoritative; this note changes none of them and records no new research. Program context: [program-status-2026-11-01.md](program-status-2026-11-01.md).

## #52 MR-05 Customer Research & Personas (open)

**Current state.** All seven original criteria are checked. The desk deliverable (ten segments, evidence-qualified JTBD, neutral interview protocol, persona-versus-customer distinction) was completed 2026-10-18 with independent reviews and five bounded technical receiving decisions ([comment 6250471522](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6250471522)). Personas remain desk hypotheses from a self-selected developer sample (Stack Overflow 2026); they supply no demand, rate or willingness-to-pay figure.

**Done.** [customers.md](customers.md); [#67](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67) initial; parent-completion-gate clarification [#433](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/433); instrument status reconciliation [#494](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/494); interviewer-conflict design and channel-rule limits [#501](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/501) (delivered 2026-10-20; historical contribution).

**Left.** The issue's "Next action" is to maintain the dated desk record as sources change. The parent stays open because its child #63 retains distinct operational work; the [accepted parent-completion correction](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6255561527) and [delivered clarification](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/52#issuecomment-6256905161) require #63 completion. The seven accepted desk criteria do not waive that gate.

## #56 MR-09 Technical Feasibility (open)

**Current state.** All seven #56 criteria are checked at their recorded scope. #56 stays open for two unfinished native children: #61 (three empirical criteria) and #62 (one pinning criterion). #65 (RAG interoperability) is closed.

**Done (merged).**

| Item | PR / path |
| --- | --- |
| Benchmark desk slices | [#83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83), [#213](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/213) |
| 15 historical dense CUDA runs (D1-D5 x 3) | [measurements/mr09-D*-r*.json](measurements/), [mr09-results-summary.json](measurements/mr09-results-summary.json) |
| 3 short Granite3.1 GM1 runs | [#251](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/251), [measurements/granite31-2026-10-18](measurements/granite31-2026-10-18) |
| 12 two-byte KV payload component pairs | [#252](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/252) |
| Duplicate-JSON-key parser integrity | [#254](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/254) |
| Prepared total-buffer proposal (execution disabled) | [#259](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/259) |
| Hardware-requirements accounting and cohort guard | [#200](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/200) |
| Receipt-preservation delivery | [#381](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/381) |
| 3 H1 initialization-buffer observations (separate bounded cohort) | [#474](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/474), [#476](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/476), [measurements/local-comparison-2026-10-19](measurements/local-comparison-2026-10-19) |
| OLMoE artifact/copy preparation (no weights downloaded) | [#499](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/499), [#502](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/502), [#503](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/503) (M4 cache observations prepared, unexecuted) |
| Native validation receipt type fix | [#514](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/514) (2026-10-29; historical contribution, not a current-main claim) |

**Left.** Whole-runtime peak-allocated estimator pairs remain **zero**. Varied MoE (OLMoE M1-M4), long-context and multi-GPU cells are unexecuted and need authorised hardware. Receiving-owner decisions for #7/#10/#11 are recorded at their bounded scope. The [coordinator decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6367324704) retains the full M1–M4, long-context and G1 scope without device or launch authorization. G1 remains unmet. Execution plan draft: [execution-plan-61-draft.md](execution-plan-61-draft.md). The historical [#508](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/508) plan-reader contribution retains its own delivery/validation records; it is not a missing empirical result.

## #62 MR-09 Benchmark comparability (open)

**Current state.** Six of seven criteria are checked (6/7, live issue re-read 2026-11-01); the unchecked one is "Pin models harnesses budgets and task versions". Gate state per [synthesis.md](synthesis.md): G1 pinning fails, G3 statistical support Unknown. **No replication is selected under #62**, so its experiment cost is not applicable (not zero).

**Done.** [benchmark-validation.md](benchmark-validation.md) via [#83](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/83), [#189](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/189) (pooled-vs-general table scope; mean vs full-credit), [#204](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/204) and [#213](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/213) (public release/result audit, 2026-10-18); five bounded receiving decisions for #25/#36/#39/#40/#41 ([6251565503](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25#issuecomment-6251565503), [6253421648](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62#issuecomment-6253421648)); background literature note [benchmark-validation-approaches.md](benchmark-validation-approaches.md) via [#510](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/510) (2026-10-25; proposed background, not accepted evidence).

**Left.** Evaluated model/grader identities and immutable published-run bindings remain missing; accepting the negative audit does not meet the literal criterion. Paired-result and dependence inputs for a ranking claim also remain missing. The contamination/task-overlap desk criterion and all five bounded receiving decisions are already accepted; do not reopen those gates or infer a missing co-owner reply. Rights: the inspected Harness-Bench repository has no detected repository-wide licence, and its tasks/trajectories are distinct from the separately licensed paper ([rights-validation.md](rights-validation.md)). The [existing publisher request](https://github.com/Qihoo360/harness-bench/issues/2#issuecomment-6265127285) remains the input route; a 2026-11-19 GitHub-only readback returned no later answer. That readback is not a refreshed paper, website or task audit.

## #63 MR-05 Customer demand and willingness to pay (open)

The [2026-11-01 co-owner decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/63#issuecomment-6564695884) approves **D-01, D-02, D-06, D-07, D-09 and D-16 as drafted**. It authorizes no recruitment, posting or fieldwork and reports no participant contact. The approval does not supply the placeholders' actual values.

Still required before any contact: the actual contact address; applicable lawful-basis choice and final rights wording; actual private store, encryption and access list with demonstrated deletion/expiry across controlled copies; and a named interviewer/conflict disclosure. Final outreach/screener/consent wording and the recipient list or channel need the approving co-owner's separate review. Reddit remains blocked until its rules are read and recorded; the paid panel remains excluded under unpaid D-05; cold DMs and bulk messages remain forbidden. No contact is permitted in the current task.

The decision reports Project Status Ready, Research Readiness Needs Input and Dependency Status Unblocked at its own cutoff. Those values were not freshly read back for this reconciliation and are not changed here. The eleven selected instrument choices, all historical decision rows and receipts, and four incomplete operational/participant acceptance criteria retain their scope. Paid demand remains Unknown; #63 and native parent #52 remain open. See the [canonical dated reconciliation](customer-validation.md#approval-reconciliation--2026-11-19).
