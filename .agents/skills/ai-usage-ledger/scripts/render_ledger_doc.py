#!/usr/bin/env python3
"""
render_ledger_doc.py - list and render the ledger document templates (references/ledger-document-catalog.md).

    python3 render_ledger_doc.py --list [--stage finance] [--type memo]
    python3 render_ledger_doc.py --template executive-summary --compiled <workdir>/compiled --var prepared_for="Finance"
    python3 render_ledger_doc.py --template account-statement --var account=codex:a3523532 --out statement.md --pdf --docx
    python3 render_ledger_doc.py --template client-billing-evidence-summary --var project=acme --anonymize

Every ledger placeholder is filled from compiled/summary.json (+ analysis.json when present). With no --compiled the
renderer uses the ledger configured by `ledger.py init` (its workdir/compiled, or workdir/anonymized/compiled with
--anonymize) and its saved branding. Output is Markdown, plus a self-contained themed HTML page; --pdf and --docx add
those formats through render_pdf.py when reportlab / python-docx are installed.

Standard library only for Markdown and HTML.
"""
import argparse
import html
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATALOG = os.path.join(ROOT, "references", "ledger-document-catalog.md")
INDEX = os.path.join(ROOT, "references", "template-index.json")
sys.path.insert(0, HERE)
import safety  # noqa: E402


# --------------------------------------------------------------------------- catalog
def load_index():
    with open(INDEX, encoding="utf-8") as fh:
        return json.load(fh)["templates"]


def extract_template(template_id):
    with open(CATALOG, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^### %s\n(?P<body>.*?)(?=^### |\Z)" % re.escape(template_id), text, re.MULTILINE | re.DOTALL)
    if not m:
        raise KeyError("template not found in the catalog: %s" % template_id)
    body = m.group("body").strip()
    body = re.sub(r"^Use when:.*?\n\n", "", body, count=1, flags=re.DOTALL)
    return body


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


# --------------------------------------------------------------------------- formatting
def fmt_int(n):
    try:
        return "{:,}".format(int(round(float(n or 0))))
    except (TypeError, ValueError):
        return str(n)


def fmt_usd(x):
    x = float(x or 0)
    return "$%s" % ("{:,.2f}".format(x) if abs(x) < 1000 else "{:,.0f}".format(x))


def fmt_pct(x):
    return "%.1f%%" % (100 * float(x or 0))


def compact(n):
    n = float(n or 0)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            return ("%.2f" % (n / div)).rstrip("0").rstrip(".") + suf
    return fmt_int(n)


def table(headers, rows, align=None):
    align = align or ["---"] * len(headers)
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(align) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out) if rows else "_no rows_"


def tail(path):
    return (path or "?").replace("\\", "/").rstrip("/").split("/")[-1] or path


# --------------------------------------------------------------------------- ledger -> placeholders
def load_ledger(compiled):
    with open(os.path.join(compiled, "summary.json"), encoding="utf-8") as fh:
        S = json.load(fh)
    A = None
    p = os.path.join(compiled, "analysis.json")
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as fh:
            A = json.load(fh)
    return S, A


