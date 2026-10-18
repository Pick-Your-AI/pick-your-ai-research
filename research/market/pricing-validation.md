# MR-07: Validate price freshness and total-cost scenarios

Issue: [#64](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/64). Assignees (live, 2026-10-17): @PUSHINGSQUARES, @appletechie. Status: first desk recheck and scenario draft; not reviewed, not accepted. Readiness: Ready.

## Question
Can local and hosted configurations be compared with complete cost units?

## Starting evidence
[monetization.md](monetization.md) (structure only, no rates); Pricebook proposals on `main` at `f297ac5`: [`t1-api-2026-10-16.json`](../../pricing/proposals/t1-api-2026-10-16.json) (8 rates) and [`t2-hosting-2026-10-16.json`](../../pricing/proposals/t2-hosting-2026-10-16.json) (5 rates); dated GPU notes in [training-compute.md](../T5-training-fine-tuning/training-compute.md) (checked 2026-10-16). This note is not a new canonical component catalog, a Pricebook or a completed measurement. It copies no rate into a new record: every amount below cites its Pricebook rate ID or note row.

## Protocol and acceptance
- [ ] Pin provider region date and billing units
- [ ] Include idle capacity storage egress and utilization
- [ ] Recheck live rates before recommendations
- [ ] Report ranges and invalidation triggers
- [ ] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain affected-owner review and accepted handoff.

Boxes stay unticked until review; progress is in the [criterion map](#6-criterion-map-against-the-live-64-checklist).

## 1. Freshness recheck (2026-10-17)

Method: unauthenticated HTTPS GET of each `provenance.source_uri` on 2026-10-17 (robots.txt checked first; all paths allowed), HTML reduced to text and the rate row read. No account, API key or paid call. Evidence class for every row: primary documentation (vendor-published list price). Confidence: high that the page states the value today; this is not an invoice, entitlement or quota check, so Pricebook `verification_status: unverified` stays correct.

| Rate ID | Catalog item @ version | Meter | Pricebook | Observed 2026-10-17 | Region / scope | Result |
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

**Totals: 13 match, 0 drift, 0 unverified (unfetchable).** Sources: [OpenAI GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4), [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), [HF Inference Endpoints pricing](https://huggingface.co/docs/inference-endpoints/pricing), [RunPod network volumes](https://docs.runpod.io/storage/network-volumes), [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/).

Conditions observed today that the Pricebook already excludes but a quote must not ignore: OpenAI regional-processing endpoints +10%; Anthropic `inference_geo: "us"` 1.1x; Anthropic 5-minute (USD 2.50) and 1-hour (USD 4) cache writes; RunPod standard volume USD 0.05/GB/month beyond 1 TB; R2 rounds up to the next billing unit; HF scale-up replicas bill at the same per-replica rate.

Note-only rates used in scenarios (not Pricebook rates, so a CostEstimate line has no `price_rate_id` for them):

| Note row | Source | 2026-10-16 note | Observed 2026-10-17 | Result |
| --- | --- | --- | --- | --- |
| RunPod RTX 4090, Secure / Community, per GPU-hour | [runpod.io/pricing](https://www.runpod.io/pricing) (page "Updated October 8, 2026") | USD 0.89 / 0.34 | USD 0.89 / 0.34 | Match; region not stated |
| US average electricity price, July 2026 (cents/kWh) | [EIA Electric Power Monthly Table 5.6.A](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a), released 2026-09-24 | — | Residential 18.31, commercial 14.53, Hawaii residential 48.00 | New; preliminary statistical average, **not a tariff** |

## 2. Total-cost scenarios (30-day horizon, USD, list prices, pre-tax)

Labelled assumptions (A) are hypotheses, not measurements. Arithmetic uses decimal multiplication rounded half-up to cents per line. Low/expected/high are assumption bands, not a confidence interval. No currency conversion.

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
- A8 R2 operations within the free allowance for low/expected; high 3M Class A and 30M Class B.
- Serving: S1 HF L4 band (A3), or S1 local power band (A4).

| Line | Rate | Low | Expected | High |
| --- | --- | --- | --- | --- |
| Training GPU | RunPod 4090 note row | 0.92 | 2.41 | 3.07 |
| Working volume | `runpod-standard-small-us-ks-2` | 3.50 | 7.00 | 14.00 |
| Artifact storage after 10 GB free | `r2-standard-storage` | 0.00 | 0.15 | 0.60 |
| R2 Class A / B after free allowance | `r2-standard-class-a/b-request` | 0.00 (A8) | 0.00 (A8) | 9.00 + 7.20 |
| Serving | `hf-aws-l4-replica-hour` | 128.00 | 288.00 | 576.00 |
| **Hosted subtotal** | | **132.42** | **297.56** | **609.87** |
| Local alternative: training + serving power | A4 × EIA | 0.12 + 6.97 = **7.09** | 0.22 + 59.32 = **59.54** | 0.99 + 207.36 = **208.35** |

Serving dominates the hosted subtotal (97% at expected), consistent with the T5 finding that hosting after training outweighs training. The local alternative is again a power-only lower bound. Training excludes setup, data loading, evaluation, retries and minimum increments (T5 caveat).

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
- the Pricebook revision or catalog version referenced here changes, or 30 days pass since 2026-10-17 (suggested staleness bound for #41; not an accepted policy).

## 5. Drift routing

No drift found, so no revision is requested from the T1 (@zwright8) or T2 (@Mattycodes69) Pricebook owners; this note does not edit either file. Optional notes for them: RunPod's rate is not data-center specific (the ID implies US-KS-2); the excluded conditions in section 1 are live on today's pages.

## 6. Criterion map against the live #64 checklist

| Live criterion | Artifact / evidence | Status | Remaining gap / reviewer |
| --- | --- | --- | --- |
| Pin provider region date and billing units | Section 1 table | Met for 13 rates; HF region and RunPod data center unbound by source | Evidence reviewer |
| Include idle capacity storage egress and utilization | S1/S2 bands, section 3 | Partially met: idle, storage, utilization shown; egress explicitly uncovered | #39 owner meter decision |
| Recheck live rates before recommendations | Section 1 (2026-10-17) | Met for this revision; no recommendation made | Repeat at decision time |
| Report ranges and invalidation triggers | Sections 2 and 4 | Met (assumption bands) | Evidence reviewer |
| Every significant conclusion linked to evidence or hypothesis | Rate IDs, sources, A1–A8 | Met in draft | Evidence reviewer |
| Technical owners review handoffs; unresolved decisions named | Sections 3 and 5 | Not met: no owner has reviewed | #9, #39, #41 owners; T1/T2 owners |
| Repository checks pass; reviewer accepts evidence | Section 7 | Checks recorded; acceptance not obtained | Program coordinator |

Issue-specific gate: no unknown egress, idle cost or utilization is treated as zero; both scenarios are partial.

## 7. Validation record

Commands (Python 3.12, revision on `feat/mr-07-price-freshness` from `f297ac5`): `python scripts/validate_market_research.py`, `python scripts/validate_research.py`, `python -m unittest discover -s tests`, `git diff --check`. These check repository structure and integrity, not price truth, rights or owner acceptance.

## Result
Partial. Desk freshness recheck complete for all 13 Pricebook rates (13 match). Two scenarios with ranges are drafted; neither is complete. No raw customer data, benchmark artifact or paid API output was collected. Consumers: #9, #39, #41; informational gate for #58.
