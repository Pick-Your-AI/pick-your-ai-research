#!/usr/bin/env python3
"""
compile_ai_logs.py - scan AI coding-agent logs (Claude Code, Codex, Copilot CLI,
opencode) and normalise every model call into one event stream.

  scan   : walk one host's log roots -> events.jsonl (+ prompts.jsonl, sessions meta)
  report : merge one or more scan outputs -> CSV/Markdown/JSON summaries

Runs on Python 3.8+ with stdlib only, so the same file works on Windows and
inside WSL (run natively there to avoid the slow 9p bridge).
"""
import argparse
import contextlib
import csv
import glob
import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

# safety.py holds the shared predicates; this file is also copied alone to SSH hosts (run_pipeline.py scp's only the
# scanner), so when the module is not beside us the same two rules are applied by the fallbacks below.
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import safety as _safety
except ImportError:  # standalone copy on a remote host
    _safety = None

import goose_usage  # noqa: E402 -- resolve sibling modules for importlib callers too

_FALLBACK_CRED_BASENAMES = ("auth.json", ".credentials.json", "credentials.json", ".env", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa")
_FALLBACK_CRED_PATTERNS = re.compile(r"(?:^|[^a-z])(?:token|secret|credential|password|passwd|apikey|api_key)(?:[^a-z]|$)|\.pem$|\.key$|\.p12$|\.pfx$|^\.env\.|^id_rsa|^id_ed25519", re.IGNORECASE)
_FALLBACK_CRED_DIRS = {".ssh", ".aws", ".gnupg", ".azure", ".kube", ".docker"}
_FALLBACK_BROAD_DIRS = {"", "appdata", "roaming", "local", ".config", ".local", "share", "documents", "desktop", "downloads", "users", "home", "library", "application support"}


def is_credential_file(path):
    """True for anything that looks like a credential, key or secret store: never read by the generic sniffer."""
    if _safety is not None:
        return _safety.is_credential_file(path)
    p = str(path or "").replace("\\", "/")
    base = p.rstrip("/").split("/")[-1]
    if base.lower() in _FALLBACK_CRED_BASENAMES or _FALLBACK_CRED_PATTERNS.search(base):
        return True
    return any(part in _FALLBACK_CRED_DIRS for part in p.split("/")[:-1])


def check_generic_root(path):
    """A generic-sniffer root must be one tool's own directory, never a home, drive root or broad container
    (AppData, .config, Documents ...): every JSON file below it will be read. Raises SystemExit when refused."""
    if _safety is not None:
        return _safety.check_generic_root(path)
    p = str(path or "").replace("\\", "/").rstrip("/")
    home = os.path.expanduser("~").replace("\\", "/").rstrip("/")
    norm = p.lower()
    if norm in ("", home.lower()) or re.fullmatch(r"[a-z]:", norm) or norm in ("/", "/home", "/users", "/root", "/mnt", "/srv", "/opt", "/var", "/tmp"):
        raise SystemExit("generic root %r is a home, drive or system root; point it at the tool's own directory" % p)
    parts = [x for x in norm.split("/") if x]
    if (parts[-1] if parts else "") in _FALLBACK_BROAD_DIRS:
        raise SystemExit("generic root %r is a broad directory; point it at the tool's own directory below it" % p)
    return p



def _private_dir(path):
    """Create or tighten an output directory (0700 on POSIX). Uses safety.py when it sits beside us, stdlib otherwise."""
    if _safety is not None:
        return _safety.private_dir(path)
    os.makedirs(path, exist_ok=True)
    if os.name != "nt":
        try:
            if os.stat(path).st_mode & 0o077:
                os.chmod(path, 0o700)
        except OSError:
            pass
    return path


def _private_file(path):
    """Tighten an existing output file to 0600 on POSIX; no-op on Windows."""
    if _safety is not None:
        return _safety.private_file(path)
    if os.name != "nt" and path and os.path.exists(path):
        try:
            if os.stat(path).st_mode & 0o077:
                os.chmod(path, 0o600)
        except OSError:
            pass
    return path


@contextlib.contextmanager
def _private_open(path, mode="w", encoding="utf-8", newline=None):
    """Open a sensitive scan/report file as 0600 from creation; its directory is made 0700 first.

    The mode passed to os.open only applies at creation, so an existing file opened with truncation is
    tightened afterwards by _private_file()."""
    _private_dir(os.path.dirname(os.path.abspath(path)) or ".")
    flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if "a" in mode else os.O_TRUNC)
    fd = os.open(path, flags, 0o600)
    try:
        if "b" in mode:
            fh = os.fdopen(fd, "wb")
        else:
            fh = os.fdopen(fd, "w", encoding=encoding, newline=newline)
        with fh:
            yield fh
    finally:
        _private_file(path)


class _NullWriter:
    """Prompt sink when prompt capture is off: nothing is kept."""

    def write(self, _text):
        return 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def iso(ts):
    """Normalise many timestamp shapes to ISO-8601 UTC string (or None)."""
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            if ts > 1e12:  # ms
                ts = ts / 1000.0
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        s = str(ts)
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        # trim >6 fractional digits (python <3.11 chokes)
        m = re.match(r"^(.*\.\d{6})\d+([+-]\d\d:\d\d)?$", s)
        if m:
            s = m.group(1) + (m.group(2) or "")
        d = datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc).isoformat()
    except Exception:
        return None


