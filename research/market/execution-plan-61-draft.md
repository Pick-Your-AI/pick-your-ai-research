# DRAFT execution plan: #61 remaining empirical criteria

Refs [#61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61) (parent [#56](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/56)). Status: **DRAFT proposal for the #61 owners and coordinator; not approved, not scheduled, and not evidence.** Prepared 2026-11-01 from `main` at `fef30de`. It restates requirements already recorded in [sizing-validation.md](sizing-validation.md#hardware-required-for-full-scope-continuation-2026-10-18), [measurements/mr09-moe-plan.json](measurements/mr09-moe-plan.json), [measurements/mr09-comparison-spec-2026-10-18.md](measurements/mr09-comparison-spec-2026-10-18.md) and [measurements/h1-prospective-admission.md](measurements/h1-prospective-admission.md). No device was probed, no price was checked, and nothing was reserved, rented, bought or run to write it.

## Spend and hardware decision (Andrew, 2026-11-01)

Recorded 2026-11-01 14:12 PT and 14:13 PT from Andrew (owner): **no paid GPU, rental, cloud or hardware purchase for #61; use existing hardware only, and test on his Mac Studio.** Planned spend is **$0**. DEV-B (purchased/rented GPU), DEV-C (second device or multi-GPU rental) and any provider-charged storage or egress are therefore **not pursued**. **No run of any kind starts on the Mac Studio (or any device) until this plan is complete and Andrew gives an explicit go-ahead for the runs.**

**Approval markers.** Paid compute and hardware purchases were declined on 2026-11-01 (see above); items formerly tagged **[NEEDS ANDREW'S YES]** are now marked **[DECLINED: $0]**. Runs on the Mac Studio are tagged **[WAITS FOR ANDREW'S GO-AHEAD]**. Items that only use already-owned spare local capacity are tagged **[NEEDS OWNER AUTHORISATION]**: #61 requires a named host/session owner and run/stop conditions, and the 2026-10-19 spare-capacity authorisation covered only the H1 cell. Nothing in this plan authorises either.

## Goal and gaps

Close the three unchecked #61 criteria: vary context / cache precision / concurrency; measure peak allocated and reserved memory; report error bounds and failures without universal fit claims. Today matched whole-runtime peak-allocated estimator pairs = **0**; the 15 dense runs, 3 GM1 runs, 12 KV component pairs and 3 H1 initialization observations stay separate cohorts and are not pooled.

## Device list

Capacity numbers are requirements transcribed from the repo, not availability observations. The repo states that its payload floor "does not justify a particular 16/24/48 GB card", so no card is recommended here.

| ID | Device | Source of the requirement | Authorisation / approval |
| --- | --- | --- | --- |
| DEV-A | Existing local RTX 5070 Ti, driver 610.88, ~10.6 GiB free observed 2026-10-19 (host i7-10700K, 16 threads, ~68.6 GB RAM) | [local inventory](measurements/local-comparison-2026-10-19/inventory.json) | [NEEDS OWNER AUTHORISATION]. Spare capacity only; pre-existing workloads untouched. Cannot hold OLMoE BF16 weights (13,838,323,712 B) |
| DEV-MS | **Andrew's Mac Studio (existing, owned; named test machine for the OLMoE cells).** Apple silicon, **48 GiB unified memory** (from a 2026-10-30 operations note; chip model, GPU core count and free disk not recorded and not probed for this plan). Already runs a local MLX inference app; that workload must be left untouched or paused only with Andrew's say-so | Andrew, 2026-11-01 14:13 PT | **[WAITS FOR ANDREW'S GO-AHEAD]**. $0. 48 GiB comfortably exceeds the 14,383,583,232 B OLMoE M1-M4 floor, but unified memory is shared with the OS and other apps, so the free-memory guard must use measured headroom at run time |
| DEV-B | One purchased or rented GPU able to hold OLMoE M1-M4 | [sizing-validation.md](sizing-validation.md) hardware table | **[DECLINED: $0]** (Andrew, 2026-11-01). Replaced by DEV-MS |
| DEV-C | Two or more GPUs for G1 multi-GPU/per-rank | [original matrix](measurements/mr09-protocol-2026-10-16.md) | **[DECLINED: $0]** (Andrew, 2026-11-01). No owned multi-GPU host is recorded, so G1 is not covered by this plan |
| DEV-D | Host RAM >= 32 GiB available and >= 28 GiB free temporary storage for OLMoE copies | [OLMoE copy plan](measurements/mr09-olmoe-artifact-copy-plan-2026-10-19.md) | Must be met on DEV-MS (local disk only). Provider-charged storage or egress **[DECLINED: $0]**. Free disk to be checked as the first step after go-ahead |

## Allocation (cells to devices)

| Cell | What | Device | Notes |
| --- | --- | --- | --- |
| H1 repeat/extend | SmolLM2 F16 GGUF, ctx 256, initialization only | DEV-A | Only via the [prospective admission launcher](measurements/h1-prospective-admission.md); new reviewed freeze first. Optional |
| M1 | OLMoE BF16, prompt 256, active 1, BF16 KV | DEV-MS | Pinned revision `7f1c97f440f06ce36705e4f2b843edb5925f4498`, Transformers 5.0.0. **Backend change needed:** the recorded pin is PyTorch 2.10.0+cu130 (CUDA); the Mac Studio needs a reviewed Apple-silicon pin (PyTorch MPS or MLX) agreed by the #61 reviewers before any run |
| M2 | prompt 2,048, active 1, BF16 KV | DEV-MS | Context axis |
| M3 | prompt 2,048, active 2, BF16 KV | DEV-MS | Concurrency axis |
| M4 | prompt 2,048, active 1, INT4 KV if supported | DEV-MS | Cache-precision axis; cache bytes, backend support and workspace unresolved ([#503](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/503) prepared observations) |
| LC | 8,192-total-position boundary | TBD | OLMoE supports only 4,096 positions; needs a different reviewed model/prompt/cache choice agreed with #7 first |
| G1 | Same dense/MoE, prompt 2,048, active 2, BF16 KV, 32 decode forwards | none ($0) | **Not covered.** Needs two or more devices; DEV-C declined. Report as unsupported under the $0 decision. This narrows the 2026-10-23 "retain full scope" coordinator choice and needs the coordinator to record it |

## Measurements

Per run: peak allocated and peak reserved device memory from the runtime allocator, an independent device-level sample (`nvidia-smi` on DEV-A; on DEV-MS a reviewed Apple-silicon equivalent such as the MPS driver-allocated counter or process footprint, since `nvidia-smi` does not exist there), native initialization-buffer ledger, tracked bytes after cleanup (zero expected), process cap used, driver/runtime/backend versions, device ID, host RAM and temp-disk at start. Every attempt is reserved and retained, including failures.

On DEV-MS, estimators that assume discrete VRAM may not model unified memory; a pair is comparable only if the estimator states it supports Apple-silicon unified memory or the reviewers accept a mapping. Estimators to pair, each with inputs semantically matched to the run (same artifact, runtime, weight/KV precision, actual context, active sequences, offload/topology, measured quantity): llmfit v1.1.17 ([evidence](../../evidence/mr09-llmfit-v1117-catalog.json)), ModelFit v1.5.3 ([evidence](../../evidence/mr09-modelfit-v153-engine.json)), Local AI Planner, and the experimental gguf-parser v0.26.4 derivative ([package](measurements/gguf-parser-mr09/README.md)). More GPU memory alone does not create a comparable pair.

## Method

1. Hardware path is DEV-MS (Andrew's Mac Studio), plus DEV-A for H1. Owners and coordinator still record in writing: host/session owner and location, device IDs/models/count and per-rank allocation, host RAM and storage budgets, exact model/runtime/driver/backend pins, process caps, topology, run/stop conditions, artifact retention and cleanup. State whether it is existing spare capacity or a new reservation.
2. Pin and hash the artifacts (three shards, sizes 4,997,744,872 / 4,997,235,176 / 3,843,741,912 B; publisher LFS SHA-256 are in [sizing-validation.md](sizing-validation.md#olmoe-artifact-metadata-for-storage-preparation--2026-10-20)); compute weight-file hashes locally after download, since the repo has only pointer-file identities.
3. Freeze each prediction and the reviewed source before any hardware run; commit it first. Use the prospective admission launcher; do not call the historical launcher.
4. **Only after Andrew's explicit go-ahead for runs on the Mac Studio:** run three serial fresh processes per cell. Re-check the free-memory guard before each. Stop on any non-success or guard failure; do not provoke OOM or contention on shared devices.
5. Report measured vs predicted per cell with versions and hardware; error bounds only where pairs are matched. Report failures and unsupported cells as such. No tolerance is invented: a decision tolerance needs separate review ([comparison spec](measurements/mr09-comparison-spec-2026-10-18.md)).
6. Deliver as a PR referencing #61 (`Refs #61`); `Closes` only once the three criteria are met and reviewed. Measured data goes to #10 as a `resource-estimate` only if #10 agrees; zero records are admitted today.

## Open decisions

| # | Decision | Owner | Needs |
| --- | --- | --- | --- |
| 1 | Paid GPU rental, serverless or cloud storage/egress | Andrew | **Declined 2026-11-01: $0** |
| 2 | Buy a GPU or second device | Andrew | **Declined 2026-11-01: $0** |
| 3 | Test machine for the OLMoE cells | Andrew | **Decided 2026-11-01: his Mac Studio (DEV-MS)** |
| 4 | Go-ahead to start runs on the Mac Studio | Andrew | **[WAITS FOR ANDREW'S GO-AHEAD]** once this plan is complete and reviewed |
| 5 | Apple-silicon backend pin (PyTorch MPS or MLX) replacing the CUDA pin | #61 reviewers | Reviewed pin before any run |
| 6 | Record the G1 narrowing (no multi-GPU at $0) against the 2026-10-23 full-scope choice | Coordinator | Written record |
| 7 | Use of local spare capacity on DEV-A for H1 | Host owner | [NEEDS OWNER AUTHORISATION] |
| 8 | Long-context model/prompt choice | #61 with #7 | Reviewed lengths |
| 9 | Decision tolerance for estimator error | Reviewers | Separate review; none exists |
| 10 | Whether M4 INT4 KV is supported by the chosen Apple-silicon backend | #61 | Source check before any run |

## Not in this plan

No pricing or availability lookups, no purchase or checkout, no reservation, no download of weights, no execution. Nothing was run on, or probed from, the Mac Studio to write this update. Open PR [#508](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/508) is out of scope.
