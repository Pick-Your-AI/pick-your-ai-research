# T4: Tools & APIs

Issue: #26 · Contract: 1.0.0 · Kinds: `tool`, `integration`
Status: original research merged via #70 and permission correction via #307; final criterion and receiving assessment below · Original research: 2026-10-16 · Final assessment: 2026-10-18

## Evidence status correction

Evidence metadata corrected at 2026-10-17T02:17:46Z under the [adopted #41 interim policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Checked primary documentation, publisher package metadata, registry entries and source inspection are not independent verification. These catalog claims and the published list-price rate remain `unverified`; the original facts, versions, source access dates and `checked_at` and pricing conditions are unchanged. No qualifying independent corroboration or runtime reproduction was supplied. Vendor capability statements remain documented claims, not measurements.

A proposed constraint may pass on eligible, versioned documentation while its evidence remains unverified. Missing eligible evidence remains unknown; absence from an unmarked capability list does not establish lack of support. Synthetic evaluator results check rule mechanics only and do not verify product behaviour. All rules and contract changes still require central versioned review through #40. This historical evidence correction did not establish receiving-owner acceptance or issue completion; the separately dated final assessment below records the later receipts and remaining delivery gate.

## User decision

Which external actions and data APIs can the agent call, and with what permissions, risks and costs?

This note defines the metadata every tool entry needs, a side-effect and risk classification, which tools need approval by default, and how tool and API usage feeds cost. Its 16 representative candidate rows use primary documentation to examine the metadata; they are source-checked findings, not independently verified product behaviour. AWS IAM supplies a separate principles row.

**Out of scope:** MCP transport and server packaging (#27), and knowledge ingestion connectors (#13). MCP *tool annotations* are used here only as evidence for risk classification.

### Deployment modes

The tool execution arrangements below describe where a call executes, where egress happens, and who holds the credential. They do not set the build's deployment mode: the accepted [operator/capacity vocabulary](../../prompts/SHARED.md#workstream-and-handoff-boundaries) assigns that mode from serving components, not tools. A managed SaaS tool can therefore accompany an API, managed or self-hosted model without itself making the build hybrid.

| Mode | What runs where | Examples source-checked here | Consequence for the builder |
| --- | --- | --- | --- |
| **API (provider-hosted server tool)** | The model provider executes the tool inside its own API; the application has no handler code (B4) | Anthropic web search and web fetch (B5, B6); OpenAI code interpreter (B41) | Uses the model provider's credential and billing. Only available when the model is called through that provider's API. Egress happens from the provider, not the user's network |
| **Managed SaaS API** | The application or agent runtime calls a vendor REST API with its own credential | GitHub, Slack, Gmail, Google Drive, Stripe, Brave Search, E2B Cloud, n8n Cloud | Needs a `credential_ref`, outbound network from the agent runtime, and the vendor's rate limits and pricing |
| **Self-hosted** | The tool's backend runs on user infrastructure | PostgreSQL (B34, B35), E2B infra (B32), n8n Community/Business (B37, B38) | The user owns patching, network policy and capacity. Licence terms apply (n8n is not OSI-licensed, B38). Can work in a network-restricted deployment |

`is_networked` (v1) covers only part of this. v1 cannot express "executes on the model provider" or "requires a specific model provider". See contract gaps.

## Candidate options

### Runtime tool category taxonomy (reusable)

Proposed values for a future `category` field (now `/tags` by convention). Categories describe *what the tool touches*. The risk class (next section) describes *what it changes*. A category does not imply a risk class.

| Category id | Covers | Typical default risk class | Source-checked (unverified) example in this note |
| --- | --- | --- | --- |
| `http_request` | Generic HTTP/API request tools where the target is configured or model-chosen | unknown until allowed targets and operations are bounded; use the conservative approval default | — (n8n HTTP-style flows, by reference) |
| `search_browse` | Web search, page fetch, headless browsing | read_only, open world | Anthropic web search/fetch, Brave Search |
| `database` | SQL or NoSQL query and mutation | read_only (with a read-only role) or write | PostgreSQL |
| `file_document` | File storage, documents, spreadsheets | read_only or write | Google Drive |
| `code_execution` | Sandboxed interpreters and VMs | high_impact (arbitrary code, cost, egress) | E2B, OpenAI code interpreter |
| `communication` | Email, chat, SMS, notifications | high_impact or irreversible (sending) | Gmail, Slack |
| `productivity` | Calendars, tasks, notes, CRM-lite | write | — |
| `developer_platform` | Source control, CI, issue trackers | read_only / write / irreversible by operation | GitHub |
| `cloud_infrastructure` | Cloud control-plane APIs (compute, IAM, storage) | high_impact or irreversible | AWS IAM (principles only) |
| `workflow_automation` | Webhook-triggered or scheduled workflow engines | unknown (depends on downstream steps) | n8n |
| `enterprise_system` | ERP, HRIS, ticketing, finance and payment systems | high_impact or irreversible | Stripe |
| `domain_specialized` | Domain APIs (maps, weather, legal, medical, scientific) | usually read_only | — |

### Representative candidates

One row per **operation family**. Families are split when side effects differ, because one provider API mixes read, write and irreversible operations under one credential (see "Operation family modelling").

| # | Tool / family | Provider (mode) | Auth method | Scopes / permissions | Rate limits | Side-effect class | Failure modes | Pricing unit | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Web search (`web_search_20260318`) | Anthropic (API server tool) | Claude API key | none beyond API access; an org admin can disable it or restrict domains in the Console | `max_uses` per request (caller-set); org rate limit (`too_many_requests`) | read_only, open world | Errors arrive inside HTTP 200 as `too_many_requests`, `max_uses_exceeded`, `query_too_long`, `request_too_large`, `invalid_tool_input`, `unavailable`; disabled tool returns 400 | per search: $10 per 1,000 searches (USD) + tokens; errors not billed | B5, B7 |
| 2 | Web fetch (`web_fetch_20260318`) | Anthropic (API server tool) | Claude API key | none; domain allow/block lists | `max_uses` (no default limit; failed fetches count) | read_only, open world, **exfiltration risk** | `url_not_in_prior_context`, `url_not_allowed`, `url_not_accessible`, `unsupported_content_type`, `too_many_requests`, `max_uses_exceeded`, `unavailable` (inside HTTP 200) | no extra charge; tokens only | B6, B7 |
| 3 | Brave web search (`/res/v1/web/search`) | Brave (SaaS) | API key in `X-Subscription-Token` | none | Search plan 50 QPS | read_only, open world | not source-checked (rate-limit page failed to load) | per request: "$5.00 per 1,000 requests", $5 monthly credit; currency code not stated | B8, B9 |
| 4 | GitHub issues read | GitHub (SaaS) | fine-grained PAT | "Issues" repository permission (read); none for public repos | 5,000 req/h authenticated; 60 req/h unauthenticated; secondary 100 concurrent, 900 points/min (GET = 1 point) | read_only | 403/429 with `x-ratelimit-remaining: 0`; wait for `x-ratelimit-reset` or `retry-after`; repeated violation "may result in the banning of your integration" | none published for REST calls (unknown) | B10, B11 |
| 5 | GitHub issues write (create) | GitHub (SaaS) | fine-grained PAT | "Issues" repository permission (write) | as above, plus 80 content-creating req/min and 500/h; POST/PATCH = 5 points | write | as above | unknown | B10, B11 |
| 6 | Slack `chat.postMessage` | Slack (SaaS) | OAuth v2 bot or user token | `chat:write` | "Special": about 1 message/s per channel, several hundred/min per workspace | high_impact (visible to others at once) | `ratelimited` with `Retry-After`; `rate_limited` (too many posts) | none published per call (unknown) | B13, B18 |
| 7 | Slack `chat.delete` | Slack (SaaS) | OAuth v2 bot or user token | **`chat:write` (same scope as posting)**; a bot token can delete only its own messages | Tier 3 (50+/min) | irreversible (project classification) | `ratelimited` + `Retry-After` | unknown | B14 |
| 8 | Slack `conversations.history` | Slack (SaaS) | OAuth v2 bot or user token | `channels:history`, `groups:history`, `im:history` or `mpim:history` | App/install cohort determines Tier 3 versus 1 request/min and 15-object pages; see dated B42/B43 readback below | read_only (private data) | HTTP 429 + `Retry-After` (B43; current readback) | unknown | B15, B16, B17; B42, B43 |
| 9 | Gmail `messages.send` | Google (SaaS) | OAuth 2.0 | `gmail.send` (Sensitive) | 100 quota units per call; 6,000 units/user/min; 1,200,000 units/project/min | irreversible (project classification) | quota errors; truncated exponential backoff advised | none published per call (unknown) | B19, B20 |
| 10 | Gmail `messages.delete` vs `messages.trash` | Google (SaaS) | OAuth 2.0 | `delete` needs `https://mail.google.com/` (Restricted); `trash` is reversible | delete 10 units; trash 20 units | delete = irreversible ("cannot be undone. Prefer messages.trash"); trash = write | as above | unknown | B20, B21 |
| 11 | Google Drive files | Google (SaaS) | OAuth 2.0 | `drive.file` (Non-sensitive, per-file) recommended over `drive` / `drive.readonly` (Restricted) | Cohort-specific quota units; see B44 readback | read_only or write by scope | 403/429; truncated exponential backoff (B44) | unknown | B22, B44 |
| 12 | Stripe create refund (`POST /v1/refunds`) | Stripe (SaaS) | restricted API key (`rk_`), agent-tagged keys recommended for agents | per-resource RAK permissions (names not fetched) | 100 req/s live, 25 req/s sandbox, 25 req/s per endpoint; 50 concurrent | irreversible (money movement; card refund cancel only briefly and only in the Dashboard) | 429 with `Stripe-Rate-Limited-Reason`; `lock_timeout`; refund can later fail (`refund.failed`) | none per API call; refunds "might incur a fee" and original processing fees are not returned | B23–B28 |
| 13 | E2B sandbox (SDK 2.56.0) | E2B (SaaS or self-hosted) | API key (`E2B_API_KEY`) | none | Hobby 20 concurrent sandboxes, 1 h sessions; Pro 100 (to 1,100), 24 h | high_impact (arbitrary code, spend, egress) | not fetched | per second: $0.000014/s per vCPU, $0.0000045/s per GiB RAM; Pro $150/month | B29–B33 |
| 14 | OpenAI code interpreter (`code_interpreter`) | OpenAI (API server tool) | OpenAI API key | none | 100 RPM per org | high_impact (contained) | container expires after 20 min idle; later use fails | "built-in tools rates" (values not extracted) | B41 |
| 15 | PostgreSQL query via read-only role (18.6 docs) | self-hosted | DB credentials (wire protocol, not HTTP) | `GRANT pg_read_all_data` or per-table `SELECT`; RLS still applies | `statement_timeout` (ms; default 0 = disabled) | read_only only if the **role** lacks write privileges | timeout aborts statement | infrastructure cost only | B34, B35 |
| 16 | n8n Webhook trigger (2.43.7) | n8n (cloud or self-hosted) | None, Basic, Header or JWT auth; IP allowlist | n/a | max payload 16 MB (configurable self-hosted) | unknown (depends on workflow) | IP not allowlisted → 403 | Cloud: per monthly workflow executions (EUR); self-hosted: licence terms | B36–B39 |
| — | AWS IAM (principles) | AWS | temporary role credentials preferred over long-term keys | least-privilege actions on specific resources under conditions; permissions boundaries; Access Analyzer policy generation | — | — | — | — | B40 |

**Status flags.** None of the candidates is deprecated.
- Anthropic web search exists in three versions (`web_search_20250305`, `20260209`, `20260318`). From 20260209 on, the default `allowed_callers` routes it through code execution (B5).
- Slack has changed `conversations.history` and `conversations.replies` limits for new non-Marketplace apps since 2025-05-29 (B16).
- PostgreSQL 19 is at RC 1; 18 is current (B34).
- n8n's Business plan is self-hosted only (B37).

### Operation family modelling (one tool item per side-effect class)

A provider API is **not** one tool. Evidence shows that one credential or scope covers operations with different risk:
- Slack `chat:write` authorises both `chat.postMessage` and `chat.delete` (B13, B14).
- Gmail `https://mail.google.com/` allows permanent deletion, while `gmail.send` only sends (B19, B21).
- Stripe secret keys have "unrestricted permissions on all Stripe APIs" (B27).

Therefore:
1. Model one `tool` item per operation family whose side-effect class is uniform, e.g. `tool.github.issues-read` (read_only) and `tool.github.issues-write` (write).
2. Model the provider connection once as an `integration` (`integration.github.rest-api`). It holds the endpoint, credential and rate limit, and lists its families in `associated_tool_refs`. That catalog list does not bind a tool selection to a particular integration selection or implement credential inheritance; the proposed binding semantics are in T4-B6 below.
3. Guardrails (#35) can allow a reviewed read family and gate the write family only when the actual invocation boundary enforces that split. Keep the credential outside model-controlled arguments and arbitrary tool code; bind the allowed method, endpoint, resource and operation to the reviewed family. A descriptive tool name or catalog entry does not restrict the upstream token.
4. Scope checks alone cannot separate families that share a scope (Slack `chat:write`). The guardrail must enforce by **operation**, not only by scope (handoff to #35). If the caller can bypass that boundary, choose another endpoint or access the raw credential, assess every reachable operation. An unproved boundary cannot justify downgrading the risk class. This is a research control requirement; the catalog and the frozen v1 rule examples do not implement it.

### `tool` vs `integration` in v1

| Aspect | `tool` (`spec_tool`) | `integration` (`spec_integration`) |
| --- | --- | --- |
| What it is | A callable capability the model can select | A connection to an external system |
| Direction | Outbound, agent-initiated | `api` (outbound), `webhook` (inbound HTTP), `event` (inbound stream), `connector` (packaged sync/action bundle) |
| Required fields | `protocol`, `side_effect` | `integration_type` |
| Risk fields | `side_effect`, `required_scopes`, `is_networked` | none; risk lives in `associated_tool_refs` |
| Limits | none in spec (timeout in settings) | `rate_limit_per_minute` in spec and settings |
| Counted by `tools.mutating_count` | yes | **no** |

**Use a `tool`** when the model decides to call it and the call has a definable side effect. This includes provider-hosted server tools and local tools with no integration.

**Use an `integration`** when:
- several tools share one provider connection, credential and rate budget (group them with `associated_tool_refs`), or
- the external system calls *into* the build (webhook, event). An inbound trigger is not model-selected, so it is not a tool. Its side effects come from the workflow it starts (n8n, B36).

**Use both** for SaaS providers with many operation families (GitHub, Slack, Google Workspace, Stripe).

### Boundary with T3 (#13): one provider identity, two owners

Google Drive and Slack each serve two roles. They are knowledge sources to ingest (T3 `data_source`, `source_type: connector|api`) and runtime action targets (T4 `tool` and `integration`). The proposed split:

1. **T4 owns the provider connection.** It owns `integration.<provider>.<api>`: endpoint, auth methods, rate limits, and the runtime operation families (`tool.*`).
2. **T3 owns ingestion semantics.** It owns `data_source.<provider>.<source>`: modality, classification, refresh, ACL and deletion. It does not redefine endpoint or credential facts.
3. **Selections link them.** A `data_source` selection has a build link `relation: "provided_by"` to the integration selection (`provided_by` exists in v1 build links). The proposed connection model then holds one provider identity and one `credential_ref`; v1 permits that link shape but does not resolve or inherit credentials through it (T4-B6).
4. **Scopes stay separate.**
   - Ingestion scopes (e.g. Drive `drive.readonly`, Restricted, B22) are justified by T3.
   - Runtime scopes (e.g. `drive.file`, Non-sensitive) sit on T4 tool items.
   - If both share one OAuth client, the granted scope set is the union. #35 must evaluate that union, not each half.
5. **v1 gap.** `spec_data_source` and `spec_tool` have no shared provider key. Propose a common `provider_id` (or `x_provider_id` until #40 decides) on `data_source`, `integration` and `tool`, so catalog search can deduplicate providers. Do not create a second catalog of providers.

### Required metadata for every tool entry

Mapped to v1 JSON pointers. "Note only" means v1 cannot express it.

| Metadata | v1 pointer | Status |
| --- | --- | --- |
| Stable id | `/id` | expressible |
| Version (upstream API or tool version) | `/version` | expressible. APIs without versions (Slack Web API) have no exact value; such items are not proposed |
| Lifecycle status | `/status` | expressible |
| Provider | — | **note only** (no `provider_ref` on tool or integration) |
| Category | `/tags` (convention) | partial; propose enum `category` |
| Supported execution interfaces (OpenAI function JSON Schema, Anthropic tool use, MCP tool, provider server tool) | `/spec/protocol` covers transport only (`mcp` is a value) | **note only**; propose `interfaces[]` with an explicit executor binding |
| Input / output contract (JSON Schema) | — | **note only**; MCP requires `inputSchema` and allows `outputSchema` (B1); OpenAI `parameters` (B3); Anthropic `input_schema` (B4) |
| Auth method | `/spec/auth_methods` (tool, integration) | partial: no `basic`, `jwt` or personal access token values |
| OAuth scopes / permissions | `/spec/required_scopes` (tool); `/settings/allowed_scopes` (selection) | expressible as strings; no scope sensitivity (Google: Non-sensitive / Sensitive / Restricted, B19, B22) |
| Credential handling | `/settings/credential_ref` (`secret://…`) on tool, integration and model provider | Direct references are expressible; connection binding, inheritance and credential readiness require the T4-B6 proposal through #40; key type is note only |
| API limits | `/spec/rate_limit_per_minute` (integration only, integer) | partial: per-hour, per-second, quota units, concurrency and "50+" tiers are not expressible |
| Network access | `/spec/is_networked` | partial: no domain allowlist, egress location or open-world flag |
| Side-effect class | `/spec/side_effect` (`read_only`, `mutating`) | partial; four-class proposal below; `x_side_effect_class` in proposals |
| Data-access scope | — | **note only**; propose `data_access_scope` (`none`, `public`, `own_account`, `workspace`, `organization`) |
| Approval requirement | — (guardrail `enforcement: escalate` is the nearest) | **note only** |
| Idempotency / retry | — | **note only**; e.g. Stripe `Idempotency-Key` (B23) |
| Failure behaviour | — | **note only**; e.g. errors inside HTTP 200 (B5, B6) vs HTTP 429 (B10, B24) |
| Usage / pricing unit | `/billing_class` + pricebook `meter` | partial: only `request` fits; per-second CPU/RAM, per execution, per container-hour have no meter |
| Licensing / usage restrictions | `/license` (software) | partial: API terms of service have no field |
| Evidence and verification date | `/provenance/*/source_uri`, `checked_at`, `verification_status` | expressible |
| Timeout | `/settings/timeout_ms` | expressible |

## Comparison fields

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| tool id → `/id` | string, `tool.<provider>.<family>` | e.g. `tool.github.issues-read` | — | One version per id under current intake |
| provider (note only) | string, provider id | `anthropic`, `github`, `google`, `stripe` … | — | Needs `provider_id` (#40) |
| version → `/version` | string, upstream API or tool version | GitHub `2026-03-10`; Stripe `2026-09-30.endive`; Anthropic `web_search_20260318`; E2B `2.56.0`; n8n `2.43.7` | B5, B11, B28, B31, B39 | Gmail `v1` and Brave `v1` come from the URL path |
| auth method → `/spec/auth_methods` | enum array `none, api_key, oauth2, service_account, mTLS` | api_key: Anthropic, Brave, GitHub PAT, Stripe, E2B; oauth2: Slack, Gmail, Drive | B9, B11, B18, B19, B27, B30 | PAT and n8n Header auth are mapped to `api_key`; n8n Basic and JWT have no value |
| scopes → `/spec/required_scopes` vs `/settings/allowed_scopes` | string array, provider-native scope strings | `chat:write`; `https://www.googleapis.com/auth/gmail.send`; GitHub `issues:read` (project notation for the fine-grained permission) | B11, B13, B19 | Scope granularity ≠ operation granularity (Slack) |
| rate limits → `/spec/rate_limit_per_minute` (integration) | integer, requests per minute | GitHub 5,000/h (≈83/min, not an integer); Stripe 100/s; Brave 50 QPS; Gmail quota units | B8, B10, B20, B24 | Most limits are not "requests per minute"; omitted from proposals rather than converted |
| side-effect class → `/spec/side_effect` + `x_side_effect_class` | enum (v1: 2 values; proposed: 4) | see taxonomy | B2 | Project classification, not vendor-stated |
| failure modes (note only) | enum proposal: `http_429_retry_after`, `http_403_rate`, `in_band_error`, `quota_units`, `lock_timeout`, `async_failure` | in-band errors (Anthropic), 403/429 (GitHub), 429 + reason header (Stripe), later `refund.failed` (Stripe) | B5, B10, B24, B25 | Needed by #35 and #38 |
| pricing unit → pricebook `/rates/*/meter` | enum; only `request` applies | Anthropic search USD 0.01/request; Brave $0.005/request (currency unstated) | B7, B8 | E2B per-second, n8n per execution, OpenAI per container: no v1 meter |
| billing class → `/billing_class` | enum `free, included, metered, unknown` | web search metered; web fetch included; GitHub, Gmail, Stripe API calls unknown | B7 | "Free API, paid account" cases stay `unknown` |
| source → `/provenance` | URI + date + status | all items | — | — |

## Evidence

Original B1–B41 entries accessed on 2026-10-16; dated follow-up entries below retain their own access dates. Grades follow `docs/RESEARCH_METHOD.md` and the adopted #41 interim policy above. Fetched with WebFetch (a summarising fetcher) or with curl for raw files and package registries. WebFetch summaries were checked against quoted text where possible.

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| B1 | MCP, https://modelcontextprotocol.io/specification/latest/server/tools | 2026-10-16 | spec 2026-07-28 | Primary documentation | Human-in-the-loop guidance is SHOULD, not MUST |
| B2 | MCP, https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2026-07-28/schema.ts | 2026-10-16 | `LATEST_PROTOCOL_VERSION = "2026-07-28"` | Primary documentation | `ToolAnnotations` are hints only |
| B3 | OpenAI, https://developers.openai.com/api/docs/guides/function-calling | 2026-10-16 | undated | Primary documentation | Strict-mode rules shown only by example |
| B4 | Anthropic, https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview | 2026-10-16 | undated | Primary documentation | — |
| B5 | Anthropic, https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool | 2026-10-16 | `web_search_20250305` / `20260209` / `20260318` | Primary documentation | — |
| B6 | Anthropic, https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool | 2026-10-16 | `web_fetch_20250910` … `20260318` | Primary documentation | — |
| B7 | Anthropic, https://platform.claude.com/docs/en/about-claude/pricing | 2026-10-16 | USD ("All prices are in USD") | Primary documentation | Claude API only; other platforms not checked |
| B8 | Brave, https://api-dashboard.search.brave.com/app/plans | 2026-10-16 | "$" without a currency code | Primary documentation | Currency code not stated |
| B9 | Brave, https://api-dashboard.search.brave.com/app/documentation/web-search/get-started | 2026-10-16 | `/res/v1/` | Primary documentation | Rate-limit guide (…/documentation/rate-limiting) failed to load |
| B10 | GitHub, https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api | 2026-10-16 | github.com | Primary documentation | — |
| B11 | GitHub, https://docs.github.com/en/rest/issues/issues | 2026-10-16 | API 2026-03-10 | Primary documentation | "Update an issue" section not in the fetched excerpt |
| B12 | GitHub, https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens | 2026-10-16 | — | Primary documentation | Page too long; repository permission sections not read. Repo deletion permission unverified |
| B13 | Slack, https://docs.slack.dev/reference/methods/chat.postMessage | 2026-10-16 | — | Primary documentation | — |
| B14 | Slack, https://docs.slack.dev/reference/methods/chat.delete | 2026-10-16 | — | Primary documentation | — |
| B15 | Slack, https://docs.slack.dev/reference/methods/conversations.history | 2026-10-16 | — | Primary documentation | Non-Marketplace limit values not rendered |
| B16 | Slack, https://docs.slack.dev/apis/web-api/rate-limits | 2026-10-16 | — | Primary documentation | Tier table rendered empty |
| B17 | Slack, https://docs.slack.dev/changelog/2018/03/01/great-rate-limits | 2026-10-16 | 2018-03-01 | Primary documentation | Dated; tier values may have changed since |
| B18 | Slack, https://docs.slack.dev/authentication/installing-with-oauth | 2026-10-16 | OAuth v2 | Primary documentation | Token rotation not covered |
| B19 | Google, https://developers.google.com/workspace/gmail/api/auth/scopes | 2026-10-16 | Gmail API v1 | Primary documentation | — |
| B20 | Google, https://developers.google.com/workspace/gmail/api/reference/quota | 2026-10-16 | — | Primary documentation | Error codes on a separate page, not fetched |
| B21 | Google, https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/delete | 2026-10-16 | v1 | Primary documentation | — |
| B22 | Google, https://developers.google.com/workspace/drive/api/guides/api-specific-auth | 2026-10-16 | — | Primary documentation | Drive quotas not fetched |
| B23 | Stripe, https://docs.stripe.com/api/idempotent_requests | 2026-10-16 | API v1 | Primary documentation | — |
| B24 | Stripe, https://docs.stripe.com/rate-limits | 2026-10-16 | — | Primary documentation | — |
| B25 | Stripe, https://docs.stripe.com/refunds | 2026-10-16 | — | Primary documentation | — |
| B26 | Stripe, https://docs.stripe.com/api/refunds/create | 2026-10-16 | — | Primary documentation | — |
| B27 | Stripe, https://docs.stripe.com/keys | 2026-10-16 | — | Primary documentation | Restricted-key permission names not fetched |
| B28 | Stripe, https://docs.stripe.com/api/versioning | 2026-10-16 | 2026-09-30.endive | Primary documentation | — |
| B29 | E2B, https://e2b.dev/pricing | 2026-10-16 | "$" without a currency code | Primary documentation | — |
| B30 | E2B, https://docs.e2b.dev/ | 2026-10-16 | — | Primary documentation | Timeout and internet defaults not covered |
| B31 | PyPI, https://pypi.org/pypi/e2b/json | 2026-10-16 | e2b 2.56.0 (2026-10-13); e2b-code-interpreter 2.11.0 | Primary documentation | license_expression MIT |
| B32 | E2B, https://raw.githubusercontent.com/e2b-dev/infra/main/README.md | 2026-10-16 | main | Vendor claim | Isolation claims not independently tested |
| B33 | E2B, https://raw.githubusercontent.com/e2b-dev/E2B/main/LICENSE | 2026-10-16 | main | Primary documentation | Root LICENSE Apache-2.0, but the python-sdk `pyproject.toml` declares MIT; unresolved |
| B34 | PostgreSQL, https://www.postgresql.org/docs/current/predefined-roles.html | 2026-10-16 | 18.6 | Primary documentation | — |
| B35 | PostgreSQL, https://www.postgresql.org/docs/current/runtime-config-client.html | 2026-10-16 | 18.6 | Primary documentation | — |
| B36 | n8n, https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/ | 2026-10-16 | — | Primary documentation | — |
| B37 | n8n, https://n8n.io/pricing/ | 2026-10-16 | EUR, annual billing | Primary documentation | No per-execution list price |
| B38 | n8n, https://raw.githubusercontent.com/n8n-io/n8n/master/LICENSE.md | 2026-10-16 | Sustainable Use License 1.0 | Primary documentation | Not an OSI or SPDX licence |
| B39 | npm, https://registry.npmjs.org/n8n | 2026-10-16 | 2.43.7 (2026-10-16) | Primary documentation | — |
| B40 | AWS, https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html | 2026-10-16 | — | Primary documentation | — |
| B41 | OpenAI, https://developers.openai.com/api/docs/guides/tools-code-interpreter | 2026-10-16 | — | Primary documentation | Prices not on page |

## Risk taxonomy and approval defaults (handoff to #35)

### Primary evidence: MCP tool annotations are hints

The MCP schema 2026-07-28 (B2) defines four `ToolAnnotations` hints:

| Hint | Meaning | Default |
| --- | --- | --- |
| `readOnlyHint` | "the tool does not modify its environment" | false |
| `destructiveHint` | "may perform destructive updates"; false means "only additive updates"; meaningful only when not read-only | true |
| `idempotentHint` | repeated calls with the same arguments have "no additional effect" | false |
| `openWorldHint` | interacts with an "open world" of external entities (e.g. web search) rather than a closed domain | true |

The schema states that "all properties in `ToolAnnotations` are **hints**", that they are "not guaranteed to provide a faithful description of tool behavior", and that "Clients should never make tool use decisions based on `ToolAnnotations` received from untrusted servers" (B2). The tools page says clients "MUST consider tool annotations to be untrusted unless they come from trusted servers" (B1). The MCP defaults are conservative: an unannotated tool is assumed to be writing, destructive, non-idempotent and open-world.

**Rule for the builder:** the catalog's own reviewed classification (`side_effect`, proposed `side_effect_class`) is authoritative. Annotations from an MCP server are input to that review, and they count only when `spec_mcp_server.trust_level` is `internal` or `trusted_external` (#27).

### Four classes

| Class | Definition | Examples (source-checked) | Maps to v1 `side_effect` | MCP hints to assess independently (B54) | Default approval | Least-privilege requirement |
| --- | --- | --- | --- | --- | --- | --- |
| `read_only` | No state change in any system. It may still read private data or reach the open web | GitHub list issues; Slack `conversations.history`; web search/fetch; Postgres SELECT under a read-only role | `read_only` | `readOnlyHint: true` is consistent with a reviewed non-mutating operation; open-world scope is separate, and no received hint proves the classification | none (auto) | read-only permission level (GitHub "read", `drive.readonly`); read-only DB role, not just a read-only transaction |
| `write` | Changes state in the caller's own resources, additive or reversible by another API call | GitHub create issue; Gmail `messages.trash` | `mutating` | `readOnlyHint: false`; assess additive/destructive updates and repeat-call effects separately. Reversibility does not imply `destructiveHint: false` | policy allowlist + audit log; no per-call human approval | narrowest write permission (GitHub "Issues: write" only) |
| `high_impact` | Reversible in principle, but with immediate effects on other people, shared spaces, spend or infrastructure | Slack `chat.postMessage` (seen at once by others); E2B sandbox (arbitrary code, per-second spend, egress); cloud resource changes | `mutating` | `readOnlyHint: false`; impact does not determine open-world interaction, destructiveness or idempotency | **human approval by default** (guardrail `escalate`), which may be relaxed per tool by policy | dedicated credential; domain and egress allowlist; spend cap |
| `irreversible` | Cannot be undone through any API once executed | Gmail `messages.delete` ("cannot be undone"); Gmail `messages.send`; Stripe refund (cancel only briefly, Dashboard only); Slack `chat.delete` | `mutating` | `readOnlyHint: false`; assess destructiveness, idempotency and open-world interaction independently. An irreversible action may still be idempotent | **human approval always**; dry-run or preview; idempotency key where available | dedicated credential boundary; narrowest provider-supported permissions and an enforced operation allowlist. Gmail permanent deletion requires the broad full-mail scope: exclude that operation when this scope is unacceptable; see the dated B50/B51 correction below. Stripe RAK resource mapping remains explicitly unresolved (B48) |

The project risk classes are not MCP annotation bundles. In B54, `destructiveHint: false` means additive-only updates, while `idempotentHint: true` concerns the effect of repeating the same arguments; neither is a reversibility score. `destructiveHint` and `idempotentHint` are meaningful only for a non-read-only tool. `openWorldHint` concerns the interaction domain independently of impact. Determine each property from eligible evidence for the actual operation, retaining unknowns and the annotation trust boundary above; do not synthesize provider hints from this taxonomy.

**Classification rules:**
1. Classify by the *worst* operation reachable through the actual credential and invocation boundary, not by the item's name. A raw `chat:write` token can permit both posting and deletion (B52/B53); a family-specific classification requires the enforced restriction described above. Required catalog scopes are prerequisites, not proof of the actual token's permissions or of enforcement.
2. Unknown uses the `irreversible` approval default until reviewed; retain the unknown evidence explicitly. This is a conservative project policy, not an MCP-defined risk enum or a claim that every unknown operation is factually irreversible.
3. An inbound integration (webhook) inherits the worst class of the workflow it triggers (n8n). If that is unknown, use `irreversible`.
4. `read_only` + `is_networked` + private data is an exfiltration path. The Anthropic web fetch docs warn of "data exfiltration risks" when untrusted input meets sensitive data (B6). MCP advises showing tool inputs "to avoid malicious or accidental data exfiltration" (B1). This needs a guardrail regardless of side effect (rule `rule.t4.tool.network.exfiltration`).

**Vendor-side approval exists.** Stripe agent-tagged restricted keys are "automatically subject to approval rules" covering "payouts, refunds, and account configuration changes" (B27). Anthropic lets an org admin disable web search and restrict its domains (B5). #35 should record whether a provider-side control satisfies the builder's approval requirement.

**v1 mapping proposal (#40).**
- Keep `spec_tool.side_effect` as the coarse, required field: `read_only` → `read_only`; `write`, `high_impact` and `irreversible` → `mutating`.
- Add an optional `spec_tool.side_effect_class` enum `read_only | write | high_impact | irreversible`. Its consistency constraint: `side_effect == read_only` iff `side_effect_class == read_only`.
- Until then, the proposals carry `extensions.x_side_effect_class`.
- Add metrics `tools.high_impact_count` and `tools.irreversible_count` beside `tools.mutating_count`.

### Idempotency and retry (note only)

- Stripe: all v1 `POST`s accept `Idempotency-Key` (≤255 characters). Keys can be pruned after 24 hours. Reuse with different parameters errors. The saved result, including a `500`, is replayed (B23).
- GitHub: back off until `x-ratelimit-reset` or `retry-after`, then exponentially (B10).
- Google: truncated exponential backoff (B20).
- Slack: honour `Retry-After` (B13, B17).
- Proposal: a builder-level rule that an `irreversible` tool must declare an idempotency mechanism (`key_header`, `natural`, or `none`). If it is `none`, automatic retries are disabled.

## Compatibility proposals

Rules are proposed to #40 using the [rule proposal template](../../templates/rule-proposal.md). Outcome (`pass/fail/unknown/skipped`) is separate from severity (`info/warning/error`).
- **Source-checked (unverified):** the assertion is supported by cited primary text, and the expression uses only v1 fields.
- **Hypothesis:** policy judgement or contract change needed.

The ten retained JSON examples below validate against `ruleset.schema.json`; T4-B7 is preserved as a superseded universal framework prerequisite, not a current rule proposal. Earlier synthetic fixture checks produced pass for scopes, guardrail and MCP rules, and skipped for cost and exfiltration rules. The former executable `credential.ref` rule is withdrawn: it falsely required a tool-local reference for shared and provider-hosted credentials. T4-B6 is now a contract-dependent proposal, not an executable v1 check; v1 cannot establish credential readiness by skipping or omitting that check.

### Problems found in baseline T4 rules

| Baseline rule | Problem | Proposal |
| --- | --- | --- |
| `rule.agent.tools.framework`, `rule.tool.mutation.guardrails` | Refs use `role: "primary"`, and a ref must match exactly one selection. A build with several tools (roles `search`, `github-write`, …) has no generic way to check every tool. Tools in non-primary roles are not checked by `rule.agent.tools.framework` at all | #40: add a per-selection quantifier (e.g. `for_each: {kind: "tool"}`) or require one rule instance per role |
| `tools.mutating_count` metric | Counts only `kind == tool`. Integrations (inbound webhooks that trigger actions) and MCP-exposed tools not separately selected are invisible | Count `integration` items whose `associated_tool_refs` are mutating, and tools in `mcp_server.tool_refs` |
| `rule.tool.mutation.guardrails` | Checks `policies` contains `tool_permissions` but not that the guardrail `targets` includes `tool`, nor that enforcement is not `audit` | Refined by `rule.t4.tool.guardrail.targets` and `rule.t4.tool.guardrail.enforcement` |
| `rule.budget.monthly.cap` and dependency graph | `affected_kinds` lists `integration` but not `tool`. The graph has `dep.cost_policy.integration` but **no `cost_policy` → `tool` edge**, though metered tools (web search, E2B) add recurring cost | Add `tool` to `affected_kinds` and an edge `cost_policy depends_on tool (informs, if_selected)` |

### T4-B1 `rule.t4.tool.scopes.allowed`: tool permissions vs selected policy (example 7)

- Participating kinds, pointers: `tool` catalog `/spec/required_scopes`; `tool` selection `/settings/allowed_scopes`.
- Applicability: a primary tool is selected and declares required scopes.
- Assertion: `required_scopes subset_of allowed_scopes`. Evidence: provider scopes gate operations (B11, B13, B19, B22).
- Severity: error. Missing `allowed_scopes` → `unknown` → `review`. Absence must not mean "unrestricted".
- Explanation and remediation: the tool cannot work within the scopes the policy allows. Widen deliberately or pick a narrower family.
- Edges: `dep.guardrail.tool`. Consumers: #35.
- Passing example (synthetic): required `["chat:write"]`, allowed `["chat:write"]`. Failing: required `["issues:write"]`, allowed `["issues:read"]`. Unknown: allowed absent.
- Version impact: none (v1 fields only). **Source-checked (unverified)** (expression); the policy semantics are a hypothesis for #35.

```json
{"id":"rule.t4.tool.scopes.allowed","severity":"error","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"exists","value":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}}}]},"assert":{"op":"subset_of","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}},"right":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/settings/allowed_scopes"}}},"on_unknown":"review","message":"The tool needs permission scopes that this build does not allow.","remediation":"Grant the missing scopes in allowed_scopes after policy review, or choose a narrower tool operation family.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B2 `rule.t4.tool.scopes.least-privilege`: over-granted scopes

- Pointers as T4-B1, reversed: `allowed_scopes subset_of required_scopes`.
- Evidence: Google advises "the most narrowly focused scope possible" (B19). AWS says to "grant only the permissions required to perform a task" (B40).
- Severity: warning; `on_unknown: review`.
- Passing: allowed `["gmail.send"]` = required. Failing: allowed `["https://mail.google.com/"]` for a send-only tool. Skipped/unknown: no `allowed_scopes`.
- **Source-checked (unverified).**

```json
{"id":"rule.t4.tool.scopes.least-privilege","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/settings/allowed_scopes"}}},{"op":"exists","value":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}}}]},"assert":{"op":"subset_of","left":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/settings/allowed_scopes"}},"right":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}}},"on_unknown":"review","message":"The build allows scopes this tool does not need.","remediation":"Remove scopes from allowed_scopes that are not in the tool's required_scopes.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B3 `rule.t4.tool.guardrail.targets`: refines `rule.tool.mutation.guardrails`

- When `tools.mutating_count > 0`, the primary guardrail's `/spec/targets` must contain `tool`.
- Evidence: MCP says applications SHOULD provide confirmation and a human able to deny invocations (B1).
- Severity: error; `on_unknown: block` (same as the baseline).
- Passing: targets `["input","tool"]`. Failing: targets `["output"]` with a `tool_permissions` policy. Unknown: no metric (catalog item missing).
- **Source-checked (unverified)** (expression); policy owned by #35.

```json
{"id":"rule.t4.tool.guardrail.targets","severity":"error","applies_when":{"op":"gt","left":{"metric":"tools.mutating_count"},"right":{"literal":0}},"assert":{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/targets"}},"right":{"literal":"tool"}},"on_unknown":"block","message":"Mutating tools are selected but the guardrail does not target tool calls.","remediation":"Select a guardrail whose targets include tool.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B4 `rule.t4.tool.guardrail.enforcement`: no audit-only or fail-open guard on mutation

- Guardrail selection `/settings/enforcement in ["block","escalate"]` and `/settings/failure_action == "fail_closed"`.
- Severity: warning; `on_unknown: review`. A missing setting may defer to the catalog default; #35 should define that precedence.
- Failing: `enforcement: "audit"`. **Hypothesis** (policy choice).

```json
{"id":"rule.t4.tool.guardrail.enforcement","severity":"warning","applies_when":{"op":"gt","left":{"metric":"tools.mutating_count"},"right":{"literal":0}},"assert":{"op":"all","args":[{"op":"in","left":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/settings/enforcement"}},"right":{"literal":["block","escalate"]}},{"op":"eq","left":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/settings/failure_action"}},"right":{"literal":"fail_closed"}}]},"on_unknown":"review","message":"Mutating tools are guarded by an audit-only or fail-open guardrail.","remediation":"Set guardrail enforcement to block or escalate and failure_action to fail_closed.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B5 `rule.t4.tool.irreversible.approval`: needs contract change via #40

- Applies when the finer side-effect class is `high_impact` or `irreversible`. Requires a guardrail that targets tools, has `tool_permissions`, and enforces `escalate` (human approval).
- Missing field: `spec_tool.side_effect_class` (today only `extensions.x_side_effect_class`). A per-tool approval mode in `settings_tool` would also be needed to allow per-tool exceptions.
- Severity: error for `irreversible`, warning for `high_impact`. `on_unknown: block`.
- Evidence: B21, B25, B27 (Stripe default approval rules for refunds and payouts), B1. **Hypothesis.**

```text
applies_when: in(catalog tool /spec/side_effect_class, ["high_impact","irreversible"])      # field missing in v1
assert: all(
  contains(catalog guardrail /spec/targets, "tool"),
  contains(catalog guardrail /spec/policies, "tool_permissions"),
  eq(selection guardrail /settings/enforcement, "escalate"))
```

### T4-B6 `rule.t4.tool.credential.ref`: credential source and resolution (needs contract change via #40)

**Status: proposed contract semantics, not adopted; the synthetic experiment below is not a production resolver.** The former v1 JSON rule required every authenticated tool to carry its own `/settings/credential_ref`. That contradicts the shared integration connection and provider-hosted execution models above. It is withdrawn rather than treating an unresolved source as authenticated or requiring duplicate references.

**Existing v1 facts:** `selection.schema.json` defines opaque `secret://` references on tool, integration and model-provider settings. `build.schema.json` permits `provided_by` links with selection IDs. Neither the schemas nor the reference evaluator define credential inheritance, credential-source selection, link traversal or effective authorization. `associated_tool_refs` names catalog items, not the active connection selection. These facts do not establish that an inherited credential works.

**Proposed resolution semantics for #40/#35 review:** introduce an explicit per-tool credential binding with source `direct`, `integration`, `model_provider` or `none`, a selected authentication method, and an exact connection selection ID when inherited. These are proposed concepts, not existing v1 fields or JSON pointers. Do not infer a binding from a role, provider name, catalog association, available secret or the absence of a tool-local reference.

| Explicit source | Proposed check | Outcome when facts are missing or contradictory |
| --- | --- | --- |
| `direct` | Only this case requires the tool's own `/settings/credential_ref`; it must be an opaque secret reference and the selected auth method must be supported | Missing required reference: `fail`; unknown auth support: `unknown` |
| `integration` | Require exactly one enabled, version-resolved integration selection identified by the binding and a `provided_by` link from this tool selection to that integration. Resolve its `/settings/credential_ref`; confirm the connection serves this operation family and supports the selected auth method | Known absent/disabled/wrong-kind target or absent required reference: `fail`; unresolved version, unknown association or multiple candidate bindings: `unknown` |
| `model_provider` | For an explicitly provider-hosted tool, require exactly one enabled, version-resolved model-provider selection identified by the binding and a `provided_by` link from this tool selection to that provider. Resolve the provider's `/settings/credential_ref`; confirm the tool is available through that provider/API | Known wrong provider or absent required reference: `fail`; unestablished execution location, API compatibility or ambiguous binding: `unknown` |
| `none` | Require an explicit unauthenticated choice supported by the selected operation and deployment | Known authentication requirement: `fail`; unknown auth requirements: `unknown` |

Absent binding, absent/empty auth metadata, or a mixed `none`/authenticated method list without an explicit choice is `unknown` with review required, never automatic `pass` or `skipped`. Conflicting local and inherited references must be resolved explicitly; neither silently overrides the other, even if their opaque strings match. No selected/enabled tool is the non-applicable (`skipped`) case. A supported alternative auth method is not a requirement to configure every method.

`rule.t4.tool.credential.ref` would apply only after the binding establishes `direct`; a companion resolution check must keep inherited, missing and ambiguous cases visible. A direct-only guard on a missing proposed field would skip under v1 `exists` semantics, so no such JSON guard is offered here. Proposed severity remains `error`, with `unknown` requiring review. A presence check is not credential validation, authorization, account entitlement or permission to execute. Scope union and least privilege remain #35/T3 review inputs, including the connection's actual granted permissions.

**Evidence and consumers:** secret handling is source-checked (unverified) under B27 (vault storage) and B40 (temporary role credentials); inheritance and outcome choices above are design hypotheses for #40, #35 and #13, not vendor claims. Read only reference metadata for research validation; never dereference secrets, copy secret values, or log them in findings, tests or evidence. Report selection IDs and missing/ambiguous source categories only.

**Synthetic acceptance cases for the future versioned contract (expected outcomes, not implemented resolver results):** direct + required reference passes the presence check; direct + missing reference fails. An explicitly bound GitHub integration with a reference and no tool-local copy passes the inherited presence check; a provider-hosted search tool uses its explicitly bound provider reference. A disabled/missing target fails; two competing bindings, a conflict between local and inherited references, absent auth metadata, or an unchosen mixed auth list require `unknown`/review. Explicit supported `none` is non-authenticated; no enabled tool is `skipped`. Passing any presence check does not assert that the credential is valid.

**Version/migration handoff:** #40 must choose the actual binding fields, link cardinality, per-selection evaluation mechanism and versioned resolver/ruleset semantics, with #35 authorization review and #13 connection-boundary review. Existing v1 builds must retain unresolved credential readiness; do not default legacy builds to `direct` or infer successful inheritance. Add versioned synthetic fixtures for every case above before a new contract/ruleset is adopted. No frozen schema, evaluator, catalog fact, price or secret is changed here.

#### Executable synthetic binding cases

The [test-only projection](../../tests/credential_binding_prototype.py) and
[cases](../../tests/test_credential_binding.py) exercise the proposed table above.
Inputs are a closed synthetic selection inventory and already-normalized,
eligible presence/support facts for an explicitly chosen authentication method.
An unknown choice represents absent, empty or ambiguous auth metadata; the
prototype does not parse a real method list, resolve a catalog or choose a method.
`None` means unknown fixture evidence, not a contract answer-state encoding.

Cases cover direct references, shared integration without a local copy,
provider-hosted binding, absent/disabled/wrong-kind/unlinked targets, unresolved
versions, unsupported versus unknown operation/auth support, competing bindings,
local/inherited conflicts and legacy builds with no binding. Multiple connections
do not become bindings automatically. A selected explicit target can disambiguate
unrelated available connections; duplicate target identities remain unknown.

Only booleans and synthetic selection IDs are inspected. No secret locator or
value is present, dereferenced, emitted or logged. Passing is the proposed metadata
readiness result, not credential validity, granted permissions, account entitlement
or permission to execute a tool. No source-use, guardrail or authorization gate
is satisfied by these cases. Frozen v1 and its historical behavior remain unchanged;
CD-6/CD-7 fields, real resolution and migration still require versioned review.

Run `python -m unittest discover -s tests -p test_credential_binding.py -v`.

### T4-B7 `rule.t4.tool.protocol.mcp-framework`: framework must support the tool's protocol

**2026-10-18 disposition: withdraw the universal framework prerequisite.**
The [follow-up source review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/318#pullrequestreview-5562844668)
reproduced this example blocking an MCP tool when a framework is absent or
disabled. It checks for a framework's presence, without establishing that the
tool uses that framework as its executor. [W-R3](../T0-configuration/workload-use-case.md#w-r3-actions-need-a-t4-component)
permits a tool or MCP component without a framework, and the [selection
experiment](../T0-configuration/component-schema-compatibility.md#cd-13-synthetic-selection-experiment-2026-10-18)
preserves the old framework requirement only as a historical counterexample.

- The original JSON below remains byte-for-byte historical evidence. It extends the old `rule.agent.mcp.framework` prerequisite to a primary tool whose protocol is `mcp`; do not publish it as a successor compatibility rule.
- Its original `error` severity and `on_unknown: block` behavior remain reproducible. B1's MCP definition and #25's framework capability evidence do not establish a universal requirement to select a framework.

```json
{"id":"rule.t4.tool.protocol.mcp-framework","severity":"error","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/protocol"}},"right":{"literal":"mcp"}}]},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"agent_framework","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"agent_framework","role":"primary","pointer":"/spec/supports_mcp"}},"right":{"literal":true}}]},"on_unknown":"block","message":"An MCP tool is selected but the framework does not support MCP.","remediation":"Choose an MCP-capable framework or a non-MCP variant of the tool.","affected_kinds":["tool","agent_framework","mcp_server"],"owner":"t4-research"}
```

**Current interface proposal for #40 review:** check the tool against its
explicitly selected executor. A framework capability check applies only after
the binding identifies that framework as the executor. Direct MCP-client and
provider-hosted paths require their own eligible protocol/provider evidence and
connection binding. A framework elsewhere in the build does not establish that
binding. Missing, ambiguous or unresolved bindings/capabilities remain unknown
for review; absence of a framework does not by itself establish tool readiness.
Known incompatibility must remain visible within the selected execution path.

- **Hypothesis; needs contract change via #40 with #25/#27:** tool interfaces, executor identity/binding and that executor's supported interfaces need a versioned representation. The earlier `spec_tool.interfaces` enum (`openai_function`, `anthropic_tool`, `mcp_tool`, `provider_server_tool`, `openapi`), `spec_agent_framework.tool_interfaces` and `spec_tool.requires_provider_ref` names are proposed concepts, not adopted v1 fields. Provider-hosted tools (including Anthropic `web_search` and OpenAI `code_interpreter`) retain their specific provider/API requirements.
- The former framework-only pseudocode below is retained verbatim. Its first assertion can apply only to an explicitly framework-bound tool; its provider assertion does not establish the binding, authentication or authorization. No new v1 guard, automatic direct-path pass or contract adoption is supplied here.

```text
assert: intersects(catalog tool /spec/interfaces, catalog agent_framework /spec/tool_interfaces)
assert (server tools): eq(catalog tool /spec/requires_provider_ref, selection model_provider /catalog_item_id)
```

### T4-B8 `rule.t4.tool.cost.metered` and `rule.t4.integration.cost.metered`: recurring cost (example 8)

- A metered tool or integration adds recurring usage cost. It needs a `cost_policy` selection so #39 includes its meter. This extends `rule.budget.monthly.cap`, which only acts once a complete quote exists.
- Severity: warning; `on_unknown: review`.
- **Source-checked (unverified)** for metered evidence (B7, B8, B29, B37); the policy is a hypothesis.
- Passing: a metered web search tool with a cost policy. Failing: a metered tool and no cost policy. Skipped: `billing_class` `free` or `included`.

```json
{"id":"rule.t4.tool.cost.metered","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/billing_class"}},"right":{"literal":"metered"}}]},"assert":{"op":"exists","value":{"ref":{"scope":"selection","kind":"cost_policy","role":"primary","pointer":"/id"}}},"on_unknown":"review","message":"A metered tool adds recurring usage cost but no cost policy is selected.","remediation":"Select a cost policy and include the tool's usage meter in the cost estimate.","affected_kinds":["tool","cost_policy"],"owner":"t4-research"}
```

```json
{"id":"rule.t4.integration.cost.metered","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"integration","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"integration","role":"primary","pointer":"/billing_class"}},"right":{"literal":"metered"}}]},"assert":{"op":"exists","value":{"ref":{"scope":"selection","kind":"cost_policy","role":"primary","pointer":"/id"}}},"on_unknown":"review","message":"A metered integration adds recurring cost but no cost policy is selected.","remediation":"Select a cost policy and include the integration's meter in the cost estimate.","affected_kinds":["integration","cost_policy"],"owner":"t4-research"}
```

### T4-B9 `rule.t4.tool.cost.unknown`: info when the cost basis is unknown

- Severity: info; `on_unknown: defer`. Many SaaS APIs publish no per-call price but sit behind a paid account (GitHub, Gmail, Stripe). **Source-checked (unverified)** (absence of published per-call prices in B10, B20, B24).

```json
{"id":"rule.t4.tool.cost.unknown","severity":"info","applies_when":{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},"assert":{"op":"ne","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/billing_class"}},"right":{"literal":"unknown"}},"on_unknown":"defer","message":"The tool's billing class is unknown, so its cost may be missing from the estimate.","remediation":"Confirm whether the tool or its upstream API is free, included or metered.","affected_kinds":["tool","cost_policy"],"owner":"t4-research"}
```

**Needs contract change via #40/#39:** "metered but no price in the pinned pricebook". The ruleset cannot see pricebooks today. It needs a metric `cost.unpriced_metered_count` (count of metered selections without a rate for their exact version). Severity: warning. **Hypothesis.**

```text
applies_when: gt(metric cost.unpriced_metered_count, 0)   # metric missing in v1 enum
assert: eq(metric cost.unpriced_metered_count, 0)
```

### T4-B10 `rule.t4.tool.network.exfiltration`: networked tool with sensitive data

- If a networked tool is used in a build with `objectives.data_classification` in `confidential` or `restricted`, the guardrail must include the `data_exfiltration` policy.
- Severity: warning; `on_unknown: review`. **Source-checked (unverified)** (B6 exfiltration warning; B1 security considerations).

```json
{"id":"rule.t4.tool.network.exfiltration","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/is_networked"}},"right":{"literal":true}},{"op":"in","left":{"ref":{"scope":"build","pointer":"/objectives/data_classification"}},"right":{"literal":["confidential","restricted"]}}]},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/policies"}},"right":{"literal":"data_exfiltration"}}]},"on_unknown":"review","message":"A networked tool runs in a build that handles confidential or restricted data without an exfiltration guardrail.","remediation":"Add a guardrail with a data_exfiltration policy, or restrict the tool's domains.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B11 `rule.t4.integration.rate-limit`: configured rate within provider limit

- Selection `/settings/rate_limit_per_minute` ≤ catalog `/spec/rate_limit_per_minute`.
- Severity: warning; `on_unknown: defer`. **Source-checked (unverified)** expression. Most providers do not publish a single per-minute number (B8, B10, B20, B24), so the rule will often be skipped.

```json
{"id":"rule.t4.integration.rate-limit","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"integration","role":"primary","pointer":"/settings/rate_limit_per_minute"}}},{"op":"exists","value":{"ref":{"scope":"catalog","kind":"integration","role":"primary","pointer":"/spec/rate_limit_per_minute"}}}]},"assert":{"op":"lte","left":{"ref":{"scope":"selection","kind":"integration","role":"primary","pointer":"/settings/rate_limit_per_minute"}},"right":{"ref":{"scope":"catalog","kind":"integration","role":"primary","pointer":"/spec/rate_limit_per_minute"}}},"on_unknown":"defer","message":"The configured integration rate exceeds the provider's documented limit.","remediation":"Lower rate_limit_per_minute to the provider limit or obtain a higher quota.","affected_kinds":["integration"],"owner":"t4-research"}
```

### Summary

| Rule | Severity | Status | Form |
| --- | --- | --- | --- |
| `rule.t4.tool.scopes.allowed` | error | Source-checked (unverified) (expression); policy hypothesis | json |
| `rule.t4.tool.scopes.least-privilege` | warning | Source-checked (unverified) | json |
| `rule.t4.tool.guardrail.targets` | error | Source-checked (unverified) | json |
| `rule.t4.tool.guardrail.enforcement` | warning | Hypothesis | json |
| `rule.t4.tool.irreversible.approval` | error / warning | Hypothesis | needs contract change |
| `rule.t4.tool.credential.ref` and source resolution | error | Hypothesis; secret-handling evidence source-checked (unverified) | needs contract change |
| `rule.t4.tool.protocol.mcp-framework` | error (historical) | Superseded universal prerequisite; retained for reproduction | historical json |
| tool interface / selected-executor rule | error (proposed) | Hypothesis; explicit executor binding and unresolved facts require review | needs contract change |
| `rule.t4.tool.cost.metered` | warning | Source-checked (unverified) evidence, policy hypothesis | json |
| `rule.t4.integration.cost.metered` | warning | Source-checked (unverified) evidence, policy hypothesis | json |
| `rule.t4.tool.cost.unknown` | info | Source-checked (unverified) | json |
| unpriced metered component | warning | Hypothesis | needs contract change |
| `rule.t4.tool.network.exfiltration` | warning | Source-checked (unverified) | json |
| `rule.t4.integration.rate-limit` | warning | Source-checked (unverified) | json |

## Pricing and capacity

**Structured:** [`pricing/proposals/t4b-anthropic-web-search.json`](../../pricing/proposals/t4b-anthropic-web-search.json).
- Meter: `request`.
- Unit price: USD `0.01`, converted from the published "$10 per 1,000 searches" (10 ÷ 1,000). The page states "All prices are in USD" (B7).
- Conditions: one search = one use regardless of results; errored searches not billed; token costs excluded.

**Units only (handed to #39), not priced here:**

| Item | Published unit | Why no pricebook |
| --- | --- | --- |
| Brave Search | $5.00 per 1,000 requests (= 0.005 per request); $5 monthly credit; Answers plan also per 1M tokens | Currency code not stated on the page (B8) |
| E2B | $0.000014 per vCPU-second, $0.0000045 per GiB-second; Pro $150/month; Enterprise min $3,000/month | No v1 meter for per-second CPU/RAM; currency code not stated (B29) |
| Anthropic code execution | 1,550 free hours per org per month, then $0.05 USD per hour per container, 5-minute minimum; free when used with web search/fetch 20260209+ | No v1 meter for container-hour; tool not proposed as an item |
| n8n Cloud | EUR per monthly workflow executions (Starter 2.5K, Pro 10K) | Plan price, not per-request; no list price per execution (B37) |
| OpenAI code interpreter | "built-in tools rates" | Values not extracted (B41) |
| GitHub, Slack, Gmail, Drive, Stripe API calls | no per-call price published | Do not assume API cost is covered by a subscription or seat. Drive has a future-charging notice (B44); Stripe refunds "might incur a fee" (B25) |

**Capacity facts for #38/#39:**
- Gmail quota units (100 per send).
- GitHub point budget (POST = 5 points).
- Stripe read allocation of 500 GET requests per transaction over 30 days, minimum 10,000/month (B24).
- E2B concurrency caps per plan.

These affect throughput and plan selection, not price per call.

## Recommendation and rationale

1. **Adopt the four-class risk taxonomy** with `irreversible` as the default for unclassified tools. Treat MCP annotations as untrusted hints (B1, B2).
2. **Model operation families, not providers, as tools.** Model providers as integrations. Scopes are coarser than risk (Slack `chat:write`, Gmail full scope).
3. **Default approvals.** `read_only` auto; `write` policy-allowlisted with audit; `high_impact` human approval by default; `irreversible` human approval always. Require an idempotency key for retries where the provider documents one (Stripe).
4. **Least privilege by default.**
   - GitHub fine-grained tokens limited to the needed repository permission.
   - Google `drive.file` for the applicable file workflow and `gmail.send` for sending. For message removal, prefer `messages.trash` with its documented `gmail.modify` option when that meets the user's need. Permanent deletion has a different mandatory scope and must be omitted when the policy rejects it; do not invent a narrower permission (B50/B51).
   - Stripe restricted, agent-tagged keys.
   - Postgres roles with only `SELECT` (or `pg_read_all_data`). Do not rely on `default_transaction_read_only`, which only sets the default for new transactions (B35).
   - AWS temporary role credentials and permissions boundaries.
5. **Prefer provider-hosted read tools** (web search/fetch) only when the model provider is fixed. They bind the tool to that provider.

## Structured artifacts

**Catalog proposals (all validate):**
- `catalog/proposals/t4b-anthropic-web-search.json`: `tool.anthropic.web-search`, read_only, metered
- `catalog/proposals/t4b-anthropic-web-fetch.json`: `tool.anthropic.web-fetch`, read_only, included
- `catalog/proposals/t4b-brave-web-search.json`: `tool.brave.web-search`, read_only, metered
- `catalog/proposals/t4b-github-issues-read.json`: `tool.github.issues-read`, read_only
- `catalog/proposals/t4b-github-issues-write.json`: `tool.github.issues-write`, mutating (`x_side_effect_class: write`)
- `catalog/proposals/t4b-github-rest-api.json`: `integration.github.rest-api`, `api`, `associated_tool_refs` the two GitHub tools
- `catalog/proposals/t4b-gmail-messages-send.json`: `tool.gmail.messages-send`, mutating (`irreversible`)
- `catalog/proposals/t4b-stripe-refunds-create.json`: `tool.stripe.refunds-create`, mutating (`irreversible`)
- `catalog/proposals/t4b-e2b-sandbox.json`: `tool.e2b.sandbox`, mutating (`high_impact`), metered
- `catalog/proposals/t4b-n8n-webhook.json`: `integration.n8n.webhook`, `webhook`

**Pricebook:** `pricing/proposals/t4b-anthropic-web-search.json`.

**Not proposed, with reasons:**
- Slack: the Web API has no upstream version string to pin.
- Google Drive: the original API-version/quota gap is supplemented by B44; no complete, reviewed catalog proposal was added by that quota readback.
- PostgreSQL: no v1 `protocol` value fits the Postgres wire protocol (`http`, `grpc`, `cli`, `embedded`, `mcp`).
- OpenAI code interpreter: price not extracted.

**Extension conventions used in proposals:**
- `x_side_effect_class`: `read_only | write | high_impact | irreversible | unknown`
- `x_operation_family`
- `x_open_world`
- `x_idempotency`

`required_scopes` for GitHub uses the project notation `issues:read` / `issues:write` for the fine-grained permission "Issues" (read/write). #40 should confirm the convention.

## Open questions and handoffs

| Question / handoff | Follow-up issue / owner |
| --- | --- |
| Add `spec_tool.side_effect_class` (4-value enum) with a consistency constraint to `side_effect`; metrics `tools.high_impact_count`, `tools.irreversible_count`; count integrations and MCP-exposed tools in mutating metrics | #40 · @tynamite |
| Add `provider_id` (shared with `data_source`), `category`, `interfaces[]`, `requires_provider_ref`, `input_schema_uri`/`output_schema_uri`, `data_access_scope`, `idempotency`, `open_world`, `operation_family` to `spec_tool` | #40 · @tynamite |
| T4-B6 credential binding and resolution: direct vs integration/provider-hosted vs none; exact active connection identity, link cardinality, ambiguous/missing outcomes, legacy migration and versioned synthetic fixtures; no inferred credential readiness in v1 | #40 · @tynamite; authorization #35; shared-connection boundary #13 |
| Auth enum: add `basic`, `jwt`, `personal_access_token` (or `bearer_token`); add `credential_kind` (restricted / unrestricted / temporary). `spec_mcp_server.auth_methods` lacks `service_account` | #40 · @tynamite; MCP side #27 |
| Rate limits: replace integer `rate_limit_per_minute` with `rate_limits[]` `{value, unit: per_second / per_minute / per_hour / quota_units / concurrent, scope: user / app / org / endpoint}` | #40 · @tynamite |
| Rule quantifier over all selections of a kind (baseline rules check only role `primary`) | #40 · @tynamite |
| Dependency graph: add `cost_policy depends_on tool`; add `tool` to `rule.budget.monthly.cap` `affected_kinds` | #40 · @tynamite; #39 · @PUSHINGSQUARES |
| Risk taxonomy, default approval matrix, operation-level (not scope-level) enforcement, provider-side approvals (Stripe agent keys) as satisfying controls, exfiltration policy for networked read tools; per-tool `approval_mode` in `settings_tool` or guardrail | handoff to #35 · @PUSHINGSQUARES |
| Pricing units: request (priced: Anthropic web search), per-second vCPU and GiB (E2B), per container-hour (Anthropic code execution), per workflow execution (n8n), plan minimums; new meters `cpu_second`, `gib_second`, `container_hour`, `execution`; metric `cost.unpriced_metered_count` | handoff to #39 · @PUSHINGSQUARES; meter enum #40 |
| MCP annotations trust: confirm that annotations count only for `trust_level` internal / trusted_external; tool naming collisions across servers | handoff to #27 · @CompleteDotTech |
| Framework support for OpenAI function schema / Anthropic tool use / MCP / provider server tools (`tool_interfaces`) | handoff to #25 · @CompleteDotTech |
| Shared provider identity and `provided_by` link between `data_source` and `integration`; union-of-scopes review when one OAuth client serves ingestion and actions | handoff to #13 · @zabyxc01 |
| Rate-limit and failure-mode signals (`Retry-After`, `x-ratelimit-*`, `Stripe-Rate-Limited-Reason`, in-band tool errors) for monitoring | handoff to #38 · @PUSHINGSQUARES |
| Evidence policy for summarising fetchers and pages that render tables in JavaScript (Slack tiers, GitHub permissions) | #41 · @tynamite |
| Remaining source decisions: exact Stripe refund-operation RAK resource mapping; E2B resolved dependency terms, applicable notice delivery and intended redistribution scope. B55 below records the exact wheel's bytes, metadata and internal inventory; it does not settle those remaining uses | #26 · @CompleteDotTech |

[Internal T4 interfaces are accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509). The final #26 assessment below records its three declared receiving interfaces; the [workstream matrix](README.md#dependency-and-handoff-matrix) retains the wider T4 scopes and follow-on decisions.


## Slack history rate-limit gap resolved (2026-10-18)

B42 — Slack, [conversations.history](https://docs.slack.dev/reference/methods/conversations.history/), mutable Web API method documentation, accessed **2026-10-18** with the browser text extractor. **Primary documentation, source checked / unverified**; no authenticated API request or measured throughput.

The previously unread B15 values are now visible: qualifying new commercially distributed non-Marketplace applications/installations from 2025-05-29 receive **1 request/minute**, with both default and maximum page size **15 objects**. Marketplace-approved and internal customer-built applications retain **Tier 3**. The current method page exempts existing installations of non-Marketplace applications from the newly posted limits. Preserve app distribution/approval and installation cohort; do not assign the restrictive rate to every external app or infer a particular customer's effective quota.

B43 — Slack, [Web API rate limits](https://docs.slack.dev/apis/web-api/rate-limits/), mutable guide, accessed **2026-10-18** through the same extractor; **Primary documentation, source checked / unverified**. The formerly unread B16 table describes Tier 3 as **50+ requests/minute**, scoped by method, workspace and app. Pagination is a condition of published tiers; omitting it can tighten limits. Burst ceilings are unpublished. Rate-limit responses use HTTP **429**, with `Retry-After` in seconds; unrelated methods/workspaces are not automatically paused.

Project interpretation for #38: retain those dimensions when grouping throttling events and retry queues. Unknown cohort remains unknown; an advertised tier is neither observed throughput nor guaranteed latency. Do not flatten all Slack methods into v1's integration-level `rate_limit_per_minute`. This resolves the two historical unread-table gaps only; other B15/B16 historical access conditions remain recorded, #40 owns richer rate-limit fields and #38 receiving acceptance remains pending. Source access grants no customer-content or publication rights.

## Drive quota gap resolved (2026-10-18)

B44 — Google, [Drive API usage limits](https://developers.google.com/workspace/drive/api/guides/limits), mutable v3 documentation, accessed **2026-10-18** with the browser text extractor. **Primary documentation, source checked / unverified**; no API request or billing observation.

The guide applies new quotas to projects created from **2026-05-01**; projects using Drive during November 2025–April 2026 retain previous quotas. Published new limits are **1,000,000 quota units/minute/project** and **325,000/minute/user/project**. Representative costs: `files.get` **5**, `files.list` **100**, `files.download` **200**, `files.update` **50** units. These are not request counts. Rate errors include **403** and **429**; use truncated exponential backoff with jitter and bounded retries.

The page separately lists a **1 TB/day/project** egress threshold and **400,000,000 units/day/project** billing threshold. Standard use is currently described as no additional cost; over-quota charging is planned later in 2026, with details and notice still forthcoming on this read. No rate or effective bill is established.

Project interpretation: #38 needs project/user/method/cohort dimensions; #39 needs an actual effective price schedule before pricing quota units. Keep billing classification unknown pending that scoped determination. v1's request-per-minute field cannot faithfully represent this model. Customer-specific quotas, authorization and receiving dispositions remain unverified; B22's historical unfetched state is preserved.

## Remaining named source-gap readbacks (2026-10-18)

All sources below were opened on **2026-10-18** with the browser text extractor (GitHub API resolved the E2B commit). Grade: **Primary documentation, source checked / unverified**. This is desk research: no authenticated product request, credential creation, execution benchmark or redistribution approval.

### Brave rate windows

B45 — Brave, [Rate limiting](https://api-dashboard.search.brave.com/documentation/guides/rate-limiting), mutable guide. The guide documents a one-second sliding request window and HTTP 429 on excess. `X-RateLimit-Limit`, `X-RateLimit-Policy`, `X-RateLimit-Remaining` and `X-RateLimit-Reset` carry multiple windows; reset values are seconds from the response, not Unix timestamps. The example values are illustrative plan data, not a universal quota. Brave states successful responses count toward quota/billing; this does not establish a monetary rate or independently reproduce enforcement. For #38, preserve all corresponding window values and plan scope when deciding retry delay; do not retry merely because the shortest window reset if another is exhausted. This resolves the previously unread header semantics; account-specific limits remain unknown.

### GitHub operation permissions

B46 — GitHub, [Repository contents](https://docs.github.com/en/rest/repos/contents?apiVersion=2026-03-10), REST API **2026-03-10** documentation. Private content reads require fine-grained **Contents: read**; public content may be read without authentication. Creating/updating file contents requires **Contents: write**, with **Workflows: write** additionally for workflow changes. These are operation/resource permissions, not generic OAuth scope strings.

B47 — GitHub, [Delete a repository](https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#delete-a-repository), same API version. Fine-grained deletion requires **Administration: write**; organizational deletion policy can still deny a member. Project implication: a content writer must not be treated as a repository administrator or deletion-authorized actor. These published prerequisites do not prove a particular token's effective access and do not relax repository protections or tool approval rules.

### Stripe permission naming boundary

B48 — Stripe, [Restricted API keys](https://docs.stripe.com/keys/restricted-api-keys), mutable documentation. Resource permissions are **None**, **Read** or **Write**; Write includes Read. The guide's named examples are **Payment Intents: Write**, **Customers: Read** and **Disputes: Read**. GET maps to reading and POST/DELETE to writing the relevant resource. It does not establish the exact resource/dependency permission set for this note's refund-creation operation. That mapping stays unknown pending an explicit applicable reference or authorized sandbox evidence; do not substitute a Stripe Apps manifest permission or a broad unrestricted key. No key was created and no refund attempted.

### E2B package-local license scope

B49 — E2B source at commit `62a17dfc3f11439d1d06bfb9bb515eadc5adfcd3`: the package-local [Python SDK LICENSE](https://raw.githubusercontent.com/e2b-dev/E2B/62a17dfc3f11439d1d06bfb9bb515eadc5adfcd3/packages/python-sdk/LICENSE) declares MIT; adjacent [pyproject.toml](https://raw.githubusercontent.com/e2b-dev/E2B/62a17dfc3f11439d1d06bfb9bb515eadc5adfcd3/packages/python-sdk/pyproject.toml) declares package `e2b` version **2.56.0** and MIT. This supplies the missing package-local source evidence behind B31, rather than applying the root repository license to every subpackage. B33's historical root-file observation remains recorded. No wheel or dependency bundle was inspected; this finding does not decide terms for hosted sandboxes, infrastructure, dependencies, user workloads or a redistributed artifact. #60 retains publication-scope review.

## Permission and operation-boundary correction (2026-10-18)

The B50–B53 primary pages were opened on **2026-10-18** with the web text extractor; B54 was read through the GitHub connector at its pinned source revision. Their findings are **Primary documentation, source checked / unverified**. No account token, message operation, credential inspection or runtime enforcement test was performed. Original B13/B14/B21 capture dates remain historical.

| ID | Primary source and version | Bounded finding |
| --- | --- | --- |
| B50 | Google, [users.messages.delete](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/delete), Gmail API v1; page updated 2026-04-15 | Permanent deletion requires `https://mail.google.com/`; the method is irreversible and Google recommends the trash operation instead. No narrower permission is listed for permanent deletion. |
| B51 | Google, [users.messages.trash](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/trash), Gmail API v1; page updated 2026-04-15 | Moving a message to trash permits either full-mail scope or `https://www.googleapis.com/auth/gmail.modify`. This source does not establish that a particular credential has either scope. |
| B52 | Slack, [chat.postMessage](https://docs.slack.dev/reference/methods/chat.postMessage/), mutable Web API method page | Both documented bot and user token forms require `chat:write` to post. A scope prerequisite does not identify the application operation that the caller intended to authorize. |
| B53 | Slack, [chat.delete](https://docs.slack.dev/reference/methods/chat.delete/), mutable Web API method page | The same scope permits deletion subject to actor permissions: a bot can delete its own messages, and a user token is limited by that user's deletion rights. |
| B54 | MCP, [ToolAnnotations in the 2026-07-28 schema](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/1155ca460e5097019f32769b38dcba194432e2fb/schema/2026-07-28/schema.ts), pinned commit `1155ca460e5097019f32769b38dcba194432e2fb`; read 2026-10-18 through GitHub's raw-file connector | Hints separately describe environment modification, additive/destructive updates, repeat-call effects and open/closed interaction domains. The schema does not equate these properties with the project's four risk classes. Destructive/idempotent hints apply only to non-read-only tools. |

**Project decision for the research interface:** use the narrowest permission the provider actually supports for the selected operation. Prefer trash when it meets the removal requirement. If permanent deletion is required, show its full-mail permission and irreversible approval requirement together; if that permission is unacceptable, omit the operation. Approval cannot manufacture a narrower OAuth scope, and possession of the scope is not approval for every operation it enables.

The earlier blanket instruction to never use full-mail scope contradicted the permanent-delete candidate and is superseded by this explicit choice. The taxonomy continues to classify operation families, with the actual enforced invocation boundary determining which operations are reachable. A shared connection is compatible with different family approvals only while the caller cannot bypass the operation/resource restrictions or extract the credential. Unknown enforcement stays unknown and uses the conservative approval default. The later independent criterion audit found that the old MCP-equivalence column also conflated reversibility, additive updates, repeat-call effects and interaction domains; B54 supports the corrected independent-property treatment. These are proposed control requirements for #35/#40, not evidence that v1 or any selected product implements them.

## Criterion and receiving-interface audit (2026-10-18)

**Recorded checkpoint.** The audit below preceded [#318's delivered revision](https://github.com/Pick-Your-AI/pick-your-ai-research/commit/e4ef6b6246a35cb91c2630a498a889b3931f6085) and the [final bounded research receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/26#issuecomment-6249459395). Its remaining-merge wording and ten-proposal count describe that earlier checkpoint. The subsequent T4-B7 disposition above supersedes the universal framework proposal while retaining its original JSON. This follow-up supplies no additional receiving acceptance or frozen-contract implementation.

This audit preserves the nine literal research acceptance criteria from [#26](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/26). It separates completion of this bounded research deliverable from adoption of a versioned ruleset, production integration and completion of its consumers. The final assessment includes the actual forward MCP receipt and a present review of the delivered cost-coverage corrections. The remaining delivery gate is independent review and merge of the B54 correction; the issue's final receipt must identify that delivered revision before closure is reported complete.

| ID | Acceptance criterion (unchanged) | Artifact or receipt and its scope |
| --- | --- | --- |
| 26.1 | Tool metadata schema | `tool`/`integration` mapping, minimum metadata and typed comparison fields above; eight tool and two integration proposals under `catalog/proposals/t4b-*.json`. Missing v1 concepts remain explicit note-only proposals. |
| 26.2 | Side-effect / risk classification handed to #35 | Four classes and operation-level approval defaults above. [PUSHINGSQUARES's receiving response](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6240050930) accepts those inputs, and [appletechie confirms the risk-class row](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6245652021). The dated scope/enforcement correction sharpens that boundary without claiming an implemented control. |
| 26.3 | Decision record merged at `research/T4-agents-integrations/tools-apis.md` following the research method | Original record delivered in [#70](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/70), with later evidence, credential and source-gap corrections retained. [#307](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/307) delivered the permission/criterion audit at `250537e10c674e8d6ba19eb08921fda15511a23b` after [independent source review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/307#pullrequestreview-5562632506). This final MCP-hint correction still needs its reviewed merge. |
| 26.4 | Candidate set covers the relevant deployment modes (API / managed / self-hosted) or states why a mode does not apply | Sixteen candidate rows cover provider-hosted tools, managed APIs and self-hosted backends. The deployment section now explicitly preserves the accepted serving-component definition of build mode. |
| 26.5 | Comparison fields defined with type, unit, and evidence requirement | Comparison-field table supplies identifiers, versions, authentication, permission strings, scoped rate dimensions, risk, failures, pricing and provenance. Unsupported quota or currency conversions remain unknown/note-only. |
| 26.6 | Compatibility rules and warnings use the shared format from #40; verified rules are separated from hypotheses | Ten v1-shaped JSON proposals retain applicability, assertions, severity, missing-input handling, evidence and remediation; policy hypotheses and required contract changes are separate. The withdrawn credential rule remains withdrawn. No independently verified joint product rule is claimed. |
| 26.7 | Every factual or numeric claim cites a primary source with access date (and version / region / currency where relevant) | B1–B41 retain the original 2026-10-16 observations; B42–B54 carry separately dated readbacks. Candidate/pricing tables link their evidence and retain platform, unit, currency and missing-source limits. B54 corrects the identified MCP-hint conflation. The single pricebook keeps its own dated, version-bound USD request rate. This is a citation/claim-scope assessment, not a blanket recheck of every source or a measured capability claim. |
| 26.8 | Each handoff listed under Dependencies is confirmed by the consuming issue's owner (link the comment or PR review) | Research interface criterion satisfied: all three declared consumers (#27, #35 and #39) have actual scoped receiving decisions below; the two #39 coverage objections are resolved by the inspected #229 delivery. No reverse-direction receipt, absent co-owner concurrence or future runtime adoption is inferred. |
| 26.9 | Open questions recorded with a named follow-up owner | The open-questions table names #35/#38/#39/#40/#41 and source-specific owners. Incomplete Stripe refund RAK mapping and E2B distribution terms stay unknown. Follow-on contract, runtime and source-use decisions are not relabelled completed. |

### Declared downstream interfaces

| Direction | Required research interface | Existing evidence and final-review boundary |
| --- | --- | --- |
| #26 → #27 MCP Servers | Operation-level tool identities and risk classes; annotations are review inputs rather than authority; a server's tool mapping needs sourced identities | [CompleteDotTech's actual forward receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/27#issuecomment-6248971927), as a current #27 assignee under delegated engineering authority, accepts this interface at `dd3f300289ff6c692785b09badd527796a16b1a7` with invocation-boundary, annotation and missing-`tool_refs`/runtime constraints. B54 corrects the independent hint properties within that same annotation-review boundary. This receipt speaks for its actual reviewer, not tynamite. The [older internal receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509) remains **#27 → #26** only for this pair. |
| #26 → #35 Guardrails | Risk classes, approval defaults, operation-level enforcement, credential and exfiltration boundaries | [PUSHINGSQUARES](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6240050930) accepts the risk/default input; [appletechie](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6245652021) confirms that row. Their MCP-description, memory-deletion and configured-key follow-ups retain their separate scopes. The dated permission correction is included in this continuation's independent review. |
| #26 → #39 Cost Estimate | Preserve published billing units and unknown costs; link the dated tool pricebook with its conditions; route unsupported meters and the tool dependency edge through #40 | The same two actual owners accept the units/unknown-cost principles. [Merged #229](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/229) and its [independent review](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/229#pullrequestreview-5561523442) supply the requested #70/#72 links and four explicit memory-cost omissions in [the receiving cost record](../T6-deployment-operations/cost-estimate.md#t4-cost-coverage-follow-up-2026-10-18-partial-research). The present independent criterion audit inspected that delivered section, including hosted/OSS distinctions and platform/version/date/quantity/token conditions, and found both stated coverage objections fulfilled. This is a new assessment of delivered conditions, not a claim that the earlier owners approved a later revision. No current vendor rate, scenario total or complete #39 is inferred. |

The wider T4 handoff matrix also tracks #13 shared provider identity, #38 telemetry and #40/#41 governance. These remain at their named owners for the scoped follow-on work. In particular, the [#40 queue receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6242626523) accepts proposed work for central review; it is not permission to edit frozen v1. The [#41 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6242626857) preserves claim-level evidence, dated current-state observations and source-specific rights. Neither contract implementation nor a universal API integration approval is an additional research criterion for #26.

## E2B distribution-artifact readback (2026-10-18)

**B55 — Primary publisher artifact and package metadata, source checked / unverified.** On **2026-10-18**, the versioned [PyPI metadata for `e2b` 2.56.0](https://pypi.org/pypi/e2b/2.56.0/json) and its exact [Python wheel](https://files.pythonhosted.org/packages/58/ec/17bee489c285b555a83a3360da1e4eeedaf7c5c767de4038cf9503104faa/e2b-2.56.0-py3-none-any.whl) were fetched over public HTTPS. The [external-artifact manifest](../../evidence/t4-e2b-2560-wheel.json) retains the stable locator and digest; the wheel is not committed. This supplements B49's earlier source-only check with an inspection of actual distribution bytes. No package installation, dependency resolution, SDK execution or hosted sandbox request was performed.

| Field | Published or locally observed value | Basis and limit |
| --- | --- | --- |
| Artifact | `e2b-2.56.0-py3-none-any.whl`, **400,291 bytes** | Locally downloaded byte count matches the versioned PyPI file metadata |
| SHA-256 | `acfb77c56a33daf1542362cab8048f062b578dffe7a48f32f87a4a3e0bef1e14` | Locally calculated digest matches PyPI; this is artifact identity, not independent product verification |
| Published upload time | `2026-10-13T15:01:53.831164Z` | PyPI's file metadata; the access date remains 2026-10-18 |
| Embedded package metadata | `Metadata-Version: 2.4`, `Name: e2b`, `Version: 2.56.0`, `Requires-Python: >=3.11`, `License-Expression: MIT` | Read from `e2b-2.56.0.dist-info/METADATA`; declarations do not prove runtime compatibility or legal scope for other materials |
| Embedded metadata SHA-256 | `3c5750a022682587e48967666c8868bc561594897f2f6ec708a56db17bcc9ea2` | Digest of the exact uncompressed `METADATA` bytes |
| ZIP inventory | **285** unique entries: **245** regular files and **40** directories | Local archive inspection; no duplicate member names |
| `RECORD` inventory | **245** unique rows cover exactly the **245** regular files | All **244** populated SHA-256/base64url digest and byte-size pairs match the corresponding members; the `RECORD` self-row has empty digest and size |
| License-file observations | No `License-File` header; no regular member basename containing `LICENSE`, `LICENCE`, `NOTICE` or `COPYING`, case-insensitively | An exact metadata/filename observation, not a claim that the software has no license or that redistribution is forbidden |

**Method and reproducibility.** Download the manifest's exact URI, compare its SHA-256 and byte count with the versioned PyPI metadata, then inspect it as a ZIP without importing its code. Read `METADATA` and CSV `RECORD`, reject duplicate paths, compare the full regular-file set with the record paths, and recompute each listed member's SHA-256 using unpadded URL-safe base64 plus its uncompressed byte length. The only unhashed row observed was `RECORD` itself. The [PyPA wheel specification](https://packaging.python.org/en/latest/specifications/binary-distribution-format/#the-dist-info-directory), checked 2026-10-18, supplies the format reference. These checks establish internal consistency of the inspected bytes; they do not authenticate a build process or assess package behavior.

The embedded `Requires-Dist` fields declare the following **12 direct dependency ranges**, copied here as an inventory rather than a resolved environment:

```text
python-dateutil>=2.8.2
wcmatch>=10.1,<12
protobuf-py>=0.1.1,<0.2
httpx>=0.27.0,<1.0.0
h2>=4.4.1,<5
attrs>=23.2.0
packaging>=24.1
typing-extensions>=4.10.0
rich>=14.0.0
connectrpc>=0.11.1,<0.12
pyqwest>=0.12.0,<0.13
e2b-dockerfile-utils>=0.1.0,<0.2
```

**Source and intended-use boundary.** B49's package-local [MIT license at source commit `62a17dfc3f11439d1d06bfb9bb515eadc5adfcd3`](https://github.com/e2b-dev/E2B/blob/62a17dfc3f11439d1d06bfb9bb515eadc5adfcd3/packages/python-sdk/LICENSE) was re-read on 2026-10-18 (Git blob `4aa6529d102d71d5410904a4331efeb8bac3e968`). It identifies FOUNDRYLABS, INC. and requires the copyright and permission notices to accompany copies or substantial portions. Agreement between the source-package version and wheel metadata does not establish that this wheel was built from that commit; no build-source attestation was examined. The metadata declaration and filename search do not determine notice coverage under every packaging or distribution arrangement.

The exact-wheel inspection gap is now narrowed to the observations above. **#26 · @CompleteDotTech** retains the source-specific follow-up: identify the actual target environment and resolved dependency artifacts, review their applicable terms and notice delivery, and assess the precise intended redistribution use under #41's evidence/intake policy. No dependency version, transitive closure, hosted-service/workload term or redistribution permission is inferred from the SDK's MIT declaration. The completed [#60 ten-source market audit](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60) keeps its own accepted scope; this readback neither extends that audit to E2B nor reopens it. The original B33/B49 observations and the nine #26 acceptance criteria remain historical evidence and unchanged criteria, respectively.
