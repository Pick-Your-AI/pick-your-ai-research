"""Reserve future H1 attempts before the preserved initialization kernel runs.

The captured 2026-10-19 cohort and its exact launcher stay unchanged. Future
cohorts need a new reviewed freeze containing this entry point and every guard
source. Admission control is not hardware reservation or research acceptance.
"""
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import re
import uuid

import mr09_local_compare_run as kernel

ROOT = kernel.ROOT
COHORT_LOCK = "H1-active-attempt.json"
REQUIRED_GUARD_SOURCES = frozenset({
    "scripts/mr09_local_compare_admission.py",
    "scripts/mr09_local_compare_run.py",
    "scripts/mr09_preflight.py",
    "scripts/mr09_native_capture.py",
    "scripts/mr09_native_qualify.py",
    "scripts/mr09_total_memory_setup.py",
})
PACKAGE = "research/market/measurements/gguf-parser-mr09"
PREPARER = "scripts/mr09_prepare_estimator.py"
PACKAGE_SOURCES = frozenset({
    f"{PACKAGE}/LICENSE.upstream", f"{PACKAGE}/README.md",
    f"{PACKAGE}/derivative.patch", f"{PACKAGE}/source-manifest.json", PREPARER,
    "tests/native/mr09_cli_admission.py",
    "tests/native/mr09_original_semantic_test.go",
    "tests/native/mr09_output_semantic_test.go",
})
PACKET_FILES = frozenset({
    "build.json", "runtime-artifacts.json", "protocol.md",
    "estimator-source-preparation.json", "estimator-windows-adaptation.json",
    "estimator-profile.json", "estimator-prediction.json", "prediction-receipt.json",
    "estimator-manifest.json", "semantic-review.json",
})
ESTIMATOR_ID = "gguf-parser-go-v0.26.4+mr09-output.2-experimental"
UPSTREAM_COMMIT = "637cd9a7a03993ab30ace3c53dd8af5c37f46a94"
UPSTREAM_TREE = "4b67ed5331cbd40639db36890f8453c61ac604b7"
H1_PROFILE = {
    "runtime_commit": kernel.RUNTIME_COMMIT,
    "stage": "completed-initialization-before-free", "allocation": "allocated",
    "placement": "single-CUDA0-all-layers", "output_backend": "CUDA0",
    "host_readback": "host", "embeddings": "disabled", "backend_samplers": "disabled",
    "flash_attention": "disabled", "mmap": "enabled", "kv_offload": "enabled",
    "operation_offload": "enabled", "cache_key": "f16", "cache_value": "f16",
    "context_size": 256, "logical_batch_size": 128, "physical_batch_size": 128,
    "sequence_capacity": 1, "outputs_max": 128, "outputs_max_per_sequence": 1,
}


def now():
    return datetime.now(timezone.utc).isoformat()