def placeholders(S, A, brand, var, config=None):
    T = S.get("total") or {}
    months = sorted({r["month"] for r in S.get("by_month_tool", [])})
    by_month = {}
    for r in S.get("by_month_tool", []):
        m = by_month.setdefault(r["month"], {"total": 0, "calls": 0, "api": 0.0, "save": 0.0, "nocache": 0.0})
        m["total"] += r["total"]
        m["calls"] += r["calls"]
        m["api"] += r["api_cost_usd"]
        m["save"] += r["cache_savings_usd"]
        m["nocache"] += r["cost_if_uncached_usd"]
    days = sorted({r["date"] for r in S.get("by_day_tool", []) if r.get("date") and r["date"] != "?"})
    tools = sorted(S.get("by_tool", []), key=lambda r: -r["total"])
    models = sorted(S.get("by_model", []), key=lambda r: -r["total"])
    projects = sorted(S.get("by_project", []), key=lambda r: -r["total"])
    hosts_rows = sorted(S.get("by_tool_host", []), key=lambda r: -r["total"])
    acc = S.get("accounts") or {}
    sub_tot = acc.get("subscription_totals") or {}
    by_account = sorted(acc.get("by_account", []), key=lambda r: -r["total"])
    total = float(T.get("total") or 0) or 1.0
    P = {}
    P["brand_name"] = brand.get("name") or "Ledger"
    P["brand_eyebrow"] = brand.get("eyebrow") or ""
    P["brand_contact"] = brand.get("contact") or ""
    P["date"] = date.today().isoformat()
    P["snapshot_date"] = (S.get("generated") or "")[:10] or P["date"]
    P["period_start"] = days[0] if days else (months[0] + "-01" if months else "?")
    P["period_end"] = days[-1] if days else (months[-1] if months else "?")
    P["period"] = "%s to %s" % (P["period_start"], P["period_end"])
    P["months_count"] = str(len(months))
    host_names = sorted({r["host"] for r in hosts_rows})
    P["hosts"] = ", ".join(host_names) or "?"
    P["hosts_count"] = str(len(host_names))
    P["tools"] = ", ".join(r["tool"] for r in tools) or "?"
    P["tools_count"] = str(len(tools))
    P["total_calls"] = fmt_int(T.get("calls"))
    P["total_sessions"] = fmt_int(S.get("sessions") or sum(r.get("sessions", 0) for r in tools))
    P["total_tokens"] = fmt_int(T.get("total"))
    P["input_uncached"] = fmt_int(T.get("input_uncached"))
    P["cache_read"] = fmt_int(T.get("cache_read"))
    P["cache_write"] = fmt_int(T.get("cache_write"))
    P["output_tokens"] = fmt_int(T.get("output"))
    P["reasoning_tokens"] = fmt_int(T.get("reasoning"))
    prompt = float(T.get("input_uncached", 0) + T.get("cache_read", 0) + T.get("cache_write", 0)) or 1.0
    P["cache_read_share_pct"] = fmt_pct(T.get("cache_read", 0) / prompt)
    P["api_equivalent_usd"] = fmt_usd(T.get("api_cost_usd"))
    P["cost_if_uncached_usd"] = fmt_usd(T.get("cost_if_uncached_usd"))
    P["cache_savings_usd"] = fmt_usd(T.get("cache_savings_usd"))
    P["cache_savings_pct"] = fmt_pct((T.get("cache_savings_usd") or 0) / (float(T.get("cost_if_uncached_usd") or 0) or 1.0))
    sub_usd = sum(v.get("subscription_usd", 0) for v in sub_tot.values())
    sub_api = sum(v.get("api_equivalent_usd", 0) for v in sub_tot.values())
    P["subscription_usd"] = fmt_usd(sub_usd)
    P["subscription_accounts_count"] = str(sum(1 for v in sub_tot.values() if v.get("subscription_usd")))
    P["subscription_months"] = str(sum(v.get("months", 0) for v in sub_tot.values() if v.get("subscription_usd")))
    P["api_to_sub_ratio"] = "%.2f" % (sub_api / sub_usd) if sub_usd else "n/a"
    P["subscription_savings_usd"] = fmt_usd(sub_api - sub_usd)
    P["usage_based_usd"] = fmt_usd(sum(r["api_cost_usd"] for r in acc.get("by_billing_month", []) if r.get("billing") == "usage-based"))
    if tools:
        P["top_tool"], P["top_tool_share_pct"] = tools[0]["tool"], fmt_pct(tools[0]["total"] / total)
    if models:
        P["top_model"], P["top_model_share_pct"] = models[0]["model"], fmt_pct(models[0]["total"] / total)
    if projects:
        P["top_project"], P["top_project_share_pct"] = tail(projects[0]["cwd"]), fmt_pct(projects[0]["total"] / total)
    if months:
        busiest = max(months, key=lambda m: by_month[m]["total"])
        P["busiest_month"], P["busiest_month_tokens"] = busiest, fmt_int(by_month[busiest]["total"])
        P["latest_month"], P["latest_month_tokens"], P["latest_month_api_usd"] = months[-1], fmt_int(by_month[months[-1]]["total"]), fmt_usd(by_month[months[-1]]["api"])
        if len(months) > 1:
            prev = months[-2]
            P["prev_month"], P["prev_month_tokens"] = prev, fmt_int(by_month[prev]["total"])
            pv = by_month[prev]["total"] or 1
            P["month_over_month_pct"] = "%+.1f%%" % (100.0 * (by_month[months[-1]]["total"] - pv) / pv)
        else:
            P["prev_month"], P["prev_month_tokens"], P["month_over_month_pct"] = "n/a", "n/a", "n/a"
        n = float(len(months))
        P["run_rate_monthly_tokens"] = fmt_int(total / n)
        rr_usd = float(T.get("api_cost_usd") or 0) / n
        P["run_rate_monthly_usd"] = fmt_usd(rr_usd)
        P["projected_12mo_api_usd"] = fmt_usd(rr_usd * 12)
        P["projected_12mo_subscription_usd"] = fmt_usd(12 * sum(v.get("subscription_usd", 0) / max(v.get("months", 1), 1) for v in sub_tot.values() if v.get("subscription_usd")))
    assumed = (S.get("costs") or {}).get("assumed_models") or {}
    P["assumed_models"] = ", ".join("%s (%s)" % (k, v) for k, v in assumed.items()) or "none"
    excluded = (config or {}).get("excluded_sources") or []
    P["excluded_sources"] = "; ".join((x if isinstance(x, str) else json.dumps(x)).rstrip(".") for x in excluded) or "none recorded"
    low = [r for r in acc.get("rules", []) if r.get("confidence") in ("low", "medium")]
    P["low_confidence_rules"] = "; ".join("%s -> %s (%s)" % (", ".join("%s=%s" % kv for kv in (r.get("when") or {}).items()) or "any other call", r.get("account"), r.get("confidence")) for r in low) or "none"
    # tables
    P["tools_table"] = table(["Tool", "Calls", "Sessions", "Tokens", "Cache read share", "API-equivalent", "Cache savings"],
                             [[r["tool"], fmt_int(r["calls"]), fmt_int(r.get("sessions", 0)), fmt_int(r["total"]),
                               fmt_pct(r["cache_read"] / (float(r["input_uncached"] + r["cache_read"] + r["cache_write"]) or 1.0)), fmt_usd(r["api_cost_usd"]), fmt_usd(r["cache_savings_usd"])] for r in tools],
                             ["---", "---:", "---:", "---:", "---:", "---:", "---:"])
    P["months_table"] = table(["Month", "Calls", "Tokens", "API-equivalent", "Without cache", "Cache savings"],
                              [[m, fmt_int(by_month[m]["calls"]), fmt_int(by_month[m]["total"]), fmt_usd(by_month[m]["api"]), fmt_usd(by_month[m]["nocache"]), fmt_usd(by_month[m]["save"])] for m in months],
                              ["---", "---:", "---:", "---:", "---:", "---:"])
    P["models_table"] = table(["Tool", "Model", "Calls", "Tokens", "Share", "API-equivalent"],
                              [[r["tool"], r["model"], fmt_int(r["calls"]), fmt_int(r["total"]), fmt_pct(r["total"] / total), fmt_usd(r["api_cost_usd"])] for r in models[:25]],
                              ["---", "---", "---:", "---:", "---:", "---:"])
    P["projects_table"] = table(["Project (directory)", "Tool", "Calls", "Sessions", "Tokens", "Share", "API-equivalent"],
                                [[tail(r["cwd"]), r["tool"], fmt_int(r["calls"]), fmt_int(r.get("sessions", 0)), fmt_int(r["total"]), fmt_pct(r["total"] / total), fmt_usd(r["api_cost_usd"])] for r in projects[:25]],
                                ["---", "---", "---:", "---:", "---:", "---:", "---:"])
    reg = acc.get("registry") or {}
    P["accounts_table"] = table(["Account", "Plan", "Calls", "Tokens", "API-equivalent", "Cache savings"],
                                [[(reg.get(r["account"]) or {}).get("label") or r["account"], (reg.get(r["account"]) or {}).get("plan") or "?", fmt_int(r["calls"]), fmt_int(r["total"]), fmt_usd(r["api_cost_usd"]), fmt_usd(r["cache_savings_usd"])] for r in by_account],
                                ["---", "---", "---:", "---:", "---:", "---:"])
    P["subscription_table"] = table(["Account", "Plan", "Active months", "Subscription paid", "API-equivalent", "Ratio"],
                                    [[v.get("label") or k, v.get("plan"), v.get("months"), fmt_usd(v.get("subscription_usd")), fmt_usd(v.get("api_equivalent_usd")), "%.2f" % (v.get("api_to_sub_ratio") or 0)]
                                     for k, v in sorted(sub_tot.items(), key=lambda kv: -(kv[1].get("api_equivalent_usd") or 0)) if v.get("subscription_usd")],
                                    ["---", "---", "---:", "---:", "---:", "---:"])
    inv_rows = []
    for inv in S.get("inventory", []):
        for r in inv.get("roots", []):
            inv_rows.append([inv.get("host"), r.get("tool"), r.get("root"), fmt_int(r.get("events", 0))])
    P["hosts_table"] = table(["Host", "Tool", "Location", "Calls"], inv_rows or [[h, "", "", ""] for h in host_names], ["---", "---", "---", "---:"])
    P["billing_table"] = table(["Month", "Billing", "Calls", "Tokens", "API-equivalent"],
                               [[r["month"], r["billing"], fmt_int(r["calls"]), fmt_int(r["total"]), fmt_usd(r["api_cost_usd"])] for r in sorted(acc.get("by_billing_month", []), key=lambda r: (r["month"], r["billing"]))],
                               ["---", "---", "---:", "---:", "---:"])
    # month scope
    month = var.get("month") or (months[-1] if months else None)
    if month:
        mt = [r for r in S.get("by_month_tool", []) if r["month"] == month]
        mm = by_month.get(month, {"total": 0, "calls": 0, "api": 0.0, "save": 0.0})
        P["month"], P["month_tokens"], P["month_calls"], P["month_api_usd"], P["month_cache_savings_usd"] = month, fmt_int(mm["total"]), fmt_int(mm["calls"]), fmt_usd(mm["api"]), fmt_usd(mm["save"])
        P["month_tools_table"] = table(["Tool", "Calls", "Tokens", "API-equivalent", "Cache savings"], [[r["tool"], fmt_int(r["calls"]), fmt_int(r["total"]), fmt_usd(r["api_cost_usd"]), fmt_usd(r["cache_savings_usd"])] for r in sorted(mt, key=lambda r: -r["total"])], ["---", "---:", "---:", "---:", "---:"])
        ma = [r for r in acc.get("by_account_month", []) if r["month"] == month]
        P["month_accounts_table"] = table(["Account", "Calls", "Tokens", "API-equivalent"], [[(reg.get(r["account"]) or {}).get("label") or r["account"], fmt_int(r["calls"]), fmt_int(r["total"]), fmt_usd(r["api_cost_usd"])] for r in sorted(ma, key=lambda r: -r["total"])], ["---", "---:", "---:", "---:"])
    # account scope
    akey = var.get("account") or (by_account[0]["account"] if by_account else None)
    if akey:
        a_row = next((r for r in by_account if r["account"] == akey), None) or {"calls": 0, "total": 0, "api_cost_usd": 0}
        st = sub_tot.get(akey) or {}
        P["account"] = akey
        P["account_label"] = (reg.get(akey) or {}).get("label") or st.get("label") or akey
        P["account_plan"] = (reg.get(akey) or {}).get("plan") or st.get("plan") or "?"
        P["account_calls"], P["account_tokens"], P["account_api_usd"] = fmt_int(a_row["calls"]), fmt_int(a_row["total"]), fmt_usd(a_row["api_cost_usd"])
        P["account_subscription_usd"], P["account_months"] = fmt_usd(st.get("subscription_usd", 0)), str(st.get("months", len({r["month"] for r in acc.get("by_account_month", []) if r["account"] == akey})))
        P["account_ratio"] = "%.2f" % (st.get("api_to_sub_ratio") or 0) if st.get("subscription_usd") else "n/a (no subscription)"
        P["account_months_table"] = table(["Month", "Calls", "Tokens", "API-equivalent", "Cache savings"], [[r["month"], fmt_int(r["calls"]), fmt_int(r["total"]), fmt_usd(r["api_cost_usd"]), fmt_usd(r["cache_savings_usd"])] for r in sorted((r for r in acc.get("by_account_month", []) if r["account"] == akey), key=lambda r: r["month"])], ["---", "---:", "---:", "---:", "---:"])
    # project scope
    pkey = var.get("project")
    prow = [r for r in projects if pkey and pkey.lower() in (r["cwd"] or "").lower()] if pkey else (projects[:1] if projects else [])
    if prow:
        name = pkey or tail(prow[0]["cwd"])
        pt = sum(r["total"] for r in prow)
        P["project"] = name
        P["project_calls"], P["project_tokens"], P["project_api_usd"], P["project_share_pct"] = fmt_int(sum(r["calls"] for r in prow)), fmt_int(pt), fmt_usd(sum(r["api_cost_usd"] for r in prow)), fmt_pct(pt / total)
        P["project_tools_table"] = table(["Directory", "Tool", "Calls", "Tokens", "API-equivalent"], [[tail(r["cwd"]), r["tool"], fmt_int(r["calls"]), fmt_int(r["total"]), fmt_usd(r["api_cost_usd"])] for r in prow], ["---", "---", "---:", "---:", "---:"])
    P.setdefault("notes", "")
    P.setdefault("prepared_for", "internal")
    P.setdefault("reference", "LEDGER-%s" % P["date"].replace("-", ""))
    for k, v in var.items():
        P[k] = v
    return P


