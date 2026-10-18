# T4: Agents & Integrations

Issue: #24 · Contract: 1.0.0 · Kinds: `agent_framework`, `tool`, `integration`, `mcp_server`, `memory_store`
Status: component research merged; external handoffs and central proposals remain open · Reconciled: 2026-10-17

This is the workstream summary for T4. All four component records and this summary are merged as reviewed research. This does not accept a production configuration or final versioned ruleset. #24–#28 remain open because external consuming-owner dispositions and issue acceptance work remain.

PRs #69, #70, #71 and #72 are merged. The component links below pin the reviewed revisions; they are historical evidence anchors, not unmerged dependencies. Original source/pricing access dates remain 2026-10-16 except explicitly dated rechecks. The 2026-10-17 corrections withdraw unsupported credential inheritance checks, fix the encryption key-reference false positive, and document the bounded Mem0 history-retention reproduction.

| Component | Issue | Decision record | Structured proposals |
| --- | --- | --- | --- |
| Agent Framework | #25 | [agent-framework.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/956d923ef335b49878ad31fee9ac8d18edf5e0b0/research/T4-agents-integrations/agent-framework.md) | 10 `agent_framework` items ([`catalog/proposals/t4a-*.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/956d923ef335b49878ad31fee9ac8d18edf5e0b0/catalog/proposals)) |
| Tools & APIs | #26 | [tools-apis.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/12188f1c8bb74c66a0ccbe6a46b46ff8323687ab/research/T4-agents-integrations/tools-apis.md) | 8 `tool` + 2 `integration` items ([`t4b-*.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/12188f1c8bb74c66a0ccbe6a46b46ff8323687ab/catalog/proposals)), 1 pricebook ([`pricing/proposals/t4b-anthropic-web-search.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/12188f1c8bb74c66a0ccbe6a46b46ff8323687ab/pricing/proposals/t4b-anthropic-web-search.json)) |
| MCP Servers | #27 | [mcp-servers.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/3d95c61efc2895d971415950dd4ebdfc1f23aba8/research/T4-agents-integrations/mcp-servers.md) | 9 `mcp_server` items ([`t4c-*.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/3d95c61efc2895d971415950dd4ebdfc1f23aba8/catalog/proposals)) |
| Agent Memory | #28 | [agent-memory.md](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/ec16c925c7038ea3ee0b88f0bb8054e4e1d8c6b2/research/T4-agents-integrations/agent-memory.md) | 6 `memory_store` items ([`t4d-*.json`](https://github.com/Pick-Your-AI/pick-your-ai-research/tree/ec16c925c7038ea3ee0b88f0bb8054e4e1d8c6b2/catalog/proposals)) |

## Scope and optionality

T4 answers whether a build takes actions, calls tools or keeps memory across interactions, and which orchestration approach fits. It is optional and must disappear cleanly when unused.

Synthetic rule mechanics checked against the v1 reference evaluator (`contracts/v1/reference/evaluate.py`, baseline ruleset plus the 24 T4 rule proposals, synthetic fixture build):

- With every T4 selection removed, or present but `enabled: false`, every rule triggered by a T4 selection (the five baseline T4 rules and all 24 proposals) evaluates to `skipped`. Two baseline rules that merely list a T4 kind among their affected kinds (`rule.embedding.dimension`, `rule.budget.monthly.cap`) are triggered by T3 and T6 selections and behave the same with or without T4.
- A build with an agent, tools, MCP and relational memory but no RAG, embedding model or vector database is valid for T4: `rule.memory.vector.storage` and `rule.embedding.dimension` are `skipped`. A vector database is not required for persistent memory.

Out of scope: building the product's agent runtime, and evaluating storage or vector products (T2 #9, T3 #13 and #15 own those).

## Triage and execution matrix

Live GitHub issue and Project API readback on 2026-10-17: all five issues remain open and **In Review**, with **Medium** priority, **Ready** readiness, **Unblocked** dependency status and **Unverified** research confidence. Assignees and triage fields were preserved; the older P2 vocabulary in repository guidance does not override the live Medium value.

