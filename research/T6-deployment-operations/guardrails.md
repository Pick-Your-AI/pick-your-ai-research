# T6: Guardrails

Issue: #35 · Contract: 1.0.0 · Kinds: `guardrail`
Status: draft · Last researched: 2026-10-17

Evidence wording follows the #41 interim definition applied in the [PR #75 review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75): **source checked** means the claim was confirmed against the cited primary source on its access date; **verified** means independently reproduced. Nothing in this note is verified. No guardrail or framework below eliminates risk; OWASP states it "is unclear if there are fool-proof methods of prevention for prompt injection" (E15).

## User decision

Which safety, security and policy controls should this build include, where are they enforced, and what does the builder say when one is missing?

The note covers three deployment modes, using the per-component mode test proposed in #3 (PR #81, pending):

- **API:** a provider-run model on shared capacity. Provider-side filters may exist, but the build does not operate them.
- **Managed:** provider-run guardrail services, called by the build. Examples: Bedrock Guardrails, Azure AI Content Safety, provider-run moderation endpoints.
- **Self-hosted:** guardrail libraries and classifier models that the user runs.

A guardrail can run in a different mode from the model it protects. For example, a self-hosted model can be screened by a hosted moderation API. That adds a data flow to a provider (see handoff to #3).

## Scope and inputs

- **In scope:** input and output controls; tool permissions and approvals; data boundaries and prompt-injection mitigations for retrieval and tools; human review; policy configuration; failure behaviour; differences by mode.
- **Out of scope:** measuring how well guardrails work (#36).
- **Inputs read, all pending and not accepted by their owners:**
  - T4 tools, PR #70 at `be96c31ffcce`: risk classes, approval defaults, and rules `rule.t4.tool.*`.
  - T4 MCP, PR #71 at `fc28a929857d`: trust levels, security findings for #35, and rules `rule.t4.mcp.*`.
  - T4 memory, PR #72 at `e76806679c32`: memory-write controls routed to #35.
  - T4 agent framework, PR #69 at `94826907229f`.
  - T0 deployment mode, PR #81 at `e2bcc35b19de`: the mode test and D-R6 residency.
  - T1 [handoffs](../T1-model-selection/handoffs.md), row #6 -> #35: terms restrictions; no safety approval implied.
  - T5 [fine-tuned model](../T5-training-fine-tuning/fine-tuned-model.md): the evidence that fine-tuning degrades safety (its Q1 and Q3).

## Control catalog

Control types. The "v1 mapping" column shows which `spec_guardrail` enums can express each control. "Note only" means v1 cannot express it.

| Control ID | Category | Applies to (component) | When it applies | v1 mapping (`targets` / `policies` / `enforcement`) | Evidence |
| --- | --- | --- | --- | --- | --- |
| C-01 | Input content moderation | `model` | Every build with a model | `input` / `content`, `toxicity` / `block`, `audit` | E01–E06, E09, E11, E12 |
| C-02 | Output content moderation | `model`, `fine_tuned_model` | Every build with a model; stronger case when fine-tuned | `output` / `content`, `toxicity` / `block`, `redact` | E01–E06, E09, T5 Q1 |
| C-03 | Direct prompt-attack (jailbreak) detection | `model` | Every build that takes user input | `input` / `prompt_injection` / `block` | E02, E04, E08, E10, E15 |
| C-04 | Indirect-injection screening of retrieved content | `rag_pipeline`, `knowledge_base` | T3 active | `retrieval` / `prompt_injection` / `block` | E04, E08, E11, E15 |
| C-05 | Tool-result screening and untrusted-content segregation | `tool`, `mcp_server` | T4 tools or MCP active | `tool` / `prompt_injection` / `block` | E04, E08, E15; PR #71 |
| C-06 | PII detection and redaction | `model`, `memory_store`, `knowledge_base` | Confidential or restricted data | `input`, `output` / `pii` / `redact`, `block` | E02, E06, E11, E13, E19 |
| C-07 | Tool permissions, allow-lists and least privilege | `tool`, `mcp_server`, `agent_framework` | Any tool; error when a tool mutates (baseline) | `tool` / `tool_permissions` / `block` | E08, E15, E17; PR #70 |
| C-08 | Human approval for high-impact actions | `tool`, `mcp_server` | High-impact or irreversible tools | `tool` / `tool_permissions` / `escalate` | E15, E17; PR #70 T4-B5 |
| C-09 | Secrets and exfiltration controls | `tool`, `mcp_server`, `integration` | Networked tools with private data | `tool`, `output` / `secrets`, `data_exfiltration` / `block` | E08; PR #70 T4-B10 |
| C-10 | Output handling: encoding and validating structured output | application, `tool` inputs | Output rendered or passed downstream | Note only; no policy enum | E12, E16 |
| C-11 | Grounding and hallucination checks | `rag_pipeline`, `model` | RAG answers | Note only; no policy enum | E02, E03 |
| C-12 | Rate limits, quotas and timeouts | `model_provider`, `deployment_target` | Every build | Note only. Spend is covered by `rule.budget.monthly.cap` | E08, E18 |
| C-13 | Qualified human in the loop for high-risk advice and decisions | `workload` | High-risk use cases | Note only; no workload field | E07 |
| C-14 | Screening memory writes for poisoning and PII | `memory_store` | T4 memory active | Note only; no `memory` target | E19; PR #72 |

### Candidate products (source checked, 2026-10-17)

| Candidate | Mode | Controls | Configuration | Failure behaviour (as documented) | Version / licence / access | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| OpenAI Moderation | API (standalone endpoint, or inline with Responses or Chat) | C-01, C-02. Some categories are text only; no audio | `omni-moderation-latest`. The application sets thresholds | Returns flags and scores; it does not block. OpenAI: "Treat moderation scores as signals ... not as an automatic blocking decision." The moderation result can be an error. Tool names and schemas are not covered | "Free to use"; requires an API account | E01 |
| Amazon Bedrock Guardrails | Managed. Can be called with Bedrock models, or through `ApplyGuardrail` without invoking a model | C-01–C-03 (content filters include Prompt Attack), denied topics, word filters, C-06 (block or mask, plus regex), C-11 (contextual grounding), Automated Reasoning | Strength per category; versioned guardrails; Classic and Standard tiers; input tagging to evaluate only part of a prompt (SDK only) | Configurable blocked message; block or mask per filter | AWS account; regions and models listed separately (not fetched); page undated | E02 |
| Azure AI Content Safety, including Prompt Shields | Managed (standalone API); also built into Foundry deployments | C-01, C-02 (four categories, severity levels), C-03 (user prompt attacks), C-04 and C-05 (document attacks; tool-response scan in preview), C-11 (groundedness), protected material | Foundry: user-prompt shield on by default, document-attack shield off by default. Default filters apply to Foundry models; turning them off needs approval | In the API, "the application decides" whether to allow or block. In Foundry, blocking happens before the model when enabled. Prompt Shields do not judge harm or grounding | Last updated 2026-10-01 and 2026-10-14; mostly trained on English; region-limited | E03–E05 |
| Google Gemini safety filters (Vertex / Agent Platform) | API, managed | C-01, C-02 (four harm categories); fixed CSAM and SPII filters; citation filter | `SafetySetting` threshold per category, by SEVERITY or PROBABILITY | `OFF` is the default for `gemini-3.5-flash` and later models, so configurable harm filtering is off unless configured; non-configurable CSAM/SPII protections remain. A block stops token generation and returns a reason code | Last updated 2026-10-15 | E06 |
| Anthropic Claude | API | Built-in real-time safeguards (not configurable). Documented patterns for C-03–C-05: a Haiku harmlessness screen, untrusted content only in `tool_result`, least privilege | Prompting and screening done by the application | A block is not by itself a policy violation. The screening model can itself refuse, which leaves no verdict to read | Usage Policy shows "Effective November 12, 2026" (later than the access date; the version in force today was not read) | E07, E08 |
| Meta Llama Guard 4 (12B) | Self-hosted classifier | C-01, C-02 for text and images; 14 hazards from the MLCommons taxonomy, including S14 Code Interpreter Abuse | Classifies prompts and responses; the host enforces | The card says it "may be susceptible to adversarial attacks or prompt injection" and points to Prompt Guard 2 for that | Card at PurpleLlama `cd9fe6579234` (2025-04-29). Llama 4 Community License, effective 2025-04-05. HF repo is gated (manual approval); weights were not accessed | E09 |
| Meta Llama Prompt Guard 2 (86M) | Self-hosted classifier | C-03, C-04, C-05 | Context window of 512 tokens; longer inputs must be split into segments | No separate injection sub-label | Same commit and licence as Llama Guard 4; gated | E10 |
| NVIDIA NeMo Guardrails | Self-hosted library or server | Input, dialog, retrieval, execution (tool) and output rails, covering C-01–C-06 | `config.yml` plus Colang. "A configuration without any configured rails will essentially forward the requests to the LLM" | A rail rejects or alters content. Built-in rails "may or may not be suitable for a given production use case." Third-party endpoints carry their own terms | v0.24.1 (2026-09-16); Apache-2.0 (LICENSE.md; the GitHub API reports NOASSERTION); repo moved to `NVIDIA-NeMo/Guardrails` | E11 |
| Guardrails AI | Self-hosted library or server | Input and output guards; Hub validators; C-10 structured output | Validators per guard | Eight `OnFailAction` values: `reask`, `fix`, `filter`, `refrain`, `noop`, `exception`, `fix_reask`, `custom`. Hosted remote inference was discontinued (planned cutoff 2026-08-25) | v0.11.0 (2026-08-14); Apache-2.0 | E12 |
| Microsoft Presidio | Self-hosted library | C-06 for text, images and structured data | Detectors and anonymizers | "No guarantee that Presidio will find all sensitive information" | 2.2.364 (2026-07-22); MIT; repo moved to `data-privacy-stack/presidio` | E13 |

### Controls by deployment mode

| Control | API | Managed | Self-hosted |
| --- | --- | --- | --- |
| C-01, C-02 | The provider's built-in filters vary. Azure filters are on by default; Gemini 3.5 and later default to `OFF`; Anthropic's safeguards cannot be configured; OpenAI returns signals only. **Do not count them as a configured guardrail unless a guardrail selection represents them with settings** | Bedrock Guardrails or Azure Content Safety, called by the build | Llama Guard 4, NeMo rails or Guardrails AI validators; the user operates and sizes them (GPU sizing goes to #10) |
| C-03–C-05 | Application patterns only (E08) | Prompt Shields (document attacks must be enabled); Bedrock Prompt Attack filter | Prompt Guard 2 (segments of 512 tokens); NeMo retrieval and execution rails |
| C-06 | Vertex has a fixed SPII filter on responses | Bedrock sensitive-information filters | Presidio; NeMo input and output masking |
| C-07–C-09, C-14 | Always the build's responsibility (agent framework, credentials, approval UX). See T4 | Same | Same |
| C-12 | Provider rate limits exist (T4 B10 and others); the application still needs its own quotas | Same | The user configures everything (gateway or engine) |

A hosted guardrail used from a self-hosted or API build sends prompts and outputs to that provider. The guardrail must therefore appear in the build's data flows for residency (D-R6) and logging (#38).

## Comparison fields

| Field | Type and unit | v1 location | Evidence requirement |
| --- | --- | --- | --- |
| `control id` | string, `C-nn` (note) | Note only; rule IDs `rule.t6.guardrail.*` | — |
| `category` | enum | `/spec/targets` (input, output, retrieval, tool, training) and `/spec/policies` (pii, prompt_injection, toxicity, data_exfiltration, content, tool_permissions, secrets) | Primary documentation naming the detection category |
| `applies to (component)` | canonical kind list | `affected_kinds` in rules | Rule proposal |
| `deployment modes` | enum list: api, managed, self_hosted | **Missing from `spec_guardrail`** (proposed for #40) | Primary documentation for how the product is offered |
| `configuration` | Selection settings | `settings_guardrail.enforcement` and `failure_action`; thresholds and categories missing | Primary documentation for each setting |
| `failure behaviour` | enum: fail_closed, fail_open | `settings_guardrail.failure_action` | Owner decision (Q1, Q2) |
| `enforcement` | enum: audit, block, redact, escalate | `/spec/enforcement` (one value) | Primary documentation; see the contract gap below |
| `source` | URL, access date, version | `provenance[]` | Primary source with access date |
| Languages and modalities | enum lists | Missing | Primary documentation; effectiveness goes to #36 |

**Contract gaps (to #40):**

- `spec_guardrail.enforcement` holds one value. Products expose an action per filter (Bedrock: block or mask), several fail actions (eight in Guardrails AI), or none at all (OpenAI, the Azure API, and Llama Guard return signals and the host enforces). A per-product value would be a configuration choice presented as a fact. Proposal: `supported_enforcement[]` in the spec; keep the chosen value in `settings_guardrail.enforcement`.
- Missing from the spec: `deployment_modes`, `languages`, `modalities`, `context_limit_tokens` (Prompt Guard 2: 512), and an `operated_by` field (provider or self).
- `targets` lacks `memory` (needed for C-14).
- `policies` lacks `grounding` (C-11) and `output_encoding` (C-10).
- No metric or field for rate limits or quotas (C-12), and no workload flag for high-risk decisions (C-13).
- `role: "primary"` references can check only one guardrail. A build with separate input and output guardrails returns `unknown` (`unsupported_selection_quantifier`, `on_unknown: review`) until coverage can be quantified across selections; it must not receive a false `fail`. This is the same per-selection quantifier gap that PR #70 raised.

## Compatibility proposals

All rules are **hypotheses**: builder policy resting on premises that were source checked. Outcome and severity are separate fields. Except for the separate production-only G-R1b candidate below, every rule uses `severity: warning` and `on_unknown: review`, so missing catalog data gives `unknown`, never `pass`. A missing guardrail selection gives `fail`. The baseline rules stay in force and are not duplicated:

- `rule.tool.mutation.guardrails` (error);
- `rule.production.gates` (error: production needs a guardrail);
- `rule.knowledge.restricted.acl`;
- `rule.training.dataset.governance`.

T4 rules `rule.t4.tool.guardrail.targets`, `rule.t4.tool.guardrail.enforcement`, `rule.t4.mcp.untrusted.guardrails` and `rule.t4.mcp.mutation.guardrails` refine the tool case. They remain owned by T4.

| Rule | Applies when | Asserts | Premise evidence | Synthetic pass / fail / unknown or skipped |
| --- | --- | --- | --- | --- |
| G-R1 `rule.t6.guardrail.model.io` | A model is selected | A guardrail exists and its targets include `input` and `output` | E01–E06 (provider filters are optional, off by default, or signal-only) | Fixture: pass · guardrail removed: fail · catalog item missing: unknown |
| G-R1b `rule.t6.guardrail.model.io.production` | A model is selected and deployment is production | Same input/output coverage assertion as G-R1; fixed severity `error`, `on_unknown: review`; unsupported multiple-selection quantification gives unknown | Policy proposal, requires #35/#40 acceptance | pass / fail / unknown as G-R1 |
| G-R2 `rule.t6.guardrail.retrieval.injection` | `rag_pipeline` or `knowledge_base` selected | Targets include `retrieval`; policies include `prompt_injection` | E04 (document attacks off by default), E11, E15 | pass / fail (output-only guardrail) / unknown |
| G-R3 `rule.t6.guardrail.tool.injection` | `tool` or `mcp_server` selected | Targets include `tool`; policies include `prompt_injection` | E08, E15; PR #71 ("treat tool output as untrusted regardless of `trust_level`") | pass / fail / unknown |
| G-R4 `rule.t6.guardrail.data.pii` | `data_classification` is confidential or restricted | Policies include `pii`; targets include `output` | E02, E13, E19 | Restricted: pass · internal fixture: skipped |
| G-R5 `rule.t6.guardrail.finetuned.output` | `fine_tuned_model` selected | Targets include `output`; policies include `content` or `toxicity` | T5 Q1 (independent measurement): 10 adversarial examples raised GPT-3.5 Turbo harmfulness from 1.8% to 88.8%. T5 Q3 (Microsoft) | Fixture: fail (its policies lack content and toxicity) · output and content guardrail: pass |
| G-R6 `rule.t6.guardrail.production.enforcing` | A guardrail is selected and the deployment target is `production` | Effective enforcement is block, redact or escalate. The selection setting overrides the catalog value (the precedence PR #70 asked for) | E01, E04 (signal-only modes need application enforcement) | `audit` setting: fail · no setting with catalog `block`: pass |
| G-R7 `rule.t6.guardrail.failure.declared` | Same as G-R6 | `settings_guardrail.failure_action` is declared, either value | E01 (a moderation step can return an error) | Declared: pass · omitted: fail |

Each rule has the same remaining fields:

- **Dependency edges:** guardrail ↔ the named kind.
- **Consumers:** #36, #37, #38, and the T4 owners.
- **Version impact:** cross-selection quantification remains a #40 gap; use unknown until supported. No frozen schema changes.
- **Remediation:** select or configure the missing control, or record an exception that an owner has approved.

Validation: the JSON below is valid against `ruleset.schema.json`. It was evaluated with `contracts/v1/reference/evaluate.py` against `contracts/v1/examples/` and against five synthetic variants built in a temporary directory and not committed. The outcomes match the table above. All examples are synthetic.

```json
{"id":"rule.t6.guardrail.model.io","severity":"warning","applies_when":{"op":"exists","value":{"ref":{"scope":"selection","kind":"model","role":"primary","pointer":"/id"}}},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/targets"}},"right":{"literal":"input"}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/targets"}},"right":{"literal":"output"}}]},"on_unknown":"review","message":"No guardrail screens both model input and model output.","remediation":"Select a guardrail whose targets include input and output, or record why provider-side controls are accepted.","affected_kinds":["model","guardrail"],"owner":"t6-guardrails"}
{"id":"rule.t6.guardrail.retrieval.injection","severity":"warning","applies_when":{"op":"any","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"rag_pipeline","role":"primary","pointer":"/id"}}},{"op":"exists","value":{"ref":{"scope":"selection","kind":"knowledge_base","role":"primary","pointer":"/id"}}}]},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/targets"}},"right":{"literal":"retrieval"}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/policies"}},"right":{"literal":"prompt_injection"}}]},"on_unknown":"review","message":"Retrieved content reaches the model without a prompt-injection guardrail on retrieval.","remediation":"Select a guardrail that targets retrieval with a prompt_injection policy.","affected_kinds":["rag_pipeline","knowledge_base","guardrail"],"owner":"t6-guardrails"}
{"id":"rule.t6.guardrail.tool.injection","severity":"warning","applies_when":{"op":"any","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"exists","value":{"ref":{"scope":"selection","kind":"mcp_server","role":"primary","pointer":"/id"}}}]},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/targets"}},"right":{"literal":"tool"}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/policies"}},"right":{"literal":"prompt_injection"}}]},"on_unknown":"review","message":"Tool or MCP results reach the model without a prompt-injection guardrail on tool traffic.","remediation":"Select a guardrail that targets tool with a prompt_injection policy; treat every tool result as untrusted.","affected_kinds":["tool","mcp_server","guardrail"],"owner":"t6-guardrails"}
{"id":"rule.t6.guardrail.data.pii","severity":"warning","applies_when":{"op":"in","left":{"ref":{"scope":"build","pointer":"/objectives/data_classification"}},"right":{"literal":["confidential","restricted"]}},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/policies"}},"right":{"literal":"pii"}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/targets"}},"right":{"literal":"output"}}]},"on_unknown":"review","message":"Confidential or restricted data is in scope but no guardrail applies a PII policy to output.","remediation":"Select a guardrail with a pii policy that targets output (and input where prompts may carry personal data).","affected_kinds":["workload","guardrail"],"owner":"t6-guardrails"}
{"id":"rule.t6.guardrail.finetuned.output","severity":"warning","applies_when":{"op":"exists","value":{"ref":{"scope":"selection","kind":"fine_tuned_model","role":"primary","pointer":"/id"}}},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/targets"}},"right":{"literal":"output"}},{"op":"any","args":[{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/policies"}},"right":{"literal":"content"}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/policies"}},"right":{"literal":"toxicity"}}]}]},"on_unknown":"review","message":"A fine-tuned model is served without an output content guardrail.","remediation":"Select an output guardrail with a content or toxicity policy; fine-tuning can weaken the base model's safety behaviour.","affected_kinds":["fine_tuned_model","guardrail"],"owner":"t6-guardrails"}
{"id":"rule.t6.guardrail.production.enforcing","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"selection","kind":"deployment_target","role":"primary","pointer":"/settings/environment"}},"right":{"literal":"production"}}]},"assert":{"op":"any","args":[{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/settings/enforcement"}}},{"op":"in","left":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/settings/enforcement"}},"right":{"literal":["block","redact","escalate"]}}]},{"op":"all","args":[{"op":"not","arg":{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/settings/enforcement"}}}},{"op":"in","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/enforcement"}},"right":{"literal":["block","redact","escalate"]}}]}]},"on_unknown":"review","message":"The production guardrail only audits; it does not block, redact or escalate.","remediation":"Set guardrail enforcement to block, redact or escalate, or record an owner-approved audit-only exception.","affected_kinds":["guardrail","deployment_target"],"owner":"t6-guardrails"}
{"id":"rule.t6.guardrail.failure.declared","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"selection","kind":"deployment_target","role":"primary","pointer":"/settings/environment"}},"right":{"literal":"production"}}]},"assert":{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/settings/failure_action"}}},"on_unknown":"review","message":"The production guardrail has no declared failure behaviour.","remediation":"Set failure_action to fail_closed or fail_open explicitly.","affected_kinds":["guardrail","deployment_target"],"owner":"t6-guardrails"}
```

**Proposals that need a #40 change (no JSON):**

- **G-R8 Memory-write screening:** `memory_store` selected → a guardrail targets `memory` with `prompt_injection` and `pii` (C-14; PR #72).
- **G-R9 Hosted guardrail data flow:** when the guardrail's operator is a provider and the data is restricted, D-R6 residency must include the guardrail (#3).
- **G-R10 Rate limits and quotas:** a requests-per-minute limit is declared for every user-facing build (C-12; E18).
- **G-R11 High-risk human in the loop:** a workload flag marks high-risk decisions → a qualified reviewer step is required (C-13; E07 lists this as a required control for that use).

## Builder display for a missing control

| Outcome | Shown as | Action |
| --- | --- | --- |
| `fail` | "Missing control" plus the message, at the rule's severity | The remediation, with the list of products that can supply the control (from the candidate table) |
| `unknown` | "Not confirmed: needs review"; never shown as satisfied | Fill the missing catalog field or record a reviewer decision |
| `skipped` | Hidden by default ("not applicable: no RAG, tools, ...") | — |
| `pass` | "Configured (documentation checked, not verified)" | Effectiveness is measured by #36 |

## Pricing and capacity

Not priced. Bedrock Guardrails, Azure Content Safety and Google filters have usage pricing that was not researched here (handoff to #39). OpenAI states that moderation is "free to use" (E01); no Pricebook was created for it, because a zero rate needs #39's semantics. Self-hosted classifiers need GPU capacity: Llama Guard 4 "can be run on a single GPU" (vendor claim, E09); sizing goes to #10.

## Recommendation and rationale

1. **Baseline for every build:** C-01, C-02, C-03 and C-12. Provider-side defaults are inconsistent: on by default (Azure), off by default (Gemini 3.5 and later), not configurable (Anthropic), or signal-only (OpenAI). The build should therefore declare its own input and output control, or explicitly accept the provider's.
2. **Conditional controls:**
   - C-04 when T3 is active;
   - C-05, C-07, C-08 and C-09 when T4 is active;
   - C-14 when memory is active;
   - C-06 for confidential or restricted data;
   - stronger output control (G-R5) for fine-tuned models;
   - C-13 for high-risk use.
3. **Separate the detector from enforcement.** Most candidates only classify; the build must choose block, redact, escalate or audit, and fail-open or fail-closed.
4. **Layer the controls.** No single product covers all fourteen. Prompt-injection defences reduce risk but do not remove it (E15).

## Structured artifacts

No CatalogItem proposals. Required `spec_guardrail.enforcement` is a single value that most products do not fix (see the contract gaps). Hosted products also need `billing_class` facts that were not researched. Rules are proposals in this note for #40 review; no ruleset file is added.

## Evidence

All accessed 2026-10-17. Grade: primary documentation unless noted. Every fetch respected robots.txt. The OpenAI usage policies page returned 403 and was not used. The Hugging Face cards for the gated Llama models were not fetched; the GitHub copies were used instead.

| ID | Publisher and URL | Version / date | Limitations / reuse |
| --- | --- | --- | --- |
| E01 | OpenAI, https://developers.openai.com/api/docs/guides/moderation | `omni-moderation-latest`; page undated | Account required |
| E02 | AWS, https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html | Undated | Region and model pages not fetched |
| E03 | Microsoft, https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview | Updated 2026-10-01 | Some models English only |
| E04 | Microsoft, https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection | Updated 2026-10-14 | Tool-response scan is in preview |
| E05 | Microsoft, https://learn.microsoft.com/en-us/azure/foundry-classic/foundry-models/concepts/content-filter (redirected from `ai-foundry/openai/concepts/content-filter`) | Updated 2026-08-04 | "Classic" Foundry docs |
| E06 | Google Cloud, https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters (redirected from the Vertex URL) | Updated 2026-10-15 | — |
| E07 | Anthropic, https://www.anthropic.com/legal/aup | "Effective November 12, 2026" | The version in force on the access date was not read |
| E08 | Anthropic, https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks | Undated | Vendor guidance |
| E09 | Meta, https://github.com/meta-llama/PurpleLlama/blob/cd9fe6579234/Llama-Guard4/12B/MODEL_CARD.md and `LICENSE` | Commit 2025-04-29; Llama 4 Community License, effective 2025-04-05 | Performance figures are vendor claims (not used) |
| E10 | Meta, https://github.com/meta-llama/PurpleLlama/blob/cd9fe6579234/Llama-Prompt-Guard-2/86M/MODEL_CARD.md | Same | Benchmark figures are vendor claims (not used) |
| E11 | NVIDIA, https://github.com/NVIDIA-NeMo/Guardrails (README at `af242f0b4757`, LICENSE.md) | v0.24.1, 2026-09-16; Apache-2.0 | — |
| E12 | Guardrails AI, https://github.com/guardrails-ai/guardrails (README at `06d0ff2c5f9b`; `guardrails/types/on_fail.py`) | v0.11.0, 2026-08-14; Apache-2.0 | Hub validators not reviewed |
| E13 | Presidio, https://github.com/data-privacy-stack/presidio | 2.2.364, 2026-07-22; MIT | — |
| E14 | OWASP, https://genai.owasp.org/llm-top-10/ | 2025 list | CC BY-SA 4.0 |
| E15 | OWASP, https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | LLM01:2025 | CC BY-SA 4.0 |
| E16 | OWASP, https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/ | LLM05:2025 | CC BY-SA 4.0 |
| E17 | OWASP, https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ | LLM06:2025 | CC BY-SA 4.0 |
| E18 | OWASP, https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/ | LLM10:2025 | CC BY-SA 4.0 |
| E19 | OWASP, https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/ | LLM02:2025 | CC BY-SA 4.0 |
| E20 | NIST, https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence (DOI 10.6028/NIST.AI.600-1) | Published 2024-07-26; record updated 2026-04-08 | Only the record page was read; the PDF was not, and no control claim relies on it |

## Open questions and handoffs

**Owner decisions for @PUSHINGSQUARES:**

| # | Decision |
| --- | --- |
| Q1 | Which controls are baseline and which conditional? Review separate production-only G-R1b (`error`); G-R1 remains fixed `warning`. |
| Q2 | Default failure behaviour: fail-closed for tool and retrieval guards, but fail-open with audit for chat moderation? Or fail-closed everywhere? |
| Q3 | May a provider's built-in filter satisfy G-R1? If so, what evidence and settings must the selection record? |
| Q4 | Should audit-only enforcement be allowed in production with an approved exception (G-R6)? |

**Handoffs:**

| Handoff | Issue · owner | Status |
| --- | --- | --- |
| Measure guardrail effectiveness: false-positive and recall rates by language and modality, regression after fine-tuning, red-team injection suites | #36 · @appletechie, @PUSHINGSQUARES | Pending |
| Runtime failure behaviour, provider endpoints, region of hosted guardrails | #37 · @appletechie, @PUSHINGSQUARES | Pending |
| Guardrail trigger and detection events; logging boundary (no raw PII in logs) | #38 · @appletechie, @PUSHINGSQUARES | Pending |
| Contract gaps above; review of G-R1 to G-R11 | #40 · @zwright8, @tynamite | Pending |
| Evidence grades and the checked-versus-verified labels | #41 · @tynamite, @PUSHINGSQUARES | Pending |
| G-R3 overlap with the T4 rules; approval UX for C-08; memory controls C-14 | #26, #27, #28 · @CompleteDotTech | Pending (PRs #70–#72 unmerged) |
| C-04 retrieval guard placement | #16 · @zabyxc01 | Pending |
| Include hosted guardrails in the D-R6 data flows | #3 · @tynamite (PR #81) | Pending |
| Guardrail pricing (Bedrock, Azure, Google) | #39 · @appletechie, @PUSHINGSQUARES | Pending |
| Classifier GPU sizing (Llama Guard 4) | #10 · @Mattycodes69 | Pending |
| Terms restrictions (row #6 -> #35) | #6 · @zwright8 | Pending; no claim here depends on it |

### Review clarification (2026-10-17)

G-R1 establishes input/output target coverage only. A PII-only guardrail may satisfy it; that does not establish content or prompt-injection baseline coverage, which needs separate policy assertions and #35/#40 acceptance. Evaluate separate input and output controls jointly when supported, otherwise return unknown with the quantifier-gap reason above.

Mode is assigned to each guardrail runtime under merged #81: provider-operated shared Bedrock Guardrails, Azure AI Content Safety and moderation endpoints are `api`, including when a managed model invokes them. `managed` requires dedicated/reserved capacity for that component. The model deployment mode is not inherited by its guardrail. Mode columns describing the caller are applicability, not guardrail mode.

The #121-first integration order and pending owner decisions are unchanged.
