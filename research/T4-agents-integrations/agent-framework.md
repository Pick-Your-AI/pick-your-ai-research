# T4: Agent Framework

Issue: #25 · Contract: 1.0.0 · Kinds: `agent_framework`
Status: research completion candidate; exact receiving review and protected delivery remain the acceptance gate · Reconciled: 2026-10-18

## Evidence status correction

Evidence metadata corrected at 2026-10-17T02:17:46Z under the [adopted #41 interim policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Checked primary documentation, publisher package metadata, registry entries and source inspection are not independent verification. These catalog claims remain `unverified`; the original facts, versions, source access dates and `checked_at` are unchanged. No qualifying independent corroboration or runtime reproduction was supplied. Vendor capability statements remain documented claims, not measurements.

A proposed constraint may pass on eligible, versioned documentation while its evidence remains unverified. Missing eligible evidence remains unknown; absence from an unmarked capability list does not establish lack of support. Synthetic evaluator results check rule mechanics only and do not verify product behaviour. All rules and contract changes still require central versioned review through #40. The original evidence correction did not itself satisfy issue completion. The current receiving packet below distinguishes actual earlier replies, the present delegated technical decisions requested for this candidate, and separate implementation or absent co-owner responses.

## User decision

Which orchestration approach should run multi-step or tool-using behaviour: a framework or SDK, or no framework (the application drives a provider SDK's tool-use loop itself)?

The answer depends on four joint facts:
- what the selected model and its serving path can do (native tool calling, JSON-schema output, `tool_choice` modes), from #6 and #11;
- which model API surfaces the framework speaks (for example OpenAI Responses vs Chat Completions);
- which MCP transports and protocol revisions the framework's MCP client supports (#27);
- where state, traces and the runtime live (library in the user's process, or a vendor-managed runtime).

Execution arrangements covered below are independent of the build's serving-component deployment mode. Under the accepted [operator/capacity definition](../../prompts/SHARED.md#workstream-and-handoff-boundaries), an application-owned framework may call a managed model endpoint; that does not require a vendor-managed framework runtime.

Execution arrangements covered alongside API, managed, self-hosted or hybrid **model serving**:
- **Application-operated orchestration:** the application can use a framework library or a direct provider SDK. The library/package and server examples in the matrix are candidate arrangements, not evidence that a particular runtime, OS or deployment is supported. LangGraph Agent Server, Agno AgentOS and LlamaIndex's server/deployment tooling have their separately documented requirements (A10, A58, A64).
- **Provider-operated orchestration:** documented examples include LangSmith Deployment, Google ADK deployment targets, Foundry hosted agents and CrewAI AMP (A10, A21, A30, A48). A listed cloud target or runtime does not establish a supported release, plan, region, entitlement or configured deployment.
- **Provider-hosted tools/MCP:** OpenAI's Responses MCP interface and Anthropic's server tools/MCP connector move that selected execution to the provider (A2, A36). The application may still own the surrounding loop. Client ownership is separate from the chosen MCP wire transport; it is not another transport enum.

These arrangements cover the issue's relevant modes without forcing an agent framework, a local inference engine or a managed framework runtime merely from the model's serving mode. Exact operator/capacity, connection and artifact evidence follows #3/W-R8/CD-4 and #37; the listed products do not supply it automatically.

Out of scope: tool catalog (#26), MCP server packaging (#27), memory semantics (#28).

## Candidate options

The matrix retains the **2026-10-16 package-version snapshot**; it is not a latest-version promise. The dated A89 readback below confirms the explicitly selected registry records and reports later releases separately, without silently upgrading the ten catalog proposals. Main-branch or current documentation remains documentation at its access date, not proof for every package in a dependency range.

"MCP client transports" lists documented client interfaces only. Provider-hosted connection ownership and custom in-memory/WebSocket channels are separately identified; they do not extend the standard transport enum. "Not documented" or "not assessed" is an explicit source-coverage gap, not unsupported status. A published release does not establish a support commitment, operational maturity or secure maintenance. Qualitative choices below are project research judgments unless attributed to a publisher.

### Matrix

| Candidate (package) | Version (release date) | License (scoped publisher evidence) | Languages | Release / lifecycle evidence | MCP client transports | State / checkpointing | Multi-agent / graph | HITL / approval | Observability | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No framework: OpenAI SDK (`openai`) | 3.31.0 (2026-10-14) | Apache-2.0 (PyPI metadata) | Python package here; other SDKs separate | published package | application MCP client not assessed; OpenAI-side remote MCP via Responses API | application-owned policy | application-owned | application-owned policy | application policy; SDK hooks not assessed | A1, A36, A80, A90 |
| No framework: Anthropic SDK (`anthropic`) | 1.15.0 (2026-10-15) | MIT (PyPI metadata) | Python package here; other SDKs separate | published package | application MCP client not assessed; Anthropic-side MCP connector | application-owned policy | application-owned | application-owned policy | application policy; SDK hooks not assessed | A2, A80 |
| LangGraph (`langgraph`) | 1.2.15 (2026-10-12); JS `@langchain/langgraph` 1.5.0 (2026-10-12) | MIT | python; typescript (separate package) | published package; support term not assessed | via LangChain `langchain[mcp]>=1.4.0` (beta): stdio, Streamable HTTP, in-memory; SSE deprecated; WebSocket not supported. `langchain-mcp-adapters` no longer maintained | checkpointers: in-memory, SQLite, Postgres; Store for long-term memory | graph; multi-agent not stated on fetched pages | interrupts | LangSmith; OTel export via `langsmith[otel]` | A6–A16 |
| Microsoft AutoGen (`autogen-agentchat`) | 0.7.5 (2025-09-30) | MIT | python | **archived**; no Microsoft bug fixes, security fixes or support; successor is Microsoft Agent Framework | not assessed | not assessed | yes | not assessed | not assessed | A17, A18, A85 |
| Microsoft Semantic Kernel (`semantic-kernel`) | 1.45.0 (2026-10-06); NuGet `Microsoft.SemanticKernel` 1.81.0 | MIT | python, .NET, Java | **superseded**: README says it "is now Microsoft Agent Framework"; still releasing | MCP plugins (transports not assessed) | not assessed | yes | not assessed | not assessed | A19, A20 |
| Microsoft Agent Framework (`agent-framework`) | 1.22.0 (2026-10-15); NuGet `Microsoft.Agents.AI` 1.25.0 (2026-10-14) | MIT | python, .NET; Go in public preview | publisher GA/LTS statement (A24); exact support term not qualified | Python: stdio (`MCPStdioTool`), Streamable HTTP (`MCPStreamableHTTPTool`), WebSocket (`MCPWebsocketTool`); .NET page shows stdio only; Foundry-hosted MCP with approval modes | workflow checkpoints at superstep boundaries; backends not stated | graph and functional workflows; sequential, concurrent, handoff, group | `RequestInfoExecutor` / `ctx.request_info()`; hosted MCP approval | built-in OpenTelemetry | A21–A27 |
| CrewAI (`crewai`) | 1.15.28 (2026-10-14) | MIT | python (>=3.10,<3.14) | published package; support term not assessed | stdio, SSE, Streamable HTTP (`mcps` field or `MCPServerAdapter`); adapter is tools-only | checkpoints of crews, flows, agents: JSON or SQLite providers | crews and flows | human input / review | depends on `opentelemetry-sdk`; anonymous telemetry by default | A28–A33 |
| OpenAI Agents SDK, Python (`openai-agents`) | 0.24.0 (2026-10-15) | MIT | python | published pre-1.0 package | stdio, Streamable HTTP, SSE (legacy); OpenAI-hosted MCP (`HostedMCPTool`) | documented Sessions, Redis extra; graph checkpointing not assessed | handoffs, agents-as-tools | built in | own tracing, exported to OpenAI by default; custom processors; unavailable under ZDR | A34–A38 |
| OpenAI Agents SDK, JS (`@openai/agents`) | 0.20.0 (2026-10-08) | MIT | typescript | published pre-1.0 package | stdio, Streamable HTTP, SSE (legacy, "deprecated by the MCP project"); hosted MCP | Sessions | handoffs | built in | not assessed | A39–A41 |
| Google ADK (`google-adk`) | 2.12.0 (2026-10-13); JS `@google/adk` 2.3.0 (2026-10-13) | Apache-2.0 | python (>=3.11); TypeScript, Go, Java, Kotlin in separate repos | published package; support term not assessed | stdio, SSE, Streamable HTTP (`McpToolset`); MCP connections not re-established on session restore | SessionService: in-memory, database, Vertex/Agent Runtime | graph workflow runtime; hierarchies; fan-out/fan-in, loops, retry | tool confirmation | OpenTelemetry, OTLP, Cloud Trace | A42–A49 |
| PydanticAI (`pydantic-ai`) | 2.57.0 (2026-10-16) | MIT | python (>=3.11) | published package; support term not assessed | Streamable HTTP, SSE (deprecated), stdio | durable execution on Temporal, DBOS, Prefect and six others | not assessed | deferred tools with approval | OpenTelemetry-native; Logfire optional | A50–A56 |
| LlamaIndex (`llama-index-core`, `llama-index-workflows`) | core 0.14.25 (2026-09-21); workflows 2.26.0 (2026-10-11) | MIT | python; TypeScript `llamaindex` 0.12.1 (2025-12-02) | published packages; publisher describes document-parsing focus | `llama-index-tools-mcp` 0.6.0: Streamable HTTP, SSE, stdio | workflows: "save and resume runs from a file, or connect to a database" | `AgentWorkflow` handoff | via `llama-agents-server` | not assessed | A57–A60 |
| Hugging Face smolagents (`smolagents`) | 1.26.0 (2026-05-29) | Apache-2.0 | python | selected release dated 2026-05-29; maintenance quality not inferred | stdio, Streamable HTTP, SSE (`MCPClient`, `mcp` extra) | agent memory in process | multi-agent hierarchies | not assessed | `telemetry` extra: OpenTelemetry + OpenInference | A61–A63 |
| Agno (`agno`) | 3.1.3 (2026-10-12) | Apache-2.0 | python | published package; support term not assessed | stdio, SSE (not recommended), Streamable HTTP (`agno[mcp]`, `mcp>=2.1`) | `db`: Postgres, SQLite, MySQL, Mongo, Redis, JSON and others | not assessed | human approval | OpenTelemetry traces; telemetry event per run by default | A64–A67 |
| Mastra (`@mastra/core`) | 1.78.0 (2026-10-15) | Apache-2.0 core; `ee/` directories under Mastra Enterprise License | typescript | published package; support term not assessed | `@mastra/mcp` 2.4.1: stdio, Streamable HTTP; SSE not documented | storage-backed suspend/resume | graph workflows (`.then()`, `.branch()`, `.parallel()`) | suspend and resume | OTel-compatible spans; Langfuse, Arize, platform exporters | A68–A71 |
| Strands Agents (`strands-agents`) | 1.61.1 (2026-10-15); TS `@strands-agents/sdk` 1.21.0 (2026-10-14) | Apache-2.0 | python, typescript | published package; support term not assessed | stdio, Streamable HTTP, SSE (Python and TypeScript) | session managers: file, S3, AgentCore Memory, custom | Graph, Swarm, agents-as-tools | not assessed | OpenTelemetry, OTLP and console exporters | A72–A76 |

Notes on the "other" slots: Mastra (the only TypeScript-only framework evaluated) and Strands Agents (Python and TypeScript, no hosted control plane) were added. Considered but not evaluated: Claude Agent SDK (`claude-agent-sdk` 0.2.168, alpha; it drives the Claude Code CLI, and the npm package's license is "SEE LICENSE IN README.md") (A82); Vercel AI SDK (`ai` 7.0.142, Apache-2.0), a toolkit rather than an agent runtime (A83); AG2 (`ag2` 1.1.2, Apache-2.0), a separately maintained AutoGen lineage (A81).

### Per-candidate notes

- **No framework (direct provider SDK).** The application runs the loop: the model returns tool calls, the application executes them and sends results back (A1, A2). Anthropic documents a "Tool Runner" that automates the round trip in its SDKs, and server tools that run on Anthropic's side (A2). OpenAI says to assume several calls per response (A1). Anthropic exposes `disable_parallel_tool_use` (A2). The application owns its orchestration, authorization and state policy; SDKs may supply helpers rather than requiring every mechanism to be rewritten. For example, the pinned OpenAI SDK documents configurable automatic retries (A90). Project judgment: direct orchestration reduces framework dependencies but leaves API adaptation and policy composition with the application; no cross-provider portability ranking was measured.
- **LangGraph.** Low-level graph runtime: "you don't need to use LangChain to use LangGraph" (A16). Checkpointers give human-in-the-loop, time travel and fault tolerance. In-memory checkpoints are lost on restart; Postgres is recommended for production (A9).
  - MCP is not in LangGraph itself. It comes from LangChain's `langchain.mcp` (beta, `langchain[mcp]>=1.4.0`, targets the 2026-07-28 MCP spec with fallback) (A13, A14). `langchain-mcp-adapters` 0.3.2 is "no longer actively maintained" (A12).
  - Managed: LangSmith Deployment in four modes: Cloud (Plus plan or above), Hybrid, Self-hosted (Enterprise plan), and a Standalone server that needs PostgreSQL, Redis and a LangSmith license (A10).
- **AutoGen.** Microsoft now describes AutoGen as archived and no longer maintained; Microsoft provides no bug fixes, security fixes, new features or support (A85, checked 2026-10-17). New users are directed to Microsoft Agent Framework. The last PyPI release is 0.7.5 on 2025-09-30 (A18). Do not offer it for new builds.
- **Semantic Kernel.** README: "Semantic Kernel is now Microsoft Agent Framework!", with a migration guide (A19). Releases continue (Python 1.45.0, .NET 1.81.0) (A20). Treat it as superseded for new builds.
- **Microsoft Agent Framework (MAF).** Python and .NET, with Go in public preview: "Declarative agents, RAG, CodeAct, and functional workflows are not yet available" in Go (A24). Providers: "Microsoft Foundry, Anthropic, Azure OpenAI, OpenAI, Ollama, and more" (A24).
  - Python MCP client classes: `MCPStdioTool`, `MCPStreamableHTTPTool`, `MCPWebsocketTool`. They need `mcp --pre` (and `mcp[ws] --pre` for WebSocket), which is a version-dependent prerequisite (A25). There is no separate SSE class.
  - Hosting samples cover A2A, Foundry hosted agents, and a separate Durable Task / Azure Functions extension (A21).
- **CrewAI.** Native SDKs for OpenAI, Anthropic, Gemini, Azure, Bedrock and Snowflake Cortex. "All other providers are powered by LiteLLM", including Ollama (A32). "Structured output support varies by provider and model" (A32).
  - Version-dependent limitations from PyPI metadata (A28): `crewai` 1.15.28 pins `mcp~=1.28.1` (the MCP Python SDK v1 line, now in maintenance per A4) and the `anthropic` extra pins `anthropic~=0.73.0`, while the current `anthropic` release is 1.15.0 (A80).
  - Checkpoint auto-writes are "best-effort: a failed write is logged and the run continues" (A33).
  - Commercial control plane: CrewAI AMP, on-premise or cloud (A30).
- **OpenAI Agents SDK.** "Provider-agnostic, supporting the OpenAI Responses and Chat Completions APIs, as well as 100+ other LLMs" through any-llm or LiteLLM (A35). Responses is the SDK default; its guide describes selecting the Chat Completions adapter for a path without Responses (A37/A88). The selected provider's actual API support remains #6 evidence.
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
  - The PydanticAI guide gives a reasoning-effort condition for particular OpenAI Chat Completions model names (A53; dated recheck A94). This is PydanticAI's published adapter guidance, not primary evidence of the provider's offering. #6 must qualify any model/API/request constraint from the provider before it can decide compatibility.
- **LlamaIndex.** `FunctionAgent` "uses an LLM provider's function/tool calling capabilities"; `ReActAgent` and `CodeActAgent` "use different prompting strategies to execute tools" (A60). The README states the vendor's current focus is document parsing (LlamaParse) (A57). Deploy targets via `llamactl`: LlamaParse, AWS Bedrock AgentCore, or own infrastructure (A58).
- **smolagents.** `CodeAgent` writes actions as Python code; `ToolCallingAgent` "leverages built-in tool calling methods" (A61). Local code execution carries risk: "no local python sandbox can ever be completely secure" (A63). Relevant to #35.
- **Agno.** Framework plus the AgentOS runtime (REST API, Postgres, MCP server, control plane) run with Docker (A64). It "sends a telemetry event per agent run"; opt out with `AGNO_TELEMETRY=false` (A64). Storage note: "session storage support does not imply support for every AgentOS domain" (A67).
- **Mastra.** TypeScript framework; the publisher advertises model routing to "40+ providers" (A69), not a measured coverage count here. Its license scopes are distinct: core Apache terms, enterprise directories and third-party terms. The fresh A93 readback qualifies the historical production-license summary: enterprise production use requires both the applicable written agreement and a valid, scoped key; no artifact-wide entitlement is inferred.
- **Strands Agents.** "Runs in your process with no hosted control plane" (A73). Providers include Bedrock, Anthropic, OpenAI, Gemini, LiteLLM, llama.cpp and Ollama (A73). Multi-agent session managers "only track the current state of the Graph/Swarm execution" (A76).

### Pinned source follow-up (2026-10-18)

The publisher's Git refs were read and resolved before inspecting the files below: OpenAI Agents Python `v0.24.0` resolves to `17d994bd3045dae71acda676a4ef4762ed8ecd94`, and LangGraph `1.2.15` resolves to `08a345637fb2bd499f69c90056a22c478a468817`. A86/A87 retain immutable source locators. Method: read GitHub's raw UTF-8 files and the package metadata/source at those commits; no package, model, tool, or server was run. Grade: Primary documentation, source checked / unverified.

- **OpenAI Agents Python 0.24.0 MCP dependency and negotiation (A86):** its package metadata accepts `mcp>=1.19.0,<3` for Python 3.10 and later. The adapter detects the installed MCP package major version; with v2, `create_v2_client` uses `mode="auto"`. The pinned guide explains that this probes `server/discover` using the installed SDK's newest protocol and falls back to a legacy `initialize` exchange where needed. The package version and the server's actually negotiated protocol are separate evidence. The stdio, SSE and Streamable HTTP adapters share that package compatibility; `HostedMCPTool` is owned by the Responses API and does not inherit this local-package contract. This resolves the client implementation/source gap for this release, without assigning a protocol revision to an untested server or claiming sampling/elicitation support.
- **LangGraph ToolNode parallel calls (A87):** the LangGraph 1.2.15 metadata requires `langgraph-prebuilt>=1.1.0,<1.2.0`; the inspected companion metadata is version 1.1.0. At the pinned commit, `ToolNode._func` dispatches its tool calls through the configured executor's `map`, and `_afunc` collects asynchronous tool calls with `asyncio.gather`. This source check resolves the previously unread parallel-tool-execution mechanism for that inspected implementation. It does not establish a numeric concurrency guarantee, safe ordering of mutating tools, multi-agent quality, or identical behavior for every later dependency in the allowed range. #35 still needs operation-specific approval/idempotency controls and #36 owns runtime evidence.

### Inference-engine prerequisites (input from #11)

The following engine bullets retain the dated A77–A79 observations and their original conditions; the exact #11 consumer contract below governs whether they are eligible for a selected release. "OpenAI-compatible HTTP" alone does not establish feature parity:
- **vLLM:** auto tool choice needs `--enable-auto-tool-choice` plus a model-specific `--tool-call-parser`. `required` is supported only from `vllm>=0.8.3`. With `tool_choice="auto"`, schema-constrained decoding applies only when a tool sets `strict: true` or the server sets `--tool-strict-level`. "Most OpenAI-compatible clients and agent frameworks never set `strict` on their tools, so ... malformed markup can leak into the response" (A77).
- **Ollama:** `/v1/chat/completions` supports `tools` and `response_format` but not `tool_choice`. `/v1/responses` (since v0.13.3) is non-stateful only (A79). The native API supports parallel tool calls and streaming tool calls (A78).
- **LiteLLM** (1.105.1) is the route CrewAI, ADK, smolagents and the OpenAI Agents SDK use for many non-native providers (A32, A35, A44, A61, A84). Feature pass-through was not assessed.

## Comparison fields

The v1 `spec_agent_framework` has one required field (`programming_languages`) and four optional booleans. The issue's comparison fields map as follows.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| `/id` | string, `agent_framework.<slug>` | identify the actual package/implementation; language is not a substitute for package identity | v1 schema; A22, A23 | Separate packages may have different versions; a grouped comparison row is not one deployable artifact |
| `/version` | string, exact registry version | see matrix | per row | v1 allows one version per ID; per-language versions need separate IDs |
| `/status` | enum `active, preview, deprecated, retired` | AutoGen → `deprecated` (archived; lifecycle mapping remains proposed); Semantic Kernel → see open questions | A85, A19 | v1 has no "archived" or "superseded" value |
| `/license/spdx_id` | v1 string holding the scoped license identifier | publisher MIT/Apache declarations in the matrix; Mastra core scope only | per row; A89, A91, A93 | One core SPDX label does not describe an entire mixed-license artifact or its dependencies. Mastra enterprise and third-party materials retain separate terms; the Claude Agent SDK npm marker is not an SPDX grant |
| `/spec/programming_languages` | array of enum `python, typescript, javascript, go, rust, java, other` | see matrix | per row | No `csharp`/`dotnet` or `kotlin`; MAF, SK and ADK need `other` |
| `/spec/supports_tool_execution` | boolean | true only in the listed, source-backed catalog proposals | per proposal and matrix row | A component-level capability does not prove the selected native, prompted, code or provider-hosted operation; direct orchestration has no fabricated framework item |
| `/spec/supports_mcp` | boolean | true where a first-party MCP client is documented | per row | Cannot express transports, protocol revision, or "via companion package in beta" (LangGraph) |
| `/spec/supports_multi_agent` | boolean | true where documented | per row | Handoff vs graph vs hosted subagents are not distinguished |
| `/spec/supports_memory` | boolean | **not populated** in proposals | — | Ambiguous: built-in conversation state, a long-term store, or integration with an external `memory_store`? See compatibility proposals |
| `/settings/agent_count`, `/max_iterations`, `/timeout_ms` (selection) | integers | no change proposed | — | Approval policy and checkpoint backend are not settings |
| supported model APIs (note only) | proposed enum array `openai_responses, openai_chat_completions, anthropic_messages, gemini, bedrock_converse, ollama_native, litellm, other` | see notes | A35, A37, A44, A54 | Needed for rule `rule.t4.model.api.surface` |
| tool-calling approach (note only) | proposed enum array `native, prompted_react, code_action, provider_hosted` | named native-tool, LlamaIndex ReAct/CodeAct, smolagents code-action and OpenAI/Anthropic hosted examples | A2, A36, A60, A61 | Determines whether model `supports_tool_calling` is a hard prerequisite |
| state / persistence (note only) | implementation/layer/recovery record; descriptive backend names carry no numeric unit | see matrix; follow #28 M1/M3 and W-R11 | A9, A33, A47, A51, A67, A76; accepted memory interface | Product, backing type, runtime operator and durability are different axes. Require the exact owner/adapter/store/operation/configuration and relevant retained layers; no backend-label intersection supplies support |
| MCP client transports (note only) | selected wire transport plus separately qualified implementation/custom-channel metadata | see matrix | per row; A3, A86 | Frozen values stay unchanged. Custom WebSocket/in-memory channels need their own binding; `provider_hosted` describes client ownership, not transport. SSE is legacy in the cited revision |
| MCP protocol revisions (note only) | array of date strings, e.g. `2025-11-25`, `2026-07-28` | LangChain targets 2026-07-28 with fallback; mcp SDK v2 serves both | A4, A14 | Per-framework revisions mostly unknown |
| observability hooks (note only) | enum array `otel_native, otlp_export, vendor_tracing, none`; boolean `default_telemetry_egress` | see matrix | A11, A38, A46, A56, A64, A75 | Feeds #38 `monitoring_stack.exporter` |
| managed runtime (note only) | list of hosting refs | LangSmith Deployment, Agent Runtime/Cloud Run/GKE, Foundry, CrewAI AMP, LlamaParse/AgentCore | A10, A21, A30, A48, A58 | Plans and prices not captured |
| human-in-the-loop (note only) | documented mechanism plus proposed selected-action/enforcement binding | see matrix | per row; #35 | A hook is availability evidence, not proof that approval precedes the actual side effect or survives handoff, parallel execution or changed tool definitions |

## Evidence

Original entries were accessed on 2026-10-16; A85 is a lifecycle recheck from 2026-10-17, and A86/A87 are pinned-source checks from 2026-10-18. A88 and the later A89–A94 register retain their own dates and methods. Grades follow `docs/RESEARCH_METHOD.md` and the adopted #41 interim policy. Package versions and dates come from the cited PyPI, npm and NuGet metadata. License provenance is **per row**: some records use publisher license files, others registry expressions or classifiers. These are scoped publisher declarations, not an artifact/dependency license inventory. Vendor documentation is primary for the vendor's own described implementation, not independent verification or primary evidence of another provider's offering. This desk-study continuation installed or executed no candidate; the separately linked FET experiments retain their original methods and pins.

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
| A85 | Microsoft, https://github.com/microsoft/autogen/commit/004749e6b7102c8fd317b9b1499ce5807223c278 | 2026-10-17 | README lifecycle update, 2026-10-16T16:14:36Z | Primary documentation | Archived; no Microsoft bug fixes, security fixes, new features or support; supersedes the lifecycle statement originally recorded under A17 |
| A86 | OpenAI, [release ref](https://api.github.com/repos/openai/openai-agents-python/git/ref/tags/v0.24.0), [package metadata](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/pyproject.toml), [MCP guide](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/docs/mcp.md), [compatibility adapter](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/src/agents/mcp/_compat.py) | 2026-10-18 | 0.24.0; commit `17d994bd3045dae71acda676a4ef4762ed8ecd94` | Primary documentation; source code | Raw files read; dependency negotiation is conditional on installed `mcp`. No server negotiation or capability was measured; link and bounded paraphrase only |
| A87 | LangChain, [release ref](https://api.github.com/repos/langchain-ai/langgraph/git/ref/tags/1.2.15), [LangGraph metadata](https://github.com/langchain-ai/langgraph/blob/08a345637fb2bd499f69c90056a22c478a468817/libs/langgraph/pyproject.toml), [companion metadata](https://github.com/langchain-ai/langgraph/blob/08a345637fb2bd499f69c90056a22c478a468817/libs/prebuilt/pyproject.toml), [ToolNode source](https://github.com/langchain-ai/langgraph/blob/08a345637fb2bd499f69c90056a22c478a468817/libs/prebuilt/langgraph/prebuilt/tool_node.py) | 2026-10-18 | LangGraph 1.2.15 / inspected prebuilt 1.1.0; commit `08a345637fb2bd499f69c90056a22c478a468817` | Primary documentation; source code | Raw files read; no execution, ordering guarantee or throughput measurement; later dependency versions require their own evidence; link and bounded paraphrase only |

## Compatibility proposals

These rules are proposed for review by #40 using the [rule proposal template](../../templates/rule-proposal.md).
- **Source-checked (unverified)** means the cited primary text supports the assertion.
- **Hypothesis** means the assertion needs a definition, measurement or contract field that does not exist yet.

Outcome (`pass/fail/unknown/skipped`) is produced by evaluation; severity (`info/warning/error`) is a property of the rule. All JSON blocks below were checked against the `rules` item schema of `contracts/v1/schemas/ruleset.schema.json`.

### Assessment of the baseline T4 rules

| Baseline rule | Problem found | Proposal |
| --- | --- | --- |
| `rule.agent.tools.framework` | A no-framework build (direct SDK loop, A1, A2) has tools but no `agent_framework` selection, so this rule fails with `error` and blocks a valid architecture. It only reads the `primary` tool; tools selected under other roles are never checked. A coarse `supports_tool_execution` fact cannot establish the actual native, prompted, code or hosted path. | Use the accepted W-R3 architecture: a selected tool or MCP server can satisfy a known action need without a framework. Preserve the historical frozen-v1 rule; #40 owns versioned successor dispatch/migration. Assess the actual selected mode and model/engine/tool/provider bindings using the proposals below, without another orchestration field or the withdrawn direct-orchestration rule. |
| `rule.agent.mcp.framework` | (1) A boolean cannot express exact transport support or distinguish an unmarked list omission from a supported negative. The historical MAF client-class list (A25), LangChain adapter list (A13) and Mastra transport list (A70) need the coverage assessment described below; an omission alone stays unknown. (2) It cannot express protocol revision: the 2026-07-28 spec changed the session model (A3), and CrewAI pins the v1 SDK (A28). (3) Provider-hosted MCP (OpenAI hosted MCP, Anthropic MCP connector, Foundry hosted MCP) makes the provider the MCP client, so "framework supports MCP" is the wrong test (A2, A26, A36). (4) Primary role only. | The framework aliases now delegate to the current canonical #27 transport/protocol/capability dispositions below; historical interim `rule.t4.mcp.transport.sse-deprecated` in [mcp-servers.md](https://github.com/itisSomeone/pick-your-ai-research/blob/3d95c61efc2895d971415950dd4ebdfc1f23aba8/research/T4-agents-integrations/mcp-servers.md) (v1-valid proposal delivered via [PR #71](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/71), merged 2026-10-17; central #40 review and receiving-owner acceptance remain separate). |
| `rule.memory.framework.compatibility` | `supports_memory` is ambiguous. Documented checkpoint/session/backend mechanisms (A9, A47, A67, A76) do not establish an actual adapter, operation, resource or recovery boundary. Proposals here leave the field unset rather than guess. | Withdraw the backend-label proxy and use accepted #28 M1/M2/M3/M4 with distinct persistence, storage binding, invocation and authority scopes; #40 owns versioned adoption. |

### Source-checked (unverified), expressible in v1

**Historical proxy boundary.** The following four JSON blocks retain their original bytes for review and reproducibility. They fit the frozen schema but do not certify the selected paths: they use single-primary guards, a framework-presence proxy and coarse model/engine/lifecycle fields. Their broad positive/negative messages cannot replace the current scoped decisions below. A known native requirement, optional structured output, direct SDK client or lifecycle support term must be evaluated at its actual scope. No frozen rule is changed or silently reinterpreted by this research.

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
  "message": "The selected inference engine is not recorded as exposing native tool calling. Native tool-call modes need scoped support and configuration evidence; prompted or code-action modes have different requirements.",
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

The framework-side evidence for flagging SSE servers is: MCP 2026-07-28 defines only stdio and Streamable HTTP as standard transports (A3); OpenAI Agents JS calls SSE "deprecated by the MCP project" (A41); PydanticAI says "The SSE transport in MCP is deprecated" (A52); LangChain says "Supported, but the transport is deprecated" (A13). An omitted SSE class in the inspected MAF page (A25) does not itself establish support, non-support or deprecation and is not used as negative evidence.

The rule itself is owned by #27 and published once, as `rule.t4.mcp.transport.sse-deprecated` in [mcp-servers.md](https://github.com/itisSomeone/pick-your-ai-research/blob/3d95c61efc2895d971415950dd4ebdfc1f23aba8/research/T4-agents-integrations/mcp-servers.md). An identical framework-side rule was drafted here and removed so the ruleset does not report the same finding twice.

#### rule.t4.framework.lifecycle: deprecated framework

- Participating: catalog `agent_framework` primary `/status` (envelope field).
- Assertion: status in `active` or `preview`. AutoGen is archived (A85).
- Severity: `warning`; `on_unknown: review`.

```json
{
  "id": "rule.t4.framework.lifecycle",
  "severity": "warning",
  "applies_when": {"op": "exists", "value": {"ref": {"scope": "selection", "kind": "agent_framework", "role": "primary", "pointer": "/id"}}},
  "assert": {"op": "in", "left": {"ref": {"scope": "catalog", "kind": "agent_framework", "role": "primary", "pointer": "/status"}}, "right": {"literal": ["active", "preview"]}},
  "on_unknown": "review",
  "message": "The selected agent framework is deprecated or retired and will not receive new features.",
  "remediation": "Choose a maintained framework (for AutoGen: Microsoft Agent Framework).",
  "affected_kinds": ["agent_framework"],
  "owner": "t4-research"
}
```

### Need contract change via #40

#### rule.t4.toolcalling.mode (compatibility example 1, full form) · Source-checked (unverified) evidence, needs #40

The earlier expression intersected the framework's available modes with prompted/code modes. That could pass a build actually configured for native calls simply because the same framework also offers ReAct. Capabilities and the selected execution path are different inputs.

Required proposed inputs: the actual application/framework/provider caller and adapter/version with source-qualified supported modes, plus the **selected mode for each configured action path** (`native`, `prompted_react`, `code_action` or `provider_hosted`). A workflow can mix paths, so a framework-wide capability array cannot choose one on the user's behalf. #40 owns their versioned representation and bindings. The [CD-3 scope/completeness policy](../T0-configuration/component-schema-compatibility.md#cd-3-synthetic-support-membership-experiment-2026-10-18) governs support: an unmarked omission is unknown, not a negative.

```text
id: rule.t4.toolcalling.mode  severity: error  on_unknown: review
for_each: enabled, bound action path and actual caller [PROPOSED; CD-7/CD-13]
assert: eligible scoped support for that path's selected execution mode

id: rule.t4.toolcalling.native-model  severity: error  on_unknown: review
applies_when: that path's selected mode == native
assert: eligible native-tool-call support for its actual model, API and request configuration
```

Known prompted/code paths skip the native-mode clause; they still need their own scoped framework/mode support and #35 controls. A missing selected mode, unresolved path binding or missing eligible support stays unknown. Provider-hosted execution retains the actual provider/API/tool binding and does not inherit local-handler capability. These are design proposals, not executable v1 fields. The historical warning-only JSON examples above retain their documented single-primary limitations.

#### rule.t4.model.api.surface (compatibility example 2, full form) · Source-checked (unverified) evidence, needs #40

A framework can support a provider API without supporting every model feature through it:
- The OpenAI Agents SDK silently drops Responses-only fields on Chat Completions (A37).
- Hosted tools and tool search are "rejected on Chat Completions models and on non-Responses backends" (A37).
- PydanticAI publishes model-specific Chat Completions advice (A53/A94); that client guidance is not admitted here as primary provider capability evidence. Any rule needs the selected provider's applicable model/API/request evidence from #6.
- PydanticAI: "Compatibility with one API does not imply support for the other or for every OpenAI feature" (A54).

Required proposed inputs: the configured API surface on the exact application/framework adapter, model and serving-path binding, source-qualified support for that surface on both sides, and the features that path actually requests. An intersection between two advertised capability lists cannot prove that the configured surface is in the intersection. The pinned SDK guide's per-provider/run/agent routing and rejection of Responses-only tools on other paths provide a concrete example (A88 below).

```text
id: rule.t4.model.api.surface  severity: error  on_unknown: review
for_each: enabled, bound caller/adapter/model serving path [PROPOSED; CD-7/CD-13]
assert: eligible support for the configured API surface on this actual adapter
        AND eligible support for the same surface on this exact serving path

id: rule.t4.model.api.feature  severity: warning  on_unknown: review
assert: each actually requested feature has eligible support for this
        caller/adapter/model/API/endpoint/request-configuration tuple
```

Keep source qualification, known negatives, list completeness and unresolved values distinct under CD-1/CD-3. For example, if both sides advertise Chat Completions but the selected route uses Responses, a common Chat Completions entry supplies no passing verdict for that route. Unknown selected surface is unknown, not an inferred default. A source-backed explicitly unsupported requested feature fails at the clause's fixed severity; an absent entry from a researched subset remains unknown.

#### rule.t4.engine.toolchoice · Source-checked (unverified) premise; selected-request proposal for #40/#11

The old framework-wide `requires_tool_choice == required` implication is withdrawn. It ignored the mode actually requested, named-tool choice, schema configuration, streaming and the selected engine route. A77/A79 are historical engine-document observations with the version limits in their source rows; they are not universal current support claims. The accepted #11 consumer boundary below owns their qualification.

- **Participants / inputs:** each enabled action path's actual model, optional inference engine, endpoint/API, engine/build/plugins, tokenizer/artifact/adapters, template/parser, selected `tool_choice`, schema/strictness backend, streaming and relevant request/configuration revision. These are proposed bound inputs, not new v1 pointers.
- **Applicability:** the configured request uses an inference engine and requests the particular native tool-choice/schema behavior. Known absence of that engine or requirement skips only this engine clause; unresolved binding or requirement is unknown.
- **Assertion:** eligible evidence supports the requested behavior in that exact tuple. An unused supported choice or a framework's alternate action mode supplies no witness.
- **Severity / unknown:** `warning` / `review`, retained separately from outcome. This warning does not certify deployment readiness; the selected request's mandatory model/API, authorization and #37 requirements still apply.
- **Cases (synthetic):** supported configured choice/parser/strictness tuple passes this narrow prerequisite; an eligible unsupported requested choice fails; an absent or wrong-revision parser/streaming fact is unknown. No engine and a known provider API path skips this rule while the provider/model checks remain applicable.
- **Remediation / versioning:** supply the missing tuple evidence or select and qualify another request/path. #11 supplies engine facts; #40 owns successor representation and migration. The frozen primary-only engine JSON remains historical.

#### rule.t4.mcp.transport.match and rule.t4.mcp.protocol.revision · Canonical #27 rules

The framework-side aliases are consolidated into #27's canonical `rule.t4.mcp.transport.client-support`, `rule.t4.mcp.protocol.era` and `rule.t4.mcp.client-capabilities`; do not emit duplicate findings. The [current MCP record](mcp-servers.md#rulet4mcptransportclient-support-compatibility-example-3-needs-contract-change-via-40) owns these rules. Its selected-connection correction was delivered in [#360](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/360), signed commit `f23fba107ae80c0e2e622e4e359b564b7624dbf8`. That PR's actual review and source observations remain separately attributable; this note accepts the delivered framework-facing research interface without claiming a runtime result.

- **Participants / inputs:** every enabled, identity-bound MCP connection: actual local application/framework or provider-hosted client and its version/configuration, selected server packaging/endpoint/revision, selected transport, requested operations, applicable required client capabilities and direct/fallback negotiation path. An SDK dependency range (A28/A86/A89) is not the installed SDK or a negotiated protocol receipt.
- **Transport assertion:** the selected transport has eligible support at both endpoints of the same configuration. A product-wide intersection only suggests alternatives. `provider_hosted` is client ownership; a hosted Responses interface does not become a local stdio client because an unrelated package supports stdio.
- **Protocol assertion:** one eligible revision and its required negotiation/fallback path are supported by both endpoints on that selected connection. The A86 source and #27's separately pinned SDK experiments retain their exact implementation/synthetic-peer limits; neither assigns a protocol set to all vendor servers.
- **Capability assertion:** every capability required by the selected operation/configuration has eligible client support, after resolving documented alternatives. An optional capability is not mandatory merely because it is advertised. Unknown required-versus-optional scope stays unknown.
- **Outcomes / policies:** transport and protocol retain canonical `error` / `on_unknown: block`; client capabilities retain `error` / `review`. A complete supported path passes only its prerequisite; an applicable explicit negative or eligible exhaustive exclusion fails. Missing binding, relevant completeness or support is unknown. Complete known absence/disabled connections skip these MCP clauses. Preserve failed/unknown paths when suggesting a separately qualified alternative.
- **Cases (synthetic):** local client and selected HTTP server with eligible matching support pass transport only; selected SSE with an exhaustive client exclusion fails; omission on A25/A70's unmarked page stays unknown. A framework-free application with an evidenced MCP client is valid. A complete direct/fallback protocol witness may pass protocol without claiming an actual exchange.
- **Remediation / migration:** qualify the missing tuple, client capability or supported server packaging. Authorization, direct stdio lifecycle, descriptions/changed tools, trust and W-R8/CD-4 remain independent #27/#35/#37 requirements. No frozen enum, new framework kind, product-wide compatibility boolean or executable successor DSL is adopted here.

#### rule.t4.memory.backend · Withdrawn duplicate; accepted #28 dispositions

The former `memory_store.backing_type in framework.state_backends` assertion is withdrawn. A matching storage label establishes neither an adapter nor its operations; absence of a separate `memory_store` selection does not reject a valid application- or framework-owned implementation. Use [#28's accepted M1–M8 interface](agent-memory.md#current-acceptance-and-receiving-packet-2026-10-18) and [the delivered versioned M1/W-R11 experiment](../T0-configuration/workload-use-case.md#w-r11-memory-need-is-met), with their actual source/review receipts in [#345](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/345) and [#351](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/351).

- **Participants / inputs:** each declared, enabled memory implementation and actual adapter/consumer path, its owner (application, framework or selected store), required read/write/delete/recovery operations, exact resource/index/namespace/representation, selected configuration/revision and relevant layer inventory. No framework or memory-store catalog item is invented for an application implementation.
- **Applicability / assertion:** when that implementation is used, eligible evidence supports its required adapter/storage operations for the exact path. A complete known inventory with no selected or required memory invocation skips M3; an explicit absence of a continuity requirement skips M1 only. Unknown need, declaration or scope stays unknown when needed by the relevant canonical rule. Other active invocation and lifecycle controls still apply. A selected backing label alone never passes them.
- **Policies / canonical ownership:** withdraw this duplicate framework-side rule ID and its former `error` policy. Invocation compatibility is #28 M3's fixed `warning` / `review`; required implementation and storage binding are M1/M2's `error` / `review`; required action authority remains M4's `error` / `block`. Do not emit a second error for M3 under this alias. Qualified support passes the narrow applicable prerequisite; a qualified required unsupported operation fails that prerequisite. Absent, ineligible, tied or mismatched facts are unknown. A known scoped failure is retained even when unrelated layers are unresolved.
- **Cases (synthetic):** an evidenced application-owned path may pass without `memory_store`; two relational labels with no adapter evidence are unknown; a required unsupported delete operation fails even if read works. Session support is not restart durability; durable storage is not proof of retention, erasure or a disaster-recovery objective.
- **Remediation / ownership:** qualify the actual adapter/resource/operation or choose an evidenced alternative. #28 M1/W-R11's existential requirement witness does not waive all-enabled independent authorization, retention, deletion, containment, context or observability checks. #40 owns encoding/migration; #13/#15 resource/action boundaries and #35/#38 lifecycle evidence remain intact.

#### rule.t4.rag.integration · Withdrawn native-preference proxy; #16 receiving requirements

The earlier assertion preferred `rag_integration == native` and assumed every candidate could expose retrieval. Neither is an evidenced hard compatibility requirement. Withdraw that native-versus-tool preference and its informational pass/fail proxy; a documented adapter is still not proof that a selected retrieval tuple works.

The [T3 receiving review below](#t3-retrieval-receiving-review-2026-10-18) accepts a declared pre-generation pipeline or retrieval-as-tool path on equal architectural terms. Bind the actual selected retrieval component/mode, wrapper/API/configuration, source/chunk revisions and citation semantics. Before any model, reranker or agent tool exposure, apply RAG-02's trusted caller/resource/action and mandatory-scope checks; model/tool arguments may only narrow authority. Preserve filters, ranking/normalization and returned-result shortfalls, and recount the complete assembled input with CTX-01 after transformations and each tool round.

**Synthetic dispositions:** an evidenced pre-generation path and an evidenced retrieval tool can each meet the interface; a missing wrapper/endpoint/mode binding is unknown; known stale permissions or a required unsupported retrieval operation fail the relevant #16/#35 prerequisite. No enabled retrieval in a complete known selection inventory skips retrieval-specific rules; unknown selection/applicability does not. A valid citation pointer alone does not prove answer support.

This withdraws a proposed preference rather than weakening RAG-02, CTX-01 or other accepted retrieval rules. Their outcomes, fixed severities and unknown policies remain with #16/#40. Adapter/configuration qualification, required evidence, remediation and versioned binding are receiving inputs; no `native` flag, new v1 operand or whole-framework retrieval guarantee is introduced.

#### rule.t4.deployment.managed · Hypothesis, needs #40, #3 and #37

The original build-mode predicate is withdrawn. A managed model endpoint does not require a managed agent runtime: the framework may still run in the application's own process. This rule concerns only an **explicitly selected provider-operated orchestration runtime**. Examples researched here include LangSmith Deployment (A10), Agent Runtime (A48), Foundry hosted agents (A21) and CrewAI AMP (A30); their existence does not establish compatibility with every framework or release.

Required proposed inputs: the selected orchestration runtime and operator, exact framework/runtime versions and configuration, and eligible compatibility evidence for that pair. Missing fields/bindings remain #40/#37 work; no new build-mode taxonomy is introduced.

```text
id: rule.t4.deployment.managed  severity: warning  on_unknown: review
applies_when: the bound orchestration runtime is explicitly provider-operated
assert: eligible compatibility evidence supports this exact
        framework/version + selected runtime/version/configuration pair
```

An explicitly application-operated framework skips this clause even when the model uses managed serving. An unresolved runtime/operator stays unknown; a nonempty catalog list is not a substitute for the selected runtime's evidence.

#### rule.t4.telemetry.egress · Source-checked (unverified) evidence, needs #40, #35 and #38

Some frameworks send data off-host by default:
- OpenAI Agents SDK traces go to OpenAI by default (A38).
- Agno sends a telemetry event per run (A64).
- CrewAI has anonymous telemetry (A30).

The later [producer-specific source and synthetic findings](framework-evaluation-telemetry.md#telemetry-controls-are-scoped-to-their-producers) show why a single `default_telemetry_egress` or `telemetry_disabled` flag is insufficient. Bind each producer/exporter to the actual selected framework/version, configuration, destination and data scope. Disabling Agent telemetry does not prove that a separate evaluator or exporter is disabled.

The original variable-severity example is replaced by two fixed-severity **policy hypotheses**. The proposed default is to disable a producer that exports outside the selected boundary; #35/#38 still own any scoped approval exception. This record does not itself adopt that policy or certify effective configuration.

```text
id: rule.t4.telemetry.egress  severity: warning  on_unknown: review
for_each: enabled, bound telemetry producer [PROPOSED]
applies_when: the producer has a configured export path outside the selected boundary
              AND its data scope is known not to include restricted data
assert: source-appropriate effective configuration and buffered-record
        handling prevent export on that path during the assessed window

id: rule.t4.telemetry.egress.restricted  severity: error  on_unknown: review
for_each: enabled, bound telemetry producer [PROPOSED]
applies_when: the producer has a configured export path outside the selected boundary
              AND its data scope includes restricted data
assert: source-appropriate effective configuration and buffered-record
        handling prevent export on that path during the assessed window
```

Known data classes select the corresponding fixed-severity clause. Missing classification, producer coverage, destination or effective control evidence stays unknown when it is needed to decide the applicable clause; do not route an unresolved scope through the non-restricted branch or infer a universal opt-out from one environment variable. The clauses are not claims that every candidate transmits restricted data. Capture suppression, processor replacement, buffered-record disposition and delivery are separate facts: pinned OpenAI tracing can flush records buffered before disabling, and adding a processor preserves the default exporter (FET-01; re-read as A92). The actual launch entry point, provider/auth mode, trace context, dependency/binary revision and effective content/export settings from [#38's framework interface](../T6-deployment-operations/monitoring.md) remain required where relevant; an unset environment variable is not a universal off signal. An evidenced in-boundary destination or complete absence of an export path skips this external-egress clause. A configured outside path with evidenced effective suppression and buffered-record handling passes its narrow assertion. A producer with pending buffered data remains in the relevant export-lifecycle inventory even after new capture is disabled. Neither outcome proves authorization, deletion or other controls.

#### Direct orchestration: use the accepted W-R3 decision

The earlier new `/objectives/orchestration` proposal is withdrawn in favor of the existing [W-R3 owner decision](../T0-configuration/workload-use-case.md#w-r3-actions-need-a-t4-component). Known action needs may be met by an enabled framework, tool or MCP server; a framework is not mandatory. Direct orchestration is therefore represented by the actual selected tool/MCP capabilities and their explicit bindings, rather than a fabricated framework catalog item.

Frozen v1's historical `rule.agent.tools.framework` still has its older requirement. The [CD-13 experiment](../T0-configuration/component-schema-compatibility.md#cd-13-synthetic-selection-experiment-2026-10-18) reproduces its selection bug without adopting that requirement. Successor dispatch/migration remains with #40; no frozen rule is changed here. Other conditions, including model/provider-hosted tool compatibility, permissions, isolation and costs, continue to apply to the actual selected path.

## Pricing and capacity

- Separate the selected library's license scope from framework hosting, model/tool usage, evaluator/judge calls, storage, telemetry and network charges. Publisher MIT/Apache declarations in the matrix are software-license facts, not a zero-cost deployment estimate. Mastra's core, enterprise and third-party scopes are distinct; the current enterprise text requires both an applicable written agreement and a valid, scoped license key for production use (A93). No artifact-wide entitlement or legal clearance is supplied here.
- A10 records dated LangSmith plan/license gates, not a price for the selected deployment. CrewAI AMP, ADK deployment targets, Foundry and other managed offerings were not priced for a defined region/tier/date. Missing prices and allowances remain unknown, not zero.
- No Pricebook proposal is made. #39 owns scenario-bound units/rates and completeness; its [current cost record](../T6-deployment-operations/cost-estimate.md) keeps uncovered cost categories visible.
- **Project modeling decision:** account for actual model input/output, tool operations, retries, branching/parallel paths, evaluator calls and runtime/storage/export work in the chosen scenario. `max_iterations` is one possible bound, not a measured main cost driver or a total-call/token guarantee. Count injected memory/RAG inside the assembled input once; repeated actual occurrences in later rounds still consume their own input. No price, throughput or performance number is estimated here.

## Recommendation and rationale

This is research guidance for builder defaults, not a product endorsement.

- **Single agent with a few tools:** offer "no framework" (direct provider SDK loop) as a first-class option. The provider documents the loop (A1, A2). W-R3 accepts tool/MCP execution without a framework; frozen v1's historical framework requirement still needs the reviewed successor dispatch/migration described above.
- **Durable, multi-step or human-approval workflows:**
  - Python: LangGraph, Microsoft Agent Framework or Google ADK. Each documents checkpoint or session persistence and human-in-the-loop (A9, A27, A47).
  - Teams that want durable execution on an existing workflow engine: PydanticAI (A51).
- **TypeScript:** Mastra, OpenAI Agents JS, LangGraph.js, ADK TypeScript or Strands TypeScript.
- **Do not offer for new builds:** AutoGen (archived; A85). Present Semantic Kernel as superseded by Microsoft Agent Framework.
- **Portability (project judgment):** an eligible common MCP transport/protocol/tool schema can reduce adapter work; the matrix does not prove that every candidate has an equivalent client or that tools, credentials, prompts, state and results transfer unchanged. No cross-framework graph/checkpoint interchange contract was established by this source set. Before a switch, assess orchestration, state serialization, migration, authorization and selected-client behavior. No portability measurement or universal rewrite requirement is claimed.
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
- **AutoGen:** archived (A85); can be proposed as `deprecated` if the builder must list it, with lifecycle mapping reviewed through #40.
- **Semantic Kernel:** status mapping undecided.
- **LlamaIndex:** the core and workflow packages have separate versions (A57/A58/A89). A later catalog submission must identify the actual package/implementation and any companion binding; the one-version-per-ID intake rule does not prohibit separate package identities. This desk study makes no combined-version item.
- **Agno:** retained in the note without a new catalog submission in this slice. Its producer-specific telemetry requirements belong in the selected configuration/evidence interface, not an invented required catalog field or a claim of incompatibility.
- **JS ports of LangGraph, ADK and Strands:** MCP and multi-agent not source-checked per port.

For LangGraph, `supports_mcp` is deliberately omitted: MCP comes from the separate `langchain[mcp]` package, which is in beta (A13). `supports_multi_agent` is omitted because no fetched page stated it (A16).

## Engine consumer acceptance specification (#11 to #25)

T4 accepts the conditional tool/schema/API contract in the merged [#11 record](../T2-infrastructure/inference-engine.md#proposed-40-contract-follow-up-no-v1-changes) as the interface for framework research. An engine-wide or OpenAI-compatible label is insufficient. The evidence key must retain engine/build/plugins, model and tokenizer revisions, artifact quantization and adapters, template/parser, API endpoint, request options, strictness, streaming mode and schema/grammar backend. This accepts the research boundary; exact extension fields, migration and executable compatibility rules remain with #40. Missing evidence is unknown, not unsupported or an automatic pass.

Synthetic request/response acceptance cases are kept in [the test fixture specification](../../tests/fixtures/t4-engine-consumer.md). They specify consumer checks and evidence identity, not observed engine support. Runtime exercises and evidence placement remain to be agreed with #11/#36.


## Open questions and handoffs

| Question | Follow-up issue / owner |
| --- | --- |
| Version the selected action/client/runtime/adapter/producer inputs below. The original catalog-field list is superseded as a decision mechanism: available modes/APIs/transports are scoped facts; memory, retrieval, authorization and telemetry require actual selected paths and completeness, not new coarse booleans | #40 · @tynamite, @zwright8; affected interfaces R1–R6 below |
| Deprecate or redefine `supports_memory`; review language values such as `csharp`/`dotnet` and `kotlin`; retain exact package identities and companion bindings instead of combining incompatible version labels | #40 · @tynamite |
| Status mapping for "archived" and "superseded" (AutoGen, Semantic Kernel) | #40 · @tynamite; #41 freshness |
| Apply the accepted W-R3 no-framework decision in successor dispatch/migration; retain actual tool/MCP and provider bindings without a competing `/objectives/orchestration` field | #40 · @tynamite |
| #6 supplies eligible model/offering/API/request support, including any reasoning-effort condition from the provider. PydanticAI advice in A53/A94 is not primary evidence of the OpenAI offering | #6 · @zwright8, @PUSHINGSQUARES; current R1 packet below |
| Exact-release engine/build/parser/endpoint/request prerequisites; historical minima and Ollama claims require eligible scoped evidence and do not add a T2 candidate | #11 · @zwright8, @Mattycodes69: [both scoped receipts recorded](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677); execution/evidence placement remains #11/#36 |
| Retrieval-as-tool vs native retrieval components; which `rag_pipeline` modes frameworks consume | #16 · @zabyxc01 |
| Tool catalog handoff: tool-calling approach per framework; approval or HITL hooks for mutating tools | #26 · @CompleteDotTech |
| MCP handoff: client transports and SDK pins per framework (matrix above); SSE deprecation; MCP 2026-07-28 revision support per framework (unknown) | #27 · @CompleteDotTech |
| Memory handoff: actual application/framework/store implementation, consumer adapter, operation, selected resource and configuration/layer/recovery scope under accepted M1/M3/W-R11; backend names remain descriptive | #28 · @CompleteDotTech; current R3 receiving packet below |
| Guardrails: approval hooks (OpenAI Agents HITL, ADK tool confirmation, PydanticAI deferred tools, MAF approval modes); smolagents local code execution risk (A63) | #35 · @PUSHINGSQUARES |
| Evaluation: [pinned OpenAI Agents, CrewAI and Agno hooks](framework-evaluation-telemetry.md) now separate scripted orchestration, judge scores, execution checks and host-function measurements; CrewAI's synthetic missing-metric case limits boolean acceptance. Other frameworks and real quality runs remain unresearched | #36 · @appletechie, @PUSHINGSQUARES |
| Deployment: library vs managed runtimes (LangSmith Deployment, Agent Runtime, Foundry hosted agents, CrewAI AMP, LlamaIndex deploy targets) | #37 · @PUSHINGSQUARES |
| Monitoring: [pinned producer-specific controls](framework-evaluation-telemetry.md#telemetry-controls-are-scoped-to-their-producers) now cover OpenAI Agents traces, CrewAI metadata and Agno Agent/evaluator telemetry; effective deployment configuration, other exporters and receiving adoption remain open | #38 · @appletechie, @PUSHINGSQUARES |
| Plan gates and prices for managed runtimes (LangSmith Plus/Enterprise, CrewAI AMP, Agent Runtime, Foundry) | #39 · @PUSHINGSQUARES |
| Evidence grading of vendor documentation used here | #41 · @tynamite |
| Still not source-checked on fetched pages: LangGraph multi-agent, OpenAI Agents SDK OpenTelemetry, MAF checkpoint storage backends and .NET MCP transports beyond stdio, Mastra SSE, PydanticAI and Agno multi-agent. LangGraph parallel tool execution is now source-checked only at A87's pinned implementation | #25 · @CompleteDotTech |

The incoming #11 consumer contract is accepted with constraints by #25 ([owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334)). Internal T4 handoffs are [accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509); external outgoing handoffs are partially received, including the reciprocal #25 -> #11 co-owner receipts; see the [workstream handoff matrix](README.md#dependency-and-handoff-matrix) for remaining scopes.

## T3 retrieval receiving review (2026-10-18)

T4/#25 accepts [#16's retrieval interface](../T3-knowledge-retrieval/rag-retrieval.md) with the following constraints for the T4 component owner's consuming scope. This records an engineering decision under the project owner's delegated authority; it does not speak for @Mattycodes69 or the T3 owners, select their default backend, or certify a framework/server tuple.

- A two-step application pipeline may complete retrieval before generation, or an agent may call a retrieval tool during a later round. Neither architecture makes a framework or RAG mandatory. The wrapper must identify the actual selected retrieval component and preserve its source/chunk revisions and citation pointers; the existence of a wrapper or connector is not evidence that the selected tuple works.
- Apply [RAG-02's caller/resource/action and mandatory-scope requirements](../T3-knowledge-retrieval/rules/retrieval-rules.md#rag-02-caller-authorization-precedes-model-and-tool-exposure) before any reranker/model call or agent tool response. User or model arguments may narrow the authorized scope, never replace it. Unknown binding, stale permissions or uncovered derived summaries cannot be accepted as protected retrieval. Treat returned content as untrusted data under #35.
- Carry the actual retrieval mode, filters, reranker identity, score/normalization semantics and any returned-result shortfall. The configured request alone does not prove that a backend honored hybrid search or a citation requirement. A valid source pointer does not establish answer support; #36 owns that evidence, and #65's existing interoperability experiment remains separate.
- Use CTX-01 on the complete input after each retrieval/tool round, with the generation tokenizer and template. Count every actual occurrence of instructions, tools, history, memory, retrieved text and citation overhead. Do not add a second conceptual memory/RAG allowance to a total that already includes those tokens; output reservation and post-transform recount still apply.
- A complete known inventory with no enabled retrieval path skips retrieval-specific checks; unknown inventory or applicability stays unknown. The former `rule.t4.rag.integration` native-preference proxy is withdrawn in the current disposition above. Actual binding/evidence fields and accepted retrieval rules still require versioned #40 adoption; no frozen-v1 rule or catalog boolean is changed here.

The T3 reply to T4's outgoing retrieval-interface request, other co-owner dispositions, actual authorization tests and selected-backend measurements remain open at their existing issues. This receiving decision supplies no production authorization or runtime evidence.

## Selected-path rule review (2026-10-18)

This continuation resolves specific false-pass/false-fail paths in the proposed rules, without changing the four original JSON rule IDs, their fixed severities, any catalog value or frozen v1. The rules remain research proposals for #40, including their CD-7/CD-13 binding and all-selection requirements.

A88 — OpenAI, [Agents SDK model guide](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/docs/models/index.md), pinned release source `17d994bd3045dae71acda676a4ef4762ed8ecd94` (Python SDK 0.24.0). Read **2026-10-18** through GitHub's raw-file connector after the web extractor could not retrieve the raw URL. **Primary documentation, source checked / unverified**. The guide distinguishes Responses and Chat Completions model adapters, per-provider/run/agent routing and Responses-only tool features; it describes dropped fields and strict validation on the Chat Completions path. This is source evidence for retaining the selected API/configuration, not an executed provider request or a new joint compatibility result. Original A37 retains its historical main-branch capture.

| Counterexample | Correct proposed disposition | Ownership and evidence boundary |
| --- | --- | --- |
| A framework offers native and prompted action modes, but the selected path is native and the model has an eligible native-tool-call negative | Native-mode clause fails; the unused prompted mode cannot make it pass | Selected mode and tuple binding require #40; a missing selected mode remains unknown |
| Framework and provider have one API surface in common, but the selected path uses a different surface | Check the selected surface and requested features on the exact path; the unused intersection proves nothing | A88 documents path-specific behavior; actual source eligibility and request configuration remain inputs |
| A managed model endpoint is called by an application-operated framework | Managed-orchestration clause is skipped for that known application-operated runtime | Accepted operator/capacity definition; no automatic framework-runtime requirement from model serving mode |
| An inspected framework page does not list an SSE client class | Unknown unless eligible explicit negative or exhaustive evidence establishes exclusion | CD-3's accepted unmarked-list distinction; no inferred unsupported capability |
| The Agent's opt-out is set but a separate evaluator/exporter may remain active | Evaluate each producer with its own control, destination and data scope; unresolved coverage stays unknown | The pinned evaluation/telemetry supplement; #35/#38 adoption and actual configuration remain separate |
| A tool is selected without an agent framework | W-R3 permits that architecture; apply the actual tool/provider/MCP bindings and other controls | W-R3/#40; historical v1 dispatch remains frozen until a reviewed successor |

The table is a logical review of proposed predicate scope. It supplies no new runtime observations, source-rights decision or receiving-owner adoption. At that selected-path review, the five remaining unchecked #25 criteria still required their full source/rule/receiving assessment; the current packet below supplies the completion candidate and preserves that historical boundary; the three artifact criteria reconciled in [the actual issue comment](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25#issuecomment-6248705617) and the original merged-record criterion retain their prior status.

## Current research decisions and acceptance packet (2026-10-18)

**Scope and status.** This is the note-only research proposal `framework-compatibility/0.1.0`, covering #25's candidate, comparison, rule and receiving requirements. It consolidates the operative decisions above and supersedes the identified coarse proxies without changing their retained JSON bytes. It creates no catalog field, frozen-v1 operand, approved ruleset or runtime implementation. The original A1–A87 rows, A88 paragraph, four JSON proxies, ten catalog proposals and dated receiving history remain intact. Final acceptance requires the actual independent source/interface reviews on this candidate and its ordinary protected delivery; a review request is not that receipt.

### A89–A94: bounded current source readback

The following primary sources were actually read on **2026-10-18**. A89 used public registry JSON metadata requests; A90–A94 used publisher UTF-8 source files. No package artifact was downloaded, installed or executed, and no model, provider API, server, judge or telemetry endpoint was invoked. All publisher findings remain **Primary documentation, source checked / unverified** under #41. Registry/commit identities locate the stated source; they do not prove installed composition, artifact origin, runtime behavior or source-use permission. Prices, currencies, account/plan entitlements and deployment regions were not assessed by this readback.

| ID | Publisher / actual source | Version and claim scope | Limits |
| --- | --- | --- | --- |
| A89 | PyPI and npm, the explicit registry locators in the table below; read at `2026-10-18T15:45:02Z` | 21 selected PyPI release records and nine selected npm version records, including companion and considered-only packages. Published version/date, language/dependency and scoped license metadata were read; observed latest labels are recorded separately | No package upgrade or artifact inspection. All selected PyPI file entries were not yanked; npm's selected records had no `deprecated` field. Those metadata observations are not support, maintenance or security guarantees. Historical NuGet entries were not re-fetched |
| A90 | OpenAI, [v3.31.0 ref](https://api.github.com/repos/openai/openai-python/git/ref/tags/v3.31.0), [SDK README](https://github.com/openai/openai-python/blob/86cae50785fb7b7bf2a5d2383370b214b304acd2/README.md#retries), [LICENSE](https://github.com/openai/openai-python/blob/86cae50785fb7b7bf2a5d2383370b214b304acd2/LICENSE) | Ref resolves to `86cae50785fb7b7bf2a5d2383370b214b304acd2`; the Python SDK documents configurable automatic retries and Apache-2.0 terms | Corrects the former claim that a direct SDK application must implement every retry. No retry/latency measurement or dependency-license inventory |
| A91 | Microsoft, [Semantic Kernel LICENSE](https://github.com/microsoft/semantic-kernel/blob/7a92cd4e7c2712370b8d85b687a474b2e858cdcc/LICENSE) and [README](https://github.com/microsoft/semantic-kernel/blob/7a92cd4e7c2712370b8d85b687a474b2e858cdcc/README.md); CrewAI [LICENSE](https://raw.githubusercontent.com/crewAIInc/crewAI/main/LICENSE); Hugging Face [smolagents LICENSE](https://raw.githubusercontent.com/huggingface/smolagents/main/LICENSE) | Observed source license declarations: MIT for the inspected SK/CrewAI files and Apache-2.0 for smolagents. SK's inspected README names Microsoft Agent Framework as its successor | SK has the stated immutable pin; CrewAI/smolagents are current-main reads at this date, not exact-release artifact clearance. A19/A29/A61 retain their original dates and methods. Publisher lifecycle language does not establish a support term for a selected deployment |
| A92 | OpenAI, [pinned tracing guide](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/docs/tracing.md) | Python Agents SDK 0.24.0 source, `17d994bd3045dae71acda676a4ef4762ed8ecd94`; default tracing/export, initialization, sensitive-content settings, additional versus replacement processors and previously buffered records | A re-read of the FET-01 source scope, not a re-run of FET probes. Capture disable does not discard earlier buffers; an additional processor retains the default exporter; separately registered processors are not a redaction gate for one another. Effective launch/configuration and delivery remain separate evidence |
| A93 | Mastra, [license partition](https://github.com/mastra-ai/mastra/blob/c21323b4e21e719338c665eb01c908e193aacfba/LICENSE.md), [enterprise license](https://github.com/mastra-ai/mastra/blob/c21323b4e21e719338c665eb01c908e193aacfba/ee/LICENSE), [README](https://github.com/mastra-ai/mastra/blob/c21323b4e21e719338c665eb01c908e193aacfba/README.md) | Observed source `c21323b4e21e719338c665eb01c908e193aacfba`; Enterprise Edition License v2.0, effective 2026-09-22. Core, `ee/` and third-party scopes are distinct; enterprise production requires the applicable agreement and a valid scoped key | Current source terms, not an inspection of every file in npm 1.78.0 or a legal/entitlement determination. A license marker alone supplies neither production permission nor a zero-cost estimate |
| A94 | Pydantic, [OpenAI model guide](https://github.com/pydantic/pydantic-ai/blob/0be309f8a0d92f5868e1779c39f93f4e5f30f1ff/docs/models/openai.md) | Observed source `0be309f8a0d92f5868e1779c39f93f4e5f30f1ff`; the guide publishes adapter advice about selected OpenAI model names, Chat Completions and reasoning configuration | Primary for PydanticAI's advice only. The former unqualified provider capability statement is withdrawn; #6 must supply applicable primary provider evidence before a rule uses it. No new model offering or endpoint test |

**A89 registry records.** Versions and release metadata are publisher-reported. The selected column preserves the dated comparison; `latest` is only the label observed in that registry response at the time above. For npm, the source is the registry document and the selected record is its `versions[version]` member. The rows include dependencies and considered-only packages, so they are not a count of evaluated frameworks. No artifact digest is presented as proof of a Git source-to-build relationship.

| Registry / selected package | Selected published version | Observed `latest` |
| --- | --- | --- |
| pypi: [`openai`](https://pypi.org/pypi/openai/3.31.0/json) | 3.31.0 | [3.35.1](https://pypi.org/pypi/openai/json) |
| pypi: [`anthropic`](https://pypi.org/pypi/anthropic/1.15.0/json) | 1.15.0 | [1.15.0](https://pypi.org/pypi/anthropic/json) |
| pypi: [`langgraph`](https://pypi.org/pypi/langgraph/1.2.15/json) | 1.2.15 | [1.2.16](https://pypi.org/pypi/langgraph/json) |
| pypi: [`autogen-agentchat`](https://pypi.org/pypi/autogen-agentchat/0.7.5/json) | 0.7.5 | [0.7.5](https://pypi.org/pypi/autogen-agentchat/json) |
| pypi: [`semantic-kernel`](https://pypi.org/pypi/semantic-kernel/1.45.0/json) | 1.45.0 | [1.45.0](https://pypi.org/pypi/semantic-kernel/json) |
| pypi: [`agent-framework`](https://pypi.org/pypi/agent-framework/1.22.0/json) | 1.22.0 | [1.22.0](https://pypi.org/pypi/agent-framework/json) |
| pypi: [`crewai`](https://pypi.org/pypi/crewai/1.15.28/json) | 1.15.28 | [1.15.28](https://pypi.org/pypi/crewai/json) |
| pypi: [`openai-agents`](https://pypi.org/pypi/openai-agents/0.24.0/json) | 0.24.0 | [0.24.0](https://pypi.org/pypi/openai-agents/json) |
| pypi: [`google-adk`](https://pypi.org/pypi/google-adk/2.12.0/json) | 2.12.0 | [2.12.0](https://pypi.org/pypi/google-adk/json) |
| pypi: [`pydantic-ai`](https://pypi.org/pypi/pydantic-ai/2.57.0/json) | 2.57.0 | [2.57.0](https://pypi.org/pypi/pydantic-ai/json) |
| pypi: [`llama-index-core`](https://pypi.org/pypi/llama-index-core/0.14.25/json) | 0.14.25 | [0.14.25](https://pypi.org/pypi/llama-index-core/json) |
| pypi: [`llama-index-workflows`](https://pypi.org/pypi/llama-index-workflows/2.26.0/json) | 2.26.0 | [2.26.0](https://pypi.org/pypi/llama-index-workflows/json) |
| pypi: [`smolagents`](https://pypi.org/pypi/smolagents/1.26.0/json) | 1.26.0 | [1.26.0](https://pypi.org/pypi/smolagents/json) |
| pypi: [`agno`](https://pypi.org/pypi/agno/3.1.3/json) | 3.1.3 | [3.1.4](https://pypi.org/pypi/agno/json) |
| pypi: [`strands-agents`](https://pypi.org/pypi/strands-agents/1.61.1/json) | 1.61.1 | [1.61.1](https://pypi.org/pypi/strands-agents/json) |
| pypi: [`mcp`](https://pypi.org/pypi/mcp/2.3.0/json) | 2.3.0 | [2.3.0](https://pypi.org/pypi/mcp/json) |
| pypi: [`llama-index-tools-mcp`](https://pypi.org/pypi/llama-index-tools-mcp/0.6.0/json) | 0.6.0 | [0.6.0](https://pypi.org/pypi/llama-index-tools-mcp/json) |
| pypi: [`langchain-mcp-adapters`](https://pypi.org/pypi/langchain-mcp-adapters/0.3.2/json) | 0.3.2 | [0.3.2](https://pypi.org/pypi/langchain-mcp-adapters/json) |
| pypi: [`ag2`](https://pypi.org/pypi/ag2/1.1.2/json) | 1.1.2 | [1.1.2](https://pypi.org/pypi/ag2/json) |
| pypi: [`claude-agent-sdk`](https://pypi.org/pypi/claude-agent-sdk/0.2.168/json) | 0.2.168 | [0.2.168](https://pypi.org/pypi/claude-agent-sdk/json) |
| pypi: [`litellm`](https://pypi.org/pypi/litellm/1.105.1/json) | 1.105.1 | [1.106.0](https://pypi.org/pypi/litellm/json) |
| npm: [`@langchain/langgraph`](https://registry.npmjs.org/@langchain/langgraph) | 1.5.0 | [1.5.1](https://registry.npmjs.org/@langchain/langgraph) |
| npm: [`@openai/agents`](https://registry.npmjs.org/@openai/agents) | 0.20.0 | [0.20.0](https://registry.npmjs.org/@openai/agents) |
| npm: [`@google/adk`](https://registry.npmjs.org/@google/adk) | 2.3.0 | [2.3.0](https://registry.npmjs.org/@google/adk) |
| npm: [`llamaindex`](https://registry.npmjs.org/llamaindex) | 0.12.1 | [0.12.1](https://registry.npmjs.org/llamaindex) |
| npm: [`@mastra/core`](https://registry.npmjs.org/@mastra/core) | 1.78.0 | [1.78.0](https://registry.npmjs.org/@mastra/core) |
| npm: [`@mastra/mcp`](https://registry.npmjs.org/@mastra/mcp) | 2.4.1 | [2.4.1](https://registry.npmjs.org/@mastra/mcp) |
| npm: [`@strands-agents/sdk`](https://registry.npmjs.org/@strands-agents/sdk) | 1.21.0 | [1.21.0](https://registry.npmjs.org/@strands-agents/sdk) |
| npm: [`@anthropic-ai/claude-agent-sdk`](https://registry.npmjs.org/@anthropic-ai/claude-agent-sdk) | 0.3.301 | [0.3.302](https://registry.npmjs.org/@anthropic-ai/claude-agent-sdk) |
| npm: [`ai`](https://registry.npmjs.org/ai) | 7.0.142 | [7.0.143](https://registry.npmjs.org/ai) |

### Complete claim-source audit

This audit covers the inherited note as well as this continuation. A capability remains an attributed, dated statement about its documented implementation. A registry release, general API compatibility, dependency range or favorable result for one tuple cannot extend it to another release, language port, provider, plan, endpoint, operation or selected configuration. The original historical pages were not all re-fetched today: their original access dates and limitations remain visible. A89–A94 identify the actual fresh reads; A86–A88 and FET retain their own earlier pinned methods.

| Claim family / note coverage | Primary basis and current disposition | Remaining explicit limit |
| --- | --- | --- |
| Direct SDK loop, hosted tools and package identity | A1/A2/A80; A36 for the OpenAI hosted MCP path; A89/A90 qualify package metadata and SDK retry helpers | Application-owned state/policy is an architecture choice, not a claim that SDKs contain no helpers or telemetry |
| MCP specification, SDK and companion versions | A3–A5, A12–A14, A28, A36, A59, A70, A86 and A89; current connection rules are canonical in #27 | Standard wire transport, custom channel, client ownership, package compatibility and actual protocol negotiation are distinct |
| LangGraph matrix and candidate notes | A6–A16; pinned ToolNode source A87; A89 retains the selected Python/JS versions separately | Parallel dispatch source is not a numeric concurrency, safe mutation-order or later companion-version guarantee |
| Microsoft lifecycle, languages and mechanisms | A17/A18/A85 (AutoGen), A19/A20 (SK), A21–A27 (MAF); A89/A91 qualify registry and inspected-source scope | Archived/superseded-to-v1 status mapping remains proposed. GA/LTS and lifecycle text are publisher statements, not an assessed support contract or language-port parity |
| CrewAI mechanisms and dependencies | A28–A33, A89/A91 and pinned FET-04–FET-10 | Dependency constraints are not an installed environment; checkpoint best-effort behavior and default telemetry are not delivery, durability or privacy proof |
| OpenAI Agents Python/JS mechanisms | A34–A41; pinned Python MCP/API/tracing A86/A88/A92; A89 keeps both packages separate | Vendor `100+` model coverage is a published claim, not measured joint feature coverage; Python source does not qualify JS or another SDK version |
| ADK and PydanticAI mechanisms | A42–A49; A50–A56/A94; A89 | Cloud targets and durable-execution adapters retain their documented scope. Pydantic advice about a different provider is not admitted as primary provider capability evidence |
| LlamaIndex and smolagents mechanisms | A57–A63; A89/A91 | Core/workflow/client packages retain separate identities; native, prompted and code-action approaches do not share an automatic native-call prerequisite |
| Agno, Mastra and Strands mechanisms | A64–A76, A89/A93; Agno's pinned FET-11–FET-17 | Mastra's `40+` routing claim is published, not measured. License partition, session-state semantics and each producer's control remain scoped |
| Engine prerequisites and compatibility labels | A77–A79, A84 and the accepted #11 exact consumer contract | Historical vLLM minima/Ollama/API claims require eligible engine/build/model/parser/request evidence before use. No proxy server or deployment is newly qualified |
| Considered-only candidates and package exclusions | A81–A83, A89; repository schema/intake rules for the ten unchanged proposals | Recording a candidate or an explicit unknown does not assert feature completeness. Separate package IDs can represent companion versions; a combined row is not one artifact |
| Typed comparison fields and structured artifact counts | The actual [v1 CatalogItem schema](../../contracts/v1/schemas/catalog-item.schema.json), [selection schema](../../contracts/v1/schemas/selection.schema.json), ten linked proposal files and the table above | Types and proposal counts are repository facts. Missing optional fields remain absent; no new enum, coarse default, evidence grade or catalog version is silently adopted |
| Rules, synthetic cases, recommendation and operational complexity | The cited candidate sources motivate the decisions; the shared envelope below, #40's decided semantics, W-R3, #28 M1–M8, #16/RAG-02 and #7/CTX-01 define the project requirements | Examples are logical synthetic cases, not product tests. Simplicity, portability and builder-default recommendations are identified engineering judgments, with no measured ranking or universal interchange assertion |
| Pricing, capacity and licensing | A10's dated plan gates; matrix publisher license evidence and A93; scenario modeling follows [#39](../T6-deployment-operations/cost-estimate.md) | No region/currency price, allowance, throughput, total-call or memory-capacity estimate is supplied. Unknown costs and unsupported meters remain unknown |
| Evaluation and observability follow-ups | Full [FET-01–FET-17 source register](framework-evaluation-telemetry.md#primary-source-register), its original isolated probes, [#36](../T6-deployment-operations/evaluation.md#framework-hooks-and-evidence-completeness-2026-10-18), [#38](../T6-deployment-operations/monitoring.md#t4-framework-telemetry-boundaries-2026-10-18-partial-source-follow-up), and actual C2 receipt below | Scripted outputs, judge scores, execution-record checks, host timing and Python traced allocations retain different claims. No new benchmark, collector, delivery, full-memory/RSS or provider/runtime observation |
| Source status, recommendations, open questions and handoff history | A1–A94 supply the dated source register; the actual repository issue comments/reviews linked below supply engineering decisions and their reviewed revisions | No merge, common assignee, public documentation, hash or silence is promoted into verification, source rights, absent co-owner agreement or completion of another issue |

Unresearched cells remain marked `not assessed`, `not documented` or named in the open-question table. They are not hidden negative claims and need not become invented booleans to complete a bounded research comparison. The corrected retry, backend-label, retrieval-preference, API-advice, portability, maintenance and license statements above are the current disposition; retaining an older source row or JSON example does not revive the withdrawn interpretation.

### Common shared-format envelope

All current proposals use the [#40 rule format and decided outcome semantics](../T0-configuration/component-schema-compatibility.md#rule-format-and-outcome-semantics-decided) and [rule proposal template](../../templates/rule-proposal.md). **Participants and pointers:** an actual selected component keeps `/id`, `/kind`, `/role`, `/enabled`, `/catalog_item_id`, `/catalog_item_version` and `/settings`, with exact applicable link/configuration/revision identity. Relevant kinds include `model`, `inference_engine`, `agent_framework`, `tool`, `integration`, `mcp_server`, `memory_store`, `rag_pipeline`, `context_policy`, `guardrail`, `monitoring_stack` and actual hosting/storage selections. The application or provider may own a caller/runtime without a separate framework selection. Declared non-catalog implementations are evidenced paths, not fabricated catalog items.

Schema/reference and build-wide identity/role validation precede predicates, including disabled and unrelated selections. The [CD-13 binding](../T0-configuration/component-schema-compatibility.md#cd-13-typed-selection-binding-proposal-2026-10-18) supplies the reviewed all-enabled-selection and required-kind distinction; it does not infer a complete runtime path inventory from a list of catalog items. Qualify the actual action/client/runtime/adapter/producer inventory separately. Preserve every scoped result; for universally required checks, a known failure takes precedence over unrelated unknowns. A positive witness can satisfy an expressly existential alternative requirement, such as M1, only within its stated scope; it never waives independent controls for other enabled paths.

**Answers, evidence and outcomes:** use the actual CD-1 states `provided`, `unknown`, `missing`, `withheld` and `not_applicable` and the current typed terminal semantics, retaining the responsible state/path/reason separately from the predicate value. Unknown/missing/withheld compatibility applicability or assertion remains unknown; explicitly not-applicable or provided false applicability skips only that predicate. A provided but unresolved predicate remains unknown. Recommendation gating and the older Boolean compatibility sidecar are not interchangeable with this typed boundary. Known false, zero, empty values and empty lists retain their field meaning; there is no Python truthiness fallback, rounded-value substitution, sentinel-string inference or parent read that exposes a withheld descendant.

Use eligible evidence for the exact component/property/configuration/revision and its assessed scope under [CD-3](../T0-configuration/component-schema-compatibility.md#cd-3-typed-support-query-and-result-candidate-2026-10-18) and #41's conflict order. Explicit negatives or eligible exhaustive exclusion can fail; an unmarked omission cannot. A complete empty required-feature set can pass its vacuous assertion only after applicability, scope and completeness are established. Missing requested-set completeness is not a known empty request; missing relevant support evidence stays unknown. A tie or an ineligible/mismatched source is not an arbitrary positive or negative. Source-checked documentation remains unverified even when it supports a passing narrow predicate.

**Optionality and explanations:** explicit complete absence/disablement skips only the applicable component/path-specific check. An unknown need or inventory is not absence, and a known requirement still receives its separate required-implementation/presence assessment. A transport pass does not authorize an action; a supported adapter does not establish persistence; an inside-boundary connection does not prove artifact readiness or deletion. Keep rule ID/version, selected identity, fixed severity, outcome, `on_unknown` policy, responsible reason and evidence/configuration references deterministic; do not copy sensitive answer values into findings or treat an opaque reference/hash as authorization.

**Version and migration:** `framework-compatibility/0.1.0` is a reviewable note revision only. #40 owns field/DSL encoding, support-cohort/source admission, versioned successor dispatch, compatibility with retained v1 and migration review. The historical four JSON blocks retain their original IDs, severities and bytes; their schema validity and any original synthetic results do not certify the new tuple bindings. Canonical #27 and #28 rules are referenced once rather than reissued under framework aliases. No rule in this note is labeled independently verified.

### Current rule and warning disposition

The preceding individual sections provide assertions, sources and participants. This table completes their common template with fixed policy, applicable synthetic cases, remediation and consumer scope. All cases are logical examples; no new evaluator or vendor execution was performed for them.

| Current decision | Fixed severity / `on_unknown` | Applicability, synthetic outcomes and remediation | Dependencies / migration |
| --- | --- | --- | --- |
| `rule.t4.toolcalling.mode` and `rule.t4.toolcalling.native-model` | `error` / `review` for each | For each actual action path, evidenced support for its configured caller/mode passes mode support. A native path with an eligible native-call negative fails native-model; an unused prompted alternative cannot pass it. Missing selected mode or tuple is unknown; known prompted/code mode skips the native-only clause. Qualify the actual mode/model/API/request | #6/#11/#26/#35; new bound inputs via #40. Direct application callers are valid |
| `rule.t4.model.api.surface` and `rule.t4.model.api.feature` | surface `error` / `review`; requested feature `warning` / `review` | Exact selected surface supported by caller adapter and serving path passes that prerequisite; an eligible selected-surface negative fails. A known unsupported requested feature fails its fixed warning. Missing binding/completeness is unknown; a complete empty requested feature set has no feature failure. Select or evidence the actual route/configuration; an unused shared API is not a witness | #6/#11/#26/#27; proposal encoding and migration #40 |
| `rule.t4.engine.toolchoice` | `warning` / `review` | Exact requested choice, schema/strictness/parser and streaming tuple passes or fails on eligible support; missing relevant tuple evidence is unknown. A known provider API path with no engine skips only this clause. Qualify or change the requested engine route | #11/#37; retains the exact engine consumer specification and historic minima limits; #40 successor |
| Framework MCP aliases → canonical #27 transport/protocol/capability rules | transport/protocol `error` / `block`; required capabilities `error` / `review` | Selected connection, required revision/negotiation and operation-required capabilities need eligible evidence. A required unsupported selected leg fails; an unmarked omission is unknown; complete absent/disabled connections skip. Qualify each actual client/server leg and its documented alternatives | #27 owns the three canonical IDs; #26/#35/#37 keep auth, stdio/process, trust, changed-tool and containment checks separate. No duplicate alias findings |
| `rule.t4.memory.backend` → accepted M1/M2/M3/M4 | M1/M2 `error` / `review`; M3 `warning` / `review`; M4 `error` / `block` | An evidenced application/framework/store implementation can satisfy its declared scope. Generic tool support or matching backend names with no binding is unknown. An eligible unsupported required operation fails the relevant rule; a complete absent optional invocation skips M3, while no continuity requirement skips M1 only and active independent controls still run. Qualify implementation, adapter, resource, recovery layers and action authority separately | #28 owns each distinct assertion; #13/#15/#35/#38 controls and W-R11 remain intact. Withdraw the duplicate framework backend rule rather than emit its old error policy |
| `rule.t4.rag.integration` native preference | Withdrawn; no new finding under this proxy | A supported pre-generation path or retrieval tool can qualify. Missing path/citation/request binding is unknown; actual stale scope or required unsupported retrieval fails the appropriate accepted prerequisite. Complete absent optional retrieval skips its checks. Qualify the wrapper and enforce RAG-02 before exposure, then CTX-01 on full input | #16/#7/#35 own their existing fixed policies; no native-framework requirement or new v1 operand |
| Historical `rule.t4.framework.lifecycle` | Retained historical `warning` / `review` proxy | Its `deprecated` test is not a general support-term assessment; the old message that all retired/superseded components lack features is not current evidence. A source-qualified lifecycle concern motivates review for a new build; unknown lifecycle or status mapping is unknown. Qualify exact release/support obligations before selection | A19/A85/A91; #40 maps archived/superseded in a versioned successor and #41 qualifies freshness. Original JSON is unchanged |
| `rule.t4.deployment.managed` | `warning` / `review`, policy hypothesis | An explicitly provider-operated orchestration runtime with eligible exact pair/configuration support passes; an eligible incompatible pair fails; unknown runtime/operator/binding stays unknown. Application-operated orchestration skips this clause even with managed model serving. Qualify the actual runtime | #3/#9/#37; source-qualified existence is separate from selected-region/plan/runtime readiness; #40 representation |
| `rule.t4.telemetry.egress` and `.restricted` | ordinary `warning` / `review`; restricted `error` / `review`, policy hypotheses | For a configured outside export path in the known data-class branch, effective suppression plus buffered-record handling passes; known continuing export contrary to this proposed policy fails. Unresolved relevant producer, destination, class, effective setting or buffer scope is unknown. Complete no export path or an inside destination skips only external egress. Configure each producer before capture and evidence its queue disposition | #35/#38 own any scoped exception and adoption. Exact launch/provider/auth/trace context and binary/dependency settings remain inputs; one opt-out does not cover all producers |
| Direct orchestration / historical framework-presence rules | Existing W-R3 requirement; no competing rule or policy here | An action need may use actual tool/MCP capabilities without a framework. A missing required implementation is evaluated separately; unknown inventory cannot silently skip it. Qualify the actual caller/provider/tool path rather than add a dummy framework | #2/#26/#27/#40; frozen v1 remains historical until explicit successor dispatch/migration |

### Receiving packet: exact proposed technical decisions

The actual earlier receipts below retain their reviewed sources and constraints. This candidate asks the delegated independent reviewers to accept, narrow or reject **R1–R6** for the precise research interfaces, naming the immutable reviewed revision in their PR reviews. These are project engineering decisions within the user's delegation. They do not claim to be separate replies from absent named co-owners, legal clearance, a live deployment, a source-rights grant or another issue's completion. Until those actual reviews are posted and this candidate is delivered, the five unchecked criteria remain unchecked.

| Packet | Declared dependency / direction and existing receipt | Decision requested on this candidate | Explicit receiving limit |
| --- | --- | --- | --- |
| **R1 — model/API/engine** | Inputs #6/#11 → #25; bidirectional #25 ↔ #6 and reciprocal #11. Earlier [#6 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6#issuecomment-6242697096), [#11 receiving](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334), [#11 zwright8](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6242698282) and [#11 Mattycodes69](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6245204677) | Accept exact caller/adapter/model/offering/API/request and optional engine/build/model/tokenizer/artifact/parser/schema/streaming bindings. Native-mode requirements apply to the selected path; direct SDK clients are legitimate. Provider features require primary provider evidence; generic labels, unused modes/APIs and SDK ranges do not establish support | The old replies remain pinned to their own revisions. No new provider or engine tuple, historical-minimum generalization, language-port parity or executable rule adoption |
| **R2 — tools and MCP** | Downstream #25 → #26/#27, compatibility #25 ↔ #27. [Internal T4 dispositions](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509); canonical MCP completion [#360](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/360) | Accept actual selected tool operation and trusted principal/resource/authority, separately bound caller/client/version/server/transport/protocol/capability/configuration and direct/fallback negotiation. A provider-hosted client is ownership, not transport; no framework is compulsory. Preserve all-enabled checks and canonical #27 rule IDs without duplicate aliases | A connector, annotation, configured secret, registry listing, approval hook or compatible package range proves no actual permission, exchange, tool safety or selected-server support. The separate #26 → #27 operation receipt is not a substitute for this direction |
| **R3 — retrieval, memory and context** | Input #16 → #25; downstream #25 → #28. Existing [T3 receiving review](#t3-retrieval-receiving-review-2026-10-18), [memory R1–R5 delivery](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/345), [W-R11 correction](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/351) and [CTX-01 zwright8](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6242697652)/[appletechie](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6245648263) | Accept equal architectural treatment of declared pre-generation and tool retrieval, RAG-02 trusted scope before model/reranker/tool exposure, source/citation identity and exact implementation/adapter/resource/recovery-layer memory bindings. Preserve #28's declared purpose, applicable project opt-in/withdrawal and event-bound per-layer lifecycle/permission requirements. Apply complete assembled-input accounting and recount after each round, counting each actual token occurrence once. M1's witness does not waive other enabled controls | No requirement for native retrieval, a vector database, framework or separate memory-store item. No invented combined context cap, duplicated conceptual token allowance, authorization/consent record, citation-support measurement, persistence or deletion execution |
| **R4 — enforcement and runtime** | Downstream #25 → #35; supplemental #37. Original [PUSHINGSQUARES T6 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6240050930) and [appletechie constrained confirmation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6245652021) | Accept hooks as mechanism evidence only; bind actual action and enforcement before side effects, including handoff/parallel calls, idempotency and changed descriptions/tool lists where applicable. Runtime ownership is independent of model-serving mode; preserve W-R8/CD-4 actual connections, required artifacts, lifecycle and selected auth/configuration | These are receiving requirements. No observed enforcement, physical isolation, current runtime deployment, broad T6 catalog adoption or retroactive expansion of old replies |
| **R5 — evaluation and monitoring** | Downstream #25 → #36/#38. Original T6 replies above; [FET source/probe record](framework-evaluation-telemetry.md); actual [#62 → #25 C2 negative-comparability receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25#issuecomment-6251565503) | Accept the FET scripted/judge/execution-record/host-function distinction, required-metric completeness and separately identified metric/grade/unit/source pins. Accept per-producer actual launch/provider/auth/trace-context/version/content/export controls, independent exporter/evaluator paths, capture versus buffer disposition and unknown-versus-zero observations. Accept the two fixed telemetry policy hypotheses for versioned review with scoped exceptions owned by #35/#38 | C2 supplies a negative comparability audit, not normalized framework ranking or causal harness effect. No new quality run, full-RSS claim, absent metric default, real collector/export success, product opt-out certification or independent-source upgrade |
| **R6 — shared format and evidence** | Supplemental #40/#41. [Actual #40 queue review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6242626523), [#41 evidence disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6242626857) and current CD-1/CD-3/CD-7/CD-13 records | Accept this common envelope and disposition table as research proposals: exact identities, all-enabled scope, conditional completeness, typed outcomes/reasons, independent fixed severity/unknown policy, canonical-rule ownership and explicit migration. Accept the full claim audit's attributed facts, published numbers, engineering judgments, preserved historical dates and named unknowns | Queue acceptance is not final field/DSL/ruleset adoption. Hashes/source access/synthetic probes do not establish rights, current deployment facts, independent verification or cross-project consumption |

For clarity, R1–R3 cover every literal information-input and compatibility relationship; R2–R5 cover all six literal downstream consumers (#26/#27/#28/#35/#36/#38). R4/R6 and the context/cost links record additional affected interfaces without inventing new issue acceptance criteria. T4/#25's own incoming decisions are recorded here under its actual delegated controller; independent review of the complete packet is the requested receiving completion evidence, not an assumption based on shared assignment. Named co-owner responses and later implementation/adoption remain separately attributable.

### Literal criterion assessment for final delivery

| Original #25 criterion | Evidence in the completed candidate | Delivery gate |
| --- | --- | --- |
| Candidate set with sourced fields | Matrix, per-candidate notes, typed field map, A1–A94 audit and explicit unresearched cells; historical package selections retained | Actual independent full source review and accepted merge |
| Framework ↔ model and framework ↔ MCP rules in the #40 format | Individual selected-path proposals, common envelope, fixed-policy/case/remediation table, R1/R2/R6 and canonical #27 ownership | Actual shared-format and receiving review; final executable encoding remains #40 |
| Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | Historical proxies explicitly bounded; source-checked/unverified premises separated from proposed managed-runtime/telemetry policies; typed outcome and migration limits retained | Actual independent proposal review; no rule falsely labeled verified |
| Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | Complete claim-source audit across the inherited record; dated register/readbacks; published metadata/counts distinguished from project judgments and historical synthetic evidence; no new price estimate | Actual source audit, with unchanged historical evidence bytes and no universal freshness claim |
| Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | R1–R6 maps all literal dependencies, actual prior receipts and the exact requested delegated technical scopes | Requires actual immutable-head receiving reviews before literal reconciliation; a request, shared assignee or merge alone does not pass |
| Four already checked criteria: merged record; relevant modes; typed fields; named open-question owners | The existing merged record and [bounded reconciliation receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/25#issuecomment-6248705617) retain their original scope; this candidate sharpens current decisions | Preserve their checked state and literal text; no retrospective widening |

After actual source/receiving acceptance, required validation, ordinary protected signed merge and post-main readback, the issue's exact five unchecked lines can be reconciled against those receipts while preserving all other body text and native metadata. This source record does not claim a fresh Project-item state or close #40/#41, runtime validation, source-rights admission, quality measurement or other owners' research. Those separate obligations remain at their named interfaces.
