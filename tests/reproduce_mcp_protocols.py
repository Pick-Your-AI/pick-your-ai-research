"""Opt-in MCP SDK stdio observation using only a synthetic echo peer.

This script is outside normal unittest discovery. It does not install packages,
contact a remote MCP endpoint, authenticate, or qualify a catalog server. Supply
isolated Python environments with the versions recorded in the companion note.
"""

import argparse
import asyncio
import ctypes
from datetime import datetime, timedelta, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys


SELF = Path(__file__).resolve()
SYNTHETIC_TEXT = "pyai-synthetic-protocol-probe"
SDK_VERSIONS = {"v1": "1.30.0", "v2": "2.3.0"}
CASES = (("v1", "v1", "legacy", "2025-11-25"),
         ("v1", "v2", "legacy", "2025-11-25"),
         ("v2", "v1", "auto", "2025-11-25"),
         ("v2", "v2", "auto", "2026-07-28"),
         ("v2", "v2", "legacy", "2025-11-25"),
         ("v2", "v1", "2026-07-28", None))


def clean_environment(python):
    return {
        "PATH": str(Path(python).absolute().parent),
        "LC_ALL": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUNBUFFERED": "1",
    }


def require_sdk(generation):
    actual = version("mcp")
    if actual != SDK_VERSIONS[generation]:
        raise ValueError("The selected Python environment has the wrong SDK version")
    if generation == "v2" and version("mcp-types") != "2.3.0":
        raise ValueError("The selected Python environment has the wrong wire-type version")
    return actual


def matches_expected(row, case):
    """A worker's successful exit alone is not a successful protocol exchange."""
    client, server, mode, protocol = case
    if any(row.get(key) != value for key, value in {
        "client_sdk": SDK_VERSIONS[client], "server_sdk": SDK_VERSIONS[server],
        "mode": mode, "transport": "stdio", "worker_exit_code": 0,
        "worker_stderr_bytes": 0,
    }.items()):
        return False
    if protocol is None:
        return (row.get("status") == "failed" and "protocol_version" not in row
                and row.get("errors") == [{"type": "MCPError", "code": -32602}]
                and "tools" not in row and "echo" not in row)
    return (row.get("status") == "passed" and row.get("protocol_version") == protocol
            and row.get("tools") == ["synthetic_echo"] and "errors" not in row
            and row.get("echo") == {"echo": SYNTHETIC_TEXT, "server_sdk": SDK_VERSIONS[server]})


def bind_parent_lifetime(expected_parent):
    """Stop this fixed Linux peer even when the SDK gives it a new session."""
    if sys.platform != "linux":
        raise RuntimeError("The observer requires Linux parent-death cleanup")
    if (type(expected_parent) is not int or expected_parent <= 0
            or os.getppid() != expected_parent):
        raise RuntimeError("The expected probe parent is no longer present")
    prctl = ctypes.CDLL(None, use_errno=True).prctl
    prctl.argtypes = [ctypes.c_int] + [ctypes.c_ulong] * 4
    prctl.restype = ctypes.c_int
    if prctl(1, int(signal.SIGKILL), 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
        raise OSError(ctypes.get_errno(), "Cannot bind the probe's parent lifetime")
    # Parent death before prctl is not retroactive; close that setup race.
    if os.getppid() != expected_parent:
        raise RuntimeError("The expected probe parent exited during setup")


def serve(generation, parent_pid):
    bind_parent_lifetime(parent_pid)
    actual = require_sdk(generation)
    if generation == "v1":
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("pyai-synthetic-stdio-peer", log_level="ERROR")
    else:
        from mcp.server import MCPServer
        server = MCPServer("pyai-synthetic-stdio-peer", log_level="ERROR")

    @server.tool()
    def synthetic_echo(text: str) -> str:
        """Return this synthetic value and the actual peer's installed SDK version."""
        if text != SYNTHETIC_TEXT:
            raise ValueError("Only the fixed synthetic probe input is accepted")
        return json.dumps({"echo": text, "server_sdk": actual}, sort_keys=True)

    server.run(transport="stdio")


async def probe(client_generation, server_generation, server_python, mode):
    client_sdk = require_sdk(client_generation)
    from mcp import StdioServerParameters
    from mcp.client.stdio import stdio_client

    parameters = StdioServerParameters(
        command=server_python,
        args=["-I", str(SELF), "--serve", server_generation, "--parent-pid", str(os.getpid())],
        env=clean_environment(server_python),
    )
    row = {"client_sdk": client_sdk, "server_sdk": SDK_VERSIONS[server_generation],
           "transport": "stdio", "mode": mode, "status": "failed"}
    try:
        if client_generation == "v1":
            from mcp import ClientSession
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=5)) as client:
                    initialized = await client.initialize()
                    row["protocol_version"] = initialized.protocolVersion
                    listing = await client.list_tools()
                    result = await client.call_tool("synthetic_echo", {"text": SYNTHETIC_TEXT})
        else:
            from mcp import Client
            async with Client(parameters, mode=mode, read_timeout_seconds=5) as client:
                listing = await client.list_tools()
                result = await client.call_tool("synthetic_echo", {"text": SYNTHETIC_TEXT})
                # A pinned modern Client can adopt a version without negotiation.
                # Record it only after the real peer has answered both operations.
                row["protocol_version"] = client.protocol_version
        names = [tool.name for tool in listing.tools]
        if names != ["synthetic_echo"]:
            raise ValueError("Unexpected synthetic peer tool list")
        is_error = getattr(result, "is_error", getattr(result, "isError", None))
        if is_error is not False or len(result.content) != 1:
            raise ValueError("Unexpected synthetic peer result shape")
        answer = json.loads(result.content[0].text)
        if answer != {"echo": SYNTHETIC_TEXT, "server_sdk": SDK_VERSIONS[server_generation]}:
            raise ValueError("Synthetic peer identity or echo differs")
        row.update(status="passed", tools=names, echo=answer)
    except Exception as error:
        def errors(exc):
            if isinstance(exc, BaseExceptionGroup):
                return [item for child in exc.exceptions for item in errors(child)]
            result = {"type": type(exc).__name__}
            code = getattr(exc, "code", None)
            if code is None:
                code = getattr(getattr(exc, "error", None), "code", None)
            if type(code) is int:
                result["code"] = code
            return [result]
        row["errors"] = errors(error)
    return row


