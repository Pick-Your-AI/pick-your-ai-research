# Cloudflare public documentation MCP: dated source and endpoint observations

Refs #27 and #25. Source inspection and endpoint observations: 2026-10-18.
Status: partial research evidence; no catalog promotion or receiving-owner adoption.

## Decision and scope

Can the public Cloudflare documentation endpoint serve both the pinned legacy
and modern Python MCP clients without a Cloudflare customer account, and what
does its historical `/sse` URL mean?

The observed endpoint answered legacy and modern Streamable HTTP requests and
one fixed documentation search without credential headers. Its `/sse` URL also
answered modern Streamable HTTP requests. A separate legacy SSE GET returned
HTTP 403; the source's conditional 410 migration response was **not reproduced**.
These are the dated results below, not availability, search-quality or general
Cloudflare integration guarantees.

The endpoint probes contacted only `https://docs.mcp.cloudflare.com/mcp` and its `/sse` alias.
The probe contacted no customer-account or model-provider endpoint, performed
no login and invoked only the named public documentation search. The one search
sends a generic public documentation question to the provider. Provider search,
metrics and error reporting can still process that request; no customer-account
mutation is a narrower claim than an absence of all server-side effects. [CF-02–CF-07]

## Source identity and interpretation

The [source manifest](../../tests/fixtures/cloudflare-docs-mcp-2026-10-18/source-identity.json)
records ten raw files from upstream commit
`e4cf085520ea7286af77abf938d645c610ef1580`, tree
`b6b2aa67cd932bf2b11692a34779389ccaaf05a6`. Each file's bytes, SHA-256 and Git
blob identity were checked against the nontruncated immutable GitHub tree. A
second in-session engineer independently checked the commit-to-tree-to-blob
chain and read the complete source snapshot and probe.

| Source finding | Implication and limit |
| --- | --- |
| The documentation app uses `createPublicMcpApp`; its factory supplies `requireAuth: false` and directly exposes the MCP handler. Absent auth props create no `AccountManager` and do not enter the authenticated OAuth router. [CF-02–CF-04] | The public documentation route has a source-supported no-customer-auth path. This does not qualify any authenticated Cloudflare product route. |
| The source registers `search_cloudflare_documentation` and `migrate_pages_to_workers_guide`, both with `readOnlyHint: true`. The first queries the provider's documentation index; the second fetches one fixed public guide. [CF-05] | The handlers support the bounded documentation task. An annotation alone is not a safety certification. Only the search tool was called; the guide was listed but not executed. The README's one-tool table is incomplete relative to source and the observed two-tool listing. |
| Both paths use the same fresh request-scoped MCP handler. Legacy `GET /sse` is changed to a migration response only after the underlying handler returns 405 and its Host/Origin policy has run. [CF-04, CF-06] | A path ending in `/sse` does not establish legacy HTTP+SSE support. The source's 410 response is conditional; our observed GET was 403 with an HTML body and no alternate link. The denial's cause is unknown. |
| The package declares `docs-ai-search` version `0.4.13`; the registry document separately declares its collection version `1.0.0`. [CF-08, CF-09] | These are distinct identity fields. The live server reported `docs-ai-search 0.4.13`, but that does not prove it deployed the inspected Git commit. |

The repository LICENSE is Apache-2.0. That source-code license is not a hosted
service contract or permission to redistribute search results. This note keeps
links, bounded paraphrase, normalized observation metadata and content digests;
it does not copy upstream source bodies or retrieved documentation text. No new
commercial-display, billing, rights or freshness decision is made. [CF-10]

## Actual endpoint observations

The [retained observation](../../tests/fixtures/cloudflare-docs-mcp-2026-10-18/observation.json)
contains the timestamps, HTTP/RPC methods, status/content-type metadata, exact
SDK versions, script hash, tool/schema identities and response summaries.

| UTC time on 2026-10-18 | Client and operation | Actual result |
| --- | --- | --- |
| 08:11:23 | `mcp 1.30.0`, legacy initialize and tools list, `/mcp` | Initialized `2025-11-25`; complete two-tool listing, no cursor. Initialize/list returned HTTP 200 with `text/event-stream`; initialized notification returned 202. No session ID or session response header was observed. This is Streamable HTTP with SSE response bodies, not the separate legacy HTTP+SSE transport. |
| 08:11:23 | `mcp 2.3.0` / `mcp-types 2.3.0`, auto discover/list and one search, `/mcp` | Used `2026-07-28`; discover, list and search returned HTTP 200 JSON. Complete two-tool listing, no cursor. Search returned explicit `isError: false`, 13 result entries and only `developers.cloudflare.com` URLs. |
| 08:12:28 | Same modern SDK, auto discover/list, `/sse` | Used `2026-07-28`; complete identical two-tool listing, no cursor. This records the historical URL functioning as a Streamable HTTP alias. No search was repeated. |
| 08:12:27 | One bounded standard-library GET `/sse`, `Accept: text/event-stream`, no redirects | HTTP 403 HTML, 7,184 response bytes, no alternate `Link`. No transport migration success or specific denial cause is inferred. No alternate header/client retry was made. |

All three SDK workers exited zero with zero stderr. The probe also requires the
actual tool result's success flag; process exit alone is not its evidence of a
successful search. All report server identity `docs-ai-search 0.4.13`. Outgoing
request hooks reject credential headers, unexpected endpoints, redirects to
other URLs, methods outside the allowlist, other tool names and a changed query.
Only the fixed inspected search can be invoked after its returned listing has
the expected read-only hint. Responses and tool descriptions remain untrusted
data; no result URL was followed. Complete listing claims above rely on the
observed absent cursors, since the probe does not paginate.