| Issue | Live co-assignees | Merged research | Remaining work |
| --- | --- | --- | --- |
| #24 | @CompleteDotTech, @appletechie | Summary #73; all four component records | Complete component acceptance criteria and external workstream handoffs; do not close before children |
| #25 | @CompleteDotTech, @Mattycodes69 | #69: framework record and 10 catalog proposals | External capability/consumer dispositions; unresearched mappings remain named unknowns; actual engine consumer runs remain scoped with #11/#36 |
| #26 | @CompleteDotTech, @zwright8 | #70: tools/integrations record, 10 catalog proposals, 1 pricebook; corrected credential proposal | #13/#35/#39 boundaries and #40 credential/rule decisions; no unsupported inheritance resolver in v1 |
| #27 | @CompleteDotTech, @tynamite | #71: MCP record and 9 catalog proposals | External hosting/trust/deployment dispositions, #40 selection semantics and per-server/client revision evidence |
| #28 | @CompleteDotTech, @PUSHINGSQUARES | #72: memory record and 6 catalog proposals; encryption tests and bounded deletion reproduction | Storage and context dispositions; #35/#38 history-retention/purge decisions; #40 configuration evidence |

No duplicate issues, new execution blockers or priority changes are introduced. Contract proposals and external acceptance gate completion, not the already completed research merges. Unpriced or incomplete product facts stay in notes; owner confirmation is never inferred from shared assignment or silence.

## Research decisions by component

### Agent frameworks (#25)

