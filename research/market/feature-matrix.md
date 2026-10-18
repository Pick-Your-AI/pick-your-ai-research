# Feature matrix review guide

Original source snapshot: 2026-10-16. The separately dated 2026-10-18 documentary review and classification records are in [the current acceptance audit](mr02-acceptance.md#current-documentary-review--2026-10-18). Original source dates remain historical; only the newly sourced ModelFit explanation has a new claim date and scope. Canonical delivery and exact receiving receipts are recorded separately from the source observations.

F = Exercised: bounded test passed with replayable evidence. P = Documented: narrower documentary support, including unverified vendor claims. N = Unsupported: explicit negative evidence under pinned conditions. ? = Unknown. No absence is inferred from silence. The old “Verified Full/Partial” names are retired following [the evidence-owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545).

[features.json](features.json) retains all 33 entities and 48 dimension IDs. It defines a test and required conditions for each dimension. After the memory and explanation reviews, the matrix has **121 P, 0 F, 0 N and 1,463 ? cells**. This is research coverage, not a product score. Every P has a source-register ID, claim-specific URL, basis, method, evidence class and audit scope. The scope records the public reading mode, dated surface, untested plan entitlements, region and reuse limits. A dated page is not a pinned software release.

## How to apply the tests

The scenario is the execution test for F. Documentary evidence can support only P and must name its narrower boundary. For F, record the exact software version or dated UI, plan, access mode, input fixture and replayable output locator. For N, obtain explicit contrary documentation or a bounded negative result that rules out configuration/access errors. Failed access alone stays ?.

The existing 48 dimension IDs and scenarios remain the working taxonomy for this documentary comparison. For `rag`, distinguish retrieval construction from evaluation; for `mcp`, distinguish registry discovery from a client/server tool exchange; for `export`, distinguish catalog data from a reusable build. A P in one branch does not establish the others. These dimensions must not be added together into an end-to-end capability count. Model release metadata is not immutable serving-version pinning.

For `harness_eval` and `evaluation`, explicitly record whether a future test executed an evaluation or inspected a procedure/result. Documentary inspection remains P; it does not become an exercised evaluation. An exercised `benchmarks` retrieval establishes retrieval, not replication. The `tco` label does not override its test's included/excluded cost scope: a same-horizon comparison with exclusions is a partial comparison, not complete priced coverage. Missing active costs remain not priced/not sized, never zero. These boundaries retain the original scenarios and prevent stronger conclusions from their broader labels.

## Selected coverage

| Product ID | natural_language | model_search | model_compare | hardware_fit | context | rag | agents | mcp | api_pricing | export |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| benchlm | ? | P | P | ? | ? | ? | ? | ? | P | P |
| harness-bench | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| llmfit | ? | P | P | P | P | ? | ? | ? | ? | P |
| local-ai-planner | ? | ? | ? | P | P | ? | ? | ? | ? | ? |
| flocci | P | P | ? | ? | ? | ? | ? | ? | ? | ? |
| artificial-analysis | ? | ? | P | ? | ? | ? | ? | ? | P | P |
| openrouter | ? | P | P | ? | P | ? | ? | ? | P | P |
| hugging-face | ? | P | P | ? | ? | ? | ? | ? | ? | P |
| arena | ? | ? | P | ? | ? | ? | ? | ? | ? | ? |
| llm-stats | ? | ? | P | ? | ? | ? | ? | ? | P | ? |
| models-dev | ? | P | P | ? | P | ? | ? | ? | P | P |
| canirun-ai | ? | ? | ? | P | ? | ? | ? | ? | ? | ? |
| canrun | ? | ? | ? | P | ? | ? | ? | ? | ? | ? |
| canitrun | ? | ? | ? | P | ? | ? | ? | ? | ? | ? |
| modelfit | ? | P | ? | P | ? | ? | ? | P | ? | P |
| ollama | ? | P | ? | ? | ? | ? | ? | ? | ? | ? |
| gpus-io | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| vast | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| runpod | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| dify | ? | ? | ? | ? | ? | P | P | ? | ? | P |
| langflow | ? | ? | ? | ? | ? | P | P | ? | ? | ? |
| flowise | ? | ? | ? | ? | ? | ? | P | ? | ? | ? |
| n8n | ? | ? | ? | ? | ? | ? | P | ? | ? | P |
| skypilot | ? | ? | ? | ? | ? | ? | ? | ? | ? | P |
| bentoml | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| langfuse | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| ragas | ? | ? | ? | ? | ? | P | ? | ? | ? | ? |
| llamaindex | ? | ? | ? | ? | ? | P | P | ? | ? | ? |
| langchain | ? | ? | ? | ? | ? | ? | P | ? | ? | ? |
| qdrant-bench | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| lm-eval | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| mcp-registry | ? | ? | ? | ? | ? | ? | ? | P | ? | ? |
| unsloth | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |

## #42 requested coverage for all 13 profiled products

All 52 cells were desk-checked against public pages or explicit docs. A ? means the required selection/version recovery behavior is not established; it does not mean unavailable. P is deliberately narrower than #42's complete versioned BuildSnapshot requirement.

| Product ID | saved | share | export | model_versions |
| --- | --- | --- | --- | --- |
| benchlm | ? | P | P | P |
| harness-bench | ? | ? | ? | ? |
| llmfit | P | P | P | ? |
| local-ai-planner | ? | ? | ? | ? |
| flocci | P | ? | ? | ? |
| artificial-analysis | ? | ? | P | P |
| openrouter | ? | ? | P | P |
| hugging-face | ? | ? | P | P |
| models-dev | ? | ? | P | P |
| modelfit | ? | ? | P | P |
| dify | P | P | P | ? |
| n8n | P | P | P | ? |
| skypilot | P | P | P | ? |

The new Dify and n8n documentation supports configuration transfer; BenchLM describes URL-encoded filter views; SkyPilot describes reusable task YAML. Catalog JSON and benchmark result sharing are weaker, distinct forms of portability. See each cell's evidence URL and basis. No configuration round-trip, recipient-permission, immutable dependency-pin or credential-sanitization test is established by these documentary cells. The current in-session #42 receiving review accepts this comparison with constraints, including the separately accepted #66 guest bookmark observation. Its exact current scope and future promotion tests are recorded in [the acceptance audit](mr02-acceptance.md#current-technical-intake-and-remaining-decisions); it does not complete #42 or attribute a response to another assignee.

## Counterexamples and conclusions

- **Overlap exists in documentary model comparison and context metadata.** OpenRouter and Models.dev expose these fields; their cells link exact docs. Neither demonstrates provider limits enforced in a live request. This supports comparing field coverage, not certifying limits.
- **Hardware planning is already documented.** llmfit, ModelFit and the Local AI Planner describe conditional recommendations. ModelFit labels load/speed as estimates; the Local AI Planner explicitly lacks context metadata for its current model set and treats multi-GPU capacity heuristically. These are counterexamples to a “no hardware-aware planner” claim, not verified GPU-sizing formulas.
- **Export/share is not an empty market.** [Dify DSL documentation](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management) and [n8n JSON workflow documentation](https://docs.n8n.io/build/manage-workflows/export-and-import.md) describe transfer mechanisms. Dify excludes knowledge data and tool API keys but can optionally include secret environment variables; n8n warns about credential metadata and imported authentication headers. Neither is established as equivalent to #42's versioned record.
- **Generated advice remains distinct from execution.** The original audit did not have a replayable response in its cited records. Later [accepted #66 receiving evidence](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/66#issuecomment-6248861238) reviewed the actual guest contradiction/bookmark captures: a tool bookmark did not retain a reusable stack in that tested path. The public Ask and Stack Builder pages support the narrower P cells retained here. This amendment does not relabel that other observer's execution, generalize the result to untested tiers, or require the same guest test again.
- **No validated market gap follows from this matrix.** There are no N cells. The claim that a reviewed versioned configuration history is differentiated remains a hypothesis for #57/#58, especially given llmfit's documented benchmark sharing and the community-fit-report counterexamples identified in the owner review.

## Adversarial checks and handoff

The audit checked high-impact advice-versus-execution, registry-versus-runtime, orchestration-versus-hosting, context input-versus-limit, export-versus-reconstruction and version-name-versus-immutable-artifact distinctions. SkyPilot `hosting` and LM Evaluation Harness `evaluation` were narrowed to ? because the cited material established orchestration and model benchmarks, respectively, rather than the selected dimension's stronger behavior. MCP registry remains P only for the explicit discovery branch.

The historical #42 review remains limited to its original revision. [The current acceptance map](mr02-acceptance.md#current-technical-intake-and-remaining-decisions) separately records later actual receiving decisions and named future implementation/evidence choices. Independent final source review, current checks and canonical delivery remain distinct gates. #48 retains source registration; #59 retains the canonical handoff ledger; #57/#58 retain positioning/MVP decisions. The matrix introduces no new contract kinds or compatibility rules.

## CanIRun.ai intake (2026-10-16)

The original intake added 48 cells: three Documented (hardware_fit, hardware_catalog, vram_ram), 45 Unknown. Directory text only; no exercised capability. See the [profile](competitors/canirun-ai.md) and `src-canirun-ai`.

## Memory-boundary correction (2026-10-18)

The `vram_ram` test asks for a memory requirement for one pinned model/runtime configuration, with units and assumptions. The `canirun-ai` cell instead cites a device's memory capacity. Capacity describes available hardware; it cannot support even a documentary claim about how much memory that model/runtime configuration requires. The cell is now **Unknown**, leaving `canirun-ai` with two Documented and 46 Unknown cells. The separate `hardware_catalog` observation remains unchanged.

The correction preserves the original device-capacity basis, source URL, source ID, access date and documentary grade as historical context; it updates only the status and its limitation. It neither infers that CanIRun.ai lacks a memory estimate nor substitutes a new model requirement, benchmark or product execution. All 1,583 other cells and all 48 test definitions remain unchanged. The [current correction record](mr02-acceptance.md#memory-boundary-correction--2026-10-18) separates this classification repair from the broader matrix, receiving and future-intake decisions. The accepted #66 observations retain their separate source and review scope; this correction promotes no cell to Exercised.

## Explanation evidence and current source limits (2026-10-18)

An explanation cell needs a documented reason tied to an input or comparison field, even for P. Artificial Analysis's retained recommender-priority claim does not establish that output, so its explanation is Unknown. This is an evidence boundary, not a finding that its product lacks explanations.

The initial ModelFit homepage basis was similarly insufficient. A separately inspected [published model/GPU result](https://modelfit.io/can-i-run/gpt-oss-20b-on-rtx-4060-ti/) supplies explicit reasons, so that cell remains P with a precise new source/date. Its inconsistent fit/context statements prevent using this review as evidence of sizing correctness. No cell becomes Exercised.

The 2026-10-18 source pass also found a [Flowise wind-down notice](https://flowiseai.com/sunset). The retained agents P describes published construction capabilities; it does not establish current support, service availability or a maintenance commitment. The dated scope and all other cells remain intact. Product-price fields, documentary fit explanations and published evaluation methods continue to require their own qualified consumer evidence before numerical or operational intake.