The search result's normalized JSON content digest is
`56ae836deb773f778b191847d15def59f99329402f019f26841bb9d27288124e`
(55,445 bytes). The record retains its count and URLs, not the result text.
The digest identifies that received value; its preimage is not retained here
and later search content may differ. Neither the count nor the digest evaluates
ranking, relevance, factual correctness, completeness, index freshness or quality.
The 403 body's byte digest is retained without its HTML.

## Reproduction and offline checks

The [SDK probe](../../tests/reproduce_cloudflare_docs_mcp.py) is bound to SHA-256
`6fec10c644ec3e311dd4c81d3590fe0e63ba124355e3c154151a2c8f6a5886b8`.
It uses the same separately isolated Python 3.12 SDK environments and dependency
locks as the [earlier SDK preparation](../../tests/fixtures/mcp-protocol-2026-10-18/preparation.json):
[legacy lock](../../tests/fixtures/mcp-protocol-2026-10-18/requirements-v1.txt) and
[modern lock](../../tests/fixtures/mcp-protocol-2026-10-18/requirements-v2.txt).
That preparation's wheel/source identity evidence is unchanged.

With those exact environments already provisioned, run from the repository root
on a host authorized to access the public documentation endpoint:

```sh
timeout 45s /path/to/v1-env/bin/python -I tests/reproduce_cloudflare_docs_mcp.py --generation v1 --mode legacy
timeout 45s /path/to/v2-env/bin/python -I tests/reproduce_cloudflare_docs_mcp.py --generation v2 --mode auto --search
timeout 45s /path/to/v2-env/bin/python -I tests/reproduce_cloudflare_docs_mcp.py --generation v2 --mode auto --route sse
```

The recorded query is `How does Streamable HTTP differ from the deprecated
HTTP+SSE transport for MCP?`. The supplied source rejects changed SDK versions,
custom endpoints, credential headers and other tool calls. Each HTTP/read
operation has a 15-second limit; the actual controller bounded each worker to
45 seconds. The script does not claim an internal whole-process deadline. Future
network failures, changed listings or protocol results must be retained as new
observations rather than substituted into this historical record.

The separate GET used Python's `urllib.request.Request`, the exact fixed URL,
method GET and the Accept header shown above, a redirect handler returning no
replacement request, a 15-second timeout and a 65,536-byte body cap. HTTP errors
were retained as responses. Its different outcome was preserved and was not
retried. These details are sufficient to repeat the bounded operation; the
same edge response is not guaranteed from another time or host.

Repository tests inspect the saved records, exact driver/source/lock identities,
method scope, successful versus denied results and original observation
preservation. They make no network request and do not upgrade a hosted service
claim. Real SDK or endpoint replay remains an explicit separate operation.

## Consumer and handoff consequences

For this endpoint, authentication should be recorded as the dated public
documentation path; do not inherit the main Cloudflare API server's OAuth or
token requirements. A legacy-only MCP client can use the observed stateless
2025 Streamable HTTP path, and the tested modern client can use discovery with
2026-07-28. These are exact tested tuples, not claims about every framework or
client implementation. [CF-01–CF-04; retained observation]

Record transport semantics separately from URL suffix and HTTP response content
type. A source-code commit, package version, registry version and live server
identity are also separate provenance facts. This observation does not supply a
deployed code hash, comprehensive supported-version list, paid-service terms,
customer authorization, security certification, production SLA or selected
framework acceptance. Other Cloudflare product servers, Notion, Linear and the
remaining #27/#25 tuples and external receiving-owner decisions stay open.
Frozen v1, catalog items and their evidence grades are unchanged.

## Primary sources

All sources were read on 2026-10-18. Immutable source-file hashes and byte counts
are in the manifest; the public documentation page is a dated mutable source.

| ID | Source | Scope |
| --- | --- | --- |
| CF-01 | [Cloudflare's own MCP servers](https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/) | Official public endpoint and documented modern/stateless-legacy transport distinction |
| CF-02 | [Documentation app README at the inspected commit](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/apps/docs-ai-search/README.md) | Explicit unauthenticated public documentation route; one-tool table limitation |
| CF-03 | [Documentation app assembly](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/apps/docs-ai-search/src/docs-ai-search.app.ts) and [public app factory](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/packages/mcp-common/src/mcp-app.ts) | Public/authenticated router distinction and server assembly |
| CF-04 | [Request-scoped server factory and handler](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/packages/mcp-common/src/server.ts) | Auth defaults, alias route, Host/Origin sequence and stateless fallback |
| CF-05 | [Complete documentation tool handlers](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/packages/mcp-common/src/shared-tools/docs-ai-search.tools.ts) | Both tool names, annotations, search/guide behavior and returned URL treatment |
| CF-06 | [Legacy transport migration response](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/packages/mcp-common/src/transport-migration.ts) | Conditional 410 problem and alternate URL; not an observed 410 receipt |
| CF-07 | [Documentation environment](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/apps/docs-ai-search/src/docs-ai-search.context.ts) | Provider-owned documentation search, metrics and error-reporting bindings; no telemetry-delivery observation |
| CF-08 | [App package metadata](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/apps/docs-ai-search/package.json) | Source package version 0.4.13 |
| CF-09 | [Registry document](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/server.json) | Collection version 1.0.0, docs Streamable HTTP URL without a credential header entry |
| CF-10 | [Repository LICENSE](https://github.com/cloudflare/mcp-server-cloudflare/blob/e4cf085520ea7286af77abf938d645c610ef1580/LICENSE) | Apache-2.0 for the source; not hosted-service or result-redistribution clearance |