- **Candidates compared (versions source-checked on PyPI/npm, 2026-10-16):** no framework (direct provider SDK loop), LangGraph 1.2.15, Microsoft Agent Framework 1.22.0 (Python), OpenAI Agents SDK 0.24.0 (Python) and 0.20.0 (JS), Google ADK 2.12.0, PydanticAI 2.57.0, CrewAI 1.15.28, smolagents 1.26.0, Agno 3.1.3, LlamaIndex (core 0.14.25, workflows 2.26.0), Strands Agents 1.61.1, Mastra 1.78.0. AutoGen 0.7.5 is archived, with no Microsoft bug fixes, security fixes or support ([Microsoft lifecycle update](https://github.com/microsoft/autogen/commit/004749e6b7102c8fd317b9b1499ce5807223c278), checked 2026-10-17), and Semantic Kernel 1.45.0 is superseded; both are recorded as not recommended for new builds.
- **Selection criteria:** language runtime; tool-calling approach; durable state and checkpointing; human approval hooks; MCP client transports and protocol revision; observability (OpenTelemetry vs vendor tracing, default telemetry egress); deployment form (library vs managed runtime); license.
- **Key findings:** "OpenAI-compatible" endpoints do not guarantee tool calling, `tool_choice`, strict schemas or the Responses API; engine configuration matters (vLLM tool parsers, Ollama limits). Tool definitions port across frameworks through MCP, but graphs, state schemas and checkpoints do not.
- **v1 limitation:** "no framework" cannot be selected, and the baseline rule `rule.agent.tools.framework` would block it.

### Tools and integrations (#26)

- **Taxonomy:** twelve reusable runtime categories (HTTP request, search/browse, database, file/document, code execution, communication, productivity, developer platform, cloud infrastructure, workflow automation, enterprise, domain-specific). The category describes what a tool touches, not what it changes.
- **Risk classes:** `read_only`, `write`, `high_impact`, `irreversible`, with approval defaults (none; allowlist plus audit; human approval by default; human approval always). Unclassified tools default to `irreversible`. v1 `side_effect` has only `read_only|mutating`; the finer class is carried as `x_side_effect_class` and proposed to #40.
- **Modelling:** a `tool` item is one operation family (for example `tool.github.issues-read` vs `tool.github.issues-write`) because OAuth scopes are coarser than risk. An `integration` item is the provider connection.
- **T3 boundary:** a provider with both ingestion and runtime actions keeps one provider identity. T3 #13 owns `data_source` ingestion semantics; T4 owns `tool`/`integration` runtime actions.

### MCP servers (#27)

- **Protocol:** the current MCP revision is **2026-07-28** (source-checked on modelcontextprotocol.io/specification/versioning). It replaces the `initialize` handshake with per-request version negotiation and a mandatory `server/discover`. 2025-11-25 and earlier are handshake-based. Clients and servers can support several versions, so the catalog must track a protocol-version set per server and per client.
- **Transports:** stdio and Streamable HTTP; HTTP+SSE is deprecated. Hosting has three categories: local process, self-hosted remote (a #9 hosting platform), and vendor-hosted remote (public egress required).
- **Trust:** criteria for `internal`, `trusted_external`, `untrusted_external` are proposed. These are proposed project classifications, not security certifications; registry presence does not certify safety. Trust in a server never makes its returned content, tool descriptions or annotations trustworthy.
- **Candidates:** GitHub (remote and local), Playwright, Stripe, Sentry, Atlassian, DBHub, and the reference fetch and filesystem servers (reference servers are "not production-ready").

### Agent memory (#28)

- **Taxonomy:** ten conceptual behaviours (in-session state, working, persistent agent state, user-scoped, organization-scoped, episodic, semantic, summarized history, retrieval-backed, explicit structured state). They are behaviours, not products, and map onto v1 `memory_type` (`working|session|long_term`) and `backing_type`.
- **Default:** no durable memory unless the user needs it. Session state on the framework's own store over #9 relational storage. Vector search only for large free-text memory, reusing the #15 vector database.
- **Privacy:** expiry and deletion are not erasure everywhere. Deleting an OpenAI conversation does not delete its items; Mem0 expiry hides records, and its pinned OSS deletion path retains prior text in SQLite history (see the scoped reproduction in the memory record). The builder must show deletion depth per product (handoff to #35).

## Shared catalog kinds

All 35 T4 CatalogItem proposals (10 frameworks, 8 tools, 2 integrations, 9 MCP servers and 6 memory stores) and the one T4 pricebook are now on main. They remain proposals with source-checked/unverified provenance; merge does not publish a production catalog. The frozen v1 contract is unchanged. Incomplete facts and unsupported meters remain note-only.

## Cross-component compatibility rules

24 rule proposals are valid v1 `Ruleset` rules (schema-checked, and every JSON pointer resolves to a real v1 field). Further proposals need contract changes and are written as text expressions. All are submitted for central review through #40; none is an approved ruleset.

| Case | Rule(s) | Evaluator outcome on synthetic builds |
| --- | --- | --- |
| 1. Framework requires model tool calling | `rule.t4.model.toolcalling` (warning) | `fail` when `supports_tool_calling` is false, `pass` when true |
| 2. Provider API supported but not every model feature | `rule.t4.model.api.surface`, `rule.t4.model.api.feature` | Needs #40: no API-surface field in v1 |
| 3. MCP transport unsupported by client | `rule.t4.mcp.transport.client-support` (canonical; same as #25's `transport.match`) | Needs #40: no client-transport field. Interim: `rule.t4.mcp.transport.sse-deprecated` |
| 4. MCP hosting or auth unavailable in deployment mode | `rule.t4.mcp.remote.air-gapped` (error), `auth.flow-available`, `stdio.colocation` | `fail` for a vendor-hosted remote server on an air-gapped platform; `skipped` for local stdio |
| 5. Memory backend needs absent storage | `rule.t4.memory.storage.backing` (warning) | `fail` with no storage or a mismatched storage type |
| 6. Persistent memory needed, only ephemeral configured | `rule.t4.memory.longterm.volatile` (v1 proxy); `persistence.required` needs #40 | `fail` for long-term memory on `in_memory` backing (synthetic item); `skipped` for a session store |
| 7. Tool permissions conflict with guardrail policy | `rule.t4.tool.scopes.allowed` (error), `rule.t4.tool.guardrail.targets` | `fail` when `required_scopes` is not a subset of `allowed_scopes` |
| 8. Tool usage adds recurring cost | `rule.t4.tool.cost.metered`, `rule.t4.integration.cost.metered`, `rule.t4.tool.cost.unknown` | `fail` (warning) for a metered tool with no cost policy |
| 9. All T4 selections absent or disabled | All T4 rules | `skipped` |
| 10. Agents without RAG or vector database | Baseline RAG and vector rules | `skipped`; no new rule needed |

Severity (`info|warning|error`) and outcome (`pass|fail|unknown|skipped`) are kept separate throughout. Each rule's participants, assumptions, user-facing message and correction are in its component note.

## Contract findings for #40 (consolidated)

These are proposals. Nothing under `contracts/` was changed.

1. **Rules only see one selection per kind.** Every baseline T4 rule references role `primary`. A build normally has several tools and MCP servers, so tools in other roles are never checked. Worse, two selections sharing role `primary` make `exists` resolve false, so `rule.agent.tools.framework` reports `skipped` instead of `unknown` (reproduced with the reference evaluator). Proposal: a quantifier over all enabled selections of a kind, and semantic rejection of duplicate primary roles before evaluation.
2. **`rule.memory.framework.compatibility` blocks real memory builds.** `supports_memory` has no defined meaning, so no real framework proposal asserts it. The rule is `error` with `on_unknown: block`, so every real framework plus memory store evaluates to `unknown` and blocks. Proposal: define or replace the field (for example `framework_refs` on `memory_store`) and downgrade to `warning` until it is populated.
3. **MCP:** `spec_mcp_server.transport` is single-valued (servers often speak several); no protocol-version field on either side; `sse` should be marked deprecated; no hosting category, maintainer, registry name or package pin; framework needs `mcp_client_transports`, `mcp_protocol_versions`, `mcp_client_capabilities`, `mcp_oauth_modes`.
4. **Tools:** explicit credential binding/resolution (direct, integration, provider-hosted or none), link cardinality, ambiguity outcomes and legacy migration; the former universal tool-local credential rule is withdrawn. Remaining proposals include `side_effect_class` (four values) and metrics `tools.high_impact_count`, `tools.irreversible_count`; `tools.mutating_count` should include integrations and MCP-exposed tools; auth values (`basic`, `jwt`, bearer/PAT); structured `rate_limits[]`; pricebook meters for per-second compute and per-execution billing.
5. **Memory:** configuration evidence for optional encryption/key consumption and covered history/storage layers; retention/purge evidence distinct from vector deletion. Remaining proposals include `scopes`, `deletion_modes`, `supports_export`, retention and TTL semantics, `storage_ref`, `vector_database_ref`, `managed_storage`, `regions`, `tenant_isolation`; `backing_type` values for graph and managed storage; a build-level persistence requirement; a `memory.max_injected_tokens` metric shared with #7.
6. **Framework:** `tool_calling_modes`, `model_api_surfaces`, state backends, human-approval support, telemetry egress; lifecycle mapping for "archived" and "superseded"; a way to select "no framework".
7. **Versioning:** hosted services and remote MCP servers change without a release tag. A snapshot-date convention for `version` is needed (with #41).

## Dependency and handoff matrix

External outgoing handoffs below remain pending. Requests are consolidated for T3 and T6, with each receiving issue named; a request is not acceptance. [Internal T4 receiving-owner dispositions](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509) accept the framework/tool/MCP/memory interfaces with explicit constraints; they do not fill missing product facts or approve #40 schemas.

| From | To | Information handed over | Owner | Status |
| --- | --- | --- | --- | --- |
| #25 | #6 AI Model | Populate `supports_tool_calling` and `supports_json_schema` per model and API surface, including reasoning-effort conditions | @zwright8, @PUSHINGSQUARES | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/6#issuecomment-6233367351) |
| #25 | #11 Inference Engine | Tool-calling prerequisites per engine (vLLM parser flags, Ollama `tool_choice` gap) | @zwright8, @Mattycodes69 | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334) |
| #28 | #7 Context Window | Memory and history tokens must fit `requested_context_tokens`; proposed injected-token metric | @zwright8, @appletechie | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/7#issuecomment-6233367558) |
| #27, #28 | #9 Hosting | Self-hosted MCP hosting categories and egress field; relational, object and file memory reuse `storage` | @Mattycodes69, @appletechie | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072) |
| #26, #28 | #13 Knowledge Base | Shared provider identity for ingestion vs actions; memory reuses knowledge storage semantics | @tynamite, @zabyxc01 | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13#issuecomment-6233368471) |
| #28 | #15 Vector Database | Vector-backed memory reuses the selected vector database (role `memory`) | @zabyxc01, @appletechie | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13#issuecomment-6233368471) |
| #25 | #16 RAG | Retrieval exposed as a tool vs native retrieval components | @zabyxc01, @appletechie | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/13#issuecomment-6233368471) |
| #26, #27, #28 | #35 Guardrails | Risk classes and approval defaults; MCP trust criteria and untrusted content; token passthrough; memory poisoning, consent, erasure gaps | @appletechie, @PUSHINGSQUARES | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6233368724) |
| #25, #28 | #36 Evaluation | Agent, tool-use and memory-quality evaluation hooks (not researched in T4) | @appletechie, @PUSHINGSQUARES | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6233368724) |
| #25, #27 | #37 Deployment | Managed runtimes; stdio needs process spawning; non-interactive targets cannot complete browser OAuth | @appletechie, @PUSHINGSQUARES | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6233368724) |
| #25, #26, #28 | #38 Monitoring | OpenTelemetry support, telemetry egress, rate-limit signals, memory growth and deletion jobs | @appletechie, @PUSHINGSQUARES | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6233368724) |
| #26, #27, #28 | #39 Cost Estimate | Pricing units (per request, per vCPU-second, per execution, credits), one priced item, graph edge `cost_policy → tool` | @appletechie, @PUSHINGSQUARES | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6233368724) |
| all | #40 Compatibility Schema | Rule proposals and the contract findings above | @zwright8, @tynamite | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6233368930) |
| all | #41 Data Freshness | Versioning of hosted services; grading of vendor docs and JavaScript-rendered pages | @tynamite, @PUSHINGSQUARES | Pending — [request](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6233369204) |


### Reconciliation with merged T2 research

T4's receiving-owner dispositions are now explicit:

- **#9 -> #27:** [accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072): hosting placement stays with T2; MCP transport/protocol/auth/trust stays with T4. Egress/process/locality capabilities require evidence; no new v1 fields are inferred.
- **#9 -> #28:** [accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072): T2 supplies infrastructure storage; T4 retains memory scope, consent, retention and deletion. Storage choice is not proof of ACLs or erasure.
- **#11 -> #25:** [accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/11#issuecomment-6233323334): tool/parser/schema/API support is conditional on the complete versioned request tuple. [Synthetic consumer cases](../../tests/fixtures/t4-engine-consumer.md) specify future checks; no engine run is certified by those examples.

These are directional acknowledgments. The reciprocal #9/#11 requests in the table above still need their receiving owners' decisions. The [T2 ledger](../T2-infrastructure/handoffs.md) links the actual T4 receipts.

## Data-source provenance

Original factual claims in the component notes cite primary sources accessed on 2026-10-16, with an evidence ID (prefixes A, B, C, D by component). Versions were read from PyPI, npm, GitHub release pages and vendor documentation. Evidence grades follow `docs/RESEARCH_METHOD.md` and the [adopted #41 interim policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Checked publisher documentation, package metadata and registry entries are not independent verification. All 112 provenance entries (111 corrected here and one already unverified) in the linked component proposals and pricebook remain `unverified`; their source access dates, `checked_at`, versions, facts and pricing conditions are retained. Eligible documentation may support a constraint passing while its evidence remains unverified; synthetic evaluator outcomes establish only rule mechanics. Final rules and contract changes require central versioned review through #40. Version-pinned facts are rechecked when the selection changes or a source is corrected; current-state facts such as prices remain as of their access date, with no TTL imposed by this interim policy. One pricebook rate (Anthropic web search, USD 10 per 1,000 searches) was re-checked against the vendor page during consolidation.

## Limitations

- The original session could not read the Project board; the 2026-10-17 reconciliation verified the live fields stated above. These are a snapshot, not automatic synchronization.
- Some vendor pages were read through a text-extracting fetcher; quotations are as extracted. Pages that render tables in JavaScript (Slack rate tiers, some pricing pages) are listed as gaps.
- No full framework, MCP server or memory service was exercised. The memory record separately documents a pinned, isolated Mem0 deletion-method/SQLite reproduction with synthetic vector/entity stubs; it does not certify the deployed service.
- The original research used Python 3.13 locally. Evidence corrections were validated on Python 3.12 with pinned requirements, on each component head, each slice against current main, and all four together; the summary was also validated separately. Automation checks structure and references, not independent product behaviour or receiving-owner acceptance.
- Schema validity does not prove claims are accurate or current.

## Outstanding questions

Each component note ends with an open-questions table naming the follow-up issue and owner. The cross-cutting ones are the #40 contract findings above, and confirming every handoff in the matrix.

## Pull requests

All four component PRs merged using partial-work references. Their reviewed heads are retained below for evidence traceability. Issue completion still requires acceptance criteria and external handoff dispositions; no issue is closed by this summary.

| PR | Reviewed merged head | Research slice |
| --- | --- | --- |
| [#69](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/69) | `956d923ef335b49878ad31fee9ac8d18edf5e0b0` | agent-framework.md |
| [#70](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/70) | `12188f1c8bb74c66a0ccbe6a46b46ff8323687ab` | tools-apis.md |
| [#71](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/71) | `3d95c61efc2895d971415950dd4ebdfc1f23aba8` | mcp-servers.md |
| [#72](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/72) | `ec16c925c7038ea3ee0b88f0bb8054e4e1d8c6b2` | agent-memory.md |
