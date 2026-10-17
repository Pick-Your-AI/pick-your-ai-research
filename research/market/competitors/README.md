# Competitor profiles (MR-03)

Issue: [#50](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/50). Status: draft for owner review. Revised 2026-10-16 from the thirteen PR #67 desk profiles. None is independently accepted or benchmark-reproduced. Hands-on substitute testing is owned by [#66](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66) ([substitute-validation.md](../substitute-validation.md)); these profiles cite it and do not extend it.

## Selection rationale

The fourteen profiles (including the CanIRun.ai intake) are drawn from the 33-entity [#48 catalog](../competitors.json), keeping its entity IDs, classifications and profile paths. #48 records the selection as a criterion ("Select 10–15 material deep dives") but no separate rationale, so this is the #50 basis for #48 to confirm:

1. **Direct substitution risk first.** Products that take a user's workload or hardware and return a recommendation: Flocci, ModelFit, llmfit, Local AI Planner, BenchLM (LLM Selector), Artificial Analysis (Model Recommender), and CanIRun.ai (provisional, added in #98: its repository README describes hardware-detected, per-use-case recommendations, which ranks it with ModelFit/llmfit on direct-substitution risk ahead of the submission databases LocalScore and LocalMaxxing; the coordinator decision on those two still stands).
2. **Decision-changing evidence and data sources**, where rights or provenance could invalidate ingestion: BenchLM, Artificial Analysis, OpenRouter, Hugging Face, Models.dev, Harness Bench.
3. **Substitute workflows** that let users skip planning and build or run directly: Dify, n8n (application/automation) and SkyPilot (compute placement).

Not profiled, with reason: Arena, LLM Stats, CanRun, CanItRun (overlap BenchLM/Artificial Analysis or ModelFit/llmfit at lower evidence availability); GPUs.io, Vast.ai, Runpod (pricing and infrastructure belong to #54/#39; GPUs.io rights are covered by PR #82); Langflow, Flowise, LlamaIndex, LangChain (same substitute archetype as Dify); Ollama, BentoML, Langfuse, Ragas, LM Evaluation Harness, Qdrant benchmarks, MCP Registry, Unsloth (components or evaluation tools rather than selection substitutes). The selection deliberately includes products that weaken Pick Your AI's differentiation.

## Evidence classes

Used in every profile's workflow table.

- **Observed**: seen in a fetch made on 2026-10-16 at the cited URL: page structure or form fields, licence files, GitHub API responses. "Observed hands-on" is only Flocci's recorded browser session. Observing a form is not running it. In [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87) terms this is still Documented, not Exercised.
- **Documented**: the operator's documentation or help text describes the behaviour; not exercised.
- **Vendor claim**: self-assessment such as accuracy, independence, "verified" or counts.
- **Unknown**: not established. Silence is not absence.
- **Hypothesis**: every counterexample unless marked observed.

Access tier for all profiles: public pages, public docs and public repository metadata. No accounts, keys, paid plans, API calls to data endpoints, installations or deployments.

## Index

| Profile | Workflow evidence | Rights evidence | Strongest counterexample (suffices for) |
| --- | --- | --- | --- |
| [Flocci Ask / Stack Builder](flocci.md) | Observed hands-on (one historical request, #66) + static pages | No terms found; © operator | Free ordered toolchain for a common local task |
| [CanIRun.ai](canirun-ai.md) | Observed static directory + README vendor claim; untested | Public repo, no licence file; no reuse grant | Hardware-detected local model choice (hypothesis) |
| [ModelFit](modelfit.md) | Observed UI structure + Documented | Licence files observed: MIT CLI (API NOASSERTION), CC BY 4.0 dataset | Best local model for one device |
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

Claims are from [differentiation.md](../differentiation.md) (#57). Each row names the strongest competing workflow. All are hypotheses until #66 tests them.

| Differentiation claim | Strongest counterexample | Where it could suffice | Remaining gap (to test, not assumed) |
| --- | --- | --- | --- |
| Workload-first guided recommendation | BenchLM LLM Selector; Flocci Stack Builder | Single hosted-model choice (BenchLM); free local toolchain (Flocci, observed once) | Joint multi-tier composition with compatibility evidence |
| Hardware-aware fit | ModelFit, llmfit, Local AI Planner, CanIRun.ai | One device, local GGUF models | Hosted-vs-local trade-off; measured, not heuristic, memory |
| Cross-provider cost/performance | Artificial Analysis, OpenRouter | API model/provider choice | Complete bill, self-hosting cost; AA data barred for this use |
| Versioned, shareable configuration | Dify DSL, n8n JSON + Git, SkyPilot YAML; BenchLM URL state | Teams that already know their components | These record what to run, not why; BenchLM links re-evaluate on current data |
| Evidence-linked defensibility | Harness Bench, BenchLM methodology; community fit-report projects (below) | Readers who want published measurements | Reproducible history of configuration outcomes is not shown by any profile, but community projects were not reviewed |

## Rights summary

Commercial access, code licence and data rights are separated in each profile. Data decisions follow pending [PR #82](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/82) (#55/#60, not yet merged) where it covers the source. Profiles add three findings for #41/#60: BenchLM website data is CC BY-NC 4.0; OpenRouter terms also bar developing "a competing service"; the ModelFit CLI and n8n/Dify licences are not auto-detected by GitHub (`NOASSERTION`), so SPDX comes from reading the file. Sources without terms (Flocci, Local AI Planner) default to no display or redistribution under the #82 decision rule.

## Matrix consistency

`saved`, `share`, `export` and `model_versions` statements match pending [PR #87](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/87) (#49) for all thirteen products. `features.json` is not edited here. Proposed #49 follow-ups: BenchLM `natural_language`, `constraints` and `guided_selection`; OpenRouter `constraints`; SkyPilot `constraints` and `multi_gpu`, each Documented by the pages cited in the profiles.

## Proposed source-register additions

For #48 to accept into [sources.json](../sources.json). Not applied here.

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

- #66: run BenchLM Selector, Artificial Analysis Recommender and ModelFit on the shared scenario; Flocci contradictory constraints and bookmark round-trip.
- #41/#60 (and #55): adopt PR #82 decisions plus the three findings above.
- #49: the matrix follow-ups above. #48: source additions, candidate entities, BenchLM classification.
- #6, #10, #25, #39: profile-specific questions in each file. Owner dispositions are not yet requested.

## Robots.txt and access record

No block prevented a planned fetch. Paths disallowed and not fetched: BenchLM `/api/`, Flocci `/ask?`, `/stack?`, `/bookmarks?`, `/api/`; docs.skypilot.ai outside `/en/latest/` and `/en/stable/`. Harness Bench, Models.dev and skypilot.ai serve no robots.txt. Artificial Analysis and OpenRouter terms restrict automated scraping, so each had at most five pages read once, and no data endpoint was called. Client-rendered content (Artificial Analysis Recommender inputs, BenchLM shortlist output, Flocci app) was not visible without a browser.
