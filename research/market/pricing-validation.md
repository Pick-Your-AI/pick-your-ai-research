# MR-07: Validate price freshness and total-cost scenarios

Issue: [#64](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/64). Assignees (GitHub readback, 2026-10-18): @appletechie and @PUSHINGSQUARES. Status: independent integration review accepted the bounded desk audit in [PR #199 review 5561243681](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/199#pullrequestreview-5561243681); the separate #9/#39/#41 consuming-owner handoffs remain pending. This record answers the research-completeness question, not the cost or service equivalence of an installed build.

## Question
Can local and hosted configurations be compared with complete cost units?

## Starting evidence
[monetization.md](monetization.md) (structure only, no rates); Pricebook proposals on `main` at `f297ac5`: [`t1-api-2026-10-16.json`](../../pricing/proposals/t1-api-2026-10-16.json) (8 rates) and [`t2-hosting-2026-10-16.json`](../../pricing/proposals/t2-hosting-2026-10-16.json) (5 rates); dated GPU notes in [training-compute.md](../T5-training-fine-tuning/training-compute.md) (checked 2026-10-16). This note is not a new canonical component catalog, a Pricebook or a completed measurement. It copies no rate into a new record: every amount below cites its Pricebook rate ID or note row.

## Protocol and acceptance
- [x] Pin provider, date and billing units; record published regional scope and explicit region/availability unknowns.
- [x] Include idle capacity, storage, egress and utilization, or identify their unpriced and unmeasured portions explicitly.
- [x] Complete the 2026-10-18 primary-source recheck of all thirteen cited rates; repeat material checks before a later recommendation.
- [x] Report assumption ranges and event-based invalidation triggers.
- [x] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain the separate consuming-owner acceptance for the #9/#39/#41 handoffs; the actual independent integration review is recorded below.

The [criterion map](#6-criterion-map-against-the-live-64-checklist) records the completed evidence and the exact receiving scopes for review. The live question explicitly permits idle, storage, egress and utilization to be shown as unknowns. A complete research audit can therefore conclude that its example quotes have incomplete coverage; it must not turn those omissions into zero or a service recommendation.

## 1. Freshness recheck (2026-10-18)

The original pass was dated 2026-10-17. This second pass reread the same primary rate sources on 2026-10-18, using the published HTML/text and, where extraction omitted a material value, the publisher's Markdown or structured HTML data as identified below. No account, API key or paid call was used. Evidence class: primary documentation (vendor-published list price); confidence is high that the source states the value at this recheck, not that an account can buy it or meet a workload. Pricebook `verification_status: unverified` remains appropriate: source checking is not independent invoice, entitlement or quota verification.

| Rate ID | Catalog item @ version | Meter | Pricebook | Rechecked 2026-10-18 | Region / scope | Result |
| --- | --- | --- | --- | --- | --- | --- |
| `rate.t1.gpt54.input.short` | `cat.model.gpt54_openai` @ `gpt-5.4-2026-03-05` | `input_tokens_1m` | USD 2.50 | USD 2.50 per 1M input | Global standard; prompts ≤272K | Match (0, 0%) |
| `rate.t1.gpt54.output.short` | same | `output_tokens_1m` | USD 15.00 | USD 15.00 | same | Match |
| `rate.t1.gpt54.cache.short` | same | `cached_input_tokens_1m` | USD 0.25 | USD 0.25 cached input | same | Match |
| `rate.t1.gpt54.input.long` | same | `input_tokens_1m` | USD 5.00 | "2x input" for prompts >272K, full session → 2 × 2.50 | same | Match (derived) |
| `rate.t1.gpt54.output.long` | same | `output_tokens_1m` | USD 22.50 | "1.5x output" → 1.5 × 15.00 | same | Match (derived) |
| `rate.t1.sonnet55.input` | `cat.model.sonnet55_anthropic` @ `claude-sonnet-5-5` | `input_tokens_1m` | USD 2.00 | USD 2 / MTok base input | Global default; full 1M context at standard rate | Match |
| `rate.t1.sonnet55.output` | same | `output_tokens_1m` | USD 10.00 | USD 10 / MTok | same | Match |
| `rate.t1.sonnet55.cache` | same | `cached_input_tokens_1m` | USD 0.10 | USD 0.10 / MTok hits and refreshes (0.05x) | same | Match |
| `hf-aws-l4-replica-hour` | `huggingface-endpoints-aws` @ `2026-10-16` | `gpu_hour` | USD 0.80 | aws `nvidia-l4` x1 USD 0.8/h; "shown by the hour … calculated by the minute" | AWS, no region bound on page | Match |
| `runpod-standard-small-us-ks-2` | `runpod-network-standard-us-ks-2` @ `2026-10-16` | `storage_gb_month` | USD 0.07 | Standard, first 1 TB USD 0.07/GB/month | Page rate is not data-center specific; `US-KS-2` appears only as an API example | Match |
| `r2-standard-storage` | `cloudflare-r2-standard` @ `2026-10-16` | `storage_gb_month` | USD 0.015 | USD 0.015 / GB-month; free 10 GB-month | Location-neutral | Match |
| `r2-standard-class-a-request` | same | `request` | USD 0.0000045 | USD 4.50 / million; free 1M/month | same | Match |
| `r2-standard-class-b-request` | same | `request` | USD 0.00000036 | USD 0.36 / million; free 10M/month | same | Match |

**Totals: 13 published rates match the referenced Pricebooks; no numeric drift was observed. All remain source-checked, not independently verified.** Sources: [OpenAI GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4), [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), [HF Inference Endpoints pricing](https://huggingface.co/docs/inference-endpoints/pricing), [RunPod network volumes](https://docs.runpod.io/storage/network-volumes), [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/).

Conditions observed today that the Pricebook already excludes but a quote must not ignore: OpenAI regional-processing endpoints +10%; Anthropic `inference_geo: "us"` 1.1x; Anthropic 5-minute (USD 2.50) and 1-hour (USD 4) cache writes; RunPod standard volume USD 0.05/GB/month beyond 1 TB; R2 rounds up to the next billing unit; HF scale-up replicas bill at the same per-replica rate.

Retrieval details for material conditions:

- **OpenAI:** the model page's linked [Markdown](https://developers.openai.com/api/docs/models/gpt-5.4.md) states the full-session multipliers for prompts above 272K input tokens; the public [pricing Markdown](https://developers.openai.com/api/docs/pricing.md) separately lists the short/long rate columns. The HTML text extraction omitted that multiplier paragraph, so it was not used to infer an absence. The source records a 10% regional-processing uplift; these scenarios select global standard rates.
- **Anthropic:** the pricing table and cache/data-residency sections explicitly identify Sonnet 5.5's three referenced rates, cache-write prices and US-only multiplier. Partner-operated platform prices are separate.
- **Hugging Face:** the AWS `nvidia-l4` x1 row and minute-billing paragraph were read. A globally listed price does not establish region-specific availability; billing includes eligible initialization and running time.
- **RunPod:** the network-volume page supplies the tier prices; `US-KS-2` is in its API example, not a regional rate table. The GPU pricing page's `application/ld+json` product `#gpu-rtx-4090` contains separate USD per-hour offers for Community and Secure Cloud. The visible text extraction exposed only Secure's $0.89; the $0.34 Community value was read from the publisher's actual structured HTML, not inferred from the toggle or a search snippet. Neither proves live supply.
- **Cloudflare:** Standard storage, Class A/B units, the monthly free tier, upward billing-unit rounding and the direct-R2 egress footnote were read together. The examples assume the quoted free allowances remain available to this workload; another workload consuming them changes the bill.

Note-only rates used in scenarios (not Pricebook rates, so a CostEstimate line has no `price_rate_id` for them):

| Note row | Source | Earlier note | Rechecked 2026-10-18 | Result |
| --- | --- | --- | --- | --- |
| RunPod RTX 4090, Secure / Community, per GPU-hour | [runpod.io/pricing](https://www.runpod.io/pricing) (page "Updated October 8, 2026") | USD 0.89 / 0.34 | USD 0.89 / 0.34 | Match; region not stated |
| US average electricity price, July 2026 (cents/kWh) | [EIA Electric Power Monthly Table 5.6.A](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a), released 2026-09-24 | — | Residential 18.31, commercial 14.53, Hawaii residential 48.00 | Matches the July 2026 table used on 2026-10-17; preliminary statistical average, **not a tariff** |

## 2. Total-cost scenarios (30-day horizon, USD, list prices, pre-tax)

Labelled assumptions (A) are hypotheses, not measurements. Arithmetic uses decimal multiplication rounded half-up to cents per line, then sums those rounded lines. Low/expected/high are assumption bands, not a confidence interval. No currency conversion. Amounts are partial subtotals for the stated 30-day period, not an accepted cost model or a complete bill.

### S1 — Assistant inference: hosted API vs dedicated endpoint vs local GPU

- A1 volume per 30 days: low 5M input / 1M output; expected 20M / 4M; high 80M / 16M tokens; every prompt ≤272K.
- A2 cache-hit share of input: low 60%, expected 30%, high 0%.
- A3 endpoint/local active hours: low 160 (8 h × 20 days, scale-to-zero), expected 360 (50%), high 720 (always on, one replica).
- A4 local whole-system draw: low 0.30 kW × 160 h; expected 0.45 kW × 720 h; high 0.60 kW × 720 h (local box left on). Price: EIA commercial 14.53 / residential 18.31 / Hawaii residential 48.00 cents/kWh.
- A5 one L4 replica or one local GPU can serve A1 at acceptable latency, and the open model is an acceptable substitute for the API models. **Both unverified**: no ResourceEstimate or QualityEvaluationRun exists, so S1 compares cost lines, not equivalent service.

| Path | Lines | Low | Expected | High | Coverage |
| --- | --- | --- | --- | --- | --- |
| Sonnet 5.5 API | `rate.t1.sonnet55.*` | 14.30 | 68.60 | 320.00 | Partial: cache writes, tools, tax uncovered |
| GPT-5.4 API | `rate.t1.gpt54.*.short` | 20.75 | 96.50 | 440.00 | Partial: tools, residency uplift, tax uncovered |
| HF L4 endpoint, 1 replica | `hf-aws-l4-replica-hour` × A3 | 128.00 | 288.00 | 576.00 | Partial: storage, egress, extra replicas, init time, tax, operator time uncovered |
| Local GPU, power only | A4 × EIA | 6.97 (48 kWh) | 59.32 (324 kWh) | 207.36 (432 kWh) | **Lower bound only**: hardware capital uncovered (no sourced price), actual tariff, cooling, operator time uncovered |

Reading: the API token-charge subtotals are below the dedicated endpoint compute subtotal in all three bands, including the high band ($320 for Sonnet and $440 for GPT versus $576 for the endpoint). These partial line items do not establish a complete cost or service ranking: A5 remains unverified, and omitted charges and service differences must be resolved before recommending an option. The local row cannot support a complete cost comparison until hardware capital and the user's actual tariff are sourced.

### S2 — Fine-tune an 8B model (LoRA/QLoRA) and serve it for 30 days

- Training workload from [training-compute.md](../T5-training-fine-tuning/training-compute.md) Scenario A: 30M training tokens; 2.703 h (LoRA, B2) or 3.454 h (QLoRA, B3) on one RTX 4090, compute-only.
- A6 training rate band: low LoRA × Community 0.34; expected LoRA × Secure 0.89; high QLoRA × Secure 0.89.
- A7 working volume (data, checkpoints) held a full month: 50 / 100 / 200 GB on RunPod standard volume; artifacts on R2: 10 / 20 / 50 GB.
- A8 R2 operations within the free allowance for low/expected; high 3M Class A and 30M Class B. The Standard free allowance is applied once at its monthly scope and is assumed unused by other work; it is not re-granted per component.
- Serving: S1 HF L4 band (A3), or S1 local power band (A4).

| Line | Rate | Low | Expected | High |
| --- | --- | --- | --- | --- |
| Training GPU | RunPod 4090 note row | 0.92 | 2.41 | 3.07 |
| Working volume | `runpod-standard-small-us-ks-2` | 3.50 | 7.00 | 14.00 |
| Artifact storage after 10 GB free | `r2-standard-storage` | 0.00 | 0.15 | 0.60 |
| R2 Class A / B after free allowance | `r2-standard-class-a/b-request` | 0.00 (A8) | 0.00 (A8) | 9.00 + 7.20 |
| Serving | `hf-aws-l4-replica-hour` | 128.00 | 288.00 | 576.00 |
| **First 30-day hosted subtotal** (one-off training plus the stated recurring lines) | | **132.42** | **297.56** | **609.87** |
| Local alternative: training + serving power | A4 × EIA | 0.12 + 6.97 = **7.09** | 0.22 + 59.32 = **59.54** | 0.99 + 207.36 = **208.35** |

The one-off training GPU subtotal is $0.92 / $2.41 / $3.07. The selected volume, artifact, request and serving lines total $131.50 / $295.15 / $606.80 for the 30-day period; they recur only while the same quantities and retained-storage assumptions continue. Training is not charged again merely because another billing period starts. Serving is 96.79% of the expected first-period hosted subtotal (288 / 297.56, estimated), a result of these assumptions rather than a universal hosting ratio. The local alternative is again a power-only lower bound. Training excludes setup, data loading, evaluation, retries and minimum increments (T5 caveat). The independently scoped [T6 W5](../T6-deployment-operations/cost-estimate.md#w5-fine-tuning-a-one-off-job-and-continuing-hosting) illustrates Together/Azure provider training and hosting formulas separately; it does not make this RunPod/HF scenario complete.

Neither scenario reaches `coverage=complete` under [PRICING_AND_GATES.md](../../contracts/v1/docs/PRICING_AND_GATES.md); `cost.monthly_total_amount` must stay `unknown`.

## 3. Uncovered meters (for #39; never zero)

| Meter / cost | Where it bites | Status |
| --- | --- | --- |
| Idle capacity | HF replicas billed while running/initializing whether or not serving; local box idle draw; RunPod volume billed while compute is stopped | Modelled only by assumption bands A3/A4; no meter for idle vs active |
| Egress | HF endpoint and RunPod transfer; local ISP | No v1 meter; unpriced. R2 states egress free (documented, not a Pricebook line) |
| Utilization / capacity | Tokens per GPU-hour, replicas needed for A1 | No ResourceEstimate; A5 unverified |
| Operator time | Local maintenance, endpoint ops | No meter, no sourced rate |
| Commitments / reservations | Provisioned throughput, reserved instances (T5 P4/P9) | Not modelled; on-demand list only |
| Hardware capital and depreciation | Local paths | No sourced price; `one_time` meter exists but no catalog/price record |
| Electricity tariff | Local paths | Only an EIA average (not a tariff); no meter for kWh |
| Cache writes | Anthropic 5 m / 1 h writes | Published, not in Pricebook |
| Tools, residency uplifts, long-context cache | OpenAI tools, +10% regional; Anthropic 1.1x US geo | Published, not in Pricebook |
| RunPod pod GPU-hour | S2 training | Note rate only; catalog `runpod-pods` has no Pricebook rate |
| Volume >1 TB tier, sub-hour rounding | RunPod | Excluded by rate condition; rounding unresolved |
| Tax | All | Not modelled |

## 4. Invalidation triggers

Recompute both scenarios and recheck the affected source before any recommendation when:
- any cited rate, free allowance, multiplier (long context, cache, residency) or billing granularity changes, or a source page stops stating it;
- a new SKU, GPU type or model snapshot replaces `gpt-5.4-2026-03-05`, `claude-sonnet-5-5`, AWS L4 or RTX 4090, or a catalog item version changes;
- the region or data-center changes (HF region unbound; RunPod data center; residency/geo endpoints);
- the currency is not USD or a quote needs tax;
- the workload assumptions A1–A8 move outside their bands, prompts exceed 272K, or a ResourceEstimate/quality run contradicts A5;
- the Pricebook revision, selected catalog version, eligible evidence for that tuple, applicable rule version or source-use decision changes; or an explicit source validity boundary is reached.

The earlier unaccepted 30-day staleness suggestion is withdrawn. This audit applies [#41's recorded event-based policy](../T0-configuration/catalog-data-sources.md#freshness): elapsed time alone neither expires a historical fact nor invalidates a saved build. Keep its access date visible. A source retrieval failure does not prove withdrawal; it prevents a claim that the current recommendation was freshly verified. Actual rate/condition drift is routed below, without silently rewriting the retained Pricebook or the saved historical view.

## 5. Drift routing

No numeric drift was found in the 13 referenced rates on 2026-10-18, so this reread proposes no new Pricebook revision. T1/T2 retain the complete dated rate records and source-specific applicability. RunPod's rate is not data-center specific despite the historical item ID; HF's public table likewise does not guarantee an eligible region or quota. For a future quote, change the region, quantity, allowance, tier or commitment only from eligible selected-offering evidence, then recompute. Uncovered costs are routed to #39; source/conflict/reuse conditions follow #41/#60. The pricebooks remain unchanged.

## 6. Criterion map against the live #64 checklist

| Live criterion | Artifact / evidence | Research result | Remaining operational or policy limit |
| --- | --- | --- | --- |
| Pin provider region date and billing units | Section 1; exact Pricebook rate/item versions | Thirteen rates source-checked on 2026-10-18 with units, USD and known scope. HF region and RunPod data-center rate binding remain explicitly unknown. | A future selected deployment needs its own eligible regional/entitlement evidence. |
| Include idle capacity storage egress and utilization | S1/S2 A1–A8; section 3 | Included as explicit assumption bands, priced lines or named unknowns, as the issue's research question permits. No unknown is zero. | Both example quotes retain incomplete coverage. |
| Recheck live rates before recommendations | Section 1 and retrieval notes | Fresh reread complete; no service-equivalence or cost recommendation is issued. | Recheck material inputs before any later recommendation. |
| Report ranges and invalidation triggers | Sections 2 and 4 | Assumption bands are separate from confidence intervals; one-off and recurring costs and event-based invalidation are explicit. | No automatic TTL, new FX policy or universal amortization convention. |
| Every significant conclusion linked to evidence or hypothesis | Rate IDs, primary links, A1–A8 and formulas | Source statements and derived arithmetic remain distinct from runtime/quality hypotheses. | A5 capacity and quality equivalence is unmeasured. |
| Relevant technical owners review handoffs; unresolved decisions named | Scoped receiving package below; [review 5561243681](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/199#pullrequestreview-5561243681) | Independent integration review accepted all three bounded scopes at `c08484c`; its exact receipt is preserved in the canonical ledger. Consuming-owner acceptance is still pending. | Live assignees are unchanged. Each named consumer must accept, reject or narrow its handoff; residual T2, #39 and #41/#60 questions remain with that consumer. |
| Repository checks pass; reviewer accepts evidence | Section 7 and [review 5561243681](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/199#pullrequestreview-5561243681) | Independent evidence, source and arithmetic review accepted; validation recorded below. | Current-head CI and the reviewed merge establish publication of this partial audit; #64 remains open for its separate consuming-owner acceptance criterion. |

### Scoped receiving package

These are concrete research interface decisions under the user's project-wide engineering delegation. They preserve live GitHub assignees and do not assert a response by an assignee who did not post one. The [independent integration review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/199#pullrequestreview-5561243681) accepted each scope on 2026-10-18 at `c08484cdc27ad43d7251da5f31ca2fad3a89c28a` (tree `3f5ae899cefadfa6dca5b637a6ded3d9dd46c37b`). These exact integration decisions are recorded in the shared handoff ledger as post-snapshot reviews, separate from its 02:50:05Z assignee-response audit. They do not satisfy the separate consuming-owner acceptance requirement: the three canonical `receiving_review_status` fields remain `not_yet_confirmed`. Each consuming owner still needs to accept, reject or narrow the corresponding research input.

| Consumer | Scope accepted by independent integration review | Named remaining question |
| --- | --- | --- |
| #9 Hosting | **Accepted:** the conditional HF per-replica/minute and RunPod volume/tier source observations as dated hosting inputs. Region, quota, startup duration and service equivalence remain unknown where the source or scenario does not establish them. | T2 hosting/compute owners retain selected-region availability, endpoint startup and actual capacity evidence. |
| #39 Cost Estimate | **Accepted:** the arithmetic audit, one-off/recurring split, scoped allowances and explicit uncovered-meter inventory as research inputs. The output is a partial subtotal, so it cannot pass a complete-coverage budget gate or prove that local/hosted service is equivalent. | #39 retains new meter, aggregation/rounding, commitments and selected-workload quantity decisions; no new unit or pricebook is adopted here. |
| #41 Data Sources | **Accepted:** the dated-source and failure/drift treatment and withdrawal of the unaccepted TTL. Source-checked facts remain unverified in v1; historical pins persist; price or condition changes trigger evidence review without an automatic saved-build rewrite. | #41/#60 retain source-use rights and conflict policy; this audit grants no extra retrieval, display or redistribution right. |

The #58 informational input is the same conclusion: cost-only recommendations require evidence beyond these partial examples. It does not establish willingness to pay, customer demand or an MVP decision.

## 7. Validation record

Historical checks for #112 were recorded on `feat/mr-07-price-freshness` from `f297ac5`. The 2026-10-18 follow-up was checked on main `df2e2712070b72a68de2eab0629c2bf12fbbe4bf` plus this focused diff, with Python 3.12.14 and pinned research requirements:

```text
python -m unittest discover -s contracts/v1/tests -v  # 21 passed
python -m unittest discover -s tests -v               # 88 passed
python scripts/validate_research.py                  # 74 proposals, 3 pricebooks
python scripts/validate_market_research.py           # 33 entities, 1584 cells, 20 issues
python prompts/mobile/validate_prompts.py            # passed
git diff --check                                    # passed
```

A separate Decimal recomputation read the thirteen unchanged Pricebook rates and the stated A1–A8 assumptions. All 37 checked scenario amounts and the expected hosting-share percentage agreed: S1 subtotals, S2 item lines, one-off/recurring/first-period sums and local power sums. It rounded each monetary line half-up to cents before summing, as stated in section 2. The rate-source review in section 1 is distinct from this arithmetic check. Neither test suite nor the calculator establishes runtime performance, source rights, account availability or actual bills; no new provider job was run.

The subsequent reconciliation with [#197](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/197) preserves its 101-pair dated audit and records only the three actual post-snapshot integration decisions. The source and arithmetic review above remains pinned to `c08484c`; [#199's checks](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/199/checks) record validation of the final integrated head. The local results above describe the reviewed source tree.

## Result
The desk audit is complete for its stated 13-rate inventory and two conditional scenarios. Its finding is that neither scenario is a complete quote and neither proves service equivalence. The independent integration review accepts that bounded result and the three proposed receiving scopes above. The reviewed merge and final CI publish this partial audit; #64 remains open until the separate consuming-owner handoffs are accepted; incomplete quote coverage is the documented result, not an omitted research step. No raw customer data, benchmark artifact or paid API output was collected. Consumers: #9, #39, #41; informational input for #58.
