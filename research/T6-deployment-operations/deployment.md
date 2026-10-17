# T6: Deployment

Issue: #37 · Contract: 1.0.0 · Kinds: `deployment_target`
Status: draft for owner review · Last researched: 2026-10-17

## User decision

What does it take to ship this build, and is it ready?

The builder answers this for each serving component of a build. Mode follows the #3 owner position adopted in the [PR #75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) and carried in [#9 hosting](../T2-infrastructure/hosting.md):
- **API:** provider-operated shared capacity.
- **Managed:** provider-operated dedicated instances or reserved throughput.
- **Self-hosted:** the user operates the runtime.
- **Hybrid:** serving components in one build use different modes. Every component keeps its own mode's checklist.

Billing, `hosting_type` and "exposes an HTTP API" never decide mode. Tools, MCP servers, storage and monitoring don't set mode, but their operator, isolation and residency are still checked. Development and production are separate builds. The per-component `deployment` object is a proposal in [PR #81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81) (`research/T0-configuration/deployment-mode.md` at `e2bcc35`), still pending. This note doesn't depend on it being accepted, and it adds no v1 fields.

Out of scope: generating or running deployable artifacts (Helm charts, manifests, IaC). Nothing was deployed, provisioned or signed up for during this research.

## Candidate options

Deployment representations, by mode. These are the targets a build can resolve to. They aren't recommendations.

