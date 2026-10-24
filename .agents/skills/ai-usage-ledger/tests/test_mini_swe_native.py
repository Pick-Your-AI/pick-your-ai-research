"""Real mini-SWE-agent adapters and agent loop against synthetic localhost APIs.

Requires mini-SWE-agent 2.4.6, LiteLLM and Portkey in the test environment only.
No provider keys, external model calls, monkey-patches, or estimated token counts.
"""
import csv
import io
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

pytest.importorskip("minisweagent")
pytest.importorskip("litellm")
pytest.importorskip("portkey_ai")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from minisweagent.agents.default import DefaultAgent  # noqa: E402
from minisweagent.environments.local import LocalEnvironment  # noqa: E402
from minisweagent.exceptions import FormatError  # noqa: E402
from minisweagent.models import GLOBAL_MODEL_STATS, get_model  # noqa: E402
from portkey_ai import Portkey  # noqa: E402

import compile_ai_logs as scanner  # noqa: E402
import ledger_store  # noqa: E402
import mini_swe_usage as usage  # noqa: E402

BACKENDS = ["litellm", "litellm_textbased", "litellm_response", "openrouter", "openrouter_textbased",
            "openrouter_response", "portkey", "portkey_response", "requesty"]


class SyntheticAPI(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
        state = self.server.state
        state["attempts"] += 1
        if state.get("retry") and state["attempts"] == 1:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"synthetic transient failure"}}')
            return
        state["calls"] += 1
        index = state["calls"]
        name = "invalid_tool" if state.get("bad_action") else "bash"
        command = "printf 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\\nverified\\n'" if index == 2 else "printf 'safe fixture\\n'"
        model = state.get("response_model") or payload["model"]
        rid = "synthetic-response-" + str(index)
        args = json.dumps({"command": command})
        if "input" in payload:
            value = {
                "id": rid, "object": "response", "created_at": 1780000000, "status": "completed",
                "error": None, "incomplete_details": None, "instructions": None, "max_output_tokens": None,
                "model": model, "output": [{"id": "fc_" + str(index), "type": "function_call", "status": "completed",
                                           "call_id": "call_" + str(index), "name": name, "arguments": args}],
                "parallel_tool_calls": False, "previous_response_id": None, "reasoning": {"effort": None, "summary": None},
                "store": False, "temperature": 1.0, "text": {"format": {"type": "text"}}, "tool_choice": "auto",
                "tools": [], "top_p": 1.0, "truncation": "disabled", "user": None, "metadata": {},
                "usage": {"input_tokens": 100 * index, "output_tokens": 20 * index, "total_tokens": 120 * index,
                          "input_tokens_details": {"cached_tokens": 30 * index},
                          "output_tokens_details": {"reasoning_tokens": 5 * index}, "cost": 0.01 * index},
            }
        else:
            content = "no executable action" if state.get("bad_action") else "```mswea_bash_command\n" + command + "\n```"
            value = {
                "id": rid, "object": "chat.completion", "created": 1780000000, "model": model,
                "choices": [{"index": 0, "finish_reason": "tool_calls" if payload.get("tools") else "stop",
                             "message": {"role": "assistant", "content": content, "tool_calls": [
                                 {"id": "call_" + str(index), "type": "function", "function": {"name": name, "arguments": args}}
                             ] if payload.get("tools") else None}}],
                "usage": {"prompt_tokens": 100 * index, "completion_tokens": 20 * index, "total_tokens": 120 * index,
                          "prompt_tokens_details": {"cached_tokens": 30 * index},
                          "completion_tokens_details": {"reasoning_tokens": 5 * index}, "cost": 0.01 * index},
            }
        if state.get("omit_cost"):
            value["usage"].pop("cost", None)
        if state.get("omit_total"):
            value["usage"].pop("total_tokens", None)
        state["evidence"].append(value["usage"])
        raw = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


@pytest.fixture
def api():
    server = ThreadingHTTPServer(("127.0.0.1", 0), SyntheticAPI)
    server.state = {"attempts": 0, "calls": 0, "evidence": []}
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server, "http://127.0.0.1:" + str(server.server_port) + "/v1"
    server.shutdown()
    server.server_close()
    thread.join()


