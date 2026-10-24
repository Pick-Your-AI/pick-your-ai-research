#!/usr/bin/env python3
"""Build a private, time-scoped usage report from the existing ledger, without scanning.

Start bounds are inclusive. Timestamp/``now`` end bounds are inclusive; a date
end includes that entire local calendar day, ending exclusively at the following
midnight. Naive timestamps use the selected timezone and must be unambiguous.
"""
import argparse
import csv
import hashlib
import html
import json
import math
import re
import sqlite3
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compile_ai_logs  # noqa: E402
import ledger_query  # noqa: E402
import render_ledger_doc  # noqa: E402
import safety  # noqa: E402

UTC = timezone.utc
TOKEN_FIELDS = ("input_uncached", "cache_read", "cache_write", "output", "reasoning", "total")
TTL_FIELDS = ("cache_write_5m", "cache_write_1h")
RATE_FIELDS = ("input", "cache_read", "cache_write_5m", "cache_write_1h", "output")
READ_FIELDS = ("ts", "tool", "host", "session", "model", *TOKEN_FIELDS, *TTL_FIELDS, "cost_usd")
EXPORT_FIELDS = ("ts", "tool", "model", *TOKEN_FIELDS, *TTL_FIELDS, "priced_as", "pricing_status",
                 "pricing_note", "api_equivalent_usd", "without_cache_usd", "cache_savings_usd")
COST_FIELDS = ("api_equivalent_usd", "without_cache_usd", "cache_savings_usd", "assumed_cost_usd")


@dataclass(frozen=True)
class Scope:
    start: datetime
    end: datetime
    tz: ZoneInfo
    end_inclusive: bool

    def contains(self, instant):
        return self.start <= instant and (instant <= self.end if self.end_inclusive else instant < self.end)

    def as_dict(self):
        return {"start_utc": self.start.isoformat(), "end_utc": self.end.isoformat(),
                "start_local": self.start.astimezone(self.tz).isoformat(),
                "end_local": self.end.astimezone(self.tz).isoformat(),
                "timezone": self.tz.key, "start_inclusive": True, "end_inclusive": self.end_inclusive}


def _localize(value, tz):
    """Round-trip both folds, rejecting gaps and repeated local clock times."""
    instants = set()
    for fold in (0, 1):
        instant = value.replace(tzinfo=tz, fold=fold).astimezone(UTC)
        if instant.astimezone(tz).replace(tzinfo=None) == value:
            instants.add(instant)
    if len(instants) != 1:
        kind = "nonexistent" if not instants else "ambiguous"
        raise ValueError("%s local time %s in %s; supply an ISO timestamp with an explicit UTC offset" %
                         (kind, value.isoformat(), tz.key))
    return instants.pop()


def _timestamp(value):
    # datetime silently truncates longer fractions; do not silently move a bound.
    if re.search(r"[.,]\d{7,}", value):
        raise ValueError("timestamps support at most six fractional-second digits")
    if not re.match(r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}", value):
        raise ValueError("expected YYYY-MM-DD or an ISO timestamp, got %r" % value)
    return datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value)


def parse_scope(since, until=None, tz="UTC", now=None):
    try:
        zone = ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as ex:
        raise ValueError("timezone %r is unavailable; use an installed IANA timezone such as UTC" % tz) from ex
    clock = now or datetime.now(UTC)
    if clock.tzinfo is None or clock.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    clock = clock.astimezone(UTC)

    def bound(raw, end=False):
        raw = raw.strip()
        if raw == "now" and end:
            return clock, True
        if raw == "today":
            local_date = clock.astimezone(zone).date()
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            local_date = date.fromisoformat(raw)
        else:
            stamp = _timestamp(raw)
            instant = _localize(stamp, zone) if stamp.tzinfo is None else stamp.astimezone(UTC)
            return instant, True
        if end:
            local_date += timedelta(days=1)
        return _localize(datetime.combine(local_date, time.min), zone), not end

    start, _ = bound(since)
    end, inclusive = bound(until or "now", end=True)
    if start > end or (start == end and not inclusive):
        raise ValueError("--until precedes --since (date end bounds are exclusive at the following midnight)")
    return Scope(start, end, zone, inclusive)


