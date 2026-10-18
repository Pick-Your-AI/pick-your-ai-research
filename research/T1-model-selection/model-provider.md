# T1 Model Provider

Issue: #5 · Contract: 1.0.0 · Kind: `model_provider`
Status: draft for owner review · Last researched: 2026-10-16

## User decision

Choose the organization/source and a particular model delivery offering under explicit access, location, privacy, quota and price conditions. Provider identity is not an offering: the same publisher's model on its API and on Bedrock has different IDs, control planes and contractual conditions. GPU hosting products remain with #9.

## Candidate options

The original table below is a dated API/weights comparison. The2026-10-17 [broader inventory](model-taxonomy.md) extends provider/source discovery to perception, retrieval, speech/music, editable image/video, spatial, predictive/scientific and action-model routes. Each [candidate row](model-research-inventory.json) cites the [primary register](model-research-sources.md) and preserves publisher versus host/reseller/UI distinctions. Exact API IDs, downloadable artifacts and services must not be collapsed merely because a reseller offers a similarly named model.

New API/service licence or account terms not inspected remain explicitly pending in those rows; weight/code/backbone/adapter/data/voice rights are separate. No unknown rate or permission becomes zero/free/allowed. New meters such as characters, images, pixels, generated seconds, credits and scientific job units require #39 definitions and dated Pricebook intake; the existing token-rate Pricebook is not a complete price comparison for these task families. The research adds no fabricated new rates or contracts.

Evidence IDs resolve in [the claim register](evidence.md). This bounded set covers first-party API, a cloud-managed marketplace/inference route, and open-weight distribution. It is representative rather than a recommendation that every provider fits every workload.

| Offering / mode | Publisher / serving party / distributor | Canonical model key -> route ID | Terms, limits and evidence |
| --- | --- | --- | --- |
| OpenAI direct / API | OpenAI / OpenAI / none | `gpt-5.4-2026-03-05` -> same snapshot ID | O1/O2: account-tier quotas; training opt-in distinction; endpoint-specific storage. Standard USD pricing below. No local weights supplied in this route. |
| Claude direct / API | Anthropic / Anthropic / none | `claude-sonnet-5-5` -> same fixed release ID | A1-A5: quota tier, feature/model-specific retention arrangements and route prices; do not inherit another cloud's region or SLA. |
| Claude on Bedrock on-demand / API | Anthropic / AWS / AWS marketplace route | same publisher release -> `anthropic.claude-sonnet-5-5` | A1/B1-B4: provider-operated shared capacity is API under #3's current owner position. Preserve endpoint/region/profile, quotas, logging and agreement; account entitlement, regional price and fine-tuning availability unknown. |
| Hugging Face dedicated Inference Endpoint / managed | Selected model publisher / Hugging Face / Hub | Selected Hub artifact/revision plus endpoint engine/configuration | H1/H2: provider-operated dedicated instance route. Candidate is conditional on exact artifact/runtime support; no Qwen deployment, account entitlement, regional quota, retention duration or price is asserted. |
| Gemini API / API | Google / Google / none | `gemini-2.5-flash` -> same provider ID | G1/G2: existing-active-user restriction; paid/unpaid and geographic data-use differences. This legacy candidate exposes access and context semantics, not current new-project availability. |
| Qwen checkpoint / self-hosted | Qwen / operator's chosen runtime / Hugging Face Hub | `Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218` -> repository/revision | Q1-Q4: public Apache-2.0 weights; distribution is not an inference service or hosted SLA. Hosting, network and operational prices are not zero because weights can be obtained. |
| Hybrid composition | Per component, e.g. Qwen local + remote API | Keep each selected offering's identity separately | Research proposal: hybrid describes a build composition, not a fictitious universal provider. Confirm interpretation with #3. |

Apply #3's [current owner position](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927): self-operated runtime is self-hosted; provider-operated shared capacity is API; provider-operated dedicated/reserved capacity is managed; different serving-component modes compose a hybrid build. Cloud branding, billing or an API endpoint alone does not determine the mode. The position informs this research; its proposed new fields are not silently added to v1.

## Comparison fields

Every research field requires source URL/access date/version and applicable conditions. Rows marked note-only do not introduce arbitrary fields into frozen v1.

