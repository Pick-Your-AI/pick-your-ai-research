#!/usr/bin/env python3
"""
detect_hosts.py - find every AI coding-agent log root and account on this machine, per OS.

    python3 detect_hosts.py                 # human-readable summary
    python3 detect_hosts.py --json          # manifest hosts + draft accounts + notes as JSON
    python3 detect_hosts.py --all-profiles  # also look at other user profiles and other drives
    python3 detect_hosts.py --no-wsl        # skip WSL distro probing on Windows

Knows the default directories and environment overrides for the tools in references/harness-catalog.md
on Windows, macOS, Linux and WSL, including VS Code / Cursor / VSCodium global storage for the Cline
family. Emits host entries in the manifest schema consumed by run_pipeline.py and a draft accounts.json
from the credential files it can read (identity claims only; tokens are never printed or stored).

Standard library only.
"""
import goose_usage
import argparse
import base64
import glob
import json
import os
import platform
import posixpath
import subprocess
import sys

IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"


def expand(p):
    return os.path.expandvars(os.path.expanduser(p))


def first_existing(paths):
    for p in paths:
        p = expand(p)
        if p and os.path.exists(p):
            return p
    return None


# ----------------------------------------------------------------------------
# per-OS root locations
# ----------------------------------------------------------------------------

def vscode_global_storage_dirs(home_fs, posix=False):
    """Every <app>/User/globalStorage directory for VS Code-family editors under a home (as seen on this filesystem)."""
    apps = ["Code", "Code - Insiders", "VSCodium", "Cursor", "Windsurf", "Trae", "Kiro", "Antigravity"]
    J = posixpath.join if posix else os.path.join
    if posix:  # a WSL or Linux home: desktop editors plus the remote-server storage used by VS Code Remote / WSL
        bases = [J(home_fs, ".config", a, "User", "globalStorage") for a in apps] + [J(home_fs, ".vscode-server", "data", "User", "globalStorage"), J(home_fs, ".cursor-server", "data", "User", "globalStorage")]
    elif IS_WIN:
        bases = [J(home_fs, "AppData", "Roaming", a, "User", "globalStorage") for a in apps]
    elif IS_MAC:
        bases = [J(home_fs, "Library", "Application Support", a, "User", "globalStorage") for a in apps]
    else:
        bases = [J(home_fs, ".config", a, "User", "globalStorage") for a in apps] + [J(home_fs, ".vscode-server", "data", "User", "globalStorage")]
    return [b for b in bases if os.path.isdir(b)]


CLINE_FAMILY = {"cline": "saoudrizwan.claude-dev", "roo-code": "rooveterinaryinc.roo-cline", "kilo-code": "kilocode.kilo-code"}


