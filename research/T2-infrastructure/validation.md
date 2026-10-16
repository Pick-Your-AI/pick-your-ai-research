# T2 validation and evidence review

Research capture and review: 2026-10-16 · Contract baseline: imported v1 unchanged · Initial runtime: Python **3.12.7**; continuation runtime: Python **3.12.14**, isolated `.venv`

## Continuation audit

This pass continues existing PR #75. It refreshed #8–#11, all direct consuming issues, additional T1/storage/artifact/policy inputs, PR reviews/inline comments and native parent/sub-issue/dependency state. Assignees remain unchanged. No submitted owner review or required handoff acknowledgement was present. Public Project views again show #8–#11 as `Backlog`, `Tier = T2 Infrastructure`, `Readiness = Ready`, with priorities Critical/High/Critical/Critical. CLI `gh project field-list` and `item-list` still fail for missing `read:project`; the in-app browser is signed out. No Project write, owner acceptance or merge is claimed.

Three bounded package audits ran in parallel. Hosting and engine researchers corrected their own records; the orchestrator completed compute corrections and shared integration from the existing PR baseline. A separate researcher who authored none of these changes reviewed the integrated diff, sources and arithmetic. This independent review is distinct from required human owner review.

Corrections supported by primary sources re-opened on 2026-10-16:

- Hosting: Runpod funding-dependent deletion and concurrent-write constraints; Modal daily storage billing snapshots, possible four-day post-delete charges and v1 inode limit; R2's documented 30-day storage metric. Existing rates remain conditional dated observations, not complete quotes. See H21/H23/H28 in [hosting.md](hosting.md).
- Engines: vLLM v0.31.0's tagged ROCm wheel table names older release ranges/nightly builds; general backend support does not pin a tested v0.31.0 binary/digest/runtime tuple. That packaging evidence remains unknown with a named #11/#37 follow-up. Omitted optional `adapter_only` evidence cannot silently mean merged weights. See E05 and [engine rules](rules/engine-compatibility.md).
- API contracts: the current tool-calling source distinguishes structural-tag tool envelopes from strict argument-schema enforcement; parser/template, per-tool strictness and server overrides stay explicit consumer inputs rather than a universal tool-support boolean.
- Rule groups: each proposed clause has fixed severity; missing-evidence and applicability diagnostics have separate IDs. Passing or unknown outcomes do not rewrite the constraint's severity. Frozen v1 is unchanged and #40 approval remains pending.
- Compute: pinned the Qwen tensor index to its immutable revision and fetched its exact metadata bytes; refreshed the directly readable AWS allocation source and AMD ROCm backend evidence; retained the AMD 192 GB/GiB source conflict. Historical/current engine evidence is separated, dense-model DP is distinguished from MoE placement, host-offload terms are explicit, and runtime memory-pool headroom is counted once. Estimator v0.2.0 adds hypothetical merged-only, headroom-boundary, missing-geometry and API-only examples without fabricating runtime estimates. A load-to-count procedure preserves unknown SLO capacity when matching performance evidence is absent.

On Python **3.12.14**, after installing `requirements-research.txt`, the 21 contract tests and 11 research tests pass; submission validation accepts 16 CatalogItems and one Pricebook. Explicit ResourceEstimate schema validation accepts the existing synthetic reference fixture only. No real build-bound resource/quality artifact is invented. Fresh issue-body comparison confirms **32 unchanged criteria**. Exact-case local Markdown links were checked; schema validation and arithmetic are separate from source, rights, freshness and owner review.

Source retrieval limits were checked separately. The engine auditor could not freshly retrieve llama.cpp's tagged `docs/models.md` through the web cache. The orchestrator recovered that exact v0.7.0 publisher file through GitHub's contents API (blob `eee5952634be3dbf7133f68c7be831d8bc69f6c7`) and confirmed its GGUF loader requirement. No mutable replacement source was substituted. The hosting auditor re-opened all 33 listed source URLs and checked the main rates and conditions; engine review sampled the release-specific support sources. This is source review, not an independent runtime reproduction or a grant of commercial reuse rights.

The independent continuation reviewer checked the integrated hosting/engine/shared diff, then the compute changes, without authoring any file. Two findings were corrected: `pass/error` can still emit a finding retaining severity and must not be described as suppressing a diagnostic; COMPUTE-04's passing example must satisfy its multi-device/multiple-instance applicability. The latter now uses two independent one-GPU dense-model replicas and remains inventory-only. Source spot-checks covered current release requirements, strict tool-schema conditions, AMD/AWS allocation units, Qwen metadata and compute assumptions. Python 3.12.14 reruns passed all 32 baseline tests, intake, explicit synthetic ResourceEstimate shape validation, the v0.2.0 arithmetic and 116 exact-case local links. All 32 issue criteria remain verbatim. This review does not approve runtime compatibility, licensing or owner handoffs.

