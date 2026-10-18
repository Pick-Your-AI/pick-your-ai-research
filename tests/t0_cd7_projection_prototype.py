"""Synthetic CD-7 redacted projection and fork draft, not a released Build.

The private factory may read a retained synthetic Build and its existing pins.
Transport accepts only the new, closed configuration-only envelopes. A new
digest binds the projection bytes; it authenticates neither their origin nor
the source's private inputs. No archive is fetched and no evaluation runs.
"""

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, ValidationError
from referencing import Resource

from t0_cd7_consumer_prototype import (
    ConsumerError, DEFAULT_ARTIFACT_BYTES, DOCUMENT_VALIDATORS,
    MAX_ENVELOPE_BYTES, MAX_REVISION, REGISTRY, bounded_json, encoded,
)
from t0_revision_lock_prototype import SnapshotArchive, digest
from selection_quantifier_prototype import Selection, validate_identities
from tests.t0_answer_state_prototype import AnswerIndex, ENCODING

VERSION = "cd7-projection-0.1"
PROJECTION = "x_t0_cd7_projection"
BINDING = "x_t0_cd7_projection_binding"
PUBLIC_SELECTION_FIELDS = ("id", "kind", "catalog_item_id", "catalog_item_version", "role", "enabled")
# Entire groups are omitted even when absent or apparently harmless in the
# source. This deliberately discloses neither presence nor private key names.
PRIVATE_BUILD_GROUPS = ("name", "owner_ref", "lifecycle", "created_at", "updated_at",
                        "objectives", "policy", "extensions")
PRIVATE_SELECTION_GROUPS = ("settings", "notes", "extensions")
QUALIFICATION = {"source_authenticity": "not_established", "source_use": "not_established",
                 "artifact_resolution": "not_established", "evaluation": "not_performed"}
SCHEMA = json.loads((Path(__file__).with_name("fixtures") / "t0-cd7-projection.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA, registry=REGISTRY.with_resource(
    "urn:pick-your-ai:cd1-answer-states:0.1", Resource.from_contents(ENCODING.schema)))


