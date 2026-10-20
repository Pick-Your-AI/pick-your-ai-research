"""Fixed-inventory OLMoE artifact preparation; import and plan/verify are offline.

No model is loaded here. Downloads require an explicit subcommand and a recorded
acquisition reference. That reference is an operator assertion, not authenticated
permission or evidence acceptance. Artifacts and receipts must remain outside Git.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
import urllib.request
import uuid

from mr09_measure import publish_result

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "research/market/measurements/mr09-olmoe-artifact-copy-plan-v1.json"
PLAN_SHA256 = "488cd584e4cbcbabd3bde62a1566600e06e6ef89c7408bd23564db58173e23bc"
MODEL_ID = "allenai/OLMoE-1B-7B-0924-Instruct"
REVISION = "7f1c97f440f06ce36705e4f2b843edb5925f4498"
FILES = (
    "model-00001-of-00003.safetensors", "model-00002-of-00003.safetensors",
    "model-00003-of-00003.safetensors", "config.json", "generation_config.json",
    "model.safetensors.index.json", "special_tokens_map.json", "tokenizer.json",
    "tokenizer_config.json",
)
CHUNK = 1024 * 1024
LOCK = ".mr09-olmoe-acquisition.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def read_control(path: Path) -> tuple[dict, str]:
    """Bounded local control input, with no duplicate or noninteger number aliases."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject(value):
        raise ValueError("control JSON requires integer tokens and finite values")

    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("regular control file required")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0)
                         | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if _identity(before) != _identity(opened):
            raise ValueError("control changed before read")
        raw = stream.read(CHUNK + 1)
        after = os.fstat(stream.fileno())
    if _identity(opened) != _identity(after) or _identity(after) != _identity(path.lstat()):
        raise ValueError("control changed during read")
    if len(raw) > CHUNK:
        raise ValueError("control JSON exceeds 1 MiB")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                       parse_float=reject, parse_constant=reject)
    if type(value) is not dict:
        raise ValueError("control JSON must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def strict_json(path: Path) -> dict:
    return read_control(path)[0]


def load_plan() -> dict:
    """Only the accepted, exact-byte plan is an inventory or loader authority."""
    plan, digest = read_control(PLAN_PATH)
    if digest != PLAN_SHA256:
        raise ValueError("accepted OLMoE plan bytes changed; separate review required")
    return plan


def inventory(plan: dict) -> list[dict]:
    entries = [*plan["weight_shards"], *plan["metadata_files"]]
    if tuple(item["file"] for item in entries) != FILES:
        raise ValueError("exact nine-file allowlist required")
    return entries


def external_directory(path: Path, *, create: bool = False) -> Path:
    """Reject repository storage and symlink components; do not silently follow aliases."""
    path = path.absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("artifact/output directory must not contain symlink components")
    if any(os.path.lexists(parent / ".git") for parent in (path, *path.parents)):
        raise ValueError("artifacts and local execution receipts must stay outside Git")
    if create:
        path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise ValueError("existing external directory required")
    return path.resolve(strict=True)


def reference(value: str) -> str:
    if (type(value) is not str or not value.strip() or len(value) > 500
            or any(ord(char) < 32 for char in value)):
        raise ValueError("nonempty acquisition/authorization reference required")
    return value


def fresh_output(path: Path, model_dir: Path | None = None) -> Path:
    parent = external_directory(path.parent)
    path = parent / path.name
    if model_dir is not None and (parent == model_dir or model_dir in parent.parents):
        raise ValueError("receipt must be outside the fixed-inventory model directory")
    if os.path.lexists(path):
        raise ValueError("output already exists; preserve it")
    return path


@contextmanager
def reservation(path: Path, record: dict):
    """Exclusive durable claim; failures keep the original record for operator review."""
    encoded = json.dumps(record, sort_keys=True, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        if stream.write(encoded) != len(encoded):
            raise OSError("short reservation write")
        stream.flush()
        os.fsync(stream.fileno())
    yield
    if path.is_symlink() or path.read_text(encoding="utf-8") != encoded:
        raise ValueError("reservation changed; preserve it for review")
    path.unlink()


def _identity(stat_result):
    return (stat_result.st_dev, stat_result.st_ino, stat_result.st_size,
            stat_result.st_mtime_ns, stat_result.st_ctime_ns)


def verify_file(path: Path, expected: dict) -> dict:
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("regular artifact required: " + expected["file"])
    if before.st_size != expected["bytes"]:
        raise ValueError("artifact length mismatch: " + expected["file"])
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0)
                         | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    sha = hashlib.sha256()
    git = hashlib.sha1(b"blob " + str(expected["bytes"]).encode("ascii") + b"\0")
    size = 0
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if _identity(before) != _identity(opened):
            raise ValueError("artifact changed before verification")
        while block := stream.read(CHUNK):
            size += len(block)
            if size > expected["bytes"]:
                raise ValueError("artifact exceeds exact length")
            sha.update(block)
            git.update(block)
        after = os.fstat(stream.fileno())
    if size != expected["bytes"] or _identity(opened) != _identity(after):
        raise ValueError("artifact changed during verification")
    if _identity(after) != _identity(path.lstat()):
        raise ValueError("artifact changed after verification")
    actual = sha.hexdigest()
    if "publisher_sha256" in expected:
        # The Git blob in an LFS record identifies its pointer, not these payload bytes.
        if actual != expected["publisher_sha256"]:
            raise ValueError("publisher payload checksum mismatch: " + expected["file"])
        basis = "publisher_lfs_sha256_and_length"
    else:
        if git.hexdigest() != expected["publisher_git_blob"]:
            raise ValueError("publisher Git blob mismatch: " + expected["file"])
        if expected["observed_sha256"] is not None and actual != expected["observed_sha256"]:
            raise ValueError("previous metadata checksum mismatch: " + expected["file"])
        basis = "publisher_git_blob_and_length"
    return {"file": expected["file"], "bytes": size, "local_sha256": actual,
            "verification_basis": basis,
            "prior_observed_sha256": expected.get("observed_sha256"),
            "source_url": f"https://huggingface.co/{MODEL_ID}/resolve/{REVISION}/{expected['file']}"}


def _check_names(directory: Path, *, locked: bool = False) -> None:
    allowed = set(FILES) | ({LOCK} if locked else set())
    if any(path.name not in allowed for path in directory.iterdir()):
        raise ValueError("unexpected artifact or retained attempt; review before proceeding")


def verify(directory: Path) -> dict:
    plan = load_plan()
    directory = external_directory(directory)
    _check_names(directory)
    observed = [verify_file(directory / spec["file"], spec) for spec in inventory(plan)]
    return {"schema_version": "mr09-olmoe-artifact-observation/v1",
            "status": "artifacts_verified_model_unexecuted", "model_id": MODEL_ID,
            "revision": REVISION, "plan_sha256": PLAN_SHA256, "artifacts": observed,
            "observed_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "complete local bytes versus pinned publisher identity; no model run or rights grant"}


class HTTPSRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        # Initial authority is fixed; never follow a publisher redirect to plaintext.
        if not newurl.startswith("https://"):
            raise ValueError("non-HTTPS artifact redirect rejected")
        return super().redirect_request(request, response, code, message, headers, newurl)


def _download_one(directory: Path, spec: dict, opener) -> dict:
    url = f"https://huggingface.co/{MODEL_ID}/resolve/{REVISION}/{spec['file']}"
    request = urllib.request.Request(url, headers={
        "User-Agent": "MR09-OLMoE-research/1.0", "Accept-Encoding": "identity",
    })
    descriptor, name = tempfile.mkstemp(prefix=".mr09-olmoe-partial-", dir=directory)
    partial = Path(name)
    # A failed transfer remains a private partial plus the failed acquisition
    # reservation. Neither is accepted by verify(); there is no blind resume.
    with os.fdopen(descriptor, "wb") as output, opener.open(request, timeout=90) as response:
        if response.status != 200:
            raise ValueError("full artifact HTTP 200 required")
        if response.headers.get("Content-Encoding", "identity") != "identity":
            raise ValueError("encoded artifact response rejected")
        lengths = response.headers.get_all("Content-Length", [])
        if lengths and (len(lengths) != 1 or not lengths[0].isascii()
                        or not lengths[0].isdigit() or int(lengths[0]) != spec["bytes"]):
            raise ValueError("HTTP artifact length disagrees with pinned inventory")
        size = 0
        while block := response.read(min(CHUNK, spec["bytes"] - size + 1)):
            size += len(block)
            if size > spec["bytes"]:
                raise ValueError("artifact exceeds pinned length")
            if output.write(block) != len(block):
                raise OSError("short artifact write")
        if size != spec["bytes"]:
            raise ValueError("artifact transfer is incomplete")
        output.flush()
        os.fsync(output.fileno())
    observed = verify_file(partial, spec)
    # Atomic no-replace publication; no rename-over-existing fallback or second copy.
    # An unavailable hard-link facility/collision retains the verified private file.
    os.link(partial, directory / spec["file"])
    partial.unlink()
    return observed


def acquire(directory: Path, authorization_reference: str) -> dict:
    plan = load_plan()
    reference(authorization_reference)
    directory = external_directory(directory, create=True)
    _check_names(directory)
    specs = inventory(plan)
    existing = {}
    # Validate every prior file before creating a transfer or contacting the publisher.
    for spec in specs:
        if os.path.lexists(directory / spec["file"]):
            existing[spec["file"]] = verify_file(directory / spec["file"], spec)
    free = shutil.disk_usage(directory).free
    if free < plan["screens"]["minimum_available_storage_bytes"]:
        raise ValueError("fresh 28 GiB available-storage screen failed; no download")
    claim = {"operation": "serial_fixed_inventory_acquisition", "attempt_id": str(uuid.uuid4()),
             "plan_sha256": PLAN_SHA256, "authorization_reference": authorization_reference,
             "started_utc": datetime.now(timezone.utc).isoformat()}
    with reservation(directory / LOCK, claim):
        # The lock winner revalidates names and bytes; an earlier winner cannot race reuse.
        _check_names(directory, locked=True)
        opener = urllib.request.build_opener(HTTPSRedirects())
        observed = []
        for spec in specs:
            path = directory / spec["file"]
            item = (verify_file(path, spec) if os.path.lexists(path)
                    else _download_one(directory, spec, opener))
            observed.append(item)
    result = verify(directory)
    if result["artifacts"] != observed:
        raise ValueError("artifact set changed at publication boundary")
    result.update(authorization_reference=authorization_reference,
                  authorization_scope="operator-supplied reference; not authenticated by this utility",
                  available_storage_before_bytes=free, reused_files=sorted(existing),
                  publication="verified_same_directory_link_then_unlink_without_replacement",
                  hub_cache_used=False, acquisition_attempt=claim["attempt_id"])
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("plan", "verify", "download"))
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--authorization-reference")
    args = parser.parse_args(argv)
    try:
        plan = load_plan()
        if args.operation == "plan":
            if any(x is not None for x in (args.model_dir, args.output, args.authorization_reference)):
                raise ValueError("plan is offline and takes no artifact/output/admission arguments")
            print(json.dumps({"plan_sha256": PLAN_SHA256, "model": plan["model"],
                              "files": list(FILES), "loader": plan["loader"],
                              "screens": plan["screens"], "status": "unexecuted"}, indent=2))
            return 0
        if args.model_dir is None or args.output is None:
            raise ValueError("model directory and fresh external output required")
        directory = external_directory(args.model_dir, create=args.operation == "download")
        output = fresh_output(args.output, directory)
        if args.operation == "download":
            result = acquire(directory, args.authorization_reference)
        else:
            if args.authorization_reference is not None:
                raise ValueError("offline verification does not take an acquisition reference")
            result = verify(directory)
        publish_result(output, json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"status": result["status"], "files": len(result["artifacts"])}))
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        # Avoid reflecting transport URLs, private paths or tokens into portable logs.
        print(json.dumps({"status": "operation_error", "error_type": type(error).__name__,
                          "reason": "artifact/control operation failed; retained attempts require review"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
