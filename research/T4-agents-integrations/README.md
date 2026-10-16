# T4: Agents & Integrations

Issue: #24 · Contract: 1.0.0 · Kinds: `agent_framework`, `tool`, `integration`, `mcp_server`, `memory_store`
Status: draft · Last researched: 2026-10-16

This is the workstream summary for T4. It consolidates the four component decision records and does not replace them. Every finding below is **draft research awaiting review**. No handoff has been confirmed by a consuming owner yet, so nothing here is an accepted decision.

| Component | Issue | Decision record | Structured proposals |
| --- | --- | --- | --- |
| Agent Framework | #25 | [agent-framework.md](agent-framework.md) | 10 `agent_framework` items (`catalog/proposals/t4a-*.json`) |
| Tools & APIs | #26 | [tools-apis.md](tools-apis.md) | 9 `tool` + 2 `integration` items (`t4b-*.json`), 1 pricebook (`pricing/proposals/t4b-anthropic-web-search.json`) |
| MCP Servers | #27 | [mcp-servers.md](mcp-servers.md) | 9 `mcp_server` items (`t4c-*.json`) |
| Agent Memory | #28 | [agent-memory.md](agent-memory.md) | 6 `memory_store` items (`t4d-*.json`) |

## Scope and optionality

T4 answers whether a build takes actions, calls tools or keeps memory across interactions, and which orchestration approach fits. It is optional and must disappear cleanly when unused.

Verified against the v1 reference evaluator (`contracts/v1/reference/evaluate.py`, baseline ruleset plus the 25 T4 rule proposals, synthetic fixture build):

- With every T4 selection removed, or present but `enabled: false`, every rule triggered by a T4 selection (the five baseline T4 rules and all 25 proposals) evaluates to `skipped`. Two baseline rules that merely list a T4 kind among their affected kinds (`rule.embedding.dimension`, `rule.budget.monthly.cap`) are triggered by T3 and T6 selections and behave the same with or without T4.
- A build with an agent, tools, MCP and relational memory but no RAG, embedding model or vector database is valid for T4: `rule.memory.vector.storage` and `rule.embedding.dimension` are `skipped`. A vector database is not required for persistent memory.

Out of scope: building the product's agent runtime, and evaluating storage or vector products (T2 #9, T3 #13 and #15 own those).

## Triage and execution matrix

GitHub state was refreshed on 2026-10-16 from the public issue pages. The Project board itself could not be read (see Limitations), so Project field values are not verified here.

| Issue | State and owner (verified) | Existing artifacts before this work | Delivered in this round | Remaining acceptance gaps | Actual blockers | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| #24 T4 parent | Open · @CompleteDotTech · `type: workstream`, `optional capability` · native sub-issues #25–28 (0 of 4 done) | None | This summary | All four sub-issues; owner-confirmed handoffs | None (sub-issue completion only) | Merge last, after #25–28 |
| #25 Agent Framework | Open · @CompleteDotTech · `type: research`, `optional capability` | None | Decision record, 10 catalog items, 4 v1-valid rules (a fifth, on SSE, was merged into the #27 rule), 11 rules needing #40 (2 shared with #27) | Owner review; handoffs to #6, #11, #16, #26, #27, #28, #35, #36, #37, #38 unconfirmed | None | Review PR; request #6 and #11 owners |
| #26 Tools & APIs | Open · @CompleteDotTech · `type: research`, `optional capability` | None | Decision record, 11 catalog items, 1 pricebook, 11 v1-valid rules, 3 needing #40 | Owner review; #35 and #39 handoffs unconfirmed; listed re-fetches | None | Review PR; request #35 and #39 owners |
| #27 MCP Servers | Open · @CompleteDotTech · `type: research`, `optional capability`, `topic: compatibility` | None | Decision record, 9 catalog items, 6 v1-valid rules, 6 needing #40 | Owner review; #9, #35, #37 handoffs unconfirmed; per-server 2026-07-28 support | None | Review PR; request #9, #35, #37 owners |
| #28 Agent Memory | Open · @CompleteDotTech · `type: research`, `optional capability`, `topic: data-governance` | None | Decision record, 6 catalog items, 4 v1-valid rules, 5 needing #40 | Owner review; storage handoff to #9, #13, #15 unconfirmed | None | Review PR; request #9 and T3 owners |