def exclusive_record(path, value):
    """Create one durable reservation; an existing path always wins."""
    data = json.dumps(value, indent=2, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def exact(actual, expected):
    """Compare JSON values without accepting bool/float aliases for integers."""
    return (json.dumps(actual, sort_keys=True, allow_nan=False)
            == json.dumps(expected, sort_keys=True, allow_nan=False))


def byte_value(value):
    if type(value) is not int or not 0 <= value < 2**64:
        raise ValueError("exact nonnegative integer byte term required")
    return value


def prediction_terms(prediction):
    expected_controls = {
        "host_readback_rows": 1, "graph_output_rows": 128, "per_sequence_context": 256,
        "declared_populated_cache_positions": 0, "declared_active_requests": 0,
        "declared_generated_tokens": 0,
    }
    if any(not exact(prediction.get(key), value) for key, value in expected_controls.items()):
        raise ValueError("prediction control/readback profile drift")
    estimate = prediction["estimate"]
    expected_estimate = {
        "type": "model", "architecture": "llama", "flashAttention": False,
        "contextSize": 256, "offloadLayers": 30, "fullOffloaded": True,
        "noMMap": False, "embeddingOnly": False, "reranking": False,
        "logicalBatchSize": 128, "physicalBatchSize": 128,
    }
    if any(not exact(estimate.get(key), value) for key, value in expected_estimate.items()):
        raise ValueError("prediction estimate/control mismatch")
    devices = estimate["devices"]
    if not isinstance(devices, list) or len(devices) != 2:
        raise ValueError("exactly host and one CUDA0 prediction device required")
    host, device = devices
    for row, expected in ((host, {"remote": False, "position": 0, "handleLayers": 0,
                                  "handleOutputLayer": False}),
                          (device, {"remote": False, "position": 0, "handleLayers": 30,
                                    "handleLastLayer": 29, "handleOutputLayer": True})):
        if any(not exact(row.get(key), value) for key, value in expected.items()):
            raise ValueError("prediction device placement mismatch")
    computation = device["computation"]
    # Check both operands, including the one discarded by max().
    graph, output = (byte_value(computation[key]) for key in ("graph", "output"))
    terms = {"footprint": device["footprint"],
             **{f"weight.{key}": device["weight"][key]
                for key in ("input", "compute", "computeOverridden", "output")},
             **{f"kvCache.{key}": device["kvCache"][key] for key in ("key", "value")},
             "computation.footprint": computation["footprint"],
             "computation.input": computation["input"],
             "computation.max_graph_output": max(graph, output)}
    return {key: byte_value(value) for key, value in terms.items()}


def verify_prediction_packet(directory, freeze, files):
    """Join the frozen source, reviewed controls, CPU output and exact arithmetic.

    This checks the recorded identities and declarations. Human source/build
    review remains necessary; a self-authored JSON review is not approval.
    """
    def read(name):
        value = kernel.read_json(directory / name)
        if not isinstance(value, dict):
            raise ValueError("prediction packet object required")
        return value

    prediction_relative = (directory / "estimator-prediction.json").relative_to(ROOT).as_posix()
    if freeze.get("prediction_file") != prediction_relative:
        raise ValueError("freeze must name this cohort's bound raw prediction")
    if not exact(freeze.get("native_model_observations_before_freeze"), 0):
        raise ValueError("a prospective freeze must declare zero prior model observations")
    frozen = kernel.utc(freeze.get("observed_utc"))
    if frozen > datetime.now(timezone.utc):
        raise ValueError("prediction freeze is in the future")
    profile, prediction = read("estimator-profile.json"), read("estimator-prediction.json")
    if not exact(profile, H1_PROFILE) or not exact(prediction.get("declared_profile"), H1_PROFILE):
        raise ValueError("future prediction must retain the exact typed H1 profile")
    expected_prediction = {"artifact_sha256": kernel.MODEL_SHA, "artifact_bytes": 270885952,
                           "identity": ESTIMATOR_ID, "upstream_commit": UPSTREAM_COMMIT}
    if any(not exact(prediction.get(key), value) for key, value in expected_prediction.items()):
        raise ValueError("future prediction artifact or estimator identity drift")
    terms = prediction_terms(prediction)
    total = byte_value(sum(terms.values()))
    receipt = read("prediction-receipt.json")
    if (not total or not exact(receipt.get("extraction_terms_bytes"), terms)
            or not exact(receipt.get("managed_device_estimate_bytes"), total)
            or not exact(freeze.get("managed_device_estimate_bytes"), total)
            or receipt.get("raw_prediction_sha256") != files[prediction_relative]
            or not exact(receipt.get("exit_code"), 0)
            or receipt.get("native_execution") != "unexecuted"
            or not exact(receipt.get("argv"), ["$EXPERIMENTAL_ESTIMATOR", "--sha256",
                                              kernel.MODEL_SHA, "--profile", H1_PROFILE])):
        raise ValueError("raw prediction/aggregation receipt mismatch")
    started, finished = (kernel.utc(receipt.get(key)) for key in ("started_utc", "finished_utc"))
    if not started <= finished <= frozen:
        raise ValueError("CPU prediction must finish before its prospective freeze")

    preparation = read("estimator-source-preparation.json")
    adaptation = read("estimator-windows-adaptation.json")
    manifest = read("estimator-manifest.json").get("manifest")
    semantic = read("semantic-review.json")
    source_manifest = kernel.read_json(ROOT / PACKAGE / "source-manifest.json")
    package_commit = preparation.get("package_commit")
    if (not isinstance(package_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", package_commit)
            or receipt.get("estimator_package_commit") != package_commit
            or semantic.get("candidate_commit") != package_commit
            or not exact(semantic.get("reviewed_profile"), H1_PROFILE)
            or not isinstance(semantic.get("disposition"), str) or not semantic["disposition"].strip()
            or preparation.get("upstream_commit") != UPSTREAM_COMMIT
            or not isinstance(manifest, dict)
            or manifest.get("upstream_commit") != UPSTREAM_COMMIT
            or manifest.get("upstream_tree") != UPSTREAM_TREE
            or source_manifest.get("upstream_commit") != UPSTREAM_COMMIT
            or source_manifest.get("upstream_tree") != UPSTREAM_TREE
            or source_manifest.get("identity") != ESTIMATOR_ID
            or source_manifest.get("runtime_commit") != kernel.RUNTIME_COMMIT):
        raise ValueError("estimator preparation/build/review identity mismatch")
    package_hashes = preparation.get("package_sha256")
    core_hashes = source_manifest.get("package_sha256")
    if (not isinstance(package_hashes, dict) or not PACKAGE_SOURCES.issubset(package_hashes)
            or not isinstance(core_hashes, dict)
            or set(core_hashes) != PACKAGE_SOURCES - {f"{PACKAGE}/README.md", f"{PACKAGE}/source-manifest.json"}
            or manifest.get("package_sha256") != core_hashes
            or any(files.get(path) != digest for path, digest in package_hashes.items())
            or any(package_hashes.get(path) != digest for path, digest in core_hashes.items())):
        raise ValueError("estimator source package is not completely bound by the freeze")
    binary_sha = manifest.get("candidate_executable_sha256")
    if (not isinstance(binary_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", binary_sha)
            or receipt.get("candidate_executable_sha256") != binary_sha
            or type(manifest.get("candidate_executable_bytes")) is not int
            or manifest["candidate_executable_bytes"] <= 0
            or adaptation.get("original_runner_sha256") != package_hashes[PREPARER]
            or not isinstance(adaptation.get("adapted_runner_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", adaptation["adapted_runner_sha256"])
            or not isinstance(adaptation.get("unified_diff"), str) or not adaptation["unified_diff"].strip()):
        raise ValueError("estimator executable/preparation adaptation binding mismatch")


def guard_source_closure(directory):
    """Validate the mandatory source identities in a future prediction freeze."""
    freeze_path = directory / "prediction-freeze.json"
    freeze = kernel.read_json(freeze_path)
    files = freeze.get("files")
    required = REQUIRED_GUARD_SOURCES | PACKAGE_SOURCES | kernel.REQUIRED_SOURCES
    required |= {(directory / name).relative_to(ROOT).as_posix() for name in PACKET_FILES}
    if not isinstance(files, dict) or not required.issubset(files):
        raise ValueError("future freeze must bind the complete source, guard and prediction packet")
    kernel.verify_files(ROOT, files)
    verify_prediction_packet(directory, freeze, files)
    profile_relative = (directory / "estimator-profile.json").relative_to(ROOT).as_posix()
    return {"prediction_freeze_sha256": kernel.sha(freeze_path),
            "estimator_profile_sha256": files[profile_relative],
            "guard_sources": {path: files[path] for path in sorted(REQUIRED_GUARD_SOURCES)}}


def release_owned_lock(path, identity):
    if kernel.read_json(path) != identity:
        raise ValueError("cohort reservation changed; keep it blocked for review")
    path.unlink()


def verify_prior_attempts(directory, repetition, closure):
    for number in range(1, repetition):
        attempt = kernel.read_json(directory / f"H1-r{number}-attempt.json")
        if (type(attempt.get("schema_version")) is not int
                or attempt["schema_version"] != 1
                or type(attempt.get("repetition")) is not int
                or attempt["repetition"] != number
                or attempt.get("cell") != "H1"
                or attempt.get("status") != "completed"
                or attempt.get("native_status") != "native_initialization_completed"
                or attempt.get("output_file") != f"H1-r{number}.json"
                or any(attempt.get(key) != value for key, value in closure.items())):
            raise ValueError("prior guarded attempt did not complete with this source freeze")
        if kernel.sha(directory / attempt["output_file"]) != attempt.get("output_sha256"):
            raise ValueError("prior guarded result changed; stop without retry")


def run(temporary, repetition, directory):
    """Serialize one declared cohort and retain every admitted attempt.

    Failed or interrupted attempts keep the cohort reservation. A caller must
    not remove it to retry automatically. Existing historical results are never
    adopted as attempts under this new control protocol.
    """
    if type(repetition) is not int or repetition not in (1, 2, 3):
        raise ValueError("only integer repetitions 1 through 3 permitted")
    directory = Path(directory).resolve(strict=True)
    temporary = Path(temporary)
    if not directory.is_dir():
        raise ValueError("existing cohort directory required")
    if ROOT.resolve() not in directory.parents:
        raise ValueError("future cohort must be within the reviewed repository")
    output = directory / f"H1-r{repetition}.json"
    preflight = directory / f"H1-r{repetition}-preflight.json"
    attempt_path = directory / f"H1-r{repetition}-attempt.json"
    protected = (output, preflight, attempt_path)
    if any(os.path.lexists(path) for path in protected):
        raise ValueError("preserve existing attempt, preflight and result records")

    lock_path = directory / COHORT_LOCK
    identity = {"schema_version": 1, "cell": "H1", "repetition": repetition,
                "attempt_id": str(uuid.uuid4()), "reserved_utc": now()}
    exclusive_record(lock_path, identity)
    # Recheck after the exclusive claim: another completed invocation may have
    # created its result between our first check and this successful open.
    if any(os.path.lexists(path) for path in protected):
        release_owned_lock(lock_path, identity)
        raise ValueError("preserve existing attempt, preflight and result records")

    attempt = {**identity,
               "classification": "prospective H1 admission control; not evidence acceptance",
               "status": "pending", "phase": "reserved", "native_status": "not_recorded",
               "output_file": output.name}
    exclusive_record(attempt_path, attempt)
    phase = "temporary_directory"
    try:
        attempt.update(phase=phase)
        kernel.write(attempt_path, attempt)
        temporary = temporary.resolve(strict=True)
        if not temporary.is_dir():
            raise ValueError("existing temporary directory required")
        phase = "source_closure"
        attempt.update(phase=phase)
        kernel.write(attempt_path, attempt)
        closure = guard_source_closure(directory)
        attempt.update(closure)
        phase = "prior_attempts"
        attempt.update(phase=phase)
        kernel.write(attempt_path, attempt)
        verify_prior_attempts(directory, repetition, closure)
        phase = "guarded_kernel"
        attempt.update(phase=phase)
        kernel.write(attempt_path, attempt)
        result = kernel.run(temporary, repetition, directory)
        phase = "result_binding"
        attempt.update(phase=phase)
        kernel.write(attempt_path, attempt)
        retained = kernel.read_json(output)
        if retained != result:
            raise ValueError("retained native result differs from the returned result")
        completed = result.get("status") == "native_initialization_completed"
        attempt.update(status="completed" if completed else "failed",
                       phase="complete" if completed else "guarded_kernel",
                       finished_utc=now(), native_status=result.get("status"),
                       output_sha256=kernel.sha(output))
        kernel.write(attempt_path, attempt)
        if completed:
            phase = "reservation_release"
            release_owned_lock(lock_path, identity)
        return result
    except BaseException as error:
        # Exception text can contain private paths or input payloads. Retain
        # the phase and exception type only. A missing native record cannot
        # establish whether an interrupted kernel ever started a child.
        attempt.update(status="failed", phase=phase, finished_utc=now(),
                       error_type=type(error).__name__)
        try:
            kernel.write(attempt_path, attempt)
        except Exception:
            # The already durable pending record and exclusive lock still
            # block admission if this later write cannot be completed.
            pass
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temporary-dir", type=Path, required=True)
    parser.add_argument("--cohort-dir", type=Path, required=True)
    parser.add_argument("--repetition", type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    try:
        result = run(args.temporary_dir, args.repetition, args.cohort_dir)
    except (Exception, KeyboardInterrupt) as error:
        # The CLI also excludes raw exception text/argv/private paths.
        print(json.dumps({"status": "admission_failed", "error_type": type(error).__name__}))
        return 1
    print(result["status"])
    return 0 if result["status"] == "native_initialization_completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
