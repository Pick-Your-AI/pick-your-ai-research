# T2: Infrastructure research

Parent: [#8](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/8) · Live co-owners: @zwright8, @Mattycodes69 (checked 2026-10-18) · Contract: 1.0.0 · Research capture: 2026-10-16

Submission: [PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75), merged to `main`. The following publication-era paragraphs are historical; the ledger records later scoped receipts.

Continuation audit on 2026-10-16 re-read live issues, comments, native relationships and the existing PR. Hosting and engine researchers checked source conditions, and an independent compute researcher audited arithmetic. The orchestrator completed compute corrections and shared integration through this existing PR. See [validation.md](validation.md) for corrections and the independent integration review; owner acceptance remains pending.

**Status: #10/#11 research is complete; #8/#9 retain their remaining acceptance criteria.** [PR #291](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/291), merged as [859f47db88f0d8f1a99899ca9029ce0da19800c8](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/859f47db88f0d8f1a99899ca9029ce0da19800c8), delivered the [final research handoff assessment](inference-engine.md#final-research-handoff-assessment--2026-10-18). All nine original #11 criteria are satisfied by reviewed artifacts and scoped consuming-owner confirmations. This completes the engine research deliverable; product implementation, runtime deployment, provisioning and training remain in their owning scopes.

The [precision intake correction](gpu-compute.md#incomplete-precision-intake-correction-2026-10-18) keeps the incomplete H100 SXM and MI300X candidates note-only; the later accepted A100/P4de records retain their separately documented native-precision scope.

## Decision records and artifacts

| Issue | Decision record / recommendation for review | Structured proposals |
| --- | --- | --- |
| [#9 Hosting](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9) | [hosting.md](hosting.md): separate operational responsibility, invocation protocol, location and billing; retain unknown stock/quotas and infrastructure-storage boundaries | [Five host and seven storage proposals](../../catalog/proposals/); [dated Pricebook](../../pricing/proposals/t2-hosting-2026-10-16.json), five conditional rates |
| [#10 GPU / Compute](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10) | [gpu-compute.md](gpu-compute.md): separate physical accelerator from provisionable profile; byte-based weights/KV/runtime/adapter sizing with per-device topology and explicit uncertainty | L40S, RTX 4090 and A100 80GB accelerator records plus two EC2 profiles in [catalog proposals](../../catalog/proposals/); H100 SXM and MI300X remain note-only; [reproducible arithmetic](compute/sizing_examples.py) |
| [#11 Inference Engine](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11) | [inference-engine.md](inference-engine.md): version-specific support tuples and API/parser/adapter semantics; retain historical rows and unknown combinations | [vLLM v0.31.0](../../catalog/proposals/t2-engine-vllm-v0.31.0.json), [llama.cpp v0.7.0](../../catalog/proposals/t2-engine-llama-cpp-v0.7.0.json), [TGI v3.3.7](../../catalog/proposals/t2-engine-tgi-v3.3.7.json) |

The 20 CatalogItems cover all five scoped canonical kinds: `hosting_platform`, `storage`, `accelerator`, `compute_profile`, `inference_engine`. Service/hardware date versions are research snapshots; engine versions are source releases. Catalog `active` is lifecycle metadata, not owner approval or security certification. No new real ResourceEstimate is emitted without real T1 build/selection inputs.

One integrated review submission keeps the shared host/profile/accelerator references resolvable together. Files and acceptance assessments remain separated by research issue. The summary, matrix and ledger are owned by the orchestrator.

## Integrated decisions proposed

1. Cover API, managed and self-hosted/hybrid routes, with GPU/runtime omission for provider-only model APIs. The hosting taxonomy is a proposal to #3, not a replacement schema. Non-model hosting includes vector databases and MCP processes/services, while product and semantic choices stay with their owners.
2. Preserve vendor source units, exact item versions and rate conditions. Prices are observations with timestamps, not complete quotes. GB/GiB, request classes, allowances, tier thresholds, invoice rounding and transfer costs need #39 agreement before automatic aggregation.
3. Treat advertised memory, provisioned allocation and usable runtime memory as distinct facts. A scenario memory screen is separate from engine support and SLO evidence. Runtime overhead/headroom are explicit uncalibrated inputs; unsupported throughput/latency remains unknown.
4. Evaluate model ↔ GPU ↔ engine jointly using exact revisions, dtype roles, quantization kernels, plugins, drivers and topology. Adapter routing, composition, multi-adapter batching and merged weights are separate concerns. #33 retains artifact identity.
5. Retain release-specific evidence and saved-build history; do not copy latest behavior into older rows. The version-retention policy and refresh/invalidation rules remain owner decisions.
6. Keep outcomes `pass/fail/unknown/skipped` separate from severities `info/warning/error`. Documentation-supported premises, independently reproduced compatibility, schema validity, owner acceptance and merge are separate states.

## Contributions for #40 review

There are 11 proposed assertion groups, with explicit applicability, fields, evidence, remediation and passing/failing/unknown examples. Former COMPUTE-05 is now shared applicability:

- [Three hosting rule groups](rules/hosting-rules.md): private-network capability, mounted-volume locality, offering membership and incomplete evidence.
- [Four compute rule groups](rules/compute-capacity.md): per-device memory, joint backend support, KV accounting and topology/inventory, each with shared component applicability. Context-limit checking remains with #7.
- [Four engine rule groups](rules/engine-compatibility.md): artifact/architecture loader, backend/precision implementation, adapter lineage, required API contract.

Rule groups separate fixed-severity constraints from evidence and applicability diagnostics. A rule's outcome does not change its severity; a `pass` on an `error` constraint is still a pass. The proposed clause splits do not publish an approved Ruleset.

[contract-proposals.md](contract-proposals.md) records T2-C01–C06, examples, affected owners and migration implications: price dimensions/aggregation, capacity intervals, allocation/topology, conditional engine support, evidence completeness/mount relationships, and multi-version intake/freshness.

**Executable-consumption gate:** the frozen reference membership rules can hard-fail on entries omitted from researched subsets. They do not implement the unknown semantics proposed here. #40 must review completeness and scoped negative/tuple evidence before these research proposals drive executable compatibility. No imported contract or reference rule is modified.

## Acceptance, handoffs and tracking

The [acceptance matrix](acceptance-matrix.md) preserves every criterion in #8–#11 and maps it to artifacts, evidence and reviewers. All required receiving interfaces are listed in [handoffs.md](handoffs.md): seven from Hosting, four from Compute, five from Engine. The original publication had no receipts. As reconciled on 2026-10-18, Hosting has scoped #10/#27/#31 receipts, appletechie's #15 boundary and historical #37/#39 responses, and [PUSHINGSQUARES's later `9192d5d` response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6247689488) confirming #37 inputs from the delivered map and narrowing #39. #14, the substantive #15 response, receiving review of the #37 map and appletechie's separate scope remain outstanding. Compute has all four #9/#11/#31/#39 receiving directions recorded, including the [actual current delegated review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) at `8a6b8a67`; Engine has #10/#25/#33/#37/#38. The final #11 assessment preserves both T6 receipt revisions and #38's explicit narrowing to source/evidence inputs. Reciprocal #25 -> #11 is accepted with constraints by both #11 co-owners; #27/#28 -> #9 is accepted with constraints by both #9 co-owners, with [appletechie's `66b46d4` receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047) retaining its own scope. A receipt does not accept every co-owner's scope or establish runtime support. The linked ledger records the actual comments.

| Issue | Live coassignees (2026-10-18) | Current research state |
| --- | --- | --- |
| #8 | @zwright8, @Mattycodes69 | Open; merged summary and records, full child acceptance remains |
| #9 | @Mattycodes69, @appletechie | Open; #37's later input confirmation and #39's narrowed unit/exclusion/billing-stage response are recorded. #14, substantive #15, receiving review of the #37 map, appletechie's separate scope, regional breadth and unresolved invoice evidence remain |
| #10 | @Mattycodes69, @appletechie | Closed as completed on 2026-10-18 through [PR #339](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/339); [all ten original research criteria are satisfied](gpu-compute.md#compute-research-artifact-assessment--2026-10-18). The [actual delegated engineering review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) receives all four directions at `8a6b8a67`, including the note-only H100/MI300X withdrawal and implemented headroom condition. The [completion receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250602587) records reviewed delivery, passing post-main CI and issue/Project readback |
| #11 | @zwright8, @Mattycodes69 | Closed as completed on 2026-10-18 through [PR #291](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/291); all nine original research criteria satisfied. Named lifecycle/#42 and runtime follow-ups retain their own scope |

The original Project observations were made on 2026-10-16: `Backlog`, `Tier = T2 Infrastructure`, `Readiness = Ready`, with #8/#10/#11 Critical and #9 High. They are historical, not current board state. An earlier API Project readback on 2026-10-18 failed with `INSUFFICIENT_SCOPES` (`read:project` missing). After #291 merged and #11 closed, a subsequent public [#11 issue-sidebar readback](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11) on the same date showed `Status = Done` in Pick Your AI — AI Builder Research. This records the observed #11 value, not a board write or a readback of other fields/issues. Preserve live fields and priorities; merged partial research alone is insufficient for Done.

After #339 merged, #10 closed as completed at 13:41:40 UTC on 2026-10-18. The coordinating engineer's [post-closure readback](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250602587) records `Status = Done` in the public issue sidebar, following the earlier `In Progress` observation. All ten literal criteria are checked; the original assignees and native relationships are unchanged. This records the observed value without claiming a Project-field write or completion of #8/#9.

Native hierarchy remains #8 → #9/#10/#11. None has a native blocked-by relationship. Scoped issue appendices were corrected to show PR #44 as merged; acceptance wording and ownership were preserved. Related unmerged T5 work was read for handoff context and is not vendor evidence.

## Validation and evidence review

See [validation.md](validation.md) for exact checks, independent review findings, corrections and limits. Python 3.12 baseline checks cover contract/import/generator integrity and submission intake, not factual truth, freshness, reuse rights, deployed behavior or handoff acceptance. The arithmetic script reproduces estimates only. Explicit ResourceEstimate validation checks the existing synthetic contract fixture; no synthetic fixture is promoted as real research.

## Remaining actions and owners

| Action / decision | Owner |
| --- | --- |
| Review remaining region coverage, CPU/edge scope, headroom and engine-retention choices; internal interface receipts are linked, with other co-owner scope separate | #8–#11 @Mattycodes69 |
| Review #3 taxonomy/hybrid semantics; #40 rules, completeness/tuple gate and contract proposals; #41 freshness/reuse policy | @tynamite |
| Confirm model/context/artifact revision assumptions and supply real T1 records for build-bound estimates | #5/#6/#7 @zwright8 |
| Confirm hosting/storage boundary and retrieval-consumer requirements | #13/#14/#15/#16 @zabyxc01 |
| T4 incoming boundaries accepted with constraints; actual tuple specifications/execution remain; #9 co-owner scope separate | #25/#27/#28 @CompleteDotTech |
| T5 scoped reuse and lineage receipts are recorded; missing records and reverse-direction decisions remain separate | #31/#33 live co-owners in [ledger](handoffs.md) |
| Resolve remaining hosting handoffs and pricing aggregation/unit policy; retain the completed compute receiving scopes | #37/#38/#39 @PUSHINGSQUARES |
| Read current Project fields with authorized access before any status update; do not replay historical instructions | @Mattycodes69 / organization Project administrator |

The [current compute assessment](gpu-compute.md#compute-research-artifact-assessment--2026-10-18) retains the 20-record intake and maps the literal #10 research criteria. The [cost record](../T6-deployment-operations/cost-estimate.md#priced-exclusions-beside-the-w1w3-totals) makes L37/L38 visible as not totalled and discloses unapplied headroom on the scoped capacity quantities without changing scenario totals. The [current receiving review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/10#issuecomment-6250287107) confirms those documentary conditions and accepts the changed H100/MI300X availability at its exact source revision. Historical authors and pins remain unchanged. Future calibration, executable rules and build-bound estimates keep their own scope.

Use `Refs #8, #9` for remaining partial work and `Refs #10, #11` for bounded compute or engine follow-ups. #10/#11 have completed their original research criteria through #339/#291. Complete each remaining issue only after its own merged record and full acceptance criteria—including actual owner confirmations—are satisfied; #8 still requires completion of #9 and its other parent criteria.


2026-10-18 supplement: A100 80GB shared-variant facts, RTX 4090 reference-design facts, the P4de default profile and S3 Standard identity are documented in the existing GPU/hosting records. S3 Standard and the subsequent RTX 4090 precision follow-up have catalog proposals. A100/P4de were note-only at the initial capture; the later [native-precision follow-up](gpu-compute.md#a100-and-p4de-precision-and-profile-follow-up--2026-10-18) adds their scoped catalog proposals. Joint engine/artifact compatibility and receiving-owner acceptance remain separate. No rates or measured results are added.

## Interface reconciliation validation (2026-10-18)

Python 3.12.14: pinned `python -m pip install -r requirements-research.txt` completed; `python -m unittest discover -s contracts/v1/tests -v` passed 21 tests; `python -m unittest discover -s tests -v` passed 107 tests with `PYTHONUTF8=1`. The initial Windows-default run failed decoding an existing Apple tracking document as cp1252; UTF-8 mode matched CI without changing tests or that document. `python scripts/validate_research.py` passed 74 CatalogItems and three Pricebooks; `python scripts/validate_market_research.py` passed 33 entities/1,584 cells/20 issues; `python scripts/validate_handoff_audit.py` passed its existing 101-row snapshot; `python prompts/mobile/validate_prompts.py` and `git diff --check` passed. This slice does not refresh #59's separate audit snapshot.

Independent review checked receipt authors, directions, scopes, counts and the preserved #61/headroom gates; its two wording/owner-list findings were corrected. Automated checks establish structure, references and existing behavior, not source truth, rights, freshness, actual engine execution or broader owner acceptance. Vendor facts, pricebooks, frozen v1 and recorded measurements are unchanged.
