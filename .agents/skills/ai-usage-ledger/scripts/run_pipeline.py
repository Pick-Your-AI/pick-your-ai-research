#!/usr/bin/env python3
"""
run_pipeline.py - one command from raw agent logs to the ledger package.

    python run_pipeline.py --manifest manifest.json
    python run_pipeline.py --manifest manifest.json --only report,analyze,build   # skip scans
    python run_pipeline.py --manifest manifest.json --hosts laptop,server         # scan a subset

The manifest (templates/manifest.example.json) lists hosts and where their logs are.
Host kinds:
  local   run compile_ai_logs.py here with the given roots
  wsl     run it inside a WSL distro (wsl.exe -d <distro>); falls back to the \\wsl$ share if the
          service refuses the call
  ssh     copy the scanner to the remote with scp, run it with the remote python, scp results back
  share   scan a mounted/UNC path from this machine (slow but dependable)

Every step is idempotent; outputs land in <workdir>/scans, <workdir>/compiled and <workdir>/reports.
Standard library only.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SCANNER = os.path.join(HERE, "compile_ai_logs.py")
sys.path.insert(0, HERE)
import safety  # noqa: E402


def log(msg):
    # messages embed paths, exceptions and remote (ssh / wsl) output: strip escape sequences and controls before the terminal sees them
    sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), safety.clean_for_terminal(msg)))


def _captured_tail(r, limit=600):
    """The last part of a subprocess' captured stderr (or stdout) as clean printable text; '' when nothing was captured."""
    for raw in (r.stderr, r.stdout):
        if not raw:
            continue
        text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)
        return safety.clean_for_terminal(text.strip()[-limit:], limit=limit)
    return ""


def run(cmd, check=True, **kw):
    """Argument lists only; a shell is never involved on the local side."""
    if isinstance(cmd, str):
        raise SystemExit("internal error: commands must be argument lists")
    log("$ " + " ".join(shlex.quote(c) for c in cmd))
    r = subprocess.run(cmd, **kw)
    if check and r.returncode != 0:
        tail = _captured_tail(r)
        raise SystemExit("command failed (%d): %s%s" % (r.returncode, safety.clean_for_terminal(" ".join(shlex.quote(c) for c in cmd), limit=1000), ("\n" + tail) if tail else ""))
    return r


def scan_args(host, capture_prompts=False):
    """Translate a manifest host entry into compile_ai_logs.py scan arguments. Prompt text is recorded only when the
    manifest says capture_prompts: true (ledger.py writes it from the prompts.capture preference); every other scan,
    on every host kind, runs with --no-prompts."""
    args = ["scan", "--host", safety.check_path(host["name"], "host name")]
    if not capture_prompts:
        args.append("--no-prompts")
    for key in ("claude_roots", "codex_roots", "copilot_roots", "opencode_dbs", "openclaw_roots", "gemini_roots", "qwen_roots", "aider_roots", "kimi_roots",
                "vibe_roots", "continue_roots", "pi_roots", "mini_swe_roots", "goose_roots", "cline_roots", "generic_roots"):
        for r in host.get(key, []):
            safety.check_path(r, key)
    for r in host.get("claude_roots", []):
        args += ["--claude-root", r]
    for r in host.get("codex_roots", []):
        args += ["--codex-root", r]
    for r in host.get("copilot_roots", []):
        args += ["--copilot-root", r]
    for r in host.get("opencode_dbs", []):
        args += ["--opencode-db", r]
    for r in host.get("openclaw_roots", []):
        args += ["--openclaw-root", r]
    for key, flag in (("gemini_roots", "--gemini-root"), ("qwen_roots", "--qwen-root"), ("aider_roots", "--aider-root"), ("kimi_roots", "--kimi-root"),
                      ("vibe_roots", "--vibe-root"), ("continue_roots", "--continue-root"), ("pi_roots", "--pi-root"), ("mini_swe_roots", "--mini-swe-root"), ("goose_roots", "--goose-root")):
        for r in host.get(key, []):
            args += [flag, r]
    for r in host.get("cline_roots", []):      # "cline=<dir>", "roo-code=<dir>", "kilo-code=<dir>"
        args += ["--cline-root", r]
    for r in host.get("generic_roots", []):    # "<tool>=<dir>"
        args += ["--generic-root", r]
    return args


