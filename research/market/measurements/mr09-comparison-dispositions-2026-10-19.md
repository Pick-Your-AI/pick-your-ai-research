# MR-09 comparison review and coordinator decisions — 2026-10-19

Refs #61. Review readback before preparing the experimental estimator correction.
Decision record: [sizing-validation.md](../sizing-validation.md). This note records
attributed GitHub receipts; it adds no estimator, prediction or runtime result.

## Reviewed revision and delivery

[PR #321](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/321) merged
on 2026-10-18 at `5bc1ade834756d5283702e527655a8076291aaa6`. The reviewed
source was `e46963794f51704b19b2ede0d2780d8edbc72dc3`; the original
[comparison specification](mr09-comparison-spec-2026-10-18.md) remains the
historical proposal, including its then-pending decision table.

CompleteDotTech's [source/evidence review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/321#pullrequestreview-5562801452)
(2026-10-18 11:43:14Z) found no blocking source finding. The later
[delivery review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/321#pullrequestreview-5562900099)
(12:00:51Z) accepted normal delivery of the bounded proposal. Both formal
review states are `COMMENTED`; neither is a separately named owner's approval
of a future candidate. Inspected hosted results are attributed to those reviews,
not described as a new local reproduction here.

The [post-merge readback](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/321#issuecomment-6249830284)
records the actual main delivery and successful push checks. It explicitly says
the closing-directive checker ran after that merge; this note does not backdate
that check. Publication of the specification did not complete #61.

## Explicit coordinator dispositions

The following summarizes **CompleteDotTech's delegated coordinator direction**
in the [2026-10-18 11:45:46Z decision receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/321#issuecomment-6249525648),
bound to the full source revision above. That receipt expressly does not speak
for the separately named co-owners or consumers. The source/delivery reviews'
pending language is retained in its original scope; the distinct explicit
coordinator receipt supplies the dispositions below.

| Decision | Coordinator disposition | Conditions retained |
| --- | --- | --- |
| D61-01: target and scope | Accept the supplemental initialization managed-device-buffer track | Original whole-runtime allocated/reserved peak question, named llmfit/ModelFit/Local AI Planner requirements and dense/MoE/context/KV/concurrency/multi-GPU coverage remain. Supplemental/component pairs do not complete them. |
| D61-02: candidate identity | Accept separate experimental identity and preparation of a minimal project derivative with synthetic CPU regressions | Preserve original upstream source/output and unmatched baseline. Pin patch/source/build/dependencies/executable, command, effective controls and raw output before comparison. A version becomes real only when built; particular build/prediction acceptance remains separate. |
| D61-03: metric and exclusions | Narrow only the supplemental comparison to native CUDA0 self's byte interval as primary, exact admission ledger as corroboration | Reconcile both; never sum rounded components. Explicitly narrow the broad no-host-fallback condition for this metric only. CPU-mapped embedding and CUDA_Host readback/compute remain separate host terms. Preserve opaque/transient/inference and callback/copy-path exclusions; unexplained effects leave a pair unmatched. Original peak scope gains no waiver. |
| D61-04: capacity semantics | Accept separate host rows, graph capacity, global/per-sequence maxima, total/per-sequence context, populated cache, active requests and generated tokens | Capacity is not demand. H1–H3 remain source-derived expectations until actual native readback; H3 implies neither 512 tokens per sequence nor two active requests. |
| D61-05: prospective validation | Accept preparation with source/build/configuration/prediction freeze before inspecting new captures | Known trials remain development evidence. Keep interval/rational differences and separate cells/cohorts. Tolerance stays unset; no pass/fail, guaranteed fit, default headroom or ResourceEstimate claim. Fix any later threshold and its purpose before assessment. |

The original GPUStack v0.26.4 output remains unmatched/ineligible. No corrected
upstream result, accepted total-buffer pair or whole-runtime peak pair is added.
Earlier #267 publication and #7 exclusion-diagnosis receipts keep their own scope.

## Remaining responses and next actions

Live PR reviews, discussion and inline comments were refreshed on 2026-10-19.
No inline finding or new appletechie/zwright8 response appears on PR #321; those
review requests remain listed. Their separate responses to this prospective
candidate/metric/protocol remain pending, rather than inferred from coordinator
direction, older handoffs or the closure of #7/#10/#11. Existing bounded receiving
decisions elsewhere keep their own scope. #61 remains open with Mattycodes69 and
appletechie; no owner, criterion or Project field is changed by this note.

1. Prepare the minimal experimental source correction and meaningful synthetic
   CPU regressions, including a semantic fixture failing on the original and
   passing on the correction. Do not calibrate an additive term to the known
   native total. This is the next preparation step permitted by the coordinator
   receipt; it has not been performed in this contribution.
2. Submit the actual patch/build identity and limitations for independent source
   review and current receiving checks. Obtain explicit remaining named-owner
   dispositions before claiming their acceptance or an accepted comparison.
3. Freeze candidate predictions before any prospective observations. A future
   native experiment requires its own pinned harness/build, tuple qualification,
   allocation/capture controls, fresh resource screens and execution authority.
   These dispositions do not authorize paid compute, new hardware access, native
   environment installation/replacement, workload changes or failed-guard bypass.

No tolerance decision is needed for descriptive reporting. A decision threshold
remains a separate prospective choice if a future use requires one. This readback
publishes no ResourceEstimate or contract change and leaves all historical
CPU/native artifacts, the original specification and #59 ledgers unchanged.
