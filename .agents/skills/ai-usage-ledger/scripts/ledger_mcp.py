#!/usr/bin/env python3
"""Local stdio MCP reporting for approved Muse sources; no optional runtime packages.

Implements the tools-only legacy handshake used by the pinned Muse MCP client
(2024-11-05 through 2025-11-25). No HTTP listener, shell, SQL or file-access tools.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
import sqlite3
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import muse_usage  # noqa: E402

VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
MAX_MESSAGE = 65536
REPORTS = {
    "ledger_status": "Availability and recorded attempt count for approved Muse sources (no paths).",
    "ledger_usage_summary": "Observed token totals and missing-usage coverage for approved Muse sources.",
    "ledger_usage_by_model": "Observed usage grouped by response model, not just the configured model.",
    "ledger_usage_by_provider": "Observed usage grouped by the operator's provider attribution.",
    "ledger_usage_by_session": "Observed usage grouped by source session identity (pseudonymous by default).",
    "ledger_cost_breakdown": "Existing ledger list-price estimates, provenance and separate gateway-reported charges.",
}
FILTERS = {key: {"type": "string", "maxLength": 256} for key in ("model", "provider", "session")}
FILTERS.update({key: {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"} for key in ("since", "until")})
FILTERS["limit"] = {"type": "integer", "minimum": 1, "maximum": 500, "default": 100}


def result(value, error=False):
    return {"content": [{"type": "text", "text": json.dumps(value, sort_keys=True, allow_nan=False)}], "isError": error}


def tools(config):
    muse_usage.authorize(config, "reporting")
    output = []
    for name, description in REPORTS.items():
        output.append({"name": name, "description": description,
                       "inputSchema": {"type": "object", "properties": {} if name == "ledger_status" else FILTERS,
                                       "additionalProperties": False},
                       "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}})
    if config["muse_mesh"].get("allow_scan") is True:
        try:
            muse_usage.authorize(config, "collection")
            output.append({"name": "ledger_scan_sources", "description": "Import only already approved local Muse usage directories.",
                           "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
                           "annotations": {"readOnlyHint": False, "destructiveHint": False,
                                           "idempotentHint": True, "openWorldHint": False}})
        except PermissionError:
            pass
    return output


class Server:
    def __init__(self, config):
        self.config = config
        self.initializing = False
        self.initialized = False
        self.calls = deque()

    def handle(self, message):
        """A single bounded request. Errors never echo paths, SQL, data or exceptions."""
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
        identity = message.get("id")
        has_id = "id" in message
        if has_id and (type(identity) not in (str, int) or (isinstance(identity, str) and len(identity) > 256)):
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request ID"}}
        method = message.get("method")
        params = message.get("params", {})
        if not isinstance(method, str) or not isinstance(params, dict):
            return self.error(identity, -32600, "Invalid request") if has_id else None
        if not has_id:
            if method == "notifications/initialized" and self.initializing:
                self.initialized = True
            return None
        if method == "initialize":
            if self.initializing:
                return self.error(identity, -32600, "Already initialized")
            requested = params.get("protocolVersion")
            if not isinstance(requested, str) or not isinstance(params.get("capabilities", {}), dict):
                return self.error(identity, -32602, "Invalid initialization")
            self.initializing = True
            return self.success(identity, {"protocolVersion": requested if requested in VERSIONS else VERSIONS[0],
                                           "capabilities": {"tools": {"listChanged": False}},
                                           "serverInfo": {"name": "ai-usage-ledger-muse", "version": "1.0.0"}})
        if method == "ping":
            return self.success(identity, {})
        if not self.initialized:
            return self.error(identity, -32600, "Initialization is required")
        if method not in ("tools/list", "tools/call"):
            return self.error(identity, -32601, "Method not found")
        now = time.monotonic()
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()
        if len(self.calls) >= 120:
            return self.error(identity, -32000, "Request limit exceeded")
        self.calls.append(now)
        try:
            # Reload every time: operator revocation takes effect without restarting.
            config = muse_usage.load_config(self.config)
            available = tools(config)
            if method == "tools/list":
                if params.keys() - {"_meta"}:
                    raise ValueError("unsupported list parameter")
                return self.success(identity, {"tools": available})
            if params.keys() - {"name", "arguments", "_meta"} or not isinstance(params.get("name"), str):
                raise ValueError("invalid tool call")
            name, args = params["name"], params.get("arguments", {})
            if name not in {tool["name"] for tool in available}:
                raise PermissionError("tool is not authorized")
            if name == "ledger_scan_sources":
                if args != {}:
                    raise ValueError("scan does not accept arguments")
                value = muse_usage.scan(config)
            else:
                value = muse_usage.report(config, name, args)
            return self.success(identity, result(value))
        except PermissionError:
            if method == "tools/list":
                return self.success(identity, {"tools": []})
            return self.success(identity, result({"error": "Tool unavailable or operator consent revoked"}, True))
        except (ValueError, KeyError, TypeError):
            return self.success(identity, result({"error": "Invalid input, configuration or conflicting usage evidence; inspect local configuration/source records"}, True))
        except (OSError, sqlite3.Error):
            return self.success(identity, result({"error": "Ledger/source unavailable; retry after the operator restores local storage"}, True))

    @staticmethod
    def success(identity, value):
        return {"jsonrpc": "2.0", "id": identity, "result": value}

    @staticmethod
    def error(identity, code, message):
        return {"jsonrpc": "2.0", "id": identity, "error": {"code": code, "message": message}}


def serve(config, source, destination):
    server = Server(config)
    while True:
        raw = source.readline(MAX_MESSAGE + 1)
        if not raw:
            break
        if len(raw) > MAX_MESSAGE:
            # Terminate rather than allocate or parse an unbounded line.
            response = server.error(None, -32600, "Message too large")
            destination.write(json.dumps(response) + "\n")
            destination.flush()
            return 1
        try:
            message = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
            response = server.handle(message)
        except (ValueError, UnicodeError, RecursionError):
            response = server.error(None, -32700, "Parse error")
        if response is not None:
            destination.write(json.dumps(response, allow_nan=False) + "\n")
            destination.flush()
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=muse_usage.config_path(), help="operator-controlled ledger config, fixed at startup")
    args = ap.parse_args()
    return serve(args.config, sys.stdin.buffer, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
