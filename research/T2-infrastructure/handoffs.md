# T2 handoffs and follow-up ledger

Original intake: 2026-10-16; scoped receipt reconciliation: 2026-10-18. The required-consumer table lists live coassignees checked on the latter date. A receipt credits only its author, direction and stated interface; it does not imply every co-owner approved or that all acceptance criteria are met.

The original continuation audit re-read the scoped and consuming issue comments plus PR #75 reviews and inline comments on 2026-10-16 and found no acknowledgments then. On 2026-10-17, the T4 receiving owner supplied the scoped #9 -> #27 and #11 -> #25 dispositions linked below. That paragraph describes the original audit; the dated reconciliation below supersedes its receipt status. Existing review requests and issue requests are retained without duplicate reminders. Parallel contributor review is not a consuming-owner decision.

## Receipt reconciliation (2026-10-18)

Live issue comments confirm the T4/T5 receipts and Mattycodes69's explicit [Hosting](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225), [Compute](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057) and [Engine](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677) dispositions against main `9344f99325510adfe678382a4672246d028e87bc`. Hosting has scoped receipts for #10/#27/#31 (three of seven required interfaces), Compute for #9/#11/#31 (three of four), and Engine for #10/#25/#33 (three of five). #28 is an additional Hosting boundary receipt, not an eighth original dependency. Other receiving-owner and co-owner decisions remain separate. No reverse-direction T5 acceptance, runtime result, headroom default or final rule approval follows.

## Required consuming-owner confirmations

| Producer | Consumer | Current consuming owner | Artifact / confirmation requested | Acknowledgement evidence |
| --- | --- | --- | --- | --- |
| #9 | #10 | @Mattycodes69, @appletechie | Hosting IDs, EC2 profile binding, regional availability unknowns | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057): dated EC2 host/profile binding; stock/quota unknown |
| #9 | #14 | @zabyxc01, @PUSHINGSQUARES | Managed embedding endpoint hosting category and residency boundary | Pending |
| #9 | #15 | @zabyxc01, @appletechie | Vector DB hosting and infrastructure storage boundary; product evaluation retained by #15 | Pending |
| #9 | #27 | @CompleteDotTech, @tynamite | MCP server hosting/network category; transport and tool semantics retained by #27 | [Accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072) |
| #9 | #31 | @tynamite, @appletechie | Host/storage IDs, availability and billing constraints; training sizing retained by #31 | [Accepted](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6230482274): reuse existing host/storage IDs; missing SKU records remain separate |
| #9 | #37 | @appletechie, @PUSHINGSQUARES | Deployment responsibility, artifacts, network and region constraints | Pending |
| #9 | #39 | @appletechie, @PUSHINGSQUARES | Dated price units, conditional rates, storage/egress exclusions | Pending |
| #10 | #9 | @Mattycodes69, @appletechie | Distinct accelerator vs provisionable compute-profile catalog IDs | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225): accelerator/profile separation; no free-memory or workload-fit claim |
| #10 | #11 | @zwright8, @Mattycodes69 | Backend/precision and per-device memory assumptions; no universal GPU fit | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677): per-device inputs and capacity/support separation; no pooled VRAM |
| #10 | #31 | @tynamite, @appletechie | Reuse accelerator catalog; independent training-specific memory/time estimates | [Accepted](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484): reuse existing accelerators/profile; training estimates remain independent |
| #10 | #39 | @appletechie, @PUSHINGSQUARES | Scenario quantities, concurrency, utilization, headroom and uncertainty | Pending |
| #11 | #10 | @Mattycodes69, @appletechie | Version-specific backend/format/precision constraints and adapter overhead | [Accepted with constraints by @Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6245205057): exact-release sizing inputs; historical results do not transfer |
| #11 | #25 | @CompleteDotTech, @Mattycodes69 | Tool parser, chat-template, structured-output and streaming requirements | [Accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334) |
| #11 | #33 | @Mattycodes69, @appletechie | Adapter/base lineage, tokenizer, merged-weight and GGUF distinctions | [Accepted with tokenizer/template ownership narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684); engine support stays with #11 |
| #11 | #37 | @appletechie, @PUSHINGSQUARES | Engine build/version, hardware/backend and serving configuration constraints | Pending |
| #11 | #38 | @appletechie, @PUSHINGSQUARES | Version/build/config labels, latency/queue/KV/device memory evidence requirements | Pending |

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

All three decision records and the T2 summary merged in #75; the focused corrections #100/#101/#103 and S3 supplement #158 also merged. These delivery gates are complete; no repeated merge is required. Every required handoff above must have an actual consuming-owner acknowledgement, and all issue acceptance criteria must be satisfied. Until then use `Refs #n`, leave #8–#11 open, and report any Project update limitation explicitly.


## Reciprocal engine receipt (2026-10-18)

[@zwright8's delegate accepts #25 -> #11 with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6242698282),
reviewing main `7acbefbf4e4e700231e88be272bc89e3a73dde15` from that co-owner's scope.
The interface retains engine/build/plugins/backend, model/tokenizer revisions,
adapter/base lineage, template/parser, endpoint, request controls, strictness,
parallel/streaming behavior and decoding mode. Consumer cases distinguish valid
correlated calls, malformed arguments, unsupported options, incomplete streams,
schema violations and changed tuples. This is interface acceptance, not evidence
that those runtime cases ran.

[Mattycodes69 now also accepts #25 -> #11 with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677), including FC-1–FC-6 as baseline consumer specifications and explicit error/cancellation and argument-schema cases before a run. The four internal T2 interfaces have explicit receipts above. #37/#38 receipts remain open. Existing #11 -> #25 and #11 -> #33 receipts retain their original direction and scope. No runtime case or final versioned rule is accepted.

## Reciprocal hosting receipt (2026-10-18)

[Mattycodes69 accepts #27/#28 -> #9 with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225): reuse hosting/storage IDs; evidence subprocess capability, network reachability/egress and locality for the actual selection. T4 retains protocol, trust and memory semantics; #15 retains vector-product evaluation and #37 deployment. Missing fields/rules remain #40 proposals. Appletechie's separate #9 co-owner disposition is not inferred.

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
