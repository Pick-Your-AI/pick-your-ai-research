# T2 handoffs and follow-up ledger

Original intake: 2026-10-16; scoped receipt reconciliation: 2026-10-18. The required-consumer table lists live coassignees checked on the latter date. A receipt credits only its author, direction and stated interface; it does not imply every co-owner approved or that all acceptance criteria are met.

The original continuation audit re-read the scoped and consuming issue comments plus PR #75 reviews and inline comments on 2026-10-16 and found no acknowledgments then. On 2026-10-17, the T4 receiving owner supplied the scoped #9 -> #27 and #11 -> #25 dispositions linked below. That paragraph describes the original audit; the dated reconciliation below supersedes its receipt status. Existing review requests and issue requests are retained without duplicate reminders. Parallel contributor review is not a consuming-owner decision.

## Receipt reconciliation (2026-10-18)

Live issue comments confirm the T4/T5 receipts and Mattycodes69's explicit [Hosting](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225), [Compute](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057) and [Engine](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677) dispositions against main `9344f99325510adfe678382a4672246d028e87bc`. At that earlier readback Hosting had scoped receipts for #10/#27/#31 (three of seven required interfaces), Compute for #9/#11/#31 (three of four), and Engine for #10/#25/#33 (three of five at that earlier readback). #28 is an additional Hosting boundary receipt, not an eighth original dependency. Other receiving-owner and co-owner decisions remain separate. No reverse-direction T5 acceptance, runtime result, headroom default or final rule approval follows.

A later 2026-10-18 [@appletechie receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245668428), reviewing main `66b46d4`, covers #11 → #37 as **accept, integration pending** and #11 → #38 as **narrow** to labels/evidence inputs pending exact-release signal reconciliation. That historical receipt retains its scope. [@PUSHINGSQUARES's subsequent receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868), checking main `9192d5d6994b644ebbb81344300fda48db6d29a8`, **confirms #37 with constraints** after the #246 map was delivered and **narrows #38** to the stated evidence inputs; it does not turn evidence-record fields into metric labels or accept actual exposition. The [#10 co-owner receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221) separately accepts #11 → #10 with constraints. The lifecycle recommendation and exact reviewed revisions are in [the engine record](inference-engine.md#version-retention-and-bounded-candidate-recommendation--2026-10-18); @zwright8's recorded concurrence does not supply @Mattycodes69's or #42's receiving decision.

## Required consuming-owner confirmations

