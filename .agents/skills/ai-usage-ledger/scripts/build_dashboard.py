#!/usr/bin/env python3
"""Build a self-contained HTML dashboard from compiled/summary.json."""
import glob
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safety  # noqa: E402
import html as _html  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "compiled/summary.json"
dst = sys.argv[2] if len(sys.argv) > 2 else "compiled/agent-ledger.html"
CFG = {}
if len(sys.argv) > 3 and os.path.isfile(sys.argv[3]):
    safety.refuse_if_shared(sys.argv[3], "report config")  # it decides branding, links and notes on the page: refuse a shared file
    CFG = json.load(open(sys.argv[3], encoding="utf-8"))
S = json.load(open(src, encoding="utf-8"))
A = {}
ap = os.path.join(os.path.dirname(src) or ".", "analysis.json")
if os.path.isfile(ap):
    A = json.load(open(ap, encoding="utf-8"))
STATS = {}
_stats_paths = {os.path.basename(os.path.dirname(p)): p for p in glob.glob(os.path.join(os.path.dirname(os.path.dirname(src) or "."), "scans", "*", "stats-cache.json"))}
for host, sp in _stats_paths.items():
    if os.path.isfile(sp):
        try:
            d = json.load(open(sp, encoding="utf-8"))
            mu = d.get("modelUsage", {})
            STATS[host] = {"lastComputedDate": d.get("lastComputedDate"), "firstSessionDate": d.get("firstSessionDate"), "totalSessions": d.get("totalSessions"),
                           "tokens": sum(sum(u.get(k, 0) for k in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens")) for u in mu.values()),
                           "models": {m: sum(u.get(k, 0) for k in ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens")) for m, u in mu.items()}}
        except Exception:
            pass


def _study_url():
    """The 'Read the study' link may only be an absolute https URL (safety.validate_study_url); a javascript:, data:,
    protocol-relative or http: value is dropped with a warning and never reaches the page."""
    for what, value in (("STUDY_URL", os.environ.get("STUDY_URL")), ("study_url in the report config", CFG.get("study_url"))):
        if not value:
            continue
        try:
            return safety.validate_study_url(value)
        except safety.UnsafeValue as ex:
            sys.stderr.write("warning: %s dropped, not rendered: %s\n" % (what, ex))
    return ""


STUDY_URL = _study_url()

# trim what the page needs
data = {
    "generated": S["generated"],
    "events": S["events"], "sessions": S["sessions"], "prompts": S["prompts"], "total": S["total"],
    "by_tool": S["by_tool"], "by_tool_host": S["by_tool_host"], "by_model": S["by_model"],
    "by_month_tool": S["by_month_tool"], "by_day_tool": S["by_day_tool"], "by_kind": S["by_kind"],
    "by_entrypoint": S["by_entrypoint"], "by_project": S["by_project"][:25], "top_sessions": S["top_sessions"][:20],
    "inventory": S["inventory"],
    "costs": S.get("costs", {}),
    "accounts": S.get("accounts"),
    "analysis": {k: A.get(k) for k in ("distributions", "session_distributions", "concentration", "validation", "sensitivity", "hour_weekday_calls", "blended_rates", "cache_ttl_split", "effort", "top_sessions", "model_month")} if A else None,
    "stats": STATS,
    "study_url": STUDY_URL,
    "config": {"excluded_note": CFG.get("dashboard_excluded_note", ""), "title": CFG.get("dashboard_title", "Agent Token Ledger"), "primary_claude_host": CFG.get("claude_primary_host")},
}

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

payload = json.dumps(data).replace("</", "<\\/")

THEMEBAR_HTML = '<div class="themebar" role="group" aria-label="Colour theme"><button type="button" data-t="light">Light</button><button type="button" data-t="system" class="on">System</button><button type="button" data-t="dark">Dark</button></div>'
html = r"""<meta charset="utf-8"><title>__PAGE_TITLE__</title>
<style>
:root{
  color-scheme:light;
  --bg:#f4f6f9;--surface:#ffffff;--surface-2:#eef1f5;--ink:#141a22;--ink-2:#5a6472;--ink-3:#8b95a3;--line:#e2e6ec;--line-2:#cfd5dd;
  --codex:#2a78d6;--claude:#eb6834;--copilot:#1baf7a;--opencode:#eda100;--openclaw:#e87ba4;
  --seq1:#cde2fb;--seq2:#9ec5f4;--seq3:#6da7ec;--seq4:#3987e5;--seq5:#256abf;--seq6:#184f95;--seq7:#0d366b;
  --focus:#2a78d6;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --bg:#14171c;--surface:#1c2027;--surface-2:#242931;--ink:#f2f4f7;--ink-2:#b4bcc8;--ink-3:#7d8794;--line:#2b313a;--line-2:#3a424d;
    --codex:#3987e5;--claude:#d95926;--copilot:#199e70;--opencode:#c98500;--openclaw:#d55181;
    --seq1:#1b2a3f;--seq2:#184f95;--seq3:#1c5cab;--seq4:#256abf;--seq5:#3987e5;--seq6:#6da7ec;--seq7:#9ec5f4;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#14171c;--surface:#1c2027;--surface-2:#242931;--ink:#f2f4f7;--ink-2:#b4bcc8;--ink-3:#7d8794;--line:#2b313a;--line-2:#3a424d;
  --codex:#3987e5;--claude:#d95926;--copilot:#199e70;--opencode:#c98500;--openclaw:#d55181;
  --seq1:#1b2a3f;--seq2:#184f95;--seq3:#1c5cab;--seq4:#256abf;--seq5:#3987e5;--seq6:#6da7ec;--seq7:#9ec5f4;
}
*{box-sizing:border-box}
html,body{overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:14px;line-height:1.5}
.wrap{max-width:1180px;margin:0 auto;padding:32px 24px 64px}
h1,h2,h3{font-family:"Barlow Condensed","Arial Narrow",sans-serif;text-wrap:balance;margin:0;letter-spacing:.005em}
h1{font-size:44px;font-weight:700;line-height:1;text-transform:uppercase}
h2{font-size:22px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:var(--ink)}
.eyebrow{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3)}
.mono,.num,td.n,th.n{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
header{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;padding-bottom:20px;border-bottom:1px solid var(--line-2)}
header .sub{color:var(--ink-2);max-width:62ch;margin-top:10px}
.hosts{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.chip.study{color:var(--ink);border-color:var(--ink);text-decoration:none}.chip.study:hover{background:var(--ink);color:var(--bg)}
.findings{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.finding{background:var(--surface);border:1px solid var(--line);padding:14px 16px;display:flex;flex-direction:column;gap:6px}
.finding .code{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.1em;color:var(--ink-3)}
.finding .code b{color:var(--ink);margin-left:6px;letter-spacing:0;font-family:"IBM Plex Sans",sans-serif;font-size:12px;text-transform:none;font-weight:600}
.finding h3{font-family:"IBM Plex Sans",sans-serif;font-size:14px;font-weight:600;margin:0;line-height:1.3}
.finding p{margin:0;font-size:13px;color:var(--ink-2)}
.caveat.b{border-left-color:var(--codex)}
.chip{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.06em;padding:4px 9px;border:1px solid var(--line-2);border-radius:3px;color:var(--ink-2);background:var(--surface)}
section{margin-top:40px}
.sechead{display:flex;align-items:baseline;justify-content:space-between;gap:16px;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.sechead p{margin:0;color:var(--ink-3);font-size:12px}
.hero{display:grid;grid-template-columns:1.6fr repeat(3,1fr);gap:14px;margin-top:24px}
.tile{background:var(--surface);border:1px solid var(--line);padding:16px 18px 14px;display:flex;flex-direction:column;gap:4px;min-width:0}
.tile .lab{font-size:12px;color:var(--ink-2)}
.tile .val{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:30px;line-height:1.1;letter-spacing:-.01em}
.tile.lead .val{font-size:56px;letter-spacing:-.02em}
.tile .foot{font-size:12px;color:var(--ink-3);margin-top:auto;padding-top:6px}
.split{display:grid;grid-template-columns:1fr 1fr;gap:28px}
@media (max-width:820px){.hero{grid-template-columns:1fr 1fr}.split{grid-template-columns:1fr}header{grid-template-columns:1fr}.hosts{justify-content:flex-start}}
.seg{display:inline-flex;border:1px solid var(--line-2);border-radius:3px;overflow:hidden}
.seg button{font:inherit;font-size:12px;padding:4px 10px;background:var(--surface);color:var(--ink-2);border:0;border-right:1px solid var(--line-2);cursor:pointer}
.seg button:last-child{border-right:0}
.seg button.on{background:var(--ink);color:var(--bg)}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--ink-2)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.chart{background:var(--surface);border:1px solid var(--line);padding:16px 12px 8px;overflow-x:auto;position:relative}
svg{display:block;max-width:100%;font-family:"IBM Plex Mono",monospace;font-size:11px}
svg text{fill:var(--ink-2)}
svg .grid{stroke:var(--line);stroke-width:1}
svg .axis{stroke:var(--line-2);stroke-width:1}
.tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--bg);font-size:12px;padding:8px 10px;border-radius:3px;line-height:1.4;z-index:9;max-width:260px;display:none;font-family:"IBM Plex Mono",monospace}
table{border-collapse:collapse;width:100%;background:var(--surface);border:1px solid var(--line);font-size:13px}
th,td{padding:7px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);font-weight:500;background:var(--surface-2)}
td.n,th.n{text-align:right;white-space:nowrap}
tr:last-child td{border-bottom:0}
td.path{font-family:"IBM Plex Mono",monospace;font-size:12px;word-break:break-all;color:var(--ink-2)}
.sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:7px;vertical-align:-1px}
.tw{overflow-x:auto}
.bar{height:14px;background:var(--surface-2);position:relative;border-radius:2px;overflow:hidden;min-width:120px}
.bar b{position:absolute;left:0;top:0;bottom:0;border-radius:0 3px 3px 0}
details{margin-top:10px}
summary{cursor:pointer;color:var(--ink-2);font-size:12px}
summary:focus-visible,button:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.cal{display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,12px);gap:3px;padding:6px 0}
.cal div{width:12px;height:12px;border-radius:2px;background:var(--surface-2)}
.calwrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line);padding:14px 16px}
.calmonths{display:flex;font-size:11px;color:var(--ink-3);font-family:"IBM Plex Mono",monospace;height:14px;position:relative}
.calmonths span{position:absolute;top:0}
.scale{display:flex;align-items:center;gap:4px;font-size:11px;color:var(--ink-3);margin-top:8px}
.scale i{width:12px;height:12px;border-radius:2px;display:inline-block}
.notes{color:var(--ink-2);max-width:72ch}
.notes li{margin-bottom:6px}
.caveat{background:var(--surface);border-left:3px solid var(--claude);padding:10px 14px;margin-top:10px;font-size:13px;max-width:72ch}
@media (prefers-reduced-motion:no-preference){.bar b{transition:width .4s ease}}
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
__BRAND_STYLE__
__THEMEBAR__
<div class="wrap">
__BRAND_HEADER__
<header>
  <div>
    <div class="eyebrow" id="range"></div>
    <h1>Agent Token Ledger</h1>
    <p class="sub">Every model call recorded on disk by the scanned agent tools and hosts, normalised into one stream. Tokens are as the tools logged them. Dollar figures are API-equivalent: the same tokens at list API prices, set against the subscriptions that actually paid for them.</p>
  </div>
  <div class="hosts" id="hosts"></div>
</header>

<div class="hero" id="heroCost"></div>
<div class="hero" id="hero" style="margin-top:14px"></div>

<section>
  <div class="sechead"><h2>Key findings</h2><p>from the study · confidence by evidence class</p></div>
  <div class="findings" id="findings"></div>
  <div class="caveat b" id="coverage"></div>
</section>

<section>
  <div class="sechead"><h2>Accounts</h2><p>who paid for what · attribution rules in accounts.json</p></div>
  <div class="tw" id="accounts"></div>
  <div class="split" style="margin-top:18px">
    <div>
      <div class="sechead"><h2>By month and account</h2><p>API-equivalent, subscription-billed calls only</p></div>
      <div class="tw" id="accountMonths"></div>
    </div>
    <div>
      <div class="sechead"><h2>Billing plan on the call</h2><p>Codex rate_limits.plan_type, recorded per call</p></div>
      <div class="tw" id="plans"></div>
      <div class="caveat" id="accountNote" style="margin-top:14px"></div>
    </div>
  </div>
</section>

<section>
  <div class="sechead"><h2>Tokens by month</h2><p>stacked by tool &middot; hover a segment</p></div>
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px;flex-wrap:wrap"><div class="legend" id="legend1"></div><div class="seg" id="metric"><button data-m="total" class="on">Total tokens</button><button data-m="output">Output tokens</button><button data-m="calls">Calls</button><button data-m="api_cost_usd">API cost</button></div></div>
  <div class="chart"><svg id="monthly" width="1140" height="300" viewBox="0 0 1140 300" role="img" aria-label="Monthly tokens stacked by tool"></svg></div>
  <details><summary>Show as table</summary><div class="tw" id="monthlyTable"></div></details>
</section>

<section class="split">
  <div>
    <div class="sechead"><h2>Subscription vs API-equivalent</h2><p>per month, per plan</p></div>
    <div class="tw" id="subs"></div>
  </div>
  <div>
    <div class="sechead"><h2>Caching</h2><p>what the cache saved, per tool</p></div>
    <div class="tw" id="caching"></div>
    <div class="sechead" style="margin-top:28px"><h2>Cache hit rate by month</h2><p>cache reads as a share of all prompt tokens</p></div>
    <div class="chart"><svg id="hitrate" width="540" height="200" viewBox="0 0 540 200" role="img" aria-label="Cache hit rate by month"></svg></div>
  </div>
</section>

<section class="split">
  <div>
    <div class="sechead"><h2>Validation</h2><p>rollout totals vs Codex's own SQLite counter</p></div>
    <div class="tw" id="validation"></div>
    <div class="sechead" style="margin-top:28px"><h2>Concentration</h2><p>share of Codex tokens by thread rank</p></div>
    <div class="tw" id="concentration"></div>
  </div>
  <div>
    <div class="sechead"><h2>Distributions</h2><p>per call and per session</p></div>
    <div class="tw" id="dist"></div>
  </div>
</section>

<section>
  <div class="sechead"><h2>Time of day</h2><p>calls by weekday and hour, America/New_York, Codex and Claude Code · square-root scale</p></div>
  <div class="chart"><svg id="heat" width="1140" height="230" viewBox="0 0 1140 230" role="img" aria-label="Calls by weekday and hour"></svg></div>
</section>

<section>
  <div class="sechead"><h2>Daily activity</h2><p>all tools &middot; total tokens per day</p></div>
  <div class="calwrap"><div class="calmonths" id="calmonths"></div><div class="cal" id="cal"></div><div class="scale" id="calscale"></div></div>
</section>

<section class="split">
  <div>
    <div class="sechead"><h2>By model</h2><p>top 14 &middot; share of all tokens</p></div>
    <div class="tw" id="models"></div>
  </div>
  <div>
    <div class="sechead"><h2>By tool and host</h2><p>calls, sessions, tokens</p></div>
    <div class="tw" id="toolhost"></div>
    <div class="sechead" style="margin-top:28px"><h2>Main vs sub-agent</h2><p>forked Codex threads, Claude agent transcripts</p></div>
    <div class="tw" id="kind"></div>
  </div>
</section>

<section>
  <div class="sechead"><h2>Working directories</h2><p>top 25 by tokens</p></div>
  <div class="tw" id="projects"></div>
</section>

<section>
  <div class="sechead"><h2>Heaviest sessions</h2><p>top 20 threads by tokens</p></div>
  <div class="tw" id="sessions"></div>
</section>

<section>
  <div class="sechead"><h2>Where the logs live</h2><p>scan inventory</p></div>
  <div class="tw" id="inventory"></div>
  <div class="caveat" id="caveat"></div>
</section>

<section>
  <div class="sechead"><h2>How to read this</h2></div>
  <ul class="notes">
    <li><b>input_uncached</b> is fresh prompt tokens; <b>cache_read</b> is prompt tokens served from the provider cache; <b>cache_write</b> is prompt tokens written to cache (Claude only); <b>output</b> includes reasoning. <b>total</b> is the sum of the four.</li>
    <li>Codex numbers come from each rollout's <span class="mono">token_count</span> events (summing <span class="mono">last_token_usage</span>). Forked and sub-agent threads replay their parent's history when spawned; those replayed events are dropped so they are not counted twice. Rollout totals match Codex's own <span class="mono">state_5.sqlite</span> per-thread figures within 2% on the threads checked.</li>
    <li>Claude Code numbers come from the assistant messages in each session transcript, de-duplicated by message id. Agent transcripts (<span class="mono">agent-*.jsonl</span>) are counted as sub-agent.</li>
    <li><b>API-equivalent cost</b> multiplies each call's tokens by the provider's list price for that model (uncached input, cache read, cache write at the 5-minute or 1-hour rate, output). It is what the same work would have cost on a pay-as-you-go API key. Codex and Claude Code ran on flat-rate subscriptions, so the real outlay for those two is the subscription line. OpenClaw, opencode and Copilot CLI are billed separately (API keys, OpenRouter, GitHub).</li>
    <li><b>Saved by caching</b> compares the API-equivalent cost with the same calls priced as if every prompt token were uncached input.</li>
    <li>Cache reads dominate: an agent loop re-sends its whole context every turn, and most of it is served from cache. Output tokens are the better measure of work produced.</li>
  </ul>
</section>
__BRAND_FOOTER__
</div>
<div class="tip" id="tip"></div>
<script>
(function(){
  var KEY="ledger-theme", root=document.documentElement;
  function apply(v){ if(v==="light"||v==="dark"){root.setAttribute("data-theme",v);}else{root.removeAttribute("data-theme");} document.querySelectorAll(".themebar button").forEach(function(b){b.classList.toggle("on", b.dataset.t===(v||"system"));}); }
  var DEF="__THEME_DEFAULT__", saved=null; try{saved=localStorage.getItem(KEY);}catch(e){}
  if(!saved && (DEF==="light"||DEF==="dark")) saved=DEF;
  apply(saved);
  document.addEventListener("click",function(ev){ var b=ev.target.closest(".themebar button"); if(!b) return; var v=b.dataset.t; try{ if(v==="system") localStorage.removeItem(KEY); else localStorage.setItem(KEY,v);}catch(e){} apply(v==="system"?null:v); });
})();
</script>
<script>
const D = __DATA__;
const TOOL = {
  "codex": {name:"Codex", v:"--codex"},
  "claude-code": {name:"Claude Code", v:"--claude"},
  "copilot-cli": {name:"Copilot CLI", v:"--copilot"},
  "opencode": {name:"opencode", v:"--opencode"},
  "openclaw": {name:"OpenClaw", v:"--openclaw"},
};
const order = ["codex","claude-code","copilot-cli","opencode","openclaw"];
const col = t => `var(${(TOOL[t]||{v:"--ink-3"}).v})`;
const tname = t => (TOOL[t]||{name:t}).name;
const fmt = n => n.toLocaleString("en-US");
const compact = n => { n = +n||0; if (n>=1e12) return (n/1e12).toFixed(2)+"T"; if (n>=1e9) return (n/1e9).toFixed(2)+"B"; if (n>=1e6) return (n/1e6).toFixed(1)+"M"; if (n>=1e3) return (n/1e3).toFixed(1)+"K"; return String(n); };
const money = n => { n = +n||0; const a = Math.abs(n); const s = n<0?"-":""; if (a>=1e6) return s+"$"+(a/1e6).toFixed(2)+"M"; if (a>=1e4) return s+"$"+(a/1e3).toFixed(1)+"K"; return s+"$"+a.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}); };
const moneyFull = n => "$"+(+n||0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
const esc = s => String(s==null?"":s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const tip = document.getElementById("tip");
function showTip(e, html){ tip.innerHTML = html; tip.style.display="block"; moveTip(e); }
function moveTip(e){ const x = Math.min(e.clientX+14, window.innerWidth-280); tip.style.left = x+"px"; tip.style.top = (e.clientY+14)+"px"; }
function hideTip(){ tip.style.display="none"; }

// header
const days = D.by_day_tool.map(r=>r.date).filter(d=>d && d!=="?").sort();
document.getElementById("range").textContent = `${days[0]} → ${days[days.length-1]} · ${D.events.toLocaleString()} calls · generated ${D.generated.slice(0,16).replace("T"," ")} UTC`;
const hosts = [...new Set(D.by_tool_host.map(r=>r.host))];
const hostsEl = document.getElementById("hosts");
hostsEl.innerHTML = hosts.map(h=>`<span class="chip">${esc(h)}</span>`).join("");
if (D.study_url && /^https:\/\/[^\s/]+/i.test(D.study_url)) {  // validated in Python already; built with DOM APIs so no markup or scheme can be smuggled in
  const link = document.createElement("a");
  link.className = "chip study"; link.href = D.study_url; link.rel = "noopener noreferrer"; link.textContent = "Read the study →";
  hostsEl.appendChild(document.createTextNode(" ")); hostsEl.appendChild(link);
}

// hero: money
const T = D.total;
const C = D.costs || {};
const ST = C.subscription_totals || {};
const ACC = D.accounts || null;
const AT = ACC ? ACC.subscription_totals : null;
const subEntries = AT ? Object.entries(AT).filter(([k,t])=>t.subscription_usd>0) : Object.entries(ST);
const subPaid = subEntries.reduce((a,[k,t])=>a+t.subscription_usd,0);
const subApi = subEntries.reduce((a,[k,t])=>a+t.api_equivalent_usd,0);
const usageBased = ACC ? (ACC.by_billing_month||[]).filter(r=>r.billing==="usage-based").reduce((a,r)=>a+r.api_cost_usd,0) : 0;
const subCovered = Object.keys(ST);
const apiAll = T.api_cost_usd||0, noCache = T.cost_if_uncached_usd||0, cacheSaved = T.cache_savings_usd||0;
const uncoveredCost = apiAll - subApi;
document.getElementById("heroCost").innerHTML = `
  <div class="tile lead"><div class="lab">API-equivalent cost, all tools</div><div class="val">${money(apiAll)}</div><div class="foot">${moneyFull(apiAll)} at list prices \u00b7 ${moneyFull(noCache)} if nothing had been cached</div></div>
  <div class="tile"><div class="lab">Subscriptions actually paid</div><div class="val">${money(subPaid)}</div><div class="foot">${AT ? subEntries.length+" subscriptions: "+subEntries.map(([k,t])=>t.label.split(" / ").pop()+" ("+t.months+" mo)").join(", ") : Object.values(ST).map(t=>t.plan+" × "+t.months+" mo").join(" · ")}</div></div>
  <div class="tile"><div class="lab">Saved by subscribing</div><div class="val">${money(subApi - subPaid)}</div><div class="foot">${(subApi/subPaid).toFixed(1)}\u00d7 the subscription price in API terms${usageBased>0.5?" · "+moneyFull(usageBased)+" was usage-based (real spend)":(uncoveredCost>0.5?" · "+moneyFull(uncoveredCost)+" of other tools is real API spend":"")}</div></div>
  <div class="tile"><div class="lab">Saved by prompt caching</div><div class="val">${money(cacheSaved)}</div><div class="foot">${(100*cacheSaved/noCache).toFixed(0)}% off the uncached price \u00b7 ${(100*T.cache_read/(T.input_uncached+T.cache_read+T.cache_write)).toFixed(0)}% of prompt tokens were cache hits</div></div>`;

// hero: tokens
const claudeOut = D.by_tool.filter(r=>r.tool==="claude-code").reduce((a,r)=>a+r.output,0);
const codexOut = D.by_tool.filter(r=>r.tool==="codex").reduce((a,r)=>a+r.output,0);
document.getElementById("hero").innerHTML = `
  <div class="tile lead"><div class="lab">Total tokens, all tools</div><div class="val">${compact(T.total)}</div><div class="foot">${fmt(T.total)} · ${(100*T.cache_read/T.total).toFixed(0)}% served from cache</div></div>
  <div class="tile"><div class="lab">Output tokens</div><div class="val">${compact(T.output)}</div><div class="foot">${compact(T.reasoning)} of it reasoning</div></div>
  <div class="tile"><div class="lab">Model calls</div><div class="val">${compact(D.events)}</div><div class="foot">${fmt(D.sessions)} sessions · ${fmt(D.prompts)} typed prompts</div></div>
  <div class="tile"><div class="lab">Active days</div><div class="val">${days.length}</div><div class="foot">${compact(T.total/days.length)} tokens per active day</div></div>`;

// legend
const toolsPresent = order.filter(t=>D.by_tool.some(r=>r.tool===t));
document.getElementById("legend1").innerHTML = toolsPresent.map(t=>`<span><i style="background:${col(t)}"></i>${tname(t)}</span>`).join("");

// monthly stacked columns
const monthly = (function(){
  const months = [...new Set(D.by_month_tool.map(r=>r.month))].filter(m=>m!=="?").sort();
  const byM = {}; D.by_month_tool.forEach(r=>{ (byM[r.month] ||= {})[r.tool] = r; });
  const W=1140,H=300,L=64,R=16,Tp=14,B=40, pw=W-L-R, ph=H-Tp-B;
  const svg = document.getElementById("monthly");
  function draw(metric){
    const val = r => r ? (r[metric]||0) : 0;
    const isMoney = metric==="api_cost_usd";
    const label = metric==="calls" ? "calls" : isMoney ? "" : "tokens";
    const fmtv = v => isMoney ? money(v) : compact(v);
    const max = Math.max(...months.map(m=>toolsPresent.reduce((a,t)=>a+val(byM[m][t]),0)));
    const step = niceStep(max/4);
    const ymax = Math.ceil(max/step)*step;
    const y = v => Tp + ph - v/ymax*ph;
    const band = pw/months.length, bw = Math.min(24, band*0.6);
    let s = "";
    for (let v=0; v<=ymax; v+=step) { s += `<line class="grid" x1="${L}" x2="${W-R}" y1="${y(v)}" y2="${y(v)}"/><text x="${L-8}" y="${y(v)+4}" text-anchor="end">${fmtv(v)}</text>`; }
    months.forEach((m,i)=>{
      const x = L + band*i + (band-bw)/2; let acc = 0;
      toolsPresent.forEach(t=>{
        const r = byM[m][t]; if (!r || !val(r)) return;
        const y1 = y(acc + val(r)), y0 = y(acc);
        const h = Math.max(0, y0 - y1 - 2);
        s += `<rect x="${x}" y="${y1}" width="${bw}" height="${h}" fill="${col(t)}" data-m="${m}" data-t="${t}" data-total="${r.total}" data-calls="${r.calls}" data-out="${r.output}" data-sess="${r.sessions}" data-cost="${r.api_cost_usd||0}" data-save="${r.cache_savings_usd||0}"/>`;
        acc += val(r);
      });
      if (acc === max) s += `<text x="${x+bw/2}" y="${y(acc)-6}" text-anchor="middle" style="fill:var(--ink)">${fmtv(acc)} ${label}</text>`;
      s += `<text x="${x+bw/2}" y="${H-B+18}" text-anchor="middle">${m}</text>`;
    });
    s += `<line class="axis" x1="${L}" x2="${W-R}" y1="${y(0)}" y2="${y(0)}"/>`;
    svg.innerHTML = s;
    svg.querySelectorAll("rect").forEach(r=>{
      r.addEventListener("mousemove", e=>showTip(e, `<b>${r.dataset.m} · ${tname(r.dataset.t)}</b><br>${fmt(+r.dataset.total)} tokens<br>${fmt(+r.dataset.out)} output<br>${fmt(+r.dataset.calls)} calls \u00b7 ${fmt(+r.dataset.sess)} sessions<br>${moneyFull(+r.dataset.cost)} API-equivalent \u00b7 ${moneyFull(+r.dataset.save)} saved by cache`));
      r.addEventListener("mouseleave", hideTip);
    });
  }
  draw("total");
  document.querySelectorAll("#metric button").forEach(b=>b.addEventListener("click", ()=>{ document.querySelectorAll("#metric button").forEach(x=>x.classList.toggle("on", x===b)); draw(b.dataset.m); }));
  // table
  let t = `<table><tr><th>Month</th>${toolsPresent.map(x=>`<th class="n">${tname(x)}</th>`).join("")}<th class="n">Total</th><th class="n">Output</th><th class="n">Calls</th><th class="n">API-equivalent</th><th class="n">Cache saved</th></tr>`;
  months.forEach(m=>{ const tot = toolsPresent.reduce((a,x)=>a+((byM[m][x]||{}).total||0),0); const out = toolsPresent.reduce((a,x)=>a+((byM[m][x]||{}).output||0),0); const calls = toolsPresent.reduce((a,x)=>a+((byM[m][x]||{}).calls||0),0); const cost = toolsPresent.reduce((a,x)=>a+((byM[m][x]||{}).api_cost_usd||0),0); const sav = toolsPresent.reduce((a,x)=>a+((byM[m][x]||{}).cache_savings_usd||0),0);
    t += `<tr><td class="mono">${m}</td>${toolsPresent.map(x=>`<td class="n">${fmt((byM[m][x]||{}).total||0)}</td>`).join("")}<td class="n"><b>${fmt(tot)}</b></td><td class="n">${fmt(out)}</td><td class="n">${fmt(calls)}</td><td class="n">${moneyFull(cost)}</td><td class="n">${moneyFull(sav)}</td></tr>`; });
  document.getElementById("monthlyTable").innerHTML = t + "</table>";
})();
function niceStep(x){ const p = Math.pow(10, Math.floor(Math.log10(x))); const f = x/p; return (f<=1?1:f<=2?2:f<=5?5:10)*p; }

// subscription vs API table
(function(){
  const rows = C.subscription_rows || [];
  const months = [...new Set(rows.map(r=>r.month))].sort();
  const tools = [...new Set(rows.map(r=>r.tool))];
  let t = `<table><tr><th>Month</th>${tools.map(x=>`<th class="n">${tname(x)} API-eq.</th>`).join("")}<th class="n">Subscriptions</th><th class="n">API / sub</th></tr>`;
  let tsub=0, tapi=0;
  months.forEach(m=>{ const rs = rows.filter(r=>r.month===m); const api = rs.reduce((a,r)=>a+r.api_equivalent_usd,0); const sub = rs.reduce((a,r)=>a+r.subscription_usd,0); tsub+=sub; tapi+=api;
    t += `<tr><td class="mono">${m}</td>${tools.map(x=>{const r=rs.find(r=>r.tool===x); return `<td class="n">${r?moneyFull(r.api_equivalent_usd):"\u2013"}</td>`;}).join("")}<td class="n">${moneyFull(sub)}</td><td class="n">${sub?(api/sub).toFixed(1)+"\u00d7":"\u2013"}</td></tr>`; });
  t += `<tr><td><b>Total</b></td>${tools.map(x=>`<td class="n"><b>${moneyFull(rows.filter(r=>r.tool===x).reduce((a,r)=>a+r.api_equivalent_usd,0))}</b></td>`).join("")}<td class="n"><b>${moneyFull(tsub)}</b></td><td class="n"><b>${(tapi/tsub).toFixed(1)}\u00d7</b></td></tr></table>`;
  t += `<p style="font-size:12px;color:var(--ink-3);margin:8px 0 0">${Object.values(ST).map(t=>`${t.plan}: ${moneyFull(t.subscription_usd)} paid over ${t.months} months of use vs ${moneyFull(t.api_equivalent_usd)} at API list price (${moneyFull(t.api_if_uncached_usd)} uncached).`).join(" ")}</p>`;
  document.getElementById("subs").innerHTML = t;
})();

// caching table + hit-rate line
(function(){
  const rows = [...D.by_tool].sort((a,b)=>b.total-a.total);
  let t = `<table><tr><th>Tool</th><th class="n">Hit rate</th><th class="n">API-equivalent</th><th class="n">If uncached</th><th class="n">Cache saved</th><th class="n">Saved</th></tr>`;
  rows.forEach(r=>{ const prompt = r.input_uncached+r.cache_read+r.cache_write; const hit = prompt? 100*r.cache_read/prompt:0; const pct = r.cost_if_uncached_usd? 100*r.cache_savings_usd/r.cost_if_uncached_usd:0;
    t += `<tr><td><span class="sw" style="background:${col(r.tool)}"></span>${tname(r.tool)}</td><td class="n">${hit.toFixed(1)}%</td><td class="n">${moneyFull(r.api_cost_usd)}</td><td class="n">${moneyFull(r.cost_if_uncached_usd)}</td><td class="n">${moneyFull(r.cache_savings_usd)}</td><td class="n">${pct.toFixed(0)}%</td></tr>`; });
  t += `</table><p style="font-size:12px;color:var(--ink-3);margin:8px 0 0">Claude cache writes cost 1.25\u00d7 (5-minute) or 2\u00d7 (1-hour) the input price and are included above; Claude Code wrote ${compact(T.cache_write)} tokens to cache. OpenAI charges nothing for cache writes.</p>`;
  document.getElementById("caching").innerHTML = t;
  // hit-rate by month, one line per tool (codex, claude)
  const months = [...new Set(D.by_month_tool.map(r=>r.month))].filter(m=>m!=="?").sort();
  const W=540,H=200,L=44,R=14,Tp=12,B=30,pw=W-L-R,ph=H-Tp-B;
  const x = i => L + (months.length>1 ? i*pw/(months.length-1) : pw/2);
  const y = v => Tp + ph - v/100*ph;
  let s = "";
  [0,25,50,75,100].forEach(v=>{ s += `<line class="grid" x1="${L}" x2="${W-R}" y1="${y(v)}" y2="${y(v)}"/><text x="${L-6}" y="${y(v)+4}" text-anchor="end">${v}%</text>`; });
  months.forEach((m,i)=>{ if (i%2===0 || months.length<8) s += `<text x="${x(i)}" y="${H-B+16}" text-anchor="middle">${m.slice(2)}</text>`; });
  ["codex","claude-code"].forEach(tool=>{
    const pts = months.map((m,i)=>{ const r = D.by_month_tool.find(r=>r.month===m && r.tool===tool); if (!r) return null; const p = r.input_uncached+r.cache_read+r.cache_write; return p? [x(i), y(100*r.cache_read/p), 100*r.cache_read/p, m]:null; }).filter(Boolean);
    if (!pts.length) return;
    s += `<polyline fill="none" stroke="${col(tool)}" stroke-width="2" stroke-linejoin="round" points="${pts.map(p=>p[0]+","+p[1]).join(" ")}"/>`;
    pts.forEach(p=>{ s += `<circle cx="${p[0]}" cy="${p[1]}" r="4" fill="${col(tool)}" stroke="var(--surface)" stroke-width="2"><title>${tname(tool)} ${p[3]}: ${p[2].toFixed(1)}%</title></circle>`; });
    const last = pts[pts.length-1]; s += `<text x="${last[0]+8}" y="${last[1]+4}" style="fill:var(--ink)">${tname(tool)} ${last[2].toFixed(0)}%</text>`;
  });
  document.getElementById("hitrate").innerHTML = s;
})();

// accounts
(function(){
  if (!ACC) { ["accounts","accountMonths","plans","accountNote"].forEach(id=>{ const el=document.getElementById(id); if (el) el.closest("section").hidden = true; }); return; }
  const reg = ACC.registry||{}; const tot = ACC.subscription_totals||{};
  const toolOf = k => k.startsWith("codex")?"codex":k.startsWith("claude")?"claude-code":k.startsWith("openclaw")?"openclaw":k.startsWith("opencode")?"opencode":k==="copilot"?"copilot-cli":"codex";
  const rows = Object.entries(tot).sort((a,b)=>b[1].api_equivalent_usd-a[1].api_equivalent_usd);
  let t = `<table><tr><th>Account</th><th>Plan</th><th class="n">Months</th><th class="n">Paid</th><th class="n">API-equivalent</th><th class="n">If uncached</th><th class="n">API / sub</th><th class="n">Calls</th><th class="n">Tokens</th></tr>`;
  rows.forEach(([k,r])=>{ const un = k==="unattributed"; t += `<tr><td>${un?"":`<span class="sw" style="background:${col(toolOf(k))}"></span>`}${esc(un?"unattributed":r.label)}<div class="mono" style="font-size:11px;color:var(--ink-3)">${esc(un?"no rule matched":k)}</div></td><td>${esc(un?"unknown":r.plan)}</td><td class="n">${r.months}</td><td class="n">${moneyFull(r.subscription_usd)}</td><td class="n">${moneyFull(r.api_equivalent_usd)}</td><td class="n">${money(r.api_if_uncached_usd)}</td><td class="n">${r.api_to_sub_ratio!=null? r.api_to_sub_ratio+"×":(r.billing==="unknown"?"unknown":"usage-based")}</td><td class="n">${fmt(r.calls)}</td><td class="n">${compact(r.total)}</td></tr>`; });
  // calls that matched no rule are never folded into a real account: they get their own row and a note
  const unRow = ((ACC.by_account||[]).find(r=>r.account==="unattributed")) || (tot.unattributed ? {calls: tot.unattributed.calls, total: tot.unattributed.total} : null);
  const unNote = unRow ? `<p style="font-size:12px;color:var(--ink-2);margin:8px 0 0"><b>Unattributed.</b> ${fmt(unRow.calls)} calls (${compact(unRow.total)} tokens) matched no rule in accounts.json and are listed as <span class="mono">unattributed</span> with billing unknown rather than assigned to an account; add a rule in accounts.json to attribute them.</p>` : "";
  document.getElementById("accounts").innerHTML = t + "</table>" + unNote;
  // month x account matrix (subscription accounts only)
  const subAccts = rows.filter(([k,r])=>r.subscription_usd>0).map(([k])=>k);
  const months = [...new Set((ACC.subscription_rows||[]).map(r=>r.month))].sort();
  const cell = (m,k) => (ACC.subscription_rows||[]).find(r=>r.month===m&&r.account===k);
  let u = `<table><tr><th>Month</th>${subAccts.map(k=>`<th class="n">${esc((reg[k]||{}).label||k).split(" / ").pop().split("@")[0]}</th>`).join("")}<th class="n">Subs paid</th></tr>`;
  months.forEach(m=>{ const paid = subAccts.reduce((a,k)=>a+((cell(m,k)||{}).subscription_usd||0),0); u += `<tr><td class="mono">${m}</td>${subAccts.map(k=>{const c=cell(m,k); return `<td class="n">${c? money(c.api_equivalent_usd):"–"}</td>`;}).join("")}<td class="n">${moneyFull(paid)}</td></tr>`; });
  document.getElementById("accountMonths").innerHTML = u + "</table>";
  // plans
  const plans = (ACC.by_plan||[]).filter(r=>r.tool==="codex").sort((a,b)=>b.total-a.total);
  let v = `<table><tr><th>Plan on the call</th><th class="n">Calls</th><th class="n">Tokens</th><th class="n">API-equivalent</th></tr>`;
  plans.forEach(r=>{ v += `<tr><td class="mono">${esc(r.plan)}</td><td class="n">${fmt(r.calls)}</td><td class="n">${compact(r.total)}</td><td class="n">${moneyFull(r.api_cost_usd)}</td></tr>`; });
  document.getElementById("plans").innerHTML = v + "</table>";
  const ub = (ACC.by_billing_month||[]).filter(r=>r.billing==="usage-based");
  document.getElementById("accountNote").innerHTML = `<b>How accounts were assigned.</b> Codex rollouts record the billing plan on every call but not the account id, so accounts are assigned by the ordered rules in accounts.json (host, plan, working directory, date), each with its evidence and confidence. Calls stamped <span class="mono">self_serve_business_usage_based</span> are billed per token rather than by subscription (${moneyFull(ub.reduce((a,r)=>a+r.api_cost_usd,0))} over ${ub.length} months, real spend at list rates). ${ACC.source==="host placeholders" ? "Accounts are per-host placeholders (credential files were not read; fill in accounts.json to name plans)." : ACC.source==="credential files, minimised" ? "Accounts come from credential files with identity minimised (pseudonymous ids and plan types only)." : "Claude accounts come from each host's <span class=\"mono\">.claude.json</span>."} ${(ACC.rules||[]).filter(r=>r.confidence!=="high").length} of ${(ACC.rules||[]).length} rules are below high confidence; challenge those first.`;
})();

// findings + coverage caveat
(function(){
  const AN = D.analysis; const box = document.getElementById("findings"); const cov = document.getElementById("coverage");
  if (!AN) { box.hidden = true; cov.hidden = true; return; }
  const bt = Object.fromEntries(D.by_tool.map(r=>[r.tool,r]));
  const br = AN.blended_rates||{}, cx = br.codex||{}, cl = br["claude-code"]||{};
  const conc = (AN.concentration||{}).codex||{};
  const dirs = [...D.by_project].sort((a,b)=>b.total-a.total).slice(0,2);
  const tail = p => (p||"").replace(/\\/g,"/").replace(/\/$/,"").split("/").pop();
  const dc = AN.distributions.codex||{}, sc = ST.codex||{}, sl = ST["claude-code"]||{};
  const sens = AN.sensitivity||{};
  const statsHosts = Object.keys(D.stats||{}); const primary = (D.config&&D.config.primary_claude_host) || statsHosts.sort((a,b)=>(D.stats[b].tokens||0)-(D.stats[a].tokens||0))[0];
  const win = primary ? D.stats[primary] : null; const winRow = D.by_tool_host.find(r=>r.tool==="claude-code"&&r.host===primary)||{};
  const eff = AN.effort.codex||{}; const effTot = Object.values(eff).reduce((a,v)=>a+v.calls,0)||1;
  const effTop = Object.entries(eff).sort((a,b)=>b[1].calls-a[1].calls).slice(0,3).map(([k,v])=>`${k} ${(100*v.calls/effTot).toFixed(0)}%`).join(", ");
  const subShare = (t,k) => { const r = D.by_kind.find(r=>r.tool===t&&r.kind===k); return r? r.total/bt[t].total : 0; };
  const F = [
    ["F01","High","Volume is concentrated", (()=>{ const mainTool=[...D.by_tool].sort((a,b)=>b.total-a.total)[0].tool; const c=(AN.concentration||{})[mainTool]||conc; return `${tail(dirs[0].cwd)} (${(100*dirs[0].total/T.total).toFixed(0)}%, ${fmt(dirs[0].sessions)} threads)${dirs[1]?` and ${tail(dirs[1].cwd)} (${(100*dirs[1].total/T.total).toFixed(0)}%, ${fmt(dirs[1].sessions)} threads)`:""}. Top 10% of ${tname(mainTool)} threads carry ${(100*(c.top10pct_share||0)).toFixed(0)}% of its tokens; the largest single thread ${(100*(c.top_session_share||0)).toFixed(1)}%.`; })()],
    ["F02","High","The cache is doing the work", (()=>{ const mainTool=[...D.by_tool].sort((a,b)=>b.total-a.total)[0].tool; const d=(AN.distributions||{})[mainTool]||{}; const b=br[mainTool]||{}; return `Median ${tname(mainTool)} call re-sends ${compact((d.prompt_tokens_per_call||{}).p50||0)} prompt tokens for ${fmt((d.output_tokens_per_call||{}).p50||0)} output tokens; ${fmt(Math.round(b.prompt_tokens_per_output_token||0))} prompt tokens per output token. Caching removed ${(100*(T.cache_savings_usd/(T.cost_if_uncached_usd||1))).toFixed(0)}% of the list price overall.`; })()],
    ["F03","Medium (class C)","Subscriptions vs list price", (()=>{ const rows=subEntries.slice(0,4).map(([k,t])=>`${(t.label||k).split(" / ").pop()} (${t.plan}): ${moneyFull(t.subscription_usd)} over ${t.months} mo against ${money(t.api_equivalent_usd)} (${t.api_to_sub_ratio}×)`); return (rows.length?rows.join("; "):"No subscription accounts configured")+". Assumes identical traffic on a metered key."; })()],
    ["F04","High","Effort and fan-out are material", (()=>{ const mainTool=[...D.by_tool].sort((a,b)=>b.total-a.total)[0].tool; const e=AN.effort[mainTool]||{}; const et=Object.values(e).reduce((a,v)=>a+v.calls,0)||1; const top=Object.entries(e).sort((a,b)=>b[1].calls-a[1].calls).slice(0,3).map(([k,v])=>`${k} ${(100*v.calls/et).toFixed(0)}%`).join(", "); return `Reasoning is ${(100*T.reasoning/(T.output||1)).toFixed(0)}% of all output. ${tname(mainTool)} effort settings: ${top}. Sub-agent share: ${order.filter(t=>bt[t]&&bt[t].total).map(t=>`${tname(t)} ${(100*subShare(t,"subagent")).toFixed(0)}%`).join(", ")}.`; })()],
    ["F05","High","Model mix over time", (()=>{ const top=[...D.by_model].sort((a,b)=>b.total-a.total)[0]; const mm=AN.model_month||{}; const months=Object.keys(mm).sort(); const last=months[months.length-1]; const lead=(mm[last]||[]).slice(0,3).map(r=>`${r.model} (${compact(r.total)})`).join(", "); return `${top.model} carries ${(100*top.total/T.total).toFixed(0)}% of all tokens; in ${last} the leading models by volume were ${lead}.`; })()],
    ["F06","Low (class B)","Claude Code is under-counted", win? `Transcripts on ${primary} survive only the retention window. Claude Code's own counter reports ${compact(win.tokens)} tokens since ${(win.firstSessionDate||"").slice(0,10)}; surviving transcripts hold ${compact(winRow.total||0)}. Claude figures here are lower bounds.` : `Transcripts survive only 30 days; Claude figures are lower bounds.`],
    ["F07","Medium","Price assumptions barely move the total", `${(100*sens.share_on_assumed_prices).toFixed(1)}% of API-equivalent cost (${money(sens.cost_on_assumed_prices)}) rests on models without a published rate. Halving or doubling those rates keeps the total between ${money(sens.band_if_assumed_prices_halved_or_doubled[0])} and ${money(sens.band_if_assumed_prices_halved_or_doubled[1])}.`],
  ];
  box.innerHTML = F.map(([c,conf,h,t])=>`<div class="finding"><div class="code">${c}<b>${esc(conf)}</b></div><h3>${esc(h)}</h3><p>${esc(t)}</p></div>`).join("");
  cov.innerHTML = win ? `<b>Coverage.</b> Claude Code deletes transcripts older than its retention window, so Claude transcripts on ${primary} cover only a recent window. Its own counter (class B evidence) records ${compact(win.tokens)} tokens across ${Object.keys(win.models).length} models since ${(win.firstSessionDate||"").slice(0,10)}, computed ${win.lastComputedDate}. Codex keeps rollouts indefinitely, so Codex coverage is complete for the scanned profiles.<br><br><b>Replay.</b> Spawned Codex threads carry a copy of their parent's history; the Codex app's own counter includes those copies and reports ${compact(D.inventory.reduce((a,i)=>a+i.roots.filter(r=>r.tool==="codex").reduce((b,r)=>b+(r.sqlite_tokens_used||0),0),0))} tokens for these profiles. De-duplicated, the same rollouts hold ${compact(bt.codex.total)} tokens of actual calls; the figures on this page are the de-duplicated ones.` : "";
})();

// validation, concentration, distributions
(function(){
  const AN = D.analysis; if (!AN) return;
  const V = AN.validation||{};
  let t = `<table><tr><th>Host</th><th class="n">Threads</th><th class="n">Within 2%</th><th class="n">Within 10%</th><th class="n">Rollout sum</th><th class="n">SQLite sum</th><th class="n">Ratio</th></tr>`;
  Object.entries(V).forEach(([h,v])=>{ if (v.error) { t += `<tr><td class="mono">${esc(h)}</td><td colspan="6">${esc(v.error)}</td></tr>`; return; }
    t += `<tr><td class="mono">${esc(h)}</td><td class="n">${fmt(v.sqlite_threads_with_tokens)}</td><td class="n">${(100*v.within_2pct/v.sqlite_threads_with_tokens).toFixed(1)}%</td><td class="n">${(100*v.within_10pct/v.sqlite_threads_with_tokens).toFixed(1)}%</td><td class="n">${compact(v.rollout_sum_same_threads)}</td><td class="n">${compact(v.sqlite_sum)}</td><td class="n">${(v.rollout_sum_same_threads/v.sqlite_sum).toFixed(3)}</td></tr>`; });
  t += `</table><p style="font-size:12px;color:var(--ink-3);margin:8px 0 0">Where SQLite exceeds the rollout on a spawned thread it has counted the replayed parent history this compile removes; where the rollout exceeds SQLite the thread outlived SQLite's counter across compactions. Rollout-derived figures are used throughout.</p>`;
  document.getElementById("validation").innerHTML = t;
  const C = AN.concentration||{};
  let u = `<table><tr><th>Tool</th><th class="n">Sessions</th><th class="n">Top 1%</th><th class="n">Top 10%</th><th class="n">Largest</th></tr>`;
  Object.entries(C).forEach(([tool,c])=>{ u += `<tr><td><span class="sw" style="background:${col(tool)}"></span>${tname(tool)}</td><td class="n">${fmt(c.sessions)}</td><td class="n">${(100*c.top1pct_share).toFixed(1)}%</td><td class="n">${(100*c.top10pct_share).toFixed(1)}%</td><td class="n">${(100*c.top_session_share).toFixed(1)}%</td></tr>`; });
  document.getElementById("concentration").innerHTML = u + "</table>";
  const Dd = AN.distributions||{}, Sd = AN.session_distributions||{};
  let w = `<table><tr><th>Tool</th><th class="n">Calls</th><th class="n">Prompt p50</th><th class="n">p90</th><th class="n">p99</th><th class="n">Output p50</th><th class="n">p90</th><th class="n">p99</th></tr>`;
  order.forEach(tool=>{ const d = Dd[tool]; if (!d||!d.prompt_tokens_per_call.n) return; const pc=d.prompt_tokens_per_call, oc=d.output_tokens_per_call;
    w += `<tr><td><span class="sw" style="background:${col(tool)}"></span>${tname(tool)}</td><td class="n">${fmt(pc.n)}</td><td class="n">${compact(pc.p50)}</td><td class="n">${compact(pc.p90)}</td><td class="n">${compact(pc.p99)}</td><td class="n">${compact(oc.p50)}</td><td class="n">${compact(oc.p90)}</td><td class="n">${compact(oc.p99)}</td></tr>`; });
  w += `</table><table style="margin-top:12px"><tr><th>Tool</th><th class="n">Sessions</th><th class="n">Calls p50</th><th class="n">p90</th><th class="n">Tokens p50</th><th class="n">p90</th><th class="n">Span p50</th><th class="n">p90</th><th class="n">max</th></tr>`;
  order.forEach(tool=>{ const sd = Sd[tool]; if (!sd||!sd.total||!sd.total.n) return; const hh = sd.hours&&sd.hours.n? sd.hours : null;
    w += `<tr><td><span class="sw" style="background:${col(tool)}"></span>${tname(tool)}</td><td class="n">${fmt(sd.total.n)}</td><td class="n">${fmt(Math.round(sd.calls.p50))}</td><td class="n">${fmt(Math.round(sd.calls.p90))}</td><td class="n">${compact(sd.total.p50)}</td><td class="n">${compact(sd.total.p90)}</td><td class="n">${hh?hh.p50.toFixed(1)+" h":"–"}</td><td class="n">${hh?hh.p90.toFixed(1)+" h":"–"}</td><td class="n">${hh?Math.round(hh.max)+" h":"–"}</td></tr>`; });
  document.getElementById("dist").innerHTML = w + "</table>";
})();

// weekday x hour heatmap
(function(){
  const AN = D.analysis; if (!AN||!AN.hour_weekday_calls) return;
  const H = AN.hour_weekday_calls; const days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const mat = days.map((_,d)=>Array.from({length:24},(_,h)=>((((H.codex||[])[d]||[])[h])||0)+((((H["claude-code"]||[])[d]||[])[h])||0)));
  const W=1140,Hh=230,L=48,T0=24, cw=(W-L-12)/24, ch=(Hh-T0-12)/7; const mx = Math.max(...mat.flat())||1;
  const seq = ["var(--surface-2)","var(--seq1)","var(--seq2)","var(--seq3)","var(--seq4)","var(--seq5)","var(--seq6)","var(--seq7)"];
  let s = "";
  for (let h=0;h<24;h+=3) s += `<text x="${(L+cw*h+cw/2).toFixed(1)}" y="${T0-8}" text-anchor="middle">${String(h).padStart(2,"0")}</text>`;
  days.forEach((dn,d)=>{ s += `<text x="${L-8}" y="${(T0+ch*d+ch/2+4).toFixed(1)}" text-anchor="end">${dn}</text>`;
    for (let h=0;h<24;h++){ const v=mat[d][h]; const lvl = v===0?0:Math.min(7,1+Math.floor(7*Math.sqrt(v/mx))); s += `<rect x="${(L+cw*h+1).toFixed(1)}" y="${(T0+ch*d+1).toFixed(1)}" width="${(cw-2).toFixed(1)}" height="${(ch-2).toFixed(1)}" rx="2" fill="${seq[lvl]}"><title>${dn} ${String(h).padStart(2,"0")}:00 · ${fmt(v)} calls</title></rect>`; } });
  document.getElementById("heat").innerHTML = s;
})();

// calendar heatmap
(function(){
  const byDay = {}; D.by_day_tool.forEach(r=>{ if(r.date==="?") return; const d = byDay[r.date] ||= {total:0,calls:0,tools:{}}; d.total+=r.total; d.calls+=r.calls; d.tools[r.tool]=r.total; });
  const first = new Date(days[0]+"T00:00:00Z"), last = new Date(days[days.length-1]+"T00:00:00Z");
  const start = new Date(first); start.setUTCDate(start.getUTCDate()-start.getUTCDay());
  const vals = Object.values(byDay).map(d=>d.total).filter(v=>v>0).sort((a,b)=>a-b);
  const q = p => vals[Math.min(vals.length-1, Math.floor(vals.length*p))];
  const th = [q(.15), q(.35), q(.55), q(.75), q(.9), q(.97)];
  const cls = v => v<=0?0: v<th[0]?1: v<th[1]?2: v<th[2]?3: v<th[3]?4: v<th[4]?5: v<th[5]?6:7;
  const seq = ["var(--surface-2)","var(--seq1)","var(--seq2)","var(--seq3)","var(--seq4)","var(--seq5)","var(--seq6)","var(--seq7)"];
  let s = "", months = "", lastM = -1, weeks = 0;
  for (let d = new Date(start); d <= last; d.setUTCDate(d.getUTCDate()+1)) {
    const key = d.toISOString().slice(0,10); const r = byDay[key];
    if (d.getUTCDay()===0) { if (d.getUTCMonth()!==lastM) { months += `<span style="left:${weeks*15}px">${d.toLocaleString("en-US",{month:"short",timeZone:"UTC"})}</span>`; lastM = d.getUTCMonth(); } weeks++; }
    const v = r ? r.total : 0;
    s += `<div style="background:${seq[cls(v)]}" data-k="${key}" data-v="${v}" data-c="${r?r.calls:0}" data-tools="${r?esc(Object.entries(r.tools).map(([t,x])=>tname(t)+" "+compact(x)).join(", ")):""}"></div>`;
  }
  const cal = document.getElementById("cal"); cal.innerHTML = s; document.getElementById("calmonths").innerHTML = months;
  cal.style.width = (weeks*15)+"px";
  cal.addEventListener("mousemove", e=>{ const t = e.target; if (t.dataset && t.dataset.k) showTip(e, `<b>${t.dataset.k}</b><br>${fmt(+t.dataset.v)} tokens · ${fmt(+t.dataset.c)} calls${t.dataset.tools?"<br>"+t.dataset.tools:""}`); else hideTip(); });
  cal.addEventListener("mouseleave", hideTip);
  document.getElementById("calscale").innerHTML = `less ` + seq.map(c=>`<i style="background:${c}"></i>`).join("") + ` more · breaks at ${th.map(compact).join(" / ")}`;
})();

// by model
(function(){
  const rows = [...D.by_model].sort((a,b)=>b.total-a.total).slice(0,14);
  const max = rows[0].total;
  let t = `<table><tr><th>Model</th><th>Tool</th><th style="width:26%">Share</th><th class="n">Tokens</th><th class="n">Output</th><th class="n">Calls</th><th class="n">Hit rate</th><th class="n">API-eq.</th></tr>`;
  rows.forEach(r=>{ const p = r.input_uncached+r.cache_read+r.cache_write; t += `<tr><td class="mono">${esc(r.model)}</td><td><span class="sw" style="background:${col(r.tool)}"></span>${tname(r.tool)}</td><td><div class="bar"><b style="width:${(100*r.total/max).toFixed(1)}%;background:${col(r.tool)}"></b></div></td><td class="n">${compact(r.total)} <span style="color:var(--ink-3)">${(100*r.total/T.total).toFixed(1)}%</span></td><td class="n">${compact(r.output)}</td><td class="n">${fmt(r.calls)}</td><td class="n">${p?(100*r.cache_read/p).toFixed(0):0}%</td><td class="n">${money(r.api_cost_usd||0)}</td></tr>`; });
  document.getElementById("models").innerHTML = t + "</table>";
})();

// tool x host
(function(){
  const rows = [...D.by_tool_host].sort((a,b)=>b.total-a.total);
  let t = `<table><tr><th>Tool</th><th>Host</th><th class="n">Calls</th><th class="n">Sessions</th><th class="n">Output</th><th class="n">Tokens</th><th class="n">API-eq.</th></tr>`;
  rows.forEach(r=>{ t += `<tr><td><span class="sw" style="background:${col(r.tool)}"></span>${tname(r.tool)}</td><td class="mono">${esc(r.host)}</td><td class="n">${fmt(r.calls)}</td><td class="n">${fmt(r.sessions)}</td><td class="n">${compact(r.output)}</td><td class="n">${compact(r.total)}</td><td class="n">${money(r.api_cost_usd||0)}</td></tr>`; });
  document.getElementById("toolhost").innerHTML = t + "</table>";
  const k = [...D.by_kind].sort((a,b)=>b.total-a.total);
  let u = `<table><tr><th>Tool</th><th>Kind</th><th class="n">Calls</th><th class="n">Sessions</th><th class="n">Tokens</th></tr>`;
  k.forEach(r=>{ u += `<tr><td><span class="sw" style="background:${col(r.tool)}"></span>${tname(r.tool)}</td><td>${esc(r.kind)}</td><td class="n">${fmt(r.calls)}</td><td class="n">${fmt(r.sessions)}</td><td class="n">${compact(r.total)}</td></tr>`; });
  document.getElementById("kind").innerHTML = u + "</table>";
})();

// projects
(function(){
  let t = `<table><tr><th>Tool</th><th>Working directory</th><th class="n">Sessions</th><th class="n">Calls</th><th class="n">Output</th><th class="n">Tokens</th><th class="n">API-eq.</th></tr>`;
  D.by_project.forEach(r=>{ t += `<tr><td><span class="sw" style="background:${col(r.tool)}"></span>${tname(r.tool)}</td><td class="path">${esc(r.cwd)}</td><td class="n">${fmt(r.sessions)}</td><td class="n">${fmt(r.calls)}</td><td class="n">${compact(r.output)}</td><td class="n">${compact(r.total)}</td><td class="n">${money(r.api_cost_usd||0)}</td></tr>`; });
  document.getElementById("projects").innerHTML = t + "</table>";
})();

// sessions
(function(){
  let t = `<table><tr><th>Tool</th><th>Host</th><th>Session / thread id</th><th class="n">Calls</th><th class="n">Output</th><th class="n">Tokens</th><th class="n">API-eq.</th></tr>`;
  D.top_sessions.forEach(r=>{ t += `<tr><td><span class="sw" style="background:${col(r.tool)}"></span>${tname(r.tool)}</td><td class="mono">${esc(r.host)}</td><td class="path">${esc(r.session)}</td><td class="n">${fmt(r.calls)}</td><td class="n">${compact(r.output)}</td><td class="n">${compact(r.total)}</td><td class="n">${money(r.api_cost_usd||0)}</td></tr>`; });
  document.getElementById("sessions").innerHTML = t + "</table>";
})();

// inventory
(function(){
  let t = `<table><tr><th>Host</th><th>Tool</th><th>Root</th><th class="n">Calls found</th><th class="n">Prompts</th><th class="n">Tool's own thread count</th><th class="n">Tool's own token total</th></tr>`;
  D.inventory.forEach(inv=>inv.roots.forEach(r=>{ t += `<tr><td class="mono">${esc(inv.host)}</td><td><span class="sw" style="background:${col(r.tool)}"></span>${tname(r.tool)}</td><td class="path">${esc(r.root)}</td><td class="n">${fmt(r.events||0)}</td><td class="n">${fmt(r.prompts||0)}</td><td class="n">${r.sqlite_threads?fmt(r.sqlite_threads):"–"}</td><td class="n">${r.sqlite_tokens_used?compact(r.sqlite_tokens_used):"–"}</td></tr>`; }));
  t += `</table>`;
  const foot = D.inventory.map(i=>`<span class="chip">${esc(i.host)}: ${fmt(i.files)} files · ${(i.bytes/1e9).toFixed(1)} GB · ${fmt(i.lines)} lines · ${i.seconds}s</span>`).join(" ");
  document.getElementById("inventory").innerHTML = t + `<div class="hosts" style="justify-content:flex-start;margin-top:10px">${foot}</div>`;
  document.getElementById("caveat").innerHTML = `${D.config&&D.config.excluded_note ? esc(D.config.excluded_note)+"<br><br>" : ""}<b>Pricing assumptions.</b> ${Object.entries(C.assumed_models||{}).map(([k,v])=>`<span class="mono">${esc(k)}</span>: ${esc(v)}`).join("; ")||"none"}. Subscriptions are counted only in months the account was used; plans and prices are in accounts.json, rates in pricing.json.`;
})();
</script>
"""
html = html.replace("__DATA__", payload)
_style, _header, _footer, _link = brand_blocks(CFG, os.path.dirname(os.path.abspath(sys.argv[3])) if len(sys.argv) > 3 else None)
html = html.replace("__BRAND_STYLE__", _link + _style).replace("__BRAND_HEADER__", _header).replace("__BRAND_FOOTER__", _footer).replace("__THEMEBAR__", THEMEBAR_HTML)
html = html.replace("__THEME_DEFAULT__", str(CFG.get("theme_default") or "system") if str(CFG.get("theme_default") or "system") in ("light", "dark", "system") else "system")
html = html.replace("__PAGE_TITLE__", _html.escape(str(CFG.get("dashboard_title") or "Agent Token Ledger"), quote=True))
safety.private_dir(os.path.dirname(os.path.abspath(dst)) or ".")
with safety.private_open(dst, "w") as fh:
    fh.write(html)
print("wrote", dst, len(html) // 1024, "KB")
