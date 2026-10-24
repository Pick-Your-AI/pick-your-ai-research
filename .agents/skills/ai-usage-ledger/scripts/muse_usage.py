#!/usr/bin/env python3
"""Opt-in Muse Mesh usage imports and bounded reports using existing ledger APIs.

No discovery of personal log roots, prompts, credentials, scheduling or networking.
Run --help for the explicit scan command. See references/muse-mesh.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compile_ai_logs  # noqa: E402
import ledger_query  # noqa: E402
import ledger_store  # noqa: E402

SCHEMA = "mu-usage/1"
SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
FINAL_NAME = re.compile(r"(" + UUID + r")\.usage\.json\Z")
START_NAME = re.compile(r"(" + UUID + r")\.started\.json\Z")
MAX_RECORD = 128 * 1024
MAX_FILES = 10000
MAX_ROWS = 50000
SAFE_INT = 2**53 - 1
TOKEN_NAMES = ("input_tokens", "output_tokens", "total_tokens", "cache_read_tokens", "cache_write_tokens", "reasoning_tokens")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _text(value, name, optional=False):
    if value is None and optional:
        return None
    if not isinstance(value, str) or not 1 <= len(value) <= 256 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("invalid " + name)
    return value


def _count(value, name):
    if value is None:
        return None
    if type(value) is not int or not 0 <= value <= SAFE_INT:
        raise ValueError("invalid count: " + name)
    return value


def _timestamp(value):
    value = _text(value, "timestamp")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("timestamp must include timezone")
    return stamp.astimezone(timezone.utc).isoformat()


def safe_path(path, *, directory=False, private=False):
    """Reject symlinks (including ancestors), devices, and writable shared config.

    POSIX confidentiality also requires the leaf source directory/data file to be
    owner-only. On Windows the operator must configure equivalent account ACLs.
    """
    p = Path(path)
    if not p.is_absolute():
        raise ValueError("configured paths must be absolute")
    for part in (p, *p.parents):
        if part.is_symlink():
            raise ValueError("symlinks are not permitted")
    info = p.stat()
    if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise ValueError("expected a regular usage file or directory")
    if os.name != "nt":
        if info.st_uid != os.getuid() or info.st_mode & (0o077 if private else 0o022):
            raise PermissionError("owner permissions are required")
    return p


def read_json(path, *, private=False, limit=MAX_RECORD):
    path = safe_path(path, private=private)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError("usage/config file is not a bounded regular file")
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("usage/config file is too large")
    data = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    return data


def config_path():
    return Path(os.environ.get("AI_USAGE_LEDGER_HOME", str(Path.home() / ".ai-usage-ledger"))) / "config.json"


def load_config(path):
    """Read without invoking ledger.load_config(), whose migration can write files."""
    config = read_json(path, private=True)
    options = config.get("muse_mesh")
    if not isinstance(options, dict) or type(options.get("version")) is not int or options["version"] != 1:
        raise PermissionError("Muse integration is not configured")
    for field in ("collection_enabled", "reporting_enabled", "allow_scan"):
        if field in options and type(options[field]) is not bool:
            raise ValueError("integration switches must be booleans")
    store = config.get("store", {})
    if not isinstance(store, dict) or store.get("kind") != "sqlite" or not isinstance(store.get("path"), str) or not Path(store["path"]).is_absolute():
        raise ValueError("live Muse integration requires an explicit SQLite store")
    sources = options.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 32:
        raise ValueError("configure between one and 32 approved Muse sources")
    ids = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("invalid source")
        for key in ("id", "provider"):
            if not isinstance(source.get(key), str) or not SLUG.fullmatch(source[key]):
                raise ValueError("invalid source identity")
        if source["id"] in ids:
            raise ValueError("duplicate source identity")
        ids.add(source["id"])
        if not isinstance(source.get("path"), str) or not Path(source["path"]).is_absolute():
            raise ValueError("source path must be absolute")
        if source.get("id_mode", "hmac-sha256") not in ("hmac-sha256", "literal"):
            raise ValueError("invalid identity mode")
    return config


def authorize(config, capability):
    options = config.get("muse_mesh", {})
    consent = {"collection": "local-usage-metadata", "reporting": "share-usage-aggregates"}[capability]
    if options.get(capability + "_enabled") is not True or options.get(capability + "_consent") != consent:
        raise PermissionError(capability + " consent is required")


def normalize(record, source):
    """Normalize only allowlisted metadata, preserving nullable measurements.

    Native response IDs are preferred over persistent pre-request UUIDs. Import
    location, scan time, retries and token quantities never enter the natural ID.
    """
    if record.get("schema") != SCHEMA or record.get("source_id") != source["id"] or record.get("provider") != source["provider"]:
        raise ValueError("usage source/schema mismatch")
    mode = record.get("id_mode")
    if mode != source.get("id_mode", "hmac-sha256"):
        raise ValueError("identity mode changed; preserve the original source/key")
    invocation = _text(record.get("invocation_id"), "invocation identity")
    if not re.fullmatch(UUID, invocation):
        raise ValueError("invocation identity must be a persisted UUID")
    native = _text(record.get("response_id"), "response identity", True)
    session = _text(record.get("session_id"), "session identity", True)
    run = _text(record.get("run_id"), "run identity", True)
    if mode == "hmac-sha256":
        for value in (native, session, run):
            if value is not None and not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("invalid pseudonymous identity")
    status = record.get("status")
    if status not in ("completed", "failed", "cancelled", "interrupted"):
        raise ValueError("started invocations are coverage, not final usage events")
    operation = record.get("operation")
    if operation not in ("agent", "memory", "web", "unscoped"):
        raise ValueError("invalid operation")
    ordinal = _count(record.get("invocation_ordinal"), "invocation ordinal")
    if ordinal is None or ordinal == 0:
        raise ValueError("invocation ordinal must be positive")
    usage_source = record.get("usage_source")
    if usage_source not in ("openai_chat_response_usage", "unavailable", "estimated"):
        raise ValueError("unrecognized usage provenance")
    values = {name: _count(record.get(name), name) for name in TOKEN_NAMES}
    model = _text(record.get("model"), "model")
    configured = _text(record.get("configured_model"), "configured model")
    ts = _timestamp(record.get("timestamp"))
    started = _timestamp(record.get("started_at"))
    stamp_source = record.get("timestamp_source")
    if stamp_source not in ("provider_created", "local_request_start"):
        raise ValueError("timestamp provenance is required")
    if type(record.get("capture_incomplete")) is not bool:
        raise ValueError("capture completeness must be explicit")
    amount = record.get("reported_charge_usd")
    if amount is not None and (type(amount) not in (int, float) or not math.isfinite(amount) or not 0 <= amount <= 1e12):
        raise ValueError("invalid reported charge")
    charge_source = record.get("charge_source")
    if (amount is None and charge_source is not None) or (amount is not None and charge_source != "gateway_usage_cost"):
        raise ValueError("reported charge provenance is required")
    semantics = record.get("input_semantics")
    if semantics not in ("openai-chat", "inclusive-cache"):
        raise ValueError("input/cache semantics must be explicit")
    inp, out, cached, written = (values[k] for k in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"))
    if semantics == "openai-chat" and written not in (None, 0):
        raise ValueError("OpenAI chat usage does not define separately billed cache writes")
    if inp is not None and sum(v or 0 for v in (cached, written)) > inp:
        raise ValueError("cached tokens exceed input")
    if out is not None and values["reasoning_tokens"] is not None and values["reasoning_tokens"] > out:
        raise ValueError("reasoning exceeds output")
    total = values["total_tokens"]
    if inp is not None and out is not None:
        if inp + out > SAFE_INT or (total is not None and total != inp + out):
            raise ValueError("inconsistent total tokens")
        total = inp + out
    estimates = None
    if usage_source == "estimated":
        estimates = values.copy()
        values = dict.fromkeys(TOKEN_NAMES)
        inp = out = cached = written = total = None
    if usage_source == "unavailable" and any(v is not None for v in values.values()):
        raise ValueError("unavailable usage cannot contain measured tokens")
    partition_known = inp is not None and cached is not None and (written is not None or semantics == "openai-chat")
    eligible = (partition_known and out is not None and not record["capture_incomplete"]
                and usage_source == "openai_chat_response_usage" and status == "completed")
    # Persist native observations. Unsupported/missing cache-write detail remains null;
    # OpenAI chat's input total already includes any cache activity in that protocol.
    event = {
        "tool": "mu", "host": source["id"], "ts": ts, "date": ts[:10], "session": session,
        "model": model, "input_uncached": inp - cached - (written or 0) if partition_known else None,
        "cache_read": cached, "cache_write": written, "cache_write_5m": None, "cache_write_1h": None,
        "output": out, "reasoning": values["reasoning_tokens"], "total": total,
        "cwd": None, "kind": operation, "entrypoint": "muse-mesh", "version": SCHEMA,
        "cost_usd": amount, "src": "mu-usage:" + source["id"], "provider": source["provider"],
        "source_id": source["id"], "run_id": run, "invocation_id": invocation, "native_response_id": native,
        "invocation_ordinal": ordinal, "retry_of": None, "status": status, "configured_model": configured,
        "started_at": started, "timestamp_source": stamp_source, "usage_source": usage_source,
        "input_tokens": inp, "input_semantics": semantics, "capture_incomplete": record["capture_incomplete"],
        "usage_pricing_eligible": bool(eligible), "estimated_usage": estimates,
        "charge_source": charge_source, "id_mode": mode,
    }
    identity = [SCHEMA, source["id"], source["provider"], "response" if native else "invocation", native or invocation]
    event["request_id"] = hashlib.sha256(canonical(identity).encode()).hexdigest()
    evidence = {key: event[key] for key in ("model", "input_tokens", "input_uncached", "cache_read", "cache_write", "output",
                                           "reasoning", "total", "cost_usd", "usage_source", "input_semantics", "capture_incomplete",
                                           "charge_source", "estimated_usage", "status", "usage_pricing_eligible")}
    event["evidence_sha256"] = hashlib.sha256(canonical(evidence).encode()).hexdigest()
    return event


def scan(config):
    """Import only fixed approved directories, in one verified SQLite transaction."""
    authorize(config, "collection")
    records, unfinished, files = [], 0, 0
    for source in config["muse_mesh"]["sources"]:
        root = safe_path(source["path"], directory=True, private=True)
        finals, starts = {}, set()
        with os.scandir(root) as entries:
            for entry in entries:
                files += 1
                if files > MAX_FILES:
                    raise ValueError("source inventory exceeds limit; rotate reviewed source archives")
                final = FINAL_NAME.fullmatch(entry.name)
                start = START_NAME.fullmatch(entry.name)
                if final:
                    final_id = final.group(1)
                    row = read_json(entry.path, private=True)
                    if row.get("invocation_id") != final_id:
                        raise ValueError("filename and invocation identity differ")
                    finals[final_id] = normalize(row, source)
                elif start:
                    starts.add(start.group(1))
        unfinished += len(starts - finals.keys())
        records.extend(finals.values())
    destination = Path(config["store"]["path"])
    safe_path(destination.parent, directory=True, private=True)
    if destination.exists() or destination.is_symlink():
        safe_path(destination, private=True)
    store = ledger_store.Store.open("sqlite", str(destination))
    try:
        added, skipped = store.ingest_verified_events(records)
    finally:
        store.close()
    return {"added": added, "skipped": skipped, "final_records": len(records), "unfinished_invocations": unfinished,
            "incomplete_usage_records": sum(not r["usage_pricing_eligible"] for r in records)}


def filters(config, arguments):
    allowed = {"since", "until", "model", "provider", "session", "limit"}
    if not isinstance(arguments, dict) or arguments.keys() - allowed:
        raise ValueError("unsupported report argument")
    args = dict(arguments)
    for name in ("since", "until"):
        if name in args:
            if not isinstance(args[name], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args[name]):
                raise ValueError("dates must be YYYY-MM-DD")
            date.fromisoformat(args[name])
    if args.get("since", "") > args.get("until", "9999-12-31"):
        raise ValueError("invalid date range")
    limit = args.get("limit", 100)
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError("limit must be between one and 500")
    where, bindings = ["tool='mu' AND version='mu-usage/1'"], []
    sources = config["muse_mesh"]["sources"]
    where.append("(" + " OR ".join("(host=? AND json_extract(extra,'$.provider')=?)" for _ in sources) + ")")
    for source in sources:
        bindings.extend([source["id"], source["provider"]])
    for name, operator, field in (("since", ">=", "date"), ("until", "<=", "date"), ("model", "=", "model"),
                                   ("session", "=", "session"), ("provider", "=", "json_extract(extra,'$.provider')")):
        if name in args:
            _text(args[name], name)
            where.append(field + operator + "?")
            bindings.append(args[name])
    return " AND ".join(where), bindings, limit


def report(config, name, arguments):
    """Read-only, fixed queries. No SQL, paths, prompt text or config in tool arguments."""
    authorize(config, "reporting")
    where, bindings, limit = filters(config, arguments)
    safe_path(config["store"]["path"], private=True)
    db = ledger_query.open_db("sqlite", config["store"]["path"])
    try:
        db.execute("PRAGMA query_only=ON")
        if name == "ledger_status":
            if arguments:
                raise ValueError("status takes no arguments")
            cols, rows = ledger_query.run_query(db, "SELECT COUNT(*) AS recorded_attempts FROM events WHERE " + where, bindings)
            return {"schema": SCHEMA, "store_kind": "sqlite", "source_count": len(config["muse_mesh"]["sources"]),
                    "recorded_attempts": rows[0][0], "collection_enabled": config["muse_mesh"].get("collection_enabled") is True,
                    "reporting_enabled": True}
        if name == "ledger_cost_breakdown":
            cols, rows = ledger_query.run_query(db, "SELECT " + ",".join(ledger_store.EVENT_COLUMNS) + ",extra FROM events WHERE " + where, bindings, MAX_ROWS + 1)
            if len(rows) > MAX_ROWS:
                raise ValueError("cost query exceeds limit; narrow the date range")
            pricing = read_json(config["pricing_path"], limit=4 * 1024 * 1024)
            snapshot = hashlib.sha256(canonical(pricing).encode()).hexdigest()
            result = {"observed_reported_charge_usd": 0.0, "charged_records": 0, "api_equivalent_usd": 0.0,
                      "priced_records": 0, "unpriced_records": 0, "assumed_records": 0, "pricing_sha256": snapshot,
                      "pricing_date": pricing.get("_as_of"), "notes": []}
            notes = set()
            for row in rows:
                event = dict(zip(cols, row))
                extra = json.loads(event.pop("extra") or "{}")
                event["usage_pricing_eligible"] = extra.get("usage_pricing_eligible")
                amount = event.get("cost_usd")
                if amount is not None:
                    result["observed_reported_charge_usd"] += float(amount)
                    result["charged_records"] += 1
                cost, _, priced_as, assumed = compile_ai_logs.price_event(event, pricing)
                rate = pricing.get("models", {}).get(priced_as, {})
                if priced_as is None or rate.get("use_logged_cost"):
                    result["unpriced_records"] += 1
                    notes.add(assumed or "No applicable API rate; reported charges are not list prices")
                else:
                    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
                        raise ValueError("invalid configured pricing")
                    result["api_equivalent_usd"] += cost
                    result["priced_records"] += 1
                    original = event["model"]
                    direct = original in pricing.get("models", {}) or ("/" in original and original.split("/", 1)[1] in pricing.get("models", {}))
                    if not direct:
                        assumed = assumed or "Tool fallback rate: " + str(priced_as)
                    if event.get("cache_write") and event.get("cache_write_5m") is None:
                        assumed = (str(assumed) + "; " if assumed else "") + "Cache-write TTL unknown; existing ledger five-minute fallback"
                    if assumed:
                        result["assumed_records"] += 1
                        notes.add(str(assumed)[:512])
            for amount, count in (("observed_reported_charge_usd", "charged_records"), ("api_equivalent_usd", "priced_records")):
                if result[count] == 0:
                    result[amount] = None
            result["notes"] = sorted(notes)[:50]
            result["charge_evidence"] = "gateway-reported usage.cost; not an invoice or proof of payment"
            return result
        groups = {"ledger_usage_summary": None, "ledger_usage_by_model": "model",
                  "ledger_usage_by_provider": "json_extract(extra,'$.provider')", "ledger_usage_by_session": "session"}
        if name not in groups:
            raise ValueError("unknown reporting tool")
        group = groups[name]
        # Existing ledger SUMS/run_query remain the accounting query primitives.
        sums = ledger_query.SUMS + ", SUM(json_extract(extra,'$.input_tokens')) AS input_tokens"
        sums += ", SUM(CASE WHEN json_extract(extra,'$.usage_pricing_eligible')=0 THEN 1 ELSE 0 END) AS incomplete_usage_records"
        sums += ", SUM(CASE WHEN total IS NULL THEN 1 ELSE 0 END) AS missing_total_records"
        sums += ", SUM(CASE WHEN json_extract(extra,'$.status')!='completed' THEN 1 ELSE 0 END) AS noncompleted_records"
        sums += ", SUM(CASE WHEN cost_usd IS NOT NULL THEN 1 ELSE 0 END) AS reported_charge_records"
        sql = "SELECT " + (group + " AS group_key, " if group else "") + sums + " FROM events WHERE " + where
        if group:
            sql += " GROUP BY " + group + " ORDER BY total DESC, group_key"
        cols, rows = ledger_query.run_query(db, sql, bindings, limit + 1 if group else None)
        output = []
        for row in rows[:limit]:
            item = dict(zip(cols, row))
            if not item["reported_charge_records"]:
                item["logged_cost_usd"] = None
            output.append(item)
        return {"rows": output, "truncated": len(rows) > limit, "tokens": "observed only; null means unavailable",
                "calls": "recorded HTTP attempts, including failures; retries with the same native ID deduplicate"}
    finally:
        db.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["scan"])
    ap.add_argument("--config", type=Path, default=config_path())
    args = ap.parse_args()
    try:
        print(json.dumps(scan(load_config(args.config)), sort_keys=True))
    except (OSError, ValueError, KeyError) as exc:
        print("Muse import refused: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
