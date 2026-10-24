#!/usr/bin/env python3
"""
ledger_query.py - answer specific questions from the accumulated store (and the raw-log archive).

    python3 ledger_query.py --presets                        # what can be asked
    python3 ledger_query.py totals --since 2026-08-01
    python3 ledger_query.py by-day --tool codex --since 2026-08-01 --until 2026-08-31
    python3 ledger_query.py by-project --account codex:a3523532 --limit 10 --format csv
    python3 ledger_query.py sessions --project libreevolve --limit 20
    python3 ledger_query.py session --session <id>          # every call and prompt of one session
    python3 ledger_query.py prompts --grep "rate limit" --since 2026-07-01
    python3 ledger_query.py sql "SELECT model, SUM(total) t FROM events GROUP BY 1 ORDER BY t DESC"
    python3 ledger_query.py logs "ECONNRESET" --since 2026-08-01   # inside the archived raw logs

Filters (all optional, combinable): --since/--until (dates, inclusive), --tool, --host, --account, --model,
--project (substring of the working directory), --session, --kind, --plan, --billing. Output: table (default),
csv, json, jsonl. The store is opened through the ledger config unless --store-kind/--store-path are given;
JSON and CSV stores are loaded into an in-memory SQLite database so every preset and free SQL works the same.

Standard library only.
"""
import argparse
import csv
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ledger_store  # noqa: E402
import safety  # noqa: E402

NUM = ("input_uncached", "cache_read", "cache_write", "cache_write_5m", "cache_write_1h", "output", "reasoning", "total")
SUMS = "COUNT(*) AS calls, SUM(input_uncached) AS input_uncached, SUM(cache_read) AS cache_read, SUM(cache_write) AS cache_write, SUM(output) AS output, SUM(reasoning) AS reasoning, SUM(total) AS total, COUNT(DISTINCT session) AS sessions, ROUND(SUM(COALESCE(cost_usd,0)),4) AS logged_cost_usd"