Classification under the triage rules:

- **Ready (executed):** #25, #26, #27, #28 research; #24 summary.
- **Needs input (informational, not blocking):** model tool-calling facts (#6), engine tool-calling prerequisites (#11), storage and vector catalogs (#9, #15), pricing semantics (#39). Each note records the unknown and continues.
- **Awaiting review:** all contract-change proposals (#40) and all handoffs. These gate closure, not research.
- **Duplicates found:** none. **New issues or sub-issues needed:** none. Small follow-ups are checklist items on the existing issues (each note's "Open questions" table).
- **Priority:** P2 remains appropriate for all five. No documented dependency or product decision justifies promotion.
- **Readiness:** Ready for #25–28. No native blockers exist; every relationship listed in `docs/DEPENDENCIES.md` for T4 is informational or a compatibility relationship.

## Research decisions by component

### Agent frameworks (#25)

- **Candidates compared (versions verified on PyPI/npm, 2026-10-16):** no framework (direct provider SDK loop), LangGraph 1.2.15, Microsoft Agent Framework 1.22.0 (Python), OpenAI Agents SDK 0.24.0 (Python) and 0.20.0 (JS), Google ADK 2.12.0, PydanticAI 2.57.0, CrewAI 1.15.28, smolagents 1.26.0, Agno 3.1.3, LlamaIndex (core 0.14.25, workflows 2.26.0), Strands Agents 1.61.1, Mastra 1.78.0. AutoGen 0.7.5 is in maintenance mode and Semantic Kernel 1.45.0 is superseded; both are recorded as not recommended for new builds.
- **Selection criteria:** language runtime; tool-calling approach; durable state and checkpointing; human approval hooks; MCP client transports and protocol revision; observability (OpenTelemetry vs vendor tracing, default telemetry egress); deployment form (library vs managed runtime); license.
- **Key findings:** "OpenAI-compatible" endpoints do not guarantee tool calling, `tool_choice`, strict schemas or the Responses API; engine configuration matters (vLLM tool parsers, Ollama limits). Tool definitions port across frameworks through MCP, but graphs, state schemas and checkpoints do not.
- **v1 limitation:** "no framework" cannot be selected, and the baseline rule `rule.agent.tools.framework` would block it.

### Tools and integrations (#26)

- **Taxonomy:** twelve reusable runtime categories (HTTP request, search/browse, database, file/document, code execution, communication, productivity, developer platform, cloud infrastructure, workflow automation, enterprise, domain-specific). The category describes what a tool touches, not what it changes.
- **Risk classes:** `read_only`, `write`, `high_impact`, `irreversible`, with approval defaults (none; allowlist plus audit; human approval by default; human approval always). Unclassified tools default to `irreversible`. v1 `side_effect` has only `read_only|mutating`; the finer class is carried as `x_side_effect_class` and proposed to #40.
- **Modelling:** a `tool` item is one operation family (for example `tool.github.issues-read` vs `tool.github.issues-write`) because OAuth scopes are coarser than risk. An `integration` item is the provider connection.
- **T3 boundary:** a provider with both ingestion and runtime actions keeps one provider identity. T3 #13 owns `data_source` ingestion semantics; T4 owns `tool`/`integration` runtime actions.

### MCP servers (#27)

- **Protocol:** the current MCP revision is **2026-07-28** (verified on modelcontextprotocol.io/specification/versioning). It replaces the `initialize` handshake with per-request version negotiation and a mandatory `server/discover`. 2025-11-25 and earlier are handshake-based. Clients and servers can support several versions, so the catalog must track a protocol-version set per server and per client.
- **Transports:** stdio and Streamable HTTP; HTTP+SSE is deprecated. Hosting has three categories: local process, self-hosted remote (a #9 hosting platform), and vendor-hosted remote (public egress required).
- **Trust:** criteria for `internal`, `trusted_external`, `untrusted_external` are proposed. Trust in a server never makes its returned content, tool descriptions or annotations trustworthy.
- **Candidates:** GitHub (remote and local), Playwright, Stripe, Sentry, Atlassian, DBHub, and the reference fetch and filesystem servers (reference servers are "not production-ready").

### Agent memory (#28)

- **Taxonomy:** ten conceptual behaviours (in-session state, working, persistent agent state, user-scoped, organization-scoped, episodic, semantic, summarized history, retrieval-backed, explicit structured state). They are behaviours, not products, and map onto v1 `memory_type` (`working|session|long_term`) and `backing_type`.
- **Default:** no durable memory unless the user needs it. Session state on the framework's own store over #9 relational storage. Vector search only for large free-text memory, reusing the #15 vector database.
- **Privacy:** expiry and deletion are not erasure everywhere. Deleting an OpenAI conversation does not delete its items; Mem0 expiry hides records. The builder must show deletion depth per product (handoff to #35).

## Shared catalog kinds

All proposals use the merged v1 contract without changes. 35 catalog files and 1 pricebook pass `scripts/validate_research.py`. Optional booleans (for example `supports_mcp`) are included only where a primary source verified them, so absence means "not verified", not "false".

## Cross-component compatibility rules

25 rule proposals are valid v1 `Ruleset` rules (schema-checked, and every JSON pointer resolves to a real v1 field). Further proposals need contract changes and are written as text expressions. All are submitted for central review through #40; none is an approved ruleset.

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
| 9. Build without agents | All T4 rules | `skipped` |
| 10. Agents without RAG or vector database | Baseline RAG and vector rules | `skipped`; no new rule needed |

Severity (`info|warning|error`) and outcome (`pass|fail|unknown|skipped`) are kept separate throughout. Each rule's participants, assumptions, user-facing message and correction are in its component note.

## Contract findings for #40 (consolidated)

These are proposals. Nothing under `contracts/` was changed.

1. **Rules only see one selection per kind.** Every baseline T4 rule references role `primary`. A build normally has several tools and MCP servers, so tools in other roles are never checked. Worse, two selections sharing role `primary` make `exists` resolve false, so `rule.agent.tools.framework` reports `skipped` instead of `unknown` (reproduced with the reference evaluator). Proposal: a quantifier over all enabled selections of a kind, and semantic rejection of duplicate primary roles before evaluation.
2. **`rule.memory.framework.compatibility` blocks real memory builds.** `supports_memory` has no defined meaning, so no real framework proposal asserts it. The rule is `error` with `on_unknown: block`, so every real framework plus memory store evaluates to `unknown` and blocks. Proposal: define or replace the field (for example `framework_refs` on `memory_store`) and downgrade to `warning` until it is populated.
3. **MCP:** `spec_mcp_server.transport` is single-valued (servers often speak several); no protocol-version field on either side; `sse` should be marked deprecated; no hosting category, maintainer, registry name or package pin; framework needs `mcp_client_transports`, `mcp_protocol_versions`, `mcp_client_capabilities`, `mcp_oauth_modes`.
4. **Tools:** `side_effect_class` (four values) and metrics `tools.high_impact_count`, `tools.irreversible_count`; `tools.mutating_count` should include integrations and MCP-exposed tools; auth values (`basic`, `jwt`, bearer/PAT); structured `rate_limits[]`; pricebook meters for per-second compute and per-execution billing.
5. **Memory:** `scopes`, `deletion_modes`, `supports_export`, retention and TTL semantics, `storage_ref`, `vector_database_ref`, `managed_storage`, `regions`, `tenant_isolation`; `backing_type` values for graph and managed storage; a build-level persistence requirement; a `memory.max_injected_tokens` metric shared with #7.
6. **Framework:** `tool_calling_modes`, `model_api_surfaces`, state backends, human-approval support, telemetry egress; lifecycle states for "maintenance" and "superseded"; a way to select "no framework".
7. **Versioning:** hosted services and remote MCP servers change without a release tag. A snapshot-date convention for `version` is needed (with #41).

## Dependency and handoff matrix

No handoff is confirmed yet. Each row needs a linked comment or PR review from the receiving owner.

| From | To | Information handed over | Owner | Status |
| --- | --- | --- | --- | --- |
| #25 | #6 AI Model | Populate `supports_tool_calling` and `supports_json_schema` per model and API surface, including reasoning-effort conditions | @zwright8 | Pending |
| #25 | #11 Inference Engine | Tool-calling prerequisites per engine (vLLM parser flags, Ollama `tool_choice` gap) | @Mattycodes69 | Pending |
| #28 | #7 Context Window | Memory and history tokens must fit `requested_context_tokens`; proposed injected-token metric | @zwright8 | Pending |
| #27, #28 | #9 Hosting | Self-hosted MCP hosting categories and egress field; relational, object and file memory reuse `storage` | @Mattycodes69 | Pending |
| #26, #28 | #13 Knowledge Base | Shared provider identity for ingestion vs actions; memory reuses knowledge storage semantics | @zabyxc01 | Pending |
| #28 | #15 Vector Database | Vector-backed memory reuses the selected vector database (role `memory`) | @zabyxc01 | Pending |
| #25 | #16 RAG | Retrieval exposed as a tool vs native retrieval components | @zabyxc01 | Pending |
| #26, #27, #28 | #35 Guardrails | Risk classes and approval defaults; MCP trust criteria and untrusted content; token passthrough; memory poisoning, consent, erasure gaps | @PUSHINGSQUARES | Pending |
| #25, #28 | #36 Evaluation | Agent, tool-use and memory-quality evaluation hooks (not researched in T4) | @PUSHINGSQUARES | Pending |
| #25, #27 | #37 Deployment | Managed runtimes; stdio needs process spawning; non-interactive targets cannot complete browser OAuth | @PUSHINGSQUARES | Pending |
| #25, #26, #28 | #38 Monitoring | OpenTelemetry support, telemetry egress, rate-limit signals, memory growth and deletion jobs | @PUSHINGSQUARES | Pending |
| #26, #27, #28 | #39 Cost Estimate | Pricing units (per request, per vCPU-second, per execution, credits), one priced item, graph edge `cost_policy → tool` | @PUSHINGSQUARES | Pending |
| all | #40 Compatibility Schema | Rule proposals and the contract findings above | @tynamite | Pending |
| all | #41 Data Freshness | Versioning of hosted services; grading of vendor docs and JavaScript-rendered pages | @tynamite | Pending |

## Data-source provenance

Every factual claim in the component notes cites a primary source accessed on 2026-10-16, with an evidence ID (prefixes A, B, C, D by component). Versions were read from PyPI, npm, GitHub release pages and vendor documentation. Evidence grades follow `docs/RESEARCH_METHOD.md` until #41 finalises the policy. One pricebook rate (Anthropic web search, USD 10 per 1,000 searches) was re-checked against the vendor page during consolidation.

## Limitations

- The GitHub Project board and the GitHub API were not readable from this session, so Project field values (Status, Priority, Readiness) are not verified here. Several issue pages show "Backlog" in their metadata while their timelines say "Todo".
- Some vendor pages were read through a text-extracting fetcher; quotations are as extracted. Pages that render tables in JavaScript (Slack rate tiers, some pricing pages) are listed as gaps.
- No framework, MCP server or SDK was executed. Behaviour is documented, not measured.
- Validation ran on Python 3.13 locally; CI uses 3.12.
- Schema validity does not prove claims are accurate or current.

## Outstanding questions

Each component note ends with an open-questions table naming the follow-up issue and owner. The cross-cutting ones are the #40 contract findings above, and confirming every handoff in the matrix.

## Pull requests

To be filled in when the PRs are opened. Each component PR uses `Refs #n`, not `Closes`, because handoffs are not yet confirmed.
