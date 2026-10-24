# Muse Mesh native usage and MCP reporting

## Compatibility and scope

This integration targets `muse-mesh/mu` at
`e537b757c112557f5256b3397523a6772d768697` and ledger main
`05849f9dd595af420dddb2f4b1cf39b88dbf67b9` (including the mini-SWE-agent
collector). The original ledger audit base was
`e9d5e225a802d8eddcc7e1a2fc72cded6db1437e`. It uses Muse's actual
`createOpenAI({fetch})` extension point in both `src/agent.ts` and
`src/web/server.ts`. Agent steps, SDK HTTP retries, memory extraction and
compaction/reset helper calls use this boundary. It does not monkey-patch the
runtime. Muse's existing UI usage estimates and cost-limit behavior are unchanged.

The pinned Muse version supports OpenAI-chat-compatible HTTP providers, not
arbitrary native Anthropic/Gemini SDKs. The provider label is an explicit operator
attribution; a gateway's upstream provider cannot be inferred reliably from its
model name. The returned response model takes precedence over the requested
model; both are retained. The adapter does not claim an undocumented Muse plugin
or event-bus API.

Muse is Apache-2.0; the ledger core is MIT. The complete upstream patch and an
Apache license copy are under `integrations/muse-mesh/`. No new runtime
packages are required: Muse uses its pinned Node 22+ dependencies, and ledger
imports/MCP use Python's standard library. Use Python 3.12+ for the integration
and repository quality suite. The ledger's other collectors and CLI remain intact.

## Data flow

1. With collection explicitly enabled, the provider fetch adapter creates a
   random invocation UUID and a private `<uuid>.started.json` marker before the
   HTTP request. Each actual HTTP retry has its own UUID and ordinal within its
   run. SDK retry-parent metadata is not exposed at this boundary, so `retry_of`
   is null rather than a guessed relationship.
2. The adapter forwards response bytes unchanged and extracts only an allowlist
   from the response JSON/SSE usage envelope. This avoids SDK defaults that turn
   omitted measurements into zero. No token estimates are generated here.
3. It atomically writes a versioned `<uuid>.usage.json` final envelope after EOF,
   cancellation or error. Read-only scans ignore incomplete `.tmp` files. A start
   marker without a final record is counted as unfinished coverage, not a free
   or zero-token call. Marker and event files remain available for replay/audit.
4. `muse_usage.py scan` validates the entire approved batch, normalizes it into
   existing ledger event columns plus `extra` metadata, and uses the public
   `SqliteStore.ingest_verified_events` transaction. No personal log discovery,
   prompt capture or new store engine is introduced.
5. `ledger_mcp.py` uses existing `ledger_query` primitives and
   `compile_ai_logs.price_event`. Reporting never initializes/migrates a ledger,
   edits configuration, schedules a scan or issues an invoice.

Live concurrent ingestion and MCP reporting require the existing SQLite backend.
Normalized events still round-trip through the existing JSON/CSV file import and
export APIs, but those backends do not provide the required live-writer transaction
and conflict guarantees. They are not silently treated as concurrent databases.

## Consent and privacy

Read the complete **Before You Start** disclosure in `SKILL.md` and the real-source
onboarding instructions in `ONBOARDING.md` before initializing or using a personal
ledger. This guide does not supersede those consent gates. The included fixture
test creates only a temporary synthetic ledger and does not enroll a real source.

There are three independent decisions. `usageLedger.enabled` permits Muse to
write local metadata; `collection_enabled` plus `collection_consent` permits its
import into a configured ledger; `reporting_enabled` plus `reporting_consent`
permits aggregate data to be given to an MCP client. The client may pass report
results to its configured remote model provider. **Local-only capture is not
consent to send reports to that provider.** Optional model-triggered scans also
require `allow_scan: true`; they are disabled by default. No tool can grant consent,
change sources, select a path, edit configuration or install a schedule.

