# Reports for an exact time window

Use `ledger.py report` when the requested deliverable is a report for a day, "since midnight", or a precise interval. It queries the existing append-only ledger, filters events before aggregating or pricing, and renders a dedicated report. The full-history dashboard and study remain separate outputs.

```bash
python scripts/ledger.py report --since today --tz America/New_York
python scripts/ledger.py report --since 2026-10-03 --until 2026-10-03 --tz America/New_York
python scripts/ledger.py report --since 2026-10-03T00:00:00-04:00 --until 2026-10-03T16:49:12.602-04:00 --tz America/New_York --pricing templates/pricing.json --out reports/october-3-afternoon
```

These commands require an initialized ledger. They read only its stored events and configuration; they do not rediscover hosts, scan transcripts, read credentials, capture prompts, install schedules or change the source store. If fresher records are needed, run the existing authorized refresh separately, then generate the report. The report's latest recorded event describes the available evidence; it does not certify that every configured host was scanned through the requested cutoff.

## Time boundaries

- `--since` is required. `today` means midnight in `--tz`; a date means the beginning of that local day. The start is inclusive.
- `--until` defaults to the current instant; `now` has the same meaning. A timestamp end is inclusive. A date includes that whole local day, using the following local midnight as an exclusive boundary.
- `--tz` defaults to the saved ledger timezone. Supply the operator's zone when it differs from that setting. Explicit timestamp offsets determine the instant; the chosen zone controls local display and date inputs.
- Offset-free timestamps are interpreted in the chosen zone. Ambiguous or nonexistent times at a daylight-saving transition require an explicit offset. Reversed ranges are rejected.
- Scoped reports require Python 3.9 or later (`zoneinfo`); the tested CI baseline is Python 3.12. On a host without an IANA timezone database, install the optional `tzdata` package in the interpreter used for the ledger.

The report and JSON carry the exact bounds, timezone and whether the end is inclusive. The older `query --since/--until` flags compare stored date columns and are not a substitute for this timestamp filter.

## Pricing and evidence

The default price file is the saved ledger snapshot. `--pricing <file>` uses a different snapshot for this report only; it does not replace operator configuration or retroactively edit stored events. Review the selected snapshot's model rows and sources before trusting a dollar estimate.

The bundled template records per-model `source`, `verified_at` and `service_tier` for the refreshed GPT-6, Opus 5.5 and Sonnet 5.5 rows. The Claude 5.5 rows were verified on 2026-10-11, including their 0.05x cache-read rates. Existing saved snapshots are not replaced automatically: use `--pricing templates/pricing.json` for a report-only update. Verification dates on those rows do not certify every historical row in the file. Models missing from the selected snapshot retain explicit fallback assumptions, and unpriced calls remain visible as incomplete valuation rather than free usage.

Rates are USD per million tokens. Existing flat rows remain supported. A row may optionally contain `long_context`, with `input_tokens_gt` and replacement input, cache-read, cache-write and output rates. The pricing function selects that tier per call when the complete prompt exceeds the threshold, including cached input and cache writes. The bundled GPT-6 threshold is greater than 272,000 input tokens. Claude Sonnet 5.5 uses its standard rate across the supported context window.

Dollar metrics are API token equivalents using the supplied snapshot and its listed rate tiers. They are not invoices or an allocation of a monthly subscription fee to a partial day. Additional service-tier premiums, regional uplifts and usage categories absent from the stored records are not inferred. Replay removal and ingestion deduplication belong to the existing scanner/store; generating a scoped report neither rescans nor repeats those transformations.

The report shows pricing provenance and assumptions alongside its metrics. It does not compare a partial-day total with lifetime tool counters or claim an intraday provider-counter validation.

## Outputs and review

Without `--out`, the command creates a new report directory under the configured working directory's `reports` tree. An explicit output directory must be new or empty; existing reports are not silently overwritten. The package contains:

| File | Purpose |
|---|---|
| `report.html` | Self-contained branded report with the saved theme, exact interval and token/cost breakdowns. |
| `report-data.json` | Machine-readable scope, metrics, evidence and pricing assumptions. |
| `pricing.json` | The price snapshot used by this report. |
| `events.csv` | Usage records included in this interval, without prompt text or raw source paths. |
| `SHA256SUMS` | Checksums binding the report artifacts. |

Outputs use the ledger's private-file helpers. They still reveal tools, models and usage patterns; review and follow the existing anonymization/publication boundaries before sharing. Successful rendering or matching checksums do not authorize publication.

Validate with synthetic data: `python -m unittest discover -s tests -p 'test_scoped_report.py' -v` and `python -m unittest discover -s tests -p 'test_pricing.py' -v`. The full Quality gate runs both suites in addition to the existing checks.
