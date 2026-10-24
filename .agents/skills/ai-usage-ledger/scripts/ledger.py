#!/usr/bin/env python3
"""
ledger.py - the one entry point people and agents use day to day.

    python3 scripts/ledger.py init            # first-run onboarding (interactive on a terminal, defaults with --yes)
    python3 scripts/ledger.py run             # scan every configured host, append new calls to the store, rebuild the reports
    python3 scripts/ledger.py status          # what is configured, what is stored, when it last ran
    python3 scripts/ledger.py export --format csv --out events.csv
    python3 scripts/ledger.py run --anonymize # also build a publishable copy: hosts, projects, accounts pseudonymised
    python3 scripts/ledger.py doc --list      # ledger documents (statements, memos, briefs) from the catalog
    python3 scripts/ledger.py doc --template executive-summary --pdf --docx
    python3 scripts/ledger.py schedule install|remove|status   # Task Scheduler / cron refresh
    python3 scripts/ledger.py archive status|list|grep|restore # the raw logs themselves (archive.raw_logs=y)
    python3 scripts/ledger.py query --presets                 # detailed questions over the store and the archive
    python3 scripts/ledger.py query by-project --since 2026-08-01 --tool codex
    python3 scripts/ledger.py report --since today --tz America/New_York # scoped HTML and dollar metrics
    python3 scripts/ledger.py publish-check <dir> # identity scan before anything leaves the machine
    python3 scripts/ledger.py reinit          # fresh onboarding; the old store is kept aside with a timestamp

Preferences (branding, storage backend, working directory, timezone, auto-detection) are captured once,
saved to <home>/config.json and mirrored into the store's prefs table, and reused on every later run.
The store is append-only: rescanning never duplicates a call, so `run` can be executed as often as wanted.

Standard library only.
"""
import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import anonymize  # noqa: E402
import detect_hosts  # noqa: E402
import ledger_archive  # noqa: E402
import ledger_store  # noqa: E402
import schedule  # noqa: E402

CONFIG_VERSION = 3  # 2: detect.wsl defaults off (implicit True withdrawn unless detect.explicit); 3: manifest/consent reconciled with detect.wsl


def home_dir():
    return os.path.expandvars(os.path.expanduser(os.environ.get("AI_USAGE_LEDGER_HOME") or "~/.ai-usage-ledger"))


def config_path():
    return os.path.join(home_dir(), "config.json")


def load_config():
    p = config_path()
    if not os.path.isfile(p):
        return None
    import safety
    safety.refuse_if_shared(p, "ledger config")
    with open(p, encoding="utf-8") as fh:
        cfg = migrate_config(json.load(fh))
    if cfg.pop("_reconcile_wsl", False):
        # whatever version wrote this home: when WSL discovery is off, the manifest must hold no WSL host. Prune
        # them; only when that actually changes the scanned scope is a scheduled consent set aside.
        changed = False
        mp = cfg.get("manifest_path")
        try:
            if not (cfg.get("detect") or {}).get("wsl") and mp:
                if not os.path.isfile(mp):  # a configured manifest that is absent right now may reappear: not reconciled yet
                    raise FileNotFoundError(mp)
                with open(mp, encoding="utf-8") as fh:
                    m = json.load(fh)
                kept = [h for h in m.get("hosts", []) if h.get("kind") != "wsl"]
                if len(kept) != len(m.get("hosts", [])):
                    m["hosts"] = kept
                    write_json_private(mp, m)
                    changed = True
                    sys.stderr.write("config migrated: WSL hosts removed from %s because WSL discovery is off\n" % mp)
        except Exception as ex:
            # the manifest was not inspected: keep the home below version 3 so the next load tries again
            cfg["version"] = min(int(cfg.get("version") or 1), 2)
            sys.stderr.write("config migrated: could not prune WSL hosts from the manifest (%s); the reconciliation will be retried on the next load, or run `init` to regenerate it\n" % ex)
        consent = os.path.join(home_dir(), schedule.CONSENT_FILE)
        if changed and os.path.isfile(consent):
            os.replace(consent, consent + ".withdrawn")
            sys.stderr.write("config migrated: the scheduled-run consent was set aside because the scanned scope changed; scheduled runs will refuse until `schedule install` is confirmed again\n")
        save_config(cfg)
    return cfg


def save_config(cfg):
    import safety
    safety.private_dir(home_dir())
    safety.write_private(config_path(), json.dumps(cfg, indent=2))


def write_json_private(path, obj):
    import safety
    safety.write_private(path, json.dumps(obj, indent=2))


def open_private(path):
    """A text file for streaming writes (jsonl exports) created owner-only (0600 on POSIX) from the first byte."""
    import safety
    safety.private_dir(os.path.dirname(os.path.abspath(path)) or ".")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    fh = os.fdopen(fd, "w", encoding="utf-8", newline="\n")
    safety.private_file(path)  # an existing file keeps its old mode through O_TRUNC; fix it
    return fh


def local_tz_name():
    try:
        tz = datetime.now().astimezone().tzinfo
        key = getattr(tz, "key", None)
        if key:
            return key
        if os.path.exists("/etc/timezone"):
            return open("/etc/timezone").read().strip()
        if os.path.islink("/etc/localtime"):
            return "/".join(os.path.realpath("/etc/localtime").split("/")[-2:])
    except Exception:
        pass
    return "UTC"


def run(cmd, **kw):
    sys.stderr.write("$ %s\n" % " ".join(cmd))
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        raise SystemExit("command failed (%d): %s" % (r.returncode, " ".join(cmd)))


# ----------------------------------------------------------------------------
# onboarding
# ----------------------------------------------------------------------------

# Neutral by default: no publisher name, contact, logo or slogan appears on a report unless the operator chooses it.
DEFAULT_BRAND = {"name": "Usage Ledger", "eyebrow": "", "tagline": "", "contact": "", "logo": "", "accent": "#1E3A8A", "footer": "", "explicit": False}

# Named presets the operator can pick explicitly (`init --brand-preset completetech` or the first onboarding question).
BRAND_PRESET_FILES = {"completetech": os.path.join(SKILL, "examples", "report_config.completetech.json")}


def brand_preset(name):
    path = BRAND_PRESET_FILES.get((name or "").lower())
    if not path or not os.path.isfile(path):
        raise SystemExit("unknown brand preset %r (available: %s)" % (name, ", ".join(sorted(BRAND_PRESET_FILES)) or "none"))
    with open(path, encoding="utf-8") as fh:
        b = dict((json.load(fh).get("branding") or {}))
    if b.get("logo") and not os.path.isabs(b["logo"]):
        b["logo"] = os.path.normpath(os.path.join(os.path.dirname(path), b["logo"]))
        if not os.path.isfile(b["logo"]):
            b["logo"] = os.path.join(SKILL, "assets", os.path.basename(b["logo"]))
    b["preset"] = name.lower()
    b["explicit"] = True
    return b