Publication of the corrections through commit `30b989672848e688a37c45cbaa3faeaceb480ece` passed [GitHub Research validation run 38907359548](https://github.com/Pick-Your-AI/pick-your-ai-research/actions/runs/38907359548). [Parent progress](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/8#issuecomment-6216457112) and [PR audit comment](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#issuecomment-6216458237) link the concrete changes and outstanding owner/Project actions. The six review requests remain pending; no owner approval or merge is inferred from successful CI.

## Automated checks executed

From the repository root, the pinned `requirements-research.txt` was installed with `python -m pip install -r requirements-research.txt`. The environment's interpreter was `.venv/Scripts/python.exe`; the commands below use `python` for readability.

| Command / check | Result | What it establishes |
| --- | --- | --- |
| `python -m unittest discover -s contracts/v1/tests -v` | **21 tests passed** | Canonical schemas, synthetic fixtures, local reference resolution and baseline evaluator behavior |
| `python -m unittest discover -s tests -v` | **11 tests passed** | Original import hashes, generated-content consistency, all-kind issue mapping and research intake rejection/acceptance behavior |
| `python scripts/validate_research.py` | **16 CatalogItem proposals, 1 Pricebook passed** | Required shapes, local catalog references, exact price versions, public provenance URL shape, dates, IDs and evidence metadata intake |
| `python research/T2-infrastructure/compute/sizing_examples.py` | **Passed arithmetic assertions and emitted scenario bounds** | Reproducibility of the stated project formulas/inputs; no device execution |
| `python contracts/v1/reference/validate_payload.py contracts/v1/schemas/resource-estimate.schema.json contracts/v1/examples/resource-estimate.json` | **VALID** | Explicit schema check of the existing **synthetic reference fixture**, not a new real build estimate |
| Exact-case local Markdown links and matrix comparison to fetched issue baseline | **32 unchanged criteria checked**; local links checked after integration | Required issue wording retained, links resolve with tracked filename case |

The Pricebook contains five rates. No new real ResourceEstimate or quality-evaluation payload is submitted; absent real T1 build/selection inputs are recorded rather than invented. The calculation script emits research arithmetic, not a schema-bound runtime artifact. No external binary artifact was created or redistributed, so no new evidence manifest is needed.

A sandboxed repeat of the research tests encountered Windows temporary-directory `PermissionError` failures. Re-running the same unchanged tests with normal host permissions passed all 11, as in the original baseline. This was an environment access failure; the imported tests and contract were not changed to bypass it.

## Independent review and corrections

GitHub-hosted [Research validation run 38904722208](https://github.com/Pick-Your-AI/pick-your-ai-research/actions/runs/38904722208) completed successfully for initial submission commit `83a66fe2f9b59241e8cf3296780c040b32418967`. Latest checks and human review state are visible on [PR #75](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75). Subsequent changes record publication/tracking links and do not change vendor facts or calculations.

A separate agent, which authored none of the package, inspected the integrated records, canonical semantics and representative primary sources before owner review was requested. It found two actionable issues:

1. Governance links used uppercase `GOVERNANCE.md` while the tracked path is `docs/governance.md`. The links were corrected and exact-case local link checking added to the integration review.
2. Engine arrays are researched subsets, but the imported reference `precision.engine` and `engine.model.format` membership checks can hard-fail on omitted entries. The engine record, summary and T2-C04/C05 review request now explicitly gate executable negative membership on #40's completeness/conditional-tuple decision. The frozen reference rules remain unchanged.

The orchestrator ran the sizing script and corrected its rank-16 Q/V LoRA arithmetic: **10,092,544 bytes per adapter**, **40,370,176 bytes for four**, with the note's derived sensitivity updated. Two displayed scenario lower bounds were aligned with calculation output: BF16 loaded **36.012 GB** and hypothetical INT4 **23.743 GB** to three decimals. All are project estimates, not measured device results.

The on-premises priced example was refreshed against the current NVIDIA US storefront; the older manufacturer announcement stays explicitly historical. Mutable prices remain dated observations with checkout, region, tax, shipping, quota and supply limitations.

## Source and evidence checks

The independent review spot-checked primary sources for:

- HF dedicated L4 rate; Modal GPU/CPU/RAM/storage rates; R2 rates, request classes, allowances and rounding; Runpod storage tiers.
- L40S, H100 SXM and MI300X physical specifications; AWS G6e allocation and CPU-core/vCPU distinction.
- Current vLLM GGUF plugin, CUDA/ROCm build requirements and tool-call flag behavior; llama.cpp LoRA batching distinction; TGI maintenance and quantization constraints.
- Pinned Qwen tensor bytes, attention/KV geometry and historical benchmark conditions.

The reviewer reported no additional material source/price/hardware/engine errors in those checks and considered the submission suitable for human research review once its findings and this summary were completed. The orchestrator separately re-opened current vendor sources for selected hardware, CPU allocation, storage/egress prices and the on-premises storefront. This is a bounded evidence review, not an exhaustive independent reproduction of every support tuple.

## Practical limits and remaining review

- No runtime deployment, hardware benchmark, vendor capacity reservation, account quota probe, training job or performance calibration was performed.
- Publisher performance statements remain vendor claims. Scenario ranges are sensitivity bounds, not statistical confidence intervals or validated error bars.
- Schema passes do not establish price completeness, source truth, evidence freshness, commercial reuse rights, license interpretation, runtime compatibility, security/compliance approval, or owner acceptance.
- Catalog provenance `verified` means the stated field was checked against its cited source; it does not certify an end-to-end model/runtime/device combination.
- Documentation licenses and service terms do not automatically establish rights to redistribute model/adapter weights or mirror vendor pages. #41 retains source reuse and freshness decisions.
- All 16 required consuming-owner handoffs remain pending. This independent agent review is not a GitHub owner acknowledgement or PR approval.
- Project fields were publicly inspected, but CLI Project scopes and an authenticated browser session were unavailable. The proposed `In Review` update is an explicit administrator action, not a completed write.

See [acceptance-matrix.md](acceptance-matrix.md), [handoffs.md](handoffs.md) and [contract-proposals.md](contract-proposals.md) for the remaining review/merge gates, owners and exact questions.