# --------------------------------------------------------------------------- HTML
def md_to_html(md):
    from render_pdf import parse_blocks
    out = []
    for blk in parse_blocks(md):
        k = blk[0]
        if k == "h":
            out.append("<h%d>%s</h%d>" % (blk[1], inline_html(blk[2]), blk[1]))
        elif k == "p":
            out.append("<p>%s</p>" % inline_html(blk[1]))
        elif k == "quote":
            out.append("<blockquote>%s</blockquote>" % inline_html(blk[1]))
        elif k == "ul":
            out.append("<ul>" + "".join("<li>%s</li>" % inline_html(x) for x in blk[1]) + "</ul>")
        elif k == "table":
            rows = blk[1]
            if not rows:
                continue
            ncol = max(len(r) for r in rows)
            numeric = [all(re.fullmatch(r"[\s$€£%+\-.,0-9×x]*", (r[c] if c < len(r) else "")) for r in rows[1:]) for c in range(ncol)]
            h = "<tr>" + "".join("<th>%s</th>" % inline_html(c) for c in rows[0]) + "</tr>"
            b = "".join("<tr>" + "".join("<td%s>%s</td>" % (' class="n"' if numeric[ci] else "", inline_html(r[ci] if ci < len(r) else "")) for ci in range(ncol)) + "</tr>" for r in rows[1:])
            out.append('<div class="tw"><table>%s%s</table></div>' % (h, b))
    return "\n".join(out)


