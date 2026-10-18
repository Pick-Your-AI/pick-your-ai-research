# T4: Agent Memory

Issue: #28 · Contract: 1.0.0 · Kinds: `memory_store`
Status: research merged via #72; external handoffs and contract proposals remain open · Last researched: 2026-10-17

## Evidence status correction

Evidence metadata corrected at 2026-10-17T02:17:46Z under the [adopted #41 interim policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Checked primary documentation, publisher package metadata, registry entries and source inspection are not independent verification. These catalog claims remain `unverified`; the original facts, versions, source access dates and `checked_at` are unchanged. No qualifying independent corroboration or runtime reproduction was supplied. Vendor capability statements remain documented claims, not measurements.

A proposed constraint may pass on eligible, versioned documentation while its evidence remains unverified. Missing eligible evidence remains unknown; absence from an unmarked capability list does not establish lack of support. Synthetic evaluator results check rule mechanics only and do not verify product behaviour. All rules and contract changes still require central versioned review through #40. Receiving-owner handoffs remain pending and this correction does not satisfy issue completion.

Follow-up on 2026-10-17: corrected the proposed encryption rule's key-reference false positive and source-checked Mem0 OSS deletion against v2.2.1 source pinned to commit `94c3fe9f238f3dbf29c9ce98643bd71eb13077cd` (D57, D58). An isolated synthetic method test also reproduced retained SQLite history text; it does not establish full-service erasure behaviour or upgrade the catalog claims above.

## User decision

What should the agent remember within a session and across sessions, where is it stored, and for how long?

The builder has to help the user make four separate choices. They are often bundled into one "memory" checkbox, but they have different storage, privacy and cost consequences:

1. **Within-session state:** does the agent need conversation history and intermediate state to survive a process restart or move between workers?
2. **Cross-session memory:** should anything persist after the session ends, and at what scope (one user, one organization, one application)?
3. **Retention and deletion:** how long is each kind kept, who can see it, and how is it erased or exported on request?
4. **Storage choice:** process memory, a relational or key-value store, object or file storage, a vector index, or a provider-managed memory service. Storage products themselves are catalogued by #9 (`storage`), #13 (`knowledge_base`) and #15 (`vector_database`). This note only references them.

Out of scope: evaluating storage products (#9, #13, #15) and designing a retrieval pipeline (#16).

### Deployment modes

| Mode | What memory looks like | Candidates in this note |
| --- | --- | --- |
| **API** (provider-hosted model, no own infrastructure) | The provider stores the conversation state, or the application does it client-side. | OpenAI Conversations API and `previous_response_id` (D14, D15). The Anthropic memory tool is API-invoked, but your application stores the files (D31). |
| **Managed** (cloud memory service) | A hosted service stores events and extracted memories, with its own TTL, IAM and encryption. | Amazon Bedrock AgentCore Memory (D25–D28); Google Agent Platform Memory Bank and VertexAiSessionService (D17, D21–D24); Zep Cloud (D40–D42); Mem0 Platform (D35); Letta Cloud (D45). |
| **Self-hosted** (library plus your own database) | Framework session or checkpoint stores, or a self-hosted memory layer, on storage the user operates (#9). | LangGraph checkpointers and stores (D1–D9); OpenAI Agents SDK sessions (D12); ADK DatabaseSessionService (D17); Microsoft Agent Framework history and context providers (D48–D50); Mem0 OSS (D33–D35); Graphiti (D39); Redis with TTL (D54). |

## Memory taxonomy

These are **conceptual behaviours, not separate products**. One product often implements several of them. For example, ADK `DatabaseSessionService` stores session state, user-scoped state and app-scoped state in one database (D18), and AgentCore Memory stores raw events and extracted long-term records in one resource (D25, D27).

The v1 contract has only two descriptive fields:
- `spec_memory_store.memory_type`: `working | session | long_term`
- `spec_memory_store.backing_type`: `in_memory | relational | vector | object | file`

The table maps each behaviour onto them.

| Behaviour | Definition used in this note | Typical scope | Typical persistence | v1 `memory_type` | v1 `backing_type` (typical) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| In-session conversational state | Ordered message and tool-call history of one conversation | session / thread | lifetime of the session; durable only if the store is | `session` | `in_memory`, `relational` | D2, D12, D17 |
| Working memory | Scratch state for one invocation or step, not carried to the next turn (ADK `temp:` state; graph state inside a step) | invocation | none | `working` | `in_memory` | D18 |
| Persistent agent state | Resumable execution state (checkpoints, pending interrupts) so a run survives restarts or moves workers | thread | until deleted or expired | `session` | `relational`, `in_memory` (Redis) | D2, D4, D9 |
| User-scoped memory | Facts and preferences about one user, shared across that user's sessions (ADK `user:` state; Mem0 `user_id`; AgentCore `actorId` namespaces; Memory Bank `scope`) | user | long-lived | `long_term` | any | D18, D22, D25, D37 |
| Organization- or app-scoped memory | Knowledge shared by all users of an app or tenant (ADK `app:` state; Mem0 Platform org/project and `app_id`) | app / org / tenant | long-lived | `long_term` | any | D18, D35 |
| Episodic memory | Records of past events or interactions, often used as few-shot examples (AgentCore `episodicMemoryStrategy`) | user or agent | long-lived | `long_term` | any | D5, D26 |
| Semantic or factual memory | Extracted facts, either as a profile document or a growing collection | user or org | long-lived | `long_term` | `relational` (profile), `vector` (collection) | D5, D25 |
| Procedural memory | Learned instructions or prompt changes. Not in the issue list; recorded for completeness | agent | long-lived | `long_term` | `relational`, `file` | D5 |
| Summarized history | A compacted or summarized form of earlier turns kept in place of the full history (OpenAI compaction; AgentCore `summaryMemoryStrategy`) | session or user | session or long-lived | `session` or `long_term` | any | D12, D14, D25 |
| Retrieval-backed memory | Memory that is searched at query time and not injected wholesale (Letta archival memory; ADK `VertexAiRagMemoryService`; LangGraph store with an index) | any | long-lived | `long_term` | `vector` (or keyword) | D3, D19, D46 |
| Explicit structured state | Typed fields the application reads and writes deterministically (shopping cart, workflow step, profile JSON) | session, user or app | per store | `session` or `long_term` | `relational`, `in_memory` | D5, D16, D18 |

### What v1 cannot express

All of these are note-only today. They are proposed to #40 below.

- **Scope:** v1 has no field for user, org, app, agent or session scope. `memory_type=long_term` does not say whose memory it is, so tenant isolation cannot be checked.
- **Content kind:** v1 has no field separating episodic, semantic, procedural or summarized memory.
- **Multiple behaviours in one product:** `memory_type` is a single value, but ADK `DatabaseSessionService` is session plus user plus app state, and AgentCore is short-term plus long-term.
- **Durability:** `memory_type=session` does not say whether a session survives a restart. ADK `InMemorySessionService` and `DatabaseSessionService` are both `session`, and only the backing type distinguishes them.
- **Retention:** `settings_memory_store.ttl_hours` (integer ≥1) exists, but there is no catalog field for:
  - minimum or maximum TTL (AgentCore long-term records need at least 31 days, D26);
  - default retention (OpenAI conversations have no 30-day TTL, D14; AgentCore records do not expire by default, D26);
  - TTL semantics (Mem0 `expiration_date` hides records and does not delete them, D36; AgentCore expired records can still be returned for "a few days", D26).
- **Deletion, export and consent:** v1 has no fields. Deletion depth also differs: OpenAI conversation deletion keeps the items (D15), Mem0 OSS deletion retains prior memory text in SQLite history (D57, D58), and Zep leaves derived node summaries (D41).
- **Storage and vector references:** COMPONENTS.md says `memory_store` "may reuse `vector_database` or `storage`", but `spec_memory_store` has no `storage_ref` or `vector_database_ref`.
  - The build link `memory_store stored_in vector_database` exists in `BuildSnapshot.links` (contracts/v1/docs/DEPENDENCIES.md).
  - The rule language cannot traverse links. Rules therefore fall back to "the primary `storage` or `vector_database` selection", which can be the wrong instance.
- **Backing types outside the enum:**
  - graph backing (Graphiti and Zep use Neo4j, FalkorDB or Neptune, D39);
  - "managed or undisclosed" for provider services, whose physical backing is not documented;
  - "client-implemented", for the Anthropic memory tool, where the application chooses storage (D31).
- **Encryption:** `encryption_at_rest` is a boolean. It cannot separate provider-managed keys from customer-managed keys (AgentCore and Memory Bank support CMK, D24, D25) or record optional application-level encryption (LangGraph `EncryptedSerializer`, D2; OpenAI `EncryptedSession`, D12).
- **Encryption configuration evidence:** `settings_memory_store.encryption_key_ref` is an opaque secret reference. Its presence does not prove that the selected store consumes it or that encryption is enabled. The v1 rule below checks documented default encryption only; optional encryption and configuration verification need #40 review with #35.
- **Access control:** the only access-related field is `settings_memory_store.encryption_key_ref`. There is no credential reference and no IAM permission list.

## Candidate options

Versions come from the PyPI JSON API on 2026-10-16. "Unknown" means not found in the fetched primary source.

### Framework-native state and persistence

| Candidate | Version (upload date) | License | Memory behaviours | Scope keys | Backends documented | Retention / TTL | Deletion / export | Encryption | Hosting | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LangGraph checkpointers | `langgraph` 1.2.15 (2026-10-12); `langgraph-checkpoint` 4.3.0; `-postgres` 3.2.0 (2026-10-14); `-sqlite` 3.1.2; `-mongodb` 0.5.1; `-redis` 0.5.2 (2026-08-20, Redis-maintained); `-aws` 1.2.5 | MIT | in-session state, persistent agent state | `thread_id` | InMemorySaver, SQLite, Postgres, MongoDB, Cosmos DB (D2); Redis (D9); AgentCore Memory, DynamoDB+S3, Valkey (D29) | OSS savers: none documented, only "prune" or a scheduled job (D1, D2). Redis saver: `default_ttl` in minutes (D9). LangSmith Agent Server: `checkpointer.ttl` in minutes, strategy `delete` or `keep_latest` (D4) | `delete_thread` required on savers (D2) | optional `EncryptedSerializer` (AES; auto on LangSmith when `LANGGRAPH_AES_KEY` is set) (D2) | library; self-hosted or LangSmith managed | D1–D4, D7–D9, D11, D29 |
| LangGraph Store (and LangMem) | store ships in `langgraph-checkpoint-postgres` 3.2.0 (D7); `langmem` 0.0.30 (2025-10-27) | MIT | user-, org- or app-scoped long-term memory; semantic, episodic and procedural (D5) | namespace tuple, e.g. `(user_id, "memories")` (D3, D6) | InMemoryStore, PostgresStore, MongoDBStore, RedisStore, UpstashStore (D3) | PostgresStore: TTL in minutes with a sweeper that must be started explicitly (D7 source); Agent Server `store.ttl` with `refresh_on_read` (D4); Redis store `default_ttl` (D9) | `delete(namespace, key)` (D3); no bulk export documented | not documented for stores | library; self-hosted or LangSmith managed | D3–D7, D10 |
| OpenAI Agents SDK sessions | `openai-agents` 0.24.0 (2026-10-15) | MIT | in-session conversational state; summarized history via compaction | `session_id` (does **not** authenticate the user, D12) | SQLite (memory or file), AsyncSQLite, Redis, SQLAlchemy, MongoDB, Dapr, OpenAI Conversations, AdvancedSQLite, EncryptedSession wrapper | Dapr `ttl` (store-dependent); EncryptedSession `ttl` (seconds in the example); others none | `clear_session()`, `pop_item()` | `EncryptedSession` wrapper; it does not verify completeness or order (D12) | library | D12, D13 |
| Google ADK SessionService and MemoryService | `google-adk` 2.12.0 (2026-10-13) | Apache-2.0 | session state; `user:` (user-scoped), `app:` (app-scoped), `temp:` (working) state; long-term memory via MemoryService | `app_name`, `user_id`, `session_id` | Session: InMemory, Database (PostgreSQL, MySQL, SQLite), VertexAi. Memory: InMemory (keyword match), VertexAiMemoryBank, VertexAiRag (vector similarity) | not documented in ADK | `delete_session(app_name, user_id, session_id)` (D17) | per backend | library; VertexAi services are managed | D16–D20 |
| Microsoft Agent Framework | `agent-framework` 1.22.0 (2026-10-15) | MIT (PyPI classifier) | session history; context providers that inject memories | `AgentSession`; the docs say to bind sessions to the authenticated user or tenant (D48) | built-in: in-memory history only. Context providers: Cosmos DB, Redis, Mem0 (Python), Foundry, Neo4j, Valkey (C#) (D50). Custom providers for others | not documented | not documented | not documented | library | D48–D51 |
| Semantic Kernel agent memory | `semantic-kernel` 1.45.0 (2026-10-06) | MIT (PyPI classifier) | `Mem0Provider` (long-term), `WhiteboardProvider` (short-term) | `ApplicationId`, `AgentId`, `ThreadId`, `UserId` | Mem0 service | not documented | not documented | not documented | library. **Experimental** (D52) | D52, D53 |

### Dedicated memory layers

| Candidate | Version | License | Behaviours | Scope keys | Backends | Retention / TTL | Deletion / export | Tenant isolation | Hosting | Status flag | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mem0 OSS | `mem0ai` 2.2.1 (2026-09-25) | Apache-2.0 | LLM-extracted semantic memory; raw storage with `infer=False` | `user_id`, `agent_id`, `run_id` (D37) | 22 vector stores in Python; default local Qdrant; history in SQLite; self-hosted server uses Postgres with pgvector (D33, D34) | `expiration_date` (YYYY-MM-DD, UTC) **hides, does not delete** (D36) | `delete`, `delete_all` remove vector records but retain prior text in SQLite history (D57, D58); no batch delete; no export (D35) | "No org/project concept" (D35) | library or Docker self-host | graph memory removed from OSS (D35) | D32–D38, D57, D58 |
| Mem0 Platform | n/a (service) | proprietary | as OSS, plus native graph | adds `app_id` and org/project (D35) | undisclosed | `expiration_date` as OSS | `batch_delete` up to 1000 per call; Memory Export jobs (D35) | multi-org and multi-project with roles (D35) | managed | — | D35 |
| Zep Cloud | `zep-cloud` SDK 4.0.0 (2026-10-14) | SDK license not in PyPI metadata (unknown) | temporal knowledge graph of users and threads | user, thread, graph; account and project isolation (D42) | undisclosed (Graphiti engine) | none by default; admin-managed retention policies (`off`, `report_only`, `enforce`) (D40) | delete edge, node, episode, thread, user, graph; asynchronous. Derived node summaries may keep deleted text (D41). Backups up to 365 days (D40) | account and project | managed or BYOC | **Community Edition deprecated** (D42) | D40–D43 |
| Graphiti | `graphiti-core` 0.31.1 (2026-10-15) | Apache-2.0 (PyPI; pinned repository LICENSE and project metadata at D65) | temporal facts with validity windows; changed facts are invalidated, not deleted (D39) | `group_id` on episode writes; `group_ids` on search/retrieval, with provider-specific routing and default/empty-scope limits (D61–D64) | Neo4j 5.26, FalkorDB 1.1.2, Neptune; Kuzu deprecated | n/a (application-managed) | unknown | Not established by partition IDs; selected authorization/ACL boundary untested (D61–D64) | self-host only | — | D39, D61–D65 |
| Letta | `letta` 0.34.12 (2026-10-12) is now **Letta Code**; the V1 API server is archived (D44) | Apache-2.0 (D45) | memory blocks (always in context), files, archival memory (vector), external RAG (D46) | agent | Letta Cloud by default; git-tracked MemFS (D45) | unknown | unknown | unknown | managed (Letta Cloud); local CLI | **V1 self-hosted server archived** | D44–D47 |

### Provider-hosted memory and state

| Candidate | Version / API | Behaviours | Scope | Retention / TTL | Deletion | Encryption / residency | Pricing units (→ #39) | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OpenAI Responses and Conversations state | API (no version) | in-session state; durable conversation objects | API key or project (D48) | Responses stored 30 days by default; `store=false` disables storage; "Conversation objects and items in them are not subject to the 30 day TTL" (D14) | `DELETE` conversation, but "Items in the conversation will not be deleted" (D15) | not covered in the fetched pages | prior turns billed as input tokens (D14) | D14, D15 |
| Anthropic memory tool | tool type `memory_20250818`; "all Claude 4 and later models" | file-based long-term memory | application-defined `/memories` directory | application-defined; the docs advise deleting files not accessed for a long time | `delete` command | application-defined | tokens only (no storage billed by the provider) | D31 |
| Amazon Bedrock AgentCore Memory | service; SDK `bedrock-agentcore` 1.24.1 | short-term events; long-term records via strategies (semantic, user preference, summary, episodic, custom or self-managed) | `actorId`, `sessionId`, namespace templates | events: expiry up to 365 days, fixed at write time. Records: no expiry by default; `recordExpiryDurationDays` ≥ 31 (D25, D26) | `DeleteMemoryRecord`, `BatchDeleteMemoryRecords`. Expired records can still be returned for "a few days" (D26) | service-managed key by default; customer-managed KMS optional (D25); setting a TTL needs IAM `bedrock-agentcore:UpdateMemoryRecordExpirySpecification` (D26) | short-term: per 1,000 events until 2026-10-05, then per GB ingested; storage per GB-month over the event TTL; retrieval per GB. Long-term: per 1,000 records per month; per 1,000 retrievals (D28) | D25–D30 |
| Google Agent Platform Memory Bank | service (Gemini Enterprise Agent Platform; formerly Vertex AI Agent Engine) | LLM extraction and consolidation of user facts and preferences; direct `CreateMemory` | `scope` dict (≤ 5 pairs; default `{"user_id": ...}`); "isolated collection" per scope (D21, D22) | Active-memory and revision TTL are separate; see [dated retention follow-up](#memory-bank-retention-source-follow-up-2026-10-18) (D59, D60) | `memories.delete`, `memories.purge` (filter plus `force`), semantic "forget" via `generate` (D22, D23); deleted-memory revisions have a recovery window (D60) | CMEK, VPC-SC, data residency at rest, HIPAA (D24). Global Memory Bank instances cannot use CMEK (D59). ML processing may use global endpoints for some models (D21). IAM Conditions per scope | not on the fetched pages; linked to Generative AI pricing (unknown) | D21–D24, D59, D60 |

### Plain storage patterns (reference #9; not re-catalogued)

| Pattern | Use | Facts used here | Evidence |
| --- | --- | --- | --- |
| Redis or Valkey with key TTL | session state, rate-limited scratch, short-retention caches | `EXPIRE` deletes a key after N seconds. Overwrite (`SET`) clears the TTL, but in-place changes (`HSET`, `LPUSH`) keep it. LangGraph Redis saver and store expose `default_ttl` in minutes | D54, D9 |
| PostgreSQL (or another RDBMS) | checkpoints, session history, profile-style user memory, optional pgvector | used by LangGraph PostgresSaver and PostgresStore, ADK DatabaseSessionService, Agents SDK SQLAlchemySession, Mem0 self-hosted server. Postgres has no native row TTL; expiry is an application sweeper (PostgresStore) or a scheduled job (D1) | D1, D7, D17, D34 |
| Object or file storage | transcripts, memory files, archives | Anthropic memory tool files; Letta MemFS (git); DynamoDB with S3 offloading (D29) | D29, D31, D45 |

The product facts for these stores (regions, encryption, capacity, price) belong to the `storage` catalog in #9.

## Comparison fields

The coordinator's required research fields, mapped to v1. "Note only" means v1 has no field; a proposed field for #40 is given where useful.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| memory system id → `/id` | string, `memory_store.<vendor>.<product>` | 6 proposals (see Structured artifacts) | — | One version per ID under the current intake rules |
| evidence / version → `/version`, `/provenance` | string; exact package version | e.g. `google-adk` 2.12.0 | D7, D13, D20, D38 | Managed services have no version; see Open questions |
| memory type → `/spec/memory_type` | enum `working, session, long_term` | see taxonomy | D5, D18 | Single value; multi-behaviour products lose information |
| storage mechanism → `/spec/backing_type` | enum `in_memory, relational, vector, object, file` | see tables | per row | No `graph`, `managed_undisclosed` or `client_defined` values |
| encryption → `/spec/encryption_at_rest`; key → `/settings/encryption_key_ref` (`secret://...`) | boolean; opaque reference | AgentCore: always encrypted, CMK optional; Memory Bank: CMEK; LangGraph: optional AES serializer | D2, D24, D25 | Assert only when documented as default. Optional app-level encryption is not "at rest" by default |
| retention support → `/spec/supports_ttl`; retention period → `/settings/ttl_hours` | boolean; integer hours ≥ 1 | PostgresStore true; AgentCore records minimum 31 days | D7, D26 | Provider units are minutes (LangGraph), seconds (Redis), days (AgentCore) and dates (Mem0). Normalize to hours with a stated rounding rule |
| capacity limits → `/settings/max_entries` | integer entries ≥ 1 | Letta guidance: < 20 blocks of < 50k characters each (D46); Memory Bank scope ≤ 5 keys (D22) | D22, D46 | No catalog field for vendor maximums. Note only |
| scope | proposed enum `session, user, agent, app, org, tenant` (array) | see taxonomy | D18, D22, D25, D37 | **Note only.** Proposed `spec_memory_store.scopes` |
| persistence (survives restart) | boolean; unknown when the required evidence is absent | Documented volatile implementations: false; other selected configurations require evidence | D17, D3; [Example 6](#example-6-persistent-memory-requires-configuration-evidence) | Not derivable from `backing_type`. Bind the value to the selected implementation/version, persistence configuration, retained storage and relevant restart/recovery scope. Note only; a structural warning or non-memory `pass` is not durability evidence |
| read/write behaviour | proposed enum `full_inject, search, tool_call, preload` plus write `hot_path, background, explicit` | ADK `load_memory` and `preload_memory` (D19); LangChain hot path vs background (D5) | D5, D19 | **Note only** |
| context requirements | tokens injected per turn (integer, tokens) | Anthropic `view` truncates at 16,000 characters (D31) | D31 | **Note only.** Proposed `settings_memory_store.max_injected_tokens` |
| retention default | enum `none, fixed, configurable` plus duration | OpenAI responses 30 days; conversations no TTL; AgentCore records none | D14, D26 | **Note only** |
| consent requirement | proposed enum `none, implicit_notice, explicit_opt_in` | the application must establish its consent policy; product enforcement is not established by this legal source | D55 (legal-policy input, not product capability evidence) | **Note only.** #35 owns the policy; evaluate any claimed product control against the actual workflow |
| deletion support | proposed enum array `item, scope_bulk, filter_purge, full_subject, async` | OpenAI conversation delete keeps items; Mem0 OSS retains SQLite history text; Zep is async with residual summaries | D15, D22, D23, D41, D57, D58 | **Note only.** Proposed `spec_memory_store.deletion_modes`; API names alone do not establish deletion depth |
| export support | boolean | Mem0 Platform yes; Mem0 OSS no | D35 | **Note only** |
| access control | proposed enum `none, app_enforced, iam_scoped` | Memory Bank IAM Conditions; Agents SDK `session_id` is not authentication | D12, D21 | **Note only** |
| tenant isolation | proposed enum `none, logical_key, project, account` | Mem0 OSS none; Zep account and project; Memory Bank per scope | D21, D35, D42 | **Note only** |
| data locality | region string | Memory Bank `eu` or `us` at rest, processing may be global | D21 | No `region` on `spec_memory_store`. Inherit from #9 `storage.region` or #15 when a reference exists |
| retrieval options | proposed enum `key, filter, keyword, vector, hybrid, graph` | ADK InMemory keyword; RAG memory vector; Graphiti graph | D19, D39 | **Note only** |
| storage costs | units only | AgentCore units in the table above | D28 | Prices go to #39 |
| framework integrations | list of `agent_framework` IDs | Mem0 ↔ LangGraph, CrewAI, MS Agent Framework (Python), Semantic Kernel; AgentCore ↔ LangGraph | D29, D32, D50, D52 | **Note only.** Proposed `spec_memory_store.framework_refs` |
| hosting requirements | `library, self_hosted_service, managed` | see Deployment modes | — | **Note only**; related to #3 deployment mode |
| storage backend reference | proposed `storage_ref` → `storage` (#9), `vector_database_ref` → `vector_database` (#15) | — | — | **Missing in v1** (see Compatibility proposals) |

## When vector search is warranted

A vector database is **not** required for persistent memory. Every framework-native persistence path source-checked here works on relational or key-value storage:
- LangGraph stores work by namespace and key; "semantic search" is enabled only if an embedding model is configured (D3).
- ADK DatabaseSessionService is relational (D17).
- AgentCore and Memory Bank do not expose a vector index to the user (D25, D21).

| Need | Recommended backing | Why |
| --- | --- | --- |
| Resume a conversation or graph run | session or checkpoint store (`relational`, or Redis `in_memory` with TTL) | Exact lookup by `thread_id` or `session_id`; no similarity needed (D2, D12) |
| Small, structured user profile (preferences, settings) | relational or key-value document (profile) | LangChain's "profile" pattern; always loaded in full (D5) |
| A few facts that always matter | in-context memory blocks or profile | Letta recommends putting small data in context directly (D46) |
| Large, growing collection of free-text memories; recall by meaning | `vector` (or a store with an optional index) | Collection pattern; "updating and searching the list is harder" without search (D5). ADK RAG memory uses vector similarity (D19) |
| Facts that change over time; "what was true when" | graph or temporal store (Graphiti, Zep) | Validity windows and invalidation (D39). v1 has no `graph` value |
| Raw transcript archive for audit | object or file | No query needs; retention and deletion matter most |
| Keyword recall is enough | keyword (ADK InMemoryMemoryService) | D19 |

Rule of thumb for the builder (Estimate, project guidance):
- Recommend `vector` only when the expected per-scope memory count is too large to inject in full within the context budget, **and** recall must be by meaning, not by key.
- If a vector index is used, reuse the build's #15 `vector_database` (COMPONENTS.md) and do not create a second, independent one.
- Keyword-only and key-value memory need no embedding model. This mirrors the existing contract statement that keyword-only RAG needs no vector database.

## Memory Bank retention source follow-up (2026-10-18)

Google's setup and revision guides were read as rendered documentation (D59/D60, both updated 2026-10-15). These are published service behaviors, source checked / unverified; no instance, SDK or deletion operation was exercised.

- **Active memories (D59):** without automatic TTL configuration or an explicit expiration, memories do not expire. A default TTL covers create/update/generate operations; covered updates replace expiration with now plus TTL. Granular TTL distinguishes direct creation, generated creation and generated updates; an omitted operation setting leaves expiration unchanged. The guide says expired memories become unavailable for retrieval and are deleted; it supplies no measured physical-purge deadline.
- **Revisions (D60):** enabled by default, with a default TTL of 365 days and instance/request overrides. Deletion creates an empty deletion revision while earlier facts remain in child revisions; those revisions can be inspected and rolled back for up to 48 hours after the parent is deleted. Revision expiration prevents inspection and rollback. Disabling creation of new revisions is not evidence that existing history was purged.
- **Configuration boundary:** D59's setup example uses `memory_revision_default_ttl`, while D60's instance example uses `revision_ttl`. Retain that documentation discrepancy until the selected SDK/API is pinned and checked; this note supplies no executable configuration. D59 also excludes CMEK for a `global` Memory Bank instance. Storage region, processing endpoint and encryption selection need their own configuration evidence.

For #35/#38, check active memory, recoverable revisions and any other retained layers separately before reporting erasure. The two published durations are service-specific conditions, not a project retention default or a legal conclusion. Backup deletion and deployed purge behavior remain unknown; #39's pricing-unit/rate follow-up is unchanged.

## Graphiti partition source follow-up (2026-10-18)

The public `v0.31.1` tag resolved to commit `5961293865a57844fe13d4eb061deb3501971fb2`; its project metadata declares `graphiti-core` 0.31.1 (D65). This read-only inspection resolves the uninspected scope-key question in D39. The [primary source manifest](../../evidence/t4-graphiti-0311-source.json) binds the 90,672-byte `graphiti.py` file to its SHA-256 and Git blob. The observations below are source checked / unverified; no SDK, database, concurrent workload or hosted service was exercised.

**Interface and validation (D61).** `add_episode` and `add_episode_bulk` accept a `group_id`; `search`, `search_` and `retrieve_episodes` accept `group_ids`. The format helper applies `^[a-zA-Z0-9_-]+$` to nonempty input and permits the empty/default case. It does not bind a group to an authenticated caller. The default helper returns `_` for FalkorDB and an empty string for the other listed providers. Episode writes resolve a local driver/client bundle: an explicit group different from the configured database calls `clone` and copies the client bundle; default or matching cases reuse the shared instances without reassigning their driver.

| Inspected path | Source behavior | Consequence for the memory decision |
| --- | --- | --- |
| Shared search normalization (D62) | `None`, `[]` and `['']` become `None`; a nonempty list of nonempty group IDs is retained. | At this stage, an empty selection supplies no restriction through the `group_ids` argument; the selected graph/database and other query filters retain their own scope. The application must distinguish an authorized group set from its own no-access outcome before calling this interface. |
| Neo4j node and edge search operations (D63) | The inspected full-text and cosine paths add a `group_id IN $group_ids` predicate only when the argument is not `None`. `Neo4jDriver` inherits the base `clone`, which returns the existing driver. | These paths use group properties within the configured database; passing `group_id` does not automatically create a separate Neo4j database or credential. Other query predicates and database permissions retain their own scope. |
| FalkorDB routing (D64) | The decorator routes a single selected group through a matching graph driver; multiple groups run per graph and merge their results. `FalkorDriver.clone` reuses the client connection. | Graph selection is provider-specific. The same parameter shape does not prove independent connections, credentials or access policy across providers. |

**Handoff implication for #13/#15/#35:** record the selected Graphiti revision, backend/driver/database, the application's caller-to-allowed-group decision and the exact write/read paths. A syntactically valid or nonempty group ID is insufficient evidence of tenant authorization. Keep selected database privileges, UUID lookup paths, custom drivers, deletion coverage and concurrency/isolation behavior as separate checks before asserting an access boundary. This supplement establishes the inspected partition interface, with the T3 storage and T6 policy handoffs still carrying their original scope; it supplies no receiving-owner acceptance or frozen-v1 field.

## Privacy, consent, retention and deletion

**Not legal advice.** The legal sources below are cited so that #35 and the product owner can decide policy. The text is from the EUR-Lex consolidated version of Regulation (EU) 2016/679, version of 2016-05-04 (D55). EUR-Lex states that consolidated texts have no legal effect; the Official Journal text is authentic.

### Legal anchors

- **Storage limitation, Art. 5(1)(e):** personal data must be "kept in a form which permits identification of data subjects for no longer than is necessary". There is an exception for archiving, research and statistics with safeguards.
  - Implication: durable user memory needs a defined retention period per memory kind. "Keep forever by default" (AgentCore records, OpenAI conversations, Zep, D14, D26, D40) must be a deliberate setting, not an accident.
- **Right to erasure, Art. 17(1):** the data subject has "the right to obtain from the controller the erasure of personal data concerning him or her", and the controller must erase "without undue delay" on six grounds, including withdrawn consent (b) and data no longer necessary (a).
  - Art. 17(3) lists exceptions, such as legal obligations and legal claims.
  - Implication: the builder must know whether a memory store can delete **all** data of one subject across scopes and derived artifacts.
- **Consent withdrawal, Art. 7(3):** "It shall be as easy to withdraw as to give consent."
- **Data portability, Art. 20:** structured, machine-readable export of data provided by the subject, where processing is based on consent or contract. This bears on export support.

### Findings that affect the rules

| Risk | Source-checked (unverified) finding | Builder implication | Route |
| --- | --- | --- | --- |
| Deletion that is not erasure | OpenAI: deleting a conversation does not delete its items (D15). Mem0: expiration hides, does not delete (D36); OSS `delete` and `delete_all` retain prior text in SQLite history (D57, D58). AgentCore: expired records can be returned for days; use `DeleteMemoryRecord` for immediate removal (D26). Zep: residual text in shared node summaries; backups up to 365 days (D40, D41) | `supports_ttl=true` must not be read as "erasure guaranteed". Show deletion depth per product; require an explicit history-retention and purge policy | #35, #38, #40 |
| Cross-session persistence without notice | ADK `user:` state persists across all of a user's sessions once a persistent SessionService is used (D18) | Persistent user memory should be visible to the user, with a consent notice and a forget control. This is a proposed application requirement; the cited persistence behavior does not establish whether any product enforces notice, consent or a forget control | #35 |
| User and tenant boundaries | Agents SDK: `session_id` "does not authenticate a user or authorize access" (D12). MS Agent Framework: "bind each stored session to the authenticated user or tenant before allowing it to resume" (D48). Mem0 OSS has no org or project concept (D35). Memory Bank isolates per scope and supports IAM Conditions (D21) | Multi-tenant builds need app-enforced or IAM-scoped isolation; v1 cannot check it | #35, #40 |
| Sensitive data | Anthropic: Claude "usually refuses" to write sensitive data; add validation for stronger guarantees (D31). OWASP: audit memory for sensitive data before persistence; encrypt or redact (D56) | Pair long-term memory for confidential or restricted builds with encryption and redaction (rule `rule.t4.memory.sensitive.encryption`) | #35 |
| Memory poisoning via prompt injection | Memory Bank: "Memory poisoning occurs when false information is stored", mitigated with Model Armor, red teaming and sandboxing (D21). OWASP: validate and sanitize before storage, isolate, expire, integrity checks (D56). Anthropic: path traversal in `/memories` must be validated (D31) | A guardrail must cover memory **writes**, not only tool calls. Hot-path writes (agent decides) carry more risk than background extraction from vetted sources | #35 |
| State corruption and recovery | Agents SDK SQLite backend does not detect external edits, deletions, reordering or replay; `EncryptedSession` does not verify completeness or order (D12). LangGraph checkpoints support time travel and fault tolerance (D1) | Integrity and backup belong to #9 storage and #38 monitoring; record per product | #9, #38 |
| Staleness and revision | Graphiti invalidates changed facts (D39); Memory Bank consolidates and keeps revisions (D21, D24); Mem0 OSS algorithm is "ADD-only" (D32) | Prefer stores with consolidation or revision when facts change; show "last updated" | #36 (evaluation of memory quality) |

## Context-window and performance implications

- Memory that is injected into the prompt consumes context tokens on every turn:
  - ADK `preload_memory` retrieves at the start of every turn (D19).
  - Letta memory blocks are always in context (D46).
  - MS Agent Framework context providers append messages and instructions on every run (D49).
  - Chained OpenAI responses bill all previous input tokens again (D14).
- In v1 these tokens must fit inside `settings_context_policy.requested_context_tokens`. `rule.model.context.fit` compares `context.total_requested_tokens` (requested plus reserved output) with `model.spec.context_window_tokens`.
  - v1 has **no** metric or field for the share of that budget that memory takes. A build can pass `rule.model.context.fit` and still overflow in practice once memory and history grow.
  - Proposed: `settings_memory_store.max_injected_tokens` and metric `memory.max_injected_tokens`. Handed to #7 and #40.
- Summarization tradeoffs:
  - Compaction keeps the active context small, but it "clears and rewrites the session history" (D12) and loses detail. Anthropic recommends pairing compaction with a memory store for "information that must survive summarization" (D31).
  - `context_policy.truncation_strategy` (`summarize`, `sliding_window`, `truncate_oldest`) is the v1 knob. A builder choosing `summarize` should know that the summarizer's own model calls add cost and latency. Unquantified here (#39, #7).
- Write path latency: hot-path memory writes add latency to the user turn; background writes do not (D5). Unquantified; handed to #38 and #36 for measurement.

## Compatibility proposals

These rules are proposed for review by #40. They were checked locally:
- The four JSON rules validate against the `rules` item of `contracts/v1/schemas/ruleset.schema.json`.
- They were run with `contracts/v1/reference/evaluate.py` on clearly synthetic builds, together with the baseline ruleset. The scratch harness is not committed.

Severity is separate from outcome. A missing optional catalog fact gives `unknown` with `on_unknown: review`, never `pass`.

### Example 5: memory backend needs storage or permissions that the configuration lacks

**`rule.t4.memory.storage.backing`** is the relational, object or file analogue of the baseline `rule.memory.vector.storage`.

- **Status:** Hypothesis. The pairing is supported by D2, D3, D17 and COMPONENTS.md. Matching on the primary role is a simplification.
- **Participating kinds and pointers:**
  - memory_store catalog `/spec/backing_type`
  - storage selection `/id`
  - storage catalog `/spec/storage_type`
- **Applicability:** a primary memory_store whose `backing_type` is `relational`, `object` or `file`.
- **Assertion:** a primary `storage` selection exists, and its `storage_type` equals the memory `backing_type`. The enums share the values `relational`, `object`, `file` and `in_memory`.
- **Severity:** `warning`, not error. Three cases legitimately pass without a separate storage selection:
  - a managed service whose storage is bundled (AgentCore, Memory Bank);
  - an embedded SQLite file (ADK, Agents SDK);
  - a primary storage selection that serves a different purpose.
- **Missing data:** `on_unknown: review`.
- **Remediation:** select matching storage (#9), or confirm in review that storage is bundled.
- **Dependency edges:** `dep.memory_store.storage` already exists (`informs`, `if_selected`). This rule makes the relationship checkable.
- **Synthetic results (local run):**
  - long-term relational memory with no storage → `fail`;
  - with relational storage → `pass`;
  - with only object storage → `fail`;
  - no memory_store → `skipped`.
- **Version impact:** none; additive.

```json
{"id":"rule.t4.memory.storage.backing","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"memory_store","role":"primary","pointer":"/id"}}},{"op":"in","left":{"ref":{"scope":"catalog","kind":"memory_store","role":"primary","pointer":"/spec/backing_type"}},"right":{"literal":["relational","object","file"]}}]},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"storage","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"storage","role":"primary","pointer":"/spec/storage_type"}},"right":{"ref":{"scope":"catalog","kind":"memory_store","role":"primary","pointer":"/spec/backing_type"}}}]},"on_unknown":"review","message":"The memory store persists to relational, object or file storage, but no primary storage selection of that type is configured.","remediation":"Select a storage offering whose storage_type matches the memory backing type, or choose a memory store whose storage is bundled or managed and confirm it in review.","affected_kinds":["memory_store","storage"],"owner":"t4-research"}
```

**Needs contract change via #40: precise version.** The rule above checks "some primary storage", not "the storage this memory uses".

- The precise version needs `spec_memory_store.storage_ref` (or a `managed_storage: true` flag), or rule-language access to `BuildSnapshot.links` with relation `stored_in`.
- The same gap affects the baseline `rule.memory.vector.storage`: it is satisfied by any primary vector database, even one dedicated to RAG with a different `index_dimension`.

```text
rule.t4.memory.storage.linked (needs contract change via #40)
applies_when: exists(selection memory_store primary /id) AND catalog memory_store /spec/backing_type in [relational, object, file]
              AND NOT (catalog memory_store /spec/managed_storage == true)            # MISSING FIELD managed_storage
assert:       exists(link from=sel(memory_store) relation=stored_in to=sel(kind=storage))  # MISSING: link operand in rule DSL
              AND catalog(storage via link) /spec/storage_type == catalog memory_store /spec/backing_type
```

**Permissions part.** v1 has no permission or IAM fields. A source-checked example: setting a TTL on AgentCore long-term records requires `bedrock-agentcore:UpdateMemoryRecordExpirySpecification`, or the request fails with `AccessDeniedException` (D26).

- **Status:** Source-checked (unverified) fact, Hypothesis rule; needs contract change via #40.
- **Severity:** warning.

```text
rule.t4.memory.permissions (needs contract change via #40)
applies_when: exists(selection memory_store primary /settings/ttl_hours)
assert:       subset_of(catalog memory_store /spec/required_permissions_for_ttl,      # MISSING FIELD
                        selection memory_store /settings/granted_permissions)           # MISSING FIELD
```

### Example 6: persistent memory requires configuration evidence

**Where the requirement lives in v1:** nowhere. Neither of these fields says "this agent must remember across sessions":
- `workload.spec.workload_type = agentic`;
- `build.objectives`, which has region, currency, budget, traffic, data_classification and latency only.

The requirement can therefore only be checked after a contract change. Two v1-expressible proxies are proposed alongside it.

**`rule.t4.memory.persistence.required`**
- **Status:** Hypothesis; **needs contract change via #40**.
- **Severity:** error when the user states the requirement.
- **Missing fields:** `build.objectives.memory_persistence` (enum `none | within_session | cross_session`), or a workload-level `settings_workload.memory_persistence`.
- **Passing example:** `cross_session` with a selected long-term store and configuration whose relevant restart/recovery behaviour is evidenced.
- **Failing example:** `cross_session` with only the documented non-persistent ADK InMemorySessionService.
- **Unknown example:** the selected store's persistence configuration or restart/recovery evidence is unavailable. A relational or in-memory backing label alone does not answer the requirement.

```text
rule.t4.memory.persistence.required (needs contract change via #40)
applies_when: build /objectives/memory_persistence == "cross_session"                   # MISSING FIELD
assert:       exists(selection memory_store primary /id)
              AND catalog memory_store /spec/memory_type == "long_term"
              AND evidenced_restart_persistence(selected implementation, configuration, required scope)
                  # MISSING: configuration/evidence operands and their semantics; not an executable v1 predicate
```

**`rule.t4.memory.longterm.volatile`** retains its proposal ID as a v1 structural review proxy. It identifies a long-term memory item labeled `in_memory`; it does not establish that the selected implementation loses data on restart.

- **Status:** Hypothesis review proxy using v1 fields. The source-checked (unverified) ADK (D17), LangGraph `InMemoryStore` (D3) and LangMem (D10) examples describe particular volatile implementations; that observation cannot be generalized to every backend with the same broad label.
- **Severity:** warning requiring configuration review. The pinned [Redis 8.10.2 configuration](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/redis.conf) documents disk snapshot and append-only persistence controls; snapshotting can be disabled, and AOF is separately configured. The [#9 software identity record](../T2-infrastructure/hosting.md#relational-and-in-memory-software-identities-2026-10-18) does not select or verify a deployed configuration. Source inspected 2026-10-18: Git blob `1d1c6284dd173ad9c5577fce211c0db2fa0ed8da`, SHA-256 `5ae0cda89cc3ab7a399280f92ee840a476a8a230249a1b8a138e589ecf522345`; no Redis deployment or recovery experiment was performed for this clarification.
- **Synthetic results:** `long_term` + `in_memory` → `fail` with a review warning, not a diagnosis of lost data; `long_term` + `relational` → `pass` for this backing-label predicate only, not a durability certificate; `session` + `in_memory` → `skipped`. An unresolved backing reference remains `unknown` with `on_unknown: review`.
- **Acceptance boundary:** establish the exact implementation/version, enabled persistence mode, retained layers, storage survival and applicable restart/recovery observations before deciding a cross-session requirement. Relabeling the item, configuring a TTL, selecting a non-memory backing or showing a warning-free v1 result is not that evidence. No new v1 field, durability outcome or production ruleset is introduced here.

```json
{"id":"rule.t4.memory.longterm.volatile","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"memory_store","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"memory_store","role":"primary","pointer":"/spec/memory_type"}},"right":{"literal":"long_term"}}]},"assert":{"op":"ne","left":{"ref":{"scope":"catalog","kind":"memory_store","role":"primary","pointer":"/spec/backing_type"}},"right":{"literal":"in_memory"}},"on_unknown":"review","message":"Confirm restart persistence for this long-term memory configuration. The in-memory backing label alone cannot determine whether data is retained.","remediation":"Review the selected implementation, persistence mode, retained layers and restart/recovery evidence. Choose an appropriately configured persistent store when cross-session retention is required; changing the backing label alone does not establish durability.","affected_kinds":["memory_store"],"owner":"t4-research"}
```

**`rule.t4.memory.ttl.support`** catches a retention period that the store cannot enforce.

- **Status:** Schema-checked as a contract-semantics proposal, using v1 fields only; product claims remain source-checked and unverified. Products differ: PostgresStore supports TTL (D7), the OSS PostgresSaver has no TTL code (D7), and Mem0 expiry hides records (D36).
- **Severity:** warning.
- **Synthetic result:** `ttl_hours` set on an item with `supports_ttl` absent → `unknown` (review), which is the intended behaviour.

```json
{"id":"rule.t4.memory.ttl.support","severity":"warning","applies_when":{"op":"exists","value":{"ref":{"scope":"selection","kind":"memory_store","role":"primary","pointer":"/settings/ttl_hours"}}},"assert":{"op":"eq","left":{"ref":{"scope":"catalog","kind":"memory_store","role":"primary","pointer":"/spec/supports_ttl"}},"right":{"literal":true}},"on_unknown":"review","message":"A memory retention period (ttl_hours) is configured, but the memory store is not documented to support automatic expiry.","remediation":"Choose a memory store with documented TTL support, or implement and evidence a scheduled deletion job before relying on ttl_hours.","affected_kinds":["memory_store"],"owner":"t4-research"}
```

**`rule.t4.memory.sensitive.encryption`** checks documented default encryption for sensitive long-term memory; configuration controls are routed to #35 and #40.

- **Status:** Hypothesis (policy choice). The control itself is backed by D56.
- **Severity:** warning.
- **Scope:** This is a conservative catalog-capability check, not proof of encryption in a running deployment. A `pass` requires `encryption_at_rest=true`, recorded only for documented default encryption as specified in the field mapping above. An opaque key reference never changes the outcome. Optional application encryption requires a separately evidenced configuration review; missing capability evidence remains `unknown` with `on_unknown: review`.
- **Synthetic results** (restricted build, long-term memory): missing `encryption_at_rest`, with or without a key → `unknown` (review); explicit `false`, with or without an unused key → `fail`; documented `true` → `pass`; internal classification, session memory or no memory selection → `skipped`. Regression coverage: `tests/test_memory_rule.py`.

```json
{"id":"rule.t4.memory.sensitive.encryption","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"memory_store","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"memory_store","role":"primary","pointer":"/spec/memory_type"}},"right":{"literal":"long_term"}},{"op":"in","left":{"ref":{"scope":"build","pointer":"/objectives/data_classification"}},"right":{"literal":["confidential","restricted"]}}]},"assert":{"op":"eq","left":{"ref":{"scope":"catalog","kind":"memory_store","role":"primary","pointer":"/spec/encryption_at_rest"}},"right":{"literal":true}},"on_unknown":"review","message":"Long-term memory for confidential or restricted data lacks documented default encryption at rest or has unknown encryption capability.","remediation":"Use a store with documented default encryption at rest, or obtain a separate configuration review with #35/#40 for optional encryption; a key reference alone is insufficient.","affected_kinds":["memory_store","workload"],"owner":"t4-research"}
```

**`rule.t4.memory.user.erasure`** handles erasure for user-scoped memory.

- **Status:** Hypothesis; needs contract change via #40.
- **Severity:** warning.

```text
rule.t4.memory.user.erasure (needs contract change via #40)
applies_when: catalog memory_store /spec/scopes contains "user"                           # MISSING FIELD scopes
              AND build /objectives/data_classification != "public"
assert:       catalog memory_store /spec/deletion_modes contains "full_subject"           # MISSING FIELD deletion_modes
```

**`rule.t4.memory.context.budget`** handles memory tokens inside the context budget (#7).

- **Status:** Hypothesis; needs contract change via #40.
- **Severity:** error when the budget is exceeded.

```text
rule.t4.memory.context.budget (needs contract change via #40)
applies_when: exists(selection memory_store primary /settings/max_injected_tokens)         # MISSING FIELD
assert:       metric memory.max_injected_tokens                                              # MISSING METRIC
              <= selection context_policy primary /settings/requested_context_tokens
```

### Example 10: a build with agents but no RAG or vector database

This build must be valid, and the baseline already allows it. No new rule is proposed.

The local run used a synthetic agentic build with workload, deployment mode, model, context policy and agent framework, and no `rag_pipeline`, `knowledge_base`, `embedding_model`, `vector_database` or `memory_store`. Every RAG, vector, memory and agent rule was `skipped`:
- `rule.rag.knowledge`
- `rule.rag.dense.dependencies`
- `rule.embedding.dimension`
- `rule.vector.dimension.support`
- `rule.vector.distance.support`
- `rule.embedding.distance.support`
- `rule.memory.vector.storage`
- `rule.memory.framework.compatibility`
- `rule.agent.tools.framework`
- `rule.agent.mcp.framework`
- the four `rule.t4.*` rules above

Why each one skips:
- Each `applies_when` starts with `exists` on a selection that is absent. The reference evaluator returns false for `exists` on an unresolved reference, and `all(false, …)` is false, so the outcome is `skipped`.
- `rule.required.foundation` does not require any T3 kind.
- The dependency edge `dep.agent_framework.rag_pipeline` is `informs` / `if_selected` and does not create a requirement.

Two related cases:
- Adding an ADK-style `session` + `in_memory` memory store keeps all memory rules skipped, except `rule.memory.framework.compatibility`, which passes when `supports_memory` is true.
- Adding a `vector`-backed memory store without a vector database correctly fails the baseline `rule.memory.vector.storage`.

An info rule ("no retrieval configured") was considered and rejected. It would fire on most valid agent builds and add noise.

### Critique of the baseline `rule.memory.framework.compatibility`

The rule applies when a memory store is selected. It asserts that an agent framework is selected **and** that `agent_framework.spec.supports_memory == true`, with severity `error` and `on_unknown: block`.

Problems:

1. **The boolean has no defined meaning.** It could mean any of three things:
   - built-in session history (every framework here has it: D2, D12, D17, D48);
   - a long-term store abstraction (LangGraph Store, ADK MemoryService);
   - pluggable external memory (MS Agent Framework context providers; SK `Mem0Provider` is experimental, D52).

   Almost every framework would be `true` under the first reading. Under the third, compatibility is per **pair** (Mem0 ↔ MS Agent Framework is Python-only, D50), which a framework-level boolean cannot express.
2. **Error plus block on a missing optional field.** Because `supports_memory` is optional in `spec_agent_framework`, a framework item that omits it blocks every build with memory.
3. **Memory without an agent framework is legitimate.** A plain chat build using OpenAI Conversations for history (D14), or Memory Bank called directly, has memory but no agent framework. The rule fails it.
4. **Any memory can be reached through tools.** Every framework that supports tool execution can call a memory API as a tool (Memory Bank: "Other frameworks can wrap Memory Bank calls in tools and callbacks", D21). Failing the build is too strong when an integration is possible but not native.

Proposed refinement (needs contract change via #40):
- Downgrade to `warning`, with `on_unknown: review`.
- Replace the boolean with a pairwise field: either `spec_memory_store.framework_refs` (array of `agent_framework` IDs with native integration) or `spec_agent_framework.memory_integrations`.
- Assert native integration, and fall back to "reachable via tool" when `supports_tool_execution` is true.

```text
rule.memory.framework.compatibility (refinement; needs contract change via #40)
applies_when: exists(selection memory_store primary /id) AND exists(selection agent_framework primary /id)
assert:       catalog memory_store /spec/framework_refs contains selection agent_framework primary /catalog_item_id   # MISSING FIELD
              OR catalog agent_framework /spec/supports_tool_execution == true
severity: warning (was error) · on_unknown: review (was block)
```

The baseline `rule.memory.vector.storage` is sound in direction: vector memory needs a vector database. It has the same "any primary vector DB" gap described under Example 5. A follow-up could also assert that the memory's embedding dimension matches the vector index used for memory (`role: memory`, per COMPONENTS.md). That needs a memory→embedding reference, which is also missing.

## Pricing and capacity

No Pricebook proposal. Units only, for #39:
- **AgentCore Memory (D28):**
  - Short-term: per 1,000 new events through 2026-10-05, then per GB ingested from 2026-10-06; storage per GB-month prorated over the event TTL; retrieval per GB.
  - Long-term: storage per 1,000 records per month (built-in and override/self-managed listed separately); retrieval per 1,000 retrievals.
- **Memory Bank:** units not on the fetched pages, which link to Generative AI pricing. Unknown.
- **OpenAI conversation state:** no separate storage fee was found on the fetched pages. Previous turns are billed again as input tokens (D14).
- **Mem0 Platform, Zep Cloud, Letta Cloud:** pricing not fetched. Unknown.
- **Self-hosted (LangGraph, ADK, Agents SDK, Mem0 OSS):** the library is free. Cost is the #9 storage, plus LLM and embedding calls for extraction (Mem0 defaults to OpenAI LLM and embeddings, D34). Extraction model calls per memory write should be modelled by #39.

Capacity facts with stated conditions:
- Memory Bank scope: at most 5 key-value pairs (D22).
- AgentCore: event expiry up to 365 days; record TTL at least 31 days (D25, D26).
- Mem0 Platform: `batch_delete` up to 1000 per call (D35).
- Anthropic memory tool: `view` truncates text views longer than 16,000 characters (D31).
- Letta: recommended limits are guidance, not hard limits (D46).

## Recommendation and rationale

1. **Default to no durable memory.** Turn on in-session persistence only when sessions must survive restarts or scale across workers. Turn on cross-session memory only when the user asks for it. Each step adds retention, consent and deletion duties (Art. 5(1)(e), Art. 17; D55).
2. **Session state:** use the framework's own session or checkpoint store on relational storage from #9:
   - LangGraph PostgresSaver;
   - ADK DatabaseSessionService;
   - Agents SDK SQLAlchemySession;
   - Redis with TTL when short retention is the goal.

   Show retention explicitly. Most OSS savers have no TTL, so a deletion job is needed (D1, D2).
3. **User memory:** start with a relational profile or namespaced store (LangGraph PostgresStore, which has TTL). Add vector search only for large free-text collections, reusing the #15 vector database. Use managed services (AgentCore, Memory Bank) when the user needs managed TTL, CMK and IAM-scoped isolation in AWS or Google Cloud.
4. **Flag status in the builder:**
   - Letta's self-hosted V1 server is archived (D44).
   - Zep Community Edition is deprecated (D42).
   - Semantic Kernel memory is experimental (D52).
   - Graph memory was removed from Mem0 OSS (D35).
5. **Never present "expiration" or "delete" as erasure without qualification.** See the deletion findings (D15, D26, D36, D40, D41, D57, D58), including Mem0 OSS SQLite history retention after vector deletion.

## Structured artifacts

Catalog proposals (all `kind: memory_store`, `tier: T4`, validated):

| File | ID | memory_type / backing_type | Optional spec fields |
| --- | --- | --- | --- |
| `catalog/proposals/t4d-langgraph-postgres-saver.json` | `memory_store.langgraph.postgres-saver` | session / relational | — |
| `catalog/proposals/t4d-langgraph-postgres-store.json` | `memory_store.langgraph.postgres-store` | long_term / relational | `supports_ttl: true` (sweeper must be started) |
| `catalog/proposals/t4d-openai-agents-sqlalchemy-session.json` | `memory_store.openai-agents.sqlalchemy-session` | session / relational | — |
| `catalog/proposals/t4d-adk-database-session-service.json` | `memory_store.google-adk.database-session-service` | session / relational | — |
| `catalog/proposals/t4d-adk-in-memory-session-service.json` | `memory_store.google-adk.in-memory-session-service` | session / in_memory | — |
| `catalog/proposals/t4d-mem0-oss.json` | `memory_store.mem0.oss` | long_term / vector | — (expiration hides, so `supports_ttl` is not asserted) |

**Multi-backend products:**
- Each item is one product mode with one backing type. Products whose backend is user-selectable (Mem0 with 22 vector stores; Agents SDK sessions with seven backends) are represented by one item per backing type, and only where the mode is documented.
- The other Agents SDK backends (Redis, SQLite, MongoDB, Dapr) and the LangGraph Redis saver are kept in the note. Their `backing_type` is ambiguous in v1: Redis is `in_memory` with optional persistence, and MongoDB is a document store with no enum value.

**Not proposed:**
- AgentCore Memory, Memory Bank, Zep Cloud, Mem0 Platform and Letta Cloud: required `backing_type` is undisclosed, and managed services have no release version.
- Graphiti: graph backing has no enum value.
- Anthropic memory tool: storage is application-defined.

## T3 storage and retrieval receiving review (2026-10-18)

T4/#28 accepts the bounded [#15 storage interface](../T3-knowledge-retrieval/vector-database.md) and [#16 retrieval interface](../T3-knowledge-retrieval/rag-retrieval.md) for the T4 component owner's consuming scope, with these constraints. The decision uses the project owner's delegated authority; @PUSHINGSQUARES's separate co-owner scope and the T3 owners' decisions remain distinct.

- Reference the actual selected store/index and memory role rather than introducing duplicate storage product records. The presence of any primary vector database is insufficient: its configured representation, dimensions, metric, normalization and authorized namespace must fit this memory use. Reusing a storage product does not establish shared permissions or compatible embedding spaces.
- Receive VDB-01's index/type-specific admission, VDB-02's resource-and-action authorization, and VDB-03's source-to-derived deletion lineage as proposed constraints. Software-level optional fields such as `supports_acl` and `regions` stay absent or unknown without eligible deployment/configuration evidence. No region, isolation guarantee, entitlement or operational price follows from the software catalog alone.
- Retrieval-backed memory inherits [RAG-02's trusted principal and mandatory scope](../T3-knowledge-retrieval/rules/retrieval-rules.md#rag-02-caller-authorization-precedes-model-and-tool-exposure) before model or tool exposure, including permission-bearing summaries and graph artifacts. Read permission does not grant write, delete or administrative permission. A successful query does not establish consent to persist its result.
- #28 retains memory purpose/scope, consent, retention and deletion semantics. Vector invisibility or a database acknowledgement does not establish removal from history, checkpoints, summaries, caches or backups. Preserve per-layer evidence and unknowns; the scoped Mem0 reproduction is not a complete-erasure guarantee.
- Apply the [framework receiving review's complete-input accounting](agent-framework.md#t3-retrieval-receiving-review-2026-10-18). Retrieval and memory labels must not charge the same assembled tokens twice; repeated text actually present in the input still consumes tokens each time. Keyword, exact-key and session-only memory do not acquire a vector-database requirement through this handoff.

This accepts T4's incoming interface only. T3's response to T4's outgoing role/ACL/region request, #40's versioned links and evidence operands, #35/#38 policy and purge coverage, and deployment/interoperability measurements remain separate. No new frozen-v1 field or production configuration is adopted.

## Open questions and handoffs

| Question | Follow-up issue / owner |
| --- | --- |
| Add to `spec_memory_store`: `scopes` (array), `deletion_modes`, `supports_export`, `default_retention`, `min_ttl_hours`, `max_ttl_hours`, `ttl_semantics` (`delete`, `hide`, `delayed_delete`), `storage_ref`, `vector_database_ref`, `framework_refs`, `managed_storage`, `region` or `regions`, `retrieval_modes`, `tenant_isolation`. Add `backing_type` values `graph`, `document`, `managed_undisclosed`, `client_defined`. Allow array `memory_types` | #40 · @tynamite |
| Add `build.objectives.memory_persistence` (or a workload setting) so the requirement in Example 6 is checkable | #40 with #2 · @tynamite |
| Add rule-DSL access to `BuildSnapshot.links` (`stored_in`) so memory→storage and memory→vector rules check the actual wired instance | #40 · @tynamite |
| Define versioned evidence for optional encryption support, enablement, key consumption by the selected store, and the covered storage/history layers. These are proposals, not v1 fields. Until approved, a key reference alone cannot satisfy the encryption rule, and missing capability evidence remains `unknown` (review); documented default capability still does not certify a deployed configuration | #40 · @tynamite; #35 · @PUSHINGSQUARES (**pending owner confirmation**) |
| Add metric `memory.max_injected_tokens` and setting `settings_memory_store.max_injected_tokens`; decide whether it is counted inside `requested_context_tokens` | #7 · @zwright8 and #40 |
| Redefine or replace `agent_framework.spec.supports_memory`; review the severity and on_unknown of `rule.memory.framework.compatibility` | #40 · @tynamite; #25 · @CompleteDotTech |
| **Storage handoff to T3 and T2, pending owner confirmation:** memory reuses `vector_database` (#15) for vector-backed memory with role `memory`, and `storage` (#9) for relational, object and file memory. #28 adds no storage product items. Confirm the role naming (`memory`) and that #15 items will carry `supports_acl` and `regions` facts usable for memory | #15, #13 · @zabyxc01; #9 · @Mattycodes69 (**pending owner confirmation**) |
| Controls for memory writes (poisoning, PII redaction before persistence, path validation for file memory), consent notice, forget control, erasure across derived artifacts | #35 · @PUSHINGSQUARES |
| Mem0 OSS v2.2.1 `delete`/`delete_all` retain prior text in SQLite history (D57, D58): decide retention/purge requirements for history, vectors, derived artifacts and backups; monitor purge completion across those layers. No complete-erasure guarantee or purge procedure is established here | #35, #38 · @PUSHINGSQUARES (**pending owner confirmation**) |
| Monitoring of memory size growth, TTL sweeper health and deletion-job success; audit logs of memory reads and writes | #38 · @PUSHINGSQUARES |
| Pricing units for AgentCore Memory, Memory Bank, Mem0 Platform, Zep and Letta Cloud; extraction LLM-call cost per memory write | #39 · @PUSHINGSQUARES |
| Evaluation of memory quality (recall, staleness, poisoning resistance) | #36 · @PUSHINGSQUARES |
| Version field for managed services (no release tag): docs snapshot date or API version? | #41 · @tynamite |
| Is ChatGPT-style consumer memory out of scope? Excluded here as consumer, not builder-selectable | #28 · @CompleteDotTech |
| Unverified facts to re-fetch: Memory Bank pricing units and selected SDK/API revision-TTL configuration (published retention semantics source-checked at D59/D60); Anthropic memory tool platform availability (Bedrock, Vertex); selected Graphiti backend and caller authorization/isolation (partition interface source-checked at D61–D64); Zep and Letta encryption and residency; MS Agent Framework TTL and deletion | #28 · @CompleteDotTech |

[Internal T4 interfaces are accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509); external receiving-owner decisions are partially received in the [workstream matrix](README.md#dependency-and-handoff-matrix). The [2026-10-18 T4 review](README.md#t6-receiving-dispositions-and-t4-memory-review-2026-10-18) records CompleteDotTech's delegated acceptance of MEM-SG01–MEM-SG06 as the constrained memory-observation interface. PUSHINGSQUARES' separate #28 confirmation remains unrecorded. It does not supply #35/#38 co-owner confirmation, T3 storage acceptance or deployed purge evidence.

## Evidence

Access dates are per entry (D1–D56: 2026-10-16; D57–D58: 2026-10-17; D59–D65: 2026-10-18). Grades follow `docs/RESEARCH_METHOD.md` and the adopted #41 interim policy above. "Wheel source" means file names and source text read from the published wheel, without executing it.

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| D1 | LangChain, https://docs.langchain.com/oss/python/langgraph/persistence/index.html | 2026-10-16 | current docs | Primary documentation | Retention guidance only ("scheduled job") |
| D2 | LangChain, https://docs.langchain.com/oss/python/langgraph/checkpointers | 2026-10-16 | current docs | Primary documentation | No TTL in OSS docs |
| D3 | LangChain, https://docs.langchain.com/oss/python/langgraph/stores | 2026-10-16 | current docs | Primary documentation | TTL not mentioned on this page |
| D4 | LangChain, https://docs.langchain.com/langsmith/configure-ttl | 2026-10-16 | Agent Server v0.8+ | Primary documentation | Applies to LangSmith/Agent Server deployments, not bare OSS savers |
| D5 | LangChain, https://docs.langchain.com/oss/python/concepts/memory | 2026-10-16 | current docs | Primary documentation | Conceptual |
| D6 | LangChain, https://docs.langchain.com/oss/python/langchain/long-term-memory | 2026-10-16 | current docs | Primary documentation | — |
| D7 | PyPI, https://pypi.org/pypi/langgraph-checkpoint-postgres/json (and its 3.2.0 wheel source) | 2026-10-16 | 3.2.0, uploaded 2026-10-14 | Primary documentation | TTL support read from source docstrings, not prose docs |
| D8 | PyPI, https://pypi.org/pypi/langgraph/json | 2026-10-16 | 1.2.15, uploaded 2026-10-12; langgraph-checkpoint 4.3.0; -sqlite 3.1.2; -mongodb 0.5.1 | Primary documentation | — |
| D9 | PyPI, https://pypi.org/pypi/langgraph-checkpoint-redis/json | 2026-10-16 | 0.5.2, uploaded 2026-08-20 | Primary documentation | Maintained by Redis (redis-developer), not LangChain |
| D10 | LangChain, https://raw.githubusercontent.com/langchain-ai/langmem/main/README.md; PyPI langmem | 2026-10-16 | 0.0.30, uploaded 2025-10-27 | Primary documentation | No release in about 12 months; activity status unknown |
| D11 | LangChain, https://raw.githubusercontent.com/langchain-ai/langgraph/main/LICENSE | 2026-10-16 | main | Primary documentation | MIT |
| D12 | OpenAI, https://openai.github.io/openai-agents-python/sessions/ | 2026-10-16 | current docs | Primary documentation | — |
| D13 | PyPI, https://pypi.org/pypi/openai-agents/json; https://raw.githubusercontent.com/openai/openai-agents-python/main/LICENSE | 2026-10-16 | 0.24.0, uploaded 2026-10-15 | Primary documentation | Pre-1.0 version |
| D14 | OpenAI, https://developers.openai.com/api/docs/guides/conversation-state | 2026-10-16 | global | Primary documentation | Deletion timing not described |
| D15 | OpenAI, https://developers.openai.com/api/reference/resources/conversations/methods/delete | 2026-10-16 | global | Primary documentation | — |
| D16 | Google, https://adk.dev/sessions/ (redirected from google.github.io/adk-docs) | 2026-10-16 | current docs | Primary documentation | — |
| D17 | Google, https://adk.dev/sessions/session/ | 2026-10-16 | current docs | Primary documentation | — |
| D18 | Google, https://adk.dev/sessions/state/ | 2026-10-16 | current docs | Primary documentation | — |
| D19 | Google, https://adk.dev/sessions/memory/ | 2026-10-16 | current docs | Primary documentation | — |
| D20 | PyPI, https://pypi.org/pypi/google-adk/json; https://raw.githubusercontent.com/google/adk-python/main/LICENSE | 2026-10-16 | 2.12.0, uploaded 2026-10-13 | Primary documentation | — |
| D21 | Google Cloud, https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank | 2026-10-16 | regional or multi-regional (`eu`, `us`) | Primary documentation | GA/Preview status not stated; TTL detail not fetched |
| D22 | Google Cloud, https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/api-quickstart | 2026-10-16 | — | Primary documentation | — |
| D23 | Google Cloud, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1beta1/projects.locations.reasoningEngines.memories/purge | 2026-10-16 | v1beta1 | Primary documentation | Beta API surface |
| D24 | Google Cloud, https://docs.cloud.google.com/agent-builder/agent-engine/memory-bank/overview | 2026-10-16 | — | Primary documentation | Enterprise security table only. The REST resource page for memory fields did not render |
| D25 | AWS, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-create-a-memory-store.html | 2026-10-16 | — | Primary documentation | Event-expiry minimum and default not stated |
| D26 | AWS, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/long-term-record-ttl.html | 2026-10-16 | — | Primary documentation | — |
| D27 | AWS, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-terminology.html | 2026-10-16 | — | Primary documentation | — |
| D28 | AWS, https://aws.amazon.com/bedrock/agentcore/pricing/ | 2026-10-16 | USD | Primary documentation | Units only; prices not recorded |
| D29 | PyPI, https://pypi.org/pypi/langgraph-checkpoint-aws/json | 2026-10-16 | 1.2.5, uploaded 2026-10-08 | Primary documentation | — |
| D30 | PyPI, https://pypi.org/pypi/bedrock-agentcore/json | 2026-10-16 | 1.24.1, uploaded 2026-10-07; Apache-2.0 | Primary documentation | SDK version, not a service version |
| D31 | Anthropic, https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool | 2026-10-16 | `memory_20250818` | Primary documentation | Platform availability (Bedrock, Vertex) not stated |
| D32 | Mem0, https://raw.githubusercontent.com/mem0ai/mem0/main/README.md | 2026-10-16 | main | Primary documentation; benchmark statements are Vendor claim | — |
| D33 | Mem0, https://docs.mem0.ai/components/vectordbs/overview | 2026-10-16 | current docs | Primary documentation | — |
| D34 | Mem0, https://docs.mem0.ai/open-source/overview | 2026-10-16 | current docs | Primary documentation | — |
| D35 | Mem0, https://docs.mem0.ai/platform/platform-vs-oss | 2026-10-16 | current docs | Primary documentation | Encryption and compliance not covered |
| D36 | Mem0, https://docs.mem0.ai/platform/features/expiration-date | 2026-10-16 | current docs | Primary documentation | — |
| D37 | Mem0, https://docs.mem0.ai/core-concepts/memory-operations/add | 2026-10-16 | current docs | Primary documentation | `agent_id` and `app_id` not defined |
| D38 | PyPI, https://pypi.org/pypi/mem0ai/json; https://raw.githubusercontent.com/mem0ai/mem0/main/LICENSE | 2026-10-16 | 2.2.1, uploaded 2026-09-25 | Primary documentation | — |
| D39 | Zep, https://raw.githubusercontent.com/getzep/graphiti/main/README.md; PyPI graphiti-core | 2026-10-16 | 0.31.1, uploaded 2026-10-15; Apache-2.0 (PyPI) | Primary documentation | LICENSE file not fetched |
| D40 | Zep, https://help.getzep.com/context-retention | 2026-10-16 | — | Primary documentation | — |
| D41 | Zep, https://help.getzep.com/deleting-data-from-the-graph | 2026-10-16 | — | Primary documentation | No regulatory statement |
| D42 | Zep, https://help.getzep.com/faq | 2026-10-16 | — | Primary documentation | Encryption and residency not covered |
| D43 | PyPI, https://pypi.org/pypi/zep-cloud/json | 2026-10-16 | 4.0.0, uploaded 2026-10-14 | Primary documentation | License absent from metadata |
| D44 | Letta, https://raw.githubusercontent.com/letta-ai/letta/main/README.md | 2026-10-16 | main | Primary documentation | V1 API server archived |
| D45 | Letta, https://github.com/letta-ai/letta-code | 2026-10-16 | main; Apache-2.0 | Primary documentation | No release listed |
| D46 | Letta, https://docs.letta.com/guides/core-concepts/memory/context-hierarchy/ | 2026-10-16 | current docs | Primary documentation | Limits are recommendations |
| D47 | PyPI, https://pypi.org/pypi/letta/json | 2026-10-16 | 0.34.12, uploaded 2026-10-12; summary "Letta Code" | Primary documentation | Package now ships Letta Code |
| D48 | Microsoft, https://learn.microsoft.com/en-us/agent-framework/agents/conversations/storage | 2026-10-16 | current docs | Primary documentation | TTL and deletion not covered |
| D49 | Microsoft, https://learn.microsoft.com/en-us/agent-framework/agents/conversations/context-providers | 2026-10-16 | current docs | Primary documentation | — |
| D50 | Microsoft, https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/context-providers/ | 2026-10-16 | current docs | Primary documentation | — |
| D51 | PyPI, https://pypi.org/pypi/agent-framework/json | 2026-10-16 | 1.22.0, uploaded 2026-10-15; MIT classifier | Primary documentation | LICENSE file not fetched |
| D52 | Microsoft, https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-memory | 2026-10-16 | footer "Last updated on 2025-06-09" | Primary documentation | Experimental; dates inconsistent on page |
| D53 | PyPI, https://pypi.org/pypi/semantic-kernel/json | 2026-10-16 | 1.45.0, uploaded 2026-10-06; MIT classifier | Primary documentation | — |
| D54 | Redis, https://redis.io/docs/latest/commands/expire/ | 2026-10-16 | current docs | Primary documentation | — |
| D55 | EUR-Lex, https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02016R0679-20160504 | 2026-10-16 | consolidated text 2016-05-04 (Regulation (EU) 2016/679) | Primary documentation (legal text) | Consolidated version has no legal effect; not legal advice. The direct curl to eur-lex was refused by the proxy; read via WebFetch |
| D56 | OWASP, https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html | 2026-10-16 | current | Primary documentation (community standard) | Guidance, not a standard with legal effect |
| D57 | Mem0, https://github.com/mem0ai/mem0/blob/94c3fe9f238f3dbf29c9ce98643bd71eb13077cd/mem0/memory/main.py#L2114 | 2026-10-17 | v2.2.1, commit `94c3fe9f238f3dbf29c9ce98643bd71eb13077cd` | Primary documentation (source code); scoped synthetic reproduction described below | `_delete_memory` deletes the vector and writes prior text into history; `delete_all` calls it. No full-service or backend-erasure test |
| D58 | Mem0, https://github.com/mem0ai/mem0/blob/94c3fe9f238f3dbf29c9ce98643bd71eb13077cd/mem0/memory/storage.py#L150 | 2026-10-17 | same v2.2.1 commit as D57 | Primary documentation (source code); scoped synthetic reproduction described below | `add_history` stores `old_memory`; `get_history` returns rows including deletion events. History-purge policy and backups not tested |
| D59 | Google Cloud, [Set up Memory Bank](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/setup) | 2026-10-18 | Mutable service guide, updated 2026-10-15 | Primary documentation | Active TTL and global-CMEK boundary; source read only. CC BY 4.0 page; linked paraphrase, no code copied |
| D60 | Google Cloud, [Memory revisions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/revisions) | 2026-10-18 | Mutable service guide, updated 2026-10-15 | Primary documentation | Revision retention/recovery, no physical-erasure measurement. CC BY 4.0 page; linked paraphrase, no code copied |
| D61 | Zep, [Graphiti entry points and request scope](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/graphiti.py); [group defaults and validation](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/helpers.py) | 2026-10-18 | v0.31.1, commit `5961293865a57844fe13d4eb061deb3501971fb2`; blobs `61ea540595de04a93860836de9777fbb68523bf6`, `9edf65c9787525b319d1d60db2abd707099c2731` | Primary documentation (source code) | Parameter and request-routing inspection; validation supplies no caller authorization |
| D62 | Zep, [shared search implementation](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/search/search.py) | 2026-10-18 | Same v0.31.1 commit; blob `9a74c84172dd15a159d4d5e2e35c10fb14d56f4a` | Primary documentation (source code) | Default/empty group normalization; no query or database executed |
| D63 | Zep, [Neo4j search operations](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/driver/neo4j/operations/search_ops.py), [Neo4j driver](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/driver/neo4j_driver.py), [base driver](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/driver/driver.py) | 2026-10-18 | Same v0.31.1 commit; blobs `9f0e308e39ddaec35d6f23dc31555f19037527be`, `350287966b5b2af2fa2d496c015190b32885e3bb`, `bf7d868a8d296bdc26878f8c8d91b03dafaa96eb` | Primary documentation (source code) | Conditional group predicates and inherited clone behavior; selected database privileges remain untested |
| D64 | Zep, [multiple-group decorator](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/decorators.py), [FalkorDB driver](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/graphiti_core/driver/falkordb_driver.py) | 2026-10-18 | Same v0.31.1 commit; blobs `80bb8700cd622204f3022e7c0bddf32b8e8d9d01`, `484bafbd6c2c26d65d618b9fe281d8cc0906f3d7` | Primary documentation (source code) | Per-graph routing and shared-client cloning; no deployment or concurrent workload tested |
| D65 | Zep, [pinned project metadata](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/pyproject.toml), [repository LICENSE](https://github.com/getzep/graphiti/blob/5961293865a57844fe13d4eb061deb3501971fb2/LICENSE) | 2026-10-18 | Same v0.31.1 commit; blobs `80bac62a0f71ea954dac393eba52c8a5ce8921da`, `5feb0d9d299a1107adfa8331306b13cc0eff2d78` | Primary documentation (source code/license) | Version and Apache-2.0 source declarations; no built-distribution/dependency rights audit or source redistribution |

### Mem0 deletion reproduction and limits

On Python 3.12.10, the v2.2.1 tag resolved to the commit in D57/D58. Downloaded tag and commit bytes matched (SHA-256: `main.py` = `f329ca4a17af1fbefb32ac10d4cc7ae7ddbdb7435a87eb74c30915cff98b8b7c`; `storage.py` = `5f5ecdadd2b260fd14f36a0f338336eb760275465dd1056a99a47e1ef07702bd`). The isolated test executed the exact AST-extracted synchronous `_delete_memory` method and its timestamp normalizer with the upstream `SQLiteManager(':memory:')`, one synthetic vector-store stub, and a no-op entity-cleanup stub. Input text was `SYNTHETIC retained text`. After deletion, the stub had no vector, but `get_history` returned that text in `old_memory` with `event='DELETE'`, `new_memory=None`, and `is_deleted=True`.

This reproduces retention in that method/storage path only. It does not exercise a full Mem0 service, actual vector or entity backends, asynchronous deletion, backups, or Mem0 Platform. `delete_all` reuse of `_delete_memory` and public `history()` delegation to `get_history` were source-checked, not executed end to end. Reproduce with `python tests/reproduce_mem0_deletion.py`: this opt-in script downloads the two pinned source files, checks the SHA-256 values before execution, and uses only synthetic text. It is excluded from automatic unittest discovery; no upstream source is vendored. Receiving owners must resolve history retention and purge policy before treating deletion as complete erasure.

### Limitations

- The GDPR text could not be downloaded with curl because the proxy refused eur-lex.europa.eu. It was read through WebFetch from the consolidated HTML. Quotes are partial, because of tool quote limits.
- These pages did not render or did not cover the point:
  - the Google REST resource page for Memory Bank `memories`;
  - the selected Memory Bank SDK/API's revision-TTL field mapping (the dated guide semantics are resolved at D59/D60);
  - Memory Bank and Mem0, Zep and Letta pricing.
- Microsoft Agent Framework and Semantic Kernel licenses come from PyPI classifiers, not LICENSE files.
- The overall `result` of the synthetic local evaluations was `indeterminate` or `invalid` because of unrelated baseline rules (for example budget and monitoring) on the minimal fixtures. Only the memory, RAG, vector and agent rule outcomes listed above are claimed.
