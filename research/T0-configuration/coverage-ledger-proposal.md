# Stage 0 coverage and entity boundaries — proposal

Issue: [#509](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509) · Status: proposed, awaiting affected-owner review

## User decision and scope

Which AI resources should the reference corpus describe, at what identity and evidence depth, without confusing research breadth with a validated product or published catalog?

This is a bounded Stage 0 proposal. Its [routing ledger](coverage-ledger-proposal.json) indexes the G01–G18 gaps in #509; it is not an entity inventory, a new contract, a source-use grant or an acceptance receipt. Repository evidence was inspected at `da3d320e239a6d37a933963230f2eb3643d1d5c4`; GitHub issue bodies, comments and relationships were read on 2026-10-25. Existing source access dates remain attached to their original claims. No vendor facts were rechecked here.

**Scope decision:** #47's **NARROW** product-validation decision governs, as recorded in [#47's synthesis](../market/synthesis.md) and [actual decision receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/47#issuecomment-6254035935). The broad, near-exhaustive #509 reference corpus is outside Stage 0 unless affected owners later agree. @appletechie recorded this reconciliation from their side; other affected-owner decisions remain open. Nothing here broadens #47's experiment or establishes demand for a directory.

## Candidate options and recommendation

| Option | Consequence |
| --- | --- |
| Treat the builder registry as the entire reference universe | Leaves applications, papers and other reference entities without faithful identities |
| Add every reference entity to frozen builder v1 | Conflates products, artifacts, evidence and selections; requires unapproved contract changes |
| **Proposed: reference identities with explicit builder projections** | Keep research discovery broad; map only eligible component facts into the existing kinds, through existing review gates |

Start with explicit, bounded cohorts rather than a target for “all AI.” A cohort declaration must name its audience/use, entity unit, source universe and exclusions, task/modality, language/geography and observation cutoff. “Unspecified” is not worldwide or multilingual coverage. Candidate discovery can include name-only or unpinned records; those remain unresolved candidates until identity evidence supports a merge or split. Restricted material stays outside public Git; a permitted pointer is not permission to copy its contents.

## Proposed identity and inclusion rules

These are research distinctions, not new v1 kinds. References between entities need the source record/revision and a qualified relation; shared branding alone does not prove identity.

| Reference entity | Include / identity unit | Exclude from that unit / relation to retain |
| --- | --- | --- |
| Model family, release, artifact | Distinguish a family grouping, exact released model, and checkpoint/file revision with format/quantization where known | Aliases and family names are unresolved until pinned; quantized artifacts do not automatically become new families. Retain `member_of`, `artifact_of`, `alias_of` only with evidence |
| Provider and hosted offering | Separate publisher, distributor/operator and exact service route, model revision, plan, region and effective conditions | A provider name is not an offering or a global price. Retain `offers`, `serves`, `operated_by` |
| Hardware, provisioned resource, runtime | Distinguish physical SKU, allocatable profile/topology and exact engine/backend/driver version | Memory size or vendor support alone does not establish executable fit. A cloud instance is not a physical accelerator |
| Dataset and benchmark definition | Dataset identity plus revision, configuration/split and intended use; separately identify benchmark task/protocol/harness | Training and evaluation roles may overlap without duplicate dataset identities. A dataset or benchmark definition is not an executed run |
| Measurement run and result | Exact inputs, model/artifact, task/split, harness, runtime/hardware, conditions, metric and uncertainty | Published/vendor score is not project reproduction. Compare only eligible matched protocols; retain run-to-result links |
| Application and software-delivered service | End-user product identity with release/channel, plan/platform/region when claims vary | The product is not its underlying model or integration. T4 exposure is a separate interface linked to the same product where evidenced |
| Framework, tool, MCP server, integration, memory | Package/runtime identity and version, operation/interface, transport, auth and state semantics as applicable | Listing or shared package name is not a safe/authorized deployment or durable-memory proof |
| Paper, method, person, organization | Scholarly work and revision; link method, author/lab and exact supporting artifacts separately | DOI/preprint versions require evidenced relationships; citations are not independent validation, and full text is not automatically redistributable |
| Use case, governance claim, guide | Scoped task/audience; dated jurisdiction/control/incident claim; or authored guide revision with evidence links | Suitability is not legal approval; organizational sustainability is not hardware energy measurement; tutorials are not measurements |

Retirements, corrections and uncertain aliases should preserve provenance and superseded identities where permitted. Count each deduplicated identity once within its declared unit, with many-to-many task and domain tags. Do not sum overlapping cohorts or count sources, tags, variants and runnable releases as interchangeable entities.

## Crosswalk to all frozen v1 kinds

The [canonical mapping](../../docs/CONTRACT_MAPPING.md), [registry](../../contracts/v1/schemas/component-registry.json) and [component guide](../../contracts/v1/docs/COMPONENTS.md) control actual payload semantics. The following is a routing boundary, not evidence that a reference record satisfies required fields. Price facts belong in Pricebooks; quality runs and resource estimates use their separate artifact contracts. Existing selectors/policies are not additional encyclopedia products.

| Canonical kind(s) | Existing issue(s) | Boundary for reference projection |
| --- | --- | --- |
| `workload`, `deployment_mode` | #2, #3 | Scoped user task/requirements and serving-mode decision; not an industry label or commercial product |
| `model_provider`, `model`, `context_policy` | #5, #6, #7 | Provider role and supported model facts; exact offering/artifact evidence stays explicit. Family names and unsupported nontext limits stay in notes |
| `hosting_platform`, `storage` | #9 | Infrastructure host and storage offerings; not knowledge semantics or arbitrary cloud-service branding |
| `accelerator`, `compute_profile` | #10 | Physical capability versus provisionable allocation/topology; neither is a measured fit result |
| `inference_engine` | #11 | Versioned execution runtime; a framework/product's name alone is insufficient |
| `data_source`, `knowledge_base` | #13 | User knowledge input and its organized retrieval collection; `data_source` is not a catalog citation/source register |
| `embedding_model` | #14 | Embedding component under its own requirements; a model's retrieval tag alone is insufficient |
| `vector_database`, `rag_pipeline` | #15, #16 | Retrieval storage and configured retrieval path; not dataset identities or benchmark results |
| `agent_framework`, `tool`, `integration` | #25, #26 | Orchestration runtime, callable operation and connection semantics; separate from end-user application identity |
| `mcp_server`, `memory_store` | #27, #28 | Server packaging/transport and agent memory semantics; not proof of authorization or durable behavior |
| `training_framework`, `training_compute` | #30, #31 | Training software and resource allocation; serving support does not establish training support |
| `training_dataset`, `fine_tuned_model` | #32, #33 | Eligible training input and derived model/lineage; dataset directory discovery is not training permission |
| `guardrail`, `evaluation_suite` | #35, #36 | Configured controls and evaluation definitions; not blanket compliance or an executed quality result |
| `deployment_target`, `monitoring_stack`, `cost_policy` | #37, #38, #39 | Deployment/observability configuration and cost method; not an operating service, a price rate or measured energy fact |

There is no direct frozen kind for a general application, paper, author/lab, guide, model family grouping, generic dataset directory entry, benchmark result or source-rights decision. Link these research identities to eligible components instead of coercing them. Any needed wire representation or migration remains a separately reviewed #40 proposal.

## Evidence depth and independent gates

Use [#41's accepted evidence policy](catalog-data-sources.md#evidence-grades-and-labels) and [research method](../../docs/RESEARCH_METHOD.md) unchanged. The following proposed depth labels are navigation aids, applied to individual claims, not replacements for evidence grades or v1 provenance enums:

| Proposed depth | Required support |
| --- | --- |
| Candidate | Discovery pointer; identity or claim may remain unresolved |
| Source-checked | Exact claim checked against a cited source/revision with access date and conditions |
| Reviewed comparison | Traceable scoped comparison with an actual review receipt at a recorded revision |
| Independently supported | Eligible independent corroboration or reproducible measurement for that claim; identify which and retain protocol/limitations |

Primary documentation, Vendor claim, Independent measurement and Estimate remain distinct evidence classes. A reviewed vendor performance claim stays a vendor claim. An estimate does not become a measurement. New checked-but-not-independently-supported v1 provenance remains `unverified`; preserve historical labels and inspect their evidence rather than bulk-relabeling them.

Record separate axes: identity resolution; claim evidence class/depth; source-check date and freshness applicability; rights by source/material/field/intended use; review receipt; publication eligibility for an exact projection; and actual release/consumer delivery. No aggregate score should hide a failed or unknown gate. Follow #41's version-pinned versus current-state distinction; invent neither a blanket TTL nor a current date for older evidence. The [publication handoff](../../docs/PUBLICATION_ELIGIBILITY_HANDOFF.md) is a dated, immutable scope assessment, not a dynamic approval service.

## Proposed gap routing ledger

Classifications describe the scoped work below, not issue status or owner agreement: **existing complete** means a cited bounded baseline is already accepted; **existing partial** means evidence exists but the proposed breadth/qualification is unfinished; **net new** means a distinct corpus beyond existing component notes (even when setup exists); **production handoff** means a consumer/operating outcome separate from research acceptance. Each G row has one primary class; its dependencies can belong to another class. All owner references mean live Assignees of the linked canonical issues, not new assignments.

**Existing complete baseline, reused:** [#40 acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6257213742) covers the bounded shared-contract research; [#41 acceptance](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6256107246) covers the bounded source-policy research. [T0's summary](README.md) retains their successor and implementation limits. Do not reopen those outcomes to create the broader ledger or infer universal publication clearance.

| Gap | Primary class | Existing evidence / canonical route | Proposed next bounded decision |
| --- | --- | --- | --- |
| G01 Scope, ontology, quality | Existing partial | This proposal; #40/#41; [#47 synthesis](../market/synthesis.md) | Agree entity units, cohort boundary and distinct reference/product purposes |
| G02 Model identity crosswalk | Existing partial | [T1 taxonomy](../T1-model-selection/model-taxonomy.md), [inventory](../T1-model-selection/model-research-inventory.json); #5–#7 | Crosswalk selected rows to family/release/artifact/offer without filling unknown fields; inventory validation is a separate active contribution |
| G03 Field/use publication decisions | Existing partial | [Publication handoff](../../docs/PUBLICATION_ELIGIBILITY_HANDOFF.md), #41/#60; website #15 | Review one exact field-level projection and each intended use; retain exclusions |
| G04 Ingestion/publication operations | Production handoff | [Pipeline program](https://github.com/Pick-Your-AI/pick-your-ai-catalog-pipeline/issues/1); #41; website #15 | Accept a permitted source, custody and exact release/withdrawal/consumer pilot |
| G05 Qualified measurement/comparison | Existing partial | [Sizing validation](../market/sizing-validation.md), [benchmark validation](../market/benchmark-validation.md); #61/#62/#36 | Resolve missing protocol/measurement inputs within existing experimental scope |
| G06 Device/runtime breadth | Existing partial | [GPU research](../T2-infrastructure/gpu-compute.md), [engine research](../T2-infrastructure/inference-engine.md); #10/#11 | Select one missing device/runtime cohort; MI300X already has note-only evidence |
| G07 Competitive feature unknowns | Existing partial | [Competitors](../market/competitors.json), [feature matrix](../market/feature-matrix.md); #48–#50 | Source-check a bounded material-alternative cohort; silence remains Unknown |
| G08 Customer/demand validation | Existing partial | [Customer validation](../market/customer-validation.md), #52/#63/#47 | Obtain applicable participant/protocol authorization and distinguish directory from builder hypotheses |
| G09 Reference website discovery | Production handoff | [Website #24](https://github.com/Pick-Your-AI/pick-your-ai-website/issues/24), #15 | Agree reference-page fields, eligible projection and receiving checks with website owners |
| G10 Routes, terms and pricing | Existing partial | [Provider](../T1-model-selection/model-provider.md), [hosting](../T2-infrastructure/hosting.md), [cost](../T6-deployment-operations/cost-estimate.md); #5/#7/#9/#39 | Pin route/region/plan/interval and keep rates separate from cost policies |
| G11 Dataset/benchmark directory | Net new, deferred/outside Stage 0 | [Datasets program](https://github.com/Pick-Your-AI/pick-your-ai-datasets/issues/1); [training dataset](../T5-training-fine-tuning/training-dataset.md), #32/#36 | No Stage 0 action; revisit only with affected-owner agreement. Directory metadata is not benchmark execution or data redistribution |
| G12 Applications directory | Net new, deferred/outside Stage 0 | [Applications program](https://github.com/Pick-Your-AI/pick-your-ai-applications/issues/1); #26 and existing market records | No Stage 0 action; revisit only with affected-owner agreement before any crosswalk |
| G13 Scholarly graph | Net new, deferred/outside Stage 0 | [Papers program](https://github.com/Pick-Your-AI/pick-your-ai-papers/issues/1); existing topic citations | No Stage 0 action; revisit only with affected-owner agreement before any scope decision |
| G14 Agent/interoperability breadth | Existing partial | [T4 summary](../T4-agents-integrations/README.md), #25–#28 | Select one versioned transport/auth/operation cohort; listing grants no trust |
| G15 Domain/language/geography | Existing partial | [Workload](workload-use-case.md), [model taxonomy](../T1-model-selection/model-taxonomy.md); #2/#6 | Declare one task/language/geography cohort with suitability evidence |
| G16 Governance/incident index | Existing partial | [Guardrails](../T6-deployment-operations/guardrails.md), [monitoring](../T6-deployment-operations/monitoring.md), #32/#35/#38/#41 | Define dated jurisdiction/control/incident claims without compliance endorsement |
| G17 Lifecycle cost and energy | Existing partial | [Cost](../T6-deployment-operations/cost-estimate.md), [compute](../T2-infrastructure/gpu-compute.md); #10/#39 | Choose a conditioned scenario; separate measured energy, sourced rates and estimates |
| G18 Guides and explanations | Production handoff | Website #24; [workload evidence](workload-use-case.md) | Select an evidence-linked guide and editorial/consumer acceptance criteria |

G11–G13 are listed only to identify broad-corpus gaps: they are deferred and outside Stage 0, and the ledger does not route work to those tracks. The machine-readable ledger preserves these stable gap IDs and links; its empty `measurements` object means **not measured**, not zero. It deliberately carries no owners' names, deadlines, counts, quality scores or approval fields. It is not loaded by the catalog intake validator.

## Observed external relationships

The [#509 native sub-issues endpoint](https://api.github.com/repos/Pick-Your-AI/pick-your-ai-research/issues/509/sub_issues) returned the pipeline, datasets, applications and papers programs linked above on 2026-10-25. The [applications parent endpoint](https://api.github.com/repos/Pick-Your-AI/pick-your-ai-applications/issues/1/parent) also returned #509. These are observed existing relationships, not suggested new issues. They supersede the relationship/setup state in the older [applications continuation comment](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509#issuecomment-6361224000) for this narrow observation; the historical attempt remains historical.

Their issue bodies describe planned or incomplete research/operating outcomes. Existence and parentage do not establish corpus completion, Project reconciliation, settings enforcement, owner acceptance, releases or a working service. No further repository split is proposed here. [Website #15](https://github.com/Pick-Your-AI/pick-your-ai-website/issues/15) still records separate publication and integration gates; [#24](https://github.com/Pick-Your-AI/pick-your-ai-website/issues/24) records existing adapter/label work, so “production handoff” must not be read as an assertion that all website work is absent.

## Measurement proposal and open decisions

Before computing coverage, agree a denominator from a revision-pinned cohort manifest and deduplication rules. Report candidate rows, resolved entities, sourced/reviewed claims, independently measured claims, eligible projections and delivered entities with their different units and cutoff. Claim counts cannot be divided by entity counts; published entities do not imply every field is eligible. `unknown`/not measured differs from a measured zero. Exclusions and overlapping domain membership must accompany every report. Do not present a global “AI coverage percentage.”

Proposed future per-cohort fields: identity rule and required fields; source universe; inclusion/exclusion; task/modality/use/language/geography; unresolved identities and known unknowns; claim source/revision/date/conditions; evidence class/depth; freshness applicability; source/use decision; exact review/release/consumer receipts; metric unit and denominator manifest. Live owner/reviewer assignments remain on canonical issues, with actual dated decisions linked when given.

Open decisions for existing issue owners: #509/#47/website receiving scope and any later expansion beyond Stage 0; #40 identity/projection semantics; #41/#60 claim-level rights/freshness; each domain's bounded cohort and review depth; and external program/website receiving scope. Candidate Stage 1 pilots require affected-owner agreement under the NARROW scope before selection; the example model/provider route and hardware/runtime or agent/tool cohort are not selected, scheduled, executed or accepted by this document. Preserve #61/#62 experiment boundaries and #63's participant authorization requirements.

Validation checks repository integrity and ledger syntax/link/kind consistency only. It does not establish source truth, freshness, independent measurements, publication eligibility, owner agreement or completion of #509. This contribution should use `Refs #509`.
