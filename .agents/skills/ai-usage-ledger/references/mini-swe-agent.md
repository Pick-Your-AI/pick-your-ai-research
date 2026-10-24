# mini-SWE-agent usage integration

## Verified source and compatibility

The dedicated collector reads `mini-swe-agent-1.1` trajectories and opt-in
`mini-swe-agent-usage-1` usage records. The integration targets mini-SWE-agent
**2.4.6**, source revision
`04d809ceab9df28f9adaed044884180159172930`. Native integration tests pin
LiteLLM **1.96.0**; the CI receipt records the resolved Portkey and other SDK
versions. Core ledger scanning still requires only the Python standard library.
Other trajectory versions, arbitrary custom schemas, streaming models, and
historical SDK cache conventions are not certified by this integration.

The native test matrix covers all nine provider adapters present at that revision:
`litellm`, `litellm_textbased`, `litellm_response`, `openrouter`,
`openrouter_textbased`, `openrouter_response`, `portkey`, `portkey_response`, and
`requesty`. `deterministic` has no provider token evidence and produces no invented
usage. Fully-qualified custom classes can be wrapped; a class without a `_query`
or `_calculate_cost` boundary is supported only when its returned message or
`FormatError` contains structured response usage. Hidden calls inside custom
classes and SDK-internal retries cannot be recovered without source evidence.
For Roulette/Interleaving meta-models, configure the individual child models;
do not assume the outer selector exposes provider responses.

## Source discovery and consent

Detection only reports a **disabled candidate** when it finds
`last_mini_run.traj.json`; it never adds `mini_swe_roots` automatically. Paths
checked include `MSWEA_GLOBAL_CONFIG_DIR`, Linux `$XDG_CONFIG_HOME/mini-swe-agent`
(default `~/.config/mini-swe-agent`), macOS
`~/Library/Application Support/mini-swe-agent`, and Windows
`%LOCALAPPDATA%/mini-swe-agent/mini-swe-agent` (platformdirs' default app-author
layout). Environment overrides apply only to the current authorized profile.
No `.env`, key, credential, or account file is opened for discovery.

Explicitly add the approved trajectory file, a dedicated trajectory directory,
and/or an export directory to a host's `mini_swe_roots`. Example manifest fragment:

```json
{
  "capture_prompts": false,
  "hosts": [{
    "name": "workstation-mini",
    "kind": "local",
    "mini_swe_roots": ["/absolute/approved/mini-runs", "/absolute/private/mini-usage"]
  }]
}
```

`ledger.py` regenerates detected manifests. Keep explicitly authorized hosts in
`config.json`'s existing `extra_hosts` list, or use a reviewed manifest with
`--no-detect`; do not rely on an edited auto-generated manifest surviving the
next discovery run. Existing local/WSL/SSH authorization rules still apply.
The normal tool selector is `--tools mini-swe-agent`.

A direct source-specific scan is also available:

```sh
python scripts/compile_ai_logs.py scan --host workstation-mini \
  --mini-swe-root /absolute/approved/mini-runs \
  --mini-swe-root /absolute/private/mini-usage \
  --no-prompts --out-dir /absolute/private/mini-scan
```

Directories admit only `*.traj.json`, `*.usage.json`, and `*.usage.jsonl` files.
An explicitly selected file can have a custom name. Broad roots are rejected;
symlinked source files/subdirectories are not followed. Files above 128 MiB and
malformed/truncated files are skipped with inventory error counts rather than
terminating the whole scan. The generic JSON sniffer deliberately excludes mini
trajectories and usage exports, including when generic roots overlap.

Remove `mini_swe_roots` (including from `extra_hosts`) or use the existing skip-tool
filter to disable ingestion. Existing ledger records are not deleted by disabling
a source. No background scanner, schedule, remote telemetry, or account discovery
is installed by this integration.

## Optional pre-cost usage export

Historical trajectories can recover only what the agent actually persisted.
The default `last_mini_run.traj.json` is overwritten; native saves are not atomic.
Native cost calculation and global cost limits can raise before a response reaches
the trajectory, whereas `FormatError` generally includes `extra.response`.

For reliable future capture, add the ledger's `scripts` directory to the mini
process's `PYTHONPATH` and select the native custom-model extension:

