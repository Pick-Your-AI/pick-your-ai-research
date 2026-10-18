# Competitive landscape

The inventory contains 33 distinct products/resources, including all 22 original named candidates, ten original additional resources and CanIRun.ai. Counts are not market shares. Classification is analytical, not a claim that each product is a complete end-to-end competitor.

The [MR-01 acceptance and selection record](../../research/market/mr01-acceptance.md) contains the merged five-seed audit, current fourteen-profile working list, revision-scoped reviews and remaining owner decisions. The [2026-10-18 follow-up](../../research/market/mr01-acceptance.md#2026-10-18-catalog-and-summary-reconciliation) reconciles CanIRun.ai documentary fields and pins the llmfit upstream identity check. Older observations below retain their stated dates; document publication does not supply issue acceptance.

- [BenchLM](https://benchlm.ai/): Partial competitor, Benchmark provider, Data source. Model and provider comparison with benchmark, price and runtime evidence.
- [Harness Bench](https://www.harness-bench.ai/): Benchmark provider, Open-source integration candidate. Model-harness evaluation in sandboxed tasks with final-artifact oracles.
- [llmfit](https://www.llmfit.org/): Partial competitor, Open-source integration candidate. Hardware detection and model-fit recommendations across quantizations and runtimes.
- [Local AI VRAM Calculator / GPU Planner](https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/): Partial competitor. Goal-based fit estimates with weights, KV cache and runtime overhead.
- [Flocci Ask / Stack Builder](https://aitools.flocci.in/ask): Direct competitor, Data source. Conversational tool discovery; adjacent Stack Builder requires direct substitute testing.
- [Artificial Analysis](https://artificialanalysis.ai/): Partial competitor, Benchmark provider, Data source. Model/provider evaluation, speed, price and recommendation surfaces.
- [OpenRouter](https://openrouter.ai/models): Partial competitor, Infrastructure provider, Data source. Model directory plus unified provider-routing API.
- [Hugging Face Hub](https://huggingface.co/models): Partial competitor, Data source, Infrastructure provider. Model discovery with task/library filters and model-card metadata.
- [Arena](https://arena.ai/): Benchmark provider, Partial competitor. Public model ranking and comparison entry point; interactive evaluation not tested.
- [LLM Stats](https://llm-stats.com/): Partial competitor, Data source. Leaderboard comparing intelligence, speed and price.
- [Models.dev](https://models.dev/): Data source, Open-source integration candidate, Partial competitor. Provider and canonical-model metadata with JSON endpoints.
- [CanRun](https://canrunllm.com/): Partial competitor. Hardware and RAM calculator for local AI model fit.
- [CanItRun](https://canitrun.dev/): Partial competitor. GPU hardware checker and VRAM calculator.
- [ModelFit](https://modelfit.io/): Direct competitor, Data source, Open-source integration candidate. Device-first local-model recommendations; CLI and documented JSON/MCP access.
- [CanIRun.ai](https://canirun.ai/): Partial competitor. Hardware/use-case local-model recommendations and documented JSON model, compatibility and recommendation interfaces; source-inspected, not exercised in the #48 follow-up. Separate from CanRun and CanItRun.
- [Ollama](https://ollama.com/library): Substitute workflow, Open-source integration candidate. Discover and run model packages through a local-model ecosystem.
- [GPUs.io](https://gpus.io/): Partial competitor, Data source. Cloud GPU rental price comparison.
- [Vast.ai](https://vast.ai/): Infrastructure provider, Potential partner. GPU rental marketplace.
- [Runpod](https://www.runpod.io/): Infrastructure provider, Potential partner. GPU cloud platform for AI workloads.
- [Dify](https://dify.ai/): Adjacent competitor, Substitute workflow. Visual agentic application and knowledge workflow platform.
- [Langflow](https://www.langflow.org/): Adjacent competitor, Substitute workflow. Low-code builder for agent and RAG applications.
- [Flowise](https://flowiseai.com/): Adjacent competitor, Substitute workflow. Visual agent construction.
- [n8n](https://n8n.io/): Adjacent competitor, Substitute workflow. Workflow automation with AI integrations.
- [SkyPilot](https://skypilot.ai/): Substitute workflow, Open-source integration candidate. Manage and execute AI compute across infrastructure providers.
- [BentoML / Bento](https://www.bentoml.com/): Substitute workflow, Infrastructure provider. Model inference deployment and scaling.
- [Langfuse](https://langfuse.com/): Adjacent competitor, Open-source integration candidate. Agent evaluation and observability.
- [Ragas](https://docs.ragas.io/en/stable/): Benchmark provider, Open-source integration candidate. Evaluation tooling for LLM and RAG applications.
- [LlamaIndex](https://www.llamaindex.ai/): Adjacent competitor, Substitute workflow. Document-oriented agent workflows and data processing.
- [LangChain](https://www.langchain.com/): Adjacent competitor, Substitute workflow. Agent development platform and ecosystem.
- [Qdrant Vector Search Benchmarks](https://qdrant.tech/benchmarks/): Benchmark provider, Data source. Vendor-published vector search comparisons.
- [LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness): Benchmark provider, Open-source integration candidate. Framework for few-shot language-model evaluation.
- [Official MCP Registry](https://github.com/modelcontextprotocol/registry): Data source, Open-source integration candidate. Community-maintained registry service for MCP server metadata.
- [Unsloth](https://unsloth.ai/): Substitute workflow, Open-source integration candidate. Local model running and training tools.

Machine-readable observations: [competitors](../../research/market/competitors.json), [feature matrix](../../research/market/features.json), [sources](../../research/market/sources.json). Unknown features remain unknown. Review detailed profiles before using claims in strategy.

## Seeds

**Operational scope selected 2026-10-18 under delegated engineering authority:** use the five entries below for the bounded #48 seed-coverage review. This resolves the working list, not the undocumented original intent: the earlier inference came from the first five catalog entries, the llmfit profile and the risk register. Selection does not certify verification, operator identity or receiving-owner acceptance. The observations below retain their original 2026-10-16 access date; no fresh site inspection is claimed.

| Seed | Operator (as established) | Site | Repository | Site vs repository boundary |
| --- | --- | --- | --- | --- |
| BenchLM | Not named: terms apply "between you and the operator of BenchLM" (`src-benchlm-legal`, terms updated 2026-10-02) | <https://benchlm.ai/> | None found | Hosted service only |
| Harness Bench | Harness Bench Team; site links to Qihoo360 repository (`src-harness-bench`) | <https://www.harness-bench.ai/> | <https://github.com/Qihoo360/harness-bench> (homepage field empty; GitHub licence API returns none) | Site links to repository; repository does not link back. Reuse rights not established |
| llmfit.org | **Unverified** (see below) | <https://www.llmfit.org/> | <https://github.com/AlexsJones/llmfit> (MIT) | Separate site; links one-way to the repository |
| Local AI VRAM Calculator / GPU Planner | Logarithmic Spirals, a pseudonymous individual blog author; links GitHub user `h93xV2` (`src-local-ai-planner-about`) | <https://logarithmicspirals.com/tools/local-ai-vram-calculator-gpu-planner/> | None for the tool found | Browser tool on a personal blog |
| Flocci Ask / Stack Builder | Flocci Technologies (footer text on the Ask page) | <https://aitools.flocci.in/ask> | None found | Hosted service only |

## Operator findings

- **llmfit.org vs AlexsJones/llmfit.** `gh api repos/AlexsJones/llmfit` returns an empty `homepage`. The repository `CNAME` and GitHub Pages config point to `llmfit.axjns.dev` (Alex Jones's domain, per his GitHub profile), and a repository code search finds no `llmfit.org` reference. llmfit.org links to the repository and installs from `llmfit.axjns.dev`, but shows only "© 2026 llmfit". The upstream maintainer is established; **the llmfit.org operator remains unverified** (`src-llmfit-upstream-pages`). Treat llmfit.org as a third-party documentation site until the maintainer confirms it.
- **LLM Stats:** about page self-describes "two people" signing as "Co-founders, llm-stats"; terms (updated 2026-10-08) cite United States law and name no entity. Legal entity unknown (`src-llm-stats-legal`).
- **CanRun:** "CanRun is an independent project", unaffiliated with GPU makers or model publishers; served by Cloudflare Pages. Operator unnamed (`src-canrun-about`).
- **CanItRun:** methodology and privacy pages (privacy updated 2026-08-16) name no operator; contact e-mail only. Unknown (`src-canitrun-about`).
- **GPUs.io:** home, about, terms and privacy returned 403 with a bot challenge to anonymous retrieval on 2026-10-16. Not bypassed; operator and content were unverified in that inspection (`src-gpus-io-recheck`). The earlier `src-gpus-io` "retrieved" record is preserved unchanged. The separately dated 2026-10-18 terms correction in `sources.json` / `src-gpus-io` names Peak Technologies, Inc. as publisher attribution; see the [MR-01 source limitations](../../research/market/mr01-acceptance.md#claimevidence-review-and-source-limitations). Independent ownership verification and intended-use permission remain separate; this summary performs no new site check.

## Community fit-report resources (staged, not yet in the catalog)

tynamite's PR #67 review (item 5) and PR #81 (D36–D41, Q9) name six community fit-report projects. All six exist and their primary pages are registered in `sources.json`. They are **not yet added to `competitors.json`** because `validate_market_research.py` requires a complete product × feature matrix: each new entity needs 48 `features.json` cells, which #49 owns. Once #49 adds them (as `Unknown` unless evidenced), the catalog would rise from 33 to 39 after the CanIRun.ai intake, inside the 30–40 bound.

| Proposed ID | Resource | Operator / repository | Proposed classification | Source | Key boundary |
| --- | --- | --- | --- | --- | --- |
| `localscore` | LocalScore | Mozilla Builders project; `cjpais/LocalScore` (Apache-2.0) | Benchmark provider, Data source, Open-source integration candidate | `src-localscore` | Optional submission; no result verification stated |
| `localmaxxing` | LocalMaxxing | Operator unnamed; CLI `LottoLottoLotto/localmaxxing-cli` (MIT) | Partial competitor, Benchmark provider, Data source | `src-localmaxxing` | Sign-in for submission; automatic plausibility checks |
| `rapid-mlx` | Rapid-MLX community benchmarks | `raullenchai/Rapid-MLX` (licence API: NOASSERTION) | Benchmark provider, Data source | `src-rapid-mlx` | Apple Silicon only; one locked run protocol |
| `metrillm` | MetriLLM | GitHub org `MetriLLM` (Apache-2.0) | Benchmark provider, Data source, Open-source integration candidate | `src-metrillm` | Requires Ollama or LM Studio; uncurated by claim |
| `openbenchmarking-llama-cpp` | OpenBenchmarking.org `pts/llama-cpp` | OpenBenchmarking.org / Phoronix Test Suite (GPL-3.0 client) | Benchmark provider, Data source | `src-openbenchmarking-llama-cpp` | Profile page blocked (403); current version unverified |
| `llama-cpp-perf-threads` | llama.cpp performance discussion threads | `ggml-org/llama.cpp` Discussions #4167, #10879, #15013 | Data source | `src-llama-cpp-perf-threads` | Community reports; maintainer-curated scoreboards |

These are direct counterexamples to the defensibility hypothesis in [differentiation](../../research/market/differentiation.md) ("a reviewed, reproducible history of configuration outcomes"): public, versioned, community-submitted fit and speed records already exist. That row should be re-judged by #57 with them included. They do not by themselves show a workload-first, multi-tier selection flow.

## Claim-level evidence

`sources.json` carries one `evidence_grade` per source, and the competitor records have no per-claim grade field. Per tynamite's review, grades below attach to claims using the four grades in [RESEARCH_METHOD](../RESEARCH_METHOD.md), plus "Observed browser behavior" scoped to recorded steps. New source records use the grade that fits their primary use (for example `src-metrillm` is graded Vendor claim).

| Entity | Claim | Grade | Source |
| --- | --- | --- | --- |
| BenchLM | Data access through API or MCP, 250 free monthly reads | Vendor claim | `src-benchlm` |
| BenchLM | Commercial display requires a separate agreement | Primary documentation (terms) | `src-benchlm`, `src-benchlm-legal` |
| Harness Bench | Measures harness effects in sandboxed tasks | Vendor claim | `src-harness-bench` |
| Harness Bench | No repository licence returned by GitHub | Observed (API response) | `src-harness-bench` |
| llmfit | Local REST API, JSON output, runtime providers | Primary documentation; untested | `src-llmfit` |
| llmfit | "Tells you which models can actually run well" | Vendor claim | `src-llmfit` |
| Local AI planner | Hardware/context/runtime controls render | Observed browser behavior | browser observations |
| Local AI planner | Fit estimates include KV cache and runtime overhead | Vendor claim; accuracy unverified | `src-local-ai-planner` |
| Flocci | Stack Builder returns ordered RAG advice | Observed browser behavior; advice correctness unverified | browser observations |
| CanRun | Calculation runs in the browser; nothing sent | Primary documentation (privacy policy); not traffic-tested | `src-canrun-about` |
| LLM Stats | 200K+ users, Fortune 500 customers | Vendor claim | `src-llm-stats-legal` |
| LocalMaxxing | Suspicious runs hidden by a physical speed ceiling | Primary documentation (policy); enforcement untested | `src-localmaxxing` |
| MetriLLM | Every submitted result displayed; reproducible by hash | Vendor claim | `src-metrillm` |
| LocalScore | Results are "directly comparable" | Vendor claim | `src-localscore` |
| llama.cpp threads | Posted tokens/s for given commit and hardware | Community report, not independent measurement | `src-llama-cpp-perf-threads` |

**Schema proposal (for #41 and the market validator owner, not applied):** add an optional `claims` array to each competitor record, with `text`, `source_id`, `evidence_grade` (Primary documentation / Vendor claim / Independent measurement / Estimate / Observed behavior), `status` (e.g. unverified, exercised) and `access_date`, and have the validator check `source_id` membership. Keep source-level `evidence_grade` only as a description of the document type, or rename it `document_type`. `deployment_support` and `apis_and_integrations` now carry entry-specific text with the grade inline, or the explicit `Unknown:` string where no primary evidence was reviewed.

## Deep-dive selection rationale

**Historical reconstruction of the original thirteen profiles.** The table below retains the initial selection explanation. The current working selection is fourteen after the already-merged CanIRun.ai intake; its [explicit #48 rationale and scoped #50 reviews](../../research/market/mr01-acceptance.md#fourteen-selected-deep-dives-for-50) were delivered through PRs #214 and #231. The four criteria are decision overlap, evidence availability, substitution risk and source relevance. Coordinator confirmation, profile acceptance and hands-on tests remain separate. This is an analyst selection, not a vendor ranking.

| Selected | Reason |
| --- | --- |
| BenchLM, Harness Bench, llmfit, Local AI planner, Flocci | The five operational seeds selected 2026-10-18; each overlaps an entry step (model choice, harness evaluation, hardware fit, guided stack) |
| ModelFit | Strongest documented hardware-first direct substitute (device/setup/results flow, CLI, MCP) |
| Artificial Analysis, OpenRouter, Hugging Face, Models.dev | Primary model, provider and price data feeds; integration and rights questions for #41 |
| Dify, n8n, SkyPilot | Build/deploy substitutes downstream of a recommendation; test export and execution boundaries |

Excluded from deep dives: Arena and LLM Stats (leaderboards overlapping Artificial Analysis and BenchLM); CanRun and CanItRun (narrower fit calculators overlapping llmfit, ModelFit and the planner, operators unknown); Ollama and Unsloth (runtimes, substitutes only for the run step); GPUs.io, Vast.ai and Runpod (infrastructure pricing, for #54/#39); Langflow, Flowise, LlamaIndex and LangChain (adjacent builders represented by Dify and n8n); Langfuse, Ragas, LM Evaluation Harness and Qdrant benchmarks (evaluation tooling for #36); MCP Registry (T4 data source).

**Coordinator decision needed:** LocalScore and LocalMaxxing are the strongest of the new community resources against the defensibility hypothesis (public, submission-based fit databases with stated protocols or plausibility checks). With the CanIRun.ai intake, profiling one brings the set to 15, within the 10–15 target. Profiling both would bring it to 16 and needs an explicit scope decision or a replacement profile. The other four are better treated as evidence sources for #41/#60 than as profiles.

## CanIRun.ai addition (2026-10-16)

[CanIRun.ai devices](https://www.canirun.ai/devices) is recorded as `canirun-ai`, a partial competitor for device-first local model selection. It is operated by GitHub user midudev, per the `midudev/canirun.ai` repository whose homepage is canirun.ai (legal entity unconfirmed). It is a separate record from CanRun (`canrunllm.com`) and CanItRun (`canitrun.dev`); ownership relationships to those are unknown. The repository README describes hardware-detected, per-use-case recommendations, which makes it a direct-substitute candidate pending #66. See the [dated profile](../../research/market/competitors/canirun-ai.md). #48 owns intake, #49 its 48 matrix cells, #50 the profile and #66 scenario testing. This adds a fourteenth profile within the 10–15 target; it does not establish a full-stack substitute or data reuse permission.

The [2026-10-18 #48 reconciliation](../../research/market/mr01-acceptance.md#2026-10-18-catalog-and-summary-reconciliation) records the later pinned README/footer/API-route evidence. The original directory and #125 browser observations retain their dates and limits; documented API shapes do not establish live availability or fit accuracy.