The spool is owner-only (0700 directories and 0600 files on POSIX). Session, run
and response IDs are HMAC-SHA256 pseudonyms by default using a private persistent
`.identity-key`. Source/provider/model identifiers remain visible for attribution.
`includeIdentifiers: true` is a separate opt-in for literal native IDs; set the
ledger source's `id_mode` to `literal` too. Windows operators must configure
account-restricted ACLs; POSIX mode bits are not represented as a Windows ACL
control. Do not run this server under an untrusted/shared account.

No prompts, completions, tool arguments/results, credentials, URLs, request
bodies, raw headers or provider error messages are exported. The response parser
necessarily sees bytes that Muse already consumes, but persists only the usage
allowlist. This integration does not disable or redact Muse's pre-existing audit
logs; configure those separately. The MCP server exposes no raw event, filesystem,
shell, SQL, credential, scheduling, configuration or HTTP-listener capabilities.
Its error messages do not echo paths or rejected inputs. Configuration is
operator-controlled and reread on every tool call, so revocation is immediate.
An agent that already has unrestricted shell access as the same OS account can
edit local files; this integration cannot provide an OS security boundary against
that separate privilege. Protect operator configuration accordingly.

## Installation

Use isolated checkouts and review the patch. Publishing the upstream Muse branch
requires its maintainers' permission; until that change is accepted, apply the
included patch to the exact pinned revision:

```bash
git clone https://github.com/CompleteTech-LLC/ai-usage-ledger-skill.git ledger
git clone https://github.com/muse-mesh/mu.git mu
git -C mu checkout -b usage-ledger e537b757c112557f5256b3397523a6772d768697
git -C mu apply --check ../ledger/integrations/muse-mesh/mu.patch.txt
git -C mu apply ../ledger/integrations/muse-mesh/mu.patch.txt
(cd mu && pnpm install --frozen-lockfile && pnpm build)
```

Use the ledger revision containing this integration. Keep absolute paths in
configuration. Configure the API key through Muse's existing secret mechanism;
do not put a credential in an example, usage record or committed configuration.

After the applicable disclosures/consent, merge this section into the existing
private ledger `config.json` (replace paths and provider/source labels):

```json
{
  "store": {"kind": "sqlite", "path": "/absolute/private/ledger/events.sqlite"},
  "pricing_path": "/absolute/ledger/templates/pricing.json",
  "muse_mesh": {
    "version": 1,
    "collection_enabled": true,
    "collection_consent": "local-usage-metadata",
    "reporting_enabled": true,
    "reporting_consent": "share-usage-aggregates",
    "allow_scan": false,
    "sources": [{"id": "workstation-mu", "provider": "my-gateway", "path": "/absolute/private/mu-usage", "id_mode": "hmac-sha256"}]
  }
}
```

Retain the other existing ledger configuration keys. The store parent directory
must already exist and be private. The scanner can create the SQLite database
only after collection consent; the report server never creates it. Keep config
owner-only (`chmod 600 config.json`) and the source/store directories owner-only
(`chmod 700 ...`). Paths must be absolute and must not contain symlink components.
The scanner reads only UUID-named final files in the approved directory; it does
not descend into other directories or read normal Muse JSONL prompt logs.

Merge this section into `.mu.json`:

```json
{
  "usageLedger": {
    "enabled": true,
    "sourceId": "workstation-mu",
    "provider": "my-gateway",
    "directory": "/absolute/private/mu-usage",
    "includeIdentifiers": false
  },
  "mcpServers": [{
    "name": "ledger",
    "transport": "stdio",
    "config": {
      "command": "/absolute/python3",
      "args": ["/absolute/ledger/scripts/ledger_mcp.py", "--config", "/absolute/private/ledger/config.json"]
    }
  }]
}
```

Only add `reportedChargeCurrency: "USD"` to `usageLedger` after confirming that
your gateway's `usage.cost` is a USD charge for that response. Otherwise the amount
remains null. The standard OpenAI-chat usage schema does not guarantee a monetary
charge field. The existing web UI's accumulated cost is not copied as an invoice.

Execute a Muse interaction, then import its finalized usage:

```bash
python3 /absolute/ledger/scripts/muse_usage.py scan --config /absolute/private/ledger/config.json
```

Scanning is explicit, not automatically scheduled or run at MCP startup. Enable
`allow_scan` only when the model may import the already approved sources. The
ledger's separate scheduling consent requirements still apply to any recurring
operation an operator later chooses to configure.