def _read_json(path, label):
    safety.refuse_if_shared(str(path), label)
    with Path(path).open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("%s must contain a JSON object" % label)
    return data


def iter_stored_events(kind, path):
    """Read only event columns, without opening credentials, sessions or prompts.

    FileStore construction repairs directories and opens every ID index; the
    file backends are therefore streamed directly instead of instantiated.
    """
    if kind == "sqlite":
        db = ledger_query.open_db(kind, str(path))
        try:
            cursor = db.execute("SELECT %s, CASE WHEN tool='mu' AND version='mu-usage/1' "
                                "THEN json_extract(CASE WHEN json_valid(extra) THEN extra ELSE '{}' END, "
                                "'$.usage_pricing_eligible') END FROM events" % ", ".join(READ_FIELDS))
            for row in cursor:
                event = dict(zip(READ_FIELDS, row[:-1]))
                event["usage_pricing_eligible"] = False if row[-1] == 0 else None
                yield event
        finally:
            db.close()
    elif kind in ("json", "csv"):
        source = Path(path) / ("events.jsonl" if kind == "json" else "events.csv")
        with source.open(encoding="utf-8", newline="") as fh:
            rows = (json.loads(line) for line in fh if line.strip()) if kind == "json" else csv.DictReader(fh)
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError("event store contains a non-object record")
                event = {key: row.get(key) for key in READ_FIELDS}
                if row.get("tool") == "mu" and row.get("version") == "mu-usage/1":
                    extra = json.loads(row.get("extra") or "{}") if kind == "csv" else row
                    event["usage_pricing_eligible"] = extra.get("usage_pricing_eligible")
                yield event
    else:
        raise ValueError("unsupported store kind %r" % kind)


def _count(value, key):
    if value in (None, ""):
        return 0
    number = Decimal(str(value))
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError("invalid nonnegative integer token field: %s" % key)
    return int(number)


def _normalize(event):
    event = dict(event)
    for key in TOKEN_FIELDS:
        event[key] = _count(event.get(key), key)
    for key in TTL_FIELDS:
        value = event.get(key)
        event[key] = None if value in (None, "") else _count(value, key)
    if event.get("usage_pricing_eligible") is not False and event["total"] != sum(event[key] for key in ("input_uncached", "cache_read", "cache_write", "output")):
        raise ValueError("stored event total does not equal its token categories")
    if event["reasoning"] > event["output"]:
        raise ValueError("stored reasoning tokens exceed output tokens")
    if event["cache_write_5m"] is None:
        # Missing TTL detail follows price_event's documented five-minute rule.
        if event["cache_write_1h"]:
            raise ValueError("cache-write TTL split is incomplete")
    elif event["cache_write_5m"] + (event["cache_write_1h"] or 0) != event["cache_write"]:
        raise ValueError("cache-write TTL split does not equal cache_write")
    event["tool"] = str(event.get("tool") or "unknown")
    event["model"] = str(event.get("model") or "?")
    return event


def _new_group():
    group = dict.fromkeys(("calls", "priced_calls", "unpriced_calls", "unpriced_tokens", "assumed_calls",
                           "assumed_tokens", *TOKEN_FIELDS), 0)
    group.update({key: Decimal(0) for key in COST_FIELDS})
    return group


def _price(event, pricing):
    try:
        cost, uncached, priced_as, assumed = compile_ai_logs.price_event(event, pricing)
    except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as ex:
        raise ValueError("invalid pricing for model %r" % event["model"]) from ex
    row = pricing.get("models", {}).get(priced_as, {})
    if priced_as is None:
        return None, None, None, "unpriced", assumed or "No applicable model rate"
    if row.get("use_logged_cost"):
        return None, None, priced_as, "unpriced", "Logged charges are not a standard API rate"
    for rate_row in (row, row.get("long_context") or {}):
        for key in RATE_FIELDS:
            value = rate_row.get(key)
            if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                raise ValueError("invalid %s rate for model %r" % (key, event["model"]))
    for value in (cost, uncached):
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("non-finite or negative pricing result for model %r" % event["model"])
    original = event["model"]
    direct = original in pricing.get("models", {}) or (
        "/" in original and original.split("/", 1)[1] in pricing.get("models", {}))
    if not direct:
        # The shared pricer allows a fallback without a note; it is still an assumption.
        assumed = assumed or "Tool fallback rate: %s" % priced_as
    return cost, uncached, priced_as, "assumed" if assumed else "priced", str(assumed or "")


