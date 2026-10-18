"""Test-only native CD-7 inspection envelope, not a publisher or production gate.

Reuse the exact-byte archive from CD-7. A complete pair here means immutable
identity and catalog/rate membership only; source use remains unqualified.
"""

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import unicodedata

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from t0_revision_lock_prototype import (
    ARTIFACT_SCHEMAS, PIN_SCHEMA, SnapshotArchive, decode, digest,
    validate_document,
)
from validate_research import SCHEMAS, price_instant

ROOT = Path(__file__).resolve().parents[1]
VERSION = "cd7-consumer-0.1"
MAX_REVISION = 2**63 - 1
DEFAULT_ARTIFACT_BYTES = 512 * 1024
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024
MAX_ENVELOPE_BYTES = 64 * 1024
MAX_DEPTH, MAX_NODES = 48, 16384
SCHEMA = json.loads((ROOT / "tests/fixtures/t0-cd7-consumer.schema.json").read_text())
# Add whole-string bounds only where a frozen schema declares one of these two
# ID patterns. Catalog reference fields also inline the entity pattern. This
# private validation view never rewrites a frozen schema or an artifact value.
ID_PATTERNS = {
    "^[a-z][a-z0-9._:-]{2,119}$": "[^a-z0-9._:-]",
    "^[a-z][a-z0-9_-]{2,79}$": "[^a-z0-9_-]",
}


def identity_profile(schema):
    schema = deepcopy(schema)
    pending = [schema]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            pattern = node.get("pattern")
            if isinstance(pattern, str) and pattern in ID_PATTERNS:
                node.setdefault("allOf", []).append({"not": {"pattern": ID_PATTERNS[pattern]}})
            pending.extend(node.values())
        elif isinstance(node, list):
            pending.extend(node)
    return schema


PROFILE_SCHEMAS = {name: identity_profile(schema) for name, schema in SCHEMAS.items()}
REGISTRY = Registry().with_resources(
    [(schema["$id"], Resource.from_contents(schema)) for schema in PROFILE_SCHEMAS.values()]
    + [("urn:pick-your-ai:cd7-pins:0.1", Resource.from_contents(PIN_SCHEMA))]
)
VALIDATOR = Draft202012Validator(SCHEMA, registry=REGISTRY, format_checker=FormatChecker())
DOCUMENT_VALIDATORS = {
    name: Draft202012Validator(PROFILE_SCHEMAS[name], registry=REGISTRY)
    for name in (*ARTIFACT_SCHEMAS.values(), "build.schema.json")
}