PRESETS = {
    "totals": ("Totals for the filtered calls", "SELECT MIN(date) AS first_day, MAX(date) AS last_day, COUNT(DISTINCT date) AS active_days, %s FROM events WHERE {where}" % SUMS),
    "by-day": ("Per calendar day", "SELECT date, %s FROM events WHERE {where} GROUP BY date ORDER BY date" % SUMS),
    "by-week": ("Per ISO week", "SELECT strftime('%%Y-W%%W', date) AS week, MIN(date) AS from_day, %s FROM events WHERE {where} GROUP BY week ORDER BY week" % SUMS),
    "by-month": ("Per month", "SELECT substr(date,1,7) AS month, %s FROM events WHERE {where} GROUP BY month ORDER BY month" % SUMS),
    "by-tool": ("Per tool", "SELECT tool, %s FROM events WHERE {where} GROUP BY tool ORDER BY total DESC" % SUMS),
    "by-host": ("Per host and tool", "SELECT host, tool, %s FROM events WHERE {where} GROUP BY host, tool ORDER BY total DESC" % SUMS),
    "by-model": ("Per model", "SELECT tool, model, %s FROM events WHERE {where} GROUP BY tool, model ORDER BY total DESC" % SUMS),
    "by-model-month": ("Model adoption over time", "SELECT substr(date,1,7) AS month, model, %s FROM events WHERE {where} GROUP BY month, model ORDER BY month, total DESC" % SUMS),
    "by-project": ("Per working directory", "SELECT cwd, tool, %s FROM events WHERE {where} GROUP BY cwd, tool ORDER BY total DESC" % SUMS),
    "by-account": ("Per account, applying the accounts.json rules", "SELECT acct(tool,host,plan,cwd,date) AS account, bill(tool,host,plan,cwd,date) AS billing, %s FROM events WHERE {where} GROUP BY 1, 2 ORDER BY total DESC" % SUMS),
    "by-account-month": ("Per account and month", "SELECT substr(date,1,7) AS month, acct(tool,host,plan,cwd,date) AS account, %s FROM events WHERE {where} GROUP BY 1, 2 ORDER BY month, total DESC" % SUMS),
    "by-plan": ("Per plan type stamped on the call", "SELECT tool, COALESCE(plan,'?') AS plan, %s FROM events WHERE {where} GROUP BY tool, plan ORDER BY total DESC" % SUMS),
    "by-kind": ("Main threads vs sub-agents", "SELECT tool, COALESCE(kind,'?') AS kind, %s FROM events WHERE {where} GROUP BY tool, kind ORDER BY total DESC" % SUMS),
    "by-entrypoint": ("CLI, IDE, desktop, SDK ...", "SELECT tool, COALESCE(entrypoint,'?') AS entrypoint, %s FROM events WHERE {where} GROUP BY tool, entrypoint ORDER BY total DESC" % SUMS),
    "by-hour": ("Calls by local hour of day (UTC unless the store carries local time)", "SELECT substr(ts,12,2) AS hour, %s FROM events WHERE {where} GROUP BY hour ORDER BY hour" % SUMS),
    "by-weekday": ("Calls by weekday (0=Sunday)", "SELECT strftime('%%w', date) AS weekday, %s FROM events WHERE {where} GROUP BY weekday ORDER BY weekday" % SUMS),
    "by-effort": ("Reasoning effort settings", "SELECT tool, COALESCE(effort,'?') AS effort, %s FROM events WHERE {where} GROUP BY tool, effort ORDER BY total DESC" % SUMS),
    "by-version": ("Client versions", "SELECT tool, COALESCE(version,'?') AS version, MIN(date) AS first_seen, MAX(date) AS last_seen, %s FROM events WHERE {where} GROUP BY tool, version ORDER BY tool, first_seen" % SUMS),
    "sessions": ("Largest sessions", "SELECT session, tool, host, MIN(ts) AS started, MAX(ts) AS ended, cwd, %s FROM events WHERE {where} GROUP BY session, tool, host ORDER BY total DESC" % SUMS),
    "session": ("Every call of one session (use --session)", "SELECT ts, tool, host, model, kind, input_uncached, cache_read, cache_write, output, reasoning, total, plan, cwd FROM events WHERE {where} ORDER BY ts"),
    "calls": ("Raw calls (use filters and --limit)", "SELECT ts, tool, host, session, model, kind, input_uncached, cache_read, cache_write, output, reasoning, total, plan, cwd FROM events WHERE {where} ORDER BY ts"),
    "biggest-calls": ("Largest single calls", "SELECT ts, tool, host, session, model, input_uncached, cache_read, output, total, cwd FROM events WHERE {where} ORDER BY total DESC"),
    "cache": ("Cache behaviour per tool", "SELECT tool, ROUND(1.0*SUM(cache_read)/NULLIF(SUM(input_uncached+cache_read+cache_write),0),3) AS cache_read_share, ROUND(1.0*SUM(input_uncached+cache_read+cache_write)/NULLIF(SUM(output),0),1) AS prompt_per_output, %s FROM events WHERE {where} GROUP BY tool ORDER BY total DESC" % SUMS),
    "first-last": ("First and last activity per tool and host", "SELECT tool, host, MIN(ts) AS first_call, MAX(ts) AS last_call, COUNT(*) AS calls FROM events WHERE {where} GROUP BY tool, host ORDER BY tool, host"),
    "prompts": ("User prompts (use --grep, filters, --limit)", "SELECT ts, tool, host, session, cwd, substr(text,1,300) AS text FROM prompts WHERE {pwhere} ORDER BY ts"),
    "prompt-count": ("Prompts per day", "SELECT substr(ts,1,10) AS date, tool, COUNT(*) AS prompts FROM prompts WHERE {pwhere} GROUP BY date, tool ORDER BY date"),
    "session-list": ("Session metadata rows (sessions table)", "SELECT tool, host, session, first_ts, last_ts, model, cwd, calls, user_msgs, tool_calls, bytes FROM sessions WHERE {swhere} ORDER BY first_ts"),
}


def attach_accounts(db, accounts_path):
    """acct()/bill() SQL functions applying the accounts.json rules, so per-account questions work on the raw store."""
    try:
        import compile_ai_logs
        AC = compile_ai_logs.load_accounts(accounts_path) if accounts_path else None
    except Exception:
        AC = None

    def acct(tool, host, plan, cwd, date):
        return compile_ai_logs.assign_account({"tool": tool, "host": host, "plan": plan, "cwd": cwd, "date": date}, AC)[0] if AC else None

    def bill(tool, host, plan, cwd, date):
        return compile_ai_logs.assign_account({"tool": tool, "host": host, "plan": plan, "cwd": cwd, "date": date}, AC)[1] if AC else None

    db.create_function("acct", 5, acct)
    db.create_function("bill", 5, bill)


