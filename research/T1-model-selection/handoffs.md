# T1 handoffs and decisions awaiting confirmation

Ownership snapshot: 2026-10-16, preserved from live GitHub assignees. Central review refreshed: 2026-10-17. **Pending means the named consumer has not accepted the specified handoff.** A reviewer request or an agent's analysis is not a receiving-owner acknowledgement. Confirmations must identify the exact artifact/PR revision, consumer and any retained constraints. T1 author integration is recorded separately from independent review. The [#3/#40/#41 owner's review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868) identifies `dbfa7dd13a7f732bff0653ae6ab45f55b2782f20`, the merged PR #88 head; its acceptance is limited to the positions below, not every consumer row.

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
| #6 -> #30 | @appletechie | License/weight-access sufficiency: repository/revision, licence text, restrictions, derivative lineage, offering eligibility and separate NOTICE presence | [Sufficient with constraints, narrowed by #30](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6245639699), 2026-10-18; reviewed artifact named, exact reviewed SHA not supplied. Normalized identifier resolution, obligation answers/inheritance and NOTICE treatment remain explicit; the [Qwen inventory](artifact-notices.md) addresses one distribution only. No broad permission or issue completion follows. |
| #6 -> #35 | @PUSHINGSQUARES | Modality/tool/schema claims and license/terms restrictions; no safety approval implied | Pending |
| #6 -> #36 | @PUSHINGSQUARES | Version-pinned candidates, evidence grades, no fabricated benchmarks, comparable quality protocol only when a workload quality target is selected | Pending |
| #6 -> #39 | @PUSHINGSQUARES | API item-version refs versus self-hosted unknown compute/operational costs | Pending |
| #7 -> #10 | @Mattycodes69 | Agree [KV input manifest](context-window.md#proposed-kv-cache-handoff-to-10): geometry, admitted occupancy, output reserve, cache layout/precision, placement | Pending; explicit #7 acceptance gate |
| #7 -> #16 | @zabyxc01 | Complete assembled input, transform/content-preservation policy, post-transform recount, separate fit/quality | Pending |
| #7 -> #28 | @CompleteDotTech | Count history/retrieved memory/thinking; preserve required content and recount after memory transforms | Pending |
| #7 -> #39 | @PUSHINGSQUARES | Prompt-length predicates, exact currencies/route/service modifiers, threshold-crossing uncertainty and full-session accounting | Pending |

## Broad-family and citation follow-up: 2026-10-17

The [taxonomy](model-taxonomy.md), six linked comparisons, [inventory](model-research-inventory.json) and [primary register](model-research-sources.md) extend the earlier language-model slice. The [retrospective audit](citation-audit-2026-10-17.md) and [market citation map](../market/citation-index-2026-10-17.md) trace previous sources without replacing historical access dates. None of the earlier owner positions accepts these new artifacts automatically.

| Receiving issues / live owners | New disposition requested | State |
| --- | --- | --- |
| #40: @tynamite with T1 author @zwright8; #41: @tynamite / @PUSHINGSQUARES | Review T1-TAX1 task/output/admission semantics and per-source evidence limitations, preserving frozen v1 and accepted CD decisions | Pending |
| #30: @appletechie with T1 author @zwright8 | Confirm separate code/checkpoint/backbone/adapter/service/data rights evidence and unresolved grants are sufficient for intake; no universal permission | Pending |
| #10: @Mattycodes69 / @appletechie; engine consumers | Identify per-task runtime/resource inputs; no text-KV formula transferred to arbitrary model families | Pending |
| #14: @zabyxc01 / @PUSHINGSQUARES | Review dense/sparse/multivector versus rerank outputs and exact modality/shape evidence; embedding catalog ownership stays with T3 | Pending |
| #39: @appletechie / @PUSHINGSQUARES | Define unsupported image/audio/video/character/credit meters before pricebook/contract intake; no new rates proposed | Pending |
| #49: @appletechie with author @zwright8; coordinator @CompleteDotTech; #59: @Mattycodes69 / @appletechie | Review retrospective citation mapping and narrower documentary evidence grades; unknown cells remain unknown | Pending |