def _json_group(group):
    return {key: float(value) if isinstance(value, Decimal) else value for key, value in group.items()}


def collect(events, scope, pricing, generated_at):
    """Scope stored events before pricing and aggregating; never reapply replay filters."""
    totals = _new_group()
    tools, models = defaultdict(_new_group), defaultdict(_new_group)
    assumptions = {}
    sessions, hosts = set(), set()
    selected, latest, latest_selected = [], None, None
    unscopable = 0
    for raw in events:
        try:
            stamp = _timestamp(str(raw.get("ts") or ""))
            if stamp.tzinfo is None or stamp.utcoffset() is None:
                raise ValueError("stored timestamp has no UTC offset")
            stamp = stamp.astimezone(UTC)
        except (ValueError, TypeError, OverflowError):
            unscopable += 1
            continue
        latest = stamp if latest is None else max(latest, stamp)
        if not scope.contains(stamp):
            continue
        event = _normalize(raw)
        cost, uncached, priced_as, status, note = _price(event, pricing)
        latest_selected = stamp if latest_selected is None else max(latest_selected, stamp)
        if event.get("session"):
            sessions.add((event["tool"], event.get("host"), event["session"]))
        if event.get("host"):
            hosts.add(event["host"])
        for group in (totals, tools[event["tool"]], models[event["model"]]):
            group["calls"] += 1
            for key in TOKEN_FIELDS:
                group[key] += event[key]
            group["unpriced_calls" if status == "unpriced" else "priced_calls"] += 1
            if status == "unpriced":
                group["unpriced_tokens"] += event["total"]
            else:
                group["api_equivalent_usd"] += Decimal(str(cost))
                group["without_cache_usd"] += Decimal(str(uncached))
                group["cache_savings_usd"] += Decimal(str(uncached)) - Decimal(str(cost))
            if status == "assumed":
                group["assumed_calls"] += 1
                group["assumed_tokens"] += event["total"]
                group["assumed_cost_usd"] += Decimal(str(cost))
        if status != "priced":
            key = (event["model"], priced_as, status, note)
            item = assumptions.setdefault(key, {"model": event["model"], "priced_as": priced_as,
                                               "status": status, "note": note, "calls": 0, "tokens": 0})
            item["calls"] += 1
            item["tokens"] += event["total"]
        record = {key: event.get(key) for key in EXPORT_FIELDS if key in event}
        record.update(ts=stamp.isoformat(), priced_as=priced_as, pricing_status=status, pricing_note=note,
                      api_equivalent_usd=cost, without_cache_usd=uncached,
                      cache_savings_usd=None if cost is None else uncached - cost)
        selected.append(record)
    selected.sort(key=lambda event: event["ts"])
    metadata = {"schema_version": 1, "generated_at_utc": generated_at.astimezone(UTC).isoformat(),
                "scope": scope.as_dict(), "source": {"kind": "existing per-call ledger records", "rescanned": False},
                "freshness": {"latest_recorded_event_utc": latest.isoformat() if latest else None,
                              "latest_in_scope_event_utc": latest_selected.isoformat() if latest_selected else None},
                "totals": _json_group(totals), "sessions": len(sessions), "contributing_hosts": len(hosts),
                "by_tool": {key: _json_group(value) for key, value in sorted(tools.items())},
                "by_model": {key: _json_group(value) for key, value in sorted(models.items())},
                "pricing": {"snapshot_date": pricing.get("_as_of"), "sources": pricing.get("_sources", []),
                            "assumed_share_of_priced_cost": float(totals["assumed_cost_usd"] / totals["api_equivalent_usd"])
                            if totals["api_equivalent_usd"] else None,
                            "exceptions": list(assumptions.values())},
                "limitations": {"records_with_unusable_timestamps": unscopable,
                                "counter_validation": "No same-period provider-counter comparison performed",
                                "subscription_spend": "Not calculated",
                                "replay_handling": "Uses stored events; does not repeat ingestion de-duplication or replay filtering",
                                "csv_formula_escaping": "Formula-like text cells have a leading apostrophe"}}
    return metadata, selected


