# Feature matrix review guide

Snapshot: 2026-10-16. Draft for #49; required owner acceptance remains open.

F = Exercised: bounded test passed with replayable evidence. P = Documented: narrower documentary support, including unverified vendor claims. N = Unsupported: explicit negative evidence under pinned conditions. ? = Unknown. No absence is inferred from silence. The old “Verified Full/Partial” names are retired following [the evidence-owner review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/67#pullrequestreview-5550697545).

[features.json](features.json) retains all 32 entities and 48 dimension IDs. It defines a test and required conditions for each dimension. The current audit has **120 P, 0 F, 0 N and 1,416 ? cells**. This is research coverage, not a product score. Every P has a source-register ID, claim-specific URL, basis, method, evidence class and audit scope. The scope records the public reading mode, dated surface, untested plan entitlements, region and reuse limits. A dated page is not a pinned software release.

## How to apply the tests

The scenario is the execution test for F. Documentary evidence can support only P and must name its narrower boundary. For F, record the exact software version or dated UI, plan, access mode, input fixture and replayable output locator. For N, obtain explicit contrary documentation or a bounded negative result that rules out configuration/access errors. Failed access alone stays ?.

Existing compound taxonomy labels remain unchanged pending owner review. For `rag`, distinguish retrieval construction from evaluation; for `mcp`, distinguish registry discovery from a client/server tool exchange; for `export`, distinguish catalog data from a reusable build. A P in one branch does not establish the others. These dimensions must not be added together into an end-to-end capability count. Model release metadata is not immutable serving-version pinning.

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

The new Dify and n8n documentation supports configuration transfer; BenchLM describes URL-encoded filter views; SkyPilot describes reusable task YAML. Catalog JSON and benchmark result sharing are weaker, distinct forms of portability. See each cell's evidence URL and basis. No round-trip reconstruction, recipient permissions, immutable dependency pinning or credential sanitization test was executed. #42 owner @tynamite must accept or narrow this evidence and choose any remaining execution tests.

## Counterexamples and conclusions

- **Overlap exists in documentary model comparison and context metadata.** OpenRouter and Models.dev expose these fields; their cells link exact docs. Neither demonstrates provider limits enforced in a live request. This supports comparing field coverage, not certifying limits.
- **Hardware planning is already documented.** llmfit, ModelFit and the Local AI Planner describe conditional recommendations. ModelFit labels load/speed as estimates; the Local AI Planner explicitly lacks context metadata for its current model set and treats multi-GPU capacity heuristically. These are counterexamples to a “no hardware-aware planner” claim, not verified GPU-sizing formulas.
- **Export/share is not an empty market.** [Dify DSL documentation](https://docs.dify.ai/en/cloud/use-dify/workspace/app-management) and [n8n JSON workflow documentation](https://docs.n8n.io/build/manage-workflows/export-and-import.md) describe transfer mechanisms. Dify excludes knowledge data and tool API keys but can optionally include secret environment variables; n8n warns about credential metadata and imported authentication headers. Neither is established as equivalent to #42's versioned record.
- **Generated advice remains distinct from execution.** Prior Flocci observations are retained in [the acceptance audit](mr02-acceptance.md), but no replayable captured response was found in the cited records. The public Ask and Stack Builder pages support narrower P claims. RAG execution and constraint handling remain unknown here.
- **No validated market gap follows from this matrix.** There are no N cells. The claim that a reviewed versioned configuration history is differentiated remains a hypothesis for #57/#58, especially given llmfit's documented benchmark sharing and the community-fit-report counterexamples identified in the owner review.

## Adversarial checks and handoff

The audit checked high-impact advice-versus-execution, registry-versus-runtime, orchestration-versus-hosting, context input-versus-limit, export-versus-reconstruction and version-name-versus-immutable-artifact distinctions. SkyPilot `hosting` and LM Evaluation Harness `evaluation` were narrowed to ? because the cited material established orchestration and model benchmarks, respectively, rather than the selected dimension's stronger behavior. MCP registry remains P only for the explicit discovery branch.

Do not treat the #42 narrowing review as acceptance of this revision. [Acceptance map and validation record](mr02-acceptance.md) names outstanding reviewers and follow-up decisions. #48 retains source registration; #59 retains the canonical handoff ledger; #57/#58 retain positioning/MVP decisions. The matrix introduces no new contract kinds or compatibility rules.
