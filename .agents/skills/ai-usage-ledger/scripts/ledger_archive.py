#!/usr/bin/env python3
"""
ledger_archive.py - keep the raw agent logs themselves, not just the numbers derived from them.

Harness-agnostic by construction: the archive does not know what a Codex rollout or a Cline task folder is. It
archives every source file the scanners actually read (the `src` on each event and the `file` on each session,
whatever the tool), plus the tools' own counters found next to those files (stats-cache.json, state_5.sqlite,
history.jsonl). A new parser therefore gets archived automatically.

Layout:  <archive>/<host>/<path with the drive or share prefix folded in>[.gz]
Index:   <archive>/index.sqlite  (files: host, path, size, mtime, sha256, archived_at, versions)

Append-only: a file is copied when it is new or has grown/changed; earlier bytes are never rewritten by the
tools (their logs are append-only), so the latest copy is a superset. Nothing is deleted here.

    python3 ledger_archive.py --archive ~/.ai-usage-ledger/archive status
    python3 ledger_archive.py --archive ... list [--host h] [--grep-path codex]
    python3 ledger_archive.py --archive ... grep "pattern" [--host h] [--since 2026-08-01] [--limit 50]
    python3 ledger_archive.py --archive ... restore --host h --to /tmp/restored [--match sessions/2026/08]

Boundaries: host names are plain identifiers, every source path is validated (absolute, no control characters,
no '..'), every destination is checked to stay inside the archive root after symlink resolution, and remote
hosts are reached with fixed commands that read NUL-delimited file lists on stdin (no remote shell script is
ever composed from paths). The archive directory and index are owner-only. Credential-looking files (auth.json,
.credentials.json, credentials.json, *token*.json, *.pem, *.key, .env, anything under .ssh/.aws/.gnupg and the
rest of safety.is_credential_file) are excluded by one predicate on every path: local, WSL share, SSH, and again
when restoring; the index refuses such rows outright, so a scanner that referenced one cannot get it archived.

Standard library only.
"""
import argparse
import glob
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safety  # noqa: E402

COUNTER_FILES = ("stats-cache.json", "state_5.sqlite", "history.jsonl", "session-store.db", "auth.json.NEVER")  # auth files are never archived


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rel_path(path):
    """Fold a native path into an archive-relative path: C:\\Users\\x -> C/Users/x ; //wsl$/Ubuntu/home/x -> home/x ; /home/x -> home/x."""
    p = path.replace("\\", "/")
    m = re.match(r"^//wsl\$/[^/]+/(.*)$", p)
    if m:
        return m.group(1)
    m = re.match(r"^//([^/]+)/(.*)$", p)  # other UNC shares: keep the server name
    if m:
        return "unc-%s/%s" % (m.group(1), m.group(2))
    m = re.match(r"^([A-Za-z]):/(.*)$", p)
    if m:
        p = "%s/%s" % (m.group(1).upper(), m.group(2))
    return safety.safe_relative(p)  # refuses '..' components and empty results


def collect_sources(scans_dir, host_name):
    """Every distinct source file the scanners read for one host, plus counters beside the roots."""
    srcs = set()
    credential_like = set()
    d = os.path.join(scans_dir, host_name)
    for pat in ("events.*.jsonl", "sessions.*.jsonl"):
        for p in glob.glob(os.path.join(d, pat)):
            with open(p, "rb") as fh:
                for raw in fh:
                    try:
                        row = json.loads(raw)
                    except Exception:
                        continue
                    s = row.get("src") or row.get("file")
                    if s:
                        if safety.is_credential_file(s):  # a scanner may reference one; the archive never copies it
                            credential_like.add(str(s))
                            continue
                        try:
                            srcs.add(safety.check_source_path(s))
                        except SystemExit as ex:  # scan output is data, not trusted: skip anything that is not a plain absolute path
                            sys.stderr.write("archive: skipped %s\n" % safety.clean_for_terminal(str(ex), limit=300))
    if credential_like:
        sys.stderr.write("archive: %s: %d credential-like source path(s) excluded from the archive\n" % (host_name, len(credential_like)))
    roots = set()
    for p in glob.glob(os.path.join(d, "inventory.*.json")):
        try:
            inv = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        for r in inv.get("roots", []):
            if r.get("root"):
                roots.add(r["root"])
    return srcs, roots


