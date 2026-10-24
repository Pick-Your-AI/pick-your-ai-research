#!/usr/bin/env python3
"""
build_report.py - render the research-grade usage study package from
compiled/summary.json + compiled/analysis.json + pricing.json + scans/**/inventory.*.json
(+ Claude Code stats-cache.json files as a second evidence class).

Environment-specific prose (host descriptions, excluded sources, extra limitations,
reproduction commands) comes from a report_config.json so the same script serves any
machine. See templates/report_config.example.json.

Outputs <out>/: USAGE_REPORT.md, report.html, ledger.json, pricing.json, README.md, SHA256SUMS
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safety  # noqa: E402
import html as _html  # noqa: E402
from collections import defaultdict, OrderedDict
from datetime import datetime, timezone

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

TOOL_NAME = {"codex": "Codex", "claude-code": "Claude Code", "copilot-cli": "GitHub Copilot CLI", "opencode": "opencode", "openclaw": "OpenClaw"}
TOOL_VAR = {"codex": "--codex", "claude-code": "--claude", "copilot-cli": "--copilot", "opencode": "--opencode", "openclaw": "--openclaw"}


def fmt(n):
    return "{:,}".format(int(round(n or 0)))


def money(n):
    return "${:,.2f}".format(n or 0)


def compact(n):
    n = float(n or 0)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            return "%.2f%s" % (n / div, suf)
    return "%d" % n


def pctf(x):
    return "%.1f%%" % (100 * x) if x is not None else "n/a"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def tail(p):
    return (p or "").replace("\\", "/").rstrip("/").split("/")[-1]


# ----------------------------------------------------------------------------
# SVG charts (theme-aware via CSS variables; drawn to scale)
# ----------------------------------------------------------------------------

def nice_step(x):
    import math
    if x <= 0:
        return 1
    p = 10 ** math.floor(math.log10(x))
    f = x / p
    return (1 if f <= 1 else 2 if f <= 2 else 5 if f <= 5 else 10) * p


def svg_stacked_months(rows, tools, key, title, fmtv, width=900, height=300):
    months = sorted({r["month"] for r in rows if r["month"] != "?"})
    if not months:
        return ""
    by = defaultdict(dict)
    for r in rows:
        by[r["month"]][r["tool"]] = r
    L, R, T, B = 70, 16, 18, 40
    pw, ph = width - L - R, height - T - B
    maxv = max(sum((by[m].get(t) or {}).get(key, 0) for t in tools) for m in months) or 1
    step = nice_step(maxv / 4)
    ymax = (int(maxv / step) + 1) * step
    def y(v):
        return T + ph - v / ymax * ph
    band = pw / len(months)
    bw = min(28, band * .6)
    s = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">' % (width, height, width, height, title)]
    v = 0
    while v <= ymax:
        s.append('<line class="grid" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/><text x="%d" y="%.1f" text-anchor="end">%s</text>' % (L, width - R, y(v), y(v), L - 8, y(v) + 4, fmtv(v)))
        v += step
    for i, m in enumerate(months):
        x = L + band * i + (band - bw) / 2
        acc = 0
        for t in tools:
            r = by[m].get(t)
            val = (r or {}).get(key, 0)
            if not val:
                continue
            y1, y0 = y(acc + val), y(acc)
            h = max(0, y0 - y1 - 2)
            s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="var(%s)"><title>%s %s: %s</title></rect>' % (x, y1, bw, h, TOOL_VAR.get(t, "--ink-3"), m, TOOL_NAME.get(t, t), fmtv(val)))
            acc += val
        if acc == maxv:
            s.append('<text x="%.1f" y="%.1f" text-anchor="middle" class="ink">%s</text>' % (x + bw / 2, y(acc) - 6, fmtv(acc)))
        s.append('<text x="%.1f" y="%d" text-anchor="middle">%s</text>' % (x + bw / 2, height - B + 18, m))
    s.append('<line class="axis" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/></svg>' % (L, width - R, y(0), y(0)))
    return "\n".join(s)


def svg_lines_months(series, title, width=900, height=240, ymax=100, yfmt=lambda v: "%d%%" % v):
    months = sorted({m for _, _, pts in series for m, _ in pts})
    if not months:
        return ""
    L, R, T, B = 60, 110, 16, 36
    pw, ph = width - L - R, height - T - B
    def x(i):
        return L + (i * pw / (len(months) - 1) if len(months) > 1 else pw / 2)

    def y(v):
        return T + ph - v / ymax * ph
    s = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">' % (width, height, width, height, title)]
    for v in [ymax * k / 4 for k in range(5)]:
        s.append('<line class="grid" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/><text x="%d" y="%.1f" text-anchor="end">%s</text>' % (L, width - R, y(v), y(v), L - 8, y(v) + 4, yfmt(v)))
    for i, m in enumerate(months):
        s.append('<text x="%.1f" y="%d" text-anchor="middle">%s</text>' % (x(i), height - B + 18, m[2:]))
    for label, var, pts in series:
        d = {m: v for m, v in pts}
        seq = [(x(i), y(min(d[m], ymax)), d[m], m) for i, m in enumerate(months) if m in d]
        if not seq:
            continue
        s.append('<polyline fill="none" stroke="var(%s)" stroke-width="2" stroke-linejoin="round" points="%s"/>' % (var, " ".join("%.1f,%.1f" % (a, b) for a, b, _, _ in seq)))
        for a, b, v, m in seq:
            s.append('<circle cx="%.1f" cy="%.1f" r="4" fill="var(%s)" stroke="var(--surface)" stroke-width="2"><title>%s %s: %s</title></circle>' % (a, b, var, label, m, yfmt(v)))
        a, b, v, _ = seq[-1]
        s.append('<text x="%.1f" y="%.1f" class="ink">%s %s</text>' % (a + 8, b + 4, label, yfmt(v)))
    s.append("</svg>")
    return "\n".join(s)


def svg_heatmap(mat, title, width=900, height=230):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    L, T = 44, 24
    cw, ch = (width - L - 10) / 24, (height - T - 10) / 7
    mx = max(max(row) for row in mat) or 1
    s = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">' % (width, height, width, height, title)]
    for h in range(24):
        if h % 3 == 0:
            s.append('<text x="%.1f" y="%d" text-anchor="middle">%02d</text>' % (L + cw * h + cw / 2, T - 8, h))
    for d in range(7):
        s.append('<text x="%d" y="%.1f" text-anchor="end">%s</text>' % (L - 8, T + ch * d + ch / 2 + 4, days[d]))
        for h in range(24):
            v = mat[d][h]
            lvl = 0 if v == 0 else min(6, 1 + int(6 * (v / mx) ** 0.5))
            s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="var(--seq%d)"><title>%s %02d:00 %s calls</title></rect>' % (L + cw * h + 1, T + ch * d + 1, cw - 2, ch - 2, lvl, days[d], h, fmt(v)))
    s.append("</svg>")
    return "\n".join(s)


def svg_bars(items, title, fmtv, width=900, var="--codex"):
    if not items:
        return ""
    L, R, rh = 250, 90, 22
    height = 12 + rh * len(items)
    mx = max(v for _, v in items) or 1
    pw = width - L - R
    s = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">' % (width, height, width, height, title)]
    for i, (label, v) in enumerate(items):
        y = 6 + rh * i
        s.append('<text x="%d" y="%.1f" text-anchor="end" class="mono">%s</text>' % (L - 8, y + 15, label[:38]))
        s.append('<rect x="%d" y="%.1f" width="%.1f" height="14" rx="2" fill="var(%s)"><title>%s: %s</title></rect>' % (L, y + 4, pw * v / mx, var, label, fmtv(v)))
        s.append('<text x="%.1f" y="%.1f" class="ink-2">%s</text>' % (L + pw * v / mx + 6, y + 15, fmtv(v)))
    s.append("</svg>")
    return "\n".join(s)


# ----------------------------------------------------------------------------
# document model (Markdown + HTML twin from the same blocks)
# ----------------------------------------------------------------------------

def md_inline(s):
    import re
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


class Doc:
    def __init__(self):
        self.md = []
        self.html = []

    def h(self, level, text):
        self.md.append("#" * level + " " + text + "\n")
        self.html.append("<h%d>%s</h%d>" % (level, md_inline(text), level))

    def p(self, text):
        self.md.append(text + "\n")
        self.html.append("<p>%s</p>" % md_inline(text))

    def table(self, header, rows, align=None):
        align = align or ["l"] + ["r"] * (len(header) - 1)
        self.md.append("| " + " | ".join(header) + " |")
        self.md.append("|" + "|".join("---:" if a == "r" else "---" for a in align) + "|")
        for r in rows:
            self.md.append("| " + " | ".join(str(c) for c in r) + " |")
        self.md.append("")
        h = ['<div class="tw"><table><tr>' + "".join("<th%s>%s</th>" % (' class="n"' if a == "r" else "", md_inline(str(c))) for c, a in zip(header, align)) + "</tr>"]
        for r in rows:
            h.append("<tr>" + "".join("<td%s>%s</td>" % (' class="n"' if a == "r" else "", md_inline(str(c))) for c, a in zip(r, align)) + "</tr>")
        h.append("</table></div>")
        self.html.append("".join(h))

    def ul(self, items):
        for it in items:
            self.md.append("- " + it)
        self.md.append("")
        self.html.append("<ul>" + "".join("<li>%s</li>" % md_inline(it) for it in items) + "</ul>")

    def ol(self, items):
        for i, it in enumerate(items, 1):
            self.md.append("%d. %s" % (i, it))
        self.md.append("")
        self.html.append("<ol>" + "".join("<li>%s</li>" % md_inline(it) for it in items) + "</ol>")

    def figure(self, svg, caption, md_fallback):
        if not svg:
            return
        self.md.append(md_fallback + "\n")
        self.html.append('<figure><div class="chart">%s</div><figcaption>%s</figcaption></figure>' % (svg, md_inline(caption)))

    def code(self, text):
        self.md.append("```\n" + text + "\n```\n")
        self.html.append("<pre><code>%s</code></pre>" % text.replace("&", "&amp;").replace("<", "&lt;"))



def _logo_data_uri(path, base_dir=None):
    """Return a data: URI for a local image file (so the page stays self-contained), else the value unchanged."""
    import base64
    import mimetypes
    if not path or str(path).startswith(("data:", "http://", "https://")):
        return path
    candidates = [path]
    if base_dir:
        candidates.insert(0, os.path.join(base_dir, path))
    here = os.path.dirname(os.path.abspath(__file__))
    candidates += [os.path.join(here, "..", path), os.path.join(here, "..", "assets", os.path.basename(path))]
    for c in candidates:
        if os.path.isfile(c):
            mime = mimetypes.guess_type(c)[0] or "image/png"
            with open(c, "rb") as fh:
                return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))
    return path


def brand_blocks(cfg, base_dir=None):
    """Return (style_override_html, header_html, footer_html, fonts_link) from cfg['branding'], all values sanitised
    by safety.sanitize_branding: text is HTML-escaped, colours/tokens/fonts validated, the logo is a local file
    turned into a data URI, remote resources and extra CSS only when explicitly allowed."""
    b = safety.sanitize_branding((cfg or {}).get("branding") or {}, base_dir, _logo_data_uri)
    vars_ = []
    if b.get("accent"):
        vars_.append("--focus:%s;--brand-accent:%s" % (b["accent"], b["accent"]))
    for k, var in (("font_display", "--font-display"), ("font_body", "--font-body"), ("font_mono", "--font-mono")):
        if b.get(k):
            vars_.append("%s:%s" % (var, b[k]))
    light = "".join("--%s:%s;" % (k, v) for k, v in (b.get("light") or {}).items())
    dark = "".join("--%s:%s;" % (k, v) for k, v in (b.get("dark") or {}).items())
    style = "<style>:root{%s%s}" % (";".join(vars_) + (";" if vars_ else ""), light)
    if dark:
        style += "@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]){%s}}:root[data-theme=\"dark\"]{%s}" % (dark, dark)
    if b.get("font_display") or b.get("font_body") or b.get("font_mono"):
        style += "h1,h2,h3,.tile .val{font-family:var(--font-display,inherit)}body{font-family:var(--font-body,inherit)}code,pre,.mono,td.n,th.n,svg{font-family:var(--font-mono,inherit)}"
    style += (".brand .eyebrow{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--brand-accent,var(--ink-2))}"
              ".brand .tagline{font-size:12px;color:var(--ink-3)}.brand .contact{font-size:11px;color:var(--ink-3);margin-left:auto;font-family:\"IBM Plex Mono\",monospace}")
    style += b.get("extra_css", "") + "</style>"
    header = ""
    if b.get("logo") or b.get("name") or b.get("eyebrow"):
        text = "".join([
            ('<div class="eyebrow">%s</div>' % b["eyebrow"]) if b.get("eyebrow") else "",
            ('<div class="name">%s</div>' % b["name"]) if b.get("name") else "",
            ('<div class="tagline">%s</div>' % b["tagline"]) if b.get("tagline") else "",
        ])
        header = '<div class="brand">%s<div>%s</div>%s</div>' % (
            ('<img src="%s" alt="%s">' % (b["logo"], b.get("name", "logo"))) if b.get("logo") else "",
            text,
            ('<div class="contact">%s</div>' % b["contact"]) if b.get("contact") else "")
    footer = ('<div class="brandfoot">%s</div>' % b["footer"]) if b.get("footer") else ""
    link = (safety.CSP_META_EXTERNAL if b.get("allow_external_resources") else safety.CSP_META)
    if b.get("google_fonts_url"):
        link += '<link rel="stylesheet" href="%s">' % b["google_fonts_url"]
    return style, header, footer, link


def price_usage(usage, pricing, model):
    row = pricing["models"].get(model)
    if not row:
        return None
    return (usage.get("inputTokens", 0) * row["input"] + usage.get("cacheReadInputTokens", 0) * row["cache_read"]
            + usage.get("cacheCreationInputTokens", 0) * row["cache_write_5m"] + usage.get("outputTokens", 0) * row["output"]) / 1e6


def root_tail(root):
    """Last path component of a scan root (`codex`, `projects`, `opencode.db`): enough to recognise the tool, never the user name or drive."""
    parts = [x for x in str(root or "").replace("\\", "/").split("/") if x]
    return parts[-1] if parts else ""


def redact_inventory(inv):
    """scan_inventory for ledger.json without absolute paths: tool, host and counts stay, the `root` key is replaced by its tail."""
    out = []
    for i in inv:
        j = dict(i)
        j["roots"] = [dict({k: v for k, v in r.items() if k != "root"}, root_tail=root_tail(r.get("root"))) for r in i.get("roots", [])]
        out.append(j)
    return out


def short_path(v):
    """A path-valued cell reduced to its last component (`repo`), keeping a tool prefix such as `openclaw:` in front of a
    path (`openclaw:pi`); values without a path separator pass through unchanged."""
    if not isinstance(v, str) or not ("/" in v or "\\" in v):
        return v
    head, sep, rest = v.partition(":")
    if sep and rest and len(head) > 1 and head.replace("-", "").replace("_", "").isalnum() and (rest[:1] in "/\\~" or (len(rest) > 2 and rest[1] == ":" and rest[2] in "/\\")):
        return head + ":" + tail(rest)
    return tail(v)


def redact_rows(rows, key):
    """Rows for ledger.json with a path-valued column (working directory, path-shaped entry point) reduced to its last
    component, the same tail the report tables show; other values pass through."""
    return [dict(r, **{key: short_path(r.get(key))}) if isinstance(r.get(key), str) else r for r in rows or []]


SENSITIVITY_MD = """# Sensitivity

