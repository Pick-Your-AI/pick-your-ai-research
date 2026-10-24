#!/usr/bin/env python3
"""
anonymize.py - make a ledger publishable without exposing who, where or what.

    python3 anonymize.py --salt <secret> --in events.x.jsonl --out events.anon.jsonl
    python3 anonymize.py --salt <secret> --accounts accounts.json --out accounts.anon.json
    python3 anonymize.py --salt <secret> --inventory inventory.x.json --out inventory.anon.json

What is replaced (deterministically, keyed on the salt so re-runs agree and outsiders cannot reverse it):

  host names          -> host-01, host-02 ... (order of first appearance is NOT used; the label comes from the hash)
  session ids         -> 12-hex digest
  request ids         -> 12-hex digest
  working directories -> project-<8 hex> (the directory name itself is dropped)
  source file paths   -> removed
  account keys        -> <tool or provider>:acct-<6 hex>; labels, e-mails, org names and evidence -> removed
  prompts             -> never copied
  inventory roots     -> "<tool> logs" (paths removed); byte and line counts kept

Kept: tool, model, plan type, timestamps, token counts, costs, kind, entrypoint, version, effort. These are what the
study is about. A private map of real -> anonymised labels is written next to the store so the owner can still
read their own published figures; it is never included in the outputs.

Standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import safety as _safety  # noqa: E402
except ImportError:  # standalone use outside the skill directory
    _safety = None

# fields whose values are never paths or identities and are kept verbatim
KEEP = {"tool", "model", "ts", "date", "kind", "plan", "billing", "account_confidence", "version", "effort", "service_tier", "granularity", "priced_as",
        "input_uncached", "cache_read", "cache_write", "cache_write_5m", "cache_write_1h", "output", "reasoning", "total", "cost_usd", "api_cost_usd",
        "cost_if_uncached_usd", "cache_savings_usd", "calls", "calls_in_session", "user_msgs", "tool_calls", "bytes", "seq", "partial", "credits", "limit_id",
        "first_ts", "last_ts", "entrypoint_kind"}
_PATHY = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\|/|~[\\/]|\.{1,2}[\\/])|[\\/].*[\\/]")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def make_salt():
    return secrets.token_hex(16)


class Anonymizer:
    def __init__(self, salt, map_path=None):
        if not salt:
            raise ValueError("a salt is required; generate one with make_salt() and keep it private")
        self.salt = salt
        self.map = {"hosts": {}, "cwds": {}, "accounts": {}}
        self.map_path = map_path

    def _h(self, kind, value, n):
        return hashlib.sha256(("%s|%s|%s" % (self.salt, kind, value)).encode("utf-8")).hexdigest()[:n]

    def host(self, v):
        if not v:
            return v
        out = "host-" + self._h("host", v, 6)
        self.map["hosts"][v] = out
        return out

    def session(self, v):
        return self._h("session", v, 12) if v else v

    def request_id(self, v):
        return self._h("request", v, 12) if v else v

    def cwd(self, v):
        if not v:
            return v
        out = "project-" + self._h("cwd", v.rstrip("/\\").lower(), 8)
        self.map["cwds"][v] = out
        return out

    def scrub(self, field, v):
        """Replace anything that looks like a filesystem path, URL or e-mail in a free-text field with a stable token."""
        if not isinstance(v, str) or field in KEEP or not v:
            return v
        if _PATHY.search(v) or "://" in v:
            return "path-" + self._h("path", v.lower(), 8)
        if _EMAIL.search(v):
            return _EMAIL.sub(lambda m: "user-" + self._h("email", m.group(0).lower(), 6), v)
        return v

    def account(self, key):
        if not key or key in ("unattributed",):
            return key
        prefix = key.split(":", 1)[0] if ":" in key else "acct"
        out = "%s:acct-%s" % (prefix, self._h("account", key, 6))
        self.map["accounts"][key] = out
        return out

    def _goose_evidence(self, node):
        """Keep numeric evidence, not stable private native identifiers."""
        if isinstance(node, list):
            return [self._goose_evidence(value) for value in node]
        if not isinstance(node, dict):
            return node
        result = {}
        for key, value in node.items():
            if key in ("source_namespace", "native_session_id", "usage_id", "provider_request_id"):
                continue
            if key == "session":
                result[key] = self.session(value)
            elif isinstance(value, (dict, list)):
                result[key] = self._goose_evidence(value)
            else:
                result[key] = self.scrub(key, value)
        return result

    # ---- rows -------------------------------------------------------------
    def event(self, e):
        e = dict(e)
        e["host"] = self.host(e.get("host"))
        e["session"] = self.session(e.get("session"))
        if e.get("request_id"):
            e["request_id"] = self.request_id(e["request_id"])
        if e.get("tool") == "mini-swe-agent":
            for key in ("source_request_id", "invocation_id", "run_id", "agent_id"):
                if e.get(key):
                    e[key] = self.request_id(e[key])
        if e.get("tool") == "goose" and isinstance(e.get("goose"), dict):
            e["goose"] = self._goose_evidence(e["goose"])
        e["cwd"] = self.cwd(e.get("cwd"))
        for k in ("src", "project", "text", "id", "ingested_at"):
            e.pop(k, None)
        if e.get("account"):
            e["account"] = self.account(e["account"])
        for k in list(e.keys()):
            if k not in ("host", "session", "request_id", "cwd", "account"):
                e[k] = self.scrub(k, e[k])
        return e

    def session_row(self, s):
        s = dict(s)
        s["host"] = self.host(s.get("host"))
        s["session"] = self.session(s.get("session"))
        s["cwd"] = self.cwd(s.get("cwd"))
        for k in ("file", "src", "id", "ingested_at", "title", "summary"):
            s.pop(k, None)
        for k in list(s.keys()):
            if k not in ("host", "session", "cwd"):
                s[k] = self.scrub(k, s[k])
        return s

    def inventory(self, inv):
        inv = dict(inv)
        inv["host"] = self.host(inv.get("host"))
        roots = []
        for r in inv.get("roots", []):
            r = dict(r)
            r["host"] = self.host(r.get("host"))
            r["root"] = "%s logs" % r.get("tool", "agent")
            r.pop("note", None)
            if r.get("tool") == "goose":
                r = self._goose_evidence(r)
            roots.append(r)
        inv["roots"] = roots
        return inv

    def accounts(self, AC):
        """accounts.json -> same rules and registry shape with identities removed."""
        reg = {}
        for key, v in (AC.get("accounts") or {}).items():
            reg[self.account(key)] = {"provider": v.get("provider"), "label": self.account(key), "plan": v.get("plan"), "monthly_usd": v.get("monthly_usd", 0),
                                      "evidence": "redacted for publication"}
        rules = []
        for r in AC.get("rules", []):
            w = dict(r.get("when", {}))
            if w.get("host"):
                w["host"] = self.host(w["host"])
            if w.get("cwd_contains"):
                w["cwd_contains"] = None  # cannot be applied after cwd hashing; rule kept for its account/billing only
                w.pop("cwd_contains")
            rules.append({"when": w, "account": self.account(r["account"]), "billing": r.get("billing"), "confidence": r.get("confidence"), "why": "redacted for publication"})
        out = {"_comment": "Anonymised copy; identities, e-mails, organisations and evidence removed.", "accounts": reg, "rules": rules}
        src = AC.get("_source") or {"placeholders": "host placeholders", "account metadata": "credential files"}.get(AC.get("_sensitivity"))
        if src:
            out["_source"] = src  # how the accounts were drafted is not identifying and the report narrative needs it
        return out

    def save_map(self):
        if self.map_path:
            try:
                import safety
                safety.write_private(self.map_path, json.dumps(self.map, indent=2, sort_keys=True))
            except ImportError:  # standalone use outside the skill directory
                fd = os.open(self.map_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    json.dump(self.map, fh, indent=2, sort_keys=True)


def anonymize_jsonl(an, src, dst, kind="events"):
    fn = an.event if kind == "events" else an.session_row
    n = 0
    _open = _safety.private_open(dst, "w") if _safety is not None else open(dst, "w", encoding="utf-8")
    with open(src, "rb") as fi, _open as fo:
        for raw in fi:
            try:
                row = json.loads(raw)
            except Exception:
                continue
            fo.write(json.dumps(fn(row)) + "\n")
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salt", required=True, help="private secret; keep it in the ledger config, never in the outputs")
    ap.add_argument("--in", dest="inp", help="events.*.jsonl or sessions.*.jsonl")
    ap.add_argument("--kind", default="events", choices=["events", "sessions"])
    ap.add_argument("--accounts", help="accounts.json to anonymise")
    ap.add_argument("--inventory", help="inventory.*.json to anonymise")
    ap.add_argument("--out", required=True)
    ap.add_argument("--map", help="write the private real->anonymised map here")
    a = ap.parse_args()
    an = Anonymizer(a.salt, a.map)
    if a.inp:
        print("rows:", anonymize_jsonl(an, a.inp, a.out, a.kind))
    elif a.accounts:
        with open(a.accounts, encoding="utf-8") as fh:
            AC = json.load(fh)
        with (_safety.private_open(a.out, "w") if _safety is not None else open(a.out, "w", encoding="utf-8")) as fh:
            json.dump(an.accounts(AC), fh, indent=2)
        print("accounts anonymised")
    elif a.inventory:
        with open(a.inventory, encoding="utf-8") as fh:
            inv = json.load(fh)
        with (_safety.private_open(a.out, "w") if _safety is not None else open(a.out, "w", encoding="utf-8")) as fh:
            json.dump(an.inventory(inv), fh, indent=2)
        print("inventory anonymised")
    else:
        ap.error("give --in, --accounts or --inventory")
    an.save_map()
    if os.path.isfile(a.out):
        print("wrote", a.out)


if __name__ == "__main__":
    main()