QUESTIONS = [
    # key, prompt, default-from-current, validator/choices
    ("brand.preset", "Brand preset (none = neutral, or a named preset such as completetech)", lambda c: c["branding"].get("preset") or "none", ["none"] + sorted(BRAND_PRESET_FILES)),
    ("brand.name", "Brand name shown on the dashboard and study", lambda c: c["branding"]["name"], None),
    ("brand.eyebrow", "Eyebrow line above the name (e.g. company legal name)", lambda c: c["branding"]["eyebrow"], None),
    ("brand.tagline", "Tagline", lambda c: c["branding"]["tagline"], None),
    ("brand.contact", "Contact line (site · e-mail)", lambda c: c["branding"]["contact"], None),
    ("brand.logo", "Logo file (PNG/SVG path, URL, or blank for none)", lambda c: c["branding"]["logo"], None),
    ("brand.accent", "Accent colour (hex)", lambda c: c["branding"]["accent"], None),
    ("brand.footer", "Footer text", lambda c: c["branding"]["footer"], None),
    ("theme", "Default theme (light / dark / system)", lambda c: c["theme"], ["light", "dark", "system"]),
    ("store.kind", "Storage backend (sqlite / json / csv)", lambda c: c["store"]["kind"], ["sqlite", "json", "csv"]),
    ("workdir", "Working directory for scans, compiled tables and reports", lambda c: c["workdir"], None),
    ("timezone", "Timezone for time-of-day analysis", lambda c: c["timezone"], None),
    ("detect.all_profiles", "Also scan other user profiles and other drives on this machine? (y/n)", lambda c: "y" if c["detect"]["all_profiles"] else "n", ["y", "n"]),
    ("detect.wsl", "Probe WSL distros on Windows? (y/n)", lambda c: "y" if c["detect"]["wsl"] else "n", ["y", "n"]),
    ("accounts.from_credentials", "Read credential files (auth.json, .claude.json) to label accounts with their plan? Tokens are never kept. (y/n)", lambda c: "y" if c["accounts"]["from_credentials"] else "n", ["y", "n"]),
    ("accounts.identifiable", "Keep e-mail addresses and organisation names in accounts.json? (n = pseudonymous account ids only) (y/n)", lambda c: "y" if c["accounts"]["identifiable"] else "n", ["y", "n"]),
    ("anonymize.on_every_run", "Also build an anonymised copy for publication on every run? (y/n)", lambda c: "y" if c["anonymize"]["on_every_run"] else "n", ["y", "n"]),
    ("prompts.capture", "Record the text of your prompts (what you typed to each agent) in the store, so `query prompts` can search it? n keeps counts and tokens only. (y/n)", lambda c: "y" if c["prompts"]["capture"] else "n", ["y", "n"]),
    ("archive.raw_logs", "Archive the raw log files themselves (every transcript the scanners read), so they outlive the tools' retention? (y/n)", lambda c: "y" if c["archive"]["raw_logs"] else "n", ["y", "n"]),
    ("archive.compress", "Compress the archive with gzip? (y/n; n keeps files re-scannable in place)", lambda c: "y" if c["archive"]["compress"] else "n", ["y", "n"]),
    ("schedule.frequency", "Refresh automatically? (none / daily / weekly / monthly)", lambda c: c["schedule"]["frequency"], ["none", "daily", "weekly", "monthly"]),
    ("schedule.time", "At what local time? (HH:MM)", lambda c: c["schedule"]["time"], None),
    ("schedule.weekday", "Weekday for a weekly refresh (mon..sun)", lambda c: c["schedule"]["weekday"], sorted(schedule.WEEKDAYS)),
]


def default_config():
    return {
        "version": CONFIG_VERSION, "initialized_at": None, "home": home_dir(),
        "store": {"kind": "sqlite", "path": os.path.join(home_dir(), "ledger.sqlite")},
        "workdir": os.path.join(home_dir(), "ledger"), "timezone": local_tz_name(), "theme": "system",
        "branding": dict(DEFAULT_BRAND), "detect": {"all_profiles": False, "wsl": False, "on_every_run": True},
        "pricing_path": os.path.join(home_dir(), "pricing.json"), "accounts_path": os.path.join(home_dir(), "accounts.json"),
        "report_config_path": os.path.join(home_dir(), "report_config.json"), "manifest_path": os.path.join(home_dir(), "manifest.json"),
        "package_prefix": "AI_Usage_Ledger", "extra_hosts": [],
        "accounts": {"from_credentials": False, "identifiable": False},
        "anonymize": {"on_every_run": False, "salt": secrets.token_hex(16)},
        "prompts": {"capture": False},  # prompt text is an explicit opt-in; counts and tokens never need it
        "archive": {"raw_logs": False, "compress": True, "path": os.path.join(home_dir(), "archive")},
        "schedule": {"frequency": "none", "time": "03:00", "weekday": "mon", "install": False, "installed_at": None},
    }


def prompt_capture(cfg):
    """True only when the operator opted in to storing prompt text (prompts.capture=y)."""
    return bool(((cfg or {}).get("prompts") or {}).get("capture"))


def set_dotted(cfg, key, value):
    if key == "brand.preset":
        if value and value != "none":
            cfg["branding"] = brand_preset(value)
        else:
            cfg["branding"] = dict(DEFAULT_BRAND, explicit=cfg["branding"].get("explicit", False))
            cfg["branding"].pop("preset", None)
    elif key.startswith("brand."):
        cfg["branding"][key[6:]] = value
        cfg["branding"]["explicit"] = True  # the operator chose this; unattended defaults never set it
    elif key == "store.kind":
        cfg["store"]["kind"] = value
        cfg["store"]["path"] = os.path.join(home_dir(), {"sqlite": "ledger.sqlite", "json": "ledger-json", "csv": "ledger-csv"}[value])
    elif key.startswith("detect."):
        cfg["detect"][key[7:]] = value in ("y", "yes", "true", True)
        cfg["detect"]["explicit"] = True
    elif key in ("accounts.from_credentials", "accounts.identifiable"):
        cfg.setdefault("accounts", {"from_credentials": False, "identifiable": False})[key[9:]] = value in ("y", "yes", "true", True)
        cfg["accounts"]["explicit"] = True
    elif key == "anonymize.on_every_run":
        cfg.setdefault("anonymize", {"salt": secrets.token_hex(16)})["on_every_run"] = value in ("y", "yes", "true", True)
    elif key == "prompts.capture":
        cfg.setdefault("prompts", {})["capture"] = value in ("y", "yes", "true", True)
    elif key in ("archive.raw_logs", "archive.compress"):
        cfg.setdefault("archive", {"path": os.path.join(home_dir(), "archive")})[key[8:]] = value in ("y", "yes", "true", True)
    elif key == "archive.path":
        cfg.setdefault("archive", {})["path"] = value
    elif key == "schedule.install":
        sys.stderr.write("schedule.install is ignored: onboarding never registers a scheduled task; run `ledger.py schedule install` and confirm there.\n")
    elif key.startswith("schedule."):
        cfg.setdefault("schedule", {})[key[9:]] = value
    else:
        cfg[key] = value


def ask(prompt, default, choices=None):
    while True:
        raw = input("%s [%s]: " % (prompt, default)).strip()
        val = raw or default
        if choices and val not in choices:
            print("  choose one of: %s" % ", ".join(choices))
            continue
        return val