def open_db(kind, path):
    """SQLite store: open directly (read-only). JSON/CSV: load into memory."""
    if kind == "sqlite":
        from urllib.parse import quote
        return sqlite3.connect("file:%s?mode=ro" % quote(path.replace("\\", "/"), safe="/:"), uri=True)
    st = ledger_store.Store.open(kind, path)
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE events (%s, extra TEXT)" % ", ".join(ledger_store.EVENT_COLUMNS))
    db.execute("CREATE TABLE sessions (%s, extra TEXT)" % ", ".join(ledger_store.SESSION_COLUMNS))
    db.execute("CREATE TABLE prompts (%s)" % ", ".join(ledger_store.PROMPT_COLUMNS))
    for table, cols, it in (("events", ledger_store.EVENT_COLUMNS, st.iter_events), ("sessions", ledger_store.SESSION_COLUMNS, lambda: st.iter_table("sessions")), ("prompts", ledger_store.PROMPT_COLUMNS, lambda: st.iter_table("prompts"))):
        rows = []
        for r in it():
            known = [r.get(c) for c in cols]
            if table != "prompts":
                known.append(json.dumps({k: v for k, v in r.items() if k not in cols}))
            rows.append(known)
        db.executemany("INSERT INTO %s VALUES (%s)" % (table, ",".join("?" * (len(cols) + (0 if table == "prompts" else 1)))), rows)
    db.commit()
    st.close()
    return db


def build_where(a, table="events"):
    w, args = [], []
    date_col = "date" if table == "events" else "substr(ts,1,10)" if table == "prompts" else "substr(first_ts,1,10)"
    if a.since:
        w.append("%s >= ?" % date_col)
        args.append(a.since)
    if a.until:
        w.append("%s <= ?" % date_col)
        args.append(a.until)
    for col in ("tool", "host", "session"):
        v = getattr(a, col, None)
        if v:
            w.append("%s = ?" % col)
            args.append(v)
    if table == "events":
        for col in ("model", "kind", "plan"):
            v = getattr(a, col, None)
            if v:
                w.append("%s = ?" % col)
                args.append(v)
        if a.account:
            w.append("acct(tool,host,plan,cwd,date) = ?")
            args.append(a.account)
        if a.billing:
            w.append("bill(tool,host,plan,cwd,date) = ?")
            args.append(a.billing)
    if a.project:
        w.append("LOWER(COALESCE(cwd,'')) LIKE ?")
        args.append("%" + a.project.lower() + "%")
    if table == "prompts" and getattr(a, "grep", None):
        w.append("LOWER(text) LIKE ?")
        args.append("%" + a.grep.lower() + "%")
    return (" AND ".join(w) if w else "1=1"), args


def run_query(db, sql, args, limit=None):
    if limit:
        sql = sql.rstrip().rstrip(";") + " LIMIT %d" % limit
    cur = db.execute(sql, args)
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()