class ConsumerError(ValueError):
    """Machine-readable boundary failure; it never substitutes artifact values."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def encoded(value):
    """Only envelope output is serialized; retained documents are never rewritten."""
    return json.dumps(value, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":"), sort_keys=True).encode("utf-8")


def bounded_json(raw, byte_limit):
    if type(raw) is not bytes:
        raise ConsumerError("malformed_document")
    if len(raw) > byte_limit:
        raise ConsumerError("byte_limit_exceeded")
    try:
        value = decode(raw)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ConsumerError("malformed_document") from error
    pending, nodes = [(value, 1)], 0
    while pending:
        child, depth = pending.pop()
        nodes += 1
        if depth > MAX_DEPTH or nodes > MAX_NODES:
            raise ConsumerError("structure_limit_exceeded")
        strings = list(child) if isinstance(child, dict) else [child] if isinstance(child, str) else []
        if any(0xD800 <= ord(character) <= 0xDFFF for string in strings for character in string):
            raise ConsumerError("unicode_scalar_unsupported")
        if isinstance(child, dict):
            # Swift String keys compare canonically equivalent Unicode alike.
            # Reject that ambiguity without normalizing retained bytes or keys.
            keys = [unicodedata.normalize("NFC", key) for key in child]
            if len(keys) != len(set(keys)):
                raise ConsumerError("ambiguous_object_keys")
        children = (child.values() if isinstance(child, dict)
                    else child if isinstance(child, list) else ())
        pending.extend((entry, depth + 1) for entry in children)
    return value


def capture_timestamp(value):
    """Check the explicit ASCII Gregorian/RFC-3339 subset without format extras."""
    try:
        # Reuse the existing intake profile: years 0001..9999, seconds 00..59,
        # explicit offset, arbitrary fractional digits, and no normalization.
        price_instant(value)
    except (TypeError, ValueError) as error:
        raise ConsumerError("artifact_representation_unsupported") from error


def artifact_fields(document, kind):
    capture_timestamp(document["captured_at"])
    if any(DOCUMENT_VALIDATORS[ARTIFACT_SCHEMAS[kind]].iter_errors(document)):
        raise ConsumerError("artifact_representation_unsupported")


def wire(raw, wrapper):
    value = bounded_json(raw, MAX_ENVELOPE_BYTES)
    if not isinstance(value, dict) or not isinstance(value.get(wrapper), dict):
        raise ConsumerError("malformed_envelope")
    packet = value[wrapper]
    if packet.get("protocol_version") != VERSION:
        raise ConsumerError("unsupported_protocol_version")
    # JSON Schema accepts 1.0 as integer. This NEW wire profile requires the
    # integer token representation and does not redefine frozen-v1 semantics.
    pending = [packet]
    while pending:
        child = pending.pop()
        if isinstance(child, dict):
            for key, entry in child.items():
                if key in {"revision", "byte_length", "max_artifact_bytes"} and type(entry) is not int:
                    raise ConsumerError("integer_representation_unsupported")
                if key == "schema_version" and entry != "1.0.0":
                    raise ConsumerError("unsupported_schema_version")
                if key == "captured_at" and isinstance(entry, str):
                    capture_timestamp(entry)
            pending.extend(child.values())
        elif isinstance(child, list):
            pending.extend(child)
    if list(VALIDATOR.iter_errors(value)):
        raise ConsumerError("malformed_envelope")
    return packet


def request(build_bytes, sidecar_bytes=None, max_artifact_bytes=DEFAULT_ARTIFACT_BYTES):
    if type(build_bytes) is not bytes or (sidecar_bytes is not None and type(sidecar_bytes) is not bytes):
        raise ConsumerError("malformed_document")
    raw = encoded({"x_t0_cd7_consumer": {
        "protocol_version": VERSION, "build_sha256": digest(build_bytes),
        "sidecar_sha256": digest(sidecar_bytes) if sidecar_bytes is not None else None,
        "max_artifact_bytes": max_artifact_bytes,
    }})
    wire(raw, "x_t0_cd7_consumer")
    return raw


def _inputs(request_bytes, build_bytes, sidecar_bytes):
    packet = wire(request_bytes, "x_t0_cd7_consumer")
    if type(build_bytes) is not bytes or (sidecar_bytes is not None and type(sidecar_bytes) is not bytes):
        raise ConsumerError("malformed_document")
    if packet["build_sha256"] != digest(build_bytes):
        raise ConsumerError("request_build_mismatch")
    if packet["sidecar_sha256"] != (digest(sidecar_bytes) if sidecar_bytes is not None else None):
        raise ConsumerError("request_sidecar_mismatch")
    bounded_json(build_bytes, packet["max_artifact_bytes"])
    if sidecar_bytes is not None:
        bounded_json(sidecar_bytes, MAX_ENVELOPE_BYTES)
    return packet


def _descriptor(binding):
    document = decode(binding.raw)
    sha256 = digest(binding.raw)
    return {"kind": binding.kind,
            **{key: document[key] for key in ("schema_version", "id", "revision", "captured_at")},
            "sha256": sha256, "byte_length": len(binding.raw),
            "retrieval_path": "/artifacts/sha256/" + sha256 + ".json"}


def _binding(binding, limit, dispositions):
    if binding is None:
        return None, None
    if binding.revision is not None and binding.revision > MAX_REVISION:
        binding = replace(binding, status="native_revision_unsupported", raw=None)
    elif binding.revision is not None:
        # Dispositions are supplied by an external adapter for this EXACT pin.
        # They can only withhold bytes. They never grant publication authority.
        key = (binding.kind, binding.id, binding.revision)
        if key in dispositions and binding.status != "content_digest_mismatch":
            binding = replace(binding, status=dispositions[key], raw=None)
    if binding.raw is not None:
        try:
            document = bounded_json(binding.raw, limit)
            artifact_fields(document, binding.kind)
        except ConsumerError as error:
            status = ("artifact_too_large" if error.code == "byte_limit_exceeded"
                      else "artifact_representation_unsupported" if error.code == "artifact_representation_unsupported"
                      else "artifact_structure_unsupported")
            binding = replace(binding, status=status, raw=None)
    result = {"id": binding.id, "status": binding.status}
    if binding.revision is not None and binding.status != "native_revision_unsupported":
        result["revision"] = binding.revision
    if binding.raw is not None:
        result["artifact"] = _descriptor(binding)
    return binding, result


def pair_identity(catalog_descriptor, pricebook_descriptor):
    # Fixed two-key JSON, ASCII escaped, sorted keys and compact separators.
    # Includes all descriptor metadata and exact byte digests, in fixed roles.
    return digest((VERSION + "\n").encode("ascii") +
                  encoded({"catalog_snapshot": catalog_descriptor,
                           "pricebook": pricebook_descriptor}))


def inspect(archive, request_bytes, build_bytes, sidecar_bytes=None, *, dispositions=None):
    """Serialize CD-7 results. No network, migration, cache write or approval."""
    packet = _inputs(request_bytes, build_bytes, sidecar_bytes)
    dispositions = {} if dispositions is None else dict(dispositions)
    if any(type(key) is not tuple or len(key) != 3 or key[0] not in ARTIFACT_SCHEMAS
           or type(key[1]) is not str or type(key[2]) is not int or key[2] < 1
           or status not in {"revoked", "temporarily_unavailable"}
           for key, status in dispositions.items()):
        raise ConsumerError("invalid_disposition")
    try:
        resolution = archive.resolve(build_bytes, sidecar_bytes)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ConsumerError("invalid_cd7_input") from error
    build = decode(build_bytes)
    if any(DOCUMENT_VALIDATORS["build.schema.json"].iter_errors(build)):
        raise ConsumerError("invalid_cd7_input")
    if build["revision"] > MAX_REVISION or build["locks"]["dependency_graph_revision"] > MAX_REVISION:
        raise ConsumerError("native_revision_unsupported")
    catalog, catalog_result = _binding(resolution.catalog_snapshot, packet["max_artifact_bytes"], dispositions)
    prices, prices_result = _binding(resolution.pricebook, packet["max_artifact_bytes"], dispositions)
    selected = []
    for selection in resolution.selections:
        status = selection.status
        if status != "not_enabled" and catalog.raw is None:
            status = "snapshot_unresolved"
        item = {"selection_id": selection.selection_id, "status": status}
        if status == "resolved":
            item["catalog_item"] = {key: selection.item[key] for key in ("id", "version", "kind")}
        selected.append(item)
    pair = {"status": "incomplete"}
    if prices is None:
        pair = {"status": "pricebook_absent"}
    elif catalog.raw is not None and prices.raw is not None:
        members = {(item["id"], item["version"]) for item in decode(catalog.raw)["items"]}
        unmatched = sorted(rate["id"] for rate in decode(prices.raw)["rates"]
                           if (rate["catalog_item_id"], rate["catalog_item_version"]) not in members)
        pair = ({"status": "rate_catalog_mismatch", "unmatched_rate_ids": unmatched} if unmatched
                else {"status": "resolved", "identity": pair_identity(catalog_result["artifact"], prices_result["artifact"])})
    result = {"x_t0_cd7_consumer_result": {
        "protocol_version": VERSION, "request_sha256": digest(request_bytes),
        "build_sha256": digest(build_bytes),
        "bindings": {"catalog_snapshot": catalog_result, "pricebook": prices_result},
        "selections": selected, "pair": pair,
        "qualification": {"publication": "not_established", "source_use": "not_established"},
    }}
    raw = encoded(result)
    wire(raw, "x_t0_cd7_consumer_result")
    return raw


def verify_complete_pair(response_bytes, request_bytes, build_bytes, sidecar_bytes, artifacts):
    """Recheck received bytes before a caller's atomic PREVIEW cache activation.

    Return an immutable complete pair only after all checks pass. This function
    neither mutates a cache nor authorizes production use. The caller must keep
    its prior complete pair on any exception, cancellation or failed approval.
    """
    packet = _inputs(request_bytes, build_bytes, sidecar_bytes)
    result = wire(response_bytes, "x_t0_cd7_consumer_result")
    if result["request_sha256"] != digest(request_bytes) or result["build_sha256"] != digest(build_bytes):
        raise ConsumerError("response_request_mismatch")
    if result["pair"]["status"] != "resolved":
        raise ConsumerError("pair_unresolved")
    if set(artifacts) != set(ARTIFACT_SCHEMAS):
        raise ConsumerError("complete_pair_required")
    for kind, raw in artifacts.items():
        binding = result["bindings"][kind]
        if binding is None or binding["status"] != "resolved":
            raise ConsumerError("pair_unresolved")
        descriptor = binding["artifact"]
        if descriptor["byte_length"] > packet["max_artifact_bytes"]:
            raise ConsumerError("byte_limit_exceeded")
        if type(raw) is not bytes or len(raw) != descriptor["byte_length"]:
            raise ConsumerError("content_length_mismatch")
        if digest(raw) != descriptor["sha256"]:
            raise ConsumerError("content_digest_mismatch")
        document = bounded_json(raw, packet["max_artifact_bytes"])
        if isinstance(document, dict) and document.get("schema_version") != "1.0.0":
            raise ConsumerError("unsupported_schema_version")
        try:
            validate_document(raw, ARTIFACT_SCHEMAS[kind])
        except ValueError as error:
            raise ConsumerError("invalid_artifact_document") from error
        if document["revision"] > MAX_REVISION:
            raise ConsumerError("native_revision_unsupported")
        artifact_fields(document, kind)
    try:
        archive = SnapshotArchive(list(artifacts.items()))
    except ValueError as error:
        raise ConsumerError("invalid_artifact_document") from error
    expected = decode(inspect(archive, request_bytes, build_bytes, sidecar_bytes))
    if expected != decode(response_bytes):
        raise ConsumerError("response_artifact_mismatch")
    return (artifacts["catalog_snapshot"], artifacts["pricebook"])
