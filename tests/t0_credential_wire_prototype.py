"""Synthetic CD-6 wire reader over exact CD-7 fixture artifacts.

This reads reference presence, never a secret value, network endpoint or vault.
Results do not contain a credential locator or any submitted free-form text.
It does not establish source eligibility, authorization or permission to execute.
"""

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from credential_binding_prototype import Outcome, combine, requirement
from t0_revision_lock_prototype import decode, digest

WIRE_SCHEMA = json.loads((ROOT / "tests/fixtures/t0-credential-bindings.schema.json").read_text())
WIRE_VALIDATOR = Draft202012Validator(WIRE_SCHEMA)
SELECTION_ID = re.compile(r"[a-z][a-z0-9_-]{2,79}")
ENTITY_ID = re.compile(r"[a-z][a-z0-9._:-]{2,119}")
SECRET_LOCATOR = re.compile(r"secret://[A-Za-z0-9/_:.-]+")


@dataclass(frozen=True)
class Check:
    code: str
    outcome: Outcome


@dataclass(frozen=True)
class ToolResult:
    selection_id: str
    outcome: Outcome
    checks: tuple[Check, ...]
    severity: str = "error"
    on_unknown: str = "review"


@dataclass(frozen=True)
class Projection:
    build_sha256: str
    tools: tuple[ToolResult, ...]
    revision_binding: str
    proposal_version: str = "cd6-0.1"
    evidence: str = "synthetic_contract_experiment"
    authorization: str = "not_evaluated"
    secret_resolution: str = "not_performed"


def _preflight(build):
    # The frozen regexes use $, which also matches before a final LF. This new
    # reader needs complete identifiers before it emits any selected identity.
    if not ENTITY_ID.fullmatch(build["id"]):
        raise ValueError("invalid build identity")
    selections = {s["id"]: s for s in build["selections"]}
    for selection in build["selections"]:
        if (not SELECTION_ID.fullmatch(selection["id"])
                or not ENTITY_ID.fullmatch(selection["catalog_item_id"])):
            raise ValueError("invalid selection identity")
        locator = selection["settings"].get("credential_ref")
        if locator is not None and not SECRET_LOCATOR.fullmatch(locator):
            raise ValueError("invalid opaque credential reference")
    link_ids = set()
    for link in build["links"]:
        if (not ENTITY_ID.fullmatch(link["id"]) or link["id"] in link_ids
                or link["from_selection_id"] not in selections
                or link["to_selection_id"] not in selections):
            raise ValueError("invalid or ambiguous link identity")
        link_ids.add(link["id"])
    return selections


def _support(spec, field, value):
    # No frozen completeness marker proves that an unlisted method/operation
    # is unsupported. A positive membership is only a metadata presence fact.
    values = spec.get(field)
    return True if values and value in values else None


def _row(selection_id, facts):
    checks = tuple(Check(code, requirement(fact)) for code, fact in facts)
    return ToolResult(selection_id, combine(tuple(c.outcome for c in checks)), checks)


def _catalog_binding(selected):
    if selected.status == "resolved":
        return True
    return False if selected.status == "selected_kind_mismatch" else None


