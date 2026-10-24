"""Synthetic schema-17 Goose records. No installation, credentials or provider calls."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

STAMP = int(datetime(2026, 10, 12, 12, tzinfo=timezone.utc).timestamp())
PRIVATE = "SYNTHETIC_PROMPT_MUST_NOT_BE_COLLECTED"


def database(path, version=17, wal=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    if wal:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA wal_autocheckpoint=0")
    conn.executescript('''
        CREATE TABLE schema_version(version INTEGER PRIMARY KEY);
        CREATE TABLE sessions(
            id TEXT PRIMARY KEY, created_at TEXT, provider_name TEXT, model_config_json TEXT,
            accumulated_input_tokens INTEGER DEFAULT 0, accumulated_output_tokens INTEGER DEFAULT 0,
            accumulated_total_tokens INTEGER DEFAULT 0, accumulated_cache_read_tokens INTEGER DEFAULT 0,
            accumulated_cache_write_tokens INTEGER DEFAULT 0, accumulated_cost REAL,
            name TEXT, working_dir TEXT, extension_data TEXT);
        CREATE TABLE usage_ledger(
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL REFERENCES sessions(id),
            created_timestamp INTEGER NOT NULL, model TEXT,
            input_tokens INTEGER, output_tokens INTEGER, total_tokens INTEGER,
            cache_read_tokens INTEGER, cache_write_tokens INTEGER, cost REAL, cost_source TEXT,
            is_compaction INTEGER DEFAULT 0);
        CREATE TABLE messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT, message_id TEXT, session_id TEXT NOT NULL,
            role TEXT NOT NULL, content_json TEXT NOT NULL, created_timestamp INTEGER,
            metadata_json TEXT);
    ''')
    conn.execute("INSERT INTO schema_version VALUES (?)", (version,))
    conn.commit()
    return conn


def invocation(conn, sid="20261012_1", model="synthetic-model-a", provider="synthetic-provider-a",
               input_tokens=1000, output_tokens=50, cache_read=200, cache_write=100,
               cost=0.012, cost_source="estimated", compaction=False, timestamp=STAMP,
               message=True, commit=True):
    total = (input_tokens or 0) + (output_tokens or 0)
    conn.execute("INSERT OR IGNORE INTO sessions(id, created_at, name, working_dir, extension_data) VALUES (?, ?, ?, ?, ?)",
                 (sid, "2026-10-12T12:00:00Z", PRIVATE, "/synthetic/private", PRIVATE))
    conn.execute("UPDATE sessions SET provider_name=?, model_config_json=? WHERE id=?",
                 (provider, json.dumps({"model_name": model}), sid))
    cur = conn.execute("INSERT INTO usage_ledger(session_id, created_timestamp, model, input_tokens, output_tokens, total_tokens, cache_read_tokens, cache_write_tokens, cost, cost_source, is_compaction) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                       (sid, timestamp, model, input_tokens, output_tokens, total, cache_read, cache_write, cost, cost_source, int(compaction)))
    uid = cur.lastrowid
    conn.execute("UPDATE sessions SET accumulated_input_tokens=accumulated_input_tokens+?, accumulated_output_tokens=accumulated_output_tokens+?, accumulated_total_tokens=accumulated_total_tokens+?, accumulated_cache_read_tokens=accumulated_cache_read_tokens+?, accumulated_cache_write_tokens=accumulated_cache_write_tokens+?, accumulated_cost=COALESCE(accumulated_cost,0)+? WHERE id=?",
                 (input_tokens or 0, output_tokens or 0, total, cache_read or 0, cache_write or 0, cost or 0, sid))
    if message and not compaction and cost_source != "carried_forward":
        usage = dict(zip(("inputTokens", "outputTokens", "totalTokens", "cacheReadTokens", "cacheWriteTokens"),
                         (input_tokens, output_tokens, total, cache_read, cache_write)))
        usage.update(cost=cost, costSource=cost_source)
        metadata = {"inference": {"provider": provider, "requestedModel": model, "resolvedModel": model},
                    "usage": usage, "operations": {"secret": PRIVATE}}
        conn.execute("INSERT INTO messages(message_id, session_id, role, content_json, created_timestamp, metadata_json) VALUES(?,?,?,?,?,?)",
                     ("msg-" + str(uid), sid, "assistant", json.dumps({"text": PRIVATE}), timestamp, json.dumps(metadata)))
    if commit:
        conn.commit()
    return uid


def export_header(sid="20261012_1", total=1050):
    return {"id": sid, "created_at": "2026-10-12T12:00:00Z", "extension_data": {}, "message_count": 2,
            "accumulated_usage": {"input_tokens": total - 50, "output_tokens": 50, "total_tokens": total}}


def pricing():
    # Test-only rates, NOT claims about any marketed model's prices.
    return {"models": {model: {"input": 2, "output": 10, "cache_read": 0.2, "cache_write_5m": 2.5, "cache_write_1h": 4}
                       for model in ("synthetic-model-a", "synthetic-model-b")}}