## MCP tools

Muse exposes `ledger_status`, `ledger_usage_summary`, `ledger_usage_by_model`,
`ledger_usage_by_provider`, `ledger_usage_by_session` and `ledger_cost_breakdown`
with the native `mcp__ledger__` prefix. `ledger_scan_sources` is discoverable and
callable only when both collection consent and `allow_scan` are true. Known names
cannot bypass authorization. Reporting-disabled configurations expose no tools.

Example calls through Muse's supported tool interface:

```text
mcp__ledger__ledger_status({})
mcp__ledger__ledger_usage_summary({"since":"2026-10-01","until":"2026-10-31"})
mcp__ledger__ledger_usage_by_model({"limit":20})
mcp__ledger__ledger_usage_by_provider({})
mcp__ledger__ledger_usage_by_session({"limit":20})
mcp__ledger__ledger_cost_breakdown({"provider":"my-gateway"})
mcp__ledger__ledger_scan_sources({})  # only after the separate scan authorization
```

Filters are fixed, parameterized date/model/provider/session fields, never SQL or
paths. Reports are limited to the approved source/provider pairs. A result's
`truncated` flag explicitly identifies limited group output. `calls` counts
recorded HTTP attempts, including failures. `missing_total_records`,
`incomplete_usage_records` and `noncompleted_records` expose coverage gaps.
`input_tokens` includes cached input; `input_uncached` does not. Null is unknown,
not zero. Sums across partly known events are observed subtotals, not complete bills.
The status tool does not scan directories to infer pending usage.

The server implements the tools-only stdio handshake used by Muse's pinned MCP
libraries: 2024-11-05, 2025-03-26, 2025-06-18 and 2025-11-25. This is not a claim of
implementing later stateless protocol revisions, HTTP authorization, resources,
prompts, sampling or subscriptions. Requests are limited to 64 KiB and 120 per
minute per process; cost queries require a scope of at most 50,000 events, groups
at most 500, and scans at most 10,000 directory entries. Narrow a query or rotate
reviewed archives rather than widening the server into an arbitrary file tool.

## Deduplication and recovery guarantees

The identity key is SHA-256 of the schema/source/provider and native response ID,
or the pre-request persistent UUID when no native response ID exists. Existing
ledger `event_id()` then scopes that request ID by tool and source. Native response
IDs and pseudonym keys must be stable. Re-scanning, overlapping imports and replay
of the same response under another local run/attempt do not add a second charge.
A real provider retry returning a *different* response ID is a separate invocation;
it is not incorrectly suppressed by hashing identical prompt text.

A separate SHA-256 fingerprint binds completion status, pricing eligibility,
capture completeness, model, observed counts, input semantics and
charge evidence. Changed evidence under an existing identity aborts the entire
transaction, including unrelated new rows in that batch. Nothing is overwritten
or silently ignored. Keep both receipts and investigate the provider/source
conflict; this integration deliberately has no automatic correction or deletion
tool. An incomplete event replayed later with different final evidence requires
operator reconciliation through an appropriate ledger maintenance workflow.

`.source.json` prevents silently changing source/provider/privacy mode in a
populated directory. Never delete or rotate `.identity-key` for an existing source;
restore it from a protected backup. Missing keys cause export to pause with a
sanitized warning rather than creating a new deduplication namespace. Export
files and identity keys are not sent through MCP. Copying a source for replay
must preserve its source identity and key; do not simultaneously enroll copies
under unrelated source IDs.

Disabled capture returns the original provider fetch function and performs no
filesystem writes. Temporary storage failures do not fail the model request.
The adapter retains up to 256 pending metadata writes in memory and retries on
subsequent requests/flush. Failed metadata writes do not retry a provider call.
A persisted start marker survives interruption; partial temp files are ignored.
It is impossible to reconstruct a missing provider usage envelope or a write
lost before durable persistence after a hard kill. Those are coverage gaps, not
invented zero-cost invocations. No live-provider, invoice or lossless-crash
verification is implied by fixture tests.

## Pricing and legacy reports