def detect_roots(home, prefix="", use_env=False):
    """Return (host_fields, found_summary) for a home directory.

    prefix: a share root such as //wsl$/Ubuntu that makes a foreign home readable here (paths are then POSIX joined).
    use_env: honour CODEX_HOME-style overrides (only meaningful for the profile this process runs as).
    """
    posix = bool(prefix) or not IS_WIN
    J = posixpath.join if posix else os.path.join

    def H(*parts):
        return J(prefix + home, *parts)

    def env(name):
        v = os.environ.get(name) if use_env else None
        return expand(v) if v else None

    h = {}
    found = []

    def add(key, path, label):
        if path and os.path.exists(path):
            h.setdefault(key, []).append(path)
            found.append("%s: %s" % (label, path))

    for path in goose_usage.candidate_roots(home, "linux" if prefix else ("win32" if IS_WIN else "darwin" if IS_MAC else "linux"),
                                            dict(os.environ) if use_env else {},
                                            roaming=goose_usage.windows_roaming_dir() if IS_WIN and use_env and not prefix else None):
        add("goose_roots", prefix + path if prefix else path, "Goose sessions (native usage)")


    codex = env("CODEX_HOME") or H(".codex")
    if os.path.isdir(J(codex, "sessions")) or os.path.isdir(J(codex, "archived_sessions")):
        add("codex_roots", codex, "Codex")
        if os.path.isfile(J(codex, "state_5.sqlite")):
            h["codex_sqlite"] = J(codex, "state_5.sqlite")
    claude = H(".claude")
    if os.path.isdir(J(claude, "projects")):
        add("claude_roots", claude, "Claude Code")
        if os.path.isfile(J(claude, "stats-cache.json")):
            h["claude_stats_cache"] = J(claude, "stats-cache.json")
    copilot = env("COPILOT_HOME") or H(".copilot")
    if os.path.isdir(J(copilot, "session-state")):
        add("copilot_roots", copilot, "Copilot CLI")
    gemini = env("GEMINI_DATA_DIR") or H(".gemini", "tmp")
    if os.path.isdir(gemini):
        add("gemini_roots", gemini, "Gemini CLI")
    qwen = env("QWEN_DATA_DIR") or H(".qwen", "history")
    if os.path.isdir(qwen):
        add("qwen_roots", qwen, "Qwen Code")
    for k in (env("KIMI_DATA_DIR"), env("KIMI_SHARE_DIR"), H(".kimi"), H(".kimi-code")):
        if k and os.path.isdir(J(k, "sessions")):
            add("kimi_roots", k, "Kimi Code")
    vibe = env("VIBE_HOME") or H(".vibe")
    if os.path.isdir(J(vibe, "logs", "session")):
        add("vibe_roots", vibe, "Mistral Vibe")
    cont = H(".continue")
    if os.path.isdir(J(cont, "dev_data")):
        add("continue_roots", cont, "Continue")
    pi = env("PI_AGENT_DIR") or H(".pi", "agent", "sessions")
    if os.path.isdir(pi):
        add("pi_roots", pi, "pi")
    for db in (os.path.join(env("OPENCODE_DATA_DIR") or "", "opencode.db") if env("OPENCODE_DATA_DIR") else None,
               H(".local", "share", "opencode", "opencode.db")):
        if db and os.path.isfile(db):
            h.setdefault("opencode_dbs", []).append(db)
            found.append("opencode: %s" % db)
    openclaw = env("OPENCLAW_DIR") or H(".openclaw")
    if os.path.isdir(J(openclaw, "agents")):
        add("openclaw_roots", openclaw, "OpenClaw")
    for gs in vscode_global_storage_dirs(prefix + home, posix=posix):
        for tool, ext in CLINE_FAMILY.items():
            d = J(gs, ext)
            if os.path.isdir(J(d, "tasks")):
                h.setdefault("cline_roots", []).append("%s=%s" % (tool, d))
                found.append("%s: %s" % (tool, d))
    cline_cli = H(".cline")
    if os.path.isdir(J(cline_cli, "data")) or os.path.isdir(J(cline_cli, "tasks")):
        h.setdefault("cline_roots", []).append("cline=%s" % cline_cli)
        found.append("Cline CLI: %s" % cline_cli)
    for tool, path in (("codebuff", env("CODEBUFF_DATA_DIR") or H(".config", "manicode")), ("droid", env("DROID_SESSIONS_DIR") or H(".factory", "sessions")),
                       ("amp", env("AMP_DATA_DIR") or H(".local", "share", "amp")), ("lmstudio", H(".lmstudio", "conversations")), ("openhands", H(".openhands")),
                       ("grok", env("GROK_HOME") or H(".grok")), ("hermes", env("HERMES_HOME") or H(".hermes")), ("zcode", env("ZCODE_HOME") or H(".zcode"))):
        if path and os.path.isdir(path):
            h.setdefault("generic_roots", []).append("%s=%s" % (tool, path))
            found.append("%s (generic): %s" % (tool, path))
    # Candidate discovery is not authorization. Adding support must not silently
    # enable a new source in a previously consented manifest or scheduled scan.
    mini_dirs = [env("MSWEA_GLOBAL_CONFIG_DIR"), H(".config", "mini-swe-agent"),
                 H("Library", "Application Support", "mini-swe-agent"), H("AppData", "Local", "mini-swe-agent", "mini-swe-agent"),
                 J(env("XDG_CONFIG_HOME"), "mini-swe-agent") if env("XDG_CONFIG_HOME") else None,
                 J(env("LOCALAPPDATA"), "mini-swe-agent", "mini-swe-agent") if env("LOCALAPPDATA") else None]
    for directory in dict.fromkeys(d for d in mini_dirs if d):
        if os.path.isfile(J(directory, "last_mini_run.traj.json")):
            found.append("mini-SWE-agent candidate (disabled; requires mini_swe_roots consent): %s" % J(directory, "last_mini_run.traj.json"))
    return h, found