def parse_iso(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def event(tool, host, ts, session, model, **kw):
    e = {
        "tool": tool,
        "host": host,
        "ts": ts,
        "date": ts[:10] if ts else None,
        "session": session,
        "model": model,
        "input_uncached": 0,
        "cache_read": 0,
        "cache_write": 0,
        "output": 0,
        "reasoning": 0,
    }
    e.update(kw)
    e["total"] = (e["input_uncached"] or 0) + (e["cache_read"] or 0) + (e["cache_write"] or 0) + (e["output"] or 0)
    return e


def walk_files(root, pattern):
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if pattern(fn):
                yield os.path.join(dirpath, fn)


class Stats:
    def __init__(self):
        self.files = 0
        self.bytes = 0
        self.lines = 0
        self.events = 0
        self.errors = 0
        self.skipped_replay = 0
        self.dedup = 0
        self.t0 = time.time()

    def log(self, msg=""):
        el = time.time() - self.t0
        sys.stderr.write("[%6.0fs] files=%d bytes=%.1fGB lines=%d events=%d err=%d %s\n" % (
            el, self.files, self.bytes / 1e9, self.lines, self.events, self.errors, msg))
        sys.stderr.flush()


# ----------------------------------------------------------------------------
# Claude Code   ~/.claude/projects/<proj>/<session>.jsonl  (+ agent-*.jsonl)
# ----------------------------------------------------------------------------

def scan_claude(root, host, out, stats, seen_msg_ids, session_meta):
    proj_root = os.path.join(root, "projects")
    if not os.path.isdir(proj_root):
        return
    for path in walk_files(proj_root, lambda f: f.endswith(".jsonl")):
        stats.files += 1
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        stats.bytes += size
        proj_dir = os.path.relpath(os.path.dirname(path), proj_root).split(os.sep)[0]
        base = os.path.basename(path)[:-6]
        is_agent = base.startswith("agent-")
        session_id = None
        cwd = None
        version = None
        entrypoint = None
        first_ts = None
        last_ts = None
        n_user = 0
        n_tool = 0
        try:
            with open(path, "rb") as fh:
                for raw in fh:
                    stats.lines += 1
                    if b'"usage"' not in raw and b'"type":"user"' not in raw and b'"cwd"' not in raw:
                        continue
                    try:
                        d = json.loads(raw)
                    except Exception:
                        stats.errors += 1
                        continue
                    if not isinstance(d, dict):
                        continue
                    t = d.get("type")
                    ts = d.get("timestamp")
                    if session_id is None and d.get("sessionId"):
                        session_id = d["sessionId"]
                    if cwd is None and d.get("cwd"):
                        cwd = d["cwd"]
                    if version is None and d.get("version"):
                        version = d["version"]
                    if entrypoint is None and d.get("entrypoint"):
                        entrypoint = d["entrypoint"]
                    if ts:
                        if first_ts is None:
                            first_ts = ts
                        last_ts = ts
                    if t == "user":
                        c = d.get("message", {}).get("content")
                        if isinstance(c, str) or (isinstance(c, list) and c and isinstance(c[0], dict) and c[0].get("type") == "text"):
                            n_user += 1
                        continue
                    if t != "assistant":
                        continue
                    msg = d.get("message") or {}
                    usage = msg.get("usage")
                    if not usage:
                        continue
                    mid = msg.get("id") or d.get("uuid")
                    if mid in seen_msg_ids:
                        stats.dedup += 1
                        continue
                    seen_msg_ids.add(mid)
                    content = msg.get("content") or []
                    n_tool += sum(1 for c in content if isinstance(c, dict) and c.get("type") == "tool_use")
                    thinking = 0
                    otd = usage.get("output_tokens_details") or {}
                    if isinstance(otd, dict):
                        thinking = otd.get("thinking_tokens") or 0
                    cc = usage.get("cache_creation") or {}
                    cw = usage.get("cache_creation_input_tokens") or 0
                    cw1h = cc.get("ephemeral_1h_input_tokens") if isinstance(cc, dict) else None
                    cw5m = cc.get("ephemeral_5m_input_tokens") if isinstance(cc, dict) else None
                    if cw1h is None and cw5m is None:
                        cw5m, cw1h = cw, 0  # older transcripts: TTL unknown, treat as 5-minute
                    e = event(
                        "claude-code", host, iso(ts), session_id or base, msg.get("model"),
                        input_uncached=usage.get("input_tokens") or 0,
                        cache_read=usage.get("cache_read_input_tokens") or 0,
                        cache_write=cw,
                        cache_write_5m=cw5m or 0,
                        cache_write_1h=cw1h or 0,
                        output=usage.get("output_tokens") or 0,
                        reasoning=thinking,
                        cwd=cwd,
                        project=proj_dir,
                        kind="subagent" if (is_agent or d.get("isSidechain")) else "main",
                        parent=d.get("agentId") if is_agent else None,
                        entrypoint=entrypoint,
                        version=version,
                        effort=d.get("effort"),
                        request_id=d.get("requestId"),
                        service_tier=usage.get("service_tier"),
                        src=path,
                    )
                    out.write(json.dumps(e) + "\n")
                    stats.events += 1
        except OSError as ex:
            stats.errors += 1
            sys.stderr.write("ERR %s: %s\n" % (path, ex))
        session_meta.append({
            "tool": "claude-code", "host": host, "session": session_id or base, "file": path,
            "bytes": size, "project": proj_dir, "cwd": cwd, "kind": "subagent" if is_agent else "main",
            "first_ts": iso(first_ts), "last_ts": iso(last_ts), "user_msgs": n_user, "tool_calls": n_tool,
            "version": version,
        })
        if stats.files % 200 == 0:
            stats.log(path)


def scan_claude_history(root, host, out_prompts):
    p = os.path.join(root, "history.jsonl")
    if not os.path.isfile(p):
        return 0
    n = 0
    with open(p, "rb") as fh:
        for raw in fh:
            try:
                d = json.loads(raw)
            except Exception:
                continue
            out_prompts.write(json.dumps({
                "tool": "claude-code", "host": host, "ts": iso(d.get("timestamp")),
                "session": d.get("sessionId"), "cwd": d.get("project"), "text": d.get("display"),
            }) + "\n")
            n += 1
    return n


# ----------------------------------------------------------------------------
# Codex   ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl  and archived_sessions/
# ----------------------------------------------------------------------------

def load_codex_threads(root):
    """thread id -> row from state_5.sqlite (for model fallback + cross-check)."""
    threads = {}
    db = os.path.join(root, "state_5.sqlite")
    if not os.path.isfile(db):
        return threads
    try:
        uri = "file:%s?mode=ro" % db.replace("\\", "/")
        c = sqlite3.connect(uri, uri=True)
        cols = [r[1] for r in c.execute("pragma table_info(threads)")]
        want = [x for x in ("id", "model", "cwd", "title", "tokens_used", "created_at", "updated_at", "source", "thread_source", "cli_version", "archived", "reasoning_effort") if x in cols]
        for row in c.execute("select %s from threads" % ",".join(want)):
            threads[row[0]] = dict(zip(want, row))
        c.close()
    except Exception as ex:
        sys.stderr.write("sqlite threads read failed %s: %s\n" % (db, ex))
    return threads


def scan_codex(root, host, out, stats, session_meta, thread_rows):
    dirs = [os.path.join(root, "sessions"), os.path.join(root, "archived_sessions")]
    for d in dirs:
        if not os.path.isdir(d):
            continue
        archived = d.endswith("archived_sessions")
        for path in walk_files(d, lambda f: f.startswith("rollout-") and f.endswith(".jsonl")):
            stats.files += 1
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            stats.bytes += size
            m = re.search(r"rollout-\d{4}-\d\d-\d\dT\d\d-\d\d-\d\d-([0-9a-f-]{36})\.jsonl$", os.path.basename(path))
            thread_id = m.group(1) if m else os.path.basename(path)[:-6]
            trow = thread_rows.get(thread_id, {})
            meta = {}
            model = None
            effort = None
            first_line_ts = None
            last_ts = None
            prev_total = None
            forked = False
            n_user = 0
            n_tool = 0
            n_events_file = 0
            last_plan = None
            last_credits = None
            last_limit = None
            plan_counts = {}
            in_replay = False     # forked/spawned rollouts start with a replay of the parent's history
            prev_line_ts = None
            try:
                with open(path, "rb") as fh:
                    for raw in fh:
                        stats.lines += 1
                        if (b'"token_count"' not in raw and b'"turn_context"' not in raw
                                and b'"session_meta"' not in raw and b'"user_message"' not in raw
                                and b'"function_call"' not in raw and b'"custom_tool_call"' not in raw):
                            continue
                        try:
                            d = json.loads(raw)
                        except Exception:
                            stats.errors += 1
                            continue
                        if not isinstance(d, dict):
                            continue
                        t = d.get("type")
                        ts = d.get("timestamp")
                        if ts and first_line_ts is None:
                            first_line_ts = ts
                        if ts:
                            last_ts = ts
                        # replay detection: the copied history is written as one burst; the first
                        # gap of more than 2 s between consecutive lines ends it
                        if in_replay and ts and prev_line_ts:
                            a_, b_ = parse_iso(iso(prev_line_ts) or ""), parse_iso(iso(ts) or "")
                            if a_ and b_ and (b_ - a_).total_seconds() > 2:
                                in_replay = False
                        if ts:
                            prev_line_ts = ts
                        p = d.get("payload") or {}
                        if t == "session_meta":
                            if meta:
                                # a second session_meta is the replayed parent's: proof of replay
                                forked = True
                                in_replay = True
                                continue
                            meta = p
                            forked = bool(p.get("forked_from_id"))
                            src = p.get("source")
                            if isinstance(src, dict) and "subagent" in src:
                                forked = True
                            in_replay = forked
                            continue
                        if t == "turn_context":
                            model = p.get("model") or model
                            cm = p.get("collaboration_mode") or {}
                            effort = (cm.get("settings") or {}).get("reasoning_effort") or p.get("reasoning_effort") or effort
                            continue
                        if t == "response_item":
                            pt = p.get("type")
                            if pt in ("function_call", "custom_tool_call"):
                                n_tool += 1
                            continue
                        if t != "event_msg":
                            continue
                        pt = p.get("type")
                        if pt == "user_message":
                            n_user += 1
                            continue
                        if pt != "token_count":
                            continue
                        rl = p.get("rate_limits") or {}
                        if isinstance(rl, dict) and rl.get("plan_type"):
                            last_plan = rl.get("plan_type")
                            last_credits = (rl.get("credits") or {}).get("has_credits")
                            last_limit = rl.get("limit_id")
                        info = p.get("info")
                        if not info:
                            continue
                        tot = (info.get("total_token_usage") or {}).get("total_tokens")
                        last = info.get("last_token_usage") or {}
                        if prev_total is not None and tot == prev_total:
                            stats.dedup += 1
                            continue
                        # replayed parent history at fork/spawn time: skip everything in the
                        # leading burst (until the first >2 s gap between lines)
                        if in_replay:
                            stats.skipped_replay += 1
                            prev_total = tot
                            continue
                        prev_total = tot
                        inp = last.get("input_tokens") or 0
                        cached = last.get("cached_input_tokens") or 0
                        e = event(
                            "codex", host, iso(ts), thread_id, model or trow.get("model"),
                            input_uncached=max(inp - cached, 0),
                            cache_read=cached,
                            cache_write=0,
                            output=last.get("output_tokens") or 0,
                            reasoning=last.get("reasoning_output_tokens") or 0,
                            cwd=meta.get("cwd") or trow.get("cwd"),
                            kind="subagent" if forked else "main",
                            parent=meta.get("forked_from_id"),
                            entrypoint=meta.get("originator"),
                            version=meta.get("cli_version"),
                            effort=effort,
                            archived=archived,
                            plan=last_plan,
                            credits=last_credits,
                            limit_id=last_limit,
                            src=path,
                        )
                        plan_counts[last_plan or "?"] = plan_counts.get(last_plan or "?", 0) + 1
                        out.write(json.dumps(e) + "\n")
                        stats.events += 1
                        n_events_file += 1
            except OSError as ex:
                stats.errors += 1
                sys.stderr.write("ERR %s: %s\n" % (path, ex))
            session_meta.append({
                "tool": "codex", "host": host, "session": thread_id, "file": path, "bytes": size,
                "cwd": meta.get("cwd") or trow.get("cwd"), "kind": "subagent" if forked else "main",
                "parent": meta.get("forked_from_id"), "originator": meta.get("originator"),
                "version": meta.get("cli_version"), "model": model or trow.get("model"),
                "first_ts": iso(meta.get("timestamp") or first_line_ts), "last_ts": iso(last_ts),
                "user_msgs": n_user, "tool_calls": n_tool, "calls": n_events_file,
                "sqlite_tokens_used": trow.get("tokens_used"), "title": trow.get("title"),
                "archived": archived, "plans": plan_counts,
            })
            if stats.files % 200 == 0:
                stats.log(path)


def scan_codex_history(root, host, out_prompts):
    p = os.path.join(root, "history.jsonl")
    if not os.path.isfile(p):
        return 0
    n = 0
    with open(p, "rb") as fh:
        for raw in fh:
            try:
                d = json.loads(raw)
            except Exception:
                continue
            out_prompts.write(json.dumps({
                "tool": "codex", "host": host, "ts": iso(d.get("ts")),
                "session": d.get("session_id"), "cwd": None, "text": d.get("text"),
            }) + "\n")
            n += 1
    return n


# ----------------------------------------------------------------------------
# GitHub Copilot CLI   ~/.copilot/session-state/<id>/events.jsonl
# ----------------------------------------------------------------------------

def scan_copilot(root, host, out, stats, session_meta, out_prompts):
    ss = os.path.join(root, "session-state")
    if not os.path.isdir(ss):
        return
    for sid in os.listdir(ss):
        path = os.path.join(ss, sid, "events.jsonl")
        if not os.path.isfile(path):
            continue
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        cwd = None
        model = None
        first_ts = last_ts = None
        n_user = n_tool = n_ev = 0
        msg_out = 0
        shutdown_seen = False
        with open(path, "rb") as fh:
            for raw in fh:
                stats.lines += 1
                try:
                    d = json.loads(raw)
                except Exception:
                    stats.errors += 1
                    continue
                t = d.get("type")
                data = d.get("data") or {}
                ts = d.get("timestamp")
                if ts:
                    first_ts = first_ts or ts
                    last_ts = ts
                if t == "session.start":
                    cwd = (data.get("context") or {}).get("cwd")
                elif t == "session.auto_mode_resolved":
                    model = data.get("chosenModel") or model
                elif t == "session.model_change":
                    model = data.get("newModel") or model
                elif t == "user.message":
                    n_user += 1
                    out_prompts.write(json.dumps({"tool": "copilot-cli", "host": host, "ts": iso(ts), "session": sid, "cwd": cwd, "text": data.get("content")}) + "\n")
                elif t == "tool.execution_start":
                    n_tool += 1
                elif t == "assistant.message":
                    # assistant.message only carries outputTokens; the authoritative
                    # per-session totals arrive in session.shutdown.tokenDetails
                    if "outputTokens" in data:
                        n_ev += 1
                        msg_out += data.get("outputTokens") or 0
                        model = data.get("model") or model
                elif t == "session.shutdown" and isinstance(data.get("tokenDetails"), dict):
                    td = data["tokenDetails"]

                    def g(k, td=td):
                        return ((td.get(k) or {}).get("tokenCount")) or 0
                    e = event(
                        "copilot-cli", host, iso(ts), sid, model,
                        input_uncached=g("input"), cache_read=g("cache_read"), cache_write=g("cache_write"), output=g("output"),
                        cwd=cwd, kind="main", entrypoint="copilot-cli", src=path, calls_in_session=n_ev,
                    )
                    out.write(json.dumps(e) + "\n")
                    stats.events += 1
                    shutdown_seen = True
        if not shutdown_seen and msg_out:
            e = event("copilot-cli", host, iso(last_ts), sid, model, output=msg_out, cwd=cwd, kind="main",
                      entrypoint="copilot-cli", src=path, calls_in_session=n_ev, partial=True)
            out.write(json.dumps(e) + "\n")
            stats.events += 1
        session_meta.append({"tool": "copilot-cli", "host": host, "session": sid, "file": path, "bytes": size,
                             "cwd": cwd, "kind": "main", "model": model, "first_ts": iso(first_ts), "last_ts": iso(last_ts),
                             "user_msgs": n_user, "tool_calls": n_tool, "calls": n_ev})


# ----------------------------------------------------------------------------
# opencode   ~/.local/share/opencode/opencode.db  (message.data JSON)
# ----------------------------------------------------------------------------

def scan_opencode(db, host, out, stats, session_meta, out_prompts):
    if not os.path.isfile(db):
        return
    stats.files += 1
    stats.bytes += os.path.getsize(db)
    try:
        c = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
        sess = {}
        for row in c.execute("select id, directory, title, model, time_created, time_updated, cost from session"):
            sess[row[0]] = {"cwd": row[1], "title": row[2], "model": row[3], "first_ts": iso(row[4]), "last_ts": iso(row[5]), "cost": row[6]}
        for mid, sid, tc, data in c.execute("select id, session_id, time_created, data from message"):
            stats.lines += 1
            try:
                d = json.loads(data)
            except Exception:
                stats.errors += 1
                continue
            if d.get("role") == "user":
                txt = None
                for (pdata,) in c.execute("select data from part where message_id=?", (mid,)):
                    try:
                        pd = json.loads(pdata)
                        if pd.get("type") == "text":
                            txt = pd.get("text")
                            break
                    except Exception:
                        pass
                out_prompts.write(json.dumps({"tool": "opencode", "host": host, "ts": iso(tc), "session": sid, "cwd": (d.get("path") or {}).get("cwd"), "text": txt}) + "\n")
                continue
            tk = d.get("tokens") or {}
            if not tk:
                continue
            cache = tk.get("cache") or {}
            e = event(
                "opencode", host, iso((d.get("time") or {}).get("created") or tc), sid,
                "%s/%s" % (d.get("providerID"), d.get("modelID")),
                input_uncached=tk.get("input") or 0, cache_read=cache.get("read") or 0, cache_write=cache.get("write") or 0,
                output=tk.get("output") or 0, reasoning=tk.get("reasoning") or 0,
                cwd=(d.get("path") or {}).get("cwd"), kind="main", entrypoint="opencode", cost_usd=d.get("cost"), src=db,
            )
            out.write(json.dumps(e) + "\n")
            stats.events += 1
        for sid, s in sess.items():
            session_meta.append(dict(tool="opencode", host=host, session=sid, file=db, kind="main", **s))
        c.close()
    except Exception as ex:
        stats.errors += 1
        sys.stderr.write("opencode db failed: %s\n" % ex)


# ----------------------------------------------------------------------------
# OpenClaw   <config>/agents/<agent>/sessions/<id>.jsonl
# ----------------------------------------------------------------------------

def scan_openclaw(root, host, out, stats, session_meta, out_prompts, seen=None, tool="openclaw"):
    """root is a directory that contains .../agents/<agent>/sessions/*.jsonl somewhere below.
    Checkpoint files (<id>.checkpoint.<x>.jsonl) replay the parent session, so message ids are
    de-duplicated across every file scanned (seen is shared by the caller)."""
    if seen is None:
        seen = set()
    for path in sorted(walk_files(root, lambda f: f.endswith(".jsonl")), key=lambda p: (".checkpoint." in p, p)):
        if tool == "openclaw" and os.sep + "sessions" + os.sep not in path and "/sessions/" not in path:
            continue
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        parts = path.replace("\\", "/").split("/")
        agent = parts[-3] if len(parts) >= 3 else "?"
        deploy = root.rstrip("/\\").split("/")[-1]
        sid = os.path.basename(path)[:-6]
        cwd = None
        model = provider = None
        first_ts = last_ts = None
        n_user = n_tool = n_ev = 0
        with open(path, "rb") as fh:
            for raw in fh:
                stats.lines += 1
                if b'"usage"' not in raw and b'"type":"session"' not in raw and b'"model_change"' not in raw and b'"role":"user"' not in raw:
                    continue
                try:
                    d = json.loads(raw)
                except Exception:
                    stats.errors += 1
                    continue
                t = d.get("type")
                ts = d.get("timestamp")
                if ts:
                    first_ts = first_ts or ts
                    last_ts = ts
                if t == "session":
                    cwd = d.get("cwd")
                elif t == "model_change":
                    provider, model = d.get("provider"), d.get("modelId")
                elif t == "message":
                    m = d.get("message") or {}
                    if m.get("role") == "user":
                        n_user += 1
                        c = m.get("content")
                        txt = c if isinstance(c, str) else next((x.get("text") for x in c if isinstance(x, dict) and x.get("type") == "text"), None) if isinstance(c, list) else None
                        if txt:
                            out_prompts.write(json.dumps({"tool": "openclaw", "host": host, "ts": iso(ts), "session": sid, "cwd": cwd, "text": txt[:2000]}) + "\n")
                        continue
                    if m.get("role") != "assistant":
                        continue
                    u = m.get("usage")
                    if not u:
                        continue
                    key = (d.get("id"), ts)
                    if key in seen:
                        stats.dedup += 1
                        continue
                    seen.add(key)
                    c = m.get("content")
                    if isinstance(c, list):
                        n_tool += sum(1 for x in c if isinstance(x, dict) and x.get("type") in ("toolCall", "tool_use", "tool_call"))
                    cost = (u.get("cost") or {}).get("total")
                    e = event(
                        tool, host, iso(ts), sid, "%s/%s" % (m.get("provider") or provider, m.get("model") or model),
                        input_uncached=u.get("input") or 0, cache_read=u.get("cacheRead") or 0, cache_write=u.get("cacheWrite") or 0,
                        output=u.get("output") or 0, reasoning=0, cwd=cwd, kind="main", entrypoint="openclaw:%s" % deploy,
                        project=agent, cost_usd=cost if cost else None, src=path,
                    )
                    out.write(json.dumps(e) + "\n")
                    stats.events += 1
                    n_ev += 1
        session_meta.append({"tool": tool, "host": host, "session": sid, "file": path, "bytes": size, "cwd": cwd, "kind": "main",
                             "model": "%s/%s" % (provider, model), "originator": "openclaw:%s" % deploy, "first_ts": iso(first_ts), "last_ts": iso(last_ts),
                             "user_msgs": n_user, "tool_calls": n_tool, "calls": n_ev})


# ----------------------------------------------------------------------------
# Gemini CLI   <root>/<project_hash>/chats/session-*.json | .jsonl   (also Qwen Code history)
# ----------------------------------------------------------------------------

def _load_json_or_jsonl(path):
    """Return a dict with a 'messages' list from either a JSON document or a JSONL stream."""
    with open(path, "rb") as fh:
        raw = fh.read()
    txt = raw.decode("utf-8", "replace").strip()
    if not txt:
        return None
    if txt[0] == "{" and txt.count(chr(10)) < 2 or path.endswith(".json"):
        try:
            d = json.loads(txt)
            if isinstance(d, dict):
                return d
        except Exception:
            pass
    head, msgs = {}, []
    for line in txt.split(chr(10)):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if isinstance(d, dict) and "messages" in d and not msgs:
            head = d
            msgs.extend(d.get("messages") or [])
        elif isinstance(d, dict) and d.get("type") in ("user", "gemini", "assistant", "model") and "id" in d:
            msgs.append(d)
        elif isinstance(d, dict) and "sessionId" in d and not head:
            head = d
    head["messages"] = msgs
    return head


def scan_gemini(root, host, out, stats, session_meta, out_prompts, tool="gemini-cli"):
    for path in walk_files(root, lambda f: f.endswith(".json") or f.endswith(".jsonl")):
        if os.sep + "chats" + os.sep not in path and "/chats/" not in path:
            continue
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        d = _load_json_or_jsonl(path)
        if not d:
            continue
        sid = d.get("sessionId") or os.path.basename(path).rsplit(".", 1)[0]
        cwd = (d.get("directories") or [None])[0] if isinstance(d.get("directories"), list) else d.get("cwd")
        kind = "subagent" if d.get("kind") == "subagent" else "main"
        n_user = n_tool = n_ev = 0
        first = last = None
        for m in d.get("messages") or []:
            stats.lines += 1
            ts = m.get("timestamp")
            first = first or ts
            last = ts or last
            if m.get("type") == "user":
                n_user += 1
                c = m.get("content")
                txt = c if isinstance(c, str) else next((x.get("text") for x in c if isinstance(x, dict) and x.get("text")), None) if isinstance(c, list) else None
                if txt:
                    out_prompts.write(json.dumps({"tool": tool, "host": host, "ts": iso(ts), "session": sid, "cwd": cwd, "text": txt[:2000]}) + chr(10))
                continue
            tk = m.get("tokens")
            if not tk:
                continue
            n_tool += len(m.get("toolCalls") or [])
            e = event(
                tool, host, iso(ts), sid, m.get("model"),
                input_uncached=max((tk.get("input") or 0) - (tk.get("cached") or 0), 0), cache_read=tk.get("cached") or 0, cache_write=0,
                output=(tk.get("output") or 0) + (tk.get("thoughts") or 0), reasoning=tk.get("thoughts") or 0,
                cwd=cwd, kind=kind, entrypoint=tool, request_id=m.get("id"), src=path,
            )
            out.write(json.dumps(e) + chr(10))
            stats.events += 1
            n_ev += 1
        session_meta.append({"tool": tool, "host": host, "session": sid, "file": path, "bytes": size, "cwd": cwd, "kind": kind,
                             "first_ts": iso(d.get("startTime") or first), "last_ts": iso(d.get("lastUpdated") or last),
                             "user_msgs": n_user, "tool_calls": n_tool, "calls": n_ev})


# ----------------------------------------------------------------------------
# Cline family (Cline, Roo Code, Kilo Code, Cline CLI)   <globalStorage>/tasks/<task>/ui_messages.json
# ----------------------------------------------------------------------------

def scan_cline(root, host, out, stats, session_meta, out_prompts, tool="cline"):
    for path in walk_files(root, lambda f: f in ("ui_messages.json", "cline_messages.json")):
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        task_dir = os.path.dirname(path)
        sid = os.path.basename(task_dir)
        model = None
        cwd = None
        mp = os.path.join(task_dir, "task_metadata.json")
        if os.path.isfile(mp):
            try:
                md = json.load(open(mp, encoding="utf-8", errors="replace"))
                mu = md.get("model_usage") or []
                if mu:
                    model = (mu[-1].get("model_id") or mu[-1].get("modelId"))
                cwd = md.get("cwd_on_task_initialization") or md.get("cwd")
            except Exception:
                pass
        try:
            msgs = json.load(open(path, encoding="utf-8", errors="replace"))
        except Exception:
            stats.errors += 1
            continue
        if not isinstance(msgs, list):
            continue
        n_user = n_tool = n_ev = 0
        first = last = None
        for m in msgs:
            stats.lines += 1
            ts = m.get("ts")
            first = first or ts
            last = ts or last
            say = m.get("say") or m.get("ask")
            if say == "text" and m.get("type") == "say" and m.get("text") and n_user == 0:
                n_user += 1
                out_prompts.write(json.dumps({"tool": tool, "host": host, "ts": iso(ts), "session": sid, "cwd": cwd, "text": str(m.get("text"))[:2000]}) + chr(10))
            if say == "tool":
                n_tool += 1
            if say != "api_req_started":
                continue
            try:
                info = json.loads(m.get("text") or "{}")
            except Exception:
                continue
            if not any(k in info for k in ("tokensIn", "tokensOut")):
                continue
            e = event(
                tool, host, iso(ts), sid, info.get("model") or model,
                input_uncached=info.get("tokensIn") or 0, cache_read=info.get("cacheReads") or 0, cache_write=info.get("cacheWrites") or 0,
                output=info.get("tokensOut") or 0, reasoning=0, cwd=cwd, kind="main", entrypoint=tool,
                cost_usd=info.get("cost"), src=path,
            )
            out.write(json.dumps(e) + chr(10))
            stats.events += 1
            n_ev += 1
        session_meta.append({"tool": tool, "host": host, "session": sid, "file": path, "bytes": size, "cwd": cwd, "kind": "main", "model": model,
                             "first_ts": iso(first), "last_ts": iso(last), "user_msgs": n_user, "tool_calls": n_tool, "calls": n_ev})


# ----------------------------------------------------------------------------
# aider   <repo>/.aider.chat.history.md
# ----------------------------------------------------------------------------

_AIDER_TOK = re.compile(r"Tokens:\s*([\d,.]+k?)\s*sent,\s*([\d,.]+k?)\s*received(?:\.\s*Cost:\s*\$([\d.]+)\s*message)?", re.I)
_AIDER_START = re.compile(r"^# aider chat started at (.+)$")
_AIDER_MODEL = re.compile(r"^>\s*Model:\s*([^\s]+)")


def _aider_num(x):
    x = x.replace(",", "").lower()
    return int(float(x[:-1]) * 1000) if x.endswith("k") else int(float(x))


def scan_aider(root, host, out, stats, session_meta, out_prompts, max_depth=6):
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath[len(root):].count(os.sep) >= max_depth:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git", ".venv", "venv")]
        if ".aider.chat.history.md" not in filenames:
            continue
        path = os.path.join(dirpath, ".aider.chat.history.md")
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        session = None
        started = None
        model = None
        n_user = n_ev = 0
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                stats.lines += 1
                m = _AIDER_START.match(line)
                if m:
                    started = m.group(1).strip()
                    session = "%s@%s" % (os.path.basename(dirpath), started)
                    continue
                m = _AIDER_MODEL.match(line)
                if m:
                    model = m.group(1)
                    continue
                if line.startswith("#### "):
                    n_user += 1
                    out_prompts.write(json.dumps({"tool": "aider", "host": host, "ts": iso(started), "session": session, "cwd": dirpath, "text": line[5:].strip()[:2000]}) + chr(10))
                    continue
                m = _AIDER_TOK.search(line)
                if not m:
                    continue
                e = event("aider", host, iso(started), session or dirpath, model,
                          input_uncached=_aider_num(m.group(1)), output=_aider_num(m.group(2)), cwd=dirpath, kind="main", entrypoint="aider",
                          cost_usd=float(m.group(3)) if m.group(3) else None, src=path)
                out.write(json.dumps(e) + chr(10))
                stats.events += 1
                n_ev += 1
        session_meta.append({"tool": "aider", "host": host, "session": session or dirpath, "file": path, "bytes": size, "cwd": dirpath, "kind": "main", "model": model,
                             "first_ts": iso(started), "last_ts": None, "user_msgs": n_user, "tool_calls": 0, "calls": n_ev})


# ----------------------------------------------------------------------------
# Kimi Code CLI   <root>/sessions/**/wire.jsonl   (turn-scoped StatusUpdate records)
# ----------------------------------------------------------------------------

def scan_kimi(root, host, out, stats, session_meta, out_prompts):
    for path in walk_files(root, lambda f: f == "wire.jsonl"):
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        parts = path.replace("\\", "/").split("/")
        sid = parts[-2] if parts[-2] not in ("agents",) else parts[-3]
        for i, part in enumerate(parts):
            if part == "sessions" and i + 2 < len(parts):
                sid = parts[i + 2]
        kind = "subagent" if "/subagents/" in path.replace("\\", "/") or "/agents/" in path.replace("\\", "/") else "main"
        n_ev = 0
        first = last = None
        model = None
        with open(path, "rb") as fh:
            for raw in fh:
                stats.lines += 1
                if b"token_usage" not in raw and b"inputOther" not in raw and b"model" not in raw:
                    continue
                try:
                    d = json.loads(raw)
                except Exception:
                    stats.errors += 1
                    continue
                ts = d.get("timestamp") or d.get("ts") or d.get("time")
                first = first or ts
                last = ts or last
                model = d.get("model") or (d.get("payload") or {}).get("model") or model
                tu = None
                scope = None
                for obj in (d, d.get("payload") or {}, d.get("data") or {}):
                    if isinstance(obj, dict):
                        tu = obj.get("token_usage") or obj.get("usage") or tu
                        scope = obj.get("scope") or scope
                if not isinstance(tu, dict):
                    continue
                if scope and str(scope).lower().startswith("session"):
                    continue  # cumulative record
                iu = tu.get("input_other", tu.get("inputOther", 0)) or 0
                cr = tu.get("input_cache_read", tu.get("inputCacheRead", 0)) or 0
                cw = tu.get("input_cache_creation", tu.get("inputCacheCreation", 0)) or 0
                o = tu.get("output", 0) or 0
                if not (iu or cr or cw or o):
                    continue
                e = event("kimi", host, iso(ts), sid, model or "kimi-for-coding", input_uncached=iu, cache_read=cr, cache_write=cw, output=o,
                          kind=kind, entrypoint="kimi", src=path)
                out.write(json.dumps(e) + chr(10))
                stats.events += 1
                n_ev += 1
        session_meta.append({"tool": "kimi", "host": host, "session": sid, "file": path, "bytes": size, "kind": kind, "model": model,
                             "first_ts": iso(first), "last_ts": iso(last), "calls": n_ev})


# ----------------------------------------------------------------------------
# Mistral Vibe   <root>/logs/session/<id>/meta.json   (session-level totals only)
# ----------------------------------------------------------------------------

def scan_vibe(root, host, out, stats, session_meta, out_prompts):
    for path in walk_files(root, lambda f: f == "meta.json"):
        if "session" not in path:
            continue
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        try:
            md = json.load(open(path, encoding="utf-8", errors="replace"))
        except Exception:
            stats.errors += 1
            continue
        st = md.get("stats") or {}
        sid = md.get("session_id") or md.get("id") or os.path.basename(os.path.dirname(path))
        model = ((md.get("model") or md.get("active_model") or {}).get("name") if isinstance(md.get("model") or md.get("active_model"), dict) else md.get("model")) or None
        cwd = (md.get("environment") or {}).get("working_directory")
        ts = md.get("created_at") or md.get("start_time") or md.get("timestamp")
        pt, ct = st.get("session_prompt_tokens") or 0, st.get("session_completion_tokens") or 0
        if pt or ct:
            e = event("mistral-vibe", host, iso(ts), sid, model, input_uncached=pt, output=ct, cwd=cwd, kind="subagent" if "/agents/" in path.replace("\\", "/") else "main",
                      entrypoint="vibe", cost_usd=st.get("session_cost"), src=path, granularity="session")
            out.write(json.dumps(e) + chr(10))
            stats.events += 1
        session_meta.append({"tool": "mistral-vibe", "host": host, "session": sid, "file": path, "bytes": size, "cwd": cwd, "kind": "main", "model": model,
                             "first_ts": iso(ts), "last_ts": iso(md.get("updated_at")), "calls": 1 if (pt or ct) else 0})


# ----------------------------------------------------------------------------
# Continue   <root>/dev_data/**/tokensGenerated.jsonl
# ----------------------------------------------------------------------------

def scan_continue(root, host, out, stats, session_meta, out_prompts):
    for path in walk_files(root, lambda f: f.lower() in ("tokensgenerated.jsonl", "tokens_generated.jsonl")):
        stats.files += 1
        size = os.path.getsize(path)
        stats.bytes += size
        n_ev = 0
        with open(path, "rb") as fh:
            for raw in fh:
                stats.lines += 1
                try:
                    d = json.loads(raw)
                except Exception:
                    stats.errors += 1
                    continue
                e = event("continue", host, iso(d.get("timestamp")), d.get("sessionId") or os.path.basename(os.path.dirname(path)),
                          "%s/%s" % (d.get("provider"), d.get("model")) if d.get("provider") else d.get("model"),
                          input_uncached=d.get("promptTokens") or 0, output=d.get("generatedTokens") or 0, kind="main", entrypoint="continue", src=path)
                out.write(json.dumps(e) + chr(10))
                stats.events += 1
                n_ev += 1
        session_meta.append({"tool": "continue", "host": host, "session": os.path.basename(os.path.dirname(path)), "file": path, "bytes": size, "kind": "main", "calls": n_ev})


# ----------------------------------------------------------------------------
# Generic usage sniffer   any JSON / JSONL tree: objects that look like a usage record
# ----------------------------------------------------------------------------

_IN_KEYS = ("input_tokens", "inputTokens", "prompt_tokens", "promptTokens", "input", "input_other", "inputOther", "promptTokenCount")
_OUT_KEYS = ("output_tokens", "outputTokens", "completion_tokens", "completionTokens", "generatedTokens", "output", "candidatesTokenCount")
_CR_KEYS = ("cache_read_input_tokens", "cacheReadInputTokens", "cached_input_tokens", "cacheRead", "cache_read", "cache_read_tokens", "input_cache_read", "cachedContentTokenCount", "cached")
_CW_KEYS = ("cache_creation_input_tokens", "cacheCreationInputTokens", "cacheWrite", "cache_write", "cache_write_tokens", "input_cache_creation", "cacheWrites")
_RS_KEYS = ("reasoning_output_tokens", "reasoning_tokens", "reasoningTokens", "reasoning", "thoughts", "thoughtsTokenCount", "thinking_tokens")
_MODEL_KEYS = ("model", "modelId", "modelID", "model_id", "model_name")
_TS_KEYS = ("timestamp", "ts", "time", "created_at", "createdAt", "created", "date")
_COST_KEYS = ("cost", "cost_usd", "costUSD", "total_cost", "spend")


def _first(d, keys):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return None


def _usage_like(d):
    return isinstance(d, dict) and _first(d, _IN_KEYS) is not None and _first(d, _OUT_KEYS) is not None and all(not isinstance(v, (dict, list)) or k == "cost" for k, v in d.items())


def _walk_usage(node, ctx, found, depth=0):
    """Yield (usage_dict, context) for every usage-like dict; ctx carries nearest model/timestamp/cost seen above."""
    if goose_usage.is_goose_session(node):
        return  # Goose exports/counters are never generic billable calls.
    if depth > 12:
        return
    if isinstance(node, dict):
        c = dict(ctx)
        for k in _MODEL_KEYS:
            if isinstance(node.get(k), str):
                c["model"] = node[k]
        for k in _TS_KEYS:
            if node.get(k) is not None and not isinstance(node.get(k), (dict, list)):
                c["ts"] = node[k]
        for k in _COST_KEYS:
            if isinstance(node.get(k), (int, float)):
                c["cost"] = node[k]
        for key in ("usage", "token_usage", "tokens", "tokenUsage", "usageMetadata", "llm_metrics"):
            u = node.get(key)
            if _usage_like(u):
                found.append((u, c))
            elif isinstance(u, dict):
                _walk_usage(u, c, found, depth + 1)
        for k, v in node.items():
            if isinstance(v, (dict, list)) and k not in ("usage", "token_usage", "tokens", "tokenUsage", "usageMetadata", "llm_metrics"):
                _walk_usage(v, c, found, depth + 1)
    elif isinstance(node, list):
        for v in node:
            _walk_usage(v, ctx, found, depth + 1)


def _is_mini_swe_source(value):
    # These records require their own explicit source consent and deduplication.
    return isinstance(value, dict) and (str(value.get("trajectory_format", "")).startswith("mini-swe-agent-")
                                      or value.get("schema") == "mini-swe-agent-usage-1")


def scan_generic(root, host, out, stats, session_meta, out_prompts, tool):
    """Best-effort reader for tools without a dedicated parser (pi, codebuff, droid, amp, LM Studio, ...).
    Reads every .json/.jsonl under root and emits one event per usage-shaped object. Verify on a sample.
    Credential-looking files (auth.json, *token*, *.pem, .env* ...) are never opened; returns how many were skipped."""
    skipped = 0
    for path in walk_files(root, lambda f: f.endswith(".json") or f.endswith(".jsonl")):
        if is_credential_file(path):
            skipped += 1
            continue
        stats.files += 1
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        if size > 512 * 1024 * 1024:
            continue
        stats.bytes += size
        found = []
        try:
            if path.endswith(".jsonl"):
                with open(path, "rb") as fh:
                    for line_number, raw in enumerate(fh):
                        stats.lines += 1
                        if line_number == 0:
                            try:
                                if goose_usage.is_goose_session(json.loads(raw)):
                                    break  # Legacy header owns the whole transcript, not just this line.
                            except (ValueError, RecursionError):
                                pass
                        if not any(k.encode() in raw for k in ("usage", "token", "Tokens")):
                            continue
                        try:
                            document = json.loads(raw)
                            if not _is_mini_swe_source(document):
                                _walk_usage(document, {}, found)
                        except Exception:
                            stats.errors += 1
            else:
                with open(path, encoding="utf-8", errors="replace") as stream:
                    document = json.load(stream)
                if not _is_mini_swe_source(document):
                    _walk_usage(document, {}, found)
                stats.lines += 1
        except Exception:
            stats.errors += 1
            continue
        if not found:
            continue
        sid = os.path.basename(path).rsplit(".", 1)[0]
        n_ev = 0
        for u, c in found:
            iu = _first(u, _IN_KEYS) or 0
            cr = _first(u, _CR_KEYS) or 0
            if "input_tokens" in u and "cached_input_tokens" in u:  # OpenAI-style: input includes cached
                iu = max(iu - cr, 0)
            cost = c.get("cost")
            if isinstance(u.get("cost"), dict):
                cost = u["cost"].get("total", cost)
            elif isinstance(u.get("cost"), (int, float)):
                cost = u["cost"]
            e = event(tool, host, iso(c.get("ts")), sid, c.get("model"), input_uncached=iu, cache_read=cr, cache_write=_first(u, _CW_KEYS) or 0,
                      output=_first(u, _OUT_KEYS) or 0, reasoning=_first(u, _RS_KEYS) or 0, kind="main", entrypoint=tool, cost_usd=cost, src=path, granularity="generic")
            out.write(json.dumps(e) + chr(10))
            stats.events += 1
            n_ev += 1
        session_meta.append({"tool": tool, "host": host, "session": sid, "file": path, "bytes": size, "kind": "main", "calls": n_ev})
    return skipped


# ----------------------------------------------------------------------------
# scan command
# ----------------------------------------------------------------------------

def _generic_specs(specs):
    """'<tool>=<dir>' entries (a bare '<dir>' is tool 'generic'), every root validated before anything is read."""
    pairs = []
    for spec in specs or []:
        tool, _, root = spec.partition("=")
        if not root:
            tool, root = "generic", tool
        check_generic_root(root)
        pairs.append((tool, root))
    return pairs


def cmd_scan(a):
    generic = _generic_specs(a.generic_root)  # refuses a home, drive root or broad directory before anything is opened or written
    mini_roots = getattr(a, "mini_swe_root", None) or []
    for root in mini_roots:
        check_generic_root(os.path.realpath(os.path.expanduser(root)))
    goose_specs = list(getattr(a, "goose_root", None) or []) + [root for tool, root in generic if tool == "goose"]
    for spec in goose_specs:
        goose_usage.split_root(spec)  # Validate all explicit paths before opening scan outputs.
    generic = [(tool, root) for tool, root in generic if tool != "goose"]
    _private_dir(a.out_dir)
    stats = Stats()
    session_meta = []
    seen = set()
    inventory = []
    capture = not getattr(a, "no_prompts", False)
    ev_path = os.path.join(a.out_dir, "events.%s.jsonl" % a.host)
    pr_path = os.path.join(a.out_dir, "prompts.%s.jsonl" % a.host)
    if not capture and os.path.exists(pr_path):  # a file left by an earlier opt-in run must not be ingested as this run's
        os.remove(pr_path)
    with _private_open(ev_path, "w") as out, (_private_open(pr_path, "w") if capture else _NullWriter()) as outp:
        for root in a.claude_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_claude(root, a.host, out, stats, seen, session_meta)
            np_ = scan_claude_history(root, a.host, outp) if capture else 0  # history.jsonl holds only prompt text: not opened when capture is off
            inventory.append({"tool": "claude-code", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0, "prompts": np_})
            stats.log("claude root done %s" % root)
        for root in a.codex_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            rows = load_codex_threads(root)
            scan_codex(root, a.host, out, stats, session_meta, rows)
            np_ = scan_codex_history(root, a.host, outp) if capture else 0
            inventory.append({"tool": "codex", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0, "prompts": np_,
                              "sqlite_threads": len(rows), "sqlite_tokens_used": sum((r.get("tokens_used") or 0) for r in rows.values())})
            stats.log("codex root done %s" % root)
        for root in a.copilot_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_copilot(root, a.host, out, stats, session_meta, outp)
            inventory.append({"tool": "copilot-cli", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for db in a.opencode_db or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_opencode(db, a.host, out, stats, session_meta, outp)
            inventory.append({"tool": "opencode", "host": a.host, "root": db, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        openclaw_seen = set()
        for root in a.openclaw_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_openclaw(root, a.host, out, stats, session_meta, outp, openclaw_seen)
            inventory.append({"tool": "openclaw", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for root in a.pi_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            pi_seen = set()
            scan_openclaw(root, a.host, out, stats, session_meta, outp, pi_seen, tool="pi")
            inventory.append({"tool": "pi", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for root in a.gemini_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_gemini(root, a.host, out, stats, session_meta, outp, "gemini-cli")
            inventory.append({"tool": "gemini-cli", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for root in a.qwen_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_gemini(root, a.host, out, stats, session_meta, outp, "qwen-code")
            inventory.append({"tool": "qwen-code", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for spec in a.cline_root or []:
            tool, _, root = spec.partition("=") if "=" in spec else ("cline", "", spec)
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_cline(root, a.host, out, stats, session_meta, outp, tool or "cline")
            inventory.append({"tool": tool or "cline", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for root in a.aider_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_aider(root, a.host, out, stats, session_meta, outp)
            inventory.append({"tool": "aider", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for root in a.kimi_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_kimi(root, a.host, out, stats, session_meta, outp)
            inventory.append({"tool": "kimi", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for root in a.vibe_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_vibe(root, a.host, out, stats, session_meta, outp)
            inventory.append({"tool": "mistral-vibe", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        for root in a.continue_root or []:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            scan_continue(root, a.host, out, stats, session_meta, outp)
            inventory.append({"tool": "continue", "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0})
        if mini_roots:
            from mini_swe_usage import scan as scan_mini_swe
            mini_seen = set()
            for root in mini_roots:
                n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
                scan_mini_swe(root, a.host, out, stats, session_meta, mini_seen)
                inventory.append({"tool": "mini-swe-agent", "host": a.host, "root": root, "events": stats.events - n0,
                                  "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0, "prompts": 0})
        goose_seen = set()
        for spec in goose_specs:
            events, coverage = goose_usage.collect(spec, a.host)
            for e in events:
                if e["request_id"] in goose_seen:
                    stats.dedup += 1
                    continue
                goose_seen.add(e["request_id"])
                out.write(json.dumps(e, allow_nan=False) + "\n")
                stats.events += 1
            stats.files += coverage["files"]
            stats.bytes += coverage["bytes"]
            stats.errors += coverage["errors"]
            inventory.append(coverage)
            by_session = defaultdict(list)
            for e in events:
                by_session[e["session"]].append(e)
            for sid, rows in by_session.items():
                session_meta.append({"tool": "goose", "host": a.host, "session": sid, "calls": len(rows),
                                     "first_ts": min(e["ts"] for e in rows), "last_ts": max(e["ts"] for e in rows),
                                     "file": None, "kind": "main", "model": rows[0]["model"] if len({e["model"] for e in rows}) == 1 else None})
        for tool, root in generic:
            n0, f0, b0, e0 = stats.events, stats.files, stats.bytes, stats.errors
            skipped = scan_generic(root, a.host, out, stats, session_meta, outp, tool)
            inventory.append({"tool": tool, "host": a.host, "root": root, "events": stats.events - n0, "files": stats.files - f0, "bytes": stats.bytes - b0, "errors": stats.errors - e0,
                              "credential_files_skipped": skipped, "note": "generic usage sniffer; %d credential-like files skipped; verify on a sample" % skipped})
    with _private_open(os.path.join(a.out_dir, "sessions.%s.jsonl" % a.host), "w") as f:
        for s in session_meta:
            f.write(json.dumps(s) + "\n")
    with _private_open(os.path.join(a.out_dir, "inventory.%s.json" % a.host), "w") as f:
        json.dump({"host": a.host, "roots": inventory, "files": stats.files, "bytes": stats.bytes, "lines": stats.lines,
                   "events": stats.events, "json_errors": stats.errors, "codex_replay_skipped": stats.skipped_replay,
                   "dedup_skipped": stats.dedup, "prompts_captured": capture, "seconds": round(time.time() - stats.t0, 1)}, f, indent=2)
    stats.log("DONE")


# ----------------------------------------------------------------------------
# report command
# ----------------------------------------------------------------------------

def fmt(n):
    return "{:,}".format(int(n))



def load_pricing(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def price_event(e, pricing):
    """Return (api_cost_usd, cost_if_nothing_cached_usd, priced_as, assumed) for one event."""
    if e.get("usage_pricing_eligible") is False:
        return 0.0, 0.0, None, "Incomplete or estimated usage; token category sums may be partial"
    if not pricing:
        return 0.0, 0.0, None, None
    models = pricing.get("models", {})
    model = e.get("model") or "?"
    row = models.get(model)
    priced_as = model
    assumed = None
    if row is None and "/" in model:  # provider-prefixed names (openclaw, opencode): try the bare model id
        bare = model.split("/", 1)[1]
        if bare in models:
            row = models[bare]
            priced_as = bare
    if row is None:
        fb = (pricing.get("fallback_by_tool") or {}).get(e.get("tool"))
        if fb:
            row = models.get(fb["model"])
            priced_as = fb["model"]
            reason = "No model recorded" if model == "?" else "No price for %s" % model
            assumed = "%s; using %s" % (reason, priced_as)
            if fb.get("note"):
                assumed += ". " + fb["note"]
        if row is None:
            return 0.0, 0.0, None, "no price for %s" % model
    if e.get("tool") == "mini-swe-agent" and e.get("partial"):
        assumed = "; ".join(x for x in (assumed, "mini-SWE usage has missing/conflicting source fields; cost covers normalized categories only") if x)
    if row.get("assumed"):
        assumed = "; ".join(x for x in (assumed, row["assumed"]) if x)
    if e.get("tool") == "goose":
        note = "Goose API-equivalent estimate: unreported cache categories use uncached input; cache-write TTL uses the snapshot default; native cost evidence is separate"
        assumed = "; ".join(x for x in (assumed, note) if x)
        if row.get("use_logged_cost") and e.get("cost_usd") is None:
            return 0.0, 0.0, None, "Goose has no currency-verified logged charge"
    if row.get("use_logged_cost"):
        c = float(e.get("cost_usd") or 0)
        return c, c, priced_as, assumed
    iu = e.get("input_uncached") or 0
    cr = e.get("cache_read") or 0
    cw5 = e.get("cache_write_5m")
    cw1 = e.get("cache_write_1h") or 0
    if cw5 is None:
        cw5 = e.get("cache_write") or 0
    out = e.get("output") or 0
    # Context premiums depend on the complete prompt, including cached tokens.
    # Existing snapshots without a tier retain their flat-rate behavior.
    tier = row.get("long_context")
    if tier and iu + cr + cw5 + cw1 > tier["input_tokens_gt"]:
        row = dict(row, **tier)
        if tier.get("assumed"):
            assumed = "; ".join(x for x in (assumed, tier["assumed"]) if x)
    cost = (iu * row["input"] + cr * row["cache_read"] + cw5 * row["cache_write_5m"] + cw1 * row["cache_write_1h"] + out * row["output"]) / 1e6
    nocache = ((iu + cr + cw5 + cw1) * row["input"] + out * row["output"]) / 1e6
    return cost, nocache, priced_as, assumed


def account_source(AC):
    """How accounts.json was drafted: its own _source, else inferred from _sensitivity (files from 1.5.5/1.5.6), else unknown."""
    if not AC:
        return None
    if AC.get("_source"):
        return AC["_source"]
    sens = AC.get("_sensitivity")
    if sens == "placeholders":
        return "host placeholders"
    if sens == "account metadata":
        return "credential files"
    if any((v.get("emails") or v.get("orgs")) for v in (AC.get("accounts") or {}).values() if isinstance(v, dict)):
        return "credential files, identifiable"
    return "unspecified"


def load_accounts(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def assign_account(e, AC):
    """Return (account_key, billing, confidence) from the first matching rule."""
    if not AC:
        return "unattributed", "unknown", "low"
    for rule in AC.get("rules", []):
        w = rule.get("when", {})
        if w.get("tool") and e.get("tool") != w["tool"]:
            continue
        if w.get("host") and e.get("host") != w["host"]:
            continue
        if w.get("plan") and (e.get("plan") or "") != w["plan"]:
            continue
        if w.get("cwd_contains") and w["cwd_contains"].lower() not in (e.get("cwd") or "").lower():
            continue
        if w.get("date_from") and (e.get("date") or "") < w["date_from"]:
            continue
        if w.get("date_to") and (e.get("date") or "") > w["date_to"]:
            continue
        return rule["account"], rule.get("billing", "subscription"), rule.get("confidence", "medium")
    return "unattributed", "unknown", "low"


def external_sort_csv(src, dst, header_line, chunk_rows=400000):
    """Sort a headerless CSV by its first field (the ISO timestamp) into dst with a header; chunked merge sort on disk."""
    import heapq
    import tempfile
    chunks = []
    tmpdir = tempfile.mkdtemp(prefix="ledger-sort-", dir=os.path.dirname(os.path.abspath(dst)) or None)
    try:
        with open(src, "r", encoding="utf-8", newline="") as fh:
            buf = []
            for line in fh:
                if not line.strip():
                    continue
                buf.append(line)
                if len(buf) >= chunk_rows:
                    buf.sort(key=lambda ln: ln.split(",", 1)[0])
                    p = os.path.join(tmpdir, "chunk-%d.csv" % len(chunks))
                    with _private_open(p, "w", newline="") as out:
                        out.writelines(buf)
                    chunks.append(p)
                    buf = []
            if buf or not chunks:
                buf.sort(key=lambda ln: ln.split(",", 1)[0])
                p = os.path.join(tmpdir, "chunk-%d.csv" % len(chunks))
                with _private_open(p, "w", newline="") as out:
                    out.writelines(buf)
                chunks.append(p)
        handles = [open(p, "r", encoding="utf-8", newline="") for p in chunks]
        try:
            with _private_open(dst, "w", newline="") as out:
                out.write(header_line)
                for line in heapq.merge(*handles, key=lambda ln: ln.split(",", 1)[0]):
                    out.write(line)
        finally:
            for h in handles:
                h.close()
    finally:
        for p in chunks:
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass


def cmd_report(a):
    _private_dir(a.out_dir)
    cols = ["ts", "date", "tool", "host", "session", "kind", "model", "effort", "entrypoint", "version", "cwd",
            "input_uncached", "cache_read", "cache_write", "cache_write_5m", "cache_write_1h", "output", "reasoning", "total",
            "api_cost_usd", "cost_if_uncached_usd", "cache_savings_usd", "priced_as", "cost_usd", "plan", "account", "billing", "account_confidence", "request_id", "src", "provider", "upstream_provider", "backend", "backend_library_version",
            "execution_status", "source_calculated_cost", "provider_reported_cost", "cost_provenance", "provider_cost_provenance",
            "timestamp_provenance", "model_provenance", "total_provenance", "unclassified_tokens", "partial", "usage_warnings"]
    NUM = ("input_uncached", "cache_read", "cache_write", "output", "reasoning", "total")
    COST = ("api_cost_usd", "cost_if_uncached_usd", "cache_savings_usd")
    pricing = load_pricing(a.pricing)
    assumed_models = {}

    def newagg():
        return {"calls": 0, "input_uncached": 0, "cache_read": 0, "cache_write": 0, "output": 0, "reasoning": 0, "total": 0,
                "api_cost_usd": 0.0, "cost_if_uncached_usd": 0.0, "cache_savings_usd": 0.0, "sessions": set()}
    aggs = {
        "by_tool": (["tool"], lambda e: e["tool"], defaultdict(newagg)),
        "by_tool_host": (["tool", "host"], lambda e: (e["tool"], e["host"]), defaultdict(newagg)),
        "by_model": (["tool", "model"], lambda e: (e["tool"], e.get("model") or "?"), defaultdict(newagg)),
        "by_month_tool": (["month", "tool"], lambda e: ((e.get("date") or "?")[:7], e["tool"]), defaultdict(newagg)),
        "by_day_tool": (["date", "tool"], lambda e: (e.get("date") or "?", e["tool"]), defaultdict(newagg)),
        "by_project": (["tool", "cwd"], lambda e: (e["tool"], (e.get("cwd") or "?")), defaultdict(newagg)),
        "by_tool_kind": (["tool", "kind"], lambda e: (e["tool"], e.get("kind") or "?"), defaultdict(newagg)),
        "by_entrypoint": (["tool", "entrypoint"], lambda e: (e["tool"], e.get("entrypoint") or "?"), defaultdict(newagg)),
        "by_session": (["tool", "host", "session"], lambda e: (e["tool"], e["host"], e.get("session")), defaultdict(newagg)),
        "by_account": (["account"], lambda e: e.get("account") or "unattributed", defaultdict(newagg)),
        "by_account_month": (["month", "account"], lambda e: ((e.get("date") or "?")[:7], e.get("account") or "unattributed"), defaultdict(newagg)),
        "by_account_host": (["account", "host", "tool"], lambda e: (e.get("account") or "unattributed", e["host"], e["tool"]), defaultdict(newagg)),
        "by_plan": (["tool", "plan"], lambda e: (e["tool"], e.get("plan") or "?"), defaultdict(newagg)),
        "by_billing_month": (["month", "billing"], lambda e: ((e.get("date") or "?")[:7], e.get("billing") or "unknown"), defaultdict(newagg)),
    }
    AC = load_accounts(a.accounts)
    n_events = 0
    goose_report_seen = set()
    unsorted = os.path.join(a.out_dir, "all_events.unsorted.csv")
    with _private_open(unsorted, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        for pat in a.events:
            for p in sorted(glob.glob(pat)):
                sys.stderr.write("reading %s\n" % p)
                with open(p, "rb") as fh:
                    for raw in fh:
                        try:
                            e = json.loads(raw)
                        except Exception:
                            continue
                        if e.get("model") == "<synthetic>" and not e.get("total"):
                            continue  # Claude Code placeholder rows, no API call behind them
                        if e.get("tool") == "goose" and e.get("request_id"):
                            key = (e.get("host"), e["request_id"])
                            if key in goose_report_seen:
                                continue
                            goose_report_seen.add(key)
                        n_events += 1
                        cost, nocache, priced_as, assumed = price_event(e, pricing)
                        e["api_cost_usd"] = round(cost, 6)
                        e["cost_if_uncached_usd"] = round(nocache, 6)
                        e["cache_savings_usd"] = round(nocache - cost, 6)
                        e["priced_as"] = priced_as
                        acct, billing, conf = assign_account(e, AC)
                        e["account"], e["billing"], e["account_confidence"] = acct, billing, conf
                        if assumed:
                            assumed_models[e.get("model") or "?"] = assumed
                        w.writerow(e)
                        for name, (keys, kf, d) in aggs.items():
                            r = d[kf(e)]
                            r["calls"] += 1
                            for c in NUM:
                                r[c] += e.get(c) or 0
                            r["api_cost_usd"] += cost
                            r["cost_if_uncached_usd"] += nocache
                            r["cache_savings_usd"] += nocache - cost
                            r["sessions"].add(e.get("session"))
    # sort merged CSV by timestamp (first column) without holding it in memory: a Python external merge sort,
    # no shell involved (paths never become part of a command line)
    final = os.path.join(a.out_dir, "all_events.csv")
    external_sort_csv(unsorted, final, ",".join(cols) + "\n")
    os.remove(unsorted)
    sys.stderr.write("merged %d events\n" % n_events)

    def write_agg(name, keynames, d):
        rows = []
        for k, r in d.items():
            k = k if isinstance(k, tuple) else (k,)
            row = dict(zip(keynames, k))
            row.update({c: r[c] for c in ("calls",) + NUM})
            row.update({c: round(r[c], 4) for c in COST})
            row["sessions"] = len(r["sessions"])
            rows.append(row)
        rows.sort(key=lambda r: tuple(str(r[k]) for k in keynames))
        with _private_open(os.path.join(a.out_dir, name + ".csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(keynames) + ["calls", "sessions"] + list(NUM) + list(COST))
            w.writeheader()
            w.writerows(rows)
        return rows

    R = {name: write_agg(name, keys, d) for name, (keys, kf, d) in aggs.items()}
    by_tool, by_host, by_model, by_month, by_day = R["by_tool"], R["by_tool_host"], R["by_model"], R["by_month_tool"], R["by_day_tool"]
    by_cwd, by_kind, by_entry, by_sess = R["by_project"], R["by_tool_kind"], R["by_entrypoint"], R["by_session"]
    by_account, by_account_month, by_account_host, by_plan, by_billing_month = R["by_account"], R["by_account_month"], R["by_account_host"], R["by_plan"], R["by_billing_month"]

    # sessions meta merge
    sessions = []
    for pat in a.sessions or []:
        for p in glob.glob(pat):
            with open(p, "rb") as fh:
                for raw in fh:
                    try:
                        sessions.append(json.loads(raw))
                    except Exception:
                        pass
    sess_tok = {(r["tool"], r["host"], r["session"]): r for r in by_sess}
    scols = ["tool", "host", "session", "kind", "first_ts", "last_ts", "model", "originator", "version", "cwd", "title", "user_msgs", "tool_calls", "calls", "total_tokens", "output_tokens", "sqlite_tokens_used", "bytes", "archived", "parent", "file"]
    with _private_open(os.path.join(a.out_dir, "all_sessions.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=scols, extrasaction="ignore")
        w.writeheader()
        for s in sorted(sessions, key=lambda s: s.get("first_ts") or ""):
            t = sess_tok.get((s["tool"], s["host"], s["session"]))
            s["total_tokens"] = t["total"] if t else 0
            s["output_tokens"] = t["output"] if t else 0
            s["calls"] = s.get("calls") or (t["calls"] if t else 0)
            w.writerow(s)

    # prompts merge
    prompts = []
    for pat in a.prompts or []:
        for p in glob.glob(pat):
            with open(p, "rb") as fh:
                for raw in fh:
                    try:
                        prompts.append(json.loads(raw))
                    except Exception:
                        pass
    prompts.sort(key=lambda p: p.get("ts") or "")
    with _private_open(os.path.join(a.out_dir, "all_prompts.jsonl"), "w") as f:
        for p in prompts:
            f.write(json.dumps(p) + "\n")
    with _private_open(os.path.join(a.out_dir, "all_prompts.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "tool", "host", "session", "cwd", "text"], extrasaction="ignore")
        w.writeheader()
        w.writerows(prompts)

    inventories = []
    for pat in a.inventory or []:
        for p in sorted(glob.glob(pat)):
            with open(p, encoding="utf-8") as fh:
                inventories.append(json.load(fh))

    # -------- subscription vs API-equivalent, per month
    subs = (pricing or {}).get("subscriptions", {})
    sub_rows = []
    months_all = sorted({r["month"] for r in by_month if r["month"] != "?"})
    for tool, sub in subs.items():
        for m in months_all:
            rows_m = [r for r in by_month if r["month"] == m and r["tool"] == tool]
            if not rows_m:
                continue
            api = sum(r["api_cost_usd"] for r in rows_m)
            nocache = sum(r["cost_if_uncached_usd"] for r in rows_m)
            calls = sum(r["calls"] for r in rows_m)
            sub_rows.append({"month": m, "tool": tool, "plan": sub["name"], "subscription_usd": sub["monthly_usd"], "calls": calls,
                             "api_equivalent_usd": round(api, 2), "api_if_uncached_usd": round(nocache, 2),
                             "savings_vs_api_usd": round(api - sub["monthly_usd"], 2),
                             "api_to_sub_ratio": round(api / sub["monthly_usd"], 2) if sub["monthly_usd"] else None})
    with _private_open(os.path.join(a.out_dir, "subscription_vs_api.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["month", "tool", "plan", "subscription_usd", "calls", "api_equivalent_usd", "api_if_uncached_usd", "savings_vs_api_usd", "api_to_sub_ratio"])
        w.writeheader()
        w.writerows(sub_rows)
    sub_tot = {}
    for r in sub_rows:
        t = sub_tot.setdefault(r["tool"], {"plan": r["plan"], "months": 0, "subscription_usd": 0.0, "api_equivalent_usd": 0.0, "api_if_uncached_usd": 0.0})
        t["months"] += 1
        t["subscription_usd"] += r["subscription_usd"]
        t["api_equivalent_usd"] += r["api_equivalent_usd"]
        t["api_if_uncached_usd"] += r["api_if_uncached_usd"]
    for t in sub_tot.values():
        t["savings_vs_api_usd"] = round(t["api_equivalent_usd"] - t["subscription_usd"], 2)
        t["api_to_sub_ratio"] = round(t["api_equivalent_usd"] / t["subscription_usd"], 1) if t["subscription_usd"] else None

    # -------- per-account subscription vs API-equivalent
    acct_reg = (AC or {}).get("accounts", {})
    acct_billing = {}
    for r in by_account_host:  # (account, host, tool) rows carry no billing; derive it from the rules that produce each account
        acct_billing.setdefault(r["account"], set())
    for rule in (AC or {}).get("rules", []):
        acct_billing.setdefault(rule.get("account"), set()).add(rule.get("billing") or "unknown")

    def billing_of(account):
        b = acct_billing.get(account) or set()
        if b == {"unknown"} or not b:
            return "unknown"
        if "usage-based" in b and "subscription" not in b:
            return "usage-based"
        return "subscription" if "subscription" in b else sorted(b)[0]
    acct_rows = []
    acct_tot = {}
    for r in by_account_month:
        if r["month"] == "?":
            continue
        reg = acct_reg.get(r["account"], {})
        monthly = reg.get("monthly_usd", 0) or 0
        acct_rows.append({"month": r["month"], "account": r["account"], "label": reg.get("label", r["account"]), "plan": reg.get("plan", "?"), "billing": billing_of(r["account"]),
                          "subscription_usd": monthly, "calls": r["calls"], "total": r["total"], "api_equivalent_usd": round(r["api_cost_usd"], 2),
                          "api_if_uncached_usd": round(r["cost_if_uncached_usd"], 2), "api_to_sub_ratio": round(r["api_cost_usd"] / monthly, 2) if monthly else None})
        t = acct_tot.setdefault(r["account"], {"label": reg.get("label", r["account"]), "plan": reg.get("plan", "?"), "provider": reg.get("provider"), "billing": billing_of(r["account"]), "months": 0, "subscription_usd": 0.0, "api_equivalent_usd": 0.0, "api_if_uncached_usd": 0.0, "calls": 0, "total": 0})
        t["months"] += 1
        t["subscription_usd"] += monthly
        t["api_equivalent_usd"] += r["api_cost_usd"]
        t["api_if_uncached_usd"] += r["cost_if_uncached_usd"]
        t["calls"] += r["calls"]
        t["total"] += r["total"]
    for t in acct_tot.values():
        t["api_to_sub_ratio"] = round(t["api_equivalent_usd"] / t["subscription_usd"], 1) if t["subscription_usd"] else None
        t["savings_vs_api_usd"] = round(t["api_equivalent_usd"] - t["subscription_usd"], 2)
    # usage-based (real spend) by month and account: re-derive from by_billing_month for the total and by_plan for the codex business calls
    ub_month = [r for r in by_billing_month if r["billing"] == "usage-based" and r["month"] != "?"]
    with _private_open(os.path.join(a.out_dir, "subscription_vs_api_by_account.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["month", "account", "label", "plan", "billing", "subscription_usd", "calls", "total", "api_equivalent_usd", "api_if_uncached_usd", "api_to_sub_ratio"], extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(acct_rows, key=lambda r: (r["account"], r["month"])))

    # -------- markdown summary
    L = []
    tot = {c: sum(r[c] for r in by_tool) for c in ("calls",) + NUM}
    tot.update({c: sum(r[c] for r in by_tool) for c in COST})
    dates = [r["date"] for r in by_day if r["date"] != "?"]
    L.append("# AI coding-agent usage, compiled\n")
    L.append("Generated %s. %s model calls from %s sessions; %s typed prompts.\n" % (
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), fmt(n_events), fmt(len(by_sess)), fmt(len(prompts))))
    if dates:
        L.append("Date range: %s to %s (%s active days).\n" % (min(dates), max(dates), fmt(len(set(dates)))))
    L.append("Token columns: input_uncached = fresh prompt tokens; cache_read = prompt tokens served from cache; cache_write = prompt tokens written to cache (Claude only); output includes reasoning. total = sum of the four.\n")

    def cell(r, c):
        v = r.get(c, 0)
        if c.endswith("_usd"):
            return "$%s" % "{:,.2f}".format(v)
        if isinstance(v, float):
            return "%.2f" % v
        return fmt(v)

    def table(rows, keys, cols=("calls", "sessions") + NUM + ("api_cost_usd", "cache_savings_usd"), limit=None, sort=None):
        rows = list(rows)
        if sort:
            rows.sort(key=sort, reverse=True)
        if limit:
            rows = rows[:limit]
        L.append("| " + " | ".join(list(keys) + list(cols)) + " |")
        L.append("|" + "---|" * (len(keys) + len(cols)))
        for r in rows:
            L.append("| " + " | ".join([str(r.get(k, "")).replace("|", "/") for k in keys] + [cell(r, c) for c in cols]) + " |")
        L.append("")

    L.append("## Grand total\n")
    L.append("| calls | input_uncached | cache_read | cache_write | output | reasoning | total | API-equivalent cost | cost if nothing cached | cache savings |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    L.append("| %s | %s | %s | %s | %s | %s | %s | $%s | $%s | $%s |\n" % (tuple(fmt(tot[c]) for c in ("calls",) + NUM) + tuple("{:,.2f}".format(tot[c]) for c in COST)))
    L.append("## Cost: subscriptions vs API-equivalent\n")
    L.append("API-equivalent = what the same tokens would cost at list API prices (pricing.json). Subscription months counted only where that tool was used.\n")
    L.append("| tool | plan | months | subscription paid | API-equivalent | API-equivalent if nothing cached | saved vs API | API / subscription |")
    L.append("|---|---|---|---|---|---|---|---|")
    for tool, t in sub_tot.items():
        L.append("| %s | %s | %d | $%s | $%s | $%s | $%s | %sx |" % (tool, t["plan"], t["months"], "{:,.2f}".format(t["subscription_usd"]), "{:,.2f}".format(t["api_equivalent_usd"]),
                                                          "{:,.2f}".format(t["api_if_uncached_usd"]), "{:,.2f}".format(t["savings_vs_api_usd"]), t["api_to_sub_ratio"]))
    L.append("")
    L.append("| month | tool | subscription | API-equivalent | if nothing cached | API / subscription |")
    L.append("|---|---|---|---|---|---|")
    for r in sub_rows:
        L.append("| %s | %s | $%s | $%s | $%s | %sx |" % (r["month"], r["tool"], "{:,.2f}".format(r["subscription_usd"]), "{:,.2f}".format(r["api_equivalent_usd"]), "{:,.2f}".format(r["api_if_uncached_usd"]), r["api_to_sub_ratio"]))
    L.append("")
    L.append("## Accounts\n")
    L.append("Each call is attributed to an account by the rules in `accounts.json` (first match wins). `plan` is the billing plan the Codex client recorded on the call itself (`rate_limits.plan_type`); the account is inferred from host, plan, working directory and date. Confidence is per rule.\n")
    L.append("| account | label | plan | provider | months | subscription paid | API-equivalent | if nothing cached | API / subscription | calls | tokens |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, t in sorted(acct_tot.items(), key=lambda kv: -kv[1]["api_equivalent_usd"]):
        L.append("| `%s` | %s | %s | %s | %d | $%s | $%s | $%s | %s | %s | %s |" % (k, t["label"], t["plan"], t["provider"], t["months"], "{:,.2f}".format(t["subscription_usd"]), "{:,.2f}".format(t["api_equivalent_usd"]), "{:,.2f}".format(t["api_if_uncached_usd"]), ("%sx" % t["api_to_sub_ratio"]) if t["api_to_sub_ratio"] is not None else "usage-based", fmt(t["calls"]), fmt(t["total"])))
    L.append("")
    L.append("| month | account | subscription | API-equivalent | if nothing cached | API / subscription | calls |")
    L.append("|---|---|---|---|---|---|---|")
    for r in sorted(acct_rows, key=lambda r: (r["month"], r["account"])):
        L.append("| %s | `%s` | $%s | $%s | $%s | %s | %s |" % (r["month"], r["account"], "{:,.2f}".format(r["subscription_usd"]), "{:,.2f}".format(r["api_equivalent_usd"]), "{:,.2f}".format(r["api_if_uncached_usd"]), ("%sx" % r["api_to_sub_ratio"]) if r["api_to_sub_ratio"] is not None else "usage-based", fmt(r["calls"])))
    L.append("")
    L.append("### Billing plan recorded on the call (Codex `rate_limits.plan_type`)\n")
    table([r for r in by_plan if r["tool"] == "codex"], ["tool", "plan"], sort=lambda r: r["total"])
    L.append("### Usage-based (real spend at list rates, not covered by a subscription)\n")
    table(ub_month, ["month", "billing"], cols=("calls", "total", "api_cost_usd"))
    L.append("### Account by host and tool\n")
    table(by_account_host, ["account", "host", "tool"], sort=lambda r: r["total"])
    L.append("## Caching\n")
    L.append("| tool | cache hit rate (cache_read / all prompt tokens) | API-equivalent cost | cost if nothing cached | cache savings | savings % |")
    L.append("|---|---|---|---|---|---|")
    for r in sorted(by_tool, key=lambda r: -r["total"]):
        prompt = r["input_uncached"] + r["cache_read"] + r["cache_write"]
        hit = 100.0 * r["cache_read"] / prompt if prompt else 0
        pct = 100.0 * r["cache_savings_usd"] / r["cost_if_uncached_usd"] if r["cost_if_uncached_usd"] else 0
        L.append("| %s | %.1f%% | $%s | $%s | $%s | %.1f%% |" % (r["tool"], hit, "{:,.2f}".format(r["api_cost_usd"]), "{:,.2f}".format(r["cost_if_uncached_usd"]), "{:,.2f}".format(r["cache_savings_usd"]), pct))
    L.append("")
    if assumed_models:
        L.append("Priced with an assumption (no published rate): " + "; ".join("`%s` (%s)" % (k, v) for k, v in sorted(assumed_models.items())) + "\n")
    L.append("## By tool\n")
    table(by_tool, ["tool"], sort=lambda r: r["total"])
    L.append("## By tool and host\n")
    table(by_host, ["tool", "host"], sort=lambda r: r["total"])
    L.append("## By month and tool\n")
    table(by_month, ["month", "tool"])
    L.append("## By model\n")
    table(by_model, ["tool", "model"], sort=lambda r: r["total"])
    L.append("## Main thread vs sub-agent\n")
    table(by_kind, ["tool", "kind"], sort=lambda r: r["total"])
    L.append("## By entrypoint / originator\n")
    table(by_entry, ["tool", "entrypoint"], sort=lambda r: r["total"])
    L.append("## Top 40 working directories\n")
    table(by_cwd, ["tool", "cwd"], limit=40, sort=lambda r: r["total"])
    L.append("## Top 30 sessions by tokens\n")
    table(by_sess, ["tool", "host", "session"], limit=30, sort=lambda r: r["total"])
    L.append("## Busiest 30 days\n")
    day_tot = defaultdict(lambda: {"calls": 0, "total": 0, "output": 0})
    for r in by_day:
        day_tot[r["date"]]["calls"] += r["calls"]
        day_tot[r["date"]]["total"] += r["total"]
        day_tot[r["date"]]["output"] += r["output"]
    rows = [dict(date=k, **v) for k, v in day_tot.items()]
    table(rows, ["date"], cols=("calls", "output", "total"), limit=30, sort=lambda r: r["total"])
    L.append("## Scan inventory\n")
    L.append("| host | tool | root | calls | prompts | tool's own thread count | tool's own token total |")
    L.append("|---|---|---|---|---|---|---|")
    for inv in inventories:
        for r in inv["roots"]:
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (inv["host"], r["tool"], r["root"], fmt(r.get("events", 0)), fmt(r.get("prompts", 0)),
                                                             fmt(r.get("sqlite_threads", 0)), fmt(r.get("sqlite_tokens_used", 0))))
    L.append("")
    for inv in inventories:
        L.append("- **%s**: %s files, %.1f GB, %s lines, %s calls, %s JSON errors, %s Codex replayed token events skipped, %s duplicate events skipped, %ss" % (
            inv["host"], fmt(inv["files"]), inv["bytes"] / 1e9, fmt(inv["lines"]), fmt(inv["events"]), fmt(inv["json_errors"]),
            fmt(inv["codex_replay_skipped"]), fmt(inv["dedup_skipped"]), inv["seconds"]))
    L.append("")
    with _private_open(os.path.join(a.out_dir, "SUMMARY.md"), "w") as f:
        f.write("\n".join(L))
    with _private_open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump({
            "generated": datetime.now(timezone.utc).isoformat(), "events": n_events, "sessions": len(by_sess), "prompts": len(prompts),
            "total": tot, "by_tool": by_tool, "by_tool_host": by_host, "by_model": by_model, "by_month_tool": by_month,
            "by_day_tool": by_day, "by_kind": by_kind, "by_entrypoint": by_entry,
            "by_project": sorted(by_cwd, key=lambda r: -r["total"])[:60],
            "top_sessions": sorted(by_sess, key=lambda r: -r["total"])[:60],
            "inventory": inventories,
            "costs": {"subscription_rows": sub_rows, "subscription_totals": sub_tot, "assumed_models": assumed_models,
                      "pricing": pricing},
            "accounts": {"registry": acct_reg, "rules": (AC or {}).get("rules", []), "source": account_source(AC), "by_account": by_account, "by_account_month": by_account_month,
                         "by_account_host": by_account_host, "by_plan": by_plan, "by_billing_month": by_billing_month,
                         "subscription_rows": acct_rows, "subscription_totals": acct_tot},
        }, f)
    sys.stderr.write("report written to %s\n" % a.out_dir)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--host", required=True)
    s.add_argument("--claude-root", action="append")
    s.add_argument("--codex-root", action="append")
    s.add_argument("--copilot-root", action="append")
    s.add_argument("--opencode-db", action="append")
    s.add_argument("--openclaw-root", action="append")
    s.add_argument("--pi-root", action="append", help="pi coding agent sessions dir (~/.pi/agent/sessions); same format as OpenClaw")
    s.add_argument("--gemini-root", action="append", help="Gemini CLI data dir (default ~/.gemini/tmp)")
    s.add_argument("--qwen-root", action="append", help="Qwen Code history dir (~/.qwen/history)")
    s.add_argument("--cline-root", action="append", help="[tool=]<globalStorage dir> for cline, roo-code, kilo-code (tasks/<id>/ui_messages.json)")
    s.add_argument("--aider-root", action="append", help="directory tree to search for .aider.chat.history.md")
    s.add_argument("--kimi-root", action="append", help="Kimi Code data dir (~/.kimi or ~/.kimi-code)")
    s.add_argument("--vibe-root", action="append", help="Mistral Vibe home (~/.vibe)")
    s.add_argument("--continue-root", action="append", help="Continue home (~/.continue)")
    s.add_argument("--mini-swe-root", action="append", help="explicitly authorized mini-SWE trajectory file or dedicated trajectory/usage directory; disabled by default")
    s.add_argument("--goose-root", action="append", help="[source-id=]<sessions directory or database>: native Goose usage; metadata only, no source writes")
    s.add_argument("--generic-root", action="append", help="<tool>=<dir>: best-effort usage sniffing over JSON/JSONL (pi, codebuff, droid, amp, lmstudio, ...); the dir must be the tool's own directory, never a home, drive root or AppData/.config; credential-looking files are skipped")
    s.add_argument("--no-prompts", action="store_true", help="do not record prompt text: no prompts.<host>.jsonl is written and prompt-only history files are not opened (run_pipeline passes this unless the manifest sets capture_prompts: true)")
    s.add_argument("--out-dir", required=True)
    s.set_defaults(fn=cmd_scan)
    r = sub.add_parser("report")
    r.add_argument("--events", action="append", required=True)
    r.add_argument("--sessions", action="append")
    r.add_argument("--prompts", action="append")
    r.add_argument("--inventory", action="append")
    r.add_argument("--pricing", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "pricing.json"))
    r.add_argument("--accounts", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.json"))
    r.add_argument("--out-dir", required=True)
    r.set_defaults(fn=cmd_report)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
