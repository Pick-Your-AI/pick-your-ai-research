# Market research program synthesis

Owner: [#47](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47) (executive synthesis and program recommendation). Inputs: the evidence audit, handoff ledger and risk register owned by [#59](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59), read here without edits.

**Status: provisional draft, not accepted. Refs #47.** Repository-state refresh 2026-10-18 against `main` at `c5139f1` and live issue/PR readback. Source access dates remain those in the underlying evidence; this refresh performs no new experiment or terms check. The go / narrow / stop decision belongs to the coordinator (@CompleteDotTech) and the #47 coassignees (@tynamite, @appletechie). This note gives a provisional recommendation for them to accept, change or reject. It does not make that decision.

## How to read this note

- **Merged** means the child file is on `main`. Child deliverables #82 and #87–#97 reached `main` through PR #67 (merged 2026-10-16T23:39:05Z); #89, #98, #105 and #109 merged to `main` directly. Merged is not accepted. All twelve workstreams and seven validation issues (#48–#66) remain open. Scoped receiving responses exist; they do not establish full issue or gate acceptance.
- Anything that is not in a merged file is labelled **pending** (open PR) or **hypothesis**. PR #83 (#62) is open with changes requested, so its findings are pending. PR #110 (T5 vocabulary, #30) merged at `104eecb`; it does not establish market-gate acceptance.
- Evidence classes: observed behavior (OBS), primary documentation (PD), vendor claim (VC), independent measurement (IM), estimate (EST), hypothesis (HYP), repository state (RS).
- Live #47 assignees are tynamite and appletechie. CompleteDotTech coordinates the program; assignment and receiving acceptance remain separate.

## Inventory (repository readback, 2026-10-18)

| Item | Count | Source |
| --- | --- | --- |
| Catalogued products and resources | 33 entities | [competitors.json](competitors.json); [landscape](../../docs/market-research/competitive-landscape.md) |
| Desk profiles | 14 | [competitors/README.md](competitors/README.md) |
| Feature matrix | 48 dimensions × 33 = 1,584 cells: 123 Documented, 0 Exercised, 0 Unsupported, 1,461 Unknown | [features.json](features.json), [feature-matrix.md](feature-matrix.md) |
| Handoff responses | Historical #59 snapshot: 28 scoped responses and 53 unconfirmed rows; later receipts await the single writer's reconciliation, so these are not live totals | [risk-register.md](risk-register.md), [handoffs.md](handoffs.md) |

The catalog and matrix show broad overlap. They are research coverage, not a product score, and they do not show that no end-to-end competitor exists: 92% of matrix cells are Unknown, and silence is not absence.

## Invalidation gates

**No gate has passed.** None has failed outright either. "Open" means the full gate criteria remain unmet; a scoped interface or source-policy receipt does not pass the gate.

| Gate | State | Evidence on `main` (PR) | Class | Owner (live) | What would change the state |
| --- | --- | --- | --- | --- | --- |
| #66 direct substitute (native blocker of #57/#58) | **Open; leaning against broad differentiation.** One free Flocci Stack Builder run returned an ordered local PDF RAG workflow with constraints and uncertainty. Whether that stack runs, preserves privacy or exports was not verified. Flocci contradiction and export checks remain blocked by sign-in/credits. ModelFit and CanIRun.ai public scenarios were observed on 2026-10-17: ModelFit could not express the CPU-only Windows scenario; CanIRun.ai supplied model-fit advice rather than the retrieval stack. These bounded observations do not establish deployed behavior. | [substitute-validation.md](substitute-validation.md) (#67, [#125](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/125)); [canirun-ai.md](competitors/canirun-ai.md) (#98, #109) | OBS (bounded page interactions) | tynamite, itisSomeone | **Fails:** a substitute meets the coordinator's definition of "satisfies" in both the common and the contradictory scenario, including a reproducible, versioned record. That narrows the program to a record layer or partnership, or stops it. **Passes:** every tested substitute fails contradiction detection or per-claim traceability. |
| #60 data rights | **Partly resolved, scoped adoption recorded.** Use decisions are recorded for 10 sources; #41 adopted the restrictions and #5/#6 accepted their narrow intake scope (receipts below). **Conditional source-use decisions:** models.dev, ModelFit (CC BY 4.0), llmfit (MIT), MCP registry, Hugging Face factual identifiers, Harness Bench paper results, and GPUs.io (paid API only, not as a competing comparison service). **Not cleared without an agreement:** BenchLM, Artificial Analysis (s2.5 bars selection-guidance products) and automated OpenRouter collection. CanIRun.ai has no licence file, so no reuse grant exists. | [rights-validation.md](rights-validation.md) (#82); [integrations.json](integrations.json); canirun-ai.md (#109) | PD (reading of terms, not legal advice) | tynamite, appletechie | **Remaining:** #39, #27 and #36/#62 dispose of their rows; exact publication artifacts must retain source/use conditions. **Stop trigger:** no rights-cleared subset can support one decision. The required-source set is a coordinator decision. |
| #62 benchmark comparability | **Open.** The file on `main` is a protocol only. Pending PR #83 at `5e1b576` has CompleteDotTech's approval and appletechie's outstanding change request. Its partial desk analysis reports that no published Harness Bench harness-effect claim passes its pinning gate, and that the repository applies an LLM-judge fallback that contradicts the website. Both findings are pending and unmerged. | [benchmark-validation.md](benchmark-validation.md) (protocol); [technical-feasibility.md](technical-feasibility.md) (#105, release-count discrepancy) | PD/EST (pending) | appletechie, PUSHINGSQUARES | **Remaining:** appletechie re-reviews #83, a qualifying revision merges, and #36/#25 plus other named receiving owners dispose of their scopes. If no claim survives pinning, quality data is limited to cited, version-pinned publisher results with no cross-harness ranking. |
| #61 sizing reproducibility | **Open.** The repository has 15 successful dense CUDA runs, covering 5 configurations of SmolLM2-135M on one RTX 5070 Ti, with 0 runtime errors or OOMs. There are 0 comparable competitor/runtime pairs, so no estimator error range exists. MoE and multi-GPU cases have not been run. | [sizing-validation.md](sizing-validation.md), [mr09-acceptance.md](mr09-acceptance.md), technical-feasibility.md (#79/#80 via #67; #105) | IM (bounded) | Mattycodes69, appletechie | **Passes:** comparable pairs exist with an error bound the coordinator accepts for the target architecture, or the owners review and narrow the scope. **Scope change:** the required runtime or placement cannot be represented. |
| #63 paid demand | **Open, awaiting a coordinator decision.** The repository has an approval package only. No one has been contacted. Decisions D-01 to D-17 and thresholds T-1 to T-5 are unset. | [customer-validation.md](customer-validation.md), [customers.md](customers.md) (#92) | HYP | zwright8, appletechie; approval by CompleteDotTech | **Moves:** the coordinator approves the package and sets T-1 to T-5 before the first interview. **Stop or narrow:** disconfirming results T-1 to T-6 hold. |
| #64 pricing (supporting gate) | **Open; partial, not accepted.** The file on `main` now contains the desk recheck of all 13 captured rates (13 match, 0 drift on 2026-10-17) and two scenarios that stay incomplete because of uncovered meters. | [pricing-validation.md](pricing-validation.md) ([PR #112](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/112), merged 2026-10-17; checked 2026-10-17) | RS | appletechie, PUSHINGSQUARES | **Moves:** dated region, currency and unit rates with idle, storage and egress costs, accepted under #39 semantics. Without these, the record shows cost units and gaps, not a comparison. |

The gates do not all carry the same weight. #66 and #63 decide whether the program continues. #60, #61, #62 and #64 decide what a bounded record is allowed to show.

## Findings by workstream

All files below are merged drafts awaiting owner acceptance.

- **#48/#49 landscape and matrix:** 33 entities. Matrix cells were re-graded to Documented/Exercised; there are no Exercised cells. Flocci and ModelFit are classed as direct competitors, and llmfit, BenchLM and Artificial Analysis overlap the entry workflows ([landscape](../../docs/market-research/competitive-landscape.md), [feature-matrix.md](feature-matrix.md); PD/VC).
- **#50 deep dives:** the 14 profiles deliberately include products that weaken differentiation. Explanation, version identity and reproducible export already exist, but in separate products: explanation in recommenders, version identity in metadata hubs, export in workflow tools ([competitors/README.md](competitors/README.md); PD/OBS).
- **#51 PCPartPicker:** robots.txt disallows AI-agent fetchers and sets `ai-input=no`, so no product page was observed. All five UX transfer ideas (H1–H5) remain hypotheses, and the proposed requirements go to #40, #42 and #39 ([pcpartpicker.md](pcpartpicker.md); PD).
- **#52 customers:** the ten segments are hypotheses. In the Stack Overflow 2026 sample, 52.1% rate source attribution very important and 48.0% trust AI output "when I can easily verify" it. This supports investigating verifiability. It is not demand ([customers.md](customers.md); PD, self-selected developer sample).
- **#53 sizing:** the scenarios use assumption inputs only. Reach and conversion dominate the result: conversion alone spans 80×. #2 rejected the scenarios as a workload input, so they are context for this note only ([market-sizing.md](market-sizing.md); EST). Paid demand is unmeasured.
- **#54 monetization:** the best-supported structure is a neutral free core plus a team subscription for versioned builds and evidence review, with labelled referrals and no paid ranking. All of it is untested ([monetization.md](monetization.md); HYP). Its rejection conditions depend on #63 and #60.
- **#56 feasibility:** traceable, assumption-explicit screening is technically plausible. Fit advice must name the artifact, runtime, context, KV cache, active sequences and topology. Validated fit accuracy, savings or quality ranking are not established ([technical-feasibility.md](technical-feasibility.md); IM/AJ).
- **#57 differentiation:** "users lack model or fit tools" is falsified. Simple guided stack advice is not distinctive. H5 (versioned outcome history) is falsified as stated for single-model inference throughput by LocalScore, Rapid-MLX and similar projects. Still open: H1 (traced compatibility advice), H3 (a versioned shared record that someone else can reconstruct) and H5b (stack-level outcomes). Historical D-57-1…7 outcomes are not retrospectively scored; the 2026-10-18 prospective follow-up protocol supplies choices only for new observations ([differentiation.md](differentiation.md); HYP).
- **#58 MVP:** the six launch approaches are rated by analyst judgement. The conditional choice is a hybrid local-versus-API decision for one workload, with a shareable versioned record. tynamite accepted the #58 → #2/#3/#40/#42 mapping with one narrowing: apply the #75 conflict order before marking a value unknown ([mvp-analysis.md](mvp-analysis.md); AJ/HYP; #58 remains blocked by #66).

## Scoped receiving receipts (read back 2026-10-18)

- [#60 source-policy handoff, 2026-10-17](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6235704731): #41 adoption is recorded; other rows remained requested.
- [#5/#6 metadata restriction receipt, 2026-10-17](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60#issuecomment-6242698806): bounded source/date/use acceptance, not a new legal grant or permission to collect.
- [#7/#11 accounting interface receipt, 2026-10-17](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6242699281): methodology/interface only; empirical coverage, comparator pairs and #10 placement remain open.
- [T5 ledger mapping and single-writer coordination, 2026-10-17](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6230504818) and [scoped audit/author dispositions](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6242699859): preserve information-only T5 use, original attribution and Mattycodes69's ledger ownership. These receipts are not blanket acceptance of later artifacts.

## Go / narrow / stop

| Option | Evidence for | Evidence against |
| --- | --- | --- |
| **Go** (broad T0–T6 builder) | Adoption is broad and growing (A1, A4, A8, A10 in market-sizing.md). Developers report trust conditional on verification (customers.md). | No gate has passed. Paid demand is unmeasured. Entry workflows are crowded (Flocci, ModelFit, llmfit, CanIRun.ai). Rights exclude BenchLM, Artificial Analysis and automated OpenRouter data. Sizing has no error range. Benchmark comparability is unresolved. The full stack has the largest maintenance surface (mvp-analysis.md). **Not supportable.** |
| **Narrow** (bounded hybrid decision record, rights-cleared sources) | A rights-cleared subset exists (rights-validation.md). Bounded screening is plausible (technical-feasibility.md). H1, H3 and H5b are still open, and no reviewed product combines rationale, per-claim source, version pin and declared unknowns in one record. That is absence of public evidence, not proof (differentiation.md). The owner accepted the hybrid mapping (mvp-analysis.md). | Every distinction is a hypothesis. The cleared subset is thin on quality data and largely consists of competitors' own datasets (ModelFit, llmfit). One Flocci run already shows constraint-aware advice with stated uncertainty. #63 has not started. |
| **Stop** | Guided output is not distinctive (OBS). H5 is falsified. Several key data sources need agreements. Nothing measures paid demand. | No substitute has been shown to satisfy the scenario end to end: the additional ModelFit/CanIRun observations are bounded, and Flocci contradiction/export tests remain unavailable. No disconfirming demand evidence exists, because demand has not been measured. Stopping now would act on an untested gate. |

## Provisional recommendation (for coordinator decision)

**Narrow, framed as narrowing the remaining validation rather than authorising a product.** Continue research on one bounded hypothesis: a hybrid local-versus-API decision for one named workload. The record shows rationale, per-claim source and date, version pins and declared unknowns, and uses only sources cleared for the intended use in rights-validation.md. No gate has passed, so this is a decision to keep testing a narrow wedge, not a go.

This note partly departs from the framing "narrow: bounded hybrid workflow on rights-cleared sources only, no gate passed":

1. **"Narrow" can be misread as a narrowed build.** The evidence supports narrowing the *research* scope, not committing to an MVP. #58 cannot be accepted before #66, and nothing about demand is known.
2. **Source-policy adoption is not artifact clearance.** #41 adopted the restrictive #60 decisions; #5/#6 accepted their bounded metadata intake scope. Remaining consumers and exact publication uses still need their own dispositions. Several cleared datasets (ModelFit, llmfit) belong to the direct substitutes, so a rights-cleared record risks repackaging them. Treat "record layer on top of, or in partnership with, an existing substitute" as an equal variant, not a fallback (mvp-analysis.md section 2).
3. **Sequence the decisive gates first.** #66 (H1 and H2 scenarios plus the H3 round trip) and #63 (approval plus T-1 to T-5) determine whether to continue at all. Bring #61, #62 and #64 forward only for the chosen workload, so that narrowing does not turn into broad content collection.

## Reversal conditions

The coordinator should set each threshold before reading the result it applies to (D-57-n, T-n).

- **Narrow → stop:** a #66 substitute passes H1 and H2 in both the common and the contradictory scenario and produces a reproducible, versioned record. Or #63 results meet the disconfirming criteria T-1 to T-5. Or no rights-cleared source set can support one decision.
- **Narrow → record-layer or partnership variant:** a substitute passes the common scenario but fails contradiction detection or traceability. Or a Dify, n8n or SkyPilot manifest reaches the D-57-3 reconstruction-parity threshold (differentiation.md kill/pivot table).
- **Narrow → go (wider scope):** #66 shows that all tested substitutes fail H1. #63 shows recurring multi-component decisions with a named payer above the thresholds. #61, #62 and #64 are accepted for the target workload. Even then, widen one tier at a time.
- **Scope change within narrow:** #61 cannot represent the required runtime or placement, which limits fit to dense, single-device, assumption-explicit screening. Or #62 finds no claim that survives pinning, which means cited results only and no ranking.

## Decisions required

- **Coordinator (@CompleteDotTech):**
  - Approve, change or reject the #63 package (D-01 to D-17) and set T-1 to T-5 before any contact.
  - Use the prospective #57 protocol only for new follow-up results; preserve unscored historical observations. Resolve any remaining #58 product-gate decisions before judging new evidence.
  - Review the operational five-seed scope recorded in the landscape; preserve unverified operator identity and receiving-review limits.
  - Choose the #51 walkthrough option: (a) a human public walkthrough, (b) an authorized account walkthrough, or (c) accept the narrower scope.
  - Preserve Mattycodes69 as the explicit active #59 ledger writer; reconcile newer scoped receipts without changing historical attribution.
  - Dispose of Mattycodes69's #79 → #58 handoff.
  - Accept, change or reject this provisional recommendation together with the #47 coassignees.
- **Owners:**
  - #41 maintains its adopted #60 source restrictions; changed terms or uses require a fresh decision.
  - #39 decides on the GPUs.io condition and the #64 economics.
  - #62/#36 resolve PR #83.
  - #10 decides ResourceEstimate placement/consumption; preserve the bounded #7/#11 interface receipt without inferring empirical completion.
  - #66 completes its protocol.
  - The receiving owners address outstanding rows after the #59 writer reconciles the historical 53-row count with later receipts.

## Not claimed

- No program decision, MVP choice, implementation, deployment, outreach or paid-compute authorization.
- No paid demand, willingness to pay, conversion, CAC or market size. The sizing scenarios are assumptions.
- No new acceptance of a child workstream, handoff or gate by this refresh. Existing scoped receipts retain their limits; "merged" does not mean accepted.
- No verdict that a direct substitute satisfies, or fails, the MVP scenario.
- No legal clearance. The rights decisions are readings of published terms.
- No calibrated fit accuracy, benchmark ranking, cost comparison or savings.
- No findings from pending PR #83 are promoted to accepted evidence; #110's merge supplies no market-gate acceptance.
- No absence inferred from Unknown matrix cells or from missing documentation.