| Mode | Representation | Example offerings (evidence) | What the user controls |
| --- | --- | --- | --- |
| API | Provider endpoint + credential | OpenAI, Anthropic, Bedrock on-demand, Azure Foundry Standard / Global Standard / Data Zone Standard (OA1, BR1, AZ1; #5 O1–A5, B1–B4) | Model ID or snapshot, region or routing profile, key scope, client retry/fallback |
| Managed | Provider endpoint configuration on dedicated capacity | Hugging Face Inference Endpoints, SageMaker real-time endpoints, Foundry Provisioned types, Bedrock Provisioned Throughput, Modal Functions, Runpod Serverless (HF1, HF2, S1–S3, AZ1, BR1, MO1, RP1; #9 H02–H08) | Artifact, instance/GPU class, replicas or workers, scaling, access level, traffic shifting where offered |
| Self-hosted | Container image, plus Kubernetes Deployment, KServe InferenceService or vLLM Production Stack Helm chart; or a local service | vLLM, llama.cpp (#11); Kubernetes (K1–K4); KServe (KS1); vLLM Production Stack (VL3); EC2, Runpod Pods, on-prem (#9) | Everything: image, engine build, probes, secrets, network, rollout, rollback |
| Hybrid | Union of the above, one per serving component | e.g. local LLM + API embedding model (#81 boundary example) | Per component, plus the data flows between them (D-R6 in #81) |

## Comparison fields

These are the issue's minimum fields. They are note-level research fields, not a JSON schema. JSON mappings are listed separately below.

| Field | Type and unit | Evidence requirement | Unknown behavior |
| --- | --- | --- | --- |
| `deployment step` | Short imperative string; stable step ID (`DS-xx`) | — | — |
| `applies to mode` | Set of `api`, `managed`, `self_hosted`; hybrid = per-component union | #3 owner position (per serving component) | A component with no resolved mode is `unknown` and gets every checklist |
| `prerequisites` | List of component kinds or issue outputs (e.g. `inference_engine` build pin from #11) | Must name the issue that supplies it | A missing input is `unknown`, never assumed |
| `readiness check` | Testable assertion with outcome `pass/fail/unknown/skipped` and a fixed severity | Primary documentation for the mechanism (URL, access date, version) | Unknown never passes (see rules) |
| `source` | Evidence ID(s) below, or an issue/evidence ID in an input note (e.g. `#9 H14`) | Primary source, access date, version or modified date | No source: the step stays a hypothesis |
| `source component` | Issue number(s) whose outputs the check reads | Linked note | Pending inputs are marked pending |

## Deployment checklist by mode

A = API, M = managed, S = self-hosted. "Source component" links each readiness check to the issue that supplies its input.

### Endpoint and artifact

| Step | Mode | Prerequisites | Readiness check | Source | Source component |
| --- | --- | --- | --- | --- | --- |
| DS-01 Pin the model route | A | Model + provider selection | Exact provider model ID or dated snapshot recorded; alias-only IDs are `unknown` | #5 O1, A1; OA1 | #5, #6 |
| DS-02 Pin the artifact | M, S | Model or fine-tune revision (full commit SHA), engine version, image digest | Every artifact is an immutable reference. A branch, tag or `main` README is not a pin | #33 G3; #11 E05; VL3 | #6, #11, #33 |
| DS-03 Check the artifact loads on the target | M, S | Format/adapter facts from #33; engine support tuple from #11 | Baseline `rule.engine.model.format` and #33 A-01 to A-11 return no fail or unknown | #33 V1–V17 | #11, #33 |
| DS-04 Configure the endpoint surface | A, M, S | API contract (chat, tools, structured output) | The consumer's request contract is supported by the engine/provider | #11 E06–E08 | #11, #25 (pending) |
| DS-05 Configure fallback and retry | A, M | Second route or provider (optional) | A fallback route has its own pins and passes its own checks. A fallback in another region re-runs residency | #5; BR1 | #5, #81 D-R6 |

### Secrets and access

| Step | Mode | Prerequisites | Readiness check | Source | Source component |
| --- | --- | --- | --- | --- | --- |
| DS-06 Keep credentials server-side | A, M, S | Secret store | No key in client code or build/manifest JSON. OpenAI: "Don't share it with others or expose it in any client-side code such as browsers or apps. Load API keys from an environment variable or key management service on the server." | OA1 | — |
| DS-07 Scope keys | A | Org/project structure | Key or project scope recorded (e.g. OpenAI projects). Other providers' scoping: unknown here | OA1 | #5 |
| DS-08 Require authentication on the endpoint | M | Endpoint access level | HF endpoints have Public ("requires no authentication"), Protected (HF token) and Private (PrivateLink only). Public in production fails T6-D07 | HF1 | #9 |
| DS-09 Protect every engine route | S | Engine version, exposed port | vLLM v0.31.0 `--api-key` protects only `/v1`, `/v2`, `/inference`, `/cohere`. `/invocations` serves inference and `/update_weights` "can alter model behavior", both unauthenticated. Needs a reverse proxy or a private network | VL1, VL2 | #11 |
| DS-10 Encrypt and restrict secrets | S | Cluster config | Kubernetes Secrets are "stored unencrypted" in etcd by default, and anyone who can create a Pod in the namespace can read them. Encryption at rest + least-privilege RBAC must be evidenced | K3 | — |
| DS-11 Inject secrets at runtime | M | Platform secret feature | Secrets are injected as environment variables (Modal `secrets=[...]`), not baked into images | MO1 | #9 |

### Network, region and residency

| Step | Mode | Prerequisites | Readiness check | Source | Source component |
| --- | --- | --- | --- | --- | --- |
| DS-12 Private path when requested | M, S | Host private-network capability | `t2-hosting-private-networking` passes. HF Private endpoints are PrivateLink-only, intra-region | #9 H14, H15; HF1 | #9 |
| DS-13 Processing region, not only deployment region | A, M | Routing profile or deployment type | Bedrock geographic profiles route "within the geography"; global profiles route to "any supported AWS commercial Region". Azure Global types "may be processed in any Azure region" while data at rest stays in the geography. Feeds #81 D-R6 | BR1, AZ1 | #5, #81 |
| DS-14 Target region equals objective | A, M, S | `settings_deployment_target.region`, `build.objectives.region` | Baseline `rule.deployment.target.region`. String equality can't express geographies or global routing (DS-13), so CD-9 in #81 applies | contract | #3, #9, #41 |
| DS-15 Outbound data flows | A, M, S | Telemetry, logging, tool destinations | Every external destination carrying workload data has a location. Shadow-response logs count (DS-24) | #81 D-R6; S3 | #38, #27 (pending) |

### Scaling and capacity

| Step | Mode | Prerequisites | Readiness check | Source | Source component |
| --- | --- | --- | --- | --- | --- |
| DS-16 Set replica bounds | M, S | `replicas_min`, `replicas_max` | `replicas_min` ≤ `replicas_max` (T6-D03) | contract | — |
| DS-17 Decide scale-to-zero | M | Latency target from #2 | HF: scales to 0 after 15 idle minutes; returns 502 while a replica initializes, with "no queueing system". Runpod: active workers bill while idle. Production with `replicas_min` = 0 warns (T6-D04) | HF2; RP1 | #2, #39 |
| DS-18 Account quota and capacity | A, M, S | Account | Quota and stock are account-specific and stay `unknown` until checked. EC2 default G/VT quota is 0 | #9 H16; #5 B3 | #9, #10 |
| DS-19 Throughput type | A, M | Provider | Bedrock inference profiles "currently don't support Provisioned Throughput" | BR1 | #5 |

### Health checks

| Step | Mode | Prerequisites | Readiness check | Source | Source component |
| --- | --- | --- | --- | --- | --- |
| DS-20 Startup probe for model load | S | Load time | Startup probe or equivalent present. Liveness/readiness don't run until it succeeds, so a long weight load isn't killed by liveness | K2 | #10, #11 |
| DS-21 Readiness gates traffic | S | Engine health route | A failing readiness probe removes the Pod from Service endpoints. vLLM exposes `/health`; llama.cpp documents health/metrics | K2; VL2; #11 E14 | #11 |
| DS-22 Managed health | M | Platform | Platform health semantics are recorded per offering; unknown where undocumented. HF 502 during init (DS-17) | HF2 | #9 |
| DS-23 Request tracing | A | — | Log provider request IDs (OpenAI `x-request-id`; `X-Client-Request-Id` optional) | OA1 | #38 |

### Rollout and rollback

| Step | Mode | Prerequisites | Readiness check | Source | Source component |
| --- | --- | --- | --- | --- | --- |
| DS-24 Choose a rollout strategy the target supports | M, S | Target capability | Canary or blue/green needs documented traffic splitting (T6-D11). See the strategy matrix below | K1, K4, KS1, S1, S2 | — |
| DS-25 Keep a rollback artifact | M, S | Previous immutable artifact + config | A rollback reference exists and is retained (T6-D01). Kubernetes keeps 10 old ReplicaSets by default; `revisionHistoryLimit: 0` means a rollout "cannot be undone" | K1; PRICING_AND_GATES §7 | #42 |
| DS-26 Rollback trigger | M, S | Alarm signals | SageMaker auto-rollback uses CloudWatch alarms during the bake period. The signals come from #38 | S1, S2 | #38 |
| DS-27 API model change | A | Snapshot pin | An API "rollout" is a model-ID change. Rollback means re-pinning the previous snapshot, which only works while the provider still serves it (lifecycle risks below) | #5 O1; #33 V17 | #5 |

### Gates and approval

| Step | Mode | Prerequisites | Readiness check | Source | Source component |
| --- | --- | --- | --- | --- | --- |
| DS-28 Compatibility clean | all | EvaluationReport for this `build_revision` | No `fail` and no blocking `unknown` (PRICING_AND_GATES §2) | contract | #40 |
| DS-29 Evaluation gate passed | all | Quality run on the current revision | Pending #36: suites, thresholds and the fine-tune safety-regression gate (#33 A-20) | pending | #36 |
| DS-30 Guardrail gate passed | all | Guardrail selection and its gate | Pending #35: which controls apply per mode, especially mutating tools and MCP | pending | #35, #27 |
| DS-31 Cost quote complete | all | CostEstimate `coverage=complete` | Budget gate can't pass on partial or unknown coverage | PRICING_AND_GATES §5 | #39 |
| DS-32 Human approvals | all | Approval scopes | Every required scope is `approved` for this revision; any `pending` keeps the manifest `proposed` (T6-D10) | contract | owner decision |
| DS-33 Monitoring present | all | `monitoring_stack` selection | Baseline `rule.production.gates` checks existence only | contract | #38 |

### Strategy matrix

| Strategy | v1 `rollout_strategy` | Kubernetes Deployment (K1, K4) | KServe 0.20 (KS1) | SageMaker (S1–S3) | Notes |
| --- | --- | --- | --- | --- | --- |
| Rolling | `rolling` | Native. Defaults: 25% max unavailable, 25% max surge; the controller stops a bad rollout; `progressDeadlineSeconds` defaults to 600 | — | Rolling deployments in batches, with alarms | Old and new versions serve together during the roll |
| Canary | `canary` | Not native: run two Deployments with a `track` label and set the ratio by replica count | `canaryTrafficPercent`. "Only supported in serverless deployment mode." Rollback by setting it to 0 | Blue/green canary mode (two steps) and linear (n steps), with a bake period | A replica-ratio canary isn't a percentage of requests |
| Blue/green | `blue_green` | Not a Deployment strategy; needs a second Deployment + Service switch (no K8s source checked) | — | Default for endpoint updates; all-at-once mode; blue fleet terminated after a clean bake | Both fleets run during the bake (cost: #39) |
| Shadow | **none** | — | — | Shadow tests: a copy of live requests goes to the shadow variant; only production responses return; shadow responses can be logged | Not a v1 enum value. Treat it as a pre-promotion test, not a rollout (proposal to #40). Shadow logs are a data flow (DS-15) |
| Manual | `manual` | `kubectl rollout undo` (optionally `--to-revision`) | Edit and re-apply | — | — |

## Readiness evaluation

Conceptual states map onto the existing v1 `EvaluationReport.deployment_readiness` enum (`ready`, `blocked`, `needs_review`). No new enum is proposed.

| Conceptual state | Condition on findings | `deployment_readiness` |
| --- | --- | --- |
| Ready | No `error` finding with outcome `fail` or `unknown` | `ready` |
| Ready with warnings | As Ready, plus `warning` findings or `on_unknown=defer` unknowns | `ready` (findings retained and shown) |
| Missing prerequisites | An existence rule fails (e.g. `rule.production.gates`, `rule.selfhost.requires.infrastructure`) | `blocked` |
| Incompatible | Any other `error` finding with outcome `fail` | `blocked` |
| Unknown | An `error` finding is `unknown` with `on_unknown=block` / `review` | `blocked` / `needs_review` |

Evidence status is separate. A check can pass on source-checked but unverified evidence, and `ready` is not deployment approval: the DeploymentManifest stays `proposed` until DS-28 to DS-33 hold for the same `build_revision`.

### Scenarios (architectural illustrations, synthetic)

| # | Scenario | Mode | Checklist rows that decide readiness |
| --- | --- | --- | --- |
| 1 | API-only chat app | A | DS-01, 05–07, 13, 23, 27–33 |
| 2 | Local single-GPU vLLM | S | DS-02, 03, 09, 10, 16, 20, 21, 25 + baseline VRAM rules (#10) |
| 3 | Multi-GPU vLLM | S | As 2, plus `rule.tensor.parallel.*` and per-device VRAM (#10, #11) |
| 4 | HF dedicated endpoint | M | DS-02, 03, 08, 12, 17, 22, 24–26 |
| 5 | RAG app | per component | Each serving component (LLM, embedding model, vector DB) gets its own mode's rows; ACLs and index rebuild belong to #13 (pending) |
| 6 | Agent with tools | per component | As its model's mode, plus DS-15 and DS-30 for tool/MCP destinations (#25, #27 pending) |
| 7 | Fine-tuned model | as its base (adapter) or own (merged) | DS-02, 03 with #33 A-01 to A-20; lifecycle risks below |
| 8 | Hybrid: local LLM + API embeddings | hybrid | The self-hosted rows for the LLM, the API rows for embeddings, and DS-13/15 across the flow |

## Artifact lifecycle risks

Each risk can turn a deployed build undeployable or unrollbackable without any user change.

| Risk | Fact | Evidence | Consequence for readiness and rollback |
| --- | --- | --- | --- |
| Provider-locked fine-tune shuts down with its base | OpenAI fine-tunes "follow the same shutdown schedule as their underlying base models" | #33 V17, A-12 | Rollback target can disappear; warn with the shutdown date |
| Idle managed deployment deleted | Foundry: no calls for more than 15 days → deployment "automatically deleted"; model kept | #33 V16, A-13 (classic FAQ only) | Re-deploy needed; a rollback "artifact" that is a deployment name isn't durable |
| Idle serverless endpoint scaled down | Runpod: 3 idle days → max workers 2; 7 days → 0, until the user raises it | RP1 | Endpoint silently stops serving; readiness must be rechecked, not cached |
| Scale-to-zero cold start | HF: 502 during init, no queue | HF2 | Production `replicas_min` = 0 warns (T6-D04) |
| Revision history pruned | Kubernetes: once an old ReplicaSet is deleted, "you lose the ability to rollback to that revision" | K1 | Rollback needs a retained image digest + config, not only cluster history (T6-D01) |
| Runtime weight mutation | vLLM `/update_weights` is unauthenticated and "can alter model behavior" | VL2 | The served model may stop matching the pinned artifact; DS-09 |
| Unpinned deployment tooling | vLLM Production Stack README on `main`; latest release `vllm-stack-0.1.13` (2026-09-29). Autoscaling on vLLM metrics is on its roadmap, not shipped | VL3 | Pin the chart release; don't assume metric autoscaling |
| Deprecated engine | TGI in maintenance mode, repository archived | #11 E20; #33 V4 | Warn for new builds (#33 A-10) |
| Regional deployment types arrive last | Azure: geography-based types "have no guaranteed availability date" | AZ1 | A residency-constrained build may have no available type; `unknown`, not fail |

## Mapping to the v1 contract

### `spec_deployment_target` (CatalogItem)

| Field | Type | Finding | Gap |
| --- | --- | --- | --- |
| `target_type` (required) | enum `api_endpoint`, `batch_worker`, `application`, `edge` | Real-time endpoints → `api_endpoint`; SageMaker async / batch → `batch_worker`; local app → `application` | Doesn't carry mode; mode comes from the serving component (#3) |
| `hosting_ref` | `hosting_platform` ID | Resolves to #9 records, e.g. `huggingface-endpoints-aws`, `runpod-serverless` | API targets have no hosting platform in v1 |
| `region` | string | Single string | Can't express a geography or a global routing profile (DS-13) |
| `supports_autoscale` | boolean | HF: true (HF2); Runpod: worker scaling (RP1) | Omitted = unknown, not false |
| `supports_rollback` | boolean | SageMaker auto-rollback (S2); KServe pin-previous (KS1) | Doesn't say which strategies; see T6-C1 |

### `settings_deployment_target` (Selection)

`environment` (`development`/`staging`/`production`) drives `rule.production.gates`. `replicas_min` (≥0), `replicas_max` (≥1), `region` and `approval_ticket` are used by DS-14, DS-16 and DS-17. Secrets, network exposure, access level, health checks and rollout parameters have no v1 field. They stay in notes.

### `DeploymentManifest`

| Field | Use | Gap |
| --- | --- | --- |
| `build_id`, `build_revision`, `*_report_id`, `quality_run_id`, `cost_estimate_id`, `resource_estimate_id` | Must all be for the same revision (PRICING_AND_GATES) | `resource_estimate_id` is required even for API-only builds, which have no self-hosted resource estimate (T6-C2) |
| `approvals[]` (`owner`, `security`, `finance`, `compliance`) | DS-32 | Which scopes are required per environment is an owner decision |
| `rollout_strategy` (`canary`, `blue_green`, `rolling`, `manual`) | DS-24 | No `shadow`; no canary percentage, bake time or trigger (T6-C1) |
| `rollback_artifact_uri` (optional) | DS-25 | Optional in v1, but §7 of PRICING_AND_GATES requires a rollback artifact/plan for production (T6-D01) |
| `status` | `proposed` until gates and approvals hold | — |

## Compatibility proposals

Proposed for #40 in the [rule proposal template](../../templates/rule-proposal.md) format. Shared fields, stated once:
- Each rule has one fixed severity. Outcome (`pass/fail/unknown/skipped`) is separate from severity (`info/warning/error`).
- **Missing data:** an input that is absent or not evidenced gives `unknown`, never `pass`. A known non-applicable scope gives `skipped`.
- **Explanation:** show the rule, the failing or unresolved part and its inputs; the remediation is in the table.
- **Version impact:** rules marked "needs field" depend on a #40 versioned change; none edits v1.
- **Examples:** synthetic only.

"Source checked" means the cited primary text was read on the access date and supports the premise, per the interim #41 definition in the [#75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Nothing here is independently verified. Rules are separated into source-checked premises and policy hypotheses.

| ID | Applies when | Assertion | Severity / `on_unknown` | Remediation | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| T6-D01 | target `environment` = production | Manifest has a retained rollback artifact (`rollback_artifact_uri`) for the previous revision | error / block | Record an immutable previous artifact and config | K1; PRICING_AND_GATES §7 | Premise source checked. Manifest isn't a v1 rule scope: deployment-service gate |
| T6-D02 | production, target catalog item present | `/spec/supports_rollback` = true | warning / defer | Use a target with rollback, or document a manual plan | S2, KS1, K1 | Source checked |
| T6-D03 | both replica bounds set | `replicas_min` ≤ `replicas_max` | error / block | Fix the bounds | contract | Policy hypothesis (schema doesn't enforce) |
| T6-D04 | production, managed or self-hosted | `replicas_min` ≥ 1 | warning / defer | Keep a warm replica or accept cold starts | HF2, RP1 | Premise source checked; threshold is an owner decision |
| T6-D05 | host or provider has a documented idle deletion/scale-down or base-shutdown policy | Lifecycle acknowledged in the build | warning / defer | Show the policy and date; keep a portable artifact (#33) | #33 V16, V17; RP1 | Source checked; needs field |
| T6-D06 | self-hosted engine reachable outside a private network | Every engine route is behind authentication (not only `--api-key`) | error / review | Reverse proxy with auth, or private network only | VL1, VL2 | Source checked (vLLM v0.31.0); needs field |
| T6-D07 | production managed endpoint | Endpoint requires authentication or is private | error / block | Use Protected or Private | HF1 | Source checked (HF); needs field |
| T6-D08 | residency constrained, API or managed component | Routing profile / deployment type keeps processing in the allowed set | error / review | Choose a geographic profile or a Data Zone / regional type | BR1, AZ1 | Source checked. Evidence input to #81 D-R6, not a separate rule if D-R6 is adopted |
| T6-D09 | production | Quality run (#36) and guardrail gate (#35) **passed** for this `build_revision` | error / block | Run the gates on this revision | PRICING_AND_GATES §3–4 | Hypothesis; gate content pending #35, #36. Extends `rule.production.gates`, which checks only existence |
| T6-D10 | manifest `status` → `approved` | Every required approval scope is `approved`; none `pending` or `rejected` | error / block | Obtain approvals | contract | Policy hypothesis; required scopes are an owner decision |
| T6-D11 | `rollout_strategy` ∈ {`canary`, `blue_green`} | Target documents traffic splitting for that strategy (KServe: serverless mode only) | error / review | Use `rolling`/`manual`, or a target that splits traffic | K1, K4, KS1, S1 | Source checked; needs field |
| T6-D12 | self-hosted production | Startup and readiness checks defined | warning / defer | Add probes | K2 | Source checked |
| T6-D13 | self-hosted on Kubernetes, production | Secret encryption at rest and least-privilege RBAC evidenced | error / review | Enable encryption at rest; restrict Secret access | K3 | Source checked; severity is an owner decision |

### Contract proposals for #40

- **T6-C1** Rollout detail: `shadow` as a pre-promotion test rather than a `rollout_strategy`; canary traffic share, bake period and rollback triggers (#38 signals); target-level supported strategies instead of a single `supports_rollback` boolean.
- **T6-C2** Make `resource_estimate_id` conditional on a self-hosted or managed serving component, or allow an explicit not-applicable reference.
- **T6-C3** Deployment-scope inputs for T6-D05 to D07, D11 and D13: endpoint exposure and auth level, idle lifecycle policy, secret-store reference (reference only, never values).
- **T6-C4** Region semantics for `deployment_target.region`: geography and global routing, aligned with #81 CD-9.

## Evidence

All accessed 2026-10-17 by direct fetch; robots.txt checked for each domain. Inputs reused from other notes keep their own IDs and dates (#5 `research/T1-model-selection/evidence.md`, #9 `hosting.md`, #11 `inference-engine.md`, #33 `fine-tuned-model.md`).

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| K1 | Kubernetes, https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | 2026-10-17 | Current docs, modified 2026-07-07 (2b91a64232) | Primary documentation | Rolling defaults, rollback, `revisionHistoryLimit`, `progressDeadlineSeconds`, canary via multiple Deployments |
| K2 | Kubernetes, https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ | 2026-10-17 | Current docs, modified 2026-06-30 (751b927b5a) | Primary documentation | — |
| K3 | Kubernetes, https://kubernetes.io/docs/concepts/configuration/secret/ | 2026-10-17 | Current docs, modified 2026-07-23 (fc26d52c23) | Primary documentation | Encryption at rest is cluster configuration; not checked on any cluster |
| K4 | Kubernetes, https://kubernetes.io/docs/concepts/workloads/management/ | 2026-10-17 | Current docs, modified 2026-07-07 | Primary documentation | Canary by `track` label and replica ratio |
| KS1 | KServe, https://kserve.github.io/website/docs/model-serving/predictive-inference/rollout-strategies/canary-example | 2026-10-17 | Docs version 0.20 | Primary documentation | Serverless (Knative) mode only |
| S1 | AWS, https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails.html | 2026-10-17 | Unversioned | Primary documentation | Real-time and asynchronous endpoints only |
| S2 | AWS, https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails-blue-green.html | 2026-10-17 | Unversioned | Primary documentation | — |
| S3 | AWS, https://docs.aws.amazon.com/sagemaker/latest/dg/shadow-tests.html | 2026-10-17 | Unversioned | Primary documentation | — |
| BR1 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html | 2026-10-17 | Unversioned | Primary documentation | "Approximately 10% savings" for global profiles is a vendor pricing claim, not used here |
| AZ1 | Microsoft, https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types | 2026-10-17 | ms.date 2026-08-06 | Primary documentation | Developer type has no SLA |
| HF1 | Hugging Face, https://huggingface.co/docs/inference-endpoints/security | 2026-10-17 | main | Primary documentation | Also in #5 H2 (30-day log retention) |
| HF2 | Hugging Face, https://huggingface.co/docs/inference-endpoints/autoscaling | 2026-10-17 | main | Primary documentation | Pending-request scaling is "experimental" |
| MO1 | Modal, https://modal.com/docs/guide/secrets | 2026-10-17 | Unversioned | Primary documentation | Rotation behavior not documented on this page (unknown) |
| RP1 | Runpod, https://docs.runpod.io/serverless/endpoints/endpoint-configurations | 2026-10-17 | Unversioned | Primary documentation | Defaults (e.g. idle timeout 5 s) are console defaults, not recommendations |
| OA1 | OpenAI, https://developers.openai.com/api/reference/overview | 2026-10-17 | Unversioned | Primary documentation | — |
| VL1 | vLLM, https://github.com/vllm-project/vllm/blob/v0.31.0/docs/serving/online_serving/openai_compatible_server.md | 2026-10-17 | v0.31.0 | Primary documentation | Same source as #11 E06 |
| VL2 | vLLM, https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/security.md | 2026-10-17 | v0.31.0 | Primary documentation | Endpoint lists are for this tag |
| VL3 | vLLM, https://github.com/vllm-project/production-stack/blob/main/README.md ; release https://github.com/vllm-project/production-stack/releases/tag/vllm-stack-0.1.13 | 2026-10-17 | `main`; latest release vllm-stack-0.1.13 (2026-09-29) | Primary documentation | README is unpinned |

## Pricing and capacity

Not priced here. Deployment choices that change cost, handed to #39:
- Blue/green and SageMaker traffic shifting run both fleets during the bake period (S1, S2).
- Shadow tests duplicate inference for the shadow variant (S3).
- Runpod active workers bill while idle (RP1); scale-to-zero trades cost for cold starts (HF2).
- Kubernetes `maxSurge` (25% default) adds temporary capacity during a roll (K1).

Capacity and VRAM belong to #10.

## Recommendation and rationale

1. **Evaluate readiness per serving component** with the checklist for its mode. A hybrid build is the union, plus the cross-component data flows (DS-13, DS-15).
2. **Pin everything immutable** (model snapshot, artifact SHA, engine version, image digest, chart release), and keep the previous set as the rollback artifact. Platform history (ReplicaSets, deployment names) isn't durable enough on its own (K1; #33 V16).
3. **Proposed default, pending owner decision:** `canary` where the target splits traffic by request (SageMaker, KServe serverless); `rolling` on plain Kubernetes; `manual` re-pin for API. Shadow testing as an optional pre-promotion step when the data-flow and logging terms allow it.
4. **Proposed access baseline, pending owner decision:** no unauthenticated production endpoint (T6-D07); engine admin routes never public (T6-D06); credentials server-side only (DS-06); Kubernetes secret encryption at rest (T6-D13).
5. **Don't let `ready` mean approved.** The manifest moves past `proposed` only with the #35/#36 gates passed, a complete quote and approvals for the same revision.

## Structured artifacts

No CatalogItem proposals. A `deployment_target` item for, say, HF endpoints or Runpod Serverless could be sourced (`target_type`, `hosting_ref`, `supports_autoscale`). But its `billing_class` is unresolved: the compute is metered on the referenced `hosting_platform`. `metered` with no rate would leave cost coverage partial, and `included` needs verified classification. That decision goes to #39/#40 before any item is submitted. No DeploymentManifest is submitted: no real build, quality run or cost estimate exists (CONTRACT_MAPPING).

## Open questions and handoffs

### Owner decisions for @PUSHINGSQUARES

| # | Decision |
| --- | --- |
| OD-1 | Default rollout strategy per mode (recommendation 3), and whether shadow testing is allowed with production data |
| OD-2 | Canary share, bake period and rollback triggers. No numbers are proposed here; triggers depend on #38 signals |
| OD-3 | Rollback retention: how many previous artifacts, and for how long |
| OD-4 | Secrets baseline: required secret store, rotation, and the severity of T6-D13 |
| OD-5 | Access baseline: is a Public endpoint ever allowed in production; is T6-D06 `review` or `block` |
| OD-6 | Whether production may run with `replicas_min` = 0 (T6-D04) |
| OD-7 | Required approval scopes per environment (T6-D10) |

### Handoffs (none confirmed yet)

| To | Owner | Request |
| --- | --- | --- |
| #38 Monitoring | @appletechie, @PUSHINGSQUARES | Rollback-trigger signals (DS-26), health/readiness signals (DS-20 to 22), request-ID logging (DS-23), shadow-log retention |
| #39 Cost | @appletechie, @PUSHINGSQUARES | Rollout capacity overlap, shadow duplication, idle-worker billing (Pricing section); `billing_class` for `deployment_target` items |
| #42 Saved builds | @tynamite, @appletechie | Manifest pinned to `build_revision`; the rollback artifact as part of a saved build; dev/prod as separate builds |
| #40 Contract | @zwright8, @tynamite | T6-C1 to C4; rules T6-D01 to D13 |
| #41 Evidence | @tynamite, @PUSHINGSQUARES | "Source checked" usage; region semantics (with #81 CD-9) |
| #35 Guardrails | @appletechie, @PUSHINGSQUARES | Gate content for DS-30 / T6-D09 (pending draft) |
| #36 Evaluation | @appletechie, @PUSHINGSQUARES | Gate content for DS-29 / T6-D09, including #33 A-20 (pending draft) |
| #3, #5, #9, #11, #33 | live assignees: @tynamite, @zwright8, @Mattycodes69, @appletechie | Confirm this note consumes their #37 handoffs as stated (mode test; endpoint/region/retention; artifacts/network/region; engine build and admin-endpoint exposure; fine-tune lifecycle) |
| #13, #25, #27 | @tynamite, @zabyxc01, @CompleteDotTech, @Mattycodes69 | RAG, agent and MCP deployment inputs not yet integrated; scenarios 5–6 stay architectural |

### Unknowns

- Managed-platform health-check semantics other than HF (DS-22).
- Blue/green on plain Kubernetes: no Kubernetes primary source was checked for a Service-switch pattern.
- Secret rotation behavior on Modal, HF and Runpod.
- Account quota and capacity for every offering (DS-18).