def run_worker(command, environment, timeout=20):
    """Bound an isolated Linux worker and its inherited process group.

    Do not drain inherited pipes again after a timeout: a peer may still hold
    them open. The SDK's separate-session synthetic peer also binds its own
    parent lifetime before loading the SDK; arbitrary process trees are not
    supported by this helper.
    """
    if sys.platform != "linux":
        raise RuntimeError("The observer requires Linux parent-death cleanup")
    worker = subprocess.Popen(command, env=environment, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, start_new_session=True)
    try:
        stdout, stderr = worker.communicate(timeout=timeout)
        return subprocess.CompletedProcess(command, worker.returncode, stdout, stderr)
    except BaseException:
        # The fresh session gives this invocation its own group, even if its
        # leader exited without yet being reaped. Never signal a recycled group
        # after communicate() has already reaped the leader on a normal path.
        if worker.returncode is None:
            try:
                os.killpg(worker.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            worker.wait(timeout=5)
        raise
    finally:
        worker.stdout.close()
        worker.stderr.close()


def observe(v1_python, v2_python):
    interpreters = {"v1": str(Path(v1_python).absolute()), "v2": str(Path(v2_python).absolute())}
    rows = []
    for case in CASES:
        client, server, mode, _ = case
        command = [interpreters[client], "-I", str(SELF), "--probe", client, server,
                   interpreters[server], mode, "--parent-pid", str(os.getpid())]
        result = run_worker(command, clean_environment(interpreters[client]))
        if result.returncode != 0:
            raise RuntimeError("A probe worker failed before recording an observation")
        row = json.loads(result.stdout)
        row["worker_exit_code"] = result.returncode
        row["worker_stderr_bytes"] = len(result.stderr.encode("utf-8"))
        row["matches_expected"] = matches_expected(row, case)
        rows.append(row)
    return {"observed_utc": datetime.now(timezone.utc).isoformat(),
            "controller_python": platform.python_version(), "platform": platform.system(),
            "machine": platform.machine(), "scope": "synthetic-local-SDK-stdio-peers",
            "script_sha256": hashlib.sha256(SELF.read_bytes()).hexdigest(),
            "expectations_satisfied": all(row["matches_expected"] for row in rows),
            "observations": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--serve", choices=SDK_VERSIONS)
    mode.add_argument("--probe", nargs=4, metavar=("CLIENT", "SERVER", "SERVER_PYTHON", "MODE"))
    mode.add_argument("--observe", nargs=2, metavar=("V1_PYTHON", "V2_PYTHON"))
    parser.add_argument("--parent-pid", type=int, help="exact parent PID for an owned worker or peer")
    args = parser.parse_args()
    if args.serve:
        serve(args.serve, args.parent_pid)
    elif args.probe:
        bind_parent_lifetime(args.parent_pid)
        print(json.dumps(asyncio.run(probe(*args.probe)), sort_keys=True))
    else:
        result = observe(*args.observe)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["expectations_satisfied"] else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
