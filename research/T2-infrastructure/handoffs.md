# T2 handoffs and follow-up ledger

Snapshot: 2026-10-16. Ownership below comes from live GitHub assignees, not the older owner tables. A requested review is not confirmation. No owner acknowledgement was present in the issue/comment intake. Internal T2 handoffs also need an explicit owner response.

The original continuation audit re-read the scoped and consuming issue comments plus PR #75 reviews and inline comments on 2026-10-16 and found no acknowledgments then. On 2026-10-17, the T4 receiving owner supplied the scoped #9 -> #27 and #11 -> #25 dispositions linked below. Other rows retain their prior snapshot; this is not a complete refresh of non-T4 acknowledgments. Existing review requests and issue requests are retained without duplicate reminders. Parallel contributor review is not a consuming-owner decision.

## Receipt reconciliation (2026-10-18)

Live issue comments confirm the three T5 receipts below. They receive T2 inputs only; they do not accept reverse-direction T5 proposals, missing catalog records, or another consumer’s handoff. Historical intake paragraphs describe their original snapshots. Other rows retain their previous snapshot and are not newly certified by this reconciliation.

## Required consuming-owner confirmations

| Producer | Consumer | Current consuming owner | Artifact / confirmation requested | Acknowledgement evidence |
| --- | --- | --- | --- | --- |
| #9 | #10 | @Mattycodes69 | Hosting IDs, EC2 profile binding, regional availability unknowns | Pending |
| #9 | #14 | @zabyxc01 | Managed embedding endpoint hosting category and residency boundary | Pending |
| #9 | #15 | @zabyxc01 | Vector DB hosting and infrastructure storage boundary; product evaluation retained by #15 | Pending |
| #9 | #27 | @CompleteDotTech | MCP server hosting/network category; transport and tool semantics retained by #27 | [Accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072) |
| #9 | #31 | @appletechie | Host/storage IDs, availability and billing constraints; training sizing retained by #31 | [Accepted](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6230482274): reuse existing host/storage IDs; missing SKU records remain separate |
| #9 | #37 | @PUSHINGSQUARES | Deployment responsibility, artifacts, network and region constraints | Pending |
| #9 | #39 | @PUSHINGSQUARES | Dated price units, conditional rates, storage/egress exclusions | Pending |
| #10 | #9 | @Mattycodes69 | Distinct accelerator vs provisionable compute-profile catalog IDs | Pending |
| #10 | #11 | @Mattycodes69 | Backend/precision and per-device memory assumptions; no universal GPU fit | Pending |
| #10 | #31 | @appletechie | Reuse accelerator catalog; independent training-specific memory/time estimates | [Accepted](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6230482484): reuse existing accelerators/profile; training estimates remain independent |
| #10 | #39 | @PUSHINGSQUARES | Scenario quantities, concurrency, utilization, headroom and uncertainty | Pending |
| #11 | #10 | @Mattycodes69 | Version-specific backend/format/precision constraints and adapter overhead | Pending |
| #11 | #25 | @CompleteDotTech | Tool parser, chat-template, structured-output and streaming requirements | [Accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334) |
| #11 | #33 | @appletechie | Adapter/base lineage, tokenizer, merged-weight and GGUF distinctions | [Accepted with tokenizer/template ownership narrowing](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6230482684); engine support stays with #11 |
| #11 | #37 | @PUSHINGSQUARES | Engine build/version, hardware/backend and serving configuration constraints | Pending |
| #11 | #38 | @PUSHINGSQUARES | Version/build/config labels, latency/queue/KV/device memory evidence requirements | Pending |

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

## Related existing work

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

[PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75) requests reviews from @CompleteDotTech, @zwright8, @tynamite, @zabyxc01, @appletechie and @PUSHINGSQUARES. GitHub metadata confirmed all six requests; the submitted-review list was empty. @Mattycodes69 is the PR author and must explicitly acknowledge internal T2 handoffs in a comment rather than requesting a self-review. These facts do not change any Pending cell above.

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

Mattycodes69's co-owner/internal #10 dispositions and #37/#38 receipts remain
open. Existing #11 -> #25 and #11 -> #33 receipts above retain their original
direction and scope; this new receipt does not accept other pending rows.