Provider usage and gateway-reported charges are separate from API-equivalent
list-price estimates. The MCP cost report reuses the ledger's existing pricing
resolution, aliases, fallback rates and cache/long-context rules; it reports the
pricing snapshot hash/date and assumed/unpriced record counts. Gateway-reported
`usage.cost` is evidence from that gateway, not proof of settlement or a customer
invoice. Missing charge is null, including when no response explicitly supplied it.
No tool queries live pricing or establishes a new billing system.

Missing input/output/cache partitions, estimated token counts, incomplete capture
and noncompleted attempts are not priced as complete API usage. Observed input
and output totals remain available when their cache split is unknown. The native
OpenAI-chat envelope does not define separate cache-write quantities; that field
remains null. The documented `inclusive-cache` envelope extension permits a
trusted adapter to supply them; an absent TTL follows the existing ledger's
five-minute pricing convention and is labeled as an assumption.

The existing scoped report now propagates the incomplete-usage flag for these
versioned Muse events only, without parsing other collectors' `extra` payloads.
Its category sums may be partial; its pricing exception explains this. Existing
legacy renderers can coalesce absent category values for presentation; use the
MCP coverage fields and canonical stored nulls for evidence-sensitive analysis.
The integration does not replace existing collectors' behavior or modify historic
records. Reports generated from old scanner export directories are not magically
refreshed by a native import; use the existing store/report workflows.

## Local development and minimal working example

The end-to-end test is the runnable minimal example: it starts a loopback
OpenAI-compatible fixture, calls the real Muse agent and web route, captures usage,
imports into a temporary SQLite ledger, and discovers/invokes the Python MCP server
through the real `loadMCPTools`. It also checks memory, compaction/reset, SDK retries
and response replay. No API key or provider account is required.

```bash
# From the patched mu checkout, with Node 22+, pnpm and Python available:
pnpm install --frozen-lockfile
pnpm exec tsc --noEmit -p tsconfig.usage-ledger.json
MU_LEDGER_REPO=/absolute/ledger PYTHON=python3 pnpm test:usage-ledger
# Optional receipt: set MU_LEDGER_EVIDENCE=/absolute/path/fixture-receipt.json

# From the ledger checkout:
python -m unittest discover -s tests -p 'test_muse_usage.py' -v
python -m unittest discover -s tests -p 'test_ledger_mcp.py' -v
python -m unittest discover -s tests -p 'test_package_*.py' -v
python scripts/validate_package.py
python scripts/validate_quality.py
```

The E2E test is skipped by the native-only test command unless `MU_LEDGER_REPO` is
set. The ledger cross-repository CI sets it explicitly and requires the receipt.
The deterministic initial record contains 100 input tokens (40 cached), 20 output
and 120 total; its illustrative gateway charge is USD 0.015 and its fixture
list-price estimate USD 0.0003. Replay must import zero new events. The expanded
fixture yields six measured responses plus one failed retry attempt: seven stored
attempts and 720 observed tokens. These numbers are not live pricing or usage.

## Troubleshooting and removal

An empty tool list means reporting is unconfigured or revoked. Confirm the fixed
config path and separate consent strings; a model-supplied override cannot help.
An unavailable-store error requires a consented initial import or restoration of
local storage. An import conflict is a receipt inconsistency, not permission to
edit an existing charge. A privacy/key warning requires restoring source identity
and permissions; do not delete keys or enroll duplicate copies. Symlinks, broad
shared directories, non-regular files, overlarge records and mismatched source
identity are rejected. Provider errors and cancellations are recorded without
secrets, with nullable usage; inspect ordinary provider diagnostics separately.

Set `usageLedger.enabled` to false or `MU_USAGE_LEDGER_DISABLED=true` to disable
future capture. Independently revoke the ledger collection/reporting flags and
remove its entry from `mcpServers`. Existing events remain append-only and local
spool files remain on disk. Review retention/backup requirements before manually
removing the spool/key; no uninstall tool destroys evidence. Restore/reverse the
upstream patch on an isolated branch only after checking for later changes. The
integration creates no daemon, service, schedule, external account or remote data
collector to uninstall.
