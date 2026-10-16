# T1 handoffs and decisions awaiting confirmation

Snapshot: 2026-10-16. Live assignees were read from GitHub. **Pending means no acceptance of this contribution exists yet.** A reviewer request or an agent's analysis is not a receiving-owner acknowledgement. Confirmations must identify the exact artifact/PR revision, consumer and any retained constraints. T1 author integration is recorded separately from independent review.

| Producer -> consumer | Current consuming owner | Artifact / decision requested | Disposition |
| --- | --- | --- | --- |
| #5 -> #6 | @zwright8 | [Provider mapping](model-provider.md) and [model identity](ai-model.md): publisher vs route IDs, conditional terms | Integrated by same T1 author; independent review pending |
| #5 -> #7 | @zwright8 | Offering-specific overrides, account access and threshold prices in [context](context-window.md) | Integrated by same T1 author; independent review pending |
| #5 -> #30 | @appletechie | Model/offering/account/region fine-tuning eligibility; no inference from provider branding | Pending |
| #5 -> #37 | @PUSHINGSQUARES | Endpoint/control-plane/region/retention conditions and explicit unknown entitlement | Pending |
| #5 -> #39 | @PUSHINGSQUARES | Exact model-version Pricebook refs, standard/long-context predicates, uncovered cache/tool/region costs | Pending |
| #6 -> #7 | @zwright8 | Snapshot-specific limits and tokenizer/config identity; separate budgets and native vs extended context | Integrated by same T1 author; independent review pending |
| #6 -> #10 | @Mattycodes69 | Qwen pinned geometry, dtype/artifact distinction, context inputs and scoped resource-evidence requirement | Pending |
| #6 -> #11 | @Mattycodes69 | Model/format/precision/architecture and exact engine/backend tuple; no universal format-fit claim | Pending |
| #6 -> #16 | @zabyxc01 | Model modalities/capabilities/context and version boundaries; no claim of retrieval quality | Pending |
| #6 -> #25 | @CompleteDotTech | Vendor-reported tool calling vs exercised workflow, API surface/engine conditions, unknown optional flags | Pending |
| #6 -> #30 | @appletechie | Confirm license/weight-access fields sufficient: repository/revision, license text, restrictions, derivative lineage, offering eligibility | Pending; explicit #6 acceptance gate |
| #6 -> #35 | @PUSHINGSQUARES | Modality/tool/schema claims and license/terms restrictions; no safety approval implied | Pending |
| #6 -> #36 | @PUSHINGSQUARES | Version-pinned candidates, evidence grades, no fabricated benchmarks, usable-context quality protocol | Pending |
| #6 -> #39 | @PUSHINGSQUARES | API item-version refs versus self-hosted unknown compute/operational costs | Pending |
| #7 -> #10 | @Mattycodes69 | Agree [KV input manifest](context-window.md#proposed-kv-cache-handoff-to-10): geometry, admitted occupancy, output reserve, cache layout/precision, placement | Pending; explicit #7 acceptance gate |
| #7 -> #16 | @zabyxc01 | Complete assembled input, transform/content-preservation policy, post-transform recount, separate fit/quality | Pending |
| #7 -> #28 | @CompleteDotTech | Count history/retrieved memory/thinking; preserve required content and recount after memory transforms | Pending |
| #7 -> #39 | @PUSHINGSQUARES | Prompt-length predicates, exact currencies/route/service modifiers, threshold-crossing uncertainty and full-session accounting | Pending |

## Central reconciliation

| Owner / issue | Precise requested disposition | Current state |
| --- | --- | --- |
| @tynamite / #3 | Confirm component operator/capacity mode taxonomy and demand vs admitted sequences; this note applies the existing [owner position](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) | Existing position applied; no acceptance of this new artifact inferred |
| @tynamite / #40 | Review [rule proposals](rules/model-offering.md) and context proposals; reconcile separate input/output semantics, offering binding/terms, lineage/geometry, conditional rates and one-version intake in a next version | Pending; frozen v1 unchanged |
| @tynamite / #41 | Confirm application of adopted checked/verified, freshness, conflict and short-paraphrase reuse policy; all vendor-backed proposal provenance remains unverified | Existing interim policy applied; this evidence set still needs review |
| @PUSHINGSQUARES / #39 | Accept meter applicability, decimal money, exact versions and uncovered costs; regional default-view and unsupported cache-write/host costs remain owned follow-ups | Pending |
| @zwright8 / #7 with #36/#40 | Present usable-context quality as unknown until matched task evidence exists, independently of documented capacity | Proposed decision; independent/product-policy review pending |

## Incoming requests preserved

T2's [merged handoff ledger](../T2-infrastructure/handoffs.md) requested exact model revision, geometry, prompt/output budgets and permitted artifacts from #5–7. This contribution supplies pinned Qwen facts and a manifest, not a real calibrated build. The older ledger's statements about missing owner responses are historical: #3/#40/#41 subsequently supplied [specific positions in PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Do not overwrite that ledger or claim the positions approve T1.

## Review/closure process

Request one coordinated review on the focused T1 PR from the six affected owners: @tynamite, @Mattycodes69, @zabyxc01, @CompleteDotTech, @appletechie and @PUSHINGSQUARES. Record actual comment/review URLs after they exist. Ask owners to **accept**, **accept with constraints**, or **reject** the specific consumer rows, with the reviewed SHA. Do not repeatedly request the same pending decision.

Use `Refs #4`, `Refs #5`, `Refs #6`, `Refs #7` while confirmations/merge are pending. No changes to other assignees, acceptance criteria, native blockers or existing decisions are made. Project update access is a tracking limitation, not a newly invented issue dependency.

## Requests actually published

[PR #88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88) requests all six affected owners listed above; GitHub readback confirmed those requests and an empty submitted-review list at publication. [Parent request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/4#issuecomment-6223171020) and [central #40 intake](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6223171381) identify the concrete artifacts and required dispositions. Requests leave all Pending rows pending. Existing signed-in browser access resolved the earlier Project API limitation; #4–7 Status is now In Review, with priorities/readiness/ownership preserved. No Done status or closure is claimed.
