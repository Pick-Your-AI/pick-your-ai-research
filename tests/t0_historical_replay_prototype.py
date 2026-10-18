"""Test-only CD-7 replay of a pinned frozen-v1 reference-evaluator report.

This checks retained-byte identity and deterministic reproduction, not publisher
authenticity, source-use rights, current compatibility, or estimator accuracy.
Only the allowlisted local evaluator can execute; archives contain JSON only.
"""

from dataclasses import dataclass
from decimal import (
    Context, DivisionByZero, InvalidOperation, Overflow, ROUND_HALF_EVEN,
    localcontext,
)
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator

from t0_cd7_consumer_prototype import (
    DEFAULT_ARTIFACT_BYTES, MAX_ENVELOPE_BYTES, MAX_REVISION,
    bounded_json, encoded,
)
from t0_revision_lock_prototype import (
    ARTIFACT_SCHEMAS, SnapshotArchive, decode, digest,
)
from validate_research import SCHEMAS, schema_errors

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = ROOT / "contracts/v1/reference/evaluate.py"
SCHEMA_DIRECTORY = ROOT / "contracts/v1/schemas"
PROFILE = "frozen-v1-reference-py312-decimal28"
EVALUATOR_SHA256 = "092c8a99495f9b5ae960df40b27e33f15eefe6d1a7cd80119658fdc79ada1a5a"
SCHEMAS_SHA256 = "eaaf51a04c9bd0c7fce23e7ecc75724226e26b337cc1da04b88a59d2a912914f"
SCHEMA = json.loads((ROOT / "tests/fixtures/t0-historical-replay.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
IDENTIFIER = re.compile(r"[a-z][a-z0-9._:-]{2,119}")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")
INPUT_SCHEMAS = {
    "ruleset": "ruleset.schema.json",
    "dependency_graph": "dependency-graph.schema.json",
    "resource_estimate": "resource-estimate.schema.json",
    "cost_estimate": "cost-estimate.schema.json",
    "evaluation_report": "evaluation-report.schema.json",
}
OPTIONAL_INPUTS = {"resource_estimate", "cost_estimate"}
MAX_RECORDS = 32
MAX_ARCHIVE_BYTES = 8 * 1024 * 1024


class ReplayError(ValueError):
    """Malformed/unbound caller input; no evaluator ran."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _integer(value):
    if type(value) is not int or not 1 <= value <= MAX_REVISION:
        raise ReplayError("integer_representation_unsupported")


def _identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ReplayError("identity_representation_unsupported")


def _document(raw, schema_name):
    document = bounded_json(raw, DEFAULT_ARTIFACT_BYTES)
    if schema_errors(document, SCHEMAS[schema_name]):
        raise ReplayError("invalid_retained_document")
    _identifier(document["id"])
    for name in ("revision", "build_revision", "dependency_graph_revision"):
        if name in document:
            _integer(document[name])
    if "build_id" in document:
        _identifier(document["build_id"])
    if schema_name == "ruleset.schema.json" and not VERSION.fullmatch(document["version"]):
        raise ReplayError("identity_representation_unsupported")
    if schema_name == "build.schema.json":
        locks = document["locks"]
        for name in ("catalog_snapshot_id", "ruleset_id", "dependency_graph_id", "pricebook_id"):
            if name in locks:
                _identifier(locks[name])
        _integer(locks["dependency_graph_revision"])
        if not VERSION.fullmatch(locks["ruleset_version"]):
            raise ReplayError("identity_representation_unsupported")
    return document


def _key(kind, document):
    if kind == "ruleset":
        return kind, document["id"], document["version"]
    if kind == "dependency_graph":
        return kind, document["id"], document["revision"]
    return kind, document["id"], document["build_id"], document["build_revision"]


def _manifest(raw):
    value = bounded_json(raw, MAX_ENVELOPE_BYTES)
    if list(VALIDATOR.iter_errors(value)):
        raise ReplayError("invalid_replay_manifest")
    packet = value["x_t0_historical_replay"]
    for pin in packet["inputs"].values():
        if pin is not None:
            for name in ("revision", "build_revision"):
                if name in pin:
                    _integer(pin[name])
    return packet


def _local_evaluator(pin):
    """Load verified local bytes, never a path or executable supplied in a pin."""
    if (pin["profile"] != PROFILE or pin["sha256"] != EVALUATOR_SHA256
            or pin["schemas_sha256"] != SCHEMAS_SHA256):
        raise ReplayError("evaluator_pin_unsupported")
    if sys.version_info[:2] != (3, 12):
        raise ReplayError("interpreter_profile_unsupported")
    try:
        source = EVALUATOR_PATH.read_bytes()
        schema_bytes = {path.name: path.read_bytes()
                        for path in sorted(SCHEMA_DIRECTORY.glob("*.schema.json"))}
    except OSError as error:
        raise ReplayError("local_evaluator_or_schemas_unavailable") from error
    if digest(source) != EVALUATOR_SHA256:
        raise ReplayError("local_evaluator_digest_mismatch")
    rows = [(name, digest(raw)) for name, raw in schema_bytes.items()]
    bundle = json.dumps(rows, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    if digest(bundle) != SCHEMAS_SHA256:
        raise ReplayError("local_schema_digest_mismatch")
    if (set(schema_bytes) != set(SCHEMAS)
            or any(encoded(decode(raw)) != encoded(SCHEMAS[name])
                   for name, raw in schema_bytes.items())):
        raise ReplayError("loaded_schema_digest_mismatch")
    namespace = {"__name__": "_cd7_frozen_replay", "__file__": str(EVALUATOR_PATH)}
    # Compile the very bytes just checked, avoiding a second source-file read.
    exec(compile(source, str(EVALUATOR_PATH), "exec"), namespace)
    return namespace["Evaluator"]


@dataclass(frozen=True)
class ReplayBinding:
    kind: str
    status: str
    raw: bytes | None = None


@dataclass(frozen=True)
class ReplayResult:
    status: str
    issues: tuple[tuple[str, str], ...]
    bindings: tuple[ReplayBinding, ...]
    original_build_bytes: bytes
    original_sidecar_bytes: bytes | None
    original_manifest_bytes: bytes
    generated_report: dict | None = None

    @property
    def qualification(self):
        return {"authenticity": "not_established", "source_use": "not_established",
                "current_compatibility": "not_established"}


class ReplayArchive:
    """Immutable exact-key JSON archive composing the existing CD-7 resolver."""

    def __init__(self, artifacts):
        records, snapshots, total = {}, [], 0
        for index, (kind, raw) in enumerate(artifacts):
            if index >= MAX_RECORDS:
                raise ReplayError("archive_limit_exceeded")
            if type(raw) is not bytes:
                raise ReplayError("invalid_retained_document")
            total += len(raw)
            if total > MAX_ARCHIVE_BYTES:
                raise ReplayError("archive_limit_exceeded")
            if kind in ARTIFACT_SCHEMAS:
                _document(raw, ARTIFACT_SCHEMAS[kind])
                snapshots.append((kind, raw))
            elif kind in INPUT_SCHEMAS:
                document = _document(raw, INPUT_SCHEMAS[kind])
                key = _key(kind, document)
                if key in records:
                    raise ReplayError("duplicate_immutable_artifact_key")
                records[key] = raw
            else:
                raise ReplayError("unsupported_artifact_kind")
        self._snapshots = SnapshotArchive(snapshots)
        self._records = records

    def _bind(self, kind, pin):
        if pin is None:
            return ReplayBinding(kind, "not_supplied" if kind in OPTIONAL_INPUTS
                                 else "required_pin_missing")
        raw = self._records.get(_key(kind, pin))
        if raw is None:
            return ReplayBinding(kind, "pinned_artifact_unavailable")
        if digest(raw) != pin["sha256"]:
            return ReplayBinding(kind, "content_digest_mismatch")
        return ReplayBinding(kind, "resolved", raw)

    def replay(self, build_bytes, sidecar_bytes, manifest_bytes):
        packet = _manifest(manifest_bytes)
        build = _document(build_bytes, "build.schema.json")
        if packet["build_sha256"] != digest(build_bytes):
            raise ReplayError("manifest_build_mismatch")
        if sidecar_bytes is not None:
            bounded_json(sidecar_bytes, MAX_ENVELOPE_BYTES)
        if packet["revision_locks_sha256"] != (digest(sidecar_bytes) if sidecar_bytes is not None else None):
            raise ReplayError("manifest_sidecar_mismatch")

        profile_issues = []

        def result(status, issues=(), bindings=(), generated=None):
            # Reader availability and retained data identity are independent.
            # An unavailable reader must not erase an exact historical report
            # or diagnostics already established for another pinned artifact.
            if profile_issues:
                status = "profile_unavailable"
                issues = [*profile_issues, *issues]
            return ReplayResult(status, tuple(issues), tuple(bindings), build_bytes,
                                sidecar_bytes, manifest_bytes, generated)

        try:
            evaluator = _local_evaluator(packet["evaluator"])
        except ReplayError as error:
            profile_issues.append(("evaluator", error.code))

        resolution = self._snapshots.resolve(build_bytes, sidecar_bytes)
        for binding in (resolution.catalog_snapshot, resolution.pricebook):
            if binding is not None and binding.revision is not None:
                _integer(binding.revision)
        bindings = [ReplayBinding("catalog_snapshot", resolution.catalog_snapshot.status,
                                  resolution.catalog_snapshot.raw)]
        if resolution.pricebook is not None:
            bindings.append(ReplayBinding("pricebook", resolution.pricebook.status,
                                          resolution.pricebook.raw))
        else:
            bindings.append(ReplayBinding("pricebook", "not_supplied"))
        bindings.extend(self._bind(kind, packet["inputs"][kind]) for kind in INPUT_SCHEMAS)
        issues = [(binding.kind, binding.status) for binding in bindings
                  if binding.status not in {"resolved", "not_supplied"}]
        if issues:
            status = ("input_digest_mismatch" if any(code == "content_digest_mismatch"
                      for _, code in issues) else "inputs_unavailable")
            return result(status, issues, bindings)
        selection_issues = [("selection:" + selection.selection_id, selection.status)
                            for selection in resolution.selections
                            if selection.status not in {"resolved", "not_enabled"}]
        if selection_issues:
            # Some frozen metrics index catalog entries by ID alone, and
            # unused kinds may produce no finding for an absent/wrong item.
            # This profile requires exact enabled-selection associations;
            # historical rule failures remain a separate evaluator outcome.
            return result("input_identity_mismatch", selection_issues, bindings)
        documents = {binding.kind: decode(binding.raw) for binding in bindings if binding.raw is not None}
        locks = build["locks"]
        rules, graph, report = (documents[kind] for kind in
                                ("ruleset", "dependency_graph", "evaluation_report"))
        if (rules["id"], rules["version"]) != (locks["ruleset_id"], locks["ruleset_version"]):
            issues.append(("ruleset", "build_lock_mismatch"))
        if (graph["id"], graph["revision"]) != (locks["dependency_graph_id"], locks["dependency_graph_revision"]):
            issues.append(("dependency_graph", "build_lock_mismatch"))
        for kind in ("resource_estimate", "cost_estimate", "evaluation_report"):
            document = documents.get(kind)
            if document is not None and (document["build_id"], document["build_revision"]) != (build["id"], build["revision"]):
                issues.append((kind, "build_identity_mismatch"))
        if any(report[name] != locks[name] for name in (
                "catalog_snapshot_id", "ruleset_id", "ruleset_version",
                "dependency_graph_id", "dependency_graph_revision")):
            issues.append(("evaluation_report", "build_lock_mismatch"))
        selections = {selection["id"]: selection for selection in build["selections"]}
        resource, cost, prices = (documents.get(kind) for kind in
                                  ("resource_estimate", "cost_estimate", "pricebook"))
        if resource is not None and any(selection_id not in selections
                for estimate in resource["estimates"] for selection_id in estimate["selection_ids"]):
            issues.append(("resource_estimate", "selection_identity_mismatch"))
        catalog = documents["catalog_snapshot"]
        members = {(item["id"], item["version"]) for item in catalog["items"]}
        if prices is not None and any((rate["catalog_item_id"], rate["catalog_item_version"]) not in members
                                      for rate in prices["rates"]):
            issues.append(("pricebook", "rate_catalog_mismatch"))
        if cost is not None:
            if prices is None or cost["pricebook_id"] != prices["id"]:
                issues.append(("cost_estimate", "pricebook_identity_mismatch"))
            else:
                rates = {rate["id"]: rate for rate in prices["rates"]}
                for line in cost["line_items"]:
                    selection, rate = selections.get(line["selection_id"]), rates.get(line["price_rate_id"])
                    if (selection is None or rate is None
                            or (rate["catalog_item_id"], rate["catalog_item_version"], rate["meter"])
                            != (selection["catalog_item_id"], selection["catalog_item_version"], line["meter"])):
                        issues.append(("cost_estimate", "line_identity_mismatch"))
                        break
                if any(selection_id not in selections for selection_id in cost["unpriced_selection_ids"]):
                    issues.append(("cost_estimate", "selection_identity_mismatch"))
        if issues:
            return result("input_identity_mismatch", issues, bindings)
        if len({item["id"] for item in catalog["items"]}) != len(catalog["items"]):
            return result("profile_unsupported", [("catalog_snapshot", "multiple_versions_per_item_id")], bindings)
        if profile_issues:
            return result("profile_unavailable", bindings=bindings)
        try:
            # The frozen evaluator uses Decimal arithmetic. Fix its ambient
            # context; never accept its development-only metrics override.
            context = Context(prec=28, rounding=ROUND_HALF_EVEN, Emin=-999999,
                              Emax=999999, capitals=1, clamp=0, flags=[],
                              traps=[InvalidOperation, DivisionByZero, Overflow])
            with localcontext(context):
                generated = evaluator(build, catalog, rules, cost_estimate=cost,
                                      resource_estimate=resource).evaluate()
            _document(encoded(generated), "evaluation-report.schema.json")
        except (ArithmeticError, KeyError, TypeError, ValueError, RecursionError):
            return result("evaluation_failed", [("evaluator", "retained_inputs_not_evaluable")], bindings)
        # Compare complete typed JSON values, including ordered findings and
        # the frozen timestamp. Do not equate JSON 1.0 or true with integer 1.
        if encoded(generated) != encoded(report):
            return result("report_mismatch", [("evaluation_report", "generated_report_differs")], bindings, generated)
        return result("reproduced", bindings=bindings, generated=generated)
