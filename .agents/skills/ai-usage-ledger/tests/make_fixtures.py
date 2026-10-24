#!/usr/bin/env python3
"""
Create small synthetic log trees for every parser, run the scanner over them, and check
that each produces events with the expected token totals. Run from the skill directory:

    python tests/make_fixtures.py

Fixtures mirror the documented shapes in references/log-formats.md and harness-catalog.md;
they are not real transcripts.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixtures")
OUT = os.path.join(HERE, "out")
SCANNER = os.path.join(HERE, "..", "scripts", "compile_ai_logs.py")


def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content if isinstance(content, str) else "\n".join(json.dumps(x) for x in content) + "\n")


def build():
    shutil.rmtree(FX, ignore_errors=True)
    # Claude Code: two lines share a message id (streamed), 1h cache write
    w(os.path.join(FX, "claude", "projects", "proj", "s1.jsonl"), [
        {"type": "user", "timestamp": "2026-01-01T10:00:00Z", "sessionId": "s1", "cwd": "/w", "version": "2.1", "entrypoint": "cli", "message": {"role": "user", "content": "hi"}},
        {"type": "assistant", "timestamp": "2026-01-01T10:00:05Z", "sessionId": "s1", "cwd": "/w", "message": {"id": "m1", "model": "claude-opus-5", "content": [{"type": "text", "text": "x"}], "usage": {"input_tokens": 10, "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 200, "output_tokens": 50, "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 200}}}},
        {"type": "assistant", "timestamp": "2026-01-01T10:00:06Z", "sessionId": "s1", "cwd": "/w", "message": {"id": "m1", "model": "claude-opus-5", "content": [{"type": "tool_use", "name": "Bash"}], "usage": {"input_tokens": 10, "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 200, "output_tokens": 50}}},
    ])
    # Codex: parent thread + a forked child that replays the parent's two events then makes one real call
    parent = [
        {"timestamp": "2026-02-01T10:00:00Z", "type": "session_meta", "payload": {"id": "p1", "cwd": "/w", "originator": "codex-tui", "cli_version": "0.1", "timestamp": "2026-02-01T10:00:00Z"}},
        {"timestamp": "2026-02-01T10:00:01Z", "type": "turn_context", "payload": {"model": "gpt-5.5"}},
        {"timestamp": "2026-02-01T10:00:20Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 1100}, "last_token_usage": {"input_tokens": 1000, "cached_input_tokens": 900, "output_tokens": 100, "reasoning_output_tokens": 10}}, "rate_limits": {"plan_type": "pro"}}},
        {"timestamp": "2026-02-01T10:00:40Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 2200}, "last_token_usage": {"input_tokens": 1000, "cached_input_tokens": 900, "output_tokens": 100, "reasoning_output_tokens": 10}}, "rate_limits": {"plan_type": "pro"}}},
    ]
    w(os.path.join(FX, "codex", "sessions", "2026", "02", "01", "rollout-2026-02-01T10-00-00-p1000000-0000-0000-0000-000000000001.jsonl"), parent)
    child = [dict(parent[0], timestamp="2026-02-01T11:00:00Z", payload=dict(parent[0]["payload"], id="c1", forked_from_id="p1", source={"subagent": {"thread_spawn": {"parent_thread_id": "p1"}}}))]
    child += [dict(x, timestamp="2026-02-01T11:00:00.5Z") for x in parent]   # replay burst, same second
    child += [
        {"timestamp": "2026-02-01T11:00:30Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 2400}, "last_token_usage": {"input_tokens": 200, "cached_input_tokens": 100, "output_tokens": 30, "reasoning_output_tokens": 0}}, "rate_limits": {"plan_type": "pro"}}},
    ]
    w(os.path.join(FX, "codex", "sessions", "2026", "02", "01", "rollout-2026-02-01T11-00-00-c1000000-0000-0000-0000-000000000002.jsonl"), child)
    # Gemini CLI (JSON document form)
    w(os.path.join(FX, "gemini", "hash1", "chats", "session-2026-03-01T10-00-abcd1234.json"), json.dumps({
        "sessionId": "g1", "projectHash": "hash1", "startTime": "2026-03-01T10:00:00Z", "lastUpdated": "2026-03-01T10:05:00Z", "messages": [
            {"id": "u1", "timestamp": "2026-03-01T10:00:00Z", "type": "user", "content": [{"text": "hello"}]},
            {"id": "a1", "timestamp": "2026-03-01T10:00:03Z", "type": "gemini", "model": "gemini-2.5-pro", "content": [{"text": "hi"}], "tokens": {"input": 500, "output": 40, "cached": 300, "thoughts": 20, "tool": 0, "total": 560}},
        ]}))
    # Cline family
    w(os.path.join(FX, "cline", "tasks", "t1", "ui_messages.json"), json.dumps([
        {"ts": 1775000000000, "type": "say", "say": "text", "text": "do the thing"},
        {"ts": 1775000001000, "type": "say", "say": "api_req_started", "text": json.dumps({"request": "...", "tokensIn": 800, "tokensOut": 60, "cacheWrites": 100, "cacheReads": 700, "cost": 0.0123})},
        {"ts": 1775000002000, "type": "say", "say": "tool", "text": "{}"},
    ]))
    w(os.path.join(FX, "cline", "tasks", "t1", "task_metadata.json"), json.dumps({"model_usage": [{"model_id": "claude-sonnet-5", "model_provider_id": "anthropic"}]}))
    # aider
    w(os.path.join(FX, "aider", "repo", ".aider.chat.history.md"), "\n".join([
        "# aider chat started at 2026-04-01 09:00:00", "", "> Model: gpt-5.5 with diff edit format", "", "#### make it work", "",
        "Sure.", "", "> Tokens: 2.8k sent, 27 received. Cost: $0.0029 message, $0.0029 session.", "",
        "#### and tests", "", "> Tokens: 36,428 sent, 120 received. Cost: $0.11 message, $0.11 session.", ""]))
    # Kimi
    w(os.path.join(FX, "kimi", "sessions", "wd1", "k1", "wire.jsonl"), [
        {"type": "StatusUpdate", "timestamp": "2026-05-01T10:00:00Z", "payload": {"scope": "turn", "model": "kimi-k2.6", "token_usage": {"input_other": 100, "input_cache_read": 900, "input_cache_creation": 50, "output": 40}}},
        {"type": "StatusUpdate", "timestamp": "2026-05-01T10:00:05Z", "payload": {"scope": "session", "token_usage": {"input_other": 100, "input_cache_read": 900, "input_cache_creation": 50, "output": 40}}},
    ])
    # Mistral Vibe
    w(os.path.join(FX, "vibe", "logs", "session", "v1", "meta.json"), json.dumps({"session_id": "v1", "created_at": "2026-06-01T10:00:00Z", "environment": {"working_directory": "/w"}, "model": {"name": "devstral-2"}, "stats": {"session_prompt_tokens": 5000, "session_completion_tokens": 300, "session_cost": 0.02}}))
    # Continue
    w(os.path.join(FX, "continue", "dev_data", "0.2.0", "tokensGenerated.jsonl"), [
        {"timestamp": "2026-07-01T10:00:00Z", "sessionId": "c1", "model": "gpt-5-mini", "provider": "openai", "promptTokens": 1200, "generatedTokens": 80},
    ])
    # pi (OpenClaw-style session file)
    w(os.path.join(FX, "pi", "--w--", "2026-08-01_p.jsonl"), [
        {"type": "session", "version": 3, "id": "pi1", "timestamp": "2026-08-01T10:00:00Z", "cwd": "/w"},
        {"type": "model_change", "id": "m0", "parentId": None, "timestamp": "2026-08-01T10:00:00Z", "provider": "anthropic", "modelId": "claude-sonnet-5"},
        {"type": "message", "id": "m1", "parentId": "m0", "timestamp": "2026-08-01T10:00:01Z", "message": {"role": "user", "content": "hi"}},
        {"type": "message", "id": "m2", "parentId": "m1", "timestamp": "2026-08-01T10:00:04Z", "message": {"role": "assistant", "provider": "anthropic", "model": "claude-sonnet-5", "content": "hey", "usage": {"input": 20, "output": 10, "cacheRead": 400, "cacheWrite": 0, "totalTokens": 430, "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "total": 0.001}}}},
    ])
    # generic (Codebuff-like)
    w(os.path.join(FX, "generic", "projects", "p", "chats", "c1", "chat-messages.json"), json.dumps({"messages": [
        {"role": "user", "content": "x", "timestamp": "2026-09-01T10:00:00Z"},
        {"role": "assistant", "content": "y", "timestamp": "2026-09-01T10:00:02Z", "model": "claude-opus-5", "metadata": {"usage": {"input_tokens": 300, "output_tokens": 25, "cache_read_input_tokens": 100}}},
    ]}))


def run():
    shutil.rmtree(OUT, ignore_errors=True)
    cmd = [sys.executable, SCANNER, "scan", "--host", "fixture", "--out-dir", OUT,
           "--claude-root", os.path.join(FX, "claude"), "--codex-root", os.path.join(FX, "codex"), "--gemini-root", os.path.join(FX, "gemini"),
           "--cline-root", "cline=" + os.path.join(FX, "cline"), "--aider-root", os.path.join(FX, "aider"), "--kimi-root", os.path.join(FX, "kimi"),
           "--vibe-root", os.path.join(FX, "vibe"), "--continue-root", os.path.join(FX, "continue"), "--pi-root", os.path.join(FX, "pi"),
           "--generic-root", "codebuff=" + os.path.join(FX, "generic")]
    subprocess.run(cmd, check=True)
    tot = {}
    for line in open(os.path.join(OUT, "events.fixture.jsonl"), encoding="utf-8"):
        e = json.loads(line)
        t = tot.setdefault(e["tool"], {"calls": 0, "total": 0, "in": 0, "cr": 0, "cw": 0, "out": 0})
        t["calls"] += 1
        t["total"] += e["total"]
        t["in"] += e["input_uncached"]
        t["cr"] += e["cache_read"]
        t["cw"] += e["cache_write"]
        t["out"] += e["output"]
    expect = {
        "claude-code": {"calls": 1, "in": 10, "cr": 1000, "cw": 200, "out": 50},
        "codex": {"calls": 3, "in": 300, "cr": 1900, "out": 230},          # 2 parent + 1 real child call; replay dropped
        "gemini-cli": {"calls": 1, "in": 200, "cr": 300, "out": 60},
        "cline": {"calls": 1, "in": 800, "cr": 700, "cw": 100, "out": 60},
        "aider": {"calls": 2, "in": 39228, "out": 147},
        "kimi": {"calls": 1, "in": 100, "cr": 900, "cw": 50, "out": 40},
        "mistral-vibe": {"calls": 1, "in": 5000, "out": 300},
        "continue": {"calls": 1, "in": 1200, "out": 80},
        "pi": {"calls": 1, "in": 20, "cr": 400, "out": 10},
        "codebuff": {"calls": 1, "in": 300, "cr": 100, "out": 25},
    }
    ok = True
    for tool, exp in expect.items():
        got = tot.get(tool)
        bad = [k for k, v in exp.items() if not got or got.get(k) != v]
        print("%-13s %s %s" % (tool, "OK " if not bad else "FAIL", json.dumps(got) if got else "no events"), "" if not bad else "expected %s" % json.dumps(exp))
        ok = ok and not bad
    inv = json.load(open(os.path.join(OUT, "inventory.fixture.json"), encoding="utf-8"))
    print("replay skipped:", inv["codex_replay_skipped"], "(expect 2)")
    ok = ok and inv["codex_replay_skipped"] == 2
    per_root = all(r.get("files", 0) >= 1 and r.get("bytes", 0) > 0 and "errors" in r for r in inv["roots"])
    print("per-root inventory counts (files, bytes, errors):", "OK" if per_root else "MISSING", [(r["tool"], r.get("files")) for r in inv["roots"]])
    ok = ok and per_root
    print("ALL OK" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    build()
    sys.exit(run())
