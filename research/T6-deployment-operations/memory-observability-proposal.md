# Memory and deletion observability proposal

Refs #28, #35 and #38. Current status: the research observation interface is accepted by the [actual R4 technical receiving review on #345](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/345#pullrequestreview-5563363848) and recorded in the [canonical monitoring decision](monitoring.md#recorded-engine-framework-and-memory-receiving-decisions-2026-10-18). The proposal identifiers, original signal definitions and evidence limits below are retained; acceptance supplies no vendor-exported metric or installed collector. The earlier [delegated T4 #28 review](../T4-agents-integrations/README.md#t6-receiving-dispositions-and-t4-memory-review-2026-10-18) and absent separate named co-owner confirmations retain their historical scope. The later actual R4 decision is recorded separately below.

## Evidence boundary

The merged [#28 memory record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/8e67caa50e29faf2f15b9004935140f8c9e9e059/research/T4-agents-integrations/agent-memory.md#mem0-deletion-reproduction-and-limits), D57/D58, reports a scoped synthetic reproduction against Mem0 OSS v2.2.1 commit `94c3fe9f238f3dbf29c9ce98643bd71eb13077cd`: deleting the vector still records prior text in SQLite history. The reproduction covers one extracted synchronous method, a synthetic vector stub and upstream in-memory SQLite manager. It does not exercise a full service, actual vector backend, asynchronous deletion, backups or Mem0 Platform. This note inspected that recorded evidence; it did not rerun or expand the experiment.

The [T6 receiving reply](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6240050930) accepts the monitoring handoff narrowly and identifies memory/history growth and deletion-job read-back as follow-up work, explicitly awaiting appletechie's confirmation. The proposal below supplies that missing content without recording that confirmation. #121 has merged; that sequencing condition is complete, while the OpenLLMetry follow-up and other T6 decisions remain separate.

## Candidate signal catalog

IDs below are local proposal identifiers, not telemetry API names. Every row is a **hypothesis / proposed instrumentation requirement** grounded in the layer distinction above; none asserts that a vendor emits this signal. Apply only when the build selects persistent memory and the named layer or lifecycle mechanism exists. A missing optional memory selection is not an error. Local versus hosted placement changes the evidence available, not the meaning of an unknown signal.

| ID | Signal / component | Unit and collection evidence | Threshold source and proposed use | Privacy / missing-data behavior |
| --- | --- | --- | --- | --- |
| MEM-SG01 | Active memory growth, selected store and namespace | Logical active-record count; allocated bytes reported separately by storage, with observation time and documented counting method | Workload capacity/budget and #28 retention policy; dashboard or warning when a declared bound is exceeded | Aggregate counts; no memory text or user identifiers as metric labels. Unsupported count/size observation is unknown, not zero |
| MEM-SG02 | History, tombstone and derived-artifact growth | Counts and bytes per declared layer; distinguish active records from retained history and deletion markers | #35/#38 retention and storage policy; show history even when active count falls | Existence of a tombstone does not prove content erasure. No copies of previous memory text in monitoring |
| MEM-SG03 | Retention sweeper coverage and delay | Last successful sweep time, eligible-item backlog, oldest eligible age; record the policy and eligibility time basis | Selected store's documented expiry behavior and an owner-approved retention objective; no invented universal TTL | A store without a sweeper needs its actual lifecycle path recorded, not a fabricated sweep metric. If eligibility cannot be computed, status is unknown |
| MEM-SG04 | Deletion job state | Requested/accepted/in-progress/completed/failed/unknown state, elapsed time and retry count, tied to sanitized audit evidence | Owner policy for completion and expected delay; pending work remains visible rather than immediately successful | Vendor API acknowledgement is not completion across all layers. Job IDs stay in restricted audit records, not high-cardinality public metric labels |
| MEM-SG05 | Per-layer deletion verification | For each policy-declared layer: observation time, method, scope, residual-record count or bounded verification result; active store/history/derived artifacts/backups tracked separately | #35/#28-approved deletion scope; aggregate completion only when each required layer meets its explicit completion criterion | Record counts/outcomes without raw content. Inaccessible layers stay unknown; approved backup expiry remains pending until its own criterion is met. A sampled check must retain sampling limits |
| MEM-SG06 | Memory access and mutation failures | Counts/error classes for authorized read/write/delete operations, with operation latency and window | Workload latency/error objectives and #35 policy; no universal failure-rate threshold | Do not log values, prompts, secrets or raw identifiers; retain access-controlled incident evidence separately. Missing instrumentation is unknown |

These observations distinguish a completed API request from a completed data-lifecycle requirement. They do not prescribe a purge command, make an erasure guarantee or imply that read-back of one backend covers another. An alert is not enforcement. Cost consumers may use observed storage quantities only with compatible meter/rate scopes; a missing quantity or price remains uncovered.

## Integration and owner decisions

- #28 supplies the selected memory/backend revision, actual layer inventory, lifecycle semantics and observation capabilities. Existing catalog `backing_type` alone does not establish these.
- #35/#38 set the retention objective, deletion coverage, acceptable verification method and access controls. The rows deliberately do not invent a numeric retention period or acceptable residual count for every product.
- #38 decides alert classes and aggregation windows; #40 reviews any eventual fields, enum extensions or executable rules. No frozen schema is changed here.
- #37 owns deployment readiness for actual collectors and credentials; the research note does not create service availability. #39 retains quantity/price applicability and uncovered costs.

## Actual receiving decision and canonical incorporation

The [R4 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/345#pullrequestreview-5563363848)
was submitted on the exact #28 source `c5e1d684aad53a987c33435e56c158ef0bd3ee1b`
and memory-note blob `006cdd26efde4c2c303650245dd211c304ebc363`, subsequently
delivered through signed
[`07e8b9ad1c44973b3ddf2185bc2fa2cd8bbe9d24`](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/07e8b9ad1c44973b3ddf2185bc2fa2cd8bbe9d24).
It explicitly accepts MEM-SG01–06 for actual application-, framework- or
store-backed persistent-memory layers and lifecycle mechanisms, without requiring
a fabricated `memory_store` selection. It preserves the units, methods, times,
event/layer scope, restricted evidence references, content-off default and the
distinction between unknown counts and zero. Sampling limits, inaccessible
layers and backup conditions remain visible.

That is an actual delegated technical receiving decision, not an inferred reply
by a named absent assignee. The older requests and hypotheses above retain their
source dates and original scope. Their candidate instrumentation status means
vendor emission and collection remain unevidenced; it does not mean the accepted
research interface still needs the same receiving decision again.

Determine applicability per observation and actual layer or lifecycle mechanism.
Growth and access/mutation observations do not require a deletion event. The
absence of an applicable deletion job cannot suppress those observations, and an
empty memory catalog selection does not establish absence of application-owned
memory. Unresolved applicability, inventory or observation capability remains
unknown. Do not invent a layer, collector or lifecycle mechanism to fill a row.

The [canonical monitoring record](monitoring.md#recorded-engine-framework-and-memory-receiving-decisions-2026-10-18)
records these accepted definitions and the per-layer completion boundary.
MEM-SG04 job state cannot substitute for MEM-SG05's complete, current event-bound
layer assessment. The actual selected policy still determines retention,
verification methods, numerical objectives, alert classes and collection windows;
unknown policy/configuration remains visible and supplies no fabricated threshold.
The original table is preserved rather than relabelled as observed telemetry.

This reconciles this supplement's status with the actual memory-observation
receiving decision. It does not establish collection, a deployed deletion/retention mechanism,
source-use rights, purge completion, final #40 encoding or whole #35/#38 research
completion. Other monitoring handoffs retain their own status.
