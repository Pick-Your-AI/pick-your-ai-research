#!/usr/bin/env python3
"""
ledger_store.py - append-only, de-duplicated persistence for the usage ledger.

Three interchangeable backends, chosen once at onboarding and remembered:

  sqlite  one file, tables events / sessions / prompts / prefs / runs, primary keys enforce uniqueness
  json    one directory of JSONL files plus an id index; human-readable, git-friendly
  csv     one directory of CSV files plus an id index; spreadsheet-friendly

Every event gets a stable id derived from its source (tool, host, session, source file, ordinal
within that file, timestamp and token counts). Agent logs are append-only, so re-scanning a host
re-derives the same ids and `ingest` simply skips what is already stored. Nothing is ever updated
or deleted by the store; `reinit` in the CLI starts a fresh store rather than editing one.

Standard library only.
"""
import csv
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safety  # noqa: E402

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

EVENT_COLUMNS = ["id", "seq", "tool", "host", "ts", "date", "session", "model", "input_uncached", "cache_read", "cache_write",
                 "cache_write_5m", "cache_write_1h", "output", "reasoning", "total", "cwd", "kind", "plan", "entrypoint",
                 "version", "effort", "request_id", "cost_usd", "src", "ingested_at"]
SESSION_COLUMNS = ["id", "tool", "host", "session", "file", "kind", "first_ts", "last_ts", "model", "cwd", "calls", "user_msgs",
                   "tool_calls", "bytes", "ingested_at"]
PROMPT_COLUMNS = ["id", "tool", "host", "ts", "session", "cwd", "text", "ingested_at"]


def _sha(*parts):
    return hashlib.sha1("|".join("" if p is None else str(p) for p in parts).encode("utf-8")).hexdigest()


def event_key(e):
    """The natural key of one call: where it was logged and what it counted."""
    return (e.get("tool"), e.get("host"), e.get("session"), os.path.basename(str(e.get("src") or "")), e.get("ts"),
            e.get("model"), e.get("input_uncached"), e.get("cache_read"), e.get("cache_write"), e.get("output"))


def event_id(e, seq):
    """Stable id: the tool's request id when it has one, else the natural key plus an ordinal among
    identical keys in the same source file. Logs are append-only, so re-scanning yields the same ids."""
    if e.get("request_id"):
        return _sha("req", e.get("tool"), e.get("host"), e.get("request_id"))
    return _sha(*(event_key(e) + (seq,)))


def session_id(s):
    return _sha("sess", s.get("tool"), s.get("host"), s.get("session"), os.path.basename(str(s.get("file") or "")))


def prompt_id(p):
    return _sha("prompt", p.get("tool"), p.get("host"), p.get("ts"), p.get("session"), (p.get("text") or "")[:500])


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    """Facade over the three backends. Use Store.open(kind, path)."""

    @staticmethod
    def open(kind, path):
        kind = (kind or "sqlite").lower()
        if kind == "sqlite":
            return SqliteStore(path)
        if kind == "json":
            return FileStore(path, "json")
        if kind == "csv":
            return FileStore(path, "csv")
        raise ValueError("unknown store kind %r (use sqlite, json or csv)" % kind)

    # ---- shared ingest logic -------------------------------------------------
    def ingest_events_file(self, path):
        """Append events from a scanner events.*.jsonl. Returns (added, skipped)."""
        added = skipped = 0
        seq_by_key = {}
        batch = []
        with open(path, "rb") as fh:
            for raw in fh:
                try:
                    e = json.loads(raw)
                except Exception:
                    continue
                key = event_key(e)
                seq = seq_by_key.get(key, 0)
                seq_by_key[key] = seq + 1
                e["seq"] = seq
                e["id"] = event_id(e, seq)
                batch.append(e)
                if len(batch) >= 5000:
                    a, s = self._put_events(batch)
                    added += a
                    skipped += s
                    batch = []
        if batch:
            a, s = self._put_events(batch)
            added += a
            skipped += s
        return added, skipped

    def ingest_sessions_file(self, path):
        rows = []
        with open(path, "rb") as fh:
            for raw in fh:
                try:
                    s = json.loads(raw)
                except Exception:
                    continue
                s["id"] = session_id(s)
                rows.append(s)
        return self._put_sessions(rows)

    def ingest_prompts_file(self, path):
        rows = []
        with open(path, "rb") as fh:
            for raw in fh:
                try:
                    p = json.loads(raw)
                except Exception:
                    continue
                p["id"] = prompt_id(p)
                rows.append(p)
        return self._put_prompts(rows)

    def record_run(self, meta):
        meta = dict(meta)
        meta.setdefault("id", _sha("run", time.time(), os.getpid()))
        meta.setdefault("finished_at", now())
        self._put_run(meta)
        return meta["id"]


