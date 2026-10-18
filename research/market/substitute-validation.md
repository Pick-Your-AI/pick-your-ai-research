# MR-03: Test direct stack-builder substitutes

Issue: [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66). Assignees: @tynamite, @itisSomeone; coordinator @CompleteDotTech. Status: common scenario run on two device-first substitutes (2026-10-17); Flocci contradictory-constraints test blocked by sign-in. Readiness: Needs input (a signed-in Flocci session).

## Question
Do Flocci and other guided builders already satisfy the proposed MVP?

## Starting evidence
[competitors.json](competitors.json). This note is not a new canonical component catalog or a completed measurement.

## Protocol and acceptance
- [x] Run a common public non-sensitive scenario (Flocci 2026-10-16; ModelFit and CanIRun.ai 2026-10-17)
- [ ] Check constraint handling and explanation quality (Flocci contradictory-constraints test blocked by sign-in)
- [x] Inspect saved or exported configuration claims (ModelFit, CanIRun.ai; Flocci export still unverified)
- [ ] Record counterexamples and pivot recommendation (interim recommendation below; Flocci result pending)
- [x] Record exact source/version, conditions, failures and confidence.
- [ ] Obtain affected-owner review and accepted handoff.

## Next action
Run the contradictory-constraints scenario on Flocci Stack Builder from a signed-in session with available credits (see 2026-10-17 results). Then check whether Flocci's output can be saved or exported.

## Result
One generated workflow was observed, as described below; no deployed-system validation is claimed. No raw customer data, benchmark artifact or paid API output was collected. Consumers: #2, #40, #42.

## Initial result
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
