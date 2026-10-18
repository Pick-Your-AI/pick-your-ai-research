# T6 sibling draft reconciliation

Workstream: [#34](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/34) · Issues: #35–#39 · Owners: @PUSHINGSQUARES, @appletechie (live issue assignees)
Status: source follow-up and retained proposals; receiving acceptance pending · Checked: 2026-10-18

## Integration decision

[#121](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/121) merged at `913c9b1e974aff3b1a3a22a8ed339b99fa8e95b4`. Its five records remain the canonical partial T6 delivery. This follow-up implements the sibling author's documented sequence: merge #121 first, carry the useful differences forward, and close the overlapping PRs as superseded. The original proposals remain available at the immutable revisions below; closing their PRs does not reject their open design alternatives or complete the underlying issues.

Source checking for this reconciliation overlapped [#191](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/191), merged at `5906084bbaab8ceed446ab4d191915f84c2dc089`. Its focused notes already carry the four source findings from the comparison drafts. F01–F04 below consolidate that provenance, pin the harness guide and distinguish the current Gemini Interactions error API from generateContent-family metadata. The evaluation note also now applies the merged [T0 operator/capacity mode definition](../T0-configuration/deployment-mode.md) to each serving component; provider name and evaluator placement do not decide serving mode.

The original sibling reconciliation did not add rule IDs or change rule counts, frozen v1 files, schema enums, numeric thresholds, default retention periods, rights decisions or receiving handoff states. The counts in the [T6 summary](README.md) describe its current rule/evidence tables, including later additions identified in those tables; F01–F04 remain a separate supplement checked against five primary documents. Nothing here is a benchmark run, a configured deployment, or a consumer receipt.

## Source findings carried into the canonical records

The five primary documents supporting F01–F04 were read on 2026-10-18. Grade: primary documentation. These are documented mechanisms, not independent operational measurements. Access to documentation does not establish permission to redistribute third-party datasets or send customer content to the named services.

| ID | Origin | Primary source and version | Source-checked finding | Canonical use and remaining limit |
| --- | --- | --- | --- | --- |
| F01 | #118, privacy requirements | Traceloop, [Prompts, Completions and Embeddings](https://www.traceloop.com/docs/openllmetry/privacy/traces), unversioned documentation | OpenLLMetry captures prompts, completions and embeddings in span attributes by default. Global disabling uses `TRACELOOP_TRACE_CONTENT=false`, or `traceContent: false` in JavaScript/TypeScript. Workflow/task options and the OpenTelemetry context key `override_enable_content_tracing` can enable content selectively. | [Monitoring](monitoring.md): SG147/P1 must inspect effective instrumentation and overrides, not just the global switch. A switch setting is not evidence that exported payloads were inspected or erased. |
| F02 | #115, EVAL-01 | EleutherAI, [TemplateAPI usage guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/docs/API_guide.md), commit `d6de81643928d653435c431bae19945d41d32520` | This harness supports likelihood/MCQ API tasks on completion endpoints, not list-of-messages chat-completion endpoints. `--apply_chat_template` on a suitable completion route preserves access to the likelihoods the task requires. | [Evaluation](evaluation.md): check each task's scoring operation against the exact backend. A generative reformulation is a different protocol, not a comparable score from the original likelihood task. No universal limitation on all evaluation tools is inferred. |
| F03 | #120, Gemini candidate | Google Cloud, [Safety and content filters](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters), current page, configurable-threshold and unsafe-response sections; Google AI for Developers, [Safety settings](https://ai.google.dev/gemini-api/docs/safety-settings), last updated 2026-10-15 | The Cloud/Agent Platform documented default for `gemini-3.5-flash` and subsequent models is `OFF`: configurable harm blocking is disabled and its metadata is absent. `BLOCK_NONE` also disables blocking but returns scores. Separate non-configurable CSAM/SPII protections remain. The Gemini API page separately documents Off defaults from 2.5 onward and Interactions API blocking via error responses. | [Guardrails](guardrails.md): record the exact model, per-category settings and enforced application action. Missing configurable-filter metadata is not evidence of a safe response or evidence that every provider safety filter is disabled. [Monitoring](monitoring.md) SG16 now distinguishes generateContent-family fields from Interactions HTTP/background/streaming errors. |
| F04 | #115, fine-tune gate and T5 Q3 | Microsoft, [Safety evaluation for fine-tuning (preview)](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-safety-evaluation), last updated 2026-07-31 | The documented service evaluates training data before training and fails a job above its harm threshold. After training it separately assesses harmful model responses before deployment. Customers cannot change these predefined evaluation filters through their custom content-filter configuration; the page also offers a request process for modified thresholds. | [Evaluation](evaluation.md): keep data-screen and model-assessment outcomes separate from the build's paired base/fine-tuned regression evidence. A provider's deployable result does not establish the workload's quality or safety acceptance. No unreported screening run is recorded. |

## Preserved proposals and their disposition

The following tables retain the useful alternatives, contract gaps, and corrected review findings from every sibling. References such as `R7`, `G-R1` and `MON-02` are scoped to the identified original PR; they are not aliases for similarly named rules in the canonical records. The immutable document links retain the full candidate tables, source rows, proposed rule text, examples and original handoff lists. Historical claims about which PRs were still open remain historical; live issue and PR state governs current work.

### #113: cost normalisation

| Retained material | Disposition after #121 |
| --- | --- |
| U1–U30 meter inventory; R1 token classes, R6 provider-specific training quantities and minimum top-up, R8 modifiers, R9 currency, R11 source region | Keep these as a compact alternative derivation alongside the canonical [cost estimate](cost-estimate.md), which supplies worked scenarios and aggregation. Do not infer uncovered meters or currencies from an existing enum. The U20 heading's reference to GB is a wording error: its stated quantity is models × months, not stored bytes. |
| R2 source-preserving decimal-GB conversion | Retain the choice between note-only precision that exceeds v1's 12 decimals and a documented lossy rate conversion. The source byte definition, conversion factor and original rate must remain available. This follow-up does not adopt a new rounding policy. |
| R3 and R7 arithmetic review corrections | A fixed period uses `24 × period_days`; a vendor's 730-hour illustration is a different period, not uncertainty in a 720-hour estimate. Require whole instance counts, then multiply by devices and billable duration: one eight-GPU instance for half an hour consumes four GPU-hours. These corrections remain prerequisites for any use of the alternative method. |
| R4/R5 billing scopes, rounding and allowances | Retain scope-specific increments/minimums, allowances applied once, and distinctions between whole-request and graduated tiers. Runpod tier meaning, byte definition and sub-hour invoice rounding remain unresolved where the source did not answer them. |
| R10 and uncertainty display | Retain 12-decimal half-even arithmetic and directional display rounding as an unadopted alternative; keep low/expected/high labelled as scenario bounds. Uncovered costs remain explicit, one-off and recurring totals stay separate, and partial coverage cannot pass a budget gate. |
| D1–D14 and G1–G10 | Retain all decisions: source units/periods, tier/allowance scope, rounding, missing egress/IOPS/throughput and training meters, device semantics, region, cache writes, threshold predicates, commitments, currency, cost snapshots and handoff receipts. Contract gaps include multiple pricebook/revision references, interval fields, per-meter uncovered reasons, unknown tax, source conversion, recurrence, region defaults and modifiers. No gap is silently filled in v1. |
| D7/D12 and review routing | Region/residency remains with #41/CD-9 and T0 D-R6. Snapshot refresh is event-driven by new input/policy revisions, rights decisions or build edits; elapsed time alone does not expire evidence. Prices show their dates. #42 remains jointly owned by @tynamite and @appletechie; #64 still owns cost-validation evidence. |

### #115: evaluation protocol alternatives

| Retained material | Disposition after #121 |
| --- | --- |
| Workload/capability taxonomy, candidate inventory and R1–R15 reproducibility fields | Retain the compact taxonomy and candidate comparison alongside canonical EV-01 onward. New source checking in this follow-up is limited to F02/F04; the other candidate versions, licenses and limits retain their original access dates. |
| EVAL-02 comparison correction and #41 receipt | The recorded #41 review accepts the protocol-identity definition only. Count changed experimental controls individually, including precision, context and chat template within R5. Result uncertainty, run date and source metadata are not manipulated experimental factors. Known incomplete protocols advertised as comparable fail; undetermined evidence remains unknown. The #60 rights gate still applies. |
| P0–P6 and EVAL-03–EVAL-05 gate alternatives | Preserve compatibility, current-revision run integrity, task/workload quality, safety, performance and cost as separate checks. Missing evidence follows `on_unknown` independently of fixed severity; warning-level review findings cannot aggregate to ready. No gate is activated here. |
| EVAL-01, EVAL-06 and EVAL-10–EVAL-14 | F02 carries the route limitation. Retain the proposals for judge identity/human agreement, eligible load/cache measurements, locale coverage, RAG retrieval/grounding, repeated end-state agent tests and HELM maintenance warnings. A supported API route is not evidence that a run passed. |
| EVAL-07–EVAL-09 and the fine-tune gate | F04 adds the provider data screen. Preserve paired safety, capability retention/task gain, and leakage checks against frozen hashes. Canonical E-R44/G5 and the explicit D-20/A-20 handoff treatment already retain freeze-before-training, canary and contamination requirements; this does not acknowledge a pending recipient on their behalf. |
| Open decisions and contract gaps | Suite adoption, W-R10 metric protocol, quality/safety margins, workload language, sample counts, frozen-set ownership and runtime gate wiring remain open with #36 and its recipients. Neither structural tests nor the #41 protocol receipt settle these choices. |

### #116: deployment checklist alternatives

| Retained material | Disposition after #121 |
| --- | --- |
| DS-01–DS-33 checklist, eight synthetic scenarios and strategy matrix | Retain the compact endpoint/artifact, secrets/access, network/residency, scaling, health, rollout/rollback and gate checklist alongside canonical deployment steps S1 onward. The scenarios remain architectural examples. Platform-specific canary, shadow and rollback capabilities cannot be generalized from one offering. |
| T6-D01–T6-D13 readiness proposals | Preserve retained rollback artifacts, bounded replicas, lifecycle acknowledgement, endpoint authentication, processing region, current-revision gates, approval scopes, strategy support, probes and Kubernetes secret controls as alternatives. DS-28 excludes blocking failures/unknowns while preserving nonblocking warnings; `on_unknown=review` independently routes to review. |
| Fine-tune and runtime lifecycle findings | Canonical D-R87 already retains the classic Foundry FAQ's idle-deployment deletion with the model retained. Keep provider base-model shutdown, scale-to-zero cold start, endpoint-idle behavior, revision-history pruning, mutable runtime routes and tooling pins as dated source leads in the original document. Account capacity and rollback availability require actual evidence. |
| T6-C1–T6-C4 | Retain target-supported strategies and rollout detail; conditional/not-applicable resource estimates; endpoint exposure, lifecycle and secret-reference inputs; geography/global-routing semantics. A required v1 reference is not silently omitted by this proposal. |
| OD-1–OD-7 and receiving handoffs | Retain rollout default, canary share/bake/trigger, artifact retention, secret/access baseline, scale-to-zero policy and approval scopes as explicit decisions. #35/#36/#38/#39/#40/#41/#42 and upstream deployment recipients remain responsible for their own acceptance. |

### #118: monitoring signal alternatives

| Retained material | Disposition after #121 |
| --- | --- |
| Component signal catalog and MON-01 | Retain coverage conditional on each active component: provider, engine, actual GPU compute, RAG, agents/tools, guardrails, cost and fine-tunes. CPU-only compute does not require GPU utilization. Engine metric availability and provider account headers remain source/version-specific. |
| Content-capture warning and MON-02/MON-02b | F01 adds the missing OpenLLMetry default and override behavior. The separate restricted/error and confidential/warning candidates each retain a fixed severity; lawful basis and retention route to #35/#38 using CD-12 attestations. These candidates do not broaden the frozen production rule into universal PII redaction. |
| MON-03, MON-04 and MON-05 | Retain provenance for thresholds, explicit engine signal gaps and account-scoped rate-limit headroom. MON-04 uses pass/fail for known configuration and unknown for missing evidence. Mean or total latency cannot satisfy an unobserved TTFT percentile. |
| Q1–Q10, H1/H2 and schema gaps | Retain workload target pointers (`latency_targets`, `throughput_target`, `availability_target`), quality cadence, multi-exporter/content-capture/runtime records, managed metric exposure, RAG freshness, agent success/retry/approval, guardrail/cost derivation, logging governance and unsurveyed AMD/Apple telemetry. Canonical signal coverage helps these questions but is not a receipt that closes them. |

### #120: guardrail coverage alternatives

| Retained material | Disposition after #121 |
| --- | --- |
| C-01–C-14 control catalog and product comparisons | Retain content, injection, PII, tool permissions, human approval, secrets/exfiltration, output handling, grounding, quotas and memory-write controls. F03 carries the missing default-filter behavior with the corrected scope. Dated candidate evidence is not a configured guardrail. |
| G-R1/G-R1b and G-R2–G-R7 | Retain the seven JSON rule sketches as unadopted proposals and the separate production-only error rule. G-R1 establishes input/output target coverage only; PII-only coverage does not establish content/injection policy coverage. Unsupported multiple-selection quantification returns unknown, not a false failure. |
| G-R8–G-R11 and contract gaps | Retain memory-write screening, hosted-control data-flow coverage, quotas and qualified human review as proposals. Proposed fields include supported versus configured enforcement, modes/operator, language/modality/context limits, memory targets, grounding/output-encoding policies and workload risk flags. No new field is added to frozen v1. |
| Runtime-mode and enforcement corrections | Each shared hosted guardrail is API under T0 even when the evaluated model uses managed capacity. Signal detection remains separate from enforcement and failure behavior. An input/output coverage pass is not effectiveness evidence. |
| Q1–Q4 and receiving handoffs | Baseline versus conditional controls, failure behavior, acceptance of built-in provider filters and audit-only exceptions remain open policy questions. Effectiveness, runtime placement, logs, T4 overlap, retrieval placement, pricing, classifier sizing and terms still require the named recipients and evidence. |

## Immutable originals

The links identify the exact reviewed original text, including proposals not repeated verbatim here. SHA-256 values cover each original UTF-8 file's raw bytes. They support faithful retrieval and future comparison; they do not certify the source claims in those files.

| PR / original document | Original head | SHA-256 of original file |
| --- | --- | --- |
| [#113 cost](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/14783c517d73538fc8eb5af18530018159b161cc/research/T6-deployment-operations/cost-estimate.md) | `14783c517d73538fc8eb5af18530018159b161cc` | `9262dca56f24fe5b42def922ff0322beabe89fb703f18920615b1281a3f3ab0c` |
| [#115 evaluation](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/9f403b4252ad646fd1f75f73da2ce4fc02bb7991/research/T6-deployment-operations/evaluation.md) | `9f403b4252ad646fd1f75f73da2ce4fc02bb7991` | `18d4b23e5635eecdc5989cb94eae3396e2a0f461283583497a3888251b117409` |
| [#116 deployment](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/9a5efb79b6bbb9fd19f87fcbd9f59367a0c35b28/research/T6-deployment-operations/deployment.md) | `9a5efb79b6bbb9fd19f87fcbd9f59367a0c35b28` | `1382b310fd02ac8be2c1192724d7a0204cbaeb50d0269c5f266a571eade49a10` |
| [#118 monitoring](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/56a25ed3ccc03f2a774f824f3ce4c2326f6fc695/research/T6-deployment-operations/monitoring.md) | `56a25ed3ccc03f2a774f824f3ce4c2326f6fc695` | `a05a1abffe9d2aec1ba211d3d768964727474ed7c296332e0e50215322a57180` |
| [#120 guardrails](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/f4721c123cbba706c46dc2f458f33f38f0f69398/research/T6-deployment-operations/guardrails.md) | `f4721c123cbba706c46dc2f458f33f38f0f69398` | `a48ca045a956e38fce37d7b5208aa8a3434f6146f3f47d1f047fe6392bd1ba4e` |

## Acceptance boundary

The supersession decision resolves competing PR destinations. The issue deliverables and receiving handoffs remain open wherever the canonical record says evidence, measurements, rights, schema versioning, configured behavior or a receiving decision is pending. A future implementation must select and review one policy for each unresolved alternative; it must not load both sets of proposals as cumulative rules. Existing authors, original revisions and review corrections remain traceable above.

## Subsequent integration into the component tables

The 2026-10-18 follow-up places F02/F04 into candidate rows E-R87/E-R88 with evidence rows E-N1001/E-N1002, F03 into G-R35, and F01 into SG147 with evidence row M-L31. They retain the source scope and receiving boundaries above. The [cost record W5](cost-estimate.md#w5-fine-tuning-a-one-off-job-and-continuing-hosting) and its calculator add provider-specific training quantities, a model-specific minimum top-up, and separate recurring hosting. Those figures are synthetic arithmetic illustrations with dated public rates, not provider bills or completed training. This integration does not install a ruleset or settle the retained policy alternatives.
