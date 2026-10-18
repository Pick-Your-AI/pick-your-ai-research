"""Synthetic CD-7 exact local snapshot resolution, not a migration or release.

The archive contains schema-valid frozen-format fixture bytes. Proposed pins
live in a separate x_t0_* sidecar bound to the original build bytes. Resolving
catalog membership does not establish support, rights, prices or full replay.
"""

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_research import SCHEMAS, intake_json, schema_errors
from selection_quantifier_prototype import Selection, validate_identities

PIN_SCHEMA = json.loads((ROOT / "tests/fixtures/t0-revision-locks.schema.json").read_text())
PIN_VALIDATOR = Draft202012Validator(PIN_SCHEMA)
ARTIFACT_SCHEMAS = {
    "catalog_snapshot": "catalog-snapshot.schema.json",
    "pricebook": "pricebook.schema.json",
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    if type(raw) is not bytes:
        raise ValueError("retained documents must be UTF-8 bytes")
    return intake_json(raw.decode("utf-8"))


def validate_document(raw, schema_name):
    document = decode(raw)
    errors = schema_errors(document, SCHEMAS[schema_name])
    if errors:
        raise ValueError("invalid retained document: " + errors[0])
    # JSON Schema treats 1.0 as an integer. Revision identities in this
    # candidate require the JSON integer representation, without coercion.
    if type(document["revision"]) is not int:
        raise ValueError("revision must use a JSON integer")
    return document


@dataclass(frozen=True)
class Binding:
    kind: str
    id: str
    revision: int | None
    status: str
    raw: bytes | None = None


@dataclass(frozen=True)
class SelectedItem:
    selection_id: str
    status: str
    item: dict | None = None


@dataclass(frozen=True)
class Resolution:
    original_bytes: bytes
    catalog_snapshot: Binding
    pricebook: Binding | None
    selections: tuple[SelectedItem, ...]


class SnapshotArchive:
    """Admit immutable fixture artifacts; look up only an exact kind/id/revision.

    The archive never chooses latest, retrieves a URL, or writes a document.
    Same-key duplicates are rejected even when byte-identical. The synthetic
    next-version membership experiment allows several versions of one item ID;
    frozen research intake's one-version-per-ID policy is unchanged.
    """

    def __init__(self, artifacts):
        records = {}
        for kind, raw in artifacts:
            if kind not in ARTIFACT_SCHEMAS:
                raise ValueError("unsupported artifact kind")
            document = validate_document(raw, ARTIFACT_SCHEMAS[kind])
            entries, identities = (document["items"] if kind == "catalog_snapshot"
                                   else document["rates"]), set()
            for entry in entries:
                identity = ((entry["id"], entry["version"]) if kind == "catalog_snapshot"
                            else entry["id"])
                if identity in identities:
                    raise ValueError("duplicate artifact member identity")
                identities.add(identity)
            key = (kind, document["id"], document["revision"])
            if key in records:
                raise ValueError("duplicate immutable artifact key")
            records[key] = raw
        self._records = records

    def _bind(self, kind, identity, pin):
        if pin is None:
            return Binding(kind, identity, None, "revision_pin_missing")
        if pin["id"] != identity:
            raise ValueError("sidecar pin disagrees with the build's artifact ID")
        raw = self._records.get((kind, identity, pin["revision"]))
        if raw is None:
            return Binding(kind, identity, pin["revision"], "pinned_revision_unavailable")
        if digest(raw) != pin["sha256"]:
            return Binding(kind, identity, pin["revision"], "content_digest_mismatch")
        return Binding(kind, identity, pin["revision"], "resolved", raw)

    def resolve(self, original_bytes, sidecar_bytes=None):
        build = validate_document(original_bytes, "build.schema.json")
        validate_identities(tuple(Selection(s["id"], s["kind"], s["role"], s["enabled"])
                                  for s in build["selections"]))
        pins = {}
        if sidecar_bytes is not None:
            sidecar = decode(sidecar_bytes)
            try:
                PIN_VALIDATOR.validate(sidecar)
            except ValidationError as error:
                raise ValueError("invalid CD-7 pins: " + error.message) from error
            proposal = sidecar["x_t0_revision_locks"]
            if proposal["build_sha256"] != digest(original_bytes):
                raise ValueError("sidecar belongs to different build bytes")
            pins = proposal["artifacts"]
            if any(type(pin["revision"]) is not int for pin in pins.values()):
                raise ValueError("pin revision must use a JSON integer")
        locks = build["locks"]
        catalog = self._bind("catalog_snapshot", locks["catalog_snapshot_id"],
                             pins.get("catalog_snapshot"))
        if "pricebook_id" in locks:
            pricebook = self._bind("pricebook", locks["pricebook_id"], pins.get("pricebook"))
        else:
            if "pricebook" in pins:
                raise ValueError("sidecar cannot add a pricebook absent from the build")
            pricebook = None
        items = ({(item["id"], item["version"]): item for item in decode(catalog.raw)["items"]}
                 if catalog.raw is not None else {})
        selected = []
        for selection in build["selections"]:
            item = None
            if not selection["enabled"]:
                status = "not_enabled"
            elif catalog.raw is None:
                status = "snapshot_unresolved"
            else:
                item = items.get((selection["catalog_item_id"], selection["catalog_item_version"]))
                if item is None:
                    status = "selected_version_absent"
                elif item["kind"] != selection["kind"]:
                    status, item = "selected_kind_mismatch", None
                else:
                    status = "resolved"
            # Reparse retained bytes per resolution; output mutations cannot
            # change later reads or the artifact's immutable content identity.
            selected.append(SelectedItem(selection["id"], status, deepcopy(item)))
        return Resolution(original_bytes, catalog, pricebook, tuple(selected))