# ----------------------------------------------------------------------------
# SQLite backend
# ----------------------------------------------------------------------------

class SqliteStore(Store):
    kind = "sqlite"

    def __init__(self, path):
        self.path = path
        safety.private_dir(os.path.dirname(os.path.abspath(path)) or ".")
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        for suffix in ("", "-wal", "-shm", "-journal"):
            safety.private_file(path + suffix)
        c = self.db
        # columns are declared without a type so integers and floats keep their type (SQLite dynamic typing)
        c.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, %s, extra TEXT)" % ", ".join(EVENT_COLUMNS[1:]))
        c.execute("CREATE INDEX IF NOT EXISTS events_ts ON events(ts)")
        c.execute("CREATE INDEX IF NOT EXISTS events_tool_host ON events(tool, host)")
        c.execute("CREATE INDEX IF NOT EXISTS events_session ON events(session)")
        c.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, %s, extra TEXT)" % ", ".join(SESSION_COLUMNS[1:]))
        c.execute("CREATE TABLE IF NOT EXISTS prompts (id TEXT PRIMARY KEY, %s)" % ", ".join(PROMPT_COLUMNS[1:]))
        c.execute("CREATE TABLE IF NOT EXISTS prefs (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, started_at TEXT, finished_at TEXT, meta TEXT)")
        c.commit()

    def ingest_verified_events(self, events, fingerprint_field="evidence_sha256"):
        """Atomically append validated request-ID events, refusing conflicting evidence.

        Additive API for live collectors. Existing file ingestion is unchanged. The
        caller supplies a SHA-256 fingerprint of charge-relevant evidence; changing
        counts under an existing native request ID is an error, never a silent skip.
        SQLite serializes competing writers. Nothing already stored is updated.
        """
        batch = []
        for event in events:
            event = dict(event)
            fingerprint = event.get(fingerprint_field)
            if not event.get("request_id") or not isinstance(fingerprint, str) or len(fingerprint) != 64:
                raise ValueError("verified ingestion requires request identity and evidence fingerprint")
            if any(c not in "0123456789abcdef" for c in fingerprint):
                raise ValueError("invalid evidence fingerprint")
            event["seq"] = 0
            event["id"] = event_id(event, 0)
            batch.append(event)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            seen = {}
            for event in batch:
                identity = event["id"]
                fingerprint = event[fingerprint_field]
                prior = seen.get(identity)
                if prior is None:
                    row = self.db.execute("SELECT extra FROM events WHERE id=?", (identity,)).fetchone()
                    if row is not None:
                        prior = (json.loads(row[0]) if row[0] else {}).get(fingerprint_field, "unknown")
                if prior is not None and prior != fingerprint:
                    raise ValueError("conflicting evidence for an existing invocation; no events imported")
                seen[identity] = fingerprint
            # _put_events uses the same connection/transaction and commits this batch.
            return self._put_events(batch)
        except BaseException:
            self.db.rollback()
            raise

    def _put_events(self, batch):
        ts = now()
        rows = []
        for e in batch:
            known = {k: e.get(k) for k in EVENT_COLUMNS}
            known["ingested_at"] = ts
            extra = {k: v for k, v in e.items() if k not in EVENT_COLUMNS}
            rows.append([known[k] for k in EVENT_COLUMNS] + [json.dumps(extra) if extra else None])
        before = self.db.total_changes
        self.db.executemany("INSERT OR IGNORE INTO events (%s, extra) VALUES (%s)" % (", ".join(EVENT_COLUMNS), ", ".join("?" * (len(EVENT_COLUMNS) + 1))), rows)
        self.db.commit()
        added = self.db.total_changes - before
        return added, len(rows) - added

    def _put_sessions(self, rows):
        ts = now()
        out = []
        for s in rows:
            known = {k: s.get(k) for k in SESSION_COLUMNS}
            known["ingested_at"] = ts
            extra = {k: v for k, v in s.items() if k not in SESSION_COLUMNS}
            out.append([known[k] for k in SESSION_COLUMNS] + [json.dumps(extra) if extra else None])
        before = self.db.total_changes
        self.db.executemany("INSERT OR IGNORE INTO sessions (%s, extra) VALUES (%s)" % (", ".join(SESSION_COLUMNS), ", ".join("?" * (len(SESSION_COLUMNS) + 1))), out)
        self.db.commit()
        added = self.db.total_changes - before
        return added, len(out) - added

    def _put_prompts(self, rows):
        ts = now()
        out = [[p.get(k) if k != "ingested_at" else ts for k in PROMPT_COLUMNS] for p in rows]
        before = self.db.total_changes
        self.db.executemany("INSERT OR IGNORE INTO prompts (%s) VALUES (%s)" % (", ".join(PROMPT_COLUMNS), ", ".join("?" * len(PROMPT_COLUMNS))), out)
        self.db.commit()
        added = self.db.total_changes - before
        return added, len(out) - added

    def _put_run(self, meta):
        self.db.execute("INSERT OR REPLACE INTO runs (id, started_at, finished_at, meta) VALUES (?,?,?,?)", (meta["id"], meta.get("started_at"), meta.get("finished_at"), json.dumps(meta)))
        self.db.commit()

    def set_pref(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO prefs (key, value, updated_at) VALUES (?,?,?)", (key, json.dumps(value), now()))
        self.db.commit()

    def get_pref(self, key, default=None):
        row = self.db.execute("SELECT value FROM prefs WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def all_prefs(self):
        return {k: json.loads(v) for k, v in self.db.execute("SELECT key, value FROM prefs")}

    def counts(self):
        return {t: self.db.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0] for t in ("events", "sessions", "prompts", "runs")}

    def last_run(self):
        row = self.db.execute("SELECT meta FROM runs ORDER BY finished_at DESC LIMIT 1").fetchone()
        return json.loads(row[0]) if row else None

    def iter_events(self):
        cur = self.db.execute("SELECT %s, extra FROM events ORDER BY ts" % ", ".join(EVENT_COLUMNS))
        for row in cur:
            e = dict(zip(EVENT_COLUMNS, row[:-1]))
            if row[-1]:
                e.update(json.loads(row[-1]))
            for k in ("seq", "input_uncached", "cache_read", "cache_write", "cache_write_5m", "cache_write_1h", "output", "reasoning", "total"):
                if e.get(k) not in (None, ""):
                    try:
                        e[k] = int(float(e[k]))
                    except (TypeError, ValueError):
                        pass
            yield e

    def iter_table(self, table):
        cols = {"sessions": SESSION_COLUMNS, "prompts": PROMPT_COLUMNS}[table]
        has_extra = table == "sessions"
        cur = self.db.execute("SELECT %s%s FROM %s" % (", ".join(cols), ", extra" if has_extra else "", table))
        for row in cur:
            d = dict(zip(cols, row[:len(cols)]))
            if has_extra and row[-1]:
                d.update(json.loads(row[-1]))
            yield d

    def close(self):
        self.db.close()


# ----------------------------------------------------------------------------
# JSON / CSV file backends (directory + id index)
# ----------------------------------------------------------------------------

class FileStore(Store):
    def __init__(self, path, fmt):
        self.kind = fmt
        self.path = path
        safety.private_dir(path)
        self.ext = "jsonl" if fmt == "json" else "csv"
        self.ids = {t: self._load_ids(t) for t in ("events", "sessions", "prompts")}

    def _file(self, table):
        return os.path.join(self.path, "%s.%s" % (table, self.ext))

    def _idx(self, table):
        return os.path.join(self.path, "%s.ids" % table)

    def _load_ids(self, table):
        p = self._idx(table)
        if not os.path.isfile(p):
            return set()
        with open(p, encoding="utf-8") as fh:
            return {line.strip() for line in fh if line.strip()}

    def _append(self, table, columns, rows):
        """rows: list of dicts with 'id'. Append the new ones; return (added, skipped)."""
        new = [r for r in rows if r["id"] not in self.ids[table]]
        if not new:
            return 0, len(rows)
        seen = set()
        uniq = []
        for r in new:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            uniq.append(r)
        path = self._file(table)
        exists = os.path.isfile(path) and os.path.getsize(path) > 0
        with open(path, "a", encoding="utf-8", newline="") as fh:
            if self.ext == "jsonl":
                for r in uniq:
                    fh.write(json.dumps(r) + "\n")
            else:
                w = csv.DictWriter(fh, fieldnames=columns + ["extra"], extrasaction="ignore")
                if not exists:
                    w.writeheader()
                for r in uniq:
                    row = {k: r.get(k) for k in columns}
                    extra = {k: v for k, v in r.items() if k not in columns}
                    row["extra"] = json.dumps(extra) if extra else ""
                    w.writerow(row)
        with open(self._idx(table), "a", encoding="utf-8") as fh:
            for r in uniq:
                fh.write(r["id"] + "\n")
        safety.private_file(path)
        safety.private_file(self._idx(table))
        self.ids[table].update(r["id"] for r in uniq)
        return len(uniq), len(rows) - len(uniq)

    def _put_events(self, batch):
        ts = now()
        for e in batch:
            e["ingested_at"] = ts
        return self._append("events", EVENT_COLUMNS, batch)

    def _put_sessions(self, rows):
        ts = now()
        for s in rows:
            s["ingested_at"] = ts
        return self._append("sessions", SESSION_COLUMNS, rows)

    def _put_prompts(self, rows):
        ts = now()
        for p in rows:
            p["ingested_at"] = ts
        return self._append("prompts", PROMPT_COLUMNS, rows)

    def _put_run(self, meta):
        with open(os.path.join(self.path, "runs.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(meta) + "\n")
        safety.private_file(os.path.join(self.path, "runs.jsonl"))

    def _prefs_path(self):
        return os.path.join(self.path, "prefs.json")

    def all_prefs(self):
        p = self._prefs_path()
        if not os.path.isfile(p):
            return {}
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)

    def set_pref(self, key, value):
        prefs = self.all_prefs()
        prefs[key] = value
        safety.write_private(self._prefs_path(), json.dumps(prefs, indent=2))

    def get_pref(self, key, default=None):
        return self.all_prefs().get(key, default)

    def counts(self):
        out = {t: len(self.ids[t]) for t in ("events", "sessions", "prompts")}
        rp = os.path.join(self.path, "runs.jsonl")
        out["runs"] = sum(1 for _ in open(rp, encoding="utf-8")) if os.path.isfile(rp) else 0
        return out

    def last_run(self):
        rp = os.path.join(self.path, "runs.jsonl")
        if not os.path.isfile(rp):
            return None
        last = None
        with open(rp, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    last = json.loads(line)
        return last

    def _iter(self, table, columns):
        path = self._file(table)
        if not os.path.isfile(path):
            return
        if self.ext == "jsonl":
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        yield json.loads(line)
        else:
            with open(path, encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    d = {k: (row.get(k) if row.get(k) != "" else None) for k in columns}
                    if row.get("extra"):
                        d.update(json.loads(row["extra"]))
                    for k in ("seq", "input_uncached", "cache_read", "cache_write", "cache_write_5m", "cache_write_1h", "output", "reasoning", "total", "calls", "user_msgs", "tool_calls", "bytes"):
                        if d.get(k) not in (None, ""):
                            try:
                                d[k] = int(float(d[k]))
                            except (TypeError, ValueError):
                                pass
                    yield d

    def iter_events(self):
        return sorted(self._iter("events", EVENT_COLUMNS), key=lambda e: e.get("ts") or "")

    def iter_table(self, table):
        return self._iter(table, {"sessions": SESSION_COLUMNS, "prompts": PROMPT_COLUMNS}[table])

    def close(self):
        pass


# ----------------------------------------------------------------------------
# export helpers (the report step reads JSONL, so every backend can feed it)
# ----------------------------------------------------------------------------

def export_jsonl(store, out_dir, host_label="store"):
    """Materialise the whole store as scanner-shaped JSONL files for compile_ai_logs.py report."""
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for table, fn, it in (("events", "events.%s.jsonl", store.iter_events), ("sessions", "sessions.%s.jsonl", lambda: store.iter_table("sessions")),
                          ("prompts", "prompts.%s.jsonl", lambda: store.iter_table("prompts"))):
        p = os.path.join(out_dir, fn % host_label)
        n = 0
        with open(p, "w", encoding="utf-8") as fh:
            for row in it():
                fh.write(json.dumps(row) + "\n")
                n += 1
        paths[table] = (p, n)
    return paths


def export_table(store, table, fmt, out_path):
    """Dump one table as json (array), jsonl or csv."""
    it = store.iter_events() if table == "events" else store.iter_table(table)
    return export_rows(it, table, fmt, out_path)


def export_rows(it, table, fmt, out_path):
    cols = {"events": EVENT_COLUMNS, "sessions": SESSION_COLUMNS, "prompts": PROMPT_COLUMNS}[table]
    n = 0
    if fmt == "csv":
        with open(out_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for row in it:
                w.writerow(row)
                n += 1
    elif fmt == "jsonl":
        with open(out_path, "w", encoding="utf-8") as fh:
            for row in it:
                fh.write(json.dumps(row) + "\n")
                n += 1
    else:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write("[\n")
            first = True
            for row in it:
                fh.write(("" if first else ",\n") + json.dumps(row))
                first = False
                n += 1
            fh.write("\n]\n")
    return n


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kind", default="sqlite", choices=["sqlite", "json", "csv"])
    ap.add_argument("--path", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ingest", help="append scanner outputs (events/sessions/prompts jsonl) into the store")
    s.add_argument("files", nargs="+")
    sub.add_parser("counts")
    e = sub.add_parser("export")
    e.add_argument("--table", default="events", choices=["events", "sessions", "prompts"])
    e.add_argument("--format", default="csv", choices=["csv", "json", "jsonl"])
    e.add_argument("--out", required=True)
    a = ap.parse_args()
    st = Store.open(a.kind, a.path)
    if a.cmd == "ingest":
        for f in a.files:
            base = os.path.basename(f)
            if base.startswith("events."):
                print(f, "events added/skipped:", st.ingest_events_file(f))
            elif base.startswith("sessions."):
                print(f, "sessions added/skipped:", st.ingest_sessions_file(f))
            elif base.startswith("prompts."):
                print(f, "prompts added/skipped:", st.ingest_prompts_file(f))
    elif a.cmd == "counts":
        print(json.dumps(st.counts()))
    elif a.cmd == "export":
        print("rows:", export_table(st, a.table, a.format, a.out))
    st.close()