def project(archive, build_bytes, revision_pins=None, credential_sidecar=None):
    """Read a chosen source without inferring one for a legacy build.

    The closed build inventory controls selection existence and enabled state.
    CD-7 resolves the exact selected item/version/kind. Unmarked catalog lists
    cannot prove an unsupported method, and v1 cannot prove provider hosting or
    tool availability on a provider/API tuple. Those checks remain unknown.
    """
    try:
        resolution = archive.resolve(build_bytes, revision_pins)
        build = decode(build_bytes)
        selections = _preflight(build)
        proposal = None
        if credential_sidecar is not None:
            document = decode(credential_sidecar)
            WIRE_VALIDATOR.validate(document)
            proposal = document["x_t0_credential_bindings"]
            if proposal["build_sha256"] != digest(build_bytes):
                raise ValueError("credential sidecar differs from retained build")
            if (revision_pins is not None
                    and proposal["revision_locks_sha256"] != digest(revision_pins)):
                raise ValueError("credential sidecar differs from retained revision pins")
    except (ValueError, TypeError, KeyError, ValidationError):
        # A JSON-schema diagnostic may include an entire submitted setting.
        # Keep original exception values and opaque locators out of diagnostics.
        raise ValueError("invalid retained credential-binding input") from None

    revision_binding = ("credential_sidecar_missing" if proposal is None else
                        "revision_pins_missing" if revision_pins is None else
                        "exact_pin_bytes_verified")
    bindings = defaultdict(list)
    for binding in proposal["bindings"] if proposal is not None else ():
        selection = selections.get(binding["selection_id"])
        if selection is None or selection["kind"] != "tool":
            raise ValueError("credential binding must name a retained tool selection")
        bindings[binding["selection_id"]].append(binding)
    resolved = {item.selection_id: item for item in resolution.selections}
    rows = []
    for selection in build["selections"]:
        if selection["kind"] != "tool":
            continue
        identity = selection["id"]
        if not selection["enabled"]:
            rows.append(ToolResult(identity, Outcome.SKIPPED,
                                   (Check("selection_not_enabled", Outcome.SKIPPED),)))
            continue
        choices = bindings[identity]
        if len(choices) != 1:
            reason = "binding_missing" if not choices else "competing_bindings"
            rows.append(_row(identity, ((reason, None),)))
            continue
        binding = choices[0]
        item = resolved[identity].item
        spec = item["spec"] if item is not None else {}
        local_present = "credential_ref" in selection["settings"]
        source = binding["source"]
        facts = [("credential_revision_pins_bound", True if revision_pins is not None else None),
                 ("catalog_" + resolution.catalog_snapshot.status,
                  True if resolution.catalog_snapshot.status == "resolved" else None),
                 ("tool_catalog_binding_valid", _catalog_binding(resolved[identity])),
                 ("chosen_tool_auth_supported", _support(spec, "auth_methods", binding["auth_method"]))]
        if source == "direct":
            facts.append(("direct_reference_present", local_present))
        elif source == "none":
            # Explicitly choosing a supported unauthenticated path is different
            # from guessing none when a binding or auth method is missing.
            pass
        else:
            if local_present:
                rows.append(_row(identity, (("local_and_inherited_source_conflict", None),)))
                continue
            target_id = binding["target_selection_id"]
            target = selections.get(target_id)
            facts.append(("target_selection_exists", target is not None))
            if target is not None:
                facts.extend((("target_kind_matches", target["kind"] == source),
                              ("target_selection_enabled", target["enabled"])))
                target_item = resolved[target_id].item
                target_spec = target_item["spec"] if target_item is not None else {}
                facts.extend((("target_catalog_binding_valid", _catalog_binding(resolved[target_id])),
                              ("target_reference_present", "credential_ref" in target["settings"])))
                method_field = "auth_methods" if source == "integration" else "supported_auth"
                facts.append(("chosen_target_auth_supported",
                              _support(target_spec, method_field, binding["auth_method"])))
                if source == "integration":
                    facts.append(("connection_serves_operation", _support(
                        target_spec, "associated_tool_refs", selection["catalog_item_id"])))
                else:
                    facts.extend((("provider_hosted_execution_evidence", None),
                                  ("provider_api_operation_evidence", None)))
            matching_links = [link for link in build["links"]
                              if link["relation"] == "provided_by"
                              and link["from_selection_id"] == identity
                              and link["to_selection_id"] == target_id]
            facts.append(("one_exact_provided_by_link", len(matching_links) == 1
                          if len(matching_links) < 2 else None))
        rows.append(_row(identity, facts))
    return Projection(digest(build_bytes), tuple(rows), revision_binding)