def check_archive_path(cfg):
    """A raw-log archive needs a dedicated directory; refuse before anything else happens in onboarding."""
    arc = cfg.get("archive") or {}
    ap_ = arc.get("path") or ""
    if arc.get("raw_logs") and os.path.isdir(ap_) and os.listdir(ap_) and not os.path.exists(os.path.join(ap_, ".ai-usage-ledger-archive")) and not ledger_archive.Archive._is_legacy_archive(ap_):
        raise SystemExit("archive.path %s already holds other files; choose an empty or new directory dedicated to the archive (it is what `remove everything` deletes)" % ap_)


def migrate_config(cfg):
    """Add keys introduced after the config was written, so older homes keep working."""
    if "accounts" not in cfg:
        cfg["accounts"] = {"from_credentials": False, "identifiable": False, "explicit": False}  # legacy home: preference never chosen
    cfg.setdefault("anonymize", {"on_every_run": False, "salt": secrets.token_hex(16)})
    cfg.setdefault("prompts", {"capture": False})  # pre-1.5.8 home: prompt text was never consented to, so it stays off
    cfg.setdefault("archive", {"raw_logs": False, "compress": True, "path": os.path.join(home_dir(), "archive")})
    cfg.setdefault("schedule", {"frequency": "none", "time": "03:00", "weekday": "mon", "installed_at": None})
    cfg.setdefault("detect", {"all_profiles": False, "wsl": False, "on_every_run": True})
    if int(cfg.get("version") or 1) < 2:
        d = cfg["detect"]
        if d.get("wsl") and not d.get("explicit"):  # never chosen by the operator: the pre-1.5.8 default is withdrawn
            d["wsl"] = False
            sys.stderr.write("config migrated: WSL discovery is now off by default; re-enable it with `init --set detect.wsl=y` if you want it.\n")
    if int(cfg.get("version") or 1) < 3:
        cfg["_reconcile_wsl"] = True  # a home saved by 1.5.9 may already be version 2 with WSL hosts still in its manifest
    if int(cfg.get("version") or 1) < CONFIG_VERSION:
        cfg["version"] = CONFIG_VERSION
    cfg.setdefault("branding", dict(DEFAULT_BRAND))
    cfg.setdefault("extra_hosts", [])
    return cfg