def scan_host(host, scans_dir, python="python", capture_prompts=False):
    kind = host.get("kind", "local")
    name = host["name"]
    out_dir = os.path.join(scans_dir, name)
    safety.private_dir(out_dir)  # scan artifacts carry prompts, project paths and session ids
    if kind == "local" or kind == "share":
        run([safety.validate_local_python(host, python), SCANNER] + scan_args(host, capture_prompts) + ["--out-dir", out_dir])
    elif kind == "wsl":
        distro, wsl_python = safety.validate_wsl_host(host)
        # the scanner and the output dir must be visible from inside the distro
        win_out = os.path.abspath(out_dir)
        wsl_out = "/mnt/" + win_out[0].lower() + win_out[2:].replace("\\", "/")
        wsl_scanner = "/mnt/" + SCANNER[0].lower() + SCANNER[2:].replace("\\", "/")
        cmd = " ".join([shlex.quote(wsl_python), shlex.quote(wsl_scanner)] + [shlex.quote(x) for x in scan_args(host, capture_prompts)] + ["--out-dir", shlex.quote(wsl_out)])
        # the WSL service intermittently refuses calls under load (Wsl/Service/0x8007274c); retry before falling back,
        # because a scan over the \wsl$ share can silently miss files (9P errors) and is four times slower
        # a previous run's outputs must not be mistaken for this run's: remove them before the first attempt, so
        # "the inventory file exists" means the scanner just wrote it
        inv_path = os.path.join(out_dir, "inventory.%s.json" % name)
        for fn in os.listdir(out_dir):
            if fn.startswith(("inventory.", "events.", "sessions.", "prompts.")) and (fn.endswith(".json") or fn.endswith(".jsonl")):
                os.remove(os.path.join(out_dir, fn))
        done = False
        for attempt in range(1, int(host.get("wsl_attempts", 3)) + 1):
            r = run(["wsl.exe", "-d", distro, "--", "bash", "-lc", cmd], check=False)
            done = r.returncode == 0 and os.path.isfile(inv_path)
            if done:
                break
            log("WSL scan attempt %d for %s failed (rc=%s)%s" % (attempt, name, r.returncode, "; retrying in 30 s" if attempt < int(host.get("wsl_attempts", 3)) else ""))
            if attempt < int(host.get("wsl_attempts", 3)):
                time.sleep(30)
        if not done:
            share = host.get("share_fallback")
            if not share:
                raise SystemExit("WSL scan failed for %s and no share_fallback given" % name)
            log("WSL service refused the call; falling back to the share %s (slower, and file counts can come up short: compare the inventory with a native `find` and rescan the host with `ledger.py run --hosts %s` once WSL responds)" % (share, name))
            alt = dict(host)
            for key in ("claude_roots", "codex_roots", "copilot_roots", "opencode_dbs", "openclaw_roots", "gemini_roots", "qwen_roots", "aider_roots", "kimi_roots", "vibe_roots", "continue_roots", "pi_roots", "mini_swe_roots"):
                alt[key] = [share.rstrip("/\\") + p for p in host.get(key, [])]
            for key in ("cline_roots", "generic_roots", "goose_roots"):
                alt[key] = [(x.split("=", 1)[0] + "=" + share.rstrip("/\\") + x.split("=", 1)[1]) if "=" in x else share.rstrip("/\\") + x for x in host.get(key, [])]
            # sqlite over a UNC share cannot be opened via URI; copy the opencode db locally first
            if alt.get("opencode_dbs"):
                copies = []
                for p in alt["opencode_dbs"]:
                    dst = os.path.join(out_dir, os.path.basename(p))
                    try:
                        safety.private_copy(p, dst)
                        copies.append(dst)
                    except OSError as ex:
                        log("could not copy %s: %s" % (p, ex))
                alt["opencode_dbs"] = copies
            run([python, SCANNER] + scan_args(alt, capture_prompts) + ["--out-dir", out_dir])
    elif kind == "ssh":
        # every remote-shell word is validated against a strict grammar and quoted; the target is checked so it
        # cannot smuggle ssh/scp options
        target, remote_tmp, remote_python = safety.validate_ssh_host(host)
        try:
            # owner-only staging (0700) before anything is written; the scanner tightens its own out dir and files
            run(["ssh", "-o", "BatchMode=yes", "--", target, "install -d -m 700 -- " + shlex.quote(remote_tmp)])
            run(["scp", "-q", "--", SCANNER, "%s:%s" % (target, shlex.quote(remote_tmp + "/compile_ai_logs.py"))])
            run(["scp", "-q", "--", os.path.join(HERE, "safety.py"), "%s:%s" % (target, shlex.quote(remote_tmp + "/safety.py"))])
            if host.get("mini_swe_roots"):
                run(["scp", "-q", "--", os.path.join(HERE, "mini_swe_usage.py"), "%s:%s" % (target, shlex.quote(remote_tmp + "/mini_swe_usage.py"))])
            run(["scp", "-q", "--", os.path.join(HERE, "goose_usage.py"), "%s:%s" % (target, shlex.quote(remote_tmp + "/goose_usage.py"))])
            cmd = " ".join([shlex.quote(remote_python), shlex.quote(remote_tmp + "/compile_ai_logs.py")] + [shlex.quote(x) for x in scan_args(host, capture_prompts)] + ["--out-dir", shlex.quote(remote_tmp + "/out")])
            run(["ssh", "-o", "BatchMode=yes", "--", target, cmd])
            run(["scp", "-q", "--", "%s:%s" % (target, shlex.quote(remote_tmp + "/out") + "/*"), out_dir])
        finally:
            # the staging dir holds the scanner, prompts and scanned data: remove it after retrieval, on success and failure alike
            run(["ssh", "-o", "BatchMode=yes", "--", target, "rm -rf -- " + shlex.quote(remote_tmp)], check=False)
    else:
        raise SystemExit("unknown host kind %r" % kind)
    # optional: stage Codex sqlite and Claude stats-cache for validation
    staged = {}
    for key, dst_name in (("codex_sqlite", "state_5.sqlite"), ("claude_stats_cache", "stats-cache.json")):
        src = host.get(key)
        if not src:
            continue
        dst = os.path.join(out_dir, dst_name)
        try:
            if kind == "ssh":
                target, _, _ = safety.validate_ssh_host(host)
                if not safety.REMOTE_PATH_RE.match(str(src)):
                    raise safety.UnsafeValue("%s on %s is not a plain absolute path: %r" % (key, name, src))
                run(["scp", "-q", "--", "%s:%s" % (target, shlex.quote(str(src))), dst])
            elif kind == "wsl" and not os.path.exists(src):
                share = host.get("share_fallback", "")
                shutil.copy(share.rstrip("/\\") + src, dst)
            else:
                safety.private_copy(src, dst)
            safety.private_file(dst)
            staged[key] = dst
        except Exception as ex:
            log("could not stage %s for %s: %s" % (key, name, ex))
    return staged


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--only", default="scan,report,analyze,build", help="comma list of steps: scan,report,analyze,build")
    ap.add_argument("--hosts", default=None, help="comma list of host names to scan (default all)")
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    safety.refuse_if_shared(a.manifest, "pipeline manifest")
    M = json.load(open(a.manifest, encoding="utf-8"))
    steps = set(a.only.split(","))
    mdir0 = os.path.dirname(os.path.abspath(a.manifest))
    work = os.path.abspath(os.path.join(mdir0, M.get("workdir", ".")))
    safety.private_dir(work)  # everything below the working directory holds scan and report data
    scans = os.path.join(work, "scans")
    compiled = os.path.join(work, "compiled")
    reports = os.path.join(work, "reports")
    date = M.get("snapshot_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pkg = os.path.join(reports, "%s_%s" % (M.get("package_prefix", "AI_Usage_Ledger"), date))
    for d in (scans, compiled, reports):
        safety.private_dir(d)  # compiled tables and reports embed project paths and account labels
    mdir = os.path.dirname(os.path.abspath(a.manifest))

    def rel(p):  # manifest-relative paths become absolute so every step can run from any cwd
        return os.path.abspath(os.path.join(mdir, p)) if p and not os.path.isabs(p) else p
    pricing = rel(M.get("pricing")) or os.path.join(HERE, "..", "templates", "pricing.json")
    accounts = rel(M.get("accounts"))
    config = rel(M.get("report_config"))
    for p in (pricing, accounts, config):
        safety.warn_if_writable(p, log)
    safety.check_path(work, "workdir")
    for h in M["hosts"]:  # root paths in the manifest are also manifest-relative when not absolute
        for key in ("claude_roots", "codex_roots", "copilot_roots", "opencode_dbs", "openclaw_roots", "gemini_roots", "qwen_roots", "aider_roots", "kimi_roots", "vibe_roots", "continue_roots", "pi_roots", "mini_swe_roots"):
            if h.get("kind", "local") in ("local", "share") and h.get(key):
                h[key] = [rel(x) for x in h[key]]
        for key in ("cline_roots", "generic_roots", "goose_roots"):
            if h.get("kind", "local") in ("local", "share") and h.get(key):
                h[key] = [(x.split("=", 1)[0] + "=" + rel(x.split("=", 1)[1])) if "=" in x else rel(x) for x in h[key]]
        for key in ("codex_sqlite", "claude_stats_cache"):
            if h.get("kind", "local") in ("local", "share") and h.get(key):
                h[key] = rel(h[key])
    tz = M.get("timezone", "UTC")
    hosts = M["hosts"]
    if a.hosts:
        want = set(a.hosts.split(","))
        hosts = [h for h in hosts if h["name"] in want]

    capture_prompts = M.get("capture_prompts") is True  # prompt text is an explicit opt-in (ledger.py prompts.capture)
    if "scan" in steps:
        for h in hosts:
            log("scanning %s (%s%s)" % (h["name"], h.get("kind", "local"), "" if capture_prompts else ", prompts off"))
            scan_host(h, scans, a.python, capture_prompts)

    if "report" in steps:
        cmd = [a.python, SCANNER, "report", "--out-dir", compiled, "--pricing", pricing]
        if accounts:
            cmd += ["--accounts", accounts]
        for pat in ("events.*.jsonl", "sessions.*.jsonl", "prompts.*.jsonl", "inventory.*.json"):
            flag = {"events.*.jsonl": "--events", "sessions.*.jsonl": "--sessions", "prompts.*.jsonl": "--prompts", "inventory.*.json": "--inventory"}[pat]
            cmd += [flag, os.path.join(scans, "*", pat)]
        run(cmd)

    if "analyze" in steps:
        cmd = [a.python, os.path.join(HERE, "analyze_events.py"), "--compiled", compiled, "--tz", tz, "--pricing", pricing]
        for h in M["hosts"]:
            p = os.path.join(scans, h["name"], "state_5.sqlite")
            if os.path.isfile(p):
                cmd += ["--sqlite", "%s=%s" % (h["name"], p)]
        run(cmd)

    if "build" in steps:
        env = dict(os.environ)
        if M.get("study_url"):
            try:  # only an absolute https URL reaches the dashboard; anything else is dropped here and again in build_dashboard
                env["STUDY_URL"] = safety.validate_study_url(M["study_url"])
            except safety.UnsafeValue as ex:
                log("warning: study_url in the manifest dropped, not rendered: %s" % ex)
                env.pop("STUDY_URL", None)
        dash_cmd = [a.python, os.path.join(HERE, "build_dashboard.py"), os.path.join(compiled, "summary.json"), os.path.join(compiled, "agent-ledger.html")]
        if config:
            dash_cmd.append(config)
        run(dash_cmd, env=env)
        cmd = [a.python, os.path.join(HERE, "build_report.py"), "--compiled", compiled, "--scans", scans, "--pricing", pricing, "--out", pkg, "--date", date, "--tz", tz]
        if config:
            cmd += ["--config", config]
        if M.get("package_paths"):  # off by default: absolute scan roots and the report config name users and directories
            cmd.append("--package-paths")
        for h in M["hosts"]:
            p = os.path.join(scans, h["name"], "stats-cache.json")
            if os.path.isfile(p):
                cmd += ["--stats-cache", "%s=%s" % (h["name"], p)]
        run(cmd)
        if accounts and os.path.isfile(accounts) and M.get("package_accounts"):  # off by default: it names people and organisations
            safety.private_copy(accounts, os.path.join(pkg, "accounts.json"))
            with safety.private_open(os.path.join(pkg, "SENSITIVITY.md"), "a") as fh:  # build_report wrote the general notice; add the accounts paragraph
                fh.write("\n## accounts.json is included\n\nThis package includes `accounts.json` (`package_accounts: true`), which names accounts (identifiers, plans and possibly "
                         "e-mail addresses or organisation names) and the credential files they were read from. Treat the package as internal.\n")
            import build_report
            build_report.write_sums(pkg)  # the checksum file binds the optional files too
        zpath = pkg + ".zip"
        with safety.private_open(zpath, "wb") as zfh:  # the archive repeats the package's contents; keep it owner-only too
            with zipfile.ZipFile(zfh, "w", zipfile.ZIP_DEFLATED) as z:
                for fn in sorted(os.listdir(pkg)):
                    z.write(os.path.join(pkg, fn), os.path.join(os.path.basename(pkg), fn))
        log("package: %s  (sha256 %s)" % (zpath, sha256(zpath)[:16]))
        log("dashboard: %s" % os.path.join(compiled, "agent-ledger.html"))
        log("report: %s" % os.path.join(pkg, "USAGE_REPORT.md"))


if __name__ == "__main__":
    main()
