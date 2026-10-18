# T4: MCP Servers

Issue: #27 · Contract: 1.0.0 · Kinds: `mcp_server`
Status: research merged via #71; owner handoffs and contract proposals remain open · Reconciled: 2026-10-18 (bounded Python SDK and public Cloudflare documentation follow-ups)

## Evidence status correction

Evidence metadata corrected at 2026-10-17T02:17:46Z under the [adopted #41 interim policy](https://github.com/Pick-Your-AI/pick-your-ai-research/pull/75#pullrequestreview-5550616927). Checked primary documentation, publisher package metadata, registry entries and source inspection are not independent verification. These catalog claims remain `unverified`; the original facts, versions, source access dates and `checked_at` are unchanged. No qualifying independent corroboration or runtime reproduction was supplied. Vendor capability statements remain documented claims, not measurements.

A proposed constraint may pass on eligible, versioned documentation while its evidence remains unverified. Missing eligible evidence remains unknown; absence from an unmarked capability list does not establish lack of support. Synthetic evaluator results check rule mechanics only and do not verify product behaviour. All rules and contract changes still require central versioned review through #40. Receiving-owner handoffs remain pending and this correction does not satisfy issue completion.

`trusted_external` is a proposed project classification under the criteria in this note, pending #35/#40 review. Registry presence and namespace/package identity checks do not certify security, safe code, benign tools or independently verified behaviour. The catalog value is not a security certification.

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

Deployment modes covered (the v1 `spec_deployment_mode.mode` enum is `api`, `managed`, `self_hosted`, `hybrid`):

| Packaging | What runs where | Fits mode | Notes |
| --- | --- | --- | --- |
| **Local stdio** | The MCP client launches the server as a subprocess on the same host (C10) | `self_hosted`, `hybrid`; `managed` only if the managed agent runtime can spawn processes (unknown per platform) | Credentials come from the environment, not MCP authorization (C12) |
| **Self-hosted remote** (Streamable HTTP) | The organisation runs the server on its own hosting platform | `self_hosted`, `hybrid`, `managed` | Needs a #9 `hosting_platform` with `hosting_type` `cloud`, `on_prem`, `edge` or `colocation` |
| **Vendor-hosted remote** (Streamable HTTP) | The API vendor runs the endpoint (GitHub, Stripe, Sentry, Atlassian) | all modes, including `api` | Maps to #9 `hosting_type` `managed_api` if modelled at all. Needs public egress and usually OAuth 2.1 |
| **Provider-hosted connector** | The model provider calls the remote server from its own infrastructure (OpenAI `HostedMCPTool`, C56) | `api` | The server must be publicly reachable from the provider. stdio is impossible |

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

**Ecosystem state today (source-checked from SDK artifacts, C31, C32):**
- The TypeScript SDK `@modelcontextprotocol/sdk` 1.32.1 (2026-10-05) sets `LATEST_PROTOCOL_VERSION = '2025-11-25'` and supports 2024-10-07 to 2025-11-25. A separate module declares `DRAFT-2026-v1`.
- The Python SDK `mcp` 1.30.0 supports 2024-11-05 to 2025-11-25 only. The 2026-10-18 pinned follow-up now inspects `mcp` 2.3.0 and its exact dependency `mcp-types==2.3.0`: the registry lists four handshake revisions (`2024-11-05`, `2025-03-26`, `2025-06-18`, `2025-11-25`) and one modern revision (`2026-07-28`). C60–C65 and the [local SDK observation](#pinned-python-sdk-protocol-follow-up-2026-10-18) replace the earlier uninspected-registry uncertainty; they do not establish the protocol set of any selected vendor server.
- The reference servers pin the legacy SDK lines: `mcp-server-fetch` and `mcp-server-git` require `mcp<2,>=1.29.0`, and `server-filesystem`/`server-everything` 1.0.0 require `@modelcontextprotocol/sdk ^1.31.0` (C36, C38, C39, C41).

**Consequence:** a protocol-version field is mandatory. A client that implements only 2026-07-28 cannot use most servers published today. "Supports MCP" (the v1 boolean) is not enough to predict compatibility.

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
| `mcp_server.dbhub` (database) | Bytebase | 1.5.0 (2026-10-09) | MIT | stdio; HTTP via `--transport http` | local or self-hosted | none for MCP; DB credentials in DSN | tools `execute_sql`, `search_objects`, opt-in `explain_sql`, `health_check`, custom SQL tools; read-only mode | npm `mcpName` `io.github.bytebase/dbhub` (registry not checked) | C53–C55, C59 |
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

Original sources C1–C59 were accessed 2026-10-16. The separately dated C60–C65 follow-up was accessed 2026-10-18.
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

## Compatibility proposals

These rules are proposed for review by #40.
- **Source-checked (unverified):** the rule's factual premise is primary-source backed; it has not been independently reproduced.
- **Hypothesis:** the rule depends on a policy choice, a proxy field or a field that v1 lacks.
- Outcomes are `pass/fail/unknown/skipped`. Severity is a separate field.
- The JSON blocks below were validated together as a ruleset against `contracts/v1/schemas/ruleset.schema.json`. They were also run through `contracts/v1/reference/evaluate.py` on a synthetic, unsaved build (GitHub remote + air-gapped hosting), which produced the expected `fail` for the air-gap rule.

**Relation to the baseline:**
- `rule.agent.mcp.framework` checks only `agent_framework.spec.supports_mcp`. That boolean cannot express transport, protocol era, auth flow or client capabilities. The rules below **extend** it and do not replace it. The boolean should be kept as a coarse gate until the #40 fields exist.
- `rule.tool.mutation.guardrails` is gated on the metric `tools.mutating_count`. The reference evaluator counts only selections of kind `tool`, so **MCP server tools are invisible to it** (problem flagged). `rule.t4.mcp.mutation.guardrails` closes this gap for v1.
- **All `role: primary` refs resolve only when exactly one active selection matches.** With two or more enabled MCP servers sharing role `primary`, those references are ambiguous. The six v1 rules below guard applicability with `exists` on that selection; the guard is false and each rule is `skipped`, so the servers are not checked individually. Per-server iteration needs a contract change (#40).

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

- **Premise:** MCP servers commonly expose mutating tools: Stripe `stripe_api_write` (C48), GitHub write tools unless `--read-only` (C42), memory `delete_entities` (C40), DBHub `execute_sql` unless read-only (C53, C59).
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
- **Assertion:** the two sets intersect. Otherwise the outcome is `fail`/error with remediation "choose another packaging of the server, or a framework with that transport".
- **Source-checked (unverified) premise (C56–C59):**

| Framework (docs, 2026-10-16) | stdio | Streamable HTTP | HTTP+SSE | Provider-hosted remote | Status in rule terms |
| --- | --- | --- | --- | --- | --- |
| OpenAI Agents SDK (Python) | yes `MCPServerStdio` | yes `MCPServerStreamableHttp` | yes `MCPServerSse` (legacy) | yes `HostedMCPTool` | source-checked compatible for all three |
| Google ADK | yes `StdioConnectionParams` | yes `StreamableHTTPConnectionParams` | yes `SseConnectionParams` | not documented | source-checked compatible for all three |
| Claude Agent SDK | yes | yes (`type: "http"`) | yes (`type: "sse"`) | not applicable | source-checked compatible for all three |
| LangChain `langchain[mcp]` (beta) | yes (script path) | yes (http/https URL) | not on the page read | — | sse = unknown |

- **Examples (synthetic):**
  - Failing: a server with `transports=["sse"]` and a framework with `mcp_client_transports=["stdio","streamable_http"]`.
  - Unknown: LangChain with an SSE-only server.

```text
applies_when: exists selection mcp_server /id
assert: intersects(catalog mcp_server /spec/transports,                 # missing: array field (replaces single transport)
                   catalog agent_framework /spec/mcp_client_transports) # missing field on spec_agent_framework
on_unknown: block   severity: error
```

### rule.t4.mcp.protocol.era (needs contract change via #40, Source-checked (unverified))

The rule implements the C7 matrix.
- **Pass:** the version sets intersect, or either side is dual-era with a version shared with the other side.
- **Fail:** a modern-only client with a legacy-only server, or the reverse.
- **Unknown:** either side lacks version data.
- **Source-checked (unverified) facts:**
  - The legacy TypeScript SDK line supports up to 2025-11-25 (C31).
  - Python `mcp` 1.30.0 supports up to 2025-11-25.
  - The reference servers are pinned to those lines (C36, C38).
- **Framework version support:** [#25's pinned A86 follow-up](agent-framework.md#pinned-source-follow-up-2026-10-18) source-checks OpenAI Agents Python 0.24.0's support for MCP Python package v1/v2 and v2 auto negotiation with legacy fallback. This is conditional client implementation evidence, not an actually negotiated protocol set for a selected server. Other framework/protocol tuples and sampling/elicitation remain unknown where no eligible evidence was read.
- **SDK-only execution:** the [2026-10-18 stdio experiment](#pinned-python-sdk-protocol-follow-up-2026-10-18) observes this SDK pair's modern exchange and legacy fallback with a synthetic echo peer. It does not run the Agents framework, remote transports or a candidate catalog server.

```text
assert: intersects(catalog mcp_server /spec/protocol_versions,            # missing field
                   catalog agent_framework /spec/mcp_protocol_versions)   # missing field
on_unknown: block   severity: error
```

### rule.t4.mcp.client-capabilities (needs contract change via #40, Source-checked (unverified) premise)

- **Assertion:** the server's required client capabilities are a subset of the framework's supported client capabilities.
- **Premise:**
  - Servers can return `MissingRequiredClientCapabilityError` (C16).
  - The filesystem reference server exits at initialization when it has neither CLI directories nor client Roots support (C35).
  - Roots and Sampling are Deprecated (C11), so new frameworks may omit them.
  - OpenAI Agents SDK docs do not mention sampling or elicitation (unknown, C56). ADK docs mention resources but not prompts or sampling (C58).
- **Severity:** error. on_unknown review, because many servers degrade gracefully.

```text
assert: subset_of(catalog mcp_server /spec/required_client_capabilities,          # missing
                  catalog agent_framework /spec/mcp_client_capabilities)          # missing
```

### rule.t4.mcp.auth.flow-available (compatibility example 4; needs contract change via #40, Source-checked (unverified) premise)

- **Assertion:** when the server accepts only `oauth2`, the selected framework and deployment can complete an MCP OAuth flow:
  - an interactive flow with a user present, or
  - an injected, pre-obtained token, or
  - the OAuth Client Credentials extension for non-interactive targets (C19).
- **Source-checked (unverified) premise:**
  - The Claude Agent SDK "doesn't open a browser or run an interactive OAuth flow". The server reports `needs-auth`, and the app must obtain the token itself and pass it in `headers` (C59). This is **conditional**: it passes only with token injection.
  - The OpenAI Agents SDK page has no OAuth section. It accepts headers and an `httpx.Auth` (C56): **conditional**.
  - ADK lists an OAuth2 auth scheme with token refresh (C58): **source-checked compatible** at doc level.
  - LangChain links an Auth page covering OAuth 2.1 (not read): **unknown**.
  - Stripe, Atlassian and Sentry offer static-token fallbacks (C48–C50). Stripe connected-account calls do not support OAuth (C48).
- **Deployment-mode interaction:** a `deployment_target.target_type = batch_worker` has no user to complete a browser consent. With an OAuth-only server, the outcome must be `fail` unless the client-credentials extension or a stored refresh token is available.

```text
applies_when: catalog mcp_server /spec/auth_methods == ["oauth2"]
assert: any(
  contains(catalog agent_framework /spec/mcp_oauth_modes, "interactive")          # missing field
    AND catalog deployment_target /spec/target_type in ["application","api_endpoint"],
  contains(catalog agent_framework /spec/mcp_oauth_modes, "token_injection")
    AND exists(selection mcp_server /settings/credential_ref),
  contains(catalog mcp_server /spec/auth_extensions, "oauth-client-credentials") # missing field
    AND contains(catalog agent_framework /spec/mcp_auth_extensions, "oauth-client-credentials"))
on_unknown: block   severity: error
```

### rule.t4.mcp.stdio.colocation (compatibility example 4; needs contract change via #40, Source-checked (unverified) premise)

- **Assertion:** a stdio server requires an agent runtime that can spawn a local subprocess on the same host (C10).
- **Fails when:**
  - the framework call is provider-hosted, as with OpenAI `HostedMCPTool`, where the round trip happens in OpenAI infrastructure (C56), or
  - the deployment mode is `api` with no customer runtime.
- **Missing data:** a runtime-locality field on `agent_framework` or `deployment_target`.

```text
applies_when: catalog mcp_server /spec/transport == "stdio"
assert: catalog deployment_mode /spec/mode in ["self_hosted","hybrid","managed"]
        AND catalog agent_framework /spec/mcp_runtime != "provider_hosted"    # missing field
        AND catalog deployment_target /spec/can_spawn_processes == true       # missing field
```

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
4. Add `spec_mcp_server.hosting` ∈ {local_process, self_hosted_remote, vendor_hosted_remote}, `maintainer`, `registry_name`, and a package pin {registry_type, identifier, version or digest, sha256}.
5. Refine `auth_methods`:
   - distinguish `mcp_oauth` (MCP authorization, client to server) from upstream credentials;
   - add `client_registration` ∈ {pre_registered, cimd, dcr} and `auth_extensions`;
   - add `required_scopes` (`spec_tool` has this field; `spec_mcp_server` does not).
6. Add `spec_mcp_server.read_only_mode_supported: boolean`.
7. Add to `spec_agent_framework`: `mcp_client_transports`, `mcp_protocol_versions`, `mcp_client_capabilities`, `mcp_oauth_modes` ∈ {interactive, token_injection, none}, `mcp_auth_extensions`, `mcp_runtime` ∈ {in_process, provider_hosted}.
8. Rules need per-selection iteration (for example "for each mcp_server selection") or a metric such as `mcp.untrusted_count`. Otherwise the six v1 rules above are `skipped` when several enabled MCP servers share role `primary`, rather than checking each server.
9. Extend the metric `tools.mutating_count` to include MCP server tools, or add `mcp.mutating_server_count`.
10. Multi-version intake: hosted remotes change without notice, so `version` needs a "snapshot date" semantic (#41).

## Security and trust findings (for #35; findings only, controls belong to #35)

| Risk | Finding | Evidence |
| --- | --- | --- |
| Untrusted servers and tool-description manipulation | Annotations and tool descriptions are server-supplied and untrusted unless the server is trusted. `listChanged` lets a server change its tool list at runtime, so a reviewed tool set can change after approval (the "rug pull" pattern; the term is not used in the spec pages read). Tool descriptions are placed in model context, so a malicious description acts as prompt injection ("tool poisoning", also not a spec term). | C15, C16, C18 |
| Prompt injection through returned content | Clients SHOULD validate tool results before passing them to the LLM. Browsing and fetch servers return arbitrary web content (Playwright is "not a security boundary"). Stripe warns about prompt injection when combining servers. | C15, C45, C48 |
| Excessive permissions | Scope minimization guidance (avoid omnibus scopes; incremental step-up). Stripe agent keys should have only the needed permissions. The Sentry stdio token needs write scopes. GitHub PAT minimum scopes. | C14, C42, C48, C50 |
| Unauthorized side effects | Spec: a human in the loop SHOULD be able to deny tool invocations. Stripe requires out-of-band human confirmation for some writes. GitHub `--read-only`. DBHub read-only mode. | C15, C42, C48, C53 |
| Remote server impersonation | Registry namespace checks cover the publisher, not the code or the remote URL. Third-party proxies (Smithery) republish vendor functionality under their own namespace with their own key. Lookalike names exist. | C20–C22, C25, C30 |
| Credential disclosure | Token passthrough forbidden. Tokens never in query strings. URL-mode elicitation for secrets, so they never transit the client. **Sentry `Sentry-Bearer` forwards an upstream Sentry token the worker "does not store, validate, exchange, or refresh"; this needs a #35 review against the spec's "MUST NOT accept or transit any other tokens".** `x-mcp-header` exposes parameters to intermediaries. | C12, C14, C17, C9, C50 |
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

## Pricing and capacity

No Pricebook is proposed. The open-source servers are free software (compute cost falls on the host, #9/#10). Pricing units observed, for #39:
- Atlassian Rovo MCP calls consume Rovo credits, varying with "data volume, reasoning depth, and per-call limits" (C49). Rate not fetched.
- GitHub remote server billing was not determined (it is served from `api.githubcopilot.com`; billing ties to Copilot plans are unknown).
- Stripe and Sentry MCP pricing was not stated on the pages read. Underlying API usage is billed under each vendor's normal terms (not source-checked).

Prices are unknown, not zero.

## Recommendation and rationale

1. **Track protocol versions, not just transports.**
   - Catalog every server with its revision set and era.
   - Default the builder to require **dual-era** clients until the major SDK lines ship 2026-07-28. Today the TypeScript SDK 1.x and Python SDK 1.x lines, and the servers built on them, are legacy-only (C31, C32).
2. **Prefer Streamable HTTP or stdio packagings.** Mark `sse` as deprecated with a warning (rule above).
3. **Model hosting explicitly.** Use three categories: local process, self-hosted remote (needs a #9 hosting platform with `hosting_type` in cloud, on_prem, edge, colocation) and vendor-hosted remote (`managed_api` at most; usually no hosting selection, but requires public egress).
4. **Show auth as a requirement profile, not a flag.** For each server, show:
   - whether MCP OAuth is required, and with which client registration (pre-registered, CIMD or DCR, with DCR deprecated);
   - whether a static-token fallback exists;
   - whether a non-interactive path exists (client-credentials extension);
   - which scopes are needed.
   The builder then checks it against the framework's OAuth mode and the deployment target (rule `auth.flow-available`).
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
| Field-level contract changes 1–10 above; rule ids and severities | #40 · @tynamite |
| Which protocol revisions, transports, client capabilities and OAuth modes each framework's MCP client supports (fields `mcp_client_transports`, `mcp_protocol_versions`, `mcp_client_capabilities`, `mcp_oauth_modes`); LangChain SSE and OAuth pages; OpenAI Agents SDK sampling and elicitation | #25 · @CompleteDotTech |
| Trust and auth requirements handed over: the trust criteria table; the rule that tool descriptions, annotations and results are untrusted; human-in-the-loop for mutating tools; token passthrough prohibition and the Sentry `Sentry-Bearer` review; SSRF on OAuth discovery; local-server consent and sandboxing; pinning policy (no `@latest`, digest pins); guardrail policy mapping for `rule.t4.mcp.untrusted.guardrails` | #35 · @PUSHINGSQUARES |
| Deployment: stdio needs process spawning in the agent runtime; vendor remotes need public egress; non-interactive targets (`batch_worker`) cannot complete browser OAuth; `deployment_target` lacks runtime-locality and egress fields | #37 · @PUSHINGSQUARES |
| Hosting categories: self-hosted remote MCP servers fit `hosting_type` cloud, on_prem, edge, colocation; vendor-hosted remotes fit `managed_api` (or no hosting selection); an egress or `allows_public_egress` field is needed for the air-gap rule | #9 · @Mattycodes69 |
| Overlap with tools: map MCP server tools to `tool` items (`tool_refs`) for side-effect counting | #26 · @CompleteDotTech |
| Pricing units for Atlassian Rovo credits and the GitHub remote server (Copilot plan dependency) | #39 · @PUSHINGSQUARES |
| Freshness policy for hosted remotes whose behaviour changes without a version; registry preview status | #41 · @tynamite |
| Candidate-by-candidate 2026-07-28 (`server/discover`) and client/transport qualification; the [Cloudflare documentation observation](cloudflare-docs-mcp.md) covers only its named dated tuples | #27 · @CompleteDotTech |
| Atlassian admin controls (IP and domain allowlists) and whether `/v1/sse` still exists; Stripe local package; other Cloudflare product servers, its unobserved legacy-GET migration response, Notion and Linear remote servers | #27 · @CompleteDotTech |

The incoming #9 hosting/network boundary is accepted with constraints by #27 ([owner disposition](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/9#issuecomment-6233323072)). Internal T4 handoffs are [accepted with constraints](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/24#issuecomment-6233347509). External outgoing handoffs are partially received; the [workstream handoff matrix](README.md#dependency-and-handoff-matrix) retains the actual scoped replies, coverage objections and remaining adoption requirements.

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

The #25/#27 next step is to bind a selected client/framework, server artifact,
transport and authentication configuration to an eligible actual exchange.
This local experiment supplies no such vendor tuple and does not infer the
capabilities of servers from their SDK dependency. External receiving-owner
dispositions and complete issue acceptance remain open.
