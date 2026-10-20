"""Check offline MR09 OLMoE planning consistency; never fetch or load a model."""
import argparse
from datetime import date, datetime, timedelta
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLAN = Path("research/market/measurements/mr09-olmoe-artifact-copy-plan-v1.json")
HISTORICAL_PLAN = Path("research/market/measurements/mr09-moe-plan.json")
SCHEMA = Path("schemas/mr09-olmoe-artifact-copy-plan.schema.json")
MAX_JSON_BYTES = 1024 * 1024
GIB = 1024 ** 3


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(path):
    """Integer tokens only, unique object keys, strict UTF-8 and bounded input."""
    path = Path(path)
    require(path.is_file(), f"not a regular JSON file: {path}")
    with path.open("rb") as source:
        raw = source.read(MAX_JSON_BYTES + 1)
    require(len(raw) <= MAX_JSON_BYTES, f"JSON exceeds {MAX_JSON_BYTES} bytes: {path}")

    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_number(token):
        raise ValueError(f"only integer JSON number tokens are allowed: {token}")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=object_pairs,
                      parse_float=reject_number, parse_constant=reject_number)


def reject_float_values(value):
    # The Python entry point has the same policy as the text reader, including
    # integral floats. JSON Schema alone treats 1.0 as an integer value.
    require(not isinstance(value, float), "floating-point values are not allowed")
    if isinstance(value, dict):
        for child in value.values():
            reject_float_values(child)
    elif isinstance(value, list):
        for child in value:
            reject_float_values(child)


def schema_check(value, schema, label):
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        first = errors[0]
        location = "/".join(map(str, first.absolute_path))
        raise ValueError(f"{label}/{location}: {first.message}")


def named_rows(rows, field, expected, label):
    names = [row[field] for row in rows]
    require(len(names) == len(set(names)), f"{label}: duplicate {field}")
    require(set(names) == set(expected), f"{label}: incomplete or unexpected inventory")
    return dict(zip(names, rows))


