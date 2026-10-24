"""Read native Goose usage without touching source databases or retaining transcripts.

Audited contract: Goose 1.54.0, session schema 17. See references/goose.md.
This module intentionally does not import pricing, accounts, or network clients.
"""
from __future__ import annotations

import hashlib
import json
import math
import ntpath
import os
import posixpath
import re
import sqlite3
import stat
import tempfile
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from safety import is_credential_file

SCHEMA_VERSION = 17
TOKEN_COLUMNS = ("input_tokens", "output_tokens", "total_tokens", "cache_read_tokens", "cache_write_tokens")
USAGE_COLUMNS = ("id", "session_id", "created_timestamp", "model", *TOKEN_COLUMNS, "cost", "cost_source", "is_compaction")
CAMEL_TOKENS = ("inputTokens", "outputTokens", "totalTokens", "cacheReadTokens", "cacheWriteTokens")
MAX_HEADER = 1024 * 1024


class SourceUnavailable(ValueError):
    """A non-sensitive coverage code, never a raw SQLite/source exception."""


def candidate_roots(home: str, platform: str, env: dict[str, str], roaming: str | None = None) -> list[str]:
    """Goose's choose_app_strategy uses XDG even on macOS, not Apple paths."""
    win = platform == "win32"
    paths = ntpath if win else posixpath
    override = env.get("GOOSE_PATH_ROOT", "")
    if override and paths.isabs(override):
        return [paths.join(override, "data", "sessions")]
    if win:
        # etcetera::Windows uses FOLDERID_RoamingAppData (APPDATA on normal profiles).
        base = env.get("APPDATA") or roaming or paths.join(home, "AppData", "Roaming")
        return [paths.join(base, "Block", "goose", "data", "sessions")]
    base = env.get("XDG_DATA_HOME", "")
    if not paths.isabs(base):
        base = paths.join(home, ".local", "share")
    return [paths.join(base, "goose", "sessions")]


def windows_roaming_dir():
    """Query the current user's Known Folder without reading a registry/profile file."""
    if os.name != "nt":
        return None
    import ctypes
    import uuid
    guid = ctypes.create_string_buffer(uuid.UUID("3eb685db-65f9-4cf6-a03a-e3ef65729f3d").bytes_le)
    result = ctypes.c_void_p()
    get_path = ctypes.windll.shell32.SHGetKnownFolderPath
    get_path.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    get_path.restype = ctypes.c_long
    free = ctypes.windll.ole32.CoTaskMemFree
    free.argtypes = [ctypes.c_void_p]
    free.restype = None
    try:
        if get_path(ctypes.byref(guid), 0, None, ctypes.byref(result)) == 0 and result.value:
            return ctypes.wstring_at(result.value)
        return None
    finally:
        if result.value:
            free(result)


def split_root(spec: str) -> tuple[str, Path]:
    """An explicit namespace permits replicas to share IDs, not independent installs."""
    namespace, sep, path = spec.partition("=")
    if not sep:
        path, namespace = spec, ""
    elif not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", namespace):
        raise ValueError("Goose source namespace must be a plain identifier")
    if not path or any(ord(ch) < 32 for ch in path) or ".." in path.replace("\\", "/").split("/"):
        raise ValueError("Goose root must be an absolute path without controls or traversal")
    if is_credential_file(path):
        raise ValueError("Goose source cannot be a credential path")
    root = Path(path).expanduser()
    if not root.is_absolute():
        raise ValueError("Goose root must be absolute")
    if not namespace:
        namespace = "path-" + hashlib.sha256(os.path.normcase(str((root / "sessions.db" if root.is_dir() else root).resolve())).encode()).hexdigest()[:24]
    return namespace, root


def _text(value, limit=256):
    return value if isinstance(value, str) and 0 < len(value) <= limit and not any(ord(c) < 32 for c in value) else None


def _count(value):
    if value is None:
        return None
    if type(value) is not int or not 0 <= value <= 2**63 - 1:
        raise ValueError("invalid_token_count")
    return value


def _cost(value):
    if value is None:
        return None
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("invalid_cost")
    return value


def _stamp(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode):
        raise SourceUnavailable("non_regular_source")
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _fingerprint(path, destination=None):
    digest = hashlib.sha256()
    # Opening the source with rb is deliberate: SQLite never opens the live path.
    with path.open("rb") as source:
        if destination is None:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        else:
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "wb") as target:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(block)
                    target.write(block)
    return digest.digest()


