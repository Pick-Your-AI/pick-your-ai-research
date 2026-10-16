# T4: Tools & APIs

Issue: #26 · Contract: 1.0.0 · Kinds: `tool`, `integration`
Status: draft · Last researched: 2026-10-16

## User decision

Which external actions and data APIs can the agent call, and with what permissions, risks and costs?

This note defines the metadata every tool entry needs, a side-effect and risk classification, which tools need approval by default, and how tool and API usage feeds cost. It does not enumerate APIs. It verifies 13 representative candidates from primary documentation to test the schema.

**Out of scope:** MCP transport and server packaging (#27), and knowledge ingestion connectors (#13). MCP *tool annotations* are used here only as evidence for risk classification.

### Deployment modes

A tool's deployment mode decides where the call executes, where egress happens, and who holds the credential. It does not decide whether the tool exists.

| Mode | What runs where | Examples verified here | Consequence for the builder |
| --- | --- | --- | --- |
| **API (provider-hosted server tool)** | The model provider executes the tool inside its own API; the application has no handler code (B4) | Anthropic web search and web fetch (B5, B6); OpenAI code interpreter (B41) | Uses the model provider's credential and billing. Only available when the model is called through that provider's API. Egress happens from the provider, not the user's network |
| **Managed SaaS API** | The application or agent runtime calls a vendor REST API with its own credential | GitHub, Slack, Gmail, Google Drive, Stripe, Brave Search, E2B Cloud, n8n Cloud | Needs a `credential_ref`, outbound network from the agent runtime, and the vendor's rate limits and pricing |
| **Self-hosted** | The tool's backend runs on user infrastructure | PostgreSQL (B34, B35), E2B infra (B32), n8n Community/Business (B37, B38) | The user owns patching, network policy and capacity. Licence terms apply (n8n is not OSI-licensed, B38). Can work in a network-restricted deployment |

`is_networked` (v1) covers only part of this. v1 cannot express "executes on the model provider" or "requires a specific model provider". See contract gaps.

## Candidate options

### Runtime tool category taxonomy (reusable)

Proposed values for a future `category` field (now `/tags` by convention). Categories describe *what the tool touches*. The risk class (next section) describes *what it changes*. A category does not imply a risk class.

| Category id | Covers | Typical default risk class | Verified example in this note |
| --- | --- | --- | --- |
| `http_request` | Generic HTTP/API request tools where the target is configured or model-chosen | write (unknown target) | — (n8n HTTP-style flows, by reference) |
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
| 3 | Brave web search (`/res/v1/web/search`) | Brave (SaaS) | API key in `X-Subscription-Token` | none | Search plan 50 QPS | read_only, open world | not verified (rate-limit page failed to load) | per request: "$5.00 per 1,000 requests", $5 monthly credit; currency code not stated | B8, B9 |
| 4 | GitHub issues read | GitHub (SaaS) | fine-grained PAT | "Issues" repository permission (read); none for public repos | 5,000 req/h authenticated; 60 req/h unauthenticated; secondary 100 concurrent, 900 points/min (GET = 1 point) | read_only | 403/429 with `x-ratelimit-remaining: 0`; wait for `x-ratelimit-reset` or `retry-after`; repeated violation "may result in the banning of your integration" | none published for REST calls (unknown) | B10, B11 |
| 5 | GitHub issues write (create) | GitHub (SaaS) | fine-grained PAT | "Issues" repository permission (write) | as above, plus 80 content-creating req/min and 500/h; POST/PATCH = 5 points | write | as above | unknown | B10, B11 |
| 6 | Slack `chat.postMessage` | Slack (SaaS) | OAuth v2 bot or user token | `chat:write` | "Special": about 1 message/s per channel, several hundred/min per workspace | high_impact (visible to others at once) | `ratelimited` with `Retry-After`; `rate_limited` (too many posts) | none published per call (unknown) | B13, B18 |
| 7 | Slack `chat.delete` | Slack (SaaS) | OAuth v2 bot or user token | **`chat:write` (same scope as posting)**; a bot token can delete only its own messages | Tier 3 (50+/min) | irreversible (project classification) | `ratelimited` + `Retry-After` | unknown | B14 |
| 8 | Slack `conversations.history` | Slack (SaaS) | OAuth v2 bot or user token | `channels:history`, `groups:history`, `im:history` or `mpim:history` | Tier 3 (50+/min); new limits since 2025-05-29 for newly created, commercially distributed non-Marketplace apps (values not rendered) | read_only (private data) | HTTP 429 + `Retry-After` (B17, 2018 changelog) | unknown | B15, B16, B17 |
| 9 | Gmail `messages.send` | Google (SaaS) | OAuth 2.0 | `gmail.send` (Sensitive) | 100 quota units per call; 6,000 units/user/min; 1,200,000 units/project/min | irreversible (project classification) | quota errors; truncated exponential backoff advised | none published per call (unknown) | B19, B20 |
| 10 | Gmail `messages.delete` vs `messages.trash` | Google (SaaS) | OAuth 2.0 | `delete` needs `https://mail.google.com/` (Restricted); `trash` is reversible | delete 10 units; trash 20 units | delete = irreversible ("cannot be undone. Prefer messages.trash"); trash = write | as above | unknown | B20, B21 |
| 11 | Google Drive files | Google (SaaS) | OAuth 2.0 | `drive.file` (Non-sensitive, per-file) recommended over `drive` / `drive.readonly` (Restricted) | not fetched | read_only or write by scope | not fetched | unknown | B22 |
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
2. Model the provider connection once as an `integration` (`integration.github.rest-api`). It holds the endpoint, credential and rate limit, and lists its families in `associated_tool_refs`.
3. Guardrails (#35) can then allow the read family automatically and gate the write family, even though the provider issues one token.
4. Scope checks alone cannot separate families that share a scope (Slack `chat:write`). The guardrail must enforce by **operation**, not only by scope (handoff to #35).

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
3. **Selections link them.** A `data_source` selection has a build link `relation: "provided_by"` to the integration selection (`provided_by` exists in v1 build links). The build then holds one provider identity and one `credential_ref`.
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
| Supported framework interfaces (OpenAI function JSON Schema, Anthropic tool use, MCP tool, provider server tool) | `/spec/protocol` covers transport only (`mcp` is a value) | **note only**; propose `interfaces[]` |
| Input / output contract (JSON Schema) | — | **note only**; MCP requires `inputSchema` and allows `outputSchema` (B1); OpenAI `parameters` (B3); Anthropic `input_schema` (B4) |
| Auth method | `/spec/auth_methods` (tool, integration) | partial: no `basic`, `jwt` or personal access token values |
| OAuth scopes / permissions | `/spec/required_scopes` (tool); `/settings/allowed_scopes` (selection) | expressible as strings; no scope sensitivity (Google: Non-sensitive / Sensitive / Restricted, B19, B22) |
| Credential handling | `/settings/credential_ref` (`secret://…`) on tool and integration | expressible; key type (restricted vs unrestricted) is note only |
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

All entries accessed on 2026-10-16. Grades follow the interim policy in `docs/RESEARCH_METHOD.md`. Fetched with WebFetch (a summarising fetcher) or with curl for raw files and package registries. WebFetch summaries were checked against quoted text where possible.

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

| Class | Definition | Examples (verified) | Maps to v1 `side_effect` | MCP hint equivalent | Default approval | Least-privilege requirement |
| --- | --- | --- | --- | --- | --- | --- |
| `read_only` | No state change in any system. It may still read private data or reach the open web | GitHub list issues; Slack `conversations.history`; web search/fetch; Postgres SELECT under a read-only role | `read_only` | `readOnlyHint: true` | none (auto) | read-only permission level (GitHub "read", `drive.file` or `drive.readonly`); read-only DB role, not just a read-only transaction |
| `write` | Changes state in the caller's own resources, additive or reversible by another API call | GitHub create issue; Gmail `messages.trash` | `mutating` | `readOnlyHint: false`, `destructiveHint: false` | policy allowlist + audit log; no per-call human approval | narrowest write permission (GitHub "Issues: write" only) |
| `high_impact` | Reversible in principle, but with immediate effects on other people, shared spaces, spend or infrastructure | Slack `chat.postMessage` (seen at once by others); E2B sandbox (arbitrary code, per-second spend, egress); cloud resource changes | `mutating` | `readOnlyHint: false`, `openWorldHint: true` | **human approval by default** (guardrail `escalate`), which may be relaxed per tool by policy | dedicated credential; domain and egress allowlist; spend cap |
| `irreversible` | Cannot be undone through any API once executed | Gmail `messages.delete` ("cannot be undone"); Gmail `messages.send`; Stripe refund (cancel only briefly, Dashboard only); Slack `chat.delete` | `mutating` | `destructiveHint: true`, `idempotentHint: false` | **human approval always**; dry-run or preview; idempotency key where available | separate credential per family; restricted keys (Stripe RAK, agent-tagged keys with approval rules, B27); never the broad scope (`https://mail.google.com/`) |

**Classification rules:**
1. Classify by the *worst* operation reachable with the item's granted scopes, not by its name. A tool holding `chat:write` can delete its own messages (B14).
2. Unknown classifies as `irreversible` until reviewed. This mirrors the MCP defaults.
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
- **Verified:** the assertion is supported by cited primary text, and the expression uses only v1 fields.
- **Hypothesis:** policy judgement or contract change needed.

All JSON rules below validate against `ruleset.schema.json`. They were also run with `contracts/v1/reference/evaluate.py` against the synthetic fixture build (`contracts/v1/examples/`). Outcomes there: pass for scopes, guardrail and MCP rules; fail for `credential.ref` (the fixture has no `credential_ref`); skipped for the cost and exfiltration rules.

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
- Version impact: none (v1 fields only). **Verified** (expression); the policy semantics are a hypothesis for #35.

```json
{"id":"rule.t4.tool.scopes.allowed","severity":"error","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"exists","value":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}}}]},"assert":{"op":"subset_of","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}},"right":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/settings/allowed_scopes"}}},"on_unknown":"review","message":"The tool needs permission scopes that this build does not allow.","remediation":"Grant the missing scopes in allowed_scopes after policy review, or choose a narrower tool operation family.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B2 `rule.t4.tool.scopes.least-privilege`: over-granted scopes

- Pointers as T4-B1, reversed: `allowed_scopes subset_of required_scopes`.
- Evidence: Google advises "the most narrowly focused scope possible" (B19). AWS says to "grant only the permissions required to perform a task" (B40).
- Severity: warning; `on_unknown: review`.
- Passing: allowed `["gmail.send"]` = required. Failing: allowed `["https://mail.google.com/"]` for a send-only tool. Skipped/unknown: no `allowed_scopes`.
- **Verified.**

```json
{"id":"rule.t4.tool.scopes.least-privilege","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/settings/allowed_scopes"}}},{"op":"exists","value":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}}}]},"assert":{"op":"subset_of","left":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/settings/allowed_scopes"}},"right":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/required_scopes"}}},"on_unknown":"review","message":"The build allows scopes this tool does not need.","remediation":"Remove scopes from allowed_scopes that are not in the tool's required_scopes.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B3 `rule.t4.tool.guardrail.targets`: refines `rule.tool.mutation.guardrails`

