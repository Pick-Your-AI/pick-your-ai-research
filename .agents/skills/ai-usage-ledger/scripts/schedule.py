#!/usr/bin/env python3
"""
schedule.py - install, remove or inspect the scheduled `ledger.py run` on this machine.

    python3 schedule.py install --frequency daily --time 03:00 [--weekday mon] [--dry-run]
    python3 schedule.py remove [--dry-run]
    python3 schedule.py status

Installing persistence needs consent that cannot come from configuration alone: `install` shows the full disclosure
(wrapper, schedule, hosts and roots, archive and anonymise flags, output directories, storage so far) and then needs
either a typed confirmation on a terminal or a consent file (`schedule-consent.json` in the ledger home) whose
configuration hash matches what is about to be installed; onboarding never installs. Optional `--expires` makes the
scheduled run stop and remove itself after a date. Existing entries are reported before they are replaced.

Windows uses Task Scheduler (schtasks, task name "AI Usage Ledger"); Linux, WSL and macOS use the user's crontab
(one line tagged `# ai-usage-ledger`). Each backend runs a small wrapper written to the ledger home
(run-ledger.cmd or run-ledger.sh) that appends output to <home>/logs/run.log, so the command line stays simple
and the wrapper can be edited by hand. Nothing here needs elevation. macOS may additionally require granting
cron Full Disk Access for the tools' directories; the status output says so.

Standard library only.
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import safety  # noqa: E402

TASK_NAME = "AI Usage Ledger"
MARK = "# ai-usage-ledger"
IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"
WEEKDAYS = {"mon": ("MON", 1), "tue": ("TUE", 2), "wed": ("WED", 3), "thu": ("THU", 4), "fri": ("FRI", 5), "sat": ("SAT", 6), "sun": ("SUN", 0)}


def parse_time(t):
    hh, mm = (t or "03:00").split(":")
    return int(hh) % 24, int(mm) % 60


def wrapper_path(home):
    return os.path.join(home, "run-ledger.cmd" if IS_WIN else "run-ledger.sh")


RUN_FLAGS = {"anonymize": "--anonymize", "archive": "--archive"}  # the only options a scheduled run may carry (plus --scheduled and --until)
CONSENT_FILE = "schedule-consent.json"


def _check_plain(value, what):
    if re.search(r"[\x00-\x1f\x7f]", str(value)):
        raise SystemExit("%s contains a control character and was refused" % what)
    return str(value)


def wrapper_body(home, python, flags=(), expires=None):
    """The scheduled command as a script. Every word is quoted for the platform; flags come from RUN_FLAGS only."""
    ledger = os.path.join(HERE, "ledger.py")
    log = os.path.join(home, "logs", "run.log")
    for v, what in ((home, "ledger home"), (python, "python path")):
        _check_plain(v, what)
    args = ["--scheduled"] + [RUN_FLAGS[f] for f in flags if f in RUN_FLAGS]
    if expires:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(expires)):
            raise SystemExit("expires must be YYYY-MM-DD")
        args += ["--until", str(expires)]
    if IS_WIN:
        cmdline = subprocess.list2cmdline([python, ledger, "run"] + args)
        if any(ch in home + log for ch in "%!^&|<>\""):
            raise SystemExit("ledger home path contains a character that cannot be placed safely in a batch file: %r" % home)
        return '@echo off\r\nset "AI_USAGE_LEDGER_HOME=%s"\r\necho [%%date%% %%time%%] scheduled run >> "%s"\r\n%s >> "%s" 2>&1\r\n' % (home, log, cmdline, log)
    words = " ".join(shlex.quote(x) for x in [python, ledger, "run"] + args)
    return "#!/bin/sh\nexport AI_USAGE_LEDGER_HOME=%s\necho \"[$(date -Iseconds)] scheduled run\" >> %s\n%s >> %s 2>&1\n" % (shlex.quote(home), shlex.quote(log), words, shlex.quote(log))


def write_wrapper(home, python, flags=(), expires=None):
    os.makedirs(os.path.join(home, "logs"), exist_ok=True)
    if not IS_WIN:
        for d in (home, os.path.join(home, "logs")):
            try:
                os.chmod(d, 0o700)
            except OSError:
                pass
    p = wrapper_path(home)
    body = wrapper_body(home, python, flags, expires)
    if IS_WIN:
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
    else:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o700)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        os.chmod(p, 0o700)
    return p


def _run(cmd, dry_run=False, input_text=None):
    print("$ " + (" ".join(shlex.quote(c) for c in cmd) if not IS_WIN else " ".join('"%s"' % c if " " in c else c for c in cmd)))
    if dry_run:
        return 0, ""
    r = subprocess.run(cmd, capture_output=True, text=True, input=input_text)
    if r.returncode != 0:
        # schtasks / crontab / ssh output is untrusted for the terminal: no escape sequences, no C0 controls
        sys.stderr.write(safety.clean_for_terminal((r.stderr or r.stdout or "").strip()) + "\n")
    return r.returncode, r.stdout


def crontab_lines():
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    except (FileNotFoundError, OSError):
        return []
    if r.returncode != 0:
        return []
    return [line for line in r.stdout.splitlines()]


def material_config(home, python, frequency, time_, weekday, flags, expires, manifest=None):
    """Everything that decides what the scheduled run will do; its hash ties a consent to exactly this."""
    hosts = []
    manifest_sha = None
    if manifest and os.path.isfile(manifest):
        try:
            with open(manifest, encoding="utf-8") as fh:
                M = json.load(fh)
            # the whole manifest, normalised, is part of the consent: workdir, package_accounts, interpreters,
            # pricing/accounts paths and every host field, not just a summary of the roots
            manifest_sha = hashlib.sha256(json.dumps(M, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:16]
            for h in M.get("hosts", []):
                roots = {k: v for k, v in h.items() if k.endswith("_roots") or k.endswith("_dbs")}
                hosts.append({"name": h.get("name"), "kind": h.get("kind", "local"), "ssh": h.get("ssh"), "distro": h.get("distro"), "roots": roots})
        except Exception:
            pass
    return {"home": home, "python": python, "frequency": frequency, "time": time_, "weekday": weekday, "flags": sorted(flags), "expires": expires,
            "wrapper": wrapper_body(home, python, flags, expires), "hosts": hosts, "manifest_sha": manifest_sha}


def config_hash(mat):
    return hashlib.sha256(json.dumps(mat, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def sensitive_reasons(mat):
    """What makes this schedule high-impact: raw-log archiving, remote hosts, other profiles or drives."""
    reasons = []
    if "archive" in mat["flags"]:
        reasons.append("raw-log archiving copies every transcript file on every run")
    for h in mat["hosts"]:
        if h.get("kind") == "ssh":
            reasons.append("reaches %s over SSH (%s)" % (h.get("name"), h.get("ssh")))
        elif h.get("kind") == "wsl":
            reasons.append("reads the WSL distro %s" % (h.get("distro") or h.get("name")))
        elif h.get("kind") == "share":
            reasons.append("reads another user profile or drive: %s" % h.get("name"))
    return reasons


def disclosure(home, mat, workdir=None):
    """The full picture the operator must see before persistence is registered."""
    out = []
    out.append("The scheduled entry will run, %s at %s%s:" % (mat["frequency"], mat["time"], (" (until %s, then it removes itself)" % mat["expires"]) if mat["expires"] else ""))
    out.append("  wrapper %s:" % wrapper_path(home))
    out += ["    " + ln for ln in mat["wrapper"].splitlines()]
    if mat["hosts"]:
        out.append("  hosts and roots it will read:")
        for h in mat["hosts"]:
            where = h["name"] + (" over ssh %s" % h["ssh"] if h.get("ssh") else " (WSL %s)" % h["distro"] if h.get("distro") else "")
            out.append("    %s" % where)
            for k, v in h["roots"].items():
                for r in v:
                    out.append("      %s" % r)
    out.append("  raw-log archive: %s   anonymised copy: %s" % ("ON" if "archive" in mat["flags"] else "off", "on" if "anonymize" in mat["flags"] else "off"))
    out.append("  writes under: %s and %s" % (home, workdir or os.path.join(home, "ledger")))
    size = 0
    for d in (home,):
        for dp, _, fns in os.walk(d):
            for fn in fns:
                try:
                    size += os.path.getsize(os.path.join(dp, fn))
                except OSError:
                    pass
    out.append("  storage used by the ledger home so far: %.2f GB (the archive grows with your logs)" % (size / 1e9))
    reasons = sensitive_reasons(mat)
    if reasons:
        out.append("  HIGH-IMPACT: " + "; ".join(reasons))
    out.append("  remove at any time: python3 scripts/ledger.py schedule remove")
    return "\n".join(out)


def consent_path(home):
    return os.path.join(home, CONSENT_FILE)


def write_consent(home, mat, approved_by, sensitive_ack):
    rec = {"approved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "approved_by": approved_by, "config_hash": config_hash(mat),
           "sensitive_acknowledged": bool(sensitive_ack), "material": mat}
    fd = os.open(consent_path(home), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2)
    return rec


def check_consent(home, mat):
    """Return (ok, reason). A consent is valid only for the exact material configuration and, when the schedule
    is high-impact, only if that was acknowledged separately."""
    p = consent_path(home)
    if not os.path.isfile(p):
        return False, "no consent recorded (%s)" % p
    try:
        with open(p, encoding="utf-8") as fh:
            rec = json.load(fh)
    except Exception as ex:
        return False, "consent file unreadable: %s" % ex
    if rec.get("config_hash") != config_hash(mat):
        return False, "the schedule, wrapper, hosts or flags changed since consent was given (%s); review and consent again" % rec.get("approved_at")
    if sensitive_reasons(mat) and not rec.get("sensitive_acknowledged"):
        return False, "this schedule is high-impact (archive, SSH, WSL or other profiles) and the consent did not acknowledge that"
    return True, "consented %s by %s" % (rec.get("approved_at"), rec.get("approved_by"))


def existing_entry():
    if IS_WIN:
        try:
            r = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME], capture_output=True, text=True)
        except (FileNotFoundError, OSError):
            return None
        return TASK_NAME if r.returncode == 0 else None
    lines = [x for x in crontab_lines() if MARK in x]
    return lines[0] if lines else None


def install(home, python, frequency, time_, weekday="mon", flags=(), dry_run=False, expires=None, manifest=None, workdir=None, consent="ask"):
    """consent: "ask" (typed confirmation on a terminal, else a valid consent file is required), or "file" (consent file only)."""
    if not re.fullmatch(r"\d{1,2}:\d{2}", str(time_ or "")):
        raise SystemExit("time must be HH:MM")
    hh, mm = parse_time(time_)
    if frequency == "none":
        return remove(home, dry_run)
    mat = material_config(home, python, frequency, time_, weekday, flags, expires, manifest)
    print(disclosure(home, mat, workdir))
    scheduler = "schtasks" if IS_WIN else "crontab"
    if not shutil.which(scheduler):
        print("Not installed: the scheduler command `%s` is not available on this system, so nothing was written or recorded." % scheduler)
        return 4
    ok, why = check_consent(home, mat)
    if not ok:
        interactive = consent == "ask" and sys.stdin.isatty() and sys.stdout.isatty()
        if not interactive:
            print("Not installed: %s.\nTo consent without a terminal, write %s with approved_by, approved_at, config_hash=%s%s (`schedule consent --print` shows the exact JSON), then run install again." % (
                why, consent_path(home), config_hash(mat), ' and sensitive_acknowledged=true' if sensitive_reasons(mat) else ""))
            return 3
        ans = input("Register this scheduled entry? Type 'yes' to confirm: ").strip().lower()
        if ans != "yes":
            print("Not installed.")
            return 3
        ack = False
        if sensitive_reasons(mat):
            ack = input("This schedule is high-impact (see HIGH-IMPACT above). Type 'yes, I understand' to confirm: ").strip().lower() == "yes, i understand"
            if not ack:
                print("Not installed.")
                return 3
        if not dry_run:
            write_consent(home, mat, os.environ.get("USERNAME") or os.environ.get("USER") or "operator", ack)
    else:
        print("  consent: %s" % why)
    prior = existing_entry()  # looked up only once consent is settled, and tolerant of a missing scheduler binary
    if prior:
        print("  NOTE: an entry already exists (%s) and will be replaced." % prior)
    wrapper = write_wrapper(home, python, flags, expires) if not dry_run else wrapper_path(home)
    if IS_WIN:
        cmd = ["schtasks", "/Create", "/F", "/TN", TASK_NAME, "/TR", '"%s"' % wrapper, "/ST", "%02d:%02d" % (hh, mm)]
        if frequency == "daily":
            cmd += ["/SC", "DAILY"]
        elif frequency == "weekly":
            cmd += ["/SC", "WEEKLY", "/D", WEEKDAYS.get(weekday, WEEKDAYS["mon"])[0]]
        elif frequency == "monthly":
            cmd += ["/SC", "MONTHLY", "/D", "1"]
        else:
            raise SystemExit("frequency must be none, daily, weekly or monthly")
        rc, _ = _run(cmd, dry_run)
        if rc == 0:
            print("Installed. Remove at any time with: python3 scripts/ledger.py schedule remove")
        return rc
    spec = {"daily": "%d %d * * *", "weekly": "%d %d * * " + str(WEEKDAYS.get(weekday, WEEKDAYS["mon"])[1]), "monthly": "%d %d 1 * *"}.get(frequency)
    if not spec:
        raise SystemExit("frequency must be none, daily, weekly or monthly")
    line = "%s %s %s" % (spec % (mm, hh), shlex.quote(wrapper), MARK)
    keep = [x for x in crontab_lines() if MARK not in x] if not dry_run else []
    new = "\n".join(keep + [line]) + "\n"
    print("crontab line: " + line)
    rc, _ = _run(["crontab", "-"], dry_run, input_text=new)
    if IS_MAC and rc == 0:
        print("macOS: if the run log shows permission errors, grant cron (or your terminal) Full Disk Access in System Settings > Privacy & Security.")
    if rc == 0:
        print("Installed. Remove at any time with: python3 scripts/ledger.py schedule remove")
    return rc


def remove(home, dry_run=False):
    if IS_WIN:
        rc, _ = _run(["schtasks", "/Delete", "/F", "/TN", TASK_NAME], dry_run)
        return 0 if rc in (0, 1) else rc  # 1 = task did not exist
    keep = [x for x in crontab_lines() if MARK not in x]
    rc, _ = _run(["crontab", "-"], dry_run, input_text="\n".join(keep) + ("\n" if keep else ""))
    return rc


def status(home):
    if IS_WIN:
        r = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST", "/V"], capture_output=True, text=True)
        if r.returncode != 0:
            print("scheduled task: not installed")
            return 1
        want = ("Task To Run", "Schedule Type", "Start Time", "Days", "Last Run Time", "Last Result", "Next Run Time", "Status")
        for line in r.stdout.splitlines():
            if any(line.strip().startswith(w) for w in want):
                print("  " + safety.clean_for_terminal(line.strip(), limit=500))
        return 0
    lines = [x for x in crontab_lines() if MARK in x]
    if not lines:
        print("cron entry: not installed")
        return 1
    for x in lines:
        print("  " + safety.clean_for_terminal(x, limit=500))
    log = os.path.join(home, "logs", "run.log")
    if os.path.isfile(log):
        with open(log, encoding="utf-8", errors="replace") as fh:
            tail = fh.readlines()[-3:]
        # the run log holds subprocess output from every host; it is data, not something the terminal may interpret
        print("  last log lines: " + safety.clean_for_terminal("".join(tail).strip().replace("\n", " | "), limit=1000))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", default=os.path.expanduser(os.environ.get("AI_USAGE_LEDGER_HOME") or "~/.ai-usage-ledger"))
    ap.add_argument("--python", default=sys.executable)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("install")
    i.add_argument("--frequency", default="daily", choices=["none", "daily", "weekly", "monthly"])
    i.add_argument("--time", default="03:00", help="HH:MM local time")
    i.add_argument("--weekday", default="mon", choices=sorted(WEEKDAYS))
    i.add_argument("--anonymize", action="store_true", help="the scheduled run also builds the anonymised copy")
    i.add_argument("--archive-raw", action="store_true", help="the scheduled run also archives the raw log files")
    i.add_argument("--expires", help="YYYY-MM-DD after which the scheduled run stops and removes the entry")
    i.add_argument("--manifest", help="manifest.json whose hosts and roots are disclosed and covered by the consent")
    i.add_argument("--workdir")
    i.add_argument("--dry-run", action="store_true", help="print the command without changing anything")
    c = sub.add_parser("consent", help="show the material configuration and its hash (for a consent file written by hand)")
    c.add_argument("--frequency", default="daily", choices=["daily", "weekly", "monthly"])
    c.add_argument("--time", default="03:00")
    c.add_argument("--weekday", default="mon", choices=sorted(WEEKDAYS))
    c.add_argument("--anonymize", action="store_true")
    c.add_argument("--archive-raw", action="store_true")
    c.add_argument("--expires")
    c.add_argument("--manifest")
    c.add_argument("--print", dest="do_print", action="store_true")
    r = sub.add_parser("remove")
    r.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "install":
        flags = [f for f, on in (("anonymize", a.anonymize), ("archive", a.archive_raw)) if on]
        return install(a.home, a.python, a.frequency, a.time, a.weekday, flags, a.dry_run, a.expires, a.manifest, a.workdir)
    if a.cmd == "consent":
        flags = [f for f, on in (("anonymize", a.anonymize), ("archive", a.archive_raw)) if on]
        mat = material_config(a.home, a.python, a.frequency, a.time, a.weekday, flags, a.expires, a.manifest)
        print(disclosure(a.home, mat))
        print(json.dumps({"approved_by": "<your name>", "approved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "config_hash": config_hash(mat),
                          "sensitive_acknowledged": bool(sensitive_reasons(mat))}, indent=2))
        print("write that JSON to %s to consent without a terminal" % consent_path(a.home))
        return 0
    if a.cmd == "remove":
        return remove(a.home, a.dry_run)
    return status(a.home)


if __name__ == "__main__":
    sys.exit(main())