def inline_html(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


HTML_CSS = """
:root{color-scheme:light;--bg:#F8FAFC;--surface:#FFFFFF;--ink:#0F172A;--ink-2:#1E293B;--ink-3:#64748B;--line:#E2E8F0;--soft:#EEF2FF;--accent:__ACCENT__}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#0F172A;--surface:#1E293B;--ink:#F1F5F9;--ink-2:#CBD5E1;--ink-3:#94A3B8;--line:#334155;--soft:#273449}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#0F172A;--surface:#1E293B;--ink:#F1F5F9;--ink-2:#CBD5E1;--ink-3:#94A3B8;--line:#334155;--soft:#273449}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 "IBM Plex Sans",system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:28px 24px 60px}
.band{background:var(--soft);border-top:4px solid var(--accent);padding:14px 24px;display:flex;align-items:center;gap:16px}
.band img{height:44px}.band .eyebrow{font-size:11px;letter-spacing:.14em;font-weight:700;color:var(--ink-3);text-transform:uppercase}
.band .doctype{margin-left:auto;font-size:11px;letter-spacing:.1em;font-weight:700;color:var(--accent);text-transform:uppercase}
h1{font-size:28px;line-height:1.2;margin:18px 0 10px}h2{font-size:18px;color:var(--accent);margin:26px 0 8px}h3{font-size:15px;margin:18px 0 6px}
p{margin:0 0 10px}blockquote{margin:0 0 10px;padding-left:12px;border-left:3px solid var(--line);color:var(--ink-3);font-style:italic}
.tw{overflow-x:auto;margin:8px 0 14px}table{border-collapse:collapse;width:100%;font-size:13.5px;background:var(--surface)}
th{background:var(--accent);color:#fff;text-align:left;padding:6px 8px;font-weight:600}td{padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:color-mix(in srgb,var(--soft) 55%,var(--surface))}td.n{text-align:right;font-variant-numeric:tabular-nums}
code{font-family:"IBM Plex Mono",ui-monospace,Consolas,monospace;font-size:.92em;background:var(--soft);padding:1px 4px;border-radius:3px}
.foot{margin-top:40px;padding-top:12px;border-top:1px solid var(--line);color:var(--ink-3);font-size:12.5px}
.themebar{position:fixed;top:10px;right:10px;display:inline-flex;border:1px solid var(--line);border-radius:3px;overflow:hidden;background:var(--surface);z-index:20}
.themebar button{font:inherit;font-size:11px;padding:4px 9px;background:transparent;color:var(--ink-2);border:0;border-right:1px solid var(--line);cursor:pointer}
.themebar button:last-child{border-right:0}.themebar button.on{background:var(--ink);color:var(--bg)}
@media print{.themebar{display:none}}
"""

THEME_JS = """<script>(function(){var KEY="ledger-theme",root=document.documentElement;function apply(v){if(v==="light"||v==="dark"){root.setAttribute("data-theme",v);}else{root.removeAttribute("data-theme");}document.querySelectorAll(".themebar button").forEach(function(b){b.classList.toggle("on",b.dataset.t===(v||"system"));});}
var DEF="__THEME_DEFAULT__",saved=null;try{saved=localStorage.getItem(KEY);}catch(e){}if(!saved&&(DEF==="light"||DEF==="dark"))saved=DEF;apply(saved);
document.addEventListener("click",function(ev){var b=ev.target.closest(".themebar button");if(!b)return;var v=b.dataset.t;try{if(v==="system")localStorage.removeItem(KEY);else localStorage.setItem(KEY,v);}catch(e){}apply(v==="system"?null:v);});})();</script>"""


def logo_uri(path):
    import base64
    import mimetypes
    if not path:
        return None
    if path.startswith("data:image/"):
        return path
    if path.startswith("http"):
        return None  # generated pages are self-contained; point branding.logo at a local file
    if not os.path.isfile(path):
        return None
    mt = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mt, base64.b64encode(fh.read()).decode("ascii"))


