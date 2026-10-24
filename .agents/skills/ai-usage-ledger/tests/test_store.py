#!/usr/bin/env python3
"""
Store, onboarding and end-to-end `ledger run` checks on the synthetic fixtures.

    python3 tests/test_store.py     # prints STORE OK on success

Covers: every backend (sqlite, json, csv) ingests the fixture scan once and skips it entirely the second
time; exported events reproduce the scanner totals; `ledger.py init --yes` writes a config, manifest and
accounts draft without prompting; `ledger.py run --no-detect` scans the fixture host into the store and
renders the dashboard and study; a second run adds nothing; prompt text stays out of the store until `prompts.capture=y`
is set (then the fixture prompts are captured); `status` and `export` work; `run --anonymize`
produces a copy with no real host, path or account label in it; `schedule install --dry-run` prints the
platform command without installing; every catalog template renders with no ledger placeholder left.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HERE)
import ledger_store  # noqa: E402
import make_fixtures  # noqa: E402

OUT = os.path.join(HERE, "out")
FX = os.path.join(HERE, "fixtures")


def totals(events):
    t = {}
    for e in events:
        a = t.setdefault(e["tool"], [0, 0])
        a[0] += 1
        a[1] += int(e["total"])
    return t


def check_backends(scan_dir):
    ev = os.path.join(scan_dir, "events.fixture.jsonl")
    base = totals(json.loads(line) for line in open(ev, encoding="utf-8"))
    ok = True
    for kind in ("sqlite", "json", "csv"):
        path = os.path.join(OUT, "store-" + kind + (".sqlite" if kind == "sqlite" else ""))
        shutil.rmtree(path, ignore_errors=True) if os.path.isdir(path) else (os.remove(path) if os.path.exists(path) else None)
        st = ledger_store.Store.open(kind, path)
        a1, s1 = st.ingest_events_file(ev)
        st.ingest_sessions_file(os.path.join(scan_dir, "sessions.fixture.jsonl"))
        st.ingest_prompts_file(os.path.join(scan_dir, "prompts.fixture.jsonl"))
        a2, s2 = st.ingest_events_file(ev)  # same scan again: everything must be skipped
        st.close()
        st = ledger_store.Store.open(kind, path)  # reopen: the id index must persist
        a3, s3 = st.ingest_events_file(ev)
        got = totals(st.iter_events())
        st.set_pref("brand", {"name": "Test"})
        pref = st.get_pref("brand")
        counts = st.counts()
        st.close()
        n = sum(v[0] for v in base.values())
        good = a1 == n and s1 == 0 and a2 == 0 and s2 == n and a3 == 0 and s3 == n and got == base and pref == {"name": "Test"} and counts["events"] == n
        print("%-7s first %d/%d  second %d/%d  reopened %d/%d  totals %s  prefs %s  %s" % (kind, a1, s1, a2, s2, a3, s3, "match" if got == base else "DIFFER", "ok" if pref else "bad", "OK" if good else "FAIL"))
        ok = ok and good
    return ok


def run(cmd, env=None, check=True):
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.stdout.write(r.stdout[-3000:])
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit("command failed: %s" % " ".join(cmd))
    return r


def check_cli(scan_dir):
    home = os.path.join(OUT, "home")
    shutil.rmtree(home, ignore_errors=True)
    env = dict(os.environ, AI_USAGE_LEDGER_HOME=home)
    py = sys.executable
    ledger = os.path.join(SCRIPTS, "ledger.py")
    run([py, ledger, "init", "--yes", "--set", "store.kind=json", "--set", "brand.name=Fixture Co", "--set", "detect.wsl=n", "--set", "detect.all_profiles=n", "--set", "workdir=" + os.path.join(OUT, "cli-work"),
         "--set", "archive.raw_logs=y", "--set", "archive.path=" + os.path.join(OUT, "archive")], env=env)
    cfg = json.load(open(os.path.join(home, "config.json"), encoding="utf-8"))
    ok = cfg["store"]["kind"] == "json" and cfg["branding"]["name"] == "Fixture Co" and os.path.isfile(cfg["manifest_path"]) and os.path.isfile(cfg["accounts_path"]) and os.path.isfile(cfg["pricing_path"])
    print("init:    config %s, store %s, brand %s  %s" % (os.path.basename(home), cfg["store"]["kind"], cfg["branding"]["name"], "OK" if ok else "FAIL"))
    # point the manifest at the fixture host only (a real run would use the auto-detected hosts); every other key the
    # onboarding wrote (capture_prompts among them) is kept
    def point_manifest_at_fixture():
        m = json.load(open(cfg["manifest_path"], encoding="utf-8"))
        m["hosts"] = [{"name": "fixture", "kind": "local", "claude_roots": [os.path.join(FX, "claude")], "codex_roots": [os.path.join(FX, "codex")], "gemini_roots": [os.path.join(FX, "gemini")],
                       "cline_roots": ["cline=" + os.path.join(FX, "cline")], "aider_roots": [os.path.join(FX, "aider")], "kimi_roots": [os.path.join(FX, "kimi")], "vibe_roots": [os.path.join(FX, "vibe")],
                       "continue_roots": [os.path.join(FX, "continue")], "pi_roots": [os.path.join(FX, "pi")], "generic_roots": ["codebuff=" + os.path.join(FX, "generic")]}]
        json.dump(m, open(cfg["manifest_path"], "w", encoding="utf-8"), indent=2)
        return m
    m = point_manifest_at_fixture()
    shutil.copy(os.path.join(ROOT, "examples", "accounts.fixtures.json"), cfg["accounts_path"])
    r1 = run([py, ledger, "run", "--no-detect"], env=env)
    r2 = run([py, ledger, "run", "--no-detect"], env=env)
    st = ledger_store.Store.open("json", cfg["store"]["path"])
    counts = st.counts()
    last = st.last_run()
    st.close()
    # prompt text is an opt-in: the default onboarding leaves it off, so the scan writes no prompts file, the store
    # holds no prompt rows, the manifest says so, and the prompt presets explain instead of answering "0 rows"
    scan_prompts = os.path.join(cfg["workdir"], "scans", "fixture", "prompts.fixture.jsonl")
    qoff = run([py, ledger, "query", "prompts", "--grep", "do the thing", "--format", "json"], env=env)
    qoff2 = run([py, ledger, "query", "prompt-count"], env=env)
    inv_off = json.load(open(os.path.join(cfg["workdir"], "scans", "fixture", "inventory.fixture.json"), encoding="utf-8"))
    pgood = (counts["prompts"] == 0 and not os.path.exists(scan_prompts) and m.get("capture_prompts") is False and inv_off.get("prompts_captured") is False
             and qoff.returncode == 0 and "prompt capture is off" in qoff.stdout and "[" not in qoff.stdout and "prompt capture is off" in qoff2.stdout
             and os.path.getsize(os.path.join(cfg["workdir"], "compiled", "all_prompts.jsonl")) == 0)
    print("prompts off (default): store prompts %d, scan prompts file %s, manifest capture_prompts %s, query explains %s  %s" % (
        counts["prompts"], "absent" if not os.path.exists(scan_prompts) else "PRESENT", m.get("capture_prompts"), "prompt capture is off" in qoff.stdout, "OK" if pgood else "FAIL"))
    if not pgood:
        sys.stdout.write(qoff.stdout[-500:] + qoff.stderr[-500:] + r1.stdout[-800:])
    ok = ok and pgood
    n = sum(1 for _ in open(os.path.join(scan_dir, "events.fixture.jsonl"), encoding="utf-8"))
    dash = os.path.join(cfg["workdir"], "compiled", "agent-ledger.html")
    pkgs = [d for d in os.listdir(os.path.join(cfg["workdir"], "reports")) if d.endswith(".zip")] if os.path.isdir(os.path.join(cfg["workdir"], "reports")) else []
    good = counts["events"] == n and last and last["added"]["events"] == 0 and counts["runs"] == 2 and os.path.isfile(dash) and pkgs and "Fixture Co" in open(dash, encoding="utf-8").read()
    # raw-log archive: every source file the scanners read is archived once; the second run archives nothing new
    srcs = set()
    for fn in ("events.fixture.jsonl", "sessions.fixture.jsonl"):
        for line in open(os.path.join(scan_dir, fn), encoding="utf-8"):
            d = json.loads(line)
            if d.get("src") or d.get("file"):
                srcs.add(os.path.normcase(d.get("src") or d.get("file")))
    st = ledger_store.Store.open("json", cfg["store"]["path"])
    runs = []
    for line in open(os.path.join(cfg["store"]["path"], "runs.jsonl"), encoding="utf-8"):
        runs.append(json.loads(line))
    st.close()
    a1, a2 = (runs[0].get("archive") or {}).get("fixture", {}), (runs[1].get("archive") or {}).get("fixture", {})
    arch_dir = os.path.join(OUT, "archive", "fixture")
    n_files = sum(len(f) for _, _, f in os.walk(arch_dir)) if os.path.isdir(arch_dir) else 0
    agood = a1.get("new") == len(srcs) and a2.get("new", 0) == 0 and a2.get("updated", 0) == 0 and n_files == len(srcs)
    print("archive: %d sources, first run new=%s, second run new=%s updated=%s, files on disk %d  %s" % (len(srcs), a1.get("new"), a2.get("new"), a2.get("updated"), n_files, "OK" if agood else "FAIL"))
    good = good and agood
    print("run x2:  %d events in store (expected %d), second run added %s, runs %d, dashboard %s, package %s  %s" % (
        counts["events"], n, last["added"]["events"] if last else "?", counts["runs"], "yes" if os.path.isfile(dash) else "no", "yes" if pkgs else "no", "OK" if good else "FAIL"))
    if not good:
        sys.stdout.write(r1.stdout[-2000:] + r2.stdout[-2000:])
    ok = ok and bool(good)
    # opt in: the same preferences with prompts.capture=y; the regenerated manifest carries capture_prompts, the
    # scan writes the prompts file and the store ingests the fixture prompts (the later query checks rely on this)
    run([py, ledger, "init", "--yes", "--set", "prompts.capture=y"], env=env)
    m_on = point_manifest_at_fixture()
    r_on = run([py, ledger, "run", "--no-detect"], env=env)
    st = ledger_store.Store.open("json", cfg["store"]["path"])
    counts_on = st.counts()
    st.close()
    inv_on = json.load(open(os.path.join(cfg["workdir"], "scans", "fixture", "inventory.fixture.json"), encoding="utf-8"))
    ogood = (m_on.get("capture_prompts") is True and r_on.returncode == 0 and counts_on["prompts"] > 0 and os.path.isfile(scan_prompts) and os.path.getsize(scan_prompts) > 0
             and counts_on["events"] == n and inv_on.get("prompts_captured") is True)
    print("prompts on (opt-in): manifest capture_prompts %s, store prompts %d, scan prompts file %s, events still %d  %s" % (
        m_on.get("capture_prompts"), counts_on["prompts"], "present" if os.path.isfile(scan_prompts) else "ABSENT", counts_on["events"], "OK" if ogood else "FAIL"))
    if not ogood:
        sys.stdout.write(r_on.stdout[-1500:] + r_on.stderr[-800:])
    ok = ok and ogood
    s = run([py, ledger, "status"], env=env)
    good = "events" in s.stdout and "Fixture Co" in s.stdout and "prompt capture: on" in s.stdout
    print("status:  %s" % ("OK" if good else "FAIL\n" + s.stdout))
    ok = ok and good
    out_csv = os.path.join(OUT, "export.csv")
    e = run([py, ledger, "export", "--format", "csv", "--out", out_csv], env=env)
    rows = sum(1 for _ in open(out_csv, encoding="utf-8")) - 1
    good = rows == n and "wrote" in e.stdout
    print("export:  %d rows  %s" % (rows, "OK" if good else "FAIL"))
    ok = ok and good
    # anonymised copy: no fixture host name, no local path, no example e-mail anywhere in the anonymised tables
    r3 = run([py, ledger, "run", "--no-detect", "--no-scan", "--anonymize"], env=env)
    anon = os.path.join(cfg["workdir"], "anonymized")
    leaks = 0
    checked = 0
    for fn in ("all_events.csv", "all_sessions.csv", "summary.json", "SUMMARY.md"):
        p = os.path.join(anon, "compiled", fn)
        if os.path.isfile(p):
            checked += 1
            txt = open(p, encoding="utf-8", errors="replace").read()
            leaks += sum(txt.count(needle) for needle in ("fixture", "example@example.com", FX.replace("\\", "/"), FX))
    anon_pkgs = [d for d in os.listdir(os.path.join(anon, "reports")) if d.endswith(".zip")] if os.path.isdir(os.path.join(anon, "reports")) else []
    anon_rows = sum(1 for _ in open(os.path.join(anon, "compiled", "all_events.csv"), encoding="utf-8")) - 1 if os.path.isfile(os.path.join(anon, "compiled", "all_events.csv")) else 0
    src_kept = False
    try:
        src_kept = "_source" in json.load(open(os.path.join(anon, "accounts.json"), encoding="utf-8")) or "_source" not in json.load(open(cfg["accounts_path"], encoding="utf-8"))
    except Exception:
        pass
    good = checked == 4 and leaks == 0 and anon_rows == n and bool(anon_pkgs) and os.path.isfile(os.path.join(home, "anonymize-map.json")) and src_kept
    print("anonym:  %d files checked, %d leaks, %d rows, package %s, map %s  %s" % (checked, leaks, anon_rows, "yes" if anon_pkgs else "no", "yes" if os.path.isfile(os.path.join(home, "anonymize-map.json")) else "no", "OK" if good else "FAIL"))
    if not good:
        sys.stdout.write(r3.stdout[-2000:])
    ok = ok and good
    pc = run([py, ledger, "publish-check", anon], env=env, check=False)
    pc_good = pc.returncode == 0
    print("publish-check on the anonymised tree: %s" % ("OK" if pc_good else "FAIL\n" + pc.stdout[-800:]))
    ok = ok and pc_good
    e2 = run([py, ledger, "export", "--anonymize", "--format", "jsonl", "--out", os.path.join(OUT, "anon.jsonl")], env=env)
    txt = open(os.path.join(OUT, "anon.jsonl"), encoding="utf-8").read()
    good = "wrote %d" % n in e2.stdout and "fixture" not in txt and "src" not in txt and "host-" in txt
    print("anon export: %s" % ("OK" if good else "FAIL"))
    ok = ok and good
    # schedule: dry run only (never installs anything on the test machine)
    s0 = run([py, ledger, "schedule", "install", "--frequency", "weekly", "--time", "04:15", "--weekday", "fri", "--dry-run"], env=env, check=False)
    unconsented = s0.returncode == 3 and "Not installed" in s0.stdout
    c = run([py, ledger, "schedule", "consent", "--frequency", "weekly", "--time", "04:15", "--weekday", "fri"], env=env)
    rec = json.loads(c.stdout[c.stdout.rfind("{"):c.stdout.rfind("}") + 1])
    rec["approved_by"] = "test"
    json.dump(rec, open(os.path.join(home, "schedule-consent.json"), "w", encoding="utf-8"))
    s1 = run([py, ledger, "schedule", "install", "--frequency", "weekly", "--time", "04:15", "--weekday", "fri", "--dry-run"], env=env)
    s2 = run([py, ledger, "schedule", "remove", "--dry-run"], env=env)
    good = ("schtasks" in s1.stdout or "crontab" in s1.stdout) and ("04:15" in s1.stdout or "15 4" in s1.stdout) and ("FRI" in s1.stdout or "* * 5" in s1.stdout) and ("schtasks" in s2.stdout or "crontab" in s2.stdout)
    cfg2 = json.load(open(os.path.join(home, "config.json"), encoding="utf-8"))
    good = good and unconsented and cfg2.get("schedule", {}).get("frequency") == "none"  # dry run must not change the saved preference
    print("schedule dry-run: %s" % ("OK" if good else "FAIL\n" + s1.stdout + s2.stdout))
    ok = ok and good
    # documents: every template renders with no ledger placeholder left; user-only placeholders may remain
    user_only = {"contract_id", "billing_period", "previous_value", "corrected_value", "cause", "affected_documents"}
    import re
    idx = json.load(open(os.path.join(ROOT, "references", "template-index.json"), encoding="utf-8"))["templates"]
    bad = []
    for t in idx:
        outp = os.path.join(OUT, "docs", t["id"] + ".md")
        r = run([py, ledger, "doc", "--template", t["id"], "--out", outp, "--var", "prepared_for=Test Reader", "--var", "reference=T-1"], env=env, check=False)
        if r.returncode != 0 or not os.path.isfile(outp):
            bad.append((t["id"], "render failed: " + r.stderr[-300:]))
            continue
        left = set(re.findall(r"\{([a-z_]+)\}", open(outp, encoding="utf-8").read())) - user_only
        if left:
            bad.append((t["id"], "unfilled: " + ", ".join(sorted(left))))
        if not os.path.isfile(outp[:-3] + ".html"):
            bad.append((t["id"], "no html"))
    anon_doc = run([py, ledger, "doc", "--template", "executive-summary", "--anonymize", "--out", os.path.join(OUT, "docs", "anon.md")], env=env, check=False)
    atxt = open(os.path.join(OUT, "docs", "anon.md"), encoding="utf-8").read() if os.path.isfile(os.path.join(OUT, "docs", "anon.md")) else ""
    if anon_doc.returncode != 0 or "fixture" in atxt or "Anonymised" not in atxt:
        bad.append(("executive-summary --anonymize", "leak or failure"))
    # queries: presets, free SQL, prompts and archived raw logs
    q1 = run([py, ledger, "query", "by-tool", "--format", "json"], env=env)
    q2 = run([py, ledger, "query", "totals", "--since", "2026-04-01", "--until", "2026-04-30", "--format", "json"], env=env)
    q3 = run([py, ledger, "query", "sql", "SELECT COUNT(*) AS c FROM events WHERE tool='codex'", "--format", "json"], env=env)
    q4 = run([py, ledger, "query", "prompts", "--grep", "do the thing", "--format", "json"], env=env)
    q5 = run([py, ledger, "query", "logs", "do the thing", "--format", "json"], env=env)
    q6 = run([py, ledger, "query", "by-account", "--format", "json"], env=env)
    q7 = run([py, ledger, "archive", "status"], env=env)
    try:
        j1, j2, j3, j4, j5, j6 = (json.loads(x.stdout) for x in (q1, q2, q3, q4, q5, q6))
        qgood = len(j1) == 10 and j2[0]["calls"] == 2 and j3[0]["c"] == 3 and len(j4) == 1 and len(j5) >= 1 and any(r["account"] == "codex:example" for r in j6) and '"files"' in q7.stdout
    except Exception as ex:
        qgood = False
        print("query parse error:", ex, q1.stdout[:200], q2.stdout[:200], q6.stdout[:200], q6.stderr[-300:])
    print("query:   by-tool %s rows, totals(April) %s, sql %s, prompts grep %s, logs grep %s, by-account %s  %s" % (
        len(j1) if qgood else "?", j2[0]["calls"] if qgood else "?", j3[0]["c"] if qgood else "?", len(j4) if qgood else "?", len(j5) if qgood else "?", "ok" if qgood else "?", "OK" if qgood else "FAIL"))
    if not qgood:
        sys.stdout.write("".join(x.stderr[-400:] for x in (q1, q2, q3, q4, q5, q6, q7)))
    ok = ok and qgood
    # tool filter: a run that skips codex and claude-code scans everything else only
    rf = run([py, ledger, "run", "--no-detect", "--skip-tools", "codex,claude-code"], env=env, check=False)
    ev = os.path.join(cfg["workdir"], "scans", "fixture", "events.fixture.jsonl")
    tools_seen = {json.loads(line)["tool"] for line in open(ev, encoding="utf-8")} if os.path.isfile(ev) else set()
    fgood = rf.returncode == 0 and tools_seen and not ({"codex", "claude-code"} & tools_seen) and "aider" in tools_seen
    print("skip-tools: scanned %s  %s" % (",".join(sorted(tools_seen)), "OK" if fgood else "FAIL\n" + rf.stdout[-800:] + rf.stderr[-800:]))
    ok = ok and fgood
    lst = run([py, ledger, "doc", "--list"], env=env)
    if len([x for x in lst.stdout.splitlines() if x.strip()]) != len(idx):
        bad.append(("--list", "count mismatch"))
    good = not bad
    print("documents: %d templates rendered%s  %s" % (len(idx), "" if good else "; " + "; ".join("%s (%s)" % b for b in bad), "OK" if good else "FAIL"))
    ok = ok and good
    return ok


def main():
    make_fixtures.build()
    scan_dir = os.path.join(OUT, "scan")
    shutil.rmtree(scan_dir, ignore_errors=True)
    run([sys.executable, os.path.join(SCRIPTS, "compile_ai_logs.py"), "scan", "--host", "fixture", "--out-dir", scan_dir,
         "--claude-root", os.path.join(FX, "claude"), "--codex-root", os.path.join(FX, "codex"), "--gemini-root", os.path.join(FX, "gemini"),
         "--cline-root", "cline=" + os.path.join(FX, "cline"), "--aider-root", os.path.join(FX, "aider"), "--kimi-root", os.path.join(FX, "kimi"),
         "--vibe-root", os.path.join(FX, "vibe"), "--continue-root", os.path.join(FX, "continue"), "--pi-root", os.path.join(FX, "pi"),
         "--generic-root", "codebuff=" + os.path.join(FX, "generic")])
    ok = check_backends(scan_dir)
    ok = check_cli(scan_dir) and ok
    print("STORE OK" if ok else "STORE CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