# ----------------------------------------------------------------------------
# hosts: local profiles, other profiles/drives, WSL distros
# ----------------------------------------------------------------------------

def local_home():
    return os.path.expanduser("~")


def other_profiles():
    """Other readable user homes on this machine (and on other drives on Windows)."""
    homes = []
    me = os.path.abspath(local_home())
    if IS_WIN:
        drives = [d + ":\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.isdir(d + ":\\")]
        for d in drives:
            for p in glob.glob(os.path.join(d, "Users", "*")):
                if os.path.isdir(p) and os.path.abspath(p) != me and os.path.basename(p) not in ("Public", "Default", "Default User", "All Users"):
                    homes.append(p)
    elif IS_MAC:
        homes = [p for p in glob.glob("/Users/*") if os.path.isdir(p) and os.path.abspath(p) != me and os.path.basename(p) != "Shared"]
    else:
        homes = [p for p in glob.glob("/home/*") if os.path.isdir(p) and os.path.abspath(p) != me]
    return homes


def wsl_distros():
    if not IS_WIN:
        return []
    try:
        out = subprocess.run(["wsl.exe", "-l", "-q"], capture_output=True, timeout=20).stdout
    except Exception:
        return []
    names = [n.strip() for n in out.decode("utf-16-le", "ignore").replace("\x00", "").splitlines() if n.strip()]
    return [n for n in names if "docker" not in n.lower()]


def wsl_homes(distro):
    """List /home/* inside a distro via the \\wsl$ share (works even when wsl.exe is flaky)."""
    share = "//wsl$/%s" % distro
    homes = []
    for p in glob.glob(os.path.join(share, "home", "*")):
        if os.path.isdir(p):
            homes.append(("/home/" + os.path.basename(p), p))
    return share, homes


def _identity(path):
    """(device, inode) of a directory, so the same directory reached by two paths is recognised."""
    try:
        st = os.stat(path)
        return (st.st_dev, st.st_ino) if st.st_ino else None
    except OSError:
        return None


def _root_identities(h):
    ids = set()
    for key, val in h.items():
        if key.endswith("_roots") or key.endswith("_dbs"):
            for v in val:
                i = _identity(v.split("=", 1)[1] if "=" in v and key in ("cline_roots", "generic_roots") else v)
                if i:
                    ids.add(i)
    return ids


def detect_hosts(all_profiles=False, probe_wsl=True):
    hosts, notes = [], []
    seen = set()
    name = platform.node().lower().replace(" ", "-") or "local"
    h, found = detect_roots(local_home(), use_env=True)
    if h:
        hosts.append(dict({"name": name, "kind": "local", "_found": found}, **h))
        seen |= _root_identities(h)
    else:
        notes.append("no agent logs under %s" % local_home())
    if all_profiles:
        for home in other_profiles():
            h, found = detect_roots(home)
            ids = _root_identities(h)
            if h and ids and ids <= seen:
                notes.append("%s is the same volume as an already detected profile (mapped drive or symlink); skipped" % home)
                continue
            if h:
                seen |= ids
                label = "%s-%s" % (name, os.path.basename(home).lower())
                if not home.lower().startswith(os.path.splitdrive(local_home())[0].lower()):
                    label = "%s-%s" % (os.path.splitdrive(home)[0].rstrip(":").lower() or "drive", os.path.basename(home).lower())
                hosts.append(dict({"name": label, "kind": "share", "_found": found}, **h))
    if probe_wsl:
        for distro in wsl_distros():
            share, homes = wsl_homes(distro)
            for wsl_home, share_home in homes:
                h, found = detect_roots(wsl_home, prefix=share.rstrip("/"))
                if not h:
                    continue
                # paths were detected through the share; the manifest wants distro-native paths with the share as fallback
                native = {}
                for key, val in h.items():
                    if isinstance(val, list):
                        native[key] = [v.replace(share, "", 1) if "=" not in v else v.split("=", 1)[0] + "=" + v.split("=", 1)[1].replace(share, "", 1) for v in val]
                    else:
                        native[key] = val.replace(share, "", 1)
                hosts.append(dict({"name": "wsl-%s" % distro.lower(), "kind": "wsl", "distro": distro, "python": "python3", "share_fallback": share, "_found": found}, **native))
    return hosts, notes


# ----------------------------------------------------------------------------
# accounts from credential files (claims only)
# ----------------------------------------------------------------------------

def jwt_claims(tok):
    try:
        p = tok.split(".")[1]
        p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p))
    except Exception:
        return {}