def build_html(md, brand, title, doc_type, theme_default="system"):
    logo = logo_uri(brand.get("logo"))
    band = '<div class="band">%s<div><div class="eyebrow">%s</div><div>%s</div></div><div class="doctype">%s</div></div>' % (
        ('<img src="%s" alt="%s logo">' % (logo, html.escape(brand.get("name") or ""))) if logo else "", html.escape(brand.get("eyebrow") or ""), html.escape(brand.get("tagline") or brand.get("name") or ""), html.escape(doc_type))
    foot = '<div class="foot">%s</div>' % html.escape(brand.get("footer") or brand.get("contact") or "")
    themebar = '<div class="themebar" role="group" aria-label="Colour theme"><button type="button" data-t="light">Light</button><button type="button" data-t="system" class="on">System</button><button type="button" data-t="dark">Dark</button></div>'
    import safety
    accent = brand.get("accent") or "#1E3A8A"
    css = HTML_CSS.replace("__ACCENT__", accent if safety.COLOR_RE.match(str(accent).strip()) else "#1E3A8A")
    return '<meta charset="utf-8"><title>%s</title>%s<style>%s</style>%s%s%s<div class="wrap">%s%s</div>' % (
        html.escape(title), safety.CSP_META, css, THEME_JS.replace("__THEME_DEFAULT__", theme_default if theme_default in ("light", "dark", "system") else "system"), themebar, band, md_to_html(md), foot)


