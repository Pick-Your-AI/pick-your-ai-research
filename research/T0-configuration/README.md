# T0: Configuration

Issue: #1 · Assignees: @tynamite, @appletechie · Status: partial workstream summary for review · Updated: 2026-10-18

T0 describes the user's workload, serving modes and the shared evidence/build model. A merged research proposal does not change frozen v1 or establish implementation readiness.

## Decisions and record status

| Issue | Record | Merged contribution and remaining scope |
| --- | --- | --- |
| #2 | [Workload / use case](workload-use-case.md) | [#81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81), [#129](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/129): typed workload inputs, optional capability recommendations and request/sequence accounting. Memory persistence is independent of turns within a conversation; injected memory is part of the input budget. Contract decisions and receiving handoffs remain open |
| #3 | [Deployment mode](deployment-mode.md) | #81/#129: classify each serving component by operator and capacity; derive hybrid only from applicable serving components. Billing and a build-level legacy label cannot supply component facts. Versioned migration remains proposed |
| #40 | [Schema and compatibility](component-schema-compatibility.md) | [#126](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/126): fixed severity separate from outcome, scoped evidence, list completeness, rule families, worked examples and conservative migration proposals. Synthetic CD-7 projection fixtures are delivered by [#134](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/134) and hardened by [#145](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/145). Released next-version contracts and affected-owner dispositions remain separate |
| #41 | [Catalog sources and freshness](catalog-data-sources.md) | [#127](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/127): source checking versus independent verification, conflict precedence, source-use routing and change events. Price-specific freshness/conflicts remain with @PUSHINGSQUARES |
| #42 | [Saved-build draft PR](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/114) | Unmerged draft; privacy, revision locking and comparison proposals. #40 remains its prerequisite; merging a partial #40 record does not complete that issue |

## Rule contributions and version boundaries

W-R1–W-R11 cover workload compatibility and recommendations; D-R1–D-R8 and their suffixed cases cover deployment constraints. The authoritative definitions remain in the component records. #40 groups cross-tier proposals into shared families instead of independently publishing every overlapping predicate.

CD-1–CD-13 route typed unknowns, memory/placement, evidence tuples, telemetry, per-stage load, relationships, migration, community evidence, jurisdictions, and other model/organization/multi-selection needs. Consult the records for exact scope and accountable owners. A routing entry is not approval of a field, an executable rule, or a third party's rights.

The migration proposal retains original v1 bytes and historical outcomes. It populates new component modes only from eligible evidence or explicit operator/capacity answers; unknown facts stay unknown. Synthetic M1–M5 and worked T1/T2 examples illustrate expectations. The test-only projection exercises normalized fixture inputs, not a released adapter for real builds. All frozen-v1 schemas/generators remain unchanged.

## Evidence and downstream handoffs

Follow [#41's label mapping](catalog-data-sources.md#mapping-evidence-labels-to-frozen-v1): old `verified` provenance does not by itself prove independent reproduction. Resolve conflicting eligible evidence by scope, version/date, authority and conservative equal-rank numeric bounds; keep genuine ties unknown. Rights decisions remain per-source under #60, and current-state facts retain their dates.

| Consumer | Interface to confirm | Remaining acceptance |
| --- | --- | --- |
| T1 / #5–#7 | Workload modality, route identity, tokenizer and input/output budget semantics | Exact receiving-owner dispositions; documented context limits do not establish measured runtime capacity, which requires separate evidence |
| T2 / #9–#11 | Operator/capacity, hardware placement and request-to-sequence admission | Hardware/runtime evidence and capacity-policy decisions |
| T3 / #13–#16 | Knowledge activation, access boundaries and retrieval budget | Source/embedding/store records and owner receipts |
| T4 / #25–#28 | Actions, memory need, credential relationships and multi-selection semantics | W-R11 is a recommendation; required persistence and CD-13 still need central versioned review |
| T5 / #30–#33 | Training independent from serving mode, permission/lineage and organization attestations | Source-specific rights and affected-owner decisions |
| T6 / #35–#39 | Evaluation targets, deployment/telemetry and cost units | Reconciliation of #121 and focused slices; price semantics and evidence gates |
| #42 | Versioned locks, change events and redacted sharing | #41 invalidation scope accepted in #114; broader contract/retention decisions pending |

## Open decisions and completion gate

@tynamite/@zwright8 own #40 versioned contract disposition; @tynamite/@PUSHINGSQUARES own #41 price-policy completion; @tynamite/@appletechie own #42 sharing/retention choices. Existing co-assignees and consumer owners retain their issue-specific decisions.

All five child issues remain open. This summary fulfills a reviewable navigation/synthesis slice, not the parent's completion criteria. Do not mark #1 Done until the child records, required evidence and receiving handoffs are accepted and the children can legitimately close.