CREDENTIAL_FILES = ("auth.json (Codex): chatgpt_account_id prefix, chatgpt_plan_type, last_refresh; with --identifiable also e-mail and organisation titles",
                    ".claude.json (Claude Code): organizationRateLimitTier, organizationType; with --identifiable also the e-mail",
                    ".claude/.credentials.json (Claude Code): subscriptionType only")


def credential_warning(paths, identifiable):
    """Say what is about to be read and what will be kept, before any credential file is opened."""
    sys.stderr.write("Reading credential files to label accounts (%s). Tokens and keys are never kept or shown.\n" % ("identifiable: e-mails and organisation names retained" if identifiable else "minimised: pseudonymous account ids and plan types only"))
    for line in CREDENTIAL_FILES:
        sys.stderr.write("  %s\n" % line)
    for p in paths:
        sys.stderr.write("  file: %s\n" % p)


def read_codex_account(codex_root, identifiable=False):
    """Extract only the claims needed for attribution and pricing from Codex's auth.json.

    Kept: an 8-character prefix of the ChatGPT account id (pseudonymous), the plan type, the refresh time.
    Kept only with identifiable=True: e-mail and organisation titles. Tokens and API keys are never retained."""
    p = os.path.join(codex_root, "auth.json")
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            d = json.load(fh)
    except Exception:
        return None
    tokens = d.get("tokens") or {}
    claims = jwt_claims(tokens.get("id_token") or tokens.get("access_token") or "")
    has_api_key = bool(d.get("OPENAI_API_KEY"))
    last_refresh = d.get("last_refresh")
    del d, tokens  # drop the credential object as soon as the claims are out
    auth = claims.get("https://api.openai.com/auth", {}) or {}
    prof = claims.get("https://api.openai.com/profile", {}) or {}
    acct = (auth.get("chatgpt_account_id") or "")[:8]
    plan = auth.get("chatgpt_plan_type")
    email = (prof.get("email") or claims.get("email")) if identifiable else None
    orgs = [o.get("title") for o in auth.get("organizations", []) if isinstance(o, dict)] if identifiable else []
    del claims, auth, prof
    if not acct and not has_api_key:
        return None
    return {"id": "codex:%s" % (acct or "api-key"), "provider": "openai", "label": email or ("API key" if has_api_key and not acct else "ChatGPT account %s" % acct),
            "emails": [email] if email else [], "chatgpt_account_id_prefix": acct, "orgs": orgs, "plan_type": plan,
            "plan": {"pro": "ChatGPT Pro", "plus": "ChatGPT Plus", "team": "ChatGPT Team", "business": "ChatGPT Business", "enterprise": "ChatGPT Enterprise"}.get(plan, "usage-based (API key)" if has_api_key and not plan else (plan or "unknown")),
            "monthly_usd": {"pro": 200, "plus": 20, "team": 30, "business": 30}.get(plan, 0),
            "evidence": ("%s (last_refresh %s)" % (p, last_refresh)) if identifiable else ("auth.json on this host (last_refresh %s)" % last_refresh)}


