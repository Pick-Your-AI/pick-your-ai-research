# Goose native usage collection

## Supported source and evidence

This collector is verified against **Goose 1.54.0 source at
`69de89c50cc01d4e0187d6645bf3618729873f74`, SQLite session schema 17**.
This is a source/fixture compatibility claim, not a certification of every Goose
release, provider, or installed binary. Older and future schemas fail closed:
readable session counters are coverage evidence, not fabricated model calls.
No Goose source changes, provider calls, credentials or third-party dependencies
are required. The existing ledger scanner, stores, queries, price snapshots and
reports are used; this is not a second billing engine.

The native `usage_ledger` table is preferred over messages and exports. Its rows
record Goose usage operations, including compaction. They are not proven one-to-one
HTTP request attempts. Counts are **Goose-recorded evidence**, not independently
verified provider invoices: Goose adapters can normalize or estimate usage.
Class A denotes the native usage-record granularity, not proof that every adapter
reported exact provider consumption. Class B denotes cumulative native counters;
Class C denotes the existing ledger's API-equivalent price estimate.

### Audited implementation

The following are immutable source references, not documentation-only schema guesses:

- [Session tables, migrations, usage recording and exports](https://github.com/aaif-goose/goose/blob/69de89c50cc01d4e0187d6645bf3618729873f74/crates/goose/src/session/session_manager.rs):
  `CURRENT_SCHEMA_VERSION`, `insert_usage_ledger_row`, `record_usage_metrics`,
  `export_session` and the `sessions`, `messages`, `usage_ledger` table definitions.
- [Token semantics](https://github.com/aaif-goose/goose/blob/69de89c50cc01d4e0187d6645bf3618729873f74/crates/goose-provider-types/src/conversation/token_usage.rs):
  `Usage` stores inclusive input and separate cache subsets; `ProviderUsage` has
  more fields than the session database persists.
- [Message metadata](https://github.com/aaif-goose/goose/blob/69de89c50cc01d4e0187d6645bf3618729873f74/crates/goose-provider-types/src/conversation/message.rs):
  `InferenceMetadata` and `MessageUsage` serialize using camelCase.
- [Usage recording](https://github.com/aaif-goose/goose/blob/69de89c50cc01d4e0187d6645bf3618729873f74/crates/goose/src/agents/state_machine/usage.rs)
  and [session effects](https://github.com/aaif-goose/goose/blob/69de89c50cc01d4e0187d6645bf3618729873f74/crates/goose/src/agents/state_machine/session.rs).
- [Legacy sessions](https://github.com/aaif-goose/goose/blob/69de89c50cc01d4e0187d6645bf3618729873f74/crates/goose/src/session/legacy.rs)
  and [path resolution](https://github.com/aaif-goose/goose/blob/69de89c50cc01d4e0187d6645bf3618729873f74/crates/goose/src/config/paths.rs).
- The pinned dependency is etcetera 0.11.0. Its
  [platform strategy](https://docs.rs/etcetera/0.11.0/etcetera/app_strategy/fn.choose_app_strategy.html)
  is XDG on both Linux and macOS; its
  [Windows implementation](https://docs.rs/etcetera/latest/src/etcetera/app_strategy/windows.rs.html)
  appends author, application and `data` to roaming application data.

## Discovery, consent and configuration

Existing onboarding disclosures and profile consent apply. Detection is limited
to the current profile unless the operator has already approved other profiles,
WSL or named SSH hosts. Detection checks the named session directory; it does not
start Goose, query a provider, load Goose configuration/credentials or enable a
schedule. Environment overrides from the current process are not applied to other
profiles. For redirected application data belonging to another approved Windows
profile, configure the exact root explicitly rather than guessing that profile's
Known Folder location.

| Platform | Default session directory |
|---|---|
| Linux | `~/.local/share/goose/sessions` |
| macOS | `~/.local/share/goose/sessions` (XDG, **not** `~/Library/Application Support`) |
| Windows | `%APPDATA%\Block\goose\data\sessions` (roaming Known Folder when `APPDATA` is unset) |
| Absolute `GOOSE_PATH_ROOT` override | `$GOOSE_PATH_ROOT/data/sessions` on all platforms |
| Absolute `XDG_DATA_HOME` override | `$XDG_DATA_HOME/goose/sessions` on Linux/macOS |

An invalid relative Goose/XDG override is ignored, matching the audited path
strategy. `sessions.db`, its adjacent WAL and immediate legacy `*.jsonl` headers
are the only native inputs. Arbitrary directory recursion is not used.

The existing manifest accepts an optional `goose_roots` list. Each entry is an
absolute database file or session directory, optionally prefixed by a stable
source namespace:

```json
{
  "workdir": "/approved/ledger-work",
  "hosts": [{
    "name": "workstation",
    "kind": "local",
    "goose_roots": ["goose-work=/approved/goose/data/sessions"]
  }]
}
```

For an already-onboarded ledger, review detected roots before running
`python scripts/ledger.py run --tools goose`. The one-off path remains
`python scripts/run_pipeline.py --manifest /approved/manifest.json --only scan`.
The scanner also accepts `--goose-root namespace=/absolute/path`.
An old `--generic-root goose=/absolute/path` is routed to the native collector,
not to the generic per-call sniffer. Recognizable native exports and legacy
headers are excluded from generic JSON collection, even when given a different
label. Unrecognizable hand-edited files are not certified Goose inputs.

Disable Goose for a run with `ledger.py run --skip-tools goose`. For a manually
maintained manifest, remove its `goose_roots` and any old `generic_roots` entries
labelled `goose`. Disabling collection does not delete already stored events.
Do not turn on extra profile, credential, raw-log or scheduling opt-ins merely
to test this integration.

## Field mapping and attribution

| Native field | Ledger representation and semantics |
|---|---|
| `usage_ledger.id`, `session_id`, `created_timestamp`; session `created_at` | Stable namespaced event identity; `goose.usage_id` and `goose.native_session_id` retain native IDs. `request_id` is a **ledger identity**, not a provider HTTP request ID. |
| `model` | Per-native-record model. Never replaced by the session's latest model. Missing model excludes the row from priced usage with a coverage reason. |
| `created_timestamp` | UTC Unix seconds converted to `ts` and `date`. This is Goose's record time, not independently measured provider start/end time. Invalid timestamps are excluded, not replaced with scan time. |
| `input_tokens` | Inclusive input. `input_uncached = input_tokens - cache_read_tokens - cache_write_tokens`. |
| `output_tokens` | `output`; no extra reasoning tokens are added. |
| `cache_read_tokens`, `cache_write_tokens` | `cache_read`, `cache_write` subsets. Original nullable values remain in `goose.native_tokens`. |
| `total_tokens` | Checked against input + output when present. If absent, total is derived only from valid input and output. |
| Reasoning tokens | Not persisted in this schema. `goose.native_tokens.reasoning_tokens` is null; the legacy arithmetic bucket is zero, **not a measured zero**. |
| `cost`, `cost_source` | `goose.native_cost.amount/source`; `provider_reported` and `estimated` remain distinct. Currency is null because the row has no currency. Neither is promoted to observed USD billing. |
| `is_compaction` | `kind=compaction` or `main`. Compaction rows remain usage even when no corresponding message survives. |
| Provider | Not stored in `usage_ledger`. Unique one-to-one equal-model/equal-token/equal-cost message metadata can provide an **inference**, explicitly labelled `inferred_unique_message_usage`; otherwise null / unavailable. |

The latest session `provider_name` is deliberately not read for historical
attribution. A provider switch cannot reassign older calls to the new session
provider. There is no durable usage-row/message foreign key: equal fingerprints
are only circumstantial evidence, not proof of a join. Repeated identical calls,
missing metadata and compaction stay provider-unknown. Same-model provider
switches can therefore leave unattributed usage. Upstream [issue #12092](https://github.com/aaif-goose/goose/issues/12092)
also documents why the current session provider is not historical evidence.

Missing input/output, negative or non-integer counts, inconsistent cache subsets,
contradictory totals, invalid identity or unknown cost-source semantics exclude a
row rather than silently clamp, estimate or bill it. Sanitized known numeric
fields remain in `inventory.<host>.json` under `excluded_usage`.
Missing cache fields use zero only in the existing arithmetic contract, with
native null evidence retained. Pricing then treats unsplit input as ordinary
input; cache-write TTL is unavailable and the configured snapshot default is an
assumption. Reports label these API-equivalent estimates. Unknown prices remain
unpriced. This collector never adds a price catalog, infers a currency from a
model name, or replaces a snapshot estimate with native estimated cost.

## Deduplication, growth and legacy evidence

IDs combine the source namespace, native session ID and creation marker, native
usage-row ID and record timestamp. With no explicit namespace, a stable hash of
the resolved database path is used. Session grouping is also namespaced because
Goose session IDs are local date/sequence identifiers. The store additionally
separates hosts. Copies of one database should use the **same explicit namespace
and host label**; independent installations must use different namespaces.
Do not change a namespace or host label after ingestion. Arbitrary cross-host
replicas and previously ingested generic records cannot be retroactively merged
by this append-only collector.

Each scan takes a fresh verified snapshot and replays native records through the
existing store's stable-ID deduplication. **Incremental accounting is supported;
source I/O is a full snapshot, not a row-offset checkpoint.** An unchanged second
scan adds zero events. An active session with one new valid usage row adds one
record, even if its cumulative counters also increase. Rebuilding scan output
cannot lose usage through a prematurely advanced checkpoint. Large histories
incur full DB/WAL copying and memory for projected usage records. No background
scan is installed.

Goose's `accumulated_*` fields are cumulative. `record_usage_metrics` can insert a
`cost_source=carried_forward` row for older consumption not present in the native
ledger. These rows, session counters, legacy JSONL headers and exports are **not
additional billable events**. They are Class B coverage/reconciliation evidence.
Session `total_tokens` is a current-context value and is not used as a cumulative
billing counter. Parent UI totals can recursively include child sessions; compare
flat native session counters, not recursive parent totals plus the same children.

Native JSON exports serialize a Session and conversation, not the usage ledger.
They have no durable usage-row IDs and cannot establish complete historical
per-model/provider usage. JSON/Markdown exports are not billable inputs. Legacy
JSONL support reads only the bounded first metadata line, preserving cumulative
counters without parsing conversation text or fabricating deltas. Older schema
counters, resumed imports and carried-forward gaps remain explicit exclusions;
there is no trustworthy final-session marker on which to base guessed accounting.

If older generic Goose records were already ingested, review/export that ledger
before choosing a clean native-only store. This integration does not silently
edit/delete prior events or claim to deduplicate identities invented by an older
collector. Immutable native rows changed externally after first ingestion cannot
update the existing append-only store. The first stored observation remains;
rebuild a separately reviewed store for corrections. Later improved provider
metadata does not create another billable event or silently rewrite history.

## Read-only safety and privacy

A SQLite `mode=ro` connection to a live WAL database can create source-side
auxiliary files. The collector instead copies the DB and adjacent WAL using
read-only file handles into an owner-private temporary directory, verifies file
identity, size, timestamps and hashes across the capture, then queries **only the
private snapshot** with `mode=ro`, `query_only=ON`, `trusted_schema=OFF` and a read
transaction. It does not use `immutable=1`, which would hide committed WAL data,
and does not copy SHM or checkpoint, migrate, clean up or modify source files.
A busy source is retried up to three captures; an unstable pair or rollback
journal is a retryable coverage gap. Invalid schemas, locks, access failures and
corruption are reported without raw exception text or fabricated usage.

**Temporary raw-data caveat:** the private snapshot physically contains the
source database's transcript bytes, even though only allowlisted usage metadata
is projected and retained in the ledger. It is removed on ordinary success or
failure; a forced process termination can leave the private temporary directory
(`ai-ledger-goose-*`) until the operator/OS removes it. This is not a durable raw
log archive or permission to capture prompts. Use an appropriately private and
adequately sized system temporary directory. Do not use this collector where
policy forbids even transient local database copies.

The collector never selects message content, session names, project directories,
full metadata objects or credential files. Prompt/completion text is not emitted,
even when another harness has prompt capture enabled. `src`/session `file` are
null, so raw-archive discovery does not copy the Goose database. Necessary
metadata includes host, approved root, model, native session/usage identifiers,
timestamps, tokens, inferred provider and qualified cost evidence. No external
service receives usage, and no personal profile or schedule is enabled.

## Validate with synthetic records

Run from a complete checkout with Python 3.12 or newer:

```bash
python -m unittest discover -s tests -p 'test_goose*.py' -v
python -m unittest discover -s tests -p 'test_package_*.py' -v
python scripts/validate_package.py
python scripts/validate_quality.py
```

The fixture builder is `tests/goose_fixtures.py`; see [fixture notes](../tests/README.goose.md).
The E2E test runs the actual scanner and SQLite, JSON and CSV stores. It checks
one initial native record, a zero-add replay, one additional record as the session
grows, query results, existing snapshot pricing, report generation and native
counter reconciliation. Test prices and model/provider names are hypothetical.
Neither unit tests nor CI call a live provider, open personal logs, authenticate
to Goose, or certify runtime/provider retry coverage.

For an approved existing ledger, query with its existing SQL query interface:

```sql
SELECT model, session, COUNT(*) AS native_usage_records, SUM(total) AS tokens
FROM events WHERE tool = 'goose' GROUP BY model, session;
```

Compare results to each scan's `inventory.<host>.json` `sessions[].counters` and
`collected_native_tokens`; explain `excluded_usage`, carried-forward rows and
provider-unknown counts instead of hiding them. Read coverage inventory alongside
the dashboard: the existing report does not automatically render every native
exclusion. Preserve the same namespace, rerun without activity, and require zero
new store events. Then add authorized activity and check only new usage records
are appended. Failed/retried requests for which Goose never persisted usage,
provider-side routing, HTTP attempt IDs, reasoning breakdowns, cost currency,
cache TTL and exact historical provider joins remain coverage gaps.

## Compatibility and publication checks

Anonymized publication removes native row/session/source identifiers from nested
Goose event evidence and inventory. Inventory session labels are salted, as are
normal event identifiers; numeric token/cost evidence remains unchanged. Private
source namespaces (including path hashes) are not publication-safe identifiers.

SQLite builds without `json_valid`/`json_extract` still collect native usage:
provider inference is marked unavailable without loading full message metadata.
Inventory source file/byte counts include the observed DB and WAL, not SHM or the
multiple internal copy/hash passes. File sizes may change after that observation
when a session is active; use token reconciliation, not footprint alone, for totals.

Onboarding drafts a host-scoped Goose placeholder with unknown billing and low
confidence. It reads no Goose credential file and does not claim that the latest
provider configuration identifies historical billing. Review account rules before
using account-specific cost summaries.

### Windows report timezone data

The native collector remains standard-library only. The existing scoped-report
renderer requires installed IANA timezone data. On Windows Python installations
without that data, install `tzdata` in the ledger Python environment
(`python -m pip install tzdata`) before generating time-scoped reports. Collection,
storage and token queries do not require it. The three-OS integration workflow
installs this report prerequisite on Windows rather than skipping report tests.
