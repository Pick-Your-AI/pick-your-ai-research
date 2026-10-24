"""Opt-in native custom-model extension; never imported by the core scanner.

Configure model_class=mini_swe_export.UsageModel and usage_export_dir explicitly.
This subclasses the chosen adapter, rather than monkey-patching provider clients.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
import time
import uuid
from importlib.metadata import PackageNotFoundError, version
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from mini_swe_usage import identifier, money, usage_snapshot

logger = logging.getLogger(__name__)
_ACTIVE: ContextVar[dict | None] = ContextVar("mini_swe_usage_call", default=None)


def write_snapshot(directory: Path, record: dict) -> None:
    """One private file per invocation, atomically replaced as status settles."""
    invocation = record["invocation_id"]
    if not isinstance(invocation, str) or len(invocation) != 32 or any(c not in "0123456789abcdef" for c in invocation):
        raise ValueError("invalid usage invocation identity")
    if directory.is_symlink():
        raise OSError("usage directory became a symlink")
    fd, temp = tempfile.mkstemp(prefix=".usage-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(record, stream, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, directory / (invocation + ".usage.json"))
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def usage_model(base: type) -> type:
    """Public composition helper for custom classes and deterministic tests."""
    if issubclass(base, UsageMixin):
        raise ValueError("cannot wrap an already instrumented model")
    return type("Usage" + base.__name__, (UsageMixin, base), {"__module__": __name__})


class UsageModel:
    def __new__(cls, *, wrapped_model_class: str = "litellm", **kwargs: Any) -> Any:
        from minisweagent.models import get_model_class
        base = get_model_class(kwargs.get("model_name", ""), wrapped_model_class)
        return usage_model(base)(**kwargs)


class UsageMixin:
    def __init__(self, *, usage_export_dir: str | None = None, usage_session_id: str | None = None,
                 usage_run_id: str | None = None, usage_agent_id: str | None = None,
                 usage_provider: str | None = None, **kwargs: Any):
        self._usage_dir = None
        if usage_export_dir is not None:
            if not usage_export_dir:
                raise ValueError("usage_export_dir must name a dedicated directory")
            directory = Path(usage_export_dir).expanduser().absolute()
            if any(p.is_symlink() for p in (directory, *directory.parents)):
                raise ValueError("usage_export_dir must not traverse symlinks")
            if directory.exists() and not directory.is_dir():
                raise ValueError("usage_export_dir must be a directory")
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            if os.name != "nt" and directory.stat().st_mode & 0o077:
                raise ValueError("usage_export_dir must be private (mode 0700)")
            self._usage_dir = directory
        self._usage_versions = {}
        if self._usage_dir is not None:
            for package in ("mini-swe-agent", "litellm", "portkey-ai"):
                try:
                    self._usage_versions[package] = version(package)
                except PackageNotFoundError:
                    pass
        self._usage_ids = {}
        for key, value in (("session_id", usage_session_id), ("run_id", usage_run_id), ("agent_id", usage_agent_id)):
            if value is not None and not identifier(value):
                raise ValueError("usage identities must be bounded identifiers")
            self._usage_ids[key] = value
        self._usage_provider = usage_provider
        if usage_provider is not None and not identifier(usage_provider):
            raise ValueError("usage_provider must be a bounded identifier")
        # Neither consumed export options nor any export path enters provider kwargs.
        super().__init__(**kwargs)

    def _persist(self, record: dict) -> None:
        try:
            write_snapshot(self._usage_dir, record)
        except (OSError, TypeError, ValueError):
            # Never let an I/O failure cause the native retry loop to repeat a paid call.
            logger.warning("mini-SWE usage export failed; usage may be incomplete")

    def _capture(self, response: Any) -> None:
        context = _ACTIVE.get()
        if not self._usage_dir or context is None or context["owner"] is not self:
            return
        try:
            base = type(self).__mro__[type(self).__mro__.index(UsageMixin) + 1]
            backend = base.__module__ + "." + base.__name__
            requested = getattr(getattr(self, "config", None), "model_name", None)
            provider = self._usage_provider
            model_kwargs = getattr(getattr(self, "config", None), "model_kwargs", {})
            if provider is None and "litellm" in backend.lower() and isinstance(model_kwargs, dict) and any(
                key in model_kwargs for key in ("api_base", "base_url")):
                provider = "openai-compatible" if (requested or "").startswith("openai/") else "custom-endpoint"
            record = usage_snapshot(response, backend=backend, requested_model=requested, provider=provider, observed_at=time.time())
            if record is None:
                return
            record.update(context["ids"], invocation_id=uuid.uuid4().hex, mini_version=self._usage_versions.get("mini-swe-agent"),
                          backend_library_version=self._usage_versions.get("portkey-ai" if "portkey" in backend.lower() else "litellm")
                          if any(name in backend.lower() for name in ("portkey", "litellm")) else None)
            context["records"].append(record)
            self._persist(record)
        except Exception:
            logger.warning("mini-SWE usage extraction failed; usage may be incomplete")

    def _query(self, *args: Any, **kwargs: Any) -> Any:
        response = super()._query(*args, **kwargs)
        self._capture(response)
        return response

    def _calculate_cost(self, response: Any) -> Any:
        context = _ACTIVE.get()
        if context is not None and context["owner"] is not self:
            context = None
        if context is not None and not context["records"]:
            self._capture(response)  # supported custom adapter that bypasses _query
        try:
            result = super()._calculate_cost(response)
        except BaseException:
            if context is not None:
                context["cost_error"] = True
            raise
        if context is not None and context["records"]:
            context["records"][-1]["calculated_cost"] = money(result.get("cost")) if isinstance(result, dict) else None
        return result

    def query(self, messages: list[dict], **kwargs: Any) -> dict:
        if self._usage_dir is None:
            return super().query(messages, **kwargs)
        prior = next((m.get("extra", {}).get("mini_swe_usage") for m in reversed(messages)
                      if isinstance(m, dict) and isinstance(m.get("extra"), dict)
                      and isinstance(m["extra"].get("mini_swe_usage"), dict)), {})
        run_id = self._usage_ids["run_id"] or identifier(prior.get("run_id")) or uuid.uuid4().hex
        context = {"owner": self, "records": [], "cost_error": False, "ids": {
            "run_id": run_id, "session_id": self._usage_ids["session_id"] or identifier(prior.get("session_id")) or run_id,
            "agent_id": self._usage_ids["agent_id"] or identifier(prior.get("agent_id")) or run_id,
        }}
        token = _ACTIVE.set(context)
        status, result, error = "post_response_error", None, None
        try:
            result = super().query(messages, **kwargs)
            if not context["records"]:
                self._capture(result.get("extra", {}).get("response", result))
            status = "completed"
            return result
        except BaseException as exc:
            error = exc
            if not context["records"]:
                for message in getattr(exc, "messages", []):
                    if isinstance(message, dict):
                        self._capture(message.get("extra", {}).get("response", message))
            status = ("cancelled" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else
                      "cost_error" if context["cost_error"] else
                      "format_error" if type(exc).__name__ == "FormatError" else "post_response_error")
            raise
        finally:
            try:
                for record in context["records"]:
                    record["status"] = status
                    self._persist(record)
                if context["records"]:
                    record = dict(context["records"][-1])
                    if isinstance(result, dict):
                        result.setdefault("extra", {})["mini_swe_usage"] = record
                    elif error is not None:
                        msgs = getattr(error, "messages", [])
                        if msgs and isinstance(msgs[0], dict):
                            msgs[0].setdefault("extra", {})["mini_swe_usage"] = record
            except Exception:
                logger.warning("mini-SWE usage finalization failed; usage may be incomplete")
            finally:
                _ACTIVE.reset(token)

    def serialize(self) -> dict:
        result = super().serialize()
        if self._usage_dir is not None:
            config = result.setdefault("info", {}).setdefault("config", {})
            base = type(self).__mro__[type(self).__mro__.index(UsageMixin) + 1]
            config["model_type"] = "mini_swe_export.UsageModel"
            model_config = config.setdefault("model", {})
            model_config.update(model_class="mini_swe_export.UsageModel",
                                wrapped_model_class=base.__module__ + "." + base.__name__,
                                usage_export_dir=str(self._usage_dir), usage_provider=self._usage_provider)
            for key, value in self._usage_ids.items():
                if value is not None:
                    model_config["usage_" + key] = value
        return result