This package was compiled from local agent logs and describes the machines and people behind them. Before it leaves the
machine it was built on, know what it contains:

- **Host names** in `ledger.json` (`scope.hosts`, `by_tool_host`, `coverage`, `scan_inventory`) and in the inventory,
  coverage and validation tables of `USAGE_REPORT.md` / `report.html`.
- **Project directory names**: the by-project and top-session tables (report and `ledger.json`) carry the last
  component of each working directory, and the top-session tables carry session ids.
- **Account labels and plan names** from `accounts.json` in the account tables and in `ledger.json` (`accounts`): these
  can be e-mail addresses or organisation names when the accounts file was drafted with identifiable credentials.
- **File-system paths**: %(paths)s

`accounts.json` itself is copied into the package only when the manifest sets `package_accounts: true`.

Treat the package as internal. Run `python3 scripts/ledger.py publish-check <this directory>` before sharing it, or
share the anonymised copy (`ledger.py run --anonymize`, which pseudonymises hosts, projects and accounts) instead.
"""


def write_sensitivity(out_dir, package_paths):
    """Every package gets SENSITIVITY.md; run_pipeline appends a paragraph when it adds accounts.json."""
    paths = ("absolute scan roots, full working directories and the report configuration ARE included in `ledger.json` because the manifest sets `package_paths: true`; they name user profiles and drives."
             if package_paths else
             "absolute scan roots, full working directories and the report configuration are omitted from `ledger.json` (only the last path component of each root and directory is kept); set `package_paths: true` in the manifest to include them.")
    with safety.private_open(os.path.join(out_dir, "SENSITIVITY.md"), "w") as fh:
        fh.write(SENSITIVITY_MD % {"paths": paths})


def write_sums(out_dir):
    """SHA256SUMS over every regular file in the package except itself; run_pipeline calls it again after adding optional files."""
    names = sorted(n for n in os.listdir(out_dir) if n != "SHA256SUMS" and os.path.isfile(os.path.join(out_dir, n)))
    with safety.private_open(os.path.join(out_dir, "SHA256SUMS"), "w") as fh:
        for name in names:
            fh.write("%s  %s\n" % (sha256(os.path.join(out_dir, name)), name))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiled", default="compiled")
    ap.add_argument("--scans", default="scans")
    ap.add_argument("--pricing", default="pricing.json")
    ap.add_argument("--config", default=None, help="report_config.json: title, hosts, excluded_sources, extra_limitations, reproduce_commands, claude_primary_host")
    ap.add_argument("--stats-cache", action="append", default=[], help="host=path to Claude Code stats-cache.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--tz", default="UTC")
    ap.add_argument("--package-paths", action="store_true", help="keep absolute scan roots and the report config in ledger.json (off by default: they name users and directories)")
    a = ap.parse_args()

    CFG = {}
    if a.config and os.path.isfile(a.config):
        safety.refuse_if_shared(a.config, "report config")  # it decides branding, links and notes in the package: refuse a shared file
        CFG = load_json(a.config)

    def pshow(v):  # working directories and path-shaped entry points: last component only unless --package-paths
        return v if a.package_paths else short_path(v)
    HOST_DESC = CFG.get("hosts", {})
    S = load_json(os.path.join(a.compiled, "summary.json"))
    A = load_json(os.path.join(a.compiled, "analysis.json"))
    P = load_json(a.pricing)
    inv = [load_json(p) for p in sorted(glob.glob(os.path.join(a.scans, "**", "inventory.*.json"), recursive=True))]
    stats_caches = {}
    for spec in a.stats_cache:
        host, path = spec.split("=", 1)
        try:
            stats_caches[host] = load_json(path)
        except Exception as ex:
            stats_caches[host] = {"error": str(ex)}

    # per (tool,host) coverage
    cov = defaultdict(lambda: {"first": None, "last": None, "files": 0, "bytes": 0})
    with open(os.path.join(a.compiled, "all_sessions.csv"), encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            c = cov[(r["tool"], r["host"])]
            first_ts, last_ts = r["first_ts"], r["last_ts"]
            if first_ts and (c["first"] is None or first_ts < c["first"]):
                c["first"] = first_ts
            if last_ts and (c["last"] is None or last_ts > c["last"]):
                c["last"] = last_ts
            c["files"] += 1
            c["bytes"] += int(r["bytes"] or 0)

    T = S["total"]
    by_tool = {r["tool"]: r for r in S["by_tool"]}
    by_host = S["by_tool_host"]
    by_month = S["by_month_tool"]
    by_model = sorted(S["by_model"], key=lambda r: -r["total"])
    costs = S["costs"]
    ST = costs["subscription_totals"]
    sub_rows = costs["subscription_rows"]
    ACC = S.get("accounts") or {}
    AREG = ACC.get("registry", {})
    ATOT = ACC.get("subscription_totals", {})
    AROWS = ACC.get("subscription_rows", [])
    ARULES = ACC.get("rules", [])
    APLAN = [r for r in ACC.get("by_plan", []) if r["tool"] == "codex"]
    AUB = [r for r in ACC.get("by_billing_month", []) if r["billing"] == "usage-based" and r["month"] != "?"]
    usage_based_total = sum(r["api_cost_usd"] for r in AUB)
    sub_accounts = {k: v for k, v in ATOT.items() if v.get("subscription_usd", 0) > 0}
    dates = sorted({r["date"] for r in S["by_day_tool"] if r["date"] != "?"})
    tools_present = [t for t in ("codex", "claude-code", "copilot-cli", "opencode", "openclaw") if t in by_tool]
    total_calls = S["events"]
    if not by_tool:
        raise SystemExit("summary.json has no events; run the scan step first (and generate fixtures if this is the example manifest)")
    top_tool = max(by_tool.values(), key=lambda r: r["total"])
    prompt_all = (T["input_uncached"] + T["cache_read"] + T["cache_write"]) or 1
    cache_hit = T["cache_read"] / prompt_all
    sub_paid = sum(t["subscription_usd"] for t in (sub_accounts or ST).values())
    sub_api = sum(t["api_equivalent_usd"] for t in (sub_accounts or ST).values())
    peak_month = max(by_month, key=lambda r: r["total"]) if by_month else {"month": "?", "total": 0, "api_cost_usd": 0}
    month_tot = defaultdict(int)
    for r in by_month:
        if r["month"] != "?":
            month_tot[r["month"]] += r["total"]
    top_months = sorted(month_tot.items(), key=lambda kv: -kv[1])[:2]
    val = A.get("validation", {})
    sens = A.get("sensitivity", {})
    conc = A.get("concentration", {})
    dist = A.get("distributions", {})
    sdist = A.get("session_distributions", {})
    blended = A.get("blended_rates", {})
    ttl = A.get("cache_ttl_split", {"cache_write_5m": 0, "cache_write_1h": 0})
    hosts_all = sorted({h for _, h in cov})

    def bl(tool, key, default=0):
        v = (blended.get(tool) or {}).get(key)
        return default if v is None else v

    # Claude Code evidence class B: stats-cache modelUsage priced
    sc_rows = []
    for host, d in stats_caches.items():
        for model, u in (d.get("modelUsage") or {}).items():
            tok = sum(u.get(k, 0) for k in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens"))
            sc_rows.append((host, model, tok, u.get("outputTokens", 0), price_usage(u, P, model)))
    sc_total_tokens = sum(r[2] for r in sc_rows)
    sc_total_cost = sum(r[4] or 0 for r in sc_rows)
    claude_primary = CFG.get("claude_primary_host") or (max(stats_caches, key=lambda h: sum(t for hh, _, t, _, _ in sc_rows if hh == h)) if sc_rows else None)
    claude_primary_row = next((r for r in by_host if r["tool"] == "claude-code" and r["host"] == claude_primary), {}) if claude_primary else {}
    sc_primary_tokens = sum(t for h, _, t, _, _ in sc_rows if h == claude_primary)
    sc_primary_cost = sum(c or 0 for h, _, _, _, c in sc_rows if h == claude_primary)
    sq_total = sum(r.get("sqlite_tokens_used", 0) or 0 for i in inv for r in i["roots"] if r["tool"] == "codex")

    D = Doc()
    gen = datetime.now(timezone.utc)
    title = CFG.get("title", "AI coding-agent usage: token volume, caching and cost study")
    D.h(1, title)
    D.p("**Snapshot date:** %s · **Timezone for time-of-day analysis:** %s · **Mode:** read-only, local logs only · **Prices:** list API rates as of %s" % (a.date, a.tz, P.get("_as_of", CFG.get("prices_as_of", "the pricing.json date"))))
    D.p("**Scope:** every model call recorded on disk by %s across %d hosts (%s), %s to %s. %s calls in %s sessions were compiled into one event stream, cross-checked against the tools' own counters, and priced at published API list rates. Dollar figures are API-equivalents; the subscription-billed work was actually paid for by %d flat-rate subscriptions%s." % (
        ", ".join(TOOL_NAME.get(t, t) for t in tools_present), len(hosts_all), ", ".join(hosts_all), dates[0] if dates else "?", dates[-1] if dates else "?", fmt(total_calls), fmt(S["sessions"]),
        len(sub_accounts), (", plus usage-based billing worth %s" % money(usage_based_total)) if usage_based_total > 0.5 else ""))

    # ---- Executive summary
    D.h(2, "Executive summary")
    dirs = sorted(S["by_project"], key=lambda r: -r["total"])[:2]
    D.p("**%s of tokens are %s, and %s of all prompt tokens were served from cache.** The two busiest working directories, `%s` (%s, %s threads) and `%s` (%s, %s threads), account for %s of all tokens; the two busiest months, %s, hold %s of the period. At list prices the compiled usage is worth %s; the same tokens without caching would be %s; the %d subscriptions that actually paid for the subscription-billed tools cost %s over the months they were used." % (
        pctf(top_tool["total"] / T["total"]), TOOL_NAME.get(top_tool["tool"], top_tool["tool"]), pctf(cache_hit),
        tail(dirs[0]["cwd"]) if dirs else "?", pctf(dirs[0]["total"] / T["total"]) if dirs else "", fmt(dirs[0]["sessions"]) if dirs else 0,
        tail(dirs[1]["cwd"]) if len(dirs) > 1 else "?", pctf(dirs[1]["total"] / T["total"]) if len(dirs) > 1 else "", fmt(dirs[1]["sessions"]) if len(dirs) > 1 else 0,
        pctf(sum(r["total"] for r in dirs) / T["total"]), " and ".join(m for m, _ in top_months), pctf(sum(v for _, v in top_months) / T["total"]),
        money(T["api_cost_usd"]), money(T["cost_if_uncached_usd"]), len(sub_accounts), money(sub_paid)))
    rows = [
        ["Model calls compiled", fmt(total_calls)],
        ["Sessions / threads", fmt(S["sessions"])],
        ["Typed prompts recovered", fmt(S["prompts"])],
        ["Active days", fmt(len(dates))],
        ["Total tokens (all four classes), de-duplicated", "%s (%s)" % (fmt(T["total"]), compact(T["total"]))],
    ]
    if sq_total:
        rows.append(["Codex tokens as the Codex app counts them (with replayed history)", compact(sq_total)])
    rows += [
        ["Output tokens (reasoning share)", "%s (%s)" % (compact(T["output"]), pctf(T["reasoning"] / T["output"] if T["output"] else 0))],
        ["Cache hit rate, all tools", pctf(cache_hit)],
        ["API-equivalent cost at list rates", money(T["api_cost_usd"])],
        ["Cost if nothing had been cached", money(T["cost_if_uncached_usd"])],
        ["Saved by prompt caching", "%s (%s)" % (money(T["cache_savings_usd"]), pctf(T["cache_savings_usd"] / T["cost_if_uncached_usd"] if T["cost_if_uncached_usd"] else 0))],
        ["Subscriptions paid (%d accounts, months with use)" % len(sub_accounts), money(sub_paid)],
        ["API-equivalent of subscription-billed calls", money(sub_api)],
        ["Usage-based calls (real spend at list rates)", money(usage_based_total)],
        ["Peak month", "%s: %s tokens, %s API-equivalent" % (peak_month["month"], compact(peak_month["total"]), money(peak_month["api_cost_usd"]))],
    ]
    D.table(["Measure", "Value"], rows)
    D.p("**Confidence definitions.** *High*: read directly from per-call usage records the tool wrote at request time, de-duplicated, and cross-checked against a second counter. *Medium*: derived from those records through a documented rule with a stated assumption (pricing rows, replay filter, account rules). *Low*: an estimate that depends on an unpublished price or on a tool-maintained aggregate that could not be reconciled call by call.")

    # ---- 1 coverage
    D.h(2, "1. Coverage and evidence rules")
    D.p("Three classes of evidence are used and kept apart throughout:")
    D.ol([
        "**Per-call usage records (class A).** Claude Code session transcripts (`~/.claude/projects/**/*.jsonl`, assistant messages carry `usage`), Codex rollouts (`~/.codex/sessions/**/rollout-*.jsonl`, `token_count` events), Copilot CLI session events, opencode's SQLite message table, and OpenClaw session files. Every number in the results sections comes from this class unless marked otherwise.",
        "**Tool-maintained aggregates (class B).** Codex `state_5.sqlite` (`threads.tokens_used`) and Claude Code `stats-cache.json` (`modelUsage`, `dailyActivity`). Used to validate class A and to bound what class A cannot see.",
        "**Derived estimates (class C).** API-equivalent cost, cache savings, subscription comparisons and account attribution. These multiply class A tokens by published list prices in `pricing.json` and apply the rules in `accounts.json`; models without a published rate are priced at a stated sibling.",
    ])
    D.h(3, "Source inventory")
    rows = []
    for (tool, host), c in sorted(cov.items(), key=lambda kv: (-kv[1]["bytes"])):
        th = next((r for r in by_host if r["tool"] == tool and r["host"] == host), {})
        rows.append([TOOL_NAME.get(tool, tool), host, fmt(c["files"]), "%.2f GB" % (c["bytes"] / 1e9), (c["first"] or "")[:10], (c["last"] or "")[:10], fmt(th.get("calls", 0)), compact(th.get("total", 0))])
    D.table(["Tool", "Host", "Files", "Size", "First", "Last", "Calls", "Tokens"], rows, ["l", "l", "r", "r", "l", "l", "r", "r"])
    if HOST_DESC:
        D.p("Hosts: " + "; ".join("**%s** = %s" % (h, HOST_DESC.get(h, h)) for h in hosts_all) + ".")
    D.h(3, "Scan provenance")
    rows = []
    for i in inv:
        for r in i["roots"]:
            rows.append([i["host"], TOOL_NAME.get(r["tool"], r["tool"]), "`%s`" % (r["root"] if a.package_paths else root_tail(r["root"])), fmt(r.get("events", 0)), fmt(r.get("prompts", 0)), fmt(r.get("sqlite_threads", 0)) if r.get("sqlite_threads") else "–", compact(r["sqlite_tokens_used"]) if r.get("sqlite_tokens_used") else "–"])
    D.table(["Host", "Tool", "Root scanned", "Calls found", "Prompts", "Tool's thread count", "Tool's token total"], rows, ["l", "l", "l", "r", "r", "r", "r"])
    if not a.package_paths:
        D.p("Scan roots are shown by their last path component only; the full paths stay on the machine unless the manifest sets `package_paths: true`.")
    D.p("Scan statistics: " + "; ".join("**%s** %s files, %.1f GB, %s lines, %s JSON errors, %s replayed Codex token events skipped, %s duplicates skipped, %ss" % (i["host"], fmt(i["files"]), i["bytes"] / 1e9, fmt(i["lines"]), fmt(i["json_errors"]), fmt(i["codex_replay_skipped"]), fmt(i["dedup_skipped"]), i["seconds"]) for i in inv) + ".")
    D.h(3, "Sources examined and excluded")
    excl = []
    if claude_primary and sc_primary_tokens:
        c = cov.get(("claude-code", claude_primary), {})
        excl.append("**Claude Code transcripts on %s cover only %s to %s.** Claude Code deletes transcripts older than its retention window (`cleanupPeriodDays`, 30 days by default). The tool's own cumulative counter (`stats-cache.json`, class B) records %s tokens on that host since its first session, versus %s recovered from surviving transcripts. Claude Code figures in this study are therefore a **lower bound**; see finding F06." % (
            claude_primary, (c.get("first") or "")[:10], (c.get("last") or "")[:10], compact(sc_primary_tokens), compact(claude_primary_row.get("total", 0))))
    excl += CFG.get("excluded_sources", [])
    if excl:
        D.ul(excl)

    # ---- 2 method
    D.h(2, "2. Method")
    D.h(3, "2.1 Parsing rules")
    D.ul([
        "**Claude Code.** Every `assistant` line with `message.usage` is one call. Streamed turns are written as several lines sharing one `message.id`; they are de-duplicated on that id across all files of a host. `agent-*.jsonl` files and `isSidechain` lines are labelled sub-agent. `cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` split cache writes by TTL for pricing; transcripts without that breakdown are treated as 5-minute writes. Lines with model `<synthetic>` and zero usage are dropped.",
        "**Codex.** Each `event_msg` of type `token_count` with a non-null `info` is one call, using `last_token_usage`. Consecutive events whose cumulative `total_token_usage.total_tokens` did not change are duplicates and dropped. Model and reasoning effort come from the most recent `turn_context`; the thread's `session_meta` supplies cwd, originator (CLI, Desktop, VS Code, exec) and version; `rate_limits.plan_type` on the same event records the billing plan. `input_tokens` includes cached tokens in Codex's schema, so uncached input = `input_tokens - cached_input_tokens`.",
        "**Replayed history.** Forked and sub-agent Codex rollouts (`forked_from_id` / `source.subagent`, and any file carrying a second `session_meta`, which is the parent's) begin with the parent's entire history copied in as one write burst, re-stamped at fork time. Everything up to the first gap of more than 2 seconds between consecutive lines is treated as replay and dropped. %s `token_count` events were removed across hosts. Without this rule the parent's usage is counted once per child, and the parent's billing plan is copied onto the child; the Codex app's own counter has exactly that inflation." % fmt(sum(i["codex_replay_skipped"] for i in inv)),
        "**Copilot CLI.** One record per session from `session.shutdown.tokenDetails` (input, cache read, cache write, output); `assistant.message` events only carry output tokens and are used as a fallback when a session has no shutdown record.",
        "**opencode.** `message.data.tokens` and `cost` from `opencode.db`; the tool's own USD cost is used as-is.",
        "**OpenClaw.** `message.usage` on assistant messages; `<id>.checkpoint.<x>.jsonl` files replay the parent session and are de-duplicated on (message id, timestamp) across files.",
    ])
    D.h(3, "2.2 Token taxonomy")
    D.table(["Column", "Meaning", "Priced at"], [
        ["`input_uncached`", "prompt tokens processed fresh", "input rate"],
        ["`cache_read`", "prompt tokens served from the provider's prompt cache", "cache-read rate"],
        ["`cache_write`", "prompt tokens written to cache (Anthropic only; OpenAI does not charge writes)", "cache-write rate for the TTL used"],
        ["`output`", "completion tokens, reasoning included", "output rate"],
        ["`reasoning`", "the reasoning / thinking share of `output`", "informational"],
        ["`total`", "sum of the first four", "–"],
    ], ["l", "l", "l"])
    D.h(3, "2.3 Pricing model")
    D.p("API-equivalent cost of a call = Σ tokens × list rate for that model, from `pricing.json`. `cost_if_uncached` re-prices the same call with every prompt token at the input rate; the difference is the cache saving. No batch discount, data-residency multiplier, fast-mode premium or long-context surcharge is applied.")
    used = {x["model"] for x in by_model} | {x.get("priced_as") for x in sens.get("priced_as", [])}
    prows = [["`%s`" % m, "$%.2f" % r["input"], "$%.3f" % r["cache_read"], "$%.2f" % r["cache_write_5m"] if r["cache_write_5m"] else "–", "$%.2f" % r["cache_write_1h"] if r["cache_write_1h"] else "–", "$%.2f" % r["output"], r.get("assumed", "published")]
             for m, r in P["models"].items() if m in used]
    D.table(["Model", "Input /M", "Cache read /M", "Cache write 5m /M", "Cache write 1h /M", "Output /M", "Basis"], prows, ["l", "r", "r", "r", "r", "r", "l"])
    D.h(3, "2.4 Accounts and subscription attribution")
    _src = (S.get("accounts") or {}).get("source") or "credential files"
    _how = {"host placeholders": "Accounts are placeholders named after each host: credential files were not read, so plans and billing are unknown until `accounts.json` is filled in.",
            "credential files, minimised": "Accounts were identified from the credential files on each host with identity minimised: pseudonymous account ids and plan types only, no e-mail addresses or organisation names.",
            "unspecified": "The accounts file does not record how it was drafted; treat its labels as operator-supplied."}.get(_src, "Accounts were identified from the credential files on each host.")
    D.p(_how + " Codex rollouts record the billing plan on every call (`rate_limits.plan_type`) but not the account, so calls are attributed to accounts by ordered rules in `accounts.json`; each rule carries its evidence and a confidence level. A subscription month is counted only when the account recorded at least one call in that month.")
    _un = next((r for r in ACC.get("by_account", []) if r.get("account") == "unattributed"), None)
    if _un:
        D.p("**Unattributed calls.** %s calls (%s tokens, %s API-equivalent) matched no rule in `accounts.json`. They are reported under the account `unattributed` with billing `unknown` rather than folded into any real account; add a rule to `accounts.json` to attribute them." % (fmt(_un["calls"]), compact(_un["total"]), money(_un["api_cost_usd"])))
    elif ACC:
        D.p("**Unattributed calls.** None: every call matched a rule in `accounts.json`.")
    if AREG:
        D.table(["Account", "Identity", "Plan", "Price", "Evidence"], [["`%s`" % k, v.get("label", ""), v.get("plan", ""), "$%d/mo" % v.get("monthly_usd", 0) if v.get("monthly_usd") else ("unknown" if (ATOT.get(k) or {}).get("billing") == "unknown" else "usage-based / n.a."), v.get("evidence", "")] for k, v in AREG.items()], ["l"] * 5)
        D.table(["Rule (first match wins)", "Account", "Billing", "Confidence", "Why"], [["`%s`" % ", ".join("%s=%s" % kv for kv in r.get("when", {}).items()), "`%s`" % r["account"], r.get("billing", ""), r.get("confidence", ""), r.get("why", "")] for r in ARULES], ["l"] * 5)
    D.h(3, "2.5 Validation against tool-maintained counters")
    if val:
        D.p("Codex keeps a per-thread `tokens_used` in `state_5.sqlite`, and the Codex app reports totals from it. That counter includes the replayed parent history for every spawned thread (section 2.1), so it over-counts in exactly the way a naive read of the rollouts does. **As the app counts it, the scanned profiles total %s tokens; de-duplicated, they total %s.** Rollout-derived totals were compared thread by thread; agreement is high for threads that were never forked and low for spawned children, whose SQLite figure carries the parent's history:" % (compact(sq_total), compact(by_tool.get("codex", {}).get("total", 0))))
        rows = []
        for host, v in val.items():
            if "error" in v:
                rows.append([host, "error: %s" % v["error"], "", "", "", "", ""])
                continue
            n = v["sqlite_threads_with_tokens"] or 1
            rows.append([host, fmt(n), pctf(v["within_2pct"] / n), pctf(v["within_10pct"] / n), compact(v["rollout_sum_same_threads"]), compact(v["sqlite_sum"]), "%.3f" % (v["rollout_sum_same_threads"] / v["sqlite_sum"] if v["sqlite_sum"] else 0)])
        D.table(["Host", "Threads compared", "Within 2%", "Within 10%", "Rollout sum", "SQLite sum", "Ratio"], rows, ["l", "r", "r", "r", "r", "r", "r"])
        worst = [[host, "`%s`" % d["thread"][:13], d.get("source") or "", compact(d["rollout"]), compact(d["sqlite"])] for host, v in val.items() for d in v.get("largest_disagreements", [])[:3]]
        if worst:
            D.table(["Host", "Thread", "Source", "Rollout", "SQLite"], worst, ["l", "l", "l", "r", "r"])
    if sc_rows:
        D.p("Claude Code's `stats-cache.json` (class B) gives a cumulative per-model counter per host. Priced with the same rates it yields the following, which bounds the transcript-based Claude figures from above:")
        rows = [[h, "`%s`" % m, compact(t), compact(o), money(c) if c is not None else "no rate"] for h, m, t, o, c in sorted(sc_rows, key=lambda r: -r[2])]
        rows.append(["**all**", "", "**%s**" % compact(sc_total_tokens), "", "**%s**" % money(sc_total_cost)])
        D.table(["Host", "Model", "Tokens", "Output", "API-equivalent"], rows, ["l", "l", "r", "r", "r"])

    # ---- 3 findings (each guarded: a finding is skipped when its inputs are absent)
    D.h(2, "3. Findings")
    findings = []

    def add(code, conf, title_, evidence_fn, impl):
        try:
            findings.append((code, conf, title_, evidence_fn(), impl))
        except Exception as ex:  # missing tool or field for this dataset
            sys.stderr.write("skipping %s: %s\n" % (code, ex))

    top_two = A.get("top_sessions", [])[:2]
    main_tool = top_tool["tool"]
    cc = conc.get(main_tool, {})
    add("F01", "High", "Volume is concentrated in a few hundred threads and two projects.",
        lambda: "Two working directories hold %s of all tokens: `%s` (%s across %s threads) and `%s` (%s across %s threads). Within %s, the top 1%% of threads (%s) hold %s of tokens and the top 10%% hold %s; the largest single thread holds %s. The two largest threads are `%s…` in `%s` (%s, %s to %s, %.0f h, %s) and `%s…` in `%s` (%s, %s to %s, %.0f h, %s)." % (
            pctf(sum(r["total"] for r in dirs) / T["total"]), tail(dirs[0]["cwd"]), pctf(dirs[0]["total"] / T["total"]), fmt(dirs[0]["sessions"]), tail(dirs[1]["cwd"]), pctf(dirs[1]["total"] / T["total"]), fmt(dirs[1]["sessions"]),
            TOOL_NAME.get(main_tool, main_tool), fmt(cc["sessions"] * .01), pctf(cc["top1pct_share"]), pctf(cc["top10pct_share"]), pctf(cc["top_session_share"]),
            top_two[0]["session"][:8], tail(top_two[0]["cwd"]), top_two[0]["model"], (top_two[0]["first"] or "")[:10], (top_two[0]["last"] or "")[:10], top_two[0]["hours"] or 0, compact(top_two[0]["total"]),
            top_two[1]["session"][:8], tail(top_two[1]["cwd"]), top_two[1]["model"], (top_two[1]["first"] or "")[:10], (top_two[1]["last"] or "")[:10], top_two[1]["hours"] or 0, compact(top_two[1]["total"])),
        "Cost and capacity planning should be done per project and per thread, not per month; a few unattended multi-thread loops set the figures.")
    dm = dist.get(main_tool, {})
    add("F02", "High", "The cache, not the model, is doing the work.",
        lambda: "%s re-sent a median of %s prompt tokens per call (p90 %s, max %s) while producing a median of %s output tokens. %s of prompt tokens were cache hits (%s). Prompt tokens per output token: %s." % (
            TOOL_NAME.get(main_tool, main_tool), compact(dm["prompt_tokens_per_call"]["p50"]), compact(dm["prompt_tokens_per_call"]["p90"]), compact(dm["prompt_tokens_per_call"]["max"]), compact(dm["output_tokens_per_call"]["p50"]),
            pctf(cache_hit), "; ".join("%s %s" % (TOOL_NAME.get(t, t), pctf(bl(t, "cache_hit_rate"))) for t in tools_present if blended.get(t)),
            "; ".join("%s %.0f" % (TOOL_NAME.get(t, t), bl(t, "prompt_tokens_per_output_token")) for t in tools_present if blended.get(t))),
        "At list rates the cache removed %s (%s) from the bill. Context length, not output, is the cost driver." % (money(T["cache_savings_usd"]), pctf(T["cache_savings_usd"] / T["cost_if_uncached_usd"] if T["cost_if_uncached_usd"] else 0)))
    add("F03", "Medium (class C)", "%d flat-rate subscriptions covered work worth far more at list price." % len(sub_accounts),
        lambda: "%s. Calls stamped usage-based total %s at list rates and are real spend, not subscription-covered. The peak month, %s, was %s API-equivalent." % (
            "; ".join("%s (%s): %s over %d months against %s (%s×)" % (AREG.get(k, {}).get("label", k), AREG.get(k, {}).get("plan", ""), money(t["subscription_usd"]), t["months"], money(t["api_equivalent_usd"]), t["api_to_sub_ratio"]) for k, t in sorted(sub_accounts.items(), key=lambda kv: -kv[1]["api_equivalent_usd"])),
            money(usage_based_total), peak_month["month"], money(peak_month["api_cost_usd"])),
        "The comparison assumes the provider would have served the same traffic on a pay-as-you-go key at list rates; rate limits on each subscription, not price, are the binding constraint in practice.")
    eff = A.get("effort", {}).get(main_tool, {})
    eff_tot = sum(v["calls"] for v in eff.values()) or 1
    add("F04", "High", "Reasoning effort and sub-agent fan-out are material.",
        lambda: "Reasoning tokens are %s of output (%s). %s calls by configured effort: %s. Sub-agent share of tokens: %s." % (
            pctf(T["reasoning"] / T["output"] if T["output"] else 0), "; ".join("%s %s" % (TOOL_NAME.get(t, t), pctf(bl(t, "reasoning_share_of_output"))) for t in tools_present if blended.get(t)),
            TOOL_NAME.get(main_tool, main_tool), ", ".join("%s %s" % (k, pctf(v["calls"] / eff_tot)) for k, v in sorted(eff.items(), key=lambda kv: -kv[1]["calls"])[:4]),
            "; ".join("%s %s" % (TOOL_NAME.get(t, t), pctf(next((r["total"] for r in S["by_kind"] if r["tool"] == t and r["kind"] == "subagent"), 0) / by_tool[t]["total"])) for t in tools_present if by_tool[t]["total"])),
        "Effort settings and fan-out multiply context re-reads; they are the two levers that change the bill without changing the task.")
    mm = A.get("model_month", {})
    latest = sorted(mm.keys())[-1] if mm else None
    add("F05", "High", "The model mix moved over time.",
        lambda: "%s carries %s of all tokens (%s of API-equivalent cost). In %s the leading models by volume were %s." % (
            by_model[0]["model"], pctf(by_model[0]["total"] / T["total"]), pctf(by_model[0]["api_cost_usd"] / T["api_cost_usd"] if T["api_cost_usd"] else 0), latest,
            ", ".join("%s (%s)" % (r["model"], compact(r["total"])) for r in mm[latest][:4])),
        "Blended cost per million output tokens: %s; these are dominated by the context re-read, not the output rate." % "; ".join("%s %s" % (TOOL_NAME.get(t, t), money(bl(t, "cost_per_M_output_tokens"))) for t in tools_present if blended.get(t)))
    if claude_primary and sc_primary_tokens:
        add("F06", "Low (class B)", "Claude Code is under-counted by transcript retention.",
            lambda: "Surviving transcripts on %s hold %s tokens (%s API-equivalent); Claude Code's own counter reports %s tokens (%s at the same rates) for the same profile since its first session." % (
                claude_primary, compact(claude_primary_row.get("total", 0)), money(claude_primary_row.get("api_cost_usd", 0)), compact(sc_primary_tokens), money(sc_primary_cost)),
            "Raise `cleanupPeriodDays` in `~/.claude/settings.json` or archive `~/.claude/projects` monthly if a complete Claude record is wanted going forward.")
    add("F07", "Medium", "Cost sensitivity to unpublished prices is %s." % ("small" if sens.get("share_on_assumed_prices", 0) < 0.05 else "material"),
        lambda: "%s of the API-equivalent total (%s) rests on models priced by assumption. Halving or doubling every assumed rate moves the total to between %s and %s." % (
            pctf(sens["share_on_assumed_prices"]), money(sens["cost_on_assumed_prices"]), money(sens["band_if_assumed_prices_halved_or_doubled"][0]), money(sens["band_if_assumed_prices_halved_or_doubled"][1])),
        "The headline cost is robust to the pricing assumptions; it is not robust to the cache-read rate, which is where most of the discount comes from.")
    for code, conf, title_, evidence, impl in findings:
        D.h(3, "%s · %s" % (code, title_))
        D.p("**Confidence:** %s. %s" % (conf, evidence))
        D.p("**Implication.** " + impl)

    # ---- 4 results
    D.h(2, "4. Results")
    D.h(3, "4.1 By tool")
    rows = [[TOOL_NAME.get(t, t), fmt(r["calls"]), fmt(r["sessions"]), compact(r["input_uncached"]), compact(r["cache_read"]), compact(r["cache_write"]), compact(r["output"]), compact(r["total"]), pctf(bl(t, "cache_hit_rate", None)), money(r["api_cost_usd"]), money(r["cache_savings_usd"])] for t, r in ((t, by_tool[t]) for t in tools_present)]
    D.table(["Tool", "Calls", "Sessions", "Uncached in", "Cache read", "Cache write", "Output", "Total", "Hit rate", "API-eq.", "Cache saved"], rows, ["l"] + ["r"] * 10)
    if ATOT:
        D.h(3, "4.1b By account")
        rows = [["`%s`" % k, t["label"], t["plan"], fmt(t["months"]), money(t["subscription_usd"]), money(t["api_equivalent_usd"]), money(t["api_if_uncached_usd"]), ("%s×" % t["api_to_sub_ratio"]) if t.get("api_to_sub_ratio") is not None else ("unknown" if t.get("billing") == "unknown" else "usage-based"), fmt(t["calls"]), compact(t["total"])] for k, t in sorted(ATOT.items(), key=lambda kv: -kv[1]["api_equivalent_usd"])]
        D.table(["Account", "Identity", "Plan", "Months", "Paid", "API-eq.", "If uncached", "API / sub", "Calls", "Tokens"], rows, ["l", "l", "l"] + ["r"] * 7)
        if "unattributed" in ATOT:
            D.p("The `unattributed` row holds the %s calls that matched no rule in `accounts.json` (see 2.4); it is not an account and carries no subscription." % fmt(ATOT["unattributed"]["calls"]))
        months_a = sorted({r["month"] for r in AROWS})
        sub_keys = [k for k, _ in sorted(sub_accounts.items(), key=lambda kv: -kv[1]["api_equivalent_usd"])]
        rows = []
        for m in months_a:
            cells, paid = [], 0
            for k in sub_keys:
                r = next((x for x in AROWS if x["month"] == m and x["account"] == k), None)
                cells.append(money(r["api_equivalent_usd"]) if r else "–")
                paid += r["subscription_usd"] if r else 0
            ub = next((x for x in AUB if x["month"] == m), None)
            rows.append([m] + cells + [money(paid), money(ub["api_cost_usd"]) if ub else "–"])
        D.table(["Month"] + [AREG.get(k, {}).get("label", k).split(" / ")[-1] for k in sub_keys] + ["Subscriptions paid", "Usage-based spend"], rows, ["l"] + ["r"] * (len(sub_keys) + 2))
        if APLAN:
            D.table(["Plan recorded on the Codex call", "Calls", "Tokens", "API-eq."], [["`%s`" % r["plan"], fmt(r["calls"]), compact(r["total"]), money(r["api_cost_usd"])] for r in sorted(APLAN, key=lambda r: -r["total"])], ["l", "r", "r", "r"])
    D.h(3, "4.2 By month")
    D.figure(svg_stacked_months(by_month, tools_present, "total", "Tokens by month, stacked by tool", compact), "Figure 1. Tokens per month, stacked by tool.", "*Figure 1 (tokens per month by tool) is rendered in the HTML version.*")
    D.figure(svg_stacked_months(by_month, tools_present, "api_cost_usd", "API-equivalent cost by month", lambda v: "$%s" % compact(v)), "Figure 2. API-equivalent cost per month, stacked by tool.", "*Figure 2 (API-equivalent cost per month) is rendered in the HTML version.*")
    months = sorted({r["month"] for r in by_month if r["month"] != "?"})
    rows = []
    for m in months:
        rs = [r for r in by_month if r["month"] == m]
        cm = A.get("cache_month", {}).get(m, {})
        sub = sum(r["subscription_usd"] for r in AROWS if r["month"] == m) if AROWS else sum(r["subscription_usd"] for r in sub_rows if r["month"] == m)
        cost = sum(r["api_cost_usd"] for r in rs)
        rows.append([m, fmt(sum(r["calls"] for r in rs)), compact(sum(r["total"] for r in rs)), compact(sum(r["output"] for r in rs))] +
                    [pctf(cm[t]["hit_rate"]) if t in cm and cm[t].get("hit_rate") is not None else "–" for t in tools_present[:2]] +
                    [money(cost), money(sub), ("%.1f×" % (cost / sub)) if sub else "–"])
    D.table(["Month", "Calls", "Tokens", "Output"] + ["%s hit" % TOOL_NAME.get(t, t) for t in tools_present[:2]] + ["API-eq.", "Subscriptions", "API/sub"], rows, ["l"] + ["r"] * (7 + min(2, len(tools_present))))
    hit_series = [(TOOL_NAME.get(t, t), TOOL_VAR.get(t, "--ink-3"), [(m, 100 * A["cache_month"][m][t]["hit_rate"]) for m in months if t in A.get("cache_month", {}).get(m, {}) and A["cache_month"][m][t]["hit_rate"] is not None]) for t in tools_present[:2]]
    D.figure(svg_lines_months(hit_series, "Cache hit rate by month"), "Figure 3. Cache hit rate (cache reads as a share of all prompt tokens) by month.", "*Figure 3 (cache hit rate by month) is rendered in the HTML version.*")
    D.h(3, "4.3 By model")
    rows = [["`%s`" % r["model"], TOOL_NAME.get(r["tool"], r["tool"]), fmt(r["calls"]), compact(r["total"]), pctf(r["total"] / T["total"]), compact(r["output"]), pctf(r["cache_read"] / (r["input_uncached"] + r["cache_read"] + r["cache_write"])) if (r["input_uncached"] + r["cache_read"] + r["cache_write"]) else "–", money(r["api_cost_usd"])] for r in by_model[:22]]
    D.table(["Model", "Tool", "Calls", "Tokens", "Share", "Output", "Hit rate", "API-eq."], rows, ["l", "l"] + ["r"] * 6)
    D.h(3, "4.4 Distributions")
    rows = [[TOOL_NAME.get(t, t), fmt(d["prompt_tokens_per_call"]["n"]), compact(d["prompt_tokens_per_call"]["p50"]), compact(d["prompt_tokens_per_call"]["p90"]), compact(d["prompt_tokens_per_call"]["p99"]), compact(d["prompt_tokens_per_call"]["max"]), compact(d["output_tokens_per_call"]["p50"]), compact(d["output_tokens_per_call"]["p90"]), compact(d["output_tokens_per_call"]["p99"]), compact(d["output_tokens_per_call"]["max"])]
            for t in tools_present for d in [dist.get(t, {})] if d.get("prompt_tokens_per_call", {}).get("n")]
    D.table(["Tool", "Calls", "Prompt p50", "p90", "p99", "max", "Output p50", "p90", "p99", "max"], rows, ["l"] + ["r"] * 9)
    rows = []
    for t in tools_present:
        s = sdist.get(t, {})
        if s.get("total", {}).get("n"):
            hh = s.get("hours", {}) if s.get("hours", {}).get("n") else None
            rows.append([TOOL_NAME.get(t, t), fmt(s["total"]["n"]), fmt(s["calls"]["p50"]), fmt(s["calls"]["p90"]), fmt(s["calls"]["max"]), compact(s["total"]["p50"]), compact(s["total"]["p90"]), compact(s["total"]["max"]), "%.1f h" % hh["p50"] if hh else "–", "%.1f h" % hh["p90"] if hh else "–", "%.0f h" % hh["max"] if hh else "–"])
    D.table(["Tool", "Sessions", "Calls p50", "p90", "max", "Tokens p50", "p90", "max", "Span p50", "p90", "max"], rows, ["l"] + ["r"] * 10)
    D.h(3, "4.5 Time of day")
    hw = A.get("hour_weekday_calls", {})
    mat = [[sum((hw.get(t) or [[0] * 24] * 7)[d][h] for t in tools_present[:2]) for h in range(24)] for d in range(7)]
    D.p("Calls by weekday and hour (%s), %s combined. Darker cells are more calls; the scale is square-root so unattended loops do not flatten everything else." % (a.tz, " and ".join(TOOL_NAME.get(t, t) for t in tools_present[:2])))
    D.figure(svg_heatmap(mat, "Calls by weekday and hour"), "Figure 4. Model calls by weekday and hour of day, %s." % a.tz, "*Figure 4 (weekday × hour heatmap) is rendered in the HTML version.*")
    hour_tot = [sum(mat[d][h] for d in range(7)) for h in range(24)]
    D.p("Busiest hours: " + ", ".join("%02d:00 (%s)" % (h, fmt(hour_tot[h])) for h in sorted(range(24), key=lambda h: -hour_tot[h])[:5]) + ". Quietest: " + ", ".join("%02d:00 (%s)" % (h, fmt(hour_tot[h])) for h in sorted(range(24), key=lambda h: hour_tot[h])[:3]) + ".")
    D.h(3, "4.6 Heaviest sessions")
    ts_ = A.get("top_sessions", [])
    D.table(["Tool", "Host", "Thread", "Working directory (tail)", "Model", "Calls", "Hours", "Tokens", "Output", "API-eq."],
            [[TOOL_NAME.get(s["tool"], s["tool"]), s["host"], "`%s`" % s["session"][:13], pshow(s["cwd"] or "")[-48:], s["model"], fmt(s["calls"]), "%.0f" % (s["hours"] or 0), compact(s["total"]), compact(s["output"]), money(s["cost"])] for s in ts_[:20]], ["l"] * 5 + ["r"] * 5)
    D.figure(svg_bars([("%s · %s" % (TOOL_NAME.get(s["tool"], s["tool"]), tail(s["cwd"]) or s["session"][:8]), s["total"]) for s in ts_[:12]], "Top sessions by tokens", compact), "Figure 5. Twelve largest sessions by tokens.", "*Figure 5 (largest sessions) is rendered in the HTML version.*")
    D.h(3, "4.7 Working directories")
    D.table(["Tool", "Directory", "Sessions", "Calls", "Tokens", "API-eq."], [[TOOL_NAME.get(r["tool"], r["tool"]), "`%s`" % pshow(r["cwd"]), fmt(r["sessions"]), fmt(r["calls"]), compact(r["total"]), money(r["api_cost_usd"])] for r in S["by_project"][:20]], ["l", "l", "r", "r", "r", "r"])
    D.h(3, "4.8 Entry points, effort and versions")
    D.table(["Tool", "Entry point / originator", "Calls", "Tokens", "API-eq."], [[TOOL_NAME.get(r["tool"], r["tool"]), pshow(r["entrypoint"]), fmt(r["calls"]), compact(r["total"]), money(r["cost"])] for r in A.get("entrypoints", [])[:12]], ["l", "l", "r", "r", "r"])
    rows = [[TOOL_NAME.get(t, t), k, fmt(v["calls"]), compact(v["output"]), pctf(v["reasoning"] / v["output"]) if v["output"] else "–", money(v["cost"])] for t in tools_present[:2] for k, v in sorted(A.get("effort", {}).get(t, {}).items(), key=lambda kv: -kv[1]["calls"])]
    D.table(["Tool", "Effort setting", "Calls", "Output", "Reasoning share", "API-eq."], rows, ["l", "l", "r", "r", "r", "r"])
    D.p("Client versions seen: " + "; ".join("**%s** %s" % (TOOL_NAME.get(t, t), ", ".join("%s (%s)" % (v, fmt(c)) for v, c in vs[:6])) for t, vs in A.get("versions", {}).items() if t in tools_present[:2]) + ".")
    tw = (ttl.get("cache_write_5m", 0) + ttl.get("cache_write_1h", 0))
    if tw:
        D.h(3, "4.9 Cache write TTL (Claude Code)")
        D.p("Of %s cache-write tokens in Claude Code transcripts, %s were 1-hour writes (2× input rate) and %s were 5-minute writes (1.25×)." % (compact(tw), pctf(ttl["cache_write_1h"] / tw), pctf(ttl["cache_write_5m"] / tw)))

    # ---- 5 uncertainty
    D.h(2, "5. Uncertainty and limitations")
    lim = [
        "**Retention.** Claude Code transcripts older than the retention window are gone (F06). Codex keeps rollouts indefinitely; Codex coverage is complete for the scanned profiles. Copilot CLI keeps only recent sessions.",
        "**Replay filter.** The gap rule that strips replayed history from forked Codex rollouts is a heuristic. A genuine first response arriving within 2 s of the end of the replay burst would be dropped; a pause of more than 2 s inside the burst would leave the rest of the parent's history counted. The per-thread comparison in 2.5 bounds the effect.",
        "**Prices are list prices at one date.** Provider rates change; everything is priced at the sheet in `pricing.json`. Historical months are approximations, not invoices.",
        "**Tokenizer.** Token counts across model generations are not directly comparable as measures of text volume.",
        "**Subscription counterfactual.** The API-equivalent figure assumes identical traffic on a pay-as-you-go key. In practice each subscription's rate limits shaped the traffic.",
        "**Account attribution.** Codex records the billing plan per call but not the account, so accounts are assigned by rules whose evidence and confidence are listed in 2.4; medium- and low-confidence rules are the ones to challenge first.",
        "**Timestamps.** Tool timestamps are UTC at write time; time-of-day analysis converts to %s. Sessions spanning DST changes are not adjusted." % a.tz,
    ] + CFG.get("extra_limitations", [])
    D.ul(lim)

    # ---- 6 reproducibility
    D.h(2, "6. Reproducibility")
    D.p(CFG.get("reproduce_intro", "All scripts are standard-library Python 3.8+. Scans run on each host (natively where possible), then one report step merges them."))
    D.code("\n".join(CFG.get("reproduce_commands") or [
        "python scripts/run_pipeline.py --manifest manifest.json          # scan every host in the manifest, then report, analyse, build",
        "python scripts/run_pipeline.py --manifest manifest.json --only report,analyze,build   # re-price / re-render without rescanning",
    ]))
    here = os.path.dirname(os.path.abspath(__file__))
    hashes = [(os.path.basename(p), sha256(p)) for p in (os.path.join(here, "compile_ai_logs.py"), os.path.join(here, "analyze_events.py"), os.path.join(here, "build_report.py"), a.pricing, os.path.join(a.compiled, "summary.json"), os.path.join(a.compiled, "analysis.json")) if os.path.isfile(p)]
    D.table(["File", "SHA-256"], [[f_, "`%s`" % h] for f_, h in hashes], ["l", "l"])
    D.p("The event-level dataset (`compiled/all_events.csv`, %s rows, one per model call with every token class, the pricing row applied, the account assigned and the source file path) is the primary artefact; every table above is an aggregation of it." % fmt(A.get("events", total_calls)))

    D.h(2, "Appendix A. Glossary")
    D.table(["Term", "Definition"], [
        ["Call", "One model request whose usage the tool recorded: an assistant message (Claude Code, OpenClaw, opencode), a `token_count` event (Codex), or a session (Copilot CLI)."],
        ["Session / thread", "One transcript file (Claude Code), one rollout file (Codex), one OpenClaw session file, one opencode session, one Copilot session."],
        ["Sub-agent", "A Codex thread spawned by another thread (`source.subagent`) or a Claude Code `agent-*.jsonl` transcript."],
        ["Cache hit rate", "`cache_read ÷ (input_uncached + cache_read + cache_write)`."],
        ["API-equivalent cost", "Tokens × list price per token class, from `pricing.json`."],
        ["Cache saving", "`cost_if_uncached − api_cost`, where `cost_if_uncached` prices every prompt token at the input rate."],
        ["Account", "A login identified from a credential file (or a per-host placeholder when credential files were not read); assigned to calls by the rules in accounts.json."],
        ["Usage-based", "A call billed per token to a prepaid or metered org rather than covered by a subscription."],
    ], ["l", "l"])
    D.h(2, "Appendix B. Package contents")
    D.ul(["`USAGE_REPORT.md` — this document.", "`report.html` — the same document with the figures rendered.", "`ledger.json` — machine-readable totals, monthly and model tables, top sessions, validation results, sensitivity, accounts, source inventory and the pricing sheet used" + (" (with absolute scan roots, full working directories and the report configuration: `package_paths` is on)." if a.package_paths else " (scan roots and working directories reduced to their last path component; the report configuration omitted)."), "`pricing.json` — the rate sheet applied.", "`SENSITIVITY.md` — what in this package names hosts, directories, accounts or paths, and how to check or anonymise it before sharing.", "`SHA256SUMS` — binds the files above."])

    # ---- write package
    safety.private_dir(a.out)
    with safety.private_open(os.path.join(a.out, "USAGE_REPORT.md"), "w") as fh:
        fh.write("\n".join(D.md))
    ledger = OrderedDict([
        ("snapshot_date", a.date), ("generated_utc", gen.isoformat()), ("timezone", a.tz),
        ("scope", {"tools": tools_present, "hosts": hosts_all, "first_date": dates[0] if dates else None, "last_date": dates[-1] if dates else None, "active_days": len(dates)}),
        ("totals", T), ("events", total_calls), ("sessions", S["sessions"]), ("prompts", S["prompts"]),
        ("by_tool", S["by_tool"]), ("by_tool_host", S["by_tool_host"]), ("by_month_tool", by_month), ("by_model", by_model), ("by_kind", S["by_kind"]),
        ("by_entrypoint", S["by_entrypoint"] if a.package_paths else redact_rows(S["by_entrypoint"], "entrypoint")),
        ("by_project_top", S["by_project"] if a.package_paths else redact_rows(S["by_project"], "cwd")),
        ("top_sessions", A.get("top_sessions", []) if a.package_paths else redact_rows(A.get("top_sessions", []), "cwd")),
        ("subscriptions", {"totals": ST, "rows": sub_rows}), ("accounts", ACC),
        ("caching", {"by_month": A.get("cache_month"), "ttl_split_claude": ttl, "blended_rates": blended}),
        ("distributions", {"per_call": dist, "per_session": sdist, "concentration": conc}),
        ("time_of_day", {"weekday_hour_calls": hw}), ("effort", A.get("effort")), ("versions", A.get("versions")),
        ("validation", {"codex_sqlite": val, "codex_app_total_with_replay": sq_total, "claude_stats_cache": [{"host": h, "model": m, "tokens": t, "output": o, "api_equivalent_usd": c} for h, m, t, o, c in sc_rows]}),
        ("sensitivity", sens), ("coverage", {"%s|%s" % k: v for k, v in cov.items()}), ("scan_inventory", inv if a.package_paths else redact_inventory(inv)),
        ("pricing", P), ("script_hashes", dict(hashes)),
    ])
    if a.package_paths:  # the report config names hosts, directories and branding contacts: packaged only on request
        ledger["config"] = CFG
    with safety.private_open(os.path.join(a.out, "ledger.json"), "w") as fh:
        json.dump(ledger, fh, indent=1, default=str)
    safety.private_copy(a.pricing, os.path.join(a.out, "pricing.json"))
    with safety.private_open(os.path.join(a.out, "README.md"), "w") as fh:
        fh.write("""# AI usage ledger package