def read_claude_account(home, identifiable=False):
    """Extract the plan tier from Claude Code's account files; the e-mail is kept only with identifiable=True,
    otherwise the account is keyed by a short hash of it (stable, pseudonymous)."""
    import hashlib
    for p in (os.path.join(home, ".claude.json"),):
        if not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                d = json.load(fh)
        except Exception:
            continue
        oa = d.get("oauthAccount") or {}
        del d
        email = oa.get("emailAddress")
        if not email:
            continue
        tier = oa.get("organizationRateLimitTier") or ""
        org_type = oa.get("organizationType")
        del oa
        cred = os.path.join(home, ".claude", ".credentials.json")
        sub = None
        if os.path.isfile(cred):
            try:
                with open(cred, encoding="utf-8", errors="replace") as fh:
                    sub = (json.load(fh).get("claudeAiOauth") or {}).get("subscriptionType")
            except Exception:
                pass
        plan = {"max_20x": "Claude Max 20x", "max_5x": "Claude Max 5x"}.get("max_20x" if "20x" in tier else "max_5x" if "5x" in tier else "", {"max": "Claude Max", "pro": "Claude Pro"}.get(sub or "", "Claude (tier unknown)"))
        monthly = 200 if "20x" in tier else 100 if "5x" in tier else 20 if sub == "pro" else 0
        pseudo = hashlib.sha256(email.lower().encode("utf-8")).hexdigest()[:8]
        key = ("claude:%s" % email.lower().replace("@", "-at-").replace(".", "-")) if identifiable else ("claude:%s" % pseudo)
        return {"id": key, "provider": "anthropic", "label": email if identifiable else "Claude account %s" % pseudo, "emails": [email] if identifiable else [], "plan": plan, "monthly_usd": monthly,
                "evidence": ("%s oauthAccount (%s, %s)" % (p, org_type, tier)) if identifiable else (".claude.json on this host (%s, %s)" % (org_type, tier))}
    return None


