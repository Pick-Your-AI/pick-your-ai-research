"""Explicit synthetic CD-3 adapter for two named frozen support assertions.

This is a per-rule mechanics experiment, not the frozen evaluator's dispatch or
a build replay. Callers establish source/date/rank/scope admission and qualify
each input independently. Matching hashes or cohort labels establish none of
that evidence. Frozen v1 files, rule definitions and all other rules stay intact.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from contracts.v1.reference import evaluate as frozen
from scripts.validate_research import SCHEMAS, schema_errors
from tests.selection_quantifier_prototype import Selection, validate_identities
from tests.support_membership_binding_prototype import (
    ELIGIBILITY, SCOPE, decode, definition, digest, validate,
)
from tests.support_membership_prototype import (
    Decision, Evidence, Outcome, Requirement, evaluate, normalized_fact,
    requested_values,
)


ROOT = Path(__file__).resolve().parents[1]
PROFILE = "cd3-frozen-support-rules-0.1"
RULESET_SHA256 = "e60e43c0abc3c5d927e10c578a39fdedfa76e00fce6242e2db3a46e4b1da907e"
EVALUATOR_SHA256 = "092c8a99495f9b5ae960df40b27e33f15eefe6d1a7cd80119658fdc79ada1a5a"
RULE_IDS = ("rule.engine.model.format", "rule.precision.engine")
COHORT = Draft202012Validator(definition("reference"))


@dataclass(frozen=True, slots=True)
class RuleEvidence:
    """Normalized caller facts, not a source/date admission or wire envelope.

    Positive support values come from the actual frozen catalog operand. An
    explicit unsupported inventory must be recorded, including an empty set;
    None is unresolved. Requested completeness applies to researched arrays.
    Neither this record nor the catalog invents its own eligibility or grade.
    """

    cohort_id: str
    cohort_version: str
    scope: dict | None
    unsupported: frozenset[str] | None = None
    exhaustive: bool | None = None
    requested_complete: bool | None = None


def _document(raw, schema_name):
    document = decode(raw)
    errors = schema_errors(document, SCHEMAS[schema_name])
    if errors:
        raise ValueError("invalid frozen input: " + errors[0])
    if type(document["revision"]) is not int:
        raise ValueError("revision must use a JSON integer")
    return document


class FrozenSupportRuleAdapter:
    """Read actual operands for only the two pinned baseline rule identities.

    Full input shape and build-wide identities are checked before shortcuts.
    Unavailable exact selections/items/versions/properties remain unresolved.
    No current/latest lookup, default setting, general interpreter, sidecar
    migration, source access or whole-build ruleset-lock decision is performed.
    """

    def __init__(self, build_raw, catalog_raw):
        ruleset_raw = (ROOT / "contracts/v1/baseline/core-ruleset.json").read_bytes()
        if (digest(ruleset_raw) != RULESET_SHA256
                or digest(Path(frozen.__file__).read_bytes()) != EVALUATOR_SHA256):
            raise ValueError("frozen rule adapter source pin mismatch")
        build = _document(build_raw, "build.schema.json")
        catalog = _document(catalog_raw, "catalog-snapshot.schema.json")
        validate_identities(tuple(Selection(s["id"], s["kind"], s["role"], s["enabled"])
                                  for s in build["selections"]))
        if len({item["id"] for item in catalog["items"]}) != len(catalog["items"]):
            raise ValueError("duplicate catalog item id")
        self._build, self._catalog = build, catalog
        self._raw = build_raw, catalog_raw, ruleset_raw
        self._ruleset = decode(ruleset_raw)
        self._rules = {rule["id"]: rule for rule in self._ruleset["rules"]
                       if rule["id"] in RULE_IDS}
        self._reader = frozen.Evaluator(build, catalog, self._ruleset)
        self._items = {item["id"]: (i, item) for i, item in enumerate(catalog["items"])}

    @property
    def original_bytes(self):
        return self._raw

    def _rule(self, rule_id):
        if type(rule_id) is not str or rule_id not in RULE_IDS:
            raise ValueError("unsupported frozen support rule")
        return self._rules[rule_id]

    def _read(self, operand):
        ref = operand["ref"]
        result = {"ref": deepcopy(ref), "state": "unknown", "reason": "selection_unresolved"}
        selection = self._reader.selected(ref)
        if selection is frozen.UNKNOWN:
            return result
        result["selection"] = {key: selection[key] for key in (
            "id", "kind", "role", "enabled", "catalog_item_id", "catalog_item_version")}
        if ref["scope"] == "selection":
            index = next(i for i, value in enumerate(self._build["selections"])
                         if value is selection)
            document, prefix = selection, f"/selections/{index}"
        else:
            entry = self._items.get(selection["catalog_item_id"])
            if entry is None:
                return result | {"reason": "catalog_item_missing"}
            index, document = entry
            result["catalog_item"] = {key: document[key] for key in ("id", "version", "kind")}
            if document["version"] != selection["catalog_item_version"]:
                return result | {"reason": "catalog_version_mismatch"}
            if document["kind"] != selection["kind"]:
                return result | {"reason": "catalog_kind_mismatch"}
            prefix = f"/items/{index}"
        value = frozen.pointer_get(document, ref["pointer"])
        if value is frozen.UNKNOWN:
            return result | {"reason": "property_missing"}
        return result | {"state": "provided", "reason": "resolved",
                         "value": deepcopy(value), "source_path": prefix + ref["pointer"]}

    def _operands(self, rule):
        applicability = rule["applies_when"]["args"]
        return {
            "deployment_mode": self._read(applicability[0]["left"]),
            "engine_presence": self._read(applicability[1]["value"]),
            "left": self._read(rule["assert"]["left"]),
            "right": self._read(rule["assert"]["right"]),
        }

    def _scope(self, supported):
        if supported["state"] != "provided":
            return None
        return {"selection_id": supported["selection"]["id"],
                "catalog_sha256": digest(self._raw[1]),
                "item": deepcopy(supported["catalog_item"]),
                "property": supported["ref"]["pointer"],
                "conditions_sha256": digest(self._raw[0])}

    def support_scope(self, rule_id):
        """Describe exact input scope; this does not qualify the evidence."""
        rule = self._rule(rule_id)
        side = "left" if rule["assert"]["op"] == "contains" else "right"
        return self._scope(self._read(rule["assert"][side]))

    def evaluate(self, rule_id, evidence, *, eligible_inputs=None, cohort_checked_only=None):
        rule = self._rule(rule_id)
        if type(evidence) is not RuleEvidence:
            raise ValueError("rule evidence must be a normalized RuleEvidence record")
        cohort = {"id": evidence.cohort_id, "version": evidence.cohort_version}
        validate(COHORT, cohort, "rule evidence cohort")
        if evidence.scope is not None:
            validate(SCOPE, evidence.scope, "rule support scope")
        json.dumps((cohort, evidence.scope), ensure_ascii=False).encode("utf-8")
        requested_values(evidence.unsupported)
        normalized_fact(evidence.exhaustive)
        normalized_fact(evidence.requested_complete)
        normalized_fact(cohort_checked_only)
        if eligible_inputs is None:
            eligible_inputs = {}
        if type(eligible_inputs) is not dict or set(eligible_inputs) - set(ELIGIBILITY):
            raise ValueError("unsupported rule input qualification")
        for value in eligible_inputs.values():
            normalized_fact(value)
        eligible = {key: eligible_inputs.get(key) for key in ELIGIBILITY}
        operands = self._operands(rule)
        scalar = rule["assert"]["op"] == "contains"
        requested = operands["right" if scalar else "left"].get("value")
        supported = operands["left" if scalar else "right"]
        scope = self._scope(supported)
        mode, engine = operands["deployment_mode"], operands["engine_presence"]
        mode_matches = (frozen.UNKNOWN if mode["state"] != "provided" else
                        mode["value"] == rule["applies_when"]["args"][0]["right"]["literal"])
        applicability = frozen.boolean_and([
            mode_matches, engine["state"] == "provided" and engine["value"] is not None])
        complete = (True if scalar and requested is not None and eligible["requested"] is True
                    else evidence.requested_complete if not scalar
                    and eligible["requested_complete"] is True else None)
        completeness_basis = ("admitted_selected_scalar" if scalar and complete is True
                              else "caller_qualified_catalog_inventory" if not scalar
                              and eligible["requested_complete"] is True
                              and evidence.requested_complete is not None else "unresolved")

        def uncertain(reason, outcome=Outcome.UNKNOWN):
            return Decision(outcome, reason, evidence.cohort_id)

        if self._build["locks"]["catalog_snapshot_id"] != self._catalog["id"]:
            decision = uncertain("catalog_snapshot_mismatch")
        elif eligible["applies_when"] is not True:
            decision = uncertain("applicability_evidence_unqualified")
        elif applicability is False:
            decision = uncertain("not_applicable", Outcome.SKIPPED)
        elif applicability is frozen.UNKNOWN:
            decision = uncertain("applicability_unknown")
        elif scope is None:
            decision = uncertain("support_operand_unresolved")
        elif evidence.scope != scope:
            decision = uncertain("support_scope_mismatch")
        elif eligible["requested"] is not True:
            decision = uncertain("requested_evidence_unqualified")
        elif requested is None:
            decision = uncertain("requirement_unknown")
        elif eligible["cohort"] is not True:
            decision = uncertain("cohort_evidence_unqualified")
        elif evidence.unsupported is None:
            decision = uncertain("unsupported_claims_unresolved")
        else:
            decision = evaluate(
                frozenset((requested,)) if scalar else frozenset(requested),
                Evidence(evidence.cohort_id, True, frozenset(supported["value"]),
                         evidence.exhaustive, evidence.unsupported,
                         checked_only=cohort_checked_only),
                Requirement.ANY, requested_complete=complete,
            )
        return {"profile": PROFILE,
                "ruleset": {"id": self._ruleset["id"], "version": self._ruleset["version"],
                            "sha256": RULESET_SHA256, "reference_sha256": EVALUATOR_SHA256},
                "rule": deepcopy(rule),
                "build_sha256": digest(self._raw[0]), "catalog_sha256": digest(self._raw[1]),
                "operands": operands, "support_scope": scope,
                "applicability": None if applicability is frozen.UNKNOWN else applicability,
                "evidence": {"cohort": cohort, "scope": deepcopy(evidence.scope),
                             "unsupported": (None if evidence.unsupported is None
                                             else sorted(evidence.unsupported)),
                             "exhaustive": evidence.exhaustive,
                             "requested_complete": evidence.requested_complete},
                "evaluation": {"eligible_inputs": eligible,
                               "cohort_checked_only": cohort_checked_only},
                "requested_completeness": {"effective": complete, "basis": completeness_basis},
                "decision": asdict(decision)}