def _presentation(config):
    brand = dict(config.get("branding") or {})
    theme = config.get("theme") or "system"
    report_path = config.get("report_config_path")
    if report_path:
        rc = _read_json(report_path, "report config")
        brand.update(rc.get("branding") or {})
        theme = rc.get("theme_default") or theme
    logo = brand.get("logo")
    if logo and not str(logo).startswith(("http:", "https:", "data:")) and not Path(logo).is_absolute():
        candidates = ([Path(report_path).resolve().parent / logo] if report_path else []) + [HERE.parent / logo]
        brand["logo"] = str(next((path for path in candidates if path.is_file()), candidates[0]))
    if str(brand.get("logo", "")).startswith("data:") and not re.fullmatch(
            r"data:image/[a-zA-Z0-9.+-]+;base64,[a-zA-Z0-9+/=\s]+", str(brand["logo"])):
        raise ValueError("branding.logo must be a local image or a base64 image data URI")
    return brand, theme


def render_report(data, pricing, brand, theme):
    """Reuse the document renderer while keeping record text literal in Markdown tables."""
    literals = {}

    def text(value):
        key = "SCOPED_LITERAL_%d_END" % len(literals)
        literals[key] = html.escape(str(value), quote=True)
        return key

    def table(headers, rows):
        return render_ledger_doc.table(headers, [[text(cell) for cell in row] for row in rows])

    def money(value):
        return "$%s" % format(value, ",.2f")

    def integer(value):
        return format(value, ",d")

    scope, totals = data["scope"], data["totals"]
    priced_label = "API equivalent (priced calls only)" if totals["unpriced_calls"] else "API equivalent"
    cache_pct = totals["cache_savings_usd"] / totals["without_cache_usd"] if totals["without_cache_usd"] else 0
    parts = ["# AI usage for the selected interval",
             "**%s through %s (%s); start inclusive, end %s.**" % (
                 text(scope["start_local"]), text(scope["end_local"]), text(scope["timezone"]),
                 "inclusive" if scope["end_inclusive"] else "exclusive"),
             "Every usage total below is limited to these timestamp bounds.", "## Usage and dollar metrics",
             table(["Metric", "Selected interval"], [
                 ["Recorded tokens", integer(totals["total"])], ["Recorded model calls", integer(totals["calls"])],
                 ["Sessions with recorded calls", integer(data["sessions"])],
                 [priced_label, money(totals["api_equivalent_usd"])],
                 ["Equivalent without caching (priced calls)", money(totals["without_cache_usd"])],
                 ["Estimated cache savings (priced calls)", "%s (%.1f%%)" % (money(totals["cache_savings_usd"]), 100 * cache_pct)],
                 ["Unpriced calls / tokens", "%s / %s" % (integer(totals["unpriced_calls"]), integer(totals["unpriced_tokens"]))]]),
             "These are API token equivalents using the supplied rate snapshot; rate tiers are listed below. "
             "They are not invoices or actual subscription charges. No additional tier or regional premiums are "
             "inferred. Unrecorded fees and unpriced calls are excluded from the dollar estimates. A configured "
             "long-context rate is applied when its threshold is exceeded.",
             "## By tool",
             table(["Tool", "Calls", "Tokens", priced_label, "Cache savings", "Unpriced calls"], [
                 [key, integer(value["calls"]), integer(value["total"]), money(value["api_equivalent_usd"]),
                  money(value["cache_savings_usd"]), integer(value["unpriced_calls"])]
                 for key, value in data["by_tool"].items()]),
             "## By model",
             table(["Model", "Calls", "Tokens", priced_label, "Unpriced calls"], [
                 [key, integer(value["calls"]), integer(value["total"]), money(value["api_equivalent_usd"]),
                  integer(value["unpriced_calls"])] for key, value in data["by_model"].items()]),
             "## Token breakdown", table(["Category", "Tokens"], [
                 [label, integer(totals[key])] for label, key in (
                     ("Uncached input", "input_uncached"), ("Cached input reads", "cache_read"),
                     ("Cache writes", "cache_write"), ("Output (includes reasoning)", "output"))]),
             "## Stored-record freshness",
             "Generated: %s. Latest recorded event in the store: %s. Latest event in this interval: %s." % (
                 text(data["generated_at_utc"]), text(data["freshness"]["latest_recorded_event_utc"] or "none"),
                 text(data["freshness"]["latest_in_scope_event_utc"] or "none")),
             "This command reads the existing ledger and does not refresh source logs. Latest-event timestamps "
             "indicate recorded activity, not proof that all configured hosts are current. Run `ledger.py run` "
             "to refresh the ledger before requesting a new report when needed.",
             "## Pricing and assumptions", "Rate snapshot date: %s. Verification dates and sources below "
             "belong to individual rate rows; a snapshot date does not verify every rate." % text(pricing.get("_as_of") or "unspecified")]
    share = data["pricing"]["assumed_share_of_priced_cost"]
    parts.append("Assumed rates account for %s calls, %s tokens and %s of the priced API equivalent (%s)." % (
        integer(totals["assumed_calls"]), integer(totals["assumed_tokens"]), money(totals["assumed_cost_usd"]),
        "%.1f%%" % (100 * share) if share is not None else "share unavailable: no priced cost"))
    exceptions = data["pricing"]["exceptions"]
    if exceptions:
        parts.append(table(["Model", "Applied model", "Status", "Calls", "Reason"], [
            [row["model"], row["priced_as"] or "none", row["status"], integer(row["calls"]), row["note"]]
            for row in exceptions]))
    applied = set()
    for model in data["by_model"]:
        match = model if model in pricing.get("models", {}) else model.split("/", 1)[-1]
        if match in pricing.get("models", {}):
            applied.add(match)
    applied.update(row["priced_as"] for row in exceptions if row["priced_as"])
    parts.append(table(["Rate model", "Verified at", "Service tier", "Source"], [
        [model, pricing["models"][model].get("verified_at", "unspecified"),
         pricing["models"][model].get("service_tier", "unspecified"),
         pricing["models"][model].get("source", "unspecified")]
        for model in sorted(applied)]))
    parts += ["The accompanying pricing.json records the rate snapshot and any fallback rules used.",
              "## Coverage and verification",
              "Only recorded per-call usage is counted. Source retention, malformed logs or missing usage "
              "fields can leave gaps; this report does not quantify missing source usage. "
              "No same-period provider-counter comparison is performed. Stored replay filtering and "
              "de-duplication are preserved; this report does not apply them again.",
              "%s stored records had missing, invalid or timezone-naive timestamps and could not be "
              "assigned to this interval. %s hosts contributed recorded calls." % (
                  integer(data["limitations"]["records_with_unusable_timestamps"]), integer(data["contributing_hosts"]))]
    page = render_ledger_doc.build_html("\n\n".join(parts), brand, "AI usage for the selected interval", "Usage report", theme)
    # Replace in one pass: dynamic text must never introduce another placeholder.
    page = re.sub(r"SCOPED_LITERAL_\d+_END", lambda match: literals.get(match.group(), match.group()), page)
    links = ['<a href="events.csv">Interval events (CSV)</a>', '<a href="report-data.json">Report data (JSON)</a>',
             '<a href="pricing.json">Pricing snapshot (JSON)</a>', '<a href="SHA256SUMS">File checksums</a>']
    sources = pricing.get("_sources", [])
    if isinstance(sources, str):
        sources = [sources]
    sources = list(sources or []) + [pricing["models"][model].get("source") for model in sorted(applied)]
    seen_sources = set()
    for source in sources:
        if isinstance(source, str) and source not in seen_sources:
            seen_sources.add(source)
            try:
                parsed = urlsplit(source)
            except ValueError:
                continue
            if parsed.scheme == "https" and parsed.netloc and not any(c.isspace() for c in source):
                links.append('<a href="%s" rel="noreferrer">%s</a>' % (html.escape(source, quote=True), html.escape(source)))
    page = page.replace('<div class="foot">', "<p>" + " · ".join(links) + '</p><div class="foot">', 1)
    page = page.replace('</style>', '.themebar{position:static;width:max-content;max-width:calc(100% - 32px);'
                        'margin:12px 16px 12px auto}.band{flex-wrap:wrap}.band img{max-width:100%;object-fit:contain}'
                        '@media(max-width:560px){.band .doctype{margin-left:0;width:100%}}'
                        '</style>', 1)
    # The shared renderer emits its theme script before the buttons exist. Defer
    # it until the body is present so saved/default theme and selected button agree.
    script = re.search(r'<script>.*?</script>', page, flags=re.DOTALL)
    if script:
        page = page[:script.start()] + page[script.end():] + script.group()
    return ('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1">' +
            page.replace('<div class="themebar"', '</head><body><div class="themebar"', 1) + '</body></html>')


