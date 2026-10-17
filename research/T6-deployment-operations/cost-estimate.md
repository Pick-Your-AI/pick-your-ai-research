# T6: Cost Estimate

Issue: #39 · Contract: 1.0.0 · Kinds: `cost_policy` (with `Pricebook` and `CostEstimate` semantics)
Status: **Partial draft — unit normalisation and open decisions** · Last researched: 2026-10-17

This draft covers only the unit-normalisation part of #39 and the decisions it depends on. Every normalisation rule below is a **PROPOSAL for decision by the #39 assignees (@PUSHINGSQUARES, @appletechie)**. Nothing here is an adopted policy, a cost-model implementation or a complete quote. No Pricebook, CatalogItem or schema file is changed. No price is added; every rate cited already exists in a merged Pricebook or upstream note, or was read from the primary source listed under [Evidence](#evidence).

## User decision

What will this build cost, under stated assumptions, and with what uncertainty? This draft answers the first research question only: which pricing units must be normalised, and how. Worked scenarios, aggregation across active components and capacity-versus-usage comparison remain for the full deliverable (see [Remaining work](#remaining-work-for-the-full-39-deliverable)).

## Inputs read

| Input | Revision / state | What it contributes |
| --- | --- | --- |
| [`pricing/proposals/t1-api-2026-10-16.json`](../../pricing/proposals/t1-api-2026-10-16.json) | `main`, revision 1 | 8 token rates (GPT-5.4, Claude Sonnet 5.5) |
| [`pricing/proposals/t2-hosting-2026-10-16.json`](../../pricing/proposals/t2-hosting-2026-10-16.json) | `main`, revision 1 | 5 rates: HF L4 replica-hour, Runpod and R2 storage, R2 Class A/B requests |
| [T1 model-provider](../T1-model-selection/model-provider.md), [context-window](../T1-model-selection/context-window.md), [handoffs](../T1-model-selection/handoffs.md) | `main` | Long-context predicates, cache read/write, regional uplift, default-view proposal; rows #5/#6/#7 → #39 pending |
| [T2 hosting](../T2-infrastructure/hosting.md), [gpu-compute](../T2-infrastructure/gpu-compute.md), [contract-proposals](../T2-infrastructure/contract-proposals.md), [handoffs](../T2-infrastructure/handoffs.md); [#39 handoff comment](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6216109139) | `main` | Note-only meters (GiB, egress, CPU/RAM-seconds, tiers, allowances, rounding); rows #9/#10 → #39 pending |
| [T5 training-compute](../T5-training-fine-tuning/training-compute.md) | `main` | Training meters proposal, epochs/validation tokens, job minimum, post-training hosting |
| [Market pricing validation](../market/pricing-validation.md), [monetization](../market/monetization.md) | `main` | #64 protocol (idle, egress, ranges, invalidation); monetization records no prices |
| [`PRICING_AND_GATES.md`](../../contracts/v1/docs/PRICING_AND_GATES.md), [pricebook](../../contracts/v1/schemas/pricebook.schema.json), [cost-estimate](../../contracts/v1/schemas/cost-estimate.schema.json), [common](../../contracts/v1/schemas/common.schema.json) schemas, `spec_cost_policy` | v1 1.0.0 | Meter enum, decimal money, coverage semantics |
| `prompts/T6.md` on [PR #74](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/74) | Merged guidance | Track E scope; not an acceptance source |

## 1. Meter and unit inventory

v1 meters (Pricebook and CostEstimate share the enum): `input_tokens_1m`, `output_tokens_1m`, `cached_input_tokens_1m`, `embedding_tokens_1m`, `request`, `gpu_hour`, `cpu_hour`, `storage_gb_month`, `vector_gb_month`, `agent_run`, `seat_month`, `license_month`, `one_time`.

"In Pricebook" means a merged rate already uses the meter. "Note only" means the unit appears in a research note without a rate record. A **published** value is the vendor's figure. A **calculated** value is this project's exact arithmetic from a published figure.

| # | Source unit as published | Where seen | Example (published, USD, source) | Maps to v1 meter | Normalisation needed |
| --- | --- | --- | --- | --- | --- |
| U1 | USD per 1M input tokens | T1 Pricebook; T2 H01; T1 CW08 | GPT-5.4 2.50; Sonnet 5.5 2.00 (O1, A3) | `input_tokens_1m` (in Pricebook) | None. "MTok" means one million tokens (N7) |
| U2 | USD per 1M output tokens (Gemini states output includes thinking, CW08) | T1 Pricebook; CW02/CW04 | GPT-5.4 15.00; Sonnet 5.5 10.00 | `output_tokens_1m` (in Pricebook) | Do not count a reported reasoning subset again (T1) |
| U3 | USD per 1M cache-hit / cache-read input tokens | T1 Pricebook | GPT-5.4 0.25; Sonnet 5.5 0.10 | `cached_input_tokens_1m` (in Pricebook) | Hit tokens are not also billed at `input_tokens_1m` |
| U4 | USD per 1M cache-write tokens, by lifetime (5 min, 1 h) | T1 notes (uncovered); N7 | Sonnet 5.5: 2.50 (5 min), 4.00 (1 h) (N7) | **no v1 meter** | Distinct from `input_tokens_1m` and from cache reads. Lifetime is part of the meter |
| U5 | Prompt-length tier: whole-session multiplier above a threshold | T1 Pricebook (`.long` rates); CW01, CW08 | GPT-5.4 >272,000 input: input 5.00, output 22.50 (calculated from O1) | Same token meters, separate rate IDs | Predicate selects the rate for the **whole session**, not marginal tokens (O1) |
| U6 | Regional / residency multiplier | O1 (10%); N7 (1.1× `inference_geo: "us"`); H07 (1.15×/1.75×); T5 P2 (1.5×) | — | **no v1 multiplier field**; would be a separate pre-multiplied rate with `region` | Anthropic states multipliers stack with batch and residency (N7) |
| U7 | USD per 1k training tokens | T5 P3, P4, P5 | Vertex Gemini 2.5 Flash-Lite 0.0015; Bedrock Nova Lite 0.002 | **no v1 meter** (T5 proposes `training_tokens_1k`) | ×1000 to per-1M: 1.5 and 2 (calculated) |
| U8 | USD per 1M training tokens; billed tokens = dataset tokens × epochs (+ validation tokens × evaluations at Together) | T5 P1–P6 | Together Llama 3.1 8B LoRA SFT 0.34 | **no v1 meter** (T5 proposes `training_tokens_1m`) | Quantity formula is provider-specific; see R6 |
| U9 | Job minimum charge | T5 P1 | Together 4.00 per job | **no v1 meter** (T5 proposes `job_minimum`) | `max(job_total, minimum)`, not additive |
| U10 | USD per GPU-hour, one device | T5 P2, P10, P11 | Fireworks H100 8.00; Lambda A100 SXM 2.79 | `gpu_hour` | None if the source is per device |
| U11 | USD per replica-hour, one GPU per replica, minute billing | T2 Pricebook (`hf-aws-l4-replica-hour`) | HF AWS L4 0.80 (H02) | `gpu_hour` (in Pricebook) | Quantity = replicas × devices per replica × hours; HF example formula multiplies replica count (N4) |
| U12 | USD per multi-GPU instance-hour | T5 P7, P8, P9, P12 | AWS p5.48xlarge (8× H100) 55.04 | `gpu_hour` only if per-device semantics are adopted | 55.04 / 8 = 6.88 per device-hour (calculated); instance remains indivisible. Owner decision D6 |
| U13 | USD per GPU-second; per CPU core-second; per GiB-second of RAM | T2 H07 (note only) | Modal H100 0.001097/s; CPU 0.0000131/core-s; RAM 0.00000222/GiB-s | GPU → `gpu_hour`; CPU → `cpu_hour` (core vs vCPU unresolved); RAM → **no v1 meter** | ×3600: 3.9492/GPU-h, 0.04716/core-h (calculated) |
| U14 | USD per hour while a fine-tuned model is deployed (no exposed device) | T5 P5 | Azure OpenAI gpt-4.1-mini 1.70/h | **no v1 meter** (not a GPU or CPU hour) | Bills while deployed regardless of traffic (P5) |
| U15 | USD per model-unit-hour, provisioned throughput, by commitment term | T5 P4 | Bedrock: no-commit 24.00, 1-month 21.18, 6-month 13.08 | **no v1 meter** | Commitment term is part of the rate |
| U16 | USD per decimal GB-month, flat | T2 Pricebook (R2) | R2 Standard 0.015 (H28) | `storage_gb_month` (in Pricebook) | Month = 30-day period, average of daily peaks; usage rounded up to next whole billing unit (N2) |
| U17 | USD per GB-month with a capacity tier | T2 Pricebook (Runpod, below 1 TB only); H21 | Runpod network volume: 0.07 below 1 TB, 0.05 above (N6) | `storage_gb_month` (in Pricebook, one tier) | Marginal vs whole-volume tier meaning unresolved; vendor GB byte definition unknown |
| U18 | USD per vendor "GB"-month where the vendor defines GB = 1024³ bytes | T2 H26 (note only) | AWS EBS gp3 example 0.08 (N5) | `storage_gb_month` only after GiB→GB conversion | The vendor's "GB" is a GiB (N5). Calculated 0.0745058059692… per decimal GB |
| U19 | USD per GiB-month after an included allowance | T2 H07/H23 (note only) | Modal Volumes 0.09/GiB-month after 1 TiB | `storage_gb_month` only after conversion | Calculated 0.0838190317153930664… per decimal GB: exceeds 12 decimal places (see R2) |
| U20 | USD per GB-month, per model (not per byte) | T5 P4 | Bedrock custom-model storage 1.95/model-month | **no v1 meter** (`storage_gb_month` would mislabel it); T5 proposes `model_storage_month` | Quantity is models × months |
| U21 | Storage billed by the hour / second with minimum | N5, N6 | EBS gp3: per second, 60-second minimum (N5); Runpod: container/volume disks per second, network volumes hourly (N6) | `storage_gb_month` quantity is GB × fraction of month | Billing increment and minimum change the quantity |
| U22 | USD per million requests, by class, with allowance and rounding | T2 Pricebook (R2 A/B) | R2 Class A 4.50/M, Class B 0.36/M (H28) | `request` (in Pricebook, exact per-request conversion) | Classes are not interchangeable; allowance once per scope; round up to next million (N2) |
| U23 | Provisioned IOPS-month, throughput MB/s-month | N5 (note only) | gp3: 3,000 IOPS and 125 MB/s included (N5) | **no v1 meter** | Uncovered line |
| U24 | Network egress per GiB above an allowance | T2 H29 (note only) | Modal 0.04/GiB above 1/10/100 TiB by plan (N3) | **no v1 meter** | Calculated 0.0372529029846191406… per decimal GB if ever converted |
| U25 | Egress stated as free / no fee | H19, H28 | Runpod Pods, R2 Internet egress | No meter needed **for that service only** | Does not make transfer from other services free (T2) |
| U26 | Commitment / prepaid plans | H19 (Runpod 3/6 months), T5 P4/P9, H05 | — | `one_time` for an upfront payment; `price_type: contract`; no term field | Term, refundability and coverage scope are not representable |
| U27 | Hardware purchase | H33 | NVIDIA DGX Spark US storefront 6,950.00 | `one_time` | Electricity, support, shipping, tax unknown (T2) |
| U28 | Tool / API calls per call or per 1k calls | T1 (uncovered); T4 #26 pending | — | `request` | Per-1k → per-request is exact division |
| U29 | Embedding tokens, vector storage, agent runs, seats, licenses | No merged rate yet (#14, #15, #25, #26) | — | `embedding_tokens_1m`, `vector_gb_month`, `agent_run`, `seat_month`, `license_month` | Not yet exercised by evidence |
| U30 | Taxes | All sources exclude tax or are silent (T5 P10, T2) | — | CostEstimate `tax` (required money) | See gap G4 |

Summary: 30 unit forms. **8** are already in merged Pricebooks (U1–U3, U5, U11, U16, U17, U22), using 6 distinct meters. **10** map to an existing meter, some only after a conversion or owner decision (U10, U12, U13 GPU/CPU, U18, U19, U21, U25, U27, U28, U29). **10** have no v1 meter at all (U4, U6, U7, U8, U9, U14, U15, U20, U23, U24); U13 RAM and the U26 commitment term are partial gaps, and U30 is a field gap. Under `PRICING_AND_GATES.md` these must appear as uncovered lines, not be hidden.

## 2. Proposed normalisation rules

All rules are **PROPOSALS** for owner decision. Arithmetic uses base-10 decimals (`PRICING_AND_GATES.md`; `common.schema.json#/$defs/decimal`, at most 12 fractional digits).

| ID | PROPOSAL | Rationale and evidence |
| --- | --- | --- |
| R1 | **Tokens.** Canonical unit is per 1,000,000 tokens. Convert per-1k rates by ×1000 (exact). Token classes are distinct meters: uncached input, cache read, cache write (per lifetime), output including reasoning. A token belongs to exactly one class. | v1 meters are per-1M. Anthropic defines MTok as one million and prices cache writes separately by lifetime (N7). T1 warns not to add a reported reasoning subset to an output total again (context-window, CW02/CW04). |
| R2 | **Bytes.** Canonical GB is decimal 10⁹ bytes (already the #40 owner position recorded in T2, PR #75 review). Convert GiB = 2³⁰ bytes: price per GB = price per GiB × 0.931322574615478515625. Treat a vendor "GB" defined as 1024³ bytes as GiB. When the vendor does not define GB, keep the vendor label and mark the byte basis unknown. Two options for the owner: **(a)** emit a converted `storage_gb_month` rate only if the conversion terminates within 12 decimals, otherwise keep note-only; **(b)** round the converted unit price half-even to 12 decimals and record the source unit, source rate and conversion in `conditions`. Draft favours (a) because it adds no rounding error to a source rate. | NIST defines 1 GB = 10⁹ B and 1 GiB = 2³⁰ B (N1). AWS states "GB = 1024^3 bytes" on its EBS pricing page (N5). Modal publishes GiB (N3). Modal's converted rate needs 23 decimals (calculated), so (b) is lossy. |
| R3 | **Period.** A CostEstimate period is `period_days` (default 30, required for `cost.monthly_total_amount`). Hourly rate × 24 × `period_days`. A vendor "month" is converted with the vendor's definition: 30-day period (R2, AWS EBS example) prorates by `period_days / 30`. Where the vendor shows a 730-hour month (HF example), show that vendor convention separately from the selected period: a 30-day estimate uses 720 h, while 730 h is a different period, not an uncertainty bound. | R2 bills GB-month over a 30-day period (N2). AWS's gp3 example divides by an 86,400 s × 30-day month (N5). HF's example uses 730 h (N4). T2: "No universal 730-hour month". |
| R4 | **Billing granularity before pricing.** Round the **quantity** up to the vendor's billing increment and minimum, per billing scope, before multiplying: R2 next whole GB-month / million operations (N2); HF per minute (N4); EBS per second, 60 s minimum (N5); Runpod network volume hourly (N6). Unknown or disputed increments: low = exact quantity, high = coarsest documented increment. | Vendors round usage, not money, in every source checked. Runpod's page states network volumes bill hourly while disks bill per second (N6); T2 records the sub-hour invoice rounding as unresolved. |
| R5 | **Allowances and tiers.** Subtract a free allowance once per vendor billing scope (account/workspace), clamped at zero. When other usage in the same scope is unknown, low assumes the full allowance and high assumes none. Tier predicates follow the source: whole-session (GPT-5.4 >272K, O1), prompt-length whole-request (Gemini Pro, CW08), capacity tier (Runpod, meaning unresolved). An estimate that straddles a threshold shows both tiers and budget checks use the higher one (T1 CTX-04, accepted by the #40 owner). | R2 applies 10 GB-month / 1M A / 10M B monthly allowances (N2, H28). Modal egress allowance is per workspace billing cycle (N3). |
| R6 | **Training quantity.** Billed training tokens = Σ over epochs of training-set tokens + validation-set tokens × evaluation count where the provider bills them, plus provider-specific adjustments (Fireworks multi-turn reasoning traces). Job cost = max(sum of lines, job minimum), shown as an explicit "minimum top-up" line. Post-training hosting (U14/U15/U20) is a separate recurring line, displayed next to the one-off training line, never amortised into it. | T5 lines 50 and 230–259 (P1–P5). T5's Azure example shows one month of hosting near 8× the training cost (P5), so hiding it misleads. |
| R7 | **Devices.** `gpu_hour` = one accelerator device for one hour. Quantity = replicas × devices per replica × hours (including initialising/idle billable time). Multi-GPU instance rates are divided by the published device count to give a per-device rate only when the division is exact within 12 decimals, with an integral instance count; GPU-hours = integer instances × devices per instance × billable hours. One eight-GPU instance for 0.5 billable hours consumes 4 GPU-hours. Otherwise keep the instance rate note-only. | HF's cost formula multiplies hourly rate by replicas and hours (N4) and bills initialising time (H02). 55.04 / 8 = 6.88 (exact); p4de 27.45 / 8 = 3.43125 (exact). |
| R8 | **Multipliers.** v1 has no multiplier field. A regional, residency, batch or commitment modifier becomes a separate rate with its own `id`, `region` and `conditions`, pre-multiplied exactly and labelled "calculated from publisher's stated multiplier" (as T1 already does). Stacking follows the source (Anthropic: multipliers stack, N7). Never average geographic prices. | Keeps each rate tied to its source; matches T1's existing `.long` rates. |
| R9 | **Currency.** Never convert currency without a pinned, dated exchange-rate source approved through #40/#41. Lines in different currencies are not summed; the estimate shows per-currency subtotals and `coverage=partial`. All evidence collected so far is USD. | `PRICING_AND_GATES.md` forbids summing currencies without a pinned policy. |
| R10 | **Rounding of money.** Keep `unit_price` and line `amount` exact up to 12 decimals (`amount = quantity × unit_price`). If a product exceeds 12 decimals, round half-even at 12 and record it. Round only for display, to the currency's minor unit: low bound down, high bound up, expected half-even, so a displayed range never understates its own bounds. | v1 requires a documented rounding rule and decimal strings. Directional display rounding is a project choice; no vendor source governs it. |
| R11 | **Region.** A rate without a stated region (HF L4, R2, Runpod public list) stays region-less and is labelled "region not bound by source". It is not applied to a user's region as a regional quote. The user's region is an explicit input; absent it, region-dependent lines are unknown. | T1's default-view proposal and T2's Pricebook conditions; owner decision D7. |

## 3. Owner decisions already routed to #39 (open questions)

None of these is decided here. "Routed by" links the record that asked.

| ID | Open decision | Routed by | Draft position offered for discussion |
| --- | --- | --- | --- |
| D1 | GB vs GiB conversion of vendor rates; vendor month convention | T2 #9→#39, [#39 comment](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/39#issuecomment-6216109139), hosting.md L194 | R2 option (a), R3 |
| D2 | Storage tiers (marginal vs whole-volume), allowances and their scope | T2 #9→#39, T2-C01 | R5; Runpod tier meaning stays unknown until sourced |
| D3 | Million-request rounding and allowance scope | T2 comment | R4/R5 |
| D4 | Runpod sub-hour network-volume rounding | T2 hosting.md L193 | R4 bounds (exact vs hourly) |
| D5 | Egress, IOPS, throughput, idle/startup time | T2 comment, T2-C01; #64 protocol | Uncovered lines (§4) until #40 adds meters |
| D6 | `gpu_hour` per GPU vs per instance; replica semantics | T5 training-compute L301; T2 #10→#39 | R7 |
| D7 | Regional default view | T1 model-provider L51, handoffs L33; #41/CD-9 and #81 D-R6 | R11: explicit region or unknown |
| D8 | Cache-write and other unsupported API costs (tools, batch/flex/priority) | T1 handoffs L33 | R1; uncovered until a meter exists |
| D9 | Prompt-threshold predicate, full-session multiplier, straddle display | T1 #7→#39, context-window L132 | R5 (CTX-04 already accepted by #40 owner) |
| D10 | Commitments, reservations, savings plans | T2 comment, T2-C01 | Show as a separate scenario with term and total obligation; never amortise into the on-demand default without owner approval |
| D11 | Default currency (`cost_policy.default_currency`) | #39 body "Open questions" | USD is the only observed currency; R9 forbids conversion |
| D12 | Cost snapshot stored with a saved build | #39 research question; #42 consumer | Store CostEstimate `id`, `pricebook_id` + Pricebook `revision` and `captured_at`, `build_revision`; show prices as of their dates; re-evaluate when a pricebook, snapshot or ruleset revision is published, a rights decision changes, or the build is edited; no elapsed-time expiry (see G5) |
| D13 | Training meters `training_tokens_1m/1k`, `training_hour`, `job_minimum`, `model_storage_month`; post-training hosting | T5 #31/#33→#39 and #40 | R6; meter names are #40's to version |
| D14 | Accept/narrow/reject pending handoff rows #5/#6/#7/#9/#10/#31/#33→#39 | T1 and T2 handoff ledgers | Owner action; this draft does not acknowledge them |

## 4. Uncertainty display (PROPOSAL)

- Each line shows **low / expected / high**, all labelled as scenario bounds, not statistical confidence intervals (consistent with T2-C02). Sources of spread: workload quantities (#2), tier straddle (R5), billing increment (R4), allowance availability (R5); month conventions are separate period scenarios (R3).
- Each line carries its evidence label (published / calculated / estimate), `price_type`, rate `checked_at` and region/currency.
- **Uncovered lines are listed explicitly** with the reason ("no v1 meter: egress", "rate unknown", "region not bound") and **never shown as 0**. The total then reads "at least *low* – *high*, plus N uncovered items", and `coverage` is `partial` or `unknown`. A budget gate cannot pass (`PRICING_AND_GATES.md`).
- When `confidence=low`, show the range only, without a single headline point.
- One-off (training, hardware, prepaid commitments) and recurring per-period costs are separate totals and are not blended.
- Display rounding per R10.

## 5. Mapping to CostEstimate fields and gaps for #40

| Need | v1 field | Gap (proposed to #40, not patched) |
| --- | --- | --- |
| Line price, quantity, amount | `line_items[].quantity/unit_price/amount` | — |
| Source rate | `line_items[].price_rate_id`, single `pricebook_id` | **G1**: an estimate spanning T1 + T2 Pricebooks needs several Pricebook IDs, or a merged Pricebook |
| low / expected / high | none | **G2**: no interval fields per line or total |
| Uncovered meter for a partly priced selection | `unpriced_selection_ids` (per selection), `warnings` (free text) | **G3**: no structured per-meter uncovered list or reason |
| Tax unknown | `tax` required money | **G4**: "0" would be fabricated; needs tax status or optional tax |
| Snapshot freshness | `pricebook_id`, `estimated_at`, `build_revision` | **G5**: no Pricebook `revision` reference |
| Source unit / conversion | `assumptions[]` (free text) | **G6**: no structured source unit, factor or rounding record |
| One-off vs recurring | `period_days` only | **G7**: no line-level recurrence |
| Region default | `cost_policy` has `default_currency`, `supports_hard_cap`, `alert_threshold_pct` | **G8**: no default region/view field |
| Missing meters | meter enum | **G9**: U4, U7–U9, U13 RAM, U14, U15, U20, U23, U24, U26 term (T2-C01 and T5 proposals overlap) |
| Multipliers | none | **G10**: no modifier/stacking representation (R8 works around it) |

## Evidence

Accessed 2026-10-17 by direct fetch of the public page (robots.txt checked; no account or paid API). Grade: PD = primary documentation.

| ID | Publisher and URL | Access date | Version / region | Grade | Claim used |
| --- | --- | --- | --- | --- | --- |
| N1 | NIST, [Prefixes for binary multiples](https://physics.nist.gov/cuu/Units/binary.html) | 2026-10-17 | Current page | PD | 1 GiB = 2³⁰ B; 1 GB = 10⁹ B |
| N2 | Cloudflare, [R2 pricing](https://developers.cloudflare.com/r2/pricing/) | 2026-10-17 | dateModified 2026-10-01; USD | PD | Round up to next billing unit; GB-month = average daily peak over 30 days; free tier |
| N3 | Modal, [Network egress billing](https://modal.com/docs/guide/network-egress-billing) | 2026-10-17 | Current; USD | PD | 0.04 per GiB above 1/10/100 TiB per billing cycle |
| N4 | Hugging Face, [Inference Endpoints pricing](https://huggingface.co/docs/inference-endpoints/pricing) | 2026-10-17 | Unversioned; USD | PD | Shown hourly, calculated by minute; cost formula multiplies replicas; examples use 730 h/month. Its CPU example shows 0.067/hr hourly but 0.064/hr in the monthly line, an inconsistency in the source |
| N5 | AWS, [Amazon EBS pricing](https://aws.amazon.com/ebs/pricing/) | 2026-10-17 | Current; example region unspecified | PD | "GB = 1024^3 bytes"; gp3 per-second, 60-second minimum; 30-day month in example |
| N6 | Runpod, [Pod pricing](https://docs.runpod.io/pods/pricing) | 2026-10-17 | Current; USD | PD | Network volume 0.07 (<1 TB) / 0.05 (>1 TB) per GB-month; disks per second, network volumes hourly; savings plans 3/6 months, compute only |
| N7 | Anthropic, [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) | 2026-10-17 | Current; USD | PD | MTok = million tokens; Sonnet 5.5 cache writes 2.50 (5 min) / 4 (1 h); multipliers stack; `inference_geo: "us"` 1.1× |

Upstream IDs (O1, A3, CW01–CW08, H01–H33, P1–P13) keep their original sources and 2026-10-16 access dates in the T1, T2 and T5 notes. All conversions above are exact calculations by this project; none is a measurement or vendor quote.

## Compatibility proposals

None. Pricing coverage outcomes (`coverage`, budget gate) are already defined by `PRICING_AND_GATES.md`. Any cost-related rule in #40's shared format waits for the full deliverable.

## Structured artifacts

None proposed. The units marked "no v1 meter" cannot be expressed as Pricebook rates, and no `cost_policy` CatalogItem is proposed until D11 is decided.

## Remaining work for the full #39 deliverable

Not done here:

- Worked scenarios stating mode per serving component under merged #81 (provider-shared api, provider-dedicated/reserved managed, user-operated self_hosted; hybrid is derived) with provenance, using #2 workload inputs.
- Aggregation method across active components, and capacity-based versus usage-based comparison. Self-hosted cost per token stays unknown until #10 has measured throughput.
- Freshness and provenance display using #41's policy.
- Comparison fields defined with type, unit and evidence requirement (from the issue's minimum list).
- Owner decisions D1–D14, handoff acknowledgements and #40 versioning of G1–G10.
- Cost rules in #40's shared format, with verified rules separated from hypotheses.
- Coordination with #64 (MR-07) so its validation protocol and this method agree.

## Open questions and handoffs

| Question | Follow-up owner |
| --- | --- |
| D1–D14 above | #39 @PUSHINGSQUARES, @appletechie |
| G1–G10 contract gaps and new meters | #40 @tynamite, with #39 |
| Exchange-rate and freshness policy | #41 @tynamite / @PUSHINGSQUARES |
| Saved-build cost snapshot | #42 (@tynamite and @appletechie), with #39 |
| Runpod tier meaning and GB byte definition; S3 GB definition (not checked here) | #9 @Mattycodes69 |
| Price freshness and total-cost validation | #64 @PUSHINGSQUARES |