```yaml
model:
  model_class: mini_swe_export.UsageModel
  wrapped_model_class: litellm
  model_name: openai/gpt-4o-mini
  usage_export_dir: /absolute/private/mini-usage
  # Optional caller-controlled identities; reuse session/run IDs when resuming.
  usage_session_id: project-session-001
  usage_run_id: agent-run-001
  usage_agent_id: worker-001
  # Optional provider override, especially for a custom gateway:
  # usage_provider: internal-openai-compatible
```

Retain the existing `cost_tracking`, model, and provider configuration unchanged.
`wrapped_model_class` accepts the native shorthand or a fully-qualified custom
class. This factory creates a subclass of that class and delegates its existing
query, retry, cost, parsing, and limit behavior. It does not patch LiteLLM or
replace provider execution. Export options are removed before backend
configuration is constructed; they do not enter provider requests or templates.
Serialization retains an importable factory and wrapped class for reconstruction.

No export directory means export is disabled, even when the factory is selected.
A new directory is created privately; an existing POSIX directory must have mode
0700. On Windows, choose a directory protected by the current user's ACLs; the
exporter does not manage Windows ACLs. POSIX records use mode 0600.

Each returned provider response is reduced to an allowlist of usage numbers,
response/model identifiers, timestamp, and provenance **before** native cost
calculation. One UUID-named file is written with flush/fsync and atomic replacement;
final status and native calculated cost replace the provisional record. Context-local
state and unique filenames prevent concurrent exporters sharing a directory from
interleaving records. Underlying backend thread-safety is unchanged.

Successful calls, format errors, native pricing failures, post-response limit
failures, and cancellation after a response all retain their usage. A crash after
the first checkpoint leaves status `response_received`, not a fabricated success
or cancellation. No response/usage means no token event. I/O failures emit a
content-free warning and do **not** enter provider retries; inspect those warnings
and do not treat a disk-full scan as complete. Power-loss durability and usage
received only inside an opaque SDK before an exception are not guaranteed.

## Token and cost mapping

| Source evidence | Ledger field / rule |
|---|---|
| Chat `prompt_tokens`; Responses `input_tokens` | Inclusive input minus reported cache read/write categories → `input_uncached` |
| Native Anthropic-style `input_tokens` with separate cache counters | Already uncached; do not subtract cache categories again |
| `prompt_tokens_details.cached_tokens`, `input_tokens_details.cached_tokens`, or `cache_read_input_tokens` | `cache_read`; alternate representations are not added together |
| Details `cache_write_tokens` / `cache_creation_tokens`, or `cache_creation_input_tokens` | `cache_write` |
| Explicit 5-minute / 1-hour cache-creation details | `cache_write_5m`, `cache_write_1h` when the breakdown reconciles |
| `completion_tokens` or `output_tokens` | `output` |
| Completion/output details `reasoning_tokens` | `reasoning`, a subset of output, never added again |
| `total_tokens` | `reported_total_tokens`, retained as source evidence; never used to derive a negative prompt count |
| Separately reported components | `total`, explicitly marked `sum_components` even when source total is missing |
| Partial counts with a reliable larger total | Remainder retained as `unclassified_tokens`, not guessed input/output; `partial` and provenance identify the limitation |
| `usage.cost` / `cost_details.upstream_inference_cost` | Separate provider/gateway cost evidence, not an invoice |
| Native `_calculate_cost` result / trajectory `extra.cost` | `source_calculated_cost` and compatibility `cost_usd`; zero may be a configured fallback, not proof of a free invoice |

Negative, fractional, boolean, nonfinite, oversized, and textual token counts are
rejected with field-level warnings. Conflicting cache subtotals cannot create
negative input or inflate a reliable prompt total: their raw values remain in
`reported_usage`, while conflicting categories are excluded from normalized
pricing. Conflicting reasoning/TTL breakdowns are likewise flagged. Inspect
`missing_usage_fields`, `usage_warnings`, `partial`, and `total_provenance` before
calling a partial result complete. Historical LiteLLM cache-write conventions
must be checked against the producing SDK, not inferred from a model name.