def draft_accounts(hosts, read_credentials=False, identifiable=False, warn=True):
    """Draft accounts.json.

    read_credentials=False (the default): no credential file is opened; each host gets one placeholder account per
    tool ("codex login on <host>") with an unknown plan for the operator to fill in.
    read_credentials=True: auth.json / .claude.json are read for the account id prefix and plan type (a warning
    names the files first); e-mails and organisation titles are kept only with identifiable=True."""
    registry, rules = {}, []
    if read_credentials and warn:
        paths = []
        for h in hosts:
            pref = h.get("share_fallback", "") if h.get("kind") == "wsl" else ""
            paths += [os.path.join(pref + r if pref else r, "auth.json") for r in h.get("codex_roots", [])]
            paths += [os.path.join(os.path.dirname(pref + r if pref else r), ".claude.json") for r in h.get("claude_roots", [])]
        credential_warning([p for p in paths if os.path.isfile(p)], identifiable)
    for h in hosts:
        pref = h.get("share_fallback", "") if h.get("kind") == "wsl" else ""
        if h.get("goose_roots"):
            key = "goose:%s" % h["name"]
            registry.setdefault(key, {"provider": "mixed", "label": "Goose usage on %s" % h["name"],
                                      "plan": "unknown (review provider accounts and billing)", "monthly_usd": 0,
                                      "evidence": "host placeholder; no Goose credential file was read"})
            rules.append({"when": {"tool": "goose", "host": h["name"]}, "account": key, "billing": "unknown", "confidence": "low",
                          "why": "host placeholder only; provider switching and billing are not inferred from current configuration"})
        for root in h.get("codex_roots", []):
            a = read_codex_account(pref + root if pref else root, identifiable) if read_credentials else None
            if a:
                registry.setdefault(a["id"], {k: v for k, v in a.items() if k != "id"})
                rules.append({"when": {"tool": "codex", "host": h["name"]}, "account": a["id"], "billing": "subscription" if a["monthly_usd"] else "usage-based", "confidence": "medium",
                              "why": "current login in %s; assumed for the host's whole history" % (root + "/auth.json")})
            elif not read_credentials:
                key = "codex:%s" % h["name"]
                registry.setdefault(key, {"provider": "openai", "label": "Codex login on %s" % h["name"], "plan": "unknown (set the plan and monthly_usd, or re-run init with accounts.from_credentials=y)", "monthly_usd": 0,
                                          "evidence": "placeholder; credential files were not read"})
                rules.append({"when": {"tool": "codex", "host": h["name"]}, "account": key, "billing": "unknown", "confidence": "low", "why": "placeholder per host; credential files were not read, so the billing is unknown until the plan is filled in"})
        for root in h.get("claude_roots", []):
            home = os.path.dirname(pref + root if pref else root)
            a = read_claude_account(home, identifiable) if read_credentials else None
            if a:
                registry.setdefault(a["id"], {k: v for k, v in a.items() if k != "id"})
                rules.append({"when": {"tool": "claude-code", "host": h["name"]}, "account": a["id"], "billing": "subscription", "confidence": "high", "why": ".claude.json oauthAccount on that host"})
            elif not read_credentials:
                key = "claude:%s" % h["name"]
                registry.setdefault(key, {"provider": "anthropic", "label": "Claude Code login on %s" % h["name"], "plan": "unknown (set the plan and monthly_usd, or re-run init with accounts.from_credentials=y)", "monthly_usd": 0,
                                          "evidence": "placeholder; credential files were not read"})
                rules.append({"when": {"tool": "claude-code", "host": h["name"]}, "account": key, "billing": "unknown", "confidence": "low", "why": "placeholder per host; credential files were not read, so the billing is unknown until the plan is filled in"})
    rules.insert(0, {"when": {"tool": "codex", "plan": "self_serve_business_usage_based"}, "account": "codex:usage-based", "billing": "usage-based", "confidence": "high",
                     "why": "the call itself is stamped usage-based; assign it to the right org in this file if you know it"})
    registry.setdefault("codex:usage-based", {"provider": "openai", "label": "Codex usage-based org", "plan": "usage-based", "monthly_usd": 0, "evidence": "rate_limits.plan_type on the calls"})
    for tool, acct, label in (("openclaw", "openclaw:api-keys", "OpenClaw gateways (API keys / local models)"), ("opencode", "opencode:provider", "opencode provider (own cost column)"),
                              ("copilot-cli", "copilot", "GitHub Copilot"), ("gemini-cli", "gemini", "Gemini CLI / Code Assist"), ("cline", "cline:provider", "Cline provider keys"),
                              ("roo-code", "cline:provider", "Cline provider keys"), ("kilo-code", "cline:provider", "Cline provider keys"), ("aider", "aider:provider", "aider provider keys"),
                              ("kimi", "kimi", "Kimi Code"), ("mistral-vibe", "mistral", "Mistral Vibe"), ("continue", "continue:provider", "Continue provider keys"), ("pi", "pi:provider", "pi provider keys")):
        registry.setdefault(acct, {"provider": "mixed", "label": label, "plan": "usage-based or bundled", "monthly_usd": 0, "evidence": "tool default; edit if a subscription applies"})
        rules.append({"when": {"tool": tool}, "account": acct, "billing": "usage-based", "confidence": "medium", "why": "tool default"})
    # no catch-all rule: a call that matches nothing is reported as `unattributed` (billing unknown) by compile_ai_logs.assign_account
    # rather than silently charged to a real account; the dashboard and study show the count so the operator can add a rule.
    src = ("credential files (identity claims only%s)" % (", identifiable" if identifiable else ", minimised: no e-mails or organisation names")) if read_credentials else "host names only (no credential file was read)"
    return {"_comment": "Drafted by detect_hosts.py from %s. Review labels, prices and rules; first match wins. This file names accounts: it is written owner-only and is not copied into study packages unless package_accounts is true." % src,
            "_sensitivity": "account metadata" if read_credentials else "placeholders",
            "_source": ("credential files, identifiable" if identifiable else "credential files, minimised") if read_credentials else "host placeholders", "accounts": registry, "rules": rules}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all-profiles", action="store_true", help="also scan other user profiles and other drives")
    ap.add_argument("--no-wsl", action="store_true")
    ap.add_argument("--read-credentials", action="store_true", help="read auth.json / .claude.json for account id prefixes and plan types (a warning lists the files first)")
    ap.add_argument("--identifiable", action="store_true", help="with --read-credentials: also keep e-mails and organisation titles")
    a = ap.parse_args()
    hosts, notes = detect_hosts(all_profiles=a.all_profiles, probe_wsl=not a.no_wsl)
    accounts = draft_accounts(hosts, read_credentials=a.read_credentials, identifiable=a.identifiable)
    if a.json:
        print(json.dumps({"os": platform.system(), "hosts": hosts, "accounts": accounts, "notes": notes}, indent=2))
        return
    print("OS: %s %s" % (platform.system(), platform.release()))
    for h in hosts:
        print("\n[%s] kind=%s%s" % (h["name"], h["kind"], (" distro=" + h["distro"]) if h.get("distro") else ""))
        for f in h.get("_found", []):
            print("   ", f)
    print("\naccounts:")
    for k, v in accounts["accounts"].items():
        if k.endswith(":provider") or v.get("provider") == "mixed":
            continue
        print("    %-28s %-32s %s" % (k, v.get("label"), v.get("plan")))
    for n in notes:
        print("note:", n)


if __name__ == "__main__":
    main()
