# Hosting and infrastructure storage

Issue: [#9](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9) · Contract: 1.0.0 · Kinds: `hosting_platform`, `storage`
Status: merged in PR #75; follow-up proposals and remaining handoffs pending · Last researched: 2026-10-17
Decision owners: @Mattycodes69 and @appletechie, live #9 assignees checked on 2026-10-17.

## User decision

Choose where each active component runs, who operates its runtime, and which location, artifact, network, persistence, capacity, and billing constraints apply. The taxonomy below was **accepted with constraints by #3** in the [PR #75 owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927), reviewed head `9e66622a4b2698a9305274f05da9c15ae5d90b8c`, accessed 2026-10-17. These owner positions are not an approved contract change. A provider exposing an HTTP API is insufficient to determine operational responsibility.

The canonical v1 schema on `main` is the submission contract. The conceptual categories below are comparison vocabulary, not additional `hosting_type` enum values. #5 retains the model/provider catalog, #10 accelerator specifications and compute profiles, #37 deployment procedures, #13 knowledge/ACL semantics, #15 vector database evaluation, #28 memory semantics, and #31 training estimates. These boundaries follow [the dependency map](../../docs/DEPENDENCIES.md) and [contract mapping](../../docs/CONTRACT_MAPPING.md).

## Candidate options

### Hosting taxonomy and deployment-mode mapping (owner-reviewed proposal)

| Category | Proposed mode | Canonical mapping | Boundary example and responsibility |
| --- | --- | --- | --- |
| Managed model inference API | API | `hosting_type=managed_api`; model/provider records owned by #5 | Amazon Bedrock on-demand model invocation: consumer chooses an available model/API rather than operating a GPU runtime. The priced illustration below is not a model recommendation. [H01] |
| Dedicated model endpoint | managed | `managed_api` for the scoped endpoint service | Hugging Face Inference Endpoints: user chooses artifacts and capacity, provider operates the service; dedicated billing does not make it self-hosted. [H02][H03][H04] |
| Cloud GPU VM or dedicated container | self-hosted runtime on rented infrastructure | `cloud` | AWS EC2 or Runpod Pods: consumer controls the software environment. A container managed by a cloud vendor is still different from vendor-operated model inference. [H05][H06] |
| Serverless GPU application | managed | `cloud` | Modal Functions or Runpod Serverless: user supplies application/container, provider starts workers and scales them. Being invoked through an API does not turn this into a provider model catalog. [H07][H08] |
| Owned on-premises workstation/server | self-hosted | `on_prem`; `edge` or `colocation` only when the actual installation warrants it | NVIDIA DGX Spark is a desktop-system example. Buying hardware supplies neither an operated inference endpoint nor a cloud capacity entitlement. [H09][H10] |
| Managed vector database service | managed on dedicated capacity; API on shared capacity | host may be `managed_api`; product is `vector_database` in #15 | Qdrant Managed Cloud operates clusters; provider-operated Hybrid Cloud on customer infrastructure remains managed. Scope the actual capacity/operator; database semantics and product ranking remain #15. [H11]; PR #75 owner review |
| Self-hosted vector database | self-hosted component | `cloud`, `on_prem`, `edge`, or `colocation` according to installation | Qdrant's local Docker example illustrates a customer-operated service plus persistent storage. A storage volume is not itself a vector database. [H12] |
| Local MCP process | self-hosted/local component | actual host location; no mandatory GPU | MCP stdio launches a subprocess in the client environment. #27 owns server/transport selection. [H13] |
| Remote MCP HTTP service | managed or self-hosted according to operator | actual service/host; no invented `mcp_host` kind | MCP Streamable HTTP uses an independent process and HTTP endpoint. A public URL alone does not establish trust, private networking, or persistent process support. #27/#35 own those requirements. [H13] |

Mode is evaluated per serving component: operator=self means self-hosted; provider-operated dedicated instances or reserved throughput means managed; provider-operated shared capacity means API. Mixed serving modes form a hybrid build, whose local checks still run. `hosting_type` and billing do not decide mode: cloud can host either EC2 self-hosting or Modal managed workers. Models, embedding models, vector databases and full fine-tuned models are serving components; adapters inherit the base model's deployment. MCP, tools, storage and monitoring retain operator/location classifications for isolation/residency without setting the build mode. These are accepted #3 owner positions for #81/#40's proposed versioned deployment object, not fields silently added to v1.

### Candidate comparison

Prices below are **published list examples in USD**, accessed **2026-10-16**, unless explicitly labeled project estimates. A visible SKU or price is not proof of stock, account entitlement, regional availability, or achieved performance. `unknown` means not verified in this research; it never means zero price, unlimited quota, or unsupported.

| Candidate / category | Region and offered GPU scope | Artifacts / networking | Price and commitment example | Availability / quota / omitted costs |
| --- | --- | --- | --- | --- |
| Amazon Bedrock / managed API | Example table covers `us-east-1`, `us-east-2`, `us-west-2`; underlying GPUs unknown and not selected by this note | Model/API surface; supported model/artifact behavior goes to #5 | MiniMax M2.5 on-demand table: **$0.30 / 1M input tokens**, **$1.20 / 1M output tokens** in those regions. [H01] | Model lifecycle, account access, request quota, private connectivity, storage and transfer conditions require #5/#37 confirmation; no model Pricebook emitted here |
| Hugging Face Inference Endpoints, AWS scope / dedicated managed endpoint | FAQ lists AWS `us-east-1`, `eu-west-1`; pricing lists L4, T4, A10G, L40S, A100 and other GPU options, without a complete GPU × region entitlement matrix. [H02][H03] | Hub model artifacts; custom public/private containers. AWS PrivateLink supports an intra-region private path. [H04][H14] | **$0.80 / hour**, one AWS L4 replica; hourly display, minute billing; initializing/running resources bill. No region-specific rate is stated in the table. [H02] | Unselectable instances require quota request; scaled-to-zero endpoints still consume quota. Storage/egress itemization unknown. Do not treat the regional subset as global coverage. [H02] |
| AWS EC2 G6e / cloud GPU VM | G6e uses NVIDIA L40S; launch documents N. Virginia, Ohio, Oregon. `aws-ec2` proposal includes researched `us-east-1` only, not an exhaustive EC2 list. [H05] | Deep Learning AMIs/containers; VPC private network support. [H05][H15] | On-demand, Reserved, Spot, Savings Plans are documented options; exact current G6e USD compute rate is **unknown** here and not fabricated. [H05] | Default G/VT on-demand vCPU quota is **0**, adjustable; actual account quota and free capacity unknown. Storage, transfer, public IPv4, NAT and other services need separate cost lines. [H16][H15][H17] |
| Runpod Pods / dedicated cloud container | Public list includes L40S and H100 SXM, among other choices; exact regional inventory unknown. [H18] | Docker registry images/templates; TCP/HTTP; no UDP, Windows or Docker Compose support. [H06] | Illustrative public list: **L40S $1.09/hour**, **H100 SXM $3.99/hour**; page does not bind displayed toggle state/region, so these are notes, not provisionable rate proposals. [H18] | On-demand has no commitment; savings plans prepay **3 or 6 months**, compute only. Docs say no ingress/egress fee. Current GPU availability and quota unknown; account spend limit is not stock. [H19] |
| Runpod Serverless / managed worker application | Public list includes H100 and a shared L40/L40S/6000 Ada/MIG class; the class does not promise a particular physical GPU or datacenter. [H18] | Custom Docker workers; queue handler and HTTP load-balancing are distinct application interfaces. [H08] | Published H100 class **$4.79/hour** display; per-second running-worker billing, startup and idle waiting can bill. Flex scales to zero; active-worker discounts require sales. [H18][H20] | Region-specific stock, account concurrency and exact class hardware unknown; persistent volumes constrain placement. Price is not token cost or steady-state latency. [H20][H21] |
| Modal Functions / managed serverless application | Documented container choices include broad `us`, `eu`, `ap` and narrow regions; container location and traffic routing are separate. [H22] | Python/container application; Volumes file storage. Exact network-isolation support not certified by this note. [H07][H23] | H100 SXM5 **$0.001097/second** base, plus CPU **$0.0000131/core-second** and RAM **$0.00000222/GiB-second**. Region selection adds broad **1.15×** or narrow **1.75×**. [H07][H22] | Published Starter limit **10 GPU concurrency**; account entitlement/capacity unknown. Load and post-input container idle time bill. Credits and plan charges are not included in example totals. [H07] |
| NVIDIA DGX Spark / on-premises | US storefront price example; delivery/site region and stock unknown; device specifications delegated to #10 | NVIDIA documents local operation, Docker runtime and NGC integration. Site/network/storage configuration is a #37 concern. [H09] | Current NVIDIA US storefront displays **$6,950.00** on 2026-10-16 [H33]. February's **$4,699** announcement is historical [H10], not today's quote. | Checkout eligibility, shipping, tax, electricity, support, financing, replacement and utilization remain unknown; no hourly equivalence or complete Pricebook asserted |

The source-complete AWS profile is produced by [#10's compute note](gpu-compute.md). Its host reference resolves to this package's `aws-ec2` record. Runpod public vCPU/RAM bundles are kept in notes because region and physical-core interpretation are not established for a complete `compute_profile`.

### Infrastructure storage comparison

| Offering / canonical type | Persistence and placement | Published price / unit / conditions, USD on 2026-10-16 | Unknowns and consumer implications |
| --- | --- | --- | --- |
| Runpod standard network volume / `file` | Independent persistent volume; for Pods, Secure Cloud only; selected datacenter constrains attached compute. Data does not automatically replicate between volumes. [H21] | First **1 TB $0.07/GB-month**, beyond **$0.05/GB-month**. Retained storage continues to cost money when compute stops. The specific hourly network-volume billing statement wins over the general per-second sentence under the adopted scope order; sub-hour invoice rounding remains unknown. [H21][H19] | Numeric maximum capacity, encryption-at-rest evidence, byte definition of vendor GB, account capacity unknown. `US-KS-2` is a documented storage endpoint, not proof of GPU availability. [H24] |
| Runpod container / volume disks / ephemeral or lease-persistent storage | Container disk temporary; volume disk retained for lease. [H19] | Container **$0.10/GB-month** while running; volume **$0.10 running / $0.20 stopped per GB-month**. [H19] | Not interchangeable with independent network-volume durability; backup/retention decisions remain #13/#28/#31. No separate catalog proposal without storage semantic review |
| AWS EBS gp3 / `block` | Block volume attached to EC2; product facts separate from chosen volume quantity. [H25] | AWS example uses **$0.08/vendor-GB-month**, **3,000 IOPS**, **125 MB/s** baseline, second billing with **60-second minimum**; example's region is unspecified. Page defines GB as **1024³ bytes**. [H26] | Not emitted as a regional price: pricing example is conditional, not a verified `us-east-1` quote. Additional IOPS, throughput, snapshots and transfer are separate. [H26] |
| Cloudflare R2 Standard / `object` | Automatic placement or location hint; hints are best effort. Jurisdiction restrictions (`eu`, `us`, restricted `fedramp`) have distinct semantics. [H27] | **$0.015/GB-month**, Class A **$4.50/million**, Class B **$0.36/million**; Internet egress free. Standard includes **10 GB-month**, **1M Class A**, **10M Class B** monthly. Usage rounds upward to billing units; the storage metric averages daily peaks over the documented **30-day** billing period. [H28] | Not a POSIX/block mount guarantee. No exact AWS region mapping; actual residency must be confirmed per bucket. Other services and origin transfer may charge. [H27][H28] |
| Modal Volumes / `file` | Distributed filesystem optimized for weight artifacts. Volumes v2 is beta with a data-loss caveat; concurrent writes to one file require care. [H23] | **$0.09/GiB-month** after included **1 TiB/month**, separately from network egress. [H07][H29] | `storage_gb_month` does not document GiB normalization sufficiently; no guessed GB price emitted. File semantics and v2 suitability need #13/#28/#31 review |
| Local disks / `block` or `file` according to exposed interface | Owned hardware/site; not a vendor cloud data-residency guarantee | Included hardware capacity and incremental disk/backup operating costs **unknown** in the on-prem example | A proposed quantity or synthetic dollar rate cannot replace an actual supplier quote |

For R2's request meters, exact conversions are **$0.0000045/Class-A request** and **$0.00000036/Class-B request**; the proposals retain class, free-allowance and rounding conditions. They do not combine the two classes into one interchangeable request rate. The storage proposal is a unit rate, not a whole-account bill. [H28]

Persistence and billing require additional conditions. Runpod warns that unfunded network volumes can eventually be terminated with unrecoverable data loss, and simultaneous worker writes can corrupt data. Independent persistence therefore does not establish backup, indefinite retention or application write coordination. [H21] Modal snapshots total storage daily and can continue charging deleted data for up to **four days**; Volumes v1 has a published **500,000-inode** limit. These are billing and filesystem constraints for #13/#15/#28/#31/#37/#39 to assess; they do not decide the consumers' retention or ACL policy. [H23]

### Networking, egress and attestations

Modal egress changed on **2026-10-01**: **$0.04/GiB** above Starter **1 TiB**, Team **10 TiB**, Enterprise **100 TiB** per workspace billing cycle. Volume reads/writes are excluded, but transfers between Modal containers and Cloud Bucket Mount uploads can count. A private path is not necessarily free. v1 has no network-transfer meter; keep this cost visible in notes pending #39/#40. [H29]

Runpod's Pod pricing documents no ingress/egress fees; AWS documents separate transfer/IP/network service charging. Neither establishes that external object-store or source-provider transfer is free. Hugging Face endpoint storage/egress line items remain unknown here. [H19][H15][H17]

Attestation **links are evidence locators, not compliance approval**. AWS provides a services-in-scope index [H30]. Runpod describes partner SOC 2/ISO 27001/PCI DSS qualifications, which is a vendor statement rather than a reviewed report for a selected datacenter [H31]. Modal's pricing page lists SOC 2 and plan-dependent HIPAA compatibility [H07]. Hugging Face publishes endpoint security documentation [H32]. Scope, report period, contracted entity, selected service/region and required agreements remain unknown until #35/#37 review. No `compliant=true` field is proposed.

## Comparison fields

This is the evidence requirement for each field, not an alternate JSON schema. Optional unverified canonical properties are omitted from JSON; notes retain explicit unknowns. A partial researched set must never be interpreted as exhaustive support.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence requirement / IDs | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/id`, `/version` | stable string; research-snapshot date when vendor has no product version | Version `2026-10-16` for unversioned services | Scope and capture date documented here | Snapshot label is project metadata, not a vendor release |
| `/spec/hosting_type` | canonical enum | `cloud`, `managed_api` | Operational boundary from product docs H01–H08 | Taxonomy adds no v1 enum |
| `/spec/regions` | array of provider-specific strings | AWS `us-east-1`; HF AWS two-region subset | Explicit region docs H03/H05 | GPU × region × account entitlement separate; absent/excluded member unknown unless exhaustive evidence exists |
| `/spec/accelerator_refs` | array of accelerator catalog IDs | Omitted for this bounded host submission | Exact device identity + resolving #10 catalog item required | Do not infer from a shared GPU price class |
| `/spec/supports_private_networking` | boolean | AWS EC2 true; scoped HF AWS true | VPC / intra-region PrivateLink docs H15/H14 | Capability does not validate an actual route or air gap |
| `/spec/storage_type` | canonical enum | `file`, `block`, `object` | Product interface docs H21/H23/H25/H28 | S3 API access does not make a mounted file volume an object store |
| `/spec/hosting_ref` | host catalog ID | Runpod → `runpod-pods`; EBS → `aws-ec2`; Modal → `modal-functions` | Explicit attachment/product linkage | All submitted references resolve locally |
| `/spec/region` | provider-specific location string | Runpod standard volume scoped `US-KS-2` | H24 endpoint table + H21 placement | Identifier syntax differs across providers; never compare geography by arbitrary text |
| `/spec/encryption_at_rest`, `/spec/max_capacity_gb` | boolean; number GB | Omitted where unverified | Explicit encryption guarantee / numeric supported capacity | Support-contact thresholds are not maxima |
| availability, quota, stock | note: enum `unknown` or sourced dated observation + scope | All account capacity unknown; published quota examples separately stated | Live public or authorized account evidence with timestamp | v1 has no canonical stock/quota field; don't add one silently |
| artifact support | note: string set + immutable artifact version/digest when selected | Containers/Hub/NGC by service | H04/H05/H06/H08/H09 | #33 owns adapter/merged-weight identity; storage choice cannot certify serving compatibility |
| networking / transport | note: protocol, endpoint reachability and route scope | TCP/HTTP, stdio, Streamable HTTP | H06/H13/H14/H15 | #27 owns MCP authentication/capability trust; #37 procedures |
| attestation | note: URL, scope, report date, entity; verified state | Vendor links, scoped reports unknown | H30/H31/H32 | Vendor claims are not independent compliance evidence |
| `/rates/*/meter`, `/unit_price` | canonical meter; decimal USD string | GPU-hour, storage-GB-month, request | H02/H07/H21/H28; source unit retained in conditions | GB/GiB, transfer meters, minima and allowances need #39 agreement |
| `/rates/*/valid_from`, `/provenance/checked_at` | RFC3339 timestamp | Observation begins 2026-10-16T12:39:46Z | Actual research capture time | Not a claim that vendor price first took effect then; no invented expiry |
| commitments, rounding, excluded costs | conditions array / note | On-demand, prepaid, minute/second/hour boundaries | H02/H07/H19/H20/H26/H28 | No universal 730-hour month; no utilization inferred |

## Evidence

Vendor URLs were accessed **2026-10-16**; the linked PR #75 owner decision was accessed **2026-10-17**. `PD` = primary documentation (published); `VC` = vendor claim (published, not independently reproduced). There are **no independent measurements** in this package. Calculations remain project estimates or exact conversions. #41's linked interim policy distinguishes checked from independently verified: this follow-up corrects source-only provenance to `unverified` in nine hosting/storage CatalogItems and the five Pricebook rates, retaining facts, versions and original check dates. Version-pinned facts are rechecked on version/source change; mutable rates, quotas, regions and terms remain dated observations with no TTL. Short paraphrases with links are acceptable interim reuse; bulk retrieval/copying awaits the per-source #41/#60 inventory.

Apply the owner's conflict order before leaving a fact unknown: normalize units, choose eligible most-specific scope, selected version/latest effective date, then fact-specific authority. Explicit requirements outrank capability lists, and billing/legal pages outrank overviews; equally ranked numeric evidence retains median/spread and a conservative decision. Equal-ranked opposite yes/no claims or missing eligible evidence remain unknown. Canonical GB is decimal 10^9 bytes; preserve vendor GiB values and conditions separately. No missing transfer/tier/rounding meter is invented.

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| H01 | [AWS Bedrock pricing][H01] | 2026-10-16 | Current page; MiniMax M2.5 table, US regions, USD | PD | Hosting boundary/price illustration; #5 must verify model lifecycle/access; no content redistribution grant inferred |
| H02 | [HF endpoint pricing][H02] | 2026-10-16 | Unversioned docs; AWS instance table, USD | PD | No complete region/GPU quota matrix; mutable |
| H03 | [HF endpoint FAQ][H03] | 2026-10-16 | AWS regions scoped; Azure/GCP also mentioned | PD | Research host record deliberately AWS-only |
| H04 | [HF custom containers][H04] | 2026-10-16 | Unversioned docs | PD | Container support doesn't establish model compatibility |
| H05 | [AWS G6e launch][H05] | 2026-10-16 | 2024-08-15; US launch regions | PD | Regional existence evidence; historical launch is not live capacity or exhaustive regional list |
| H06 | [Runpod Pods overview][H06] | 2026-10-16 | Page modified 2026-10-05 | PD | Environment/interface support; not a stock guarantee |
| H07 | [Modal pricing][H07] | 2026-10-16 | Current base Functions rates; USD; no chosen region | PD / VC for compliance line | No independent capacity/performance or report audit; reuse permission unknown |
| H08 | [Runpod Serverless overview][H08] | 2026-10-16 | Current service | PD | Queue versus load-balancing distinction |
| H09 | [NVIDIA DGX Spark user guide][H09] | 2026-10-16 | Updated 2026-09-10 | PD | Local host example; accelerator fit deferred |
| H10 | [NVIDIA price-change announcement][H10] | 2026-10-16 | February 2026 manufacturer post; dollar MSRP | PD | Historical published price, no October sale/stock guarantee; USD interpretation of manufacturer dollar MSRP |
| H11 | [Qdrant Managed Cloud][H11] | 2026-10-16 | Unversioned product docs | PD | Boundary example only; no DB product evaluation/prices copied |
| H12 | [Qdrant local quickstart][H12] | 2026-10-16 | Mutable Docker example | PD | Example deployment is not production certification |
| H13 | [MCP transports][H13] | 2026-10-16 | Protocol 2025-11-25 | PD | Pinned transport document; #27 must decide retained protocol versions |
| H14 | [HF AWS PrivateLink][H14] | 2026-10-16 | AWS intra-region service | PD | Requires correct private endpoint/account/network setup |
| H15 | [AWS VPC guide][H15] | 2026-10-16 | Current docs | PD | Logical isolation capability; billed network components separate |
| H16 | [AWS EC2 quotas][H16] | 2026-10-16 | Regional vCPU quotas | PD | Defaults are not actual account quotas |
| H17 | [AWS EC2 IP addressing][H17] | 2026-10-16 | Current docs | PD | Transfer/IP charging categories, no asserted numeric transfer rate |
| H18 | [Runpod public pricing][H18] | 2026-10-16 | Updated 2026-10-08; USD | PD | Toggle state/region not bound in extracted price display; not emitted as specific Pod rates |
| H19 | [Runpod Pod pricing][H19] | 2026-10-16 | Modified 2026-07-20; USD | PD | Intro versus network-volume billing granularity conflict retained |
| H20 | [Runpod Serverless billing][H20] | 2026-10-16 | Modified 2026-10-15; USD | PD | Startup/idle phases bill; shared price class not exact GPU promise |
| H21 | [Runpod network volumes][H21] | 2026-10-16 | Modified 2026-07-20; USD | PD | Location / Secure Cloud / persistence, insufficient-balance deletion and concurrent-write constraints; no throughput claims adopted |
| H22 | [Modal region selection][H22] | 2026-10-16 | Current routing/container policy | PD | Location, routing, input storage differ; region choice alone not full residency proof |
| H23 | [Modal Volumes][H23] | 2026-10-16 | v1 and v2 distinguished; v2 beta | PD / VC for durability | Daily billing snapshots/post-delete tail and v1 inode limit are published conditions; no measured filesystem capacity result; beta caveat retained |
| H24 | [Runpod S3-compatible API][H24] | 2026-10-16 | `US-KS-2` supported endpoint | PD | Endpoint existence doesn't imply GPU capacity |
| H25 | [AWS EBS volumes][H25] | 2026-10-16 | Current EBS docs | PD | Block interface classification |
| H26 | [AWS EBS pricing][H26] | 2026-10-16 | Conditional gp3 example; USD; region unspecified | PD | Do not turn example into regional live quote |
| H27 | [Cloudflare R2 data location][H27] | 2026-10-16 | Updated 2026-08-19 | PD / VC for residency guarantee | Hints differ from jurisdiction restrictions; no AWS-code equivalence |
| H28 | [Cloudflare R2 pricing][H28] | 2026-10-16 | Updated 2026-10-01; Standard, USD | PD | Request classes, rounding, allowances separate; complete account cost needs scenario |
| H29 | [Modal egress billing][H29] | 2026-10-16 | Effective 2026-10-01; USD | PD | Workspace allowance; GiB; no v1 transfer meter |
| H30 | [AWS compliance service index][H30] | 2026-10-16 | Current index; selected report scope unknown | PD | Index link is not report review or workload approval |
| H31 | [Runpod security documentation][H31] | 2026-10-16 | Secure Cloud partner claims | VC | Certification scope/report not independently inspected |
| H32 | [HF endpoint security][H32] | 2026-10-16 | Current docs | PD | Link for consuming security review, no compliance conclusion |
| H33 | [NVIDIA US DGX Spark storefront][H33] | 2026-10-16 | US storefront; dollar display interpreted as USD | PD | Displayed hardware anchor, not completed checkout, tax/shipping total or stock confirmation |

Only paraphrased component facts and source locators are submitted. Automated collection/republication rights and definitive retention terms are **unresolved** for #41; public readability is not treated as permission to redistribute documentation. No raw crawls, weights, private data or restricted reports are included, so no external-artifact manifest is required.

## Compatibility proposals

[Hosting rule proposals](rules/hosting-rules.md) use the shared template and separate outcomes from severity:

- `t2-hosting-private-networking`: evidenced capability check; actual route and full residency remain unverified.
- `t2-hosting-mounted-storage-locality`: provider-agnostic mount constraint, with Runpod as one evidenced instance; v1 `stored_in` exists, while CD-6 proposes mount-versus-fetch and CD-9 location semantics. Replaces the earlier Runpod-specific proposal ID.
- `t2-hosting-offering-membership`: conservative positive-support evidence; hypotheses about absence/exhaustiveness cannot become hard failures.

All are **proposed for #40 review**, not approved rules or compatibility certifications. Pass/fail/unknown/skipped are outcomes; info/warning/error are severities.

## Pricing and capacity

Two bounded, reproducible **project estimates**, with no measured workload claim:

1. HF AWS L4 endpoint, one replica, 60 fully billable minutes at the published hourly price: `1 replica × 1 hour × $0.80 = $0.80` compute. Region is an available AWS region from H03, but exact GPU/region entitlement is unknown. Network, storage, taxes and any additional plan charges are excluded; this is not a total deployment quote. [H02][H03]
2. Modal base H100 GPU time, no selected region, exactly 3,600 billed GPU seconds: `3,600 × $0.001097 = $3.9492` GPU-only. CPU, RAM, idle/startup, storage, egress and credits must be accounted for separately. A selected region applies its documented multiplier; the numeric result is an exact unit conversion, not achieved inference cost. [H07][H22]

Cloud VM and on-prem categories also have the published Runpod and hardware price anchors above, with their known regional/current-quote gaps visible. No throughput, latency, active GPU capacity or utilization has been inferred from price. #39 must apply the user's actual runtime, idle interval, requests/tokens, quantities, month length, location, free usage, commitments and taxes.

The R2 unit rates are sufficiently complete for constrained proposals. For Runpod network storage, the small-volume unit rate is usable as a research rate with explicit conditions; tier boundary and sub-hour invoice rounding remain questions. No automatic cost aggregation is approved by these proposals.

## Recommendation and rationale

Adopt the taxonomy and conservative unknown handling for review. Keep operational responsibility separate from invocation protocol. Compare complete cost scopes before selecting a vendor: managed API tokens, dedicated replica time, running serverless workers, rented instance time, and owned capital cost are different quantities. Storage must stay visible when compute is stopped; placement constraints can reduce the eligible GPU pool. Location capability, account quota, current stock and contractual reservation should be separate facts.

Start structured intake with the constrained service/storage snapshots listed below. Treat them as research inputs, preserve exact versions in prices, and require deployment/security/consumer review before turning the notes into compatibility assertions. No contract files change.

## Structured artifacts

Each service version `2026-10-16` denotes this researched snapshot, not a vendor semantic release. Required canonical fields are sourced; optional unknown facts are omitted, not fabricated. Proposal status `active` describes the documented service, not research approval.

- Hosting: [AWS EC2](../../catalog/proposals/t2-hosting-aws-ec2.json), [Runpod Pods](../../catalog/proposals/t2-hosting-runpod-pods.json), [Runpod Serverless](../../catalog/proposals/t2-hosting-runpod-serverless.json), [HF AWS endpoints](../../catalog/proposals/t2-hosting-huggingface-endpoints-aws.json), [Modal Functions](../../catalog/proposals/t2-hosting-modal-functions.json).
- Storage: [Runpod standard volume, US-KS-2](../../catalog/proposals/t2-hosting-runpod-network-standard-us-ks-2.json), [EBS gp3](../../catalog/proposals/t2-hosting-aws-ebs-gp3.json), [R2 Standard](../../catalog/proposals/t2-hosting-cloudflare-r2-standard.json), [Modal Volumes v1](../../catalog/proposals/t2-hosting-modal-volumes-v1.json).
- Prices: [constrained hosting/storage rates](../../pricing/proposals/t2-hosting-2026-10-16.json). Every rate references an exact submitted item version. Bedrock model rates stay with #5; uncertain Pod/EC2/hardware rates, GiB-based storage and egress stay in notes.

No complete `ResourceEstimate`, `CostEstimate`, runtime configuration or deployment manifest is asserted by this package.

## Open questions and handoffs

Live owners were checked through GitHub on 2026-10-16. **No consuming-owner acknowledgements were present for this package at research time.** The orchestrator must link actual comments/reviews before checking the handoff criterion; agent coordination is not owner acceptance.

| Consumer / live owner | Specific requested acknowledgement | State / impact |
| --- | --- | --- |
| #10 @Mattycodes69 | `aws-ec2` ID/version and researched region subset; source-complete profiles versus incomplete Runpod offers | Research coordinated; human acceptance pending |
| #14, #15 @zabyxc01 | API/managed/self-hosted categories; object/block/file interfaces; vector DB evaluation remains T3 | Pending; no embedding/vector product choice made |
| #27 @CompleteDotTech | Local stdio versus remote HTTP host requirements; service lifetime, auth/trust and timeout evidence still theirs | Pending; no MCP server suitability assertion |
| #31 @appletechie | Persistent storage cost/locality/parallel-write caveats, funding/deletion and inode constraints, and non-shared training estimate ownership | Pending; no training sizing duplicated |
| #37, #39 @PUSHINGSQUARES | Deployment constraints, unknown quota/capacity, storage/egress and conditions including post-delete billing; billing aggregation policy | Pending; research can be reviewed independently |
| #13 @zabyxc01; #28 @CompleteDotTech | Infrastructure product facts do not decide ACL propagation, retention, consent or deletion semantics | Pending boundary review |
| #3, #40, #41 current coassignees; scoped response by @tynamite | Taxonomy; rule applicability/coverage; source/freshness/reuse | PR #75 accepts taxonomy with constraints, narrows rule intake and adopts interim policy; final contract and per-source rights work remain |
| #5/#6/#7 @zwright8; #33 @appletechie | Model/API lifecycle and context assumptions; artifact access, adapter/merged weights and immutable provenance | Pending; not inferred from host artifact support |

| Question / follow-up owner | Required action and impact |
| --- | --- |
| Initial regions — #9 @Mattycodes69 / @appletechie | #3 imposes no region requirement and accepts US examples as samples; #9 still decides product coverage breadth. No global coverage commitment is inferred |
| Current inventory and access — #9/#10 @Mattycodes69 | Obtain dated public/account availability and quota evidence only if a deployability claim is needed; keep unknown meanwhile |
| Invoice rounding — #39 live owners with Runpod | Specific network-volume hourly billing outranks generic wording; confirm sub-hour invoice rounding and avoid unsupported invoice predictions |
| Storage units and transfer meters — #39/#40 live owners | Decimal GB is confirmed canonical by #40; preserve vendor GiB. Define aggregation and new transfer/IOPS/throughput/minimum fields only through versioned proposal; affected #9/#31/#39/#42 consumers remain |
| Tier and allowance semantics — #39 @PUSHINGSQUARES | Adopt exact threshold/rounding/allowance aggregation before automatic costing; rates in notes/conditions do not implement tier logic |
| Full residency and security — #35/#37 @PUSHINGSQUARES, #13 @zabyxc01 | Review all processing, routing, artifact and backup locations, agreement/report scope; host region alone is insufficient |
| Freshness/reuse — #41 @tynamite / @PUSHINGSQUARES | Interim version-pinned/current-state distinction and conflict order are adopted; per-source rights inventory and automated reuse remain unresolved |
| Compatibility metadata — #40 @tynamite | Model mounted-volume relationship and evidence completeness, retain unknown behavior, review three rules; no v1 migration made here |

## Acceptance assessment and validation

The criteria below preserve the live issue wording. “Prepared” means an artifact exists for review, not issue completion.

| #9 criterion | Artifact / evidence | Current assessment / required reviewer |
| --- | --- | --- |
| Taxonomy with boundary examples | Taxonomy table; H01–H13 | Prepared; #3 @tynamite / #9 @Mattycodes69 review pending |
| Candidate set per category with priced examples and provenance | Candidate and storage tables; H01–H10, H18–H29; explicit incomplete quote scope | Prepared; #9/#39 review pending; no complete regional cloud VM or current on-prem quote claimed |
| Availability represented with explicit `unknown` handling | Candidate table, field requirements, rules; H16/H21/H24 | Prepared; stock/entitlement remain unknown |
| Decision record merged at `research/T2-infrastructure/hosting.md` following the research method | This note + structured artifacts; PR #75 | Merged at `ec612eb14edaf63cc9caca2ab655d053c9114dd4`; changed follow-up and full acceptance remain pending |
| Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | Taxonomy, API/managed/cloud/on-prem comparisons and non-model boundaries | Prepared; #3/#9 review pending |
| Comparison fields defined with type, unit, and evidence requirement | Comparison-fields table | Prepared; #40 unit/completeness questions explicit |
| Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | [Three rule proposals](rules/hosting-rules.md) | Prepared; evidence-backed assertions separated from hypotheses; #40 approval pending |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | Claim-level H01–H33 links and evidence table; published/estimate labels | Source accuracy rechecked against primary pages on 2026-10-16; owner accuracy/rights/freshness review pending |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | Handoff table, seven direct consumers | **Not satisfied:** no human acknowledgements yet |
| Open questions recorded with a named follow-up owner | Questions table using live assignees | Prepared; owner decisions pending |

Validation is reported after running the canonical workflow by the integration orchestrator. Schema validity establishes structure/references only; it does not establish claim truth, freshness, licensing permission, stock, compatibility, owner acceptance or merge. The source review here checked the cited page conditions and preserved unresolved conflicts; it did not audit private compliance reports or run workloads.

Follow-up validation on 2026-10-17, Python 3.12.14: pinned dependency installation, 21 contract tests, 24 research tests, research intake (30 catalog proposals / two Pricebooks), market integrity (32 entities / 1,536 cells / 20 issues) and `git diff --check` pass. Research tests used normal temporary-directory access outside the Windows sandbox. JSON semantic comparison confirms only 24 provenance labels and nine `updated_at` values changed; all facts, prices, versions, URLs and source-check dates are preserved. Independent review checked the workload/host private-network OR predicate and preserved API-region checks when local hardware is opaque. Remaining regional breadth, billing aggregation, consumer acceptance and final versioned contract work are not automated checks.

[H01]: https://aws.amazon.com/bedrock/pricing/
[H02]: https://huggingface.co/docs/inference-endpoints/pricing
[H03]: https://huggingface.co/docs/inference-endpoints/faq
[H04]: https://huggingface.co/docs/inference-endpoints/guides/custom_container
[H05]: https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-ec2-g6e-instances/
[H06]: https://docs.runpod.io/pods/overview
[H07]: https://modal.com/pricing
[H08]: https://docs.runpod.io/serverless/overview
[H09]: https://docs.nvidia.com/dgx/dgx-spark/index.html
[H10]: https://forums.developer.nvidia.com/t/2-23-2026-price-change-announcement/361713
[H11]: https://qdrant.tech/documentation/cloud/
[H12]: https://qdrant.tech/documentation/quickstart/
[H13]: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
[H14]: https://huggingface.co/docs/inference-endpoints/guides/private_link
[H15]: https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
[H16]: https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-quotas.html
[H17]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html
[H18]: https://www.runpod.io/pricing
[H19]: https://docs.runpod.io/pods/pricing
[H20]: https://docs.runpod.io/serverless/pricing
[H21]: https://docs.runpod.io/storage/network-volumes
[H22]: https://modal.com/docs/guide/region-selection
[H23]: https://modal.com/docs/guide/volumes
[H24]: https://docs.runpod.io/storage/s3-api
[H25]: https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes.html
[H26]: https://aws.amazon.com/ebs/pricing/
[H27]: https://developers.cloudflare.com/r2/reference/data-location/
[H28]: https://developers.cloudflare.com/r2/pricing/
[H29]: https://modal.com/docs/guide/network-egress-billing
[H30]: https://aws.amazon.com/compliance/services-in-scope/
[H31]: https://docs.runpod.io/references/security-and-compliance
[H32]: https://huggingface.co/docs/inference-endpoints/security
[H33]: https://marketplace.nvidia.com/en-us/enterprise/personal-ai-supercomputers/dgx-spark/