Snapshot date: %s (%s). Read-only study of locally recorded AI coding-agent usage.

Start with `USAGE_REPORT.md` (or `report.html` for the figures). It contains the executive summary, evidence rules, source inventory, method, findings with confidence levels, per-account results, full result tables, uncertainty and limitations, and reproduction steps.

`ledger.json` is the machine-readable ledger. `pricing.json` is the rate sheet applied.

`SENSITIVITY.md` lists what in this package names hosts, project directories, accounts or file-system paths, and how to check or anonymise it before it is shared. Read it before sending the package anywhere.

Nothing was changed on any host. Dollar figures are API-equivalents at list prices, not invoices. Claude Code figures are lower bounds where the tool's retention window has deleted transcripts.

SHA256SUMS binds the content files in this package.
""" % (a.date, a.tz))
    write_sensitivity(a.out, a.package_paths)
    with safety.private_open(os.path.join(a.out, "report.html"), "w") as fh:
        _style, _header, _footer, _link = brand_blocks(CFG, os.path.dirname(os.path.abspath(a.config)) if a.config else None)
        _theme = str(CFG.get("theme_default") or "system")
        fh.write(HTML_HEAD.replace("__TITLE__", _html.escape(str(CFG.get("html_title", "Agent Usage Study")), quote=True)) + _link + _style + THEME_JS.replace("__THEME_DEFAULT__", _theme if _theme in ("light", "dark", "system") else "system") + THEMEBAR_HTML + '<div class="wrap">' + _header + "\n".join(D.html) + _footer + "</div>")
    write_sums(a.out)
    print("package written to", a.out)


THEME_JS = '<script>\n(function(){\n  var KEY="ledger-theme", root=document.documentElement;\n  function apply(v){ if(v==="light"||v==="dark"){root.setAttribute("data-theme",v);}else{root.removeAttribute("data-theme");} document.querySelectorAll(".themebar button").forEach(function(b){b.classList.toggle("on", b.dataset.t===(v||"system"));}); }\n  var DEF="__THEME_DEFAULT__", saved=null; try{saved=localStorage.getItem(KEY);}catch(e){}\n  if(!saved && (DEF==="light"||DEF==="dark")) saved=DEF;\n  apply(saved);\n  document.addEventListener("click",function(ev){ var b=ev.target.closest(".themebar button"); if(!b) return; var v=b.dataset.t; try{ if(v==="system") localStorage.removeItem(KEY); else localStorage.setItem(KEY,v);}catch(e){} apply(v==="system"?null:v); });\n})();\n</script>'
THEMEBAR_HTML = '<div class="themebar" role="group" aria-label="Colour theme"><button type="button" data-t="light">Light</button><button type="button" data-t="system" class="on">System</button><button type="button" data-t="dark">Dark</button></div>'
HTML_HEAD = r"""<meta charset="utf-8"><title>__TITLE__</title>
<style>
:root{color-scheme:light;--bg:#f6f6f3;--surface:#ffffff;--surface-2:#eeeeea;--ink:#1a1a17;--ink-2:#55554f;--ink-3:#8a8a82;--line:#e2e2dc;--line-2:#cfcfc7;
--codex:#2a78d6;--claude:#eb6834;--copilot:#1baf7a;--opencode:#eda100;--openclaw:#e87ba4;
--seq0:#eeeeea;--seq1:#cde2fb;--seq2:#9ec5f4;--seq3:#6da7ec;--seq4:#3987e5;--seq5:#256abf;--seq6:#0d366b;--focus:#2a78d6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#16161a;--surface:#1e1e23;--surface-2:#27272d;--ink:#f1f1ec;--ink-2:#b6b6ad;--ink-3:#7f7f78;--line:#2e2e35;--line-2:#3c3c45;
--codex:#3987e5;--claude:#d95926;--copilot:#199e70;--opencode:#c98500;--openclaw:#d55181;
--seq0:#27272d;--seq1:#1b2a3f;--seq2:#184f95;--seq3:#1c5cab;--seq4:#256abf;--seq5:#3987e5;--seq6:#9ec5f4}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#16161a;--surface:#1e1e23;--surface-2:#27272d;--ink:#f1f1ec;--ink-2:#b6b6ad;--ink-3:#7f7f78;--line:#2e2e35;--line-2:#3c3c45;
--codex:#3987e5;--claude:#d95926;--copilot:#199e70;--opencode:#c98500;--openclaw:#d55181;
--seq0:#27272d;--seq1:#1b2a3f;--seq2:#184f95;--seq3:#1c5cab;--seq4:#256abf;--seq5:#3987e5;--seq6:#9ec5f4}
*{box-sizing:border-box}html,body{overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Source Serif 4",Georgia,"Times New Roman",serif;font-size:16px;line-height:1.55}
.wrap{max-width:960px;margin:0 auto;padding:40px 28px 80px}
h1,h2,h3{font-family:"IBM Plex Sans",system-ui,sans-serif;text-wrap:balance;line-height:1.15;margin:0}
h1{font-size:34px;font-weight:600;margin-bottom:14px;letter-spacing:-.01em}
h2{font-size:22px;font-weight:600;margin-top:44px;padding-top:14px;border-top:1px solid var(--line-2)}
h3{font-size:16px;font-weight:600;margin-top:26px;color:var(--ink)}
p{margin:10px 0;max-width:72ch}
ul,ol{max-width:72ch;padding-left:22px}li{margin:6px 0}
code{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;font-size:.85em;background:var(--surface-2);padding:1px 4px;border-radius:3px}
pre{background:var(--surface);border:1px solid var(--line);padding:12px 14px;overflow-x:auto;font-size:12.5px;line-height:1.5}pre code{background:none;padding:0}
.tw{overflow-x:auto;margin:12px 0 18px}
table{border-collapse:collapse;width:100%;background:var(--surface);border:1px solid var(--line);font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:13px}
th,td{padding:6px 9px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);font-weight:500;background:var(--surface-2);white-space:nowrap}
td.n,th.n{text-align:right;white-space:nowrap;font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums;font-size:12.5px}
tr:last-child td{border-bottom:0}
figure{margin:18px 0 26px}figcaption{font-family:"IBM Plex Sans",sans-serif;font-size:12.5px;color:var(--ink-2);margin-top:8px}
.chart{background:var(--surface);border:1px solid var(--line);padding:14px 10px 6px;overflow-x:auto}
svg{display:block;max-width:100%;font-family:"IBM Plex Mono",monospace;font-size:11px}
svg text{fill:var(--ink-2)}svg .ink{fill:var(--ink)}svg .ink-2{fill:var(--ink-2)}svg .mono{font-family:"IBM Plex Mono",monospace}
svg .grid{stroke:var(--line);stroke-width:1}svg .axis{stroke:var(--line-2);stroke-width:1}
a{color:var(--codex)}a:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.themebar{position:fixed;top:10px;right:10px;display:inline-flex;border:1px solid var(--line-2);border-radius:3px;overflow:hidden;background:var(--surface);z-index:20;font-family:"IBM Plex Sans",system-ui,sans-serif}
.themebar button{font:inherit;font-size:11px;letter-spacing:.04em;padding:4px 9px;background:transparent;color:var(--ink-2);border:0;border-right:1px solid var(--line-2);cursor:pointer}
.themebar button:last-child{border-right:0}.themebar button.on{background:var(--ink);color:var(--bg)}
.themebar button:focus-visible{outline:2px solid var(--focus);outline-offset:-2px}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:14px;font-family:"IBM Plex Sans",system-ui,sans-serif}
.brand img{height:36px;width:auto;max-width:200px}
.brand .name{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
.brandfoot{margin-top:48px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--ink-3);font-family:"IBM Plex Sans",system-ui,sans-serif}
@media (prefers-reduced-motion:no-preference){.themebar button{transition:background .15s}}
</style>
"""

if __name__ == "__main__":
    main()
