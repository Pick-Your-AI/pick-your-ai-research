"""Run only the prospective MR-09 H1 native initialization, under fresh guards.

The prediction freeze is an identity/chronology gate, not estimator acceptance.
No generation, warmup, inference or generic command interface is exposed.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from mr09_native_capture import (PREFLIGHT_METHODS, PREFLIGHT_THRESHOLDS,
                                 driver_readback, loads, read_json, read_regular)
from mr09_native_qualify import write
from mr09_total_memory_setup import managed_snapshot_interval

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "research/market/measurements/local-comparison-2026-10-19"
MODEL = "SmolLM2-135M-Instruct-f16.gguf"
MODEL_SHA = "f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57"
RUNTIME_COMMIT = "620d2225cc436ab0b001e3200e590e3b286ef9ab"
CAP_BYTES = 2136809472
RUNTIME_LEDGER_SHA = "d788e18ba59ab6f210c1ceb61599f39269440a774664c8f515ffca9a7041cfcd"
REQUIRED_SOURCES = {"research/market/measurements/native/mr09_native_h1.cpp",
                    "research/market/measurements/native/mr09_quota.hpp"}
CHILD_TIMEOUT_SECONDS = 90
TELEMETRY_TIMEOUT_SECONDS = 10


def sha(path):
    return hashlib.sha256(read_regular(path)).hexdigest()


def utc(value):
    if not isinstance(value, str):
        raise ValueError("timezone-aware timestamp required")
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() is None:
        raise ValueError("timezone-aware timestamp required")
    return parsed


def bound_file(base, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("nonempty forward-slash relative artifact path required")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or ":" in relative:
        raise ValueError("artifact path escapes its declared root")
    resolved = (base / path).resolve()
    if resolved == base.resolve() or base.resolve() not in resolved.parents:
        raise ValueError("artifact path escapes its declared root")
    return resolved


def verify_files(base, files):
    if not isinstance(files, dict) or not files:
        raise ValueError("nonempty artifact hash mapping required")
    for relative, expected in files.items():
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("SHA-256 artifact binding required")
        if sha(bound_file(base, relative)) != expected:
            raise ValueError("artifact drift: " + relative)


def admit(temporary, directory):
    """Bind existing source/build/runtime/model and frozen prediction bytes."""
    build_path = directory / "build.json"
    ledger_path = directory / "runtime-artifacts.json"
    freeze_path = directory / "prediction-freeze.json"
    build = read_json(build_path)
    ledger = read_json(ledger_path)
    freeze = read_json(freeze_path)
    if build.get("runtime_commit") != RUNTIME_COMMIT:
        raise ValueError("runtime commit drift")
    if not isinstance(build.get("harness_git_ref"), str) or not re.fullmatch(r"[0-9a-f]{40}", build["harness_git_ref"]):
        raise ValueError("full harness source revision required")
    verify_files(ROOT, build.get("source_files"))
    if not REQUIRED_SOURCES.issubset(build["source_files"]):
        raise ValueError("H1 harness and quota source bindings required")
    executable_sha = build.get("executables", {}).get("native-init.exe")
    if not isinstance(executable_sha, str) or sha(temporary / "native-init.exe") != executable_sha:
        raise ValueError("native executable drift")
    model = temporary / MODEL
    if model.stat().st_size != 270885952 or sha(model) != MODEL_SHA:
        raise ValueError("pinned GGUF size/hash drift")
    files = ledger.get("files")
    if sha(ledger_path) != RUNTIME_LEDGER_SHA:
        raise ValueError("complete pinned runtime artifact ledger required")
    if not isinstance(files, list) or not files:
        raise ValueError("runtime artifact ledger required")
    runtime_files = {}
    for item in files:
        if not isinstance(item, dict) or item.get("file") in runtime_files:
            raise ValueError("invalid or repeated runtime artifact")
        runtime_files[item.get("file")] = item.get("sha256")
    verify_files(temporary / "runtime", runtime_files)
    freeze_files = freeze.get("files")
    verify_files(ROOT, freeze_files)
    prediction = freeze.get("prediction_file")
    if not isinstance(prediction, str) or prediction not in freeze_files:
        raise ValueError("frozen raw prediction binding required")
    required = {Path(__file__).resolve().relative_to(ROOT).as_posix(),
                build_path.resolve().relative_to(ROOT).as_posix(),
                ledger_path.resolve().relative_to(ROOT).as_posix()}
    if not required.issubset(freeze_files):
        raise ValueError("freeze must bind launcher, build and runtime ledger")
    frozen = utc(freeze.get("observed_utc"))
    return {"harness_sha256": executable_sha, "harness_git_ref": build["harness_git_ref"],
            "build_sha256": sha(build_path), "launcher_sha256": sha(Path(__file__)),
            "model_sha256": MODEL_SHA, "runtime_artifact_ledger_sha256": sha(ledger_path),
            "prediction_freeze_sha256": sha(freeze_path), "prediction_file": prediction,
            "prediction_sha256": freeze_files[prediction]}, frozen


def validate_screen(screen, frozen, started):
    expected = {"classification": "read-only capacity screen; not inference or a fit guarantee",
                "reason": "all screens satisfied; recheck before inference", "profile": "granite31",
                "thresholds": PREFLIGHT_THRESHOLDS, "methods": PREFLIGHT_METHODS,
                "status": "admitted_to_download_screen_only"}
    if any(json.dumps(screen.get(key), sort_keys=True) != json.dumps(value, sort_keys=True)
           for key, value in expected.items()):
        raise ValueError("fresh spare-capacity screen failed or drifted; no launch")
    for group in ("observed", "guards"):
        if type(screen.get(group)) is not dict or set(screen[group]) != set(PREFLIGHT_THRESHOLDS):
            raise ValueError("missing or ambiguous capacity guards")
    for key, threshold in PREFLIGHT_THRESHOLDS.items():
        observed = screen["observed"][key]
        if type(observed) is not int or observed < threshold or screen["guards"][key] is not True:
            raise ValueError("spare-capacity guard failed; no launch")
    observed = utc(screen.get("observed_utc"))
    if not frozen <= observed <= started or (started - observed).total_seconds() > 30:
        raise ValueError("prediction freeze/preflight chronology drift; no launch")


def validate_h1(record):
    """Check the fixed native safety/readback boundary before another launch."""
    if type(record["exit_code"]) is not int or record["exit_code"] != 0:
        raise ValueError("native child failed")
    events = [loads(line) for line in record["stdout"].splitlines() if line.strip()]
    if len(events) != 7 or any(type(event) is not dict for event in events):
        raise ValueError("exact seven-event native H1 trace required")
    probe, after_probe, effective, before, capture, cleanup, result = events
    if (probe.get("mr09_event") != "qualification" or probe.get("status") != "probe_passed"
            or probe.get("device") != "CUDA0" or probe.get("graphs_disabled") is not True
            or probe.get("decode_api_loaded") is not False):
        raise ValueError("native CUDA/graph qualification failed")
    total, free = probe.get("driver_total_bytes"), probe.get("cuda_reported_free_bytes")
    if type(total) is not int or type(free) is not int or not 4 * 2**30 <= free <= total <= 2**64 - 1:
        raise ValueError("native spare-capacity guard failed")
    expected_effective = {"mr09_event": "effective", "no_alloc": False, "context": 256,
                          "batch": 128, "ubatch": 128, "sequences": 1,
                          "generation_forwards": 0, "warmup": False, "extra_buffer_types": False}
    if effective != expected_effective or any(type(effective[k]) is not type(v) for k, v in expected_effective.items()):
        raise ValueError("effective H1 tuple drift")
    cap = min(CAP_BYTES, 2**31, total // 8)
    for event, stage, calls in ((after_probe, "after_probe", 1), (before, "before_capture", 4),
                                (cleanup, "after_cleanup", 4)):
        if event.get("mr09_event") != "cap" or event.get("stage") != stage:
            raise ValueError("native phase/cap event drift")
        for key in ("cap_bytes", "live_bytes", "peak_admitted_bytes", "admission_denials", "native_allocator_calls", "graph_denials"):
            if type(event.get(key)) is not int or event[key] < 0:
                raise ValueError("invalid native cap counter")
        if (event["cap_bytes"] != cap or not event["live_bytes"] <= event["peak_admitted_bytes"] <= cap
                or event["admission_denials"] != 1 or event["graph_denials"] != 1
                or event["native_allocator_calls"] != calls):
            raise ValueError("native cap/graph boundary drift")
    if (after_probe["live_bytes"] != 0 or after_probe["peak_admitted_bytes"] != 8388608
            or cleanup["live_bytes"] != 0 or cleanup["peak_admitted_bytes"] != before["peak_admitted_bytes"]
            or before["peak_admitted_bytes"] < after_probe["peak_admitted_bytes"]):
        raise ValueError("native probe/cleanup ledger drift")
    if capture.get("type") != "fit_memory_breakdown" or result.get("mr09_event") != "result" or result.get("status") != "initialization_qualified":
        raise ValueError("native capture incomplete")
    data = capture["data"]
    interval = managed_snapshot_interval({**data, "metric": "managed_device_buffers_snapshot", "no_alloc": False})
    if not interval[0] <= before["live_bytes"] <= interval[1]:
        raise ValueError("native self/admission ledger mismatch")
    device = next(row for row in data["rows"] if row["kind"] == "device")
    if (type(device.get("total")) is not int or device["total"] != total // 2**20
            or type(device.get("free")) is not int or not 0 <= device["free"] <= device["total"]):
        raise ValueError("native capture capacity drift")
    stderr = record["stderr"]
    if any(text not in stderr for text in ("offloaded 31/31 layers to GPU", "(load_mode = mmap)", "K (f16)", "V (f16)")):
        raise ValueError("native placement/cache readback missing")
    for name, value in (("n_outputs_max", 128), ("n_outputs_max_per_seq", 1)):
        if re.findall(r"^llama_context: " + name + r"\s*=\s*(\d+)\s*$", stderr, re.MULTILINE) != [str(value)]:
            raise ValueError("native H1 output capacity drift")
    return {"exact_admitted_live_buffer_bytes": before["live_bytes"],
            "native_self_byte_interval": list(interval), "cap_bytes": cap,
            "cleanup_live_bytes": 0, "model_graph_dispatches": 0}


def run(temporary, repetition, directory=DIRECTORY):
    if type(repetition) is not int or repetition not in (1, 2, 3):
        raise ValueError("only integer repetitions 1 through 3 permitted")
    output = directory / f"H1-r{repetition}.json"
    preflight = directory / f"H1-r{repetition}-preflight.json"
    if output.exists() or preflight.exists():
        raise ValueError("preserve observations; existing repetition cannot be overwritten")
    prior = None
    if repetition > 1:
        prior = read_json(directory / f"H1-r{repetition - 1}.json")
        if prior.get("status") != "native_initialization_completed":
            raise ValueError("previous trial did not qualify; stop without retry")
        validate_h1(prior)
    identities, frozen = admit(temporary, directory)
    if prior is not None and any(prior.get(key) != value for key, value in identities.items()):
        raise ValueError("source/build/prediction cohort drift; stop without retry")
    pre_driver = query_driver()
    pre_hardware = matching_driver(pre_driver)
    subprocess.run([sys.executable, str(ROOT / "scripts/mr09_preflight.py"), "--profile", "granite31",
                    "--temporary-dir", str(temporary), "--output", str(preflight)],
                   check=True, capture_output=True, text=True, timeout=40)
    started = datetime.now(timezone.utc)
    screen = read_json(preflight)
    validate_screen(screen, frozen, started)
    if prior is not None and utc(screen["observed_utc"]) <= utc(prior["finished_utc"]):
        raise ValueError("serial fresh-process chronology drift; no launch")
    identities.update(preflight_file=preflight.name, preflight_sha256=sha(preflight))
    runtime, model = temporary / "runtime", temporary / MODEL

    def sanitized(value):
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        for path, label in ((model, "$GGUF_FILE"), (runtime, "$RUNTIME_DIR"), (temporary, "$TASK_TEMP"), (ROOT, "$REPO"), (Path.home(), "$USER_HOME")):
            value = value.replace(str(path), label).replace(str(path).replace("\\", "/"), label)
        return value

    timed_out = False
    try:
        child = subprocess.run([str(temporary / "native-init.exe"), str(runtime), str(CAP_BYTES), str(model)],
                               cwd=runtime, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=CHILD_TIMEOUT_SECONDS)
        code, stdout, stderr = child.returncode, child.stdout, child.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        code, stdout, stderr = -1, error.stdout or "", error.stderr or ""
        stderr = sanitized(stderr) + "\nNative child timed out and was killed; stop without retry."
    except OSError as error:
        code, stdout, stderr = -1, "", type(error).__name__ + ": " + str(error)
    record = {"classification": "prospective H1 initialization measurement; pending evidence review",
              "cell": "H1", "repetition": repetition, "started_utc": started.isoformat(),
              "finished_utc": datetime.now(timezone.utc).isoformat(), "exit_code": code,
              "argv": ["$NATIVE_INIT", "$RUNTIME_DIR", str(CAP_BYTES), "$GGUF_FILE"], **identities,
              "native_status": "timed_out" if timed_out else ("completed" if code == 0 else "failed"),
              "stdout": sanitized(stdout), "stderr": sanitized(stderr), "generation_forwards": 0,
              "warmup": False, "driver_csv": None,
              "driver_preflight_csv": pre_driver.strip(),
              "driver_readback": {"status": "pending", "timeout_seconds": TELEMETRY_TIMEOUT_SECONDS},
              "status": "post_run_telemetry_pending" if code == 0 else "qualification_failure"}
    write(output, record)
    try:
        record["native_validation"] = validate_h1(record)
        probe = loads(record["stdout"].splitlines()[0])
        if abs(probe["driver_total_bytes"] - int(pre_hardware["memory.total [MiB]"].split()[0]) * 2**20) > 2**20:
            raise ValueError("native/preflight device capacity mismatch")
    except (ValueError, KeyError, TypeError, StopIteration) as error:
        record["native_validation"] = {"status": "failed", "error": sanitized(str(error))}
        record["status"] = "qualification_failure"
    try:
        raw = query_driver()
        record["driver_csv"] = sanitized(raw.strip())
        post_hardware = matching_driver(record["driver_csv"])
        if post_hardware["memory.total [MiB]"] != pre_hardware["memory.total [MiB]"]:
            raise ValueError("pre/post device capacity mismatch")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError) as error:
        record["driver_readback"] = {"status": "failed", "timeout_seconds": TELEMETRY_TIMEOUT_SECONDS,
                                     "error_type": type(error).__name__, "error": sanitized(str(error)),
                                     "stdout": sanitized(getattr(error, "stdout", None) or ""),
                                     "stderr": sanitized(getattr(error, "stderr", None) or "")}
        record["status"] = "qualification_failure"
    else:
        record["driver_readback"] = {"status": "completed", "timeout_seconds": TELEMETRY_TIMEOUT_SECONDS}
        if code == 0 and record["native_validation"].get("status") != "failed":
            record["status"] = "native_initialization_completed"
    write(output, record)
    return record


def query_driver():
    return subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free", "--format=csv"],
                                   text=True, encoding="utf-8", errors="replace", stderr=subprocess.PIPE,
                                   timeout=TELEMETRY_TIMEOUT_SECONDS)


def matching_driver(raw):
    hardware = driver_readback(raw)
    if hardware["name"] != "NVIDIA GeForce RTX 5070 Ti" or hardware["driver_version"] != "610.88":
        raise ValueError("pinned RTX 5070 Ti / driver 610.88 required; no launch or cohort change")
    return hardware


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temporary-dir", type=Path, required=True)
    parser.add_argument("--repetition", type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    result = run(args.temporary_dir.resolve(), args.repetition)
    print(result["status"])
    return 0 if result["status"] == "native_initialization_completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