def configured(backend, directory, base_url, **kwargs):
    config = {"model_class": "mini_swe_export.UsageModel", "wrapped_model_class": backend,
              "model_name": "openai/gpt-4o-mini" if backend.startswith(("litellm", "openrouter", "requesty")) else "gpt-4o-mini",
              "usage_export_dir": str(directory.resolve()), "usage_run_id": "synthetic-run", "usage_session_id": "synthetic-session",
              "cost_tracking": "ignore_errors", **kwargs}
    if backend.startswith("litellm"):
        config["model_kwargs"] = {"api_base": base_url, "api_key": "synthetic-not-a-provider-key"}
    model = get_model(config=config)
    if backend.startswith(("openrouter", "requesty")):
        model._api_url = base_url + ("/responses" if "response" in backend else "/chat/completions")
    if backend.startswith("portkey"):
        model.client = Portkey(api_key="synthetic-not-a-provider-key", base_url=base_url)
    return model


def collected(root):
    out, stats = io.StringIO(), scanner.Stats()
    usage.scan(str(root), "synthetic-host", out, stats, [], set())
    assert stats.errors == 0
    return [json.loads(line) for line in out.getvalue().splitlines()]


@pytest.mark.parametrize(("backend", "bad_action"), [(b, bad) for b in BACKENDS for bad in (False, True)])
def test_real_adapter_success_and_format_error(backend, bad_action, tmp_path, api):
    server, base_url = api
    server.state["bad_action"] = bad_action
    model = configured(backend, tmp_path / "usage", base_url)
    if bad_action:
        with pytest.raises(FormatError) as exc:
            model.query([{"role": "user", "content": "synthetic prompt"}])
        message = exc.value.messages[0]
    else:
        message = model.query([{"role": "user", "content": "synthetic prompt"}])
    # Inspect the native persisted shape and the same invocation's usage export.
    (tmp_path / "run.traj.json").write_text(json.dumps({"trajectory_format": usage.TRAJECTORY, "messages": [message]}))
    events = collected(tmp_path)
    assert len(events) == 1
    event = events[0]
    assert [event[k] for k in ("input_uncached", "cache_read", "output", "reasoning", "total")] == [70, 30, 20, 5, 120]
    assert event["execution_status"] == ("format_error" if bad_action else "completed")
    assert server.state["attempts"] == 1
    assert "synthetic prompt" not in json.dumps(events)
    assert "synthetic-not-a-provider-key" not in json.dumps(events)
    serialized = model.serialize()["info"]["config"]
    assert serialized["model_type"] == "mini_swe_export.UsageModel"
    assert serialized["model"]["wrapped_model_class"].startswith("minisweagent.models.")


def test_real_native_retry_has_one_usage_event(tmp_path, api):
    server, base_url = api
    server.state["retry"] = True
    configured("openrouter", tmp_path / "usage", base_url).query([{"role": "user", "content": "synthetic"}])
    assert (server.state["attempts"], server.state["calls"]) == (2, 1)
    assert len(collected(tmp_path)) == 1


def test_real_litellm_missing_price_preserves_tokens_and_exception(tmp_path, api):
    server, base_url = api
    server.state.update(response_model="unregistered-local-fixture", omit_total=True, omit_cost=True)
    model = configured("litellm", tmp_path / "usage", base_url, model_name="openai/unregistered-local-fixture", cost_tracking="default")
    with pytest.raises(RuntimeError, match="Error calculating cost"):
        model.query([{"role": "user", "content": "synthetic"}])
    event = collected(tmp_path)[0]
    assert (event["input_uncached"], event["cache_read"], event["output"], event["total"]) == (70, 30, 20, 120)
    assert event["source_calculated_cost"] is None
    assert event["execution_status"] == "cost_error"
    assert server.state["calls"] == 1


def test_actual_global_cost_limit_is_not_weakened(tmp_path, api):
    _, base_url = api
    model = configured("openrouter", tmp_path / "usage", base_url)
    previous = GLOBAL_MODEL_STATS.cost_limit
    GLOBAL_MODEL_STATS.cost_limit = GLOBAL_MODEL_STATS.cost + 0.001
    try:
        with pytest.raises(RuntimeError, match="Global cost/call limit exceeded"):
            model.query([{"role": "user", "content": "synthetic"}])
    finally:
        GLOBAL_MODEL_STATS.cost_limit = previous
    event = collected(tmp_path)[0]
    assert event["total"] == 120
    assert event["execution_status"] == "post_response_error"