def emit(cols, rows, fmt, out=sys.stdout):
    if fmt == "json":
        json.dump([dict(zip(cols, r)) for r in rows], out, indent=2, default=str)
        out.write("\n")
    elif fmt == "jsonl":
        for r in rows:
            out.write(json.dumps(dict(zip(cols, r)), default=str) + "\n")
    elif fmt == "csv":
        w = csv.writer(out)
        w.writerow(cols)
        w.writerows(rows)
    else:
        # table mode goes straight to a terminal: text cells (prompts, cwd, session, archive snippets) are data from the
        # tools' logs, so escape sequences and control characters are stripped and line breaks flattened to one line
        def cell(v):
            if v is None:
                return ""
            if isinstance(v, int) and not isinstance(v, bool) and abs(v) >= 10000:
                return "{:,}".format(v)
            if isinstance(v, str):
                return safety.clean_for_terminal(v, limit=400).replace("\n", " ").replace("\t", " ")
            return str(v)
        srow = [[cell(v) for v in r] for r in rows]
        widths = [max([len(c)] + [len(r[i]) for r in srow]) for i, c in enumerate(cols)]
        widths = [min(w, 60) for w in widths]
        line = "  ".join(c.ljust(widths[i])[:widths[i]] for i, c in enumerate(cols))
        out.write(line + "\n" + "-" * len(line) + "\n")
        for r in srow:
            out.write("  ".join((v[:widths[i]] if not v.replace(",", "").replace(".", "").replace("-", "").isdigit() else v.rjust(widths[i]))[:widths[i]].ljust(widths[i]) for i, v in enumerate(r)) + "\n")
        out.write("(%d rows)\n" % len(rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("preset", nargs="?", help="a preset name, 'sql', or 'logs'")
    ap.add_argument("arg", nargs="?", help="SQL text for 'sql'; pattern for 'logs'")
    ap.add_argument("--presets", action="store_true", help="list presets")
    ap.add_argument("--store-kind", choices=["sqlite", "json", "csv"])
    ap.add_argument("--store-path")
    ap.add_argument("--archive", help="archive directory for 'logs' (default from the ledger config)")
    ap.add_argument("--accounts", help="accounts.json for acct()/bill() (default from the ledger config)")
    for f in ("since", "until", "tool", "host", "account", "model", "project", "session", "kind", "plan", "billing", "grep"):
        ap.add_argument("--" + f)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--format", default="table", choices=["table", "csv", "json", "jsonl"])
    a = ap.parse_args()
    if a.presets or not a.preset:
        for k, (desc, _) in PRESETS.items():
            print("%-16s %s" % (k, desc))
        print("%-16s %s" % ("sql", "free SQL over tables events, sessions, prompts (read-only)"))
        print("%-16s %s" % ("logs", "regex search inside the archived raw logs (needs archive.raw_logs)"))
        return 0
    kind, path, archive, accounts = a.store_kind, a.store_path, a.archive, a.accounts
    try:
        import ledger
        cfg = ledger.load_config()
    except Exception:
        cfg = None
    if cfg:
        kind = kind or cfg["store"]["kind"]
        path = path or cfg["store"]["path"]
        archive = archive or (cfg.get("archive") or {}).get("path")
        accounts = accounts or cfg.get("accounts_path")
    # prompt text is stored only after the operator opted in (prompts.capture=y); until then the prompts table is
    # empty by design, so say so instead of answering "0 rows". An explicit --store-path is queried as given.
    capture_off = cfg is not None and not a.store_path and not ((cfg.get("prompts") or {}).get("capture"))
    if a.preset in ("prompts", "prompt-count") and capture_off:
        print("prompt capture is off (prompts.capture=n): no prompt text is stored, only counts and tokens; enable it with `ledger.py init --set prompts.capture=y` and run again")
        return 0
    if a.preset == "logs":
        import ledger_archive
        if not archive or not os.path.isdir(archive):
            raise SystemExit("no archive directory; enable archive.raw_logs at onboarding or pass --archive")
        if not a.arg:
            raise SystemExit("logs needs a pattern")
        if capture_off:
            sys.stderr.write("note: prompt capture is off; `logs` searches the archived raw files (archive.raw_logs), which is a separate opt-in from the prompts table\n")
        ar = ledger_archive.Archive(archive)
        hits = list(ar.grep(a.arg, a.host, a.since, a.until, a.project, a.limit))
        emit(["ts", "host", "path", "line", "snippet"], [(h["ts"], h["host"], h["path"], h["line"], h["snippet"]) for h in hits], a.format)
        return 0
    if not (kind and path):
        raise SystemExit("no store configured; run ledger.py init or pass --store-kind/--store-path")
    db = open_db(kind, path)
    attach_accounts(db, accounts)
    if a.preset == "sql":
        if not a.arg:
            raise SystemExit("sql needs a query")
        cols, rows = run_query(db, a.arg, [], a.limit if "limit" not in a.arg.lower() else None)
    else:
        if a.preset not in PRESETS:
            raise SystemExit("unknown preset %s (see --presets)" % a.preset)
        sql = PRESETS[a.preset][1]
        table = "prompts" if "{pwhere}" in sql else "sessions" if "{swhere}" in sql else "events"
        where, args = build_where(a, table)
        sql = sql.replace("{where}", where).replace("{pwhere}", where).replace("{swhere}", where)
        cols, rows = run_query(db, sql, args, None if a.preset == "totals" else a.limit)
    emit(cols, rows, a.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
