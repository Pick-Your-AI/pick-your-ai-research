# Competitor profiles (MR-03)

Issue: [#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50). Status: fourteen desk profiles merged as partial research; full acceptance remains open. The original desk sources retain their 2026-10-16 access dates. Repository-state reconciliation: 2026-10-18. [#125](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/125) supplies independently reviewed, bounded 2026-10-17 browser observations for ModelFit and CanIRun.ai and the Flocci access gate. These are not performance benchmarks. Hands-on testing remains with [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66) ([substitute-validation.md](../substitute-validation.md)); this reconciliation performs no new session and does not complete that child.

## Selection rationale

The fourteen profiles (including the CanIRun.ai intake) are drawn from the 33-entity [#48 catalog](../competitors.json), keeping its entity IDs, classifications and profile paths. The merged [#48 selection rationale and revision-scoped #50 reviews](../mr01-acceptance.md#fourteen-selected-deep-dives-for-50) now record the working-list decision; the selection basis below remains the #50 explanation. Coordinator confirmation, full profile acceptance and #66 hands-on results remain separate. Later [CanIRun.ai documentary reconciliation](../mr01-acceptance.md#2026-10-18-catalog-and-summary-reconciliation) does not refresh these historical profile observations:

1. **Direct substitution risk first.** Products that take a user's workload or hardware and return a recommendation: Flocci, ModelFit, llmfit, Local AI Planner, BenchLM (LLM Selector), Artificial Analysis (Model Recommender), and CanIRun.ai (provisional, added in #98: its repository README describes hardware-detected, per-use-case recommendations, which ranks it with ModelFit/llmfit on direct-substitution risk ahead of the submission databases LocalScore and LocalMaxxing; the coordinator decision on those two still stands).
2. **Decision-changing evidence and data sources**, where rights or provenance could invalidate ingestion: BenchLM, Artificial Analysis, OpenRouter, Hugging Face, Models.dev, Harness Bench.
3. **Substitute workflows** that let users skip planning and build or run directly: Dify, n8n (application/automation) and SkyPilot (compute placement).

Not profiled, with reason: Arena, LLM Stats, CanRun, CanItRun (overlap BenchLM/Artificial Analysis or ModelFit/llmfit at lower evidence availability); GPUs.io, Vast.ai, Runpod (pricing and infrastructure belong to #54/#39; GPUs.io rights are covered by PR #82); Langflow, Flowise, LlamaIndex, LangChain (same substitute archetype as Dify); Ollama, BentoML, Langfuse, Ragas, LM Evaluation Harness, Qdrant benchmarks, MCP Registry, Unsloth (components or evaluation tools rather than selection substitutes). The selection deliberately includes products that weaken Pick Your AI's differentiation.

## Evidence classes

Used in every profile's workflow table.

- **Observed**: a dated observation of page structure, form fields, licence files or repository metadata, rather than verified runtime behavior. Original desk observations are from 2026-10-16. Later recorded browser observations are explicitly dated and linked to #66/#125. Seeing a form is not executing a scenario; scenario interaction is not a performance measurement. Profile prose does not automatically promote a matrix cell to Exercised.
- **Documented**: the operator's documentation or help text describes the behaviour; not exercised.
- **Vendor claim**: self-assessment such as accuracy, independence, "verified" or counts.
- **Unknown**: not established. Silence is not absence.
- **Hypothesis**: every counterexample unless marked observed.

Access tier for all profiles: public pages, public docs and public repository metadata. No accounts, keys, paid plans, API calls to data endpoints, installations or deployments.

## Index

| Profile | Workflow evidence | Rights evidence | Strongest counterexample (suffices for) |
| --- | --- | --- | --- |
| [Flocci Ask / Stack Builder](flocci.md) | Observed hands-on (one historical request, #66) + static pages | No terms found; © operator | Free ordered toolchain for a common local task |
| [CanIRun.ai](canirun-ai.md) | Static intake plus bounded Iris Xe preset observation, 2026-10-17 (#125); estimates unverified | Public repo, no licence file; no reuse grant established | Single-device model-fit slice; the tested preset did not supply the PDF retrieval stack |
| [ModelFit](modelfit.md) | UI/documentation plus bounded device-flow observation, 2026-10-17 (#125) | Licence files observed: MIT CLI (API NOASSERTION), CC BY 4.0 dataset | Local-model selection; the common CPU-only Windows scenario was not expressible in that session |
| [llmfit](llmfit.md) | Documented | MIT via licence API | Local model and quantization fit on one machine |
| [Local AI Planner](local-ai-planner.md) | Observed UI (form fields) | No terms found | Single-GPU or Mac local model with speed targets |
| [BenchLM](benchlm.md) | Observed UI (selector form) + Documented | Terms quoted: CC BY-NC website data; display agreement | Hosted API model for one task under budget |
| [Artificial Analysis](artificial-analysis.md) | Documented (recommender inputs not visible statically) | Terms quoted; Data Platform Terms s2.5 per PR #82 | Hosted model/provider by intelligence, speed, price |
| [OpenRouter](openrouter.md) | Documented | Terms quoted: no automated scraping, competing-service clause | Provider choice and execution for a known model |
| [Hugging Face Hub](hugging-face.md) | Observed UI (filters) | ToS + per-repository licences | Filtered model search with pinned revisions |
| [Models.dev](models-dev.md) | Observed UI (table) | MIT via licence API | Hosted model catalogue lookup |
| [Harness Bench](harness-bench.md) | Observed site content | Licence API 404; paper CC BY 4.0 | Harness choice for a fixed model |
| [Dify](dify.md) | Documented | Modified Apache 2.0 (API NOASSERTION) | Building a RAG/agent app with known components |
| [n8n](n8n.md) | Documented | Sustainable Use License (API NOASSERTION) | Automating a known process from a template |
| [SkyPilot](skypilot.md) | Documented | Apache-2.0 via licence API | Placing a known GPU workload across clouds |

## Material differentiation counterexamples

Claims are from [differentiation.md](../differentiation.md) (#57). Each row names a competing workflow and retains its stated hypothesis boundary. #125 adds narrow observed counterexample evidence for two device-first tools, not a market-wide sufficiency or runtime-accuracy conclusion. Flocci's contradictory-constraints and export tests remain incomplete under #66.

| Differentiation claim | Strongest counterexample | Where it could suffice | Remaining gap (to test, not assumed) |
| --- | --- | --- | --- |
| Workload-first guided recommendation | BenchLM LLM Selector; Flocci Stack Builder | Single hosted-model choice (BenchLM); free local toolchain (Flocci, observed once) | Joint multi-tier composition with compatibility evidence |
| Hardware-aware fit | ModelFit, llmfit, Local AI Planner, CanIRun.ai | One device, local GGUF models | Hosted-vs-local trade-off; measured, not heuristic, memory |
| Cross-provider cost/performance | Artificial Analysis, OpenRouter | API model/provider choice | Complete bill, self-hosting cost; AA data barred for this use |
| Versioned, shareable configuration | Dify DSL, n8n JSON + Git, SkyPilot YAML; BenchLM URL state | Teams that already know their components | These record what to run, not why; BenchLM links re-evaluate on current data |
| Evidence-linked defensibility | Harness Bench, BenchLM methodology; community fit-report projects (below) | Readers who want published measurements | Reproducible history of configuration outcomes is not shown by any profile, but community projects were not reviewed |

## Rights summary

Commercial access, code licence and data rights are separated in each profile. [#82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82) merged the source-use audit; consult the current [#60 decision record](../rights-validation.md) and [source-specific register](../integrations.json) before reuse. The dated profiles record BenchLM's website-data CC BY-NC scope, OpenRouter's competing-service restriction and file-read licences where GitHub reports `NOASSERTION`. They do not grant access, ingestion, commercial display or redistribution. For sources without an established permission basis, product reuse stays excluded pending the responsible owner's review; missing documentation does not establish a legal prohibition or a licence grant. Historical profile dates are not refreshed by this repository reconciliation.

## Matrix consistency

[#87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87) and [#98](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/98) are merged. Their current `features.json` is a separate capability-evidence artifact; this profile reconciliation does not promote a cell. At the 2026-10-18 readback, BenchLM `natural_language`/`constraints`/`guided_selection`, OpenRouter `constraints` and SkyPilot `constraints`/`multi_gpu` remain Unknown. The older profile suggestions are leads for the bounded #49 capability tests, not sufficient proof to mark them Documented or Exercised. CanIRun.ai `vram_ram` remains a documentary device-capacity observation, explicitly not a measured model-memory requirement; its profile retains the re-basing question.

## Historical source-register leads

The desk pass proposed these URLs for #48's [source register](../sources.json).
#48 owns their current inclusion and disposition; compare the live register
before adding anything rather than assuming every historical lead is absent.
This reconciliation changes no source registration or original access date.

| Entity | Proposed supporting URLs (all accessed 2026-10-16) |
| --- | --- |
| `src-benchlm` | https://benchlm.ai/tools/llm-selector, https://benchlm.ai/stack, https://benchlm.ai/terms |
| `src-artificial-analysis` | https://artificialanalysis.ai/models/recommend, https://artificialanalysis.ai/terms-of-use |
| `src-openrouter` | https://openrouter.ai/terms, https://openrouter.ai/docs/guides/routing/provider-selection |
| `src-hugging-face` | https://huggingface.co/terms-of-service |
| `src-modelfit` | https://modelfit.io/terms/, https://modelfit.io/about/, https://github.com/Wecko-ai/modelfit, https://github.com/Wecko-ai/modelfit-hardware-dataset |
| `src-flocci` | https://aitools.flocci.in/discover/ai-tools-catalog.html |
| `src-local-ai-planner` | https://logarithmicspirals.com/about/ |
| `src-dify` | https://docs.dify.ai/en/cloud/use-dify/workspace/app-management, https://dify.ai/legal/terms-of-service, https://github.com/langgenius/dify |
| `src-n8n` | https://docs.n8n.io/build/manage-workflows/export-and-import.md, https://github.com/n8n-io/n8n |
| `src-skypilot` | Canonical URL is now https://skypilot.ai/ (skypilot.co redirects); https://docs.skypilot.ai/en/latest/reference/yaml-spec.html, https://github.com/skypilot-org/skypilot |
| `src-harness-bench` | arXiv v2 licence (CC BY 4.0) on https://arxiv.org/abs/2605.27922 |

Candidate new entities (not reviewed by #50; URLs not guessed): the community fit-report projects listed in [PR #81](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/81) and raised in the PR #67 review: LocalScore, LocalMaxxing, Rapid-MLX, MetriLLM, OpenBenchmarking `pts/llama-cpp` and the llama.cpp performance threads. They may counter the defensibility row above. Classification review for #48: BenchLM's LLM Selector may justify "Direct competitor" for the hosted model-first segment.

## Routing and unresolved decisions

- #66: retain #125's dated ModelFit/CanIRun.ai observations and their session limits; complete Flocci contradictory constraints and save/export from an authorized session. Other proposed scenarios remain with the existing child owners; this index starts none.
- #41/#60 (and #55): preserve the merged #82 audit and review changed source/material/use scopes separately; a licence or merged desk profile is not integration acceptance.
- #49: the matrix follow-ups above. #48: source additions, candidate entities, BenchLM classification.
- #6: [narrowed receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/59#issuecomment-6242699859) accepts discovery/context only at `7acbefbf`, not recommendations or technical capability. Other co-owner scope is unrecorded.
- #41: [historical acceptance with provenance changes](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545) retains its original scope. #10/#25/#39 receiving decisions remain pending in the canonical [handoff ledger](../handoffs.md); the #59 writer owns that ledger.

## Acceptance after reconciliation

The fourteen profiles are within the issue's 10–15 target, but inventory size is
not full acceptance. The receiving-owner and coordinator still review the
workflow/architecture evidence, source-use boundaries and counterexample
interpretation. #66's unfinished Flocci test prevents a complete differentiation
verdict. Unknowns, proposed matrix changes and source-register additions remain
with their named owners. #50 stays open; no checklist, Project field, assignment
or native relationship is changed by this documentation contribution.

## Robots.txt and access record

No block prevented a planned fetch. Paths disallowed and not fetched: BenchLM `/api/`, Flocci `/ask?`, `/stack?`, `/bookmarks?`, `/api/`; docs.skypilot.ai outside `/en/latest/` and `/en/stable/`. Harness Bench, Models.dev and skypilot.ai serve no robots.txt. Artificial Analysis and OpenRouter terms restrict automated scraping, so each had at most five pages read once, and no data endpoint was called. Client-rendered content (Artificial Analysis Recommender inputs, BenchLM shortlist output, Flocci app) was not visible without a browser.
