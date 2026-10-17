# T4: Agent Framework

Issue: #25 · Contract: 1.0.0 · Kinds: `agent_framework`
Status: draft · Last researched: 2026-10-16

## Evidence status correction

Evidence metadata corrected at 2026-10-17T02:17:46Z under the [adopted #41 interim policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Checked primary documentation, publisher package metadata, registry entries and source inspection are not independent verification. These catalog claims remain `unverified`; the original facts, versions, source access dates and `checked_at` are unchanged. No qualifying independent corroboration or runtime reproduction was supplied. Vendor capability statements remain documented claims, not measurements.

A proposed constraint may pass on eligible, versioned documentation while its evidence remains unverified. Missing eligible evidence remains unknown; absence from an unmarked capability list does not establish lack of support. Synthetic evaluator results check rule mechanics only and do not verify product behaviour. All rules and contract changes still require central versioned review through #40. Receiving-owner handoffs remain pending and this correction does not satisfy issue completion.

## User decision

Which orchestration approach should run multi-step or tool-using behaviour: a framework or SDK, or no framework (the application drives a provider SDK's tool-use loop itself)?

The answer depends on four joint facts:
- what the selected model and its serving path can do (native tool calling, JSON-schema output, `tool_choice` modes), from #6 and #11;
- which model API surfaces the framework speaks (for example OpenAI Responses vs Chat Completions);
- which MCP transports and protocol revisions the framework's MCP client supports (#27);
- where state, traces and the runtime live (library in the user's process, or a vendor-managed runtime).

Deployment modes covered:
- **API:** no framework, or a thin loop over a provider API. Some providers run tools or MCP servers on their side (OpenAI hosted MCP tools, Anthropic server tools and MCP connector) (A1, A2, A36).
- **Self-hosted:** every candidate below is a library that runs in the user's process or container. Some ship an optional self-hostable server (LangGraph Agent Server, Agno AgentOS, LlamaIndex `llama-agents-server`).
- **Managed:** vendor runtimes exist for some frameworks: LangSmith Deployment, Google Agent Runtime / Cloud Run / GKE, Microsoft Foundry hosted agents, CrewAI AMP, and LlamaIndex deploy targets. These are offerings of the framework vendor or a cloud, not properties of the library.

Out of scope: tool catalog (#26), MCP server packaging (#27), memory semantics (#28).

## Candidate options

Versions are the latest release on the package registry on 2026-10-16. "MCP client transports" lists only transports named in a fetched primary page. "Not documented" means the fetched page did not name it; it does not mean unsupported.

### Matrix

| Candidate (package) | Version (release date) | License (LICENSE file) | Languages | Maintenance | MCP client transports | State / checkpointing | Multi-agent / graph | HITL / approval | Observability | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No framework: OpenAI SDK (`openai`) | 3.31.0 (2026-10-14) | Apache-2.0 (PyPI metadata) | per SDK | active | none in loop; OpenAI-side remote MCP via Responses API | application-owned | application-owned | application-owned | application-owned | A1, A80 |
| No framework: Anthropic SDK (`anthropic`) | 1.15.0 (2026-10-15) | MIT (PyPI metadata) | per SDK | active | none in loop; Anthropic-side MCP connector | application-owned | application-owned | application-owned | application-owned | A2, A80 |
| LangGraph (`langgraph`) | 1.2.15 (2026-10-12); JS `@langchain/langgraph` 1.5.0 (2026-10-12) | MIT | python; typescript (separate package) | active | via LangChain `langchain[mcp]>=1.4.0` (beta): stdio, Streamable HTTP, in-memory; SSE deprecated; WebSocket not supported. `langchain-mcp-adapters` no longer maintained | checkpointers: in-memory, SQLite, Postgres; Store for long-term memory | graph; multi-agent not stated on fetched pages | interrupts | LangSmith; OTel export via `langsmith[otel]` | A6–A16 |
| Microsoft AutoGen (`autogen-agentchat`) | 0.7.5 (2025-09-30) | MIT | python | **maintenance mode**; successor is Microsoft Agent Framework | not assessed | not assessed | yes | not assessed | not assessed | A17, A18 |
| Microsoft Semantic Kernel (`semantic-kernel`) | 1.45.0 (2026-10-06); NuGet `Microsoft.SemanticKernel` 1.81.0 | MIT | python, .NET, Java | **superseded**: README says it "is now Microsoft Agent Framework"; still releasing | MCP plugins (transports not assessed) | not assessed | yes | not assessed | not assessed | A19, A20 |
| Microsoft Agent Framework (`agent-framework`) | 1.22.0 (2026-10-15); NuGet `Microsoft.Agents.AI` 1.25.0 (2026-10-14) | MIT | python, .NET; Go in public preview | active (1.0 GA, LTS commitment) | Python: stdio (`MCPStdioTool`), Streamable HTTP (`MCPStreamableHTTPTool`), WebSocket (`MCPWebsocketTool`); .NET page shows stdio only; Foundry-hosted MCP with approval modes | workflow checkpoints at superstep boundaries; backends not stated | graph and functional workflows; sequential, concurrent, handoff, group | `RequestInfoExecutor` / `ctx.request_info()`; hosted MCP approval | built-in OpenTelemetry | A21–A27 |
| CrewAI (`crewai`) | 1.15.28 (2026-10-14) | MIT | python (>=3.10,<3.14) | active | stdio, SSE, Streamable HTTP (`mcps` field or `MCPServerAdapter`); adapter is tools-only | checkpoints of crews, flows, agents: JSON or SQLite providers | crews and flows | human input / review | depends on `opentelemetry-sdk`; anonymous telemetry by default | A28–A33 |
| OpenAI Agents SDK, Python (`openai-agents`) | 0.24.0 (2026-10-15) | MIT | python | active (pre-1.0) | stdio, Streamable HTTP, SSE (legacy); OpenAI-hosted MCP (`HostedMCPTool`) | Sessions (Redis extra); no graph checkpointing found | handoffs, agents-as-tools | built in | own tracing, exported to OpenAI by default; custom processors; unavailable under ZDR | A34–A38 |
| OpenAI Agents SDK, JS (`@openai/agents`) | 0.20.0 (2026-10-08) | MIT | typescript | active (pre-1.0) | stdio, Streamable HTTP, SSE (legacy, "deprecated by the MCP project"); hosted MCP | Sessions | handoffs | built in | not assessed | A39–A41 |
| Google ADK (`google-adk`) | 2.12.0 (2026-10-13); JS `@google/adk` 2.3.0 (2026-10-13) | Apache-2.0 | python (>=3.11); TypeScript, Go, Java, Kotlin in separate repos | active | stdio, SSE, Streamable HTTP (`McpToolset`); MCP connections not re-established on session restore | SessionService: in-memory, database, Vertex/Agent Runtime | graph workflow runtime; hierarchies; fan-out/fan-in, loops, retry | tool confirmation | OpenTelemetry, OTLP, Cloud Trace | A42–A49 |
| PydanticAI (`pydantic-ai`) | 2.57.0 (2026-10-16) | MIT | python (>=3.11) | active | Streamable HTTP, SSE (deprecated), stdio | durable execution on Temporal, DBOS, Prefect and six others | not assessed | deferred tools with approval | OpenTelemetry-native; Logfire optional | A50–A56 |
| LlamaIndex (`llama-index-core`, `llama-index-workflows`) | core 0.14.25 (2026-09-21); workflows 2.26.0 (2026-10-11) | MIT | python; TypeScript `llamaindex` 0.12.1 (2025-12-02) | active; vendor focus now document parsing | `llama-index-tools-mcp` 0.6.0: Streamable HTTP, SSE, stdio | workflows: "save and resume runs from a file, or connect to a database" | `AgentWorkflow` handoff | via `llama-agents-server` | not assessed | A57–A60 |
| Hugging Face smolagents (`smolagents`) | 1.26.0 (2026-05-29) | Apache-2.0 | python | active, slower cadence (no release for 4.5 months) | stdio, Streamable HTTP, SSE (`MCPClient`, `mcp` extra) | agent memory in process | multi-agent hierarchies | not assessed | `telemetry` extra: OpenTelemetry + OpenInference | A61–A63 |
| Agno (`agno`) | 3.1.3 (2026-10-12) | Apache-2.0 | python | active | stdio, SSE (not recommended), Streamable HTTP (`agno[mcp]`, `mcp>=2.1`) | `db`: Postgres, SQLite, MySQL, Mongo, Redis, JSON and others | not assessed | human approval | OpenTelemetry traces; telemetry event per run by default | A64–A67 |
| Mastra (`@mastra/core`) | 1.78.0 (2026-10-15) | Apache-2.0 core; `ee/` directories under Mastra Enterprise License | typescript | active | `@mastra/mcp` 2.4.1: stdio, Streamable HTTP; SSE not documented | storage-backed suspend/resume | graph workflows (`.then()`, `.branch()`, `.parallel()`) | suspend and resume | OTel-compatible spans; Langfuse, Arize, platform exporters | A68–A71 |
| Strands Agents (`strands-agents`) | 1.61.1 (2026-10-15); TS `@strands-agents/sdk` 1.21.0 (2026-10-14) | Apache-2.0 | python, typescript | active | stdio, Streamable HTTP, SSE (Python and TypeScript) | session managers: file, S3, AgentCore Memory, custom | Graph, Swarm, agents-as-tools | not assessed | OpenTelemetry, OTLP and console exporters | A72–A76 |

Notes on the "other" slots: Mastra (the only TypeScript-only framework evaluated) and Strands Agents (Python and TypeScript, no hosted control plane) were added. Considered but not evaluated: Claude Agent SDK (`claude-agent-sdk` 0.2.168, alpha; it drives the Claude Code CLI, and the npm package's license is "SEE LICENSE IN README.md") (A82); Vercel AI SDK (`ai` 7.0.142, Apache-2.0), a toolkit rather than an agent runtime (A83); AG2 (`ag2` 1.1.2, Apache-2.0), a separately maintained AutoGen lineage (A81).

### Per-candidate notes

- **No framework (direct provider SDK).** The application runs the loop: the model returns tool calls, the application executes them and sends results back (A1, A2). Anthropic documents a "Tool Runner" that automates the round trip in its SDKs, and server tools that run on Anthropic's side (A2). OpenAI says to assume several calls per response (A1). Anthropic exposes `disable_parallel_tool_use` (A2). State, retries, approval and tracing are application code. Portability is lowest across providers because each API's tool format differs, but there is no framework dependency to migrate.
- **LangGraph.** Low-level graph runtime: "you don't need to use LangChain to use LangGraph" (A16). Checkpointers give human-in-the-loop, time travel and fault tolerance. In-memory checkpoints are lost on restart; Postgres is recommended for production (A9).
  - MCP is not in LangGraph itself. It comes from LangChain's `langchain.mcp` (beta, `langchain[mcp]>=1.4.0`, targets the 2026-07-28 MCP spec with fallback) (A13, A14). `langchain-mcp-adapters` 0.3.2 is "no longer actively maintained" (A12).
  - Managed: LangSmith Deployment in four modes: Cloud (Plus plan or above), Hybrid, Self-hosted (Enterprise plan), and a Standalone server that needs PostgreSQL, Redis and a LangSmith license (A10).
- **AutoGen.** "AutoGen is now in maintenance mode. It will not receive new features or enhancements and is community managed going forward. New users should start with Microsoft Agent Framework" (A17). The last PyPI release is 0.7.5 on 2025-09-30 (A18). Do not offer it for new builds.
- **Semantic Kernel.** README: "Semantic Kernel is now Microsoft Agent Framework!", with a migration guide (A19). Releases continue (Python 1.45.0, .NET 1.81.0) (A20). Whether it is "maintenance" in the AutoGen sense is not stated. Treat it as superseded for new builds.
- **Microsoft Agent Framework (MAF).** Python and .NET, with Go in public preview: "Declarative agents, RAG, CodeAct, and functional workflows are not yet available" in Go (A24). Providers: "Microsoft Foundry, Anthropic, Azure OpenAI, OpenAI, Ollama, and more" (A24).
  - Python MCP client classes: `MCPStdioTool`, `MCPStreamableHTTPTool`, `MCPWebsocketTool`. They need `mcp --pre` (and `mcp[ws] --pre` for WebSocket), which is a version-dependent prerequisite (A25). There is no separate SSE class.
  - Hosting samples cover A2A, Foundry hosted agents, and a separate Durable Task / Azure Functions extension (A21).
- **CrewAI.** Native SDKs for OpenAI, Anthropic, Gemini, Azure, Bedrock and Snowflake Cortex. "All other providers are powered by LiteLLM", including Ollama (A32). "Structured output support varies by provider and model" (A32).
  - Version-dependent limitations from PyPI metadata (A28): `crewai` 1.15.28 pins `mcp~=1.28.1` (the MCP Python SDK v1 line, now in maintenance per A4) and the `anthropic` extra pins `anthropic~=0.73.0`, while the current `anthropic` release is 1.15.0 (A80).
  - Checkpoint auto-writes are "best-effort: a failed write is logged and the run continues" (A33).
  - Commercial control plane: CrewAI AMP, on-premise or cloud (A30).
- **OpenAI Agents SDK.** "Provider-agnostic, supporting the OpenAI Responses and Chat Completions APIs, as well as 100+ other LLMs" through any-llm or LiteLLM (A35). The Responses API is the default, but "many other LLM providers still do not support it", so the user must switch to Chat Completions (A37).
  - On Chat Completions, Responses-only fields are "silently dropp[ed]" unless strict feature validation is enabled (A37).
  - Some OpenAI-compatible providers stream tool-call deltas unreliably; a buffering option exists (A37).
  - Tracing is on by default, uploads to OpenAI, and is "unavailable for organizations that use OpenAI's APIs under a Zero Data Retention (ZDR) policy" (A38).
  - MCP: supports `mcp>=1.19.0,<3` (A36).
- **Google ADK.** "While optimized for Gemini, ADK is model-agnostic" (A42). Connectors: LiteLLM, Ollama, vLLM, Apigee, LiteRT-LM (A44).
  - Ollama: use `ollama_chat`, because plain `ollama` "can result in unexpected behaviors such as infinite tool call loops" (A45).
  - MCP: production agents "must define McpToolset synchronously", and restored sessions "do not automatically re-establish active MCP connections" (A43).
  - Managed targets: Agent Runtime, Cloud Run, GKE (A48).
- **PydanticAI.** Model profiles encode per-model tool-schema restrictions. "Compatibility with one API does not imply support for the other or for every OpenAI feature" (A54).
  - vLLM tool calling "requires server configuration" (`--enable-auto-tool-choice`, `--tool-call-parser`) (A54).
  - For `gpt-6-sol` and `gpt-6-luna`, Chat Completions supports function calling only with `openai_reasoning_effort='none'` (A53).
- **LlamaIndex.** `FunctionAgent` "uses an LLM provider's function/tool calling capabilities"; `ReActAgent` and `CodeActAgent` "use different prompting strategies to execute tools" (A60). The README states the vendor's current focus is document parsing (LlamaParse) (A57). Deploy targets via `llamactl`: LlamaParse, AWS Bedrock AgentCore, or own infrastructure (A58).
- **smolagents.** `CodeAgent` writes actions as Python code; `ToolCallingAgent` "leverages built-in tool calling methods" (A61). Local code execution carries risk: "no local python sandbox can ever be completely secure" (A63). Relevant to #35.
- **Agno.** Framework plus the AgentOS runtime (REST API, Postgres, MCP server, control plane) run with Docker (A64). It "sends a telemetry event per agent run"; opt out with `AGNO_TELEMETRY=false` (A64). Storage note: "session storage support does not imply support for every AgentOS domain" (A67).
- **Mastra.** TypeScript only. Model routing to "40+ providers" (A69). Dual license: `ee/` directories are under the Mastra Enterprise License, which "require a valid enterprise license for production" (A68, A69).
- **Strands Agents.** "Runs in your process with no hosted control plane" (A73). Providers include Bedrock, Anthropic, OpenAI, Gemini, LiteLLM, llama.cpp and Ollama (A73). Multi-agent session managers "only track the current state of the Graph/Swarm execution" (A76).

### Inference-engine prerequisites (input from #11)

"OpenAI-compatible HTTP" is not the same as feature parity:
- **vLLM:** auto tool choice needs `--enable-auto-tool-choice` plus a model-specific `--tool-call-parser`. `required` is supported only from `vllm>=0.8.3`. With `tool_choice="auto"`, schema-constrained decoding applies only when a tool sets `strict: true` or the server sets `--tool-strict-level`. "Most OpenAI-compatible clients and agent frameworks never set `strict` on their tools, so ... malformed markup can leak into the response" (A77).
- **Ollama:** `/v1/chat/completions` supports `tools` and `response_format` but not `tool_choice`. `/v1/responses` (since v0.13.3) is non-stateful only (A79). The native API supports parallel tool calls and streaming tool calls (A78).
- **LiteLLM** (1.105.1) is the route CrewAI, ADK, smolagents and the OpenAI Agents SDK use for many non-native providers (A32, A35, A44, A61, A84). Feature pass-through was not assessed.

## Comparison fields

The v1 `spec_agent_framework` has one required field (`programming_languages`) and four optional booleans. The issue's comparison fields map as follows.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/id` | string, `agent_framework.<slug>` | one item per package and language | — | Multi-language frameworks ship separate packages with different versions (MAF Python 1.22.0 vs .NET 1.25.0) |
| `/version` | string, exact registry version | see matrix | per row | v1 allows one version per ID; per-language versions need separate IDs |
| `/status` | enum `active, preview, deprecated, retired` | AutoGen → `deprecated` (maintenance mode); Semantic Kernel → see open questions | A17, A19 | v1 has no "maintenance" or "superseded" value |
| `/license/spdx_id` | SPDX string | MIT or Apache-2.0 for all evaluated, except Mastra (dual) | per row | Mastra cannot be expressed as one SPDX ID; Claude Agent SDK npm license not SPDX |
| `/spec/programming_languages` | array of enum `python, typescript, javascript, go, rust, java, other` | see matrix | per row | No `csharp`/`dotnet` or `kotlin`; MAF, SK and ADK need `other` |
| `/spec/supports_tool_execution` | boolean | true for all evaluated | per row | Does not say native vs prompted (ReAct/code) tool calling |
| `/spec/supports_mcp` | boolean | true where a first-party MCP client is documented | per row | Cannot express transports, protocol revision, or "via companion package in beta" (LangGraph) |
| `/spec/supports_multi_agent` | boolean | true where documented | per row | Handoff vs graph vs hosted subagents are not distinguished |
| `/spec/supports_memory` | boolean | **not populated** in proposals | — | Ambiguous: built-in conversation state, a long-term store, or integration with an external `memory_store`? See compatibility proposals |
| `/settings/agent_count`, `/max_iterations`, `/timeout_ms` (selection) | integers | no change proposed | — | Approval policy and checkpoint backend are not settings |
| supported model APIs (note only) | proposed enum array `openai_responses, openai_chat_completions, anthropic_messages, gemini, bedrock_converse, ollama_native, litellm, other` | see notes | A35, A37, A44, A54 | Needed for rule `rule.t4.model.api.surface` |
| tool-calling approach (note only) | proposed enum array `native, prompted_react, code_action, provider_hosted` | native for most; LlamaIndex ReAct/CodeAct; smolagents CodeAgent; OpenAI/Anthropic hosted tools | A2, A36, A60, A61 | Determines whether model `supports_tool_calling` is a hard prerequisite |
| state / persistence (note only) | proposed enum array `in_memory, sqlite, postgres, redis, object_store, file, managed, durable_engine` | see matrix | A9, A33, A47, A55, A67, A76 | Overlaps #28 `backing_type`; needs #28 agreement |
| MCP client transports (note only) | array of enum `stdio, streamable_http, sse` (reuse `spec_mcp_server.transport`) plus `websocket`, `in_memory`, `provider_hosted` | see matrix | per row | `sse` is not a standard transport in MCP 2026-07-28 (A3) |
| MCP protocol revisions (note only) | array of date strings, e.g. `2025-11-25`, `2026-07-28` | LangChain targets 2026-07-28 with fallback; mcp SDK v2 serves both | A4, A14 | Per-framework revisions mostly unknown |
| observability hooks (note only) | enum array `otel_native, otlp_export, vendor_tracing, none`; boolean `default_telemetry_egress` | see matrix | A11, A38, A46, A56, A64, A75 | Feeds #38 `monitoring_stack.exporter` |
| managed runtime (note only) | list of hosting refs | LangSmith Deployment, Agent Runtime/Cloud Run/GKE, Foundry, CrewAI AMP, LlamaParse/AgentCore | A10, A21, A30, A48, A58 | Plans and prices not captured |
| human-in-the-loop (note only) | boolean | see matrix | per row | — |

## Evidence

All entries accessed on 2026-10-16. Grades follow `docs/RESEARCH_METHOD.md` and the adopted #41 interim policy above. Versions and dates come from the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`), the npm registry (`https://registry.npmjs.org/<pkg>`) and the NuGet v3 API. Licenses come from LICENSE files fetched from raw.githubusercontent.com. Capability claims are vendor documentation, graded Primary documentation because they describe the vendor's own software. No candidate was installed or executed.

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| A1 | OpenAI, https://developers.openai.com/api/docs/guides/function-calling | 2026-10-16 | current | Primary documentation | `parallel_tool_calls` and argument streaming not on this page |
| A2 | Anthropic, https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | 2026-10-16 | current | Primary documentation | Tool Runner details on a linked page, not fetched |
| A3 | MCP project, https://modelcontextprotocol.io/specification/2026-07-28/basic/transports | 2026-10-16 | spec 2026-07-28 | Primary documentation | — |
| A4 | MCP project, https://py.sdk.modelcontextprotocol.io/whats-new/ | 2026-10-16 | Python SDK v2 | Primary documentation | — |
| A5 | PyPI, https://pypi.org/pypi/mcp/json | 2026-10-16 | 2.3.0 (2026-10-02); 2.0.0 (2026-07-28) | Primary documentation | — |
| A6 | PyPI, https://pypi.org/pypi/langgraph/json | 2026-10-16 | 1.2.15 (2026-10-12) | Primary documentation | — |
| A7 | LangChain, https://raw.githubusercontent.com/langchain-ai/langgraph/main/LICENSE | 2026-10-16 | main | Primary documentation | — |
| A8 | LangChain, https://github.com/langchain-ai/langgraph/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| A9 | LangChain, https://docs.langchain.com/oss/python/langgraph/persistence | 2026-10-16 | current | Primary documentation | Durability-modes section empty on fetch |
| A10 | LangChain, https://docs.langchain.com/langsmith/deployments | 2026-10-16 | current | Primary documentation | No prices |
| A11 | LangChain, https://docs.langchain.com/langsmith/trace-with-opentelemetry | 2026-10-16 | langsmith ≥0.4.1 | Primary documentation | — |
| A12 | LangChain, https://github.com/langchain-ai/langchain-mcp-adapters/blob/main/README.md | 2026-10-16 | 0.3.2 (PyPI 2026-08-06) | Primary documentation | Unmaintained |
| A13 | LangChain, https://docs.langchain.com/oss/python/migrate/langchain-mcp-adapters | 2026-10-16 | langchain ≥1.4.0 | Primary documentation | Beta API |
| A14 | LangChain, https://www.langchain.com/blog/mcp-in-langchain-stateless-protocol-elicitation-and-more | 2026-10-16 | published 2026-09-03 | Vendor claim | Blog |
| A15 | npm, https://registry.npmjs.org/@langchain/langgraph | 2026-10-16 | 1.5.0 (2026-10-12), MIT | Primary documentation | — |
| A16 | LangChain, https://docs.langchain.com/oss/python/langgraph/overview | 2026-10-16 | current | Primary documentation | No multi-agent statement |
| A17 | Microsoft, https://github.com/microsoft/autogen/blob/main/README.md and https://raw.githubusercontent.com/microsoft/autogen/main/LICENSE-CODE | 2026-10-16 | main | Primary documentation | — |
| A18 | PyPI, https://pypi.org/pypi/autogen-agentchat/json | 2026-10-16 | 0.7.5 (2025-09-30) | Primary documentation | — |
| A19 | Microsoft, https://github.com/microsoft/semantic-kernel/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| A20 | PyPI https://pypi.org/pypi/semantic-kernel/json; NuGet https://api.nuget.org/v3-flatcontainer/microsoft.semantickernel/index.json | 2026-10-16 | 1.45.0 (2026-10-06); .NET 1.81.0 (date not fetched) | Primary documentation | — |
| A21 | Microsoft, https://github.com/microsoft/agent-framework/blob/main/README.md | 2026-10-16 | main | Primary documentation | README also mentions Go in one sentence |
| A22 | Microsoft, https://raw.githubusercontent.com/microsoft/agent-framework/main/LICENSE; https://pypi.org/pypi/agent-framework/json | 2026-10-16 | 1.22.0 (2026-10-15) | Primary documentation | — |
| A23 | NuGet, https://api.nuget.org/v3/registration5-gz-semver2/microsoft.agents.ai/index.json | 2026-10-16 | 1.25.0 (2026-10-14), MIT | Primary documentation | — |
| A24 | Microsoft, https://learn.microsoft.com/en-us/agent-framework/user-guide/overview | 2026-10-16 | current | Primary documentation | — |
| A25 | Microsoft, https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools | 2026-10-16 | current | Primary documentation | .NET transports beyond stdio not stated |
| A26 | Microsoft, https://learn.microsoft.com/en-us/agent-framework/agents/tools/hosted-mcp-tools | 2026-10-16 | current | Primary documentation | — |
| A27 | Microsoft, https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/ | 2026-10-16 | current | Primary documentation | Checkpoint backends not on page |
| A28 | PyPI, https://pypi.org/pypi/crewai/json | 2026-10-16 | 1.15.28 (2026-10-14) | Primary documentation | Dependency pins read from `requires_dist` |
| A29 | CrewAI, https://raw.githubusercontent.com/crewAIInc/crewAI/main/LICENSE | 2026-10-16 | main | Primary documentation | MIT text without a title line; README names MIT |
| A30 | CrewAI, https://github.com/crewAIInc/crewAI/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| A31 | CrewAI, https://docs.crewai.com/en/mcp/overview | 2026-10-16 | current | Primary documentation | — |
| A32 | CrewAI, https://docs.crewai.com/en/concepts/llms | 2026-10-16 | current | Primary documentation | vLLM not mentioned |
| A33 | CrewAI, https://docs.crewai.com/en/concepts/checkpointing.md | 2026-10-16 | current | Primary documentation | — |
| A34 | PyPI https://pypi.org/pypi/openai-agents/json; https://raw.githubusercontent.com/openai/openai-agents-python/main/LICENSE | 2026-10-16 | 0.24.0 (2026-10-15) | Primary documentation | — |
| A35 | OpenAI, https://github.com/openai/openai-agents-python/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| A36 | OpenAI, https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/mcp.md | 2026-10-16 | main | Primary documentation | — |
| A37 | OpenAI, https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/models/index.md | 2026-10-16 | main | Primary documentation | — |
| A38 | OpenAI, https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tracing.md | 2026-10-16 | main | Primary documentation | OTel support not assessed |
| A39 | npm https://registry.npmjs.org/@openai/agents; https://raw.githubusercontent.com/openai/openai-agents-js/main/LICENSE | 2026-10-16 | 0.20.0 (2026-10-08) | Primary documentation | — |
| A40 | OpenAI, https://github.com/openai/openai-agents-js/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| A41 | OpenAI, https://raw.githubusercontent.com/openai/openai-agents-js/main/docs/src/content/docs/guides/mcp.mdx | 2026-10-16 | main | Primary documentation | — |
| A42 | PyPI https://pypi.org/pypi/google-adk/json; https://github.com/google/adk-python/blob/main/README.md; https://raw.githubusercontent.com/google/adk-python/main/LICENSE | 2026-10-16 | 2.12.0 (2026-10-13) | Primary documentation | — |
| A43 | Google, https://adk.dev/tools-custom/mcp-tools/index.md | 2026-10-16 | current | Primary documentation | Fetched via WebFetch (curl blocked) |
| A44 | Google, https://adk.dev/agents/models/index.md | 2026-10-16 | current | Primary documentation | — |
| A45 | Google, https://adk.dev/agents/models/ollama/index.md | 2026-10-16 | current | Primary documentation | — |
| A46 | Google, https://adk.dev/observability/traces/index.md | 2026-10-16 | current | Primary documentation | — |
| A47 | Google, https://adk.dev/sessions/session/index.md | 2026-10-16 | current | Primary documentation | — |
| A48 | Google, https://adk.dev/deploy/index.md | 2026-10-16 | current | Primary documentation | — |
| A49 | npm, https://registry.npmjs.org/@google/adk | 2026-10-16 | 2.3.0 (2026-10-13), Apache-2.0 | Primary documentation | — |
| A50 | PyPI https://pypi.org/pypi/pydantic-ai/json; https://raw.githubusercontent.com/pydantic/pydantic-ai/main/LICENSE | 2026-10-16 | 2.57.0 (2026-10-16) | Primary documentation | — |
| A51 | Pydantic, https://github.com/pydantic/pydantic-ai/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| A52 | Pydantic, https://raw.githubusercontent.com/pydantic/pydantic-ai/main/docs/mcp/client.md | 2026-10-16 | main | Primary documentation | — |
| A53 | Pydantic, https://raw.githubusercontent.com/pydantic/pydantic-ai/main/docs/models/openai.md | 2026-10-16 | main | Primary documentation (for PydanticAI behaviour) | Statements about OpenAI model behaviour are second-hand; #6 should confirm them from OpenAI documentation |
| A54 | Pydantic, https://raw.githubusercontent.com/pydantic/pydantic-ai/main/docs/models/compatible-apis.md | 2026-10-16 | main | Primary documentation | — |
| A55 | Pydantic, https://raw.githubusercontent.com/pydantic/pydantic-ai/main/docs/deferred-tools.md | 2026-10-16 | main | Primary documentation | — |
| A56 | Pydantic, https://raw.githubusercontent.com/pydantic/pydantic-ai/main/docs/logfire.md | 2026-10-16 | main | Primary documentation | — |
| A57 | PyPI https://pypi.org/pypi/llama-index-core/json; https://github.com/run-llama/llama_index/blob/main/README.md; https://raw.githubusercontent.com/run-llama/llama_index/main/LICENSE | 2026-10-16 | 0.14.25 (2026-09-21) | Primary documentation | — |
| A58 | PyPI https://pypi.org/pypi/llama-index-workflows/json; https://github.com/run-llama/workflows-py/blob/main/README.md | 2026-10-16 | 2.26.0 (2026-10-11) | Primary documentation | Repository redirects to `llama-agents` |
| A59 | LlamaIndex, https://raw.githubusercontent.com/run-llama/llama_index/main/llama-index-integrations/tools/llama-index-tools-mcp/README.md | 2026-10-16 | 0.6.0 (PyPI 2026-08-31) | Primary documentation | — |
| A60 | LlamaIndex, https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/index.md | 2026-10-16 | current | Primary documentation | Requirement for tool-calling models is implied, not stated |
| A61 | PyPI https://pypi.org/pypi/smolagents/json; https://github.com/huggingface/smolagents/blob/main/README.md; https://raw.githubusercontent.com/huggingface/smolagents/main/LICENSE | 2026-10-16 | 1.26.0 (2026-05-29) | Primary documentation | — |
| A62 | Hugging Face, https://raw.githubusercontent.com/huggingface/smolagents/main/docs/source/en/tutorials/tools.md | 2026-10-16 | main | Primary documentation | — |
| A63 | Hugging Face, https://raw.githubusercontent.com/huggingface/smolagents/main/docs/source/en/tutorials/secure_code_execution.md | 2026-10-16 | main | Primary documentation | — |
| A64 | PyPI https://pypi.org/pypi/agno/json; https://github.com/agno-agi/agno/blob/main/README.md; https://raw.githubusercontent.com/agno-agi/agno/main/LICENSE | 2026-10-16 | 3.1.3 (2026-10-12) | Primary documentation | — |
| A65 | Agno, https://docs.agno.com/tools/mcp/transports/sse.md | 2026-10-16 | current | Primary documentation | — |
| A66 | Agno, https://docs.agno.com/tools/mcp/transports/streamable_http.md | 2026-10-16 | current | Primary documentation | — |
| A67 | Agno, https://docs.agno.com/runtime/storage | 2026-10-16 | current | Primary documentation | — |
| A68 | npm https://registry.npmjs.org/@mastra/core; https://raw.githubusercontent.com/mastra-ai/mastra/main/LICENSE.md | 2026-10-16 | 1.78.0 (2026-10-15) | Primary documentation | `ee/LICENSE` terms not read |
| A69 | Mastra, https://github.com/mastra-ai/mastra/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| A70 | Mastra, https://mastra.ai/reference/tools/client/llms.txt; npm https://registry.npmjs.org/@mastra/mcp | 2026-10-16 | @mastra/mcp 2.4.1 (2026-10-15) | Primary documentation | SSE not mentioned |
| A71 | Mastra, https://mastra.ai/docs/observability/overview | 2026-10-16 | current | Primary documentation | OTLP not named |
| A72 | PyPI https://pypi.org/pypi/strands-agents/json; npm https://registry.npmjs.org/@strands-agents/sdk; https://raw.githubusercontent.com/strands-agents/harness-sdk/main/LICENSE.APACHE | 2026-10-16 | 1.61.1 (2026-10-15); TS 1.21.0 (2026-10-14) | Primary documentation | Repo moved to `strands-agents/harness-sdk` |
| A73 | AWS, https://github.com/strands-agents/sdk-python/blob/main/README.md (monorepo README) and https://raw.githubusercontent.com/strands-agents/harness-sdk/main/strands-py/README.md | 2026-10-16 | main | Primary documentation | — |
| A74 | AWS, https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/ | 2026-10-16 | current | Primary documentation | — |
| A75 | AWS, https://strandsagents.com/docs/user-guide/observability-evaluation/traces/index.md | 2026-10-16 | current | Primary documentation | — |
| A76 | AWS, https://strandsagents.com/docs/user-guide/concepts/agents/session-management/index.md | 2026-10-16 | current | Primary documentation | — |
| A77 | vLLM, https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/tool_calling.md; https://pypi.org/pypi/vllm/json | 2026-10-16 | main; 0.31.0 (2026-10-05) | Primary documentation | Main-branch docs may run ahead of the release |
| A78 | Ollama, https://raw.githubusercontent.com/ollama/ollama/main/docs/capabilities/tool-calling.mdx | 2026-10-16 | main | Primary documentation | Server version not pinned |
| A79 | Ollama, https://raw.githubusercontent.com/ollama/ollama/main/docs/api/openai-compatibility.mdx | 2026-10-16 | main | Primary documentation | Server version not pinned |
| A80 | PyPI, https://pypi.org/pypi/openai/json and https://pypi.org/pypi/anthropic/json | 2026-10-16 | openai 3.31.0 (2026-10-14); anthropic 1.15.0 (2026-10-15) | Primary documentation | — |
| A81 | PyPI, https://pypi.org/pypi/ag2/json | 2026-10-16 | 1.1.2 (2026-10-03), Apache-2.0 | Primary documentation | Not evaluated |
| A82 | PyPI https://pypi.org/pypi/claude-agent-sdk/json; https://github.com/anthropics/claude-agent-sdk-python/blob/main/README.md; npm https://registry.npmjs.org/@anthropic-ai/claude-agent-sdk | 2026-10-16 | 0.2.168 (2026-10-15); npm 0.3.301 | Primary documentation | Not evaluated |
| A83 | npm, https://registry.npmjs.org/ai | 2026-10-16 | 7.0.142 (2026-10-15), Apache-2.0 | Primary documentation | Not evaluated |
| A84 | PyPI, https://pypi.org/pypi/litellm/json | 2026-10-16 | 1.105.1 (2026-10-14), MIT | Primary documentation | Feature pass-through not assessed |

## Compatibility proposals

These rules are proposed for review by #40 using the [rule proposal template](../../templates/rule-proposal.md).
- **Source-checked (unverified)** means the cited primary text supports the assertion.
- **Hypothesis** means the assertion needs a definition, measurement or contract field that does not exist yet.

Outcome (`pass/fail/unknown/skipped`) is produced by evaluation; severity (`info/warning/error`) is a property of the rule. All JSON blocks below were checked against the `rules` item schema of `contracts/v1/schemas/ruleset.schema.json`.

### Assessment of the baseline T4 rules

| Baseline rule | Problem found | Proposal |
| --- | --- | --- |
| `rule.agent.tools.framework` | A no-framework build (direct SDK loop, A1, A2) has tools but no `agent_framework` selection, so this rule fails with `error` and blocks a valid architecture. It only reads the `primary` tool; tools selected under other roles are never checked. `supports_tool_execution` is true for every framework evaluated, so it does not discriminate. | Keep, but add an explicit "direct orchestration" option (see `rule.t4.direct.orchestration`). Move the discriminating check to the model and engine (`rule.t4.model.toolcalling`, `rule.t4.engine.toolcalling`). |
| `rule.agent.mcp.framework` | (1) A boolean cannot express transports: MAF Python has no SSE class (A25); LangChain has no WebSocket (A13); Mastra documents stdio and Streamable HTTP only (A70). (2) It cannot express protocol revision: the 2026-07-28 spec changed the session model (A3), and CrewAI pins the v1 SDK (A28). (3) Provider-hosted MCP (OpenAI hosted MCP, Anthropic MCP connector, Foundry hosted MCP) makes the provider the MCP client, so "framework supports MCP" is the wrong test (A2, A26, A36). (4) Primary role only. | Refine with `rule.t4.mcp.transport.match` and `rule.t4.mcp.protocol.revision` (need #40); interim `rule.t4.mcp.transport.sse-deprecated` in mcp-servers.md (v1-valid). |
| `rule.memory.framework.compatibility` | `supports_memory` is ambiguous. Every candidate keeps some conversation state; what differs is which external backends it can use (LangGraph checkpointers, ADK SessionService, Agno `db`, Strands session managers) (A9, A47, A67, A76). Proposals here leave it unset rather than guess. | Replace with `rule.t4.memory.backend` (needs #40 and #28). |

### Source-checked (unverified), expressible in v1

#### rule.t4.model.toolcalling: native tool calling required by the selected model

- Participating kinds, roles, and JSON pointers: `agent_framework` primary `/id`; `tool` primary `/id` or `mcp_server` primary `/id`; catalog `model` primary `/spec/supports_tool_calling`. **`spec_model.supports_tool_calling` exists in v1**, so this rule needs no contract change.
- Applicability condition: a framework is selected and at least one tool or MCP server is selected.
- Assertion and source evidence: model `supports_tool_calling == true`. Native tool loops depend on the model's tool-call output (A1, A2, A60 `FunctionAgent`, A61 `ToolCallingAgent`).
- Severity: `warning`, not `error`, because prompted ReAct and code-action agents (LlamaIndex `ReActAgent`/`CodeActAgent`, smolagents `CodeAgent`) execute tools without native tool calling (A60, A61). Upgrade to `error` once `rule.t4.toolcalling.mode` can tell the modes apart.
- Missing-data behaviour: the model field is optional, so it is often unknown. `on_unknown: review`.
- Explanation and remediation: select a model with tool calling, or a framework mode that uses prompted or code actions.
- Dependency edges and affected consumers: `dep.agent_framework.model`; #6 must populate the field.
- Passing example (synthetic): model `supports_tool_calling: true` with a tool selected → pass.
- Failing example (synthetic): model `supports_tool_calling: false` with a tool selected → fail / warning.
- Unknown / non-applicable example: field absent → unknown; no tool or MCP server selected → skipped.
- Version and migration impact: none; additive.

```json
{
  "id": "rule.t4.model.toolcalling",
  "severity": "warning",
  "applies_when": {"op": "all", "args": [
    {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "agent_framework", "role": "primary", "pointer": "/id"}}},
    {"op": "any", "args": [
      {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "tool", "role": "primary", "pointer": "/id"}}},
      {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "mcp_server", "role": "primary", "pointer": "/id"}}}
    ]}
  ]},
  "assert": {"op": "eq", "left": {"ref": {"scope": "catalog", "kind": "model", "role": "primary", "pointer": "/spec/supports_tool_calling"}}, "right": {"literal": true}},
  "on_unknown": "review",
  "message": "The selected model is not recorded as supporting native tool calling; tool-using agents may fail unless the framework uses prompted or code-action tools.",
  "remediation": "Select a model with tool calling, or use a framework mode that does not rely on native tool calls (for example a ReAct or code-action agent).",
  "affected_kinds": ["agent_framework", "model", "tool", "mcp_server"],
  "owner": "t4-research"
}
```

#### rule.t4.engine.toolcalling: self-hosted engine must expose tool calling

- Participating: `agent_framework` primary; `inference_engine` primary catalog `/spec/supports_tool_calling` (exists in v1).
- Applicability: a framework, an inference engine, and a tool or MCP server are all selected.
- Assertion: engine `supports_tool_calling == true`. vLLM needs `--enable-auto-tool-choice` plus a parser (A77, A54). Ollama's OpenAI endpoint has `tools` but not `tool_choice` (A79).
- Severity: `warning`. The boolean cannot capture server flags or parser choice (see `rule.t4.engine.toolchoice`).
- Missing data: `on_unknown: review`.
- Passing / failing / unknown: engine true → pass; false → fail; absent → unknown; no engine (API mode) → skipped.
- Consumers: #11 populates the field and should record the required flags in its note.

```json
{
  "id": "rule.t4.engine.toolcalling",
  "severity": "warning",
  "applies_when": {"op": "all", "args": [
    {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "agent_framework", "role": "primary", "pointer": "/id"}}},
    {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "inference_engine", "role": "primary", "pointer": "/id"}}},
    {"op": "any", "args": [
      {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "tool", "role": "primary", "pointer": "/id"}}},
      {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "mcp_server", "role": "primary", "pointer": "/id"}}}
    ]}
  ]},
  "assert": {"op": "eq", "left": {"ref": {"scope": "catalog", "kind": "inference_engine", "role": "primary", "pointer": "/spec/supports_tool_calling"}}, "right": {"literal": true}},
  "on_unknown": "review",
  "message": "The selected inference engine is not recorded as exposing tool calling; an agent framework cannot receive tool calls from it.",
  "remediation": "Choose an engine with tool-call support and configure it (for vLLM: --enable-auto-tool-choice and a model-specific --tool-call-parser).",
  "affected_kinds": ["agent_framework", "inference_engine", "model", "tool"],
  "owner": "t4-research"
}
```

#### rule.t4.model.jsonschema: structured output depends on JSON-schema support (compatibility example 2, partial)

- Participating: `agent_framework` primary; catalog `model` primary `/spec/supports_json_schema` (exists in v1).
- Assertion: when an agent framework is used, a model without JSON-schema output risks invalid structured output. Primary text: "providers that don't support structured JSON outputs will occasionally produce invalid JSON" (A37); "Structured output support varies by provider and model" (A32).
- Severity: `info`. v1 cannot tell whether the build uses structured output.
- Missing data: `on_unknown: defer`.
- Example: model `supports_json_schema: false` → fail / info; absent → unknown.

```json
{
  "id": "rule.t4.model.jsonschema",
  "severity": "info",
  "applies_when": {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "agent_framework", "role": "primary", "pointer": "/id"}}},
  "assert": {"op": "eq", "left": {"ref": {"scope": "catalog", "kind": "model", "role": "primary", "pointer": "/spec/supports_json_schema"}}, "right": {"literal": true}},
  "on_unknown": "defer",
  "message": "The selected model is not recorded as supporting JSON-schema output; framework structured outputs may be invalid or rejected.",
  "remediation": "Use a model or serving path with JSON-schema output, or validate and retry structured outputs in the framework.",
  "affected_kinds": ["agent_framework", "model"],
  "owner": "t4-research"
}
```

#### SSE MCP servers: consolidated into `rule.t4.mcp.transport.sse-deprecated`

The framework-side evidence for flagging SSE servers is: MCP 2026-07-28 defines only stdio and Streamable HTTP as standard transports (A3); OpenAI Agents JS calls SSE "deprecated by the MCP project" (A41); PydanticAI says "The SSE transport in MCP is deprecated" (A52); LangChain says "Supported, but the transport is deprecated" (A13); MAF Python has no SSE class (A25).

The rule itself is owned by #27 and published once, as `rule.t4.mcp.transport.sse-deprecated` in [mcp-servers.md](mcp-servers.md). An identical framework-side rule was drafted here and removed so the ruleset does not report the same finding twice.

#### rule.t4.framework.lifecycle: deprecated framework

- Participating: catalog `agent_framework` primary `/status` (envelope field).
- Assertion: status in `active` or `preview`. AutoGen is in maintenance mode (A17).
- Severity: `warning`; `on_unknown: review`.

```json
{
  "id": "rule.t4.framework.lifecycle",
  "severity": "warning",
  "applies_when": {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "agent_framework", "role": "primary", "pointer": "/id"}}},
  "assert": {"op": "in", "left": {"ref": {"scope": "catalog", "kind": "agent_framework", "role": "primary", "pointer": "/status"}}, "right": {"literal": ["active", "preview"]}},
  "on_unknown": "review",
  "message": "The selected agent framework is deprecated or retired and will not receive new features.",
  "remediation": "Choose the successor framework (for AutoGen: Microsoft Agent Framework) or accept maintenance-only support.",
  "affected_kinds": ["agent_framework"],
  "owner": "t4-research"
}
```

### Need contract change via #40

#### rule.t4.toolcalling.mode (compatibility example 1, full form) · Source-checked (unverified) evidence, needs #40

Missing field: `spec_agent_framework.tool_calling_modes` (array enum `native, prompted_react, code_action, provider_hosted`). With it, rule 1 can become an `error` that passes for prompted or code modes (A60, A61).

```text
id: rule.t4.toolcalling.mode  severity: error  on_unknown: review
applies_when: exists(selection agent_framework primary /id) AND (exists tool primary OR exists mcp_server primary)
assert: any(
  intersects(catalog agent_framework primary /spec/tool_calling_modes [MISSING], ["prompted_react","code_action"]),
  eq(catalog model primary /spec/supports_tool_calling, true))
```

#### rule.t4.model.api.surface (compatibility example 2, full form) · Source-checked (unverified) evidence, needs #40

A framework can support a provider API without supporting every model feature through it:
- The OpenAI Agents SDK silently drops Responses-only fields on Chat Completions (A37).
- Hosted tools and tool search are "rejected on Chat Completions models and on non-Responses backends" (A37).
- PydanticAI: gpt-6-sol and gpt-6-luna allow function calling on Chat Completions only with reasoning effort `none` (A53).
- PydanticAI: "Compatibility with one API does not imply support for the other or for every OpenAI feature" (A54).

Missing fields: `spec_agent_framework.model_api_surfaces`, `spec_model_provider.api_surfaces` (or per-model), and a feature list such as `required_api_features` in `settings_agent_framework`.

```text
id: rule.t4.model.api.surface  severity: error  on_unknown: review
assert: intersects(catalog agent_framework primary /spec/model_api_surfaces [MISSING],
                   catalog model_provider primary /spec/api_surfaces [MISSING])
id: rule.t4.model.api.feature  severity: warning  on_unknown: review
assert: subset_of(selection agent_framework primary /settings/required_api_features [MISSING],
                  catalog model primary /spec/api_features [MISSING])
```

#### rule.t4.engine.toolchoice · Source-checked (unverified) evidence, needs #40 and #11

Ollama's `/v1/chat/completions` does not accept `tool_choice` (A79). vLLM supports `required` only from 0.8.3 and enforces schemas for `auto` only with `strict` or a strictness floor (A77). Frameworks that force a tool call (for example for structured output, or `tool_choice='required'`) then fail or degrade.

Missing fields: `spec_inference_engine.tool_choice_modes` and `spec_agent_framework.requires_tool_choice`.

```text
assert: implies(eq(catalog agent_framework primary /spec/requires_tool_choice [MISSING], "required"),
                contains(catalog inference_engine primary /spec/tool_choice_modes [MISSING], "required"))
severity: warning
```

#### rule.t4.mcp.transport.match · Source-checked (unverified) evidence, needs #40

Same proposal as `rule.t4.mcp.transport.client-support` in [mcp-servers.md](mcp-servers.md), which is the canonical version for #40 review. This section supplies the framework-side transport evidence.

Missing field: `spec_agent_framework.mcp_client_transports`, reusing the `spec_mcp_server.transport` enum and adding `websocket` and `provider_hosted`.

```text
id: rule.t4.mcp.transport.match  severity: error  on_unknown: review
applies_when: exists(selection mcp_server primary /id)
assert: in(catalog mcp_server primary /spec/transport, catalog agent_framework primary /spec/mcp_client_transports [MISSING])
```

Failing example from evidence: an SSE server with MAF Python, which has no SSE class (A25). Unknown example: Mastra with SSE (not documented, A70).

#### rule.t4.mcp.protocol.revision · Hypothesis, needs #40 and #27

Same proposal as `rule.t4.mcp.protocol.era` in [mcp-servers.md](mcp-servers.md), which is the canonical version for #40 review.

Revision 2026-07-28 removed the connection-scoped `initialize` session and relies on fallback for older counterparts (A3, A4). Frameworks pin different SDK lines: CrewAI `mcp~=1.28.1` (A28), Agno `mcp>=2.1` (A64), OpenAI Agents `mcp>=1.19,<3` (A36). Whether a v1-SDK client works with a 2026-only server is not documented.

Missing fields: `spec_agent_framework.mcp_protocol_revisions`, `spec_mcp_server.protocol_revisions`.

```text
assert: intersects(catalog agent_framework primary /spec/mcp_protocol_revisions [MISSING],
                   catalog mcp_server primary /spec/protocol_revisions [MISSING])
severity: warning
```

#### rule.t4.memory.backend (replaces rule.memory.framework.compatibility) · Hypothesis, needs #40 and #28

Missing field: `spec_agent_framework.state_backends`, reusing `spec_memory_store.backing_type`. The mapping from product names (Postgres, Redis, S3) to `relational / object / file` needs #28.

```text
applies_when: exists(selection memory_store primary /id)
assert: in(catalog memory_store primary /spec/backing_type, catalog agent_framework primary /spec/state_backends [MISSING])
severity: error  on_unknown: review
```

#### rule.t4.rag.integration · Hypothesis, needs #40 and #16

Every candidate can expose retrieval as a tool. Some have native retrieval components: LlamaIndex (A57), Mastra RAG (A69), Agno knowledge (A67), CrewAI knowledge (A30). There is no evidence of a hard incompatibility, so this stays `info`.

Missing field: `spec_agent_framework.rag_integration` (enum `native, tool_only`).

```text
applies_when: exists(selection rag_pipeline primary /id) AND exists(selection agent_framework primary /id)
assert: eq(catalog agent_framework primary /spec/rag_integration [MISSING], "native")
severity: info
```

#### rule.t4.deployment.managed · Hypothesis, needs #40, #3 and #37

A managed deployment mode needs a managed runtime the framework vendor or the cloud supports: LangSmith Deployment (A10), Agent Runtime (A48), Foundry hosted agents (A21), CrewAI AMP (A30). Missing field: `spec_agent_framework.managed_runtime_refs` (references to `hosting_platform`).

```text
applies_when: eq(catalog deployment_mode primary /spec/mode, "managed") AND exists(selection agent_framework primary /id)
assert: exists(catalog agent_framework primary /spec/managed_runtime_refs [MISSING])
severity: warning
```

#### rule.t4.telemetry.egress · Source-checked (unverified) evidence, needs #40, #35 and #38

Some frameworks send data off-host by default:
- OpenAI Agents SDK traces go to OpenAI by default (A38).
- Agno sends a telemetry event per run (A64).
- CrewAI has anonymous telemetry (A30).

Missing field: `spec_agent_framework.default_telemetry_egress` (boolean).

```text
applies_when: eq(catalog agent_framework primary /spec/default_telemetry_egress [MISSING], true)
assert: eq(selection agent_framework primary /settings/telemetry_disabled [MISSING], true)
severity: warning (error when a restricted data_source is selected)
```

#### rule.t4.direct.orchestration · Hypothesis, needs #40

v1 cannot represent "no framework". Proposal: a build-level field `/objectives/orchestration` with values `framework` or `direct_sdk`. `rule.agent.tools.framework` would apply only when it is `framework`.

```text
rule.agent.tools.framework applies_when: exists(tool primary) AND ne(build /objectives/orchestration [MISSING], "direct_sdk")
```

## Pricing and capacity

- All evaluated frameworks are open-source libraries with no per-use charge for the library itself. Mastra `ee/` features need an enterprise license for production (A69).
- Managed runtimes have plan gates but no prices were captured: LangSmith Cloud needs Plus or above, self-hosted needs Enterprise, and the standalone server needs a LangSmith license (A10). CrewAI AMP, Google Agent Runtime and Foundry hosted agents were not priced.
- No Pricebook proposal is made. Price units are left to #39.
- Agent cost is driven by model tokens and tool calls. Iteration caps (`settings_agent_framework.max_iterations`) are the main lever #39 should model.

## Recommendation and rationale

This is research guidance for builder defaults, not a product endorsement.

- **Single agent with a few tools:** offer "no framework" (direct provider SDK loop) as a first-class option. It has the fewest dependencies, and the provider documents the loop (A1, A2). v1 cannot select it today (see `rule.t4.direct.orchestration`).
- **Durable, multi-step or human-approval workflows:**
  - Python: LangGraph, Microsoft Agent Framework or Google ADK. Each documents checkpoint or session persistence and human-in-the-loop (A9, A27, A47).
  - Teams that want durable execution on an existing workflow engine: PydanticAI (A51).
- **TypeScript:** Mastra, OpenAI Agents JS, LangGraph.js, ADK TypeScript or Strands TypeScript.
- **Do not offer for new builds:** AutoGen (maintenance mode). Present Semantic Kernel as superseded by Microsoft Agent Framework.
- **Portability:** tool definitions are portable in practice through MCP; every framework evaluated has an MCP client. Agent graphs, state schemas and checkpoints are framework-specific, with no common format found. Treat a framework switch as a rewrite of orchestration code and a state migration.
- **Local models:** the builder must check the engine path, not just "OpenAI-compatible". Tool calling, `tool_choice`, strict schemas and the Responses API vary by engine and configuration (A37, A54, A77, A79).

## Structured artifacts

Ten CatalogItem proposals were written. Each contains only source-checked `programming_languages` and source-checked booleans. `supports_memory` is left out of all of them because it is ambiguous.

| File | ID | Version | Booleans included |
| --- | --- | --- | --- |
| `catalog/proposals/t4a-langgraph.json` | `agent_framework.langgraph` | 1.2.15 | tool_execution |
| `catalog/proposals/t4a-microsoft-agent-framework-python.json` | `agent_framework.microsoft-agent-framework-python` | 1.22.0 | tool_execution, mcp, multi_agent |
| `catalog/proposals/t4a-openai-agents-python.json` | `agent_framework.openai-agents-python` | 0.24.0 | tool_execution, mcp, multi_agent |
| `catalog/proposals/t4a-openai-agents-js.json` | `agent_framework.openai-agents-js` | 0.20.0 | tool_execution, mcp, multi_agent |
| `catalog/proposals/t4a-google-adk-python.json` | `agent_framework.google-adk-python` | 2.12.0 | tool_execution, mcp, multi_agent |
| `catalog/proposals/t4a-pydantic-ai.json` | `agent_framework.pydantic-ai` | 2.57.0 | tool_execution, mcp |
| `catalog/proposals/t4a-crewai.json` | `agent_framework.crewai` | 1.15.28 | tool_execution, mcp, multi_agent |
| `catalog/proposals/t4a-smolagents.json` | `agent_framework.smolagents` | 1.26.0 | tool_execution, mcp, multi_agent |
| `catalog/proposals/t4a-strands-agents-python.json` | `agent_framework.strands-agents-python` | 1.61.1 | tool_execution, mcp, multi_agent |
| `catalog/proposals/t4a-mastra.json` | `agent_framework.mastra` | 1.78.0 | tool_execution, mcp |

Not proposed:
- **No framework:** `spec_agent_framework` requires `programming_languages` and a single `version`. A "direct SDK" option is an architecture choice, not a versioned component, and an item would make baseline rules treat it as a framework.
- **AutoGen:** maintenance mode; can be added as `deprecated` if the builder must list it.
- **Semantic Kernel:** status mapping undecided.
- **LlamaIndex:** agent and workflow packages version separately (`llama-index-core` 0.14.25, `llama-index-workflows` 2.26.0), so the one-version-per-ID rule is ambiguous here.
- **Agno:** default telemetry egress needs a field before listing.
- **JS ports of LangGraph, ADK and Strands:** MCP and multi-agent not source-checked per port.

For LangGraph, `supports_mcp` is deliberately omitted: MCP comes from the separate `langchain[mcp]` package, which is in beta (A13). `supports_multi_agent` is omitted because no fetched page stated it (A16).

## Open questions and handoffs

| Question | Follow-up issue / owner |
| --- | --- |
| Add `spec_agent_framework` fields: `tool_calling_modes`, `model_api_surfaces`, `mcp_client_transports`, `mcp_protocol_revisions`, `state_backends`, `rag_integration`, `managed_runtime_refs`, `default_telemetry_egress`, `observability` (enum `otel_native, otlp_export, vendor_tracing`), `supports_human_approval` | #40 · @tynamite |
| Deprecate or redefine `supports_memory`; extend `programming_languages` with `csharp`/`dotnet` and `kotlin`; per-language versions under one framework ID | #40 · @tynamite |
| Status values for "maintenance mode" and "superseded" (AutoGen, Semantic Kernel) | #40 · @tynamite; #41 freshness |
| Represent "no framework / direct SDK orchestration" in a build; fix `rule.agent.tools.framework` and `rule.agent.mcp.framework` for provider-hosted MCP | #40 · @tynamite |
| #6 must populate `supports_tool_calling` and `supports_json_schema` per model and per API surface (Responses vs Chat Completions), including reasoning-effort conditions (A53) | #6 · @zwright8 |
| #11 must record tool-calling prerequisites per engine: vLLM `--enable-auto-tool-choice`, `--tool-call-parser`, `--tool-strict-level`, `required` from 0.8.3; Ollama no `tool_choice` and stateless Responses only | #11 · @Mattycodes69 |
| Retrieval-as-tool vs native retrieval components; which `rag_pipeline` modes frameworks consume | #16 · @zabyxc01 |
| Tool catalog handoff: tool-calling approach per framework; approval or HITL hooks for mutating tools | #26 · @CompleteDotTech |
| MCP handoff: client transports and SDK pins per framework (matrix above); SSE deprecation; MCP 2026-07-28 revision support per framework (unknown) | #27 · @CompleteDotTech |
| Memory handoff: framework state backends (LangGraph checkpointers, ADK SessionService, Agno `db`, Strands session managers, CrewAI checkpoint providers) mapped to `memory_store.backing_type` | #28 · @CompleteDotTech |
| Guardrails: approval hooks (OpenAI Agents HITL, ADK tool confirmation, PydanticAI deferred tools, MAF approval modes); smolagents local code execution risk (A63) | #35 · @PUSHINGSQUARES |
| Evaluation: agent-level eval hooks per framework (not researched) | #36 · @PUSHINGSQUARES |
| Deployment: library vs managed runtimes (LangSmith Deployment, Agent Runtime, Foundry hosted agents, CrewAI AMP, LlamaIndex deploy targets) | #37 · @PUSHINGSQUARES |
| Monitoring: OTel support per framework; default telemetry egress (OpenAI Agents traces, Agno, CrewAI) | #38 · @PUSHINGSQUARES |
| Plan gates and prices for managed runtimes (LangSmith Plus/Enterprise, CrewAI AMP, Agent Runtime, Foundry) | #39 · @PUSHINGSQUARES |
| Evidence grading of vendor documentation used here | #41 · @tynamite |
| Not source-checked on fetched pages: LangGraph multi-agent and parallel tool execution, OpenAI Agents SDK OpenTelemetry, MAF checkpoint storage backends and .NET MCP transports beyond stdio, Mastra SSE, PydanticAI and Agno multi-agent | #25 · @CompleteDotTech |

None of the handoffs above is confirmed yet.
