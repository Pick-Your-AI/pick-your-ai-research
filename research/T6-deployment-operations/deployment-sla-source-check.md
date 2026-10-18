# Deployment SLA source check

Refs #37 and #38. Access date: 2026-10-18. This supporting note addresses the unread/current-SLA question in the [merged #121 deployment record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/38a83764f4819fde6900dcb8b7219b7cec2315ef/research/T6-deployment-operations/deployment.md#open-questions). It does not approve a deployment or establish measured availability.

## Amazon Bedrock: page read

[The publisher's SLA](https://aws.amazon.com/bedrock/sla/) was opened successfully. It still identifies October 4, 2023 as its update date; do not invent a newer effective date or declare the page invalid solely because of its age. Grade: Primary documentation, source checked; all figures below are published contractual definitions, not measurements.

The page describes a per-region monthly commitment and conditional service-credit schedule: below 99.9% but at least 99.0% gives 10%; below 99.0% but at least 95.0% gives 25%; below 95.0% gives 100%. Monthly uptime averages five-minute availability intervals. Its error definition is HTTP 500; intervals without requests count as fully available. Exclusions and claim requirements apply, including request logs with sensitive information removed. The page is evidence of these definitions, not proof of a particular account's eligibility or actual uptime.

Research consequence: retain the exact measurement definition when comparing a workload objective with this SLA. End-to-end application latency, every client-visible error class and every dependency are not established by that figure. #38 must distinguish workload observability from a provider's service-credit computation. No new uptime threshold is proposed here.

## Microsoft: October 2026 document read

The old [Azure Cognitive Services SLA locator](https://azure.microsoft.com/en-us/support/legal/sla/cognitive-services/v1_1/) redirects to the [Microsoft Online Services SLA catalog](https://www.microsoft.com/licensing/docs/view/Service-Level-Agreements-SLA-for-Online-Services?lang=1). The catalog was opened and identifies an English October 2026 edition, dated October 1, 2026.

The initial reader/download failures were environmental limitations. A subsequent authorized public download on 2026-10-18 retrieved the [linked DOCX](https://www.microsoft.com/licensing/docs/documents/download/OnlineSvcsConsolidatedSLA%28WW%29%28English%29%28October_2026%29%28CR%29.docx): 380,353 bytes, SHA-256 `77e3e636513b0b3be8ada4d976d91d4543dd12564c418f2f0ead8fa5b7166f41`. The title page dates it October 1, 2026. Text, tables and equations were read from its Word XML; [the manifest](../../evidence/microsoft-online-services-sla-2026-10.json) identifies the exact source without redistributing the document. Grade: Primary documentation, source checked; confidence is high for the transcription, not account eligibility.

A complete local render was also inspected for the Introduction, General Terms and Foundry Models section, including its continuing latency table, on rendered pages 6–8 and 87–88. The source table of contents retains different pagination; section names and the artifact hash are the stable locators. The source DOCX, extracted text and render remain outside this repository.

| Selected section | Published definition and boundary |
| --- | --- |
| Foundry Models: uptime | Uptime is 100% minus the average of per-minute error rates; a minute without requests has zero error rate. The credit table gives 10% below 99.9% uptime and 25% below 99%. Credits apply only to Foundry Models Sold by Azure; Developer tier is excluded |
| Foundry Models: priority latency | Provisioned Managed Deployment and Priority Processing use a model-specific token-speed target from product documentation. Generation speed excludes the first token; model documentation chooses five-minute P50 or one-minute mean. Attainment below 99% gives 10% credit. Intervals with error requests, oversized requests or responses generating fewer than one token are excluded from the latency calculation; Developer tier is excluded |
| General definitions | Error Code includes failed operations such as HTTP 5xx, unlike Bedrock's HTTP-500-only definition. Applicable Period depends on billing: metered PAYG uses the 30 days through the incident's first day; other services use the calendar month. General exclusions and claim approval still apply |
| General limits | Previews and free tiers are excluded. Unsupported configurations, quota excess and other General Terms limitations apply. Azure claims require supporting incident details within 60 days of the incident. Subscription term and renewal determine the applicable edition; current publication alone does not |

These are distinct measures, not a common end-to-end application SLO. No per-model latency target or selected offering's eligibility is inferred. #37/#38 still need the actual service/tier/model, product-specific target, measurement window and exclusions before applying these terms. Other Microsoft services and separate Azure OpenAI terms are not assumed equivalent to this selected Foundry Models section. No credentials or paid access were used.

## Acceptance boundary

The Bedrock page and Microsoft's selected Foundry Models section are now source checked. Applying either to a build remains scoped review; no measured availability or latency is supplied. This note does not settle the separate NIM licence conflict, legal role questions or rollout-owner decisions. #121 has merged; its receiving decisions and this supplement's owner acceptance remain distinct from that merge.