- When `tools.mutating_count > 0`, the primary guardrail's `/spec/targets` must contain `tool`.
- Evidence: MCP says applications SHOULD provide confirmation and a human able to deny invocations (B1).
- Severity: error; `on_unknown: block` (same as the baseline).
- Passing: targets `["input","tool"]`. Failing: targets `["output"]` with a `tool_permissions` policy. Unknown: no metric (catalog item missing).
- **Verified** (expression); policy owned by #35.

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

### T4-B6 `rule.t4.tool.credential.ref`: credential must be a secret reference

- If `auth_methods` exists and does not contain `none`, the tool selection must have `/settings/credential_ref` (`secret://…`, never the credential).
- Severity: error; `on_unknown: review`.
- **Verified.** Evidence: Stripe "Store sensitive keys in a secrets vault" (B27); AWS prefers temporary role credentials (B40).
- The key *type* (restricted vs unrestricted, temporary vs long-term) needs a contract field (`credential_kind`). Note only.

```json
{"id":"rule.t4.tool.credential.ref","severity":"error","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"exists","value":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/auth_methods"}}},{"op":"not","arg":{"op":"contains","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/auth_methods"}},"right":{"literal":"none"}}}]},"assert":{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/settings/credential_ref"}}},"on_unknown":"review","message":"The tool needs credentials but no secret reference is configured.","remediation":"Set credential_ref to a secret:// reference for a least-privilege credential.","affected_kinds":["tool"],"owner":"t4-research"}
```

