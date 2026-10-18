# T2: Infrastructure research

Parent: [#8](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/8) · Live owner: @Mattycodes69 · Contract: 1.0.0 · Research capture: 2026-10-16

Submission: [PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75), merged to `main`. The following publication-era paragraphs are historical; the ledger records later scoped receipts.

Continuation audit on 2026-10-16 re-read live issues, comments, native relationships and the existing PR. Hosting and engine researchers checked source conditions, and an independent compute researcher audited arithmetic. The orchestrator completed compute corrections and shared integration through this existing PR. See [validation.md](validation.md) for corrections and the independent integration review; owner acceptance remains pending.

**Status: records and summary merged; research completion is not claimed.** Consuming-owner confirmations and remaining issue criteria still apply. No product implementation, runtime deployment, provisioning or training job is included.

## Decision records and artifacts

| Issue | Decision record / recommendation for review | Structured proposals |
| --- | --- | --- |
| [#9 Hosting](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9) | [hosting.md](hosting.md): separate operational responsibility, invocation protocol, location and billing; retain unknown stock/quotas and infrastructure-storage boundaries | [Five host and five storage proposals](../../catalog/proposals/); [dated Pricebook](../../pricing/proposals/t2-hosting-2026-10-16.json), five conditional rates |
| [#10 GPU / Compute](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10) | [gpu-compute.md](gpu-compute.md): separate physical accelerator from provisionable profile; byte-based weights/KV/runtime/adapter sizing with per-device topology and explicit uncertainty | Three accelerator records and one EC2 profile in [catalog proposals](../../catalog/proposals/); [reproducible arithmetic](compute/sizing_examples.py) |
| [#11 Inference Engine](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11) | [inference-engine.md](inference-engine.md): version-specific support tuples and API/parser/adapter semantics; retain historical rows and unknown combinations | [vLLM v0.31.0](../../catalog/proposals/t2-engine-vllm-v0.31.0.json), [llama.cpp v0.7.0](../../catalog/proposals/t2-engine-llama-cpp-v0.7.0.json), [TGI v3.3.7](../../catalog/proposals/t2-engine-tgi-v3.3.7.json) |

The 17 CatalogItems cover all five scoped canonical kinds: `hosting_platform`, `storage`, `accelerator`, `compute_profile`, `inference_engine`. Service/hardware date versions are research snapshots; engine versions are source releases. Catalog `active` is lifecycle metadata, not owner approval or security certification. No new real ResourceEstimate is emitted without real T1 build/selection inputs.

One integrated review submission keeps the shared host/profile/accelerator references resolvable together. Files and acceptance assessments remain separated by research issue. The summary, matrix and ledger are owned by the orchestrator.

## Integrated decisions proposed

1. Cover API, managed and self-hosted/hybrid routes, with GPU/runtime omission for provider-only model APIs. The hosting taxonomy is a proposal to #3, not a replacement schema. Non-model hosting includes vector databases and MCP processes/services, while product and semantic choices stay with their owners.
2. Preserve vendor source units, exact item versions and rate conditions. Prices are observations with timestamps, not complete quotes. GB/GiB, request classes, allowances, tier thresholds, invoice rounding and transfer costs need #39 agreement before automatic aggregation.
3. Treat advertised memory, provisioned allocation and usable runtime memory as distinct facts. A scenario memory screen is separate from engine support and SLO evidence. Runtime overhead/headroom are explicit uncalibrated inputs; unsupported throughput/latency remains unknown.
4. Evaluate model ↔ GPU ↔ engine jointly using exact revisions, dtype roles, quantization kernels, plugins, drivers and topology. Adapter routing, composition, multi-adapter batching and merged weights are separate concerns. #33 retains artifact identity.
5. Retain release-specific evidence and saved-build history; do not copy latest behavior into older rows. The version-retention policy and refresh/invalidation rules remain owner decisions.
6. Keep outcomes `pass/fail/unknown/skipped` separate from severities `info/warning/error`. Documentation-supported premises, independently reproduced compatibility, schema validity, owner acceptance and merge are separate states.

## Contributions for #40 review

There are 12 proposed assertion groups, with explicit applicability, fields, evidence, remediation and passing/failing/unknown examples:

- [Three hosting rule groups](rules/hosting-rules.md): private-network capability, mounted-volume locality, offering membership and incomplete evidence.
- [Five compute rule groups](rules/compute-capacity.md): per-device memory, joint backend support, context/KV, topology/inventory, API applicability.
- [Four engine rule groups](rules/engine-compatibility.md): artifact/architecture loader, backend/precision implementation, adapter lineage, required API contract.

Rule groups separate fixed-severity constraints from evidence and applicability diagnostics. A rule's outcome does not change its severity; a `pass` on an `error` constraint is still a pass. The proposed clause splits do not publish an approved Ruleset.

[contract-proposals.md](contract-proposals.md) records T2-C01–C06, examples, affected owners and migration implications: price dimensions/aggregation, capacity intervals, allocation/topology, conditional engine support, evidence completeness/mount relationships, and multi-version intake/freshness.

**Executable-consumption gate:** the frozen reference membership rules can hard-fail on entries omitted from researched subsets. They do not implement the unknown semantics proposed here. #40 must review completeness and scoped negative/tuple evidence before these research proposals drive executable compatibility. No imported contract or reference rule is modified.

## Acceptance, handoffs and tracking

The [acceptance matrix](acceptance-matrix.md) preserves every criterion in #8–#11 and maps it to artifacts, evidence and reviewers. All required owner acknowledgements are in [handoffs.md](handoffs.md): seven from Hosting, four from Compute, five from Engine. **Confirmed: none at publication.** A request or independent agent review is not a consuming-owner acknowledgement.

| Issue | Live assignee | Research state after submission | Observed Project state / preserved priority |
| --- | --- | --- | --- |
| #8 | @Mattycodes69 | Open; summary and all child acceptance/merge gates pending | Backlog / Critical |
| #9 | @Mattycodes69 | Open; decision-record PR review and handoffs pending | Backlog / High |
| #10 | @Mattycodes69 | Open; decision-record PR review and handoffs pending | Backlog / Critical |
| #11 | @Mattycodes69 | Open; decision-record PR review and handoffs pending | Backlog / Critical |

All four Project items were observed as `Tier = T2 Infrastructure`, `Readiness = Ready`. The actual board has `Backlog` and a `Tier` field, which differ from the brief/documentation vocabulary. Its existing status options include `Backlog`, `Ready`, `In Progress`, `In Review`, `Blocked`, `Done`; readiness options match the documented Ready/Needs input/Blocked/Awaiting decision set. The correct status for the open record PR is `In Review`, but the CLI token lacks Project scope and the public browser is signed out. No board write is claimed. @Mattycodes69 / Project administrator must set #8–#11 to `In Review` using the existing option, preserving priority and Tier; @tynamite should reconcile documented field names. No status/priority labels, dates, estimates, iterations or native blockers are added.

Native hierarchy remains #8 → #9/#10/#11. None has a native blocked-by relationship. Scoped issue appendices were corrected to show PR #44 as merged; acceptance wording and ownership were preserved. Related unmerged T5 work was read for handoff context and is not vendor evidence.

## Validation and evidence review

See [validation.md](validation.md) for exact checks, independent review findings, corrections and limits. Python 3.12 baseline checks cover contract/import/generator integrity and submission intake, not factual truth, freshness, reuse rights, deployed behavior or handoff acceptance. The arithmetic script reproduces estimates only. Explicit ResourceEstimate validation checks the existing synthetic contract fixture; no synthetic fixture is promoted as real research.

## Remaining actions and owners

| Action / decision | Owner |
| --- | --- |
| Review T2 records and proposed region coverage, CPU/edge scope, headroom and engine-retention policy; explicitly confirm internal T2 handoffs | #8–#11 @Mattycodes69 |
| Review #3 taxonomy/hybrid semantics; #40 rules, completeness/tuple gate and contract proposals; #41 freshness/reuse policy | @tynamite |
| Confirm model/context/artifact revision assumptions and supply real T1 records for build-bound estimates | #5/#6/#7 @zwright8 |
| Confirm hosting/storage boundary and retrieval-consumer requirements | #13/#14/#15/#16 @zabyxc01 |
| Confirm MCP hosting, agent API/tool requirements and memory boundary | #25/#27/#28 @CompleteDotTech |
| Confirm training reuse and adapter/base/merged-artifact semantics | #31/#33 @appletechie |
| Confirm deployment/monitoring handoffs and pricing aggregation/unit policy | #37/#38/#39 @PUSHINGSQUARES |
| Restore Project write access or apply the verified status updates manually, then re-read them | @Mattycodes69 / organization Project administrator |

Use `Refs #8, #9, #10, #11`. Close no scoped issue until its merged record and full acceptance criteria—including actual owner confirmations—are satisfied; close #8 only after all children and the merged summary meet their gates.


2026-10-18 supplement: A100 80GB shared-variant facts, RTX 4090 reference-design facts, the P4de default profile and S3 Standard identity are documented in the existing GPU/hosting records. Only S3 Standard is a new catalog proposal. Hardware/profile facts remain note-only because non-exhaustive precision coverage is unsafe under frozen-v1 membership rules. No rates or measured results are added.