def _check_out(path):
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        raise ValueError("report output must not be a symlink or junction")
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ValueError("report output must be a new or empty directory: %s" % path)


def _csv_text(value):
    if isinstance(value, str) and (value.startswith(("=", "+", "-", "@", "\t", "\r", "\n")) or
                                   value.lstrip().startswith(("=", "+", "-", "@"))):
        return "'" + value
    return value


def generate_report(config, since, until=None, tz=None, out=None, pricing_path=None, now=None):
    """Return (output Path, report data). Inputs and the existing store are never modified."""
    generated = now or datetime.now(UTC)
    scope = parse_scope(since, until, tz or config.get("timezone") or "UTC", generated)
    explicit_out = Path(out).expanduser().absolute() if out else None
    if explicit_out is not None:
        _check_out(explicit_out)
    price_path = pricing_path or config.get("pricing_path")
    if not price_path:
        raise ValueError("no pricing configured; supply --pricing")
    pricing = _read_json(price_path, "pricing snapshot")
    if not isinstance(pricing.get("models"), dict):
        raise ValueError("pricing snapshot must contain a models object")
    store = config.get("store") or {}
    if not store.get("path") or not store.get("kind"):
        raise ValueError("no store configured; run ledger.py init first")
    brand, theme = _presentation(config)
    data, events = collect(iter_stored_events(store["kind"], store["path"]), scope, pricing, generated)
    page = render_report(data, pricing, brand, theme)
    if explicit_out is None:
        reports = Path(config["workdir"]) / "reports"
        safety.private_dir(str(reports))
        output = Path(tempfile.mkdtemp(prefix="usage-%s-" % generated.strftime("%Y%m%d-%H%M%S"), dir=reports))
    else:
        _check_out(explicit_out)
        explicit_out.mkdir(parents=True, exist_ok=True, mode=0o700)
        output = explicit_out
    safety.private_dir(str(output))
    # A second writer sees a nonempty directory; exclusive output opens never overwrite a file.
    marker = output / ".report-writing"
    with safety.private_open(str(marker), "x"):
        pass
    artifacts = {"report.html": page, "report-data.json": json.dumps(data, indent=2, allow_nan=False) + "\n",
                 "pricing.json": json.dumps(pricing, indent=2, allow_nan=False) + "\n"}
    for name, content in artifacts.items():
        with safety.private_open(str(output / name), "x") as fh:
            fh.write(content)
    with safety.private_open(str(output / "events.csv"), "x", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for event in events:
            writer.writerow({key: _csv_text(value) for key, value in event.items()})
    with safety.private_open(str(output / "SHA256SUMS"), "x") as fh:
        for name in (*artifacts, "events.csv"):
            digest = hashlib.sha256((output / name).read_bytes()).hexdigest()
            fh.write("%s  %s\n" % (digest, name))
    marker.unlink()
    return output, data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", required=True, help="inclusive start: today, YYYY-MM-DD or ISO timestamp")
    parser.add_argument("--until", help="end: now (default), inclusive date, or inclusive ISO timestamp")
    parser.add_argument("--tz", help="IANA timezone for dates and naive timestamps (default: configured timezone)")
    parser.add_argument("--out", help="new or empty output directory (default: unique directory under workdir/reports)")
    parser.add_argument("--pricing", help="report-only pricing JSON override; the saved configuration is unchanged")
    args = parser.parse_args(argv)
    try:
        import ledger
        # load_config() can migrate a manifest and consent; reporting must be read-only.
        config = _read_json(ledger.config_path(), "ledger config")
        output, data = generate_report(config, args.since, args.until, args.tz, args.out, args.pricing)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, ArithmeticError) as ex:
        parser.exit(2, "report: %s\n" % ex)
    print(json.dumps({"report": str(output / "report.html"), "scope": data["scope"], "totals": data["totals"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