@contextmanager
def snapshot(db: Path):
    """Copy and verify a stable DB/WAL pair, then let SQLite read the private WAL.

    mode=ro on a live WAL database can create/alter source-side auxiliary files.
    We never use immutable=1 (which would hide committed WAL frames), copy SHM,
    checkpoint the source, or accept a hot rollback journal. If a writer prevents
    a stable capture, the source is a retryable coverage gap rather than a guess.
    """
    sources = [db, Path(str(db) + "-wal")]
    journal = Path(str(db) + "-journal")
    with tempfile.TemporaryDirectory(prefix="ai-ledger-goose-") as directory:
        target = Path(directory) / "sessions.db"
        copied = [target, Path(str(target) + "-wal")]
        for _ in range(3):
            before = [_stamp(p) for p in sources]
            journal_before = _stamp(journal)
            if before[0] is None:
                raise SourceUnavailable("missing_database")
            if journal_before and journal_before[2]:
                raise SourceUnavailable("rollback_journal_retry")
            hashes = []
            for source, dest, stamp in zip(sources, copied, before):
                if stamp is None:
                    dest.unlink(missing_ok=True)
                    hashes.append(None)
                else:
                    hashes.append(_fingerprint(source, dest))
            if before != [_stamp(p) for p in sources] or journal_before != _stamp(journal):
                continue
            verified = [_fingerprint(p) if stamp else None for p, stamp in zip(sources, before)]
            if hashes == verified and before == [_stamp(p) for p in sources] and journal_before == _stamp(journal):
                break
        else:
            raise SourceUnavailable("source_changed_retry")
        conn = sqlite3.connect(target.as_uri() + "?mode=ro", uri=True, timeout=0.2)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA query_only=ON")
            conn.execute("PRAGMA trusted_schema=OFF")
            conn.execute("BEGIN")
            yield conn
        finally:
            conn.close()


def _columns(conn, table):
    # table names are fixed here, not interpolated source metadata.
    return {r[1] for r in conn.execute('PRAGMA table_info("%s")' % table)}


def _signature(row):
    return (row["session_id"], row["model"], *(row[k] for k in TOKEN_COLUMNS), row["cost"], row["cost_source"])


def _provider_evidence(conn, tables, rows):
    """Correlation is labelled inferred, NEVER a native provider/request join.

    Only unique one-to-one equal-usage/equal-model pairs qualify. Repeated calls,
    missing usage, imported copies, compaction and ambiguous providers stay unknown.
    Session.provider_name is the latest selection and is intentionally not read.
    """
    if "messages" not in tables or not {"session_id", "message_id", "role", "metadata_json"} <= _columns(conn, "messages"):
        return {}
    paths = ["inference.provider", "inference.resolvedModel", "inference.requestedModel", *["usage." + t for t in CAMEL_TOKENS], "usage.cost", "usage.costSource"]
    extracts = ["json_extract(CASE WHEN json_valid(metadata_json) THEN metadata_json ELSE '{}' END, '$.%s')" % p for p in paths]
    matches = defaultdict(list)
    for record in conn.execute("SELECT session_id, message_id, " + ", ".join(extracts) + " FROM messages WHERE role='assistant'"):
        sid, mid, provider, resolved, requested, *usage = record
        if not (_text(mid) and _text(provider) and _text(resolved or requested)):
            continue
        signature = (sid, resolved or requested, *usage)
        try:
            hash(signature)
        except TypeError:
            continue
        matches[signature].append((provider, mid))
    counts = Counter(_signature(r) for r in rows if not r["is_compaction"] and r["cost_source"] != "carried_forward")
    return {key: value[0][0] for key, value in matches.items() if len(value) == counts.get(key) == 1}


def _session_counters(conn, namespace, columns):
    selected = ["id"] + ["accumulated_" + k for k in TOKEN_COLUMNS if "accumulated_" + k in columns]
    if "accumulated_cost" in columns:
        selected.append("accumulated_cost")
    result = []
    for row in conn.execute("SELECT " + ", ".join(selected) + " FROM sessions"):
        sid = _text(row["id"])
        if not sid:
            continue
        counters = {}
        for key in selected[1:]:
            try:
                counters[key] = _cost(row[key]) if key.endswith("cost") else _count(row[key])
            except ValueError:
                counters[key] = None
        result.append({"source_namespace": namespace, "session": sid, "evidence_class": "B", "counters": counters})
    return result