The ledger's existing `pricing.json` and `price_event` remain the API-equivalent
pricing authority. There is no new pricing database. Missing prices do not remove
token events; unknown-priced models remain unpriced with the existing report
annotation. Local models retain tokens, including when source cost is zero.
Source costs are not substituted for list-price estimates unless the operator
explicitly configures the existing `use_logged_cost` pricing option. Provider
cost units may be gateway credits; these fields are evidence, not invoices.
This integration deliberately preserves existing mini cost limits and errors,
including the pinned Portkey missing-total failure rather than silently relaxing it.

## Identity, replay, and reliability boundaries

A response ID is namespaced by the observed upstream provider when available,
falling back to the configured provider, and by the observed model. The
reporting `provider` routing label and `upstream_provider` evidence are both
preserved. Different providers returning the same ID/model must not collapse;
the same observed provider response reached through different routing labels
must not be counted twice. Without a response ID, the
exported invocation UUID is used. These keys survive copies, resumed history,
repeated scans, and trajectory/export overlap **on the same ledger host identity**.
Source IDs, invocation/run/agent IDs, and response-vs-configuration model provenance
are retained separately. A provider ID is not a tool-call ID. Reused provider IDs
are assumed to identify the same response; an adapter that reuses IDs for distinct
calls must supply trustworthy distinct IDs before exact reconciliation is possible.

For legacy records without invocation IDs, a conservative path/session/message
ordinal/time/usage key is used. Identical no-ID records in different files are
not collapsed. Consequently relocated/copy-only no-ID logs cannot be perfectly
deduplicated; overwritten indistinguishable no-ID histories cannot be recovered.
The final run configuration is a labeled fallback only when a per-call model is
unavailable. Legacy trajectories often lack session/run/time metadata; those
missing values are not invented from file modification times.

Experimental imports from before the observed-provider identity fix should be
rebuilt from approved source records before using the corrected collector;
append-only stores do not migrate earlier routing-only identity keys.

The existing append-only stores remain append-only. A scan during an invocation
can ingest its provisional record; subsequent scans add no duplicate tokens but
cannot enrich already-ingested status/cost evidence in place. For settled evidence,
scan after execution or retain/rebuild from the final usage records. Concurrent
exporters are supported; serialize ledger writes for JSON/CSV stores and prefer
SQLite when ledger ingestion processes might overlap. Cross-host mirror copies
still require consistent host naming under the existing store identity contract.

## Verify the result

```sh
python -m unittest discover -s tests -p 'test_package_mini_swe*.py' -v
# In a separate test environment with the pinned mini source and its SDKs:
python -m pytest tests/test_mini_swe_native.py -v
python scripts/compile_ai_logs.py report \
  --events /absolute/private/mini-scan/events.workstation-mini.jsonl \
  --out-dir /absolute/private/mini-report
```

The native tests run actual adapters against localhost APIs and execute a
`DefaultAgent` run using LiteLLM then OpenRouter. They compare every normalized
token category with synthetic provider evidence, verify report pricing using
explicitly synthetic rates, ingest twice, and require zero second-pass additions.
They separately exercise rejected actions, retries, missing pricing, native limits,
and process termination immediately before cost calculation. The CI artifact
`mini-swe-reconciliation` contains the reconciliation receipt and dependency list.
Core tests cover all three stores, malformed inputs, source immutability, consent,
concurrent exporters, partial metadata, cache writes/TTLs, and anonymization.

No prompt, completion, command/tool output, credential, raw exception text, or
arbitrary model configuration is included in usage exports or normalized records.
Native trajectories themselves may contain sensitive text and keys; keep them
private. The anonymizer additionally pseudonymizes mini source/invocation/run/agent
identifiers. Existing publication checks still apply before sharing any report.

## Source audit

- [Pinned model registry and custom class loader](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/__init__.py)
- [Pinned LiteLLM response/cost/FormatError ordering](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/litellm_model.py)
- [Pinned Portkey pre-cost mutation and missing-total behavior](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/models/portkey_model.py)
- [Pinned agent save/termination/limit behavior](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py)
- [Upstream Portkey issue #935](https://github.com/SWE-agent/mini-swe-agent/issues/935) and [proposed fix #936](https://github.com/SWE-agent/mini-swe-agent/pull/936)
- [Upstream proposed cost fallback #952](https://github.com/SWE-agent/mini-swe-agent/pull/952)

These proposed upstream changes were not treated as merged source dependencies.
