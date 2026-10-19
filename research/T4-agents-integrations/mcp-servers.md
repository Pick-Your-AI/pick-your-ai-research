# T4: MCP Servers

Issue: #27 · Contract: 1.0.0 · Kinds: `mcp_server`
Status: research completion assessment below; versioned contract adoption and selected-build qualification remain separate · Reconciled: 2026-10-18

## Evidence status correction

Evidence metadata corrected at 2026-10-17T02:17:46Z under the [adopted #41 interim policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Checked primary documentation, publisher package metadata, registry entries and source inspection are not independent verification. These catalog claims remain `unverified`; the original facts, versions, source access dates and `checked_at` are unchanged. The original catalog claims were not independently reproduced. The later SDK and Cloudflare observations retain their separately dated, narrower scope. Vendor capability statements remain documented claims, not measurements.

A proposed constraint may pass on eligible, versioned documentation while its evidence remains unverified. Missing eligible evidence remains unknown; absence from an unmarked capability list does not establish lack of support. Synthetic evaluator results check rule mechanics only and do not verify product behaviour. All rules and contract changes still require central versioned review through #40. The original evidence correction did not itself satisfy issue completion; the present criterion assessment and actual receiving decisions are recorded below.

`trusted_external` is a project research classification under the criteria in this note, with the [current #35 receiving interpretation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6251677799); versioned rule adoption remains with #40. Registry presence and namespace/package identity checks do not certify security, safe code, benign tools or independently verified behaviour. The catalog value is not a security certification or permission to waive a required control.

The separately dated [Cloudflare documentation-server observation](cloudflare-docs-mcp.md)
adds actual public-endpoint discovery/listing and one documentation search to the
earlier desk study and local SDK experiments. It does not upgrade the original
catalog claims or establish other vendor endpoints, framework clients or adoption.

## User decision

Which Model Context Protocol (MCP) servers can supply tools and context to the selected agent framework or client, and how is each one hosted, authenticated and trusted?

The builder has to answer three joint questions for every selected server:

1. **Can the client talk to it?** Protocol revision (era), transport and the client capabilities the server needs.
2. **Can the deployment reach and authorize it?** Local subprocess or remote endpoint, who hosts it, and whether the required authorization flow can run in the chosen deployment mode.
3. **How far should it be trusted?** Who publishes it, how identity is source-checked, and what its tools can change.

Deployment modes covered (the v1 `spec_deployment_mode.mode` enum is `api`, `managed`, `self_hosted`, `hybrid`): MCP placement does not set the build's serving mode. The [accepted #3 operator/capacity position](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927) and [#40 isolation disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6242626523) require per-component placement and actual connection evidence. The following taxonomy covers MCP use alongside each serving mode; it does not qualify every client/server combination.

| Packaging | What runs where | Applicability across serving modes | Evidence and limits |
| --- | --- | --- | --- |
| **Local stdio** | The selected MCP client launches the server and owns its standard streams (C10, C70) | Can accompany `api`, `managed`, `self_hosted` or `hybrid` serving when that client has the required launch, stream and lifecycle path | Credentials come from the environment, not the HTTP MCP authorization flow (C12, C66). Using a model API does not identify the MCP client's execution locality |
| **Self-hosted remote** (Streamable HTTP) | The organisation runs the server on its own hosting platform | Can accompany any serving mode; assess the separate MCP runtime and network path | Reuse an eligible #9 host identity for the actual placement. Cloud, on-premises, edge and colocation are placement possibilities, not proof that a corresponding catalog record or configured service exists |
| **Vendor-hosted remote** (Streamable HTTP) | The API vendor runs the endpoint (GitHub, Stripe, Sentry, Atlassian; C25, C27–C29) | Can accompany any serving mode, subject to the selected endpoint's reachability and authorization | Check the actual route and isolation boundary. Vendor operation alone proves neither public egress nor private containment; do not infer mode, trust or availability from `managed_api` |
| **Provider-hosted connector** | The model provider calls the remote server from its own infrastructure (OpenAI `HostedMCPTool`, C56, C69) | Applies when that provider/API interface is selected; other serving components keep their own modes | A custom server URL must be reachable by the provider. Direct subprocess stdio is outside this documented interface; a separately introduced intermediary requires its own transport and authorization assessment |

Out of scope: the general tool catalog (#26) and framework selection (#25). Facts about frameworks below are limited to what was needed to ground the rule shapes.

## Candidate options

### Protocol baseline (what the catalog must track)

Published revisions (C1, C2): `2024-11-05`, `2025-03-26`, `2025-06-18`, `2025-11-25`, and **`2026-07-28` (Current)**, plus a `draft`. Earlier dated revisions are Final.

| Revision | Era | Transports defined | Main changes relevant to the catalog | Evidence |
| --- | --- | --- | --- | --- |
| 2024-11-05 | legacy | stdio, HTTP+SSE | Base protocol, `initialize` handshake | C2, C9 |
| 2025-03-26 | legacy | stdio, Streamable HTTP (HTTP+SSE deprecated) | OAuth 2.1 authorization framework; tool annotations; `completions` capability; JSON-RPC batching (removed again in 2025-06-18) | C6 |
| 2025-06-18 | legacy | same | MCP servers are OAuth resource servers with RFC 9728 protected resource metadata; clients MUST use RFC 8707 resource indicators; elicitation; structured tool output; `MCP-Protocol-Version` header; batching removed | C5 |
| 2025-11-25 | legacy | same | Client ID Metadata Documents (CIMD) recommended; OpenID Connect discovery; incremental scope consent; URL-mode elicitation; experimental tasks; tool icons; tool naming guidance | C4 |
| **2026-07-28** | **modern** | stdio, Streamable HTTP (redefined) | **Stateless**: `initialize` removed, version and client capabilities in every request's `_meta`; mandatory `server/discover`; no protocol sessions (`Mcp-Session-Id` removed); server-to-client requests replaced by Multi Round-Trip Requests; `subscriptions/listen`; tasks moved to an extension; Roots, Sampling, Logging and Dynamic Client Registration **Deprecated** | C3, C7, C11 |

**Era compatibility (C7, source-checked).** The spec defines "modern" (2026-07-28 and later), "legacy" (2025-11-25 and earlier) and "dual-era" implementations:

| Client | Server | Outcome |
| --- | --- | --- |
| Modern | Modern | Works |
| Modern | Legacy | **Fails** |
| Dual-era | Modern or legacy | Works (stdio: probe with `server/discover`, fall back to `initialize`; HTTP: inspect the 400 body, then fall back, possibly to HTTP+SSE) |
| Legacy | Modern | **Fails** (no fall-forward) |
| Legacy | Dual-era or legacy | Works |

**Dated implementation observations (source-checked SDK artifacts, C31, C32; later C60–C65):**
- The TypeScript SDK `@modelcontextprotocol/sdk` 1.32.1 (2026-10-05) sets `LATEST_PROTOCOL_VERSION = '2025-11-25'` and supports 2024-10-07 to 2025-11-25. A separate module declares `DRAFT-2026-v1`.
- The Python SDK `mcp` 1.30.0 supports 2024-11-05 to 2025-11-25 only. The 2026-10-18 pinned follow-up now inspects `mcp` 2.3.0 and its exact dependency `mcp-types==2.3.0`: the registry lists four handshake revisions (`2024-11-05`, `2025-03-26`, `2025-06-18`, `2025-11-25`) and one modern revision (`2026-07-28`). C60–C65 and the [local SDK observation](#pinned-python-sdk-protocol-follow-up-2026-10-18) replace the earlier uninspected-registry uncertainty; they do not establish the protocol set of any selected vendor server.
- The reference servers pin the legacy SDK lines: `mcp-server-fetch` and `mcp-server-git` require `mcp<2,>=1.29.0`, and `server-filesystem`/`server-everything` 1.0.0 require `@modelcontextprotocol/sdk ^1.31.0` (C36, C38, C39, C41).

**Research consequence:** record a protocol-version field. A modern-only client cannot use a server known to be legacy-only (C7); the inspected packages do not establish what proportion of the ecosystem is legacy. "Supports MCP" (the v1 boolean) is not enough to predict compatibility. The Python 2.3.0 follow-up supplies modern and fallback evidence only for its pinned implementation and observed tuples.

**Transports.**
- `stdio`: client-launched subprocess, newline-delimited JSON-RPC (C10).
- `streamable_http`: one POST endpoint. In 2026-07-28 it requires the `MCP-Protocol-Version`, `Mcp-Method` and `Mcp-Name` headers, and drops sessions, the GET stream and resumability (C9). Revisions 2025-03-26 to 2025-11-25 used a different shape (sessions, GET stream, `Last-Event-ID`), so `streamable_http` alone does not determine compatibility; the protocol version must accompany it.
- `sse` (HTTP+SSE, 2024-11-05): Deprecated. The earliest removal is three months after SEP-2596 reaches Final (C11). Registry docs say to publish an `sse` remote "only to support existing clients" (C23).
- Custom transports are allowed and SHOULD reuse stdio framing (C8).

**Capabilities (C16, schema 2026-07-28).**
- Server: `tools{listChanged}`, `resources{subscribe,listChanged}`, `prompts{listChanged}`, `completions`, `logging` (Deprecated), `extensions`, `experimental`.
- Client: `roots` (Deprecated), `sampling{context,tools}` (Deprecated), `elicitation{form,url}`, `extensions`, `experimental`.
- A server can reject a request with `MissingRequiredClientCapabilityError` (-32021) when a capability it needs was not declared.
- Official extensions: Tasks (`io.modelcontextprotocol/tasks`), MCP Apps (`io.modelcontextprotocol/ui`), Skills over MCP, plus auth extensions (C7, C18, C19).

**Tool annotations (C16).** `title`, `readOnlyHint` (default false), `destructiveHint` (default true), `idempotentHint` (default false), `openWorldHint` (default true). Clients **MUST** consider annotations untrusted unless they come from trusted servers (C15, C18).

**Authorization (C12, C13).**
- Optional. HTTP transports SHOULD conform. stdio SHOULD NOT and "instead retrieve credentials from the environment".
- MCP servers are OAuth 2.1 resource servers and MUST publish RFC 9728 protected resource metadata. Clients MUST send the RFC 8707 `resource` parameter. Servers MUST validate the token audience.
- Servers "MUST NOT accept or transit any other tokens" (no token passthrough). Clients MUST validate `iss` (RFC 9207) when it is present.
- Client registration priority: pre-registration, then CIMD, then Dynamic Client Registration (Deprecated in 2026-07-28), then manual entry.
- Machine-to-machine and enterprise IdP cases are covered only by the opt-in extensions OAuth Client Credentials and Enterprise-Managed Authorization (C19).

### Representative servers

Status flags: reference servers are "not production-ready" (C33). Fifteen former reference servers are archived (GitHub, GitLab, PostgreSQL, Puppeteer, Redis, Sentry, Slack, SQLite, Brave Search and others), several of them replaced by vendor servers (C33).

| Server (proposed id) | Maintainer | Version (date) | License | Transports | Hosting | Auth | Capabilities exposed | Registry name (status) | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mcp_server.github-remote` | GitHub | 2.0.2 (2026-10-08) | MIT (code) | streamable_http | vendor-hosted (`api.githubcopilot.com/mcp/`; ghe.com variant; not GHES) | OAuth (host must configure a GitHub/OAuth App) or PAT bearer | tools (toolsets, read-only mode, insiders) | `io.github.github/github-mcp-server` (active) | C25, C42–C44 |
| `mcp_server.github-local` | GitHub | 2.0.2 | MIT | stdio (OCI image, Go binary) | local | OAuth browser login (token in memory) or `GITHUB_PERSONAL_ACCESS_TOKEN`; GitHub App for non-interactive | tools; `--read-only` | same entry, `packages[0]` | C25, C42, C43 |
| `mcp_server.playwright` | Microsoft | 0.0.83 npm (2026-09-28); registry lists 0.0.82 | Apache-2.0 | stdio (default); HTTP at `/mcp` with `--port` | local or self-hosted | none documented; binds localhost by default | tools (browser automation) | `io.github.microsoft/playwright-mcp` (active) | C26, C45–C47 |
| `mcp_server.stripe-remote` | Stripe | 0.2.4 (registry, 2025-10-28) | n/a (hosted) | streamable_http | vendor-hosted `mcp.stripe.com` | OAuth or agent API key bearer; untagged restricted and full secret keys rejected from December 2026 | tools including generic `stripe_api_write`; human confirmation for some writes | `com.stripe/mcp` (active) | C27, C48 |
| `mcp_server.sentry-remote` | Sentry | 0.42.0 (2026-09-25) | FSL-1.1-ALv2 (source) | streamable_http (remote); stdio npm `@sentry/mcp-server` | vendor-hosted `mcp.sentry.dev/mcp`; stdio for self-hosted Sentry | MCP OAuth (`Bearer`) or forwarded `Sentry-Bearer` token; stdio uses `SENTRY_ACCESS_TOKEN` with write scopes | tools ("skills" groups); AI search tools call an external LLM provider | `io.github.getsentry/sentry-mcp` (active) | C28, C50–C52 |
| `mcp_server.atlassian-remote` | Atlassian | 2.0.0 (2026-09-09) | n/a (hosted) | streamable_http (two endpoints, v2 and v1/authv2) | vendor-hosted `mcp.atlassian.com` | OAuth 2.1 primary, API token optional | tools for Jira, JSM, Confluence, Bitbucket, Goals, Projects, Loom; respects user permissions; consumes Rovo credits | `com.atlassian/atlassian-mcp-server` (active) | C29, C49 |
| `mcp_server.dbhub` (database) | Bytebase | 1.5.0 (2026-10-09) | MIT | stdio; HTTP via `--transport http` | local or self-hosted | none for MCP; DB credentials in DSN | tools `execute_sql`, `search_objects`, opt-in `explain_sql`, `health_check`, custom SQL tools; read-only mode | npm `mcpName` `io.github.bytebase/dbhub` (registry not checked) | C53–C55 |
| `mcp_server.reference-fetch` | MCP steering group | 2026.10.10 (2026-10-11) | PyPI: MIT; repository in MIT to Apache-2.0 transition | stdio | local | none | tools (annotated read-only, open-world), prompts | not found in registry search | C33, C34, C37, C38 |
| `mcp_server.reference-filesystem` | MCP steering group | 1.0.0 (2026-10-11) | "SEE LICENSE IN LICENSE" (mixed MIT/Apache-2.0) | stdio | local | none | tools; **requires client Roots or CLI args** | `mcpName` set but exact-name lookup returned 404 | C30, C35, C36 |
| reference `git` (note only) | MCP steering group | 2026.10.10 | MIT (PyPI, README) | stdio | local | none | tools | not checked | C39 |
| reference `memory` (note only) | MCP steering group | 1.0.0 | MIT (README) | stdio | local | none | tools (mutating), resources with update notifications | not checked | C40 |
| reference `everything` (note only, test server) | MCP steering group | 1.0.0 | mixed | stdio, HTTP+SSE, Streamable HTTP | local | none | prompts, tools, resources, sampling | not checked | C41 |

`everything` shows the v1 single-transport gap: one artifact speaks all three transports.

### Discovery channels and identity

- **Official MCP Registry** (registry.modelcontextprotocol.io) is **in preview**: "Breaking changes or data resets may occur before general availability" (C20).
  - It hosts metadata only (`server.json`) and delegates security scanning to package registries and downstream aggregators.
  - It is intended for aggregators, not direct host consumption. It does not support private servers. Organisations should run their own registry implementing the OpenAPI spec.
- **Namespace verification** (C21):
  - `io.github.<user|org>/*` needs GitHub login.
  - Reverse-DNS names (`com.example/*`) need a DNS TXT record or an HTTP `/.well-known/mcp-registry-auth` proof.
- **Package ownership** (C22):
  - npm: `mcpName` in `package.json`.
  - PyPI, NuGet, Cargo: an `mcp-name:` string in the README.
  - OCI: the `io.modelcontextprotocol.server.name` label.
  - MCPB: `fileSha256`, which the registry does not validate; clients do.
- **Versions** (C24): a published version is immutable, and version ranges are prohibited. Each entry carries `_meta.io.modelcontextprotocol.registry/official.status` (`active` observed) and `isLatest` (C25).
- **What the registry does not prove:** that the remote URL belongs to the namespace owner, that code is safe, or that the tools are benign.
  - A registry search for "github" returned third-party proxy entries (for example `ai.smithery/smithery-ai-github`, routed via `server.smithery.ai` with a Smithery bearer key) next to GitHub's own entry (C25).
  - A search for `server-filesystem` returned only `io.github.bytedance/mcp-server-filesystem` (a different publisher's server with a similar name) while the reference server's own `mcpName` was not found (C30).
- **Other channels seen:** vendor docs pages (Stripe, Atlassian, Sentry), the modelcontextprotocol/servers README (now pointing to the registry), host connector directories (the Claude directory and ChatGPT plugins are linked from Stripe docs, C48), and third-party marketplaces (Smithery). None of these was evaluated for curation quality.

## Comparison fields

The issue's conceptual fields map to v1 as follows. Most do not exist in v1.

| Field / JSON pointer | Type and unit | Candidate finding | Evidence ID | Conditions / unknowns |
| --- | --- | --- | --- | --- |
| server id → `/id` | string, `mcp_server.<slug>` | one item per transport packaging (see Structured artifacts) | — | v1 workaround; see #40 proposals |
| `/version` | string, exact upstream version (registry `server.json` version, package version, or release tag) | e.g. 2.0.2, 0.0.83 | C25–C29 | Registry and package versions can differ (Playwright 0.0.82 vs 0.0.83). Hosted remotes change without a version bump |
| `/status` | enum active/preview/deprecated/retired | all proposed items `active` | C25–C29 | Registry status `active` observed; deprecated or deleted values not observed |
| transports → `/spec/transport` | **single** enum `stdio`, `streamable_http`, `sse` | see table | C9–C11 | Cannot hold multiple transports. `sse` names the Deprecated HTTP+SSE transport. `streamable_http` does not say which revision shape |
| protocol version (note only) | array of `YYYY-MM-DD` revision strings, plus derived era `legacy`/`modern`/`dual` | mostly unknown per server; SDK-derived legacy for reference servers | C7, C31, C32 | **No v1 field.** Evidence requirement: `server/discover` output, the `initialize` result, or SDK version pin, with date |
| capabilities exposed (note only) | set of `tools`, `resources`, `prompts`, `completions`, `logging`, extension ids | see table | C16 | **No v1 field.** `tool_refs` only links catalog `tool` items |
| required client capabilities (note only) | set of `roots`, `sampling`, `elicitation.form`, `elicitation.url`, extension ids | filesystem needs roots or args; everything uses sampling | C35, C41 | **No v1 field** |
| auth method → `/spec/auth_methods` | array enum `none`, `api_key`, `oauth2`, `mTLS` | oauth2 + api_key for vendor remotes | C42, C48–C50 | Cannot say MCP OAuth (resource server) vs upstream OAuth; registration method (pre-registered, CIMD, DCR); client-credentials extension; required scopes |
| trust → `/spec/trust_level` | enum `internal`, `trusted_external`, `untrusted_external` | trusted_external for vendor and steering-group servers | criteria below | A project judgement, not a vendor fact. Must cite the criteria version |
| hosting local/remote (note only) | enum proposal `local_process`, `self_hosted_remote`, `vendor_hosted_remote` | see table | C10, C25–C29 | **No v1 field.** `transport` is a weak proxy |
| maintainer (note only) | string plus registry namespace | see table | C21, C25 | v1 has no maintainer or publisher field; `provenance` holds sources only |
| source → `/provenance` | array of {source_uri, checked_at, verification_status, notes} | registry entry, README, LICENSE | — | Required per claim |
| `/license` | {spdx_id, commercial_use_allowed, self_hosting_allowed} | MIT, Apache-2.0; Sentry FSL-1.1-ALv2 | C43, C47, C51, C55 | Not meaningful for hosted endpoints (ToS governs) |
| registry name (note only) | string, reverse-DNS `namespace/name` | see table | C21 | **No v1 field.** Needed for identity checks and impersonation detection |
| package pin (note only) | {registry_type, identifier, version or digest, sha256} | OCI tag `ghcr.io/github/github-mcp-server:2.0.2`; MCPB `fileSha256` | C22, C25 | **No v1 field.** Lifecycle risk below |
| `/settings/endpoint` (selection) | uri | remote URL | C25–C29 | Must not carry tokens (C12 forbids tokens in query strings) |
| `/settings/credential_ref` (selection) | `secret://` reference | — | — | One credential only; no OAuth client or registration fields |
| `/settings/read_only` (selection) | boolean | user intent | C42 (GitHub `--read-only`) | Only meaningful if the server enforces it; v1 has no `supports_read_only_mode` |

## Evidence

Original sources C1–C59 were accessed 2026-10-16. The separately dated C60–C65 SDK follow-up, C66–C71 authorization/locality follow-up and C72–C73 Sentry policy review were accessed 2026-10-18. These rechecks do not refresh unrelated original observations.
- Pages on modelcontextprotocol.io, github.com, docs and vendor sites were read with a fetch tool that returns extracted Markdown, so quotations are as extracted.
- JSON APIs (MCP Registry, npm, PyPI) and raw.githubusercontent.com files were read directly.
- The original 2026-10-16 desk study executed no MCP server or SDK. The separate 2026-10-18 experiment below executes pinned SDKs against local synthetic peers only.

| ID | Publisher and URL | Access date | Version / region | Evidence grade | Limitations / reuse terms |
| --- | --- | --- | --- | --- | --- |
| C1 | MCP, https://modelcontextprotocol.io/specification/versioning | 2026-10-16 | current = 2026-07-28 | Primary documentation | — |
| C2 | MCP, https://modelcontextprotocol.io/llms.txt | 2026-10-16 | lists 2024-11-05 … 2026-07-28, draft | Primary documentation | Index page |
| C3 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/changelog.md | 2026-10-16 | 2026-07-28 | Primary documentation | — |
| C4 | MCP, https://modelcontextprotocol.io/specification/2025-11-25/changelog.md | 2026-10-16 | 2025-11-25 | Primary documentation | — |
| C5 | MCP, https://modelcontextprotocol.io/specification/2025-06-18/changelog.md | 2026-10-16 | 2025-06-18 | Primary documentation | — |
| C6 | MCP, https://modelcontextprotocol.io/specification/2025-03-26/changelog.md | 2026-10-16 | 2025-03-26 | Primary documentation | — |
| C7 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning.md | 2026-10-16 | 2026-07-28 | Primary documentation | Era compatibility matrix |
| C8 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/index.md | 2026-10-16 | 2026-07-28 | Primary documentation | — |
| C9 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http.md | 2026-10-16 | 2026-07-28 | Primary documentation | Includes HTTP+SSE back-compat guidance |
| C10 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio.md | 2026-10-16 | 2026-07-28 | Primary documentation | — |
| C11 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/deprecated.md | 2026-10-16 | 2026-07-28 | Primary documentation | Removal dates are eligibility, not commitment |
| C12 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index.md | 2026-10-16 | 2026-07-28 | Primary documentation | — |
| C13 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration.md | 2026-10-16 | 2026-07-28 | Primary documentation | — |
| C14 | MCP, https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices.md | 2026-10-16 | 2026-07-28 | Primary documentation | Session hijacking for legacy versions is on the 2025-11-25 page (not fetched) |
| C15 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/server/tools.md | 2026-10-16 | 2026-07-28 | Primary documentation | — |
| C16 | MCP, https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/schema/2026-07-28/schema.ts | 2026-10-16 | main branch | Primary documentation | Normative schema per C18 |
| C17 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation.md | 2026-10-16 | 2026-07-28 | Primary documentation | URL mode marked as a new feature that may change |
| C18 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/index.md | 2026-10-16 | 2026-07-28 | Primary documentation | Security principles are non-normative lowercase "must" |
| C19 | MCP, https://modelcontextprotocol.io/extensions/auth/overview.md | 2026-10-16 | ext-auth drafts | Primary documentation | Extension specs live in `draft` |
| C20 | MCP Registry, https://modelcontextprotocol.io/registry/about.md | 2026-10-16 | preview | Primary documentation | — |
| C21 | MCP Registry, https://modelcontextprotocol.io/registry/authentication.md | 2026-10-16 | preview | Primary documentation | — |
| C22 | MCP Registry, https://modelcontextprotocol.io/registry/package-types.md | 2026-10-16 | server.schema 2025-12-11 | Primary documentation | — |
| C23 | MCP Registry, https://modelcontextprotocol.io/registry/remote-servers.md | 2026-10-16 | preview | Primary documentation | — |
| C24 | MCP Registry, https://modelcontextprotocol.io/registry/versioning.md | 2026-10-16 | preview | Primary documentation | — |
| C25 | MCP Registry API, https://registry.modelcontextprotocol.io/v0.1/servers/io.github.github%2Fgithub-mcp-server/versions/latest (and `?search=github`) | 2026-10-16 | 2.0.2 | Primary documentation | Publisher-supplied metadata; preview registry |
| C26 | MCP Registry API, https://registry.modelcontextprotocol.io/v0.1/servers/io.github.microsoft%2Fplaywright-mcp/versions/latest | 2026-10-16 | 0.0.82 | Primary documentation | Lags npm |
| C27 | MCP Registry API, https://registry.modelcontextprotocol.io/v0.1/servers/com.stripe%2Fmcp/versions/latest | 2026-10-16 | 0.2.4 | Primary documentation | — |
| C28 | MCP Registry API, https://registry.modelcontextprotocol.io/v0.1/servers/io.github.getsentry%2Fsentry-mcp/versions/latest | 2026-10-16 | 0.42.0 | Primary documentation | — |
| C29 | MCP Registry API, https://registry.modelcontextprotocol.io/v0.1/servers/com.atlassian%2Fatlassian-mcp-server/versions/latest | 2026-10-16 | 2.0.0 | Primary documentation | — |
| C30 | MCP Registry API, https://registry.modelcontextprotocol.io/v0.1/servers?search=server-filesystem | 2026-10-16 | — | Primary documentation | Exact-name lookup of `io.github.modelcontextprotocol/server-filesystem` returned 404. Search for `server-everything` timed out |
| C31 | npm, https://registry.npmjs.org/@modelcontextprotocol/sdk/-/sdk-1.32.1.tgz | 2026-10-16 | 1.32.1 (2026-10-05), MIT | Primary documentation | Constants read from `dist/esm` without running code |
| C32 | PyPI, https://pypi.org/pypi/mcp/json (wheels 2.3.0 and 1.30.0) | 2026-10-16 | 2.3.0 (2026-10-02); 1.30.0 (2026-09-07) | Primary documentation | 2.3.0 version list is in package `mcp_types`, not inspected |
| C33 | MCP, https://github.com/modelcontextprotocol/servers/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| C34 | MCP, https://github.com/modelcontextprotocol/servers/blob/main/LICENSE | 2026-10-16 | main | Primary documentation | MIT to Apache-2.0 transition; per-contribution licence varies |
| C35 | MCP, https://github.com/modelcontextprotocol/servers/blob/main/src/filesystem/README.md | 2026-10-16 | main | Primary documentation | — |
| C36 | npm, https://registry.npmjs.org/@modelcontextprotocol/server-filesystem | 2026-10-16 | 1.0.0 (2026-10-11) | Primary documentation | — |
| C37 | MCP, https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/README.md | 2026-10-16 | main | Primary documentation | — |
| C38 | PyPI, https://pypi.org/pypi/mcp-server-fetch/json | 2026-10-16 | 2026.10.10 | Primary documentation | — |
| C39 | MCP, https://github.com/modelcontextprotocol/servers/blob/main/src/git/README.md and https://pypi.org/pypi/mcp-server-git/json | 2026-10-16 | 2026.10.10 | Primary documentation | Tool list not extracted |
| C40 | MCP, https://github.com/modelcontextprotocol/servers/blob/main/src/memory/README.md and https://registry.npmjs.org/@modelcontextprotocol/server-memory | 2026-10-16 | 1.0.0 | Primary documentation | — |
| C41 | MCP, https://github.com/modelcontextprotocol/servers/blob/main/src/everything/README.md and https://registry.npmjs.org/@modelcontextprotocol/server-everything | 2026-10-16 | 1.0.0 | Primary documentation | Test server |
| C42 | GitHub, https://github.com/github/github-mcp-server/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| C43 | GitHub, https://github.com/github/github-mcp-server/blob/main/LICENSE | 2026-10-16 | main | Primary documentation | MIT |
| C44 | GitHub, https://github.com/github/github-mcp-server/releases/tag/v2.0.2 | 2026-10-16 | v2.0.2, Latest, 08 Oct | Primary documentation | Year inferred from registry `publishedAt` 2026-10-08. The `/releases` list page showed stale v1.11.0 entries |
| C45 | Microsoft, https://github.com/microsoft/playwright-mcp/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| C46 | npm, https://registry.npmjs.org/@playwright/mcp | 2026-10-16 | 0.0.83 (2026-09-28) | Primary documentation | — |
| C47 | Microsoft, https://github.com/microsoft/playwright-mcp/blob/main/LICENSE | 2026-10-16 | main | Primary documentation | Apache-2.0 |
| C48 | Stripe, https://docs.stripe.com/mcp | 2026-10-16 | global | Primary documentation | — |
| C49 | Atlassian, https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/ | 2026-10-16 | global | Primary documentation | Admin controls page not read; page mixes v1 and v2 URLs |
| C50 | Sentry, https://github.com/getsentry/sentry-mcp/blob/main/README.md | 2026-10-16 | main | Primary documentation | docs.sentry.io/product/sentry-mcp redirects to mcp.sentry.dev (not fetched) |
| C51 | Sentry, https://github.com/getsentry/sentry-mcp/blob/main/LICENSE.md | 2026-10-16 | main | Primary documentation | FSL-1.1 with Apache-2.0 future licence |
| C52 | npm, https://registry.npmjs.org/@sentry/mcp-server | 2026-10-16 | 0.42.0 (2026-09-25) | Primary documentation | — |
| C53 | Bytebase, https://github.com/bytebase/dbhub/blob/main/README.md | 2026-10-16 | main | Primary documentation | — |
| C54 | npm, https://registry.npmjs.org/@bytebase/dbhub | 2026-10-16 | 1.5.0 (2026-10-09) | Primary documentation | — |
| C55 | Bytebase, https://github.com/bytebase/dbhub/blob/main/LICENSE | 2026-10-16 | main | Primary documentation | MIT |
| C56 | OpenAI, https://openai.github.io/openai-agents-python/mcp/ | 2026-10-16 | current docs | Primary documentation | Sampling and elicitation not mentioned (unknown, not unsupported) |
| C57 | LangChain, https://docs.langchain.com/oss/python/langchain/mcp | 2026-10-16 | `langchain[mcp]>=1.4.0` (beta) | Primary documentation | Separate Auth, Connections and Tools pages not read |
| C58 | Google, https://adk.dev/tools-custom/mcp-tools/ | 2026-10-16 | current docs | Primary documentation | Redirected from google.github.io/adk-docs |
| C59 | Anthropic, https://code.claude.com/docs/en/agent-sdk/mcp | 2026-10-16 | current docs | Primary documentation | — |
| C60 | MCP publisher / PyPI, https://pypi.org/pypi/mcp/2.3.0/json | 2026-10-18 | 2.3.0 | Primary package metadata; source checked / unverified | Exact `mcp-types==2.3.0` dependency and wheel identity; no remote-server result |
| C61 | MCP publisher / PyPI, https://pypi.org/pypi/mcp-types/2.3.0/json | 2026-10-18 | 2.3.0 | Primary package metadata; source checked / unverified | Versioned wheel identity; [PyPI provenance page](https://pypi.org/project/mcp-types/2.3.0/) identifies publishing commit `2118f14f8a19bc158d8a1cf90af58d85d187f849` |
| C62 | MCP, https://github.com/modelcontextprotocol/python-sdk/blob/2118f14f8a19bc158d8a1cf90af58d85d187f849/src/mcp-types/mcp_types/version.py | 2026-10-18 | 2.3.0 publishing revision | Primary source; source checked / unverified | Exact known, handshake and modern sets; installed and wheel bytes match the pinned Git blob |
| C63 | MCP, https://github.com/modelcontextprotocol/python-sdk/blob/2118f14f8a19bc158d8a1cf90af58d85d187f849/src/mcp/client/client.py | 2026-10-18 | 2.3.0 publishing revision | Primary source; source checked / unverified | `Client.__aenter__` distinguishes auto, legacy and direct modern adoption |
| C64 | MCP, https://github.com/modelcontextprotocol/python-sdk/blob/2118f14f8a19bc158d8a1cf90af58d85d187f849/src/mcp/client/_probe.py | 2026-10-18 | 2.3.0 publishing revision | Primary source; source checked / unverified | Conditional fallback and transport-error boundary, not an unconditional interoperability promise |
| C65 | MCP publisher / PyPI, https://pypi.org/pypi/mcp/1.30.0/json | 2026-10-18 | 1.30.0 | Primary package metadata and wheel source; source checked / unverified | Separate legacy SDK environment; no reference-server package was installed |
| C66 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/index | 2026-10-18 | 2026-07-28 | Primary specification; source checked / unverified | HTTP scope, intended resource/audience, operation scopes, token errors and discretionary refresh-token issuance; no authorization server or credential exercised |
| C67 | MCP, https://modelcontextprotocol.io/extensions/auth/overview and https://modelcontextprotocol.io/extensions/auth/oauth-client-credentials | 2026-10-18 | Current extension documentation, independently versioned from core | Primary documentation; source checked / unverified | Explicit client support and accepted client-credentials flow; server discovery advertisement is recommended, not mandatory proof of support or non-support |
| C68 | Anthropic, https://code.claude.com/docs/en/agent-sdk/mcp#oauth2-authentication | 2026-10-18 | Current Agent SDK documentation, no installed package qualification | Primary documentation; source checked / unverified | Application-owned OAuth acquisition and header injection; no actual client/server/token result |
| C69 | OpenAI, https://openai.github.io/openai-agents-python/mcp/ | 2026-10-18 | Current Agents Python documentation; local MCP v1/v2 distinctions | Primary documentation; source checked / unverified | Local transport ownership, hosted Responses path, header injection and version-dependent HTTP auth types; no account or model request |
| C70 | MCP, https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio | 2026-10-18 | 2026-07-28 | Primary specification; source checked / unverified | Subprocess/stream ownership and lifecycle; custom channels have separate equivalents. No new process experiment |
| C71 | Google, https://adk.dev/tools-custom/mcp-tools/#remote-mcp-authentication-and-resource-access | 2026-10-18 | Current ADK documentation, no installed package qualification | Primary documentation; source checked / unverified | Documented authentication integration does not establish a selected credential, issuer, operation entitlement or renewal capability |
| C72 | Sentry, https://github.com/getsentry/toolkit/blob/main/README.md#remote-with-an-explicit-sentry-token | 2026-10-18 | Current README; earlier `getsentry/sentry-mcp` URL redirects here | Primary documentation; source checked / unverified | Distinguishes MCP OAuth `Bearer` from custom upstream `Sentry-Bearer`; describes forwarding without worker validation, exchange or renewal. No deployed revision or credential was tested |
| C73 | MCP, https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices#token-passthrough | 2026-10-18 | 2026-07-28 guidance | Primary documentation; source checked / unverified | Audience-validation and downstream-forwarding boundary, read with C66; grounds the separate project policy assessment below |

## Compatibility proposals

These rules are proposed for review by #40.
- **Source-checked (unverified):** the rule's factual premise is primary-source backed; it has not been independently reproduced.
- **Hypothesis:** the rule depends on a policy choice, a proxy field or a field that v1 lacks.
- Outcomes are `pass/fail/unknown/skipped`. Severity is a separate field.
- The JSON blocks below were validated together as a ruleset against `contracts/v1/schemas/ruleset.schema.json`. They were also run through `contracts/v1/reference/evaluate.py` on a synthetic, unsaved build (GitHub remote + air-gapped hosting), which produced the expected `fail` for the air-gap rule.

**Relation to the baseline:**
- `rule.agent.mcp.framework` checks only `agent_framework.spec.supports_mcp`. That boolean cannot express transport, protocol era, auth flow or client capabilities. The rules below **extend** it and do not replace it. The boolean should be kept as a coarse gate until the #40 fields exist.
- `rule.tool.mutation.guardrails` is gated on the metric `tools.mutating_count`. The reference evaluator counts only selections of kind `tool`, so **MCP server tools are invisible to it** (problem flagged). The limited v1 `rule.t4.mcp.mutation.guardrails` proposal exposes this gap; its user-intent field and single-primary guard do not prove per-tool enforcement.
- **All `role: primary` refs resolve only when exactly one active selection matches.** With two or more enabled MCP servers sharing role `primary`, those references are ambiguous. The six v1 rules below guard applicability with `exists` on that selection; the guard is false and each rule is `skipped`, so the servers are not checked individually. Per-server iteration needs a contract change (#40).

**Current shared interpretation (2026-10-18).** Apply the accepted #40 identity/role preflight and all-enabled-selection scope before evaluating successor proposals. Bind transport, protocol, required client capabilities and authorization to the **same selected connection, client implementation, server packaging and relevant configuration**. Separate support somewhere in two product-wide lists cannot prove that combined path. A direct SDK client is a valid no-framework case; missing an `agent_framework` selection does not itself prove no MCP client exists. Its client identity still needs a reviewed #40 representation.

Use the adopted #41 evidence eligibility and #40/CD-3 completeness policy for every membership assertion: eligible explicit unsupported evidence or absence from an eligible exhaustive list can establish a negative; an omission from an unmarked list remains unknown. A supported path may pass its narrow prerequisite on checked documentation, with its unverified grade displayed. Preserve per-path findings and distinguish a suggested alternative from the user's selected path. Historical v1 JSON below remains a limited research illustration; no credential-presence, trust-label or user-intent guard certifies the corresponding #35 control.

### Rule summary

| Rule id | Example | Status | Format | Severity | on_unknown |
| --- | --- | --- | --- | --- | --- |
| `rule.t4.mcp.transport.sse-deprecated` | transport lifecycle | Source-checked (unverified) | json | warning | review |
| `rule.t4.mcp.remote.air-gapped` | (4) hosting unavailable in deployment | Historical proxy; new work routed to W-R8/CD-4 | json (historical) | error | review |
| `rule.t4.mcp.untrusted.guardrails` | trust | Hypothesis (policy on a source-checked premise) | json | error | block |
| `rule.t4.mcp.trust-level.required` | trust data completeness | Hypothesis (policy) | json | warning | review |
| `rule.t4.mcp.credential.secret-ref` | credentials | Hypothesis | json | warning | review |
| `rule.t4.mcp.mutation.guardrails` | side effects | Hypothesis | json | error | block |
| `rule.t4.mcp.transport.client-support` | (3) transport unsupported by client | Source-checked (unverified) premise | needs contract change via #40 | error | block |
| `rule.t4.mcp.protocol.era` | version compatibility | Source-checked (unverified) | needs contract change via #40 | error | block |
| `rule.t4.mcp.client-capabilities` | capability compatibility | Source-checked (unverified) | needs contract change via #40 | error | review |
| `rule.t4.mcp.auth.flow-available` | (4) authorization unavailable in deployment | Source-checked (unverified) premise | needs contract change via #40 | error | block |
| `rule.t4.mcp.stdio.colocation` | (4) local process impossible in mode | Source-checked (unverified) premise | needs contract change via #40 | error | block |
| `rule.t4.mcp.registry.identity` | impersonation | Hypothesis | needs contract change via #40 | warning | review |

### rule.t4.mcp.transport.sse-deprecated (Source-checked (unverified))

- **Participating kinds, roles and JSON pointers:** `mcp_server` (primary) `/spec/transport`; `agent_framework`.
- **Applicability condition:** an MCP server is selected.
- **Assertion and source evidence:** transport ≠ `sse`. HTTP+SSE is Deprecated (C9, C11); registry guidance limits it to existing clients (C23).
- **Severity:** warning.
- **Missing-data behavior:** `unknown`, then review.
- **Explanation and remediation:** see the JSON.
- **Dependency edges and affected consumers:** `dep.mcp_server.agent_framework`; #25 (which frameworks keep SSE clients: OpenAI Agents SDK `MCPServerSse`, ADK `SseConnectionParams` and Claude Agent SDK `type: "sse"` were seen, C56, C58, C59).
- **Examples (synthetic):**
  - Passing: `mcp_server.github-remote` (`streamable_http`).
  - Failing: a server item with `transport: "sse"`.
  - Unknown: an item without `/spec/transport`, which is impossible in v1 because the field is required.
- **Version and migration impact:** when HTTP+SSE is Removed, raise the severity to error.

```json
{
  "id": "rule.t4.mcp.transport.sse-deprecated",
  "severity": "warning",
  "applies_when": {
    "op": "exists",
    "value": {
      "ref": {
        "scope": "selection",
        "kind": "mcp_server",
        "role": "primary",
        "pointer": "/id"
      }
    }
  },
  "assert": {
    "op": "ne",
    "left": {
      "ref": {
        "scope": "catalog",
        "kind": "mcp_server",
        "role": "primary",
        "pointer": "/spec/transport"
      }
    },
    "right": {
      "literal": "sse"
    }
  },
  "on_unknown": "review",
  "message": "The selected MCP server packaging uses the HTTP+SSE transport from protocol 2024-11-05, which is Deprecated and eligible for removal.",
  "remediation": "Select the server's Streamable HTTP or stdio packaging. Keep an SSE packaging only for a legacy server, and confirm the agent framework still ships an SSE client.",
  "affected_kinds": [
    "mcp_server",
    "agent_framework"
  ],
  "owner": "t4-research"
}
```

### rule.t4.mcp.remote.air-gapped (Hypothesis, compatibility example 4)

**Central-review disposition (reconciled 2026-10-18).** [The actual #40 queue review](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6242626523) narrows this proxy into [W-R8](../T0-configuration/workload-use-case.md#w-r8-air-gapped-builds-have-no-external-connections) and CD-4. Assess enabled runtime connections against the selected isolation boundary and require runtime artifacts inside it. A provider-operated endpoint inside that boundary can pass with the required evidence; a self-operated endpoint reached across the boundary fails. Missing connection, lifecycle or boundary evidence remains unknown. The following proxy, proposed hosting enum and JSON are retained as historical research, not the current isolation assertion or an adopted executable rule. Per-component deployment and versioned boundary representation remain with #40.

- **Participating kinds:** `mcp_server` `/spec/transport` and `/spec/trust_level`; `hosting_platform` selection `/settings/network_isolation`.
- **Applicability condition:** a remote transport combined with an externally operated server, approximated by `trust_level` ∈ {trusted_external, untrusted_external}. **The proxy is the reason this rule is a hypothesis.** `trust_level` describes trust, not who hosts the endpoint. A self-hosted copy of an external project would be wrongly flagged unless it is catalogued as `internal`.
- **Assertion:** `network_isolation` ≠ `air_gapped`. A vendor-hosted remote server must be publicly accessible (C23), and an air-gapped platform cannot reach it.
- **Severity:** error. **Missing data:** review.
- **Examples (synthetic):**
  - Passing: GitHub remote with `network_isolation: private` where egress exists (egress itself is not modelled).
  - Failing: GitHub remote with `air_gapped`.
  - Unknown: no hosting platform selected.
- **Contract change (#40):** replace the proxy with `mcp_server.spec.hosting` ∈ {`local_process`, `self_hosted_remote`, `vendor_hosted_remote`} and a hosting-platform egress field. Intended expression:

```text
applies_when: catalog mcp_server /spec/hosting == "vendor_hosted_remote"   # missing field: spec_mcp_server.hosting
assert: selection hosting_platform /settings/network_isolation != "air_gapped"
        AND catalog hosting_platform /spec/allows_public_egress == true      # missing field: spec_hosting_platform.allows_public_egress
```

```json
{
  "id": "rule.t4.mcp.remote.air-gapped",
  "severity": "error",
  "applies_when": {
    "op": "all",
    "args": [
      {
        "op": "exists",
        "value": {
          "ref": {
            "scope": "selection",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/id"
          }
        }
      },
      {
        "op": "in",
        "left": {
          "ref": {
            "scope": "catalog",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/spec/transport"
          }
        },
        "right": {
          "literal": [
            "streamable_http",
            "sse"
          ]
        }
      },
      {
        "op": "in",
        "left": {
          "ref": {
            "scope": "catalog",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/spec/trust_level"
          }
        },
        "right": {
          "literal": [
            "trusted_external",
            "untrusted_external"
          ]
        }
      }
    ]
  },
  "assert": {
    "op": "ne",
    "left": {
      "ref": {
        "scope": "selection",
        "kind": "hosting_platform",
        "role": "primary",
        "pointer": "/settings/network_isolation"
      }
    },
    "right": {
      "literal": "air_gapped"
    }
  },
  "on_unknown": "review",
  "message": "A remote MCP server operated outside the organisation cannot be reached from an air-gapped hosting platform.",
  "remediation": "Use a local stdio packaging or a self-hosted (internal) deployment of the server, or change the network isolation setting.",
  "affected_kinds": [
    "mcp_server",
    "hosting_platform",
    "deployment_target"
  ],
  "owner": "t4-research"
}
```

### rule.t4.mcp.untrusted.guardrails (Hypothesis: policy on a source-checked premise)

- **Premise (source-checked):**
  - Clients MUST treat tool annotations as untrusted unless the server is trusted (C15).
  - Hosts must obtain consent before invoking tools (C18, non-normative).
  - Tool results flow into model context (C15 asks clients to validate results before passing them to the LLM).
- **Policy (hypothesis):** require a guardrail targeting `tool` with `tool_permissions` and `prompt_injection` policies when `trust_level = untrusted_external`.
- **Severity:** error. **Missing data:** block.
- **Examples (synthetic):**
  - Passing: untrusted server with a guardrail that has both policies.
  - Failing: no guardrail.
  - Skipped: `trusted_external` server.
- **Handoff:** the control design (enforcement mode, approval UX) belongs to #35.

```json
{
  "id": "rule.t4.mcp.untrusted.guardrails",
  "severity": "error",
  "applies_when": {
    "op": "all",
    "args": [
      {
        "op": "exists",
        "value": {
          "ref": {
            "scope": "selection",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/id"
          }
        }
      },
      {
        "op": "eq",
        "left": {
          "ref": {
            "scope": "catalog",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/spec/trust_level"
          }
        },
        "right": {
          "literal": "untrusted_external"
        }
      }
    ]
  },
  "assert": {
    "op": "all",
    "args": [
      {
        "op": "exists",
        "value": {
          "ref": {
            "scope": "selection",
            "kind": "guardrail",
            "role": "primary",
            "pointer": "/id"
          }
        }
      },
      {
        "op": "contains",
        "left": {
          "ref": {
            "scope": "catalog",
            "kind": "guardrail",
            "role": "primary",
            "pointer": "/spec/targets"
          }
        },
        "right": {
          "literal": "tool"
        }
      },
      {
        "op": "contains",
        "left": {
          "ref": {
            "scope": "catalog",
            "kind": "guardrail",
            "role": "primary",
            "pointer": "/spec/policies"
          }
        },
        "right": {
          "literal": "tool_permissions"
        }
      },
      {
        "op": "contains",
        "left": {
          "ref": {
            "scope": "catalog",
            "kind": "guardrail",
            "role": "primary",
            "pointer": "/spec/policies"
          }
        },
        "right": {
          "literal": "prompt_injection"
        }
      }
    ]
  },
  "on_unknown": "block",
  "message": "An untrusted external MCP server supplies tool descriptions, annotations and results that the protocol says to treat as untrusted.",
  "remediation": "Add a guardrail targeting tools with tool_permissions and prompt_injection policies, or replace the server with a trusted or internal one.",
  "affected_kinds": [
    "mcp_server",
    "guardrail",
    "agent_framework"
  ],
  "owner": "t4-research"
}
```

### rule.t4.mcp.trust-level.required (Hypothesis)

`trust_level` is optional in v1. Without it, the untrusted rule is skipped, which fails open. This rule makes the gap visible. An alternative for #40 is to make `trust_level` required for `mcp_server`.

```json
{
  "id": "rule.t4.mcp.trust-level.required",
  "severity": "warning",
  "applies_when": {
    "op": "exists",
    "value": {
      "ref": {
        "scope": "selection",
        "kind": "mcp_server",
        "role": "primary",
        "pointer": "/id"
      }
    }
  },
  "assert": {
    "op": "exists",
    "value": {
      "ref": {
        "scope": "catalog",
        "kind": "mcp_server",
        "role": "primary",
        "pointer": "/spec/trust_level"
      }
    }
  },
  "on_unknown": "review",
  "message": "The selected MCP server has no recorded trust level, so trust-dependent checks cannot run.",
  "remediation": "Record trust_level on the catalog item using the published criteria, or treat the server as untrusted_external.",
  "affected_kinds": [
    "mcp_server",
    "guardrail"
  ],
  "owner": "t4-research"
}
```

### rule.t4.mcp.credential.secret-ref (Hypothesis)

- **Premise:**
  - stdio servers take credentials from the environment (C12).
  - Remote servers take bearer tokens in the `Authorization` header and never in the query string (C12).
  - GitHub, Stripe and Sentry all document static-token alternatives to OAuth (C42, C48, C50).
- **Policy:** a credential-bearing server needs a `secret://` reference on the selection.
- **Limitation:** interactive OAuth clients may hold tokens in their own store. Because of that, severity is warning and the rule is a hypothesis.

```json
{
  "id": "rule.t4.mcp.credential.secret-ref",
  "severity": "warning",
  "applies_when": {
    "op": "all",
    "args": [
      {
        "op": "exists",
        "value": {
          "ref": {
            "scope": "selection",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/id"
          }
        }
      },
      {
        "op": "exists",
        "value": {
          "ref": {
            "scope": "catalog",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/spec/auth_methods"
          }
        }
      },
      {
        "op": "not",
        "arg": {
          "op": "contains",
          "left": {
            "ref": {
              "scope": "catalog",
              "kind": "mcp_server",
              "role": "primary",
              "pointer": "/spec/auth_methods"
            }
          },
          "right": {
            "literal": "none"
          }
        }
      }
    ]
  },
  "assert": {
    "op": "exists",
    "value": {
      "ref": {
        "scope": "selection",
        "kind": "mcp_server",
        "role": "primary",
        "pointer": "/settings/credential_ref"
      }
    }
  },
  "on_unknown": "review",
  "message": "The MCP server requires credentials but the selection has no secret-manager reference.",
  "remediation": "Store the API key, or the OAuth refresh token for non-interactive runs, in a secret manager and set credential_ref. Never place tokens in the endpoint URL.",
  "affected_kinds": [
    "mcp_server"
  ],
  "owner": "t4-research"
}
```

### rule.t4.mcp.mutation.guardrails (Hypothesis; fixes a baseline gap)

- **Premise:** The inspected MCP servers include mutating tools: Stripe `stripe_api_write` (C48), GitHub write tools unless `--read-only` (C42), memory `delete_entities` (C40), DBHub `execute_sql` unless read-only (C53).
- **Gap:** the baseline metric does not count these tools.
- **Assertion:** `read_only` is set on the selection, or a `tool_permissions` guardrail exists.
- **Limitation:** `read_only` is user intent. v1 cannot say whether the server enforces a read-only mode (GitHub and DBHub do; Stripe documents none). A #40 field `spec_mcp_server.read_only_mode_supported` would make this rule verifiable.

```json
{
  "id": "rule.t4.mcp.mutation.guardrails",
  "severity": "error",
  "applies_when": {
    "op": "exists",
    "value": {
      "ref": {
        "scope": "selection",
        "kind": "mcp_server",
        "role": "primary",
        "pointer": "/id"
      }
    }
  },
  "assert": {
    "op": "any",
    "args": [
      {
        "op": "eq",
        "left": {
          "ref": {
            "scope": "selection",
            "kind": "mcp_server",
            "role": "primary",
            "pointer": "/settings/read_only"
          }
        },
        "right": {
          "literal": true
        }
      },
      {
        "op": "all",
        "args": [
          {
            "op": "exists",
            "value": {
              "ref": {
                "scope": "selection",
                "kind": "guardrail",
                "role": "primary",
                "pointer": "/id"
              }
            }
          },
          {
            "op": "contains",
            "left": {
              "ref": {
                "scope": "catalog",
                "kind": "guardrail",
                "role": "primary",
                "pointer": "/spec/policies"
              }
            },
            "right": {
              "literal": "tool_permissions"
            }
          }
        ]
      }
    ]
  },
  "on_unknown": "block",
  "message": "MCP server tools may mutate external systems, and the baseline tools.mutating_count metric does not count them.",
  "remediation": "Set read_only on the selection (only where the server enforces a read-only mode) or add a guardrail with a tool_permissions policy.",
  "affected_kinds": [
    "mcp_server",
    "guardrail",
    "agent_framework"
  ],
  "owner": "t4-research"
}
```

### rule.t4.mcp.transport.client-support (compatibility example 3; needs contract change via #40)

- **Participating fields (missing):** `spec_mcp_server.transports` (array) and `spec_agent_framework.mcp_client_transports` (array).
- **Current assertion:** the selected transport is supported by the bound client implementation and server packaging. A product-wide set intersection only identifies a candidate path; it cannot select or prove the configured path. If the research question permits several alternatives, a positive alternative needs evidence for the same complete connection tuple, and an overall negative needs all relevant alternatives resolved as unsupported.
- **Outcomes:** `pass` for the narrow transport prerequisite when both sides have eligible support evidence; `fail` for an eligible explicit incompatibility or exhaustive negative; `unknown` for missing applicability, support or relevant alternative-completeness evidence; `skipped` when no enabled applicable MCP selection exists. **Severity:** `error`; **on_unknown:** `block`. Remediation identifies the unsupported/missing selected path and may suggest a separately assessed packaging or client.
- **Source-checked (unverified) premise (C56–C59):**

| Framework (docs, 2026-10-16) | stdio | Streamable HTTP | HTTP+SSE | Provider-hosted remote | Status in rule terms |
| --- | --- | --- | --- | --- | --- |
| OpenAI Agents SDK (Python) | yes `MCPServerStdio` | yes `MCPServerStreamableHttp` | yes `MCPServerSse` (legacy) | yes `HostedMCPTool` | documented client interfaces; selected server/version/configuration still required |
| Google ADK | yes `StdioConnectionParams` | yes `StreamableHTTPConnectionParams` | yes `SseConnectionParams` | not documented | documented client interfaces; selected server/version/configuration still required |
| Claude Agent SDK | yes | yes (`type: "http"`) | yes (`type: "sse"`) | not applicable | documented client interfaces; selected server/version/configuration still required |
| LangChain `langchain[mcp]` (beta) | yes (script path) | yes (http/https URL) | not on the page read | — | sse = unknown |

- **Examples (synthetic):**
  - Failing: selected SSE connection where the client's eligible exhaustive support list contains only `stdio` and `streamable_http`.
  - Unknown: the same omission on a non-exhaustive client page; LangChain's original unread SSE detail is such an unknown.
  - No combined pass: client/server products both list HTTP and stdio, but the selected provider-hosted interface has no direct stdio path. A different local client would require a separate binding and assessment.

```text
# Conceptual successor inputs; not executable v1 or a new adopted DSL.
applies_to: each enabled, identity-bound MCP connection
assert: selected transport has eligible support at both bound endpoints
        in the selected implementation/configuration
outcomes: use scoped support and completeness evidence, retaining each path
on_unknown: block   severity: error
```

### rule.t4.mcp.protocol.era (needs contract change via #40, Source-checked (unverified))

The rule uses the C7 era matrix as a protocol prerequisite, with the current selected-connection and evidence interpretation above. The words modern, legacy or dual-era alone do not establish a negotiated configuration.
- **Pass:** eligible evidence identifies a common revision supported by both endpoints on the selected transport and the required direct/fallback negotiation path in the selected configuration. This is protocol support evidence, not an observed exchange unless an attributed run supplies one.
- **Fail:** the selected configuration is explicitly unsupported, or complete eligible revision/negotiation evidence leaves no usable shared path; a modern-only client and legacy-only server are an example (C7).
- **Unknown:** required version, transport, negotiation or completeness evidence is missing. An incomplete list without an observed intersection cannot establish incompatibility.
- **Skipped:** no enabled applicable MCP connection. **Severity:** `error`; **on_unknown:** `block`. Remediation identifies the missing or incompatible revision/negotiation requirement.
- **Source-checked (unverified) facts:**
  - The legacy TypeScript SDK line supports up to 2025-11-25 (C31).
  - Python `mcp` 1.30.0 supports up to 2025-11-25.
  - The reference servers are pinned to those lines (C36, C38).
- **Framework version support:** [#25's pinned A86 follow-up](agent-framework.md#pinned-source-follow-up-2026-10-18) source-checks OpenAI Agents Python 0.24.0's support for MCP Python package v1/v2 and v2 auto negotiation with legacy fallback. This is conditional client implementation evidence, not an actually negotiated protocol set for a selected server. Other framework/protocol tuples and sampling/elicitation remain unknown where no eligible evidence was read.
- **SDK-only execution:** the [2026-10-18 stdio experiment](#pinned-python-sdk-protocol-follow-up-2026-10-18) observes this SDK pair's modern exchange and legacy fallback with a synthetic echo peer. It does not run the Agents framework, remote transports or a candidate catalog server.

```text
# Conceptual successor inputs, evaluated after shared identity/role preflight.
assert: one eligible revision and negotiation path is supported by both
        endpoints of the same selected transport/configuration
outcomes: retain unsupported paths and unknown incomplete alternatives
on_unknown: block   severity: error
```

### rule.t4.mcp.client-capabilities (needs contract change via #40, Source-checked (unverified) premise)

- **Assertion:** each capability required for the selected server operation/configuration has eligible support in the bound client on that connection. An optional feature is not a mandatory prerequisite merely because a server advertises it. Record accepted configuration alternatives, such as filesystem CLI roots, separately.
- **Premise:**
  - Servers can return `MissingRequiredClientCapabilityError` (C16).
  - The filesystem reference server exits at initialization when it has neither CLI directories nor client Roots support (C35).
  - Roots and Sampling are Deprecated (C11), so new frameworks may omit them.
  - OpenAI Agents SDK docs do not mention sampling or elicitation (unknown, C56). ADK docs mention resources but not prompts or sampling (C58).
- **Severity:** error. on_unknown review; resolve required-versus-optional capability and configuration alternatives explicitly.
- **Outcomes:** pass when every applicable required capability is evidenced; fail on a known required unsupported capability after resolving applicable configuration alternatives; unknown when a required input or list completeness is missing; skip when the operation has no applicable requirement. Keep the same source/selection boundaries as transport and protocol, rather than treating an unmarked missing member as false.

```text
# Conceptual note-only requirement and scoped support sets; not executable v1.
assert: every applicable required client capability has eligible support
        on the bound operation/connection, including accepted alternatives
on_unknown: review   severity: error
```

### rule.t4.mcp.auth.flow-available (compatibility example 4; needs contract change via #40, Source-checked (unverified) premise)

**Current disposition, 2026-10-18.** Retain the rule ID and `error` severity, but withdraw the earlier target-type and secret-reference shortcuts. A `batch_worker` label does not establish which authorization paths are available; `application` does not establish a working browser/callback path. A `credential_ref` identifies secret storage, not a usable, authorized credential. The following is a research decision and proposed #40 input, not released schema syntax or an authorization grant.

**Source findings:**

- C66 limits the core authorization flow to HTTP. It binds access tokens to the MCP resource and requires operation-appropriate permissions; invalid/expired tokens and insufficient permissions have distinct responses. Refresh-token issuance is discretionary. A stored refresh-token reference cannot establish a renewable grant.
- C67 documents a client-credentials path for unattended workloads. Support must be explicit in the client and accepted by the selected authorization/resource-server arrangement. Its discovery advertisement is optional on the server side; an omitted unmarked extension entry is not an exhaustive negative.
- C68 documents application-owned OAuth acquisition for the Claude Agent SDK, followed by access-token headers. A challenge without a stored token leaves that server needing authentication. Application integration can supply the flow; the SDK's lack of an internal browser is not a universal deployment prohibition.
- C69 documents OpenAI's local header injection and distinguishes `httpx.Auth` for MCP v1 from `httpx2.Auth` for v2. `HostedMCPTool` instead delegates the remote connection to the Responses API. C71 supplies ADK authentication-integration documentation. These are client implementation capabilities, not proof of a selected grant, server support or future renewal. Unread LangChain authentication details remain unknown.

**Scope and evidence inputs.** Evaluate every enabled server selection against the actual client, transport, endpoint, operation, principal and relevant configuration/revision. Resolve the selected authorization alternative even when a catalog lists several `auth_methods`; comparing the entire array to `["oauth2"]` can skip a protected operation. Run the shared #40 identity/role preflight first: invalid or ambiguous bindings cannot yield a compatibility result. For valid bindings, missing applicability evidence remains unknown rather than being silently skipped. Use the shared per-selection/evidence mechanics; do not rewrite v1's historical single-primary behavior.

| Proposed input | Type / unit | Required evidence boundary |
| --- | --- | --- |
| Selected connection and operation | Bound selection IDs, endpoint/resource ID and operation identifier; no numeric unit | Client/server versions or dated service configuration, transport, principal and requested resource/action |
| Applicable authorization paths | Set of accepted alternatives with per-member evidence | Actual protected operation and relevant authorization server; distinguish a documented anonymous operation from a missing requirement |
| Acquisition/continuation capability | Per-path `yes` / `no` / `unknown`, with scope | Client integration, registration, required interaction/callback, token acquisition, and any renewal or step-up needed for this use |
| Credential applicability | Scoped evidence result plus opaque secret reference | Intended issuer/resource, permissions, principal, validity and selected injection mechanism; never publish the credential value |
| Required execution/lifecycle scope | Declared operation and relevant validity/renewal conditions | A currently usable token may cover a bounded operation without proving unattended renewal; future-use prerequisites need separate evidence |
| Evidence eligibility and alternative completeness | Scoped evidence records; `known` or `unknown` coverage | No unsupported result from omission on a non-exhaustive capability page; conflicting evidence remains visible |

**Decision (project proposal):** `pass` requires one completely supported applicable path for the stated operation/lifecycle scope. A documented incompatibility can fail that path; report an overall `fail` only when the applicable alternatives are known complete and all fail. If no path passes and a required input or alternative remains unresolved, return `unknown`. A disabled selection or an explicitly evidenced anonymous operation is `skipped` for this protected-HTTP-authentication rule. STDIO upstream credentials are a separate requirement, not an inferred HTTP OAuth flow. Keep per-path findings so a rejected credential or flow is not hidden by a viable alternative.

The proposed `on_unknown: block` handling prevents declaring this prerequisite satisfied while preserving the `unknown` outcome; it is not a conversion to known incompatibility. Remediation identifies the failed or missing requirement: select an accepted flow, provide the appropriate client integration/configuration evidence, or obtain an authorized credential for the exact operation. A research `pass` does not authorize an invocation or replace #35's operation-level permissions and runtime checks.

```text
# Conceptual outcome ordering only; not executable v1 or an adopted successor DSL.
for each enabled, identity-bound MCP connection and requested operation:
  resolve whether this protected-HTTP authorization requirement applies
  evaluate each eligible accepted path against its exact use and lifecycle scope
  pass if an applicable path has all required evidence
  fail if the alternative set is complete and every applicable path is known to fail
  unknown otherwise; retain each path's evidence and reasons
severity: error
on_unknown: block
```

| Synthetic case (not an executed service result) | Proposed outcome |
| --- | --- |
| Batch worker; accepted client-credentials flow, configured client support and eligible evidence for the operation and required renewal | `pass` for that scope; the target label contributes no authorization evidence |
| Application target; browser/callback availability is unexamined | `unknown` |
| Token-injection support and `credential_ref` exist; issuer/resource, scope or validity is unexamined | `unknown` |
| Only applicable flow is known to require unavailable interaction; alternative inventory is complete | `fail` |
| One examined flow fails, but another accepted path remains unresolved | `unknown`, retaining the known failed path |
| A usable injected access token covers the bounded operation; no renewable grant is established | Bounded-operation `pass` only if all its evidence is eligible; required unattended-renewal readiness remains `unknown` |
| Server advertises both OAuth and another method; selected operation requires OAuth | Evaluate the selected OAuth path; the multi-value catalog array does not cause `skipped` |
| Operation is explicitly anonymous, or the server selection is disabled | `skipped` for this rule only; trust and tool-policy checks remain separate |

### rule.t4.mcp.stdio.colocation (compatibility example 4; needs contract change via #40, Source-checked (unverified) premise)

**Current disposition, 2026-10-18.** Assess the selected direct stdio connection by its actual process/stream ownership, not a build-level deployment-mode enum. C70 specifies client-launched subprocess communication and process lifecycle. C69 separates a local `MCPServerStdio` connection from the hosted Responses connection. Model-API use can coexist with a customer-side MCP process; an `api` model choice alone is not a failure.

- **Scope:** each enabled selection whose chosen connection is direct subprocess stdio. A known HTTP connection is skipped for this rule; unknown transport/locality remains unknown.
- **Proposed inputs:** exact selected client/runtime and server packaging, executable/launch configuration, ability to start the owned process and connect its streams, and the lifecycle and permitted-resource evidence for that configuration. These are note-only typed identity/configuration/evidence inputs for #40; a generic `can_spawn_processes` flag alone is insufficient.
- **Pass:** eligible evidence establishes those prerequisites for the selected connection. This is the scoped stdio prerequisite, not whole-server, protocol, artifact-trust or deployment certification.
- **Fail:** an eligible requirement is known unsatisfied, such as a selected client with no direct subprocess path. A `HostedMCPTool`-only path cannot itself launch the user's local stdio package. Unknown client/locality evidence is not a known failure.
- **Unknown:** required launch, stream, locality or lifecycle evidence is missing or conflicting. **Severity:** `error`; **on_unknown:** `block`. Remediation identifies the missing/unsupported local capability or proposes a separately assessed remote packaging.
- **Intermediaries:** a bridge adds a distinct connection and operator boundary. Evaluate each leg, authorization and lifecycle explicitly. The specification allows custom stream transports with channel-specific lifecycle equivalents (C70); they are not automatically the direct-subprocess tuple assessed here.

```text
# Conceptual prerequisite; no new v1 fields or executable successor rule.
applies_to: each enabled, identity-bound direct-subprocess stdio connection
requires: selected client owns an evidenced launch, stream and lifecycle path
outcomes: pass / fail / unknown / skipped, with the scoped reasons retained
severity: error
on_unknown: block
```

Synthetic review cases: model API plus an evidenced customer-side subprocess can pass this prerequisite; a managed-runtime label with unknown process support remains unknown; a hosted-Responses-only client with no direct subprocess path fails that selected direct-stdio requirement. These examples add no runtime measurements.

### rule.t4.mcp.registry.identity (Hypothesis; needs contract change via #40)

- **Rule:** when a `registry_name` is recorded, its namespace should match the maintainer's GitHub org or domain, and the remote URL host should belong to that domain. Otherwise: warning plus review.
- **Premise:**
  - The registry verifies namespaces (C21) but not URL ownership of remotes.
  - Proxy and lookalike entries exist next to the vendor's own entry (C25, C30).

```text
assert: registry_namespace_matches(catalog mcp_server /spec/registry_name,     # missing field
                                   catalog mcp_server /spec/remote_url_host)  # missing field; also needs a new operator
```

### Contract gaps for #40 (field level)

1. Replace `spec_mcp_server.transport` (single value) with `transports: array of enum` or with `packagings[]` carrying {transport, url or package, hosting}. Rename or annotate `sse` as `http_sse_legacy`, Deprecated since 2025-03-26.
2. Add `spec_mcp_server.protocol_versions: array of YYYY-MM-DD` (or `protocol_era`).
3. Add `spec_mcp_server.capabilities` (server features) and `required_client_capabilities`.
4. Original packaging proposal: `spec_mcp_server.hosting` ∈ {local_process, self_hosted_remote, vendor_hosted_remote}, plus `maintainer`, `registry_name` and a package pin {registry_type, identifier, version or digest, sha256}. **Current #40 disposition:** retain the packaging distinction as research metadata; use the common per-component operator/capacity and connection-boundary representation rather than adopting a new hosting category or trust/egress proxy.
5. Refine `auth_methods`:
   - distinguish `mcp_oauth` (MCP authorization, client to server) from upstream credentials;
   - add `client_registration` ∈ {pre_registered, cimd, dcr} and `auth_extensions`;
   - add `required_scopes` (`spec_tool` has this field; `spec_mcp_server` does not).
6. Add `spec_mcp_server.read_only_mode_supported: boolean`.
7. Original framework field proposals: `mcp_client_transports`, `mcp_protocol_versions`, `mcp_client_capabilities`, `mcp_oauth_modes` ∈ {interactive, token_injection, none}, `mcp_auth_extensions`, `mcp_runtime` ∈ {in_process, provider_hosted}. The current dispositions require these facts to be bound to a selected client/connection, with explicit non-interactive and acquisition/continuation evidence; those coarse enums are not exhaustive or sufficient. A direct SDK/no-framework client also needs a representation.
8. Rules need per-selection iteration (for example "for each mcp_server selection") or a metric such as `mcp.untrusted_count`. Otherwise the six v1 rules above are `skipped` when several enabled MCP servers share role `primary`, rather than checking each server.
9. Extend the metric `tools.mutating_count` to include MCP server tools, or add `mcp.mutating_server_count`.
10. The [actual #41 receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6242626857) accepts capture dates for unversioned hosted-service facts using the existing string `version`. Retain the selected snapshot; a later observation alone does not invalidate a build. Multi-version intake and successor encoding remain separate #40 work.
11. Bind authorization and direct stdio prerequisites to the actual connection, client/runtime, endpoint/operation and relevant configuration. The [authorization disposition](#rulet4mcpauthflow-available-compatibility-example-4-needs-contract-change-via-40-source-checked-unverified-premise) supplies typed evidence inputs and synthetic outcome cases; it replaces target-type, single-method-array and secret-reference shortcuts. The [stdio disposition](#rulet4mcpstdiocolocation-compatibility-example-4-needs-contract-change-via-40-source-checked-unverified-premise) replaces the build-mode proxy. Adopt encoding and migration centrally, preserving historical v1 results.

## Security and trust findings (for #35; findings only, controls belong to #35)

| Risk | Finding | Evidence |
| --- | --- | --- |
| Untrusted servers and tool-description manipulation | The specification's explicit untrusted-unless-trusted rule addresses annotations. Tool descriptions and changed definitions create a separate prompt-injection risk when exposed to the model; treating them as untrusted data and invalidating stale approval is the accepted #35 project-policy inference. `listChanged` is a change notification, not authority to expose a new tool or a guarantee of current definitions. | C15, C16, C18; [description follow-up](../T6-deployment-operations/guardrails.md#mcp-description-and-tool-list-change-follow-up-2026-10-18) and [current receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6251677799) |
| Prompt injection through returned content | Clients SHOULD validate tool results before passing them to the LLM. Browsing and fetch servers return arbitrary web content (Playwright is "not a security boundary"). Stripe warns about prompt injection when combining servers. | C15, C45, C48 |
| Excessive permissions | Scope minimization guidance (avoid omnibus scopes; incremental step-up). Stripe agent keys should have only the needed permissions. The Sentry stdio token needs write scopes. GitHub PAT minimum scopes. | C14, C42, C48, C50 |
| Unauthorized side effects | Spec: a human in the loop SHOULD be able to deny tool invocations. Stripe requires out-of-band human confirmation for some writes. GitHub `--read-only`. DBHub read-only mode. | C15, C42, C48, C53 |
| Remote server impersonation | Registry namespace checks cover the publisher, not the code or the remote URL. Third-party proxies (Smithery) republish vendor functionality under their own namespace with their own key. Lookalike names exist. | C20–C22, C25, C30 |
| Credential disclosure | HTTP MCP token audience and downstream-token separation are required; query strings must not carry access tokens. URL-mode elicitation keeps its sensitive exchange outside the MCP client. Sentry's documented `Sentry-Bearer` path forwards an upstream token; the separately dated policy assessment below rejects that path for the project's audience-bound HTTP requirement. `x-mcp-header` exposes parameters to intermediaries. | C12, C14, C17, C9, C50; C66, C72, C73 |
| Confused deputy (proxy servers) | MCP proxies with static client IDs MUST implement per-client consent. | C14 |
| SSRF | Malicious servers can point OAuth discovery URLs at internal or metadata endpoints. Clients SHOULD block private ranges and use egress proxies. The fetch reference server blocks private IPs by default but not DNS rebinding. | C14, C37 |
| Session or state hijacking | 2026-07-28 has no sessions. State handles MUST NOT be treated as authentication. Legacy `Mcp-Session-Id` guidance sits on the 2025-11-25 page (not fetched). | C14 |
| Local server compromise | One-click local configuration MUST show the full command and get explicit consent. SHOULD sandbox. Local HTTP servers SHOULD bind localhost and validate `Origin` (DNS rebinding). | C9, C14 |
| Lifecycle and update risk | `npx @playwright/mcp@latest` and `uvx mcp-server-fetch` in vendor docs resolve to the newest version on every launch. Registry versions are immutable but packages are pulled by tag. OCI tags can move unless a digest is pinned. MCPB carries `fileSha256`. Hosted remotes change silently (Atlassian moves v1 users to v2 tools on 2027-03-01; Stripe stops accepting legacy keys in December 2026). | C22, C24, C45, C48, C49 |
| Third-party data egress | Sentry AI search tools call an external LLM provider. Atlassian calls consume Rovo credits (cost). | C49, C50 |
| Licensing | Sentry MCP source is FSL-1.1-ALv2 (source-available, converts to Apache-2.0 later), not OSI open source. The reference servers carry mixed MIT and Apache-2.0 terms during relicensing. | C34, C51 |

### Trust level criteria (proposal; v1 enum)

| trust_level | Criteria (all must hold) |
| --- | --- |
| `internal` | Operated by the user's organisation on its own hosting platform or local machines, from source or images it controls (pinned version or digest), and reachable only inside its trust boundary |
| `trusted_external` | Maintained by the vendor of the upstream API, or by a named organisation (MCP steering group, Microsoft, Bytebase); publisher identity source-checked through the official registry namespace or the vendor's own documentation; public source or vendor-operated endpoint; active releases within about 90 days |
| `untrusted_external` | Anything else: unverified namespace, third-party proxy of another vendor's API, or archived or unmaintained |

Trust level does not make returned **content** trusted: Playwright and fetch are `trusted_external` yet return untrusted web content. #35 should treat tool output as untrusted regardless of `trust_level`.

### Sentry token-path policy assessment (2026-10-18)

C72 distinguishes MCP OAuth `Bearer` from custom `Sentry-Bearer`, which forwards
an upstream Sentry API token without worker validation, exchange or renewal.
C66/C73 require MCP-resource audience validation and reject token passthrough.
The [actual #35 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6251677799)
therefore rejects the described custom path for this project's audience-bound
HTTP MCP authorization requirement. A different scheme name does not establish
the missing validation or token separation. This is a source-based project
policy decision, not a deployed vulnerability finding or executed negative test.

The documented MCP OAuth path remains a separate candidate, needing its own
eligible issuer/resource/scope and acquisition/continuation evidence. Local stdio
has its separate environment-credential boundary. No account, token or live
Sentry operation was exercised. C50 remains the original dated observation;
this review does not silently replace its source date or qualify a deployed
version.

## Pricing and capacity

No Pricebook is proposed. Keep package licensing, host/runtime charges and
upstream-service prices separate in #39; a package classification cannot establish
the total cost of a selected deployment. Pricing units observed, for #39:
- Atlassian Rovo MCP calls consume Rovo credits, varying with "data volume, reasoning depth, and per-call limits" (C49). Rate not fetched.
- GitHub remote server billing was not determined (it is served from `api.githubcopilot.com`; billing ties to Copilot plans are unknown).
- Stripe and Sentry MCP pricing was not stated on the pages read. Underlying API charges, included allowances and billing conditions were not established here and remain unknown inputs for #39.

Prices are unknown, not zero.

## Recommendation and rationale

1. **Track protocol versions, not just transports.**
   - Catalog every server with its revision set and era.
   - When the intended server set spans legacy and modern revisions, require evidence for both paths in the chosen client/configuration. The inspected TypeScript 1.32.1 and Python 1.30.0 artifacts are legacy, while the pinned Python 2.3.0 follow-up supports modern operation and conditional legacy fallback (C31, C32, C60–C65). Do not generalize those artifacts to every release, server or framework.
2. **Prefer Streamable HTTP or stdio packagings.** Mark `sse` as deprecated with a warning (rule above).
3. **Record the actual MCP placement and connections.** The local-process, self-hosted-remote and vendor-hosted-remote taxonomy describes candidate packaging. Use the accepted per-component deployment model and W-R8/CD-4 isolation evidence; no category, trust label or model-serving mode proves subprocess support, public egress, private reachability or artifact readiness. Reuse #9 identities only where eligible records exist.
4. **Show auth as a requirement profile, not a flag.** For each server, show:
   - whether MCP OAuth is required, and with which client registration (pre-registered, CIMD or DCR, with DCR deprecated);
   - whether a static-token fallback exists;
   - which accepted acquisition and continuation paths fit the intended operation, including applicable client credentials, application-owned acquisition or existing-token use, with renewal assessed separately;
   - which scopes are needed.
   Check that profile against the selected client/connection and operation/lifecycle scope (rule `auth.flow-available`), with the #35 Sentry token-path disposition above.
5. **Trust:** use the criteria above. Default unknown to `untrusted_external`. Never infer trust from presence in a registry or marketplace.
6. **Reference servers:** list them for learning and testing only. Mark them "not production-ready" and do not recommend them as production defaults (C33).

## Structured artifacts

Catalog proposals (all `kind: mcp_server`, validated):
- `catalog/proposals/t4c-github-remote.json`
- `catalog/proposals/t4c-github-local.json`
- `catalog/proposals/t4c-playwright.json`
- `catalog/proposals/t4c-stripe-remote.json`
- `catalog/proposals/t4c-sentry-remote.json`
- `catalog/proposals/t4c-atlassian-remote.json`
- `catalog/proposals/t4c-dbhub.json`
- `catalog/proposals/t4c-reference-fetch.json`
- `catalog/proposals/t4c-reference-filesystem.json`

Notes on these proposals:
- **v1 workaround:** one item per transport packaging (`github-remote` vs `github-local`), because `spec_mcp_server.transport` is single-valued.
  - Playwright and DBHub record only stdio; their HTTP packagings are described in the item description and this note.
  - Sentry's stdio package is not given its own item.
- `tool_refs` is omitted because no `tool` items are proposed in these files.
- `license` is set only where a LICENSE file was read and is a single SPDX licence: GitHub MIT, Playwright Apache-2.0, DBHub MIT. It is omitted for hosted remotes, for the reference servers (mixed licensing) and for Sentry (FSL; the SPDX id and commercial terms were not reviewed).
- `billing_class` is `metered` for Atlassian (Rovo credits), `free` for open-source local servers, and `unknown` elsewhere.
- Not proposed:
  - reference `git`, `memory` and `everything` (note only);
  - Stripe's local package (not researched);
  - Cloudflare (the public documentation endpoint now has a [bounded follow-up](cloudflare-docs-mcp.md), without a catalog proposal; other Cloudflare product servers remain outside it);
  - Notion and Linear (not researched in this pass).

## Open questions and handoffs

| Question / handoff | Follow-up issue / owner |
| --- | --- |
| Field-level contract changes 1–11 above; rule ids and severities | #40 · @tynamite |
| Which protocol revisions, transports, client capabilities and OAuth modes each framework's MCP client supports (fields `mcp_client_transports`, `mcp_protocol_versions`, `mcp_client_capabilities`, `mcp_oauth_modes`); LangChain SSE and OAuth pages; OpenAI Agents SDK sampling and elicitation | #25 · @CompleteDotTech |
| Trust/auth research handoff is [accepted with its actual policy interpretation](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6251677799), including description/change review, operation-level permission, audience separation, local consent and isolation. The Sentry raw-token question is dispositioned above. Selected-control configuration/enforcement, exact refresh policy and successor representation remain receiving work; a secret reference or research prerequisite pass does not authorize an action | #35 · @PUSHINGSQUARES / @appletechie |
| Deployment handoff is [accepted for readiness design](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/37#issuecomment-6251683433): bind stdio launch/stream/lifecycle and authorization acquisition/continuation to the selected connection; apply W-R8/CD-4 to actual connections/artifacts. Actual target configuration, containment, token tests and deployment/rollback evidence remain separate | #37 · @PUSHINGSQUARES / @appletechie |
| Hosting: retain the original `hosting_type` examples above as candidate descriptions. The [current isolation disposition](#rulet4mcpremoteair-gapped-hypothesis-compatibility-example-4) uses per-component boundary, connection/lifecycle and artifact evidence; a new hosting category or `allows_public_egress` flag alone cannot decide air-gap compatibility. Final encoding adoption and source admission remain with #40/#41 | #9 · @Mattycodes69 |
| Overlap with tools: map MCP server tools to `tool` items (`tool_refs`) for side-effect counting | #26 · @CompleteDotTech |
| Pricing units for Atlassian Rovo credits and the GitHub remote server (Copilot plan dependency) | #39 · @PUSHINGSQUARES |
| Freshness policy for hosted remotes whose behaviour changes without a version; registry preview status | #41 · @tynamite |
| Candidate-by-candidate 2026-07-28 (`server/discover`) and client/transport qualification; the [Cloudflare documentation observation](cloudflare-docs-mcp.md) covers only its named dated tuples | #27 · @CompleteDotTech |
| Atlassian admin controls (IP and domain allowlists) and whether `/v1/sse` still exists; Stripe local package; other Cloudflare product servers, its unobserved legacy-GET migration response, Notion and Linear remote servers | #27 · @CompleteDotTech |

The incoming #9 hosting/network boundary is accepted with constraints by #27 ([owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072)); its reciprocal #27-to-#9 interface has [Mattycodes69's](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245204225) and [appletechie's](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6245668047) actual constrained acceptance. Internal T4 handoffs are [accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509). The current #35/#37 decisions above complete #27's two declared downstream research handoffs. They are CompleteDotTech's present decisions under the user's delegated engineering authority, without attributing another response to either T6 co-owner. The [workstream handoff matrix](README.md#dependency-and-handoff-matrix) retains earlier scoped replies and separate work from other T4 producers; the dated assessment here supplies the later #27 disposition.

## Research completion assessment (2026-10-18)

This assessment preserves the nine original criteria on #27. It concerns the
representative research deliverable and its receiving interfaces. The issue
explicitly distinguishes research completion from builder implementation; it
does not require runtime certification of every possible vendor/client tuple.
Unresearched candidates and selected-build evidence requirements remain named
above rather than being assigned invented results.

| Original criterion | Delivered evidence and disposition |
| --- | --- |
| Client/framework-to-server compatibility rules in #40 format | The shared-format rule sections provide participating inputs, applicability, assertion, outcome/missing-data handling, severity, remediation and examples. Six original JSON proposals retain their v1 limits; successor transport/protocol/capability/auth/locality inputs are explicit note-only proposals. The [actual #40 queue receipt](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40#issuecomment-6242626523) accepts and narrows the interface; it does not adopt a final DSL. |
| Trust and auth requirements handed to #35 | The risk/criteria table, description-change follow-up and source-backed Sentry assessment are covered by the [current #35 receiving decision](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/35#issuecomment-6251677799), alongside the original two co-owner receipts. |
| Canonical decision record merged following the research method | #71 delivered this path and nine catalog proposals. Its [independent approval at `3d95c61`](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/71#pullrequestreview-5557512959) verified the provenance correction and exposed the single-primary limitation. #272/#277/#281/#308/#352 supplied separately reviewed follow-ups. Final completion depends on independent review and merge of this assessment. |
| Candidate set covers API / managed / self-hosted or explains applicability | Twelve representative server rows and the provider-hosted client interface cover local processes, independently hosted services and vendor endpoints. The opening taxonomy explicitly considers each serving mode without treating MCP placement as its determinant. Python and Cloudflare observations add bounded execution; other tuple results remain unknown. |
| Comparison fields with type, unit and evidence requirement | The comparison table maps all eight minimum issue fields and additional trust/pin/selection inputs to v1 or explicit proposed types. Protocol revisions, identity, transport, capabilities, auth and hosting each retain sources and conditions; missing fields are not invented in JSON. |
| Shared rule format; verified rules separated from hypotheses | The rule summary separates source-checked/unverified premises, policy hypotheses and historical proxies. Current dispositions specify evidence eligibility and completeness on the same selected connection. No source-only claim or synthetic fixture is promoted to independent runtime verification. |
| Primary sources, access dates and applicable versions/conditions | C1–C73 and the separate pinned Cloudflare record identify source, access date, version and claim boundary. Package/runtime observations retain their exact identities and conditions. Unsupported population and billing assertions were removed; unresearched prices remain unknown rather than zero. |
| Every declared downstream handoff confirmed | #35 and #37 are the two consumers listed in #27's Dependencies table; both have actual current receiving decisions linked above. Hosting is also accepted in both directions; [#41 accepts](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41#issuecomment-6242626857) grading, snapshot and source-specific rights semantics. No technical receipt grants publication rights or claims a deployed result. |
| Open questions recorded with named follow-up owners | The table above retains #25 client-feature research, #27 future candidate/tuple qualification, #35/#37 configured controls and deployment evidence, #39 prices, and #40/#41 representation/source intake. These follow-ups do not replace missing acceptance evidence with an assumed pass. |

Final review must inspect this assessment and the changed technical dispositions,
then apply the repository's required validation and closing-directive checks to
the exact PR. Successful validation establishes repository structure and
mechanics; it is separate from source review, rights and real runtime evidence.

## Limitations

- modelcontextprotocol.io, github.com (pages and release feeds), unpkg and jsDelivr refused direct `curl` through the proxy. Those pages were read with a fetch tool that returns extracted text, so quotations are as extracted.
- The GitHub `/releases` list page returned stale v1.11.0 entries. The tags page was blocked by robots rules.
- Registry search queries were slow, and one timed out. Exact-name lookups worked.
- No server, SDK or framework was executed in the original 2026-10-16 desk study. The follow-up below adds local synthetic-peer SDK execution; the separate [Cloudflare documentation record](cloudflare-docs-mcp.md) adds narrowly scoped public-endpoint execution. Other candidate-server tuples and agent frameworks remain unexecuted here.

## Pinned Python SDK protocol follow-up (2026-10-18)

This closes the narrow source-inspection gap in the Python 2.3.0 paragraph. It
does not complete #27's candidate coverage, trust/auth handoffs or #40 contract
decisions. The supported-version fields still require the reviewed next version;
no frozen schema, catalog item or provenance grade changes here.

### Exact source and package identity

C60–C65 identify the publisher's versioned artifacts. Downloaded wheel sizes and
SHA-256 values matched the versioned PyPI JSON responses. All installed Python
source files also matched their corresponding downloaded wheels: 110 in `mcp`
1.30.0, 124 in `mcp` 2.3.0 and eight in `mcp-types` 2.3.0. These are observed
artifact-integrity checks, not independent confirmation of every SDK capability.

| Package | Wheel bytes | SHA-256 | External artifact manifest |
| --- | ---: | --- | --- |
| `mcp==1.30.0` | 234581 | `666edb5009503e1047c9d60346a756f94b261f05cc2625f23d41c728ffc484d0` | [Legacy SDK](../../evidence/t4-mcp-1300-wheel.json) |
| `mcp==2.3.0` | 368664 | `dd0c44c089d16453e8ae31a3877a0054d7a2314caaa81f5e0541b9b1734b2377` | [Current SDK](../../evidence/t4-mcp-230-wheel.json) |
| `mcp-types==2.3.0` | 69108 | `968efdbdaedfab06adae40d378a34395f1090c5921d4be3c9cde283aaf76d91d` | [Wire types](../../evidence/t4-mcp-types-230-wheel.json) |

The [preparation receipt](../../tests/fixtures/mcp-protocol-2026-10-18/preparation.json)
retains inspected file hashes and resolved dependency-lock identities. The type
registry, high-level client and automatic negotiation modules also match the
corresponding Git blobs at publishing revision `2118f14f8a19bc158d8a1cf90af58d85d187f849`.
The publisher identifies the packages as MIT; no package binary or third-party
source is copied into this repository.

C62 enumerates known revisions rather than comparing arbitrary date strings.
`LATEST_HANDSHAKE_VERSION` is `2025-11-25`, `LATEST_MODERN_VERSION` is `2026-07-28`,
and the deprecated `SUPPORTED_PROTOCOL_VERSIONS` constant is the union of both
sets. Reading that union alone cannot establish the selected connection mode.
C63's `auto` mode probes discovery; C64 may fall back to the legacy handshake.
A disjoint modern-only peer remains an error, while non-RPC transport exceptions
propagate. A modern revision passed directly as `mode` instead adopts local
state without a probe. A reported adopted version therefore is not evidence of
a successful peer exchange.

### Actual local synthetic-peer observation

The [opt-in reproduction](../../tests/reproduce_mcp_protocols.py) launched real
SDK server subprocesses over stdio in two isolated CPython 3.12.14 environments
on Linux x86_64. Each peer exposed one synthetic echo function and returned its
actual installed SDK version with the fixed test text. Every successful row
required a real tool listing and matching echo response. No catalog vendor,
framework, HTTP transport, OAuth flow, Roots, Sampling or elicitation was tested.

| Client SDK | Peer SDK | Client mode | Observed exchange |
| --- | --- | --- | --- |
| 1.30.0 | 1.30.0 | Legacy `ClientSession` | Tool listing and echo passed at `2025-11-25` |
| 1.30.0 | 2.3.0 | Legacy `ClientSession` | Tool listing and echo passed at `2025-11-25` |
| 2.3.0 | 1.30.0 | `auto` | Fallback exchange passed at `2025-11-25` |
| 2.3.0 | 2.3.0 | `auto` | Modern exchange passed at `2026-07-28` |
| 2.3.0 | 2.3.0 | `legacy` | Tool listing and echo passed at `2025-11-25` |
| 2.3.0 | 1.30.0 | Explicit `2026-07-28` | RPC failed with `MCPError` code `-32602`; no successful listing/echo or negotiated revision recorded |

The [original recorded matrix](../../tests/fixtures/mcp-protocol-2026-10-18/observation.json)
binds these observations to the [original reproduction](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/5faa554a6f9ecebdba17186d07fe053f99ca6e94/tests/reproduce_mcp_protocols.py)
hash. The later cleanup correction below has its own replay; the original record
and dependency/source preparation remain unchanged. The last row exercises
an explicit-modern RPC against a legacy peer; it is not an automatic-negotiation
failure. The five success rows cover two observed revisions, not execution of
all five revisions listed in the source registry.

An earlier [restricted-host trial](../../tests/fixtures/mcp-protocol-2026-10-18/host-restricted-trial.json)
recorded six request timeouts, including the same-version controls. That trial
used the initial observation helper before script-hash and matrix-expectation
instrumentation. It is retained as an unqualified host observation, not evidence
of protocol incompatibility. Repeating with working process isolation produced
the matrix above. The [offline guards](../../tests/test_mcp_protocol_observation.py)
reject those timeouts, wrong peer/revision bindings, diagnostic output and
locally adopted versions without a successful exchange. Passing these guards
checks record interpretation; it does not rerun SDK processes.

### Reproduction and remaining coverage

Create two separate Python 3.12 environments and install the exact wheel locks
for this Linux x86_64 observation, using PyPI and `--require-hashes --only-binary=:all:`:
[v1 lock](../../tests/fixtures/mcp-protocol-2026-10-18/requirements-v1.txt) and
[v2 lock](../../tests/fixtures/mcp-protocol-2026-10-18/requirements-v2.txt).
Package acquisition uses the network; the experiment itself configures only
local stdio peers, with a small explicit environment and no authentication.
From the repository root, supply those environments' Python executables:

```sh
python tests/reproduce_mcp_protocols.py --observe /path/to/v1/bin/python /path/to/v2/bin/python
python -m unittest discover -s tests -p test_mcp_protocol_observation.py -v
python -m unittest discover -s tests -p test_mcp_worker_cleanup.py -v
```

The observer uses five-second read deadlines and a 20-second worker deadline;
an unexpected matrix result exits nonzero. A process/setup failure is not a
compatibility verdict. The SDK's context managers own peer shutdown during
normal and error unwinding. No peer remained after the original normal/error
runs, but a separate disposable sleeping-peer reproduction demonstrated that
the original outer deadline could kill/reap its worker while leaving a live peer.

### Linux probe lifetime correction (2026-10-18)

The current observer requires Linux and fails before launching an observation
worker on another platform. Each worker starts in its own session; a timeout or
exception path kills only its still-unreaped owned group, waits up to five seconds to
reap the worker and closes its pipes without a second potentially unbounded drain.
It does not signal a group after the leader has already been reaped.

The pinned SDKs also create the stdio peer in a **separate session**. This was
inspected in the original verified wheels at `mcp/client/stdio/__init__.py`
(1.30.0) and `mcp/client/stdio.py` (2.3.0); a worker-group signal alone cannot
terminate that peer. The fixed synthetic peer therefore installs Linux
`PR_SET_PDEATHSIG` with `SIGKILL` before loading the SDK. Both worker and peer
receive their exact expected parent PID and check it before and after installing
the guard. Invalid/stale parents and syscall failure stop setup. This closes the
registration race documented by the [Linux manual](https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html)
(inspected 2026-10-18): the signal is not retroactive when the creating parent
thread has already died. The [Python subprocess documentation](https://docs.python.org/3.12/library/subprocess.html#subprocess.Popen)
(inspected 2026-10-18) supplies the session, timeout and reaping API semantics.

Four offline lifecycle methods include two actual timeout topologies: an inherited
worker group and an independently sessioned peer with the lifetime guard. The
peer writes readiness only after setup; the regression checks its parent/group
identity, its `SIGKILL` exit, an already-reaped worker and an unaffected unrelated
sentinel. The test process temporarily adopts/reaps its own fixture orphans and
restores that process-local setting. Failure cleanup signals only a verified
unreaped direct/adopted child. Invalid parent types, changed-parent setup and
syscall/platform failures have separate guards; no MCP installation is needed
for these lifecycle tests.

The [new six-case SDK replay](../../tests/fixtures/mcp-protocol-2026-10-18/cleanup-observation.json)
was captured at **2026-10-18 07:45:19 UTC** with the unchanged pinned environments.
Its current-script hash is independently checked by the observation tests. All
five successful exchanges and the explicit-modern `-32602` failure remain the
same, with zero worker stderr and exit code zero in all six rows. An independent
reviewer also reran the six-case matrix and the four lifecycle methods.

The production claim is termination of this fixed Linux peer plus worker reaping.
It is not a generic process-tree supervisor: the parent-death setting is not
inherited across fork and can be cleared by credential changes; arbitrary peer
children and other platforms remain unqualified. Reaping a terminated orphan
normally belongs to the host init/subreaper; the observer itself does not become
a subreaper. The standard research requirements and automatic CI do not install
the optional SDK environments. No vendor endpoint, authentication or catalog
qualification is added by this correction.

### Lifecycle fixture startup boundary (2026-10-18)

A later required repository run exposed a separate test-fixture error: the
two-second timeout could kill the worker before its independently sessioned peer
finished importing the observer and wrote its post-guard readiness record. The
test then errored on the absent readiness file. A deliberate 2.25-second peer
startup delay reproduced that error through the actual `observe()` path; this
does not demonstrate a failure of the unchanged observer's cleanup implementation.

The offline regression now gives fixture startup a bounded 15-second budget and
checks the recorded worker/peer/parent/group identities before starting the
existing two-second cleanup deadline. The separate-session case retains that
delayed-start control. The actual timeout must still kill the owned peer with
`SIGKILL`, reap its worker, permit reaping of the adopted peer and leave the
unrelated sentinel running. Readiness failure remains a test failure, and the
existing owned-child cleanup and restored subreaper state remain required.

This changes the test fixture, not `run_worker()`, the observer's normal
20-second worker budget, the pinned SDK replay or any server-compatibility claim.
The original failed run and delayed-start control remain distinct from the
corrected lifecycle tests; no SDK exchange is newly attributed to this repair.

The selected-tuple follow-up for #25/#27 is to bind a client/framework, server artifact,
transport and authentication configuration to an eligible actual exchange.
This local experiment supplies no such vendor tuple and does not infer the
capabilities of servers from their SDK dependency. External receiving-owner
dispositions retain their actual scopes in the
[research completion assessment](#research-completion-assessment-2026-10-18);
that completed research does not qualify unexamined runtime configurations.