def onboard(args):
    cfg = load_config() if not args.reinit else None
    fresh = cfg is None
    cfg = migrate_config(cfg or default_config())
    prev_accounts_pref = dict(cfg.get("accounts") or {})
    if getattr(args, "brand_preset", None):
        set_dotted(cfg, "brand.preset", args.brand_preset)
    for kv in args.set or []:
        k, _, v = kv.partition("=")
        set_dotted(cfg, k.strip(), v.strip())
    interactive = sys.stdin.isatty() and sys.stdout.isatty() and not args.yes
    if interactive:
        print("\nAI usage ledger — onboarding. Press Enter to accept a default.\n")
        for key, prompt, current, choices in QUESTIONS:
            set_dotted(cfg, key, ask(prompt, current(cfg), choices))
    check_archive_path(cfg)  # before detection, credential reads or any file is written
    # detection
    print("\nDetecting agent logs on this machine%s..." % (" and its WSL distros" if cfg["detect"]["wsl"] and detect_hosts.IS_WIN else ""))
    hosts, notes = detect_hosts.detect_hosts(all_profiles=cfg["detect"]["all_profiles"], probe_wsl=cfg["detect"]["wsl"])
    for h in hosts:
        print("  [%s] %s" % (h["name"], "; ".join(h.get("_found", []))[:400]))
    for n in notes:
        print("  note:", n)
    acc_pref = cfg.setdefault("accounts", {"from_credentials": False, "identifiable": False})
    accounts = detect_hosts.draft_accounts(hosts, read_credentials=acc_pref.get("from_credentials", False), identifiable=acc_pref.get("identifiable", False))
    if interactive:
        print("\nAccounts drafted (%s):" % ("from credential files" if acc_pref.get("from_credentials") else "placeholders; credential files were not read"))
        for k, v in accounts["accounts"].items():
            if v.get("provider") in ("openai", "anthropic"):
                print("  %-28s %-34s %s" % (k, v.get("label"), v.get("plan")))
        extra = ask("Add an SSH host to scan? (user@host or blank)", "")
        while extra:
            cfg["extra_hosts"].append({"name": extra.split("@")[-1].split(".")[0], "kind": "ssh", "ssh": extra, "python": "python3",
                                       "claude_roots": ["~/.claude"], "codex_roots": ["~/.codex"], "_comment": "edit roots in manifest.json"})
            extra = ask("Add another SSH host? (user@host or blank)", "")
    # write files (owner-only: they name accounts, hosts and what will be executed)
    import safety
    safety.private_dir(home_dir())
    if fresh or not os.path.isfile(cfg["pricing_path"]):
        with open(os.path.join(SKILL, "templates", "pricing.json"), encoding="utf-8") as fh:
            safety.write_private(cfg["pricing_path"], fh.read())
    acc_now = cfg.get("accounts") or {}
    pref_changed = {k: v for k, v in acc_now.items() if k != "explicit"} != {k: v for k, v in prev_accounts_pref.items() if k != "explicit"}
    legacy_draft = False
    if os.path.isfile(cfg["accounts_path"]) and not prev_accounts_pref.get("explicit", True):
        try:
            with open(cfg["accounts_path"], encoding="utf-8") as fh:
                legacy_draft = "_sensitivity" not in json.load(fh)  # drafted before the preference existed: credential-derived by default
        except Exception:
            legacy_draft = False
    acc_now["explicit"] = True  # after onboarding the preference is a decision, whether typed, set or accepted as default
    if fresh or not os.path.isfile(cfg["accounts_path"]) or args.reinit:
        write_json_private(cfg["accounts_path"], accounts)
    elif pref_changed or legacy_draft:
        backup = cfg["accounts_path"] + ".before-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy(cfg["accounts_path"], backup)
        write_json_private(cfg["accounts_path"], accounts)
        print("accounts.json redrafted %s; the previous file is kept at %s" % ("because the credential preferences changed" if pref_changed else "under the credential preference now on record (it predated that preference)", backup)),
    write_manifest(cfg, hosts)
    write_report_config(cfg)
    if fresh or not cfg.get("initialized_at"):
        cfg["initialized_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cfg.setdefault("accounts", {"from_credentials": False, "identifiable": False})
    cfg.setdefault("anonymize", {"on_every_run": False, "salt": secrets.token_hex(16)})
    cfg.setdefault("archive", {"raw_logs": False, "compress": True, "path": os.path.join(home_dir(), "archive")})
    cfg.setdefault("schedule", {"frequency": "none", "time": "03:00", "weekday": "mon", "install": False, "installed_at": None})
    save_config(cfg)
    sch = cfg["schedule"]
    sch.pop("install", None)
    if sch.get("frequency", "none") != "none":
        print("Scheduled refresh preference saved (%s at %s). Nothing was registered: onboarding never installs persistence. "
              "When you are ready, run `python3 scripts/ledger.py schedule install`; it shows exactly what will run and asks you to confirm "
              "(remove later with `schedule remove`)." % (sch["frequency"], sch.get("time")))
    st = ledger_store.Store.open(cfg["store"]["kind"], cfg["store"]["path"])
    for k, v in cfg.items():
        st.set_pref(k, v)
    st.close()
    print("\nSaved preferences to %s" % config_path())
    print("Store: %s at %s" % (cfg["store"]["kind"], cfg["store"]["path"]))
    print("Manifest: %s (%d hosts)  Accounts: %s  Pricing: %s" % (cfg["manifest_path"], len(hosts) + len(cfg["extra_hosts"]), cfg["accounts_path"], cfg["pricing_path"]))
    print("Next: python3 scripts/ledger.py run")


def write_manifest(cfg, hosts):
    clean = []
    for h in hosts:
        clean.append({k: v for k, v in h.items() if not k.startswith("_")})
    clean += cfg.get("extra_hosts", [])
    m = {"_comment": "Generated by ledger.py from detect_hosts.py; hand-added hosts live in config.json extra_hosts and survive regeneration.",
         "workdir": cfg["workdir"], "snapshot_date": None, "timezone": cfg["timezone"], "package_prefix": cfg["package_prefix"],
         "pricing": cfg["pricing_path"], "accounts": cfg["accounts_path"], "report_config": cfg["report_config_path"], "package_accounts": False,
         "capture_prompts": prompt_capture(cfg), "hosts": clean}
    write_json_private(cfg["manifest_path"], m)


def write_report_config(cfg):
    b = dict(cfg["branding"])
    if not b.get("explicit"):  # unattended defaults: an unbranded report that says so, never a publisher identity
        b = {"name": "Usage Ledger", "accent": b.get("accent", "#1E3A8A"), "footer": "Unbranded report: run `ledger.py init` to set your own branding."}
    rc = {"title": "AI coding-agent usage: token volume, caching and cost study", "html_title": "Agent Usage Study", "dashboard_title": "Agent Token Ledger",
          "prices_as_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "theme_default": cfg.get("theme", "system"), "hosts": {}, "excluded_sources": [], "extra_limitations": [],
          "dashboard_excluded_note": "", "branding": b}
    write_json_private(cfg["report_config_path"], rc)


# ----------------------------------------------------------------------------
# run
# ----------------------------------------------------------------------------

TOOL_ROOT_KEYS = {"codex": ["codex_roots", "codex_sqlite"], "claude-code": ["claude_roots", "claude_stats_cache"], "copilot-cli": ["copilot_roots"],
                  "opencode": ["opencode_dbs"], "openclaw": ["openclaw_roots"], "gemini-cli": ["gemini_roots"], "qwen-code": ["qwen_roots"], "kimi": ["kimi_roots"],
                  "mistral-vibe": ["vibe_roots"], "continue": ["continue_roots"], "pi": ["pi_roots"], "aider": ["aider_roots"], "mini-swe-agent": ["mini_swe_roots"], "goose": ["goose_roots"]}
PREFIXED_KEYS = ("cline_roots", "generic_roots")  # "<tool>=<dir>" entries


def filter_manifest(src, dst, only=None, skip=None):
    """Write a copy of the manifest keeping only the roots of the wanted tools; hosts left without roots are dropped."""
    with open(src, encoding="utf-8") as fh:
        m = json.load(fh)
    only = set(only or [])
    skip = set(skip or [])

    def keep(tool):
        return (not only or tool in only) and tool not in skip

    hosts = []
    for h in m.get("hosts", []):
        h = dict(h)
        for tool, keys in TOOL_ROOT_KEYS.items():
            if not keep(tool):
                for k in keys:
                    h.pop(k, None)
        for k in PREFIXED_KEYS:
            if h.get(k):
                h[k] = [x for x in h[k] if keep(x.split("=", 1)[0] if "=" in x else k.split("_")[0])]
                if not h[k]:
                    h.pop(k)
        if any(h.get(k) for keys in TOOL_ROOT_KEYS.values() for k in keys if k.endswith("_roots") or k.endswith("_dbs")) or any(h.get(k) for k in PREFIXED_KEYS):
            hosts.append(h)
    m["hosts"] = hosts
    m["_comment"] = "Filtered copy for one run (--tools / --skip-tools); the full manifest is manifest.json."
    write_json_private(dst, m)  # it names hosts, SSH targets and roots like the manifest it was copied from
    return [h["name"] for h in hosts]


def do_run(args):
    if getattr(args, "until", None) and datetime.now().strftime("%Y-%m-%d") > args.until:
        if os.path.isfile(schedule.consent_path(home_dir())):
            print("scheduled run expired on %s; removing the schedule" % args.until)
            rc = schedule.remove(home_dir())
            cfg0 = load_config()
            if rc == 0 and cfg0:
                cfg0.setdefault("schedule", {}).update({"frequency": "none", "expires": None, "installed_at": None, "consent": None})
                save_config(cfg0)
            return rc
        print("scheduled run expired on %s; nothing to do (no schedule consent recorded for %s)" % (args.until, home_dir()))
        return 0
    cfg = load_config()
    if cfg is None:
        raise SystemExit("No configuration at %s. Run `python3 scripts/ledger.py init` first (interactive), or `init --yes` for neutral defaults; "
                         "nothing is scanned and no branding is chosen without that step." % config_path())
    if getattr(args, "scheduled", False):
        # a scheduled run may only do what was consented to: no host re-detection, no one-shot options, and the
        # complete manifest, the flags actually passed and the schedule must still hash to the consented configuration
        args.no_detect = True
        one_shot = [n for n in ("hosts", "tools", "skip_tools", "no_scan") if getattr(args, n, None)]
        if one_shot:
            raise SystemExit("scheduled run refused: one-shot options are not allowed under --scheduled (%s)" % ", ".join("--" + n.replace("_", "-") for n in one_shot))
        sch = cfg.get("schedule") or {}
        flags = ["anonymize"] if cfg.get("anonymize", {}).get("on_every_run") else []
        if cfg.get("archive", {}).get("raw_logs"):
            flags.append("archive")
        passed = [f for f, on in (("anonymize", getattr(args, "anonymize", False)), ("archive", getattr(args, "archive", False))) if on]
        if sorted(passed) != sorted(flags):
            raise SystemExit("scheduled run refused: the invocation's flags (%s) differ from the consented configuration (%s); the wrapper was edited. Re-run `schedule install`." % (", ".join(passed) or "none", ", ".join(flags) or "none"))
        if (getattr(args, "until", None) or None) != (sch.get("expires") or None):
            raise SystemExit("scheduled run refused: the invocation's expiry differs from the consented configuration; re-run `schedule install`.")
        mat = schedule.material_config(home_dir(), sys.executable, sch.get("frequency") or "daily", sch.get("time") or "03:00", sch.get("weekday") or "mon", flags, sch.get("expires"), cfg.get("manifest_path"))
        ok, why = schedule.check_consent(home_dir(), mat)
        if not ok:
            raise SystemExit("scheduled run refused: %s. Re-run `python3 scripts/ledger.py schedule install` to review and consent again." % why)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    t0 = time.time()
    if cfg["detect"].get("on_every_run", True) and not args.no_detect:
        hosts, _ = detect_hosts.detect_hosts(all_profiles=cfg["detect"]["all_profiles"], probe_wsl=cfg["detect"]["wsl"])
        write_manifest(cfg, hosts)
    write_report_config(cfg)
    work = cfg["workdir"]
    os.makedirs(work, exist_ok=True)
    py = sys.executable
    pipeline = os.path.join(HERE, "run_pipeline.py")
    manifest = cfg["manifest_path"]
    if getattr(args, "tools", None) or getattr(args, "skip_tools", None):
        manifest = os.path.join(home_dir(), "manifest.run.json")
        kept = filter_manifest(cfg["manifest_path"], manifest, (args.tools or "").split(",") if args.tools else None, (args.skip_tools or "").split(",") if args.skip_tools else None)
        print("tool filter: only=%s skip=%s -> hosts with roots left: %s" % (args.tools or "-", args.skip_tools or "-", ", ".join(kept) or "none"))
    if not args.no_scan:
        run([py, pipeline, "--manifest", manifest, "--only", "scan"] + (["--hosts", args.hosts] if args.hosts else []))
    archive_summary = None
    if (cfg.get("archive", {}).get("raw_logs") or args.archive) and not args.no_scan:
        with open(manifest, encoding="utf-8") as fh:
            mhosts = json.load(fh).get("hosts", [])
        if args.hosts:
            mhosts = [h for h in mhosts if h["name"] in args.hosts.split(",")]
        ar = ledger_archive.Archive(cfg["archive"].get("path") or os.path.join(home_dir(), "archive"), compress=cfg["archive"].get("compress", True))
        archive_summary = ledger_archive.archive_from_scans(ar, mhosts, os.path.join(work, "scans"))
        ar.close()
    # append-only ingest
    st = ledger_store.Store.open(cfg["store"]["kind"], cfg["store"]["path"])
    added = {"events": 0, "sessions": 0, "prompts": 0}
    skipped = {"events": 0, "sessions": 0, "prompts": 0}
    capture = prompt_capture(cfg)
    scans = os.path.join(work, "scans")
    for hostdir in sorted(os.listdir(scans)) if os.path.isdir(scans) else []:
        d = os.path.join(scans, hostdir)
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if fn.startswith("events.") and fn.endswith(".jsonl"):
                a, s = st.ingest_events_file(p)
                added["events"] += a
                skipped["events"] += s
            elif fn.startswith("sessions.") and fn.endswith(".jsonl"):
                a, s = st.ingest_sessions_file(p)
                added["sessions"] += a
                skipped["sessions"] += s
            elif fn.startswith("prompts.") and fn.endswith(".jsonl") and capture:  # off: nothing reaches the store even if a scan left a file
                a, s = st.ingest_prompts_file(p)
                added["prompts"] += a
                skipped["prompts"] += s
    print("store: added %s, already present %s%s" % (json.dumps(added), json.dumps(skipped), "" if capture else " (prompt capture off)"))
    # materialise the whole store for the report step, then analyse and build
    export_dir = os.path.join(work, "store-export")
    paths = ledger_store.export_jsonl(st, export_dir)
    counts = st.counts()
    compiled = os.path.join(work, "compiled")
    inv = os.path.join(scans, "*", "inventory.*.json")
    run([py, os.path.join(HERE, "compile_ai_logs.py"), "report", "--events", paths["events"][0], "--sessions", paths["sessions"][0], "--prompts", paths["prompts"][0],
         "--inventory", inv, "--pricing", cfg["pricing_path"], "--accounts", cfg["accounts_path"], "--out-dir", compiled])
    run([py, pipeline, "--manifest", manifest, "--only", "analyze,build"])
    anon_out = None
    if args.anonymize or cfg.get("anonymize", {}).get("on_every_run"):
        anon_out = build_anonymized(cfg, st, work, py, pipeline)
    meta = {"started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "seconds": round(time.time() - t0, 1),
            "added": added, "skipped": skipped, "store_counts": counts, "workdir": work, "anonymized": anon_out, "archive": archive_summary}
    st.record_run(meta)
    st.close()
    print("run recorded: %s events in store (%s added this run), %.0fs" % (counts["events"], added["events"], meta["seconds"]))


def build_anonymized(cfg, st, work, py, pipeline):
    """A second compiled/ + reports/ tree under <workdir>/anonymized with hosts, projects and accounts pseudonymised."""
    salt = cfg.setdefault("anonymize", {}).get("salt")
    if not salt:
        salt = cfg["anonymize"]["salt"] = secrets.token_hex(16)
        save_config(cfg)
    an = anonymize.Anonymizer(salt, os.path.join(home_dir(), "anonymize-map.json"))  # the map is written 0600 by the anonymiser
    root = os.path.join(work, "anonymized")
    export = os.path.join(root, "store-export")
    scans = os.path.join(root, "scans")
    compiled = os.path.join(root, "compiled")
    for d in (export, scans, compiled):
        os.makedirs(d, exist_ok=True)
    ev = os.path.join(export, "events.anon.jsonl")
    se = os.path.join(export, "sessions.anon.jsonl")
    n = 0
    # the exports and config copies are pseudonymised, but the tree still describes the owner's machines and accounts
    # (the pseudonyms map back through anonymize-map.json), so every file is created owner-only like the store itself
    with open_private(ev) as fh:
        for e in st.iter_events():
            fh.write(json.dumps(an.event(e)) + "\n")
            n += 1
    with open_private(se) as fh:
        for s in st.iter_table("sessions"):
            fh.write(json.dumps(an.session_row(s)) + "\n")
    # inventories: one anonymised copy per real host
    import glob as _glob
    for p in _glob.glob(os.path.join(work, "scans", "*", "inventory.*.json")):
        with open(p, encoding="utf-8") as fh:
            inv = an.inventory(json.load(fh))
        d = os.path.join(scans, inv["host"])
        os.makedirs(d, exist_ok=True)
        write_json_private(os.path.join(d, "inventory.%s.json" % inv["host"]), inv)
    with open(cfg["accounts_path"], encoding="utf-8") as fh:
        AC = json.load(fh)
    acc_path = os.path.join(root, "accounts.json")
    write_json_private(acc_path, an.accounts(AC))
    with open(cfg["report_config_path"], encoding="utf-8") as fh:
        rc = json.load(fh)
    rc["hosts"] = {}
    rc.pop("claude_primary_host", None)
    rc["dashboard_excluded_note"] = ""
    rc["title"] = (rc.get("title") or "AI coding-agent usage study") + " (anonymised for publication)"
    rc.setdefault("extra_limitations", []).append("Anonymised: host names, working directories, session ids and account identities are replaced by salted pseudonyms; source paths and prompts are removed.")
    rc_path = os.path.join(root, "report_config.json")
    write_json_private(rc_path, rc)
    an.save_map()
    with open(cfg["pricing_path"], encoding="utf-8") as fh:
        pricing = json.load(fh)
    pricing_anon = {"_comment": "Price tables only; operator notes removed for publication.", "models": pricing.get("models", {}), "fallback_by_tool": pricing.get("fallback_by_tool", {})}
    for k in ("as_of", "sources", "currency"):
        if k in pricing:
            pricing_anon[k] = pricing[k]
    if isinstance(pricing.get("subscriptions"), dict):  # keep plan names and prices, drop the evidence notes
        pricing_anon["subscriptions"] = {t: {"name": v.get("name"), "monthly_usd": v.get("monthly_usd")} for t, v in pricing["subscriptions"].items() if isinstance(v, dict)}
    pricing_path = os.path.join(root, "pricing.json")
    write_json_private(pricing_path, pricing_anon)
    run([py, os.path.join(HERE, "compile_ai_logs.py"), "report", "--events", ev, "--sessions", se, "--inventory", os.path.join(scans, "*", "inventory.*.json"),
         "--pricing", pricing_path, "--accounts", acc_path, "--out-dir", compiled])
    manifest = {"_comment": "generated for the anonymised build", "workdir": ".", "timezone": cfg.get("timezone", "UTC"), "package_prefix": cfg.get("package_prefix", "AI_Usage_Ledger") + "_anonymized",
                "pricing": pricing_path, "accounts": acc_path, "report_config": rc_path, "hosts": []}
    mpath = os.path.join(root, "manifest.json")
    write_json_private(mpath, manifest)
    run([py, pipeline, "--manifest", mpath, "--only", "analyze,build"])
    print("anonymised copy: %s (%d events; private map at %s)" % (root, n, os.path.join(home_dir(), "anonymize-map.json")))
    return root


def do_status(args):
    cfg = load_config()
    if cfg is None:
        print("not initialised; run: python3 scripts/ledger.py init")
        return
    st = ledger_store.Store.open(cfg["store"]["kind"], cfg["store"]["path"])
    print("config:   %s (initialised %s)" % (config_path(), cfg.get("initialized_at")))
    print("store:    %s  %s" % (cfg["store"]["kind"], cfg["store"]["path"]))
    print("counts:   %s" % json.dumps(st.counts()))
    lr = st.last_run()
    print("last run: %s" % (json.dumps({k: lr[k] for k in ("finished_at", "seconds", "added") if k in lr}) if lr else "never"))
    print("workdir:  %s" % cfg["workdir"])
    print("brand:    %s · %s · accent %s · theme %s" % (cfg["branding"].get("name"), cfg["branding"].get("tagline"), cfg["branding"].get("accent"), cfg.get("theme")))
    sch = cfg.get("schedule") or {}
    print("schedule: %s%s%s" % (sch.get("frequency", "none"), (" at %s" % sch.get("time")) if sch.get("frequency", "none") != "none" else "", (" (consented %s)" % sch.get("installed_at")) if sch.get("installed_at") else ""))
    schedule.status(home_dir())
    print("          remove with: python3 scripts/ledger.py schedule remove")
    print("anonymise on every run: %s" % ("yes" if (cfg.get("anonymize") or {}).get("on_every_run") else "no"))
    print("prompt capture: %s" % ("on (prompt text is stored; query prompts / prompt-count search it)" if prompt_capture(cfg) else "off (counts and tokens only; enable with --set prompts.capture=y)"))
    arc = cfg.get("archive") or {}
    if arc.get("raw_logs"):
        try:
            ar = ledger_archive.Archive(arc["path"], compress=arc.get("compress", True))
            s_ = ar.status()
            ar.close()
            print("archive:  %s files, %.2f GB original, %.2f GB on disk at %s" % (sum(h["files"] for h in s_["hosts"]), sum(h["bytes_original"] for h in s_["hosts"]) / 1e9, s_["bytes_on_disk"] / 1e9, arc["path"]))
        except Exception as ex:
            print("archive:  enabled, not readable yet (%s)" % ex)
    else:
        print("archive:  off (raw logs are not kept; enable with --set archive.raw_logs=y)")
    try:
        with open(cfg["manifest_path"], encoding="utf-8") as fh:
            m = json.load(fh)
        print("hosts:    %s" % ", ".join("%s(%s)" % (h["name"], h.get("kind")) for h in m.get("hosts", [])))
    except Exception:
        print("hosts:    manifest not written yet")
    st.close()


def do_export(args):
    cfg = load_config()
    if cfg is None:
        raise SystemExit("not initialised; run init first")
    st = ledger_store.Store.open(cfg["store"]["kind"], cfg["store"]["path"])
    if args.anonymize:
        if args.table == "prompts":
            raise SystemExit("prompts are never exported anonymised; they contain the user's own text")
        an = anonymize.Anonymizer(cfg.setdefault("anonymize", {}).get("salt") or secrets.token_hex(16))
        rows = (an.event(e) for e in st.iter_events()) if args.table == "events" else (an.session_row(s) for s in st.iter_table("sessions"))
        n = ledger_store.export_rows(rows, args.table, args.format, args.out)
    else:
        n = ledger_store.export_table(st, args.table, args.format, args.out)
    st.close()
    print("wrote %d %s to %s%s" % (n, args.table, args.out, " (anonymised)" if args.anonymize else ""))


def do_schedule(args):
    cfg = load_config()
    if cfg is None:
        raise SystemExit("not initialised; run init first")
    sch = cfg.setdefault("schedule", {"frequency": "none", "time": "03:00", "weekday": "mon"})
    if args.action == "install":
        freq = args.frequency or sch.get("frequency") or "daily"
        if freq == "none":
            freq = "daily"
        t = args.time or sch.get("time") or "03:00"
        wd = args.weekday or sch.get("weekday") or "mon"
        flags = ["anonymize"] if cfg.get("anonymize", {}).get("on_every_run") else []
        if cfg.get("archive", {}).get("raw_logs"):
            flags.append("archive")
        expires = args.expires or sch.get("expires")
        rc = schedule.install(home_dir(), sys.executable, freq, t, wd, flags, args.dry_run, expires, cfg.get("manifest_path"), cfg.get("workdir"))
        if rc == 0 and not args.dry_run:
            sch.update({"frequency": freq, "time": t, "weekday": wd, "expires": expires, "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "consent": os.path.join(home_dir(), schedule.CONSENT_FILE)})
            save_config(cfg)
        return rc
    if args.action == "consent":
        flags = ["anonymize"] if cfg.get("anonymize", {}).get("on_every_run") else []
        if cfg.get("archive", {}).get("raw_logs"):
            flags.append("archive")
        freq = args.frequency or sch.get("frequency") or "daily"
        mat = schedule.material_config(home_dir(), sys.executable, freq if freq != "none" else "daily", args.time or sch.get("time") or "03:00", args.weekday or sch.get("weekday") or "mon", flags, args.expires or sch.get("expires"), cfg.get("manifest_path"))
        print(schedule.disclosure(home_dir(), mat, cfg.get("workdir")))
        print(json.dumps({"approved_by": "<your name>", "approved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "config_hash": schedule.config_hash(mat), "sensitive_acknowledged": bool(schedule.sensitive_reasons(mat))}, indent=2))
        print("write that JSON to %s to consent without a terminal, then run `schedule install`" % schedule.consent_path(home_dir()))
        return 0
    if args.action == "remove":
        rc = schedule.remove(home_dir(), args.dry_run)
        if rc == 0 and not args.dry_run:
            sch.update({"frequency": "none", "installed_at": None})
            save_config(cfg)
        return rc
    return schedule.status(home_dir())


def do_archive(args):
    cfg = load_config()
    if cfg is None:
        raise SystemExit("not initialised; run init first")
    arc = cfg.get("archive") or {}
    cmd = [sys.executable, os.path.join(HERE, "ledger_archive.py"), "--archive", arc.get("path") or os.path.join(home_dir(), "archive")]
    if not arc.get("compress", True):
        cmd.append("--no-compress")
    return subprocess.run(cmd + args.rest).returncode


def do_query(args):
    return subprocess.run([sys.executable, os.path.join(HERE, "ledger_query.py")] + args.rest).returncode


IDENTITY_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def publish_check(target, accounts_path=None, extra_terms=()):
    """Scan a directory (or file) that is about to leave the machine for e-mails, account identifiers, organisation
    names, credential-file paths and known host names. Returns a list of (file, kind, snippet)."""
    # each term is a compiled pattern: identifiers need boundaries so an 8-digit account prefix does not match inside
    # a number and a host name does not match inside an unrelated word; host names match case-sensitively
    terms = []

    def add(kind, value, boundary=None, flags=re.IGNORECASE):
        v = str(value or "").strip()
        if len(v) < (2 if boundary else 4):  # bounded terms may be short ("dev", "IBM"); substring terms must not be
            return
        pat = re.escape(v)
        if boundary == "alnum":
            pat = r"(?<![0-9A-Za-z])" + pat + r"(?![0-9A-Za-z])"
        elif boundary == "word":
            pat = r"\b" + pat + r"\b"
        terms.append((kind, re.compile(pat, flags)))

    if accounts_path and os.path.isfile(accounts_path):
        try:
            with open(accounts_path, encoding="utf-8") as fh:
                AC = json.load(fh)
            for key, v in (AC.get("accounts") or {}).items():
                for e in v.get("emails") or []:
                    add("account e-mail", e)
                for o in v.get("orgs") or []:
                    add("organisation name", o, "word")
                if v.get("chatgpt_account_id_prefix"):
                    add("account id prefix", v["chatgpt_account_id_prefix"], "alnum")
                if ":" in key and not key.endswith((":provider", ":usage-based", ":api-keys")):
                    add("account key", key, "alnum")
        except Exception:
            pass
    for t in extra_terms:
        add("host name or operator term", t, "word", 0)
    # a credential *file* counts only when it appears as a path (a separator before the name); generic documentation
    # that merely names `.claude.json` is not a leak. Secret-bearing keys count anywhere and are reported without values.
    cred_path_re = re.compile(r"[\\/][^\s\"'`<>]{0,200}?(auth\.json|\.credentials\.json|\.claude\.json)\b", re.IGNORECASE)
    secret_key_re = re.compile(r"\b(id_token|access_token|refresh_token|OPENAI_API_KEY|ANTHROPIC_API_KEY|api_key)\b\s*[\"':=]", re.IGNORECASE)
    findings = []
    texts = []  # (display name, text)
    binary = (".png", ".sqlite", ".gz", ".db", ".jpg", ".jpeg", ".ico", ".woff", ".woff2", ".ttf")

    def document_text(path):
        """Text of a DOCX (its XML parts) or a PDF (pypdf when installed); None when it cannot be read."""
        low = path.lower()
        if low.endswith(".docx"):
            import zipfile
            import xml.etree.ElementTree as ET
            try:
                with zipfile.ZipFile(path) as z:
                    parts = [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml")]
                    lines = []
                    for n in parts:
                        root = ET.fromstring(z.read(n))
                        # adjacent runs inside one paragraph are joined with nothing between them, so an identifier
                        # split across <w:t> elements ("person@" + "corp.example") is seen whole
                        for para in root.iter():
                            if para.tag.endswith("}p"):
                                lines.append("".join(t.text or "" for t in para.iter() if t.tag.endswith("}t")))
                        if not lines:
                            lines.append("".join(t.text or "" for t in root.iter() if t.tag.endswith("}t")))
                return "\n".join(lines)
            except Exception:
                return None
        if low.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(path)
                text = " ".join((pg.extract_text() or "") for pg in reader.pages)
                if len(reader.pages) and len(text.strip()) < 20:
                    return None  # pages without extractable text (scanned / image-only): cannot be checked
                return text
            except ImportError:
                return None
            except Exception:
                return None
        return None

    def add_file(path):
        if path.lower().endswith(binary):
            return
        if path.lower().endswith((".pdf", ".docx")):
            t = document_text(path)
            if t is None:
                findings.append((path, "unscannable document", "install pypdf to scan PDFs, or check the Markdown source instead"))
            else:
                texts.append((path, t))
            return
        if path.lower().endswith(".zip"):
            import zipfile
            try:
                with zipfile.ZipFile(path) as z:
                    for info in z.infolist():
                        if info.is_dir() or info.filename.lower().endswith(binary):
                            continue
                        if info.filename.lower().endswith((".pdf", ".docx")):
                            findings.append((path + "!" + info.filename, "unscannable document", "extract the archive and check the document, or its Markdown source"))
                            continue
                        texts.append((path + "!" + info.filename, z.read(info).decode("utf-8", "replace")))
            except zipfile.BadZipFile:
                findings.append((path, "unreadable archive", "not a zip file"))
            return
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                texts.append((path, fh.read()))
        except OSError:
            pass

    if os.path.isdir(target):
        for dp, _, fns in os.walk(target):
            for fn in fns:
                add_file(os.path.join(dp, fn))
    else:
        add_file(target)
    for f, text in texts:
        for m in IDENTITY_RE.finditer(text):
            if not m.group(0).lower().endswith(("example.com", "example.net", "example.org")):
                findings.append((f, "e-mail address", m.group(0)))
                break
        for kind, rx in terms:
            m = rx.search(text)
            if m:
                findings.append((f, kind, text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")))
        m = cred_path_re.search(text)
        if m:
            findings.append((f, "credential file path", "path ending in %s (value not shown)" % m.group(1)))
        m = secret_key_re.search(text)
        if m:
            findings.append((f, "secret-bearing key", "%s present (value not shown)" % m.group(1)))
    return findings


def do_publish_check(args):
    cfg = load_config()
    target = args.path
    if not target and cfg:
        target = os.path.join(cfg["workdir"], "anonymized") if os.path.isdir(os.path.join(cfg["workdir"], "anonymized")) else os.path.join(cfg["workdir"], "reports")
    if not target or not os.path.exists(target):
        raise SystemExit("give a directory or file to check (e.g. the study package or the anonymised tree)")
    hosts = []
    if cfg:
        try:
            with open(cfg["manifest_path"], encoding="utf-8") as fh:
                hosts = [h["name"] for h in json.load(fh).get("hosts", [])]
        except Exception:
            pass
    findings = publish_check(target, cfg["accounts_path"] if cfg else None, hosts + list(args.term or []))
    if not findings:
        print("publish-check: no e-mail, account identifier, organisation name, host name, credential-file path or secret-bearing key found in %s" % target)
        return 0
    seen = set()
    import safety
    for f, kind, snip in findings:
        k = (f, kind)
        if k in seen:
            continue
        seen.add(k)
        shown = os.path.relpath(f, target) if os.path.isdir(target) and not f.startswith(target + "!") else f
        # snippets are lines from the files being checked: strip escape sequences and controls before they reach the terminal
        print("%-28s %s\n    %s" % (kind, safety.clean_for_terminal(shown, limit=300), safety.clean_for_terminal(snip.strip()[:140], limit=140)))
    print("publish-check: %d finding(s); this content identifies people, accounts or machines. Use the anonymised copy (ledger.py run --anonymize) before publishing." % len(seen))
    return 1


def do_doc(args):
    cmd = [sys.executable, os.path.join(HERE, "render_ledger_doc.py")] + args.rest
    r = subprocess.run(cmd)
    return r.returncode


def do_report(args):
    """Render a bounded report from recorded events without refreshing sources."""
    return subprocess.run([sys.executable, os.path.join(HERE, "scoped_report.py")] + args.rest).returncode


def do_reinit(args):
    cfg = load_config()
    if cfg and os.path.exists(cfg["store"]["path"]):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        moved = cfg["store"]["path"].rstrip("/\\") + ".before-reinit-" + stamp
        shutil.move(cfg["store"]["path"], moved)
        print("previous store kept at %s" % moved)
    args.reinit = True
    onboard(args)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init", help="first-run onboarding")
    i.add_argument("--yes", action="store_true", help="accept defaults without prompting (for agents and CI); branding stays neutral unless --brand-preset or --set brand.* is given")
    i.add_argument("--brand-preset", help="apply a named brand preset explicitly (e.g. completetech)")
    i.add_argument("--set", action="append", help="override a preference, e.g. --set brand.name=Acme --set store.kind=json")
    i.add_argument("--reinit", action="store_true", help=argparse.SUPPRESS)
    i.set_defaults(fn=onboard)
    r = sub.add_parser("run", help="scan, append to the store, rebuild dashboard and study")
    r.add_argument("--hosts", help="comma list of host names to scan")
    r.add_argument("--tools", help="comma list of tools to scan (e.g. copilot-cli,opencode,openclaw); others are left out of this run")
    r.add_argument("--skip-tools", help="comma list of tools to leave out of this run (e.g. codex,claude-code)")
    r.add_argument("--no-scan", action="store_true", help="rebuild from the store without rescanning")
    r.add_argument("--no-detect", action="store_true", help="do not refresh the manifest from detection")
    r.add_argument("--anonymize", action="store_true", help="also build the anonymised copy under <workdir>/anonymized")
    r.add_argument("--archive", action="store_true", help="also archive the raw log files this once (archive.raw_logs=y does it every run)")
    r.add_argument("--until", help="YYYY-MM-DD: used by scheduled wrappers; after this date the run does nothing and removes the schedule")
    r.add_argument("--scheduled", action="store_true", help="used by the scheduled wrapper: no host re-detection, and the run refuses unless the consented configuration still matches")
    r.set_defaults(fn=do_run)
    s = sub.add_parser("status")
    s.set_defaults(fn=do_status)
    e = sub.add_parser("export")
    e.add_argument("--table", default="events", choices=["events", "sessions", "prompts"])
    e.add_argument("--format", default="csv", choices=["csv", "json", "jsonl"])
    e.add_argument("--out", required=True)
    e.add_argument("--anonymize", action="store_true", help="pseudonymise hosts, sessions, projects and accounts; drop paths")
    e.set_defaults(fn=do_export)
    sc = sub.add_parser("schedule", help="install, remove or show the scheduled refresh (Task Scheduler / cron)")
    sc.add_argument("action", choices=["install", "remove", "status", "consent"])
    sc.add_argument("--expires", help="YYYY-MM-DD after which the scheduled run stops and removes the entry")
    sc.add_argument("--frequency", choices=["daily", "weekly", "monthly"])
    sc.add_argument("--time", help="HH:MM local time")
    sc.add_argument("--weekday", choices=sorted(schedule.WEEKDAYS))
    sc.add_argument("--dry-run", action="store_true")
    sc.set_defaults(fn=do_schedule)
    arp = sub.add_parser("archive", help="raw-log archive: status, list, grep, restore (arguments pass through to ledger_archive.py)")
    arp.add_argument("rest", nargs=argparse.REMAINDER)
    arp.set_defaults(fn=do_archive)
    qp = sub.add_parser("query", help="detailed questions over the store and archive (arguments pass through to ledger_query.py)")
    qp.add_argument("rest", nargs=argparse.REMAINDER)
    qp.set_defaults(fn=do_query)
    pc = sub.add_parser("publish-check", help="scan a package, directory or file for e-mails, account ids, organisation names, host names and credential references before it leaves the machine")
    pc.add_argument("path", nargs="?", help="default: the anonymised tree if present, else the reports directory")
    pc.add_argument("--term", action="append", help="extra string that must not appear (repeatable)")
    pc.set_defaults(fn=do_publish_check)
    dc = sub.add_parser("doc", help="render a ledger document; all arguments pass through to render_ledger_doc.py")
    dc.add_argument("rest", nargs=argparse.REMAINDER)
    dc.set_defaults(fn=do_doc)
    rp = sub.add_parser("report", help="render usage and dollar metrics for an exact time window from the store")
    rp.add_argument("rest", nargs=argparse.REMAINDER)
    rp.set_defaults(fn=do_report)
    ri = sub.add_parser("reinit", help="fresh onboarding; the previous store is kept with a timestamp")
    ri.add_argument("--yes", action="store_true")
    ri.add_argument("--brand-preset")
    ri.add_argument("--set", action="append")
    ri.set_defaults(fn=do_reinit)
    if len(sys.argv) > 1 and sys.argv[1] == "doc":  # everything after `doc` belongs to the renderer, including --list
        sys.exit(subprocess.run([sys.executable, os.path.join(HERE, "render_ledger_doc.py")] + sys.argv[2:]).returncode)
    if len(sys.argv) > 1 and sys.argv[1] == "query":
        sys.exit(do_query(argparse.Namespace(rest=sys.argv[2:])))
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        sys.exit(do_report(argparse.Namespace(rest=sys.argv[2:])))
    if len(sys.argv) > 1 and sys.argv[1] == "archive":
        sys.exit(do_archive(argparse.Namespace(rest=sys.argv[2:])))
    a = ap.parse_args()
    rc = a.fn(a)
    if isinstance(rc, int) and rc:
        sys.exit(rc)


if __name__ == "__main__":
    main()
