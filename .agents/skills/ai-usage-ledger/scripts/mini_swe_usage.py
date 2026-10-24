"""Usage-only mini-SWE-agent records and a read-only, standard-library collector.

No mini-SWE-agent import is required to scan. Counts are provider evidence, not
inferred from conversation text, cost, model statistics, or request attempts.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

SCHEMA = "mini-swe-agent-usage-1"
TRAJECTORY = "mini-swe-agent-1.1"
TOOL = "mini-swe-agent"
MAX_FILE = 128 * 1024 * 1024
MAX_LINE = 1024 * 1024
MAX_COUNT = (2**63 - 1) // 8
IDENTIFIER = re.compile(r"[A-Za-z0-9_./:@+ -]{1,256}\Z")
STATES = {"response_received", "completed", "format_error", "cost_error", "cancelled", "post_response_error", "unknown"}
COUNT_PATHS = (
    "prompt_tokens", "completion_tokens", "input_tokens", "output_tokens", "total_tokens",
    "cache_read_input_tokens", "cache_creation_input_tokens", "reasoning_tokens",
    "prompt_tokens_details.cached_tokens", "prompt_tokens_details.cache_write_tokens",
    "prompt_tokens_details.cache_creation_tokens", "completion_tokens_details.reasoning_tokens",
    "input_tokens_details.cached_tokens", "input_tokens_details.cache_write_tokens",
    "output_tokens_details.reasoning_tokens", "cache_creation.ephemeral_5m_input_tokens",
    "cache_creation.ephemeral_1h_input_tokens",
    "prompt_tokens_details.cache_creation_token_details.ephemeral_5m_input_tokens",
    "prompt_tokens_details.cache_creation_token_details.ephemeral_1h_input_tokens",
)
COST_PATHS = ("cost", "cost_details.upstream_inference_cost")


def get(value: Any, path: str, default: Any = None) -> Any:
    for part in path.split("."):
        value = value.get(part) if isinstance(value, dict) else getattr(value, part, None)
        if value is None:
            return default
    return value


def count(value: Any) -> int | None:
    return value if type(value) is int and 0 <= value <= MAX_COUNT else None


def money(value: Any) -> float | None:
    if type(value) not in (int, float):
        return None
    try:
        return float(value) if math.isfinite(value) and value >= 0 else None
    except (OverflowError, ValueError):
        return None


def identifier(value: Any) -> str | None:
    return value if isinstance(value, str) and IDENTIFIER.fullmatch(value) else None


def timestamp(value: Any) -> str | None:
    try:
        if type(value) in (float, int):
            return datetime.fromtimestamp(value, timezone.utc).isoformat()
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc).isoformat() if parsed.tzinfo else None
    except (ValueError, OverflowError, OSError):
        pass
    return None


def digest(*parts: Any) -> str:
    return hashlib.sha256(json.dumps(parts, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def backend_name(value: str) -> str:
    lower = str(value).lower()
    for name in ("openrouter", "portkey", "requesty", "litellm"):
        if name in lower:
            return name
    return "custom"


def provider_name(backend: str, model: str | None, override: str | None = None) -> str:
    if identifier(override):
        return override
    family = backend_name(backend)
    if family in ("openrouter", "portkey", "requesty"):
        return family
    prefix = (model or "").partition("/")[0]
    if family == "litellm" and "/" in (model or ""):
        return identifier(prefix) or "unknown"
    return "unknown"


def usage_snapshot(response: Any, *, backend: str = "custom", requested_model: str | None = None,
                   provider: str | None = None, observed_at: Any = None) -> dict | None:
    """Copy only explicitly allowlisted fields, before a backend can mutate usage."""
    usage = get(response, "usage")
    if usage is None:
        return None
    fields: dict[str, Any] = {}
    invalid = []
    for path in COUNT_PATHS + COST_PATHS:
        raw = get(usage, path)
        if raw is None:
            continue
        valid = count(raw) if path in COUNT_PATHS else money(raw)
        if valid is None:
            invalid.append(path)
            continue
        target = fields
        parts = path.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = valid
    if not any(get(fields, path) is not None for path in COUNT_PATHS):
        return None  # cost-only and network errors are not token evidence
    model = identifier(get(response, "model"))
    created = timestamp(get(response, "created") or get(response, "created_at"))
    return {
        "schema": SCHEMA, "backend": identifier(backend) or "custom", "usage": fields,
        "source_request_id": identifier(get(response, "id")), "model": model,
        "upstream_provider": identifier(get(response, "provider")),
        "requested_model": identifier(requested_model),
        "provider": provider_name(backend, requested_model or model, provider),
        "timestamp": created or timestamp(observed_at),
        "timestamp_provenance": "provider" if created else "observation" if timestamp(observed_at) else "missing",
        "status": "response_received", "invalid_usage_fields": invalid,
    }


def sanitize_snapshot(raw: dict) -> dict | None:
    snap = usage_snapshot({"usage": raw.get("usage"), "id": raw.get("source_request_id"), "model": raw.get("model")},
                          backend=raw.get("backend", "custom"), requested_model=raw.get("requested_model"),
                          provider=raw.get("provider"), observed_at=raw.get("timestamp"))
    if snap is None:
        return None
    for key in ("invocation_id", "session_id", "run_id", "agent_id", "mini_version", "backend_library_version", "upstream_provider"):
        snap[key] = identifier(raw.get(key))
    snap["calculated_cost"] = money(raw.get("calculated_cost"))
    snap["status"] = raw.get("status") if isinstance(raw.get("status"), str) and raw.get("status") in STATES else "unknown"
    snap["timestamp_provenance"] = raw.get("timestamp_provenance") if isinstance(raw.get("timestamp_provenance"), str) and raw.get("timestamp_provenance") in (
        "provider", "observation", "message", "missing") else "missing"
    snap["invalid_usage_fields"] = sorted(set(snap["invalid_usage_fields"]) | {
        v for v in raw.get("invalid_usage_fields", []) if isinstance(v, str) and v in COUNT_PATHS + COST_PATHS
    }) if isinstance(raw.get("invalid_usage_fields", []), list) else snap["invalid_usage_fields"]
    return snap


def is_source(value: Any) -> bool:
    return isinstance(value, dict) and (str(value.get("trajectory_format", "")).startswith("mini-swe-agent-")
                                       or value.get("schema") == SCHEMA)


def records(document: Any, path: Path) -> Iterator[dict]:
    """Never recursively sniff arbitrary messages/configuration for usage."""
    if not isinstance(document, dict):
        return
    if document.get("schema") == SCHEMA:
        if snap := sanitize_snapshot(document):
            yield snap
        return
    if document.get("trajectory_format") != TRAJECTORY:
        return
    config = get(document, "info.config.model", {})
    backend = identifier(get(document, "info.config.model_type")) or "custom"
    requested = identifier(get(config, "model_name"))
    messages = document.get("messages")
    if not isinstance(messages, list):
        return
    # With no native session ID, path-scoping is deliberately conservative. Never
    # collapse independent no-ID/no-time runs merely because their counts match.
    session = identifier(get(document, "info.session_id")) or "path-" + digest(str(path.resolve()))
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            continue
        extra = message.get("extra") if isinstance(message.get("extra"), dict) else {}
        exported = extra.get("mini_swe_usage")
        if isinstance(exported, dict) and exported.get("schema") == SCHEMA:
            if snap := sanitize_snapshot(exported):
                snap["ordinal"] = index
                yield snap
                continue
        response = extra.get("response")
        if not isinstance(response, dict):
            response = message if message.get("object") == "response" or message.get("role") == "assistant" else None
        if response is None:
            continue
        call_model = identifier(message.get("model_name")) or requested
        configured_kwargs = get(config, "model_kwargs", {})
        provider = None
        if backend_name(backend) == "litellm" and isinstance(configured_kwargs, dict) and any(
                key in configured_kwargs for key in ("api_base", "base_url")):
            provider = "openai-compatible" if (call_model or "").startswith("openai/") else "custom-endpoint"
        snap = usage_snapshot(response, backend=backend, requested_model=call_model, provider=provider, observed_at=extra.get("timestamp"))
        if snap is None:
            continue
        snap.update(session_id=session, ordinal=index, calculated_cost=money(extra.get("cost")),
                    mini_version=identifier(get(document, "info.mini_version")))
        snap["status"] = "format_error" if extra.get("interrupt_type") == "FormatError" else "completed"
        if snap["timestamp_provenance"] == "observation":
            snap["timestamp_provenance"] = "message"
        yield snap


def normalize(snap: dict, host: str, path: Path) -> dict:
    u = snap["usage"]
    warnings = ["invalid:" + p for p in snap.get("invalid_usage_fields", [])]

    def first(*paths: str) -> int | None:
        return next((get(u, p) for p in paths if get(u, p) is not None), None)

    prompt = first("prompt_tokens", "input_tokens")
    output = first("completion_tokens", "output_tokens")
    cr = first("prompt_tokens_details.cached_tokens", "input_tokens_details.cached_tokens", "cache_read_input_tokens") or 0
    cw = first("prompt_tokens_details.cache_write_tokens", "input_tokens_details.cache_write_tokens",
               "prompt_tokens_details.cache_creation_tokens", "cache_creation_input_tokens") or 0
    cw5 = first("cache_creation.ephemeral_5m_input_tokens", "prompt_tokens_details.cache_creation_token_details.ephemeral_5m_input_tokens")
    cw1 = first("cache_creation.ephemeral_1h_input_tokens", "prompt_tokens_details.cache_creation_token_details.ephemeral_1h_input_tokens")
    if not cw and (cw5 is not None or cw1 is not None):
        cw = (cw5 or 0) + (cw1 or 0)
    reasoning = first("completion_tokens_details.reasoning_tokens", "output_tokens_details.reasoning_tokens", "reasoning_tokens") or 0
    # Native Anthropic input is uncached. Verified modern LiteLLM and OpenAI-
    # compatible/Responses usage includes cache categories in prompt/input.
    native = "input_tokens" in u and "prompt_tokens" not in u and (
        "cache_read_input_tokens" in u or "cache_creation_input_tokens" in u) and not (
            "input_tokens_details" in u or "response" in snap.get("backend", "").lower())
    input_value = prompt or 0
    if not native and prompt is not None:
        if cr + cw > prompt:
            warnings.append("cache_categories_exceed_input")
            # Do not invent a negative count or inflate the reliable prompt total.
            # Preserve conflicting raw categories as evidence; do not price them.
            cr = cw = 0
        input_value = prompt - cr - cw
    if output is not None and reasoning > output:
        warnings.append("reasoning_exceeds_output")
        reasoning = 0
    total = input_value + cr + cw + (output or 0)
    reported = first("total_tokens")
    missing = [name for name, value in (("input", prompt), ("output", output)) if value is None]
    if reported is not None and reported != total:
        warnings.append("reported_total_differs_from_components")
    if (cw5 is not None or cw1 is not None) and (cw5 or 0) + (cw1 or 0) != cw:
        warnings.append("cache_write_breakdown_differs")
        cw5 = cw1 = None
    unclassified = 0
    if missing and reported is not None and reported >= total:
        unclassified = reported - total
        total = reported
    source_id = snap.get("source_request_id")
    invocation = snap.get("invocation_id")
    model = snap.get("model") or snap.get("requested_model") or "unknown"
    provider = snap.get("provider") or "unknown"
    if source_id:
        # A routing alias is not the observed provider: independent providers
        # may return identical response IDs for the same model.
        identity_provider = snap.get("upstream_provider") or provider
        identity = ("provider", identity_provider, model, source_id)
        identity_kind = "provider_response_id"
    elif invocation:
        identity = ("invocation", invocation)
        identity_kind = "export_invocation_id"
    else:
        identity = ("path", str(path.resolve()), snap.get("session_id"), snap.get("ordinal", 0),
                    snap.get("timestamp"), model, u)
        identity_kind = "path_and_ordinal"
    ts = snap.get("timestamp")
    provider_cost = money(get(u, "cost"))
    calculated = money(snap.get("calculated_cost"))
    e = {
        "tool": TOOL, "host": host, "session": snap.get("session_id") or "unknown", "ts": ts,
        "date": ts[:10] if ts else None, "model": model, "provider": provider,
        "input_uncached": input_value, "cache_read": cr, "cache_write": cw,
        "output": output or 0, "reasoning": reasoning, "total": total, "unclassified_tokens": unclassified,
        "partial": bool(missing or warnings),
        "request_id": "mini-swe:" + digest(*identity), "identity_provenance": identity_kind,
        "source_request_id": source_id, "invocation_id": invocation,
        "run_id": snap.get("run_id"), "agent_id": snap.get("agent_id"),
        "requested_model": snap.get("requested_model"), "model_provenance": "response" if snap.get("model") else "configuration_fallback",
        "backend": snap.get("backend"), "version": snap.get("mini_version"),
        "backend_library_version": snap.get("backend_library_version"), "upstream_provider": snap.get("upstream_provider"),
        "execution_status": snap.get("status", "unknown"),
        "timestamp_provenance": snap.get("timestamp_provenance", "missing"),
        "cost_usd": calculated, "source_calculated_cost": calculated,
        "provider_reported_cost": provider_cost, "provider_cost_provenance": "response.usage.cost" if provider_cost is not None else "unavailable",
        "upstream_inference_cost": money(get(u, "cost_details.upstream_inference_cost")),
        "cost_provenance": "mini_calculated_or_fallback" if calculated is not None else "unavailable",
        "reported_usage": u, "reported_total_tokens": reported,
        "total_provenance": "reported_with_unclassified_tokens" if unclassified else "sum_available_components_partial" if missing else "sum_components",
        "input_semantics": "uncached" if native else "cache_inclusive",
        "missing_usage_fields": missing, "usage_warnings": warnings,
        "kind": "main", "entrypoint": TOOL, "granularity": "provider_response", "src": str(path),
    }
    if cw5 is not None or cw1 is not None:
        e.update(cache_write_5m=cw5 or 0, cache_write_1h=cw1 or 0)
    return e


def source_paths(root: str) -> Iterator[Path]:
    base = Path(root).expanduser()
    if base.is_symlink():
        raise ValueError("mini-SWE source root must not be a symlink")
    if base.is_file():
        yield base
        return
    for directory, dirs, files in os.walk(base, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not Path(directory, d).is_symlink() and not d.startswith("."))
        for name in sorted(files):
            path = Path(directory, name)
            if not path.is_symlink() and name.endswith((".traj.json", ".usage.json", ".usage.jsonl")):
                yield path


def scan(root: str, host: str, out: Any, stats: Any, session_meta: list, seen: set) -> None:
    sessions = {}
    for path in source_paths(root):
        if path.is_symlink():
            continue
        try:
            size = path.stat().st_size
            if size > MAX_FILE:
                stats.errors += 1
                continue
            stats.files += 1
            stats.bytes += size
            with path.open(encoding="utf-8") as stream:
                if path.suffix == ".jsonl":
                    documents = []
                    for raw in stream:
                        stats.lines += 1
                        if len(raw) > MAX_LINE:
                            stats.errors += 1
                            continue
                        try:
                            documents.append(json.loads(raw))
                        except (ValueError, RecursionError):
                            stats.errors += 1
                else:
                    stats.lines += 1
                    documents = [json.load(stream)]
            for document in documents:
                for snap in records(document, path):
                    e = normalize(snap, host, path)
                    if e["request_id"] in seen:
                        stats.dedup += 1
                        continue
                    seen.add(e["request_id"])
                    out.write(json.dumps(e, allow_nan=False) + "\n")
                    stats.events += 1
                    session = sessions.setdefault(e["session"], {"tool": TOOL, "host": host, "session": e["session"],
                        "file": str(root), "calls": 0, "kind": "main", "model": e["model"], "first_ts": None, "last_ts": None})
                    session["calls"] += 1
                    if session["model"] != e["model"]:
                        session["model"] = None
                    if e["ts"]:
                        session["first_ts"] = min(session["first_ts"] or e["ts"], e["ts"])
                        session["last_ts"] = max(session["last_ts"] or e["ts"], e["ts"])
        except (OSError, ValueError, TypeError, RecursionError, AttributeError):
            stats.errors += 1
    session_meta.extend(sessions.values())