| Field / mapping | Type and unit | Evidence requirement / unknown behavior |
| --- | --- | --- |
| Provider ID / CatalogItem `id` | Stable string | Publisher or serving organization's identity; do not equate a host with model author. |
| Offering type | Enum API/managed/weights; note-only | Route-specific documentation. Hybrid is composed per component. |
| Canonical model key and provider model ID | Two strings + revision; v1 `provided_by` binding plus proposed endpoint key | Exact publisher and route IDs, explicit mapping confidence; ambiguous version stays unmapped. Rich endpoint/region/tier metadata remains a #40 proposal. |
| `spec.api_base_url` | URI, optional | Actual endpoint documentation; omit if not checked. Distribution URL is not an API endpoint. |
| `spec.supported_regions` / serving and residency regions | String array; role-qualified notes | Model/endpoint/plan-specific region evidence. Unknown is not unrestricted; a country of API access is not a processing-region guarantee. |
| Rates | Decimal currency per typed meter in Pricebook | Capture date, route, billing region, currency, conditions, exact item version. Unpriced operations remain uncovered. |
| Rate limits / quota | Integer requests/minute and tokens/minute plus account tier; note-only | Per-account/provider evidence; unknown numeric entitlement until account checked. |
| Retention | Duration plus purpose, feature, exception, agreement; note-only | O2/A4/B2/G2; separate abuse monitoring, application state, logging and third parties. |
| Training use / residency | Conditional policy and source; note-only | Account opt-ins, paid/unpaid mode, country and endpoint; never reduce a conditional arrangement to universal false. |
| SLA | Agreement URI/version, metric, exclusions and eligibility; note-only | B4 provides candidate agreement. Purchased eligibility for any offering remains unknown. |
| `spec.supports_fine_tuning` on provider and model | Optional boolean | Existing v1 capability: explicit false on either fails a selected fine-tuning action; missing is unknown. Provider true does not override model false or prove account/region/license eligibility. O1 says this GPT-5.4 model is unsupported; other candidates remain route-specific unknowns here. |
| Source / checked date | Public URI / UTC timestamp | Public field-level provenance; #41 determines freshness/reuse policy. |

## Pricing and capacity

Published standard first-party rates, USD per million tokens, accessed 2026-10-16: OpenAI GPT-5.4 input **2.50**, eligible cached input **0.25**, output **15.00** (O1); Claude Sonnet 5.5 input **2.00**, eligible cache read **0.10**, output **10.00** (A3). These are standard published API rates without a regional processing uplift, not country-specific contractual quotes.

For GPT-5.4 prompts over 272K input, the published multipliers yield input **5.00** and output **22.50** USD/Mtoken (project calculation from O1, not a measurement). Cache multipliers for that route require separate confirmation before claiming full cost coverage. Claude's cache-write lifetimes, tool charges, batch/priority routes and geographic processing modifiers are separate conditions, not discounts to apply universally. Bedrock/Gemini rates and self-hosting compute remain unpriced in this submission.

Default-view proposal: show the user's chosen currency and serving/billing region with its dated source; require an explicit region choice or show unknown when absent. Never average geographic prices or invent an exchange rate. #39 must accept price aggregation and applicability; #41 must accept refresh policy.

## Compatibility proposals

See [offering and access rules](rules/model-offering.md). Facts checked against docs and proposed builder behavior are distinguished there. Missing account/region/terms evidence yields unknown, not a compatible offering.

The [#40 owner's PR #88 review at `dbfa7dd`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/88#pullrequestreview-5554964868), accessed 2026-10-17, accepts T1-O1 on existing `provided_by` links and narrows T1-O2 into two concerns. Technical fine-tuning capability uses existing model/provider flags. License/terms conditions become answerable `license_conditions` / `licence_answers` under #81 D-R2a/b, subject to #30 interpretation and #40 versioning; a user answer can resolve its condition without overriding unsupported capability. No proposed field is added to v1.

The actual API agreement references and conditional customization/output restrictions are recorded in [the model license section](ai-model.md#license-and-access-conditions-for-30), with O3/A6/G2/Q3 primary terms. They are source facts for #30 to review, not a universal right to train from service outputs. H2 additionally distinguishes published endpoint payload handling from30-day log retention; it is not a claim about a customer's negotiated agreement.

## Recommendation and rationale

Keep model publisher, serving provider and distributor distinct. Normalize exact route IDs while preserving raw vendor IDs. Record privacy/retention and fine-tuning eligibility at offering/model/feature/account scope. API, managed and local offerings need different evidence, although they can share a publisher model identity.

## Structured artifacts

`catalog/proposals/t1-provider-*.json` holds the sourced identity captures; optional fields not checked are omitted. Provider `version=2026-10-16` versions this research capture, not a claim of a vendor release. `billing_class=unknown` avoids treating an organization as a free inference service. Model rates reference the exact model item versions in `pricing/proposals/t1-api-2026-10-16.json`.

v1 has no first-class offering entity or conditional terms/quota/region schema. This information stays in notes; proposed extensions need #40 review. No generated schema was changed.

## Open questions and handoffs

See [handoffs](handoffs.md) for every consumer, owner, exact request and disposition. #6/#7 are integrated by this T1 author, with independent evidence review still pending. #30 must confirm license-field sufficiency and ambiguous condition interpretation; #37 needs route/control-plane/region constraints; #39 needs meter conditions and uncovered costs. Those consumer rows remain pending. Regional default-view choice belongs to #39/#3; #41 accepted the applied interim evidence policy at `dbfa7dd`; remaining contract details and migration stay with #40.
