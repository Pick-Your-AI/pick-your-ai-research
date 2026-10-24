#!/usr/bin/env python3
"""
analyze_events.py - second-pass statistics over compiled/all_events.csv for the
research report: distributions, temporal patterns, model mix, caching economics,
cost sensitivity, and validation of Codex rollout totals against Codex's own
state_5.sqlite. Writes compiled/analysis.json.

usage: python analyze_events.py --compiled compiled --sqlite windows=path --sqlite wsl-ubuntu=path ... --tz America/New_York
"""
import argparse
import csv
import json
import os
import sqlite3
import sys
import time
from collections import defaultdict, Counter
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import safety  # noqa: E402


def pct(sorted_vals, q):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * q
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def summarize(vals):
    if not vals:
        return {"n": 0}
    vals.sort()
    n = len(vals)
    return {"n": n, "mean": sum(vals) / n, "p50": pct(vals, .5), "p90": pct(vals, .9), "p99": pct(vals, .99), "max": vals[-1], "min": vals[0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiled", default="compiled")
    ap.add_argument("--sqlite", action="append", default=[], help="host=path/to/state_5.sqlite")
    ap.add_argument("--tz", default="America/New_York")
    ap.add_argument("--pricing", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "pricing.json"))
    a = ap.parse_args()
    tz = ZoneInfo(a.tz) if ZoneInfo else timezone.utc
    t0 = time.time()

    ev_path = os.path.join(a.compiled, "all_events.csv")
    ctx = defaultdict(list)       # tool -> per-call prompt size
    outp = defaultdict(list)      # tool -> per-call output
    hour_mat = defaultdict(lambda: [[0] * 24 for _ in range(7)])   # tool -> weekday x hour calls
    hour_tok = defaultdict(lambda: [[0] * 24 for _ in range(7)])
    model_month = defaultdict(lambda: defaultdict(lambda: {"calls": 0, "total": 0, "output": 0, "cost": 0.0}))
    kind_month = defaultdict(lambda: defaultdict(lambda: {"calls": 0, "total": 0, "cost": 0.0}))
    effort = defaultdict(lambda: defaultdict(lambda: {"calls": 0, "output": 0, "reasoning": 0, "cost": 0.0}))
    entry = defaultdict(lambda: {"calls": 0, "total": 0, "cost": 0.0})
    priced_as = defaultdict(lambda: {"calls": 0, "total": 0, "cost": 0.0, "models": set()})
    ttl = {"cache_write_5m": 0, "cache_write_1h": 0}
    sess_tok = defaultdict(lambda: {"calls": 0, "total": 0, "output": 0, "cost": 0.0, "first": None, "last": None, "cwd": None, "kind": None, "model": Counter()})
    cache_month = defaultdict(lambda: defaultdict(lambda: {"iu": 0, "cr": 0, "cw": 0, "cost": 0.0, "nocache": 0.0}))
    tool_tot = defaultdict(lambda: {"calls": 0, "iu": 0, "cr": 0, "cw": 0, "out": 0, "reasoning": 0, "cost": 0.0, "nocache": 0.0})
    version_tool = defaultdict(Counter)
    n = 0
    with open(ev_path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            n += 1
            tool = r["tool"]
            iu, cr, cw, out, rs = int(r["input_uncached"] or 0), int(r["cache_read"] or 0), int(r["cache_write"] or 0), int(r["output"] or 0), int(r["reasoning"] or 0)
            cost = float(r["api_cost_usd"] or 0)
            nocache = float(r["cost_if_uncached_usd"] or 0)
            prompt = iu + cr + cw
            ctx[tool].append(prompt)
            outp[tool].append(out)
            month = (r["date"] or "?")[:7]
            ts = r["ts"]
            if ts:
                try:
                    d = datetime.fromisoformat(ts).astimezone(tz)
                    hour_mat[tool][d.weekday()][d.hour] += 1
                    hour_tok[tool][d.weekday()][d.hour] += prompt + out
                except Exception:
                    pass
            mm = model_month[month][(tool, r["model"] or "?")]
            mm["calls"] += 1
            mm["total"] += prompt + out
            mm["output"] += out
            mm["cost"] += cost
            km = kind_month[month][(tool, r["kind"] or "main")]
            km["calls"] += 1
            km["total"] += prompt + out
            km["cost"] += cost
            ef = effort[tool][r["effort"] or "unset"]
            ef["calls"] += 1
            ef["output"] += out
            ef["reasoning"] += rs
            ef["cost"] += cost
            en = entry[(tool, r["entrypoint"] or "?")]
            en["calls"] += 1
            en["total"] += prompt + out
            en["cost"] += cost
            pa = priced_as[(tool, r["priced_as"] or "?")]
            pa["calls"] += 1
            pa["total"] += prompt + out
            pa["cost"] += cost
            pa["models"].add(r["model"] or "?")
            if r.get("cache_write_5m"):
                ttl["cache_write_5m"] += int(r["cache_write_5m"] or 0)
            if r.get("cache_write_1h"):
                ttl["cache_write_1h"] += int(r["cache_write_1h"] or 0)
            st = sess_tok[(tool, r["host"], r["session"])]
            st["calls"] += 1
            st["total"] += prompt + out
            st["output"] += out
            st["cost"] += cost
            st["first"] = ts if st["first"] is None or (ts and ts < st["first"]) else st["first"]
            st["last"] = ts if st["last"] is None or (ts and ts > st["last"]) else st["last"]
            st["cwd"] = st["cwd"] or r["cwd"]
            st["kind"] = st["kind"] or r["kind"]
            st["model"][r["model"] or "?"] += 1
            cm = cache_month[month][tool]
            cm["iu"] += iu
            cm["cr"] += cr
            cm["cw"] += cw
            cm["cost"] += cost
            cm["nocache"] += nocache
            tt = tool_tot[tool]
            tt["calls"] += 1
            tt["iu"] += iu
            tt["cr"] += cr
            tt["cw"] += cw
            tt["out"] += out
            tt["reasoning"] += rs
            tt["cost"] += cost
            tt["nocache"] += nocache
            version_tool[tool][r["version"] or "?"] += 1
            if n % 1000000 == 0:
                sys.stderr.write("  %d rows %.0fs\n" % (n, time.time() - t0))

    sys.stderr.write("events read: %d (%.0fs)\n" % (n, time.time() - t0))

    # ---- distributions
    dist = {}
    for tool in ctx:
        dist[tool] = {"prompt_tokens_per_call": summarize(ctx[tool]), "output_tokens_per_call": summarize(outp[tool])}
    # per-session distributions
    sess_dist = {}
    per_tool_sessions = defaultdict(lambda: {"calls": [], "total": [], "output": [], "cost": [], "hours": []})
    sessions_out = []
    for (tool, host, sid), s in sess_tok.items():
        hrs = None
        try:
            if s["first"] and s["last"]:
                hrs = (datetime.fromisoformat(s["last"]) - datetime.fromisoformat(s["first"])).total_seconds() / 3600.0
        except Exception:
            pass
        p = per_tool_sessions[tool]
        p["calls"].append(s["calls"])
        p["total"].append(s["total"])
        p["output"].append(s["output"])
        p["cost"].append(s["cost"])
        if hrs is not None:
            p["hours"].append(hrs)
        sessions_out.append({"tool": tool, "host": host, "session": sid, "calls": s["calls"], "total": s["total"], "output": s["output"],
                             "cost": round(s["cost"], 2), "hours": round(hrs, 2) if hrs is not None else None, "cwd": s["cwd"], "kind": s["kind"],
                             "model": s["model"].most_common(1)[0][0], "first": s["first"], "last": s["last"]})
    for tool, p in per_tool_sessions.items():
        sess_dist[tool] = {k: summarize(v) for k, v in p.items()}
    sessions_out.sort(key=lambda s: -s["total"])

    # Lorenz / concentration: share of tokens in top 1%, 10% of sessions
    conc = {}
    for tool, p in per_tool_sessions.items():
        tot = sorted(p["total"], reverse=True)
        s = sum(tot)
        if not s:
            continue
        def share(frac):
            k = max(1, int(len(tot) * frac))
            return sum(tot[:k]) / s
        conc[tool] = {"sessions": len(tot), "top1pct_share": share(.01), "top10pct_share": share(.10), "top_session_share": tot[0] / s}

    # ---- codex validation vs sqlite
    validation = {}
    for spec in a.sqlite:
        host, path = spec.split("=", 1)
        try:
            c = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
            rows = {}
            cols = [r[1] for r in c.execute("pragma table_info(threads)")]
            src_col = "thread_source" if "thread_source" in cols else ("source" if "source" in cols else "NULL")
            model_col = "model" if "model" in cols else "NULL"
            for tid, tok, src, model in c.execute("select id, tokens_used, %s, %s from threads" % (src_col, model_col)):
                if src and src not in ("user", "subagent", "cli", "exec"):
                    src = "subagent" if "subagent" in str(src) else src
                rows[tid] = (tok or 0, src, model)
            c.close()
        except Exception as ex:
            validation[host] = {"error": str(ex)}
            continue
        mine = {sid: s["total"] for (tool, h, sid), s in sess_tok.items() if tool == "codex" and h == host}
        cmp = []
        for tid, (tok, src, model) in rows.items():
            if tok <= 0:
                continue
            cmp.append((tid, mine.get(tid, 0), tok, src))
        within2 = sum(1 for _, m, s, _ in cmp if abs(m - s) <= 0.02 * s)
        within10 = sum(1 for _, m, s, _ in cmp if abs(m - s) <= 0.10 * s)
        sub_over = sum(1 for _, m, s, src in cmp if src == "subagent" and s > m * 1.1)
        validation[host] = {
            "sqlite_threads_with_tokens": len(cmp), "rollout_threads": len(mine),
            "sqlite_sum": sum(s for _, _, s, _ in cmp), "rollout_sum_same_threads": sum(m for _, m, _, _ in cmp),
            "rollout_sum_all": sum(mine.values()),
            "within_2pct": within2, "within_10pct": within10,
            "subagent_threads_where_sqlite_exceeds_rollout": sub_over,
            "largest_disagreements": sorted([{"thread": t, "rollout": m, "sqlite": s, "source": src} for t, m, s, src in cmp], key=lambda x: -abs(x["rollout"] - x["sqlite"]))[:8],
        }

    # ---- cost sensitivity
    total_cost = sum(t["cost"] for t in tool_tot.values())
    pricing = json.load(open(a.pricing, encoding="utf-8"))
    assumed = {k for k, v in pricing["models"].items() if v.get("assumed")}
    assumed_cost = sum(v["cost"] for (tool, pa), v in priced_as.items() if pa in assumed or any(m not in pricing["models"] for m in v["models"]))
    sensitivity = {
        "total_cost": total_cost,
        "cost_on_assumed_prices": assumed_cost,
        "share_on_assumed_prices": assumed_cost / total_cost if total_cost else 0,
        "band_if_assumed_prices_halved_or_doubled": [total_cost - assumed_cost / 2, total_cost + assumed_cost],
        "codex_cost_if_cached_rate_were_full_input": None,
        "priced_as": [{"tool": t, "priced_as": pa, "calls": v["calls"], "total": v["total"], "cost": v["cost"], "models": sorted(v["models"])} for (t, pa), v in sorted(priced_as.items(), key=lambda kv: -kv[1]["cost"])],
    }
    # blended effective rates per tool
    blended = {}
    for tool, t in tool_tot.items():
        prompt = t["iu"] + t["cr"] + t["cw"]
        blended[tool] = {
            "cost_per_M_output_tokens": (t["cost"] / t["out"] * 1e6) if t["out"] else None,
            "cost_per_call": t["cost"] / t["calls"] if t["calls"] else None,
            "cache_hit_rate": t["cr"] / prompt if prompt else None,
            "prompt_tokens_per_output_token": prompt / t["out"] if t["out"] else None,
            "reasoning_share_of_output": t["reasoning"] / t["out"] if t["out"] else None,
            "savings_pct": (t["nocache"] - t["cost"]) / t["nocache"] if t["nocache"] else None,
        }

    out = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "events": n,
        "timezone": a.tz,
        "distributions": dist,
        "session_distributions": sess_dist,
        "concentration": conc,
        "top_sessions": sessions_out[:40],
        "hour_weekday_calls": {t: m for t, m in hour_mat.items()},
        "hour_weekday_tokens": {t: m for t, m in hour_tok.items()},
        "model_month": {m: [{"tool": t, "model": mo, **v} for (t, mo), v in sorted(d.items(), key=lambda kv: -kv[1]["total"])] for m, d in sorted(model_month.items())},
        "kind_month": {m: [{"tool": t, "kind": k, **v} for (t, k), v in d.items()] for m, d in sorted(kind_month.items())},
        "effort": {t: dict(d) for t, d in effort.items()},
        "entrypoints": [{"tool": t, "entrypoint": e, **v} for (t, e), v in sorted(entry.items(), key=lambda kv: -kv[1]["total"])],
        "cache_ttl_split": ttl,
        "cache_month": {m: {t: {**v, "hit_rate": (v["cr"] / (v["iu"] + v["cr"] + v["cw"])) if (v["iu"] + v["cr"] + v["cw"]) else None} for t, v in d.items()} for m, d in sorted(cache_month.items())},
        "tool_totals": tool_tot,
        "blended_rates": blended,
        "versions": {t: c.most_common(12) for t, c in version_tool.items()},
        "validation": validation,
        "sensitivity": sensitivity,
        "seconds": round(time.time() - t0, 1),
    }
    with safety.private_open(os.path.join(a.compiled, "analysis.json"), "w") as f:
        json.dump(out, f, indent=1, default=lambda o: list(o) if isinstance(o, set) else str(o))
    sys.stderr.write("analysis.json written (%.0fs)\n" % (time.time() - t0))


if __name__ == "__main__":
    main()