The #9 → #37 hosting linkage requested in [appletechie's receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047)
was subsequently delivered in [#247](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/247),
merged at `31467ea945ea01bd9e9f48eaa8c87497d58a0caf`.
The [three-group map](../T6-deployment-operations/deployment.md#hosting-rule-to-step-linkage-proposal-2026-10-18)
links offering membership to S1/S17/S28, private-network capability to S10/S45,
and mounted-storage locality to S43/S50. [Source review 5561644402](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/247#pullrequestreview-5561644402)
records its independent documentary review. The earlier receipt keeps its
`66b46d4` pin. [PUSHINGSQUARES's actual later response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6247689488),
reviewing `9192d5d`, confirms its responsibility, artifact, network and region
inputs and separately narrows the #39 cost interface below. That response
explicitly leaves receiving review of the map and appletechie's separate scope
open. No selected deployment or final ruleset is accepted.

| Producer | Consumer | Current consuming owner | Artifact / confirmation requested | Acknowledgement evidence |
| --- | --- | --- | --- | --- |
| #9 | #10 | @Mattycodes69, @appletechie | Hosting IDs, EC2 profile binding, regional availability unknowns | Historical state: [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057): dated EC2 host/profile binding; stock/quota unknown. [Actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362`: Current host/profile reuse is accepted with constraints; stock, quota, price eligibility and workload fit are not inferred. |
| #9 | #14 | @zabyxc01, @PUSHINGSQUARES | Managed embedding endpoint hosting category and residency boundary | Historical state: Pending. [Actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362`: The current pinned-artifact/hosted-alias hosting interface is accepted with constraints after independent technical receiving review; actual sizing, account eligibility and residency remain separately evidenced. |
| #9 | #15 | @zabyxc01, @appletechie | Vector DB hosting and infrastructure storage boundary; product evaluation retained by #15 | Historical state: [@appletechie accepts boundary](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047), main `66b46d4`; @zabyxc01 substantive disposition separate. [Actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362`: The current product-side software/instance/cloud-offering and meter interface is accepted with constraints after independent technical receiving review; no absent co-assignee response or deployed tuple is inferred. |
| #9 | #27 | @CompleteDotTech, @tynamite | MCP server hosting/network category; transport and tool semantics retained by #27 | Historical state: [Accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072). [Actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362`: Current reuse of the local-process/remote-placement interface is accepted with constraints; T4 retains actual process, egress, authentication and trust evidence. |
| #9 | #31 | @tynamite, @appletechie | Host/storage IDs, availability and billing constraints; training sizing retained by #31 | Historical state: [Accepted](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6230482274): reuse existing host/storage IDs; missing SKU records remain separate. [Actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362`: Current host/storage identity reuse is accepted with constraints; Google Cloud, Azure, Lambda and CoreWeave host records remain named follow-ups, and training sizing/time/cost stay separate. |
| #9 | #37 | @appletechie, @PUSHINGSQUARES | Deployment responsibility, artifacts, network and region constraints | Historical state: [@appletechie's historical accept, integration-pending receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047) retains `66b46d4`. [@PUSHINGSQUARES confirms with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6247689488) at `9192d5d`: responsibility/artifact/network/region inputs from #247's delivered offering/private-network/mounted-storage map are confirmed. Proposal 0.3.0 remains documentary, with entitlement, actual route and actual mount separately evidenced. The response explicitly leaves receiving review of the map and appletechie's separate scope open. [Actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362`: The exact three-group/seven-step 0.3.0 map and qualified CD-9 admission decision are accepted with constraints after independent technical receiving review; final ruleset and selected deployment evidence remain separate. |
| #9 | #39 | @appletechie, @PUSHINGSQUARES | Dated price units, conditional rates, storage/egress exclusions | Historical state: [@appletechie accepts with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047) at `66b46d4`. [@PUSHINGSQUARES narrows](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6247689488) at `9192d5d`: retain scoped units/conversions/allowances and readable L37/L38 estimates as not-totalled rows under #113. Display rate, accrual cadence, credit admission and invoice rounding remain distinct; the last is unadopted, and Runpod sub-hour cadence remains open. [Actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362`: The delivered #339 L37/L38 not-totalled rows resolve the earlier display condition; retained unit/allowance and billing-stage inputs are accepted with constraints, while missing quantities and invoice semantics remain unresolved. |
| #10 | #9 | @Mattycodes69, @appletechie | Distinct accelerator vs provisionable compute-profile catalog IDs | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225): accelerator/profile separation; no free-memory or workload-fit claim. The [actual delegated receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) at `8a6b8a67` separately accepts the retained current subset and explicit withdrawals, preserving source units and offering/stock/fit distinctions |
| #10 | #11 | @zwright8, @Mattycodes69 | Backend/precision and per-device memory assumptions; no universal GPU fit | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677): per-device inputs and capacity/support separation; no pooled VRAM. The [actual delegated receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) at `8a6b8a67` separately accepts current native-hardware facts and withdrawals as joint-support research inputs; artifact/engine/KV/admission evidence and completed #11 research retain their own scope |
| #10 | #31 | @tynamite, @appletechie | Reuse accelerator catalog; independent training-specific memory/time estimates | [Historical acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484): reuse the then-existing accelerators/profile; training estimates remain independent. The [actual delegated receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) at `8a6b8a67` expressly accepts L40S/RTX 4090/A100 and the documented profiles after the [H100/MI300X note-only correction](gpu-compute.md#incomplete-precision-intake-correction-2026-10-18); historical notes supply no current structured target, training estimate or missing profile |
| #10 | #39 | @appletechie, @PUSHINGSQUARES | Scenario quantities, concurrency, utilization, headroom and uncertainty | [@appletechie accepts with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221), reviewed `66b46d4`. [@PUSHINGSQUARES narrows](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6247689665), checked `9192d5d`: retain quantity/utilization boundaries, but #39 has no headroom term; disclose **headroom not applied** on capacity lines until an explicit input is adopted. The [cost record](../T6-deployment-operations/cost-estimate.md#reference-workload-used-by-the-worked-scenarios) now implements that disclosure on its scoped capacity rows/results. Neither receipt supplies calibrated headroom or a ResourceEstimate, and the implementation is not a newly authored response from either owner. The [actual delegated receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) at `8a6b8a67` confirms that implementation, unchanged arithmetic and the retained unknown reserve; the dated W3 H100 illustration supplies no new catalog/build binding |
| #11 | #10 | @Mattycodes69, @appletechie | Version-specific backend/format/precision constraints and adapter overhead | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057): exact-release sizing inputs; historical results do not transfer; [@appletechie separately accepts with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245668221), preserving dtype/adapter roles and non-pooling. Neither is independent runtime verification |
| #11 | #25 | @CompleteDotTech, @Mattycodes69 | Tool parser, chat-template, structured-output and streaming requirements | [Accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334) |
| #11 | #33 | @Mattycodes69, @appletechie | Adapter/base lineage, tokenizer, merged-weight and GGUF distinctions | [Accepted with tokenizer/template ownership narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684); engine support stays with #11 |
| #11 | #37 | @appletechie, @PUSHINGSQUARES | Engine build/version, hardware/backend and serving configuration constraints | [@appletechie's historical accept, integration-pending receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245668428) retains `66b46d4`. [@PUSHINGSQUARES confirms with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868) at `9192d5d`: #246's ENGINE map is delivered; S45/R30 cover engine routes, R18 is the separate tool/MCP credential check. This accepts research mapping, not an executable rule or selected service's runtime evidence |
| #11 | #38 | @appletechie, @PUSHINGSQUARES | Version/build/config evidence-record fields and latency/queue/KV/device-memory source requirements | [@appletechie's narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245668428) retains `66b46d4`. [@PUSHINGSQUARES narrows](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6247689868) at `9192d5d`: exact-release source mapping accepted as inputs; version/build/config are evidence fields, not required metric labels. Live `_total` scrape forms remain unverified, missing series are unavailable, and new llama.cpp SG IDs wait for a selected build/tuple |

To acknowledge, the owner should link the PR/commit and specify **accept**, **accept with constraints**, or **reject**, identifying the consumer issue and retained unknowns. Record the actual comment or submitted-review URL here only after it exists. A review request alone leaves this table pending.

## Additional reconciliation requests

| Issue / current owner | Precise question or input | Impact and next action |
| --- | --- | --- |
| #2/#3 @tynamite | Confirm workload/concurrency meanings and component-scoped interpretation of hybrid mode; map operational responsibility to canonical hosting types such as `managed_api`, `cloud`, and `on_prem` | T2 uses stated research assumptions until T0 accepts terminology; does not block parallel research |
| #5/#6/#7 @zwright8 | Supply exact model version/revision, architecture/KV geometry, supported precisions, prompt/output budgets, and permitted artifacts for a real pinned build | Worked arithmetic is a project estimate, not a measured or compatible production build; retain note-only examples until T1 records exist |
| #13 @zabyxc01; #28 @CompleteDotTech | Confirm that T2 storage catalog describes infrastructure, while ACLs/document rights/deletion and session/durable memory semantics stay with T3/T4 | #28 accepts the infrastructure/memory boundary with constraints ([receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072)); #13 disposition remains separate. Do not infer application ACL or retention guarantees from storage product choice |
| #16 @zabyxc01 | Confirm retrieval consumers' reranking/embedding inputs, context-budget and streaming expectations | Prevent generation-runtime claims from becoming retrieval quality claims |
| #33 @appletechie | Confirm adapter vs merged checkpoint identity, immutable base revision and tokenizer/template ownership | [Accepted with narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684): #33 records added tokens/training template; #32 owns training-data template; #11 determines engine support. Generic format match still cannot prove compatibility |
| #39 @PUSHINGSQUARES | Approve GB/GiB and GB-month/hour semantics, nonlinear storage tiers, allowances, egress and commitment treatment | Do not silently convert unsupported rates into canonical meters or zero cost |
| #40 @tynamite | Review the linked rule proposals and contract gaps in [contract-proposals.md](contract-proposals.md) | v1 remains frozen; proposed rules are not an approved versioned ruleset |
| #41 @tynamite | Adopt/replace interim grades; decide refresh windows, source-conflict priority and reuse permissions for vendor data | This capture has access dates; no automatic freshness or commercial redistribution permission is asserted |
| #8–#11 @Mattycodes69; Project administrator | Restore Project read/write access; verify existing status option for open research PRs and reconcile board field naming with documentation | Board is publicly readable but edits are unavailable. Preserve observed `Tier` and `Critical/High` values; do not invent new fields/options |

## Related existing work (historical intake)

[PR #68](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/68) contains T5 framework research and an output-artifact handoff to #33/#11; its note was read as an unmerged proposal, not promoted as authoritative vendor evidence. PR #46 is closed without merge. The continuation check confirms #68 now targets `main`, while open [PR #67](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67) still targets `research-contract-v1`; their maintainers own retargeting. Related agent/MCP/memory PRs #69/#71/#72 contain proposed consumer requirements, with no submitted reviews or T2 handoff acknowledgements at this check. Their authors and proposal text do not replace live issue assignees or confirm acceptance.

The canonical baseline comes from merged [PR #44](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/44) and current `main`, not stale issue appendices. Scoped #8–#11 appendices were corrected without changing acceptance criteria, assignees, labels, or native relationships.

## Posted requests (not acknowledgements)

- [Parent progress / Project access action](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/8#issuecomment-6216105045)
- [Hosting consumer requests](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6216105719)
- [Compute consumer requests](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6216106309)
- [Engine consumer requests](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6216107081)
- [#40 rule and contract submission](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6216107964)
- [#41 evidence/freshness/reuse request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6216108532)
- [#39 price/quantity reconciliation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6216109139)

At the original publication snapshot, [PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75) requested reviews from @CompleteDotTech, @zwright8, @tynamite, @zabyxc01, @appletechie and @PUSHINGSQUARES. GitHub metadata confirmed all six requests; the submitted-review list was empty. @Mattycodes69 is the PR author and must explicitly acknowledge internal T2 handoffs in a comment rather than requesting a self-review. That historical request snapshot does not replace the later explicit receipts above.

## Closure gates

All three decision records and the T2 summary merged in #75; the focused corrections #100/#101/#103 and S3 supplement #158 also merged. These delivery gates are complete; no repeated merge is required. Every required handoff must have an actual consuming-owner acknowledgement, and each issue's own acceptance criteria must be satisfied before its completion. #9 is complete through [#355](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355) and its [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6251909151); [the separate parent assessment below](#parent-declared-handoff-completion-2026-10-18) records #8's later completion. [The current compute reconciliation](#current-compute-scope-and-cost-condition-integration-2026-10-18) records #10's later completion. Report any Project update limitation explicitly.

The [final research handoff assessment](inference-engine.md#final-research-handoff-assessment--2026-10-18) accounts for all five required #11 consumers using the actual comments above, including #38's expressly accepted narrowing to source/evidence inputs. [PR #291](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/291), merged as [859f47db88f0d8f1a99899ca9029ce0da19800c8](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/859f47db88f0d8f1a99899ca9029ce0da19800c8) on 2026-10-18, completed the reviewed assessment and #11 is now closed. The earlier #266 audit supplied the eight artifact criteria, and #285 reconciled the later T6 receipt. The full assessment preserves those records and each receipt's author, revision, direction and limits. Named lifecycle/#42 and selected-runtime follow-ups remain in their owning scopes; completion of #11 does not complete the parent or its receiving issues.


## Reciprocal engine receipt (2026-10-18)

[@zwright8's delegate accepts #25 -> #11 with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6242698282),
reviewing main `7acbefbf4e4e700231e88be272bc89e3a73dde15` from that co-owner's scope.
The interface retains engine/build/plugins/backend, model/tokenizer revisions,
adapter/base lineage, template/parser, endpoint, request controls, strictness,
parallel/streaming behavior and decoding mode. Consumer cases distinguish valid
correlated calls, malformed arguments, unsupported options, incomplete streams,
schema violations and changed tuples. This is interface acceptance, not evidence
that those runtime cases ran.

[Mattycodes69 now also accepts #25 -> #11 with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677), including FC-1–FC-6 as baseline consumer specifications and explicit error/cancellation and argument-schema cases before a run. The four internal T2 interfaces have explicit receipts above. The later #37/#38 co-owner responses are recorded above with their individual research scopes; they do not establish runtime acceptance. Existing #11 -> #25 and #11 -> #33 receipts retain their original direction and scope. No runtime case or final versioned rule is accepted.

## Reciprocal hosting receipt (2026-10-18)

[Mattycodes69 accepts #27/#28 -> #9 with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225): reuse hosting/storage IDs; evidence subprocess capability, network reachability/egress and locality for the actual selection. T4 retains protocol, trust and memory semantics; #15 retains vector-product evaluation and #37 deployment. Missing fields/rules remain #40 proposals. [Appletechie's separate #9 co-owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047), reviewing `66b46d4`, also accepts #27/#28 -> #9 with constraints. It requires evidence for actual subprocess support, placement and egress; absent storage/host records remain gaps, and a shared catalog ID does not identify a shared instance. Neither response supplies another consuming owner's decision or completes #9.

## #61 measurement intake proposal (2026-10-18)

Live #10/#61 co-owners are @Mattycodes69 and @appletechie. The
[#10 disposition](gpu-compute.md#headroom-and-measurement-handoff-disposition-2026-10-18)
offers the 15 existing dense observations as note-only accounting evidence,
retained in `research/market/measurements/`, and specifies a proposed future
build-bound ResourceEstimate intake path. Both co-owners' dispositions remain
required. There is no new ResourceEstimate, empirical calibration or coverage
waiver. Missing headroom/eligibility remains unknown for review.

[Zwright8's #61 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61#issuecomment-6242699281)
accepts #7/#11 interfaces only, at its stated revision. It does not accept #10's
new proposal or replace appletechie's #7 / Mattycodes69's #11 responses. The
existing #10 -> #31 receipt above remains unchanged. Mattycodes69's #9/#11 interface receipts are now linked above; #39 and other co-owner dispositions remain separate. These interface receipts do not accept the headroom/measurement proposal. This scoped note does not refresh
unrelated handoffs or take over #59's canonical market ledgers.


## #9 regional-scope and billing continuation (2026-10-18)

The [hosting record](hosting.md#proposed-initial-regional-scope-and-expansion-gates-2026-10-18)
now proposes bounded initial samples and evidence-led expansion, separates
public offering from account access/AZ capacity, and rechecks regional and
Runpod billing/placement documentation as H34–H37. No rate or catalog changes
follow. appletechie's #15/#37/#39 responses above retain their `66b46d4` scope.
PUSHINGSQUARES's later `9192d5d` response confirms #37 inputs from the map and
narrows #39 to the stated unit, visible-exclusion and billing-stage conditions.
Receiving review of the #37 map, appletechie's separate scope, #14 and the
substantive #15 response remain outstanding. Both #9 owners still decide the
regional recommendation; unresolved invoice semantics remain with #39.


## Current compute scope and cost-condition integration (2026-10-18)

The [compute artifact assessment](gpu-compute.md#compute-research-artifact-assessment--2026-10-18)
preserves the 20-record T2 intake after #301 and all original receiving pins.
The required #10 → #39 disclosure is now present on 23 capacity ledger rows,
the W2/W3 capacity results and five comparisons. A reserve remains unspecified;
the cache-hit variable and requests-in-flight quantity are not repurposed as
headroom or request rate. The [separate L37/L38 display](../T6-deployment-operations/cost-estimate.md#priced-exclusions-beside-the-w1w3-totals)
retains their priced examples as **not totalled**, satisfying the documentary
exclusion condition in the actual #9 → #39 response without claiming invoice
rounding, a free allowance balance or a complete quote.

The [actual current receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107)
at published `8a6b8a67019a7abbddd66be59a9d14f8cf9a592f`, tree
`38cda613ed05c30adf9fdb34cd2d0584866de414`, records all four declared
#10 → #9/#11/#31/#39 dispositions against the retained current set, note-only
withdrawals and cost disclosures. It was posted by `CompleteDotTech` as the
coordinating engineer under the user's project delegation. Every original
author, revision and scope is preserved; no absent-assignee response is inferred.
This satisfies 10.9. [PR #339](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/339)
received [independent source review at `94ea2422`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/339#pullrequestreview-5563188565)
and delivered the assessment in signed
[`a2bba46f`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/a2bba46ff850af5d6263561a94f9866b01c03c05).
The [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250602587)
records successful post-main CI, the completed issue with all ten criteria
checked, and the subsequent public Project `Done` readback. Numeric defaults,
runtime calibration, future ResourceEstimates and downstream issue completion
retain their own named owners and factual requirements.

## Current hosting scope and receiving completion (2026-10-18)

The [actual CompleteDotTech delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) of `f007736206697f58c0d28cf24dae94598f3e8a07` receives all seven required #9 → #10/#14/#15/#27/#31/#37/#39 directions with constraints. It incorporates the independent current embedding/vector/deployment interface review and the retained historical receipts and delivered cost conditions. This satisfies 9.9 through an actual newly attributed review, not a new statement by an absent assignee. [PR #355](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355) delivered the concrete source as [`26a82d0a`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/26a82d0aba1fa9f382b143089434f65fdd4c1f83); the [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6251909151) records actual final validation and issue completion. Earlier “pending” statements above retain their historical source revisions. The completed research does not adopt an invoice formula, a real jurisdiction map, a final ruleset or a selected deployment, and it does not complete a downstream issue or the parent.

## Parent-declared handoff completion (2026-10-18)

The [actual #8 Current triage and completed closure](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/8) at **2026-10-18T16:48:37Z** records CompleteDotTech's separate delegated parent acceptance after independent review. Its three literal handoff clauses use the following four receiving directions. The broader child ledger above retains its own scope; the parent audit adds no requirement to obtain new responses for every legacy row.

| Parent-declared boundary | Actual receiving evidence | Retained scope |
| --- | --- | --- |
| #10 → #31: reuse the accelerator catalog; T5 supplies training estimates | [appletechie's original receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484) and [current CompleteDotTech delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) at `8a6b8a67` | Current L40S/RTX 4090/A100 and documented profiles; H100/MI300X stay note-only. Training-specific memory/time estimates remain with #31 |
| #11 → #33: T2 serving compatibility; T5 artifact definition | [appletechie's actual artifact/engine boundary acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684) and the [delivered final assessment](inference-engine.md#final-research-handoff-assessment--2026-10-18) | #33 retains artifact identity/tokenizer information; engine compatibility stays with #11. No unsupported serving tuple or installed result is inferred |
| #9 → #15: vector-database hosting category; T3 product choice | [appletechie's historical hosting boundary receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047) and [current CompleteDotTech receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362` | Software, process/instance, cloud offering and meter remain distinct; #15 retains vector-product evaluation |
| #9 → #27: MCP hosting category; T4 protocol/trust choices | [CompleteDotTech's original acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072) and [current CompleteDotTech receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/355#pullrequestreview-5563649987) at `f0077362` | Process/remote placement remains separate from MCP protocol, transport, authorization, trust and lifecycle semantics |

The issue's original three criteria and coassignees are preserved. The [parent assessment](acceptance-matrix.md#current-parent-completion-assessment-2026-10-18) also records qualifying child closure and the existing workstream summary. These actual research decisions retain their authors and dated inputs; they do not complete another workstream or supply runtime/source evidence that was missing from its own record.