class ProjectionError(ValueError):
    """Stable boundary code without echoing private source values."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True, repr=False)
class ProjectionBytes:
    projection: bytes
    binding: bytes

    def __repr__(self):
        return "ProjectionBytes"


def _version(version):
    if type(version) is not str or version != VERSION:
        raise ProjectionError("unsupported_projection_version")


def _integer(value):
    if type(value) is not int or not 1 <= value <= MAX_REVISION:
        raise ProjectionError("integer_representation_unsupported")


def _decode(raw, limit):
    try:
        return bounded_json(raw, limit)
    except ConsumerError as error:
        raise ProjectionError(error.code) from None


def _envelope(raw, wrapper):
    document = _decode(raw, MAX_ENVELOPE_BYTES)
    if type(document) is not dict or type(document.get(wrapper)) is not dict:
        raise ProjectionError("malformed_projection_envelope")
    packet = document[wrapper]
    _version(packet.get("protocol_version"))
    # The public profile has no free-form settings. This scan additionally
    # rejects a secret locator disguised as a public version or decoded key.
    pending = [document]
    while pending:
        value = pending.pop()
        strings = list(value) if isinstance(value, dict) else [value] if isinstance(value, str) else []
        if any("secret://" in string.casefold() for string in strings):
            raise ProjectionError("secret_locator_forbidden")
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"revision", "dependency_graph_revision", "projection_byte_length"}:
                    _integer(child)
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    if next(VALIDATOR.iter_errors(document), None) is not None:
        raise ProjectionError("malformed_projection_envelope")
    return packet


def _answer_states(configuration, identity, state):
    answers = {}

    def provided(path, value):
        answers[path] = {"state": "provided", "value": deepcopy(value)}

    for key in ("id", "revision"):
        provided("/" + key, identity[key])
    for key in ("schema_version", "locks", "links"):
        provided("/" + key, configuration[key])
    for key in PRIVATE_BUILD_GROUPS:
        answers["/" + key] = {"state": state}
    for index, selection in enumerate(configuration["selections"]):
        prefix = f"/selections/{index}/"
        for key in PUBLIC_SELECTION_FIELDS:
            provided(prefix + key, selection[key])
        for key in PRIVATE_SELECTION_GROUPS:
            answers[prefix + key] = {"state": state}
    return {"x_t0_answer_states": {"proposal_version": "cd1-0.1", "answers": answers}}


def _check_semantics(packet):
    identity, source = packet["identity"], packet["source"]
    if packet["kind"] == "share":
        if identity != {key: source[key] for key in ("id", "revision")} or packet["parent_projection_sha256"] is not None:
            raise ProjectionError("projection_identity_mismatch")
        state = "withheld"
    else:
        if identity["id"] == source["id"] or identity["revision"] != 1 or packet["parent_projection_sha256"] is None:
            raise ProjectionError("fork_identity_mismatch")
        state = "missing"
    configuration = packet["configuration"]
    try:
        validate_identities(tuple(Selection(s["id"], s["kind"], s["role"], s["enabled"])
                                  for s in configuration["selections"]))
    except ValueError:
        raise ProjectionError("selection_identity_rejected") from None
    expected = _answer_states(configuration, identity, state)
    # Exact JSON types matter: True/1 and integer/float aliases cannot satisfy
    # a recomputed provided value or an omitted-state record.
    if encoded(packet["answer_states"]) != encoded(expected):
        raise ProjectionError("projection_answer_states_mismatch")
    AnswerIndex(encoded(expected))
    pins = packet["source_artifact_pins"]
    if source["sidecar_sha256"] is None and pins:
        raise ProjectionError("source_pins_without_sidecar")
    locks = configuration["locks"]
    for kind, pin in pins.items():
        if pin["id"] != locks.get(kind + "_id"):
            raise ProjectionError("source_pin_identity_mismatch")


def read_projection(version, projection_bytes, binding_bytes):
    """Verify new transport integrity and state semantics, without source authority.

    A self-consistent digest cannot prove who issued a projection or that its
    redaction came from the claimed private source. The qualification records
    retain that limit; this function never returns a Build or an assessment.
    """
    _version(version)
    packet = _envelope(projection_bytes, PROJECTION)
    binding = _envelope(binding_bytes, BINDING)
    if binding["projection_byte_length"] != len(projection_bytes):
        raise ProjectionError("projection_length_mismatch")
    if binding["projection_sha256"] != digest(projection_bytes):
        raise ProjectionError("projection_digest_mismatch")
    _check_semantics(packet)
    return packet


def projection_answers(version, projection_bytes, binding_bytes):
    """Use current typed CD-1 reads; omitted share/fork inputs remain unresolved."""
    packet = read_projection(version, projection_bytes, binding_bytes)
    return AnswerIndex(encoded(packet["answer_states"]))


def _pack(kind, identity, source, configuration, pins, parent=None):
    packet = {
        "protocol_version": VERSION, "profile": "configuration_only", "kind": kind,
        "identity": deepcopy(identity), "source": deepcopy(source),
        "source_artifact_pins": deepcopy(pins),
        "parent_projection_sha256": parent, "configuration": deepcopy(configuration),
        "answer_states": _answer_states(configuration, identity, "withheld" if kind == "share" else "missing"),
        "qualification": deepcopy(QUALIFICATION),
    }
    raw = encoded({PROJECTION: packet})
    bound = encoded({BINDING: {"protocol_version": VERSION,
                              "projection_sha256": digest(raw), "projection_byte_length": len(raw)}})
    read_projection(VERSION, raw, bound)
    return ProjectionBytes(raw, bound)


def create_projection(version, build_bytes, sidecar_bytes=None):
    """Private factory shared by share/export; only redacted envelopes leave it.

    Retained bytes stay unchanged. All settings, free text, workload groups,
    owner/lifecycle metadata and extensions are omitted. No opt-in group,
    history payload, price, credential locator or attestation is copied.
    """
    _version(version)
    build = _decode(build_bytes, DEFAULT_ARTIFACT_BYTES)
    try:
        DOCUMENT_VALIDATORS["build.schema.json"].validate(build)
    except ValidationError:
        raise ProjectionError("source_build_invalid") from None
    _integer(build["revision"])
    _integer(build["locks"]["dependency_graph_revision"])
    original_pins = _decode(sidecar_bytes, MAX_ENVELOPE_BYTES) if sidecar_bytes is not None else None
    try:
        # Empty archive: reuse existing source/pin/identity checks, but perform
        # no fetch, latest fallback or new artifact qualification.
        SnapshotArchive([]).resolve(build_bytes, sidecar_bytes)
    except ValueError:
        raise ProjectionError("source_binding_invalid") from None
    pins = original_pins["x_t0_revision_locks"]["artifacts"] if original_pins is not None else {}
    source = {"id": build["id"], "revision": build["revision"], "build_sha256": digest(build_bytes),
              "sidecar_sha256": digest(sidecar_bytes) if sidecar_bytes is not None else None}
    configuration = {key: deepcopy(build[key]) for key in ("schema_version", "locks", "links")}
    configuration["selections"] = [{key: deepcopy(selection[key]) for key in PUBLIC_SELECTION_FIELDS}
                                    for selection in build["selections"]]
    return _pack("share", {key: build[key] for key in ("id", "revision")}, source, configuration, pins)


# Both user actions must use identical default redaction, without an export
# bypass that includes credentials, private settings or organisation answers.
export_projection = create_projection


def fork_projection(version, projection_bytes, binding_bytes, *, new_build_id):
    """Create an unanswered revision-1 draft, without completing a frozen Build."""
    packet = read_projection(version, projection_bytes, binding_bytes)
    if packet["kind"] != "share":
        raise ProjectionError("fork_requires_share_projection")
    if type(new_build_id) is not str or re.fullmatch(r"[a-z][a-z0-9._:-]{2,119}", new_build_id) is None:
        raise ProjectionError("fork_identity_invalid")
    if new_build_id == packet["source"]["id"]:
        raise ProjectionError("fork_identity_mismatch")
    return _pack("fork_draft", {"id": new_build_id, "revision": 1}, packet["source"],
                 packet["configuration"], packet["source_artifact_pins"], digest(projection_bytes))