Live issue assignees were read from GitHub on 2026-10-17; existing assignments and triage were preserved. This is a research checkpoint, not full acceptance of #4–7/#49, measured quality, rights clearance or approved contract migration.

## Central reconciliation (earlier language-model slice)

| Owner / issue | Precise requested disposition | Current state |
| --- | --- | --- |
| @tynamite / #3 | Component operator/capacity mode taxonomy and demand vs admitted sequences | **Accepted as applied at `dbfa7dd`** in the [PR #88 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868); this does not decide another consumer's capacity inputs |
| @tynamite / #40 | Route identity and proposed rule/contract reconciliation | **Owner positions recorded at `dbfa7dd`** below. Five requested corrections applied in this follow-up; review of the changed revision and versioned contract/executable-rule approval remain pending. Frozen v1 unchanged |
| @tynamite / #41 | Checked vs verified, freshness, conflict and short-paraphrase reuse policy | **Accepted as applied at `dbfa7dd`** in the same PR #88 review. Vendor-backed proposal provenance remains unverified; no independent benchmark or universal fact certification is inferred |
| @PUSHINGSQUARES / #39 | Accept meter applicability, decimal money, exact versions and uncovered costs; regional default-view and unsupported cache-write/host costs remain owned follow-ups | Pending |
| @zwright8 / #7 with #36/#40 | Check quality only for a selected workload `quality_target`, under #81 W-R10; retain strategy support and recount after transforms | #40 owner narrowed CTX-03 in PR #88. Follow-up applies that position; #36 protocol/acceptance policy and contract versioning remain pending |

### Recorded #40 dispositions and follow-up