### T4-B7 `rule.t4.tool.protocol.mcp-framework`: framework must support the tool's protocol

- Expressible today for MCP only. It extends `rule.agent.mcp.framework`, which triggers only when an `mcp_server` is selected, to tools whose `protocol` is `mcp`.
- Severity: error; `on_unknown: block`. **Verified** (B1 defines MCP tools; the framework capability comes from #25).

```json
{"id":"rule.t4.tool.protocol.mcp-framework","severity":"error","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/protocol"}},"right":{"literal":"mcp"}}]},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"agent_framework","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"agent_framework","role":"primary","pointer":"/spec/supports_mcp"}},"right":{"literal":true}}]},"on_unknown":"block","message":"An MCP tool is selected but the framework does not support MCP.","remediation":"Choose an MCP-capable framework or a non-MCP variant of the tool.","affected_kinds":["tool","agent_framework","mcp_server"],"owner":"t4-research"}
```

**Needs contract change via #40:** a general interface rule. Provider-hosted server tools (Anthropic `web_search`, OpenAI `code_interpreter`) also require a specific model provider.
- Missing fields: `spec_tool.interfaces` (enum `openai_function`, `anthropic_tool`, `mcp_tool`, `provider_server_tool`, `openapi`), `spec_agent_framework.tool_interfaces`, and `spec_tool.requires_provider_ref`.
- **Hypothesis.**

```text
assert: intersects(catalog tool /spec/interfaces, catalog agent_framework /spec/tool_interfaces)
assert (server tools): eq(catalog tool /spec/requires_provider_ref, selection model_provider /catalog_item_id)
```

### T4-B8 `rule.t4.tool.cost.metered` and `rule.t4.integration.cost.metered`: recurring cost (example 8)

- A metered tool or integration adds recurring usage cost. It needs a `cost_policy` selection so #39 includes its meter. This extends `rule.budget.monthly.cap`, which only acts once a complete quote exists.
- Severity: warning; `on_unknown: review`.
- **Verified** for metered evidence (B7, B8, B29, B37); the policy is a hypothesis.
- Passing: a metered web search tool with a cost policy. Failing: a metered tool and no cost policy. Skipped: `billing_class` `free` or `included`.

```json
{"id":"rule.t4.tool.cost.metered","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/billing_class"}},"right":{"literal":"metered"}}]},"assert":{"op":"exists","value":{"ref":{"scope":"selection","kind":"cost_policy","role":"primary","pointer":"/id"}}},"on_unknown":"review","message":"A metered tool adds recurring usage cost but no cost policy is selected.","remediation":"Select a cost policy and include the tool's usage meter in the cost estimate.","affected_kinds":["tool","cost_policy"],"owner":"t4-research"}
```

```json
{"id":"rule.t4.integration.cost.metered","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"integration","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"integration","role":"primary","pointer":"/billing_class"}},"right":{"literal":"metered"}}]},"assert":{"op":"exists","value":{"ref":{"scope":"selection","kind":"cost_policy","role":"primary","pointer":"/id"}}},"on_unknown":"review","message":"A metered integration adds recurring cost but no cost policy is selected.","remediation":"Select a cost policy and include the integration's meter in the cost estimate.","affected_kinds":["integration","cost_policy"],"owner":"t4-research"}
```

### T4-B9 `rule.t4.tool.cost.unknown`: info when the cost basis is unknown

- Severity: info; `on_unknown: defer`. Many SaaS APIs publish no per-call price but sit behind a paid account (GitHub, Gmail, Stripe). **Verified** (absence of published per-call prices in B10, B20, B24).

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
- Severity: warning; `on_unknown: review`. **Verified** (B6 exfiltration warning; B1 security considerations).

```json
{"id":"rule.t4.tool.network.exfiltration","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"tool","role":"primary","pointer":"/id"}}},{"op":"eq","left":{"ref":{"scope":"catalog","kind":"tool","role":"primary","pointer":"/spec/is_networked"}},"right":{"literal":true}},{"op":"in","left":{"ref":{"scope":"build","pointer":"/objectives/data_classification"}},"right":{"literal":["confidential","restricted"]}}]},"assert":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"guardrail","role":"primary","pointer":"/id"}}},{"op":"contains","left":{"ref":{"scope":"catalog","kind":"guardrail","role":"primary","pointer":"/spec/policies"}},"right":{"literal":"data_exfiltration"}}]},"on_unknown":"review","message":"A networked tool runs in a build that handles confidential or restricted data without an exfiltration guardrail.","remediation":"Add a guardrail with a data_exfiltration policy, or restrict the tool's domains.","affected_kinds":["tool","guardrail"],"owner":"t4-research"}
```

### T4-B11 `rule.t4.integration.rate-limit`: configured rate within provider limit

- Selection `/settings/rate_limit_per_minute` ≤ catalog `/spec/rate_limit_per_minute`.
- Severity: warning; `on_unknown: defer`. **Verified** expression. Most providers do not publish a single per-minute number (B8, B10, B20, B24), so the rule will often be skipped.

```json
{"id":"rule.t4.integration.rate-limit","severity":"warning","applies_when":{"op":"all","args":[{"op":"exists","value":{"ref":{"scope":"selection","kind":"integration","role":"primary","pointer":"/settings/rate_limit_per_minute"}}},{"op":"exists","value":{"ref":{"scope":"catalog","kind":"integration","role":"primary","pointer":"/spec/rate_limit_per_minute"}}}]},"assert":{"op":"lte","left":{"ref":{"scope":"selection","kind":"integration","role":"primary","pointer":"/settings/rate_limit_per_minute"}},"right":{"ref":{"scope":"catalog","kind":"integration","role":"primary","pointer":"/spec/rate_limit_per_minute"}}},"on_unknown":"defer","message":"The configured integration rate exceeds the provider's documented limit.","remediation":"Lower rate_limit_per_minute to the provider limit or obtain a higher quota.","affected_kinds":["integration"],"owner":"t4-research"}
```

### Summary

| Rule | Severity | Status | Form |
| --- | --- | --- | --- |
| `rule.t4.tool.scopes.allowed` | error | Verified (expression); policy hypothesis | json |
| `rule.t4.tool.scopes.least-privilege` | warning | Verified | json |
| `rule.t4.tool.guardrail.targets` | error | Verified | json |
| `rule.t4.tool.guardrail.enforcement` | warning | Hypothesis | json |
| `rule.t4.tool.irreversible.approval` | error / warning | Hypothesis | needs contract change |
| `rule.t4.tool.credential.ref` | error | Verified | json |
| `rule.t4.tool.protocol.mcp-framework` | error | Verified | json |
| tool interface / provider-hosted tool rule | error | Hypothesis | needs contract change |
| `rule.t4.tool.cost.metered` | warning | Verified evidence, policy hypothesis | json |
| `rule.t4.integration.cost.metered` | warning | Verified evidence, policy hypothesis | json |
| `rule.t4.tool.cost.unknown` | info | Verified | json |
| unpriced metered component | warning | Hypothesis | needs contract change |
| `rule.t4.tool.network.exfiltration` | warning | Verified | json |
| `rule.t4.integration.rate-limit` | warning | Verified | json |

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
| GitHub, Slack, Gmail, Drive, Stripe API calls | no per-call price published | Cost is in the subscription or seat; Stripe refunds "might incur a fee" (B25) |

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
   - Google `drive.file` / `gmail.send` rather than Restricted scopes.
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
- Google Drive: API version and quotas not fetched.
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
| Re-fetch: Slack current tier table and non-Marketplace limits; Brave rate-limit headers; GitHub repository permissions (Contents, Administration, repo delete); Stripe RAK permission names; Drive quotas; E2B SDK licence conflict (MIT vs Apache-2.0) | #26 · @CompleteDotTech |

None of the handoffs above is confirmed yet.