class Archive:
    def __init__(self, path, compress=True):
        self.path = path
        self.compress = compress
        marker = os.path.join(path, ".ai-usage-ledger-archive")
        if os.path.isdir(path) and os.listdir(path) and not os.path.exists(marker) and not self._is_legacy_archive(path):
            raise safety.UnsafeValue("archive directory %s already holds other files; the archive needs a dedicated directory (it is what `remove everything` deletes)" % path)
        safety.private_dir(path)
        if not os.path.exists(marker):
            safety.write_private(marker, "This directory is owned by the AI usage ledger's raw-log archive. Delete the whole directory to remove the archive.\n")
        self.db = sqlite3.connect(os.path.join(path, "index.sqlite"))
        safety.private_file(os.path.join(path, "index.sqlite"))
        self.db.execute("CREATE TABLE IF NOT EXISTS files (host TEXT, path TEXT, rel TEXT, size INTEGER, mtime REAL, sha256 TEXT, archived_at TEXT, versions INTEGER DEFAULT 1, PRIMARY KEY (host, path))")
        self.db.execute("CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY AUTOINCREMENT, host TEXT, started_at TEXT, finished_at TEXT, files_new INTEGER, files_updated INTEGER, bytes INTEGER, note TEXT)")
        self.db.commit()

    @staticmethod
    def _is_legacy_archive(path):
        """An unmarked directory counts as one of our archives only if its index has our schema and every other
        entry is a host directory with a plain name; anything else could be someone's data and is refused."""
        idx = os.path.join(path, "index.sqlite")
        if not os.path.isfile(idx):
            return False
        try:
            from urllib.parse import quote
            db = sqlite3.connect("file:%s?mode=ro" % quote(idx.replace("\\", "/"), safe="/:"), uri=True)
            kinds = {r[0]: r[1] for r in db.execute("SELECT name, type FROM sqlite_master WHERE name IN ('files', 'runs')")}
            files_cols = {r[1] for r in db.execute("PRAGMA table_info(files)")}
            runs_cols = {r[1] for r in db.execute("PRAGMA table_info(runs)")}
            db.close()
        except sqlite3.Error:
            return False
        if kinds.get("files") != "table" or kinds.get("runs") != "table":  # a view with our columns is not our index
            return False
        if not {"host", "path", "rel", "size", "mtime", "sha256", "archived_at", "versions"} <= files_cols:
            return False
        if not {"id", "host", "started_at", "finished_at", "files_new", "files_updated", "bytes", "note"} <= runs_cols:
            return False
        for name in os.listdir(path):
            if name in ("index.sqlite", "index.sqlite-wal", "index.sqlite-shm", "index.sqlite-journal"):
                continue
            if not (os.path.isdir(os.path.join(path, name)) and safety.HOST_NAME_RE.match(name)):
                return False
        return True

    # ---- helpers --------------------------------------------------------------
    def _known(self, host):
        return {row[0]: (row[1], row[2]) for row in self.db.execute("SELECT path, size, mtime FROM files WHERE host=?", (host,))}

    def dest_for(self, host, path):
        safety.check_host_name(host)
        rel = rel_path(path)
        dest = os.path.join(self.path, host, rel + (".gz" if self.compress else ""))
        return dest, rel

    def _checked_dest(self, host, path):
        """Destination inside the archive root, verified after creating (and resolving) its parent directory."""
        dest, rel = self.dest_for(host, path)
        safety.private_dir(os.path.dirname(dest))
        if not safety.contained(self.path, dest):
            raise safety.UnsafeValue("archive destination escapes the archive root: %r" % path[:80])
        return dest, rel

    def _write(self, host, path, data, size, mtime, sha, existed):
        if safety.is_credential_file(path):  # the index refuses credential-like rows whatever code path produced them
            raise safety.UnsafeValue("refusing to archive a credential-like file: %r" % str(path)[:80])
        dest, rel = self._checked_dest(host, path)
        tmp = dest + ".part"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        if self.compress:
            with gzip.GzipFile(fileobj=os.fdopen(fd, "wb"), mode="wb", compresslevel=6) as fh:
                fh.write(data)
        else:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
        os.replace(tmp, dest)
        safety.private_file(dest)
        if existed:
            self.db.execute("UPDATE files SET size=?, mtime=?, sha256=?, archived_at=?, versions=versions+1, rel=? WHERE host=? AND path=?", (size, mtime, sha, now(), rel, host, path))
        else:
            self.db.execute("INSERT INTO files (host, path, rel, size, mtime, sha256, archived_at) VALUES (?,?,?,?,?,?,?)", (host, path, rel, size, mtime, sha, now()))

    # ---- local / share / wsl-share -------------------------------------------
    def archive_local(self, host, paths, prefix="", log=print):
        """paths are native paths on that host; prefix (e.g. //wsl$/Ubuntu) makes them readable here."""
        safety.check_host_name(host)
        known = self._known(host)
        new = upd = nbytes = creds = 0
        started = now()
        for p in sorted(paths):
            if safety.is_credential_file(p):
                creds += 1
                continue
            try:
                p = safety.check_source_path(p)
            except SystemExit as ex:
                log("  skip: %s" % safety.clean_for_terminal(str(ex), limit=300))
                continue
            local = (prefix.rstrip("/\\") + p) if prefix and not p.startswith(prefix) else p
            try:
                st = os.stat(local)
            except OSError:
                continue
            if not os.path.isfile(local):
                continue
            prev = known.get(p)
            if prev and prev[0] == st.st_size and abs(prev[1] - st.st_mtime) < 1:
                continue
            try:
                with open(local, "rb") as fh:
                    data = fh.read()
            except OSError as ex:
                log("  skip %s: %s" % (safety.clean_for_terminal(p, limit=300), safety.clean_for_terminal(str(ex), limit=300)))
                continue
            sha = hashlib.sha256(data).hexdigest()
            self._write(host, p, data, st.st_size, st.st_mtime, sha, existed=prev is not None)
            nbytes += st.st_size
            if prev:
                upd += 1
            else:
                new += 1
            if (new + upd) % 200 == 0:
                self.db.commit()
                log("  %s: %d new, %d updated, %.2f GB" % (host, new, upd, nbytes / 1e9))
        if creds:
            log("  %s: %d credential-like path(s) excluded from the archive" % (host, creds))
        self.db.execute("INSERT INTO runs (host, started_at, finished_at, files_new, files_updated, bytes) VALUES (?,?,?,?,?,?)", (host, started, now(), new, upd, nbytes))
        self.db.commit()
        return new, upd, nbytes

    # ---- ssh ------------------------------------------------------------------
    # fixed remote commands: paths never enter the command line; they arrive NUL-delimited on stdin
    REMOTE_STAT = "xargs -0 -r stat -c '%s %Y %n' -- 2>/dev/null"  # constant; missing files are simply absent from the output
    REMOTE_TAR = "tar czf - --null -T -"

    def archive_ssh(self, host, ssh_cfg, paths, log=print):
        """Pull the listed files in one tar stream; the remote side needs tar, xargs, stat and ssh access only.

        ssh_cfg is the manifest host entry (validated by safety.validate_ssh_host) or a plain target string."""
        safety.check_host_name(host)
        cfg = ssh_cfg if isinstance(ssh_cfg, dict) else {"ssh": ssh_cfg}
        target, _, _ = safety.validate_ssh_host(cfg)
        known = self._known(host)
        wanted = []
        creds = 0
        for p in sorted(paths):
            if safety.is_credential_file(p):  # same predicate as the local path: never asked for, never transferred
                creds += 1
                continue
            try:
                p = safety.check_source_path(p, "remote source path")
            except SystemExit as ex:
                log("  skip: %s" % safety.clean_for_terminal(str(ex), limit=300))
                continue
            if not safety.REMOTE_PATH_RE.match(p) and not re.match(r"^/[^\x00-\x1f\x7f]+$", p):
                log("  skip: not a plain absolute path: %r" % p[:80])
                continue
            wanted.append(p)
        if creds:
            log("  %s: %d credential-like path(s) excluded from the archive" % (host, creds))
        if not wanted:
            return 0, 0, 0
        # size+mtime first so unchanged files are not transferred (bytes mode: no CRLF translation on Windows)
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "--", target, self.REMOTE_STAT], input=("\0".join(wanted) + "\0").encode("utf-8"), capture_output=True)
        if r.returncode not in (0, 123):  # 123: xargs ran but some files did not exist, which is expected for optional counters
            log("  ssh stat failed for %s: %s" % (host, safety.clean_for_terminal(r.stderr.decode("utf-8", "replace")[-300:], limit=300)))
        remote = {}
        for line in r.stdout.decode("utf-8", "replace").splitlines():
            parts = line.split(" ", 2)
            if len(parts) == 3:
                remote[parts[2]] = (int(parts[0]), float(parts[1]))
        todo = [p for p in wanted if p in remote and not (known.get(p) and known[p][0] == remote[p][0] and abs(known[p][1] - remote[p][1]) < 1)]
        if not todo:
            return 0, 0, 0
        started = now()
        proc = subprocess.Popen(["ssh", "-o", "BatchMode=yes", "--", target, self.REMOTE_TAR], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate(input=("\0".join(todo) + "\0").encode("utf-8"))
        if proc.returncode not in (0, 1):  # 1 = some files changed while reading; acceptable for append-only logs
            log("  ssh tar failed for %s: %s" % (host, safety.clean_for_terminal(err.decode("utf-8", "replace")[-300:], limit=300)))
            return 0, 0, 0
        new = upd = nbytes = 0
        with tarfile.open(fileobj=io.BytesIO(out), mode="r:gz") as tf:
            for m in tf:
                if not m.isfile():
                    continue
                p = "/" + m.name.lstrip("./") if not m.name.startswith("/") else m.name
                if p not in remote:  # only files we asked for, by their exact path
                    continue
                data = tf.extractfile(m).read()
                sha = hashlib.sha256(data).hexdigest()
                prev = known.get(p)
                size, mtime = remote.get(p, (len(data), m.mtime))
                self._write(host, p, data, size, mtime, sha, existed=prev is not None)
                nbytes += len(data)
                if prev:
                    upd += 1
                else:
                    new += 1
        self.db.execute("INSERT INTO runs (host, started_at, finished_at, files_new, files_updated, bytes) VALUES (?,?,?,?,?,?)", (host, started, now(), new, upd, nbytes))
        self.db.commit()
        return new, upd, nbytes

    # ---- reading back ----------------------------------------------------------
    def status(self):
        rows = self.db.execute("SELECT host, COUNT(*), SUM(size), MAX(archived_at) FROM files GROUP BY host ORDER BY host").fetchall()
        on_disk = 0
        for dp, _, fns in os.walk(self.path):
            for fn in fns:
                if fn != "index.sqlite":
                    on_disk += os.path.getsize(os.path.join(dp, fn))
        return {"hosts": [{"host": h, "files": n, "bytes_original": s or 0, "last_archived": la} for h, n, s, la in rows], "bytes_on_disk": on_disk, "path": self.path, "compressed": self.compress}

    def list(self, host=None, grep_path=None):
        q = "SELECT host, path, size, mtime, archived_at, versions FROM files"
        args = []
        if host:
            q += " WHERE host=?"
            args.append(host)
        for row in self.db.execute(q + " ORDER BY host, path", args):
            if grep_path and grep_path.lower() not in row[1].lower():
                continue
            if safety.is_credential_file(row[1]):  # a row archived before the exclusion existed is never listed, searched or restored
                continue
            yield {"host": row[0], "path": row[1], "size": row[2], "mtime": datetime.fromtimestamp(row[3]).isoformat(timespec="seconds"), "archived_at": row[4], "versions": row[5]}

    def purge_credential_rows(self):
        """Remove index rows and stored files that match the credential predicate. A row is dropped only once its
        file is confirmed gone in both storage modes; otherwise it stays so a later purge can retry.
        Returns (purged, unremovable)."""
        rows = [(h, p) for h, p in self.db.execute("SELECT host, path FROM files") if safety.is_credential_file(p)]
        purged = unremovable = 0
        for h, p in rows:
            try:
                safety.check_host_name(h)
                rel = rel_path(p)
            except SystemExit:
                unremovable += 1
                sys.stderr.write("archive: legacy row %r %r has an unsafe host or path; kept as unremovable (delete the archive directory to be rid of it)\n" % (h, p))
                continue
            candidates = [os.path.join(self.path, h, rel), os.path.join(self.path, h, rel + ".gz")]
            if not all(safety.contained(self.path, c) for c in candidates):
                unremovable += 1
                sys.stderr.write("archive: legacy row %r %r resolves outside the archive; kept as unremovable\n" % (h, p))
                continue
            ok = True
            for dest in candidates:
                if os.path.isfile(dest):
                    try:
                        os.remove(dest)
                    except OSError:
                        ok = False
            if ok and not any(os.path.isfile(c) for c in candidates):
                self.db.execute("DELETE FROM files WHERE host=? AND path=?", (h, p))
                purged += 1
            else:
                unremovable += 1
                sys.stderr.write("archive: could not remove credential-like file for %s %s; its index row is kept\n" % (h, p))
        self.db.commit()
        return purged, unremovable

    def open(self, host, path):
        dest, _ = self.dest_for(host, path)
        return gzip.open(dest, "rb") if self.compress else open(dest, "rb")

    def grep(self, pattern, host=None, since=None, until=None, path_filter=None, limit=100, context=160, ignore_case=True):
        """Search inside the archived logs. Dates come from a timestamp-looking field on the matching line when there is one."""
        rx = re.compile(pattern.encode("utf-8"), re.IGNORECASE if ignore_case else 0)
        ts_rx = re.compile(rb'"(?:timestamp|ts|created_at|createdAt|time)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}[^"]*)"?')
        n = 0
        for f in self.list(host):
            if path_filter and path_filter.lower() not in f["path"].lower():
                continue
            if since and f["mtime"][:10] < since:
                continue
            try:
                with self.open(f["host"], f["path"]) as fh:
                    for lineno, line in enumerate(fh, 1):
                        m = rx.search(line)
                        if not m:
                            continue
                        tm = ts_rx.search(line)
                        ts = tm.group(1).decode("utf-8", "replace")[:19] if tm else ""
                        if since and ts and ts[:10] < since:
                            continue
                        if until and ts and ts[:10] > until:
                            continue
                        a = max(0, m.start() - context // 2)
                        snippet = line[a:a + context].decode("utf-8", "replace").replace("\n", " ")
                        yield {"host": f["host"], "path": f["path"], "line": lineno, "ts": ts, "snippet": snippet}
                        n += 1
                        if n >= limit:
                            return
            except (OSError, EOFError) as ex:
                yield {"host": f["host"], "path": f["path"], "line": 0, "ts": "", "snippet": "unreadable: %s" % ex}

    def restore(self, host, to, match=None):
        """Decompress a host's files under `to`; index rows are re-validated and every destination is kept inside `to`."""
        safety.check_host_name(host)
        safety.private_dir(to)
        n = creds = 0
        for f in self.list(host, match):
            if safety.is_credential_file(f["path"]):  # an index written before this rule may still hold one; never put it back on disk
                creds += 1
                continue
            try:
                rel = rel_path(safety.check_source_path(f["path"]))
            except SystemExit as ex:
                sys.stderr.write("restore: skipped %s\n" % safety.clean_for_terminal(str(ex), limit=300))
                continue
            dest = os.path.join(to, host, rel)
            safety.private_dir(os.path.dirname(dest))
            if not safety.contained(to, dest):
                sys.stderr.write("restore: refused destination outside %s for %r\n" % (to, f["path"]))
                continue
            src_path, _ = self.dest_for(host, f["path"])
            if not safety.contained(self.path, src_path):
                continue
            with self.open(host, f["path"]) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
            safety.private_file(dest)
            n += 1
        if creds:
            sys.stderr.write("restore: %d credential-like index row(s) skipped\n" % creds)
        return n

    def close(self):
        self.db.close()


def archive_from_scans(archive, hosts, scans_dir, log=print):
    """Archive every source the last scan touched, per host, using the host kind from the manifest."""
    summary = {}
    for h in hosts:
        name = h["name"]
        srcs, roots = collect_sources(scans_dir, name)
        for r in roots:  # counters that sit beside the roots
            for fn in COUNTER_FILES:
                if fn.endswith(".NEVER"):
                    continue
                srcs.add(os.path.join(r, fn).replace("\\", "/") if "/" in r else os.path.join(r, fn))
        if not srcs:
            continue
        t0 = time.time()
        kind = h.get("kind", "local")
        if kind == "ssh":
            res = archive.archive_ssh(name, h, srcs, log)
        elif kind == "wsl":
            share = h.get("share_fallback") or ("//wsl$/%s" % h.get("distro", "Ubuntu"))
            res = archive.archive_local(name, srcs, prefix=share, log=log)
        else:
            res = archive.archive_local(name, srcs, log=log)
        summary[name] = {"new": res[0], "updated": res[1], "bytes": res[2], "seconds": round(time.time() - t0, 1)}
        log("archive %s: %d new, %d updated, %.2f GB in %.0fs" % (name, res[0], res[1], res[2] / 1e9, time.time() - t0))
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", required=True, help="archive directory")
    ap.add_argument("--no-compress", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    ls = sub.add_parser("list")
    ls.add_argument("--host")
    ls.add_argument("--grep-path")
    g = sub.add_parser("grep")
    g.add_argument("pattern")
    g.add_argument("--host")
    g.add_argument("--since")
    g.add_argument("--until")
    g.add_argument("--path", dest="path_filter")
    g.add_argument("--limit", type=int, default=100)
    g.add_argument("--json", action="store_true")
    rs = sub.add_parser("restore")
    rs.add_argument("--host", required=True)
    rs.add_argument("--to", required=True)
    rs.add_argument("--match")
    a = ap.parse_args()
    ar = Archive(a.archive, compress=not a.no_compress)
    if a.cmd == "status":
        purged, unremovable = ar.purge_credential_rows()  # purge first so the snapshot describes the archive as it is now
        st = ar.status()
        st["credential_rows_purged"] = purged
        st["credential_rows_unremovable"] = unremovable
        print(json.dumps(st, indent=2))
    elif a.cmd == "list":
        for f in ar.list(a.host, a.grep_path):
            print("%-14s %10d  %s  v%d  %s" % (f["host"], f["size"], f["mtime"], f["versions"], f["path"]))
    elif a.cmd == "grep":
        for hit in ar.grep(a.pattern, a.host, a.since, a.until, a.path_filter, a.limit):
            if a.json:
                print(json.dumps(hit))
            else:
                print("%s  %s:%d  %s\n    %s" % (hit["ts"] or "----------T--:--:--", hit["path"], hit["line"], hit["host"], hit["snippet"]))
    elif a.cmd == "restore":
        print("restored %d files under %s" % (ar.restore(a.host, a.to, a.match), a.to))
    ar.close()


if __name__ == "__main__":
    sys.exit(main())