def validate_plan(plan, root=ROOT):
    """Validate submitted metadata/allowances, not their external truth or fit."""
    root = Path(root).resolve()
    reject_float_values(plan)
    schema = strict_json(root / SCHEMA)
    schema_check(plan, schema, "plan")

    def inventory(field, key):
        spec = schema["properties"][field]
        return named_rows(plan[field], key, spec["items"]["properties"][key]["enum"], field)

    shards = inventory("weight_shards", "file")
    metadata = inventory("metadata_files", "file")
    cells = inventory("cells", "id")
    source_spec = schema["properties"]["loader"]["properties"]["source_files"]
    named_rows(plan["loader"]["source_files"], "path",
               source_spec["items"]["properties"]["path"]["enum"], "loader source files")

    access_date = date.fromisoformat(plan["access_date"])
    instant = plan["metadata_observation"]["api_observed_at"]
    require(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
                         r"(?:\.[0-9]{1,6})?(?:Z|\+00:00)", instant) is not None,
            "metadata observation needs an exact UTC timestamp")
    observed_at = datetime.fromisoformat(instant)
    require(observed_at.utcoffset() == timedelta(0) and observed_at.date() == access_date,
            "metadata observation and access date disagree")

    manifest_schema = strict_json(root / "schemas/evidence-manifest.schema.json")
    evidence_root = (root / "evidence").resolve()
    for filename, shard in shards.items():
        number = int(filename.split("-")[1])
        expected_manifest = f"mr09-olmoe-0924-instruct-shard-{number:02}.json"
        require(shard["external_manifest"] == expected_manifest,
                f"{filename}: wrong external manifest")
        manifest_path = (evidence_root / expected_manifest).resolve()
        require(manifest_path.parent == evidence_root, "external manifest escaped evidence directory")
        manifest = strict_json(manifest_path)
        schema_check(manifest, manifest_schema, expected_manifest)
        expected = {
            "id": Path(expected_manifest).stem,
            "version": plan["model"]["revision"],
            "sha256": shard["publisher_sha256"],
            "uri": (f"https://huggingface.co/{plan['model']['id']}/resolve/"
                    f"{plan['model']['revision']}/{filename}"),
        }
        for field, value in expected.items():
            require(manifest[field] == value, f"{expected_manifest}: {field} differs from plan")

    for filename, entry in metadata.items():
        metadata_only = filename == "tokenizer.json"
        require((entry["observed_sha256"] is None) == metadata_only,
                f"{filename}: incorrect local checksum observation scope")
        expected = ("publisher_git_metadata_only" if metadata_only
                    else "small_file_read_and_git_blob_matched")
        require(entry["observation"] == expected, f"{filename}: incorrect metadata observation scope")

    geometry = plan["geometry"]
    layers, hidden = geometry["layers"], geometry["hidden_size"]
    experts, width = geometry["experts"], geometry["intermediate_size"]
    # Untied embeddings/head; three expert projections; Q/K/V/O projections;
    # router; input/post-attention/Q/K norms; and one final norm.
    elements = (2 * geometry["vocabulary_size"] * hidden + layers *
                (3 * experts * hidden * width + 4 * hidden * hidden +
                 experts * hidden + 4 * hidden) + hidden)
    weight_bytes = sum(shard["bytes"] for shard in shards.values())
    metadata_bytes = sum(entry["bytes"] for entry in metadata.values())
    payload_bytes = 2 * elements
    expected_totals = {
        "stored_parameter_elements": elements,
        "index_tensor_count": layers * experts * 3 + layers * 9 + 3,
        "expert_projection_tensor_count": layers * experts * 3,
        "tensor_payload_bytes": payload_bytes,
        "weight_file_bytes": weight_bytes,
        "file_header_overhead_bytes": weight_bytes - payload_bytes,
        "metadata_file_bytes": metadata_bytes,
        "load_artifact_bytes": weight_bytes + metadata_bytes,
        "largest_shard_bytes": max(shard["bytes"] for shard in shards.values()),
    }
    for field, value in expected_totals.items():
        require(plan["totals"][field] == value, f"totals/{field}: inconsistent arithmetic")

    historical = strict_json(root / HISTORICAL_PLAN)
    require(historical["model_id"] == plan["model"]["id"] and
            historical["revision"] == plan["model"]["revision"], "historical model pin differs")
    require(historical["publisher_metadata"]["parameter_elements"] == elements and
            historical["publisher_metadata"]["weight_index_tensor_bytes"] == payload_bytes,
            "historical tensor payload differs")
    prior_cells = named_rows(historical["planned_cells"], "id", cells, "historical cells")
    cache_names = {"bf16": "bf16",
                   "int4 if supported; otherwise unsupported outcome": "int4_if_supported"}
    kv_per_position = (2 * layers * geometry["kv_heads"] * geometry["head_dim"] * 2)
    for ident, cell in cells.items():
        prior = prior_cells[ident]
        for field in ("prompt_tokens", "decode_forwards", "active_sequences"):
            require(cell[field] == prior[field], f"{ident}/{field}: historical workload changed")
        require(prior["kv"] in cache_names, f"{ident}: unrecognized historical cache policy")
        expected_cache = cache_names[prior["kv"]]
        require(cell["kv_cache"] == expected_cache, f"{ident}: historical cache policy changed")
        positions = cell["prompt_tokens"] + cell["decode_forwards"]
        require(cell["terminal_cache_positions_per_sequence"] == positions and
                positions <= geometry["max_positions"], f"{ident}: incorrect terminal cache positions")
        kv = kv_per_position * positions * cell["active_sequences"] if expected_cache == "bf16" else None
        floor = payload_bytes + kv if kv is not None else None
        require(cell["derived_bf16_kv_payload_bytes"] == kv and
                cell["derived_weights_plus_kv_floor_bytes"] == floor,
                f"{ident}: wrong derived floor or invented unsupported cache result")

    screens = plan["screens"]
    lower_bounds = {
        "complete_artifact_copies": 2,
        "storage_reserve_bytes": 2 * GIB,
        "host_file_mapping_allowance_bytes": weight_bytes,
        "host_parameter_allowance_bytes": payload_bytes,
        # Packed gate+up for one layer; source stack/cat overlap is separate
        # from the complete parameter and file-mapping allowances.
        "host_conversion_allowance_bytes": experts * hidden * (2 * width) * 2,
        "host_process_reserve_bytes": 4 * GIB,
    }
    for field, minimum in lower_bounds.items():
        require(screens[field] >= minimum, f"screens/{field}: below selected design allowance")
    storage = (screens["complete_artifact_copies"] * expected_totals["load_artifact_bytes"] +
               screens["storage_reserve_bytes"])
    host = sum(screens[key] for key in ("host_file_mapping_allowance_bytes",
               "host_parameter_allowance_bytes", "host_conversion_allowance_bytes", "host_process_reserve_bytes"))
    require(screens["storage_budget_bytes"] == storage, "storage budget arithmetic differs")
    require(screens["host_budget_bytes"] == host, "host budget arithmetic differs")
    require(screens["minimum_available_storage_bytes"] >= storage,
            "available-storage screen is below the planned budget")
    require(screens["minimum_available_host_bytes"] >= host,
            "available-host screen is below the planned budget")
    return {"classification": plan["classification"], "execution_status": plan["execution_status"],
            "load_artifact_bytes": expected_totals["load_artifact_bytes"],
            "storage_budget_bytes": storage, "host_budget_bytes": host}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=ROOT / PLAN,
                        help="local candidate JSON; manifests and schemas remain repository-pinned")
    args = parser.parse_args(argv)
    try:
        result = validate_plan(strict_json(args.plan))
    except (ValueError, OSError, RecursionError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    print("Validated metadata/copy-plan consistency only; no weight verification, runtime fit or measurement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