def _excluded(row, reason):
    tokens = {}
    for key in TOKEN_COLUMNS:
        try:
            tokens[key] = _count(row[key])
        except ValueError:
            tokens[key] = None
    try:
        cost = _cost(row["cost"])
    except ValueError:
        cost = None
    return {"usage_id": row["id"] if type(row["id"]) is int else None,
            "session": _text(row["session_id"]), "model": _text(row["model"]),
            "native_tokens": tokens, "native_cost": {"amount": cost, "currency": None, "source": _text(row["cost_source"])},
            "reason": reason, "billable": False}


def _read_database(db, namespace, host):
    with snapshot(db) as conn:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "sessions" not in tables or "id" not in _columns(conn, "sessions"):
            raise SourceUnavailable("not_goose_schema")
        counters = _session_counters(conn, namespace, _columns(conn, "sessions"))
        version = None
        if "schema_version" in tables and "version" in _columns(conn, "schema_version"):
            version = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
            if type(version) is not int:
                version = None
        if version != SCHEMA_VERSION or "usage_ledger" not in tables or not set(USAGE_COLUMNS) <= _columns(conn, "usage_ledger"):
            return [], counters, {"status": "unsupported_schema", "schema_version": version, "not_billable": True}
        rows = [dict(row) for row in conn.execute("SELECT " + ", ".join(USAGE_COLUMNS) + " FROM usage_ledger ORDER BY id")]
        provider_status = "available"
        try:
            providers = _provider_evidence(conn, tables, rows)
        except sqlite3.OperationalError as ex:
            # JSON1 is optional in older SQLite builds. Never read full message
            # metadata as a fallback or discard usage for missing inference.
            if not re.fullmatch(r"no such function: json_(valid|extract)", str(ex)):
                raise
            providers = {}
            provider_status = "sqlite_json_functions_unavailable"
        created = {}
        if "created_at" in _columns(conn, "sessions"):
            created = {r[0]: r[1] for r in conn.execute("SELECT id, created_at FROM sessions")}
        events, excluded, excluded_usage = [], Counter(), []
        totals = defaultdict(lambda: {key: 0 for key in TOKEN_COLUMNS})
        for row in rows:
            if row["cost_source"] == "carried_forward":
                excluded["carried_forward"] += 1
                excluded_usage.append(_excluded(row, "carried_forward"))
                continue
            try:
                sid, model = _text(row["session_id"]), _text(row["model"])
                if not sid or not model or type(row["id"]) is not int or row["id"] < 1:
                    raise ValueError("missing_identity_or_model")
                tokens = {key: _count(row[key]) for key in TOKEN_COLUMNS}
                cost = _cost(row["cost"])
                if tokens["input_tokens"] is None or tokens["output_tokens"] is None:
                    raise ValueError("missing_input_or_output")
                if type(row["created_timestamp"]) is not int:
                    raise ValueError("invalid_timestamp")
                ts = datetime.fromtimestamp(row["created_timestamp"], timezone.utc).isoformat()
                cr, cw = tokens["cache_read_tokens"] or 0, tokens["cache_write_tokens"] or 0
                uncached = tokens["input_tokens"] - cr - cw
                total = tokens["input_tokens"] + tokens["output_tokens"]
                if uncached < 0 or tokens["total_tokens"] not in (None, total):
                    raise ValueError("inconsistent_token_categories")
                if row["cost_source"] not in (None, "provider_reported", "estimated"):
                    raise ValueError("unknown_cost_source")
                if row["is_compaction"] not in (0, 1):
                    raise ValueError("invalid_compaction_flag")
            except (ValueError, OverflowError, OSError) as ex:
                reason = str(ex) if isinstance(ex, ValueError) and re.fullmatch("[a-z_]+", str(ex)) else "invalid_timestamp"
                excluded[reason] += 1
                excluded_usage.append(_excluded(row, reason))
                continue
            identity = [namespace, sid, created.get(sid), row["id"], row["created_timestamp"]]
            request_id = "goose:usage:" + hashlib.sha256(json.dumps(identity, separators=(",", ":")).encode()).hexdigest()
            provider = providers.get(_signature(row)) if not row["is_compaction"] else None
            events.append({
                "tool": "goose", "host": host, "ts": ts, "date": ts[:10], "session": namespace + ":" + sid, "model": model,
                "input_uncached": uncached, "cache_read": cr, "cache_write": cw,
                "output": tokens["output_tokens"], "reasoning": 0, "total": total,
                "request_id": request_id, "provider": provider,
                "kind": "compaction" if row["is_compaction"] else "main", "entrypoint": "goose",
                "granularity": "native_usage_record", "src": None,
                "evidence_class": "A", "token_source": "goose_recorded", "token_confidence": "native_record_not_independently_provider_verified",
                "provider_confidence": "inferred_unique_message_usage" if provider else "unavailable",
                "goose": {"schema_version": version, "source_namespace": namespace, "usage_id": row["id"], "native_session_id": sid,
                          "provider_request_id": None, "native_tokens": {**tokens, "reasoning_tokens": None},
                          "native_cost": {"amount": cost, "currency": None, "source": row["cost_source"]},
                          "pricing_basis": "ledger_snapshot_estimate", "cache_write_ttl": None},
            })
            for key, value in tokens.items():
                totals[sid][key] += value or 0
        for counter in counters:
            counter["collected_native_tokens"] = totals.get(counter["session"], {key: 0 for key in TOKEN_COLUMNS})
        return events, counters, {"status": "ok", "schema_version": version, "native_rows": len(rows), "excluded_rows": dict(excluded), "excluded_usage": excluded_usage,
                                 "provider_unknown_events": sum(e["provider"] is None for e in events), "provider_inference_status": provider_status}


