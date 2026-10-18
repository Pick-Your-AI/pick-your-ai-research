# Deployment SLA source check

Refs #37 and #38. Access date: 2026-10-18. This supporting note addresses the unread/current-SLA question in the [#121 deployment draft](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/38a83764f4819fde6900dcb8b7219b7cec2315ef/research/T6-deployment-operations/deployment.md#open-questions). It does not approve a deployment or establish measured availability.

## Amazon Bedrock: page read

[The publisher's SLA](https://aws.amazon.com/bedrock/sla/) was opened successfully. It still identifies October 4, 2023 as its update date; do not invent a newer effective date or declare the page invalid solely because of its age. Grade: Primary documentation, source checked; all figures below are published contractual definitions, not measurements.

The page describes a per-region monthly commitment and conditional service-credit schedule: below 99.9% but at least 99.0% gives 10%; below 99.0% but at least 95.0% gives 25%; below 95.0% gives 100%. Monthly uptime averages five-minute availability intervals. Its error definition is HTTP 500; intervals without requests count as fully available. Exclusions and claim requirements apply, including request logs with sensitive information removed. The page is evidence of these definitions, not proof of a particular account's eligibility or actual uptime.

Research consequence: retain the exact measurement definition when comparing a workload objective with this SLA. End-to-end application latency, every client-visible error class and every dependency are not established by that figure. #38 must distinguish workload observability from a provider's service-credit computation. No new uptime threshold is proposed here.

## Microsoft: edition located, document unread

The old [Azure Cognitive Services SLA locator](https://azure.microsoft.com/en-us/support/legal/sla/cognitive-services/v1_1/) redirects to the [Microsoft Online Services SLA catalog](https://www.microsoft.com/licensing/docs/view/Service-Level-Agreements-SLA-for-Online-Services?lang=1). The catalog was opened and identifies an English October 2026 edition, dated October 1, 2026.

The [linked DOCX](https://www.microsoft.com/licensing/docs/documents/download/OnlineSvcsConsolidatedSLA%28WW%29%28English%29%28October_2026%29%28CR%29.docx) could not be read: the web reader reported unsupported `application/octet-stream`; a direct download attempt from the execution environment failed at its network tunnel with HTTP 403. No bytes were obtained, so no hash, terms text, Azure OpenAI/Foundry coverage or numeric commitment is asserted. This is a concrete retrieval limitation, not evidence that Microsoft publishes no SLA.

Remaining action for #37: obtain the exact document through an authorized readable route, inspect the selected service/tier's scope and exclusions, and retain edition/source evidence. Do not substitute the catalog title, a historical document or a marketing availability statement for the unread terms. No credentials, paid access or access-control workaround was attempted.

## Acceptance boundary

The Bedrock source-read question is resolved narrowly; applying it to a selected build remains scoped review. Microsoft's numeric/source-scope question remains unknown for the stated retrieval reason. This note does not settle the separate NIM licence conflict, legal role questions or rollout-owner decisions. It preserves the #121 owner review and focused-draft sequencing.