# --------------------------------------------------------------------------- main
def parse_vars(raw):
    out = {}
    for item in raw or []:
        if "=" not in item:
            raise SystemExit("--var must be key=value, got: %s" % item)
        k, v = item.split("=", 1)
        out[k.strip()] = v
    return out


def ledger_defaults(anonymize=False):
    """compiled dir, branding, theme and report config from the ledger configured by ledger.py (if any)."""
    try:
        import ledger
        cfg = ledger.load_config()
    except Exception:
        cfg = None
    if not cfg:
        return None, {}, "system", {}
    work = cfg.get("workdir")
    compiled = os.path.join(work, "anonymized", "compiled") if anonymize else os.path.join(work, "compiled")
    rc = {}
    try:
        with open(cfg["report_config_path"], encoding="utf-8") as fh:
            rc = json.load(fh)
    except Exception:
        pass
    return compiled, cfg.get("branding") or {}, cfg.get("theme") or "system", rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list template ids")
    ap.add_argument("--stage", help="filter --list by stage")
    ap.add_argument("--type", dest="doc_type_filter", help="filter --list by type")
    ap.add_argument("--template", help="template id to render")
    ap.add_argument("--compiled", help="compiled/ directory (default: the configured ledger's)")
    ap.add_argument("--report-config", help="report_config.json for branding and exclusions (default: the configured ledger's)")
    ap.add_argument("--anonymize", action="store_true", help="read the anonymised compiled/ directory produced by `ledger.py run --anonymize`")
    ap.add_argument("--var", action="append", default=[], help="placeholder value as key=value (repeatable)")
    ap.add_argument("--out", help="Markdown output path (default: <workdir or cwd>/documents/<template>-<date>.md)")
    ap.add_argument("--html", action="store_true", help="also write a themed HTML page beside the Markdown (default on)")
    ap.add_argument("--no-html", action="store_true")
    ap.add_argument("--pdf", action="store_true", help="also write a branded PDF (needs reportlab)")
    ap.add_argument("--docx", action="store_true", help="also write a DOCX (needs python-docx)")
    ap.add_argument("--png", action="store_true", help="also write a PNG preview of the PDF (needs pypdfium2 + pillow)")
    ap.add_argument("--print", dest="do_print", action="store_true", help="print the Markdown to stdout")
    a = ap.parse_args()

    templates = load_index()
    if a.list:
        for t in templates:
            if a.stage and t["stage"] != a.stage:
                continue
            if a.doc_type_filter and t["type"] != a.doc_type_filter:
                continue
            print("%-36s %-12s %-15s %s" % (t["id"], t["stage"], t["type"], t.get("title", "")))
        return 0
    if not a.template:
        ap.error("provide --list or --template")
    item = next((t for t in templates if t["id"] == a.template), None)
    if not item:
        print("unknown template: %s (see --list)" % a.template, file=sys.stderr)
        return 2

    compiled, brand, theme, rc = ledger_defaults(a.anonymize)
    if a.compiled:
        compiled = a.compiled
    if a.report_config:
        with open(a.report_config, encoding="utf-8") as fh:
            rc = json.load(fh)
    if rc.get("branding"):
        brand = dict(rc["branding"], **{k: v for k, v in brand.items() if k not in rc["branding"]}) if brand else rc["branding"]
        if brand.get("logo") and not os.path.isabs(brand["logo"]) and not brand["logo"].startswith(("http", "data:")):
            cands = [os.path.join(os.path.dirname(os.path.abspath(a.report_config)), brand["logo"])] if a.report_config else []
            cands += [os.path.join(ROOT, brand["logo"]), os.path.join(os.getcwd(), brand["logo"])]
            brand["logo"] = next((c for c in cands if os.path.isfile(c)), brand["logo"])
    if not brand.get("logo") and os.path.isfile(os.path.join(ROOT, "assets", "logo.png")):
        brand["logo"] = os.path.join(ROOT, "assets", "logo.png")
    if not compiled or not os.path.isfile(os.path.join(compiled, "summary.json")):
        print("no compiled/summary.json found; pass --compiled <dir> or run `ledger.py run` first", file=sys.stderr)
        return 2
    S, A = load_ledger(compiled)
    var = parse_vars(a.var)
    P = placeholders(S, A, brand, var, rc)
    md = extract_template(a.template).format_map(SafeDict(P)).strip() + "\n"
    if a.anonymize:
        md = md.rstrip() + "\n\n_Anonymised for publication: hosts, projects and accounts are replaced by stable pseudonyms; identities and paths are removed._\n"
    if a.do_print:
        sys.stdout.write(md)
    out = a.out
    if not out:
        base = os.path.dirname(os.path.dirname(compiled)) if compiled.endswith("anonymized" + os.sep + "compiled") else os.path.dirname(compiled)
        out = os.path.join(base, "documents", "%s-%s%s.md" % (a.template, P["date"], "-anon" if a.anonymize else ""))
    safety.private_dir(os.path.dirname(os.path.abspath(out)) or ".")
    with safety.private_open(out, "w") as fh:
        fh.write(md)
    print("Markdown:", out)
    title = item.get("title") or a.template.replace("-", " ").title()
    doc_type = "%s · %s" % (item["stage"], item["type"])
    stem = os.path.splitext(out)[0]
    if not a.no_html:
        with safety.private_open(stem + ".html", "w") as fh:
            fh.write(build_html(md, brand, title, doc_type, theme))
        print("HTML:", stem + ".html")
    if a.pdf or a.docx:
        import render_pdf
        cfg = {"logo": brand.get("logo") if brand.get("logo") and os.path.isfile(brand["logo"]) else None, "title": title, "eyebrow": brand.get("eyebrow") or brand.get("name"),
               "doc_type": doc_type, "footer": (brand.get("footer") or brand.get("contact") or "") + " · API-equivalent figures at list price, not an invoice",
               "accent": brand.get("accent"), "date": P["date"], "name": brand.get("name")}
        if a.pdf:
            try:
                render_pdf.build_pdf(md, cfg, stem + ".pdf")
                print("PDF:", stem + ".pdf")
                if a.png:
                    try:
                        render_pdf.montage(stem + ".pdf", stem + ".png")
                        print("PNG:", stem + ".png")
                    except ImportError as ex:
                        print("[skip PNG] %s; pip install pypdfium2 pillow" % ex, file=sys.stderr)
            except ImportError as ex:
                print("[skip PDF] %s; pip install reportlab" % ex, file=sys.stderr)
        if a.docx:
            try:
                render_pdf.build_docx(md, cfg, stem + ".docx")
                print("DOCX:", stem + ".docx")
            except ImportError as ex:
                print("[skip DOCX] %s; pip install python-docx" % ex, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