def is_goose_session(node):
    """Recognize native exports/legacy headers before the generic usage sniffer."""
    return isinstance(node, dict) and "id" in node and "created_at" in node and "extension_data" in node and (
        "accumulated_usage" in node or "accumulated_total_tokens" in node or "message_count" in node)


def _legacy_header(path):
    # Legacy JSONL header only; no prompts/completions or recursive directories.
    with path.open("rb") as fh:
        raw = fh.readline(MAX_HEADER + 1)
    if len(raw) > MAX_HEADER:
        raise SourceUnavailable("legacy_header_incomplete_or_large")
    node = json.loads(raw)
    if not is_goose_session(node):
        raise SourceUnavailable("unrecognized_legacy_header")
    nested = node.get("accumulated_usage") or {}
    if not isinstance(nested, dict):
        raise SourceUnavailable("invalid_legacy_usage")
    counts = {}
    for key in TOKEN_COLUMNS:
        native = key.replace("cache_read_tokens", "cache_read_input_tokens").replace("cache_write_tokens", "cache_write_input_tokens")
        counts["accumulated_" + key] = _count(nested.get(native, node.get("accumulated_" + key)))
    return {"session": _text(node["id"]) or path.stem, "evidence_class": "B", "counters": counts, "status": "legacy_totals_only"}


def collect(spec: str, host: str):
    """Return normalized events and latest coverage; never initialize a ledger."""
    namespace, root = split_root(spec)
    coverage = {"tool": "goose", "host": host, "root": str(root), "source_namespace": namespace,
                "events": 0, "files": 0, "bytes": 0, "errors": 0, "sessions": [], "legacy": []}
    events = []
    try:
        if root.is_dir():
            db = root / "sessions.db"
            legacy = [p for p in root.iterdir() if p.suffix.lower() == ".jsonl" and not is_credential_file(str(p))]
            if not db.exists() and legacy:
                db = None
        elif root.suffix.lower() == ".jsonl":
            db, legacy = None, [root]
        elif root.suffix.lower() == ".json":
            coverage["status"] = "export_not_billable_use_native_database"
            return events, coverage
        else:
            db, legacy = root, []
        if db is not None:
            # Report the observed source footprint, including active WAL data,
            # not SQLite's private SHM and not the number of copy/hash reads.
            for source in (db, Path(str(db) + "-wal")):
                stamp = _stamp(source)
                if stamp is not None:
                    coverage["files"] += 1
                    coverage["bytes"] += stamp[2]
            events, coverage["sessions"], details = _read_database(db, namespace, host)
            coverage.update(details)
        else:
            coverage["status"] = "legacy_totals_only"
        native_sessions = {r["session"] for r in coverage["sessions"]}
        for path in legacy:
            try:
                stamp = _stamp(path)
                info = _legacy_header(path)
                if info["session"] not in native_sessions:
                    coverage["legacy"].append(info)
                coverage["files"] += 1
                coverage["bytes"] += stamp[2] if stamp else 0
            except (OSError, ValueError, RecursionError):
                coverage["errors"] += 1
        coverage["events"] = len(events)
    except SourceUnavailable as ex:
        coverage.update(status=str(ex), errors=1)
    except (OSError, sqlite3.Error, ValueError, TypeError, RecursionError):
        coverage.update(status="unreadable_or_corrupt_source", errors=1)
    return events, coverage