def test_two_provider_agent_run_scan_report_and_idempotency(tmp_path, api):
    server, base_url = api
    first = configured("litellm", tmp_path / "usage", base_url, cost_tracking="default")
    second = configured("openrouter", tmp_path / "usage", base_url, model_name="other-provider/model-b")

    class TwoModelsAgent(DefaultAgent):
        def query(self):
            self.model = first if self.n_calls == 0 else second
            return super().query()

    trajectory_path = tmp_path / "run.traj.json"
    agent = TwoModelsAgent(first, LocalEnvironment(cwd=str(tmp_path)), system_template="Synthetic deterministic test",
                           instance_template="{{task}}", step_limit=3, output_path=trajectory_path)
    result = agent.run("Run the safe, deterministic fixture")
    assert result["exit_status"] == "Submitted"
    assert server.state["calls"] == 2
    out = tmp_path / "scan"
    command = [sys.executable, str(ROOT / "scripts/compile_ai_logs.py"), "scan", "--host", "synthetic-host",
               "--mini-swe-root", str(tmp_path), "--no-prompts", "--out-dir", str(out)]
    subprocess.run(command, check=True, capture_output=True)
    event_file = out / "events.synthetic-host.jsonl"
    events = [json.loads(line) for line in event_file.read_text().splitlines()]
    assert len(events) == 2
    assert {e["provider"] for e in events} == {"openai-compatible", "openrouter"}
    assert {e["model"] for e in events} == {"gpt-4o-mini", "other-provider/model-b"}
    assert {e["session"] for e in events} == {"synthetic-session"}
    actual = {key: sum(e[key] for e in events) for key in ("input_uncached", "cache_read", "cache_write", "output", "reasoning", "total")}
    expected = {"input_uncached": 210, "cache_read": 90, "cache_write": 0, "output": 60, "reasoning": 15, "total": 360}
    assert actual == expected
    assert sum(e["prompt_tokens"] + e["completion_tokens"] for e in server.state["evidence"]) == actual["total"]
    store = ledger_store.Store.open("sqlite", str(tmp_path / "ledger.sqlite"))
    try:
        assert store.ingest_events_file(str(event_file)) == (2, 0)
        subprocess.run(command, check=True, capture_output=True)
        assert store.ingest_events_file(str(event_file)) == (0, 2)
        assert sum(e["total"] for e in store.iter_events()) == 360
    finally:
        store.close()
    rate = {"input": 2, "cache_read": 1, "cache_write_5m": 3, "cache_write_1h": 4, "output": 4}
    pricing = tmp_path / "synthetic-pricing.json"
    pricing.write_text(json.dumps({"models": {model: rate for model in {e["model"] for e in events}}}))
    report_dir = tmp_path / "report"
    subprocess.run([sys.executable, str(ROOT / "scripts/compile_ai_logs.py"), "report", "--events", str(event_file),
                    "--pricing", str(pricing), "--out-dir", str(report_dir)], check=True, capture_output=True)
    with (report_dir / "all_events.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert sum(int(e["total"]) for e in rows) == 360
    assert sum(float(e["api_cost_usd"]) for e in rows) == pytest.approx(0.00075)
    receipt = {"source_totals": expected, "ledger_totals": actual, "first_ingest": [2, 0], "second_ingest": [0, 2],
               "synthetic_api_equivalent_usd": 0.00075, "events": events, "source_provider_usage": server.state["evidence"]}
    if directory := os.getenv("MINI_SWE_TEST_RECEIPTS"):
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        (target / "reconciliation.json").write_text(json.dumps(receipt, indent=2))


def test_process_termination_keeps_pre_cost_checkpoint(tmp_path, api):
    _, base_url = api
    script = '''
import os
from minisweagent.models.litellm_model import LitellmModel
from mini_swe_export import usage_model
class TerminateAfterResponse(LitellmModel):
    def _calculate_cost(self, response):
        os._exit(19)
model = usage_model(TerminateAfterResponse)(model_name="openai/gpt-4o-mini", usage_export_dir=os.environ["TEST_EXPORT"],
    usage_provider="openai-compatible", model_kwargs={"api_base":os.environ["TEST_API_BASE"], "api_key":"synthetic"})
model.query([{"role":"user", "content":"synthetic"}])
'''
    result = subprocess.run([sys.executable, "-c", script], env={**os.environ, "TEST_EXPORT": str(tmp_path / "usage"),
                            "TEST_API_BASE": base_url, "PYTHONPATH": str(ROOT / "scripts")}, capture_output=True)
    assert result.returncode == 19, result.stderr.decode()
    event = collected(tmp_path)[0]
    assert (event["total"], event["execution_status"]) == (120, "response_received")