Source for all rows: [@tynamite's PR #88 review at `dbfa7dd`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), submitted 2026-10-17. The reviewer explicitly calls these owner positions, not approved contract changes. This ledger records those positions without declaring acceptance of the new follow-up revision.

| Item | Owner disposition | Applied follow-up / remaining gate |
| --- | --- | --- |
| T1-O1 | Accept using existing v1 links | Document `provided_by`; richer endpoint identity uses #81's proposed key |
| CTX-01 | Accept with conservative bounded-estimate change | Upper-bound decision; straddling range returns fail flagged **may not fit**, range displayed |
| CTX-02 | Accept with native-limit fallback | Missing extension proof uses known native ceiling; Qwen 100,000 vs 32,768 fails that limit predicate |
| CTX-03 | Narrow | Keep v1 strategy-support predicate/recount; quality only under selected `quality_target` / W-R10 |
| CTX-04 | Accept | #39 owns rates; show both straddling scenarios and use the higher tier for budget checks |
| T1-O2 | Narrow into license conditions and offering capability | D-R2a/b use proposed answerable `license_conditions`/`licence_answers`; v1 model/provider `supports_fine_tuning: false` rejects fine-tuning. #30 sufficiency/interpretation remains pending |
| Former T1-M1 | Merge into #75 joint-support family | Reference COMPUTE-02/ENGINE-02/D-R3; T1 supplies pinned artifact/geometry/precision rather than another rule ID |
| Former T1-M2 | Merge into #75 memory-fit family | Reference COMPUTE-01/W-R6 with `on_unknown: review`; #10/#11 still own resource/runtime evidence |
| Contract gap 1 | Accept, narrowed | Existing `provided_by`; opaque-endpoint key for route identity; region mapping CD-9; account/terms conditions CD-6 |
| Contract gap 2 | Accept as CD-11 | Proposed `context_semantics` shared/separate and `max_input_tokens`, route overrides; total `max_allowed_tokens` meaning preserved; migration CD-7 |
| Contract gap 3 | Accept, routed | #81 `input_tokens` {mean,max}/`tokenizer_assumption`; lineage and context-model binding CD-6; per-stage policies CD-5 |
| Contract gap 4 | Accept; #39 first, then CD-7 | Exact-version rates, cache/region/session conditions and multi-version intake await their owners/versioned migration |

## Incoming requests preserved

T2's [merged handoff ledger](../T2-infrastructure/handoffs.md) requested exact model revision, geometry, prompt/output budgets and permitted artifacts from #5–7. This contribution supplies pinned Qwen facts and a manifest, not a real calibrated build. The older ledger's statements about missing central responses are historical: #3/#40/#41 supplied [specific positions in PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) and later the scoped PR #88 dispositions above. These do not substitute for #10/#11 acceptance of T1's inputs. Do not overwrite that ledger or infer acceptance of all T1 handoffs.

## Review/closure process

Request one coordinated review on the focused T1 PR from the six affected owners: @tynamite, @Mattycodes69, @zabyxc01, @CompleteDotTech, @appletechie and @PUSHINGSQUARES. Record actual comment/review URLs after they exist. Ask owners to **accept**, **accept with constraints**, or **reject** the specific consumer rows, with the reviewed SHA. Do not repeatedly request the same pending decision.

Use `Refs #4`, `Refs #5`, `Refs #6`, `Refs #7` while full acceptance remains pending. PR #88 merged the decision records; that merge does not meet unconfirmed consumer gates. No changes to assignees, acceptance criteria, native blockers or existing decisions are made.

## Requests actually published

[PR #88](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88) requests all six affected owners listed above; GitHub readback confirmed those requests and an empty submitted-review list at publication. [Parent request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/4#issuecomment-6223171020) and [central #40 intake](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6223171381) identify the concrete artifacts and required dispositions. Requests leave all Pending rows pending. Existing signed-in browser access resolved the earlier Project API limitation; #4–7 Status is now In Review, with priorities/readiness/ownership preserved. No Done status or closure is claimed.

The publication paragraph is a historical readback. The 2026-10-17 refresh reads the actual submitted central owner review above, superseding its empty-review state for @tynamite. It makes no new Project or assignment changes. Other consumer rows remain pending until their owners provide a disposition on the specific handoff.


## Reciprocal receiving receipts (2026-10-18)

A live readback found three incoming T4 interface decisions at reviewed main
`7acbefbf4e4e700231e88be272bc89e3a73dde15`. These are receiving dispositions
from the named delegate's co-owner scope, not acceptance of T1's outgoing rows.

| Direction | Receipt and scope | Remaining decision |
| --- | --- | --- |
| #25 -> #6 | [@zwright8 delegate accepts with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6#issuecomment-6242697096): capability evidence is scoped to model/offering/API surface and request conditions, including reasoning, parser/template, strictness and streaming; missing eligible evidence remains unknown | @PUSHINGSQUARES co-owner response and @appletechie's #30 licence-field sufficiency remain separate |
| #28 -> #7 | [@zwright8 delegate accepts with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6242697652): memory/history are part of assembled input; reserve output/thinking without double counting and recount after transforms; independent caps stay independent | @appletechie co-owner disposition, #16 assembly details and #10 reciprocal KV agreement remain separate |

The #25 -> #11 receipt is recorded in the [T2 ledger](../T2-infrastructure/handoffs.md#reciprocal-engine-receipt-2026-10-18).
None supplies runtime measurements, changes v1, accepts the reverse direction, or closes #4–7.

## Current provider receiving reconciliation (2026-10-18)

The five original #5 rows above remain byte-identical as the earlier T1 record. The current decisions below supplement their earlier same-author/Pending states without rewriting that history. Each was actually posted by the coordinating engineer through `CompleteDotTech` under the user's delegated project engineering authority, after reviewing the complete provider input and the relevant receiving interface. These are that engineer's decisions; no personal approval is attributed to an absent co-assignee, and any distinct explicitly required named-person response remains separate.

All five decisions pin producer [model-provider.md at `d81f4cb34099e757096a59b7ad1fe3fda5d8509c`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/d81f4cb34099e757096a59b7ad1fe3fda5d8509c/research/T1-model-selection/model-provider.md), tree `0df599c3152042c70bd81fd241841469c0f988ac`, note `ad87e5f85088892f374e138d27d5e7f5499ae0de`. The receiving note blobs were independently checked unchanged at main `be60732a1353f9d4efab9d1a4c5fbf7627d49abf`. The canonical author fetched and read each actual comment before appending this section.

| Direction / retained current co-assignees | Exact receiving note blob | Actual decision, receipt and UTC time | Retained scope |
| --- | --- | --- | --- |
| #5 → #6 / @zwright8, @PUSHINGSQUARES | `ai-model.md`: `652bee45b1d72e2c883cbcb3457e47baecfcde29` | **Accept with constraints**, [6251441085](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6#issuecomment-6251441085), 2026-10-18T15:04:34Z | Separate publisher/distributor/operator/offering, raw model/revision and access/terms. No cross-route behavior identity, runtime support or broad rights clearance; #25/#30/#33/#40 and broader-family work remain separately owned. |
| #5 → #7 / @zwright8, @appletechie | `context-window.md`: `f4f2d73e6fe47f2e3d6fceb1628e4a32f5ac602c` | **Accept with constraints**, [6251441996](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6251441996), 2026-10-18T15:04:39Z | Route-scoped caps and assembled/reserved token quantities remain separate from observed counts, quality, quota maxima and capacity. Exact price conditions are model/route-specific. Whole-KV acceptance, resident-sequence admission, #10 agreement and #16/#28 assembly remain outside this receipt. |
| #5 → #30 / @zwright8, @appletechie | `../T5-training-fine-tuning/training-framework.md`: `236f72a8977eba022bc967e7a6687ff9dc6bb498` | **Accept with constraints**, [6251442684](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/30#issuecomment-6251442684), 2026-10-18T15:04:43Z | Capability, method/service, account history, rights and export are independent. The OpenAI new-job cutoff and exact derived-inference tables refine F18 without a universal January 6 inference shutdown. Other provider/terms scope limits, the separate actual #6-field receipt, NOTICE/obligation interpretation and T5 gates remain intact. |
| #5 → #37 / @appletechie, @PUSHINGSQUARES | `../T6-deployment-operations/deployment.md`: `f2e0b63deab225f44f5c7611434a90f6b81c597f` | **Accept with constraints**, [6251443356](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6251443356), 2026-10-18T15:04:48Z | Proposed lifecycle/location/quota/authentication/retention/SLA readiness inputs are accepted. No check is executed; actual route/account/credential/region/data-flow, operating horizon, deployment/rollback and whole-Build evidence remain required. Existing hosting/ENGINE/CD-9 limits are preserved. |
| #5 → #39 / @appletechie, @PUSHINGSQUARES | `../T6-deployment-operations/cost-estimate.md`: `6405fd07b1465178c82bcfeab18d13990ad2836e` | **Accept with constraints**, [6251444143](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6251444143), 2026-10-18T15:04:52Z | Preserve all eight exact rates and original unverified grades, eligible meters/thresholds and uncovered costs. Broader Bedrock/newer-model cost evidence remains intact. Regional/default fallback, unchosen-region display, FX, rounding and aggregation are still their own policy decisions; no total CostEstimate or actual quote follows. |

Independent source review is separately recorded in the [current provider note](model-provider.md#actual-independent-evidence-receipts): B/Q/H review5563451005 at `9dc003a`, the actual A6 finding5563489219 at that source, and corrected O/A/G/lifecycle review5563518287 at `d81f4cb`. The one-line A6 correction changes none of the accepted B/Q/H rows or earlier record. Their actual dates, authors and review scopes are retained.

These five current receipts complete the delegated technical intake of #5's specified input. They do not accept every T1/T5/T6 criterion, change frozen v1 or catalog evidence grades, adopt a successor rule/contract, certify a selected service or replace any other outgoing/reciprocal handoff. The historical #6/#7 rows, central #88 positions, earlier #30 licence-field receipt, all other owners and the separate market-ledger pairs remain exact. Final validation, protected delivery, actual main and literal #5/Project reconciliation are tracked in [PR #348](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/348).
