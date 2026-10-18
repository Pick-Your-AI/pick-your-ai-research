# MR-03: Test direct stack-builder substitutes

Issue: [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66). Assignees: @tynamite, @itisSomeone; coordinator @CompleteDotTech. Status: common scenario recorded on two device-first substitutes (2026-10-17); Flocci contradiction, bookmark and navigation test completed as a guest (2026-10-18). Evidence and scoped receiving decisions are accepted in the [2026-10-18 review](#receiving-and-research-acceptance-review-2026-10-18); final amendment validation, review and delivery remain the completion gate. The completed guest observation supersedes the earlier sign-in gate for this test only.

## Question
Do Flocci and other guided builders already satisfy the proposed MVP?

## Starting evidence
[competitors.json](competitors.json). This note is not a new canonical component catalog or a completed measurement.

## Protocol and acceptance
- [x] Run a common public non-sensitive scenario (Flocci 2026-10-16; ModelFit and CanIRun.ai 2026-10-17)
- [x] Check constraint handling and explanation quality (Flocci guest result, 2026-10-18)
- [x] Inspect saved or exported configuration claims (Flocci bookmark and return-navigation test, 2026-10-18; earlier ModelFit and CanIRun.ai observations)
- [x] Record counterexamples and pivot recommendation (bounded narrowing accepted in the dated receiving review below)
- [x] Record exact source/version, conditions, failures and confidence.
- [x] Obtain affected-owner review and accepted handoff (actual delegated project-engineering dispositions below; no absent-assignee response inferred).

## Next action
Deliver the reviewed acceptance amendment with current checks, then reconcile the literal #66 checklist and let #50/#57/#58 assess their own conclusions against this accepted input. The [actual #2/#40/#42 receiving receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66#issuecomment-6248861238) supplies the bounded decisions; automation alone does not. The historical sections retain their original access observations; they do not describe the latest completed test.

## Result
Two dated Flocci outputs are recorded: the original common-scenario workflow and the 2026-10-18 contradictory-constraints response. The latter explicitly identified the conflict, proposed a local alternative, and exposed individual tool bookmarks. A reusable configuration was not obtained through the tested guest flow. No deployed-system validation is claimed. No raw customer data, benchmark artifact or paid API output was collected. Consumers: #2, #40, #42.

## Initial result (2026-10-16, historical)
A completed free Stack Builder test returned an ordered local PDF RAG workflow for Windows, 16 GB RAM and no GPU. It acknowledged memory/latency uncertainty and suggested reproducibility steps. The visible result named Docling, txtai, Chroma, Ollama, Gemma and Open WebUI. This verifies generated workflow advice, not that the combination runs, preserves privacy or produces an executable export.

Remaining: test contradictory constraints, verify actual deployment and export behavior, and obtain owner review. Second-substitute comparisons were run on 2026-10-17 (below).

## Historical CanIRun.ai intake (2026-10-16)

At intake, [CanIRun.ai](competitors/canirun-ai.md) was queued alongside ModelFit and llmfit with directory inspection only. The dated 2026-10-17 observations below supersede that initial untested state for ModelFit and CanIRun.ai. They do not complete the Flocci contradictory-constraints/export test or establish deployed-system behavior. PR #125 delivered those observations to main (`6b14b7f`, merge state checked 2026-10-18); the acceptance gates remain unchanged.

## 2026-10-17 tests (@tynamite)

Method: a browser session with no account, no personal data and nothing installed or deployed. The common scenario is unchanged: answer questions over local PDFs on a Windows laptop with 16 GB RAM and no discrete GPU. The contradictory-constraints scenario prepared for Flocci was: fully offline (no internet), must use a hosted API model, 16 GB RAM, no GPU, zero budget. Observations are what the pages showed at access, not verified product behaviour.

| Tool and page | Scenario | Observation | Evidence class | Confidence |
| --- | --- | --- | --- | --- |
| Flocci Ask (<https://aitools.flocci.in/ask>) and Stack Builder (<https://aitools.flocci.in/stack>) | Contradictory constraints | **Not run.** Both pages showed "That's today's free answers used" / "That's today's free stacks used. Sign in for more" before any input. The site states that the Ask assistant and Stack Builder are priced in Flocci credits, while browsing and comparing need no account. | Observed behaviour | High for the access gate; nothing about constraint handling |
| ModelFit (<https://modelfit.io/>, device list <https://modelfit.io/devices/>) | Common | **Scenario not expressible.** Device choices are MacBook Air/Pro, Mac Mini, Mac Studio, iPhone, NVIDIA GPU and AMD (Strix Halo). The device list has no CPU-only, Windows or Intel integrated entry. Output is model fit only (one "best local model" plus an Ollama command); no retrieval stack. Export: open dataset (CC BY 4.0), JSON API, MCP endpoint and CLI, all for model and device data rather than a saved configuration. | Observed behaviour | High |
| CanIRun.ai (<https://www.canirun.ai/>, device page <https://www.canirun.ai/device/iris-xe>) | Common, via the "Intel integrated · Iris Xe" preset (16 GB RAM field) | **Partial.** Grades chat and coding models that fit (for example Qwen 3 8B, grade B, 4.6 GB, about 10 tokens/s; tiny models grade A/B) and reports no image or video models fit. It doesn't cover document Q&A, retrieval, embeddings or a UI, so no stack. The only save/share-like control is "compare"; the device page URL is shareable. The Iris Xe page's picks section was headed "Top open models for Apple M1", a label mismatch at access. The site says its estimates rely on browser APIs. | Observed behaviour; speeds are the tool's estimates | Medium: preset values were defaults, not a specific laptop |

### Interim finding

- **Device-first tools don't substitute for the MVP in this scenario.** ModelFit can't express a CPU-only Windows machine. CanIRun.ai answers "which model fits" but not the rest of the stack, constraint conflicts or a reusable configuration. Both overlap only with the model-fit slice (#2 hardware inputs, #10 sizing).
- **Flocci remains the decisive direct counterexample, and its constraint handling is still untested.** Its 2026-10-16 result already produced an ordered stack with uncertainty notes. If it also detects the offline-plus-hosted-API contradiction and offers a reusable export, the MVP premise is falsified for this scenario (#57, #58).
- **Interim recommendation:** keep the hybrid bounded-workflow MVP under validation. Don't differentiate on model fit, which device-first tools already cover. Test explicit constraint-conflict detection and a versioned, shareable configuration record against Flocci first.

### Needed to finish

A Flocci session with credits. Account creation was outside this run's scope, so the coordinator or an assignee signs in, and the same scenario is then run and logged here with the exact output.

## 2026-10-18 guest contradiction and saved-output test

### Conditions and evidence

Publisher: Flocci Technologies. Source interfaces: [Stack Builder](https://aitools.flocci.in/stack) and [Saved tools](https://aitools.flocci.in/bookmarks), both accessed 2026-10-18. The completed response was captured at 04:50 UTC; bookmark inspection and return navigation finished at 04:56 UTC. These are observation timestamps, not a latency measurement. The product build, generator model/revision, serving region and quota-reset mechanism were not exposed and remain unknown.

A guest cloud-browser session submitted the exact public input requested by @tynamite in the [2026-10-17 test request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66#issuecomment-6233448082). No account, credit purchase, private PDF, installation or stack deployment was used. The page displayed an exhausted-free-stack banner, but entering the prompt enabled the ordinary submission button. One click produced a completed response while that banner remained visible. This records the successful interaction and inconsistent UI signals; it does not establish why it worked or guarantee another guest request. No second generation or alternative API route was attempted.

Exact submitted input:

> Answer questions over my local PDF files on a Windows laptop with 16 GB RAM and no GPU. It must work fully offline with no internet, must use a hosted API model such as GPT, and the budget is zero.

The response explicitly identified the offline/hosted-API contradiction and proposed replacing the hosted call with a model served on localhost. Its five ordered recommendations were Docling for parsing, Ollama for local serving, Microsoft's Phi family for generation, AnythingLLM for the retrieval/chat application, and optional RAGFlow for grounded-answer checking. It claimed the proposed tools could run on the specified Windows CPU laptop without paid service access and without a network after setup. Those are generated claims; this test did not verify them.

The bounded review capture preserves the displayed response and controls, together with screenshots of the result and actual saved page. The public log paraphrases the result rather than copying the catalog. The captures are supporting review artifacts outside this repository, not public product exports or independent benchmark evidence:

| Capture | Bytes | SHA-256 |
| --- | ---: | --- |
| `flocci-contradiction-observation.json` | 10424 | `61c77623e1163ef8f2fbc7f5f23b0e2fb273d99779c9b307a6738c655ac6ebfd` |
| `flocci-contradiction-result-20261018.jpg` | 146604 | `66afc1c25fc5c86caf217b10c5d48c7f81fe1cea43bab9646579a46aaa0c090e` |
| `flocci-saved-tool-20261018.jpg` | 92171 | `0ef6c47bc195e91c6375583b3a6cd8d539093fe4c5502f8e27ff8502023ddd71` |

These hashes identify the reviewer captures; the source URLs do not encode the transient generated result and cannot reproduce it by themselves. The observations and analysis establish no catalog/data reuse licence or permission to redistribute publisher material. Reuse-rights scope for the underlying product content remains unknown.

### Constraint and artifact assessment

| Required property | Observed result and interpretation | Confidence and limit |
| --- | --- | --- |
| Detect and explain conflicting constraints | The response named the conflict and explained the proposed local substitution. This supplies a positive counterexample to differentiation based only on detecting this contradiction. | High for the displayed behavior in one run; no repeatability estimate. |
| Preserve every original hard constraint | The proposed local model changes the hosted-model requirement. The response also qualifies offline operation as applying after setup. It therefore does not demonstrate satisfaction of the original conjunction. | High for the changed requirements; accepting either relaxation is a user decision, not an observed acceptance. |
| Establish Windows, CPU and 16 GB feasibility at zero service spend | The response asserted feasibility and named a model family, but supplied no exact model/checkpoint, quantization, embedding model, runtime versions or measured resource envelope for the whole stack. | Unknown for actual fit, end-to-end cost and runtime success. A plausible generated explanation is insufficient evidence. |
| Preserve a reusable recommendation/configuration | Saving Docling changed the saved count from zero to one. The saved page contained a Docling catalog bookmark; it did not display the prompt, conflict explanation, ordered stack or the other four recommendations. | High for the tested bookmark's visible contents; storage implementation and other access tiers were not inspected. |
| Export/share the tested result and recover it after navigation | No result export/share control was observed in the result or saved-tool section. Returning with ordinary browser Back showed an empty input and no generated result. No configuration file or result-specific URL was obtained. | High for this navigation sequence and inspected controls; absence in this flow does not prove no such feature exists elsewhere. |

The generic catalog download link does not identify this generated recommendation. The bookmark created by this test was removed after inspection, restoring the observed initial saved count of zero. The navigation result concerns the tested UI sequence; it does not establish permanent deletion of any server-side data.

### Proposed narrowing decision and receiving questions

**Narrow the differentiation hypothesis.** Ordered local-stack advice and explicit recognition of this constraint conflict already overlap with Flocci's observed behavior. The initial 2026-10-16 output and this new response should both be retained as counterevidence. The device-first substitutes' narrower 2026-10-17 results remain relevant to model fit; those narrower interfaces were not failed general-purpose stack builders.

Contradiction detection is a positive result for the tested capability. The deliberately impossible prompt is not a fair requirement that any tool satisfy every conflicting constraint; proposing a coherent relaxation is useful behavior. The broader substitute criterion remains unproven because the exercised saving path retained a catalog bookmark and the proposed stack's feasibility was not reproduced. Continue evaluating explicit user acceptance of constraint changes, version-pinned configuration records, reusable exports and evidence for whole-stack feasibility. These are candidate distinctions requiring product and customer validation; one guest interaction does not establish commercial demand or invalidate competitors' untested tiers. The optional RAGFlow step also prevents generalizing the first run's output into a claim that Flocci never proposes a verification step.

| Receiver | Decision input from this observation | Required disposition and remaining question |
| --- | --- | --- |
| #2 | A concrete conflict between offline operation and a required hosted model; a proposed relaxation must remain distinguishable from original requirements. | Accept/narrow the workload and user-confirmation implications at this artifact revision. No workload wire change is proposed here. |
| #40 | A generated conflict explanation is useful UX evidence but does not prove a compatibility result or supply immutable component identities. | Accept/narrow the evidence boundary; decide separately how proposed alternatives preserve original constraints. Frozen v1 remains unchanged. |
| #42 | An exercised catalog bookmark loses the configuration context needed for this decision; this run obtained no reusable stack artifact. | Accept/narrow the saved-build comparison fields and persistence/export interpretation. Its existing #40 prerequisite remains. |
| #50 / #57 / #58 | The decisive Flocci contradiction step now has an actual guest result, with bounded export/persistence evidence and a proposed narrowing decision. | Coordinator and issue owners review the evidence and resulting differentiation/MVP scope. This note does not supply their acceptance or remove native blockers. |

The completed observation resolved the prior access-only gap for this scenario. At #227 delivery, #66 remained open for evidence review, current repository checks and required receiving handoffs; the dated acceptance review below records the subsequent dispositions. Further deployment experiments, exact runtime claims or other access tiers require their own documented inputs and scope; none is inferred from this completed UI test.

## Receiving and research acceptance review (2026-10-18)

This review evaluates the existing observation at note blob
`fbaff0a01df683fd7444769118d18ba0f2d5a473`, delivered by
[#227](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/227) at
`49896b41b6e0add6f333406112e8d009e7ad9ee6` and retained unchanged through
main `3d395801742461aa82ac31a21857ec6f8d0270fb`. It does not refresh the
historical source-access dates or claim another live product test.

The in-session research engineer independently read the full note, the original
10,424-byte observation capture and both screenshots, and recomputed all three
hashes listed above. The capture supports the displayed conflict explanation,
the tested single-tool bookmark, the recorded return navigation and the stated
limits. The initial and second-substitute observations retain their original
authors and dates. Their interface limits are findings within the attempted
common scenario; they are not failed runtime deployments.

The [in-session coordinating engineer's actual receiving receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66#issuecomment-6248861238),
posted through `CompleteDotTech` at `2026-10-18T10:40:31Z`, records a separate
reading of the complete note and capture, visual inspection of both screenshots
and verification of the exact lengths and hashes.
That reviewer also checked the #2 workload inputs, #40 evaluation/evidence
boundaries and #42 revision/pin/adoption semantics. The following are actual
delegated project-engineering receiving decisions. They are not statements by
the listed GitHub assignees; their ownership is unchanged. They cover this
research input only and do not complete any receiving issue.

### Accepted receiving decisions

| Receiver | Disposition at the reviewed artifact | How the consumer uses it and what remains unresolved |
| --- | --- | --- |
| #2 | Accept with constraints: keep each original hard requirement distinct from a proposed relaxation. | The generated local-model alternative and its offline-after-setup qualification must not silently replace the hosted-model and fully-offline requirements. Present the changed requirements, retain the original inputs, and let the user explicitly adopt a new candidate/revision. This follows the workload note's no-substitution policy; no new workload field or wire encoding is adopted. |
| #40 | Accept with constraints: use the observation as conflict-explanation evidence, with compatibility evidence assessed separately. | The [pure-evaluation policy](../T0-configuration/component-schema-compatibility.md#cycles-and-recomputation-proposal) already separates suggestions from verdicts. A generated explanation supplies no exact model/checkpoint, embedding, runtime, resource, price or source-eligibility evidence. Missing eligible facts remain unresolved. Frozen v1, future encodings and the successor-release criteria remain unchanged. |
| #42 | Accept with constraints: a catalog bookmark does not meet the proposed saved-configuration comparison scope. | Apply the existing [reproducibility](../T0-configuration/saved-shared-builds.md#what-makes-a-build-reproducible-proposal) and [revisit](../T0-configuration/saved-shared-builds.md#save-and-revisit-proposal) semantics: retain the inputs, selected identities, settings, links, locks and revision-bound reports; adopting alternatives creates a new revision. This observation establishes no feature-absence claim outside the tested guest path. Sharing sensitivity, field design, persistence implementation and #42's #40 prerequisite retain their separate owners and criteria. |

The research decision is to adopt the narrowing described above:
ordered advice, model-fit suggestions and this contradiction check cannot
carry an exclusive differentiation claim. Continue testing explicit adoption
of changed constraints, exact reusable configuration records and evidence for
whole-stack feasibility. These remain product hypotheses. The observed
verification suggestion also prevents a categorical claim that Flocci never
proposes verification. #50/#57/#58 must reconcile their own criteria against
the accepted observation; this review does not infer customer demand,
willingness to pay, deployment success, export rights or consumer completion.

### Literal #66 criterion map

| Original criterion | Evidence or decision | Review status |
| --- | --- | --- |
| Run a common public non-sensitive scenario | Dated Flocci, ModelFit and CanIRun.ai tests; original common scenario preserved | Evidence reviewed |
| Check constraint handling and explanation quality | 2026-10-18 captured conflict explanation and the separate analysis of changed requirements | Evidence reviewed |
| Inspect saved or exported configuration claims | Actual Docling bookmark, inspected controls and return-navigation result; uninspected tiers remain unknown | Evidence reviewed |
| Record counterexamples and pivot recommendation | Both Flocci responses, device-first scope limits and the bounded narrowing above | Narrowing accepted within the stated research scope |
| Link every significant conclusion to evidence or an explicit hypothesis | Dated source interfaces, original capture hashes, historical attributions and explicit feasibility/product unknowns | Evidence reviewed |
| Relevant technical owners review handoffs; unresolved decisions are named | Actual independent delegated engineering dispositions for the exact #2/#40/#42 scopes above; remaining product, contract and runtime questions stay with the named issues | Accepted with constraints; no absent-assignee response inferred |
| Repository checks pass; reviewer accepts the evidence before Done | Prior #227 evidence review and delivery checks are retained; this amendment passed the required local checks listed below and remains subject to final source review and canonical delivery | Local checks passed; final review and delivery required |

Amendment validation used Python 3.12.14 and the pinned
`requirements-research.txt`: 486 repository tests passed on the original
`3d395801` input; after composing with accepted main `301b7c9c`, all 509
repository tests and 21 frozen-contract tests passed, together with research,
market, handoff-audit and mobile-prompt
validators, dependency consistency and whitespace checks. A direct comparison
with the accepted main input confirmed that exactly the three existing #66
handoff rows append current decisions; every prior field outside their current
acceptance/action text, every historical response and the 44/55/2 cutoff
classification remain unchanged. These checks establish record integrity, not
new product behavior. Final review and merge evidence are recorded on the
delivery PR and #66 before its status is reconciled.
